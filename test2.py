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


def countingMachine(results, postingDepartment, postingTeam, postingTitle, postingArchiveStatus, postingID, origin, countingVariable, stage):
	if postingDepartment is None:
		postingDepartment = {'$regex':'.'}
	if postingTeam is None:
		postingTeam = {'$regex':'.'}
	if postingTitle is None:
		postingTitle = {'$regex':'.'}
	if postingArchiveStatus is None:
		postingArchiveStatus = {'$regex':'.'}

	# print(postingDepartment)
	# print(postingTeam)
	# print(postingTitle)
	# print(postingArchiveStatus)
	# print(postingID)
	# print(origin)
	# print(countingVariable)
	# print(stage)
	# print("\n")
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
	    	#print(doc)
	    	count += 1
	    #print(count)
	finally:
	    client.close()
	print(count)
	if(len(results) == 0):
		results[0]['_children'][countingVariable] = count
	else:
		for p in range(len(results)):
			results[p]['_children'][countingVariable] = count


results = []
temp = dict()
temp['Posting ID'] = "70ed7df5-faa0-4754-bcb3-a28cb0510b90"
temp['_children'] = dict()
results.append(temp)
countingMachine(results, None, None, "Head- IT Infrastructure", None, "70ed7df5-faa0-4754-bcb3-a28cb0510b90", "applied", "recruiterScreenCount", "Stage - Phone interview")
countingMachine(results, None, None, "Strategic Partner Manager", None, "ed7a6b28-f5f1-48d0-89bc-61d55bdb76fa", "applied", "newApplicantCount", "Stage - New applicant")
print(results)