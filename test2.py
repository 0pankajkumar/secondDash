import flask
from flask import request, jsonify, render_template, url_for
from pymongo import MongoClient, CursorType
import json
from bson import json_util, ObjectId
from bson.int64 import Int64
import datetime

app = flask.Flask(__name__,static_url_path='',
            static_folder='static',
            template_folder='templates')
app.config["DEBUG"] = True

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["ApprovedUsers"]

# collection.insert_one({ "users" : "pankajkum@directi.com", "type" : "admin", "tatMember" : "Nope", "companiesActuallyAllowed" : [ "Flock", "Radix", "Shared Services" ] })
# collection.insert_one({ "users" : "heman@flock.com", "type" : "admin", "tatMember" : "Nope", "companiesActuallyAllowed" : [ "Flock", "Radix", "Shared Services" ] })
# collection.insert_one({ "users" : "shwetha.d@directi.com", "type" : "admin", "tatMember" : "Nope", "companiesActuallyAllowed" : [ "Flock", "Radix", "Shared Services" ] })


rows = collection.find({"users": {"$in": ["pankajkum@directi.com", "shwetha.d@directi.com"]}}, cursor_type=CursorType.EXHAUST)

for ro in rows:
	print(ro['companiesActuallyAllowed'])


