#!/bin/bash

# docker build . --file docker/Dockerfile --tag stock_brokerage:$(date +%s)
docker build . --file docker/Dockerfile --tag stock_brokerage

