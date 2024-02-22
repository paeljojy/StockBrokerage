from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import time
import requests

import os
print("CWD IS: ", os.getcwd())

class Bid:
    def __init__(self, id, user):
        self.id = id
        self.user = user

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
        return None  # Return None if no user with the given id is found

class Server():
    cachedData = None
    lastFetchTime = None
    loggedInUsers = set()

    def init(self):
        self.cachedData = None
        self.loggedInUsers = set(self.loggedInUsers)

    def getCachedData(self):
        return self.cachedData

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
@app.route('/api/login', methods=['POST'])
def sendlogin():
    userEmail = request.form.get("email", "")
    userSub = request.form.get("sub", "")

    # Convert user sub string to int and back to string to remove possible sql injection
    userSubNumber = int(userSub)
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
        try:
            cursor = conn.execute("INSERT INTO USERS (sub, email) VALUES (?, ?)", (userSub, userEmail))
            succ = conn.commit()
            server.loggedInUsers.add(User(userSubNumber, userEmail))
            return jsonify("success_newUser, login success: new user!")
        except:
            return jsonify("error_newUser, login failed: new user error!")
        finally:
            cursor.close()
            conn.close()

    cursor.close()
    conn.close()

    server.loggedInUsers.add(User(userSubNumber, userEmail))
    return jsonify("success_existingUser, login success: existing user!")
    
# INFO: Handles log out requests
# FIXME: User does not exist in loggedInUsers for some god knows what reason
@app.route('/api/logout', methods=['POST'])
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
    
