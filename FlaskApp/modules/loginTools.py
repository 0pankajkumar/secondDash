from pymongo import MongoClient
from flask_login import current_user

# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB links for ApprovedUsers collection
collection2 = database["ApprovedUsers"]



def checkAdmin(user):
	# Checking whether user is admin or not
	pa = collection2.find({'users': current_user.id})
	for p in pa:
		if p['type'] == 'admin':
			return True
		else:
			return False


def checkTeamMembership(user):
	# Checking whether user is admin or not
	pa = collection2.find({'users': user})
	for p in pa:
		if p['tatMember'] == 'Yeah':
			return True
		else:
			return False
