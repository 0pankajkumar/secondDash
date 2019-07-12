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
    res = []
    for i in range(1, 10):
        res.append(fakePostId('post-id' + str(i), randint(1,3)))
    return res

def fakePostId(postId, numChildren):
    children = []
    for i in range(1, numChildren):
        children.append(fakeResultForOrigin('origin-' + str(i)))
    return {
        'Posting ID': postId,
        '_children': children
    }

def fakeResultForOrigin(origin):
    return {
        'origin': origin,
        'newApplicantCount': smallRandomNumber(),
        "recruiterScreenCount": smallRandomNumber(),
        "phoneInterviewCount": smallRandomNumber(),
        "onsiteInterviewCount": smallRandomNumber(),
        "offerCount": smallRandomNumber(),
        "newLeadCount": smallRandomNumber(),
        "reachedOutCount": smallRandomNumber()
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
