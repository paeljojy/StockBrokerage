from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import requests
import time
import os
from enum import Enum

# print("CWD IS: ", os.getcwd())

# NOTE: Response object is a wrapper for the response data that is sent to the client
# It contains the status code of the response, the message and the actual data
# The status code is used to determine if the request was successful or not
# based on situation specific criteria this can be anything you want
# and the method using a response object should clearly indicate what each status code means
# for example: 0 = success, 1 = error etc.
# NOTE: Be careful when refactoring status codes, as the client and the server
# have to both match the status code logic to work properly
#
# INFO: You can use enums to make this more readable
# enum StatusCode { Success = 0, Error = 1, Unauthorized = 2, Unknown = 3, } etc...

class Response:
    status = -1
    message = ''
    data = None

    def __init__(self, status = -1, message = '', data = None):
        self.status = status
        self.message = message
        self.data = data 

    def get_status(self):
        return self.status

    def get_message(self):
        return self.message

    def get_data(self):
        # Make the object into a dictionary for JSON conversion
        return self.__dict__

    # Jsonify the response object to be sent to the client
    def jsonify(self):
        return jsonify(self.__dict__)

class Stock:
    id = -1
    name = ""
    price = -1
    fetched_time = None

    def __init__(self, id = -1, name = '', price = -1, fetched_time = 0):
        self.id = id
        self.name = name
        self.price = price
        self.fetched_time = fetched_time

    def __hash__(self):
        return hash((self.id, self.name))

    def __eq__(self, other):
        return (self.id, self.name) == (other.id, other.name)

    def is_valid(self):
        return self.id != -1

