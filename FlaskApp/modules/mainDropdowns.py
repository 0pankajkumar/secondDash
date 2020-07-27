"""Makes data for the chain of dropdowns in the Home page
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


def makeBigDict(bigDict, postDept, postTeam, postTitle):
	"""Making of bigDict
	
	bigDict : An object having info about posting
	based on it's company and posting department
	"""

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
	"""
	Generates main page dropdowns dict containing
	posting department, posting team and posting title
	"""

	postingDepartment = set()
	postingArchiveStatus = set()
	profileArchiveStatus = set()

	# companiesAllowed = set()
	# companiesAllowed = {'Campus', 'Codechef', 'Flock', 'Radix', 'Shared Services'}

	rows = approvedUsersCollection.find({"users": current_user.id})
	for row in rows:
		companiesAllowed = row["companiesActuallyAllowed"]

	rows = candidatesCollection.find({"Posting Department": {"$in": companiesAllowed}})
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

def generateMainPageDropdownsRecruiter(Status):
	postingOwner = set()
	postingArchiveStatus = set()
	profileArchiveStatus = set()

	rows = approvedUsersCollection.find({"users": current_user.id})
	for row in rows:
		companiesAllowed = row["companiesActuallyAllowed"]

	# Get all users registred TAT members from our user database
	rows = approvedUsersCollection.find({"tatMember": "Yeah"})
	allUsersSet = set()
	for row in rows:
		allUsersSet.add(row["users"])

	rows = postingStatusCollection.find(
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

