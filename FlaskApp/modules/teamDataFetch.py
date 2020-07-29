"""Tools for calculating data at Team page (Marvel)
"""

from pymongo import MongoClient, CursorType
from flask_login import current_user
import datetime, time, math
from flask import jsonify

# Making connection to DB
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB link for ApprovedUsers collection
candidatesCollection = database["dolphinDB"]


def whoAreTheseNPeople(postingId, origin, stage, profileStatus, fromDate, toDate):
	"""Determines the names of Candidates with profile id to their lever profile"""

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

def generateNewApplicantDict(fromDate, toDate, originType, allowedOrigins):
	"""Makes data for the referal page

	yearlyTable : The upper table
	averageDaysPack : 
	deadlineCasesPack : 
	"""

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


	yearlyTable = dict()
	candidateRecruiterTable = list()
	# averageDaysPack is for determing time to move to 2nd stage in candidate lifecycle
	averageDaysPack = dict()
	deadlineCasesPack = dict()
	test = dict()
	tem2 = dict()
	monthList = ['*', 'Jan', 'Feb', 'Mar', 'Apr', 'May',
				 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

	for ro in rows:
		if ro['Posting Archived At (GMT)'] == datetime.datetime(1990, 1, 1) and ro['Current Stage'] == 'New applicant':
			tem = dict()

			tem['Profile ID'] = ro['Profile ID']
			tem['Posting Owner Name'] = ro['Posting Owner Name']
			tem['Application ID'] = ro['Application ID']
			tem['Posting ID'] = ro['Posting ID']
			tem['Posting Title'] = ro['Posting Title']
			tem['Applied At (GMT)'] = ro['Applied At (GMT)']
			tem['Last Story At (GMT)'] = ro['Last Story At (GMT)']
			tem['CandidateName'] = ro['Candidate Name']
			tem['Ageing'] = datetime.datetime.now() - tem['Applied At (GMT)']
			tem['Ageing'] = tem['Ageing'].days
			tem['ProfileLink'] = 'https://hire.lever.co/candidates/' + \
				tem['Profile ID']

			if tem['Posting Owner Name'] not in yearlyTable:
				yearlyTable[tem['Posting Owner Name']] = [0] * 13
				yearlyTable[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] = 1
			else:
				yearlyTable[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] += 1



			# Making deadlineCasesPack data for counting cases which are older than c
			c = 21
			if tem['Posting Owner Name'] not in deadlineCasesPack:
				deadlineCasesPack[tem['Posting Owner Name']] = dict()
				deadlineCasesPack[tem['Posting Owner Name']]['lte_c'] = 0
				deadlineCasesPack[tem['Posting Owner Name']]['gt_c'] = 0
			if tem['Ageing'] <= c:
				deadlineCasesPack[tem['Posting Owner Name']]['lte_c'] += 1
			else:
				deadlineCasesPack[tem['Posting Owner Name']]['gt_c'] += 1


			# The regular lower pack packing
			candidateRecruiterTable.append(tem)

		
		if ro['Posting Owner Name'] not in averageDaysPack:
			if ro['Days to move from first stage'] >= 0:
				averageDaysPack[ro['Posting Owner Name']] = [ro['Days to move from first stage']]
			else:
				averageDaysPack[ro['Posting Owner Name']] = [0]
		else:
			if ro['Days to move from first stage'] >= 0:
				averageDaysPack[ro['Posting Owner Name']].append(ro['Days to move from first stage'])

		if ro['Posting Owner Name'] not in test:
			if ro['Days to move from first stage'] >= 0:
				test[ro['Posting Owner Name']] = [ro['Profile ID']]
		else:
			if ro['Days to move from first stage'] >= 0:
				test[ro['Posting Owner Name']].append('https://hire.lever.co/candidates/'+ro['Profile ID'])

	# Calculating average of all days in averageDaysPack
	averageDaysPackFinal = list()
	for k,v in averageDaysPack.items():
		avg = sum(v) / len(v)
		t = dict()
		t['Recruiter Name'] = k
		t['Average Action Days'] = math.ceil(avg)
		averageDaysPackFinal.append(t)

	averageDaysPackFinal.sort(key=lambda a:a['Average Action Days'], reverse=True)

	
	deadlineCasesPackFinal = list() # Making deadlineCasesPack suitable to be consumed by frontend graph

	deadlineCasesPackFinalTable = list() # Making deadlineCasesPack suitable for consumption by frontend TABLE
	for k,v in deadlineCasesPack.items():

		# Making for graph
		t = list()
		t.append(k)
		t.append(v['lte_c'])
		t.append(v['gt_c'])
		deadlineCasesPackFinal.append(t)

		# Making for table
		t2 = dict()
		t2['Recruiter Name'] = k
		t2['lte_c'] = v['lte_c']
		t2['gt_c'] = v['gt_c']
		deadlineCasesPackFinalTable.append(t2)

	# Sorting it based on gt_c in descinding order
	deadlineCasesPackFinalTable.sort(key=lambda a: a['gt_c'], reverse=True)
	deadlineCasesPackFinal.sort(key=lambda a: a[2], reverse=True)
		



	# Making a dict to be readable at Front end Tabulator
	yearlyTableForTabulator = []

	for key, value in yearlyTable.items():
		tempDict = {}
		tempDict['Recruiter'] = key

		thatTotal = sum(value)
		tempDict['Grand Total'] = thatTotal

		# if value

		i = 0
		for mon in monthList:
			if value[i] != 0:
				# value[i] += 1
				tempDict[mon] = value[i]
			else:
				tempDict[mon] = value[i]
			i += 1

		yearlyTableForTabulator.append(tempDict)

	return jsonify({'low': candidateRecruiterTable, 'up': yearlyTableForTabulator, 'side': averageDaysPackFinal, "side2": deadlineCasesPackFinal, "side2_table": deadlineCasesPackFinalTable, "test":test})

def generateArchivedDict(fromDate, toDate, originType, allowedOrigins):

	if originType not in allowedOrigins:
		return jsonify([])

	try:
		fromDate = datetime.datetime.strptime(fromDate, '%d-%m-%Y')
		toDate = datetime.datetime.strptime(toDate, '%d-%m-%Y')

	except:
		fromDate = datetime.datetime(2000, 1, 1)
		toDate = datetime.datetime(2030, 1, 1)

	t1 = time.time()
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
	t2 = time.time()
	print(f"Took {t2 - t1}s in DB transaction")

	averageDaysPack = dict()
	candidateRecruiterTable = list()
	averageDaysPackForTabulator = []

	t3 = time.time()
	for ro in rows:
		if ro['Posting Archive Status'] == "true" and not isinstance(ro['Posting Owner Name'], datetime.date):
			# Do things
			tem = dict()

			tem['Profile ID'] = ro['Profile ID']
			tem['Posting Owner Name'] = ro['Posting Owner Name']
			tem['Application ID'] = ro['Application ID']
			tem['Posting ID'] = ro['Posting ID']
			tem['Posting Title'] = ro['Posting Title']
			tem['Applied At (GMT)'] = ro['Applied At (GMT)']
			tem['Last Story At (GMT)'] = ro['Last Story At (GMT)']
			tem['Posting Archived At (GMT)'] = ro['Posting Archived At (GMT)']
			tem['CandidateName'] = ro['Candidate Name']
			tem['Last Story At (GMT)'] = ro['Last Story At (GMT)']

			tem['Ageing'] = tem['Posting Archived At (GMT)'] - \
				tem['Applied At (GMT)']
			tem['Ageing'] = tem['Ageing'].days

			tem['ProfileLink'] = 'https://hire.lever.co/candidates/' + \
				tem['Profile ID']

			if tem['Posting Owner Name'] not in averageDaysPack:
				averageDaysPack[tem['Posting Owner Name']] = [0] * 13
				averageDaysPack[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] = 1
			else:
				averageDaysPack[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] += 1

			candidateRecruiterTable.append(tem)
	t4 = time.time()
	print(f"Took {t4 - t3}s in Calculations")

	return jsonify({'low': candidateRecruiterTable, 'up': averageDaysPackForTabulator})

def generateOfferedDict(fromDate, toDate, originType, allowedOrigins):

	if originType not in allowedOrigins:
		return jsonify([])

	try:
		fromDate = datetime.datetime.strptime(fromDate, '%d-%m-%Y')
		toDate = datetime.datetime.strptime(toDate, '%d-%m-%Y')

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

	averageDaysPack = dict()
	candidateRecruiterTable = list()
	averageDaysPackForTabulator = []

	for ro in rows:
		if (ro['Current Stage'] == 'Offer' or ro['Current Stage'] == 'Offer Approval' or ro['Current Stage'] == 'Offer Approved') and not isinstance(ro['Posting Owner Name'], datetime.date):
			# Do things
			tem = dict()

			tem['Profile ID'] = ro['Profile ID']
			tem['Posting Owner Name'] = ro['Posting Owner Name']
			tem['Application ID'] = ro['Application ID']
			tem['Posting ID'] = ro['Posting ID']
			tem['Posting Title'] = ro['Posting Title']
			tem['Applied At (GMT)'] = ro['Applied At (GMT)']
			tem['Stage - Offer'] = ro['Stage - Offer']
			tem['Posting Archived At (GMT)'] = ro['Posting Archived At (GMT)']
			tem['CandidateName'] = ro['Candidate Name']
			tem['Stage - Offer Approval'] = ro['Stage - Offer Approval']
			tem['Stage - Offer Approved'] = ro['Stage - Offer Approved']

			# Picking up the Offer dates appropiately as Offer has sub stages
			if tem['Stage - Offer'] == datetime.datetime(1990, 1, 1):
				if tem['Stage - Offer Approval'] == datetime.datetime(1990, 1, 1):
					if tem['Stage - Offer Approved'] == datetime.datetime(1990, 1, 1):
						continue
					else:
						tem['Ageing'] = tem['Stage - Offer Approved'] - \
							tem['Applied At (GMT)']
				else:
					tem['Ageing'] = tem['Stage - Offer Approval'] - \
						tem['Applied At (GMT)']
			else:
				tem['Ageing'] = tem['Stage - Offer'] - tem['Applied At (GMT)']

			tem['Ageing'] = tem['Ageing'].days
			tem['ProfileLink'] = 'https://hire.lever.co/candidates/' + \
				tem['Profile ID']

			if tem['Posting Owner Name'] not in averageDaysPack:
				averageDaysPack[tem['Posting Owner Name']] = [0] * 13
				averageDaysPack[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] = 1
			else:
				averageDaysPack[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] += 1

			candidateRecruiterTable.append(tem)

	return jsonify({'low': candidateRecruiterTable, 'up': averageDaysPackForTabulator})

