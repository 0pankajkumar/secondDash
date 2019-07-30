import flask
from flask import request, jsonify, render_template, url_for
from werkzeug import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads, UploadNotAllowed
from pymongo import MongoClient, CursorType
import json
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
from random import randint
import os
import datetime

app = flask.Flask(__name__, static_url_path='',
				  static_folder='static',
				  template_folder='templates')
app.config["DEBUG"] = False

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["dolphinDB"]


# configure flask_upload API
documents = UploadSet("documents", ('csv'))
app.config["UPLOADED_DOCUMENTS_DEST"] = "uploaded_csv"
configure_uploads(app, documents)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'GET':
		return render_template('uploader.html')
	elif request.method == 'POST':
		f = request.files['file']
		# print(f.filename, secure_filename(f.filename))
		file = documents.save(request.files['file'])
		# f = request.files['file']
		# f.save(secure_filename(f.filename))
		# os.remove(app.config["UPLOADED_DOCUMENTS_DEST"] + "/" + str())
		return 'file uploaded successfully'



@app.route('/test2', methods=['GET'])
def test1():
	return render_template('test2.html')

@app.route('/trial3', methods=['GET'])
def trial3():
	return render_template('trial3.html')

@app.route('/funnel', methods=['GET'])
def funnel():
	postingDepartment = set()
	postingArchiveStatus = set()
	rows = collection.find(cursor_type=CursorType.EXHAUST)
	for row in rows:
		flag = False
		if row['Posting Department'] == 'Kapow' or row['Posting Department'] == None or row['Posting Department'] == 'Yikes! No Relevant Roles' or row['Posting Department'] == "":
			continue
		else:
			postingDepartment.add(row['Posting Department'])
			flag = True
		postingArchiveStatus.add(row['Posting Archive Status'])
	return render_template('funnel.html', postingDepartment=postingDepartment, postingArchiveStatus = postingArchiveStatus)


@app.route('/getTable', methods=['POST'])
def getTable():
	# collection.createIndex('Posting Department')

	postingTitle = request.form.get('postingTitle')
	companyName = request.form.get('companyName')
	postingTeam = request.form.get('postingTeam')
	postingArchiveStatus = request.form.get('postingArchiveStatus')
	age = request.form.get('age')

	results = getResults(postingTitle, companyName, postingTeam, postingArchiveStatus, age)
	# results = getResults("Backend Engineer", "Flock", "Software Engineering", "All")
	return jsonify(results)


def getResults(title, companyName, team, archiveStatus, age):
	ts = time.time()
	rows = getFromDB(companyName) # title, companyName, team, archiveStatus
	print('db: ' + str(time.time() - ts))
	res = []
	counts = dict()
	benchmark_date = interpretAge(age)
	for item in rows:
		if item['Posting Title'] != title and title != 'All':
			continue
		if item['Posting Team'] != team and team != 'All':
			continue
		if item['Posting Archive Status'] != archiveStatus and archiveStatus != 'All' and archiveStatus != 'Both':
			continue
		
		if item['Min Date'] < benchmark_date:
			# print(f"{item['Min Date']} < {benchmark_date}")
			continue
		

		# Modified posting ID for display
		# item['Created At (GMT)'] =  datetime.datetime.strptime(str(item['Created At (GMT)']), '%Y-%m-%d %H:%M:%S').strftime('%B %Y')
		# postId = str(item['Posting ID']) + ", " + str(item['Posting Title']) + ", " + str(item['Posting Location']) + ", " + item['Created At (GMT)']

		if 'postingCreatedDate' in item:
			dateForLabel = str(item['postingCreatedDate'].strftime('%b')) + " " + str(item['postingCreatedDate'].strftime('%Y'))
		else:
			dateForLabel = "$"
		postId = str(item['Posting Title']) + ", " + str(item['Posting Location']) + ", " + dateForLabel 

		origin = item['Origin']
		if not postId in counts:
			counts[postId] = dict()
		if not origin in counts[postId]:
			counts[postId][origin] = dict()
			counts[postId][origin]['new_lead'] = 0
			counts[postId][origin]['reached_out'] = 0
			counts[postId][origin]['new_applicant'] = 0
			counts[postId][origin]['recruiter_screen'] = 0
			counts[postId][origin]['phone_interview'] = 0
			counts[postId][origin]['onsite_interview'] = 0
			counts[postId][origin]['offer'] = 0
		originCounts = counts[postId][origin]
		
		if 'Stage - New lead' in item and item['Stage - New lead'] != None:
			originCounts['new_lead'] += 1
		if 'Stage - Reached out' in item and item['Stage - Reached out'] != None:
			originCounts['reached_out'] += 1
		if 'Stage - New applicant' in item and item['Stage - New applicant'] != None:
			originCounts['new_applicant'] += 1
			# print(item['Profile ID'])	
		if 'Stage - Recruiter screen' in item and item['Stage - Recruiter screen'] != None:
			originCounts['recruiter_screen'] += 1
		if 'Stage - Phone interview' in item and item['Stage - Phone interview'] != None:
			originCounts['phone_interview'] += 1
		if 'Stage - On-site interview' in item and item['Stage - On-site interview'] != None:
			originCounts['onsite_interview'] += 1
		if 'Stage - Offer' in item and item['Stage - Offer'] != None:
			originCounts['offer'] += 1

	for postId in counts:
		res.append(actualPostId(postId, counts[postId]))
	print('total: ' + str(time.time() - ts))
	return res


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


