#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

from pymongo import MongoClient

import numpy as np
from sklearn.metrics import r2_score
from sklearn.model_selection import ShuffleSplit
import seaborn as sns

from sklearn.ensemble import RandomForestRegressor

from scipy import stats
from sklearn.cluster import KMeans

import xgboost

from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt

from sklearn.ensemble import GradientBoostingRegressor
import re


# In[2]:


# In[4]:


def change_Parking(x):
    if re.search("Garage", x):
        x = 1
    elif re.search("\d", x):
        x = int(re.sub("\D", "", x))
    else:
        x = 0
    return x


# In[5]:


def convert_cha(x):
    if x is None or isNaN(x) or x == "":
        x = 0
    return x


# In[6]:


def correct_Bath(x):
    if x >= 100:
        x = x / 100
    elif x > 10:
        x = x / 10
    return x


# In[7]:


def process_value(df):
    df['Parking'] = df['Parking'].apply(change_Parking)
    df['Bathrooms'] = df['Bathrooms'].apply(convert_cha)
    df['Bedrooms'] = df['Bedrooms'].apply(convert_cha)
    df['AreaSpace_SQFT'] = df['AreaSpace_SQFT'].apply(convert_cha)
    df['Bathrooms'] = df.Bathrooms.astype(float)
    df['Bathrooms'] = df['Bathrooms'].apply(correct_Bath)
    # df['ZipCode'] = df.ZipCode.astype(int)
    return df


# In[8]:


def drop_columns(df):
    df = df[['AreaSpace_SQFT', 'Bedrooms', 'Bathrooms', 'Parking', 'ZipCode', 'Rent']]
    return df


# In[9]:


def drop_zero(df):
    df = df[(df[['AreaSpace_SQFT', 'Bedrooms', 'Bathrooms', 'ZipCode', 'Rent']] != 0).all(axis=1)]
    return df


# In[10]:


def set_Xy(df):
    # Converting df1 dataframe into numpyarray
    df1 = df.values
    # checking for outlinears
    X = df1[:, 0:5]
    y = df1[:, 5]

    return X, y


def isNaN(num):
    return num != num


# In[11]:


# In[12]:


# Import 'r2_score'


def performance_metric(y_true, y_predict):
    """ Calculates and returns the performance score between
        true (y_true) and predicted (y_predict) values based on the metric chosen. """

    score = r2_score(y_true, y_predict)

    # Return the score
    return score


# In[13]:


from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV


