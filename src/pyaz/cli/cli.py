import os
import sys
import json
import csv
import click
import dotenv
from . import command as cmd

def json_printer(indent=None):
    def json_print(doc):
        print(json.dumps(doc, indent=indent))
    return json_print

_printer = None

@click.group()
@click.option('--indent', '-i', type=int, help='Output indent')
def cli(indent):
    global _printer

    dotenv.load_dotenv()
    _printer = json_printer(indent=indent)

@cli.group(name='helper')
def cli_helper():
    pass

@cli_helper.command(name='json-to-csv', help='Transform JSON file to CSV')
@click.option('--input-file', '-i', help='Input file name')
@click.option('--mapping', '-m', required=True, help='Mapping file name')
def helper_json_to_csv(input_file, mapping):
    if input_file:
        with open(input_file, 'r') as f:
            input = f.read()
    else:
        input = sys.stdin.read()
    result = cmd.helper_transform(input, mapping)
    writer = csv.writer(sys.stdout)
    writer.writerows(result)

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

