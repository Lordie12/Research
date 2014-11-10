# -*- coding: utf-8 -*-
"""
Created on Fri Nov  7 11:14:15 2014

@author: Lanfear
"""

import json
import networkx as NX
import community as C
import numpy as NP
import itertools as IT
import math as M
import csv
from collections import OrderedDict as OD

movie_data_url = '/Users/Lanfear/Desktop/Research/CLuuData/TimeWindowResults/moviewindow'
cl_movie_url = '/Users/Lanfear/Desktop/Research/CLuuData/CLuuScriptsGeneData/moviegenes.txt'
res_url = '/Users/Lanfear/Desktop/Research/CLuuData/Results/'
filter_url = '/Users/Lanfear/Desktop/Research/CLuuData/CLuuResults/filtergenes.txt'
pcentile = 0.90
use_weighted_roi = False
rating_sort = False
filter_genes = True

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
                #Create co-occurrence network
                gene1 = str(gene1).lower()
                gene2 = str(gene2).lower()

                if gene1 == gene2:
                    continue

                adj[gtoidict[gene1]][gtoidict[gene2]] += 1
                adj[gtoidict[gene2]][gtoidict[gene1]] += 1

    #create the graph with named edges
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


def compute_cosine(tGene, sGene, sMovie, EVCDict, filtergenes):
    nr = 0.0
    dr1 = 0.0
    dr2 = 0.0
    for gene in tGene:
        if gene in sGene:
            #Skip the iteration if we are to filter out the post production 
            #gene
            if filter_genes == True and gene in filtergenes:
                continue
            try:
                nr += EVCDict[gene.lower()]
                dr1 += EVCDict[gene.lower()] ** 2
                dr2 += 1
            except:
                    continue

    try:
        return dict(Movie=sMovie, 
                    Sim=M.sqrt(nr) / ((M.sqrt(dr1)) * M.sqrt(dr2)))
    except:
        return None


def compute_ROI(cl, cluster_set, weight=False):
    '''
    Compute unweighted ROI average for now,
    can be changed to weighted if required
    '''
    ROI = 0.0
    totwt = 0.0
    for tup in cl:
        wt = 1
        if weight == True:
            wt = tup['Sim']
        ROI += cluster_set[tup['Movie']]['ROI'] * wt
        totwt += wt
    return ROI / totwt


def compute_cosine_similarity(movie, cluster_set, genedict,\
            EVCDict, filtergenes):
    cosine_list = []
    '''
    Compute the distance between a movie in genedict with every movie
    in EVC Dict which is our training set, find out the top 10 %tile
    movies and take an average of their ROIs and report that as the
    ROI of the current genedict movie
    '''
    for m in cluster_set:        
        if cluster_set[m]['Rating'] > 6:
            Mtype = 'Top100'
        else:
            Mtype = 'Bot100'
            
        res = compute_cosine(genedict[movie]['Genes'], cluster_set[m]['Genes'], 
                             m, EVCDict[Mtype], filtergenes)
        
        if res is not None:
            cosine_list.append(res)

    cosine_list = sorted(cosine_list, key=lambda k: k['Sim']) 
    pTile = [cosine_list[k]['Sim'] for k in range(len(cosine_list))]
    return cosine_list[percentile(pTile, pcentile):]


def mean(genedict):
    m = 0.0
    for movie in genedict:
        m += float(genedict[movie]['ROI'])
    return m / len(genedict.keys())


def MSE(mean, ROIDict):
    mse = 0.0
    for movie in ROIDict:
        mse += (ROIDict[movie] - mean) ** 2
    return mse / len(ROIDict.keys())
    
    
def MAE(mean, ROIDict):
    mae = 0.0
    for movie in ROIDict:
        mae += abs(ROIDict[movie] - mean)
    return mae / len(ROIDict.keys())


def R2(mse, mae):
    return 1 - (mse / float(mae))


def main():
    murl = movie_data_url + str(start_year) + '-' + str(end_year) + '.csv'
    moviedata = read_csv(murl, 2, None)
    cluster_set = convert_raw_to_dict(moviedata)

    genedict = json.load(open(cl_movie_url, 'r'))
    filtergenes = json.load(open(filter_url, 'r'))
    tempdict = {}
    gtoidict = {}
    itogdict = {}
    EVCDict = {}
    EVCDict['Top100'] = {}
    EVCDict['Bot100'] = {}
    ROIDict = {}

    #Filter all gene dictionaries to the movies within 1980 - 1990
    genedict = {k:genedict[k] for k in genedict.keys() if 
                int(genedict[k]['Year']) >= start_year and
                int(genedict[k]['Year']) <= end_year}

    for movie in cluster_set.keys():
        for gene in cluster_set[movie]['Genes']:
            tempdict[str(gene).lower()] = 0

    count = 0
    for gene in sorted(tempdict.keys()):
        gtoidict[gene] = count
        itogdict[count] = gene
        count += 1

    #Split into top 100 movies and bottom 100 movies
    if (rating_sort == True):
        top100_cluster = OD(IT.islice(cluster_set.items(), 0, 100))
        bot100_cluster = OD(IT.islice(cluster_set.items(), 100, 200))
        
    else:
        #Here we sort by ROIs and not ratings        
        keys = sorted(cluster_set, key=lambda k: cluster_set[k]['ROI']) 
        sdict = OD()
        for key in keys:
            sdict[key]= cluster_set[key]
            
        top100_cluster = OD(IT.islice(sdict.items(), 0, 100))
        bot100_cluster = OD(IT.islice(sdict.items(), 100, 200))
        
    G = {}
    G['Top100'] = fill_Graph(top100_cluster, count, gtoidict, itogdict)
    G['Bot100'] = fill_Graph(bot100_cluster, count, gtoidict, itogdict)

    nlistt100 = get_c_from_partition(C.best_partition(G['Top100']))
    nlistb100 = get_c_from_partition(C.best_partition(G['Bot100']))

    #Get the individual community NX graphs from the original
    commGraphs = {}
    commGraphs['Top100'] = []
    commGraphs['Bot100'] = []
    for index in range(len(nlistt100)):
        commGraphs['Top100'].append(NX.subgraph(G['Top100'], nlistt100[index]))
    for index in range(len(nlistb100)):
        commGraphs['Bot100'].append(NX.subgraph(G['Bot100'], nlistt100[index]))

    sampledict = {}
    sampledict['Top100'] = {}
    sampledict['Bot100'] = {}
    #We finally have the eigenvector values
    for gname in ['Top100', 'Bot100']:
        for subgraph in range(len(commGraphs[gname])):
            EVCDict[gname].update(NX.eigenvector_centrality_numpy(
                G[gname], commGraphs[gname][subgraph]))

    for movie in genedict:
        cl = compute_cosine_similarity(movie, cluster_set, genedict,\
            EVCDict, filtergenes)
        ROIDict[movie] = compute_ROI(cl, cluster_set, use_weighted_roi)

    meanROI = mean(genedict)
    mse = MSE(meanROI, ROIDict)
    mae = MAE(meanROI, ROIDict)
    print 'MSE ' + str(start_year) + ' - ' + str(end_year) + ': ' +\
        str(round(mse, 6))
    print 'MAE ' + str(start_year) + ' - ' + str(end_year) + ': ' +\
        str(round(mae, 6))
    print 'R2 ' + str(start_year) + ' - ' + str(end_year) + ': ' +\
        str(round(R2(mse, mae), 6))


if __name__ == '__main__':
    main()
