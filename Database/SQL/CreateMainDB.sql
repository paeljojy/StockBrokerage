-- Drop table if it exists
DROP TABLE IF EXISTS users;

-- Create the user table
CREATE TABLE users (
	sub TEXT NOT NULL,
	email TEXT,
	CONSTRAINT users_pk PRIMARY KEY (sub)
);

-- Drop table if it exists
DROP TABLE IF EXISTS bids;

-- Create user bids (buy offers)
CREATE TABLE bids (
	id INTEGER NOT NULL,
	user_id TEXT,
	CONSTRAINT bids_pk PRIMARY KEY (bid_id)
);

-- Create user sell offers  
CREATE TABLE bids (
	id INTEGER NOT NULL,
	user_id TEXT NOT NULL,
	CONSTRAINT bids_pk PRIMARY KEY (bid_id)
);

-- Create stocks table for currently tradeable stocks
CREATE TABLE stocks (
    id INTEGER NOT NULL,
    name TEXT NOT NULL,
    current_price REAL NOT NULL,
    CONSTRAINT stocks_pk PRIMARY KEY (stock_id)
);


