
/* --Drop table if it exists */
/* DROP TABLE IF EXISTS users; */
/**/
/* --Create the user table */
/* CREATE TABLE users( */
/* sub INTEGER NOT NULL, */
/* email TEXT, */
/* CONSTRAINT users_pk PRIMARY KEY(sub) */
/* ); */
/**/
/* --Drop table if it exists */
/* DROP TABLE IF EXISTS bids; */
/**/
/* --Create user bids */
/* CREATE TABLE bids( */
/* bid_id INTEGER NOT NULL, */
/* "user" INTEGER, */
/* CONSTRAINT bids_pk PRIMARY KEY(bid_id) */
/* );`, (_, res) => console.log(res) */

/* export async function getDB(): Promise<any> { */
/*     const db = new Database('Database/Main.db'); */
/*         db.get(`SELECT RANDOM() % 100 as result;`, (_, res) => console.log(res) */
/*     ); */
/*     return db; */
/* } */

/* import mariadb from 'mariadb'; */

export async function getDB(): Promise<any> {
    console.log("getDB() called on frontend!");
    const data = fetch('http://127.0.0.1:5000/getdb')
        /* fetch('http://localhost:3000/') */
        .then(response => response.json())
        .then(data => console.log(data));
    return data;
}

export async function getStocksFromServer(): Promise<any> {
    console.log("getStocks() called on frontend!");
    const data = fetch('http://localhost:3000/api/stocks/apple')
        .then(response => response.json())
        .then(data => console.log(data));
    return data;
}


