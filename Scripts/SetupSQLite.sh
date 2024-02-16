#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

sqlite3 Database/Main.db < Database/SQL/CreateMainDB.sql

# Insert some sample data into main db
sqlite3 -line Database/Main.db "INSERT INTO users (sub, email) VALUES ('2', 'teppo@gmail.com');"

echo "Users: "
sqlite3 -line Database/Main.db "SELECT * FROM users;"

popd > /dev/null


