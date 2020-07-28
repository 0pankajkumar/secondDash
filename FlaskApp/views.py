"""All routes of the web app are here"""

from FlaskApp.FlaskApp import app
from flask import request, jsonify, render_template, url_for, redirect, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_uploads import UploadSet, IMAGES, configure_uploads, UploadNotAllowed
from pymongo import MongoClient, CursorType
import datetime, time

# Importing modules
from FlaskApp.FlaskApp.modules.update import *
from FlaskApp.FlaskApp.modules.commonTools import *
from FlaskApp.FlaskApp.modules.customFiltersTools import *
from FlaskApp.FlaskApp.modules.mainDataFetch import *
from FlaskApp.FlaskApp.modules.mainDropdowns import *
from FlaskApp.FlaskApp.modules.specificDropdowns import *
from FlaskApp.FlaskApp.modules.teamDataFetch import *
from FlaskApp.FlaskApp.modules.update import *
from FlaskApp.FlaskApp.modules.user import *

# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB link for ApprovedUsers collection
candidatesCollection = database["dolphinDB"]

# DB link for ApprovedUsers collection
approvedUsersCollection = database["ApprovedUsers"]

# DB link for Posting status collection
postingStatusCollection = database["jobPostingWiseDB"]

# configure flask_upload API
documents = UploadSet("documents", ('csv'))
app.config["UPLOADED_DOCUMENTS_DEST"] = "/var/www/FlaskApp/FlaskApp/uploaded_csv"
configure_uploads(app, documents)


@app.after_request
def after_request(response):
	"""Clearing caches"""

	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	response.headers["Expires"] = 0
	response.headers["Pragma"] = "no-cache"
	return response

@app.route('/privacy', methods=['GET'])
def privacy():
	"""privacy policy of web app usage"""

	return render_template("privacyPolicy.html")

@app.route('/getUploadPage', methods=['GET'])
@login_required
def getUploadPage():
	if checkAdmin(current_user.id):
		loginOption = True
		teamOptions = False
		if checkTeamMembership(current_user.id):
			teamOptions = True
		return render_template('uploader.html', lastUpdated=getLastUpdatedTimestamp(), adminOptions=True, loginOption=loginOption, teamOptions=teamOptions, uploadHighlight="active")
	else:
		return render_template("unauthorized.html"), 403


@app.route('/receiveUploadingData', methods=['POST'])
@login_required
def receiveUploadingData():
	
	# Deleting everything in uploads folder
	flushUploadsFolder()

	f = request.files['file']
	file = documents.save(request.files['file'], name="dump.csv")

	f2 = request.files['file2']
	file2 = documents.save(
		request.files['file2'], name="JobPostingDump.csv")

	return redirect(url_for('uploadedSuccessfully'))


@app.route('/uploadedSuccessfully', methods=['GET', 'POST'])
@login_required
def uploadedSuccessfully():
	loginOption = True
	return render_template("uploadedSuccessfully.html", lastUpdated=getLastUpdatedTimestamp(), loginOption=loginOption)


# This route gives status when it's uploading
@app.route('/triggerUpdateOfDB', methods=['GET', 'POST'])
@login_required
def triggerUpdateOfDB():

	# The database uploading method comes here
	res = 'starting'
	# updateMongo()
	try:
	  updateMongo()
	  res = 'Database Successfully Updated'
	except:
	  res = 'Database update failed. Please contact admin'
	return res


