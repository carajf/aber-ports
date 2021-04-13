# IMPORTING REQUIRED MODULES
from pprint import pprint



# CONNECTING TO THE DATABASE
import pymongo
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client.aber_ship_db
coll = db.aber_ships



## PRACTISING SOME QUERYING
def vess_Loyalty():
  query = { "vessel name": "Loyalty" }
  result = coll.find(query)
  for doc in result:
    pprint(doc)

# vess_Loyalty()



## SAMPLE FORMATTING
def show_formatting():
  """Prints a document to the console to show how the document is formatted. Useful for finding out the correct querying syntax."""

  query = [ { "$sample": { "size": 1} }
          ]
  result = coll.aggregate(query)
  for doc in result:
    pprint(doc)

# show_formatting()



## LIST SAILORS FOR SELECTION
def extract_sailors():
  """Gathers all of the sailor information from each document in the collection (aka from each ship log upon visiting Aberystwyth).

  Stores these sailors in some sort of data structure, ready to be retrieved."""

  # Preparing a list in which sailors will be stored
  sailors = []

  # Finding any mariner arrays which have more than 0 entries
  filter_array_length = { "mariners.0": {"$exists": True} }
  
          
  result = coll.find(query)
  for doc in result:
    pprint(doc)

  

  # Count and group mariners
  # grouped_mariner_counts = [ { "$project": {"_id": False, "vessel name": True, "count_mariners": {"$size": "$mariners"} } },
  #                        { "$group": {"_id": "$vessel name", "total_mariners": {"$sum": "$num_mariners"} } }
  #                      ]
  
  # result = coll.aggregate(grouped_mariner_counts)
  # for doc in result:
  #   print(doc)

extract_sailors()







  
  
  






