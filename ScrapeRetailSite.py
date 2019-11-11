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
#from time import sleep
import requests
import random
import csv
import apikey
import pandas as pd


class RequestsBS4():
    def __init__(self, site):
        self.site = site
        self.user_agent_list = [
            #Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            #Firefox
            'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
            'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
            'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
            ]
        user_agent = random.choice(self.user_agent_list)
        self.headers = {'User-Agent': user_agent}
        self.page = None
        self.soup = None
                        
        
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
            self.soup = Soup(self.page.content, "html.parser")
        except:
            print('\nSkipping. Connection Error')
        
        return self.soup
    
    
    def scraper_api(self):
        your_api_key = apikey.Key()
        payload = {'api_key':your_api_key, 'url':self.site}
        self.page = requests.get('http://api.scraperapi.com', 
                            headers = self.headers,
                            params = payload, timeout=60) 
        self.soup = Soup(self.page.content, "html.parser")
        
        return self.soup 
    
    
class Scraper:
    def __init__(self, site="https://www.macys.com"):
        self.site = site 
        self.Categories = set()
        print("\nIf you're going to use ScraperAPI, make sure to\
                        \nspecify your api key in apikey.py.")
        self.which_request = input("\nEnter '1' for basic request,\
                        \nor enter '2' to use ScraperAPI: ")
        answer = ['1', '2']
        while self.which_request not in answer: 
            message = input("\nPlease try again!\
                            \nEnter '1' for basic request,\
                        \nor enter '2' to use ScraperAPI: ")
            self.which_request = message
        

    def get_url_categories(self):
        print("\nGETTING CATEGORIES URLs...")
        request = RequestsBS4(self.site)
        if self.which_request == '1':
            soup = request.basic_request()
        elif self.which_request == '2':
            soup = request.scraper_api()
        for tag in soup.find_all("a", href=True):
            path = tag["href"]
            if "http" not in path\
                and "COL" in path\
                and "/shop/" in path:
                self.Categories.add(self.site+path)
                
        self.Categories = list(self.Categories)
        
        return self.Categories
    
    
    def get_url_products(self, url = None):       
        #For small sample testing
        self.get_url_categories()
        test = self.Categories[-1]
        request = RequestsBS4(test)
        if self.which_request == '1':
            soup = request.basic_request()
        elif self.which_request == '2':
            soup = request.scraper_api()
        URLs = set() 
        for tag in soup.find_all("a", {"class": "productDescLink"}):
                path = tag.get("href")
                URLs.add(tuple([self.site+path]))
        print('\n{} URLs are now fetched from {}'.format(len(URLs), test))
        
        #For full website run
# =============================================================================
#         request = RequestsBS4(url)
#         if self.which_request == '1':
#             soup = request.basic_request()
#         elif self.which_request == '2':
#             soup = request.scraper_api()
#         URLs = set()
#         for tag in soup.find_all("a", {"class": "productDescLink"}):
#             try:
#                 path = tag.get("href")
#                 URLs.add(tuple([self.site+path]))
#             except requests.exceptions.SSLError:
#                 pass 
#         print('\n{} URLs are now fetched from {}'.format(len(URLs), url))
# =============================================================================
            
        links = list(URLs)
        
        with open('product-url.csv', 'a') as csvf:
            w = csv.writer(csvf)
            for i in links:
                w.writerow(i)
            
        return URLs
            
        
    def scrape_and_save(self, url):
        with open("macys-products-raw.csv", "a") as csvf:
            w = csv.writer(csvf, delimiter=",")
            request = RequestsBS4(url)
            if self.which_request == '1':
                soup = request.basic_request()
            elif self.which_request == '2':
                soup = request.scraper_api()
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
    scraper.get_url_products()
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