@app.route('/elaborate2', methods=['GET'])
@login_required
def elaborate2():

	fromDate = request.args.get('fromDate')
	toDate = request.args.get('toDate')
	originType = request.args.get('origin')
	postingOwnerName = request.args.get('postingOwnerName')
	requestType = request.args.get('requestType')
	subRequestType = request.args.get('subRequestType')
	allowedOrigins = ["referred", "agency", "applied", "sourced"]

	if originType not in allowedOrigins:
		return jsonify([])

	try:
		fromDate = datetime.datetime.strptime(fromDate, '%d-%m-%Y')
		toDate = datetime.datetime.strptime(toDate, '%d-%m-%Y')
		toDate += datetime.timedelta(days=1)

	except:
		fromDate = datetime.datetime(2000, 1, 1)
		toDate = datetime.datetime(2030, 1, 1)

	if originType != "referred":
		query = {"Origin": originType, "$and": [{"Applied At (GMT)": {"$gte": fromDate}}, {
			"Applied At (GMT)": {"$lte": toDate}}]}
		rows = candidatesCollection.find(query, cursor_type=CursorType.EXHAUST)
	else:
		query = {"$and": [{"Applied At (GMT)": {"$gte": fromDate}}, {
			"Applied At (GMT)": {"$lte": toDate}}]}
		rows = list()
		rows_temp = candidatesCollection.find(query, cursor_type=CursorType.EXHAUST)
		for row in rows_temp:
			if row["Referred"] == "true" or row["Is Social Referral"] == "true" or row["Is Employee Referral"] == "true" or row["Is Manual Referral"] == "true":
				rows.append(row)

	ans = list()

	if requestType == "average":
		count = 1
		for ro in rows:
			if ro['Posting Owner Name'] == postingOwnerName and ro['Days to move from first stage'] >= 0:
				t = dict()
				t['count'] = count
				t['Candidate Name'] = ro['Candidate Name']
				t['Profile ID'] = ro['Profile ID']
				t['Days to move from first stage'] = ro['Days to move from first stage']
				count += 1
				ans.append(t)
	elif requestType == "c":
		count = 1
		for ro in rows:
			if ro['Posting Archived At (GMT)'] == datetime.datetime(1990, 1, 1) and ro['Current Stage'] == 'New applicant' and ro['Posting Owner Name'] == postingOwnerName:
				c = 21
				ageing = (datetime.datetime.now() - ro['Applied At (GMT)']).days
				if subRequestType == "lte_c" and ageing <= c:
					t = dict()
					t['count'] = count
					t['Candidate Name'] = ro['Candidate Name']
					t['Profile ID'] = ro['Profile ID']
					t['Ageing'] = ageing
					ans.append(t)
					count += 1
				if subRequestType == "gt_c" and ageing > c:
					t = dict()
					t['count'] = count
					t['Candidate Name'] = ro['Candidate Name']
					t['Profile ID'] = ro['Profile ID']
					t['Ageing'] = ageing
					ans.append(t)
					count += 1

	adminOptions = False
	loginOption = True
	teamOptions = False
	if checkTeamMembership(current_user.id):
		teamOptions = True
	if checkAdmin(current_user.id):
		adminOptions = True

	return render_template('numbersElaborated2.html', candidates=ans, tableType=requestType, lastUpdated=getLastUpdatedTimestamp(), adminOptions=adminOptions, loginOption=loginOption, teamOptions=teamOptions, livePostingHighlight="active")





@app.route('/elaborate', methods=['GET'])
@login_required
def elaborate():
	postingId = request.args.get('postingId')
	origin = request.args.get('origin')
	stage = request.args.get('stage')
	profileStatus = request.args.get('profileStatus')
	fromDate = request.args.get('fromDate')
	toDate = request.args.get('toDate')

	print("fromDate before is", fromDate)
	print("toDate before is", toDate)
	try:
		fromDate = datetime.datetime.strptime(fromDate, '%d-%m-%Y')
		toDate = datetime.datetime.strptime(toDate, '%d-%m-%Y')
	except:
		fromDate = datetime.datetime(2000, 1, 1)
		toDate = datetime.datetime(2030, 1, 1)

	print("fromDate is", fromDate)
	print("toDate is", toDate)

	# if (postingId is None) or (origin is None) or (stage = None):
	# return "Thers is some problem with your URL"

	adminOptions = False
	loginOption = True
	teamOptions = False
	if checkTeamMembership(current_user.id):
		teamOptions = True
	if checkAdmin(current_user.id):
		adminOptions = True

	results = whoAreTheseNPeople(postingId, origin, stage, profileStatus, fromDate, toDate)
	return render_template('numbersElaborated.html', candidates=results, lastUpdated=getLastUpdatedTimestamp(), adminOptions=adminOptions, loginOption=loginOption, teamOptions=teamOptions, livePostingHighlight="active")
	# return jsonify(results)


