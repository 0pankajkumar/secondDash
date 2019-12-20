
from pymongo import MongoClient, CursorType
import json
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
from random import randint
import os
import csv
from pathlib import Path

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["jobPostingWiseDB"]

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
data_folder = Path("/var/www/FlaskApp/FlaskApp/")

# data_folder = Path("C:\\Users\\pankaj.kum\\Desktop\\zetaDash")
file_to_open = data_folder / "JobPostingDump.csv"

def getInDateFormat(r, ty):
	# 2017-11-13 10:15:40
	# 2019-09-03 05:50:35
	r = r.strip()
	r = unicode(r, "utf-8")
	try:
		return datetime.datetime.strptime(r, '%Y-%m-%d %H:%M:%S')
	except:
		try:
			return datetime.datetime.strptime(r, '%d-%m-%Y %H:%M')
		except:
			try:
				return datetime.datetime.strptime(r, '%Y-%m-%d')
			except:
				try:
					return datetime.datetime.strptime(r, '%m-%d-%y %H:%M')
				except:
					try:
						return datetime.datetime.strptime(r, '%d-%m-%y %H:%M')
					except:
						try:
							return datetime.datetime.strptime(r, '%d-%m-%Y %H:%M %p')
						except:
							ty[0] += 1
							print(f"{r} {type(r)} is problematic -------*************-------------<<<<<")
							return r



with open(str(file_to_open), 'r', encoding="utf8" ) as csvfile:
	myReader = csv.reader(csvfile, delimiter=',')

	titlesWanted = ["Posting ID", "Posting Title", "Applications", "Date Created (GMT)", "Last Updated (GMT)", "Status", "Posting Team", "Posting Owner", "Posting Owner Email", "Posting Department", "State"]
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
					# 	r = getInDateFormat(r, ty)
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

print(ty)
# for fi in finalBox:
# 	collection.insert_one(fi)
