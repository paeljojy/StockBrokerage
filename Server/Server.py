from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import mariadb
from datetime import datetime
import time
import requests

class Server():
    cachedData = None
    cachedData = None
    lastFetchTime = None

    def init(self):
        self.cachedData = None

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

@app.route('/getdb')
def getdb():
    conn = sqlite3.connect('Database/Main.db')
    cursor = conn.execute("SELECT * FROM USERS")
    list = []
    for row in cursor:
        list.append(row)
    cursor.close()
    conn.close()
    return jsonify(list)

