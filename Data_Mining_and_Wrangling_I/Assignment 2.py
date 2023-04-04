import json
import sqlite3
import re
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote

def get_continent_urls():
    """
    The function returns a dictionary with continent name as key and
    absolute url to that OAV page as value.
    """

    response = (requests.get(url))
    soup = BeautifulSoup(response.content, "html.parser")
    continent = {}
    for link in soup.find_all('a', limit=4):
        continent[link.get_text()] = urljoin(url, link.get('href'))
    return continent

def get_fsp_urls(continent):
    """
    The function returns a dictionary with foreign service posts in that
    continent as key and the list of urls to the precint JSON files as values.
    """

    response = (requests.get(url))
    soup = BeautifulSoup(response.content, "html.parser")
    for link in soup.find_all('a', limit=4):
        if continent in link.get('href'):
            new_url = urljoin(url, link.get('href'))
    response = (requests.get(new_url))
    soup = BeautifulSoup(response.content, "html.parser")
    fsp_urls = {}
    for link in soup.find_all('a')[4:]:
        if fsp_urls.get(link.get_text().split('-')[0].strip()) == None:
            fsp_urls[link.get_text().split('-')[0].strip()] = list()
        fsp_urls[link.get_text().split('-')[0].strip()
                 ].append(urljoin(url, link.get('href')))
    return fsp_urls

def senator_votes(continent, fsp):
    """
    The function returns a dictionary with the candidate name as key and
    the total votes received in the given continent and fsp as values.
    """

    response = (requests.get(url))
    soup = BeautifulSoup(response.content, "html.parser")
    for link in soup.find_all('a', limit=4):
        if continent in link:
            new_url = urljoin(url, link.get('href'))
    new_response = (requests.get(new_url))
    soup = BeautifulSoup(new_response.content, "html.parser")
    sv = {}
    for link in soup.find_all('a'):
        if fsp in link.get_text():
            new_url = urljoin(url, link.get('href'))
            new_response = (requests.get(new_url).json())
            for i in range(len(new_response['results'])):
                if sv.get(new_response['results'][i]['bName']) == None:
                    sv[new_response['results'][i]['bName']] = list()
                sv[new_response['results'][i]['bName']].append(
                    int(new_response['results'][i]['votes']))
    for i in sv:
        sv[i] = sum(sv[i])
    return sv

def latest_stories():
    """
    The function returns the category, title and published timestamp of the
    latest stories in a url as a pandas data frame sorted by order of
    appearance on the webpage.
    """

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    stories = pd.DataFrame(columns=['category'])
    for i, data in enumerate(soup.select('div .swiper-slide > #tr_boxs3')):
        stories.loc[i, 'category'] = data.select('h6')[0].text.upper()
        stories.loc[i, 'title'] = data.select('h2')[0].text
        stories.loc[i, 'published'] = data.select('h6')[1].text
    return stories

def category_posts(topic):
    """
    The function returns the title and link to posts under the topic box in
    a url as a pandas data frame storted by order of apperance on the
    webpage.
    """

    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    info = f"div[data-tb-region='Channel Box - {topic.title()}']"
    more_info = soup.select_one(info)
    result = [{'title': a.get_text(), 'link': a['href']}
              for a in more_info.select('h3>a')]
    return pd.DataFrame(result)

def get_books():
    """
    The function returns a list of tuples with the book title as the first
    element and paperback selling price as the second element for all the
    books in data_warngling.html. Sort them in order of appearance.
    """

    response = ''
    t_list = []
    p_list = []
    html_file = 'data_wrangling.html'
    t = open(html_file, "r")
    for v in t.readlines():
        response += v
    soup = BeautifulSoup(response)
    for i in range(len(soup.select('div[data-index]'))):
        t_list.append([e.text.strip()
                           for e in soup.select(
                               f'div[data-index="{i}"] h2 > a')][0])
        s_soup = ([e.parent.parent.parent.parent.parent.parent
                    for e in soup.select(f'div[data-index="{i}"] h2 > a')][0])
        p_raw = ([e.text.strip()
                      for e in s_soup.select(
                          'div.a-row a.a-size-base span')])
        if len(p_raw) == 0:
            p_list.append(None)
        elif 'to buy' in p_raw:
            p_list.append(p_raw[9])
        else:
            p_list.append(p_raw[1])
    return [(t, p) for t, p in list(zip(t_list, p_list))]

