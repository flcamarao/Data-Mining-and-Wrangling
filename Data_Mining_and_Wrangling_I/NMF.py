
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_boston


from sklearn.decomposition import NMF

nmf = NMF()
U = nmf.fit_transform(X)
V = nmf.components_.T

from sklearn.decomposition import PCA

pca = PCA(2)
plt.scatter(*pca.fit_transform(X).T, c=U.argmax(axis=1), cmap='Set1')
plt.xlabel('PC1')
plt.ylabel('PC2');

from sklearn.cluster import KMeans

kmeans = KMeans()
plt.scatter(*pca.fit_transform(X).T, c=kmeans.fit_predict(U), cmap='Set1')
plt.xlabel('PC1')
plt.ylabel('PC2');

pca = PCA(2)
plt.scatter(*pca.fit_transform(X).T, c=U.argmax(axis=1), cmap='Set1')
plt.xlabel('PC1')
plt.ylabel('PC2');

kmeans = KMeans()
plt.scatter(*pca.fit_transform(X).T, c=kmeans.fit_predict(U), cmap='Set1')
plt.xlabel('PC1')
plt.ylabel('PC2');
