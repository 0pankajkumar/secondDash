from pymongo import MongoClient, CursorType
from flask_login import current_user
import datetime, time

# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB links for ApprovedUsers collection
collection = database["dolphinDB"]

# DB links for ApprovedUsers collection
collection2 = database["ApprovedUsers"]

# From new dup
collection4 = database["jobPostingWiseDB"]


def getLastUpdatedTimestamp():
	timestamp = None
	try:
		o = collection.find_one({})
		timestamp = str(o['_id'])
		timestamp = timestamp[0:8]
		timestamp = int(timestamp, 16)

		timestamp = time.strftime(
			'%d-%m-%Y %H:%M:%S', time.localtime(timestamp))
		print(timestamp)
	except:
		timestamp = "Coudn't get last updated date"
		print(timestamp)
	return timestamp

def generateMainPageDropdowns2(Status):
	postingOwner = set()
	postingArchiveStatus = set()
	profileArchiveStatus = set()

	rows = collection2.find({"users": current_user.id})
	for row in rows:
		companiesAllowed = row["companiesActuallyAllowed"]

	# Get all users registred TAT members from our user database
	rows = collection2.find({"tatMember": "Yeah"})
	allUsersSet = set()
	for row in rows:
		allUsersSet.add(row["users"])

	rows = collection4.find(
		{"Posting Department": {"$in": companiesAllowed}}, cursor_type=CursorType.EXHAUST)
	for row in rows:
		if row['Posting Owner Email'] not in allUsersSet:
			continue
		if row['Posting Department'] not in companiesAllowed:
			continue
		if row['Status'] != Status:
			continue
		else:
			postingOwner.add(row['Posting Owner'])

	# Sorting the set alphabatically
	postingOwner = sorted(postingOwner)

	# Packing everything to return
	returnList = {}
	returnList['postingOwner'] = postingOwner

	return returnList

def generateMainPageDropdowns():
	postingDepartment = set()
	postingArchiveStatus = set()
	profileArchiveStatus = set()

	# companiesAllowed = set()
	# companiesAllowed = {'Campus', 'Codechef', 'Flock', 'Radix', 'Shared Services'}

	rows = collection2.find({"users": current_user.id})
	for row in rows:
		companiesAllowed = row["companiesActuallyAllowed"]

	rows = collection.find({"Posting Department": {"$in": companiesAllowed}})
	for row in rows:
		if row['Posting Department'] not in companiesAllowed:
			continue
		else:
			postingDepartment.add(row['Posting Department'])
		postingArchiveStatus.add(row['Posting Archive Status'])
		profileArchiveStatus.add(row['Profile Archive Status'])

	# Sorting the set alphabatically
	postingDepartment = sorted(postingDepartment)

	# Packing everything to return
	returnList = {}
	returnList['postingDepartment'] = postingDepartment
	returnList['postingArchiveStatus'] = postingArchiveStatus
	returnList['profileArchiveStatus'] = profileArchiveStatus

	return returnList

def getEligiblePostingTeams(companyName):
	print("companyName ", companyName)
	rows = collection4.find({"Posting Department": companyName})
	mySet = set()
	for row in rows:
		if row['Posting Department'] == companyName:
			mySet.add(row['Posting Team'])

	return mySet

def getEligiblePostingTitles(companyName, team):
	print("companyName ", companyName)
	print("team ", team)
	rows = collection4.find(
		{"Posting Department": companyName, "Posting Team": team})
	mySet = set()
	for row in rows:
		if row['Posting Department'] == companyName and row['Posting Team'] == team:
			mySet.add(row['Posting Title'])

	return mySet

def get_live_or_archived_dict():
	rows = collection4.find({})
	anotherDict = dict()
	for ro in rows:
		if ro['Posting ID'] not in anotherDict:
			anotherDict[ro['Posting ID']] = ro['Status']

	return anotherDict

