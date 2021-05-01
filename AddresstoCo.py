#!/usr/bin/env python
# -*- coding: utf-8 -*-

from geopy.geocoders import Nominatim
from pymongo import MongoClient
client = MongoClient("mongodb://129.174.126.176:27018/")
db = client.Zillow
collection = db.SchoolRating

geolocator = Nominatim(user_agent="a")

from geopy.extra.rate_limiter import RateLimiter
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

mydoc = collection.find({'location':{'$exists': False}}, no_cursor_timeout=True)

for x in mydoc:
    if x['Address'] is not None:
        print(x['Address'], x['City'], x['State'])
        if x['Address'] is None or x['City']is None or x['State'] is None:
            continue
        add = x['Address'] + ', ' +x['City']+', '+x['State']
        loca = geocode(add)
        print(x['Address'] + ', ' +x['City']+', '+x['State'])
        print(loca)
        if loca is not None:
            collection.update_one({"_id": x["_id"]}, {"$set" : {"location": {"type": "Point",
                                                                         "coordinates": [loca.longitude, loca.latitude]}}})
        else: collection.update_one({"_id": x["_id"]}, {"$set" : {"location": loca}})
mydoc.close()