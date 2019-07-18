import psycopg2
import csv
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

# with open('d4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (4).csv','rt',encoding="utf-8")as f:
# 	data = csv.reader(f)
# 	i = 0
# 	for row in data:
# 		if i == 1:
# 			print(row)
# 			break
# 		i += 1

# 		datetime_object = datetime.strptime('2017-12-06 16:03:36', '%d-%m-%y %H:%M')



result = pd.read_csv('d4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (5).csv')


# result["Created At (GMT)"] =  pd.to_datetime(result["Created At (GMT)"], format='%d-%m-%y %H:%M')
# result["Applied At (GMT)"] =  pd.to_datetime(result["Applied At (GMT)"], format='%d-%m-%y %H:%M')
# result["Posting Archived At (GMT)"] =  pd.to_datetime(result["Posting Archived At (GMT)"], format='%d-%m-%y %H:%M')
# result["Last Story At (GMT)"] =  pd.to_datetime(result["Last Story At (GMT)"], format='%d-%m-%Y %H:%M:%S %p')
# result["Last Advanced At (GMT)"] =  pd.to_datetime(result["Last Advanced At (GMT)"], format='%Y-%m-%d %H:%M:%S')
# result["Start Date"] =  pd.to_datetime(result["Start Date"], format='%d-%m-%y %H:%M')
# result["Stage - New lead"] =  pd.to_datetime(result["Stage - New lead"], format='%d-%m-%y %H:%M')
# result["Stage - Reached out"] =  pd.to_datetime(result["Stage - Reached out"], format='%d-%m-%y %H:%M')
# result["Stage - Responded"] =  pd.to_datetime(result["Stage - Responded"], format='%d-%m-%y %H:%M')
# result["Stage - New applicant"] =  pd.to_datetime(result["Stage - New applicant"], format='%d-%m-%y %H:%M')
# result["Stage - Recruiter screen"] =  pd.to_datetime(result["Stage - Recruiter screen"], format='%d-%m-%y %H:%M')
# result["Stage - Profile review"] =  pd.to_datetime(result["Stage - Profile review"], format='%d-%m-%y %H:%M')
# result["Stage - Case study"] =  pd.to_datetime(result["Stage - Case study"], format='%d-%m-%y %H:%M')
# result["Stage - Phone interview"] =  pd.to_datetime(result["Stage - Phone interview"], format='%d-%m-%y %H:%M')
# result["Stage - On-site interview"] =  pd.to_datetime(result["Stage - On-site interview"], format='%d-%m-%y %H:%M')
# result["Stage - Offer"] =  pd.to_datetime(result["Stage - Offer"], format='%d-%m-%y %H:%M')
# result["Stage - Offer Approval"] =  pd.to_datetime(result["Stage - Offer Approval"], format='%d-%m-%y %H:%M')
# result["Stage - Offer Approved"] =  pd.to_datetime(result["Stage - Offer Approved"], format='%d-%m-%y %H:%M')



# print(result["Stage - Phone interview"][0])


engine = create_engine('postgresql://postgres:Quad2core@@localhost:5432/postgres')
result.to_sql('table_name', engine, if_exists='replace', index=False)