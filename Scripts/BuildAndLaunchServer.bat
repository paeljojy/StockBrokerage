@echo off

pushd "%~dp0.."

@REM cd Server
@REM tsc
@REM cd ..
@REM node Server/dist/Server.js

call Server\venv\Scripts\activate.bat
flask --app Server\Server.py run

popd 

