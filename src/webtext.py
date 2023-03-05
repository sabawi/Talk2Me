"""
        By  : Al Sabawi
            : 01/03/2011
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import xmltodict, json
import html
from html.parser import HTMLParser

from io import StringIO
from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def readpage(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

def readfeed(url):

    t = xmltodict.parse(urlopen(url).read())
    return t

def get_headlines():
    urls = { # Replace local news rss feed with your fav local source
        "Local News": "https://rssfeeds.pressconnects.com/binghamton/home&x=1",
        "CBS Top News": "https://www.cbsnews.com/latest/rss/main",
        "New York Times": "http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "CNBC News": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15837362",
        "CNN": "http://rss.cnn.com/rss/cnn_latest.rss"
        }
    output = ''
    max_per_site = 2 # 2 headlines per source is good enough
    for v in urls:
        output += (f"\n\nTop Headlines from {v}:\n")
        jtext = readfeed(urls[v])
        h = html.parser
        headline_count = 0

        for i in range(len(jtext['rss']['channel']['item'])):
            if i >= max_per_site:
                break;
            else:
                title = h.unescape(jtext['rss']['channel']['item'][i]['title'])
                description = h.unescape(jtext['rss']['channel']['item'][i]['description'])
                output += '\n'+title+":\n"+description
                headline_count +=1
    return strip_tags(output)

if __name__ == "__main__":
    print(get_headlines())