def whoAreTheseNPeople(postingId, origin, stage, profileStatus, fromDate, toDate):
	stageBank = {
		"newLead": "New lead",
		"reachedOut": "Reached out",
		"newApplicant": "New applicant",
		"recruiterScreen": "Recruiter screen",
		"phoneInterview": "Phone interview",
		"onsiteInterview": "On-site interview",
		"offer": "Offer",
		"offerApproval": "Offer Approval",
		"offerApproved": "Offer Approved"
	}

	query = dict()
	query['Posting ID'] = postingId

	if origin != "Total":
		if len(origin) < 12:
			query['Origin'] = origin

	if profileStatus == "Both":
		query['$or'] = [{'Posting Archive Status' : 'false'}, {'Posting Archive Status' : 'true'}]
	else:
		query['Posting Archive Status'] = profileStatus

	# We have Offer, Offer Approved, Offer Approval all counted in offer, To encounter that
	result = list()
	if stage == "offer":
		query['$or'] = [{'Current Stage': 'Offer Approval'}, {'Current Stage': 'Offer Approved'}, {'Current Stage': 'Offer'}]
		result = list(candidatesCollection.find(query, cursor_type=CursorType.EXHAUST))
	elif stage == "hired":
		benchDate = datetime.datetime(2015, 1, 1)
		outcome = list(candidatesCollection.find(query, cursor_type=CursorType.EXHAUST))
		for out in outcome:
			if out["Hired"] > benchDate:
				result.append(out)
	else:
		query['Current Stage'] = stageBank[stage]
		result = list(candidatesCollection.find(query, cursor_type=CursorType.EXHAUST))

	packet = []
	count = 1
	for res in result:
		if res['Last Story At (GMT)'] >= fromDate and res['Last Story At (GMT)'] <= toDate:
			dic = dict()
			dic["Candidate Name"] = res["Candidate Name"]
			dic["Profile ID"] = res["Profile ID"]
			dic["count"] = count
			packet.append(dic)
			count += 1
	return packet


@app.route('/getTable', methods=['POST'])
@login_required
def getTable():
	# collection.createIndex('Posting Department')
	recruiter = request.form.get('recruiter')
	postingTitle = request.form.getlist('postingTitle[]')
	companyName = request.form.get('companyName')
	postingTeam = request.form.get('postingTeam')
	requestType = request.form.get('requestType')
	print("PPPPosting title here ---- ", postingTitle)
	# postingArchiveStatus = request.form.get('postingArchiveStatus')
	profileArchiveStatus = request.form.get('profileArchiveStatus')
	fromDate = request.form.get('from')
	toDate = request.form.get('to')

	results = getResults(postingTitle, companyName, postingTeam,
						 profileArchiveStatus, fromDate, toDate, requestType, recruiter)
	# results = getResults("Backend Engineer", "Flock", "Software Engineering", "All")
	return jsonify(results)


