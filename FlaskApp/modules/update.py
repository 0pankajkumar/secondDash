import os
from pymongo import MongoClient, CursorType, ASCENDING, DESCENDING
import csv, datetime
from pathlib import Path
from flask_login import current_user

# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB links for ApprovedUsers collection
collection = database["dolphinDB"]

# DB links for ApprovedUsers collection
collection2 = database["ApprovedUsers"]

# From new dup
collection4 = database["jobPostingWiseDB"]

def updateMongo():
	updatePostingInfo()
	updateDump()


def updatePostingInfo():
	client = MongoClient("mongodb://localhost:27017")
	database = client["local"]
	collection = database["jobPostingWiseDB"]

	collection.delete_many({})
	print("Deleted everything in posting info DB")
	print("Adding posting info records...")

	script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
	data_folder = Path("/var/www/FlaskApp/FlaskApp/uploaded_csv")

	# data_folder = Path("C:\\Users\\pankaj.kum\\Desktop\\zetaDash")
	file_to_open = data_folder / "JobPostingDump.csv"

	with open(str(file_to_open), 'r', encoding="utf8") as csvfile:
		myReader = csv.reader(csvfile, delimiter=',')

		titlesWanted = ["Posting ID", "Posting Title", "Applications",
						"Date Created (GMT)", "Last Updated (GMT)", "Status", "Posting Team", "Posting Owner", "Posting Owner Email", "Posting Department", "State"]
		titles = list()
		titlesNumber = set()
		finalBox = list()
		i = 0
		ty = [0]
		for row in myReader:
			if i > 0:
				j = 0
				tempDict = dict()
				for r in row:
					if j in titlesNumber:
						# if titles[j] in ["Date Created (GMT)", "Last Updated (GMT)"]:
						#   r = getInDateFormat(r, ty)
						tempDict[titles[j]] = r
					j += 1
				finalBox.append(tempDict)
			else:
				titles = row
				for i in range(len(titles)):
					if titles[i] in titlesWanted:
						titlesNumber.add(i)

			i += 1

	collection.insert_many(finalBox)

	# os.remove(file_to_open)
	print("File Deleted")

	print(ty)