# INFO: Manages stock trades, bids and sell offers
# it can be used to add, remove, update and get trades
# Consider this as a singleton
# Implementation:
# We start by matching bids with sell offers by the highest offer price and the lowest bid price
# (Similar to how RuneScape's Grand Exchange works)
# given that the trades are always made when a new offer or bid is added
# the system will always be up to date unless the stock market price changes
# when the stock market price changes we update the whole system and match bids with sell offers
class StockTradeManager:
    trades = []     # Already made trades

    # Both of these shouldn't store bids or selloffers that could be matched
    # unless the stock price has just changed, that's why we keep track of them on the server
    bids = []       # Bids that are waiting to be matched with sell offers
    sell_offers = [] # Sell offers that are waiting to be matched with bids
    # current_stock = None # The current stock price of the current stock that is being traded NOTE: this should be set to the price of the stock that is being traded before update is called
    current_stock = -1.0 # The current stock price of the current stock that is being traded NOTE: this should be set to the price of the stock that is being traded before update is called

    def __init__(self):
        self.trades = {}
        self.bids = {}
        self.sell_offers = {}

        # Query the database for the current stock price
        conn = sqlite3.connect('Database/Main.db')
        # Fetch apple stock price
        cursor = conn.execute("SELECT * FROM stocks")
        # stock = cursor.fetchone()[0]

        # TODO: Use a stock object atm we just the stock price float 
        stocks = []
        for row in cursor:
            stocks.append(row)
        stock = stocks[0]
        # self.current_stock = Stock(stock[0], stock[1], stock[2], stock[3])

        # TODO: Get the current stock price from the REST API if the time since the last fetch is greater than 1 hour etc.

        # if (self.current_stock == Stock()):
        #     print("ERROR: Failed to fetch the current stock price from the database!")
        self.current_stock = stock[2]

        # Query the database for bids
        cursor = conn.execute("SELECT * FROM BIDS")
        bids = []
        for row in cursor:
            bids.append(row)
        cursor.close()

        for bid in bids:
            self.bids[bid[0]] = Order(bid[0], bid[1], bid[2], bid[3], bid[4])

        # Query the database for sell offers
        cursor = conn.execute("SELECT * FROM OFFERS")
        sell_offers = []
        for row in cursor:
            sell_offers.append(row)

        for sell_offer in sell_offers:
            self.sell_offers[sell_offer[0]] = Order(sell_offer[0], sell_offer[1], sell_offer[2], sell_offer[3], sell_offer[4])

        # Query the database for trades
        cursor = conn.execute("SELECT * FROM TRADES")
        trades = []
        for row in cursor:
            trades.append(row)

        for trade in trades:
            self.trades[trade[0]] = Order(trade[0], trade[1], trade[2], trade[3], trade[4], trade[5])
        
        # Clean up
        cursor.close()
        conn.close()

    # Adds a new trade to the trades list
    # NOTE: This is called when a bid is matched with a sell offer with a valid price
    # and a transaction has been made
    def add_trade(self, bid, sellOffer, time):
        # TODO: Insert into database

        conn = sqlite3.connect('Database/Main.db')
        cursor = conn.execute("INSERT INTO TRADES (buyer_user_id, seller_user_id, stock_id, amount, price, time) VALUES (?, ?, ?, ?, ?)", (bid.user_id, sellOffer.sellers_user_id, bid.stock_id, bid.amount, bid.price, time))

        try:
            conn.commit()
        except:
            print("ERROR: Failed to add trade to the database!")
        finally:
            cursor.close()
            conn.close()

    # Adds a new sell offer and updates
    def add_offer(self, newOffer):
        self.sell_offers.append(newOffer)
        self.update()

    # Adds a new bid and updates
    def add_bid(self, newBid):
        self.bids.append(newBid)
        self.update()

    # General update that is used whenever a new stock price is fetched 
    # and when bids or sell offers are added 
    # This will update the whole system and match bids with sell offers if possible
    # based on the newest stock market price
    def update(self):
        for bid in self.bids:
            for sell_offer in self.sell_offers:
                # Early exit if the bid and sell offer user_id is the same (user would be buying from themselves)
                if sell_offer.user_id == bid.user_id:
                    continue

                # TODO: (Pate 󰯈 ) Check against the market price that this is not more than ±10% of the market price
                # Match the bid with the sell offer
                if bid.price >= sell_offer.price:
                    # TODO: (Pate 󰯈 ) We should split the sell offer if the amount is greater than the bid amount here

                    # NOTE: We have a chance to duplicate a stock here if the server would crash during this
                    # TODO: Make this transactional
                    conn = sqlite3.connect('Database/Main.db')
                    # Remove the bid and the sell offer from the lists
                    # cursor = conn.execute("DELETE FROM bids WHERE id = ?", (bid.id))
                    cursor = conn.execute("DELETE FROM bids WHERE id = ?", (bid.id))
                    try:
                        conn.commit()
                    except:
                        pass

                    finally:
                        cursor.close()
                        conn.close()

                    # Get time for the trade
                    time = datetime.now()

                    self.add_trade(bid, sell_offer, time)

                    # Add a new trade to the trades list
                    # TODO: We should split the sell offer if the amount is greater than the bid amount

                    # conn.commit()

class User:
    # NOTE: User is not valid if the id is -1
    # also if your subs are really small integers you might have a problem
    id = -1
    first_name = ""
    last_name = ""
    email = ""

    def __init__(self, id = -1, first_name = "", last_name = "", email = ""):
        self.id = int(id)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def __hash__(self):
        return hash((self.id, self.email))

    def __eq__(self, other):
        return (self.id, self.email) == (other.id, other.email)

    def is_valid(self):
        return self.id != -1

class Order:
    user = User()
    id = -1
    stock_id = -1
    amount = -1
    price = -1
    order_type = 0 # 0 = bid, 1 = sell offer

    # NOTE: We query the database for the next available id and use it as the id of the bid
    def __init__(self, id, user, stock_id, amount, price, order_type = 0): # NOTE: By default we init a bid 1 for sell offer
        self.id = id         # NOTE: this is id of the bid, NOT THE USER
        self.user = user     # Actual user object
        self.stock_id = stock_id

        self.amount = amount
        self.price = price

