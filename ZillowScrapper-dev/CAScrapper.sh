#! /bin/bash 

# python3 /home/testapiuser/HouseApp_2/ZillowScrapper-dev/main.py "CA"
python3 /home/testapiuser/HouseApp_2/ZillowScrapper-dev/impute_insert.py "CA"
python3.6 /home/testapiuser/HouseApp_2/PricePrediction/CAPrice.py >> /home/testapiuser/HouseApp_2/PricePrediction/log/CAPrice.py.log 2>&1
python3.6 /home/testapiuser/HouseApp_2/PricePrediction/CARent.py >> /home/testapiuser/HouseApp_2/PricePrediction/log/CARent.py.log 2>&1
python3 /home/testapiuser/HouseApp_2/ZillowScrapper-dev/InsertDB.py "CA"
