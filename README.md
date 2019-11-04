# scrape_retail_site
The web scraper will scrape Macys.com.

Whenever running the program, it will scrape all of the products
listed on Macy's homepage, and save the following data for each product
in a CSV file: the product name, price, and description.

## Implementation in progress:
1. Speed up the web scraper by using multiprocessing 

## Guides:
1. *"ScrapeRetailSite.py"*:
  - Run the "ScrapeRetailSite.py" to scrape, save, and search through data gotten from www.macys.com.
  - Data of interest are products listed on Macy's homepage.

2. *"apikey.py"* 
  - A module written for "ScrapeRetailSite.py" to collect user's API key from www.scraperapi.com.
  - **If user(s) will be using Scraper API to scrape data, please specify your API key in "apikey.py".** 

3. *"macys-product.csv"*
  - Where outputs from "ScrapeRetailSite.py" will be collected and stored.
  - Each row of outputs shows the product name, price, and description, respectively.
  - The current data shown is a small sample collected when testing the code.
