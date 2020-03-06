import csv  
import json
import datetime
from pymongo import MongoClient, CursorType
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
import datetime  


client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["ApprovedUsers"]

makeAdmin = True
addThisUser = "pankajkum@directi.com"

if makeAdmin == True:
    collection.insert_one({"users": addThisUser, "type":"admin"})
else:
    collection.insert_one({"users": addThisUser, "type":"regular"})

#pa = collection.find({})
#usersList = list()
#for p in pa:
#	usersDict = dict()
#	usersDict['users'] = p['users']
#	usersDict['type'] = p['type']
#	usersList.append(usersDict)
#	print(p["users"])

# print(usersList)

# Deleteing or Dropping the collection
# collection.delete_many({})

# rows = collection.find({"users": "pankajkum@directi.com"}, cursor_type=CursorType.EXHAUST)

# if rows:
# 	# Do something else
# 	collection.update_one({"users":"pankajkum@directi.com"}, {"$set":{'type':'admin'}})
# else:
# 	collection.insert_one({"users":"pankajkum@directi.com", "type":"admin"})

