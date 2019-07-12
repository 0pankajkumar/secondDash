import flask
from flask import request, jsonify, render_template, url_for
from pymongo import MongoClient, CursorType
import json
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
from random import randint

app = flask.Flask(__name__, static_url_path='',
                  static_folder='static',
                  template_folder='templates')
app.config["DEBUG"] = True

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["antDB"]


@app.route('/test1', methods=['GET'])
def test1():
    return render_template('test1.html')


@app.route('/getTable', methods=['POST'])
def getTable():
    postingTitle = request.form.get('postingTitle')
    companyName = request.form.get('companyName')
    postingTeam = request.form.get('postingTeam')
    postingArchiveStatus = request.form.get('postingTeam')

    results = getResults(postingTitle, companyName, postingTeam, postingArchiveStatus)
    return jsonify(results)


def getResults(title, companyName, team, archiveStatus):
    ts = time.time()
    rows = getFromDB(companyName)
    print('db: ' + str(time.time() - ts))
    res = []
    counts = dict()
    for item in rows:
        if item['Posting Title'] != title and title != 'All':
            continue
        if item['Posting Department'] != companyName and companyName != 'All':
            continue

        postId = item['Posting ID']
        origin = item['Origin']
        if not postId in counts:
            counts[postId] = dict()
        if not origin in counts[postId]:
            counts[postId][origin] = dict()
            counts[postId][origin]['new_lead'] = 0
            counts[postId][origin]['recruiter_screen'] = 0
        originCounts = counts[postId][origin]
        if 'Stage - New lead' in item and item['Stage - New lead'] != None:
            originCounts['new_lead'] += 1
        elif 'Stage - Recruiter screen' in item and item['Stage - Recruiter screen'] != None:
            originCounts['recruiter_screen'] += 1

    for postId in counts:
        res.append(actualPostId(postId, counts[postId]))
    print('total: ' + str(time.time() - ts))
    return res


def getFromDB(companyName):
    # collection.drop()
    # collection.insert_one({'posting_id' : randint(1,10), 'origin' : randint(1,3), 'Stage - New Lead' : '2019-01-01'})
    # collection.insert_one({'posting_id' : randint(1,10), 'origin' : randint(1,3), 'Stage - Recruiter Screen': '2019-02-02'})
    query = dict()
    if companyName != 'All':
        query['Posting Department'] = companyName
    return list(collection.find(query, cursor_type=CursorType.EXHAUST))


def actualPostId(postId, postIdCounts):
    children = []
    for origin in postIdCounts:
        children.append(actualResultForOrigin(origin, postIdCounts[origin]))
    return {
        'Posting ID': postId,
        '_children': children
    }


def actualResultForOrigin(origin, originCounts):
    return {
        'origin': origin,
        # 'newApplicantCount': smallRandomNumber(),
        "newLeadCount": originCounts['new_lead'],
        "recruiterScreenCount": originCounts['recruiter_screen'],
        # "phoneInterviewCount": smallRandomNumber(),
        # "onsiteInterviewCount": smallRandomNumber(),
        # "offerCount": smallRandomNumber(),
        # "reachedOutCount": smallRandomNumber()
    }


def smallRandomNumber():
    return randint(0, 10)


@app.route('/', methods=['GET'])
def uidropdowns():
    postingDepartment = set()
    postingTeam = set()
    postingTitle = set()
    postingArchiveStatus = set()

    rows = collection.find(cursor_type=CursorType.EXHAUST)
    for row in rows:
        postingDepartment.add(row['Posting Department'])
        postingTeam.add(row['Posting Team'])
        postingTitle.add(row['Posting Title'])
        postingArchiveStatus.add(row['Posting Archive Status'])
    return render_template('index.html', postingDepartment=postingDepartment, postingTeam=postingTeam,
                           postingTitle=postingTitle, postingArchiveStatus=postingArchiveStatus)


if __name__ == '__main__':
    app.run(debug=True)
























# Last
