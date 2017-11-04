# NFCity Server

This server is intended to run on AWS. It will do the handling of
giving requests from the NFC station, and it will do image processing
that is sent from the RaspberryPi. The license plate processing is
based on [openalpr](https://github.com/openalpr/openalpr/wiki/Compilation-instructions-(Ubuntu-Linux))
.

## Author
Taisei Klasen

## HackGSU
This is part of the HackGSU project

## Team
Jonathan Lopez

## Dependencies
Since the server uses openalpr, the server will need to run
these commands:
sudo apt-get update && sudo apt-get install -y openalpr openalpr-daemon openalpr-utils libopenalpr-dev

Additionally, the server is based on a Flask framework. This means that
the files will run on a virtual environment with some dependencies there.

## Database

The database that will be storing the information will be hosted on
Mlab, so it will be a MongoDB database.


# Documentation

## Starting a lot
to start a lot, first encode information into a JSON file like this:

{ card: card info (string),
  lot: lot number (int) }

Then send a GET request to this url with the JSON:

http://NFCityServer.com/start_lot

Then the server will send back a JSON file formatted as:

{ start: True or False (boolean)
  transaction: number (int) }

If start is true, then that means that the server started to log that parking
lot and started calculating costs. It will send back a special ID number
that is related to that transaction. The NFC pole should store this transaction
number.

Once the transaction has started, the NFC pole should send this request about
every 30 seconds with this encoding of JSON:

{ transaction: number (int) }

to this url (GET request please):

http://NFCityServer.com/check_lot

the server will then respond with this JSON:

{ cost: number (float),
  final: True or False (bool)}

The cost is how much the lot costs in that moment.
If final is true, then that means the car is gone - the NFC pole
can stop sending requests over. In a final product, the NFC pole will
then charge the customer that amount of money. IF final is false, then
the NFC pole should send this check_lot url again in 30 seconds or so.