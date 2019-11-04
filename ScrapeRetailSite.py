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
from time import sleep
import requests
import csv
import apikey
import pandas as pd


class RequestsBS4():
    def __init__(self, site):
        self.site = site
        self.agent = {"User-Agent":"Mozilla/5.0"} 
        self.page = None
        self.soup = None
        
        
    def basic_request(self):
        self.page = requests.get(self.site, headers=self.agent, timeout=60)
        if self.page.status_code != 200:
            print(self.page.text)
        self.soup = Soup(self.page.content, "html.parser")
        
        return self.soup
    
    
    def scraper_api(self):
        your_api_key = apikey.Key()
        payload = {'api_key':your_api_key, 'url':self.site}
        self.page = requests.get('http://api.scraperapi.com', 
                            headers = self.agent,
                            params = payload, timeout=60) 
        self.soup = Soup(self.page.content, "html.parser")
        
        return self.soup 
    
    
class Scraper:
    def __init__(self, site="https://www.macys.com"):
        self.site = site 
        self.Categories = set()
        

    def get_url_categories(self):
        print("GETTING CATEGORIES URLs...")
        soup = RequestsBS4(self.site).basic_request()
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
        soup = RequestsBS4(test).basic_request()
        URLs = set() 
        for tag in soup.find_all("a", {"class": "productDescLink"}):
                path = tag.get("href")
                URLs.add(tuple([self.site+path]))
        print('{} URLs are now fetched from {}'.format(len(URLs), test))
        
        #For full website run
# =============================================================================
#         soup = RequestsBS4(url).basic_request()
#         URLs = set()
#         for tag in soup.find_all("a", {"class": "productDescLink"}):
#             path = tag.get("href")
#             URLs.add(tuple([self.site+path]))
#         print('{} URLs are now fetched from {}'.format(len(URLs), url))
# =============================================================================
            
        links = list(URLs)
        
        with open('product-url.csv', 'a') as csvf:
            w = csv.writer(csvf)
            for i in links:
                w.writerow(i)
            
        return URLs
            
        
    def scrape_and_save(self, url):
        with open("macys-products.csv", "a") as csvf:
            w = csv.writer(csvf, delimiter=",")
            request = RequestsBS4(url)
            soup = request.basic_request()
            page = request.page
            products = []
            if page.status_code == 200:
                print('Processcing... {}'.format(url))  
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
            product_name = input("Search product name\
                                 \nOr type 'q' to quit the program: ")
            name = str(product_name).upper()
            if name == 'Q':
                break
            with open("macys-products.cvs", "r") as csvf:
                r = csv.reader(csvf, delimiter=",")
                for row in r:
                    if name == row[0]:
                        print("\n product name: {}\
                              \n price: {}\
                              \n details: {}"\
                              .format(row[0], row[1], row[2]))
                        break    
                print('\nNo product with such name. Please try again!')
                
     
if __name__ == "__main__": 
        
    scraper = Scraper()
    scraper.get_url_products()
    
    
    #=================Setup a parallel processing tasks=============
    #Get product urls:
# =============================================================================
#     category_urls = scraper.get_url_categories()
#     p1 = Pool(processes=4)
#     url_scraping = p1.map(scraper.get_url_products, category_urls)
#     p1.terminate()
#     p1.join()
# =============================================================================
    
    #Scrape, parse, and save data:
    url = []
    with open ('product-url.csv', 'r') as csvf:
        r = csv.reader(csvf)
        for row in r:
            url.append(row[0])
    
    p2 = Pool(processes=4)
    product_scraping = p2.map(scraper.scrape_and_save, url)
    p2.terminate()
    p2.join()
    
    
    #=================Remove duplicates from data output=============
    colnames = ['Product name', 'Price', 'Details']
    data = pd.read_csv('macys-products.csv', names=colnames)
    data.sort_values('Product name', inplace = True)
    data.drop_duplicates(subset='Product name', keep=False, inplace=True)
    
    
    #==============Search product info by name========================
    scraper.get_product_info()



