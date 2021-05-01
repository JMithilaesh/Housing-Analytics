from pyvirtualdisplay import Display
from datetime import datetime
import re
import json
import os
import time
import sys
import math
import traceback
from bs4 import BeautifulSoup
import requests
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys
from pathlib import Path



# print(dir_path)
# sys.exit()
def setupDriver():

    # in linux start the display before chrome start
    # https://stackoverflow.com/a/28188009
    display = Display(visible=0, size=(800, 800))  
    display.start()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    Path(dir_path+"/data_files/").mkdir(parents=True, exist_ok=True)
    dir_dat=dir_path+'/data_files/'

    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    # headless doesnt work with some websites
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument("--enable-javascript")

    # make sure to change the path of the def download when changing envs or across devices
    # prefs = {"download.default_directory": '/home/vbandi/Downloads/paragon_scraper/data_files/',"directory_upgrade": True, "download.prompt_for_download": False}
    prefs = {"download.default_directory": dir_dat,"directory_upgrade": True}
    # "profile.managed_default_content_settings.images": 2 # use this in prefs to disable images but some of the pages use image buttons so cannot use it here
    chrome_options.add_experimental_option("prefs", prefs)

    # d = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
    # d = webdriver.Chrome("/home/admin/HousingApp/HouseApp_2/paragon_scraper/chromedriver",options=chrome_options)
    d = webdriver.Chrome(dir_path+'/chromedriver',options=chrome_options)
    # d = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)

    # https://stackoverflow.com/a/51725319
    # its a feature that is implemented in chrome driver to disable download in headless mode, this is a workaround
    # d.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    # params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': "/home/vbandi/Downloads/paragon_scraper/data_files/"}}
    # d.execute("send_command", params)


    return d


def setupLoginMLS(d):
    # MLS access page 1
    d.maximize_window()
    d.get("https://pro.mlslistings.com")
    d.implicitly_wait(2)
    d.find_element_by_name(
        "ctl00$MainContent$UCLogin$unknownUserDRE").send_keys("01783775")
    d.find_element_by_name("ctl00$MainContent$UCLogin$unknownUserContinue").click()

    # MLS access page 2 with signin Image loaded
    d.implicitly_wait(2)
    d.find_element_by_name("ctl00$MainContent$UCLogin$ibtnSignIn").click()

    # MSLPRO Login Page
    d.implicitly_wait(2)
    d.find_element_by_id("logonIdentifier").send_keys("01783775")
    d.find_element_by_id("password").send_keys("Astute1234!")
    d.find_element_by_id("next").click()
    print('Log: Login Pass')

    # Navigate to products and get Paragon
    d.implicitly_wait(5)
    d.find_element_by_id("MainMenu1_MyProductsLink").click()
    d.implicitly_wait(2)
    d.find_element_by_link_text("Paragon").click()
    return d

def pass_frame_home(driver_handle, type_handle):

    # WebDriverWait(driver_handle, 60).until(EC.visibility_of_element_located((By.ID,('HomeTab'))))
    # driver_handle.implicitly_wait(10)
    frame = driver_handle.find_element_by_id('HomeTab')
    driver_handle.switch_to.frame(frame)

    listingStatus = driver_handle.find_element_by_xpath('//*[@id="f_11__1-2-3-4-5-6-7-8-9-10"]')
    listingStatus.send_keys(Keys.BACKSPACE)
    listingStatus.send_keys(Keys.BACKSPACE)
    listingStatus.send_keys("A")
    time.sleep(2)
    listingStatus.send_keys(Keys.TAB)

    propertyTypeInput = driver_handle.find_element_by_xpath('//*[@id="f_3__1-2-3-4-5-6-7-8-9-10"]')
    propertyTypeInput.send_keys(Keys.BACKSPACE)
    propertyTypeInput.send_keys(Keys.BACKSPACE)
    propertyTypeInput.send_keys(type_handle)
    time.sleep(2)
    propertyTypeInput.send_keys(Keys.TAB)

    time.sleep(5)
    driver_handle.find_element_by_xpath('//*[@id="Search"]').click()

    time.sleep(10)
    driver_handle.switch_to.default_content()

    frame = driver_handle.find_element_by_id('tab1_1')
    driver_handle.switch_to.frame(frame)

    exportBut = driver_handle.find_element_by_xpath('//*[@id="Export"]')
    time.sleep(2)
    exportBut.click()
    time.sleep(2)
    driver_handle.find_element_by_xpath('//*[@id="ExportCSV"]').click()

    driver_handle.switch_to.default_content()
    time.sleep(5)
    driver_handle.find_element_by_xpath('//*[@id="Export"]').click()

def navigateParagon(d):

    window_after = d.window_handles[1]
    d.switch_to.window(window_after)
    d.set_page_load_timeout(30)
    time.sleep(20)
    print('Log: Paragon Redirect')


    d.switch_to.default_content()
    pass_frame_home(d,'RE-SFR')
    time.sleep(10)
    d.switch_to.default_content()
    print('Log: SFR Done')
    d.find_element_by_xpath('//*[@id="tab-bg"]/li[2]/em').click()
    time.sleep(5)
    pass_frame_home(d,'RE-TWNHM')
    time.sleep(10)
    d.switch_to.default_content()
    print('Log: TWNHM Done')
    d.find_element_by_xpath('//*[@id="tab-bg"]/li[2]/em').click()
    time.sleep(5)
    pass_frame_home(d,'RE-CONDO')
    print('Log: CONDO Done')


    time.sleep(20)
    driver.quit()
    return d

driver = setupDriver()
driver = setupLoginMLS(driver)
driver = navigateParagon(driver)
