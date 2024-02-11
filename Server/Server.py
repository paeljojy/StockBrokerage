import flask
from flask import request, jsonify
import sqlite3
import mariadb

app = flask.Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/getdb', methods=['GET'])
def getdb():
    conn = sqlite3.connect('Database/Main.db')
    cursor = conn.execute("SELECT * FROM USERS")
    list = []
    for row in cursor:
        list.append(row)
    cursor.close()
    conn.close()
    return jsonify(list)
