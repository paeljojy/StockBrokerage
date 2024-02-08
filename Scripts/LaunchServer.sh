#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

cd Server
rm Server.js
tsc -p Server.ts
node Server.js

popd > /dev/null

