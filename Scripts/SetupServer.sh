#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

cd Server
npm install 
tsc

popd > /dev/null

