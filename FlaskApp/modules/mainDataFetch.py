"""Tools required to make data for the Home page
"""

from pymongo import MongoClient, CursorType
from flask_login import current_user
from flask import jsonify
import datetime, time

# Making connection to DB
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB link for ApprovedUsers collection
candidatesCollection = database["dolphinDB"]

# DB link for ApprovedUsers collection
approvedUsersCollection = database["ApprovedUsers"]

# DB link for Posting status collection
postingStatusCollection = database["jobPostingWiseDB"]


def getPipelineTableData(title, companyName, team, profileArchiveStatus, fromDate, toDate, requestType, recruiter=None):
	"""
	Generates the number of candidates in each Posting 
	classified further into Origin & various Stages
	"""

	try:
		fromDate = datetime.datetime.strptime(fromDate, '%d-%m-%Y')
		toDate = datetime.datetime.strptime(toDate, '%d-%m-%Y')
	except:
		fromDate = datetime.datetime(2000, 1, 1)
		toDate = datetime.datetime(2030, 1, 1)

	rows = getFromDB(title, companyName, team, recruiter)
	res = []
	counts = dict()

	# This variable will hold the live or archived status of all posting, yes all
	live_or_archived_dict = get_live_or_archived_dict()

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

		# Making custom string for Posting title 
		if 'postingCreatedDate' in item:
			dateForLabel = f"{str(item['postingCreatedDate'].strftime('%b'))} {str(item['postingCreatedDate'].strftime('%Y'))}, "
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

			# Initilizing the counts
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

			# variable for % counts :: Work in Progress
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
			# Counting for % conversion :: Work in progress
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

	# If they are all zeros return blank else return all the complete result
	if wereTheyAllZeros:
		return []
	else:
		return res

def getTotalForEachPosting(res):
	"""Counts the total number of candidates for a Posting.

	Reports True if > 0 otherwise False
	Helpful at the fontend as zero counted posting table will
	not be sent to the frontend fr displaying.
	"""

	holderForTotalCountHolder = 0

	for i in range(len(res)):
		holder = res[i]['_children']

		stageNames = ["hiredCount", "newApplicantCount", "newLeadCount", "offerApprovalCount", "offerCount", "onsiteInterviewCount",
				 "onsiteToOfferCount", "phoneInterviewCount", "phoneToOfferCount", "phoneToOnsiteCount", "reachedOutCount", "recruiterScreenCount"]
		totalCountHolder = [0] * 12

		for h in holder:
			for q in range(len(stageNames)):
				localCountHolder = stageNames[q]
				totalCountHolder[q] += h[localCountHolder]

		# counting grand total of all total counts
		holderForTotalCountHolder += sum(totalCountHolder)

		tempDict = dict(zip(stageNames, totalCountHolder))

		# Writing total with the title row itself so that total will appear on the top of each posting 
		for k,v in tempDict.items():
			res[i][k] = v
		res[i]['topTag'] = "true"   # Used to indicate at front-end about top tag
		res[i]['posting_id'] = res[i]['_children'][0]['posting_id']

		# By commenting the below, we are not writing total field
		# tempDict['title'] = 'Total'
		# tempDict['posting_id'] = holder[0]['posting_id']
		# holder.append(tempDict)

	# Returning back with a signal that all counts were Zero, don't display table for this
	return True if holderForTotalCountHolder == 0 else False

def getFromDB(title, companyName, team, recruiter=None):
	"""Fetches all the required rows from DB based on criterias passed"""

	query = dict()

	if title[0] == 'All':
		title = {'$regex': '.*'}
	else:
		title = {"$in": title}
	if team == 'All':
		team = {'$regex': '.*'}
	if companyName == 'All':
		companyName = {'$regex': '.*'}
	if recruiter == "All" or recruiter == None:
		print("recruiter is actually --- ", recruiter)
		recruiter = {'$regex': '.*'}

	query['Posting Department'] = companyName
	query['Posting Title'] = title
	query['Posting Team'] = team
	query['Actual Posting Owner Name'] = recruiter
	# query['Posting Archive Status'] = archiveStatus
	return list(candidatesCollection.find(query, cursor_type=CursorType.EXHAUST))

def actualPostId(postId, postIdCounts):
	"""Packs data into a convinient dict object"""

	children = []
	for origin in postIdCounts:
		children.append(actualResultForOrigin(origin, postIdCounts[origin]))
	return {
		'title': postId,
		'_children': children
	}

def actualResultForOrigin(origin, originCounts):
	"""Packs data into a convinient dict object"""

	return {
		'title': origin,
		'newApplicantCount': originCounts['new_applicant'],
		"newLeadCount": originCounts['new_lead'],
		"recruiterScreenCount": originCounts['recruiter_screen'],
		"phoneInterviewCount": originCounts['phone_interview'],
		"onsiteInterviewCount": originCounts['onsite_interview'],
		"offerCount": originCounts['offer'],
		"offerApprovalCount": originCounts['offerApproval'],
		"hiredCount": originCounts['hired'],
		"reachedOutCount": originCounts['reached_out'],
		"phoneToOnsiteCount": originCounts['phone_To_Onsite'],
		"phoneToOfferCount": originCounts['phone_To_Offer'],
		"onsiteToOfferCount": originCounts['onsite_To_Offer'],
		"posting_id": originCounts['posting_id']
	}

def get_live_or_archived_dict():
	"""Packs the status of all postings from DB in a dict"""

	rows = postingStatusCollection.find({})
	postingStatusDict = dict()
	for ro in rows:
		if ro['Posting ID'] not in postingStatusDict:
			postingStatusDict[ro['Posting ID']] = ro['Status']

	return postingStatusDict
