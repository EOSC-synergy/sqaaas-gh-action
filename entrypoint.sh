#!/bin/sh -l

repo=$1
branch=$2

if [ -n "$branch" ]; then
    branch_msg = 'using default branch'
else
    branch_msg = 'branch: $branch'
fi 

echo "Triggering SQAaaS assessment for repository $repo ($branch_msg)"

echo "{}" | python3 -m json.tool >> $GITHUB_OUTPUT
