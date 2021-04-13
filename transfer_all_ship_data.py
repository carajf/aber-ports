### PYTHON SCRIPT TO TRANSFER SHIP DATA TO A DOCUMENT DATABASE.

# Establish connection to mongodb.
import pymongo
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.aber_ship_db
coll = db.aber_mariners

# Import necessary modules (including get_records script which retrieves the data from the xlxs files and converts to JSON)
import os
import get_records

# Establish the list in which records will be stored
all_records = []

# Locating the root directory of all ship data
ships_dir = 'Data\ABERSHIP_transcription_vtls004566921'

# Initialising a unique key
u_key = 1

# Walking through each file in the directory
for root, dirs, files in os.walk(ships_dir):
    for file in files:
        name, ext = os.path.splitext(file)
        if ext == '.xlsx':

            # Adding the data in the csv->json file to the all_ships list
            the_records, u_key = get_records.get_records(os.path.join(root, file), u_key)
            all_records += the_records

# Printing to test the data is being read correctly before importing to the db
# from pprint import pprint
# pprint(all_records)

# Inserting the data in the all_ships list into the database
result = coll.insert_many(all_records)

# Printing the results of the insert command into the console (akak letting us know if the import is complete/successful)
print(result)
