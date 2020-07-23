from flask import Flask
import flask
from flask import request, jsonify, render_template, url_for, redirect, session
from flask_session import Session
from werkzeug import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads, UploadNotAllowed
from pymongo import MongoClient, CursorType, ASCENDING, DESCENDING
import json, math
from bson import json_util, ObjectId
from bson.int64 import Int64
import time
from random import randint
import os
import tempfile
import datetime
from functools import wraps

# For deleting uploads
import os
import shutil

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

# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["dolphinDB"]

# DB links for ApprovedUsers collection
collection2 = database["ApprovedUsers"]

# From new dup
collection4 = database["jobPostingWiseDB"]

# For saving custom filters for each user
collection5 = database["moreInfo"]


# app = Flask(__name__)
app = Flask(__name__, static_url_path='',
				  static_folder='FlaskApp/FlaskApp/static',
				  template_folder='FlaskApp/FlaskApp/templates')
app.config["DEBUG"] = False

from FlaskApp.FlaskApp import views