def getResults(title, companyName, team, profileArchiveStatus, fromDate, toDate, requestType, recruiter=None):
	try:
		fromDate = datetime.datetime.strptime(fromDate, '%d-%m-%Y')
		toDate = datetime.datetime.strptime(toDate, '%d-%m-%Y')
	except:
		fromDate = datetime.datetime(2000, 1, 1)
		toDate = datetime.datetime(2030, 1, 1)
	ts = time.time()
	rows = getFromDB(title, companyName, team, recruiter)
	print('db: ' + str(time.time() - ts))
	res = []
	counts = dict()

	# This variable will hold the live or archived status of all posting, yes all
	live_or_archived_dict = get_live_or_archived_dict()

	# The restriction is there mark this flag
	# We want to display only postings related to him/her if he/she is marked so
	whichPositions = "all"
	whichPositionsrows = approvedUsersCollection.find({"users": current_user.id})
	for row in whichPositionsrows:
		whichPositions = row["whichPositions"]

	for item in rows:
		# If that flag was marked check whether the email of
		# ... signed in user is in "Posting Owners email id" or "Hiring mangers email id"
		# ... if yes then only display otherwise skip (continue) the loop
		if whichPositions == "respective":
			if not (item["Posting Owner Email"] == current_user.id or item["Posting Hiring Manager Email"] == current_user.id):
				continue

		if item['Posting ID'] in live_or_archived_dict:
			if requestType == "live":
				if not (live_or_archived_dict[item['Posting ID']] == "active"):
					continue
			if requestType == "archived":
				if not (live_or_archived_dict[item['Posting ID']] == "closed"):
					continue
		else:
			continue

		if '(I)' in item['Posting Title']:
			continue

		if item['Posting Archive Status'] != profileArchiveStatus and profileArchiveStatus != 'All' and profileArchiveStatus != 'Both':
			continue

		if 'postingCreatedDate' in item:
			dateForLabel = f"{str(item['postingCreatedDate'].strftime('%b'))} {str(item['postingCreatedDate'].strftime('%Y'))}, "
			# dateForLabel = str(item['postingCreatedDate'].strftime('%b')) + " " + str(item['postingCreatedDate'].strftime('%Y'))
			dateForLabel += str(item['Actual Posting Owner Name'])
		else:
			dateForLabel = f" $ "
			dateForLabel += str(item['Actual Posting Owner Name'])
		postId = str(item['Posting Title']) + ", " + \
			str(item['Posting Location']) + ", " + dateForLabel
		postIdHash = item['Posting ID']

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
			counts[postId][origin]['offerApproval'] = 0
			counts[postId][origin]['hired'] = 0
			counts[postId][origin]['posting_id'] = postIdHash

			# var for % counts
			counts[postId][origin]['phone_To_Onsite'] = 0
			counts[postId][origin]['phone_To_Offer'] = 0
			counts[postId][origin]['onsite_To_Offer'] = 0

		originCounts = counts[postId][origin]

		if item['Last Story At (GMT)'] >= fromDate and item['Last Story At (GMT)'] <= toDate and item['Current Stage'] == "New lead":
			originCounts['new_lead'] += 1
		if item['Last Story At (GMT)'] >= fromDate and item['Last Story At (GMT)'] <= toDate and item['Current Stage'] == "Reached out":
			originCounts['reached_out'] += 1
		if item['Last Story At (GMT)'] >= fromDate and item['Last Story At (GMT)'] <= toDate and item['Current Stage'] == "New applicant":
			originCounts['new_applicant'] += 1
		if item['Last Story At (GMT)'] >= fromDate and item['Last Story At (GMT)'] <= toDate and item['Current Stage'] == "Recruiter screen":
			originCounts['recruiter_screen'] += 1

		if item['Last Story At (GMT)'] >= fromDate and item['Last Story At (GMT)'] <= toDate and item['Current Stage'] == "Phone interview":
			originCounts['phone_interview'] += 1
			# Counting for % conversion
			if 'Stage - On-site interview' in item and item['Stage - On-site interview'] != None:
				originCounts['phone_To_Onsite'] += 1
			if 'Stage - Offer' in item and item['Stage - Offer'] != None:
				originCounts['phone_To_Offer'] += 1

		if item['Last Story At (GMT)'] >= fromDate and item['Last Story At (GMT)'] <= toDate and item['Current Stage'] == "On-site interview":
			originCounts['onsite_interview'] += 1
			# Counting for % conversion
			if 'Stage - Offer' in item and item['Stage - Offer'] != None:
				originCounts['onsite_To_Offer'] += 1

		if item['Last Story At (GMT)'] >= fromDate and item['Last Story At (GMT)'] <= toDate and item['Current Stage'] == "Offer":
			originCounts['offer'] += 1

		if item['Last Story At (GMT)'] >= fromDate and item['Last Story At (GMT)'] <= toDate and item['Current Stage'] == "Offer Approval":
			originCounts['offer'] += 1

		if item['Last Story At (GMT)'] >= fromDate and item['Last Story At (GMT)'] <= toDate and item['Current Stage'] == "Offer Approved":
			originCounts['offer'] += 1

		if item['Hired'] >= fromDate and item['Hired'] <= toDate:
			originCounts['hired'] += 1

	for postId in counts:
		res.append(actualPostId(postId, counts[postId]))

	# Adding a total row for each posting so that we can utilize grand total
	wereTheyAllZeros = getTotalForEachPosting(res)

	print('total: ' + str(time.time() - ts))

	# If they are all zeros return blank else return all the complete result
	if wereTheyAllZeros:
		return []
	else:
		return res



