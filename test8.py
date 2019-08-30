import json
import datetime
from pymongo import MongoClient, CursorType
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
import datetime

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["antDB"]

o = collection.find_one({})
# for o in ob:
timestamp = str(o['_id'])
timestamp = timestamp[0:8]
timestamp = int(timestamp,16)

timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
print(timestamp)
# break