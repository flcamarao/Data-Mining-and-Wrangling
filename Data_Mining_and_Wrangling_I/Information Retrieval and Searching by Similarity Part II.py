import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_wine, fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer

def get_confusion(actual, results, all_labels):
    """
    The function accepts the label of the correct class and returns the
    results as indices to the objects and all lables into a
    confusion matrix as a pandas DataFrame.
    """

    TP = sum([1 for r in results if all_labels[r] == actual])
    FP = sum([1 for r in results if all_labels[r] != actual])
    FN = sum([1 for i, l in enumerate(all_labels)
             if i not in results and l == actual])
    TN = sum([1 for i, l in enumerate(all_labels)
             if i not in results and l != actual])
    return pd.DataFrame([[TP, FP],
                         [FN, TN]],
                        columns=['relevant', 'irrelevant'],
                        index=['relevant', 'irrelevant'])

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
    most_similar : ndarray
        Indices to the most similar objects in the database
    """
    return np.argsort([dist(query, obj) for obj in objects])[:k]

def precision(confusion):
    """
    The function accepts a confusion matrix and returns the precision.
    """

    TP = confusion.loc['relevant', 'relevant']
    FP = confusion.loc['relevant', 'irrelevant']
    return TP / (TP + FP)

def recall(confusion):
    """
    The function accepts a confusion matrix and returns the call.
    """

    TP = confusion.loc['relevant', 'relevant']
    FN = confusion.loc['irrelevant', 'relevant']
    return TP / (TP + FN)

def f_measure(precision, recall, beta=1):
    """
    The function accepts the precision, recall and beta
    and returns the F-measure.
    """

    left = 1 + beta**2
    right = (precision * recall) / ((beta**2 * precision) + recall)
    return left * right

def pr_curve(query, objects, dist, actual, all_labels):
    all_labels = np.asarray(all_labels)
    results = nearest_k(query, objects, len(all_labels), dist)
    rs = (all_labels[results] == actual).cumsum()
    N = (all_labels == actual).sum()
    precisions = rs / np.arange(1, len(rs)+1)
    recalls = rs / N
    recalls = [0] + recalls.tolist()
    precisions = [1] + precisions.tolist()

    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.step(recalls, precisions, where='post')
    ax.fill_between(recalls, precisions, step='post', alpha=0.8)
    ax.set_xlim(0,1)
    ax.set_ylim(0,1)
    ax.set_xlabel('recall')
    ax.set_ylabel('precision');
    return ax

def auc_pr(query, objects, dist, actual, all_labels):
    from scipy.integrate import trapz
    all_labels = np.asarray(all_labels)
    results = nearest_k(query, objects, len(all_labels), dist)
    rs = (all_labels[results] == actual).cumsum()
    N = (all_labels == actual).sum()
    precisions = rs / np.arange(1, len(rs)+1)
    recalls = rs / N
    recalls = [0] + recalls.tolist()
    precisions = [1] + precisions.tolist()
    return trapz(precisions, recalls)

class Standardizer:
    def __init__(self, df):
        """Store the mean and standard deviation of each column"""
        self.mean = df.mean()
        self.std = df.std()

    def standardize(self, values):
        """Standardize values per column"""
        return (values - self.mean) / self.std

standardizer = Standardizer(df_wine)
ax = pr_curve(standardizer.standardize(df_wine.iloc[0]),
              standardizer.standardize(df_wine).to_numpy(),
              euclidean, target_wine[0],
              target_wine)
ax.set_title('First wine as query')
ax.text(0.65, 0.8,
        'AUC={:0.2f}'.format(
            auc_pr(standardizer.standardize(df_wine.iloc[0]),
                   standardizer.standardize(df_wine).to_numpy(),
                   euclidean, target_wine[0], 
                   target_wine)),
         fontsize=12);

class MinMax:
    def __init__(self, df):
        """Store the minimum and maximum values of each column"""
        self.min = df.min()
        self.max = df.max()

    def minmax(self, values):
        """Standard values per column"""
        return (values - self.min) / (self.max - self.min)

class TFIDF:
    def __init__(self, df):
        """Store the idf of each column"""
        n_docs = df.shape[0]
        count = df[df > 0].count()
        self.idf = np.log(n_docs / count)

    def tfidf(self, values):
        """Standard values per column"""
        return self.idf * values

def normalize1(values):
    """
    The function accepts values and normalizes by their L1-norm.
    """

    try:
        return values.divide(values.sum(axis=1), axis=0)
    except:
        return np.divide(values, values.sum())

def normalize2(values):
    """
    The function accepts values and normalizes by their L2-norm.
    """

    try:
        return values.divide(np.sqrt((values**2).sum(axis=1)), axis=0)
    except:
        return np.divide(values, np.sqrt((values**2).sum()))
