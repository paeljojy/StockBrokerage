# INFO: This file contains all the primitive objects that are used in the stock exchange system
from flask import jsonify

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

    def __init__(self, status=-1, message='', data=None):
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



class User:
    # NOTE: User is not valid if the id is -1
    # also if your subs are really small integers you might have a problem
    id : int = -1
    first_name : str = ''
    last_name : str = ''
    email : str = ''

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

class Trade:
    buyer_user_id : str = ''
    seller_user_id : str = ''
    stock_id : int = 0
    amount : int = 0
    price : float = 0
    date: str = '1970 01 01 00:00:00.000000'

    def __init__(self, buyer_user_id : str, seller_user_id : str, stock_id : int=1, amount=0, price=-1.0, date='1970 01 01 00:00:00.000000'):
        self.buyer_user_id = buyer_user_id
        self.seller_user_id = seller_user_id
        self.stock_id = stock_id
        self.amount = amount
        self.price = price
        self.date = date 

class Stock:
    id : int = -1
    name : str = ""
    price : float = -1.0
    fetched_time : str = '' # NOTE: The time that the stocks last traded price was fetched at from the REST API

    def __init__(self, id : int=-1, name : str='', price : float=-1.0, fetched_time : str=''):
        self.id = id
        self.name = name
        self.price = price
        self.fetched_time = fetched_time

    def get_data(self):
        # Make the object into a dictionary for JSON conversion
        return self.__dict__

class Order:
    id = -1 # NOTE: The order id and not the user id ↓ 
    user = User() # NOTE: The user has the user id
    stock_id : int = -1
    amount : int = -1
    price : float = -1
    order_type : int = 0  # NOTE: 0 = bid, 1 = sell offer
    date = '' # NOTE: Used for time when the offer or bid was made

    # NOTE: We query the database for the next available id and use it as the id of the bid
    def __init__(self, id: int, user: User, stock_id, amount: int, price: float, date: str, order_type: int=0): # NOTE: By default we init a bid 1 for sell offer
        self.id = id         # NOTE: this is id of the bid, NOT THE USER
        self.user = user     # Actual user object
        self.stock_id = stock_id
        self.date = date

        self.amount = amount
        self.price = price
        self.order_type = order_type
