# SPDX-FileCopyrightText: Copyright contributors to the Software Quality Assurance as a Service (SQAaaS) project.
#
# SPDX-License-Identifier: GPL-3.0-only

import jinja2
import json
import logging
import os
import requests
import sys
import time


COMPLETED_STATUS = ['SUCCESS', 'FAILURE', 'UNSTABLE', 'ABORTED']
SUCCESFUL_STATUS = ['SUCCESS', 'UNSTABLE']
# FIXME: add as CLI argument
ENDPOINT = "https://api-staging.sqaaas.eosc-synergy.eu/v1"
SUMMARY_TEMPLATE_TABLE= """
| Result | Assertion | Subcriterion ID | Criterion ID |
| ------ | --------- | --------------- | ------------ |
{%- for result in results %}
| {{ ":heavy_check_mark:" if result.status else ":red_circle:" }} | {{ result.assertion }} | {{ result.subcriterion }} | {{ result.criterion }} |
{%- endfor -%}
"""
SUMMARY_TEMPLATE = """## SQAaaS summary :bellhop_bell:

{0}

:clipboard: _View full report at_ ___{1}___
"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sqaaas-gh-action')


def create_payload(repo, branch=None):
    return json.dumps({
        'repo_code': {
            'repo': repo,
            'branch': branch
        },
        'repo_docs': {
            'repo': repo,
            'branch': branch
        }
    })


def sqaaas_request(method, path, payload={}):
    method = method.upper()
    headers = {
        "Content-Type": "application/json"
    }
    args = {
        'method': method,
        'url': '{}/{}'.format(ENDPOINT, path),
        'headers': headers
    }
    if method in ['POST']:
        args['json'] = payload

    _error_code = None
    try:
        response = requests.request(**args)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except requests.HTTPError as http_err:
        logger.info(f'HTTP error occurred: {http_err}')
        _error_code = 101
    except Exception as err:
        logger.info(f'Other error occurred: {err}')
        _error_code = 102
    else:
        logger.info('Success!')
        return response
    if _error_code:
        sys.exit(_error_code)


def run_assessment(repo, branch=None):
    pipeline_id = None
    action = 'create'
    sqaaas_report_json = {}

    wait_period = 5
    keep_trying = True
    while keep_trying:
        # logger.info(f'Performing {action} on pipeline {pipeline_id}')
        # if action in ['create']:
        #     payload = json.loads(create_payload(repo, branch))
        #     response = sqaaas_request('post', f'pipeline/assessment', payload=payload)
        #     response_data = response.json()
        #     pipeline_id = response_data['id']
        #     action = 'run'
        # elif action in ['run']:
        #     response = sqaaas_request('post', f'pipeline/{pipeline_id}/{action}')
        #     action = 'status'
        # elif action in ['status']:
        #     response = sqaaas_request('get', f'pipeline/{pipeline_id}/{action}')
        #     response_data = response.json()
        #     build_status = response_data['build_status']
        #     if build_status in COMPLETED_STATUS:
        #         action = 'output'
        #         logging.info(f'Pipeline {pipeline_id} finished with status {build_status}')
        #     else:
        #         time.sleep(wait_period)
        #         logger.info(f'Current status is {build_status}. Waiting {wait_period} seconds..')
        # elif action in ['output']:
            pipeline_id = '0c066a45-f2ab-46d7-b78f-308bb457ae82'
            action = 'output'
            keep_trying = False
            response = sqaaas_request('get', f'pipeline/assessment/{pipeline_id}/{action}')
            sqaaas_report_json = response.json()

    return sqaaas_report_json


def get_table(sqaaas_report_json):
    assessment_results = []
    for criterion, criterion_data in sqaaas_report_json['report'].items():
        for subcriterion, subcriterion_data in criterion_data['subcriteria'].items():
            for evidence in subcriterion_data['evidence']:
                # Fix message
                msg = evidence['message']
                msg = msg.replace('<', '_')
                msg = msg.replace('>', '_')
                msg = msg.replace('\n', '<br />')
                # Generate entry for result
                assessment_results.append({
                    'status': evidence['valid'],
                    'assertion': msg,
                    'subcriterion': subcriterion,
                    'criterion': criterion
                })
    template = jinja2.Environment().from_string(SUMMARY_TEMPLATE_TABLE)
    return template.render(results=assessment_results)


def write_summary(*args):
    if "GITHUB_STEP_SUMMARY" in os.environ :
        logger.info('Setting GITHUB_STEP_SUMMARY environment variable')
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f :
            print(SUMMARY_TEMPLATE.format(*args), file=f)


def main(repo, branch=None):
    # Get assessment report (JSON format)
    sqaaas_report_json = run_assessment(repo, branch=None)
    if sqaaas_report_json:
        table = get_table(sqaaas_report_json)
        logger.info(table)
        report_url = sqaaas_report_json['meta']['report_json_url']
        logger.info(SUMMARY_TEMPLATE.format(table, report_url))
        write_summary(table, report_url)
    else:
        logger.info('Could not get report data from SQAaaS platform')


if __name__ == "__main__":
    script, repo, branch = sys.argv
    main(repo, branch)