def updateDump():
	client = MongoClient("mongodb://localhost:27017")
	database = client["local"]
	collection = database["dolphinDB"]

	all_The_Stages = ['Stage - New lead', 'Stage - Reached out', 'Stage - Responded', 'Stage - New applicant',
					  'Stage - Recruiter screen', 'Stage - Profile review', 'Stage - Case study', 'Stage - Phone interview', 'Stage - On-site interview', 'Stage - Offer', 'Stage - Offer Approval', 'Stage - Offer Approved', 'Hired']
	all_The_Stages_minus_hired = ['Stage - New lead', 'Stage - Reached out', 'Stage - Responded', 'Stage - New applicant',
					  'Stage - Recruiter screen', 'Stage - Profile review', 'Stage - Case study', 'Stage - Phone interview', 'Stage - On-site interview', 'Stage - Offer', 'Stage - Offer Approval', 'Stage - Offer Approved']
	all_The_date_columns = ['Posting Archived At (GMT)', 'Created At (GMT)', 'Applied At (GMT)', 'Last Story At (GMT)', 'Last Advanced At (GMT)', 'Stage - New lead', 'Stage - Reached out', 'Stage - Responded', 'Stage - New applicant',
					  'Stage - Recruiter screen', 'Stage - Profile review', 'Stage - Case study', 'Stage - Phone interview', 'Stage - On-site interview', 'Stage - Offer', 'Stage - Offer Approval', 'Stage - Offer Approved', 'Hired']
	headers = tuple()
	line_count = 0
	dict_of_posting_creation_date = dict()
	box = []
	fileName = "uploaded_csv/dump.csv"

	collection.delete_many({})
	print("Deleted everything")
	print("Adding records...")

	# relative path inspired from here https://medium.com/@ageitgey/python-3-quick-tip-the-easy-way-to-deal-with-file-paths-on-windows-mac-and-linux-11a072b58d5f
	script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
	data_folder = Path("/var/www/FlaskApp/FlaskApp/uploaded_csv")
	file_to_open = data_folder / "dump.csv"

	# The correcting code for Null found in csv
	fi = open(file_to_open, 'rb')
	data = fi.read()
	fi.close()
	fo = open(file_to_open, 'wb')
	fo.write(data.replace(b'\x00', b''))
	fo.close()

	with open(str(file_to_open), 'r', encoding="utf8") as csvfile:
		myReader = csv.reader(csvfile, delimiter=',')
		print("Opened file for uploading")
		for row in myReader:
			minDateCandidates = list()
			dict_to_be_written = dict()
			phoneToOnsite = False
			phoneToOffer = False
			onsiteToOffer = False
			if line_count > 0:
				# Making dict for DB

				row = [r.strip() for r in row]

				# First date at which candidate lifecycle started, its mostly the Applied At date
				firstDate = None
				# Second date is the date just after date of Applying. Used to know how fast recruiter acted upon the candidate
				secondDate = None
				# Ths list used for firstDate and secondDate in index 0 and 1 respectively
				firstSecondDates = list()

				for i in range(numberOfColumns):

					# Adding column for % conversion calculation
					# Phone interview to ...
					if(row[53] != "" and (type(row[53]) is datetime.datetime or type(row[53]) is str)):
						# On-site
						if(row[54] != "" and (type(row[54]) is datetime.datetime or type(row[54]) is str)):
							phoneToOnsite = True
						else:
							phoneToOnsite = False
						# Offer
						if(row[55] != "" and (type(row[55]) is datetime.datetime or type(row[55]) is str)):
							phoneToOffer = True
						else:
							phoneToOffer = False

					# Onsite to ...
					if(row[54] != "" and (type(row[54]) is datetime.datetime or type(row[54]) is str)):
						# offer
						if(row[55] != "" and (type(row[55]) is datetime.datetime or type(row[55]) is str)):
							onsiteToOffer = True
						else:
							onsiteToOffer = False

					# Writing to dict
					dict_to_be_written['phoneToOnsite'] = phoneToOnsite
					dict_to_be_written['phoneToOffer'] = phoneToOffer
					dict_to_be_written['onsiteToOffer'] = onsiteToOffer

					# Converting date strings to datetime objects
					if headers[i] in all_The_date_columns and row[i] != '':
						if type(row[i]) is datetime.datetime:
							minDateCandidates.append(row[i])
						else:
							try:
								row[i] = datetime.datetime.strptime(
									row[i], '%Y-%m-%d %H:%M:%S')
								minDateCandidates.append(row[i])
							except:
								try:
									row[i] = datetime.datetime.strptime(
										row[i], '%d-%m-%Y %H:%M')
									minDateCandidates.append(row[i])
								except:
									try:
										row[i] = datetime.datetime.strptime(
											row[i], '%Y-%m-%d')
										minDateCandidates.append(row[i])
									except:
										try:
											row[i] = datetime.datetime.strptime(
												row[i], '%m-%d-%y %H:%M')
											minDateCandidates.append(row[i])
										except:
											try:
												row[i] = datetime.datetime.strptime(
													row[i], '%d-%m-%y %H:%M')
												minDateCandidates.append(row[i])
											except:
												print(
													f"{row[i]} is problematic -------*************-------------<<<<<")


					if row[i] == "":
						# row[i] = None
						row[i] = datetime.datetime(1990, 1, 1)

					


					# Deciding minimum Created date for posting
					# Note that this is actually an approximation since it finds the first applied date for a posting
					# row[21] is Created At date
					# row[24] is Posting ID
					try:
						row[22] = datetime.datetime.strptime(
							row[22], '%Y-%m-%d %H:%M:%S')
					except:
						try:
							row[22] = datetime.datetime.strptime(
								row[22], '%d-%m-%Y %H:%M')
						except:
							row[22] = row[22]
					if row[24] != "" and row[24] != None:
						if row[24] not in dict_of_posting_creation_date:
							dict_of_posting_creation_date[row[24]] = row[22]
						else:
							if dict_of_posting_creation_date[row[24]] > row[22]:
								dict_of_posting_creation_date[row[24]
															  ] = row[22]

					# Making dict entry for each column
					dict_to_be_written[headers[i]] = row[i]



					# Properly determine firstDate and secondDate in candidates lifecycle
					if headers[i] in all_The_Stages_minus_hired and row[i] != datetime.datetime(1990, 1, 1):
						firstSecondDates.append(row[i])
					

					# This will help in deciding number of days taken by recruiter in acting on an applied candidate
					if len(firstSecondDates) >= 2:
						dict_to_be_written['Days to move from first stage'] = (firstSecondDates[1]-firstSecondDates[0]).days
						dict_to_be_written['Days to move from first stage_decider'] = str(firstSecondDates[1]) + " - " + str(firstSecondDates[0])
						# print(f"Difference in days{firstSecondDates[1]} - {firstSecondDates[0]}  = {(firstSecondDates[1]-firstSecondDates[0]).days}")
					
					else:
						dict_to_be_written['Days to move from first stage'] = -1




				if len(minDateCandidates) > 0:
					dict_to_be_written['Min Date'] = min(minDateCandidates)
					dict_to_be_written['Max Date'] = max(minDateCandidates)
				else:
					dict_to_be_written['Min Date'] = datetime.datetime(
						2005, 12, 1)
					dict_to_be_written['Max Date'] = datetime.datetime(
						2030, 12, 1)

				box.append(dict_to_be_written)

				line_count += 1
				# print(f"Inserting: {line_count}")
				# if line_count == 3:
				#   break

			else:
				headers = tuple(row)
				numberOfColumns = len(headers)
				line_count += 1

	# Inserting the posting created date in dict
	for i in range(len(box)):
		if box[i]['Posting ID'] is not None:
			box[i]["postingCreatedDate"] = dict_of_posting_creation_date[box[i]['Posting ID']]

	# Inserting into MOngoDB
	# for di in box:
	#   collection.insert_one(di)

	postingActualOwnersDict = dict()

	# Removing duplicates & then adding to DB
	currentStages = ['New lead', 'Reached out', 'Responded', 'New applicant',   'Recruiter screen', 'Profile review',
					 'Case study', 'Phone interview', 'On-site interview', 'Offer', 'Offer Approval', 'Offer Approved']
	postingDict = {}
	for row in box:
		addPostingToPostingDict(
			row, postingDict, currentStages, postingActualOwnersDict)

	# Determining Actual Posting Owner Name before writing
	# Now fetchingActual Posting Owner Name directly from jobPostingWiseDB, we don't have to detemine that now
	jobPostingWiseDBCollection = database["jobPostingWiseDB"]
	jobPostingWiseDBBox = jobPostingWiseDBCollection.find({})
	postingActualOwnersDict2 = dict()
	for jobPostingWise in jobPostingWiseDBBox:
		if jobPostingWise["Posting ID"] not in postingActualOwnersDict2:
			postingActualOwnersDict2[jobPostingWise["Posting ID"]
									 ] = jobPostingWise["Posting Owner"]

	for x in postingDict.keys():
		for y in postingDict[x].keys():
			postingDict[x][y]["Actual Posting Owner Name"] = postingActualOwnersDict2[x]
			collection.insert_one(postingDict[x][y])

	# Compound Indexing DB
	# collection.create_index([("Posting Title", pymongo.DESCENDING)])
	collection.create_index([("Posting Department", ASCENDING), ("Posting Team", ASCENDING), (
		"Posting Title", ASCENDING), ("Actual Posting Owner Name", ASCENDING)])

	collection.create_index(
		[("Origin", DESCENDING), ("Applied At (GMT)", DESCENDING)])

	# os.remove(file_to_open)
	print("File Deleted")




