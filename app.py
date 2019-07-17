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

app = flask.Flask(__name__, static_url_path='',
				  static_folder='static',
				  template_folder='templates')
app.config["DEBUG"] = False

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["antDB"]


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



@app.route('/test1', methods=['GET'])
def test1():
	return render_template('test1.html')

@app.route('/funnel', methods=['GET'])
def funnel():
	postingDepartment = set()
	postingTeam = set()
	postingTitle = set()
	postingArchiveStatus = set()

	query = {}
	query['Posting Department'] = {'$regex':'.'}
	rows = collection.find(query, cursor_type=CursorType.EXHAUST)
	for row in rows:
		postingDepartment.add(row['Posting Department'])
		# postingTeam.add(row['Posting Team'])
		# postingTitle.add(row['Posting Title'])
		# postingArchiveStatus.add(row['Posting Archive Status'])
	return render_template('funnel.html', postingDepartment=postingDepartment, postingTeam=postingTeam,
						   postingTitle=postingTitle, postingArchiveStatus=postingArchiveStatus)
	#return render_template('funnel.html')


@app.route('/getTable', methods=['POST'])
def getTable():
	# collection.createIndex('Posting Department')
	postingTitle = request.form.get('postingTitle')
	companyName = request.form.get('companyName')
	postingTeam = request.form.get('postingTeam')
	postingArchiveStatus = request.form.get('postingTeam')

	results = getResults(postingTitle, companyName, postingTeam, postingArchiveStatus)
	return jsonify(results)


def getResults(title, companyName, team, archiveStatus):
	ts = time.time()
	rows = getFromDB(companyName) # title, companyName, team, archiveStatus
	print('db: ' + str(time.time() - ts))
	res = []
	counts = dict()
	for item in rows:
		if item['Posting Title'] != title and title != 'All':
			continue
		# if item['Posting Department'] != companyName and companyName != 'All':
		#     continue
		if item['Posting Team'] != team and team != 'All':
			continue
		if item['Posting Archive Status'] != archiveStatus and archiveStatus != 'All':
			continue

		postId = item['Posting ID']
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


@app.route('/', methods=['GET'])
def uidropdowns():
	postingDepartment = set()
	postingTeam = set()
	postingTitle = set()
	postingArchiveStatus = set()

	rows = collection.find(cursor_type=CursorType.EXHAUST)
	for row in rows:
		postingDepartment.add(row['Posting Department'])
		postingTeam.add(row['Posting Team'])
		postingTitle.add(row['Posting Title'])
		postingArchiveStatus.add(row['Posting Archive Status'])
	return render_template('index.html', postingDepartment=postingDepartment, postingTeam=postingTeam,
						   postingTitle=postingTitle, postingArchiveStatus=postingArchiveStatus)


if __name__ == '__main__':
	app.run(debug=True)
























# Last
