#!/bin/bash

set -e
set -x

DATE=$1

echo DATE = $DATE

wget "https://s3-us-west-2.amazonaws.com/telemetry-public-analysis-2/collect-nightly-background-hang-report-native-stacks/data/dump-$DATE.json"
python symbolicate.py "$DATE"
python generate.py "$DATE"

echo "DONE"
