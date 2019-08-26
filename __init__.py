import flask
from flask import request, jsonify, render_template, url_for, redirect, session
from flask_session import Session
from werkzeug import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads, UploadNotAllowed
from pymongo import MongoClient, CursorType
import json
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
from random import randint
import os, tempfile
import datetime
from functools import wraps

# For helpers
import csv
from pathlib import Path

# For google login
from google.oauth2 import id_token
from google.auth.transport import requests













# Python standard libraries
import json
import os
import sqlite3

# Third party libraries
from flask import Flask, redirect, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
# from db import init_db_command
from FlaskApp.user import User


app = flask.Flask(__name__, static_url_path='',
                  static_folder='static',
                  template_folder='templates')
app.config["DEBUG"] = False

# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["eucalyptusDB"]

# DB links for ApprovedUsers collection
collection2 = database["ApprovedUsers"]

# Clearing caches
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = tempfile.mkdtemp()
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# configure flask_upload API
documents = UploadSet("documents", ('csv'))
app.config["UPLOADED_DOCUMENTS_DEST"] = "/var/www/FlaskApp/FlaskApp/uploaded_csv"
configure_uploads(app, documents)


# def login_required(f):
#     """
#     Decorate routes to require login.
#     http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
#     """
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         # print("333333333333 Inside Decorators 33333333333")
#         if session.get("user_id") is None:
#             # print("Inside")
#             # print(session)
#             return redirect("/")
#         # else:
#         #   print("Outisde")
#         #   print(session)
#         return f(*args, **kwargs)
#     return decorated_function




@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template('uploader.html')
    elif request.method == 'POST':
        f = request.files['file']
        print(f.filename, secure_filename(f.filename))
        file = documents.save(request.files['file'], name="dump.csv")
        # f = request.files['file']
        # f.save(secure_filename(f.filename))
        # os.remove(app.config["UPLOADED_DOCUMENTS_DEST"] + "/" + str())
        return 'File Uploaded Successfully'

# This route gives status when it's uploading
@app.route('/updating', methods=['GET', 'POST'])
@login_required
def updating():

    # The database uploading method comes here
    res = 'starting'
    updateMongo()
    # try:
    #   updateMongo()
    #   res = 'Database Successfully Updated'
    # except:
    #   res = 'Database update failed. Please contact admin'
    return jsonify(res)


@app.route('/test2', methods=['GET'])
@login_required
def test1():
    return render_template('test2.html')

@app.route('/trial3', methods=['GET'])
# @login_required
def trial3():
    return render_template('trial3.html')


def generateMainPageDropdowns():
    postingDepartment = set()
    postingArchiveStatus = set()
    profileArchiveStatus = set()

    companiesAllowed = set()
    companiesAllowed = {'Campus', 'Codechef', 'Flock', 'Radix', 'Shared Services'}

    rows = collection.find(cursor_type=CursorType.EXHAUST)
    for row in rows:
        if row['Posting Department'] not in companiesAllowed:
            continue
        else:
            postingDepartment.add(row['Posting Department'])
        postingArchiveStatus.add(row['Posting Archive Status'])
        profileArchiveStatus.add(row['Profile Archive Status'])

    #Sorting the set alphabatically
    postingDepartment = sorted(postingDepartment)

    # Packing everything to return
    returnList = {}
    returnList['postingDepartment'] = postingDepartment
    returnList['postingArchiveStatus'] = postingArchiveStatus
    returnList['profileArchiveStatus'] = profileArchiveStatus

    return returnList


@app.route('/funnel', methods=['GET'])
@login_required
def funnel():
    returnedDict = generateMainPageDropdowns()
    return render_template('funnel.html', postingDepartment=returnedDict['postingDepartment'], postingArchiveStatus = returnedDict['postingArchiveStatus'], profileArchiveStatus = returnedDict['profileArchiveStatus'])


@app.route('/getTable', methods=['POST'])
@login_required
def getTable():
    # collection.createIndex('Posting Department')

    postingTitle = request.form.get('postingTitle')
    companyName = request.form.get('companyName')
    postingTeam = request.form.get('postingTeam')
    postingArchiveStatus = request.form.get('postingArchiveStatus')
    profileArchiveStatus = request.form.get('profileArchiveStatus')
    age = request.form.get('age')

    results = getResults(postingTitle, companyName, postingTeam, postingArchiveStatus, profileArchiveStatus, age)
    # results = getResults("Backend Engineer", "Flock", "Software Engineering", "All")
    return jsonify(results)