@app.route('/getDropdownOptionsLive', methods=['GET'])
@login_required
def getDropdownOptionsLive():
	liveBigDictPre = dict()

	rows = approvedUsersCollection.find({"users": current_user.id})
	for row in rows:
		companiesAllowed = row["companiesActuallyAllowed"]

	rows = postingStatusCollection.find(
		{"Posting Department": {"$in": companiesAllowed}, "Status": "active"})

	for row in rows:
		if row['Posting Department'] not in companiesAllowed:
			print("Continuing as Posting Department not in companiesAllowed")
			continue
		if row['Status'] != "active":
			continue
		if '(I)' in row['Posting Title']:
			continue

		# Making a big data structure for all dropdowns in front end
		makeDropdownOptions(
			liveBigDictPre, row['Posting Owner'], row['Posting Department'], row['Posting Team'], row['Posting Title'])
		liveBigDict = prepareDropdownOptionsSending(liveBigDictPre)
	return jsonify(liveBigDict)


@app.route('/getDropdownOptionsArchived', methods=['GET'])
@login_required
def getDropdownOptionsArchived():
	archivedBigDictPre = dict()

	rows = approvedUsersCollection.find({"users": current_user.id})
	for row in rows:
		companiesAllowed = row["companiesActuallyAllowed"]

	rows = postingStatusCollection.find(
		{"Posting Department": {"$in": companiesAllowed}, "Status": "closed"})

	for row in rows:
		if row['Posting Department'] not in companiesAllowed:
			print("Continuing as Posting Department not in companiesAllowed")
			continue
		if row['Status'] != "closed":
			continue
		if '(I)' in row['Posting Title']:
			continue

		# Making a big data structure for all dropdowns in front end
		makeDropdownOptions(archivedBigDictPre, row['Posting Owner'],
							row['Posting Department'], row['Posting Team'], row['Posting Title'])
		archivedBigDict = prepareDropdownOptionsSending(archivedBigDictPre)
	return jsonify(archivedBigDict)


@app.route('/getBigDictLive', methods=['GET'])
@login_required
def getBigDictLive():
	liveBigDict = dict()

	rows = approvedUsersCollection.find({"users": current_user.id})
	for row in rows:
		companiesAllowed = row["companiesActuallyAllowed"]

	rows = postingStatusCollection.find(
		{"Posting Department": {"$in": companiesAllowed}, "Status": "active"})

	for row in rows:
		if row['Posting Department'] not in companiesAllowed:
			print("Continuing as Posting Department not in companiesAllowed")
			continue
		if row['Status'] != "active":
			continue
		if '(I)' in row['Posting Title']:
			continue

		# Making a big data structure for all dropdowns in front end
		makeBigDict(liveBigDict, row['Posting Department'],
					row['Posting Team'], row['Posting Title'])
	return jsonify(liveBigDict)


