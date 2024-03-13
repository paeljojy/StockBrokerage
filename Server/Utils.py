# INFO: This file contains static utility functions
import sqlite3
import requests
from datetime import datetime
from StockModules import Stock

# NOTE: This should only be called when an connection to the database is already established
# and connection should be closed after this call MANUALLY
def query_next_id_for_table(table):
    # Query the database for the next available bid id
    conn = sqlite3.connect('Database/Main.db')
    cursor = None
    if table == "bids":
        # INFO: This is used to add new bids to the database, as the user can have multiple bids
        cursor = conn.execute("SELECT MAX(id) FROM bids")
    elif table == "offers":
        cursor = conn.execute("SELECT MAX(id) FROM offers")

    # Determine the next id to be used as an bid id (row id)
    last_id = cursor.fetchone()[0]
    print("Last id: ", last_id)
    next_id = 1 if last_id is None else last_id + 1
    print("Next id: ", next_id)

    # NOTE: We don't close the connection here, as the caller should close the connection

    return next_id

def resolve_cached_data(stock_id):
    # 1. Fetch stock data from data base
    # 2. If doesn't exists, insert 
    # 3. Check fetched time is < 3600
    # 4. If not, fetch and update in the database
    # 5. Return up to date Stock object

    conn = sqlite3.connect('Database/Main.db')
    cursor = conn.execute("SELECT * FROM stocks WHERE id = ?", (stock_id, ))
    stock_list = []
    for row in cursor:
        stock_list.append(row)
    
    if len(stock_list) < 1:
        time = datetime.now()
        res = requests.get('https://api.marketdata.app/v1/stocks/quotes/AAPL/')
        data = res.json()
        name = str(data['symbol'][0])
        price = float(data['last'][0])
        cursor = conn.execute("INSERT INTO stocks (id, name, current_price, fetched_at) VALUES (?, ?, ?, ?)", (stock_id, name, price, time))
        conn.commit()
        cursor.close()
        conn.close()
        return Stock(stock_id, name, price, str(time))

    stock_time = datetime.strptime(str(stock_list[0][3]), '%Y-%m-%d %H:%M:%S.%f')
    time = stock_time
    price = float(stock_list[0][2])
    current_time = datetime.now()
    
    if (current_time - stock_time).total_seconds() > 3600:
        time = current_time
        res = requests.get('https://api.marketdata.app/v1/stocks/quotes/AAPL/')
        data = res.json()
        price = float(data['last'][0])
        cursor = conn.execute("UPDATE stocks SET current_price = ?, fetched_at = ? WHERE id = ?", (price, time, stock_id))
        conn.commit()
        
    cursor.close()
    conn.close()
    return Stock(stock_id, str(stock_list[0][1]), price, str(time))