def getResults(title, companyName, team, archiveStatus, profileArchiveStatus, age):
    ts = time.time()
    rows = getFromDB(companyName) # title, companyName, team, archiveStatus
    print('db: ' + str(time.time() - ts))
    res = []
    counts = dict()
    benchmark_date = interpretAge(age)
    for item in rows:
        if item['Posting Title'] != title and title != 'All':
            continue
        if item['Posting Team'] != team and team != 'All':
            continue
        if item['Posting Archive Status'] != archiveStatus and archiveStatus != 'All' and archiveStatus != 'Both':
            continue
        if item['Profile Archive Status'] != profileArchiveStatus and profileArchiveStatus != 'All' and profileArchiveStatus != 'Both':
            continue
        
        if item['Min Date'] < benchmark_date:
            # print(f"{item['Min Date']} < {benchmark_date}")
            continue
        

        # Modified posting ID for display
        # item['Created At (GMT)'] =  datetime.datetime.strptime(str(item['Created At (GMT)']), '%Y-%m-%d %H:%M:%S').strftime('%B %Y')
        # postId = str(item['Posting ID']) + ", " + str(item['Posting Title']) + ", " + str(item['Posting Location']) + ", " + item['Created At (GMT)']

        if 'postingCreatedDate' in item:
            dateForLabel = str(item['postingCreatedDate'].strftime('%b')) + " " + str(item['postingCreatedDate'].strftime('%Y'))
        else:
            dateForLabel = "$"
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

            # var for % counts
            counts[postId][origin]['phone_To_Onsite'] = 0
            counts[postId][origin]['phone_To_Offer'] = 0
            counts[postId][origin]['onsite_To_Offer'] = 0

        originCounts = counts[postId][origin]
        
        if 'Stage - New lead' in item and item['Stage - New lead'] != None:
            originCounts['new_lead'] += 1
        if 'Stage - Reached out' in item and item['Stage - Reached out'] != None:
            originCounts['reached_out'] += 1
        if 'Stage - New applicant' in item and item['Stage - New applicant'] != None:
            originCounts['new_applicant'] += 1
        if 'Stage - Recruiter screen' in item and item['Stage - Recruiter screen'] != None:
            originCounts['recruiter_screen'] += 1

        if 'Stage - Phone interview' in item and item['Stage - Phone interview'] != None:
            originCounts['phone_interview'] += 1
            # Counting for % conversion
            if 'Stage - On-site interview' in item and item['Stage - On-site interview'] != None:
                originCounts['phone_To_Onsite'] += 1
            if 'Stage - Offer' in item and item['Stage - Offer'] != None:
                originCounts['phone_To_Offer'] += 1

        if 'Stage - On-site interview' in item and item['Stage - On-site interview'] != None:
            originCounts['onsite_interview'] += 1
            # Counting for % conversion
            if 'Stage - Offer' in item and item['Stage - Offer'] != None:
                originCounts['onsite_To_Offer'] += 1

        if 'Stage - Offer' in item and item['Stage - Offer'] != None:
            originCounts['offer'] += 1

    for postId in counts:
        res.append(actualPostId(postId, counts[postId]))
    print('total: ' + str(time.time() - ts))
    return res


def getFromDB(companyName): # title, companyName, team, archiveStatus):
    # collection.drop()
    # collection.insert_one({'posting_id' : randint(1,10), 'origin' : randint(1,3), 'Stage - New Lead' : '2019-01-01'})
    # collection.insert_one({'posting_id' : randint(1,10), 'origin' : randint(1,3), 'Stage - Recruiter Screen': '2019-02-02'})
    query = dict()
    if companyName != 'All':
        query['Posting Department'] = companyName
        # query['Posting Title'] = title
        # query['Posting Team'] = team
        # query['Posting Archive Status'] = archiveStatus
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
        'newApplicantCount': originCounts['new_applicant'],
        "newLeadCount": originCounts['new_lead'],
        "recruiterScreenCount": originCounts['recruiter_screen'],
        "phoneInterviewCount": originCounts['phone_interview'],
        "onsiteInterviewCount": originCounts['onsite_interview'],
        "offerCount": originCounts['offer'],
        "reachedOutCount": originCounts['reached_out'],
        "phoneToOnsiteCount": originCounts['phone_To_Onsite'],
        "phoneToOfferCount": originCounts['phone_To_Offer'],
        "onsiteToOfferCount": originCounts['onsite_To_Offer']
    }


def smallRandomNumber():
    return randint(0, 10)

# Returns back date n days from now based on string passed
def interpretAge(age):
    if age == "beginningOfTime":
        return(datetime.datetime(2005,12,1))
    lis = age.split()
    multiplier = int(lis[0])
    day_or_month = lis[1]

    if day_or_month == "Days":
        # code for day
        benchmark_date = datetime.datetime.now() - datetime.timedelta(days=multiplier)


    if day_or_month == "Months":
        # code for month
        benchmark_date = datetime.datetime.now() - datetime.timedelta(days=multiplier*30)

    return benchmark_date



@app.route('/getBigDict', methods=['GET'])
@login_required
def getBigDict():
    bigDict = dict()
    rows = collection.find(cursor_type=CursorType.EXHAUST)

    for row in rows:
        if row['Posting Department'] == 'Kapow' or row['Posting Department'] == None or row['Posting Department'] == 'Yikes! No Relevant Roles' or row['Posting Department'] == "":
            continue

        # Making a big data structure for all dropdowns in front end
        makeBigDict(bigDict, row['Posting Department'], row['Posting Team'], row['Posting Title'])
    return jsonify(bigDict)

