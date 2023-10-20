#!/bin/sh -l

# SPDX-FileCopyrightText: Copyright contributors to the Software Quality Assurance as a Service (SQAaaS) project.
#
# SPDX-License-Identifier: GPL-3.0-only

repo=$1
branch=$2

# report_url=$(python assess.py $repo $branch | /usr/bin/jq -r '.meta.report_json_url')
# echo "@@@@ report_url: $report_url @@@@"

# echo "### SQAaaS summary :clipboard:" >> $GITHUB_STEP_SUMMARY
# echo "" >> $GITHUB_STEP_SUMMARY
# echo "- Quality assessment report (JSON): $report_url" >> $GITHUB_STEP_SUMMARY

python /usr/bin/assess.py $repo $branch
