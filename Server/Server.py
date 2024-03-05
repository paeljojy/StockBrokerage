from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import time
import requests

import os
print("CWD IS: ", os.getcwd())

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

    def __init__(self, status, message, data):
        self.status = status
        self.message = message
        self.data = data 

    def getStatus(self):
        return self.status

    def getMessage(self):
        return self.message

    def getData(self):
        # Make the object into a dictionary for JSON conversion
        return self.__dict__

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
    sellOffers = [] # Sell offers that are waiting to be matched with bids

    def __init__(self):
        self.trades = []

        self.bids = []
        self.sellOffers = []

    def addTrade(self):
        pass

    # Adds a new bid and matches it with a sell offer if possible
    def addBid(self, newBid):
        self.bids.append(newBid)
        pass

    # General update that is used whenever a new stock price is fetched
    # This will update the whole system and match bids with sell offers if possible
    # based on the new stock market price
    def update(self):
        pass

class Bid:
    # INFO: We query the database for the next available id
    # and use it as the id of the bid
    def __init__(self, id, user_id, stock_id, amount, price):
        self.id = id # INFO: this is id of the bid, NOT THE USER
        self.user_id = user_id
        self.stock_id = stock_id
        self.amount = amount
        self.price = price

class SellOffer:
    def __init__(self, id, user):
        self.id = id
        self.user = user

class User:
    def __init__(self, id, email):
        self.id = id
        self.email = email

    def __hash__(self):
        return hash((self.id, self.email))

    def __eq__(self, other):
        return (self.id, self.email) == (other.id, other.email)

    @staticmethod
    def get_user_by_id(users, id):
        for user in users:
            if user.id == id:
                return user
        return User(-1, "")  # Return None if no user with the given id is found

class Server():
    cachedData = None
    lastFetchTime = None
    loggedInUsers = set()

    def init(self):
        self.cachedData = None
        self.loggedInUsers = set(self.loggedInUsers)


    def getCachedData(self):
        return self.cachedData

    @staticmethod
    def queryNextBidId():
        # Query the database for the next available bid id
        # INFO: This is used to add new bids to the database, as the user can have multiple bids
        conn = sqlite3.connect('Database/Main.db')
        cursor = conn.execute("SELECT MAX(id) FROM bids")

        # Determine the next id to be used as an bid id (row id)
        last_id = cursor.fetchone()[0]
        print("Last id: ", last_id)
        next_id = 1 if last_id is None else last_id + 1
        print("Next id: ", next_id)

        # Clean up
        # cursor.close()
        # conn.close()

        return next_id

server = Server()

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

def resolveCachedData(server):
    data = server.getCachedData()
    server.currentTime = datetime.now()

    # If we have cached data and it's less than an hour old, return it
    # INFO: 3600s = 1 hour
    if server.cachedData is not None and (server.currentTime - server.lastFetchTime).total_seconds() < 3600:
        return server.cachedData

    # Otherwise, fetch new data from REST API
    res = requests.get('https://api.marketdata.app/v1/stocks/quotes/AAPL/')
    data = res.json()

    # Update the cache and the fetch time
    server.cachedData = data
    server.lastFetchTime = server.currentTime

    return data

@app.route('/api/stocks/apple')
def getStocks():
    data = resolveCachedData(server)
    return jsonify(data)

# INFO: Rest api for getting all the made trades
@app.route('/api/stocks/public/trades')
def getTrades():
    conn = sqlite3.connect('Database/Main.db')
    cursor = conn.execute("SELECT * FROM trades")
    trades = []
    for row in cursor:
        trades.append(row)
    cursor.close()
    conn.close()
    return jsonify(trades)

@app.route('/api/getdb')
def getdb():
    conn = sqlite3.connect('Database/Main.db')
    cursor = conn.execute("SELECT * FROM USERS")
    list = []
    for row in cursor:
        list.append(row)
    cursor.close()
    conn.close()
    return jsonify(list)

# INFO: Handles log in requests
@app.route('/api/auth/login', methods=['POST'])
def sendlogin():
    userEmail = request.form.get("email", "")
    userSub = request.form.get("sub", "")
    first_name = request.form.get("first_name", "")
    last_name = request.form.get("last_name", "")

    # Convert user sub string to int and back to string to remove possible sql injection
    userSubNumber = int(userSub)
    userSub = str(userSubNumber)

    print("Received email:" + userEmail)
    print("Received sub:" + userSub)

    # Check if user is already logged in
    if userSubNumber == User.get_user_by_id(server.loggedInUsers, userSubNumber).id:
        return jsonify("error_alreadyLoggedIn, logout error: user is already logged in!")

    conn = sqlite3.connect('Database/Main.db')

    # Make prepared statement instead
    cursor = conn.execute("SELECT * FROM USERS WHERE sub = ?", (userSub,))

    list = []
    for row in cursor:
        list.append(row)

    if len(list) == 0:
        try:
            cursor = conn.execute("INSERT INTO USERS (sub, email, first_name, last_name) VALUES (?, ?, ?, ?)", (userSub, userEmail, first_name, last_name))
            conn.commit()
            server.loggedInUsers.add(User(userSubNumber, userEmail))
            return jsonify("success_newUser, login success: new user!")
        except:
            print("error_newUser, login failed: new user error! database doesn't most likely exists on disk")
            return jsonify("error_newUser, login failed: new user error!")
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.close()
        conn.close()

    server.loggedInUsers.add(User(userSubNumber, userEmail))
    return jsonify("success_existingUser, login success: existing user!")
    
