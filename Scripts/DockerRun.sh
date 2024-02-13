#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

# docker container kill stock_brokerage:latest
docker run -p 5173:5173 stock_brokerage:latest

popd > /dev/null

