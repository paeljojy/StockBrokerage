# Stock Brokerage Design Doc

## Application overview
Web application for stock brokerage who wants to do off market trades (Orders are matched outside of a stock exchange) for single stock -
APPLE (AAPL).

The web application interacts with end users through a REST API.

Web application should fetch latest market data of the stock from a feed in order to validate the price of the input orders.

## System Requirement
1. Web application should provide a REST end point for the end users to submit orders, An order consists of
    a. Whether its a Bid (buy) or an sell offer
        i.  Bid - User want’s to buy
        ii. Sell Offer - User want’s to sell

    b. Price - Up to two decimal places
        i. In case of a Bid - Max price the user is willing to pay per unit quantity
        ii. In case of an Offer - Min price the user is willing to get for the sale of unit quantity

    c. Quantity - Integer
        i. Amount of stock the user is willing to Buy or Sell

2. Any input order’s price should be validated against market data of AAPL’s last traded price

    a. To verify the brokerage execution prices are inline with actual trade prices
    b. Fetch last traded price from the third party API - Introduction | Market Data Docs
        i. Fetch last trade price ('last') of AAPL from endpoint - GET /v1/stocks/quotes/AAPL
    c. Respect the rate limitations mentioned here - Rate Limiting | Market Data Docs
        i. Configure the application to fetch the data hourly
    d. System should validate that at the input, Price of an order is within +- 10% of the last traded price

3. Input orders should be matched with existing orders on the other side
    a. If they match, system should record a trade, Trade should contain
        i. Traded time
        ii. Traded price (Highest value of the Bid and Offer prices)
        iii. Traded quantity (Min of Bid and Offer Quantity)

    b. If the input order does not match or only matches partially, then the remaining quantity should be stored in the system, Any upcoming
    order will match with these.

    c. If there are multiple orders in the system eligible for matching, then
        i. System should start according to order priority
            1. Bid order priority - Highest Price to Lowest price
            2. Offer order priority - Lowest price to Highest price
        ii. If there are multiple orders with the same priority / price, then System should start matching from the oldest order
    d. Refer example below

4. System should provide a REST end point to get the trade information, ordered in the trade time ascending order

## Expected Outcome
1. Develop the above system with CI setup
2. CI should be configured to provide:
    a. Unit test report including code coverage
    b. E2E testing for given scenarios - Refer scenarios below
    c. Automated Releases generation with:
        i. Change log
        ii. version number

## Additional items
1. Setup code quality testing in the CI and generate code quality report
2. Setup code security analysis (eg. Static Application Security Testing in GitLab - SA

// FIXME: add the actual examples 
### Examples of input orders and expected output
1. Initial order submission - Market last traded price - 190.00
    a. Input Bid of Qty: 1000, Price: 200.00 is stored in the system - Ord 1

2. Second order - Market last traded price - 200.00
    a. Input Bid of Qty: 500, Price: 210.00 - Ord 2

// FIXME: add the actual examples 
| Ord | Bid          | Offer price|
|-----|--------------|:----------:|
| 1   | 1000         |  200       |
| 2   | 500          |  210       |




