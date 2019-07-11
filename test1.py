import flask
from flask import request, jsonify, render_template, url_for
from pymongo import MongoClient
import json
from bson import json_util, ObjectId
from bson.int64 import Int64
import datetime

app = flask.Flask(__name__,static_url_path='',
            static_folder='static',
            template_folder='templates')
app.config["DEBUG"] = True

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["antDB"]

postingDepartment = {'$regex':'.'}
postingTeam = {'$regex':'.'}
postingTitle = "Product Manager"
postingArchiveStatus = {'$regex':'.'}
postingID = "1dac0efc-31ed-4948-94c9-751ea09778b9"
origin = "applied"
countingVariable = "recruiterScreenCount"
stage = "Stage - Recruiter screen"

print(postingDepartment)
print(postingTeam)
print(postingTitle)
print(postingArchiveStatus)
print(postingID)
print(origin)
print(countingVariable)
print(stage)

#Counting values
pipeline = [
    {
        u"$match": {
            u"Posting Department": postingDepartment,
            u"Posting Team": postingTeam,
            u"Posting Title": postingTitle,
            u"Posting Archive Status": postingArchiveStatus,
            u"Posting ID": postingID,
            u"Origin": origin
        }
    }, 
    {
        u"$project": {
            stage: f"${stage}",
            u"_id": 0
        }
    }, 
    {
        u"$group": {
            u"_id": None,
            u"distinct": {
                u"$addToSet": u"$$ROOT"
            }
        }
    }, 
    {
        u"$unwind": {
            u"path": u"$distinct",
            u"preserveNullAndEmptyArrays": False
        }
    }, 
    {
        u"$replaceRoot": {
            u"newRoot": u"$distinct"
        }
    }
]

cursor = collection.aggregate(
    pipeline, 
    allowDiskUse = True
)
count = 0
try:
    for doc in cursor:
    	count += 1
finally:
    client.close()
print(count)