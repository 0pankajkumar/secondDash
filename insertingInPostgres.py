import psycopg2
import csv
from datetime import datetime

# with open('d4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (4).csv','rt',encoding="utf-8")as f:
# 	data = csv.reader(f)
# 	i = 0
# 	for row in data:
# 		if i == 1:
# 			print(row)
# 			break
# 		i += 1

# 		datetime_object = datetime.strptime('2017-12-06 16:03:36', '%Y-%m-%d %H:%M:%S')


import pandas as pd
result = pd.read_csv('d4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (4).csv')
result["Stage - New lead"] =  pd.to_datetime(result["Stage - New lead"], format='%Y-%m-%d %H:%M:%S')

result["Created At (GMT)"] =  pd.to_datetime(result["Created At (GMT)"], format='%Y-%m-%d %H:%M:%S')
result["Applied At (GMT)"] =  pd.to_datetime(result["Applied At (GMT)"], format='%Y-%m-%d %H:%M:%S')
result["Posting Archived At (GMT)"] =  pd.to_datetime(result["Posting Archived At (GMT)"], format='%Y-%m-%d %H:%M:%S')
result["Last Story At (GMT)"] =  pd.to_datetime(result["Last Story At (GMT)"], format='%Y-%m-%d %H:%M:%S')
result["Last Advanced At (GMT)"] =  pd.to_datetime(result["Last Advanced At (GMT)"], format='%Y-%m-%d %H:%M:%S')
result["Start Date"] =  pd.to_datetime(result["Start Date"], format='%Y-%m-%d %H:%M:%S')
result["Stage - New lead"] =  pd.to_datetime(result["Stage - New lead"], format='%Y-%m-%d %H:%M:%S')
result["Stage - Reached out"] =  pd.to_datetime(result["Stage - Reached out"], format='%Y-%m-%d %H:%M:%S')
result["Stage - Responded"] =  pd.to_datetime(result["Stage - Responded"], format='%Y-%m-%d %H:%M:%S')
result["Stage - New applicant"] =  pd.to_datetime(result["Stage - New applicant"], format='%Y-%m-%d %H:%M:%S')
result["Stage - Recruiter screen"] =  pd.to_datetime(result["Stage - Recruiter screen"], format='%Y-%m-%d %H:%M:%S')
result["Stage - Profile review"] =  pd.to_datetime(result["Stage - Profile review"], format='%Y-%m-%d %H:%M:%S')
result["Stage - Case study"] =  pd.to_datetime(result["Stage - Case study"], format='%Y-%m-%d %H:%M:%S')
result["Stage - Phone interview"] =  pd.to_datetime(result["Stage - Phone interview"], format='%Y-%m-%d %H:%M:%S')
result["Stage - On-site interview"] =  pd.to_datetime(result["Stage - On-site interview"], format='%Y-%m-%d %H:%M:%S')
result["Stage - Offer"] =  pd.to_datetime(result["Stage - Offer"], format='%Y-%m-%d %H:%M:%S')
result["Stage - Offer Approval"] =  pd.to_datetime(result["Stage - Offer Approval"], format='%Y-%m-%d %H:%M:%S')
result["Stage - Offer Approved"] =  pd.to_datetime(result["Stage - Offer Approved"], format='%Y-%m-%d %H:%M:%S')



print(result["Stage - Phone interview"][0])