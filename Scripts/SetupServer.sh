#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# cd Server
# npm install 
# tsc
#
popd > /dev/null

