import flask
from flask import request, jsonify, render_template, url_for
from pymongo import MongoClient
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
collection = database["antDB"]

@app.route('/', methods=['GET'])
def test1():
	return render_template('test1.html')

@app.route('/getTable', methods=['POST'])
def getTable():
	return "yes"

if __name__ == '__main__':
	app.run(debug=True)
























#Last
