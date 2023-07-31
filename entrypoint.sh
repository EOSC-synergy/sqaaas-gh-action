#!/bin/sh -l

repo=$1
branch=$2

report=$(python assess.py $repo $branch)

echo "report=$report" >> "$GITHUB_OUTPUT"
