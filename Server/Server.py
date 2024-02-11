import flask
from flask import request, jsonify

def Server():
    app = flask.Flask(__name__)

    @app.route('/')
    def home():
        return "Hello, World!"

    @app.route('/api', methods=['GET'])
    def api():
        return jsonify({'data': 'Hello, World!'})


if __name__ == "__main__":
    Server()

