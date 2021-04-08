### PYTHON SCRIPT TO TRANSFER SHIP DATA TO A DOCUMENT DATABASE.

# Establish connection to mongodb.
import pymongo
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client.aber_ship_db

# Import necessary modules (including get_ships script which retrieves the data from the xlxs files and converts to JSON)
import os
import get_ships

# Establish the list in which ships will be stored
all_ships = []

# Locating the root directory of all ship data
ships_dir = 'Data\ABERSHIP_transcription_vtls004566921'

# Walking through each file in the directory
for root, dirs, files in os.walk(ships_dir):
    for file in files:
        name, ext = os.path.splitext(file)
        if ext == '.xlsx':

            # Adding the data in the csv->json file to the all_ships list
            all_ships += get_ships.get_ships( os.path.join(root, file))

# Inserting the data in the all_ships list into the database
result = db.aber_ships.insert_many(all_ships)

# Printing the results of the insert command into the console
print(result)
