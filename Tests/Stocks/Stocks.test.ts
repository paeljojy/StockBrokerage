import { expect } from 'vitest'
import { test } from 'vitest';

// Import our frontend StocksAPI functions
import { getStocksFromServer } from '../../src/stocks/StocksAPI.ts'
import { getTradesFromServer } from '../../src/stocks/StocksAPI.ts'

test('getStocks', async () => {
    // Login info NOTE: This is provided by the Google Auth API
    const login = {
        sub: '115529453441494604337',
        email: 'paeljojy@jyu.student.fi'
    };

    // Query the data from the server
    const data = await getStocksFromServer(login);

    // Check that the data is not null or undefined
    expect(data).not.toBeNull();
    expect(data).not.toBeUndefined();

    // If the data is an object, check that it's not empty
    if (typeof data === 'object' && data !== null) {
        expect(Object.keys(data).length).toBeGreaterThan(0);
    }

    // Log the data to the console
    console.log(data);
});

