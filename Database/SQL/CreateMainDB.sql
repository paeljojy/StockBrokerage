
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

-- Create user bids
CREATE TABLE bids (
	bid_id INTEGER NOT NULL,
	user INTEGER,
	CONSTRAINT bids_pk PRIMARY KEY (bid_id)
);

