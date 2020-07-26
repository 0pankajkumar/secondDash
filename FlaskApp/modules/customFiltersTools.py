from pymongo import MongoClient, CursorType
from flask_login import current_user
from flask import jsonify
import datetime

# Making connection to DB
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB link for ApprovedUsers collection
approvedUsersCollection = database["ApprovedUsers"]

def saveCustomFilter(oneUser, filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate):
	"""Saves Custom filter (with a unique name otherwise not)"""

	pageType = determinePageType(pageType)

	dbDataResults = approvedUsersCollection.find({"users": oneUser}, cursor_type=CursorType.EXHAUST)
	dbData = None
	for d in dbDataResults:
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

	# Saving only when it's unique name
	if duplicateFound:
		return "No two filters can have same name"
	else:
		filtersToBeSaved = getfiltersToBeSavedReady(filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate)
		dbData.append(filtersToBeSaved)
		print("dbData before writing", dbData)
		try:
			approvedUsersCollection.update(
					{"users": oneUser},
					{"$set" : {"customFilters": dbData}}
				)
			return "Filter saved Successfully"
		except:
		    return "Some error occured while saving filter"

def getfiltersToBeSavedReady(filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate):
	"""Prepares the filter in a dict format convenient for saving"""

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
		temp["fromDate"] = datetime.datetime.strptime(fromDate, '%d-%m-%Y')
		temp["toDate"] = datetime.datetime.strptime(toDate, '%d-%m-%Y')
	except:
		temp["fromDate"] = ""
		temp["toDate"] = ""

	return temp 

def determinePageType(pageType):
	"""Determining type of page. Whether Live or Archived"""

	if pageType in ["Live Posts", "Live Posts - Recruiter Filter"]:
		pageType = "live"
	elif pageType in ["Archives", "Archives - Recruiter Filter"]:
		pageType = "archive"
	else:
		pageType = "unknown"
	return pageType

def getThoseParticularOptions(filterName, pageType):
	"""Fetches all the parameters of a matching filter name"""

	pageType = determinePageType(pageType)
	dbDataStarting = approvedUsersCollection.find({"users": current_user.id}, cursor_type=CursorType.EXHAUST)
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
	"""Deletes all parameter of a matching filter"""

	dbDataResults = approvedUsersCollection.find({"users": current_user.id}, cursor_type=CursorType.EXHAUST)
	dbData = None
	for d in dbDataResults:
		dbData = d
	if "customFilters" in dbData:
		dbData = dbData["customFilters"]
	else:
		dbData = []

	dictToBeStoredAgain = list() 
	# All data except for the filter which needs to be deleted will be stored again
	for d in dbData:
		if d["filterName"] != filterName:
			dictToBeStoredAgain.append(d)

	approvedUsersCollection.update(
		{"users": current_user.id},
		{"$set" : {"customFilters": dictToBeStoredAgain}}
	)
	return "Filter Deleted"

def shareToThesePeople(usernamesToBeSharedWith, filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate):
	"""Saves a filter for the usernames specified. This is sharing.
	"""

	duplicateCount = 0
	successCount = 0
	for us in usernamesToBeSharedWith:
		resp = saveCustomFilter(us, filterName, pageType, recruiter, postingTitle, companyName, postingTeam, requestType, profileArchiveStatus, fromDate, toDate)
		if resp == "No two filters can have same name":
			duplicateCount += 1
		if resp == "Filter saved Successfully":
			successCount += 1

	resp = f"Sent to {successCount} people"
	if duplicateCount > 0:
		resp += f"\n But, Sharing with {duplicateCount} people failed due to duplicate filter names"

	return resp

def getAllUsernameForSharing():
	"""Sends usernames of all members of TA Reports club"""

	dbDataStarting = approvedUsersCollection.find({}, cursor_type=CursorType.EXHAUST)
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

def generateCustomFilterNames(pageType):
	"""Initialises the DB for the user to get stated with filters"""

	dbDataResults = approvedUsersCollection.find({"users": current_user.id}, cursor_type=CursorType.EXHAUST)
	dbData = None
	for d in dbDataResults:
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
