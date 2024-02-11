import flask
from flask import request, jsonify
import sqlite3
import mariadb

app = flask.Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"