def get_revisions_timeseries():
    """
    The function returns a pandas Series with index eqial to months in
    YYYY-MM format and values corresponding to the number of revisions made
    in the English Wikipedia article Data Science.
    Sorted by chronological order.
    """

    revs = []
    params = {
        'action': 'query',
        'prop': 'revisions',
        'titles': 'Data science',
        'rvstart': '2022-10-01T00:00:00Z',
        'rvprop': 'timestamp',
        'rvlimit': 'max',
        'format': 'json',
    }
    while True:
        response = (requests
                    .get(
                        'https://en.wikipedia.org/w/api.php',
                        params=params
                    )
                    .json())
        revs.extend(
            list(response['query']['pages'].values())[0]['revisions'])
        if 'continue' in response:
            params.update(response['continue'])
        else:
            break
    df = pd.DataFrame(revs)
    return df.groupby(df.timestamp.str[0:7]).size()

def get_foobar_link_revs_asof():
    """
    The function returns the list of the revision ID, as of 1 September 2022
    UTC, of each linked page in revision id 1114361016 of the
    English Wikipedia.
    """

    sept_date = datetime(2022, 9, 1)
    params = {
        'action': 'query',
        'revids': '1114361016',
        'prop': 'links',
        'pllimit': 'max',
        'format': 'json'
    }
    response = (requests
                .get(
                    'https://en.wikipedia.org/w/api.php',
                    params=params
                )
                .json())
    title = list(response['query']['pages'].values())[0]['links']
    rev_ids = []
    for i in title:
        if i['ns'] == 0:
            new_title = i['title']
            params = {
                'action': 'query',
                'titles': new_title,
                'prop': 'revisions',
                'rvlimit': 'max',
                'format': 'json'
            }
            response = (requests
                        .get(
                            'https://en.wikipedia.org/w/api.php',
                            params=params
                        )
                        .json())
            my_ls = list(response['query']['pages'].values())[0]['revisions']
            for i in my_ls:
                new_date = pd.to_datetime(
                    i['timestamp'], format="%Y-%m-%dT%H:%M:%SZ")
                if new_date <= sept_date:
                    rev_ids.append(i['revid'])
                    break
    return sorted(rev_ids)

def followed_accounts(username, bearer_token):
    """
    The function returns the id, username, name, location and created_at of
    the Twitter accounts followed by the given username and bearer_token
    as pandas data frame sorted by id.
    """

    headers = {'Authorization': f'Bearer {bearer_token}'}
    url = f'https://api.twitter.com/2/users/by/username/{username}'
    params = {'user.fields': 'id'}
    response = (requests.get(url, headers=headers, params=params).json())
    userid = response['data']['id']
    url = f'https://api.twitter.com/2/users/{userid}/following'
    params = {'max_results': 1000,
              'user.fields': 'id,username,name,location,created_at'
              }
    resp = (requests.get(url, headers=headers, params=params).json())
    df = pd.DataFrame(resp['data']).astype({'id': 'int'}).sort_values('id')
    return df[['id', 'username', 'name', 'location', 'created_at']]

def user_videos(channel_id, api_key):
    """
    The functions returns the video_id, title and publish_time of videos on
    the given YouTube channel_id as a pandas data frame sorted
    publish_time.
    """

    videos = []
    params = {
        'part': 'id,snippet',
        'type': 'video',
        'channelId': channel_id,
        'publishedBefore': '2021-01-01T00:00:00Z',
        'publishedAfter': '2020-01-01T00:00:00Z',
        'order': 'date',
        'key': api_key,
        'maxResults': 50
    }
    while True:
        response = (requests
                    .get(
                        'https://www.googleapis.com/youtube/v3/search',
                        params=params
                    )
                    .json())
        videos.extend(response['items'])
        if 'nextPageToken' in response:
            params.update({'pageToken': response['nextPageToken']})
        else:
            break
    video_id = [i['id'].get('videoId') for i in videos]
    title = [i['snippet'].get('title') for i in videos]
    publish_time = [i['snippet'].get('publishedAt') for i in videos]
    df = (pd.DataFrame(
        {'video_id': video_id, 'title': title, 'publish_time': publish_time})
        .sort_values(by='publish_time', ignore_index=True))
    return df