@app.route('/table', methods=['GET'])
@login_required
def table():
    returnedDict = generateMainPageDropdowns()
    return render_template('index.html', postingDepartment=returnedDict['postingDepartment'], postingArchiveStatus = returnedDict['postingArchiveStatus'], profileArchiveStatus = returnedDict['profileArchiveStatus'])



# Make this function reject users who are already added
# Add a delete option as well
@app.route("/modifyUser", methods=['GET', 'POST'])
# @login_required
def addUser():

    usersList = list()
    fetchUsers(usersList)
    
    if request.method == "GET":
        return render_template("modifyUser.html",usersList = usersList)

    if request.method == "POST":
        # Do the insertion stuff
        if request.form.get('actionType') == "addUser":
            addThisUser = request.form.get('emailID')
            makeAdmin = request.form.get('typeOfUser')
            
            if makeAdmin == "Admin":
                collection2.insert_one({"users": addThisUser, "type":"admin"})
            else:
                collection2.insert_one({"users": addThisUser, "type":"regular"})

            # Fetch users
            usersList = []
            fetchUsers(usersList)

        if request.form.get('actionType') == "deleteUser":
            deleteThisUser = request.form.get('users')
            collection2.delete_many( { "users" : deleteThisUser } );
            print(f"Deleted {deleteThisUser}")

    return render_template("modifyUser.html",usersList = usersList)


def fetchUsers(usersList):
    pa = collection2.find({})
    for p in pa:
        usersDict = dict()
        usersDict['users'] = p['users']
        usersDict['type'] = p['type']
        usersList.append(usersDict)


# Make that bigDict step by step
def makeBigDict(bigDict, postDept, postTeam, postTitle):
    if postDept not in bigDict:
        bigDict[str(postDept)] = {}
    if postTeam not in bigDict[str(postDept)]:
        bigDict[str(postDept)][str(postTeam)] = []
    if 'All' not  in bigDict[str(postDept)]:
        bigDict[str(postDept)]['All'] = []
    if postTitle not in bigDict[postDept][postTeam]:
        bigDict[str(postDept)][str(postTeam)].append(postTitle)
        bigDict[str(postDept)]['All'].append(postTitle)


# Helpers file
def customMessages(message):
    render_template("customMessages.html", message = message)


def updateMongo():
    client = MongoClient("mongodb://localhost:27017")
    database = client["local"]
    collection = database["eucalyptusDB"]


    all_The_Stages = ['Stage - New lead', 'Stage - Reached out', 'Stage - Responded', 'Stage - New applicant', 'Stage - Recruiter screen', 'Stage - Profile review', 'Stage - Case study', 'Stage - Phone interview', 'Stage - On-site interview', 'Stage - Offer']
    headers = tuple()
    line_count = 0
    dict_of_posting_creation_date = dict()
    box = []
    fileName = "uploaded_csv/dump.csv"

    collection.delete_many({})
    print("Deleted everything")
    print("Adding records...")

    # relative path inspired from here https://medium.com/@ageitgey/python-3-quick-tip-the-easy-way-to-deal-with-file-paths-on-windows-mac-and-linux-11a072b58d5f
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    data_folder = Path("/var/www/FlaskApp/FlaskApp/uploaded_csv")
    file_to_open = data_folder / "dump.csv" 

    with open(str(file_to_open), 'r', encoding="utf8" ) as csvfile:
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
                            try:
                                row[i] = datetime.datetime.strptime(row[i], '%d-%m-%Y %H:%M')
                                minDateCandidates.append(row[i])
                            except:
                                row[i] = datetime.datetime.strptime(row[i], '%Y-%m-%d')
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
                else:
                    dict_to_be_written['Min Date'] = datetime.datetime(2005,12,1)


                box.append(dict_to_be_written)
            


                line_count += 1
                # print(f"Inserting: {line_count}")
                # if line_count == 3:
                #   break

                
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

    os.remove(file_to_open)
    print("File Deleted")








































@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404




# Configuration
GOOGLE_CLIENT_ID = open('/etc/googleauth/googleauthid','r').readlines()[0].strip()
GOOGLE_CLIENT_SECRET = open('/etc/googleauth/googleauthsecret','r').readlines()[0].strip()
#GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
#GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
# app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    return render_template("unauthorized.html"), 403


# Naive database setup
# try:
#     init_db_command()
# except sqlite3.OperationalError:
#     # Assume it's already been created
#     pass

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/settings")
@login_required
def settings():
    return "Authorized"

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('table'))


    else:
        # return '<a class="button" href="/login">Google Login</a>'
        return render_template("login.html")


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    user = User(
        id_=users_email
    )

    # Doesn't exist? Add to database
    if not User.get(users_email):
        # User.create(users_email)
        print("User doesn't exist")

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


if __name__ == "__main__":
    app.run()
