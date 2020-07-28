"""User management & validation"""

from flask_login import UserMixin
from pymongo import MongoClient, CursorType
from flask_login import current_user
from flask import jsonify

client = MongoClient("mongodb://localhost:27017")
database = client["local"]
approvedUsersCollection = database["ApprovedUsers"]

class User(UserMixin):
    """A user centric class which validates & reports suspicion"""

    def __init__(self, id_):
        self.id = id_

    @staticmethod
    def get(users_email):
        """Returns user object for assimilation"""

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
        """log unauthorized users"""

        SuspiciousUsersCollection = database["SuspiciousUsers"]

        try:
            SuspiciousUsersCollection.insert_one({'email': users_email})
        except:
            print("Could not get hold of this trespassing")
        print("Logged in unauthorized")

def fetchUsers(usersList):
    """Packs all users & their details"""

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

def addUserHelper(addThisUser, makeAdmin, positionFilter, tatmember, companiesToBeAllowed):
    """Helps in adding user to the club"""

    if makeAdmin == "Admin":
        if tatMember == "Nope":
            approvedUsersCollection.insert_one({"users": addThisUser, "type": "admin", "tatMember": "Nope",
                                    "companiesActuallyAllowed": companiesToBeAllowed, "whichPositions": positionFilter})
        elif tatMember == "Yeah":
            approvedUsersCollection.insert_one({"users": addThisUser, "type": "admin", "tatMember": "Yeah",
                                    "companiesActuallyAllowed": companiesToBeAllowed, "whichPositions": positionFilter})
    else:
        if tatMember == "Nope":
            approvedUsersCollection.insert_one({"users": addThisUser, "type": "regular", "tatMember": "Nope",
                                    "companiesActuallyAllowed": companiesToBeAllowed, "whichPositions": positionFilter})
        elif tatMember == "Yeah":
            approvedUsersCollection.insert_one({"users": addThisUser, "type": "regular", "tatMember": "Yeah",
                                    "companiesActuallyAllowed": companiesToBeAllowed, "whichPositions": positionFilter})

def deleteUserHelper(deleteThisUser):
    """Helps in deleting user from the club"""

    approvedUsersCollection.delete_many({"users": deleteThisUser})
    print(f"Deleted {deleteThisUser}")

def modifyUserHelper(modifyThisUser, hisType, hisTatMember, hisWhichPositions):
    """Helps in modifying user details in the club"""

    approvedUsersCollection.update({"users": modifyThisUser}, {"$set": {
        "type": hisType,
        "tatMember": hisTatMember,
        "whichPositions": hisWhichPositions
    }
    })