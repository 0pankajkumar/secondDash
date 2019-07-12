import flask
from flask import request, jsonify, render_template, url_for
from pymongo import MongoClient
import json
from bson import json_util, ObjectId
from bson.int64 import Int64
import datetime
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
    results = getResults()
    return jsonify(results)

def getResults():
    rows = getFromDB()
    res = []
    counts = dict()
    for item in rows:
        postId = item['posting_id']
        origin = item['origin']
        if not postId in counts:
            counts[postId] = dict()
        if not origin in counts[postId]:
            counts[postId][origin] = dict()
            counts[postId][origin]['new_lead'] = 0
            counts[postId][origin]['recruiter_screen'] = 0
        originCounts = counts[postId][origin]
        if item['stage'] == 'new_lead':
            originCounts['new_lead'] += 1
        elif item['stage'] == 'recruiter_screen':
            originCounts['recruiter_screen'] += 1

    for postId in counts:
        res.append(actualPostId(postId, counts[postId]))
    return res


def getFromDB():
    # collection.drop()
    # collection.insert_one({'posting_id' : randint(1,10), 'origin' : randint(1,3), 'stage' : 'new_lead'})
    # collection.insert_one({'posting_id' : randint(1,10), 'origin' : randint(1,3), 'stage' : 'recruiter_screen'})
    return collection.find()

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
    postingDepartment = []
    postingTeam = []
    postingTitle = []
    postingArchiveStatus = []

    box = []
    box.append(postingDepartment)
    box.append(postingTeam)
    box.append(postingTitle)
    box.append(postingArchiveStatus)

    return render_template('index.html', postingDepartment=postingDepartment, postingTeam=postingTeam,
                           postingTitle=postingTitle, postingArchiveStatus=postingArchiveStatus)


if __name__ == '__main__':
    app.run(debug=True)
























# Last
