#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

# docker build . --file docker/Dockerfile --tag stock_brokerage:$(date +%s)
docker build . --file docker/Dockerfile --tag stock_brokerage

popd > /dev/null
