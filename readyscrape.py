"""
The module performs common manipulation when building a web scraper

Author: Ye N.E.

Description:
    (1) make request to a url using "requests" module 
    (2) parse the url's content using "BeautifulSoup" frameworks 
    (3) NOTE: If you want to use Scraper API, 
        you must provide your API_KEY obtained from scraperapi.com.
	Search for "REPLACE_ME" in this code to find the correct place 
        to provide that key. 
        Search for "SCRAPER_API" in this code and change its value to "ON".  
"""

from bs4 import BeautifulSoup as Soup
from itertools import cycle
import requests
from requests.exceptions import Timeout
import random
import useragentls
import sys
import pandas as pd


API_KEY = 'REPLACE_ME'
SCRAPER_API = 'OFF' #choose 'ON' or 'OFF'


class RequestsBS4:
    def __init__(self, site):
        self.site = site
        self.user_agent_list = useragentls.list
        user_agent = random.choice(self.user_agent_list)
        self.headers = {'User-Agent': user_agent}
        self.page = None
        self.soup = None
                        
    def get_proxies(self):
        proxies = set()
        url = 'https://free-proxy-list.net/'
        page = requests.get(url)
        soup = Soup(page.content, "html.parser")
        table = soup.find('table', id="proxylisttable")
        rows = table.find_all('tr')
        for row in rows[1:]:
            try:
                IP = (row.find_all('td'))[0].text
                port = (row.find_all('td'))[1].text
                proxies.add(":".join([IP, port]))
            except IndexError:
                pass
        return proxies
       
    def basic_request(self):
        proxy_pool = cycle(self.get_proxies())
        proxy = next(proxy_pool)
        proxies = {"http": proxy, "https": proxy}
        try:
            self.page = requests.get(self.site, 
                                 headers = self.headers,
                                 proxies = proxies,
                                 timeout = 60)
            if self.page.status_code != 200:
                print(self.page.status_code, self.page.text)
            self.soup = Soup(self.page.content, "html.parser")
        except Timeout:
            print('The request timed out')
        return self.soup
    
    def scraper_api(self):
        your_api_key = API_KEY 
        if your_api_key == 'REPLACE_ME':
            sys.exit("\nERROR: You have not provided your api key.\n")
        else:
            payload = {'api_key':your_api_key, 'url':self.site}
            self.page = requests.get('http://api.scraperapi.com', 
                                headers = self.headers,
                                params = payload, timeout=60) 
            self.soup = Soup(self.page.content, "html.parser")
        return self.soup 
    
    def get_url(self):
        if SCRAPER_API == "OFF": 
            print("PERFORMING BASIC SCRAPING")
            scrape = self.basic_request()
        elif SCRAPER_API == "ON":
            print("SCRAPE WITH SCRAPER API") 
            scrape = self.scraper_api()
        return scrape


class DataProcessing:    
    def __init__(self, add_data={}, colnames=['col_1'], fname="output.csv"):
        self.add_data = add_data
        self.colnames = colnames
        self.fname = fname
        
    def add_to_csv(self):
        df = pd.read_csv(self.fname, names=self.colnames)
        df1 = pd.DataFrame(self.add_data)
        df2 = df.append(df1, ignore_index=True) 
        df2.drop_duplicates(inplace=True)
        df2.to_csv(self.fname, header=False, index=False)
        output_col_1 = df2[self.colnames[0]].values.tolist() 
        return output_col_1
