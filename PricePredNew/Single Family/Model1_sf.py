# Importing all the library files required for sale prediction
import pandas as pd
import datetime
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import LinearRegression,Ridge, Lasso
import numpy as np
import re
import warnings
import sys
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing  import LabelEncoder
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
warnings.filterwarnings('ignore')
from sklearn.pipeline import Pipeline
from pymongo import MongoClient



#lot conversion function to create lot feature
def convert_lot(x):
  if 'acres' in x:
    x = re.findall('\d+', x)
    res = int("".join(map(str, x)))
    res = (res * 43560)/(10**(len(str(res))))
  else:
    x = re.findall('\d+', x)
    res = int("".join(map(str, x)))
  return res

#function to handle missing data
def convert_to_nan(x):
    if x == 'No Data' or x == 'None' or x == 0 or x == '':
        x = np.nan
    return x

#label encoding of parking feature
def convert_parking(x):
  for i in x.split():
    if i.isdigit():
      x = str(i)
  if 'Attached' in x:
    x = 'Attached'
  if 'On street' in x:
    x = 'On street'
  if 'Off street' in x:
    x = 'Off street'
  if 'carport' in x:
    x = 'carport'
  if 'Detached' in x:
    x = 'Detached'
  if 'No' in x:
    x = np.nan
  return x

#label encoding of heating feature
def convert_heating(x):
  if 'Baseboard' in x:
    x = 'Baseboard'
  if 'Forced' in x:
    x = 'Forced'
  if 'Electric' in x:
    x = 'Electric'
  if 'Heat Pump' in x:
    x = 'Gas'
  if 'Other' in x:
    x = 'Other'
  if 'Stove' in x:
    x = 'Stove'
  if ('No' in x) or ('Contact' in x):
    x = np.nan
  return x

#label encoding of cooling feature
def convert_cooling(x):
  if 'Central' in x:
    x = 'Central'
  if 'Other' in x:
    x = 'Other'
  if 'Evaporative' in x:
    x = 'Evaporative'
  if ('No' in x) or ('Contact' in x):
    x = np.nan
  return x

#combining all the data pre processing functions and preparing the dataset for single family/townhouse types
def dataset_preprocessing(dataset):
  dataset = dataset[['Heating','Cooling','Parking','AreaSpace_SQFT','Bathrooms','Bedrooms','Price','Lot','YearBuilt','Price_PerSQFT']]
  dataset['Bathrooms'] = dataset['Bathrooms'].apply(convert_to_nan)
  dataset['Bedrooms'] = dataset['Bedrooms'].apply(convert_to_nan)
  dataset['Lot'] = dataset['Lot'].apply(convert_to_nan)
  dataset['Price_PerSQFT'] = dataset['Price_PerSQFT'].apply(convert_to_nan)
  dataset['YearBuilt'] = dataset['YearBuilt'].apply(convert_to_nan)
  dataset['Heating'] = dataset['Heating'].apply(convert_heating)
  dataset['Cooling'] = dataset['Cooling'].apply(convert_cooling)
  dataset['Parking'] = dataset['Parking'].apply(convert_parking)
  dataset['AreaSpace_SQFT'] = dataset['AreaSpace_SQFT'].apply(convert_to_nan)
  dataset= dataset.dropna()
  dataset = dataset.reset_index(drop = True)
  le = LabelEncoder()
  dataset['Parking'] = le.fit_transform(dataset.Parking.astype(str))
  dataset.Parking = dataset.Parking.astype(int)
  dataset['Cooling'] = le.fit_transform(dataset.Cooling.astype(str))
  dataset.Cooling = dataset.Cooling.astype(int)
  dataset['Heating'] = le.fit_transform(dataset.Heating.astype(str))
  dataset.Heating = dataset.Heating.astype(int)
  dataset.Bathrooms = dataset.Bathrooms.astype(float)
  dataset.Bedrooms = dataset.Bedrooms.astype(float)
  dataset.AreaSpace_SQFT = dataset.AreaSpace_SQFT.astype(float)
  dataset.Price_PerSQFT = dataset.Price_PerSQFT.astype(int)
  dataset.Lot = dataset.Lot.astype(str)
  dataset.Lot = dataset.Lot.apply(convert_lot)
  dataset.YearBuilt = dataset.YearBuilt.astype(int)
  return dataset

