"""
Library that writes information into the database.
"""
import pymongo
import arrow
import bson
import base64
import softheon

key = 'a4337bc45a8fc544c03f52dc550cd6e1e87021bc896588bd79e901e2df2j'

softheon_client = "1f18b0ea-46b0-4b07-87cb-7894df80b973"
softheon_secret = "69c9d7f7-2507-4d73-9044-754a4cf07287"
TRIVIAL_ADDRESS = {
    'address1': '111 test',
    'address2': '111 test',
    'city': 'Stony Brook',
    'state': 'NY',
    'zipCode': '11111'
}
TRIVIAL_CARD = softheon.CreditCard(4134185779995000,
                                   123,
                                   3,
                                   2017,
                                   'Test',
                                   TRIVIAL_ADDRESS,
                                   'example@example.com')

MONGO_CLIENT_URL = "mongodb://lot_one:hackGSU@ds147265.mlab.com:47265/nfcity"
dbclient = pymongo.MongoClient(MONGO_CLIENT_URL)
database = dbclient.nfcity
transaction_cl = database.transactions
spot_rist_cl = database.spotrisk
userinfo_cl = database.userinfo

DOLLARS_PER_HOUR = float(60)


def create_document(license_plate, spot):
    """Adds a new entry to the database

    The information added is the card, the lot, the license plate number,
    and the time that this information was added into the database.

    Args:
        spot: int, specifying what spot
        license_plate: license plate number

    Returns:
        a unique transaction string number that corresponds to that
        transaction.
    """
    time = arrow.now()
    entry = {"card": "UNDEFINED",
             "spot": encode(key, spot),
             "license_plate": encode(key, license_plate),
             "time": encode(key, time.isoformat()),
             "cost": encode(key, 0),
             "softheon": "UNDEFINED"}
    transaction = transaction_cl.insert_one(entry).inserted_id
    return str(transaction)


def update_document_card(card, transaction):
    """Updates the card information for the parking spot

    Args:
        card: string with card information
        transaction: unique id string

    Returns:
        True if successful else False
    """
    tr = bson.objectid.ObjectId(transaction)
    try:
        transaction_cl.update_one({"_id": tr},
                                  {"$set": {"card": encode(key, card)}})
        entry = transaction_cl.find_one({"_id": tr})
        print(entry)
        userid = entry["license_plate"]
        spot = entry["spot"]
        user = userinfo_cl.find_one({"user_id": userid})
        if user:
            prev_freq = user["spots"][spot]
            userinfo_cl.update_one({"user_id": userid},
                                   {"$set":
                                        {"spots": {spot: encode(key,
                                                                prev_freq + 1)}}},
                                   upsert=True)
        else:
            new_user = {"user_id": encode(key, userid),
                        "spots": {spot: encode(key, 1)}}
            userinfo_cl.insert_one(new_user)
    except ValueError:
        return False
    return True


def close_transaction(transaction):
    """Close the transaction, sending a request to softheon

    Args:
        transaction: unique id string
    """
    tr = bson.objectid.ObjectId(transaction)
    entry = transaction_cl.find_one({"_id": tr})
    begin_time = arrow.get(decode(key, entry["time"]))
    hours = (begin_time - arrow.now()).seconds / 3600
    cost = format(float(hours * DOLLARS_PER_HOUR), ".2f")
    transaction_cl.update_one({"_id": tr},
                              {"$set": {"cost": encode(cost)}})
    access_token = softheon.retrieve_access_token(softheon_client,
                                                  softheon_secret)
    credit_card_token = softheon.retrieve_credit_card_token(TRIVIAL_CARD,
                                                            access_token)
    resp_json = softheon.make_payment(access_token,
                                      credit_card_token, float(cost))
    if str(resp_json['result']['status']) == 'Authorized':
        result = {"success": True}
    else:
        result = {"success": False}
    return result


def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()


def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)
