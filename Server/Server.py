from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

# Import the stock modules, these contain primitives for the stock trade manager 
from StockModules import *
from StockTradeManager import *

class Server():
    logged_in_users = {}
    stock_trade_manager = StockTradeManager()

    def __init__(self):
        self.cached_data = [] 

        # Init empty 
        self.logged_in_users = {}

        # NOTE: Initialization process:
        # 1. Fetch the stock data from the REST API
        # and store it in the cache
        # 2. Fetch logged in users
        # 3. Fetch the trades from the database
        # 4. Fetch the bids from the database
        # 5. Fetch the sell offers from the database

        conn = sqlite3.connect('Database/Main.db')

        # 2. Fetch logged in users
        # cursor = conn.execute("SELECT * FROM logged_in_users WHERE logged_in = 1")
        # NOTE: sub is the user id
        cursor = conn.execute("SELECT sub, first_name, last_name, email FROM users WHERE sub IN (SELECT sub FROM logged_in_users WHERE logged_in = 1);")
        conn.commit()

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

    def is_user_logged_in(self, id):
        # conn = sqlite3.connect('Database/Main.db')
        #
        # # Make prepared statement instead
        # cursor = conn.execute("SELECT * FROM USERS WHERE sub = ?", (userSub, ))
        #
        # conn.commit()

        if id in self.logged_in_users:
            return self.logged_in_users[id]
        return User()  # Return None if no user with the given id is found

    def get_cached_data(self, stock_id):
        return self.cached_data[stock_id]

# Initialize the server
server = Server()

##############################################################################################################
## FLASK API ENDPOINTS
##############################################################################################################

app = Flask(__name__) # Initialize the Flask app
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/api/stocks/price', methods=['POST'])
def getLastTradedPriceForStock():
    stock_id = request.form.get("stock_id", "")  # Get the wanted stock id from the request
    stock_id = int(stock_id)

    stocks = []
    stocks.append(resolve_cached_data(stock_id))
    data = [stock.get_data() for stock in stocks]

    print("Last traded price for stock: \"{}\" is : ${}".format(data[0]['name'], data[0]['price']))

    return Response(0, "Fetch success: Successfully fetched last traded price data from the server!", data[0]).jsonify()

@app.route('/api/stocks/apple', methods=['POST'])
def get_stocks():
    data = resolve_cached_data(1)
    return Response(0, "Fetch success: Successfully fetched stock data from the server!", data).jsonify()

# INFO: Rest api for getting all the made trades
@app.route('/api/stocks/public/trades')
def get_trades():
    conn = sqlite3.connect('Database/Main.db')
    cursor = conn.execute("SELECT * FROM trades ORDER BY time")
    trades = []
    for row in cursor:
        trades.append(row)
    cursor.close()
    conn.close()
    return Response(0, "Fetch success: Successfully fetched trades from the server!", trades).jsonify()

@app.route('/api/getdb')
def get_db():
    conn = sqlite3.connect('Database/Main.db')
    cursor = conn.execute("SELECT * FROM USERS")
    list = []
    for row in cursor:
        list.append(row)
    cursor.close()
    conn.close()
    # FIXME: Use response object
    return jsonify(list)

# INFO: Handles log in requests from clients
# StatusCodes: 
# 0 = success
# 1 = error
@app.route('/api/auth/login', methods=['POST'])
def handle_login_request():
    userEmail : str = request.form.get("email", "")
    userSub : str = request.form.get("sub", "")
    first_name : str = request.form.get("first_name", "")
    last_name : str = request.form.get("last_name", "")

    if userSub == 'undefined':
        return Response(0, "Login success: user is already logged in!").jsonify()

    # Convert user sub string to int and back to string to remove possible sql injection
    userSubNumber : int = int(userSub)
    userSub : str = str(userSubNumber)

    print("Received email:" + userEmail)
    print("Received sub:" + userSub)

    # Check if user is already logged in
    if userSubNumber == server.is_user_logged_in(userSubNumber).id:
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

            # Add the user some initial money
            cursor_insert = conn.execute("INSERT INTO user_owned_money (user_id, amount) VALUES (?, ?)", (userSub, 2000))
            conn.commit()

            # Add the user some initial stock
            cursor_insert = conn.execute("INSERT INTO user_owned_stocks (user_id, stock_id, amount) VALUES (?, ?, ?)", (userSub, 1, 100))
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
    userEmail : str = request.form.get("email", "")
    userSub : str  = request.form.get("sub", "")

    # Convert user sub string to int 
    userSubNumber : int = int(userSub)

    # Check if user is actually still logged in
    if userSubNumber != server.is_user_logged_in(userSubNumber).id:
        return Response(1, "Logout error: user is not logged in!", "error").jsonify()

    # Convert back to string to remove possible sql injection
    userSub : str = str(userSubNumber)

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

    if userSubNumber != server.is_user_logged_in(userSubNumber).id:
        # FIXME: Use response object
        return jsonify("error_userNotLoggedIn, Failed to get bids from server error: user is not logged in!")
        # return Response(1, "")

    conn = sqlite3.connect('Database/Main.db')
    # TODO: (Anyone) Link the user id with user name so the users don't see their or other's user ids'
    cursor = conn.execute("SELECT * FROM bids WHERE user_id = ?", (userSub,))   
    # TODO: (Anyone) Something like this: SELECT * FROM BIDS WHERE user_id = user_id
    # and replace "*" with the fields we want to show to the user in the frontend

    try:
        conn.commit()
        bids = []
        for row in cursor:
            bids.append(row)
        cursor = conn.execute("SELECT * FROM offers WHERE user_id = ?", (userSub,))
        conn.commit()
        offers = []
        for row in cursor:
            offers.append(row)
            
        response = Response(0, "Fetch success: Successfully fetched bids from the server!", (bids, offers))
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

    # FIXME: Use response object
    # return jsonify("success_getBids, Fetch success: existing user fetched bids!")

