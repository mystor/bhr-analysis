#!/bin/bash

set -e
set -x

DATE=$1

S3USWEST=https://s3-us-west-2.amazonaws.com

URL=$S3USWEST/telemetry-public-analysis-2/collect-nightly-background-hang-report-native-stacks/data

if [ "$DATE" == '' ]; then
    DATE=`curl $URL/dates.json | python -c 'import json; import sys; print json.load(sys.stdin)[0]'`
fi

echo DATE = $DATE

S3PATH="bhr-data/v1/$DATE"
if curl -output /dev/null --silent --head --fail "$S3USWEST/$S3PATH/index.html"; then
    echo already finished
else
    if [ ! -d "out/$DATE" ]; then
        if [ ! -d "symbolicated-$DATE" ]; then
            if [ ! -f "dump-$DATE.json" ]; then
                wget "https://s3-us-west-2.amazonaws.com/telemetry-public-analysis-2/collect-nightly-background-hang-report-native-stacks/data/dump-$DATE.json"
            fi
            python symbolicate.py "$DATE"
        fi
        python mkjson.py "$DATE"
    fi
    python generate.py "$DATE"
    aws --region us-west-2 s3 cp out/$DATE s3://$S3PATH --recursive

    echo finished, cleaning up
    rm "dump-$DATE.json" || true
    rm -r "symbolicated-$DATE" || true
    rm -r "out/$DATE" || true
fi

echo "DONE"
