# transfer ship data to a MongoDB collection

# get a connection to MongoDB
from pymongo

user = 'eds'
dbpath = 'nosql.dcs.aber.ac.uk/eds'
password = '*********'
connection_string = 'mongodb://'+user+':'+password+'@'+dbpath

client = pymongo.MongoClient(connection_string)

db = client.eds

# walk the ship data directory to find the excel files

import os
import get_ships

all_ships = []

ships_dir = '/aber/eds/mongodb/prac2/ABERSHIP_transcription_vtls004566921/ABERSHIP_transcription_vtls004566921'

for root, dirs, files in os.walk(ships_dir):
    for file in files:
        name, ext = os.path.splitext(file)
        if ext == '.xlsx':
            all_ships += get_ships.get_ships( os.path.join(root, file) )

result = db.eds.insert_many(all_ships)
print(result)