def generateCustomFilterNames(pageType):
	dbDataStarting = collection2.find({"users": current_user.id}, cursor_type=CursorType.EXHAUST)
	dbData = None
	for d in dbDataStarting:
		dbData = d
	if "customFilters" in dbData:
		dbData = dbData["customFilters"]
	else:
		dbData = []

	allNames = []
	for d in dbData:
		if d["pageType"] == pageType:
			allNames.append(d["filterName"])
	return allNames

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
		result = list(collection.find(query, cursor_type=CursorType.EXHAUST))
	elif stage == "hired":
		benchDate = datetime.datetime(2015, 1, 1)
		outcome = list(collection.find(query, cursor_type=CursorType.EXHAUST))
		for out in outcome:
			if out["Hired"] > benchDate:
				result.append(out)
	else:
		query['Current Stage'] = stageBank[stage]
		result = list(collection.find(query, cursor_type=CursorType.EXHAUST))

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
	whichPositionsrows = collection2.find({"users": current_user.id})
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

def getTotalForEachPosting(res):

	holderForTotalCountHolder = 0

	for i in range(len(res)):
		holder = res[i]['_children']

		monte = ["hiredCount", "newApplicantCount", "newLeadCount", "offerApprovalCount", "offerCount", "onsiteInterviewCount",
				 "onsiteToOfferCount", "phoneInterviewCount", "phoneToOfferCount", "phoneToOnsiteCount", "reachedOutCount", "recruiterScreenCount"]
		totalCountHolder = [0] * 12

		for h in holder:
			for q in range(len(monte)):
				sawTooth = monte[q]
				totalCountHolder[q] += h[sawTooth]

		# counting grand total of all total counts
		holderForTotalCountHolder += sum(totalCountHolder)

		tempDict = dict(zip(monte, totalCountHolder))

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

# title, companyName, team, archiveStatus):
def getFromDB(title, companyName, team, recruiter=None):
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
	return list(collection.find(query, cursor_type=CursorType.EXHAUST))

def actualPostId(postId, postIdCounts):
	children = []
	for origin in postIdCounts:
		children.append(actualResultForOrigin(origin, postIdCounts[origin]))
	return {
		'title': postId,
		'_children': children
	}

def actualResultForOrigin(origin, originCounts):
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

def smallRandomNumber():
	return randint(0, 10)

# Returns back date n days from now based on string passed
def interpretAge(age):
	if age == "beginningOfTime":
		return(datetime.datetime(2005, 12, 1))
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

# Makaing a long list of dicts containing all the items required for dropdown
def prepareDropdownOptionsSending(whale):
	box = list()

	for k, v in whale.items():
		for kk, vv in whale[k].items():
			for kkk, vvv in whale[k][kk].items():
				for kkkk in whale[k][kk][kkk]:
					t = dict()
					t["recruiter"] = k
					t["company"] = kk
					t["dept"] = kkk
					t["post"] = kkkk
					box.append(t)
	return box

def makeDropdownOptions(bigDict, postOwn, postDept, postTeam, postTitle):
	if postOwn not in bigDict:
		bigDict[str(postOwn)] = {}

	if postDept not in bigDict[postOwn]:
		bigDict[postOwn][str(postDept)] = {}

	if postTeam not in bigDict[postOwn][postDept]:
		bigDict[postOwn][str(postDept)][str(postTeam)] = list()

	if postTitle not in bigDict[postOwn][postDept][postTeam]:
		bigDict[postOwn][postDept][postTeam].append(postTitle)

