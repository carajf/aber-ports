# IMPORTING REQUIRED MODULES
from pprint import pprint

# CONNECTING TO THE DATABASE
import pymongo
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.aber_ship_db
col = db.aber_ships





