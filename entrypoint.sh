#!/bin/sh -l

repo=$1
branch=$2

code_payload=$(jq --null-input \
	           --arg repo "$repo" \
	           --arg branch "$branch" \
		   '{"repo": $repo, "branch": $branch}')
request_payload=$(jq --null-input \
	             --argjson repo_code "$code_payload" \
	             '{$repo_code}')

api_endpoint=https://api-staging.sqaaas.eosc-synergy.eu/v1

if [ -n "$branch" ]; then
    branch_msg='using default branch'
else
    branch_msg="branch: $branch"
fi 
echo "Triggering SQAaaS assessment for repository $repo ($branch_msg)"

# --header "Authorization: Bearer ${token}"
id=$(curl -X POST $api_endpoint/pipeline/assessment --header '"Content-Type: application/json"' -d "$request_payload" | jq -r '.id')
echo "Assessment submitted with ID: $id"

run_output=$(curl -X POST $api_endpoint/pipeline/$id/run --header '"Content-Type: application/json"')

status_output=$(curl -X GET $api_endpoint/pipeline/$id/status --header '"Content-Type: application/json"' | jq -r '.build_status')
echo $status_output

# echo "report={}" >> "$GITHUB_OUTPUT"
