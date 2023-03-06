"""
        By  : Al Sabawi
            : 01/03/2011
"""
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import html
from html.parser import HTMLParser
from io import StringIO
from html.parser import HTMLParser
import feedparser
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

def feed2json(rss_url):
    # Parse the RSS feed
    feed = feedparser.parse(rss_url)

    # Convert the feed to JSON
    feed_json = json.dumps(feed.entries)

    # return the JSON output
    return feed_json

def readpage(url):
    html = urlopen(url).read().decode('utf-8')
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
    # Parse the RSS feed
    feed = feedparser.parse(url)

    # Convert the feed to a dictionary
    feed_dict = {'feed': {'title': feed.feed.title, 'link': feed.feed.link, 'entries': []}}
    for entry in feed.entries:
        # Check if the description field is present
        if 'description' in entry:
            # Remove HTML tags from the description using BeautifulSoup
            soup = BeautifulSoup(entry.description, 'html.parser')
            description = soup.get_text()
        else:
            description = ''
        feed_dict['feed']['entries'].append({'title': entry.title, 'link': entry.link, 'description': description})

    return feed_dict

def get_headlines():
    urls = { # Replace local news rss feed with your fav local source
        "Local News": "https://rssfeeds.pressconnects.com/binghamton/home&x=1",
        "New York Times": "http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "Reuters Top News": "https://www.reutersagency.com/feed/?best-regions=north-america&post_type=best'",
        "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
        "CNBC News": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15837362",
        "CNN Top Stories": "http://rss.cnn.com/rss/cnn_topstories.rss"
        }
    output = ''
    max_per_site = 2 # 2 headlines per source is good enough
    for v in urls:
        output += (f"\nTop Headlines from {v}:")
        feed = readfeed(urls[v])
        h = html.parser
        headline_count = 0

        for i in feed['feed']['entries']:
            if headline_count >= max_per_site:
                break;
            else:
                # clean these headlines 
                title = str(h.unescape(i['title'])).strip()
                description = str(h.unescape(i['description'])).strip()
                output += '\n'+title+":\n"+description
                headline_count +=1
    text = str(strip_tags(output)).strip()
    return text

if __name__ == "__main__":
    print(get_headlines())