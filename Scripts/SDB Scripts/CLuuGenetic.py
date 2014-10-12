# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 21:16:10 2014

@author: Lanfear
"""

import json
import networkx as NX
import community as C
import numpy as NP
import matplotlib.pyplot as PLT
import os
import operator

file_url = '/Users/Lanfear/Desktop/Research/CLuuData/CLuuScriptsGeneData/moviegenes.txt'
res_url = '/Users/Lanfear/Desktop/Research/CLuuData/Results/'

start_year = 2000
end_year = 2010
'''
/----------------------------------\
'''
def fill_Graph(genedict, count, gtoidict, itogdict):
    
    G = NX.Graph()
    adj = NP.zeros((count, count), dtype = int)
    
    for movie in genedict.keys():

        #Constrain movies by year
        year = int(genedict[movie]['Year'])
        if not (year >= start_year and year <= end_year):
            continue
                    
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
            G.add_edges_from([(itogdict[row], itogdict[col])], weight = adj[row][col])
    
    return G

'''
/----------------------------------\
'''
def get_components_of_G(adjmat, res, gtoidict, itogdict):
    '''
    Get the different graph components and add them into a sparse graph,
    we need to build different graphs for different components and
    calculate EVCs and influential nodes in each of them
    '''
    numC = len(set(res.values()))
    
    cList = []
    for c in range(numC):
        vlist = sorted([gtoidict[vertex] for vertex in res if res[vertex] == c])
        cList.append(vlist)
    
    CompGraphs = []
    #For loop for each component
    for c in range(numC):
        G = NX.Graph()
        #For loop for each row in that component
        for row in cList[c]:
            for col in cList[c]:
                try:
                    G.add_edges_from([(itogdict[row], itogdict[col])], weight = adjmat[row, col])
                except IndexError:
                    continue
                
        CompGraphs.append(G)

    folder_path = res_url + str(start_year) + '-' + str(end_year) + '/'
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path, 0755)

    mode = ''
    file_path = folder_path + str(start_year) + '-' + str(end_year) + '.txt'
    if os.path.isfile(file_path):
        mode = 'w+'
    else:
        mode = 'a+'
    f = open(file_path, mode)      
        
    colors = ['y', 'r', 'm', 'g', 'c']
    for comp in range(len(CompGraphs)):
        PLT.figure(comp + 1, figsize = (15, 15))
        PLT.title('Component #%d %d to %d' % ((comp + 1), start_year, end_year))

        #Scale nodes by their EVC values        
        EVC = NX.eigenvector_centrality_numpy(CompGraphs[comp])
        scale = 1000 / max(EVC.values())
        
        NX.draw(CompGraphs[comp], NX.spring_layout(CompGraphs[comp], scale = 3.5, iterations = 100), 
                node_size = [scale * EVC[k] for k in CompGraphs[comp].nodes()], font_size = 12, alpha = 0.25, 
                             edge_color = colors[comp], with_labels=True)
        
        PLT.savefig(folder_path + 'Comp#%d' % comp + '.png', bbox_inches='tight')
        
        EVCToWrite = sorted(EVC.items(), key=operator.itemgetter(1), reverse=True)
        
        f.write('START OF COMPONENT #%d\n\n' % (comp + 1))
        for item in EVCToWrite:
            f.write('%-25s' % item[0] + str(scale * item[1]) + '\n')
        f.write('\n/-------END OF COMPONENT/--------\n\n')
    
    f.close()
        
'''
/----------------------------------\
'''
def main():
    
    genedict = json.load(open(file_url, 'r'))    
    tempdict = {}
    gtoidict = {}
    itogdict = {}
    
    for movie in genedict.keys():
        for gene in genedict[movie]['Genes']:
            gene = str(gene).lower()
            tempdict[gene] = 0
    
    count = 0
    for gene in tempdict.keys():
        gtoidict[gene] = count
        itogdict[count] = gene
        count += 1
    
    G = fill_Graph(genedict, count, gtoidict, itogdict)
    mat = NX.to_numpy_matrix(G)
    res = C.best_partition(G)      
    
    get_components_of_G(mat, res, gtoidict, itogdict)    

if __name__ == '__main__':
    main()