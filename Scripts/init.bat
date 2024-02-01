@echo off

pushd %~dp0

npm install
npm update
npm run dev
@REM npm run build

popd

