from pymongo import MongoClient, CursorType
from flask_login import current_user
import datetime, time

# DB links for main collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]

# DB links for ApprovedUsers collection
collection = database["dolphinDB"]

# DB links for ApprovedUsers collection
collection2 = database["ApprovedUsers"]

# From new dup
collection4 = database["jobPostingWiseDB"]

