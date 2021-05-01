import math
import traceback
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from db import mongo
import re
import json
import os
import time
import sys
from csv_utils import write_to_csv, get_unvisited_zip, write_visited_zip_code, remove_zip_code, write_to_json
import multiprocessing

from pyvirtualdisplay import Display
from datetime import datetime

# use "pkill chrome" if chrome takes up CPU and start again", due to incorrect program execution of code before 2021
##Comment this line if running on local machine##
display = Display(visible=0, size=(1366, 768))
display.start()
#####################################################

# proxyKey = 'XZApcdn3rvxztE9KQeuJgLyomYw7V5DT'
proxyKey = "B7fx3zoM6qTUtchpQH8PFSAXuwG2DRVe"
logger = logging.getLogger("Zillow Logger:")

timestamp = datetime.today().strftime('%Y-%m-%d')

# zid_file = open('run_data.txt', 'a')


def returnString(data):
    if data is None:
        return ""
    else:
        return data.get_text().strip()
        # return data.text.strip()

def string_to_int(string):
    result = re.sub('[^0-9]', '', string)
    try:
        result = int(result)
    except ValueError as e:
        print(e)
    return result

def returnInteger(data):
    string = returnString(data)
    if string == "":
        return ""
    else:
        return string_to_int(string)

def return_number(data):
    if data is None:
        return ""
    else:
        return re.sub('[^0-9]', '', returnString(data))