def dataset_pred(dataset):
  dataset = dataset[['zid','Heating','Cooling','Parking','AreaSpace_SQFT','Bathrooms','Bedrooms','Lot','YearBuilt','Price_PerSQFT']]
  dataset['Bathrooms'] = dataset['Bathrooms'].apply(convert_to_nan)
  dataset['Bedrooms'] = dataset['Bedrooms'].apply(convert_to_nan)
  dataset['Lot'] = dataset['Lot'].apply(convert_to_nan)
  dataset['Price_PerSQFT'] = dataset['Price_PerSQFT'].apply(convert_to_nan)
  dataset['YearBuilt'] = dataset['YearBuilt'].apply(convert_to_nan)
  dataset['Heating'] = dataset['Heating'].apply(convert_heating)
  dataset['Cooling'] = dataset['Cooling'].apply(convert_cooling)
  dataset['Parking'] = dataset['Parking'].apply(convert_parking)
  dataset['AreaSpace_SQFT'] = dataset['AreaSpace_SQFT'].apply(convert_to_nan)
  dataset= dataset.dropna()
  dataset = dataset.reset_index(drop = True)
  le = LabelEncoder()
  dataset['Parking'] = le.fit_transform(dataset.Parking.astype(str))
  dataset.Parking = dataset.Parking.astype(int)
  dataset['Cooling'] = le.fit_transform(dataset.Cooling.astype(str))
  dataset.Cooling = dataset.Cooling.astype(int)
  dataset['Heating'] = le.fit_transform(dataset.Heating.astype(str))
  dataset.Heating = dataset.Heating.astype(int)
  dataset.Bathrooms = dataset.Bathrooms.astype(float)
  dataset.Bedrooms = dataset.Bedrooms.astype(float)
  dataset.AreaSpace_SQFT = dataset.AreaSpace_SQFT.astype(float)
  dataset.Price_PerSQFT = dataset.Price_PerSQFT.astype(int)
  dataset.Lot = dataset.Lot.astype(str)
  dataset.Lot = dataset.Lot.apply(convert_lot)
  dataset.YearBuilt = dataset.YearBuilt.astype(int)
  return dataset

#test train splitting of dataset
def create_train_test(dataset):
  X = dataset
  Y = dataset.Price
  X = X.drop(['Price'], axis = 1)
  X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
  return X_train, X_test, Y_train, Y_test

#predicting the sale price on test data
def find_estimate(X_train, Y_train):
  models = Pipeline([('regressor', KernelRidge())])
  param_space = [{'regressor': [KernelRidge(kernel = 'polynomial')],
                  'regressor__alpha': [0.1, 0.5, 0.9],
                  'regressor__degree': [1, 1.5, 2, 2.5, 3],
                  'regressor__coef0' : [0.5, 1, 1.5, 2, 2.5]},
                 {'regressor': [GradientBoostingRegressor(loss = 'huber', criterion = 'friedman_mse', max_features = 'sqrt')],
                  'regressor__max_depth' : [2,4,6],
                  'regressor__alpha':[0.1,0.5,0.9]},
                 {'regressor': [Lasso()]},
                 {'regressor': [Ridge()]},
                 {'regressor': [LinearRegression()]} 
                ]
  grid = GridSearchCV(models, param_space)
  best_model_setting = grid.fit(X_train,Y_train)
  return best_model_setting


def sf_job():
    host = 'mongodb://localhost:27017/'
    db = 'Zillow'
    client = MongoClient('mongodb://localhost:27017/')
    db = client.Zillow
    col = 'House'
    counter = 0

    now = datetime.datetime.now()
    print("Current date and time: " + now.strftime("%Y-%m-%d %H:%M:%S"))

    print('Successfully connect to DB.')

    myquery_price = {"Type": {"$regex": "^Single", "$options": "i" }}
    cursor_price = db[col].find(myquery_price)
    data_DB_price = pd.DataFrame(list(cursor_price))

    data_grouped_zip = data_DB_price.groupby('ZipCode')
    for zipcode, zgroup in data_grouped_zip:
      if zgroup.Address.count() > 5 and zgroup.State.iloc[0] == "CA":
        try:
          data_price = dataset_preprocessing(zgroup)
          X_train, X_test, Y_train, Y_test = create_train_test(data_price)
          best_model_setting = find_estimate(X_train, Y_train)
          myquery_pred = {"ZipCode": {"$regex": zipcode}, "Type": {"$regex": "^Single", "$options": "i" }}
          cursor_pred = db[col].find(myquery_pred)
          data_pred = pd.DataFrame(list(cursor_pred))
          data_pred = dataset_pred(data_pred)
          pred_data_id = data_pred['zid'].astype(int)
          pred_data = data_pred.drop(['zid'], axis = 1)
          X_data = pred_data
          if best_model_setting.score(X_test, Y_test) >= 0.60:
            print("Predictions made so far: ", counter)
            print("ZipCode: ",zipcode)
            print('train score for the model:', best_model_setting.score(X_train, Y_train))
            print('test score for the model:', best_model_setting.score(X_test, Y_test))
            print("Total Predictions Done: ", pred_data_id.count())
            Y_pred = best_model_setting.predict(X_data)
            for zid, pred_value in zip(pred_data_id,Y_pred):
                  db[col].update_one({"zid": str(zid)}, {"$set": {"PredictionPrice": pred_value}}) 
                  counter = counter + 1
                  pred_value=0
        except:
          print("Unexpected error:", sys.exc_info())
          continue     
sf_job()
