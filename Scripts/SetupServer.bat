@echo off

pushd %~dp0..

cd Server
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

popd