class SellOffer:
    def __init__(self, id, user):
        self.id = id
        self.user = user

class Server():
    cached_data = None
    last_fetch_time = None
    logged_in_users = {}
    stock_trade_manager = StockTradeManager()

    def __init__(self):
        self.cached_data = None

        # Init empty 
        self.logged_in_users = {}

        # NOTE: Initialization process:
        # 1. Fetch the stock data from the REST API
        # and store it in the cache
        # 2. Fetch logged in users
        # 3. Fetch the trades from the database
        # 4. Fetch the bids from the database
        # 5. Fetch the sell offers from the database

        # TODO: 1. Fetch the stock data from the REST API

        # 2. Fetch logged in users
        conn = sqlite3.connect('Database/Main.db')
        # cursor = conn.execute("SELECT * FROM logged_in_users WHERE logged_in = 1")
        # NOTE: sub is the user id
        cursor = conn.execute("SELECT sub, first_name, last_name, email FROM users WHERE sub IN (SELECT sub FROM logged_in_users WHERE logged_in = 1);")

        # SELECT name FROM users WHERE user_id IN (SELECT user_id FROM logged_in_users);

        logged_in_users = []
        for row in cursor:
            logged_in_users.append(row)

        # NOTE: This is a tuple so elements are accesses with [0] [1] etc...
        for user in logged_in_users:
            #  NOTE: in order: user.id, user.first_name, user.last_name, user.email (look into sql query to see the order)
            self.logged_in_users[int(user[0])] = User(user[0], user[1], user[2], user[3])

        # Init the stock trade manager NOTE: This will fetch the current stock trader state from the database
        self.stock_trade_manager = StockTradeManager()

        # Clean up
        cursor.close()
        conn.close()

    def get_user_by_id(self, id):
        if id in self.logged_in_users:
            return self.logged_in_users[id]
        return User()  # Return None if no user with the given id is found

    def get_cached_data(self):
        return self.cached_data

    @staticmethod
    # NOTE: This should only be called when an connection to the database is already established
    # and connection should be closed after this call MANUALLY
    def query_next_bid_id():
        # Query the database for the next available bid id
        # INFO: This is used to add new bids to the database, as the user can have multiple bids
        conn = sqlite3.connect('Database/Main.db')
        cursor = conn.execute("SELECT MAX(id) FROM bids")

        # Determine the next id to be used as an bid id (row id)
        last_id = cursor.fetchone()[0]
        print("Last id: ", last_id)
        next_id = 1 if last_id is None else last_id + 1
        print("Next id: ", next_id)

        # NOTE: We don't close the connection here, as the caller should close the connection

        return next_id

# Initialize the server
server = Server()

##############################################################################################################
## FLASK API Under this TODO: Move this into a separate file
##############################################################################################################

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

def resolve_cached_data(server):
    data = server.get_cached_data()
    server.current_time = datetime.now()

    # If we have cached data and it's less than an hour old, return it
    # INFO: 3600s = 1 hour
    if server.cached_data is not None and (server.current_time - server.last_fetch_time).total_seconds() < 3600:
        return server.cached_data

    # Otherwise, fetch new data from REST API
    res = requests.get('https://api.marketdata.app/v1/stocks/quotes/AAPL/')
    data = res.json()

    # Update the cache and the fetch time
    server.cached_data = data
    server.last_fetch_time = server.current_time

    return jsonify(data)

@app.route('/api/stocks/apple', methods=['POST'])
def get_stocks():
    data = resolve_cached_data(server)
    return Response(0, "Fetch success: Successfully fetched stock data from the server!", data).jsonify()

# INFO: Rest api for getting all the made trades
@app.route('/api/stocks/public/trades')
def get_trades():
    conn = sqlite3.connect('Database/Main.db')
    cursor = conn.execute("SELECT * FROM trades")
    trades = []
    for row in cursor:
        trades.append(row)
    cursor.close()
    conn.close()
    return jsonify(trades)

