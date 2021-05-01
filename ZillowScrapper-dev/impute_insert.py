#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from pymongo import MongoClient
import numpy as np
import json
import sys


host = 'mongodb://localhost:27017/'
db = 'Zillow'
client = MongoClient("mongodb://localhost:27017/")
db = client.Zillow
col = 'Test'



def impute_HOA(state):
    myquery = {"State": state}
    cursor = db[col].find(myquery,{"_id":1, "Locality":1, "HOAFee":1, "Type":1})
    df = pd.DataFrame(list(cursor))
    # print(df)
    print(df.head())
    df['HOAFee'] = df['HOAFee'].replace('', 0)
    df['HOAFee'] = df['HOAFee'].replace('None', 0)
    df['HOAFee'] = df['HOAFee'].replace('No Data', np.nan)
    df['HOAFee'] = df['HOAFee'].replace('Yes', np.nan)
    df['HOAFee'] = pd.to_numeric(df['HOAFee'])

    df_s = df[df['Type'] == 'Single Family']
    df_s.HOAFee = df_s.groupby(['Locality','Type'])['HOAFee'].apply(lambda x: x.fillna(0))
    print(df_s.head())

    df_other = df[df['Type'] != 'Single Family']
    print(df_other.groupby(['Locality','Type'])['HOAFee'].mean().round())
    df_other.HOAFee = df_other.groupby(['Locality','Type'])['HOAFee'].apply(lambda x: x.fillna(x.mean())).round()

    result = pd.concat([df_s, df_other])

    # Update data into DB
    for index, row in result.iterrows():
        # access data using column names
        print(row['_id'], row['HOAFee'])
        db["Test"].update_one({"_id": row["_id"]}, {"$set": {"HOAFee": row['HOAFee']}})


def move_to_House(state):
    myquery = {"State": state}
    db['House'].delete_many(myquery)
    data = list(db['Test'].find(myquery))
    db['House'].insert_many(data)
    print('Insert to House.')


State = sys.argv[1]    # Change the State to what you need to impute HOAFee
impute_HOA(State)
move_to_House(State)

# Remove the zipcodes of the state from visited_zip.json
with open('visited_zip.json') as data_file:
    data = dict(json.load(data_file))
    if State in data:
        data.pop(State)

with open('visited_zip.json', 'w') as data_file:
    data = json.dump(data, data_file)