import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["local"]
mycol = mydb["ApprovedUsers"]

myquery = { "users": "pankajkum@directi.com" }
newvalues = { "$set": { "whichPositions": "all" } }

mycol.update_one(myquery, newvalues)

#print "customers" after the update:
for x in mycol.find():
    print(x)
