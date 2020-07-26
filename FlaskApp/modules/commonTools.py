"""Common tools for the App

This has a few tools or functions which may be used
by almost all of the routes happening in the App.
"""

from pymongo import MongoClient
from flask_login import current_user
from flask import jsonify
import time

# Making connection to DB
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB links for candidate's collection
candidatesCollection = database["dolphinDB"]

# DB links for ApprovedUsers collection
approvedUsersCollection = database["ApprovedUsers"]

def getLastUpdatedTimestamp():
	"""Fetches last updated time

	It reverse calculates time of storage from unique serial
	number given on each row entry by MongoDB
	"""

	timestamp = None
	try:
		o = candidatesCollection.find_one({})
		timestamp = str(o['_id'])
		timestamp = timestamp[0:8]
		timestamp = int(timestamp, 16)

		timestamp = time.strftime(
			'%d-%m-%Y %H:%M:%S', time.localtime(timestamp))
	except:
		timestamp = "Coudn't get last updated date"
	return timestamp

def checkAdmin(user):
	"""Checking whether logged in user is admin or not"""

	dbFetchResult = approvedUsersCollection.find({'users': current_user.id})
	for d in dbFetchResult:
		if d['type'] == 'admin':
			return True
		else:
			return False

def checkTeamMembership(user):
	"""Checking whether user is TA team member or not"""

	dbFetchResult = approvedUsersCollection.find({'users': user})
	for d in dbFetchResult:
		if d['tatMember'] == 'Yeah':
			return True
		else:
			return False
