from pyvirtualdisplay import Display
from datetime import datetime
import re, json, os, time, sys, math, traceback
from bs4 import BeautifulSoup
import requests
import logging

from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
d = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
# d.get('https://www.google.com/')


# option = webdriver.ChromeOptions()
# option.add_argument("--incognito")
# browser = webdriver.Chrome(executable_path='./chromedriver', chrome_options=option)
# # driver = webdriver.Chrome(executable_path='./chromedriver')
# results = browser.get('https://pro.mlslistings.com')
# browser.set_page_load_timeout(150)

# d.get_attribute('innerHTML')

# soup = BeautifulSoup(d.content, 'html.parser')
# print(soup.prettify())


# d.quit()

d.implicitly_wait(2)
d.get("https://pro.mlslistings.com")
# to identify element and obtain innerHTML with get_attribute
licenseID = d.find_element_by_name("ctl00$MainContent$UCLogin$unknownUserDRE")
licenseID.send_keys("01783775")
continueLogin = d.find_element_by_name("ctl00$MainContent$UCLogin$unknownUserContinue")
continueLogin.click()
d.implicitly_wait(2)
d.find_element_by_name("ctl00$MainContent$UCLogin$ibtnSignIn").click()
d.implicitly_wait(2)
html = d.page_source
print(html)
# print("HTML code of element: " + l.get_attribute('innerHTML'))


