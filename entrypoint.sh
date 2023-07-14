#!/bin/sh -l

REPO=$1
BRANCH=$2

PAYLOAD='{
  "repo_code": {
    "repo": "'$REPO'",
    "branch": "'$BRANCH'"
  },
  "repo_docs": {
    "repo": "",
    "branch": ""
  }
}'

API_ENDPOINT=https://api-staging.sqaaas.eosc-synergy.eu/v1
 
if [ -n "$BRANCH" ]; then
    BRANCH_MSG='using default branch'
else
    BRANCH_MSG="branch: $BRANCH"
fi 

echo "Triggering SQAaaS assessment for repository $REPO ($BRANCH_MSG)"
curl -X POST $API_ENDPOINT/pipeline/assessment --header '"Content-Type: application/json"' -d "$PAYLOAD"
# --header "Authorization: Bearer ${TOKEN}"

# echo "report={}" >> "$GITHUB_OUTPUT"
