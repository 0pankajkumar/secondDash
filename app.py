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
	    	# print(doc['Posting ID'])
	    	uniquePostingIDs.append(doc['Posting ID'])
	finally:
	    client.close()


	#Getting related Origins
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
	    	#print(doc)
	    	relatedOrigins.append(doc)
	finally:
	    client.close()

	results = []



	# print(f'postingDepartment : {postingDepartment}')
	# print(f'postingTeam: {postingTeam}')
	# print(f'postingTitle : {postingTitle}')
	# print(f'postingArchiveStatus : {postingArchiveStatus}')

	for pos in uniquePostingIDs:
		temp = dict()
		temp['Posting ID'] = pos
		temp['_children'] = dict()
		results.append(temp)

		for ori in relatedOrigins:
			# print(f'{type(ori["Origin"])} : {ori["Origin"]}')
			# print(f'{type(pos)} : {pos}')
			#fetching all counts
			print(f'{postingDepartment}\n {postingTeam}\n {postingTitle}\n {postingArchiveStatus}\n {pos}\n {ori["Origin"]}\n "NewApplicantCount"\n "Stage - New applicant"')
			print("\n")
			# countingMachine(results, postingDepartment, postingTeam, postingTitle, postingArchiveStatus, pos, ori["Origin"], "NewApplicantCount", "Stage - New applicant")
			# countingMachine(results, postingDepartment, postingTeam, postingTitle, postingArchiveStatus, pos, ori["Origin"], "ProfileReviewCount", "Stage - Profile Review")
			# countingMachine(results, postingDepartment, postingTeam, postingTitle, postingArchiveStatus, pos, ori["Origin"], "RecruiterScreenCount", "Stage - Recruiter screen")
			# countingMachine(results, postingDepartment, postingTeam, postingTitle, postingArchiveStatus, pos, ori["Origin"], "CaseStudyCount", "Stage - Case study")
			# countingMachine(results, postingDepartment, postingTeam, postingTitle, postingArchiveStatus, pos, ori["Origin"], "PhoneInterviewCount", "Stage - Phone interview")
			# countingMachine(results, postingDepartment, postingTeam, postingTitle, postingArchiveStatus, pos, ori["Origin"], "OnsiteInterviewCount", "Stage - On-site interview")
			# countingMachine(results, postingDepartment, postingTeam, postingTitle, postingArchiveStatus, pos, ori["Origin"], "OfferCount", "Stage - Offer")

			# countingMachine(results, None, None, "Head- IT Infrastructure", None, "70ed7df5-faa0-4754-bcb3-a28cb0510b90", "applied", "recruiterScreenCount", "Stage - Phone interview")
			countingMachine(results, None, None, "Strategic Partner Manager", None, "4cd7ba07-9cc4-49a9-b4bc-288a936cfb70", "applied", "recruiterScreenCount", "Stage - Recruiter screen")


	return jsonify(results)

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
	    	count += 1
	    	#print(doc)
	    #print(count)
	finally:
	    client.close()
	#print(count)
	if(len(results) == 0):
		results[0]['_children']['origin'] = origin
		results[0]['_children'][countingVariable] = count
	else:
		for p in range(len(results)):
			results[p]['_children']['origin'] = origin
			results[p]['_children'][countingVariable] = count
	#print(results)












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

	box = []
	box.append(postingDepartment)
	box.append(postingTeam)
	box.append(postingTitle)
	box.append(postingArchiveStatus)

	# box = {}
	# box['postingDepartment'] = postingDepartment
	# box['postingTeam'] = postingTeam
	# box['postingTitle'] = postingTitle
	# box['postingArchiveStatus'] = postingArchiveStatus
	return render_template('index.html', postingDepartment=postingDepartment, postingTeam=postingTeam, postingTitle=postingTitle, postingArchiveStatus=postingArchiveStatus)



if __name__ == '__main__':
	app.run(debug=True)
























#Last
