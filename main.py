# SETTING UP THE DATABASE
import pymongo
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false')
db = client.adm_db

## INSERT TEST DATA
def insert_test_data():
  result = db.ships.insert_one({
     "ship": "Black Pearl"
  })

# insert_test_data()

## TEST QUERY
def test_query():
  result = db.ships.find( {"$or":
                          [ 
                            {"ship": {"$exists": True}},
                            {"flag": {"$exists": True}}
                          ] } )

  for doc in result:
    print(doc)

# test_query()

## TRANSFORM CSV TO JSON



