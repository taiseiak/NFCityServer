"""
Main server that will be running the calls back and forth from the pi.
This server will also do any image processing.
"""

import flask
from flask import request
from database import add_to_database, update_database
from imageprocess import check_car

# Globals
app = flask.Flask(__name__)


# Main API routing
@app.route("/start_lot")
def start_lot():
    card = request.args.get("card", type=str)
    lot = request.args.get("lot", type=int)
    license_plate = check_car(lot)
    if license_plate:
        transaction = add_to_database(card, lot, license_plate)
        result = {"start": True,
                  "transaction": transaction}
    else:
        result = {"start": False,
                  "transaction": "invalid"}
    return flask.jsonify(result=result)


@app.route("/check_lot")
def check_lot():
    transaction = request.args.get("transaction", type=int)
    lot = request.args.get("lot", type=int)
    license_place = check_car(lot)
    if license_place:
        cost = update_database(transaction)
        result = {"cost": cost,
                  "final": False}
    else:
        cost = update_database(transaction)
        result = {"cost": cost,
                  "final": True}
    return flask.jsonify(result=result)

if __name__ == "__main__":
    app.run()