# INFO: Handles log out requests
@app.route('/api/auth/logout', methods=['POST'])
def sendlogout():
    userEmail = request.form.get("email", "")
    userSub = request.form.get("sub", "")

    # Convert user sub string to int 
    userSubNumber = int(userSub)

    # Check if user is actually still logged in
    if userSubNumber != User.get_user_by_id(server.loggedInUsers, userSubNumber).id:
        return jsonify("error_userNotLoggedIn, logout error: user is not logged in!")

    # Convert back to string to remove possible sql injection
    userSub = str(userSubNumber)

    print("Received email:" + userEmail)
    print("Received sub:" + userSub)
    conn = sqlite3.connect('Database/Main.db')

    # Make prepared statement instead
    cursor = conn.execute("SELECT * FROM USERS WHERE sub = ?", (userSub,))

    list = []
    for row in cursor:
        list.append(row)

    if len(list) == 0:
        cursor.close()
        conn.close()

        return jsonify("error_userNotFound, logout error: no user found!")

    cursor.close()
    conn.close()

    server.loggedInUsers.remove(User(userSubNumber, userEmail))
    return jsonify("success_existingUser, logout success: existing user!")
    
# INFO: Handles request to get all the bids for a stock
@app.route('/api/stocks/bids', methods=['POST'])
def handleGetBidsRequest():
    # userEmail = request.form.get("email", "")
    userSub = request.form.get("sub", "")

    # Convert user sub string to int
    userSubNumber = int(userSub) # INFO: This is used as the user id

    if userSubNumber != User.get_user_by_id(server.loggedInUsers, userSubNumber).id:
        return jsonify("error_userNotLoggedIn, Failed to get bids from server error: user is not logged in!")

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
        data = response.getData()
        return jsonify(data)

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
def handleBidAddition():
    userEmail = request.form.get("email", "")
    userSub = request.form.get("sub", "")

    # Convert user sub string to int
    userSubNumber = int(userSub) # INFO: This is used as the user id

    # Check if user is actually still logged in
    # BUG: Currently, the frontend allows the user to easily attempt adding bids without logging in
    # which is not wanted, we want the user to log in first before we allow them to place bids, 
    # as we wouldn't be able to recognize who is making the bids otherwise
    if userSubNumber != User.get_user_by_id(server.loggedInUsers, userSubNumber).id:
        return jsonify("error_userNotLoggedIn, bid addition error: user is not logged in!")

    # print("User id of the bid is: {}".format(userSub))
    # User is surely logged in: Parse all the fields (of the bid) from the request form
    user_id = request.form.get("bidData.user_id", "")
    stock_id = request.form.get("bidData.stock_id", "")
    amount = request.form.get("bidData.amount", "")
    price = request.form.get("bidData.price", "")

    # TODO: Query next id from the database
    newBid = Bid(Server.queryNextBidId(), user_id, stock_id, amount, price)

    # Convert back to string to remove possible sql injection
    userSub = str(userSubNumber)

    print("Handling bid addition for:")
    print("Received email:" + userEmail)
    print("Received sub:" + userSub)

    # print("DATA: {}".format(request.form))
    print("\nBID DATA: \n==============\nuser_id: \
            {}\nstock_id: {}\namount: {}\nprice: {}\n==============".\
            format(newBid.user_id, newBid.stock_id, newBid.amount, newBid.price))

    # TODO: Investigate: does sqlite3 have a connection limit similar to MySQL/MariaDB or is just the
    # OS concurrent file read limit
    conn = sqlite3.connect('Database/Main.db')

    # Make prepared statement instead of using raw sql
    cursor = conn.execute("INSERT INTO bids (id, user_id, stock_id, amount, price) VALUES (?, ?, ?, ?, ?)", (newBid.id, newBid.user_id, newBid.stock_id, newBid.amount, newBid.price))

    try:
        conn.commit()
    except:
        cursor.close()
        conn.close()
        return jsonify("error_bidAddition, Bid addition error: failed to add bid to the database!")
    finally:
        cursor.close()
        conn.close()

    # TODO: Depending on what limits we have on the database we might want to keep connections open per logged in user 
    # for performance reasons, closing a connection on a sql database is usually somewhat a costly operation so this
    # might also be the case when using sqlite

    return jsonify("success_bidAdded, Bid addition success: existing user added a bid!")
    
