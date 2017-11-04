"""
Library that writes information into the database.
"""
import pymongo
import arrow

MONGO_CLIENT_URL = "mongodb://lot_one:hackGSU@ds147265.mlab.com:47265/nfcity"
dbclient = pymongo.MongoClient(MONGO_CLIENT_URL)
database = dbclient.nfcity
collection = database.parking_lot_one

DOLLARS_PER_HOUR = 1.5


def add_to_database(card, lot, license_plate):
    """Adds a new entry to the database

    The information added is the card, the lot, the license plate number,
    and the time that this information was added into the database.

    Args:
        card: card information, for now a string
        lot: int, specifying what lot
        license_plate: license plate number

    Returns:
        a unique transaction string number that corresponds to that
        transaction.
    """
    time = arrow.now()
    entry = {"card": card,
             "lot": lot,
             "license_plate": license_plate,
             "time": time.isoformat(),
             "cost": 0}
    transaction = collection.insert_one(entry).inserted_id
    return str(transaction)


def update_database(transaction):
    """Update the document

    Updates the document for that specific transaction.

    Args:
        transaction: unique id string

    Returns:
        the amount that transaction currently costs in a float format
    """
    entry = collection.find_one({"_id": transaction})
    begin_time = arrow.get(entry["time"])
    hours = (begin_time - arrow.now()).hour
    cost = float(hours * DOLLARS_PER_HOUR)
    collection.update_one({"_id": transaction},
                          {"cost": cost})
    return cost