def addPostingToPostingDict(ro, postingDict, currentStages, postingActualOwnersDict):
	# if ro['Posting ID'] and ro['Profile ID'] is not None:
	if not isinstance(ro['Posting ID'], datetime.datetime) and not isinstance(ro['Profile ID'], datetime.datetime):
		pst = ro['Posting ID']
		prfl = ro['Profile ID']
	else:
		return

	if pst not in postingDict:
		postingDict[pst] = {}
		postingDict[pst][prfl] = ro

		# Create a new posting entry in dict
		postingActualOwnersDict[pst] = dict()
		postingActualOwnersDict[pst]["Actual Posting Owner Name"] = ro["Posting Owner Name"]
		postingActualOwnersDict[pst]["Applied At (GMT)"] = ro["Applied At (GMT)"]

	else:

		# Check posting date & if its earlier changing the Name
		if postingActualOwnersDict[pst]["Applied At (GMT)"] < ro["Applied At (GMT)"]:
			postingActualOwnersDict[pst]["Actual Posting Owner Name"] = ro["Posting Owner Name"]
			postingActualOwnersDict[pst]["Applied At (GMT)"] = ro["Applied At (GMT)"]

		if prfl not in postingDict[pst]:
			postingDict[pst][prfl] = ro

		else:
			stg1 = postingDict[pst][prfl]['Current Stage']
			stg2 = ro['Current Stage']

			# if currentStages.index(stg2) > currentStages.index(stg1):
			if ro['Max Date'] >= postingDict[pst][prfl]['Max Date']:
				postingDict[pst][prfl] = ro
			# postingDict[pst][prfl] = ro

# To delete /uploads folder at start of upload
def flushUploadsFolder():
	folder = '/var/www/FlaskApp/FlaskApp/uploaded_csv'
	for the_file in os.listdir(folder):
		file_path = os.path.join(folder, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			# elif os.path.isdir(file_path): shutil.rmtree(file_path)
		except Exception as e:
			print(e)
