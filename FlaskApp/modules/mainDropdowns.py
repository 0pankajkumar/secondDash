from pymongo import MongoClient, CursorType
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