# INFO: Handles request to remove a specific bid
@app.route('/api/stocks/bid_cancel', methods=['POST'])
def handle_bid_cancellation():
    bidId = request.form.get("bid", "")
    stockId = request.form.get("stock", "")
    userSub = request.form.get("sub", "")

    userSubNumber = int(userSub)
    bidIdNumber = int(bidId)
    stockIdNumber = int(stockId)

    if userSubNumber != server.is_user_logged_in(userSubNumber).id:
        return Response(1, "error_userNotLoggedIn, Failed to get bids from server error: user is not logged in!", "error").jsonify()
        
    conn = sqlite3.connect('Database/Main.db')

    # Make prepared statement instead of using raw sql
    # NOTE: We convert user id to string here to fit the sub (as it's more than 64 bits and doesn't fit into an int64)
    cursor = conn.execute("SELECT amount, price FROM bids WHERE id = ? AND user_id = ? AND stock_id = ?", (bidId, userSub, stockIdNumber))
    amounts = []
    for row in cursor:
        amounts.append(row)

    if len(amounts) != 1:
        return Response(1, "Bid cancellation error: failed to remove bid from the database!", "error").jsonify()
    
    cursor = conn.execute("DELETE FROM bids WHERE id = ? AND user_id = ? AND stock_id = ?", (bidIdNumber, userSub, stockIdNumber))

    try:
        conn.commit()

        # Return the amount of money to the user's money count
        cursor = conn.execute("UPDATE user_owned_money SET amount = amount + ? WHERE user_id = ?", (amounts[0][0] * amounts[0][1], userSub))
        conn.commit()

        # remove_bid returns true if all went ok. Otherwise an exception is raised and
        # it will be handled in the except block.
        if not (server.stock_trade_manager.remove_bid(bidIdNumber, userSubNumber, stockIdNumber)):
            raise Exception()
    except:
        return Response(1, "error_bidCancellation, Bid cancellation error: failed to remove bid from the database!", "error").jsonify()
    finally:
        cursor.close()
        conn.close()

    return Response(0, "success_bidRemoved, Bid remove success: existing user removed a bid!", "success").jsonify()

