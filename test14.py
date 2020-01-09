import flask
from flask import request, jsonify, render_template, url_for, redirect, session
from flask_session import Session
from werkzeug import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads, UploadNotAllowed
from pymongo import MongoClient, CursorType, ASCENDING, DESCENDING
import json
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
from random import randint
import os, tempfile
import datetime
from functools import wraps

app = flask.Flask(__name__, static_url_path='',
				  static_folder='static',
				  template_folder='templates')
app.config["DEBUG"] = False

# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection4 = database["jobPostingWiseDB"]


companyName = "Flock"
rows = collection4.find({"Posting Department": companyName})

for ro in rows:
	print(ro["Posting Department"])
	
