import json
from collections.abc import Iterable
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from ..helper.etree import as_etree, as_table

_connection = None
_project = None
_build_client = None
_test_client = None

def connect(pat, organization, project):
    global _connection, _project
    organization_url = 'https://dev.azure.com/{ORGANIZATION_NAME}'.format(ORGANIZATION_NAME=organization)
    credentials = BasicAuthentication('', pat)
    _connection = Connection(base_url=organization_url, creds=credentials)
    _project = project

def init_build():
    global _build_client, _connection
    _build_client = _connection.clients_v6_0.get_build_client()



def make_json_friendly(doc):
    if isinstance(doc, Iterable):
        return [make_json_friendly(i) for i in doc]
    else:
        return doc.as_dict()

def build_get_builds():
    global _build_client, _project
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
