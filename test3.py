import flask
from flask import request, jsonify, render_template, url_for
from werkzeug import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads, UploadNotAllowed
from pymongo import MongoClient, CursorType
import json
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
from random import randint
import os

app = flask.Flask(__name__, static_url_path='',
				  static_folder='static',
				  template_folder='templates')
app.config["DEBUG"] = False

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["antDB"]


@app.route('/getTable', methods=['POST'])
def getTable():
	# collection.createIndex('Posting Department')
	postingTitle = request.form.get('postingTitle')
	companyName = request.form.get('companyName')
	postingTeam = request.form.get('postingTeam')
	postingArchiveStatus = request.form.get('postingArchiveStatus')

	print(postingTitle)
	print(companyName)
	print(postingTeam)
	print(postingArchiveStatus)

	results = getResults(postingTitle, companyName, postingTeam, postingArchiveStatus)
	#results = getResults("Backend Engineer", "Flock", "Software Engineering", "All")
	return jsonify(results)

def getResults(title, companyName, team, archiveStatus):
	print(title)
	print(companyName)
	print(team)
	print(archiveStatus)
	return ["Success"]


if __name__ == '__main__':
	app.run(debug=True)