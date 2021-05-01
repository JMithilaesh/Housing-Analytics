import sys
from pathlib import Path
import os
import glob
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from bson import Code

# take a backup of db before you run this !!!!!
# https://stackoverflow.com/a/29383334
# https://stackoverflow.com/a/10627056

client = MongoClient("mongodb://localhost:27017/")
db = client.Zillow
col = 'House'

timestamp = datetime.today().strftime('%Y-%m-%d')

def check_zid_existence(zid):
    return db[col].find_one({"zid": zid})

def setupPath():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    extension = 'csv'

    os.chdir(dir_path+'/data_files/')
    result = glob.glob('*.{}'.format(extension))

    # print(result)
    return result

def processFrame(df):
    # print(df)
    # my_list = df.columns.values.tolist()
    # print(my_list)

    for index, row in df.iterrows():

        db_data = dict()

        # use get to handle key error
        mid = row.get('MLS #', default=0)
        if (mid != 0):
            mlsid = "MLS"+mid
            if(check_zid_existence("mlsid") == None):
                db_data["zid"] = mlsid

                mlsaddress = ''

                
                # address, locality, state, zipcode, type, status
                if(pd.notnull(row.get('Address'))):
                    mlsaddress+=row.get('Address')
                else:
                    continue

                if(pd.notnull(row.get('City'))):
                    mlsaddress+=', '+row.get('City')
                    db_data["Locality"] = row.get('City')
                else:
                    continue

                if(pd.notnull(row.get('State'))):
                    mlsaddress+=', '+row.get('State')
                    db_data["State"] = row.get('State')
                else:
                    continue

                if(pd.notnull(row.get('Zip Code'))):
                    mlsaddress+=' '+row.get('Zip Code')
                    db_data["ZipCode"] = row.get('Zip Code')
                else:
                    continue

                db_data['Address'] = mlsaddress

                db_data["Status"] = "For sale"


                if(pd.notnull(row.get('Property Type'))):
                    mlstype = row.get('Property Type')
                    if(mlstype=='Condominium'):
                        db_data["Type"] = "Condo"
                    elif(mlstype=='Single Family Home'):
                        db_data["Type"] = "Single Family"
                    elif(mlstype=='Townhouse'):
                        db_data["Type"] = "Townhouse"
                    else:
                        continue
                else:
                    continue

                
                if(pd.notnull(row.get('Beds'))):
                    db_data["Bedrooms"] = int(row.get('Beds'))
                else:
                    continue


                mlsbath = 0
                if(pd.notnull(row.get('Half Baths'))):
                    mlsbath+=int(row.get('Half Baths'))
                if(pd.notnull(row.get('1/4 Baths'))):
                    mlsbath+=int(row.get('1/4 Baths'))
                if(pd.notnull(row.get('3/4 Baths'))):
                    mlsbath+=int(row.get('3/4 Baths'))

                if(mlsbath!=0):
                    db_data["Bathrooms"] = int(mlsbath)
                else:
                    print("Here")
                    print(db_data)
                    print("***")

                    continue
                


                







                # TimeStamp
                db_data["TimeStamp"] = timestamp

                

                # gets None if doesnt exsits
                # fake_address = row.get('address5')
                # print(fake_address)

        # print(row['Address'], row['Price'])
        print(db_data)
        
        #tag:rem_func 
        if(index>10):
            return


files = setupPath()
for x in files:
    df = pd.read_csv(x)
    processFrame(df)
    # break   #tag:rem_func


# rem_func:remove after the function coding is done 