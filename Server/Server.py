from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import time
import requests

import os
print("CWD IS: ", os.getcwd())

class User:
    def __init__(self, id, email):
        self.id = id
        self.email = email

    def __hash__(self):
        return hash((self.id, self.email))

    def __eq__(self, other):
        return (self.id, self.email) == (other.id, other.email)

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


# IǸFO: 
@app.route('/api/login', methods=['POST'])
def sendlogin():
    userEmail = request.form.get("email", "")
    userSub = request.form.get("sub", "")

    # Convert user sub string to int and back to string to remove possible sql injection
    userSubNumber = int(userSub)
    userSub = str(userSubNumber)

    print("received email:" + userEmail)
    print("received sub:" + userSub)
    conn = sqlite3.connect('Database/Main.db')

    # Make prepared statement instead
    cursor = conn.execute("SELECT * FROM USERS WHERE sub = ?", (userSub,))

    list = []
    for row in cursor:
        list.append(row)

    if len(list) == 0:
        cursor = conn.execute("INSERT INTO USERS (sub, email) VALUES (?, ?)", (userSub, userEmail))
        succ = conn.commit()
        cursor.close()
        conn.close()

        if succ:
            server.loggedInUsers.add(User(userSub, userEmail))
            return jsonify("success_newUser, login success: new user!")
        return jsonify("error_newUser, login failed: new user error!")

    cursor.close()
    conn.close()

    server.loggedInUsers.add(User(userSub, userEmail))
    return jsonify("success_existingUser, login success: existing user!")
    
