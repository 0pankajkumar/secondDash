"""This has all helper modules for enumerating & elaborating about candidates"""

import datetime
from pymongo import MongoClient

# Making connection to DB
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB link for candidate's collection
candidatesCollection = database["dolphinDB"]


def elaborateTeamReportsNewApplicantsHelper(fromDate, toDate, originType, postingOwnerName, requestType, subRequestType, allowedOrigins):
	"""Gives out names of all candidates matching the criterias passed"""

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
	return ans

def elaborateHomepageCandidatesHelper(postingId, origin, stage, profileStatus, fromDate, toDate):
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
