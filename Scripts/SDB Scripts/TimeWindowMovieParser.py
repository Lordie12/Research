# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 19:36:32 2014

@author: Lanfear
"""

from GetGenes import GetGenes
import imdb

base_url = 'http://www.jinni.com/movies/'
file_url = '/Users/Lanfear/Desktop/Research/CLuuData/TimeWindowResults/'

def main():
    G = GetGenes()    
    i = imdb.IMDb()
    #List of search URLs, first two contain 2 pages of the first 100 results in desc
    #The next two contain 2 pages of the first 100 results in asc 

if __name__ == '__main__':
    main()
