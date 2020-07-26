from pymongo import MongoClient, CursorType
from flask_login import current_user
from flask import jsonify
import datetime, time

# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB links for ApprovedUsers collection
candidatesCollection = database["dolphinDB"]

# DB links for ApprovedUsers collection
approvedUsersCollection = database["ApprovedUsers"]

# From new dup
postingStatusCollection = database["jobPostingWiseDB"]


# Makaing a long list of dicts containing all the items required for dropdown
def prepareDropdownOptionsSending(unprocessedDict):

	# to store processed data
	box = list()

	# Looping through the dict three levels deep
	for recruiterKey in unprocessedDict:
		for companyKey in unprocessedDict[recruiterKey]:
			for deptKey in unprocessedDict[recruiterKey][companyKey]:
				for postKey in unprocessedDict[recruiterKey][companyKey][deptKey]:
					temp = dict()
					temp["recruiter"] = recruiterKey
					temp["company"] = companyKey
					temp["dept"] = deptKey
					temp["post"] = postKey
					box.append(temp)
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

