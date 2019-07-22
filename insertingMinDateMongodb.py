import flask
from pymongo import MongoClient, CursorType
import json
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
import datetime

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["antDB"]

rows = collection.find(cursor_type=CursorType.EXHAUST)

def checkFun(row, box, vari):
	try:
		if row[vari] != None:
			box.append(row[vari])
	except:
		print(f"Error with {row['_id']} and {vari}")

try:
	for row in rows:
		box = list()
		all_The_Stages = ['Stage - New lead', 'Stage - Reached out', 'Stage - Responded', 'Stage - New applicant', 'Stage - Recruiter screen', 'Stage - Profile review', 'Stage - Case study', 'Stage - Phone interview', 'Stage - On-site interview', 'Stage - Offer']
		for stage in all_The_Stages:
			checkFun(row, box, stage)

		try:
			minDict = {}
			minDict['Min Date'] = min(box)
		except:
			minDict = {}
			minDict['Min Date'] = None
			print("Inserting None MinDate")

		collection.update_one(
		   {'_id': row['_id']},
		   {'$set' : minDict
		    }
		)
finally:
	client.close()

