import json
import datetime
import time
import io
from types import SimpleNamespace
from collections.abc import Iterable
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from ..helper.etree import as_etree, as_table

class DefaultSimpleNamespace(SimpleNamespace):
    def __getattribute__(self, attr):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            return None


_connection = None
_project = None
_build_client = None
_test_client = None
_git_client = None
_pipeline_client = None

def connect(pat, organization, project):
    global _connection, _project
    organization_url = 'https://dev.azure.com/{ORGANIZATION_NAME}'.format(ORGANIZATION_NAME=organization)
    credentials = BasicAuthentication('', pat)
    _connection = Connection(base_url=organization_url, creds=credentials)
    _connection._config.verify=False
    _project = project

def init_build():
    global _build_client, _connection

    _connection._config.verify=False
    _build_client = _connection.clients_v6_0.get_build_client()
    _build_client.config.verify=False
    
def make_json_friendly(doc):
    if isinstance(doc, str):
        return doc
    if isinstance(doc, datetime.datetime):
        return doc.isoformat()
    if isinstance(doc, Iterable) and not isinstance(doc, dict):
        return [make_json_friendly(i) for i in doc]
    else:
        if hasattr(doc, '__dict__'):
            result = { k: make_json_friendly(v) for k,v in doc.__dict__.items() }
        else:
            result = doc
        return result
        return doc.as_dict()

def build_get_builds():
    global _build_client, _project
    _build_client.config.connection.verify = False
    build_list = _build_client.get_builds(_project)
    result = make_json_friendly(build_list)
    return result

def build_get_definitions():
    global _build_client, _project
    build_list = _build_client.get_definitions(_project)
    result = make_json_friendly(build_list)
    return result



def init_test():
    global _test_client, _connection
    _test_client = _connection.clients_v6_0.get_test_client()

def test_get_test_runs(*args, **kwargs):
    global _test_client, _project

    if len(args) < 1 and not kwargs.get('project',None):
        kwargs['project'] = _project

    raw_result = _test_client.get_test_runs(*args, **kwargs)
    result = make_json_friendly(raw_result)
    return result

def test_get_test_run_by_id(*args, **kwargs):
    global _test_client, _project

    if len(args) < 1 and not kwargs.get('project',None):
        kwargs['project'] = _project

    raw_result = _test_client.get_test_run_by_id(*args, **kwargs)
    result = make_json_friendly(raw_result)
    return result



def helper_transform(input, mapping_filename):
    with open(mapping_filename, 'r') as f:
        mapping = json.load(f)
    
    doc = as_etree(json.loads(input), root_tag=mapping['root_name'], 
                   item_tag=mapping['item_name'])
    mapping_options = dict(
        path_item=mapping.get('item_path', None), 
        field_map=mapping['field_map'],
        header_row=mapping.get('header_row', None),
        path_root=mapping.get('root_path', None),
        output_fields=mapping.get('output_fields', None)
    )
    result = as_table(doc,**mapping_options)
    return result

def init_git():
    global _git_client, _connection
    _git_client = _connection.clients_v6_0.get_git_client()


def git_get_repositories(*args, **kwargs):
    global _git_client, _project

    if len(args) < 1 and not kwargs.get('project',None):
        kwargs['project'] = _project
    raw_result = _git_client.get_repositories(*args, **kwargs)
    result = make_json_friendly(raw_result)
    return result

def git_commit_list(repository_id, project=None, top=100):
    global _git_client, _project

    search_criteria = DefaultSimpleNamespace()
    search_criteria.top = top
    
    params = {
        'project': project or _project,
        'repository_id': repository_id,
        'search_criteria': search_criteria
    }
    raw_result = _git_client.get_commits(**params)
    result = make_json_friendly(raw_result)
    return result



def init_pipeline():
    global _pipeline_client, _connection
    _pipeline_client = _connection.clients_v6_0.get_pipelines_client()


def pipeline_list_pipelines(*args, **kwargs):
    global _pipeline_client, _project

    if len(args) < 1 and not kwargs.get('project',None):
        kwargs['project'] = _project
    raw_result = _pipeline_client.list_pipelines(*args, **kwargs)
    result = make_json_friendly(raw_result)
    return result

def pipeline_get_pipeline(*args, **kwargs):
    global _pipeline_client, _project

    if len(args) < 1 and not kwargs.get('project',None):
        kwargs['project'] = _project
    
    if (kwargs.get('pipeline_id',None)):
        raw_result = _pipeline_client.get_pipeline(*args, **kwargs)
        # print(raw_result._links)
        # return ({})
    else:
        if 'pipeline_id' in kwargs:
            del(kwargs['pipeline_id'])
        raw_result = []
        for pipeline in _pipeline_client.list_pipelines(*args, **kwargs):
            kwargs['pipeline_id'] = pipeline.id
            pipeline = _pipeline_client.get_pipeline(*args, **kwargs)
            raw_result.append(pipeline)
            time.sleep(2)
    result = make_json_friendly(raw_result)
    return result

def pipeline_list_runs(project, pipeline_id, relax_interval=0):
    global _pipeline_client, _project

    project = project or _project
    
    if pipeline_id:
        raw_result = _pipeline_client.list_runs(project, pipeline_id)
    else:
        raw_result = []
        for pipeline in _pipeline_client.list_pipelines(project):
            pipeline_runs = _pipeline_client.list_runs(project, pipeline.id)
            raw_result.extend(pipeline_runs)
            time.sleep(relax_interval)
    result = make_json_friendly(raw_result)
    return result
