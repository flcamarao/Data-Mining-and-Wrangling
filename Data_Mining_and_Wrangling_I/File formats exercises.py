
import pandas as pd
import numpy as np
import csv
import json
from xml.etree import ElementTree as ET

def list_recipes(recipe_xml):
    """
    Returns the list of ingredients in recipe_xml.
    """

    root = ET.fromstring(recipe_xml)
    return [ingredient.text for ingredient in root.findall('ingredient')]

def catalog_sizes(catalog_xml):
    """
    Returns the unique catalog sizes in catalog_xml.
    """

    root = ET.fromstring(catalog_xml)
    return set([size.get('description') for size in root.findall('.//size')])

def read_fantasy(books_xml):
    """
    Returns a pandas dataframe with columns id, author, title, genre, price,
    publish_date and description from the books_xml
    and having fantasy as genre.
    """

    return pd.read_xml(books_xml, xpath='./book/genre[.="Fantasy"]/...',
                       parser='etree')

def dct2str(dct):
    """
    Converts a python dictionary to a JSON string object.
    """

    return json.dumps(dct)

def dct2file(dct):
    """
    Saves a dictionary into a JSON file called 'dict.json'.
    """

    with open('dct.json', 'w') as file:
        json.dump(dct, file)

def count_journals():
    """
    returns a journal count from the Allen Institute datasource.
    """
    df = pd.read_json(filepath,
                      lines=True)
    df = df.groupby('journal')['journal'].count().sort_values(ascending=False)
    return list(zip(df.index, df))

def business_labels():
    """
    Returns a pandas Series where the index is the businnes_id and the values
    are the set of labels posted for that businnes.
    """

    df = pd.read_json(filepath, lines=True)
    return df.groupby('business_id')['label'].apply(set)


def get_businesses():
    """
    Returns a dataframe cointaining details of a businnes in the Yelp Academic
    Dataset. The nested keys will be normalize with "json_normalize".
    """
    
    with open(filepath) as file:
        data = [json.loads(line) for line in file][:10000]
    return pd.json_normalize(data).set_index('business_id')

def pop_ncr():
    """
    Reads the data from NCR 2020 datasource and returns a pandas Dataframe
    with two coulmns "Province, City, Municipality, and Barangay" and
    "Total Population". Empty cells are dropped from the DataFrame.
    """

    df = pd.read_excel(filepath,
                       sheet_name='NCR by barangay',
                       usecols=[2, 3],
                       skiprows=4,
                       names=['Province, City, Municipality, and Barangay',
                              'Total Population'])
    return df.dropna()

def dump_airbnb_beds():
    """
    Reads the data from the zip file and returns an Excel file where each
    sheetname is the bed_type and the contents are host_location and price.
    """

    df = pd.read_csv(filepath,
                     compression='gzip',
                     usecols=['bed_type', 'host_location', 'price'])
    
    display(df)
    with pd.ExcelWriter('airbnb.xlsx') as newfile:
        for types in sorted(df.bed_type.unique()):
            df[df['bed_type'] == types].to_excel(newfile,
                                                 sheet_name=types,
                                                 index=False,
                                                 columns=['host_location',
                                                          'price'])

def age_counts():
    """
    Returs a Pandas Dataframe with index corresponding to the single-year age
    and columns with "Both Sexes", "Male", and "Female".
    """

    cols = ['Single-Year Age','Both Sexes', 'Male', 'Female']
    df1 = pd.read_excel(fp, sheet_name='T2',
                        skiprows=[0, 1, 3, 4, 5, 6],
                        skipfooter=6, usecols=cols)
    df2 = pd.read_excel(fp, sheet_name='T3',
                        skiprows=[0, 1, 3, 4, 5, 6],
                        skipfooter=3, usecols=cols)
    df3 = pd.merge(df1, df2, how="inner", on=['Single-Year Age'],
                   suffixes=(" (Total)", " (Household)"))
    return df3.set_index('Single-Year Age')

