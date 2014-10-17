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
window_url = '/Users/Lanfear/Desktop/Research/CLuuData/TimeWindowResults/TimeWindow1990-2000.csv'
gml_path = '/Users/Lanfear/Desktop/graph.gml'
initial_pop = 120
phi = 10
pc = 0.72
pm = 0.03

'''
/----------------------------------\
'''
def produce_population(genedict):
    randList = random.sample(range(0, 200), initial_pop)
    geneItems = genedict.items()
    popList = [geneItems[index] for index in randList]
    return popList
    
'''
/----------------------------------\
'''
def calc_fitness_x(currPop, EVCTop, EVCBot, gtoidict, itogdict):
    
    fitness = {}
    count = 0
    for pop in currPop:
        fitness[count] = {}
        fitness[count]['Genes'] = pop[1]['Genes']
        currFitness = 0
        for gene in pop[1]['Genes']:
            #Compute fitness according to equation
            currFitness += 2 * EVCTop[gtoidict[gene]] - EVCBot[gtoidict[gene]]
            #Have to add community detection restricting to number of communities
            #difficult to do in python, implementation does not exist as of yet
        fitness[count]['Fitness'] = currFitness
        count += 1
    
    return fitness

'''
/----------------------------------\
'''
def filter_genes(geneList):
    fitnessList = [row['Fitness'] for row in geneList]
    print fitnessList

'''
/----------------------------------\
'''
def get_new_dict(Graphs):
    newdict = {'gtoi': {'Top': {}, 'Bot': {}}, 'itog': {'Top': {}, 'Bot': {}}}
    
    for gType in ['Top', 'Bot']:
        count = 0
        for gene in Graphs[gType].nodes():
            newdict['gtoi'][gType][gene] = count
            newdict['itog'][gType][gene] = count
            count += 1
    
    return newdict    
    
'''
/----------------------------------\
'''
def perform_GA(Graphs, gtoidict, itogdict, genedict):
    '''
    Perform the GA algorithm here
    '''
    EVCTop = NX.eigenvector_centrality_numpy(Graphs['Top'])
    EVCBot = NX.eigenvector_centrality_numpy(Graphs['Bot'])
    
    randPop = produce_population(genedict)    
    
    '''
    We need this because we now have a new node mapping per graph,
    need this to main EVC array consistency
    '''
    #newdict = get_new_dict(Graphs)
    #gtoidict = newdict['gtoi']
    #itogdict = newdict['itog']
    
    while (phi > 0):
        geneList = calc_fitness_x(randPop, EVCTop, EVCBot, gtoidict, itogdict)
        filterList = filter_genes(geneList.values())
        break

'''
/----------------------------------\
'''
def to_graphical_form(gtoidict, itogdict, genedict):
    dim = len(gtoidict.keys())
    adjGraphs = {}
    Graphs = {'Top': NX.Graph(), 'Bot': NX.Graph()}
    adjGraphs['Top'] = NP.zeros((dim, dim), dtype = int)
    adjGraphs['Bot'] = NP.zeros((dim, dim), dtype = int)
    
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
                                itogdict[col])], weight = adjGraphs[gType][row][col])

    perform_GA(adjGraphs, gtoidict, itogdict, genedict)
    
'''
/----------------------------------\
'''
def main():
    movierawdata = list(csv.reader(open(window_url, 'rU'), dialect=csv.excel_tab,
                    delimiter=','))[2:]
                    
    genedict = collections.OrderedDict()
    tempdict = {}
    for row in movierawdata:
        genedict[row[0]] = {}
        genedict[row[0]]['Rating'] = row[1]
        genedict[row[0]]['Genre'] = row[2]
        genedict[row[0]]['Genes'] = sorted([str(gene).lower() for gene in row[3:]
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