# INFO: Handles request to remove a specific offer
@app.route('/api/stocks/offer_cancel', methods=['POST'])
def handle_offer_cancellation():
    offerId = request.form.get("offer", "")
    stockId = request.form.get("stock", "")
    userSub = request.form.get("sub", "")

    userSubNumber = int(userSub)
    offerIdNumber = int(offerId)
    stockIdNumber = int(stockId)

    if userSubNumber != server.is_user_logged_in(userSubNumber).id:
        return Response(1, "error_userNotLoggedIn, Failed to get offers from server error: user is not logged in!", "error").jsonify()
        
    conn = sqlite3.connect('Database/Main.db')

    # Make prepared statement instead of using raw sql
    # NOTE: We convert user id to string here to fit the sub (as it's more than 64 bits and doesn't fit into an int64)
    cursor = conn.execute("SELECT amount FROM offers WHERE id = ? AND user_id = ? AND stock_id = ?", (offerIdNumber, userSub, stockIdNumber))
    amounts = []
    for row in cursor:
        amounts.append(row)

    if len(amounts) != 1:
        return Response(1, "Offer cancellation error: failed to remove offer from the database!", "error").jsonify()

    cursor = conn.execute("DELETE FROM offers WHERE id = ? AND user_id = ? AND stock_id = ?", (offerIdNumber, userSub, stockIdNumber))

    try:
        conn.commit()

        # Return the amount of stocks to the user's stock count
        cursor = conn.execute("UPDATE user_owned_stocks SET amount = amount + ? WHERE user_id = ? AND stock_id = ?", (amounts[0][0], userSub, stockId))
        conn.commit()

        # remove_sell_offer returns true if all went ok. Otherwise an exception is raised and
        # it will be handled in the except block.
        if not (server.stock_trade_manager.remove_sell_offer(offerIdNumber, userSubNumber, stockIdNumber)):
            raise Exception()
    except:
        return Response(1, "error_offerCancellation, Offer cancellation error: failed to remove offer from the database!", "error").jsonify()
    finally:
        cursor.close()
        conn.close()

    return Response(0, "success_offerRemoved, Offer remove success: existing user removed an offer!", "success").jsonify()

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
    if userSubNumber != server.is_user_logged_in(userSubNumber).id:
        print("User id of the bid is: {}".format(userSub))
        return Response(1, "Bid addition error: user is not logged in!", "error").jsonify()
        # return jsonify("error_userNotLoggedIn, bid addition error: user is not logged in!")

    # print("User id of the bid is: {}".format(userSub))
    # User is surely logged in: Parse all the fields (of the bid) from the request form
    user_id = request.form.get("bidData.user_id", "")
    stock_id : int = int(request.form.get("bidData.stock_id", ""))
    amount : int = int(request.form.get("bidData.amount", ""))
    date = datetime.now()

    # FIXME: Use different status code in the response to indicate different problems with the bid
    # addition so we can display correct messages to the user
    # this could also be done by setting limits in the input boxes
    # because in that way we don't tell the client about how the server is handling the sent data
    if (amount < 1):
        print("The user has to sell at least one stock!")
        return Response(1, "The user has to sell at least one stock!", "error").jsonify()

    price : float = float(request.form.get("bidData.price", ""))

    # Check that the bid price is ±10% of the current market price of the stock
    if not (abs(price - server.stock_trade_manager.current_stock) <= server.stock_trade_manager.current_stock * 0.1):
        return Response(1, "Price is outside the allowed range!", "error").jsonify()

    newBid = Order(query_next_id_for_table("bids"), server.logged_in_users[int(user_id)], stock_id, amount, price, str(date))

    # TODO: Query next id from the database

    # Convert back to string to remove possible sql injection
    userSub : str = str(userSubNumber)

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
    cursor = conn.execute("SELECT amount FROM user_owned_money WHERE user_id = ?", (str(newBid.user.id), ))
    
    amounts = []
    for row in cursor:
        amounts.append(row)

    if len(amounts) != 1 or amounts[0][0] < newBid.amount * newBid.price:
        return Response(1, "Bid addition error: can't buy with more money than owned", "error").jsonify()

    cursor = conn.execute("INSERT INTO bids (id, user_id, stock_id, amount, price, date) VALUES (?, ?, ?, ?, ?, ?)", (newBid.id, str(newBid.user.id), newBid.stock_id, newBid.amount, newBid.price, newBid.date))

    try:
        conn.commit()
        # Remove the amount of money from the user's money count
        cursor = conn.execute("UPDATE user_owned_money SET amount = amount - ? WHERE user_id = ?", (newBid.amount * newBid.price, str(newBid.user.id)))
        conn.commit()
    except:
        print("ERROR: Failed to add bid to the database!")
        return jsonify("error_bidAddition, Bid addition error: failed to add bid to the database!")
    finally:
        cursor.close()
        conn.close()

    # All good, we can add the bid to the stock trade manager now
    server.stock_trade_manager.add_bid(newBid)

    # TODO: Depending on what limits we have on the database we might want to keep connections open per logged in user 
    # for performance reasons, closing a connection on a sql database is usually somewhat a costly operation so this
    # might also be the case when using sqlite

    return Response(0, "success_bidAdded, Bid addition success: existing user added a bid!", "success").jsonify()

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
    if userSubNumber != server.is_user_logged_in(userSubNumber).id:
        # FIXME: Use response object
        return jsonify("error_userNotLoggedIn, sell offer addition error: user is not logged in!")

    # print("User id of the bid is: {}".format(userSub))
    # User is surely logged in: Parse all the fields (of the bid) from the request form
    user_id = request.form.get("sellData.user_id", "")
    stock_id : int = int(request.form.get("sellData.stock_id", ""))
    date = datetime.now()
    amount :int = int(request.form.get("sellData.amount", ""))
    price : float = float(request.form.get("sellData.price", ""))

    if (amount < 1):
        print("The user has to buy at least one stock!")
        return Response(1, "The user has to buy at least one stock!", "error").jsonify()

    # Check that the bid price is ±10% of the current market price of the stock
    if not (abs(price - server.stock_trade_manager.current_stock) <= server.stock_trade_manager.current_stock * 0.1):
        return Response(1, "Price is outside the allowed range!", "error").jsonify()

    newOffer = Order(query_next_id_for_table("offers"), server.logged_in_users[int(user_id)], stock_id, amount, price, str(date), 1) # Init a sell offer

    # TODO: Query next id from the database

    # Convert back to string to remove possible sql injection
    userSub : str = str(userSubNumber)

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

    cursor = conn.execute("SELECT amount FROM user_owned_stocks WHERE user_id = ? AND stock_id = ?", (str(newOffer.user.id), newOffer.stock_id))
    
    amounts = []
    for row in cursor:
        amounts.append(row)

    if len(amounts) != 1 or amounts[0][0] < newOffer.amount:
        return Response(1, "Offer addition error: can't sell more stocks than owned", "error").jsonify()

    # Make prepared statement instead of using raw sql
    # NOTE: We convert user id to string here to fit the sub (as it's more than 64 bits and doesn't fit into an int64)
    cursor = conn.execute("INSERT INTO offers (id, user_id, stock_id, amount, price, date) VALUES (?, ?, ?, ?, ?, ?)", (newOffer.id, str(newOffer.user.id), newOffer.stock_id, newOffer.amount, newOffer.price, newOffer.date))

    try:
        conn.commit()

        # Remove the amount of stocks from the user's stock count
        cursor = conn.execute("UPDATE user_owned_stocks SET amount = amount - ? WHERE user_id = ? AND stock_id = ?", (newOffer.amount, userSub, stock_id))
        conn.commit()

        # All good, we can add the offer to the stock trade manager now
        server.stock_trade_manager.add_offer(newOffer)
    except:
        # cursor.close()
        # conn.close()
        # FIXME: Use response object
        return jsonify("error_offerAddition, Bid addition error: failed to add offer to the database!")
    finally:
        cursor.close()
        conn.close()

    # TODO: Depending on what limits we have on the database we might want to keep connections open per logged in user 
    # for performance reasons, closing a connection on a sql database is usually somewhat a costly operation so this
    # might also be the case when using sqlite

    # FIXME: Use response object
    return jsonify("success_offerAdded, Bid addition success: existing user added an offer!")

