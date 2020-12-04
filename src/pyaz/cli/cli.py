import os
import io
import re
import sys
import time
import json
import csv
import click
import dotenv
from . import command as cmd

def json_printer(indent=None, print_to_file=None):
    def json_print(doc):
        if print_to_file:
            with open(print_to_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(doc, indent=indent))
        else:
            print(json.dumps(doc, indent=indent))
    return json_print

_printer = None

@click.group()
@click.option('--indent', '-i', type=int, help='Output indent')
@click.option('--print-to-file', '-f', type=str, help='Print output to a file')
def cli(indent, print_to_file):
    global _printer

    dotenv.load_dotenv()
    _printer = json_printer(indent=indent, print_to_file=print_to_file)

@cli.group(name='helper')
def cli_helper():
    pass

@cli_helper.command(name='json-to-csv', help='Transform JSON file to CSV')
@click.option('--input-file', '-i', help='Input file name')
@click.option('--output-file', '-o', help='Output file name')
@click.option('--mapping', '-m', required=True, help='Mapping file name')
def helper_json_to_csv(input_file, output_file, mapping):
    if input_file:
        with open(input_file, 'r') as f:
            input = f.read()
    else:
        input = sys.stdin.read()
    buffer = io.StringIO()
    result = cmd.helper_transform(input, mapping)
    writer = csv.writer(buffer)
    writer.writerows(result)
    lines = [ line for line in re.split('[\\r\\n]', buffer.getvalue()) if line ]
    f = open(output_file, 'w', encoding='utf-8') if output_file else sys.stdout
    for line in lines:
        print(line, file=f)
    if (f is not sys.stdout): 
        f.close()

@cli.group(name='devops')
@click.option('--pat-token', '-t', help='Azure DevOps personal access token (PAT).')
@click.option('--organization', '-o', help='Azure DevOps organization name.')
@click.option('--project', '-p', help='Azure DevOps project name.')
def az_devops(pat_token, organization, project):
    pat_token = pat_token or os.environ.get('DEVOPS_PAT', None)
    if not pat_token:
        raise ValueError('Required personal access token is missing or empty. Use --pat-token/-t option or DEVOPS_PAT environment variable to define.')
    organization = organization or os.environ.get('DEVOPS_ORGANIZATION', None)
    if not organization:
        raise ValueError('Required organization name is missing or empty. Use --organization/-o option or DEVOPS_ORGANIZATION environment variable to define.')
    project = project or os.environ.get('DEVOPS_PROJECT', None)
    cmd.connect(pat_token, organization, project)

@az_devops.group(name="build")
def az_devops_build():
    cmd.init_build()

@az_devops_build.command(name='get-builds')
def az_devops_build_get_builds():
    global _printer

    builds = cmd.build_get_builds()
    _printer(builds)

@az_devops_build.command(name='get-definitions')
def az_devops_build_get_definitions():
    global _printer

    builds = cmd.build_get_definitions()
    _printer(builds)


@az_devops.group(name="test")
def az_devops_test():
    cmd.init_test()

@az_devops_test.command(name='get-test-runs')
@click.option('--project', '-p', help='Azure DevOps project name.')
@click.option('--include-run-details', is_flag=True)
def az_devops_test_get_test_runs(*args, **kwargs):
    global _printer

    result = cmd.test_get_test_runs(*args, **kwargs)
    _printer(result)

@az_devops_test.command(name='get-test-run-by-id')
@click.option('--project', '-p', help='Azure DevOps project name.')
@click.option('--run-id', required=True, type=int, help='Test Run ID.')
def az_devops_test_get_test_run_by_id(*args, **kwargs):
    global _printer

    result = cmd.test_get_test_run_by_id(*args, **kwargs)
    _printer(result)


@az_devops.group(name="git")
def az_devops_git():
    cmd.init_git()

@az_devops_git.command(name='list')
@click.option('--project', '-p', help='Azure DevOps project name.')
@click.option('--include-links', is_flag=True)
@click.option('--include-hidden', is_flag=True)
@click.option('--include-all-urls', is_flag=True)
def az_devops_git_list(*args, **kwargs):
    global _printer

    result = cmd.git_get_repositories(*args, **kwargs)
    _printer(result)

@az_devops_git.group(name="commit")
def az_devops_git_commit():
    cmd.init_git()


@az_devops_git_commit.command(name='list', help="List commits in a git repository")
@click.option('--project', '-p', help='Azure DevOps project name.')
@click.option('--repository-id', '-i', help="Repository ID")
@click.option('--add-repository-id', '-a', is_flag=True, help="If specified, repository_id will be added to each commit")
@click.option('--top', '-t', default=100, type=int, help="Time to wait, ")
@click.option('--relax-interval', '-i', default=2.0, type=float, help="Time to wait, ")
def az_devops_git_commit_list(*args, **kwargs):
    global _printer

    if kwargs.get('repository_id', None):
        repository_id_list = [kwargs['repository_id']]
        relax_interval = 0.0
    else:
        repositories_result = cmd.git_get_repositories()
        repository_id_list = [repo_info['id'] for repo_info in repositories_result]
        relax_interval = float(kwargs.get('relax_interval', 2))

    result = []
    params = {
        'top': kwargs['top']
    }

    is_first = True
    for repository_id in repository_id_list:
        if not is_first:
            time.sleep(relax_interval)
            is_first = False
        params['repository_id'] = repository_id
        repository_result = cmd.git_commit_list(**params)
        if kwargs.get('add_repository_id', False):
            for i in range(len(repository_result)):
                repository_result[i]['repository_id'] = repository_id
        result.extend(repository_result)
    _printer(result)


@az_devops.group(name="pipeline")
def az_devops_pipeline():
    cmd.init_pipeline()

@az_devops_pipeline.command(name='list')
@click.option('--project', '-p', help='Azure DevOps project name.')
# @click.option('--include-links', is_flag=True)
# @click.option('--include-hidden', is_flag=True)
# @click.option('--include-all-urls', is_flag=True)
def az_devops_pipeline_list(*args, **kwargs):
    global _printer

    result = cmd.pipeline_list_pipelines(*args, **kwargs)
    _printer(result)


@az_devops_pipeline.command(name='get')
@click.option('--project', '-p', help='Azure DevOps project name.')
@click.option('--pipeline-id', '-i', help='Pipeline ID')
def az_devops_pipeline_list(*args, **kwargs):
    global _printer

    result = cmd.pipeline_get_pipeline(*args, **kwargs)
    _printer(result)

@az_devops_pipeline.command(name='list-runs')
@click.option('--project', '-p', help='Azure DevOps project name.')
@click.option('--pipeline-id', '-i', help='Pipeline ID')
@click.option('--relax-interval', '-i', default=2.0, type=float, help="Time to wait, ")
def az_devops_pipeline_list(project, pipeline_id, relax_interval):
    global _printer

    result = cmd.pipeline_list_runs(project, pipeline_id, relax_interval=relax_interval)
    _printer(result)
