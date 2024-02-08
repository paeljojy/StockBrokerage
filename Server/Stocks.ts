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
