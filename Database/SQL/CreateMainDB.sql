-- INFO: We drop tables if they exist to avoid errors when creating the tables
-- CAUTION: This will delete all data in the tables when you init the sqlite database

DROP TABLE IF EXISTS users;

-- Create the user table
CREATE TABLE users (
	sub TEXT NOT NULL,
	email TEXT,
    first_name TEXT,
    last_name TEXT,
	CONSTRAINT users_pk PRIMARY KEY (sub)
);

DROP TABLE IF EXISTS offers;

-- TODO: Create user sell offers  
CREATE TABLE offers(
	id INTEGER NOT NULL,
	user_id TEXT,
	CONSTRAINT offers_pk PRIMARY KEY (id)
);

DROP TABLE IF EXISTS bids;

-- Create user bids (buy offers)
CREATE TABLE bids(
	id INTEGER NOT NULL,
	user_id TEXT NOT NULL,
	stock_id INTEGER NOT NULL,
	amount INTEGER NOT NULL,
	price REAL NOT NULL,
    -- TODO: Might not need to have user_id and stock_id as part of the primary key
    --we could just increment bid id
	CONSTRAINT bids_pk PRIMARY KEY (id, user_id, stock_id)
);

DROP TABLE IF EXISTS stocks;

-- Create stocks table for currently tradeable stocks
CREATE TABLE stocks(
    id INTEGER NOT NULL,
    name TEXT NOT NULL,
    current_price REAL NOT NULL,
    -- TODO: Add rest of the fields found in the REST API
    CONSTRAINT stocks_pk PRIMARY KEY (id, name) -- INFO: We don't want to have two stocks with the same name
);

-- Insert Apple stock for testing
INSERT INTO stocks (id, name, current_price) VALUES (1, 'Apple, Inc', 1337.00);

DROP TABLE IF EXISTS user_owned_stocks;

-- Create user owned stocks
CREATE TABLE user_owned_stocks(
    user_id TEXT NOT NULL,
    stock_id TEXT NOT NULL,
    amount INTEGER NOT NULL,
    CONSTRAINT user_owned_stock_pk PRIMARY KEY (user_id, stock_id)
);

DROP TABLE IF EXISTS trades;

-- Create trades INFO: trade is a transaction between two users
CREATE TABLE trades(
    buyer_user_id TEXT NOT NULL,
    seller_user_id TEXT NOT NULL,
    stock_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    price INTEGER NOT NULL,
    time DATETIME NOT NULL,
    CONSTRAINT user_owned_stock_pk PRIMARY KEY (buyer_user_id, seller_user_id, time)
);

