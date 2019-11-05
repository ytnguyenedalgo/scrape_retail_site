# scrape_retail_site
The web scraper will scrape Macys.com.

Whenever running the program, it will scrape all of the products
listed on Macy's homepage, and save the following data for each product
in a CSV file: the product name, price, and description.

## New implementation:
  - Speed up the web scraper by using multiprocessing module ✓

## Guides:
1. *"ScrapeRetailSite.py"*:
  - Run the "ScrapeRetailSite.py" to scrape, save, and search through data gotten from www.macys.com.
  - Data of interest are products listed on Macy's homepage.

2. *"apikey.py"* 
  - A module written for "ScrapeRetailSite.py" to collect user's API key from www.scraperapi.com.
  - **If user(s) will be using Scraper API to scrape data, please specify your API key in "apikey.py".** 
  
3. *"product-url.csv"*
  - Where product urls from "ScrapeRetailSite.py" will be collected and stored.
  - Each row of outputs shows the URL from where the information about the products would be obtained 

4. *"macys-product-raw.csv"*
  - Where the products information from "ScrapeRetailSite.py" will be collected and stored.
  - Each row of outputs shows the product name, price, and description, respectively.
  
5. *"macys-product-clean.csv"*
  - Data cleansing of "macys-product-raw.csv" using pandas software to sort product by their names and
 remove duplicates 
  - Each row of outputs shows the product name, price, and description, respectively.
  - The current data shown might not be complete due to Issue #1

## Current limitation:
  - Issue #1 : Without using Scraper API, site access will be denied (for a day or two) at some point during web scraping. Using Scraper API will help avoid this issue but this approach will cost. 
