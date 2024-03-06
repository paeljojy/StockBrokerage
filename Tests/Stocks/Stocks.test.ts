import { expect } from 'vitest'

import { getStocksFromServer } from '../../src/stocks/StocksAPI.ts'

/* import { getStocks } from '../../src/stocks/Stocks.ts' */
import { test } from 'vitest';

test('getStocks', async () => {
    /* console.log("hue"); */
    const data = await getStocksFromServer();

    // Check that the data is not null or undefined
    expect(data).not.toBeNull();
    expect(data).not.toBeUndefined();

    // If the data is an object, check that it's not empty
    if (typeof data === 'object' && data !== null) {
        expect(Object.keys(data).length).toBeGreaterThan(0);
    }
    console.log(data);
});
