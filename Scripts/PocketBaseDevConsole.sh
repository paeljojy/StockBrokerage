#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

# Launch pocketBase backend
./Tools/pocketbase serve

# INFO: you can open the browser and navigate to http://localhost:8090/_/ to see the pocketBase backend console

popd > /dev/null 2>&1

