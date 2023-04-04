import json
import re
import sqlite3

import pandas as pd
import numpy as np

from xml.etree import ElementTree

def get_purchase_order_xpath():
    xpath = './PurchaseOrder/Address[@Type="Shipping"]/Country[.="USA"]/../..'
    return xpath

def has_comments_xpath():
    xpath = './PurchaseOrder/Items/Item/Comment/../../..'
    return xpath

from glob import glob
def plot_counts():
    df = (pd.concat([pd.read_json(f_name, lines=True)
                     for f_name in sorted(glob('sensor/*.json'))]))
    df1 = pd.json_normalize(df['data'], max_level = 1)
    df2 = pd.json_normalize(df1['viewer.male']).sum(axis = 1)
    df3 = pd.json_normalize(df1['viewer.female']).sum(axis = 1)
    pd_list = (df2+df3).tolist()
    path = 'sensor/*.json'
    files= glob(path)
    filename = []
    for file in sorted(files):
        filename.append(file.split("/")[1].split(".")[0])
    return pd.Series(dict(zip(filename, pd_list)))

import os.path
def get_age_population(path, min_age, max_age, gender='M/F'):
    """Return the total population of an age based on the supplied data
    
    Parameters
    ----------
    path : filepath
        Path to a census file
    min_age : int from 0 to 80, inclusive
        Lower bound of the age range
    max_age : int from 0 to 80, inclusive
        Upper bound of the age range
    gender : 'M', 'F' or 'M/F', optional
        Gender to consider
        
    Returns
    -------
    pop_count : int or None
        Total population of age range or `None` if the age range is not 
        allowed or the file cannot be located
    """
    if (min_age < 0 or min_age > 80 or min_age > max_age 
        or max_age < 0 or max_age > 80):
        return None
    if not os.path.isfile(path):
        return None
    df = pd.read_excel(
    path,
    skiprows=[0,1,3,4,5,6], sheet_name='T2', usecols=[0, 1, 2, 3],
    skipfooter=3
    )
    df.loc[df['Single-Year Age'] == "Under  1"] = 0
    df.loc[df['Single-Year Age'] == "80 years and over"] = 80
    df = (df[(df['Single-Year Age'] >= min_age) &
             (df['Single-Year Age'] <= max_age)])
    if gender == "M/F":
        return int(df['Both Sexes'].sum())
    elif gender == "M":
        return int(df['Male'].sum())
    elif gender == "F":
        return int(df['Female'].sum())

def get_prev_word(inp, search_term):
    regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
    if(regex.search(search_term) == None):
        if re.findall(rf'(\.)\s{search_term}?\b', inp):
            return []
        else:
            return re.findall(rf'\w+(?=[",;\'-\*]?\s{search_term}?\b)', inp)
    else:
        search_term =  re.sub("(.)", r"\\\1", search_term)
        return re.findall(rf'(\w+)\s{search_term}', inp)

def repeating_words(text):
    result =  (re.findall(r'((\b\w+\b)[ ,-]\w+[ ,-]\w+[-, ]+\w+[-, ]+\b\2\b|'
                          r'(\b\w+\b)[ ,-]\w+[ ,-]\b\3\b|'
                          r'(\b\w+\b)[ ,-]\b\4\b)', text, re.IGNORECASE))
    value = []
    for item in result:
        value.append(item[0])
    return value

def red_stuff():
    df = pd.read_csv(filepath)
    df1 = (df[df['product_name']
              .str.
              contains(r'[R]ed\s[a-zA-Z0-9\.]+\s[a-zA-Z0-9\.]+|'
                       '[R]ed\s[a-zA-Z0-9\.]+$',regex=True)])
    df1 = df1.set_index('product_id')
    return (df1['product_name']
            .str.extract(r'(\b[R]ed \w+ \w+|\b[R]ed \w+)').squeeze())

def has_keyword():
    conn = sqlite3.connect(filepath)
#     pd.read_sql_query('PRAGMA table_list', conn)
    pd.read_sql_query('PRAGMA table_info(movies)', conn)
    pd.read_sql_query('PRAGMA table_list(movies_keywords)', conn)
    pd.read_sql_query('PRAGMA table_list(keywords)', conn)
    sql = """
        SELECT m.title
        FROM movies as m
            LEFT JOIN movies_keywords as mk
                ON mk.idmovies = m.idmovies
            LEFT JOIN keywords as k
                on mk.idkeywords = k.idkeywords
        WHERE
            k.keyword = ?
        GROUP BY 1
        ORDER BY 1
    """
    return sql, conn
def aka_phils():
    conn = sqlite3.connect(filepath)
#     pd.read_sql_query('PRAGMA table_list', conn)
    pd.read_sql_query('PRAGMA table_info(movies)', conn)
    pd.read_sql_query('PRAGMA table_info(aka_titles)', conn)
    sql = """
        SELECT ak.year as year, count(ak.year) as title
        FROM movies as m
            LEFT JOIN aka_titles as ak
                ON m.idmovies = ak.idmovies
        WHERE ak.location = 'Philippines: English title'
        GROUP BY ak.year, ak.location
        HAVING count(ak.year) >= 10
        ORDER BY title DESC
    """
    return sql, conn

def convert_twitter():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE twitter (
        id INT,
        text TEXT,
        is_quote_status BOOLEAN,
        favorite_count INT,
        created_at TEXT,
        timestamp_ms INT
        )""")
    df = pd.read_json('./data_twitter_sample.json',
                      lines=True, convert_dates=False)
    df = df[['id', 'text', 'is_quote_status',
             'favorite_count', 'created_at', 'timestamp_ms']]
    df.to_sql('twitter', conn, if_exists='append', index=False)
    return conn