"""
Build a web scraper for one of the retail websites: macys.com.

Author: Ye N.E.

Description:
    (1) The web scraper should scrape Macys.com
        whenever you run your program, scrape all of the products
        listed on Macy's homepage,
        and save the following data for each product
        in a CSV file: the product name, price, and description.
    (2) The information should come from the product pages
        (such as here: https://mcys.co/2GiLTRq)
    (3) Your program needs a function that allows me to search 
        by name all of the products in the CSV file.
        If a product is found, your program should print
        the product name, price, and description.
"""

from bs4 import BeautifulSoup as Soup
from multiprocessing import Pool 
from lxml.html import fromstring
from itertools import cycle
import requests
import random
import csv
import apikey
import useragentls
import pandas as pd
import sys


print("If you're going to use ScraperAPI,\
      \nplease specify your api key in 'apikey.py'.\
      \nGet your api key at 'ScraperAPI.com'.")
which_request = input("\nEnter '1' for basic request,\
                        \n '2' to use ScraperAPI\
                        \n or 'q' to quit the program: ")
if which_request == 'q':
    sys.exit()
answer = ['1', '2', 'q']
while which_request not in answer: 
    message = input("\nPlease try again!\
                    \nEnter '1' for basic request,\
                \nor enter '2' to use ScraperAPI: ")
    which_request = message


class RequestsBS4():
    def __init__(self, site):
        self.site = site
        self.user_agent_list = useragentls.list
        user_agent = random.choice(self.user_agent_list)
        self.headers = {'User-Agent': user_agent}
        self.page = None
                        
    def get_proxies(self):
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = set()
        for i in parser.xpath('//tbody/tr')[:10]:
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                #Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], 
                                  i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)
        return proxies
         
    def basic_request(self):
        proxy_pool = cycle(self.get_proxies())
        proxy = next(proxy_pool)
        proxies = {"http": proxy, "https": proxy}
        try: 
            self.page = requests.get(self.site, 
                                     headers = self.headers,
                                     proxies = proxies,
                                     timeout=60)
            if self.page.status_code != 200:
                print(self.page.status_code, self.page.text)
            soup = Soup(self.page.content, "html.parser")
        except:
            print('\nSkipping. Connection Error')
        return soup
    
    def scraper_api(self):
        your_api_key = apikey.key
        if your_api_key == 'YOUR_KEY_HERE':
            sys.exit("\nERROR: You have not provided your api key.\n")
        else:
            payload = {'api_key':your_api_key, 'url':self.site}
            self.page = requests.get('http://api.scraperapi.com', 
                                headers = self.headers,
                                params = payload, timeout=60) 
            soup = Soup(self.page.content, "html.parser")
        return soup 
    
    def get_url(self):
        global which_request 
        if which_request == '1':
            soup = self.basic_request()
        elif which_request == '2':
            soup = self.scraper_api()
        return soup 
    
    
class Scraper:
    def __init__(self, site="https://www.macys.com"):
        self.site = site 
        self.Categories = set()
        
    def get_url_categories(self):
        soup = RequestsBS4(self.site).get_url()
        print("\nGETTING CATEGORIES URLs...")
        for tag in soup.find_all("a", href=True):
            path = tag["href"]
            if "http" not in path\
                and "COL" in path\
                and "/shop/" in path:
                self.Categories.add(self.site+path)
        self.Categories = list(self.Categories)
        return self.Categories
    
    def get_url_products_test(self):       
        #For small sample testing
        self.get_url_categories()
        test = self.Categories[-1]
        soup = RequestsBS4(test).get_url()
        URLs = set() 
        for tag in soup.find_all("a", {"class": "productDescLink"}):
                path = tag.get("href")
                URLs.add(tuple([self.site+path]))
        print('\n{} URLs are now fetched from {}'.format(len(URLs), test))
        links = list(URLs)
        with open('product-url.csv', 'a') as csvf:
            w = csv.writer(csvf)
            for i in links:
                w.writerow(i)
        return URLs
        
    def get_url_products(self, url = None):  
        #For full website run
        soup = RequestsBS4(url).get_url()
        URLs = set()
        for tag in soup.find_all("a", {"class": "productDescLink"}):
            try:
                path = tag.get("href")
                URLs.add(tuple([self.site+path]))
            except requests.exceptions.SSLError:
                pass 
        print('\n{} URLs are now fetched from {}'.format(len(URLs), url))
        links = list(URLs)
        with open('product-url.csv', 'a') as csvf:
            w = csv.writer(csvf)
            for i in links:
                w.writerow(i)
        return URLs
            
    def scrape_and_save(self, url = None):
        with open("macys-products-raw.csv", "a") as csvf:
            w = csv.writer(csvf, delimiter=",")
            request = RequestsBS4(url)
            soup = request.get_url()
            page = request.page
            products = []
            if page.status_code == 200:
                print('\nProcesscing... {}'.format(url))  
            try:
                name = (((soup.find_all("h1", {"class": "p-name h3"})[0].text)\
                        .replace("\n","")).strip()).upper()
                price = ((soup.find_all("div", {"class": "price"})[0].text)\
                         .replace("\n","")).strip()
                des = ((soup.find_all("p", {"data-auto": "product-description"})[0].text)\
                       .replace("\n","")).strip()
                products.append((name, price, des))
                w.writerow(products[-1])
            except IndexError:
                pass
        return products

    def get_product_info(self):
        while True:
            found = False
            product_name = input("\nEnter product name\
                                 \nOr type 'q' to quit the program: ")
            name = str(product_name).upper()
            if name == 'Q':
                break
            df = pd.read_csv('macys-products-clean.csv')
            for index, row in df.iterrows():
                if name == row[0]:
                    print("\nProduct Name: {} \n\
                          \nPrice: {} \n\
                          \nDetails: {}"\
                          .format(row[0], row[1], row[2]))
                    found = True
            if found == True: 
                print('\nNext search...')
            elif found == False:
                print('\nNo product with such name. Please try again!')
                
     
if __name__ == "__main__": 
        
    scraper = Scraper()
    
    #For small sample test run:
    scraper.get_url_products_test()
    url = []
    with open ('product-url.csv', 'r') as csvf:
        r = csv.reader(csvf)
        for row in r:
            url.append(row[0])
    
    p2 = Pool(processes=4)
    product_scraping = p2.map(scraper.scrape_and_save, url)
    p2.terminate()
    p2.join()
    
    
    #=================For full web run: setup parallel processing tasks========
    #Get product urls:
# =============================================================================
#     category_urls = scraper.get_url_categories()
#     p1 = Pool(processes=4)
#     url_scraping = p1.map(scraper.get_url_products, category_urls)
#     p1.terminate()
#     p1.join()
#     
#     #Scrape, parse, and save data:
#     url = []
#     with open ('product-url.csv', 'r') as csvf:
#         r = csv.reader(csvf)
#         for row in r:
#             url.append(row[0])
#     
#     p2 = Pool(processes=4)
#     product_scraping = p2.map(scraper.scrape_and_save, url)
#     p2.terminate()
#     p2.join()
# =============================================================================
    
    
    #=================Data cleansing: remove duplicates from data output=======
    colnames = ['Product name', 'Price', 'Details']
    data = pd.read_csv('macys-products-raw.csv', names=colnames)
    data.sort_values('Product name', inplace = True)
    data.drop_duplicates(subset='Product name', keep=False, inplace=True)
    df = pd.DataFrame(data)
    df.to_csv('macys-products-clean.csv', header=False, index=False)
    
    
    #==============Search product info by name========================
    scraper.get_product_info()



