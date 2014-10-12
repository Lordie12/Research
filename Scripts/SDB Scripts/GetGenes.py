# -*- coding: utf-8 -*-
"""
Created on Sun Oct  5 09:08:33 2014

@author: Lanfear

"""
import urllib2, sys
import getopt, BeautifulSoup
import json, csv

base_url = 'http://www.jinni.com/movies/'
file_url = '/Users/Lanfear/Desktop/Research/CLuuData/CLuuScriptsGeneData/moviegenes.txt'
movieinfopath = '/Users/Lanfear/Desktop/Research/CLuuData/Data/Movie Results (Cleaned) - Final Training Set - 44 - 3rd dim.csv'
genedict = {}

def Parse_Genes(html):
    #Obtain genome elements by parsing link href values
    soup = BeautifulSoup.BeautifulSoup(html)
    attrs = ''
    genelist = []
    for link in soup.findAll("a"):
        attrs = link.get("href")
        genelist.append(str(attrs[attrs.rfind('=') + 1:]))
        
    return genelist

def Get_Genes(url, mName):
    response = urllib2.urlopen(url)
    html = response.read()

    sIndex = html.find('right_genomeGroup')
    eIndex = html.lower().find('more online info')
    html = html[sIndex:eIndex]
    
    if (html.find('right_genomeTitleColor Audience')):
        '''
        We are removing extraneous genome elemtents such as audience
        by stripping off that part of the HTML content
        '''
        temphtml = html[html.find('right_genomeTitleColor Audience') : ]
        temphtml = temphtml[temphtml.find('right_genomeGroup') : ]
        
        html = html[ : html.find('right_genomeTitleColor Audience')] + temphtml
    
    tempname = mName.replace('-', ' ')
    genedict[tempname] = {}
    genedict[tempname]['Genes'] = Parse_Genes(html)

def main(argv):
    if not len(argv) == 2 and not len(argv) == 4:
        print "Usage: python GetGenes.py -m 'movieName' -f genefilename (optional)"
        return 
    
    myopts, args = getopt.getopt(argv, 'm:f:')    
    mName = ''
    gFName = ''    
    
    for o, a in myopts:     
        if o == '-m':
            mName = a
        elif o == '-f':
            gFName = a
    
    mName = mName.replace(' ', '-')   

    url = base_url + mName
    Get_Genes(url, mName)    
    
if __name__ == '__main__':
    #main(sys.argv[1:])
    movierawdata = list(csv.reader(open(movieinfopath, 'rU'), dialect=csv.excel_tab,
                        delimiter=','))[1:]
    movierawdata = [row[0:3] for row in movierawdata]
    for row in movierawdata:
        mName = row[0].replace(' ', '-')
        print mName
        try:
            Get_Genes(base_url + mName, mName)
        except:
            print 'YOU MAD BRO? SHOULD NEVER SEE THIS'
        
        genedict[row[0]]['Year'] = row[1]
        genedict[row[0]]['Genre'] = row[2]
    
    json.dump(genedict, open(file_url, 'w'))
    print movierawdata