import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_boston, fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer

def truncated_svd(X):
    """
    The functions returns q, sigma, p and the normalized sum of squared
    distance from the origin.
    """
    q, s, p = np.linalg.svd(X)
    res = q, np.diag(s), p.T, (s / np.linalg.norm(s))**2
    return res

def plot_svd(X_new, features, p):
    """
    Plot transformed data and features on to the first two singular vectors
    
    Parameters
    ----------
    X_new : array
        Transformed data
    featurs : sequence of str
        Feature names
    p : array
        P matrix
    """
    fig, ax = plt.subplots(1, 2, subplot_kw=dict(aspect='equal'), 
                           gridspec_kw=dict(wspace=0.4), dpi=150)
    ax[0].scatter(X_new[:,0], X_new[:,1])
    ax[0].set_xlabel('SV1')
    ax[0].set_ylabel('SV2')

    for feature, vec in zip(features, p):
        ax[1].arrow(0, 0, vec[0], vec[1], width=0.01, ec='none', fc='r')
        ax[1].text(vec[0], vec[1], feature, ha='center', color='r', fontsize=5)
    ax[1].set_xlim(-1, 1)
    ax[1].set_ylim(-1, 1)
    ax[1].set_xlabel('SV1')
    ax[1].set_ylabel('SV2')

def project_svd(q, s, k):
    """
    The function returns the design matrix projected on to the
    first k singular vectors.
    """
    return q[:, :k].dot(s[:k, :k])

from sklearn.decomposition import PCA

pca = PCA()
X_new2 = pca.fit_transform(X)
fig, ax = plt.subplots(1, 1, subplot_kw=dict(aspect='equal'), dpi=150)
ax.scatter(X_new2[:,0], X_new2[:,1])
for feature, vec in zip(features, pca.components_.T):
    ax.arrow(0, 0, 100*vec[0], 100*vec[1], width=5, ec='none', fc='r')
    ax.text(130*vec[0], 130*vec[1], feature, ha='center', color='r')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2');

from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
def preprocess(document):
    """Accepts documents and returns only the necessary words."""
    wordnet_lemmatizer = WordNetLemmatizer()
    tokenizer = RegexpTokenizer(r'[a-z]+')
    stop_words = set(stopwords.words('english'))

    document = document.lower()  # Convert to lowercase
    words = tokenizer.tokenize(document)  # Tokenize
    words = [w for w in words if not w in stop_words]  # Removing stopwords

    # Lemmatizing
    for pos in [wordnet.NOUN, wordnet.VERB, wordnet.ADJ, wordnet.ADV]:
        words = [wordnet_lemmatizer.lemmatize(x, pos) for x in words]

    return " ".join(words)