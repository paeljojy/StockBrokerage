
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

let lastFetchTime: number | null = null;
let cachedData: any = null;

export async function getStocks(): Promise<any> {
    const currentTime = Date.now();

    // If we have cached data and it's less than an hour old, return it
    // INFO: 3600 * 1000ms = 1 hour
    if (cachedData && currentTime - (lastFetchTime as number) < 3600 * 1000) {
        return cachedData;
    }

    // Otherwise, fetch new data from REST API
    const res = await fetch('https://api.marketdata.app/v1/stocks/quotes/AAPL/');
    const data = await res.json();

    // Update the cache and the fetch time
    cachedData = data;
    lastFetchTime = currentTime;

    /* console.log(data); */
    return data;
}


