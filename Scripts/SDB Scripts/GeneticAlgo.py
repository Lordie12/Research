# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 19:36:32 2014

@author: Lanfear
"""

import csv
import collections
import numpy as NP
import networkx as NX
import random
import community as C

sample = '/Users/Lanfear/Desktop/text.txt'
window_url = ('/Users/Lanfear/Desktop/Research/CLuuData/'
              'TimeWindowResults/TimeWindow1990-2000.csv')
initial_pop = 120
phi = 10
pc = 0.72
pm = 0.03


def produce_population(genedict):
    randList = random.sample(range(0, 200), initial_pop)
    geneItems = genedict.items()
    popList = [geneItems[index] for index in randList]
    return popList


def compute_local_clustering(genelist, T250, commGraphs):
    '''
    First part computes clustering coefficient of a subset of nodes delta
    in the set
    Second part computes communities in T250 and calculates the third term
    '''
    vertexList = {k: [] for k in range(0, len(commGraphs.keys()))}
    for comm in commGraphs:
        for gene in genelist:
            if gene in commGraphs[comm].nodes():
                vertexList[comm].append(gene)

    k = 0
    delta = 0
    for comm in vertexList.keys():
        if len(vertexList[comm]) > 0:
            delta += NX.transitivity(NX.subgraph(commGraphs[comm],
                                                 vertexList[comm]))
            k += 1

    return delta / float(k)


def calc_fitness_x(currPop, EVCTop, EVCBot, gtoidict, itogdict,
                   TopGraph, commGraphs):
    fitness = {}
    count = 0
    for pop in currPop:
        fitness[count] = {}
        fitness[count]['Genes'] = pop[1]['Genes']
        currFitness = 0
        delta = compute_local_clustering(pop[1]['Genes'], TopGraph, commGraphs)
        for gene in pop[1]['Genes']:
            #Compute fitness according to equation
            currFitness += 2 * EVCTop[gtoidict[gene]] - EVCBot[gtoidict[gene]]
            + delta
            #Have to add community detection restricting to num of communities
            #difficult to do in python, implementation does not exist as of yet
        fitness[count]['Fitness'] = currFitness
        count += 1

    return fitness


def filter_genes(geneList):
    fitnessList = [row['Fitness'] for row in geneList]
    mShift = min(fitnessList)
    if mShift < 0:
        mShift = mShift * -1
        for row in geneList:
            row['Fitness'] += mShift


def split_graph_into_communities(OrigGraph, CommVector):
    comms = {k: [] for k in range(0, max(CommVector.values()) + 1)}
    for node in CommVector:
        comms[CommVector[node]].append(node)

    Graphs = {}
    for cNum in comms.keys():
        Graphs[cNum] = NX.subgraph(OrigGraph, comms[cNum])

    return Graphs


def perform_GA(Graphs, commGraphs, gtoidict, itogdict, genedict):
    '''
    Perform the GA algorithm here, Graphs has the original graphs with all
    Nodes in both top and bottom networks, commGraphs contains only the
    specific communities needed for the third part of the equation
    '''
    EVCTop = NX.eigenvector_centrality_numpy(Graphs['Top'])
    EVCBot = NX.eigenvector_centrality_numpy(Graphs['Bot'])

    randPop = produce_population(genedict)

    communities = split_graph_into_communities(commGraphs['Top'],
                                        C.best_partition(commGraphs['Top']))

    while (phi > 0):
        geneList = calc_fitness_x(randPop, EVCTop, EVCBot, gtoidict, itogdict,
                                  commGraphs['Top'], communities)
        filterList = filter_genes(geneList.values())
        break


def to_graphical_form(gtoidict, itogdict, genedict):
    dim = len(gtoidict.keys())
    adjGraphs = {}
    Graphs = {'Top': NX.Graph(), 'Bot': NX.Graph()}
    adjGraphs['Top'] = NP.zeros((dim, dim), dtype=int)
    adjGraphs['Bot'] = NP.zeros((dim, dim), dtype=int)

    '''
    Build the MGC network as an adjacency matrix here
    '''
    for movie in genedict:
        cat = ''
        if (float(genedict[movie]['Rating']) > 5):
            cat = 'Top'
        else:
            cat = 'Bot'
        for gene1 in genedict[movie]['Genes']:
            for gene2 in genedict[movie]['Genes']:
                if gene1 == gene2:
                    continue
                adjGraphs[cat][gtoidict[gene1]][gtoidict[gene2]] += 1
                adjGraphs[cat][gtoidict[gene2]][gtoidict[gene1]] += 1

    for gType in ['Top', 'Bot']:
        for row in range(len(adjGraphs[gType])):
            for col in range(len(adjGraphs[gType][0])):
                if (adjGraphs[gType][row][col] == 0):
                    continue
                Graphs[gType].add_edges_from([(itogdict[row],
                                             itogdict[col])],
                                             weight=
                                             adjGraphs[gType][row][col])

    fullAdjGraph = {}
    for gType in ['Top', 'Bot']:
        fullAdjGraph[gType] = NX.from_numpy_matrix(adjGraphs[gType])

    perform_GA(fullAdjGraph, Graphs, gtoidict, itogdict, genedict)


def main():
    movierawdata = list(csv.reader(open(window_url, 'rU'),
                        dialect=csv.excel_tab, delimiter=','))[2:]

    genedict = collections.OrderedDict()
    tempdict = {}
    for row in movierawdata:
        genedict[row[0]] = {}
        genedict[row[0]]['Rating'] = row[1]
        genedict[row[0]]['Genre'] = row[2]
        genedict[row[0]]['Genes'] = sorted([str(gene).lower()
                                           for gene in row[3:]
                                           if gene != ''])

        for gene in genedict[row[0]]['Genes']:
            tempdict[gene] = 0

    gtoidict = collections.OrderedDict()
    itogdict = collections.OrderedDict()
    keylist = [gene for gene in sorted(tempdict.keys())]
    for gene in keylist:
        gtoidict[gene] = 0

    count = 0
    for gene in gtoidict.keys():
        gtoidict[gene] = count
        itogdict[count] = gene
        count += 1

    to_graphical_form(gtoidict, itogdict, genedict)

'''
/----------------------------------\
'''
if __name__ == '__main__':
    main()
