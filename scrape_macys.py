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
    (3) Your program needs a function that allows searching
        by name all of the products in the CSV file.
        If a product is found, your program should print
        the product name, price, and description.
    (4) NOTE: If you want to use Scraper API, 
        you must provide your API_KEY obtained from scraperapi.com.
	Search for "REPLACE_ME" in this code to find the correct place
	to provide that key
"""

from multiprocessing import Pool 
from readyscrape import RequestsBS4, DataProcessing
import pandas as pd
import sys


class Scraper:
    def __init__(self, site="https://www.macys.com"):
        self.site = site 
        
    def get_url_categories(self):
        request = RequestsBS4(self.site)
        soup = request.get_url()
        page = request.page
        print(page.status_code)
        print("\nGETTING CATEGORIES URLs...")
        Categories = set()
        for tag in soup.find_all("a", href=True):
            path = tag["href"]
            if "http" not in path\
                and "COL" in path\
                and "/shop/" in path:
                Categories.add(self.site+path)
        Categories = list(Categories)
        return Categories
    
    def get_url_products_test(self):       
        #For small sample testing
        category_urls = self.get_url_categories()
        test = category_urls[-1]
        soup = RequestsBS4(test).get_url()
        URLs = []
        for tag in soup.find_all("a", {"class": "productDescLink"}):
                path = tag.get("href")
                URLs.append(self.site+path)
        print('\n{} URLs are now fetched from {}'.format(len(URLs), test))
        add_data = {'url':URLs}
        colnames = ['url']
        fname = "product-url.csv"
        URLs = DataProcessing(add_data, colnames, fname).add_to_csv()
        return URLs
        
    def get_url_products(self, url = None):  
        #For full website run
        soup = RequestsBS4(url).get_url()
        URLs = []
        for tag in soup.find_all("a", {"class": "productDescLink"}):
                path = tag.get("href")
                URLs.append(self.site+path)
        print('\n{} URLs are now fetched from {}'.format(len(URLs), url))
        add_data = {'url':URLs}
        colnames = ['url']
        fname = "product-url.csv"
        URLs = DataProcessing(add_data, colnames, fname).add_to_csv()
        return URLs
            
    def scrape_and_save(self, url = None):
        request = RequestsBS4(url)
        soup = request.get_url()
        page = request.page
        name_ls, price_ls, des_ls = [], [], []
        if page.status_code == 200:
            print('\nProcesscing... {}'.format(url))  
        try:
            name = (((soup.find_all("h1", {"class": "p-name h3"})[0].text)\
                    .replace("\n","")).strip()).upper()
            price = ((soup.find_all("div", {"class": "price"})[0].text)\
                     .replace("\n","")).strip()
            des = ((soup.find_all("p", {"data-auto": "product-description"})[0].text)\
                   .replace("\n","")).strip()
            if name!= None and price!= None and des!= None:
                name_ls.append(name)
                price_ls.append(price)
                des_ls.append(des)
        except IndexError:
            pass
        colnames = ['name', 'price', 'des']
        fname = "macys-products.csv"
        add_data = {colnames[0]:name_ls,
                    colnames[1]:price_ls, 
                    colnames[2]:des_ls}
        DataProcessing(add_data, colnames, fname).add_to_csv()

    def get_product_info(self):
        while True:
            found = False
            product_name = input("\nEnter product name\
                                 \nOr type 'q' to quit the program: ")
            name = str(product_name).upper()
            if name == 'Q':
                break
            df = pd.read_csv('macys-products.csv')
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

    scrape_choice = input("\nEnter 't' to scrape a small sample,\
                          \n'f' to scape full web,\
                          \n's' to search for product information,\
                          \nor press 'q' to quit the program: ").upper()
    
    while scrape_choice not in ['T', 'F', 'S', 'Q']:
        scrape_choice = scrape_choice
    
    if scrape_choice == 'Q':
        sys.exit() 
    
    #For small sample test run
    if scrape_choice == 'T': 
        url = scraper.get_url_products_test()
        p2 = Pool(processes=2)
        product_scraping = p2.map(scraper.scrape_and_save, url)
        p2.terminate()
        p2.join()
    
    #For full web run: setup parallel processing tasks
    elif scrape_choice == 'F':
        #Get product urls:
        category_urls = scraper.get_url_categories()
        p1 = Pool(processes=4)
        url_scraping = p1.map(scraper.get_url_products, category_urls)
        p1.terminate()
        p1.join()
        #Scrape, parse, and save data:
        product_urls = pd.read_csv("product-url.csv", names=["url"])
        url = product_urls["url"].values.tolist()
        p2 = Pool(processes=2)
        product_scraping = p2.map(scraper.scrape_and_save, url)
        p2.terminate()
        p2.join()
    
    #Search product info by name    
    elif scrape_choice == 'S':
        scraper.get_product_info()