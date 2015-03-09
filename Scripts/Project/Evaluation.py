#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  19 17:13:16 2015

@author: Lanfear
"""
import csv

from collections import OrderedDict
from numpy import mean, median, std
from sklearn.metrics import precision_recall_fscore_support

w1URL = 'moviewindow1980-1990.csv'
w2URL = 'moviewindow1990-2000.csv'
w3URL = 'moviewindow2000-2010.csv'

pOWCU = 'PredOrigWithCosine.csv'
pRWCU = 'PredReducedWithCosine.csv'
pOWtCU = 'PredOrigWithoutCosine.csv'


def parse_csv_w(path, csvType):
    '''
    Parses a csv file and returns a dictionary of movies
    '''
    if csvType == 1:
        # File parser for the moviewindowxxxx-xxxx.csv files
        movierawdata = list(csv.reader(open(path, 'rU'), dialect=csv.excel_tab,
                            delimiter=','))[2:]

        tempDict = OrderedDict()
        for row in movierawdata:
            tempDict[row[0]] = {}
            tempDict[row[0]]['Rating'] = float(row[1])
            tempDict[row[0]]['Genre'] = row[2]
            tempDict[row[0]]['Budget'] = float(row[3])
            tempDict[row[0]]['ROI'] = float(row[4])
            tempDict[row[0]]['Genes'] = row[5:]
        return tempDict

    else:
        # File parser for my result csv files
        movierawdata = list(csv.reader(open(path, 'rU'), dialect=csv.excel_tab,
                            delimiter=','))[1:]

        tempDict = OrderedDict()
        for row in movierawdata:
            tempDict[row[0]] = {}
            tempDict[row[0]]['AROI'] = float(row[1])
            tempDict[row[0]]['CROI'] = float(row[2])
            tempDict[row[0]]['MYROI'] = float(row[3].rstrip())
        return tempDict


def get_ROIs(w1, w2, w3):
    '''
    Extract ROIs individually from the three files
    and combine them together, find mean, median and
    stddev of the three
    '''
    w1R = [w1[key]['ROI'] for key in w1]
    w2R = [w2[key]['ROI'] for key in w2]
    w3R = [w3[key]['ROI'] for key in w3]
    # Build a full list of ROIs from all 3 ROI lists
    finROIs = sorted(w1R + w2R + w3R)
    mean1 = round(mean(finROIs), 6)
    median1 = round(median(finROIs), 6)
    std1 = round(std(finROIs), 6)
    return mean1, median1, std1


def classify_movies(ROIList, mM, hM, string):
    print string, 'measures:'
    r = ROIList
    aROI = [0 if r[k]['AROI'] < mM else 1 if
            (r[k]['AROI'] >= mM and r[k]['AROI'] < hM) else 2 for k in ROIList]
    myROI = [0 if r[k]['MYROI'] < mM else 1 if (r[k]['MYROI'] >= mM
             and r[k]['MYROI'] < hM) else 2 for k in ROIList]

    prec, recall, f1, _ = precision_recall_fscore_support(aROI,
                                                          myROI,
                                                          average='macro'
                                                          )
    print 'Precision:', round(prec, 6), 'Recall: ', round(recall, 6),\
        'F1 Score:', round(f1, 6)


def begin_evaluation():
    w1d = parse_csv_w(w1URL, 1)
    w2d = parse_csv_w(w2URL, 1)
    w3d = parse_csv_w(w3URL, 1)
    # Original with cosine
    pOWC = parse_csv_w(pOWCU, 2)
    # Original without cosine
    pOWtC = parse_csv_w(pOWtCU, 2)
    # Reduced with cosine
    pRWC = parse_csv_w(pRWCU, 2)
    _, med, stddev = get_ROIs(w1d, w2d, w3d)

    categories = [med, med + 0.38 * stddev]
    classify_movies(pOWtC, *categories, string='OriginalWithoutCosine')
    classify_movies(pOWC, *categories, string='OriginalWithCosine')
    classify_movies(pRWC, *categories, string='ReducedWithCosine')


def main():
    begin_evaluation()


if __name__ == '__main__':
    main()
