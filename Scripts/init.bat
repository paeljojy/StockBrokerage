@echo off

pushd %~dp0

npm install
npm update
npm run build

popd

