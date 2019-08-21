from flask_login import UserMixin

# from db import get_db

# Mongodb manadatory inclusions
from pymongo import MongoClient, CursorType


class User(UserMixin):
    def __init__(self, id_):
        self.id = id_

    @staticmethod
    def get(users_email):
        client = MongoClient("mongodb://localhost:27017")
        database = client["local"]
        collection2 = database["ApprovedUsers"]
        # db = get_db()
        # user = db.execute(
        #     "SELECT * FROM user WHERE id = ?", (user_id,)
        # ).fetchone()
        # if not user:
        #     return None

        print(f"\nIn get {users_email}\n")
        pa = collection2.find({'users': users_email})

        if pa:
            for p in pa:
                if p['users'] == users_email:
                    print("\nYeah, found in mongoDB\n")
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
        # if pa:
        #     print("Yeah, found in mongoDB")
        # else:
        #     return None



    # @staticmethod
    # def create(id_, name, email, profile_pic):
    #     db = get_db()
    #     db.execute(
    #         "INSERT INTO user (id, name, email, profile_pic)"
    #         " VALUES (?, ?, ?, ?)",
    #         (id_, name, email, profile_pic),
    #     )
    #     db.commit()
