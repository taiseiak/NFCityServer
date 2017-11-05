"""
Main server that will be running the calls back and forth from the pi.
This server will also do any image processing.
"""

import json

import flask
import requests
from flask import request

from block_crypto import decrypt_json
from database import update_document_card,\
    create_document, close_transaction

key = 'a4337bc45a8fc544c03f52dc550cd6e1e87021bc896588bd79e901e2df2j'

# Globals
application = flask.Flask(__name__)

spots = {}


# Dummy url routing
@application.route("/")
def hello():
    return "Hello, World!"


# Main API routing
@application.route("/send_card")
def update_card():
    """Adds the card information to the document"""
    data = request.args
    card = data["card"]
    spot = str(data["spot"])
    transaction = spots[spot]
    spots[spot] = update_document_card(card, transaction)
    result = {"success": True}
    return flask.jsonify(result=result)


@application.route("/send_license", methods=["POST"])
def get_licence():
    """Gets the license plate information from the PI and processes it"""
    data = request.form
    ciphertext = data["ciphertext"]
    print(ciphertext)
    hashvalue = data["hashvalue"]
    ret_json = decrypt_json(hashvalue, ciphertext, "pi")
    print(ret_json)
    try:
        """
        ret_json = subprocess.check_output(['python2.7', 'block_crypto.py',
                                            'hashjson',  'pi'])
        # ret_json = json.load(ret_json)
        print(ret_json.decode("utf8"))
        """
        ret_json = json.loads(ret_json)
        print(ret_json)
        license_plate = ret_json["platenumber"]
        spot = ret_json["spot"]
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