@app.route('/getBigDictArchived', methods=['GET'])
@login_required
def getBigDictArchived():
	archivedBigDict = dict()

	rows = approvedUsersCollection.find({"users": current_user.id})
	for row in rows:
		companiesAllowed = row["companiesActuallyAllowed"]

	rows = postingStatusCollection.find(
		{"Posting Department": {"$in": companiesAllowed}, "Status": "closed"})

	for row in rows:
		if row['Posting Department'] not in companiesAllowed:
			print("Continuing as Posting Department not in companiesAllowed")
			continue
		if row['Status'] != "closed":
			continue
		if '(I)' in row['Posting Title']:
			continue

		# Making a big data structure for all dropdowns in front end
		makeBigDict(archivedBigDict, row['Posting Department'],
					row['Posting Team'], row['Posting Title'])
	return jsonify(archivedBigDict)


@app.route('/getBigDict', methods=['GET'])
@login_required
def getBigDict():
	bigDict = dict()

	rows = approvedUsersCollection.find({"users": current_user.id})
	for row in rows:
		companiesAllowed = row["companiesActuallyAllowed"]

	rows = candidatesCollection.find({"Posting Department": {
						   "$in": companiesAllowed}}, cursor_type=CursorType.EXHAUST)

	for row in rows:
		if row['Posting Department'] not in companiesAllowed:
			continue

		# Making a big data structure for all dropdowns in front end
		makeBigDict(bigDict, row['Posting Department'],
					row['Posting Team'], row['Posting Title'])
	return jsonify(bigDict)



@app.route('/customFilters', methods=['POST'])
@login_required
def customFilters():
	if request.method == "POST":
		filterName = request.form.get('filterName') 
		pageType = request.form.get('pageType')
		recruiter = request.form.get('recruiter')
		postingTitle = request.form.getlist('postingTitle[]')
		companyName = request.form.get('companyName')
		postingTeam = request.form.get('postingTeam')
		requestType = request.form.get('requestType')
		# postingArchiveStatus = request.form.get('postingArchiveStatus')
		profileArchiveStatus = request.form.get('profileArchiveStatus')
		fromDate = request.form.get('from')
		toDate = request.form.get('to')
		usernamesToBeSharedWith = request.form.getlist('usernamesToBeSharedWith[]')

		if requestType == "save":
			oneUser = current_user.id
			msg = saveCustomFilter(oneUser, filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate)
			return msg

		if requestType == "getThoseOptions":
			return getThoseParticularOptions(filterName, pageType)

		if requestType == "delete":
			return deleteThisParticularFilter(filterName)

		if requestType == "getAllUsernameForSharing":
			return getAllUsernameForSharing()

		if requestType == "shareToThesePeople":
			return shareToThesePeople(usernamesToBeSharedWith, filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate)







@app.route('/team', methods=['GET', 'POST'])
@login_required
def team():
	if request.method == "GET":

		teamOptions = False

		if checkTeamMembership(current_user.id):
			# Do all
			adminOptions = False
			loginOption = True
			teamOptions = True

			if checkAdmin(current_user.id):
				adminOptions = True
			return render_template('teamPage.html', lastUpdated=getLastUpdatedTimestamp(), adminOptions=adminOptions, loginOption=loginOption, teamOptions=teamOptions, teamHighlight="active")
		else:
			return render_template("unauthorized.html"), 403

	# Return json data
	if request.method == "POST":
		fromDate = request.form.get('fromDate')
		toDate = request.form.get('toDate')
		requestType = request.form.get('requestType')
		originType = request.form.get('origin')

		allowedOrigins = ["referred", "agency", "applied", "sourced"]

		if requestType == "InNewApplicantStage":
			returnedDict = generateNewApplicantDict(
				fromDate, toDate, originType, allowedOrigins)

		if requestType == "applicationToArchive":
			returnedDict = generateArchivedDict(
				fromDate, toDate, originType, allowedOrigins)

		if requestType == "applicationToOffer":
			returnedDict = generateOfferedDict(
				fromDate, toDate, originType, allowedOrigins)

		return returnedDict