def generateReferalDict(fromDate, toDate, originType, allowedOrigins):

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
		rows = collection.find(query, cursor_type=CursorType.EXHAUST)
	else:
		query = {"$and": [{"Applied At (GMT)": {"$gte": fromDate}}, {
			"Applied At (GMT)": {"$lte": toDate}}]}
		rows = list()
		rows_temp = collection.find(query, cursor_type=CursorType.EXHAUST)
		for row in rows_temp:
			if row["Referred"] == "true" or row["Is Social Referral"] == "true" or row["Is Employee Referral"] == "true" or row["Is Manual Referral"] == "true":
				rows.append(row)

	upperPack = dict()
	lowerPack = list()
	# sidepack is for determing time to move to 2nd stage in candidate lifecycle
	sidePack = dict()
	sidePack2 = dict()
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

			if tem['Posting Owner Name'] not in upperPack:
				upperPack[tem['Posting Owner Name']] = [0] * 13
				upperPack[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] = 1
			else:
				upperPack[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] += 1



			# Making sidePack2 data for counting cases which are older than c
			c = 21
			if tem['Posting Owner Name'] not in sidePack2:
				sidePack2[tem['Posting Owner Name']] = dict()
				sidePack2[tem['Posting Owner Name']]['lte_c'] = 0
				sidePack2[tem['Posting Owner Name']]['gt_c'] = 0
			if tem['Ageing'] <= c:
				sidePack2[tem['Posting Owner Name']]['lte_c'] += 1
			else:
				sidePack2[tem['Posting Owner Name']]['gt_c'] += 1


			# The regular lower pack packing
			lowerPack.append(tem)

		
		if ro['Posting Owner Name'] not in sidePack:
			if ro['Days to move from first stage'] >= 0:
				sidePack[ro['Posting Owner Name']] = [ro['Days to move from first stage']]
			else:
				sidePack[ro['Posting Owner Name']] = [0]
		else:
			if ro['Days to move from first stage'] >= 0:
				sidePack[ro['Posting Owner Name']].append(ro['Days to move from first stage'])

		if ro['Posting Owner Name'] not in test:
			if ro['Days to move from first stage'] >= 0:
				test[ro['Posting Owner Name']] = [ro['Profile ID']]
		else:
			if ro['Days to move from first stage'] >= 0:
				test[ro['Posting Owner Name']].append('https://hire.lever.co/candidates/'+ro['Profile ID'])

	# Calculating average of all days in sidepack
	sidePackFinal = list()
	for k,v in sidePack.items():
		avg = sum(v) / len(v)
		t = dict()
		t['Recruiter Name'] = k
		t['Average Action Days'] = math.ceil(avg)
		sidePackFinal.append(t)

	sidePackFinal.sort(key=lambda a:a['Average Action Days'], reverse=True)

	
	sidePack2Final = list() # Making sidePack2 suitable to be consumed by frontend graph

	sidePack2Final2 = list() # Making sidePack2 suitable for consumption by frontend TABLE
	for k,v in sidePack2.items():

		# Making for graph
		t = list()
		t.append(k)
		t.append(v['lte_c'])
		t.append(v['gt_c'])
		sidePack2Final.append(t)

		# Making for table
		t2 = dict()
		t2['Recruiter Name'] = k
		t2['lte_c'] = v['lte_c']
		t2['gt_c'] = v['gt_c']
		sidePack2Final2.append(t2)

	# Sorting it based on gt_c in descinding order
	sidePack2Final2.sort(key=lambda a: a['gt_c'], reverse=True)
	sidePack2Final.sort(key=lambda a: a[2], reverse=True)
		



	# Making a dict to be readable at Front end Tabulator
	upperPackForTabulator = []

	for key, value in upperPack.items():
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

		upperPackForTabulator.append(tempDict)

	return jsonify({'low': lowerPack, 'up': upperPackForTabulator, 'side': sidePackFinal, "side2": sidePack2Final, "side2_table": sidePack2Final2, "test":test})

def generateReferalArchivedDict(fromDate, toDate, originType, allowedOrigins):

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
		rows = collection.find(query, cursor_type=CursorType.EXHAUST)
	else:
		query = {"$and": [{"Applied At (GMT)": {"$gte": fromDate}}, {
			"Applied At (GMT)": {"$lte": toDate}}]}
		rows = list()
		rows_temp = collection.find(query, cursor_type=CursorType.EXHAUST)
		for row in rows_temp:
			if row["Referred"] == "true" or row["Is Social Referral"] == "true" or row["Is Employee Referral"] == "true" or row["Is Manual Referral"] == "true":
				rows.append(row)

	upperPack = dict()
	lowerPack = list()
	upperPackForTabulator = []

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

			if tem['Posting Owner Name'] not in upperPack:
				upperPack[tem['Posting Owner Name']] = [0] * 13
				upperPack[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] = 1
				# for i in range(1,len(monthList) + 1):
				#   upperPack[tem['Candidate Owner Name']][monthList[i]] = 0
			else:
				upperPack[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] += 1

			lowerPack.append(tem)

	return jsonify({'low': lowerPack, 'up': upperPackForTabulator})

