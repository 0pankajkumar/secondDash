from flask_login import UserMixin
from pymongo import MongoClient, CursorType
from flask_login import current_user
from flask import jsonify

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
approvedUsersCollection = database["ApprovedUsers"]

class User(UserMixin):
    def __init__(self, id_):
        self.id = id_

    @staticmethod
    def get(users_email):
        print(f"\nReceiving {users_email}\n")
        pa = approvedUsersCollection.find({'users': users_email})

        if pa:
            for p in pa:
                if p['users'] == users_email:
                    print("\nYeah, found a member of the club\n")
                    user = User(
                        id_=users_email
                    )
                    return user
                else:
                    print("\nNot found in DB\n")
                    return None
        else:
            print("\nNot found in DB\n")
            return None


    @staticmethod
    def suspicious(users_email):
        #log unauthorized users
        SuspiciousUsersCollection = database["SuspiciousUsers"]

        try:
            SuspiciousUsersCollection.insert_one({'email': users_email})
        except:
            print("Could not get hold of this trespassing")
        print("Logged in unauthorized")

def fetchUsers(usersList):
    pa = approvedUsersCollection.find({})
    for p in pa:
        usersDict = dict()
        usersDict['users'] = p['users']
        usersDict['type'] = p['type']
        usersDict['tatMember'] = p['tatMember']
        if 'whichPositions' in p:
            usersDict['whichPositions'] = p['whichPositions']
        else:
            usersDict['whichPositions'] = "Not defined"
        usersList.append(usersDict)
