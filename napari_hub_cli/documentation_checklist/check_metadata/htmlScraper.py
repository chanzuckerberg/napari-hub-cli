from html.parser import HTMLParser
import requests
from bs4 import BeautifulSoup

def get_html(readme_link):
    """Scrapes the HTML from a specified link

    Parameters
    ----------
    readme_link : str
        link to the repository where the citation is needed
        
    Returns
    -------
        data from the HTML link specified
        
    """
    html = requests.get(readme_link).text
    return BeautifulSoup(html, 'html5lib')
    

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    """Strips the HTML tags from the HTML data collected

    Parameters
    ----------
    html : str
        HTML scraped data from the link specified
        
    Returns
    -------
        scraped data from the link specified without HTML tags
        
    """
    s = MLStripper()
    s.feed(html)
    return s.get_data()