@app.route('/api/getdb')
def get_db():
    conn = sqlite3.connect('Database/Main.db')
    cursor = conn.execute("SELECT * FROM USERS")
    list = []
    for row in cursor:
        list.append(row)
    cursor.close()
    conn.close()
    return jsonify(list)

# INFO: Handles log in requests from clients
# StatusCodes: 
# 0 = success
# 1 = error
@app.route('/api/auth/login', methods=['POST'])
def handle_login_request():

    userEmail = request.form.get("email", "")
    userSub = request.form.get("sub", "")
    first_name = request.form.get("first_name", "")
    last_name = request.form.get("last_name", "")

    if userSub == 'undefined':
        return Response(0, "Login success: user is already logged in!").jsonify()

    # Convert user sub string to int and back to string to remove possible sql injection
    userSubNumber = int(userSub)
    userSub = str(userSubNumber)

    print("Received email:" + userEmail)
    print("Received sub:" + userSub)

    # Check if user is already logged in
    if userSubNumber == server.get_user_by_id(userSubNumber).id:
        return Response(0, "Login success: user is already logged in!").jsonify()

    conn = sqlite3.connect('Database/Main.db')

    # Make prepared statement instead
    cursor = conn.execute("SELECT * FROM USERS WHERE sub = ?", (userSub,))
    conn.commit()

    list = []
    for row in cursor:
        list.append(row)

    if len(list) == 0:
        try:
            cursor_insert = conn.execute("INSERT INTO USERS (sub, email, first_name, last_name) VALUES (?, ?, ?, ?)", (userSub, userEmail, first_name, last_name))
            conn.commit()

            # Add the user to the logged in users
            time = datetime.now() # Get the current time for the logged in time
            cursor_insert = conn.execute("INSERT INTO logged_in_users (sub, logged_in, logged_in_at) VALUES (?, ?, ?)", (userSub, 1, time))
            conn.commit()

            cursor_insert.close()

            server.logged_in_users[userSubNumber] = (User(userSubNumber, userEmail))
            return Response(0, "Login success: new user!").jsonify()
            # return jsonify("success_newUser, login success: new user!")

        except:
            print("error_newUser, login failed: new user error! database doesn't most likely exists on disk")
            return Response(1, "Login failed: new user error!").jsonify()
            # return jsonify("error_newUser, login failed: new user error!")
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.close()
        conn.close()

    server.logged_in_users[userSubNumber] = User(userSubNumber, userEmail)
    return jsonify("success_existingUser, login success: existing user!")
    
# INFO: Handles log out requests
@app.route('/api/auth/logout', methods=['POST'])
def handle_logout_request():
    userEmail = request.form.get("email", "")
    userSub = request.form.get("sub", "")

    # Convert user sub string to int 
    userSubNumber = int(userSub)

    # Check if user is actually still logged in
    if userSubNumber != server.get_user_by_id(userSubNumber).id:
        return Response(1, "Logout error: user is not logged in!", "error").jsonify()

    # Convert back to string to remove possible sql injection
    userSub = str(userSubNumber)

    print("Received email:" + userEmail)
    print("Received sub:" + userSub)

    conn = sqlite3.connect('Database/Main.db')

    # TODO: Wrap in try catch and use a transaction
    cursor = conn.execute("SELECT * FROM logged_in_users WHERE sub = ?", (userSub, ))

    users = []
    for row in cursor:
        users.append(row)
    
    # Check if the user is already logged out
    # the user can either not be found or the logged_in field is 0
    # NOTE: users[0] is the first row of the result (we are only expecting one as subs (user_id) are unique)
    # [1] is the logged_in field (the second field in the row)
    # the reason why we can do an or check like this without checking the length of the list is that
    # python will early exist the if statment if the first condition is already true
    if len(users) == 0 or users[0][1] == 0:
        cursor.close()
        conn.close()
        return Response(1, "Logout error: user is not logged in!", "error").jsonify()

    cursor = conn.execute("UPDATE logged_in_users SET logged_in = 0 WHERE sub = ?", (userSub,))
    conn.commit()

    cursor.close()
    conn.close()

    del server.logged_in_users[userSubNumber]
    print("User with sub: {} logged out succesfully".format(userSubNumber))
    return Response(0, "Logout success: existing user!").jsonify()
    