def fit_model(X, y):
    """ Performs grid search over the 'max_depth' parameter for a
        decision tree regressor trained on the input data [X, y]. """

    # Create cross-validation sets from the training data
    cv_sets = ShuffleSplit(n_splits=10, test_size=0.20, random_state=0)

    # Create a decision tree regressor object
    regressor = RandomForestRegressor(n_estimators=100)

    # Create a dictionary for the parameter 'max_depth' with a range from 1 to 10
    params = {'max_depth': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

    # Transform 'performance_metric' into a scoring function using 'make_scorer'
    scoring_fnc = make_scorer(performance_metric)

    # Create the grid search cv object --> GridSearchCV()
    grid = GridSearchCV(estimator=regressor, param_grid=params, scoring=scoring_fnc, cv=cv_sets)

    # Fit the grid search object to the data to compute the optimal model
    grid = grid.fit(X, y)

    # Return the optimal model after fitting the data
    return grid.best_estimator_


# In[14]:


from sklearn.ensemble import VotingRegressor


def fit_voteReg(X_train, y_train, X_test, y_test):
    reg1 = GradientBoostingRegressor(alpha=0.9, criterion='friedman_mse', init=None,
                                     learning_rate=0.11030827845994358, loss='ls',
                                     max_depth=9, max_features=1, max_leaf_nodes=None,
                                     min_impurity_decrease=0.0, min_impurity_split=None,
                                     min_samples_leaf=1, min_samples_split=2,
                                     min_weight_fraction_leaf=0.0, n_estimators=394,
                                     n_iter_no_change=None, presort='auto',
                                     random_state=101, subsample=1.0, tol=0.0001,
                                     validation_fraction=0.1, verbose=0, warm_start=False)
    reg1.fit(X_train, y_train)
    reg2 = fit_model(X_train, y_train)
    reg2.fit(X_train, y_train)
    reg3 = xgboost.XGBRegressor(objective='reg:squarederror', learning_rate=0.07, n_estimators=100, max_depth=5,
                                min_child_weight=1, gamma=0, subsample=0.8, colsample_bytree=0.8, nthread=10,
                                scale_pos_weight=1, seed=27)
    reg3.fit(X_train, y_train)
    ereg = VotingRegressor(estimators=[('gb', reg1), ('xg', reg3)])
    ereg = ereg.fit(X_train, y_train)

    # predict values from voting method compare it to y_test
    vote_pred = ereg.predict(X_test)

    # mse in $
    mse = mean_absolute_error(y_test, vote_pred)
    print("The mean absolute error is:$", mse)
    # chceking r^2
    print("r_Score:", r2_score(y_test, vote_pred))

    print('Voting Regressor (in):', ereg.score(X_train, y_train))
    print('Voting Regressor:', ereg.score(X_test, y_test))

    return ereg


def call_rentPred(Area, Bed, Bath, Zipcode):
    if Area is not None and Bed is not None and Bath is not None and Zipcode is not None:
        no_cluster = km.predict([[Area]])
        A = [Area, Bed, Bath, Zipcode, no_cluster]
        dfa = pd.DataFrame([A])
        # p=random_forest.predict(dfa.values)
        p = model.predict(dfa.values)
        result = np.array(p)[0]
        return result


# In[101]:


host = 'mongodb://129.174.126.176:27018/'
db = 'Zillow'
client = MongoClient("mongodb://129.174.126.176:27018/")
db = client.Zillow
colZip = 'zipcodes'
col = 'House'

import datetime

now = datetime.datetime.now()
print("Current date and time: " + now.strftime("%Y-%m-%d %H:%M:%S"))

print('Successfully connect to DB.')

# Regions from: https://arizona.reaproject.org/

Region1 = [
    "La Paz",
    "Mohave",
    "Yuma"
]

Region2 = ["Maricopa"]

Region3 = [
    "Apache",
    "Coconino",
    "Navajo",
    "Yavapai"
]

Region4 = ["Gila", "Pinal"]

Region5 = ['Pima']

Region6 = ["Graham", "Cochise", "Cochise", "Greenlee"]

Region = [Region1, Region2, Region3, Region4, Region5, Region6]

for i in Region:
    print('For ' + str(i) + '#################################################################')
    R1_Zip = db[colZip].distinct("zip", {'state_id': 'AZ', "county_name": {"$in": i}})
    R1_Zip = [str(int(i)).zfill(5) for i in R1_Zip]
    # print(R1_Zip)

    myquery = {"ZipCode": {"$in": R1_Zip}, "Status": {"$regex": "rent"}}
    cursor = db[col].find(myquery)
    df = pd.DataFrame(list(cursor))
    df["Bathrooms"] = pd.to_numeric(df.Bathrooms, errors='coerce')
    df["Bathrooms"] = df["Bathrooms"].apply(correct_Bath)
    df["Bedrooms"] = pd.to_numeric(df.Bedrooms, errors='coerce')
    del df['_id']
    df = df.replace('--', 0)
    df = drop_columns(df)
    df1 = process_value(df)
    df1 = drop_zero(df1)
    # print(df1.count())

    # In[102]:

    df1.dropna()
    df2 = df1
    df2['AreaSpace_SQFT'] = df2['AreaSpace_SQFT'].astype(int)

    df2 = df1

    sns.boxplot(df2['AreaSpace_SQFT'])
    sns.boxplot(df2['Rent'])

    z = np.abs(stats.zscore(df2['Rent']))
    threshold = 7
    # print(np.where(z > 7))
    z1 = df2.Rent[(z < 7)]
    sns.boxplot(z1)
    df2['Rent'] = z1

    za = np.abs(stats.zscore(df2['AreaSpace_SQFT']))
    threshold = 7
    # print(np.where(za > 6))
    z2 = df2.AreaSpace_SQFT[(za < 6)]
    sns.boxplot(z2)
    df2['AreaSpace_SQFT'] = z2
    # print(df2.head())

    df2 = df2.dropna()

    df2 = df2.astype(int)

    plt.scatter(df2['AreaSpace_SQFT'], df2['Rent'])

    km = KMeans(n_clusters=3)
    # k_pred=km.fit_predict(df2[['Rent','AreaSpace_SQFT']])
    k_pred = km.fit_predict(df2[['AreaSpace_SQFT']])
    k_pred

    df2['cluster'] = k_pred

    d1 = df2[df2.cluster == 0]
    d2 = df2[df2.cluster == 1]
    d3 = df2[df2.cluster == 2]

    plt.scatter(d1.AreaSpace_SQFT, d1['AreaSpace_SQFT'], color='green')
    plt.scatter(d2.AreaSpace_SQFT, d2['AreaSpace_SQFT'], color='red')
    plt.scatter(d3.AreaSpace_SQFT, d3['AreaSpace_SQFT'], color='blue')

    # df2=df2.astype(int)

    df2 = df2[['AreaSpace_SQFT', 'Bedrooms', 'Bathrooms', 'ZipCode', 'cluster', 'Rent']]
    # print(df2.head())
    df3 = df2.values

    X = df3[:, 0:5]
    y = df3[:, 5]

    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42, shuffle=True)
    X_train

    # In[103]:

    random_forest = RandomForestRegressor(n_estimators=100)
    random_forest.fit(X_train, y_train)
    rand_pred = random_forest.predict(X_test)
    print('train score for random_forest:', random_forest.score(X_train, y_train))
    print('test score for random_forest:', random_forest.score(X_test, y_test))

    y_pred = random_forest.predict(X_test)

    model = fit_voteReg(X_train, y_train, X_test, y_test)

    # In[105]:

    myquery3 = {"ZipCode": {"$in": R1_Zip}, "Status": {"$regex": "sale"}}
    mydoc = db[col].find(myquery3)

    for x in mydoc:
        if x['AreaSpace_SQFT'] is None or x['AreaSpace_SQFT'] == "":
            x['AreaSpace_SQFT'] = 0
        if x['Bedrooms'] is None or x['Bedrooms'] == "":
            x['Bedrooms'] = 0
        if x['Bathrooms'] is None or isNaN(x['Bathrooms']) or x['Bathrooms'] == "":
            x['Bathrooms'] = 0
        x['Bathrooms'] = correct_Bath(float(x['Bathrooms']))
        # if not all([x['AreaSpace_SQFT'], x['Bedrooms'], x['Bathrooms'],  x['ZipCode']]):
        print(x['_id'])
        p = call_rentPred(x['AreaSpace_SQFT'], x['Bedrooms'], x['Bathrooms'], x['ZipCode'])
        # print(x['_id'])
        print("p: ", p)
        db[col].update_one({"_id": x["_id"]}, {"$set": {"PredictionRent": p}})