@app.route('/archivedPostings', methods=['GET'])
@login_required
def archivedPostings():

	adminOptions = False
	loginOption = True
	teamOptions = False
	if checkTeamMembership(current_user.id):
		teamOptions = True
	if checkAdmin(current_user.id):
		adminOptions = True
	returnedDict = generateMainPageDropdowns()
	customFilterNames = generateCustomFilterNames("archive")
	return render_template('archivedPostings.html', activateDropdownsAndTable="yes", postingDepartment=returnedDict['postingDepartment'], postingArchiveStatus=returnedDict['postingArchiveStatus'], profileArchiveStatus=returnedDict['profileArchiveStatus'], lastUpdated=getLastUpdatedTimestamp(), adminOptions=adminOptions, loginOption=loginOption, teamOptions=teamOptions, archivedPostingHighlight="active", customFilterNames=customFilterNames)



@app.route('/livePostings', methods=['GET'])
@login_required
def livePostings():
	adminOptions = False
	loginOption = True
	teamOptions = False
	if checkTeamMembership(current_user.id):
		teamOptions = True
	if checkAdmin(current_user.id):
		adminOptions = True
	returnedDict = generateMainPageDropdowns()
	customFilterNames = generateCustomFilterNames("live")
	return render_template('livePostings.html', activateDropdownsAndTable="yes", postingDepartment=returnedDict['postingDepartment'], postingArchiveStatus=returnedDict['postingArchiveStatus'], profileArchiveStatus=returnedDict['profileArchiveStatus'], lastUpdated=getLastUpdatedTimestamp(), adminOptions=adminOptions, loginOption=loginOption, teamOptions=teamOptions, livePostingHighlight="active", customFilterNames=customFilterNames)


@app.route('/recruiterArchivedPostings', methods=['GET'])
@login_required
def recruiterArchivedPostings():

	adminOptions = False
	loginOption = True
	teamOptions = False
	if checkTeamMembership(current_user.id):
		teamOptions = True
	if checkAdmin(current_user.id):
		adminOptions = True
	returnedDict = generateMainPageDropdownsRecruiter('closed')
	customFilterNames = generateCustomFilterNames("archive")
	return render_template('recruiterArchivedPostings.html', activateDropdownsAndTable="yes", activateRecruiterDropdown="yes", postingOwner=returnedDict['postingOwner'], lastUpdated=getLastUpdatedTimestamp(), adminOptions=adminOptions, loginOption=loginOption, teamOptions=teamOptions, archivedPostingHighlight="active", customFilterNames=customFilterNames)


@app.route('/recruiterLivePostings', methods=['GET'])
@login_required
def recruiterLivePostings():

	adminOptions = False
	loginOption = True
	teamOptions = False
	if checkTeamMembership(current_user.id):
		teamOptions = True
	if checkAdmin(current_user.id):
		adminOptions = True
	returnedDict = generateMainPageDropdownsRecruiter('active')
	customFilterNames = generateCustomFilterNames("live")
	return render_template('recruiterLivePostings.html', activateDropdownsAndTable="yes", activateRecruiterDropdown="yes", postingOwner=returnedDict['postingOwner'], lastUpdated=getLastUpdatedTimestamp(), adminOptions=adminOptions, loginOption=loginOption, teamOptions=teamOptions, livePostingHighlight="active", customFilterNames=customFilterNames)


