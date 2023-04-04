import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from IPython.display import display, display_html

def label_encode(ord_values, value_mapping):
    """
    The function accepts a list of ordinal values and returns their label
    encoded values as list.
    """

    lst = [value_mapping[i] for i in ord_values]
    return lst

from sklearn.preprocessing import OneHotEncoder
def onehot_encode(cat_values):
    """
    The function accepts a list of categorical values and returns their
    one-hot encoded values as a pandas DataFrame.
    """

    test = np.reshape(cat_values, (-1, 1))
    enc = OneHotEncoder(handle_unknown='ignore')
    enc.fit(test)
    df = pd.DataFrame(enc.transform(test).toarray())
    df.columns = enc.categories_[0]
    if df.shape[1] == 2:
        return df.iloc[:, 1:2]
    else:
        return df

def vectorize_people(people, value_mappings):
    """
    The function accepts a list of people in the form of dicts and a dict of
    dicts corresponding to the mapping of ordinal values then returns
    a design matrix as pandas DataFrame and sorted by columns alphabetically.
    """

    df = pd.DataFrame(people)
    for i, o in value_mappings.items():
        df[i] = df[i].map(o)
    vect = pd.get_dummies(df, drop_first=True)
    return vect.reindex(sorted(vect.columns), axis=1)

def get_wine_df(data_wine):
    """
    The function accepts a bunch of objects and returns the
    design matrix as pandas DataFrame.
    """

    cols = data_wine['feature_names']
    return pd.DataFrame(data_wine['data'], columns=cols)

def to_bow(docs):
    """
    The function accepts a list of documents and returns a pandas DataFrame
    of their bag-of-words representation. Sort columns alphabetically.
    """

    docs = [doc.lower() for doc in docs]
    df = pd.DataFrame([Counter(doc.split()) for doc in docs])
    df.fillna(0, inplace=True)
    return df.reindex(sorted(df.columns), axis=1)

def lpnorm(vec1, vec2, p=2):
    """Compute the L_p-norm distance between vec1 and vec2

    If `vec1` and `vec2` are same-sized matrices, an ndarray of the L_p-norm 
    of corresponding rows will be returned instead.

    Parameters
    ----------
    vec1 : ndarray
        First vector
    vec2 : ndarray
        Second vector
    p : int or float, optional
        Order of L_p norm; the `p` in L_p norm

    Returns
    -------
    float
        L_p norm distance of `vec1` and `vec2`
    """

    if vec1.ndim == 1:
        return (np.sum(np.abs(vec1 - vec2)**p))**(1/p)
    else:
        return (np.sum(np.abs(vec1 - vec2)**p, axis=1)**(1/p))

def cossim(vec1, vec2):
    """Compute cosine similarity between vec1 and vec2

    If `vec1` and `vec2` are same-sized matrices, an ndarray of the cosine 
    similarity of corresponding rows will be returned instead.

    Parameters
    ----------
    vec1 : ndarray
        First vector
    vec2 : ndarray
        Second vector

    Returns
    -------
    float
        cosine similarity of `vec1` and `vec2`
    """

    if vec1.ndim == 1:
        return (np.dot(vec1, vec2) /
                (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    else:
        return (np.dot(vec1, vec2) /
                (np.linalg.norm(vec1, axis=1) * np.linalg.norm(vec2, axis=1)))

def dcos(vec1, vec2):
    """Compute cosine distance between vec1 and vec2

    If `vec1` and `vec2` are same-sized matrices, an ndarray of the cosine 
    distance of corresponding rows will be returned instead.

    Parameters
    ----------
    vec1 : ndarray
        First vector
    vec2 : ndarray
        Second vector

    Returns
    -------
    float
        cosine distance of `vec1` and `vec2`
    """

    distance = cossim(vec1, vec2)
    return 1 - cossim(vec1, vec2)

def nearest_k(query, objects, k, dist):
    """Return the indices to objects most similar to query

    Parameters
    ----------
    query : ndarray
        query object represented in the same form vector representation as the
        objects
    objects : ndarray
        vector-represented objects in the database; rows correspond to 
        objects, columns correspond to features
    k : int
        number of most similar objects to return
    dist : function
        accepts two ndarrays as parameters then returns their distance

    Returns
    -------
    ndarray
        Indices to the most similar objects in the database
    """

    return np.argsort([dist(query, obj) for obj in objects])[:k]

class Vectorizer:
    def __init__(self):
        self.index_word = {}
        self.word_index = {}

    def build_mappings(self, docs):
        """Initialize word-index mappings

        Parameter
        ---------
        docs : sequence of str
            Corpus to build mappings for
        """
        words = sorted(set(" ".join(docs).split()))
        self.index_word = {i: word for i, word in enumerate(words)}
        self.word_index = {
            word.lower(): i for i, word in self.index_word.items()}

    def vectorize(self, doc):
        """Return the BoW vector representation of doc

        Parameters
        ----------
        doc : str
            Text to compute the vector representation of

        Returns
        -------
        vec : ndarray
            BoW vector representation of doc
        """

        words = dict.fromkeys(self.word_index, 0)
        freq = Counter(doc.lower().split())
        for i in freq.keys():
            if i in words.keys():
                words[i] = freq[i]
        return pd.Series(words).sort_index().values.astype(float)