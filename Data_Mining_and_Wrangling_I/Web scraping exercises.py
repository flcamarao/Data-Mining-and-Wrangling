import datetime
import os
import requests
import bs4
import numpy as np
import pandas as pd

def summarize_items():
    """
    The function reads a url and returns a pandas data frame corresponding
    to the OASIS Item Summary table on the page.
    """

    return pd.read_html(url, header=0)[0]

def item_values():
    """
    The function reads a url and return a pandas datafram corresponding to the
    OASIS Item Values table on the page.
    """

    return pd.read_html(url, header=1)[2]

from urllib.parse import urljoin
def all_item_values():
    """
    The function returns a pandas data frame of all item values with columns
    Item, Value, LOINC and Text from a url.
    """

    response = requests.get(url)
    html = bs4.BeautifulSoup(response.text)
    df = pd.DataFrame()
    for i in html.select('a[href]'):
        url = urljoin(url, i.get('href'))
        df2 = pd.read_html(url, header=1)[2]
        df2.insert(loc=0, column='Item', value=i.text)
        df = pd.concat([df, df2], ignore_index=True)
    return df


def all_item_edits():
    """
    The function returns the Edit ID, Edit Type, Severity and Edit Text of
    all OASIS Edits in a url and sort by numerically increasing Edit ID.
    """

    response = requests.get(url)
    html = bs4.BeautifulSoup(response.text)
    li_url = html.find_all('a', target='VIEW_WINDOW', href=True)
    df = pd.read_html(urljoin(url, li_url[0]['href']), header=0)[0]
    df['Edit Text'] = [pd.read_html(
        urljoin(url, i['href']), header=0)[1].iloc[4, 1] for i in li_url[1:]]
    return df.rename(columns={'Type': 'Edit Type'})

def article_info(url):
    """
    The function returns the title, author and published timestamp of a
    Rappler article given by url as a dictionary.
    """

    response = requests.get(url)
    html = bs4.BeautifulSoup(response.text)
    art_info_dict = {'title': html.select_one('h1.post-single__title').text,
                'author': html.select_one('div.post-single__authors').text,
                'published': html.select_one('time.entry-date').text}
    return art_info_dict

def latest_news():
    """
    The function returns the title, category and timestamp of the latest news
    at a url as a dictionary.
    """

    response = requests.get(url)
    html = bs4.BeautifulSoup(response.text)
    html = html.find(class_='latest-stories')
    result = {
        'title': html.find(class_='post-card__title').text.strip(),
        'category': html.find(class_='post-card__category').text.strip(),
        'timestamp': datetime.datetime.fromisoformat(
            html.find(class_="post-card__timeago")['datetime']
        )
    }
    return result

def get_category_posts(category):
    """
    The function returns the titles of posts under the case-insensitive
    category given by category in a url.
    """

    resp = requests.get(url)
    html_doc = resp.text
    soup = bs4.BeautifulSoup(html_doc)
    titles = []
    for i in soup.select('div.post-card__more-secondary-story > a ~ h3'):
        if (i.parent.select_one('a').text.strip().lower() == 
            category.lower()):
            titles.append(i.text.strip())
    return titles

def subsection_posts(url):
    """
    The function returns the title and timestamp of all posts under a
    subsection given by url as a pandas data frame.
    """

    soup = bs4.BeautifulSoup(requests.get(url).content)
    titles = ([i.get_text().strip()
               for i in
               soup.select('div.archive-article__content > h2 > a')])
    timestamp = ([i.get_text().strip()
                  for i in
                  soup.select('div.archive-article__content > h2 ~ time')])
    return pd.DataFrame({'title': titles, 'timestamp': timestamp})

def subsection_authors(url):
    """
    The function return the title and author of all posts under a subsection
    given by url as a pandas data frame sorted by title.
    """

    proxies = url
    soup = bs4.BeautifulSoup(requests.get(url, proxies=proxies).content)
    titles = ([i.get_text().strip() for i
               in soup.select('div.archive-article__content > h2 > a')])
    urls = [url_.get('href') for url_ in
            soup.select('div.archive-article__content > h2 > a')]
    authors = []
    for url2 in urls:
        soup2 = bs4.BeautifulSoup(requests.get(url2, proxies=proxies).content)
        authors.append(soup2.select_one('.post-single__authors').text)

    df = pd.DataFrame({'title': titles,
                       'author': authors})
    return df.sort_values(by='title')

import re
from urllib.parse import urlparse
def download_images(url):
    """
    The function will download to a directory named images all post images
    in the subsection given by url.
    """

    response = requests.get(url)
    html = bs4.BeautifulSoup(response.text)
    images = html.findAll('img')
    pics = []
    if not os.path.exists('images'):
        os.makedirs('images')
    for image in images[1:]:
        link = image['src']
        o = urlparse(link)
        print(link)
        print(urlparse(link).path)
        img_name = os.path.basename(urlparse(link).path)
        
        print(img_name)
        file = re.findall(r'.*(?=\?resize)', image['src'])[0].split('/')[6]
        with open('./images/'+file, 'wb') as f:
            response = (requests.get(image['src']))
            f.write(response.content)
