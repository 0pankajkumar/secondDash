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

@app.route('/test1', methods=['GET'])
def test1():
	return render_template('test1.html')

@app.route('/getTable', methods=['POST'])
def getTable():
	# print("Received")
	# print(request.form.get('postingTitle'))
	# print(request.form.get('companyName'))
	# print(request.form.get('postingTeam'))
	# print(request.form.get('postingArchiveStatus'))
	# print(type(request.form.get('postingTitle')))

	


	if request.form.get('postingTitle') == "All":
		postingTitle = None
	else:
		postingTitle = request.form.get('postingTitle')

	if request.form.get('companyName') == "All":
		postingDepartment = None
	else:
		postingDepartment = request.form.get('companyName')

	if request.form.get('postingTeam') == "All":
		postingTeam = None
	else:
		postingTeam = request.form.get('postingTeam')

	if request.form.get('postingArchiveStatus') == "Both":
		postingArchiveStatus = None
	else:
		postingArchiveStatus = request.form.get('postingTeam')

	# Getting all related Posting IDs for respective posting title
	pipeline = [
	    {
	        u"$match": {
	            u"Posting Title": postingTitle
	        }
	    }, 
	    {
	        u"$project": {
	            u"Posting ID": u"$Posting ID",
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
	uniquePostingIDs = []
	try:
	    for doc in cursor:
	    	uniquePostingIDs.append(doc['Posting ID'])
	finally:
	    client.close()


	# Getting related Origins
	pipeline = [
	    {
	        u"$match": {
	            u"Posting Title": postingTitle
	        }
	    }, 
	    {
	        u"$project": {
	            u"Origin": u"$Origin",
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
	relatedOrigins = []
	try:
	    for doc in cursor:
	    	relatedOrigins.append(doc['Origin'])
	finally:
	    client.close()

	results = []

	i = 0

	for pos in uniquePostingIDs:
		temp = dict()
		temp['Posting ID'] = pos
		temp['_children'] = []
		results.append(temp)
		for ori in relatedOrigins:
			temp = dict()
			temp['origin'] = ori
			results[i]['_children'].append(temp)
			pos = pos
			countingMachine(results, postingDepartment, postingTeam, postingTitle, None, str(pos), ori, "newApplicantCount", "Stage - New applicant")
			countingMachine(results, postingDepartment, postingTeam, postingTitle, None, str(pos), ori, "recruiterScreenCount", "Stage - Recruiter screen")
			countingMachine(results, postingDepartment, postingTeam, postingTitle, None, str(pos), ori, "phoneInterviewCount", "Stage - Phone interview")
			countingMachine(results, postingDepartment, postingTeam, postingTitle, None, str(pos), ori, "onsiteInterviewCount", "Stage - On-site interview")
			countingMachine(results, postingDepartment, postingTeam, postingTitle, None, str(pos), ori, "offerCount", "Stage - Offer")
			countingMachine(results, postingDepartment, postingTeam, postingTitle, None, str(pos), ori, "newLeadCount", "Stage - New lead")
			countingMachine(results, postingDepartment, postingTeam, postingTitle, None, str(pos), ori, "reachedOutCount", "Stage - Reached out")
		i += 1

	return jsonify(results)

def getFromDB(companyName): # title, companyName, team, archiveStatus):
    # collection.drop()
    # collection.insert_one({'posting_id' : randint(1,10), 'origin' : randint(1,3), 'Stage - New Lead' : '2019-01-01'})
    # collection.insert_one({'posting_id' : randint(1,10), 'origin' : randint(1,3), 'Stage - Recruiter Screen': '2019-02-02'})
    query = dict()
    if companyName != 'All':
        query['Posting Department'] = companyName
        # query['Posting Title'] = title
        # query['Posting Team'] = team
        # query['Posting Archive Status'] = archiveStatus
    return list(collection.find(query, cursor_type=CursorType.EXHAUST))


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
	
	# Counting values
	pipeline = [
	    {
	        u"$match": {
	            u"Posting Department": postingDepartment,
	            u"Posting Team": postingTeam,
	            u"Posting Title": postingTitle,
	            u"Posting Archive Status": postingArchiveStatus,
	            u"Posting ID": postingID,
	            u"Origin": origin,
	            stage: {
                u"$ne": None
            }
	        }
	    }, 
	    {
	        u"$project": {
	            stage: f"${stage}",
	            u"Application ID": u"$Application ID",
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
	if(len(results) == 0):
		results[0]['_children']['origin'] = origin
		results[0]['_children'][countingVariable] = count
	else:
		for p in range(len(results)):
			if results[p]['Posting ID'] == postingID:
				# notFound is a flag
				notFound = True
				for q in range(len(results[p]['_children'])):
					if results[p]['_children'][q]['origin'] == origin:
						results[p]['_children'][q][countingVariable] = count



@app.route('/', methods=['GET'])
def uidropdowns():
	postingDepartment = []
	postingTeam = []
	postingTitle = []
	postingArchiveStatus = []


	#Getting Posting Department
	pipeline = [
	    {
	        u"$project": {
	            u"Posting Department": u"$Posting Department",
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
	
	try:
	    for doc in cursor:
	    	if doc['Posting Department'] == 'Kapow' or doc['Posting Department'] == 'None' or doc['Posting Department'] == 'Yikes! No Releveant Roles':
	    		continue
	    	else:
	        	postingDepartment.append(doc)
	finally:
	    client.close()

	

	#Fetching Posting Team
	pipeline = [
	    {
	        u"$project": {
	            u"Posting Team": u"$Posting Team",
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
	
	try:
	    for doc in cursor:
	    	if doc['Posting Team'] == 'Refer your buddy as per function' or doc['Posting Team'] == 'None':
	    		continue
	    	else:
	        	postingTeam.append(doc)
	finally:
	    client.close()


	#Fetching Posting Title
	pipeline = [
	    {
	        u"$project": {
	            u"Posting Title": u"$Posting Title",
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
	
	try:
	    for doc in cursor:
	        postingTitle.append(doc)
	finally:
	    client.close()


	#Fetching Posting Archive Status
	pipeline = [
	    {
	        u"$project": {
	            u"Posting Archive Status": u"$Posting Archive Status",
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
	
	try:
	    for doc in cursor:
	        postingArchiveStatus.append(doc)
	finally:
	    client.close()

	return render_template('index.html', postingDepartment=postingDepartment, postingTeam=postingTeam, postingTitle=postingTitle, postingArchiveStatus=postingArchiveStatus)



if __name__ == '__main__':
	app.run(debug=True)
























#Last