def actualPostId(postId, postIdCounts):
	children = []
	for origin in postIdCounts:
		children.append(actualResultForOrigin(origin, postIdCounts[origin]))
	return {
		'Posting ID': postId,
		'_children': children
	}


def actualResultForOrigin(origin, originCounts):
	return {
		'origin': origin,
		'newApplicantCount': originCounts['new_applicant'],
		"newLeadCount": originCounts['new_lead'],
		"recruiterScreenCount": originCounts['recruiter_screen'],
		"phoneInterviewCount": originCounts['phone_interview'],
		"onsiteInterviewCount": originCounts['onsite_interview'],
		"offerCount": originCounts['offer'],
		"reachedOutCount": originCounts['reached_out']
	}


def smallRandomNumber():
	return randint(0, 10)

# Returns back date n days from now based on string passed
def interpretAge(age):
	if age == "beginningOfTime":
		return(datetime.datetime(2005,12,1))
	lis = age.split()
	multiplier = int(lis[0])
	day_or_month = lis[1]

	if day_or_month == "Days":
		# code for day
		benchmark_date = datetime.datetime.now() - datetime.timedelta(days=multiplier)


	if day_or_month == "Months":
		# code for month
		benchmark_date = datetime.datetime.now() - datetime.timedelta(days=multiplier*30)

	return benchmark_date

@app.route('/getBigDict', methods=['GET'])
def getBigDict():
	bigDict = dict()
	rows = collection.find(cursor_type=CursorType.EXHAUST)
	for row in rows:
		flag = False
		if row['Posting Department'] == 'Kapow' or row['Posting Department'] == None or row['Posting Department'] == 'Yikes! No Relevant Roles' or row['Posting Department'] == "":
			continue
		else:
			flag = True

		# Making a big data structure for all dropdowns in front end
		if flag == True:
			makeBigDict(bigDict, row['Posting Department'], row['Posting Team'], row['Posting Title'])
	return jsonify(bigDict)

@app.route('/', methods=['GET'])
def uidropdowns():
	postingDepartment = set()
	postingArchiveStatus = set()
	rows = collection.find(cursor_type=CursorType.EXHAUST)
	for row in rows:
		flag = False
		if row['Posting Department'] == 'Kapow' or row['Posting Department'] == None or row['Posting Department'] == 'Yikes! No Relevant Roles' or row['Posting Department'] == "":
			continue
		else:
			postingDepartment.add(row['Posting Department'])
			flag = True
		postingArchiveStatus.add(row['Posting Archive Status'])

	#Sorting the set alphabatically
	postingDepartment = sorted(postingDepartment)

	return render_template('index.html', postingDepartment=postingDepartment, postingArchiveStatus = postingArchiveStatus)

	

# Make that bigDict step by step
def makeBigDict(bigDict, postDept, postTeam, postTitle):
	if postDept not in bigDict:
		bigDict[str(postDept)] = {}
	if postTeam not in bigDict[str(postDept)]:
		bigDict[str(postDept)][str(postTeam)] = []
	if postTitle not in bigDict[postDept][postTeam]:
		bigDict[str(postDept)][str(postTeam)].append(postTitle)





if __name__ == '__main__':
	app.run(debug=True)
























# Last
