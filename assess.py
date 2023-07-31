import requests
import sys


COMPLETED_STATUS = ['SUCCESS', 'FAILURE', 'UNSTABLE', 'ABORTED']
SUCCESFUL_STATUS = ['SUCCESS', 'UNSTABLE']
# FIXME: add as CLI argument
ENDPOINT = "https://api-staging.sqaaas.eosc-synergy.eu/v1" 


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
        print(f'HTTP error occurred: {http_err}')
        _error_code = 101
    except Exception as err:
        print(f'Other error occurred: {err}')
        _error_code = 102
    else:
        print('Success!')
        return response
    if _error_code:
        sys.exit(_error_code)


def main():
    pipeline_id = '9449025c-f9d8-4235-a040-e9a2b2184713'
    action = 'status'
    
    keep_trying = True
    build_url, build_status = (None, None)
    sqaaas_report_json = {}
    while keep_trying:
        print(f'Checking {action} of pipeline {pipeline_id}')
        if action in ['status']:
            response = sqaaas_request('get', f'pipeline/{pipeline_id}/{action}')
            response_data = response.json()
            build_status = response_data['build_status']
            if build_status in COMPLETED_STATUS:
                # keep_trying = False
                action = 'output'
        elif action in ['output']:
            keep_trying = False
            response = sqaaas_request('get', f'pipeline/assessment/{pipeline_id}/{action}')
            sqaaas_report_json = response.json()

    print(sqaaas_report_json)


if __name__ == "__main__":
   main()
