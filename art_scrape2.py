from bs4 import BeautifulSoup
import feedparser
import requests
import json
from datetime import datetime,date

def art_parser(link):
    r = requests.get(link)
    page = r.text
    soup = BeautifulSoup(page,"lxml")
    paras = soup.find_all('p')
    article = [x for x in paras]
    atriclestrip = [art.get_text() for art in article]
    prep_art = ' '.join(atriclestrip)
    return prep_art

def get_feed_links(feed,lang):
    try:
        d = feedparser.parse(feed)
    except:
        print('feed error '+feed)
        pass
    links = []
    for x in range(len(d['entries'])):
        try:
            if 'http://' in d['entries'][x]['link'] or 'https://' in d['entries'][x]['link']:
                page_link = d['entries'][x]['link']
                links.append(page_link)
            else:
                print('bad link')
        except:
            print('bad link')

    prevrsslinkfile = 'prev_' + lang + '_rsslinks.txt'
    prev_rsslinks = json.load(open(prevrsslinkfile))
    newlinks = set(links).difference(set(prev_rsslinks))

    return newlinks

def get_feed_articles(links,min_len=1000):
    today = date.today()
    articles = []
    for link in links:
        try:
            art = art_parser(link)
            item = {'link':link,'date':today, 'article':art}
            if len(art) > min_len:
                articles.append(item)
        except:
            print('art error '+link)
            pass

    return articles

def prep_articles(feed,lang):
    new_links = get_feed_links(feed,lang)
    articles = get_feed_articles(new_links)
    return articles,new_links

def get_articles(lang):
    rsslinks = json.load(open(lang + '_rsslinks.txt'))
    total = len(rsslinks)
    print(total)
    articles = []
    usedlinks = []
    count = 0
    for feed in rsslinks:
        arts,new_links = prep_articles(feed,lang)
        articles.append(arts)
        usedlinks.append(new_links)
        count += 1
        percent = count / total
        print(len(arts),feed,percent)
    articles = [item for items in articles for item in items]
    usedlinks = [item for items in usedlinks for item in items]
    prev_articles = json.load(open(lang +'_arts1.txt'))
    prev_total = len(prev_articles)
    prev_articles.extend(articles)
    prevrsslinkfile = 'prev_' + lang + '_rsslinks.txt'
    prev_rsslinks = json.load(open(prevrsslinkfile))
    prev_rsslinks.extend(usedlinks)
    with open(prevrsslinkfile, 'w') as outfile:
        json.dump(prev_rsslinks, outfile)

    print('old arts: ' + str(prev_total))
    print('total arts: ' + str(len(prev_articles)))
    print('gained: ' + str(len(prev_articles) - prev_total))
    return prev_articles

def main():
    pass


if __name__ == '__main__':
    main()
