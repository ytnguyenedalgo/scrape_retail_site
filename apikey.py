"""
If you use ScraperAPI.com tool to scrape, 
    please modify and specify your API key provided by scraperapi.com\
    to variable your_key below
"""

your_key = 'YOUR_KEY_HERE'

class Key():
    def __init__(self):
        global your_key
        self.key = "{}".format(your_key)

    def __repr__(self):
        return self.key
