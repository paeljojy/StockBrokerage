#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

# NOTE: This is deprecated! 
# use BuildAndLaunchServer.sh and SetupServer.sh instead

cd Server
rm Server.js
tsc -p Server.ts
node Server.js

popd > /dev/null

