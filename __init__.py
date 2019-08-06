import flask
from flask import request, jsonify, render_template, url_for, redirect, session
from flask_session import Session
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
from functools import wraps


app = flask.Flask(__name__, static_url_path='',
				  static_folder='static',
				  template_folder='templates')
app.config["DEBUG"] = False

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["eucalyptusDB"]

# Clearing caches
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure flask_upload API
documents = UploadSet("documents", ('csv'))
app.config["UPLOADED_DOCUMENTS_DEST"] = "uploaded_csv"
configure_uploads(app, documents)


def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route('/upload', methods=['GET', 'POST'])
# @login_required
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
# @login_required
def test1():
	return render_template('test2.html')

@app.route('/trial3', methods=['GET'])
# @login_required
def trial3():
	return render_template('trial3.html')

@app.route('/funnel', methods=['GET'])
# @login_required
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
# @login_required
def getTable():
	# collection.createIndex('Posting Department')

	postingTitle = request.form.get('postingTitle')
	companyName = request.form.get('companyName')
	postingTeam = request.form.get('postingTeam')
	postingArchiveStatus = request.form.get('postingArchiveStatus')
	profileArchiveStatus = request.form.get('profileArchiveStatus')
	age = request.form.get('age')

	results = getResults(postingTitle, companyName, postingTeam, postingArchiveStatus, profileArchiveStatus, age)
	# results = getResults("Backend Engineer", "Flock", "Software Engineering", "All")
	return jsonify(results)


def getResults(title, companyName, team, archiveStatus, profileArchiveStatus, age):
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
		if item['Profile Archive Status'] != profileArchiveStatus and profileArchiveStatus != 'All' and profileArchiveStatus != 'Both':
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

			# var for % counts
			counts[postId][origin]['phone_To_Onsite'] = 0
			counts[postId][origin]['phone_To_Offer'] = 0
			counts[postId][origin]['onsite_To_Offer'] = 0

		originCounts = counts[postId][origin]
		
		if 'Stage - New lead' in item and item['Stage - New lead'] != None:
			originCounts['new_lead'] += 1
		if 'Stage - Reached out' in item and item['Stage - Reached out'] != None:
			originCounts['reached_out'] += 1
		if 'Stage - New applicant' in item and item['Stage - New applicant'] != None:
			originCounts['new_applicant'] += 1
		if 'Stage - Recruiter screen' in item and item['Stage - Recruiter screen'] != None:
			originCounts['recruiter_screen'] += 1

		if 'Stage - Phone interview' in item and item['Stage - Phone interview'] != None:
			originCounts['phone_interview'] += 1
			# Counting for % conversion
			if 'Stage - On-site interview' in item and item['Stage - On-site interview'] != None:
				originCounts['phone_To_Onsite'] += 1
			if 'Stage - Offer' in item and item['Stage - Offer'] != None:
				originCounts['phone_To_Offer'] += 1

		if 'Stage - On-site interview' in item and item['Stage - On-site interview'] != None:
			originCounts['onsite_interview'] += 1
			# Counting for % conversion
			if 'Stage - Offer' in item and item['Stage - Offer'] != None:
				originCounts['onsite_To_Offer'] += 1

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
		"reachedOutCount": originCounts['reached_out'],
		"phoneToOnsiteCount": originCounts['phone_To_Onsite'],
		"phoneToOfferCount": originCounts['phone_To_Offer'],
		"onsiteToOfferCount": originCounts['onsite_To_Offer']
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
# @login_required
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

@app.route('/table', methods=['GET'])
# @login_required
def uidropdowns():
	postingDepartment = set()
	postingArchiveStatus = set()
	profileArchiveStatus = set()
	rows = collection.find(cursor_type=CursorType.EXHAUST)
	for row in rows:
		flag = False
		if row['Posting Department'] == 'Kapow' or row['Posting Department'] == None or row['Posting Department'] == 'Yikes! No Relevant Roles' or row['Posting Department'] == "":
			continue
		else:
			postingDepartment.add(row['Posting Department'])
			flag = True
		postingArchiveStatus.add(row['Posting Archive Status'])
		profileArchiveStatus.add(row['Profile Archive Status'])

	#Sorting the set alphabatically
	postingDepartment = sorted(postingDepartment)

	return render_template('index.html', postingDepartment=postingDepartment, postingArchiveStatus = postingArchiveStatus, profileArchiveStatus = profileArchiveStatus)


@app.route('/login', methods=['GET'])
def loginPage1():

	# Forget any user_id
	session.clear()

	if request.method == "GET":
		return render_template('login.html')
	if request.method == "POST":
		googID = request.form.get('idtoken')
		print(googID + " received")
		return render_template("welcome.html")


@app.route('/', methods=['GET'])
def loginPage():
	return render_template('login.html')
	

# Make that bigDict step by step
def makeBigDict(bigDict, postDept, postTeam, postTitle):
	if postDept not in bigDict:
		bigDict[str(postDept)] = {}
	if postTeam not in bigDict[str(postDept)]:
		bigDict[str(postDept)][str(postTeam)] = []
	if postTitle not in bigDict[postDept][postTeam]:
		bigDict[str(postDept)][str(postTeam)].append(postTitle)





if __name__ == '__main__':
	app.run(debug=True,host="172.16.140.211")

# if __name__ == '__main__':
# 	app.run(debug=True)
























# Last
