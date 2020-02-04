#!/usr/bin/env bash

cat ${1} | python -c "import sys, json; json.load(sys.stdin)['data']['__schema']" > /dev/null 2>&1

if [[ $? -eq 0 ]]; then
    exit 0
else
    echo "You must have a valid graphql.json file. If you only have SDL, you may use the convert.js script, which requires node."
    exit 1
fi
