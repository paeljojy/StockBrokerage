import Link from 'next/link';
import styles from './Stock.module.css';

async function getStocks() {
    /* const res = await fetch('http://localhost:3000/api/stock'); */
    // GET /v1/stocks/quotes/AAPL
    // TODO: move stock id to argument 
    const stockID = 'AAPL';
    /* const res = await fetch('https://api.marketdata.app/v1/stocks/quotes/${stockID}/}', */
    // TODO: configure this to be fetched hourly as stated in the docs
    const res = await fetch('https://api.marketdata.app/v1/stocks/quotes/AAPL/');
    // TODO: do we need an account?
    // we get:
    // {
    //   s: 'error',
    //   errmsg: 'Invalid token header. No credentials provided.'
    // }

    /* const res = await fetch('https://api.marketdata.app/v1/stocks/quotes/AAPL/}', */
    /*     { */
    // TODO: this is in seconds so just make it an hour to align with the docs
    /*         next : { revalidate: 10 }, */
    /*     } */
    /* ); */

    const json = await res.json();
    /* return json; */
    /* return data?.items as any[]; */
    return json;
}

export default async function StockPage() {
    const stock = await getStocks();

    // Debug
    console.log(stock);

    return (
        <div>
            {/* <div className={styles.grid}> */}
            <div className={styles.stock}>
                <h1>Apple Stock</h1>
                <p>Symbol: {stock.symbol}</p>
                <p>Ask: $ {stock.ask}</p>
                <p>Ask Size: {stock.askSize}</p>
                <p>Bid: $ {stock.bid}</p>
                <p>Bid Size: {stock.bidSize}</p>
                <p>Mid: $ {stock.mid}</p>
                <p>Last: $ {stock.last}</p>
                <p>Change: $ {stock.change}</p>
                <p>Change Percentage: {stock.changepct}%</p>
                <p>Volume: {stock.volume}</p>
                <p>Updated: {new Date(stock.updated * 1000).toLocaleString()}</p>
            </div>
            <div className={styles.stockInput}>
                <h1>Sell stock</h1>
                <input type="text" placeholder="Amount" />
            </div>
            <div className={styles.stockInput}>
                <h1>Bid stock</h1>
                <input type="text" placeholder="Amount" />
            </div>

        </div>
    );
}

function Stock({ stock }: any) {
    const { } = stock || {};

    if (!stock) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>Apple Stock</h1>
            <p>Symbol: {stock.symbol}</p>
            <p>Ask: {stock.ask}</p>
            <p>Ask Size: {stock.askSize}</p>
            <p>Bid: {stock.bid}</p>
            <p>Bid Size: {stock.bidSize}</p>
            <p>Mid: {stock.mid}</p>
            <p>Last: {stock.last}</p>
            <p>Change: {stock.change}</p>
            <p>Change Percentage: {stock.changepct}</p>
            <p>Volume: {stock.volume}</p>
            <p>Updated: {new Date(stock.updated * 1000).toLocaleString()}</p>
        </div>
    );

    /* return ( */
    /*     <Link href={`/stock/${id}`}> */
    /*     <div> */
    /*         <h2>{title}</h2> */
    /*         <p>{content}</p> */
    /*         <p>{created}</p> */
    /*     </div> */
    /*     </Link> */
    /* ); */
}
