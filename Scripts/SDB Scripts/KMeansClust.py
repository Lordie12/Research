# -*- coding: utf-8 -*-
"""
Created on Tue Jan  6 19:25:10 2015

@author: Lanfear
"""
import csv
from collections import OrderedDict
# from pylab import plot, show
from numpy import vstack, newaxis
from numpy.random import rand
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist

TrainPath = ('/Users/Lanfear/Desktop/Research/CLuuData/'
             'CLuuResults/FinalTrainSet1stDim.csv')
select_rand_feature = True
n_clust = 6


def parse_csv(path):
    '''
    Parses a csv file and returns a dictionary of movies
    '''

    movierawdata = list(csv.reader(open(path, 'rU'), dialect=csv.excel_tab,
                        delimiter=','))[1:]

    tempDict = OrderedDict()
    for row in movierawdata:
        tempDict[row[0]] = {}
        tempDict[row[0]]['Year'] = int(row[1])
        tempDict[row[0]]['Genre'] = str(row[2])
        tempDict[row[0]]['AROI'] = float(row[6])
        tempDict[row[0]]['Features'] = row[8:]
    return tempDict


Trainset = parse_csv(TrainPath)


def create_rand_feat_index():
    num_feat = int(rand() * 100) % 44
    feat_index = []
    for i in range(num_feat):
        rand_num = (int(rand() * 100) % 44)

        while rand_num in feat_index:
            rand_num = (int(rand() * 100) % 44)
        feat_index.append(rand_num)

    return sorted(feat_index)


# def create_rand_feat(Trainset):
#     feat_index = []
#     while len(feat_index) == 0:
#         feat_index = create_rand_feat_index()
#     print feat_index
#     return [(d, list(map(float, [Trainset[d]['Features'][i]
#             for i in feat_index]))) for d in Trainset]

# features = create_rand_feat(Trainset)
feat_index = [0, 1, 4, 6, 9, 10, 17, 22, 23, 27, 30, 32, 36, 37, 40, 41, 42]


def create_rand_feat(Trainset, feat_index):
    '''
    This is where the features are trimmed according
    to the randomly generated feature index list
    '''
    return [list(map(float, [Trainset[d]['Features'][i]
            for i in feat_index])) for d in Trainset]

features = create_rand_feat(Trainset, feat_index)
# features = [(d, list(map(float, Trainset[d]['Features']))) for d in Trainset]

# data generation
data = vstack([row for row in features])

#
kmeans_model = KMeans(n_clusters=n_clust, random_state=1, n_jobs=-1).fit(data)
labels = kmeans_model.labels_
centroids = kmeans_model.cluster_centers_

# computing K-Means with K = num_clust clusters
# centroids, _ = kmeans(data, num_clust)
# assign each sample to a cluster
# idx, _ = vq(data, centroids)
# print idx

mList = []
for i in range(n_clust):
    mList.append([])

mInfo = [(k, Trainset[k]['Genre']) for k in Trainset.keys()]

# Create the list of movies with genres, grouped into their classified groups
for index in range(len(labels)):
    mList[labels[index]].append(mInfo[index][1])

print str(n_clust) + ' Clusters'
for k in mList:
    print k, '\n'


def minkowski(X, Y):
    '''
    Minkowski distance, a.k.a. p-norm of 2-vectors
    is defined as (sigma (i=1 to n) (|xi - yi) ^ p) ^ (1/p)
    '''
    return cdist(X[newaxis, :], Y[newaxis, :], 'minkowski', p=len(X))


# print silhouette_score(data, labels, metric=minkowski)
print "Silhouette Score - " + str(silhouette_score(data, labels, metric='euclidean'))

# some plotting using numpy's logical indexing
# plot(data[idx == 0, 0], data[idx == 0, 1], 'ob',
#      data[idx == 1, 0], data[idx == 1, 1], 'or',
#      data[idx == 2, 0], data[idx == 2, 1], 'oy',)
# plot(centroids[:, 0], centroids[:, 1], 'sg', markersize=8)
# show()
