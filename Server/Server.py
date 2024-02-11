import flask
from flask import request, jsonify

app = flask.Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

