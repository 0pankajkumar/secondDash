from pymongo import MongoClient, CursorType
from bson import json_util, ObjectId
from bson.int64 import Int64
import datetime

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["dolphinDB"]

rows = collection.find({})

setOfProfilePostingID = set()

for row in rows:
    if isinstance(row['Posting ID'], datetime.date):
        continue
    if isinstance(row['Profile ID'],datetime.date):
        continue
    tmp = row['Posting ID'] + ' ' + row['Profile ID']

    if tmp not in setOfProfilePostingID:
        setOfProfilePostingID.add(tmp)
    else:
        print('Profile ID')
        break
