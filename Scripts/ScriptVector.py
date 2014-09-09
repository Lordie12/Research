# -*- coding: utf-8 -*-
"""
Created on Mon Sep  8 17:48:37 2014

@author: Lanfear
"""

import os, mmap, numpy as np
from pickle import dump

filepath = '/Users/Lanfear/Desktop/Research/MovieScripts'
scriptmatpath = '/Users/Lanfear/Desktop/Research/Scenematrices'
allwords = 'allwords.txt'
xtab = 'xtab.txt'

def saveScenesIntoMatrix(scenemat, fname):        
    dump(scenemat, open(fname, 'wb'))

if __name__ == '__main__':
    
    #Get all script names in the folder
    scripts = [sname for sname in os.listdir(filepath) if sname.endswith('.txt')]
    
    for scriptFolderName in scripts:
        finalPath = filepath + '/' + scriptFolderName
    
        xt = open(finalPath + '/' + xtab)
        xtmmap = mmap.mmap(xt.fileno(), 0, access=mmap.ACCESS_READ)    
        #Skip the line consisting of words    
        wordcount = len(xtmmap.readline().rstrip('\n').rstrip(' ').split(' '))
        scenemat = np.zeros(wordcount)
    
        for line in iter(xtmmap.readline, ''):
            scenemat = np.vstack([scenemat, 
                    line.rstrip('\n').rstrip(' ').split(' ')[1:]])
    
        scenemat = np.delete(scenemat, (0), axis=0)
        saveScenesIntoMatrix(scenemat, scriptmatpath + '/'+ 
                    scriptFolderName[7:].split('.')[0] + '.mat')
        xt.close()
    
    