def generateReferalOfferDict(fromDate, toDate, originType, allowedOrigins):

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
		rows = collection.find(query, cursor_type=CursorType.EXHAUST)
	else:
		query = {"$and": [{"Applied At (GMT)": {"$gte": fromDate}}, {
			"Applied At (GMT)": {"$lte": toDate}}]}
		rows = list()
		rows_temp = collection.find(query, cursor_type=CursorType.EXHAUST)
		for row in rows_temp:
			if row["Referred"] == "true" or row["Is Social Referral"] == "true" or row["Is Employee Referral"] == "true" or row["Is Manual Referral"] == "true":
				rows.append(row)

	upperPack = dict()
	lowerPack = list()
	upperPackForTabulator = []

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

			if tem['Posting Owner Name'] not in upperPack:
				upperPack[tem['Posting Owner Name']] = [0] * 13
				upperPack[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] = 1
				# for i in range(1,len(monthList) + 1):
				#   upperPack[tem['Candidate Owner Name']][monthList[i]] = 0
			else:
				upperPack[tem['Posting Owner Name']
						  ][tem['Applied At (GMT)'].month] += 1

			lowerPack.append(tem)

	return jsonify({'low': lowerPack, 'up': upperPackForTabulator})

def getfiltersToBeSavedReady(filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate):
	temp = dict()
	temp["filterName"] = filterName
	temp["pageType"] = pageType
	temp["recruiter"] = recruiter
	temp["postingTitle"] = postingTitle
	temp["companyName"] = companyName
	temp["postingTeam"] = postingTeam
	temp["requestType"] = requestType
	temp["profileArchiveStatus"] = profileArchiveStatus
	try:
		fromDate = datetime.datetime.strptime(fromDate, '%d-%m-%Y')
		toDate = datetime.datetime.strptime(toDate, '%d-%m-%Y')
	except:
		fromDate = ""
		toDate = ""
	temp["fromDate"] = fromDate
	temp["toDate"] = toDate

	return temp 

def cleaningPageType(pageType):
	# Saving pageType as Live or Archived
	if pageType in ["Live Posts", "Live Posts - Recruiter Filter"]:
		pageType = "live"
	elif pageType in ["Archives", "Archives - Recruiter Filter"]:
		pageType = "archive"
	else:
		pageType = "unknown"
	return pageType

def saveCustomFilterPlease(oneUser, filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate):
	pageType = cleaningPageType(pageType)

	dbDataStarting = collection2.find({"users": oneUser}, cursor_type=CursorType.EXHAUST)
	dbData = None
	for d in dbDataStarting:
		dbData = d
	if "customFilters" in dbData:
		dbData = dbData["customFilters"]
	else:
		dbData = []

	duplicateFound = False
	for dbD in dbData:
		if dbD["filterName"] == filterName:
			duplicateFound = True
			break

	if duplicateFound:
		return "No two filters can have same name"
	else:
		filtersToBeSaved = getfiltersToBeSavedReady(filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate)
		dbData.append(filtersToBeSaved)
		print("dbData before writing", dbData)
		# try:
		collection2.update(
				{"users": oneUser},
				{"$set" : {"customFilters": dbData}}
			)
		return "Filter saved Successfully"
		# except:
		#     return "Some error occured while saving filter"

def getThoseParticularOptions(filterName, pageType):
	pageType = cleaningPageType(pageType)
	dbDataStarting = collection2.find({"users": current_user.id}, cursor_type=CursorType.EXHAUST)
	dbData = None
	for d in dbDataStarting:
		dbData = d
	if "customFilters" in dbData:
		dbData = dbData["customFilters"]
	else:
		dbData = []

	dictToBeReturned = dict()
	dictToBeReturned["resultFound"] = "no"
	for d in dbData:
		if d["filterName"] == filterName and d["pageType"] == pageType:
			dictToBeReturned["filterName"] = d["filterName"]
			dictToBeReturned["pageType"] = d["pageType"]
			dictToBeReturned["recruiter"] = d["recruiter"]
			dictToBeReturned["postingTitle"] = d["postingTitle"]
			dictToBeReturned["companyName"] = d["companyName"]
			dictToBeReturned["postingTeam"] = d["postingTeam"]
			dictToBeReturned["requestType"] = d["requestType"]
			dictToBeReturned["profileArchiveStatus"] = d["profileArchiveStatus"]
			dictToBeReturned["fromDate"] = str(d["fromDate"])[:10]
			dictToBeReturned["toDate"] = str(d["toDate"])[:10]
			dictToBeReturned["resultFound"] = "yes"
			break

	return jsonify(dictToBeReturned)

