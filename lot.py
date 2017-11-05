"""
Main server that will be running the calls back and forth from the pi.
This server will also do any image processing.
"""

import flask
from flask import request
from database import update_document_card,\
    create_document, close_transaction
from block_crypto import decrypt_json

key = 'a4337bc45a8fc544c03f52dc550cd6e1e87021bc896588bd79e901e2df2j'

# Globals
application = flask.Flask(__name__)

spots = {}


# Dummy url routing
@application.route("/")
def hello():
    return "Hello, World!"


# Main API routing
@application.route("/send_card", methods=["POST"])
def update_card():
    """Adds the card information to the document"""
    data = request.form
    ciphertext = data["ciphertext"]
    hashvalue = data["hashvalue"]
    try:
        json = decrypt_json(ciphertext, hashvalue, 'dragon')
        card = json["card"]
        spot = json["spot"]
        transaction = spots[spot]
        spots[spot] = update_document_card(card, transaction)
        result = {"success": True}
    except KeyError:
        result = {"success": False}
    except ValueError:
        result = {"success": False}
    return flask.jsonify(result=result)


@application.route("/send_license", methods=["POST"])
def get_licence():
    """Gets the license plate information from the PI and processes it"""
    data = request.form
    ciphertext = data["ciphertext"]
    hashvalue = data["hashvalue"]
    try:
        json = decrypt_json(ciphertext, hashvalue, 'pi')
        license_plate = json["platenumber"]
        spot = json["spot"]
        spots[spot] = create_document(license_plate, spot)
        result = {"success": True}
    except ValueError:
        result = {"success": False}
    return flask.jsonify(result=result)


@application.route("/end_transaction", methods=["POST"])
def update_lot():
    """Updates the cost of the lot in the database"""
    data = request.form
    ciphertext = data["ciphertext"]
    hashvalue = data["hashvalue"]
    try:
        json = decrypt_json(ciphertext, hashvalue, 'pi')
        spot = json["spot"]
        transaction = spots[spot]
        spots[spot] = close_transaction(transaction)
        result = {"success": True}
    except ValueError:
        result = {"success": False}
    return flask.jsonify(result=result)


if __name__ == "__main__":
    application.run()
