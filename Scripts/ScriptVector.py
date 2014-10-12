# -*- coding: utf-8 -*-
"""
Created on Mon Sep  8 17:48:37 2014

@author: Lanfear
"""

import os, mmap, numpy as np
import csv
from pickle import dump

filepath = '/Users/Lanfear/Desktop/Research/ParsedCluuScripts'
scriptmatpath = '/Users/Lanfear/Desktop/Research/Scenematrices'
movieinfopath = '/Users/Lanfear/Desktop/Research/CLuuResults/MovieInfo.csv'
allwords = 'allwords.txt'
xtab = 'xtab.txt'

def saveScenesIntoMatrix(scenemat, fname):        
    dump(scenemat, open(fname, 'wb'))

if __name__ == '__main__':
    
    #Get all script names in the folder
    scripts = [sname for sname in os.listdir(filepath) if sname.endswith('.txt')
                if sname != 'Parsed_Juno_g2.txt']
    
    movieinfo = {}
    #Extract movie info like year, genre from the csv file              
    #Skip first line
    
    movierawdata = list(csv.reader(open(movieinfopath, 'rU'), dialect=csv.excel_tab,
                        delimiter=','))[1:]

    for line in movierawdata:
        movieinfo[line[0]] = {}
        movieinfo[line[0]]['Year'] = line[1]
        movieinfo[line[0]]['Genre'] = line[2]
        movieinfo[line[0]]['Rating'] = line[3]
        movieinfo[line[0]]['Gross'] = line[4]
        movieinfo[line[0]]['Budget'] = line[5]
        movieinfo[line[0]]['ROI'] = line[6]
        movieinfo[line[0]]['numScenes'] = 0

    for scriptFolderName in scripts:
        finalPath = filepath + '/' + scriptFolderName
    
        #Store number of scenes, required for B-Spline interpolation        
        listofScenes = [x for x in os.listdir(finalPath + '/') 
                    if x.endswith('.txt')]
        movieinfo[scriptFolderName]['numScenes'] = len(listofScenes) - 2
        
        #print scriptFolderName
        xt = open(finalPath + '/' + xtab)
        xtmmap = mmap.mmap(xt.fileno(), 0, access=mmap.ACCESS_READ)    
        #Skip the first line consisting of words    
        wordcount = len(xtmmap.readline().rstrip('\n').rstrip(' ').split(' '))
        scenemat = np.zeros(wordcount)
    
        for line in iter(xtmmap.readline, ''):
            scenemat = np.vstack([scenemat, 
                    line.rstrip('\n').rstrip(' ').split(' ')[1:]])
    
        scenemat = np.delete(scenemat, (0), axis=0)
        movieinfo[scriptFolderName]['sceneVector'] = scenemat
        
        '''Save entire movie info in the format
        movieinfo['Rating'], movieinfo['sceneVector'],
        movieinfo['Gross'], movieinfo['Budget'], movieinfo['Year'],
        movieinfo['Genre'], movieinfo['ROI']
        '''
        saveScenesIntoMatrix(movieinfo[scriptFolderName], scriptmatpath + '/'+ 
                    scriptFolderName[7:].split('.')[0] + '.mat')
                    
        xt.close()

    print "Extracting sceneMatrices Ended"
    
    