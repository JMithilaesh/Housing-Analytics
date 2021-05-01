#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

import pandas as pd
data = pd.read_csv('/home/testapiuser/HouseApp_2/src/VA_rent_2.csv')

#print(data.head(1))

Area = sys.argv[1]
Bed = sys.argv[2]
Bath = sys.argv[3]
Parking = sys.argv[4]
Zipcode = sys.argv[5]


print("First name: " + sys.argv[1]) 
print("Last name: " + sys.argv[2])
print("First name: " + sys.argv[3]) 
print("Last name: " + sys.argv[4])
print("First name: " + sys.argv[5])
