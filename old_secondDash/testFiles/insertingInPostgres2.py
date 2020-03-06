import psycopg2
import csv
from datetime import datetime

with open('d4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (5).csv','rt',encoding="utf-8")as f:
	data = csv.reader(f)
	i = 0
	for row in data:
		if i == 1:
			print(row)
			break
		i += 1

		#datetime_object = datetime.strptime('2017-12-06 16:03:36', '%d-%m-%y %H:%M')