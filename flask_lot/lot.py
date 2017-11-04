"""
Main server that will be running the calls back and forth from the pi.
This server will also do any image processing.
"""

import flask
from flask import request
from database import update_document_card, update_document,\
    create_document, close_transaction

# Globals
app = flask.Flask(__name__)

spots = {
    1: ""
}


# Dummy url routing
@app.route("/")
def hello():
    return "Hello, World!"


# Main API routing
@app.route("/send_card")
def update_card():
    """Adds the card information to the document"""
    card = request.args.get("card", type=str)
    lot = request.args.get("lot", type=int)
    success = update_document_card(card, spots[lot])
    result = {"success": success}
    return flask.jsonify(result=result)


@app.route("/send_license")
def get_licence():
    """Gets the license plate information from the PI and processes it"""
    data = request.form
    license_plate = data["platenumber"]
    spot = data["spot"]
    if license_plate:
        spots[spot] = create_document(license_plate, spot)
        result = {"success": True}
    else:
        result = {"success": False}
    return flask.jsonify(result=result)


@app.route("/update_lot")
def update_lot():
    """Updates the cost of the lot in the database"""
    data = request.form
    exists = data["exists"]
    spot = data["spot"]
    update_document(spots[spot])
    if not exists:
        cost = close_transaction(spots[spot])
    return flask.jsonify(result={"cost": cost})


if __name__ == "__main__":
    app.run()
