#!/bin/bash

pushd "$(dirname "$0")/.." > /dev/null

# Install MariaDB
# sudo pacman -S mariadb

# Ensure MariaDB is running with systemd
# sudo systemctl enable mariadb.service

# if systemctl --quiet is-active "mariadb.service"
# then
#     echo "MariaDB Service is running"
# else
#     echo "MariaDB Service is not running"
#     sudo systemctl start mariadb.service
# fi

# INFO: Use to grant all privileges to the root user on mariadb
# grant all on *.* to 'root'@'localhost' identified by 'my_password' with grant option;

sudo mariadb -u root -p "" -e "CREATE DATABASE IF NOT EXISTS stock_brokerage;"

sudo mariadb -u root -p stock_brokerage < Database/SQL/CreateMainDB.sql

# INFO: Use to check the databases
# show databases;

# INFO: Use to show tables
# show tables;

# INFO:Create a database
# create database stock_brokerage;

popd > /dev/null

