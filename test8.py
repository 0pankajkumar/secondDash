import json
import datetime
from pymongo import MongoClient, CursorType, DESCENDING, ASCENDING
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
import datetime

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["antDB"]

collection.create_index([("Posting Department",ASCENDING), ("Posting Team",ASCENDING), ("Posting Title",ASCENDING)])
# collection.create_index([("Posting Department",DESCENDING)])