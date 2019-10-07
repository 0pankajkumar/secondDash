import json
import datetime
from pymongo import MongoClient, CursorType, DESCENDING, ASCENDING
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
import datetime
import sys

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["dolphinDB"]

rows = collection.find({})

currentStages = ['New lead', 'Reached out', 'Responded', 'New applicant',	'Recruiter screen',	'Profile review', 'Case study', 'Phone interview', 'On-site interview', 'Offer', 'Offer Approval', 'Offer Approved']
postingDict = {}

def addPostingToPostingDict(ro):
	if ro['Posting ID'] and ro['Profile ID'] is not None:
		pst = ro['Posting ID']
		prfl = ro['Profile ID']
	else:
		return

	if pst not in postingDict:
		postingDict[pst] = {}
		postingDict[pst][prfl] = ro
	else:
		if prfl not in postingDict[pst]:
			postingDict[pst][prfl] = ro

		else:
			stg1 = postingDict[pst][prfl]['Current Stage']
			stg2 = ro['Current Stage']

			if currentStages.index(stg2) < currentStages.index(stg1):
				postingDict[pst][prfl] = ro
			# postingDict[pst][prfl] = ro
				

y = 0
for row in rows:
	addPostingToPostingDict(row)

print(sys.getsizeof(postingDict))
# print(postingDict)

# collection2 = database["filteredDB"]


# for x in postingDict.keys():
# 	for y in postingDict[x].keys():
# 		collection2.insert_one(postingDict[x][y])


	