#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

# INFO: This script is used to setup the SQLite database for the project.
# CAUTION: This script will delete the existing database (including data) 
# and create a new one.
sqlite3 Database/Main.db < Database/SQL/CreateMainDB.sql

# Insert some sample data into main db
sqlite3 -line Database/Main.db "INSERT INTO users (sub, email) VALUES ('2', 'teppo@gmail.com');"

sqlite3 -line Database/Main.db "INSERT INTO bids (id, user_id, stock_id, amount, price) VALUES (1, '1', '1', 30, 30);"

echo "Users: "
sqlite3 -line Database/Main.db "SELECT * FROM users;"
echo "=============================================="

echo "Stocks: "
sqlite3 -line Database/Main.db "SELECT * FROM stocks;"
echo "=============================================="

echo "Bids: "
sqlite3 -line Database/Main.db "SELECT * FROM bids;"
echo "=============================================="

echo "Trades: "
sqlite3 -line Database/Main.db "SELECT * FROM trades;"
echo "=============================================="

popd > /dev/null


