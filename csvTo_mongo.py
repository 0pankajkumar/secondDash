import csv  
import json
import datetime
from pymongo import MongoClient, CursorType
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
import datetime  


client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["dolphinDB"]


all_The_Stages = ['Stage - New lead', 'Stage - Reached out', 'Stage - Responded', 'Stage - New applicant', 'Stage - Recruiter screen', 'Stage - Profile review', 'Stage - Case study', 'Stage - Phone interview', 'Stage - On-site interview', 'Stage - Offer']
headers = tuple()
line_count = 0
dict_of_posting_creation_date = dict()
box = []

collection.delete_many({})
print("Deleted everything")
print("Adding records...")
with open('d4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (4).csv', 'r', encoding="utf8" ) as csvfile:
	myReader = csv.reader(csvfile, delimiter=',')
	for row in myReader:
		minDateCandidates = list()
		dict_to_be_written = dict()
		if line_count > 0:
			#Making dict for DB

			row = [r.strip() for r in row]
			 
			for i in range(numberOfColumns):
				if headers[i] in all_The_Stages and row[i] != '':
					try:
						row[i] = datetime.datetime.strptime(row[i], '%Y-%m-%d %H:%M:%S')
						minDateCandidates.append(row[i])
					except:
						row[i] = datetime.datetime.strptime(row[i], '%d-%m-%Y %H:%M')
						minDateCandidates.append(row[i])
					
				if row[i] == "":
					row[i] = None



				# Deciding minimum Created date for posting
				# Note that this is actually an approximation since it finds the first applied date for a posting
				# row[21] is Created At date
				# row[24] is Posting ID
				try:
					row[21] = datetime.datetime.strptime(row[21], '%Y-%m-%d %H:%M:%S')
				except:
					try:
						row[21] = datetime.datetime.strptime(row[21], '%d-%m-%Y %H:%M')
					except:
						row[21] = row[21]
				if row[24] != "" and row[24] != None:
					if row[24] not in dict_of_posting_creation_date:
						dict_of_posting_creation_date[row[24]] = row[21]
					else:
						if dict_of_posting_creation_date[row[24]] > row[21]:
							dict_of_posting_creation_date[row[24]] = row[21]

				# postingIdNow = None
				# Deciding which is the earliest date for Posting
				# if headers[i] == "Posting ID"
				# 	if row[i] not in dict_of_posting_created:
				# 		dict_of_posting_created[row[i]] = datetime.datetime(2050,12,1)
				# 		postingIdNow = row[i]
				# if headers[i] == "Created At (GMT)":
				# 	if dict_of_posting_created[row[i]] < row[i] and headers[i] == "Created At (GMT)"
				# 		dict_of_posting_created[row[i]]


				# postingCreatedDate = datetime.datetime(2005,12,1)
				# if headers[i] == "Created At (GMT)":
				# 	try:
				# 		just_a_Date = datetime.datetime.strptime(row[i], '%Y-%m-%d %H:%M:%S')
				# 	except:
				# 		just_a_Date = datetime.datetime.strptime(row[i], '%d-%m-%Y %H:%M')
				# 	if just_a_Date < postingCreatedDate:
				# 		postingCreatedDate = just_a_Date
				# dict_to_be_written['postingCreatedDate'] = postingCreatedDate


				# Making dict entry for each column
				dict_to_be_written[headers[i]] = row[i]

			if len(minDateCandidates) > 0:
				dict_to_be_written['Min Date'] = min(minDateCandidates)
			else:
				dict_to_be_written['Min Date'] = datetime.datetime(2005,12,1)


			box.append(dict_to_be_written)
		


			line_count += 1
			# print(f"Inserting: {line_count}")
			# if line_count == 3:
			# 	break

			
		else:
			headers= tuple(row)
			numberOfColumns = len(headers)
			line_count += 1
			

# Inserting the posting created date in dict
for i in range(len(box)):
	if box[i]['Posting ID'] is not None:
		box[i]["postingCreatedDate"] = dict_of_posting_creation_date[box[i]['Posting ID']]

# Inserting into MOngoDB
for di in box:
	collection.insert_one(di)