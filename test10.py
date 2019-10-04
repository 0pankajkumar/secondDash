from pymongo import MongoClient, CursorType
from bson import json_util, ObjectId
from bson.int64 import Int64
import datetime, time

def actualPostId(postId, postIdCounts):
    children = []
    for origin in postIdCounts:
        children.append(actualResultForOrigin(origin, postIdCounts[origin]))
    return {
        'title': postId,
        '_children': children
    }


def actualResultForOrigin(origin, originCounts):
    return {
        'title': origin,
        'newApplicantCount': originCounts['new_applicant'],
        "newLeadCount": originCounts['new_lead'],
        "recruiterScreenCount": originCounts['recruiter_screen'],
        "phoneInterviewCount": originCounts['phone_interview'],
        "onsiteInterviewCount": originCounts['onsite_interview'],
        "offerCount": originCounts['offer'],
        "offerApprovalCount": originCounts['offerApproval'],
        "hiredCount": originCounts['hired'],
        "reachedOutCount": originCounts['reached_out'],
        "phoneToOnsiteCount": originCounts['phone_To_Onsite'],
        "phoneToOfferCount": originCounts['phone_To_Offer'],
        "onsiteToOfferCount": originCounts['onsite_To_Offer']
    }


client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["dolphinDB"]

rows = collection.find({'Posting Department':'Flock'})

listOfBoxes = []


ts = time.time()
# Inbetween whatever you want to measure

title = 'Senior DevOps Engineer'
team = 'Software Engineering'
profileArchiveStatus = 'Both'
res = []
counts = dict()


for item in rows:
    if item['Posting Title'] != title and title != 'All':
        continue
    if item['Posting Team'] != team and team != 'All':
        continue

    if item['Profile Archive Status'] != profileArchiveStatus and profileArchiveStatus != 'All' and profileArchiveStatus != 'Both':
        continue

    
    if 'postingCreatedDate' in item:
        dateForLabel = f"{str(item['postingCreatedDate'].strftime('%b'))} {str(item['postingCreatedDate'].strftime('%Y'))}, "
        # dateForLabel = str(item['postingCreatedDate'].strftime('%b')) + " " + str(item['postingCreatedDate'].strftime('%Y'))
        dateForLabel += str(item['Posting Owner Name'])
    else:
        dateForLabel = f" $ "
        dateForLabel += str(item['Posting Owner Name'])
    postId = str(item['Posting Title']) + ", " + str(item['Posting Location']) + ", " + dateForLabel 

    origin = item['Origin']
    if not postId in counts:
        counts[postId] = dict()
    if not origin in counts[postId]:
        counts[postId][origin] = dict()
        counts[postId][origin]['new_lead'] = 0
        counts[postId][origin]['reached_out'] = 0
        counts[postId][origin]['new_applicant'] = 0
        counts[postId][origin]['recruiter_screen'] = 0
        counts[postId][origin]['phone_interview'] = 0
        counts[postId][origin]['onsite_interview'] = 0
        counts[postId][origin]['offer'] = 0
        counts[postId][origin]['offerApproval'] = 0
        counts[postId][origin]['hired'] = 0

        # var for % counts
        counts[postId][origin]['phone_To_Onsite'] = 0
        counts[postId][origin]['phone_To_Offer'] = 0
        counts[postId][origin]['onsite_To_Offer'] = 0

    originCounts = counts[postId][origin]



    if item['Stage - New lead'] >= fromDate and item['Stage - New lead'] <= toDate:
        originCounts['new_lead'] += 1
    if item['Stage - Reached out'] >= fromDate and item['Stage - Reached out'] <= toDate:
        originCounts['reached_out'] += 1
    if item['Stage - New applicant'] >= fromDate and item['Stage - New applicant'] <= toDate:
        originCounts['new_applicant'] += 1
    if item['Stage - Recruiter screen'] >= fromDate and item['Stage - Recruiter screen'] <= toDate:
        originCounts['recruiter_screen'] += 1

    if item['Stage - Phone interview'] >= fromDate and item['Stage - Phone interview'] <= toDate:
        originCounts['phone_interview'] += 1
        # Counting for % conversion
        if 'Stage - On-site interview' in item and item['Stage - On-site interview'] != None:
            originCounts['phone_To_Onsite'] += 1
        if 'Stage - Offer' in item and item['Stage - Offer'] != None:
            originCounts['phone_To_Offer'] += 1

    if item['Stage - On-site interview'] >= fromDate and item['Stage - On-site interview'] <= toDate:
        originCounts['onsite_interview'] += 1
        # Counting for % conversion
        if 'Stage - Offer' in item and item['Stage - Offer'] != None:
            originCounts['onsite_To_Offer'] += 1

    if item['Stage - Offer'] >= fromDate and item['Stage - Offer'] <= toDate:
        originCounts['offer'] += 1

    if item['Stage - Offer Approval'] >= fromDate and item['Stage - Offer Approval'] <= toDate:
        originCounts['offerApproval'] += 1

    if item['Stage - Offer Approved'] >= fromDate and item['Stage - Offer Approved'] <= toDate:
        originCounts['offerApproval'] += 1

    if item['Hired'] >= fromDate and item['Hired'] <= toDate:
        originCounts['hired'] += 1

    for postId in counts:
        res.append(actualPostId(postId, counts[postId]))



print(len(res))

print('db: ' + str(time.time() - ts))

    