# Scraper code start
class App:

    def __init__(self, state):
        self.proxyDict = {}
        self.req_headers = self.setHeaders()
        self.handle_fetch_cards_exception()
        self.driver = self.setSeleniumDriver()
        self.mongo_client = mongo()

        # Get first zipcode within a particular state code
        zipcode = self.get_zip_codes(state)[0]
        while zipcode is not None:
            self.current_zipcode = str(zipcode)
            self.current_state = state
            write_visited_zip_code(state, zipcode)
            try:
                self.find_articles_by_zip(str(zipcode), "for_sale")
                self.find_articles_by_zip(str(zipcode), "for_rent")
            except KeyboardInterrupt:
                # Remove the zipcode from visited
                print("KeyBoardInterupt. Removing zipcode..")
                remove_zip_code(state, zipcode)
                return
            except Exception as e:
                # In case of any other exception remove the zipcode and then throw the exception again
                print("caught in top level exception handler")
                remove_zip_code(state, zipcode)
                print(traceback.format_exc())
                # self.driver.close()
                time.sleep(4)
                raise e
            # get next zipcode for that particular state
            zipcode = self.get_zip_codes(state)[0]
        self.driver.close()

    def get_zip_codes(self, state):
        zipcodes = get_unvisited_zip(state)
        return zipcodes

    def check_recaptcha(self, soup):
        captcha = soup.find("div", {"class": "g-recaptcha"})
        if captcha is None:
            return False
        else:
            print("Bot detected..")
            return True

    def rotate_ip(self):
        success = False
        proxyRotatorUrl = "http://falcon.proxyrotator.com:51337/?apiKey=" + proxyKey + "&get=true"
        while not success:
            try:
                json_response = requests.get(proxyRotatorUrl).json()
                success = True
            except Exception as e:
                print("Exception while fetching proxy url" + str(e) + "retrying...")
        proxy = json_response["proxy"]
        print("Rotating IP...new proxy=" + proxy)
        return proxy

    def setHeaders(self):
        return {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.8',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        }

    def setSeleniumDriver(self):
        proxy = self.rotate_ip()
        options = webdriver.ChromeOptions()
        # options.addExtensions(new File("C:\\whatever\\Block-image_v1.0.crx"))
        options.add_argument('--proxy-server=%s' % proxy)
        options.add_argument(
            "accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--incognito")
        options.add_argument("--window-size=1366, 768")
        options.add_argument('--no-sandbox')



        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2})  # 'disk-cache-size': 4096
        # TODO zipcode and above optimization and that error in bottom

        # Change the executable path to chrome before running. Also make sure it matches the chrome version installed on the OS
        # driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver",options=options)
        driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
        # /usr/local/bin/chromedriver
        driver.set_page_load_timeout(150)
        return driver

    def scrapeForSale(self, soup2, returndata, script_str):
        # print("*** Entered For Sale Function***")
        # returndata["Price"] = returnInteger(soup2.find("span", {"class": "ds-value"}))

        returndata["Status"] = returnString(soup2.find("span", {"class": "ds-status-details"}))

        # Changes made: feb 9, Charan Bandi, price needed to get only if for sale status and from a h4 banner in summary
        # returndata["Price"] = string_to_int((soup2.find("div",  {"class": "ds-summary-row"})).find("h4").text)
        # Change Made: March 5 2021, Charan Bandi, Price was readjust so spliiting strings to get values now
        # returndata["Price"] = string_to_int((soup2.find("div",  {"class": "ds-summary-row"}).text).split()[0])
        # Change Made: March 17 2021, Charan Bandi, Price was changed to multiple divs and hence matching it
        for x in (soup2.find("div",  {"class": "ds-summary-row"})):
            returndata["Price"] = string_to_int(x.text)
            break
        if "Price" not in returndata:
            return

        try:
            returndata["Description"] = returnString(
                soup2.find("div", {"class": "ds-overview-section"}).find("div", recursive=False))
        except Exception as e:
            print("unable to fetch overview")
            logger.error(repr(e))
            pass

        # Changes made: feb 5, Charan Bandi, passing a previous script and getting details from there

        soup3 = BeautifulSoup(script_str, "html.parser")
        returndata["Address"] = str(json.loads("".join(soup3.find("script", {"type":"application/ld+json"}).contents))['name'])
        returndata["ZipCode"] = str(json.loads("".join(soup3.find("script", {"type":"application/ld+json"}).contents))['address']['postalCode'])
        returndata["State"] = str(json.loads("".join(soup3.find("script", {"type":"application/ld+json"}).contents))['address']['addressRegion'])
        returndata["Locality"] = str(json.loads("".join(soup3.find("script", {"type":"application/ld+json"}).contents))['address']['addressLocality'])

        # Change made: Charan Bandi Apr 5, conversion from div to spans
        # finding all spans which gives bed bath and area
        bed_bath_area = soup2.find("span", {"class": "ds-bed-bath-living-area-container"})

        for x in bed_bath_area:
            if (x.text != ""):
                if 'bd' in (x.text):
                    returndata["Bedrooms"] = string_to_int(x.text)
                elif 'ba' in (x.text):
                    returndata["Bathrooms"] = string_to_int(x.text)
                elif 'sqft' in (x.text):
                    returndata["AreaSpace_SQFT"] = string_to_int(x.text)
        try:
            while float(returndata["Bathrooms"]) > 10:
                returndata["Bathrooms"] = float(returndata["Bathrooms"]) / 10
        except Exception as e:
            print("Can't convert bath", returndata["zid"])
            logger.error(repr(e))
            pass



        try:
            scores = soup2.findAll("a", {"class": "ws-value"})
            returndata["WalkScore"] = returnInteger(scores[0])
            returndata["TransitScore"] = returnInteger(scores[1])
        except Exception as e:
            print("unable to fetch walk/trasit score")
            logger.error(repr(e))
            pass


        # Changes made: feb 8, Charan Bandi, zestimate uses a jargon div, this regex allows the first values as estimate
        try:
            # removes all commas and then gets the first integer values in the div.
            returndata["ZestimatePrice"] = re.search(r'\d+', soup2.find("div", {"id": "ds-home-values"}).text.replace(",", "")).group()
            if(returndata["ZestimatePrice"]==int(returndata["ZipCode"])):
                returndata.pop('ZestimatePrice', None)
        except Exception as e:
            print("unable to fetch ZestimatePrice")
            pass
    
        # Changes made: feb 9, Charan Bandi, fact is now using jardon value hence switched to textual extraction
        # this causes extra empty field in return data if no fact is present
        facts = soup2.find("ul", {"class": "ds-home-fact-list"}).find_all("li")
        for fact in facts:
            label, value = (fact.text).split(":")
            if '$' in value:
                returndata[label] = string_to_int(value)
            else:
                returndata[label] = value
        
        # Correct the field name
        if "Year built" in returndata:
            returndata["YearBuilt"] = returndata.pop("Year built")
        if "Type"in returndata:
            returndata["Type"] = returndata.pop("Type")
        if "Heating" in returndata:
            returndata["Heating"] = returndata.pop("Heating")
        if "Cooling" in returndata:
            returndata["Cooling"] = returndata.pop("Cooling")
        if "Parking" in returndata:
            returndata["Parking"] = returndata.pop("Parking")
        if "Lot" in returndata:
            returndata["Lot"] = returndata.pop("Lot")
        if "Price/sqft" in returndata:
            returndata["Price_PerSQFT"] = returndata.pop("Price/sqft")
        if "HOA" in returndata:
            returndata["HOAFee"] = returndata.pop("HOA")
        if "Date available" in returndata:
            returndata["Date_available"] = returndata.pop("Date available")
        if "Pets" in returndata:
            returndata["Pets"] = returndata.pop("Pets")
        if "Laundry:" in returndata:
            returndata["Laundry"] = returndata.pop("Laundry")
        if "Deposit & fees" in returndata:
            returndata["Deposit_fees"] = returndata.pop("Deposit & fees")
        if "rent" in returndata["Status"]:
            returndata["Rent"] = returndata.pop("Price")

        # change made: Mar 7, Charan Bandi Zillow uses different layouts for price and rent, omits year and Lotsize from rental, hence we get it from further details, works as of March 7 2021 with h5
        if "YearBuilt" not in returndata:
            try:
                list_li = soup2.find("h5", string="Construction details").find_next('div').find_all('li')
                for li in list_li:
                    label, value = (li.text).split(":")
                    if label == "Year built":
                        returndata["YearBuilt"] = value.strip()
                        break
                        # print(li.text)
            except Exception as e:
                print(e)
                pass

        if "Lot" not in returndata:
            try:
                list_li = soup2.find("h5", string="Property details").find_next('div').find_all('li')
                for li in list_li:
                    label, value = (li.text).split(":")
                    if label.strip() == "Lot size":
                        returndata["Lot"] = value.strip()
                        break
            except Exception as e:
                print(e)
                pass



        # change made: Feb 10, Charan Bandi changes price history completely, structure was changed on Zillow, works as of March 5 2021
        try:
            price_history = soup2.find("h5", string="Price history").find_next('div').find_all("tr")
            historyList = []
            for tr in price_history:
                tds = tr.find_all('td')
                if(len(tds)==3):
                    hist = dict()
                    hist["date"] = (tds[0].text)
                    hist["event"] = (tds[1].text)
                    hist["price"] = (tds[2].text)
                    historyList.append(hist)
            returndata["SaleHistory"] = historyList
        except Exception as e:
            print("Sale History Error")
            returndata["SaleHistory"] = ""
            pass


        returndata["TimeStamp"]=timestamp


        # WRITING TO CSV FILE
        print(returndata)
        # zid_file.write(str(returndata["zid"])+'\n') 
        self.mongo_client.insert_article_without_upsert(returndata)
        # write_to_json(returndata)

    def scrapeArticle(self, result, type, retry=0):
        returndata = dict()
        # print("*** Entered For Scrape Article with Type"+str(type)+ " and result***")
        # print(str(result))

        # use selenium to load individual house article
        # print(str(type))
        if type == 1:
            # data is obtained from result directly
            try:
                houseurl = "https://www.zillow.com/homes/for_sale/" + result['data-zpid'] + "_zpid"
                returndata["zid"] = result['data-zpid']
            except KeyError as e:
                houseurl = "https://www.zillow.com/homes/for_sale/" + result['id'][5:] + "_zpid"
                returndata["zid"] = result['id'][5:]
            except Exception as e:
                logger.error("exception fetching card 1" + repr(e))
                return

            # Bug Fixed on Feb 5, Changes Made: Charan, Error: result. script convert to string before parse causing none type exception
            if(str(result.script) == None or str(result.script)==""):
                returndata["Latitude"] = ""
                returndata["Longitude"] = ""
            else:
                soup3 = BeautifulSoup(str(result.script), "html.parser")
                # returndata["Latitude"] = json.loads(returnString(result.script))['geo']['latitude']
                # returndata["Longitude"] = json.loads(returnString(result.script))['geo']['longitude']
                returndata["Latitude"] = (json.loads("".join(soup3.find("script", {"type":"application/ld+json"}).contents))['geo']['latitude'])
                returndata["Longitude"] = (json.loads("".join(soup3.find("script", {"type":"application/ld+json"}).contents))['geo']['longitude'])
                # print("Location data is :"+str(returndata["Latitude"])+str(returndata["Longitude"]))
            # returndata["Latitude"] = float(result["data-latitude"]) / 1000000
            # returndata["Longitude"] = float(result["data-longitude"]) / 1000000
        else:
            # else in case data is obtained from result.article
            try:
                houseurl = "https://www.zillow.com/homes/for_sale/" + result.article[
                    'data-zpid'] + "_zpid"
                returndata["zid"] = result.article['data-zpid']
            except KeyError as e:
                houseurl = "https://www.zillow.com/homes/for_sale/" + result.article['id'][
                                                                      5:] + "_zpid"
                returndata["zid"] = result.article['id'][5:]
            except Exception as e:
                logger.error("exception fetching card 2" + repr(e))
                return
                
            print("Scrape Article parse with url: " + str(houseurl))
            # print(result.script)
            # Bug Fixed on Feb 5, Changes Made: Charan, Error: result. script convert to string before parse causing none type exception
            if(str(result.script) == None or str(result.script)==""):
                returndata["Latitude"] = ""
                returndata["Longitude"] = ""
            else:
                soup3 = BeautifulSoup(str(result.script), "html.parser")
                # returndata["Latitude"] = json.loads(returnString(result.script))['geo']['latitude']
                # returndata["Longitude"] = json.loads(returnString(result.script))['geo']['longitude']
                returndata["Latitude"] = (json.loads("".join(soup3.find("script", {"type":"application/ld+json"}).contents))['geo']['latitude'])
                returndata["Longitude"] = (json.loads("".join(soup3.find("script", {"type":"application/ld+json"}).contents))['geo']['longitude'])
                # print("Location data is :"+str(returndata["Latitude"])+str(returndata["Longitude"]))
            


            

        if self.mongo_client.check_if_zid_already_exist(returndata["zid"]) is not None:
            print("zid: " + returndata["zid"] + " already exist in db")
            return

        # print(str(returndata["longitude"]) + " / " + str(returndata["latitude"]))
        returndata["location"] = {"type": "Point",
                                  "coordinates": [returndata["Longitude"], returndata["Latitude"]]}

        # print("Fetching..." + houseurl)

        try:
            self.driver.get(houseurl)
        except Exception as e:
            print(str(e) + " exception while fetching houseurl [self.driver.get()]")
            self.driver.quit()
            self.driver = self.setSeleniumDriver()
            self.scrapeArticle(result, type)
            return

        html = self.driver.page_source
        soup2 = BeautifulSoup(html, 'lxml')

        # restart scraping for same article if captcha or error deteted
        if self.check_recaptcha(soup2):
            print("Bot detected")
            self.driver.quit()
            self.driver = self.setSeleniumDriver()
            self.scrapeArticle(result, type, 0)
            return

        if soup2.find("div", {"id": "main-frame-error"}) is not None:
            print("Error window detected")
            self.driver.quit()
            self.driver = self.setSeleniumDriver()
            if retry == 0:
                self.scrapeArticle(result, type, 0)
            return

        try:
            if soup2.find("span", {"class": "ds-status-details"}) is not None:
                html = self.driver.page_source
                soup2 = BeautifulSoup(html, 'lxml')
                self.scrapeForSale(soup2, returndata, str(result.script))
        except TimeoutException as e:
            print("Timeout exception while waiting for element")

            # EXPERIMENTAL CHANGES#
            if retry == 0:
                self.scrapeArticle(result, type, 1)
            else:
                self.driver.quit()
                self.driver = self.setSeleniumDriver()
            # self.scrapeArticle(result, type)
            # EXPERIMENTAL CHANGES
            pass
        except Exception as e:
            # raise e
            print(traceback.format_exc())
            logger.error("exception " + repr(e) + " for url " + houseurl)
            pass

    def find_articles_by_state(self):
        self.find_articles_by_zip("Dallas-TX")

    def handle_fetch_cards_exception(self):
        logger.error("Setting up new proxy for fetching cards...")
        self.cards_proxy = self.rotate_ip()
        print("http://" + self.cards_proxy)
        self.proxyDict = {
            "http": "http://" + self.cards_proxy,
            "https": "http://" + self.cards_proxy
        }

    def find_articles_by_zip(self, zip, status):
        # get webpage and create soup
        with requests.Session() as s:
            url = "https://www.zillow.com/homes/" + status + "/" + str(
                zip) + "_rb/house,townhouse,condo_type/any_days/"
            # url = "https://www.zillow.com/homes/" + str(
            #     zip) + "_rb/house,townhouse,condo_type/0_rs/1_fs/1_fr/0_mmm/30_days/"
            # url = 'https://www.zillow.com/homes/recently_sold/' + str(zip) + "_rb"
            # https://www.zillow.com/homes/for_sale/20002_rb/house_type/66126_rid/1_fr/1_rs/1_fs/0_mmm/
            # url = 'https://www.zillow.com/homes/for_sale/' + str(zip) + "_rb"

            try:
                r = s.get(url, proxies=self.proxyDict, timeout=20.0, headers=self.req_headers)
            except Exception as e:
                print(str(e))
                self.handle_fetch_cards_exception()
                self.find_articles_by_zip(zip, status)
                return

        # print(r.text)
        soup = BeautifulSoup(r.text, 'lxml')
        if self.check_recaptcha(soup):
            self.handle_fetch_cards_exception()
            self.find_articles_by_zip(zip, status)
            return

        # Changes made Feb 10, Charan, Inconsistent Code Fix: Due to changes in rent and sale config in site, different cases to check for empty results/ and page code changes traverse until 9 only

        # print(soup.find("meta", {"name": "description"}))
        if (status == "for_rent" and soup.find("span", {"class": "result-count"}) is None):
            print("no rental results for zip " + zip)
            return

        if (status == "for_sale" and soup.find("div", {"class": "total-text"}) is None):
            print("no sale results for zip " + zip)
            return
            
        # get number of pages
        try:
            str_pages = returnString(soup.find("div", {"class", "search-pagination"}))
            list_pages = re.findall('\d+', str_pages)
            list_pages = list(map(int, list_pages)) 
            pages = 1
            for x in list_pages:
                if (x<10 and x>pages):
                    pages = x
            # print("pages is : "+ str_pages+ "max: "+str(pages))

            # pages = returnString(soup.find("li", {"class", "zsg-pagination-next"}).previous_sibling)
        except AttributeError:
            pages = 1

        # itereate over each page
        # for page in range(1, int(pages) + 1):
        page = 1
        while page < int(pages) + 1:
            print("PAGE:" + str(page))

            # make a request for that particular page and create soup for that page
            with requests.Session() as s:
                url = "https://www.zillow.com/homes/" + status + "/" + str(
                    zip) + "_rb/house,townhouse,condo_type/any_days/" + str(
                    page) + "_p"
                # url = "https://www.zillow.com/homes/" + str(
                #     zip) + "_rb/house,townhouse,condo_type/0_rs/1_fs/1_fr/0_mmm/30_days/" + str(
                #     page) + "_p"
                print(url)
                try:
                    r = s.get(url, proxies=self.proxyDict, timeout=20.0, headers=self.req_headers)
                except Exception as e:
                    print(str(e))
                    self.handle_fetch_cards_exception()
                    continue

            soup = BeautifulSoup(r.content, 'lxml')

            cards = soup.find("ul", {"class": "photo-cards"})
            if cards is None:
                if self.check_recaptcha(soup):
                    self.handle_fetch_cards_exception()
                    continue
                else:
                    page += 1
                    continue

            if cards["class"] == ["photo-cards"]:
                results = cards.find_all("article")
                card_type = 1
            else:
                results = cards.find_all("li", recursive=False)
                card_type = 0

            # find number of articles in that page and iterate over it
            for result in results:
                try:
                    self.scrapeArticle(result, card_type)
                except Exception as e:
                    # raise e
                    print(traceback.format_exc())
                    logger.error(
                        repr(
                            e) + " exception occoured while handling a zid. Moving to next zid....")
                    continue
            page += 1


def spawnProcess(state):
    App(state)


if __name__ == "__main__":
    start_time = datetime.now()

    # state = input("Enter State Code:")
    state = sys.argv[1]
    # process_count = int(input("How many process would you like to spawn in parallel:"))
    process_count = 20
    # # original process count 20, made 1 for testing on Jan 18 2021, please revert if this line is not removed 
    # process_count = 1
    # Comment below line if running on local
    # os.system('sudo killall chrome')
    # os.system('sudo killall chromedriver')
    # os.system('sudo killall xvfb')
    ########################################
    # spawnProcess(state)  # Uncomment this line if running on local

    # Comment below line if running on local
    for i in range(0, process_count):
        p1 = multiprocessing.Process(target=spawnProcess, args=(state,))
        p1.start()
        time.sleep(5)
    ########################################

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

# zillow url parameters:- /0_mmm - show only for sale items
# https://www.zillow.com/homes/for_sale/Washington-DC-20002/house,apartment_duplex_type/66126_rid/38.953802,-76.915885,38.861765,-77.039481_rect/12_zm/
# 1_fr,1_rs,11_zm
# any_days/30_days/...
