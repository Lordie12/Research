# -*- coding: utf-8 -*-
"""
Created on Fri Nov  7 11:14:15 2014

@author: Lanfear
"""

import csv
import json
import math as M
import numpy as NP
import community as C
import itertools as IT
import networkx as NX

from collections import OrderedDict as OD
from sklearn.metrics.pairwise import pairwise_distances

movie_data_url = ('/Users/Lanfear/Desktop/Research/CLuuData/'
                  'TimeWindowResults/moviewindow')
cl_movie_url = ('/Users/Lanfear/Desktop/Research/CLuuData/'
                'CLuuScriptsGeneData/moviegenes.txt')
res_url = '/Users/Lanfear/Desktop/Research/CLuuData/Results/'

start_year = 2000
end_year = 2010


def percentile(N, P):
    """
    Find the percentile of a list of values

    @parameter N - A list of values.  N must be sorted.
    @parameter P - A float value from 0.0 to 1.0

    @return - The percentile of the values.
    """
    n = int(round(P * len(N) + 0.5))
    return n-1


def fill_Graph(genedict, count, gtoidict, itogdict):
    G = NX.Graph()
    adj = NP.zeros((count, count), dtype=int)

    for movie in genedict.keys():
        for gene1 in genedict[movie]['Genes']:
            for gene2 in genedict[movie]['Genes']:
                # Create co-occurrence network
                gene1 = str(gene1).lower()
                gene2 = str(gene2).lower()

                if gene1 == gene2:
                    continue

                adj[gtoidict[gene1]][gtoidict[gene2]] += 1
                adj[gtoidict[gene2]][gtoidict[gene1]] += 1

    # Create the graph with named edges
    for row in range(len(adj)):
        for col in range(len(adj[0])):
            if (adj[row][col] == 0):
                continue
            G.add_edges_from([(itogdict[row], itogdict[col])],
                             weight=adj[row][col])

    return G


def read_csv(path, skip_lines=0, cols=1):
    movierawdata = list(csv.reader(open(path, 'rU'), dialect=csv.excel_tab,
                        delimiter=','))[skip_lines:]
    if cols is not None:
        movierawdata = [row[0:cols] for row in movierawdata]
    return movierawdata


def convert_raw_to_dict(raw):
    gdict = OD()
    for row in raw:
        movie = str(row[0])
        gdict[movie] = {}
        gdict[movie]['Rating'] = float(row[1])
        gdict[movie]['Genre'] = row[2].split(' ')[:-1]
        gdict[movie]['Budget'] = float(row[3])
        gdict[movie]['ROI'] = float(row[4])
        gdict[movie]['Genes'] = [g for g in row[5:] if not len(g) == 0]

    return gdict


def get_c_from_partition(commArray):
    nodelist = [[] for x in range(max(commArray.values()) + 1)]
    for gene in commArray:
        cnum = commArray[gene]
        nodelist[cnum].append(gene)

    return nodelist


def compute_ROI(cl, cluster_set, weight=False):
    '''
    Compute unweighted ROI average for now,
    can be changed to weighted if required
    '''
    ROI = 0.0
    totwt = 0.0
    for tup in cl:
        wt = 1
        # if weight is True:
            # wt = tup['Sim']
        ROI += cluster_set[tup['Movie']]['ROI'] * wt
        totwt += wt
    return ROI / totwt


def compute_cosine_similarity(movie, genedict,
                              EVCDict, geneList):
    '''
    Compute the distance between a movie in genedict with every movie
    in genedict which is our training set, find out the ROI of top 2
    and bottom 2 movies and take an average of their ROIs and report
    that as the ROI of the current genedict movie
    '''

    movieGenes = sorted(list(genedict[movie]['Genes']))

    # Stores a list of EVC values for genome elements in the top communities
    topBaseArray = [0] * len(geneList)
    for i, gene in enumerate(geneList):
        if gene in EVCDict['Top100'].keys():
            topBaseArray[i] = 1

    topArray = [0] * len(geneList)
    for i, gene in enumerate(geneList):
        if gene in movieGenes and gene in EVCDict['Top100']:
            topArray[i] = EVCDict['Top100'][gene]

    pos = pairwise_distances(topBaseArray, topArray, 'cosine')[0][0]

    botBaseArray = [0] * len(geneList)
    for i, gene in enumerate(geneList):
        if gene in EVCDict['Bot100'].keys():
            botBaseArray[i] = 1

    botArray = [0] * len(geneList)
    for i, gene in enumerate(geneList):
        if gene in movieGenes and gene in EVCDict['Bot100']:
            botArray[i] = EVCDict['Bot100'][gene]

    neg = pairwise_distances(botBaseArray, botArray, 'cosine')[0][0]
    return round(100 * (pos - neg) / 2.0, 6)


def main():
    murl = movie_data_url + str(start_year) + '-' + str(end_year) + '.csv'
    moviedata = read_csv(murl, 2, None)
    cluster_set = convert_raw_to_dict(moviedata)

    genedict = json.load(open(cl_movie_url, 'r'))
    tempdict = {}
    gtoidict = {}
    itogdict = {}
    EVCDict = {}
    EVCDict['Top100'] = {}
    EVCDict['Bot100'] = {}

    for movie in cluster_set.keys():
        for gene in cluster_set[movie]['Genes']:
            tempdict[str(gene).lower()] = 0

    count = 0
    for gene in sorted(tempdict.keys()):
        gtoidict[gene] = count
        itogdict[count] = gene
        count += 1

    top100_cluster = OD(IT.islice(cluster_set.items(), 0, 100))
    bot100_cluster = OD(IT.islice(cluster_set.items(), 100, 200))

    G = {}
    G['Top100'] = fill_Graph(top100_cluster, count, gtoidict, itogdict)
    G['Bot100'] = fill_Graph(bot100_cluster, count, gtoidict, itogdict)

    nlistt100 = get_c_from_partition(C.best_partition(G['Top100']))
    nlistb100 = get_c_from_partition(C.best_partition(G['Bot100']))

    # Get the individual community NX graphs from the original
    commGraphs = {}
    commGraphs['Top100'] = []
    commGraphs['Bot100'] = []
    for index in range(len(nlistt100)):
        commGraphs['Top100'].append(NX.subgraph(G['Top100'], nlistt100[index]))
    for index in range(len(nlistb100)):
        commGraphs['Bot100'].append(NX.subgraph(G['Bot100'], nlistb100[index]))

    sampledict = {}
    sampledict['Top100'] = {}
    sampledict['Bot100'] = {}
    # We finally have the eigenvector values
    for gname in ['Top100', 'Bot100']:
        for subgraph in range(len(commGraphs[gname])):
            EVCDict[gname].update(NX.eigenvector_centrality_numpy(
                G[gname], commGraphs[gname][subgraph]))

    newd = {}
    geneList = sorted(list(set(EVCDict['Top100'].keys()) |
                      set(EVCDict['Bot100'].keys())))

    for movie in genedict:
        newd[movie] = {}
        newd[movie]['cos'] = compute_cosine_similarity(movie,
                                                       genedict,
                                                       EVCDict,
                                                       geneList)

    json.dump(newd, open('/Users/Lanfear/Desktop/TrainCosine.txt', 'w'))


if __name__ == '__main__':
    main()
