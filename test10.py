from pymongo import MongoClient, CursorType
from bson import json_util, ObjectId
from bson.int64 import Int64
import datetime

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["gooseDB"]

rows = collection.find({})

setOfProfilePostingID = set()
setOfProfilePostingIDAlreadyThere = set()

dictOfProfilePostingID = dict()
dictOfProfilePostingIDAlreadyThere = dict()

class box:
    def __self__(self, idOfObj, CreatedAt):
        _id = idOfObj
        date = CreatedAt

listOfBoxes = []


for row in rows:
    if isinstance(row['Posting ID'], datetime.date) or row['Posting ID'] is None:
        continue
    if isinstance(row['Profile ID'],datetime.date):
        continue




    tmp = row['Posting ID'] + '-%-' + row['Profile ID']

    if tmp not in dictOfProfilePostingID:
        ob = box(row['_id'], row['Created At (GMT)'])

    elif dictOfProfilePostingID[tmp][0]
        setOfProfilePostingIDAlreadyThere.add(tmp)




print(len(setOfProfilePostingID))
print()
print(len(setOfProfilePostingIDAlreadyThere))




#     tmp = row['Posting ID'] + ' ' + row['Profile ID']

#     if tmp not in setOfProfilePostingID:
#         setOfProfilePostingID[tmp] = {row['_id'] : row['Created At (GMT)']}
#     else:
#         setOfProfilePostingID[tmp][row['_id']] : row['Created At (GMT)']
        

# for key,value in setOfProfilePostingID.items():
#     if len(value) > 1:
#         print(value)

# print(setOfProfilePostingID)
