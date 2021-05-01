import json
import datetime
import math
import numpy as np
import sys
import progressbar
from time import sleep

from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client.Zillow
collection = db.House
# collectiontest = db.Test
# collectiontestbackup = db.TestBackupMar23

collectionHouse = db.House

count=0

# cursor = collectiontestbackup.find({'TimeStamp':{'$exists':False}})
# for data in cursor:
#     count+=1
#     print(data['zid'])
#     db["Test"].insert(data)
#     print(count)


# cursor = collectiontestbackup.find({'TimeStamp':'2021-02-11'})
# for data in cursor:
#     count+=1
#     print(data['zid'])
#     db["Test"].insert(data)
#     print(count)
# cursor = collectiontestbackup.find({'TimeStamp':'2021-02-18'})
# for data in cursor:
#     count+=1
#     print(data['zid'])
#     db["Test"].insert(data)
#     print(count)
# cursor = collectiontestbackup.find({'TimeStamp':'2021-03-17'})
# for data in cursor:
#     count+=1
#     print(data['zid'])
#     db["Test"].insert(data)
#     print(count)
# cursor = collectiontestbackup.find({'TimeStamp':'2021-03-21'})
# for data in cursor:
#     count+=1
#     print(data['zid'])
#     db["Test"].insert(data)
#     print(count)
# cursor = collection.find({'TimeStamp': {"$gt":'2021-03-01'}, 'TimeStamp': {"$lt":'2021-03-13'}}, {'_id': 0}, no_cursor_timeout=True)
# count=0
# print(len(cursor[0]['comments']))
# for data in cursor:
#     if("Price" in data):
#         if(data['Bedrooms'] != "" and data['Price']!=""):
#             count+=1
#     elif("Rent" in data):
#         if(data['Bedrooms'] != "" and data['Rent']!=""):
#             count+=1
#     if("Price" in data):
#         if(data['Bedrooms'] != "" and data['Price']!=""):
#             corrected = int(str(int(data['Price']))[:-1])
#             print(str(data['zid'])+ "   "+str(data['Price'])+"   "+str(corrected))
#             db["House"].update({"zid": data["zid"]}, {"$set": {"Price":corrected}} ,multi=True)
#     if("Rent" in data):
#         if(data['Bedrooms'] != "" and data['Rent']!=""):
#             corrected = int(str(int(data['Rent']))[:-1])
#             print(str(data['zid'])+ "   "+str(data['Rent'])+"   "+str(corrected))
#             db["House"].update({"zid": data["zid"]}, {"$set": {"Rent":corrected}} ,multi=True)
# print("count is :"+str(count))


# cursor = collection.find({'TimeStamp':{"$exists":True}}, {'_id': 0}, no_cursor_timeout=True)
# for data in cursor:
#     if (('ZestimatePrice') in data) and (('ZipCode') in data):
#         if (data['ZestimatePrice']==data['ZipCode']):
#             print(data["zid"])
#             # db["House"].update_one({"_id": data["_id"]}, {"$set": {"HOAFee": row['HOAFee']}})
#             db["House"].update({"zid": data["zid"]}, {"$unset": {"ZestimatePrice":1}} ,False, True);


# cursor = collection.find({'TimeStamp':{"$exists":True}}, {'_id': 0}, no_cursor_timeout=True)
# for data in cursor:
#     if (('Price') in data) and (('Rent') in data):
#         if (data['ZestimatePrice']==data['ZipCode']):
#             print(data["zid"])
#             # db["House"].update_one({"_id": data["_id"]}, {"$set": {"HOAFee": row['HOAFee']}})
#             db["House"].update({"zid": data["zid"]}, {"$unset": {"ZestimatePrice":1}} ,False, True);


# cursor = collection.find({'TimeStamp': '2021-03-14'}, {'_id': 0}, no_cursor_timeout=True).count()
# cursor = collection.find({'TimeStamp': '2021-03-14'}, {'_id': 0}, no_cursor_timeout=True)

# cursor = collection.find({'TimeStamp': {"$exists":False}}, {'_id': 0}, no_cursor_timeout=True)

# Code for adding timestamps to previous data
# print(int(collection.count({'TimeStamp': {"$exists":False}})))
# bar = progressbar.ProgressBar(maxval=int(collection.count({'TimeStamp': {"$exists":False}})), \
#     widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

# bar.start()
# # bar.finish()

#     # bar.update(count)
# id_count = []

# count=0
# for data in collectionHouse.find({'TimeStamp': {"$exists":False}}, no_cursor_timeout=True):
# #     # print(data.get('_id'))
    
#     # print(data["SaleHistory"])

#     if data["SaleHistory"] != "":
#         # count+=1
# #         print(data["zid"])
#         if(len(data["SaleHistory"])>0):
#             # count+=1
#             dt = str(data["SaleHistory"][0]["date"])
#             # print(dt)
#             # count+=1
#             if(len(dt)>=8):
#                 count+=1
#                 print(dt)
#                 # print(data["SaleHistory"][0]["date"])
#                 ts = datetime.datetime.strptime(dt, '%m/%d/%Y').strftime('%Y-%m-%d')
#                 print(ts)
#                 record = collection.find({"_id":data.get('_id')})
#                 print(record)
#                 collection.update({"_id":data.get('_id')},{"$set" : {"TimeStamp":ts}},False, True) 
#                 # if(count%100000==0):
#                 #     print(data["zid"])
# print(count)


# cursor = collection1.find({'State':'CA', 'Status': { '$regex': 'rent' },'TimeStamp':{'$exists':False}})
# count=0
# for data in cursor:
#     count+=1
#     print(data['zid'])