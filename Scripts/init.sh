#!/bin/bash

pushd "$(dirname "$0")/" > /dev/null

# Init database
./SetupSQLite.sh
# ./SetupMariaDB.sh

# Init frontend
npm install
npm update
# npm run dev
# npm run build

# Init backend
cd ../Server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

popd > /dev/null

