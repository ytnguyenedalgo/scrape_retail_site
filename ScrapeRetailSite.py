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
import requests
import csv
import apikey


class RequestsBS4():
    def __init__(self, site):
        self.site = site
        self.agent = {"User-Agent":"Mozilla/5.0"} 
        self.soup = None
        
        
    def basic_request(self):
        page = requests.get(self.site, headers=self.agent)
        print(page.status_code)
        self.soup = Soup(page.content, "html.parser")
        
        return self.soup
    
    
    def scraper_api(self):
        your_api_key = apikey.Key()
        payload = {'api_key':your_api_key, 'url':self.site}
        page = requests.get('http://api.scraperapi.com', 
                            headers = self.agent,
                            params = payload, timeout=60) 
        self.soup = Soup(page.content, "html.parser")
        
        return self.soup 
    
    
class Scraper: 
    def __init__(self, site="https://www.macys.com"):
        self.site = site 
        self.Categories = set()
        self.URLs = set()
        self.products = []
        self.soup = None
        

    def get_url_categories(self):
        soup = RequestsBS4(self.site).basic_request()
        for tag in soup.find_all("a", href=True):
            path = tag["href"]
            if "http" not in path\
                and "COL" in path\
                and "/shop/" in path:
                self.Categories.add(self.site+path)
        
        return self.Categories
    
    
    def get_url_products(self):
        self.get_url_categories()
        
        #For small sample testing
        test = self.Categories.pop()
        self.Categories.add(test)
        soup = RequestsBS4(test).basic_request()
        for tag in soup.find_all("a", {"class": "productDescLink"}):
                path = tag.get("href")
                self.URLs.add(self.site+path)
        
        #For full website run
# =============================================================================
#         for url in self.Categories:
#             soup = RequestsBS4(url).basic_request()
#             for tag in soup.find_all("a", {"class": "productDescLink"}):
#                 path = tag.get("href")
#                 self.URLs.add(self.site+path)
# =============================================================================
        
        return self.URLs
            
        
    def scrape_and_save(self):
        self.get_url_products()
        with open("macys-products.cvs", "w+") as csvf:
            w = csv.writer(csvf, delimiter=",")
            for url in self.URLs:
                soup = RequestsBS4(url).basic_request()
                try: 
                    name = (((soup.find_all("h1", {"class": "p-name h3"})[0].text)\
                            .replace("\n","")).strip()).upper()
                    price = ((soup.find_all("div", {"class": "price"})[0].text)\
                             .replace("\n","")).strip()
                    des = ((soup.find_all("p", {"data-auto": "product-description"})[0].text)\
                           .replace("\n","")).strip()
                    self.products.append([name, price, des])
                    w.writerow(self.products[-1])
                except IndexError:
                    pass
            
        return self.products
    
        
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
            
            
scrape = Scraper()

#=================Scrape and save data from macys.com=============
scrape.scrape_and_save()

#==============Search product info by name========================
scrape.get_product_info()

