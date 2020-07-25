

# Makaing a long list of dicts containing all the items required for dropdown
def prepareDropdownOptionsSending(whale):
	box = list()

	for k, v in whale.items():
		for kk, vv in whale[k].items():
			for kkk, vvv in whale[k][kk].items():
				for kkkk in whale[k][kk][kkk]:
					t = dict()
					t["recruiter"] = k
					t["company"] = kk
					t["dept"] = kkk
					t["post"] = kkkk
					box.append(t)
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

