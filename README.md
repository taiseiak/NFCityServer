# NFCity Server

This server is intended to run on AWS. It will do the handling of
giving requests from the NFC station, and it will read and write informaton
to the database. Additionally, it will do payments through the Softheon API.

## Author
Taisei Klasen

## HackGSU
This is part of the HackGSU project

## Team
Jonathan Lopez

## Dependencies
Additionally, the server is based on a Flask framework. This means that
the files will run on a virtual environment with some dependencies there.

## Database

The database that will be storing the information will be hosted on
Mlab, so it will be a MongoDB database.


# Documentation

## Starting a lot

There will be a POST request from the Docker that holds the information
of the license plate info. They will send over what spot and what the number
is. This will store the lot to a transaction in an internal dictionary.

When there is a request from the NFC reader, the frequency of the user to
that spot, and the card info will be updated for the transaction.

There will be information every 30 seconds from the PI on if the
car exists there or not. Once the car goes away, the server will do transactions
with the softheon api.