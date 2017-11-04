"""
Library that writes information into the database.
"""
import pymongo
import arrow
import bson

MONGO_CLIENT_URL = "mongodb://lot_one:hackGSU@ds147265.mlab.com:47265/nfcity"
dbclient = pymongo.MongoClient(MONGO_CLIENT_URL)
database = dbclient.nfcity
transaction_cl = database.transactions
spot_rist_cl = database.spotrisk
userinfo_cl = database.userinfo

DOLLARS_PER_HOUR = float(120)


def create_document(license_plate, lot):
    """Adds a new entry to the database

    The information added is the card, the lot, the license plate number,
    and the time that this information was added into the database.

    Args:
        lot: int, specifying what lot
        license_plate: license plate number

    Returns:
        a unique transaction string number that corresponds to that
        transaction.
    """
    time = arrow.now()
    entry = {"card": "UNDEFINED",
             "lot": lot,
             "license_plate": license_plate,
             "time": time.isoformat(),
             "cost": 0,
             "softheon": "UNDEFINED"}
    transaction = transaction_cl.insert_one(entry).inserted_id
    return str(transaction)


def update_document(transaction):
    """Update the document

    Updates the document for that specific transaction.

    Args:
        transaction: unique id string

    Returns:
        the amount that transaction currently costs in a float format
    """
    tr = bson.objectid.ObjectId(transaction)
    entry = transaction_cl.find_one({"_id": tr})
    begin_time = arrow.get(entry["time"])
    hours = (begin_time - arrow.now()).seconds / 3600
    cost = format(float(hours * DOLLARS_PER_HOUR), ".2f")
    transaction_cl.update_one({"_id": transaction},
                              {"$set": {"cost": cost}})
    return cost


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
        transaction_cl.update_one({"_id": tr}, {"$set": {"card": card}})
        entry = transaction_cl.find_one({"_id": tr})
        userid = entry["license_plate"]
        spot = entry["spot"]
        user = userinfo_cl.find_one({"user_id": userid})
        if user:
            prev_freq = user["spots"][spot]
            userinfo_cl.update_one({"user_id": userid},
                                   {"$set": {"spots": {spot: prev_freq + 1}}},
                                   upsert=True)
        else:
            new_user = {"user_id": userid, "spots": {spot: 1}}
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
    return True
