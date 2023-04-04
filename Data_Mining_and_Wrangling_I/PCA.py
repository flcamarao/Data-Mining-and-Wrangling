import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.datasets import load_wine, fetch_20newsgroups, load_boston

def pca(X):
    """
    The function accepts a design matrix and returns
    the rotated design matrix.
    """
    A = X - X.mean(axis=0)
    cov = np.cov(A, rowvar=False, bias=True)
    e_val, e_vec = np.linalg.eig(cov)
    order = e_val.argsort()[::-1]
    e_val = e_val[order]
    w = e_vec[:, order]
    X_new = np.dot(A, w)
    variance_explained = e_val/sum(e_val)
    return X_new, w, variance_explained
