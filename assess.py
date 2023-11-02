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


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('sqaaas-gh-action')

COMPLETED_STATUS = ['SUCCESS', 'FAILURE', 'UNSTABLE', 'ABORTED']
SUCCESFUL_STATUS = ['SUCCESS', 'UNSTABLE']
LINKS_TO_STANDARD = {
    'QC.Acc': 'https://indigo-dc.github.io/sqa-baseline/#code-accessibility-qc.acc',
    'QC.Wor': 'https://indigo-dc.github.io/sqa-baseline/#code-workflow-qc.wor',
    'QC.Man': 'https://indigo-dc.github.io/sqa-baseline/#code-management-qc.man',
    'QC.Rev': 'https://indigo-dc.github.io/sqa-baseline/#code-review-qc.rev',
    'QC.Ver': 'https://indigo-dc.github.io/sqa-baseline/#semantic-versioning-qc.ver',
    'QC.Lic': 'https://indigo-dc.github.io/sqa-baseline/#licensing-qc.lic',
    'QC.Met': 'https://indigo-dc.github.io/sqa-baseline/#code-metadata-qc.met',
    'QC.Doc': 'https://indigo-dc.github.io/sqa-baseline/#documentation-qc.doc',
    'QC.Sty': 'https://indigo-dc.github.io/sqa-baseline/#code-style-qc.sty',
    'QC.Uni': 'https://indigo-dc.github.io/sqa-baseline/#unit-testing-qc.uni',
    'QC.Har': 'https://indigo-dc.github.io/sqa-baseline/#test-harness-qc.har',
    'QC.Tdd': 'https://indigo-dc.github.io/sqa-baseline/#test-driven-development-qc.tdd',
    'QC.Sec': 'https://indigo-dc.github.io/sqa-baseline/#security-qc.sec',
    'QC.Del': 'https://indigo-dc.github.io/sqa-baseline/#automated-delivery-qc.del',
    'QC.Dep': 'https://indigo-dc.github.io/sqa-baseline/#automated-deployment-qc.dep'
}
# FIXME: add as CLI argument
ENDPOINT = "https://api-staging.sqaaas.eosc-synergy.eu/v1"
BADGE_SHARE_MARKDOWN = {
    'gold': {
        'sqaaas': '[![SQAaaS badge](https://github.com/EOSC-synergy/SQAaaS/raw/master/badges/badges_150x116/badge_software_gold.png)]({assertion} "SQAaaS gold badge achieved")',
        'shields': '[![SQAaaS badge shields.io](https://img.shields.io/badge/sqaaas%20software-gold-yellow)]({assertion} "SQAaaS gold badge achieved")'
    },
    'silver': {
        'sqaaas': '[![SQAaaS badge](https://github.com/EOSC-synergy/SQAaaS/raw/master/badges/badges_150x116/badge_software_silver.png)]({assertion} "SQAaaS silver badge achieved")',
        'shields': '[![SQAaaS badge shields.io](https://img.shields.io/badge/sqaaas%20software-silver-lightgrey)]({assertion} "SQAaaS silver badge achieved")'
    },
    'bronze': {
        'sqaaas': '[![SQAaaS badge](https://github.com/EOSC-synergy/SQAaaS/raw/master/badges/badges_150x116/badge_software_bronze.png)]({assertion} "SQAaaS bronze badge achieved")',
        'shields': '[![SQAaaS badge shields.io](https://img.shields.io/badge/sqaaas%20software-bronze-e6ae77)]({assertion} "SQAaaS bronze badge achieved")'
    },
}
SUMMARY_TEMPLATE = """## SQAaaS results :bellhop_bell:

### Quality criteria summary
| Result | Assertion | Subcriterion ID | Criterion ID |
| ------ | --------- | --------------- | ------------ |
{%- for result in report_results %}
| {{ ":heavy_check_mark:" if result.status else ":heavy_multiplication_x:" }} | {{ result.assertion }} | {{ result.subcriterion }} | {{ result.criterion }} |
{%- endfor %}

### Quality badge
{%- if badge_results.assertion %}
 - SQAaaS-based badge: {{ badge_results.badge_sqaaas_md }}
 - shields.io-based badge: {{ badge_results.badge_shields_md }}
{%- else %}
 - _No SQAaaS badge has been obtained_
{%- endif %}
{%- if badge_results.next_level_badge %}
 - Missing quality criteria for next level badge ({{ badge_results.next_level_badge }}): {% for criterion_to_fulfill in badge_results.to_fulfill %}[`{{ criterion_to_fulfill }}`]({{ links_to_standard[criterion_to_fulfill] }}) {% endfor %}
{%- endif %}

### :clipboard: __View full report in the [SQAaaS platform]({{ report_url }})__
"""


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
        logger.info(f'Performing {action} on pipeline {pipeline_id}')
        if action in ['create']:
            payload = json.loads(create_payload(repo, branch))
            response = sqaaas_request('post', f'pipeline/assessment', payload=payload)
            response_data = response.json()
            pipeline_id = response_data['id']
            action = 'run'
        elif action in ['run']:
            response = sqaaas_request('post', f'pipeline/{pipeline_id}/{action}')
            action = 'status'
        elif action in ['status']:
            response = sqaaas_request('get', f'pipeline/{pipeline_id}/{action}')
            response_data = response.json()
            build_status = response_data['build_status']
            if build_status in COMPLETED_STATUS:
                action = 'output'
                logging.info(f'Pipeline {pipeline_id} finished with status {build_status}')
            else:
                time.sleep(wait_period)
                logger.info(f'Current status is {build_status}. Waiting {wait_period} seconds..')
        elif action in ['output']:
            keep_trying = False
            response = sqaaas_request('get', f'pipeline/assessment/{pipeline_id}/{action}')
            sqaaas_report_json = response.json()

    return sqaaas_report_json


