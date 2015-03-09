#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 21:16:10 2014

@author: Lanfear
"""
import os
import csv
import json
import operator
import numpy as NP
import community as C
import networkx as NX
import matplotlib.pyplot as PLT

from collections import OrderedDict

baseURL = '/Users/Lanfear/Desktop/Research/CLuuData/TimeWindowResults/'
start_year = 1990
end_year = 2000
year = str(start_year) + '-' + str(end_year)
finalURL = baseURL + 'moviewindow' + year + '.csv'
t = '100B'

# URL where we write the final components and files
resBaseURL = '/Users/Lanfear/Desktop/Research/CLuuData/Results/'
resURL = resBaseURL + t + year + '/'

# Filter genes URL
filterURL = '/Users/Lanfear/Desktop/Research/CLuuData/CLuuResults/filtergenes.txt'

pcent = 0.99


def percentile(N, P):
    """
    Find the percentile of a list of values

    @parameter N - A list of values.  N must be sorted.
    @parameter P - A float value from 0.0 to 1.0

    @return - The percentile of the values.
    """
    n = int(round(P * len(N) + 0.5))
    return n-1


def fill_Graph(genedict, count, gtoidict, itogdict, filtergenes):

    G = NX.Graph()
    adj = NP.zeros((count, count), dtype=int)

    for movie in genedict.keys():
        for gene1 in genedict[movie]['Genes']:
            if gene1 in filtergenes:
                continue
            for gene2 in genedict[movie]['Genes']:
                if gene2 in filtergenes:
                    continue
                # Create co-occurrence network
                gene1 = str(gene1).lower()
                gene2 = str(gene2).lower()

                if gene1 == gene2:
                    continue

                adj[gtoidict[gene1]][gtoidict[gene2]] += 1
                adj[gtoidict[gene2]][gtoidict[gene1]] += 1

    # create the graph with named edges
    for row in range(len(adj)):
        for col in range(len(adj[0])):
            if (adj[row][col] == 0):
                continue
            G.add_edges_from([(itogdict[row], itogdict[col])],
                             weight=adj[row][col])

    return G


def get_components_of_G(adjmat, res, gtoidict, itogdict):
    '''
    Get the different graph components and add them into a sparse graph,
    we need to build different graphs for different components and
    calculate EVCs and influential nodes in each of them
    '''
    numC = len(set(res.values()))

    cList = []
    for c in range(numC):
        vlist = sorted([gtoidict[vertex] for vertex in res
                        if res[vertex] == c])
        cList.append(vlist)

    CompGraphs = []
    # For loop for each component
    for c in range(numC):
        G = NX.Graph()
        # For loop for each row in that component
        for row in cList[c]:
            for col in cList[c]:
                try:
                    G.add_edges_from([(itogdict[row], itogdict[col])],
                                     weight=adjmat[row, col])
                except IndexError:
                    # Should never happen
                    continue

        CompGraphs.append(G)

    folder_path = resURL
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path, 0755)

    mode = ''
    file_path = folder_path + 'Components.txt'
    if os.path.isfile(file_path):
        mode = 'w+'
    else:
        mode = 'a+'
    f = open(file_path, mode)

    for comp in range(len(CompGraphs)):
        PLT.figure(comp + 1, figsize=(15, 15))
        PLT.title('Component #%d %d to %d' % ((comp + 1),
                  start_year, end_year))
        PLT.xlim(0, 1)
        PLT.ylim(0, 1)

        G = CompGraphs[comp]
        # Scale nodes by their EVC values
        EVC = NX.eigenvector_centrality_numpy(G)
        scale = 4000 / max(EVC.values())
        layout = NX.random_layout(G)

        NX.draw(G, layout, node_size=[scale * EVC[k] for k in G.nodes()],
                font_size=15, alpha=0.20,
                edge_color='c', with_labels=False)

        labels = {}
        # Here we label only those influential nodes > some percentile
        # value compared to the rest
        ScaledEVC = {k: scale * EVC[k] for k in EVC.keys()}
        pcentval = percentile(sorted(ScaledEVC.values()), pcent)
        for node in G.nodes():
            if ScaledEVC[node] >= pcentval:
                labels[node] = node

        NX.draw_networkx_labels(G, layout, labels, font_size=15,
                                font_color='r', font_weight='bold')

        PLT.savefig(folder_path + 'Comp#%d' % comp +
                    '.png', bbox_inches='tight')

        # Save an EVC sorted list of genes in a text file
        EVCToWrite = sorted(EVC.items(), key=operator.itemgetter(1),
                            reverse=True)
        f.write('START OF COMPONENT #%d\n\n' % (comp + 1))
        for item in EVCToWrite:
            f.write('%-25s' % item[0] + str(scale * item[1]) + '\n')
        f.write('\n/-------END OF COMPONENT/--------\n\n')

    f.close()


def read_raw_csv(path):
    movieDict = OrderedDict()
    if t == '100T':
        # Read the top 100 movies
        movierawdata = list(csv.reader(open(path, 'rU'),
                            dialect=csv.excel_tab, delimiter=','))[2:102]
    elif t == '100B':
        # Read the bottom 100 movies
        movierawdata = list(csv.reader(open(path, 'rU'),
                            dialect=csv.excel_tab, delimiter=','))[102:]

    for row in movierawdata:
        movieDict[row[0]] = {}
        movieDict[row[0]]['Rating'] = float(row[1])
        movieDict[row[0]]['Genres'] = row[2].rstrip().split()
        movieDict[row[0]]['Budget'] = int(row[3])
        movieDict[row[0]]['ROI'] = float(row[4])
        movieDict[row[0]]['Genes'] = row[5:len(row) - 1]
    return movieDict


def main():

    genedict = read_raw_csv(finalURL)

    filterGenes = json.load(open(filterURL, 'r'))

    tempdict = {}
    gtoidict = {}
    itogdict = {}

    for movie in genedict.keys():
        for gene in genedict[movie]['Genes']:
            if gene in filterGenes:
                continue
            gene = str(gene).lower()
            tempdict[gene] = 0

    count = 0
    for gene in tempdict.keys():
        gtoidict[gene] = count
        itogdict[count] = gene
        count += 1

    G = fill_Graph(genedict, count, gtoidict, itogdict, filterGenes)
    mat = NX.to_numpy_matrix(G)
    res = C.best_partition(G)

    get_components_of_G(mat, res, gtoidict, itogdict)

if __name__ == '__main__':
    main()
