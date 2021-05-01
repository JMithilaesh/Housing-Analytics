from datetime import datetime
import math
from pymongo import MongoClient
import requests
import urllib.parse

db = MongoClient("mongodb://localhost:27017/").Zillow
collectionLocalityRent = db['LocalityRent']
collectionHouse = db.House

timestamp = datetime.today().strftime('%Y-%m-%d')


def Average(lst):
    return sum(lst) / len(lst)


# https://code.activestate.com/recipes/577305-python-dictionary-of-us-states-and-territories/
state_code = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MP': 'Northern Mariana Islands',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NA': 'National',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VI': 'Virgin Islands',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}

state_list = []
cursor = collectionHouse.distinct('State')
# str_temp = ''
for x in cursor:
    # print(x)
    # str_temp+=("'"+x+"'"+',')
    state_list.append(x)
# print(str_temp)

for state in state_list:
    cursor = collectionHouse.distinct(
        'Locality', {'State': state, 'Status': {"$regex": 'rent'}})
    count = 0
    locality_list = []
    for data in cursor:
        # print(data)
        locality_list.append(data)
        # count+=1
    # print(count)

    for locality in locality_list:
        cursor = collectionHouse.find(
            {'Locality': locality, 'Status': {"$regex": 'rent'}})
        temp_rent, temp_price = [], []
        for data in cursor:
            if(("PredictionPrice") in data and ('Rent' in data)):
                if(data['PredictionPrice'] != 0 and data['Rent'] != 0):
                    temp_rent.append(data['Rent'])
                    temp_price.append(data['PredictionPrice'])
                    # print(data['Rent'])
                    # print(data['PredictionPrice'])
        #   Have to have atleast 5 values for each locality
        if (len(temp_rent) > 5 and len(temp_price) > 5):
            avg_rent = Average(temp_rent)
            avg_price = Average(temp_price)
            avg_rent_to_price = avg_rent/avg_price
            # print(avg_rent_to_price)
            if state in state_code:
                address = locality+' '+state_code[state]+' United States'
                url = 'https://nominatim.openstreetmap.org/search/' +urllib.parse.quote(address) + '?format=json'
                response = requests.get(url).json()
                # print(url)
                # print(response[0]["lat"])
                # print(response[0]["lon"])
                location = {"type": "Point", "coordinates": [
                    response[0]["lat"], response[0]["lon"]]}

                print(state, locality, avg_rent_to_price, location, timestamp)
                collectionLocalityRent.update_one({'State':state,'Locality':locality}, {"$set":{'State':state,'Locality':locality,'AverageRP':avg_rent_to_price,'Location':location,'TimeStamp':timestamp}},upsert=True)
