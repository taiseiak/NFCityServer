"""
Main server that will be running the calls back and forth from the pi.
This server will also do any image processing.
"""

import flask
from flask import request
from database import update_document_card, update_document,\
    create_document, close_transaction

# Globals
application = flask.Flask(__name__)

spots = {
    1: "",
    2: ""
}


# Dummy url routing
@application.route("/")
def hello():
    return "Hello, World!"


# Main API routing
@application.route("/send_card", methods=["POST"])
def update_card():
    """Adds the card information to the document"""
    data = request.form
    card = data["card"]
    spot = data["spot"]
    success = update_document_card(card, spots[spot])
    result = {"success": success}
    return flask.jsonify(result=result)


@application.route("/send_license", methods=["POST"])
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


@application.route("/update_lot", methods=["POST"])
def update_lot():
    """Updates the cost of the lot in the database"""
    data = request.form
    exists = bool(data["exists"])
    spot = data["spot"]
    cost = update_document(spots[spot])
    if not exists:
        cost = close_transaction(spots[spot])
        del spots[spot]
    return flask.jsonify(result={"cost": cost})


if __name__ == "__main__":
    application.run()