@app.route('/api/stocks/getstockcount', methods=['POST'])
def get_stock_count():
    # userEmail = request.form.get("email", "")
    userSub : str = request.form.get("sub", "")
    stockId : int = int(request.form.get("stock_id", ""))

    # Convert user sub string to int
    userSubNumber : int = int(userSub) # INFO: This is used as the user id

    if userSubNumber != server.is_user_logged_in(userSubNumber).id:
        return Response(1, "error_userNotLoggedIn, Failed to get stock amount from server error: user is not logged in!", "error").jsonify()

    conn = sqlite3.connect('Database/Main.db')
    # TODO: (Anyone) Link the user id with user name so the users don't see their or other's user ids'
    cursor = conn.execute("SELECT amount FROM user_owned_stocks WHERE user_id = ? AND stock_id = ?", (userSub, stockId))
    # TODO: (Anyone) Something like this: SELECT * FROM BIDS WHERE user_id = user_id
    # and replace "*" with the fields we want to show to the user in the frontend

    try:
        conn.commit()
        stockAmount = []
        for row in cursor:
            stockAmount.append(row[0])
        cursor = conn.execute("SELECT amount FROM user_owned_money WHERE user_id = ?", (userSub,))
        conn.commit()
        moneyAmount = []
        for row in cursor:
            moneyAmount.append(row[0])
            
        response = Response(0, "Fetch success: Successfully fetched stock and money amount from the server!", (stockAmount, moneyAmount))
        return jsonify(response.get_data())

    except:
        cursor.close()
        conn.close()
        response = Response(1, "Fetch error: Failed to get stock amount from the database!", "error")
        return jsonify(response)

        # return jsonify("error_getBids, Fetch error: failed to get bids from the database!")
    finally:
        cursor.close()
        conn.close()
