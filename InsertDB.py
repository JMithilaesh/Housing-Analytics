#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 @Time    : 2020-06-29 15:55
 @Author  : Yilei
 @Site    : 
 @File    : InsertDB.py
 @Software: PyCharm
'''

import json
from datetime import date
import math
import numpy as np


from pymongo import MongoClient
client = MongoClient("mongodb://129.174.126.176:27018/")
db = client.Zillow
collection1 = db.House
collection2 = db.History


# filename = 'TX.json'
# with open(filename, 'r') as f:
#     distros_dict = json.load(f)
#
# # Insert data to current DB
# result = collection1.insert_many(distros_dict)
# print('Inserted data to Test')

# Run models on Current DB


def update_tags(zid, new_tag):
    collection2.update_one({'zid': zid}, {'$push': {'History': new_tag}})
    print('Appended update ', zid)


# Compare if the values are changed except for nan
def check_not_equal(differ_items):
    flag = False
    for x in differ_items:
        #if not math.isnan(differ_items[x]):
        if differ_items[x] == differ_items[x]:
            flag = True
    return flag


today = date.today()
d3 = today.strftime("%m/%d/%y")


# Export data as json from Current DB: data
# state = input("Enter State Code:")
cursor = collection1.find({'State': 'VA'}, {'_id': 0}, no_cursor_timeout=True)
# cursor = collection1.find({}, {'_id': 0}, no_cursor_timeout=True)

for data in cursor:
    # for each, check if zid exists in History
    exists = collection2.find_one({"zid": data['zid']})
    if exists:
        # Check if Price changed
        a = exists['History'][-1]
        a.pop('date')
        is_not_equal = a != data
        if is_not_equal:
            differ_items = {k: data[k] for k in a if k in data and a[k] != data[k]}
            # check value in differ_items
            if check_not_equal(differ_items):
                print(differ_items)
                #print(check_not_equal(differ_items))
                data['date'] = d3
                update_tags(data['zid'], data)
                #print('update', data['zid'])
    else:
        # create json {zid:{history:[{}, ...]}}
        record = dict()
        record['zid'] = data['zid']
        data['date'] = d3
        record['History'] = [data]
        #print(record)
        post_id = collection2.insert_one(record)
        print('Appended new record ', record['zid'])

cursor.close() # use this or cursor keeps waiting so ur resources are used up

