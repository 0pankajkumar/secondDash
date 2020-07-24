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
