#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 @Time    : 2020-08-14 23:39
 @Author  : Yilei
 @Site    : 
 @File    : download_data.py
 @Software: PyCharm
'''

import pandas as pd
from pymongo import MongoClient
import sys

client = MongoClient("mongodb://129.174.126.176:27018/")
db = client.Zillow

doc = db.House.find({})
df = pd.DataFrame(list(doc))

sys.setrecursionlimit(15000)
path = '/home/testapiuser/HouseApp_2/backup_House.csv'
df.to_csv(path, index = None, header=True)

doc_h = db.History.find({})
df_h = pd.DataFrame(list(doc_h))

sys.setrecursionlimit(15000)
path_h = '/home/testapiuser/HouseApp_2/backup_History.csv'
df_h.to_csv(path_h, index = None, header=True)

doc_t = db.Test.find({})
df_t = pd.DataFrame(list(doc_t))

sys.setrecursionlimit(15000)
path_t = '/home/testapiuser/HouseApp_2/backup_Test.csv'
df_t.to_csv(path_t, index = None, header=True)