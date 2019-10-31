i"""
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
import os

        
class Scraper: 
    def __init__(self, site="https://www.macys.com"):
        self.site = site 
        self.Categories = set()
        self.URLs = set()
        self.products = []
        self.soup = None
        
    def get_parse(self, site): 
        agent = {"User-Agent":"Mozilla/5.0"} 
        my_api_key = apikey.Key()
        payload = {'api_key':my_api_key, 'url':site}
        #page = requests.get(site, headers=agent)
        
        #For when using Scraper API to avoid getting blocked 
        page = requests.get('http://api.scraperapi.com', 
                            headers = agent,
                            params = payload, timeout=60) 
        self.soup = Soup(page.content, "html.parser")
    

    def get_url_categories(self):
        self.get_parse(self.site)
        soup = self.soup
        #print(soup)
        for tag in soup.find_all("a", href=True):
            path = tag["href"]
            if "http" not in path\
                and "COL" in path\
                and "/shop/" in path:
                self.Categories.add(self.site+path)
        
        return self.Categories
    
    
    def get_url_products(self):
        self.get_url_categories()
#         test = self.Categories.pop()
#         self.Categories.add(test)
#         self.get_parse(test)
#         soup = self.soup
        for url in self.Categories:
            self.get_parse(url)
            soup = self.soup
            for tag in soup.find_all("a", {"class": "productDescLink"}):
                path = tag.get("href")
                self.URLs.add(self.site+path)
        
        return self.URLs
            
        
    def scrape(self):
        self.get_url_products()
        for url in self.URLs:
            self.get_parse(url)
            soup = self.soup
            try: 
                name = (((soup.find_all("h1", {"class": "p-name h3"})[0].text)\
                        .replace("\n","")).strip()).upper()
                price = ((soup.find_all("div", {"class": "price"})[0].text)\
                         .replace("\n","")).strip()
                des = ((soup.find_all("p", {"data-auto": "product-description"})[0].text)\
                       .replace("\n","")).strip()
                self.products.append([name, price, des])
            except IndexError:
                pass
            
        return self.products
    
    
    def save_cvs(self):
        self.scrape()
        with open("macys-products.cvs", "w+") as csvf:
            w = csv.writer(csvf, delimiter=",")
            for i in self.products:
                w.writerow(i)
                
    
    def get_product_info(self, name):
        name = str(name).upper()
        with open("macys-products.cvs", "r") as csvf:
            r = csv.reader(csvf, delimiter=",")
            for row in r:
                if row[0]==name:
                    print("\n product name: {}\
                          \n price: {}\
                          \n details: {}"\
                          .format(row[0], row[1], row[2]))    
            
            
scrape = Scraper()

#=================Scrape and save data from macys.com=============
#scrape.scrape()
scrape.save_cvs()

#==============Search product info by name========================
product_name = input("Search product name: ")
scrape.get_product_info(product_name)

