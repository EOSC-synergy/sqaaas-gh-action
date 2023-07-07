# SQAaaS docker action

This action triggers the quality assessment of a source code repository.

## Inputs

## `repo`

**Required** The URL of the repository to assess.

## `branch`

The branch to fetch from the previous repository name. If a branch is not provided, the SQAaaS platform takes the default one.

## Outputs

## `report`

JSON payload containing the full QA report.

## Example usage

uses: actions/sqaaas-docker-action@v1
with:
  repo: 'https://github.com/eosc-synergy/sqaaas-api-server'
  branch: 'master'