# INFO: Handles request to get all the bids for a stock
@app.route('/api/stocks/bids', methods=['POST'])
def handle_get_bids_request():
    # userEmail = request.form.get("email", "")
    userSub = request.form.get("sub", "")

    # Convert user sub string to int
    userSubNumber = int(userSub) # INFO: This is used as the user id

    if userSubNumber != server.get_user_by_id(userSubNumber).id:
        return jsonify("error_userNotLoggedIn, Failed to get bids from server error: user is not logged in!")
        return Response(1, "")

    conn = sqlite3.connect('Database/Main.db')
    # TODO: (Anyone) Link the user id with user name so the users don't see their or other's user ids'
    cursor = conn.execute("SELECT * FROM BIDS");
    # TODO: (Anyone) Something like this: SELECT * FROM BIDS WHERE user_id = user_id
    # and replace "*" with the fields we want to show to the user in the frontend

    try:
        conn.commit()
        bids = []
        for row in cursor:
            bids.append(row)
        response = Response(0, "Fetch success: Successfully fetched bids from the server!", bids)
        return jsonify(response.get_data())

    except:
        cursor.close()
        conn.close()
        response = Response(1, "Fetch error: Failed to get bids from the database!", "error")
        return jsonify(response)

        # return jsonify("error_getBids, Fetch error: failed to get bids from the database!")
    finally:
        cursor.close()
        conn.close()

    # return jsonify("success_getBids, Fetch success: existing user fetched bids!")

# INFO: Handles bid addition requests from the client
# This is the trade request that the user makes to the server
# with the intention of buying a stock with a given
# amount and maximum price the user is willing to pay
# given that there is a sell offer that matches the bid
# the user making the bid will be matched with the sell offer
# and only charged the price of the sell offer that is 
# the highest price that is still equal or lower than the bid price
@app.route('/api/stocks/bid', methods=['POST'])
def handle_bid_addition():
    userEmail = request.form.get("email", "")
    userSub = request.form.get("sub", "")

    # Convert user sub string to int
    userSubNumber = int(userSub) # INFO: This is used as the user id

    # Check if user is actually still logged in
    # BUG: Currently, the frontend allows the user to easily attempt adding bids without logging in
    # which is not wanted, we want the user to log in first before we allow them to place bids, 
    # as we wouldn't be able to recognize who is making the bids otherwise
    if userSubNumber != server.get_user_by_id(userSubNumber).id:
        return jsonify("error_userNotLoggedIn, bid addition error: user is not logged in!")

    # print("User id of the bid is: {}".format(userSub))
    # User is surely logged in: Parse all the fields (of the bid) from the request form
    user_id = request.form.get("bidData.user_id", "")
    stock_id = request.form.get("bidData.stock_id", "")
    amount = request.form.get("bidData.amount", "")
    price = request.form.get("bidData.price", "")
    newBid = Order(Server.query_next_bid_id(), server.logged_in_users[int(user_id)], stock_id, amount, price)

    # TODO: Query next id from the database

    # Convert back to string to remove possible sql injection
    userSub = str(userSubNumber)

    print("Handling bid addition for:")
    print("Received email:" + userEmail)
    print("Received sub:" + userSub)

    # print("DATA: {}".format(request.form))
    print("\nBID DATA: \n==============\nuser_id: \
            {}\nstock_id: {}\namount: {}\nprice: {}\n==============".\
            format(repr(newBid.user.id), newBid.stock_id, newBid.amount, newBid.price))

    # TODO: Investigate: does sqlite3 have a connection limit similar to MySQL/MariaDB or is just the
    # OS concurrent file read limit
    conn = sqlite3.connect('Database/Main.db')

    # Make prepared statement instead of using raw sql
    # NOTE: We convert user id to string here to fit the sub (as it's more than 64 bits and doesn't fit into an int64)
    cursor = conn.execute("INSERT INTO bids (id, user_id, stock_id, amount, price) VALUES (?, ?, ?, ?, ?)", (newBid.id, str(newBid.user.id), newBid.stock_id, newBid.amount, newBid.price))

    try:
        conn.commit()
        server.stock_trade_manager.add_bid(newBid)
    except:
        # cursor.close()
        # conn.close()
        return jsonify("error_bidAddition, Bid addition error: failed to add bid to the database!")
    finally:
        cursor.close()
        conn.close()

    # TODO: Depending on what limits we have on the database we might want to keep connections open per logged in user 
    # for performance reasons, closing a connection on a sql database is usually somewhat a costly operation so this
    # might also be the case when using sqlite

    return jsonify("success_bidAdded, Bid addition success: existing user added a bid!")

