from pymongo import MongoClient, CursorType
from flask_login import current_user
import datetime

# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB links for ApprovedUsers collection
collection2 = database["ApprovedUsers"]


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
		try:
			collection2.update(
					{"users": oneUser},
					{"$set" : {"customFilters": dbData}}
				)
			return "Filter saved Successfully"
		except:
		    return "Some error occured while saving filter"

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
