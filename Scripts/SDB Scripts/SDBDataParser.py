# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 22:50:58 2014

@author: Lanfear
"""

import collections
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

movieinfo_url = '/Users/Lanfear/Desktop/Research/SDBData/movies_gene_data.txt'

def topbotmatrix(gtoi, itog, mdict):
    #Build adjacency matrix of top-250 and bottom-100 movies
    adj = np.zeros((668, 668), dtype=int)
    for mname in mdict:
        genelist = mdict[mname]
        
        for i in range(len(genelist)):
            for j in range(len(genelist)):
                if i == j:
                    continue
                else:
                    row = gtoi[genelist[i].lower()]
                    col = gtoi[genelist[j].lower()]
                    adj[row][col] += 1
                    adj[col][row] += 1

def main():

    moviedict = {}    
    tempdict = {}
    f = open(movieinfo_url, 'r')
    for line in f:
        moviename = line[:line.find('[')].rstrip()
        genelist = line[line.find('[')+1 : line.find(']')].replace("'", '').replace(" ", '').split(',')
        moviedict[moviename] = genelist
        
        for gene in genelist:
            tempdict[gene] = 0
    
    gtoidict = collections.OrderedDict()
    itogdict = collections.OrderedDict()
    keylist = [gene.lower() for gene in sorted(tempdict.keys())]    
    
    
    for gene in keylist:
        gtoidict[gene] = 0
    
    count = 0
    
    for gene in gtoidict.keys():
        gtoidict[gene] = count
        itogdict[count] = gene
        count += 1

    topbotmatrix(gtoidict, itogdict, moviedict)

if __name__ == '__main__':
    main()