def get_summary(sqaaas_report_json):
    # Collect quality report data
    report_results = []
    for criterion, criterion_data in sqaaas_report_json['report'].items():
        for subcriterion, subcriterion_data in criterion_data['subcriteria'].items():
            for evidence in subcriterion_data['evidence']:
                # Fix message
                msg = evidence['message']
                msg = msg.replace('<', '_')
                msg = msg.replace('>', '_')
                msg = msg.replace('\n', '<br />')
                # Generate entry for result
                report_results.append({
                    'status': evidence['valid'],
                    'assertion': msg,
                    'subcriterion': subcriterion,
                    'criterion': criterion
                })
    # Collect quality badge data
    badge_software = sqaaas_report_json['badge']['software']
    badge_sqaaas_md, badge_shields_md, missing = (None, None, None)
    try:
        assertion = badge_software['data']['openBadgeId']
    except KeyError:
        assertion = None
    else:
        to_fulfill = []
        next_level_badge = ''
        for badgeclass in ['gold', 'silver', 'bronze']:
            missing = badge_software['criteria'][badgeclass]['missing']
            if not missing:
                logger.debug(
                    'Not missing criteria: achieved %s badge' % badgeclass
                )
                badge_share_data = BADGE_SHARE_MARKDOWN[badgeclass]
                badge_sqaaas_md = badge_share_data['sqaaas'].format(
                    assertion=assertion
                )
                badge_shields_md = badge_share_data['shields'].format(
                    assertion=assertion
                )
                break
            else:
                to_fulfill = missing
                next_level_badge = badgeclass
                logger.debug(
                    'Missing criteria found (%s) for %s badge, going one '
                    'level down' % (to_fulfill, badgeclass)
                )

    badge_results = {
        'assertion': assertion,
        'badge_sqaaas_md': badge_sqaaas_md,
        'badge_shields_md': badge_shields_md,
        'to_fulfill': to_fulfill,
        'next_level_badge': next_level_badge
    }
    full_report_url = '/'.join([
        'https://sqaaas.eosc-synergy.eu/#/full-assessment/report',
        sqaaas_report_json['meta']['report_json_url']
    ])
    # Render & return report
    template = jinja2.Environment().from_string(SUMMARY_TEMPLATE)
    return template.render(
        report_results=report_results,
        badge_results=badge_results,
        report_url=full_report_url,
        links_to_standard=LINKS_TO_STANDARD
    )


def write_summary(sqaaas_report_json):
    summary = get_summary(sqaaas_report_json)
    if "GITHUB_STEP_SUMMARY" in os.environ:
        logger.info('Setting GITHUB_STEP_SUMMARY environment variable')
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f :
            print(summary, file=f)
            logger.info('Summary data added to GITHUB_STEP_SUMMARY')
    else:
        logger.warning('Cannot set GITHUB_STEP_SUMMARY')

    return summary


def get_repo_data():
    repo = os.environ.get('INPUT_REPO', None)
    branch = os.environ.get('INPUT_BRANCH', None)
    if not repo:
        repo = os.environ.get('GITHUB_REPOSITORY', None)
        if repo:
            repo = os.path.join('https://github.com', repo)
    if not branch:
        branch = os.environ.get('GITHUB_REF_NAME', None)

    return (repo, branch)


def main():
    repo, branch = get_repo_data()
    if not repo:
        logger.error(
            'Repository URL for the assessment not defined: cannot continue'
        )
        sys.exit(1)
    else:
        logger.info(
            'Trigger SQAaaS assessment with code repository: %s' % repo
        )

    sqaaas_report_json = run_assessment(repo=repo, branch=branch)
    if sqaaas_report_json:
        logger.info('SQAaaS assessment data obtained. Creating summary..')
        logger.debug(sqaaas_report_json)
        summary = write_summary(sqaaas_report_json)
        if summary:
            logger.debug(summary)
    else:
        logger.info('Could not get report data from SQAaaS platform')


if __name__ == "__main__":
    main()
