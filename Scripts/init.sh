#!/bin/bash

pushd `dirname $0` > /dev/null

npm install
npm update
npm run build

popd > /dev/null


