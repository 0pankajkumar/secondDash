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
with open('d4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (4).csv', encoding="utf_8" ) as csvfile:
	myReader = csv.reader(csvfile, delimiter=',')
	

	for row in myReader:
		minDateCandidates = list()
		dict_to_be_written = dict()
		phoneToOnsite = False
		phoneToOffer = False
		onsiteToOffer = False
		if line_count > 0:
			#Making dict for DB

			row = [r.strip() for r in row]
			 
			for i in range(numberOfColumns):




				# Adding column for % conversion calculation
				#Phone interview to ...
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




				# Making dict entry for each column
				dict_to_be_written[headers[i]] = row[i]

			if len(minDateCandidates) > 0:
				dict_to_be_written['Min Date'] = min(minDateCandidates)
				dict_to_be_written['Max Date'] = max(minDateCandidates)
			else:
				dict_to_be_written['Min Date'] = datetime.datetime(2005,12,1)
				dict_to_be_written['Max Date'] = datetime.datetime(2030,12,1)


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