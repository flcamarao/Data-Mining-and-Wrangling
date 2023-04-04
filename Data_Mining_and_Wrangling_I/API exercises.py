import requests
import pandas as pd
from datetime import date
from urllib.parse import urljoin, urlencode

def establishment_info(establishment_id):
    """
    The function returns the name, city and region of an establishment with
    with establishment_id as a dictory from a url.
    """

    response = (requests
                .get(url
                     f'/rest/establishment/{establishment_id}',
                     )
                .json()
                )
    del response["establishment_id"]
    return response

from datetime import datetime

def check_in(establishment_id, year, month, day, hour, minute, seconds):
    """Check in at an establishment given by `establishment_id`

    Parameters
    ----------
    establishment_id: int
        Establishment ID
    year: int
        Check-in year
    month: int
        Check-in month
    day: int
        Check-in day
    hour: int
        Check-in hour from 0 to 23
    minute: int
        Check-in minute
    seconds: int
        Check-in seconds

    Returns
    -------
    response: dict
        API response

    Note
    ----
    Date and time should be in UTC.
    """

    dt = datetime(year, month, day, hour, minute, seconds)
    response = (requests
                .post(url
                      'rest/visit/check-in',
                      json={
                          "establishment_id": establishment_id,
                          "checkin_ts": dt.isoformat()
                      }
                      )
                .json()
                )
    return response

def visits(establishment_id, start_date, end_date):
    """Return the number of visits in `establishment_id` for each day

    Parameters
    ----------
    establishment_id: int
        Establishment ID
    start_date: datetime.date
        Start date
    end_date: datetime.date
        End date (inclusive)

    Returns
    -------
    date_visits: dict
        Dictionary with date (in YYYY-MM-DD format) as key and number of
        visits as value
    """

    date_range = pd.date_range(start_date, end_date)
    visits = {}
    for i in date_range:
        response = (requests
                    .get(url
                         f'rest/establishment/{establishment_id}'
                         f'/visits?date={i.date()}',
                         )
                    .json()
                    )['visits']
        visits[str(i.date())] = int(response)
    return visits

def pageprops(title):
    """The function returns the properties of a page title as a dictionary"""

    response = (requests
                .get(
                    'https://en.wikipedia.org/w/api.php',
                    params={
                        'action': 'query',
                        'prop': 'pageprops',
                        'titles': title,
                        'format': 'json'
                    }
                )
                .json())
    return list(response['query']['pages'].values())[0]['pageprops']

def contributors(revid):
    """
    The function returns the userid and name of contributors that contributed
    to a page as of given revid as a pandas data frame sorted by userid.
    """
    contributors = []
    params = {
        'action': 'query',
        'prop': 'revisions',
        'revids': revid,
        'format': 'json',
    }
    response = (requests
                    .get(
                        'https://en.wikipedia.org/w/api.php',
                        params=params
                    )
                    .json())
    title = list(response['query']['pages'].values())[0]['title']
    
    params1 = {
        'action': 'query',
        'prop': 'revisions',
        'titles': title,
        'rvprop': 'userid|user',
        'rvstart': '2022-10-24T00:00:00Z',
        'rvlimit': 'max',
        'format': 'json',
    }
    while True:
        response1 = (requests
                    .get(
                        'https://en.wikipedia.org/w/api.php',
                        params=params1
                    )
                    .json())
        contributors.extend(
            list(response1['query']['pages'].values())[0]['revisions'])
        if 'continue' in response1:
            params1.update(response1['continue'])
        else:
            break
    df = pd.DataFrame(contributors)[['userid', 'user']]
    df = df.rename(columns={'user': 'name'}).dropna().drop_duplicates()
    df = df[df['userid'] != 0].sort_values('userid').astype({'userid': 'int'})
    return df

def revisions(title):
    """
    The function returns the revisions before 2007 (UTC) of a given page
    title as a pandas data frame with columns revid, user, timestamp and sha1.
    The dataframe is sorted by increasing revid.
    """

    revisions = []
    params = {
        'action': 'query',
        'prop': 'revisions',
        'titles': title,
        'rvprop': 'ids|user|timestamp|sha1',
        'rvstart': '2007-01-01T00:00:00Z',
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
        revisions.extend(list(response['query']['pages'].values())[0]['revisions'])
        if 'continue' in response:
            params.update(response['continue'])
        else:
            break
    df = pd.DataFrame(revisions).drop(columns=['parentid', 'anon'])
    return df.sort_values('revid')

import time
def nearby_drugs(api_key):
    """
    The function returns the name and vicinity of the 50 closest nearby places
    with a place name, address, or category of establishments of drug from
    coordinates (14.552665405264284,121.01868822115196) as a pandas data frame
    using the Google Places API and the provided api_key.
    """
    drugs = []
    params = {
        'location': '14.552665405264284,121.01868822115196',
        'keyword': 'drug',
        'rankby': 'distance',
        'key': api_key
    }
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

    for i in range(3):
        response = (requests
                    .get(url,
                         params=params)
                    .json())
        drugs.extend(response['results'])
        if 'next_page_token' in response:
            params.update({'pagetoken': response['next_page_token']})
            time.sleep(5)
        else:
            break
    df = pd.DataFrame(drugs)
    return df

def account_info(username, bearer_token):
    """
    The function returns the id, username, name, location and created_at of
    a Twitter username given a bearer_token to access the Twitter API.
    """

    response = (requests
                .get(f'https://api.twitter.com/2/users/by/username/{username}',
                     headers={
                         'Authorization': f'Bearer {bearer_token}'},
                     params={
                         "user.fields": "location,created_at"
                     }
                     )
                .json()['data']
                )
    return response

def tweets_2021(user_id, bearer_token):
    """
    The function returns all of the tweets of user_id in 2021 as a pandas 
    data frame with columns id, created_at and text sorted by created_at.
    """

    tweets = []
    param = {
        'tweet.fields': 'created_at',
        'start_time': '2021-01-01T00:00:00Z',
        'end_time': '2022-01-01T00:00:00Z',
    }

    while True:
        response = (requests
                    .get(f'https://api.twitter.com/2/users/{user_id}/tweets',
                         headers={'Authorization': f'Bearer {bearer_token}'},
                         params=param
                         )
                    .json()
                    )
        print(response['data'])
        tweets.extend(response['data'])
        if 'next_token' in response['meta']:
            param.update({'pagination_token': response['meta']['next_token']})
        else:
            break
    df = pd.DataFrame(tweets).drop(columns=['edit_history_tweet_ids'])
    return df[['id', 'created_at', 'text']].sort_values('created_at')

def crawl_page():
    """
    The function crawls the API responses from a url and returns the text
    of the last API page.
    """

    messages = []
    params = {}
    while True:
        response = (requests
                    .get(url
                         '?fixed-token=gniparcs-bew',
                         params=params
                         )
                    .json()
                    )
        messages.append(response)
        if 'continue' in response:
            params.update(response)
        else:
            break
    return messages[-1]['message']