def deleteThisParticularFilter(filterName):
	dbDataStarting = collection2.find({"users": current_user.id}, cursor_type=CursorType.EXHAUST)
	dbData = None
	for d in dbDataStarting:
		dbData = d
	if "customFilters" in dbData:
		dbData = dbData["customFilters"]
	else:
		dbData = []

	dictToBeStoredAgain = list() # All data except for the filter which needs to be deleted will be stored again
	for d in dbData:
		if d["filterName"] != filterName:
			dictToBeStoredAgain.append(d)

	collection2.update(
		{"users": current_user.id},
		{"$set" : {"customFilters": dictToBeStoredAgain}}
	)
	return "Filter Deleted"

def getAllUsernameForSharing():
	dbDataStarting = collection2.find({}, cursor_type=CursorType.EXHAUST)
	allUsernames = list()
	for d in dbDataStarting:
		allUsernames.append(d["users"])

	sendDict = dict()
	if len(allUsernames) > 0:
		sendDict["foundUsernames"] = "yes"
	else:
		sendDict["foundUsernames"] = "no"

	sendDict["usernames"] = allUsernames
	return jsonify(sendDict)

def shareToThesePeople(usernamesToBeSharedWith, filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate):
	duplicateCount = 0
	successCount = 0
	for us in usernamesToBeSharedWith:
		resp = saveCustomFilterPlease(us, filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate)
		if resp == "No two filters can have same name":
			duplicateCount += 1
		if resp == "Filter saved Successfully":
			successCount += 1

	resp = f"Sent to {successCount} people"
	if duplicateCount > 0:
		resp += f"\n But, Sharing with {duplicateCount} people failed due to duplicate filter names"

	return resp

def fetchUsers(usersList):
	pa = collection2.find({})
	for p in pa:
		usersDict = dict()
		usersDict['users'] = p['users']
		usersDict['type'] = p['type']
		usersDict['tatMember'] = p['tatMember']
		if 'whichPositions' in p:
			usersDict['whichPositions'] = p['whichPositions']
		else:
			usersDict['whichPositions'] = "Not defined"
		usersList.append(usersDict)

# Make that bigDict step by step
def makeBigDict(bigDict, postDept, postTeam, postTitle):
	if postDept not in bigDict:
		bigDict[str(postDept)] = {}
	if postTeam not in bigDict[str(postDept)]:
		bigDict[str(postDept)][str(postTeam)] = []
	if 'All' not in bigDict[str(postDept)]:
		bigDict[str(postDept)]['All'] = []
	if postTitle not in bigDict[postDept][postTeam]:
		bigDict[str(postDept)][str(postTeam)].append(postTitle)
		bigDict[str(postDept)]['All'].append(postTitle)

# Helpers file
def customMessages(message):
	render_template("customMessages.html", message=message)

# Classification based on Stage in which candidate is
# For same Profile ID no more than one entry is allowed
def addPostingToPostingDict(ro, postingDict, currentStages, postingActualOwnersDict):
	# if ro['Posting ID'] and ro['Profile ID'] is not None:
	if not isinstance(ro['Posting ID'], datetime.datetime) and not isinstance(ro['Profile ID'], datetime.datetime):
		pst = ro['Posting ID']
		prfl = ro['Profile ID']
	else:
		return

	if pst not in postingDict:
		postingDict[pst] = {}
		postingDict[pst][prfl] = ro

		# Create a new posting entry in dict
		postingActualOwnersDict[pst] = dict()
		postingActualOwnersDict[pst]["Actual Posting Owner Name"] = ro["Posting Owner Name"]
		postingActualOwnersDict[pst]["Applied At (GMT)"] = ro["Applied At (GMT)"]

	else:

		# Check posting date & if its earlier changing the Name
		if postingActualOwnersDict[pst]["Applied At (GMT)"] < ro["Applied At (GMT)"]:
			postingActualOwnersDict[pst]["Actual Posting Owner Name"] = ro["Posting Owner Name"]
			postingActualOwnersDict[pst]["Applied At (GMT)"] = ro["Applied At (GMT)"]

		if prfl not in postingDict[pst]:
			postingDict[pst][prfl] = ro

		else:
			stg1 = postingDict[pst][prfl]['Current Stage']
			stg2 = ro['Current Stage']

			# if currentStages.index(stg2) > currentStages.index(stg1):
			if ro['Max Date'] >= postingDict[pst][prfl]['Max Date']:
				postingDict[pst][prfl] = ro
			# postingDict[pst][prfl] = ro
