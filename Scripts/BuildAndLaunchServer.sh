#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

# cd Server
# tsc
# cd ..
# node Server/dist/Server.js

source Server/venv/bin/activate
flask --app Server/Server run

popd > /dev/null