@app.route('/api/stocks/sell', methods=['POST'])
def handle_sell_addition():
    userEmail = request.form.get("email", "")
    userSub = request.form.get("sub", "")

    # Convert user sub string to int
    userSubNumber = int(userSub) # INFO: This is used as the user id

    # Check if user is actually still logged in
    # BUG: Currently, the frontend allows the user to easily attempt adding bids without logging in
    # which is not wanted, we want the user to log in first before we allow them to place bids, 
    # as we wouldn't be able to recognize who is making the bids otherwise
    if userSubNumber != server.get_user_by_id(userSubNumber).id:
        return jsonify("error_userNotLoggedIn, sell offer addition error: user is not logged in!")

    # print("User id of the bid is: {}".format(userSub))
    # User is surely logged in: Parse all the fields (of the bid) from the request form
    user_id = request.form.get("sellData.user_id", "")
    stock_id = request.form.get("sellData.stock_id", "")
    amount = request.form.get("sellData.amount", "")
    price = request.form.get("sellData.price", "")
    newOffer = Order(Server.query_next_bid_id(), server.logged_in_users[int(user_id)], stock_id, amount, price, 1) # Init a sell offer

    # TODO: Query next id from the database

    # Convert back to string to remove possible sql injection
    userSub = str(userSubNumber)

    print("Handling offer addition for:")
    print("Received email:" + userEmail)
    print("Received sub:" + userSub)

    # print("DATA: {}".format(request.form))
    print("\nSELL OFFER DATA: \n==============\nuser_id: \
            {}\nstock_id: {}\namount: {}\nprice: {}\n==============".\
            format(repr(newOffer.user.id), newOffer.stock_id, newOffer.amount, newOffer.price))

    # TODO: Investigate: does sqlite3 have a connection limit similar to MySQL/MariaDB or is just the
    # OS concurrent file read limit
    conn = sqlite3.connect('Database/Main.db')

    # Make prepared statement instead of using raw sql
    # NOTE: We convert user id to string here to fit the sub (as it's more than 64 bits and doesn't fit into an int64)
    cursor = conn.execute("INSERT INTO offers (id, user_id, stock_id, amount, price) VALUES (?, ?, ?, ?, ?)", (newOffer.id, str(newOffer.user.id), newOffer.stock_id, newOffer.amount, newOffer.price))

    try:
        conn.commit()
        server.stock_trade_manager.add_offer(newOffer)
    except:
        cursor.close()
        conn.close()
        return jsonify("error_offerAddition, Bid addition error: failed to add offer to the database!")
    finally:
        cursor.close()
        conn.close()

    # TODO: Depending on what limits we have on the database we might want to keep connections open per logged in user 
    # for performance reasons, closing a connection on a sql database is usually somewhat a costly operation so this
    # might also be the case when using sqlite

    return jsonify("success_offerAdded, Bid addition success: existing user added an offer!")
    