@app.route("/modifyUser", methods=['GET', 'POST'])
@login_required
def modifyUser():

	# Fetch users
	usersList = list()
	fetchUsers(usersList)

	print(f"Got current user iD , yeahhh!!! {current_user.id}")
	loginOption = True
	teamOptions = False

	if request.method == "GET":
		if checkTeamMembership(current_user.id):
			teamOptions = True

		if checkAdmin(current_user.id):
			return render_template("modifyUser.html", usersList=usersList, lastUpdated=getLastUpdatedTimestamp(), adminOptions=True, loginOption=loginOption, teamOptions=teamOptions, modifyUserHighlight="active")
		else:
			return render_template("unauthorized.html"), 403

	if request.method == "POST":
		# Do the insertion stuff
		if request.form.get('actionType') == "addUser":
			addThisUser = request.form.get('emailID')
			makeAdmin = request.form.get('typeOfUser')
			positionFilter = request.form.get('positionFilter')
			tatMember = request.form.get('tatmember')
			companiesToBeAllowed = request.form.getlist('companiesToBeAllowed')

			if makeAdmin == "Admin":
				if tatMember == "Nope":
					approvedUsersCollection.insert_one({"users": addThisUser, "type": "admin", "tatMember": "Nope",
											"companiesActuallyAllowed": companiesToBeAllowed, "whichPositions": positionFilter})
				elif tatMember == "Yeah":
					approvedUsersCollection.insert_one({"users": addThisUser, "type": "admin", "tatMember": "Yeah",
											"companiesActuallyAllowed": companiesToBeAllowed, "whichPositions": positionFilter})
			else:
				if tatMember == "Nope":
					approvedUsersCollection.insert_one({"users": addThisUser, "type": "regular", "tatMember": "Nope",
											"companiesActuallyAllowed": companiesToBeAllowed, "whichPositions": positionFilter})
				elif tatMember == "Yeah":
					approvedUsersCollection.insert_one({"users": addThisUser, "type": "regular", "tatMember": "Yeah",
											"companiesActuallyAllowed": companiesToBeAllowed, "whichPositions": positionFilter})
			return redirect(url_for('modifyUser'))

		if request.form.get('actionType') == "deleteUser":
			deleteThisUser = request.form.get('users')
			approvedUsersCollection.delete_many({"users": deleteThisUser})
			print(f"Deleted {deleteThisUser}")

		if request.form.get('actionType') == "modifyUser":
			modifyThisUser = request.form.get('users')
			hisType = request.form.get('typeData')
			hisTatMember = request.form.get('tatMemberData')
			hisWhichPositions = request.form.get('whichPositionsData')

			approvedUsersCollection.update({"users": modifyThisUser}, {"$set": {
				"type": hisType,
				"tatMember": hisTatMember,
				"whichPositions": hisWhichPositions
			}
			})

		return render_template("modifyUser.html", usersList=usersList, lastUpdated=getLastUpdatedTimestamp(), loginOption=loginOption)


@app.route("/docs", methods=['GET'])
@login_required
def docs():
	if request.method == "GET":
		if checkAdmin(current_user.id):
			return render_template("documentation.html")
		else:
			return render_template("unauthorized.html"), 403

# Feedback & bug central
@app.route('/bugs')
def filefeaturebugs():
	return redirect("https://docs.google.com/forms/d/e/1FAIpQLSetmFiudVkH9Ek60ZgiIpu06DCzSqqZaWcaKaFmPOyuz1OQKw/viewform", code=302)


@app.route('/bugscentral')
def featurebugscentral():
	return redirect("https://docs.google.com/spreadsheets/d/1L2Kmaq5r5YvzOErQqrefd60fJG3ko4CzpOXhUOU7Nns/edit#gid=280194824", code=302)


@app.errorhandler(404)
def page_not_found(e):
	# note that we set the 404 status explicitly
	return render_template('404.html'), 404


@app.route("/")
def index():
	if current_user.is_authenticated:
		return redirect(url_for('livePostings'))

	else:
		# return '<a class="button" href="/login">Google Login</a>'
		loginOption = False
		return render_template("login.html", loginOption=loginOption)


