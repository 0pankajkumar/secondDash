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
collection = database["bullDB"]

all_The_Stages = ['Stage - New lead', 'Stage - Reached out', 'Stage - Responded', 'Stage - New applicant', 'Stage - Recruiter screen', 'Stage - Profile review', 'Stage - Case study', 'Stage - Phone interview', 'Stage - On-site interview', 'Stage - Offer']
minDateCandidates = list()
headers = tuple()
line_count = 0

with open('d4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (5).csv', 'r', encoding="utf8" ) as csvfile:
	myReader = csv.reader(csvfile, delimiter=',')
	for row in myReader:
		dict_to_be_written = dict()
		if line_count > 0:
			#Making dict for DB

			row = [r.strip() for r in row]
			 
			for i in range(numberOfColumns):
				if headers[i] in all_The_Stages and row[i] != '':
					row[i] = datetime.datetime.strptime(row[i], '%d-%m-%y %H:%M')
					minDateCandidates.append(row[i])

				dict_to_be_written[headers[i]] = row[i]

			if len(minDateCandidates) > 0:
				dict_to_be_written['Min Date'] = min(minDateCandidates)
			else:
				dict_to_be_written['Min Date'] = datetime.datetime(2005,12,1)



			
			# print(f"{minDateCandidates} \n Min is : {dict_to_be_written['Min Date']}")

			# print(json.dumps(dict_to_be_written, sort_keys=True, indent=4))
			collection.insert_one(dict_to_be_written)
			# print(dict_to_be_written)












			line_count += 1
			# print(f"Inserting: {line_count}")
			# if line_count == 3:
			# 	break

			










		else:
			headers= tuple(row)
			numberOfColumns = len(headers)
			line_count += 1
			

