#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

cd Server
tsc
cd ..
node Server/dist/Server.js

popd > /dev/null

