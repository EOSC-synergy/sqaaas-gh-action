<!--
SPDX-FileCopyrightText: Copyright contributors to the Software Quality Assurance as a Service (SQAaaS) project.

SPDX-License-Identifier: GPL-3.0-only
-->

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
```yaml
uses: actions/sqaaas-docker-action@v1
with:
  repo: 'https://github.com/eosc-synergy/sqaaas-api-server'
  branch: 'master'
```

## Report summary

This action provides a summary of the SQAaaS assessment report, as well as the link to the complete version of it:
![GH action's summary report](./imgs/summary_report.png)
