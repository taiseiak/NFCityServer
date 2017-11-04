"""
Main server that will be running the calls back and forth from the pi.
This server will also do any image processing.
"""

import flask
from flask import request
import pymongo
import arrow
from database import add_to_database, update_database, close_database
from imageprocess import check_car

# Globals
app = flask.Flask(__name__)
MONGO_CLIENT_URL = "mongodb://lot_one:hackGSU@ds147265.mlab.com:47265/nfcity"
dbclient = pymongo.MongoClient(MONGO_CLIENT_URL)
database = dbclient.nfcity
collection = database.parking_lot_one


# Main API routing
@app.route("/start_lot")
def start_lot():
    card = request.args.get("card", type=str)
    lot = request.args.get("lot", type=int)
    if check_car(lot):
        transaction = add_to_database(card)
        result = {"start": True,
                  "transaction": transaction}
    else:
        result = {"start": False,
                  "transaction": 0}
    return flask.jsonify(result=result)


@app.route("/check_lot")
def check_lot():
    transaction = request.args.get("transaction", type=int)
    if check_car():
        cost = update_database(transaction)
        result = {"cost": cost,
                  "final": False}
    else:
        cost = close_database(transaction)
        result = {"cost": cost,
                  "final": True}
    return flask.jsonify(result=result)
