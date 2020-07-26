from pymongo import MongoClient
from flask_login import current_user
from flask import jsonify
import time

# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB links for candidate's collection
candidatesCollection = database["dolphinDB"]

# DB links for ApprovedUsers collection
approvedUsersCollection = database["ApprovedUsers"]

def getLastUpdatedTimestamp():
	timestamp = None
	try:
		o = candidatesCollection.find_one({})
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

def checkAdmin(user):
	# Checking whether user is admin or not
	pa = approvedUsersCollection.find({'users': current_user.id})
	for p in pa:
		if p['type'] == 'admin':
			return True
		else:
			return False

def checkTeamMembership(user):
	# Checking whether user is admin or not
	pa = approvedUsersCollection.find({'users': user})
	for p in pa:
		if p['tatMember'] == 'Yeah':
			return True
		else:
			return False
