#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

# INFO: This script is used to setup the SQLite database for the project.
# CAUTION: This script will delete the existing database (including data) 
# and create a new one.
sqlite3 Database/Main.db < Database/SQL/CreateMainDB.sql

# Insert some sample data into main db
sqlite3 -line Database/Main.db "INSERT INTO users (sub, email, first_name, last_name) VALUES ('2', 'teppo@gmail.com', 'Teppo', 'Testi');"

# sqlite3 -line Database/Main.db "INSERT INTO bids (id, user_id, stock_id, amount, price, date) VALUES (1, '1', '1', 30, 30, '2024-03-11 19:19:54.359319');"

# Add some user owned stocks for user

# Owns 69 stocks
sqlite3 -line Database/Main.db "INSERT INTO user_owned_stocks (user_id, stock_id, amount) VALUES ('115529453441494604337', 1, 69);"

# Bids two stocks for 160 each
# sqlite3 -line Database/Main.db "INSERT INTO bids (id, user_id, stock_id, amount, price) VALUES (2, '115529453441494604337', 1, 2, 160);"

# Owns 2 stocks
sqlite3 -line Database/Main.db "INSERT INTO user_owned_stocks (user_id, stock_id, amount) VALUES ('104294035584677999327', 1, 2);"

# User 2 sells 2 stocks
# sqlite3 -line Database/Main.db "INSERT INTO offers (id, user_id, stock_id, amount, price, date) VALUES (1, '104294035584677999327', 1, 2, 160, '2024-03-11 19:19:54.359319');"

# Trade between two users (user 1 buys 2 stocks from user 2)
# sqlite3 -line Database/Main.db "INSERT INTO trades (buyer_user_id, seller_user_id, stock_id, amount, price, time) VALUES ('115529453441494604337', '104294035584677999327', 1, 30, 200, '0');"

echo "=============================================="
echo "Users: "
sqlite3 -line Database/Main.db "SELECT * FROM users;"
echo "=============================================="

echo "Stocks: "
sqlite3 -line Database/Main.db "SELECT * FROM stocks;"
echo "=============================================="

echo "Bids: "
sqlite3 -line Database/Main.db "SELECT * FROM bids;"
echo "=============================================="

echo "Offers: "
sqlite3 -line Database/Main.db "SELECT * FROM offers;"
echo "=============================================="

echo "Trades: "
sqlite3 -line Database/Main.db "SELECT * FROM trades;"
echo "=============================================="

echo "User owned stocks: "
sqlite3 -line Database/Main.db "SELECT * FROM user_owned_stocks;"
echo "=============================================="

popd > /dev/null


