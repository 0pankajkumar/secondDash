from pymongo import MongoClient, CursorType
from flask_login import current_user

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
