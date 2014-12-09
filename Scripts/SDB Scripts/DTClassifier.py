# -*- coding: utf-8 -*-
"""
Created on Sat Dec  6 12:58:06 2014

@author: Lanfear
"""

from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import BaggingRegressor
from sklearn.metrics import r2_score
from collections import OrderedDict
import csv

TrainPath = ('/Users/Lanfear/Desktop/Research/CLuuData/'
             'CLuuResults/FinalTrainSet1stDim.csv')
HoldoutPath = ('/Users/Lanfear/Desktop/Research/CLuuData/CLuuResults/'
               'FinalHoldoutSet.csv')
max_d = 7
mss = 2
numTrees = 50
numTests = 1000


def parse_csv(path):
    movierawdata = list(csv.reader(open(path, 'rU'), dialect=csv.excel_tab,
                        delimiter=','))[1:]
    tempDict = OrderedDict()
    for row in movierawdata:
        tempDict[row[0]] = {}
        tempDict[row[0]]['Features'] = row[8:]
        tempDict[row[0]]['AROI'] = float(row[6])
        tempDict[row[0]]['Year'] = int(row[1])
        tempDict[row[0]]['Genre'] = str(row[2])

    return tempDict

Trainset = parse_csv(TrainPath)
Testset = parse_csv(HoldoutPath)

numSamples = len(Trainset)
#The training features
trainfeatures = [Trainset[k]['Features'] for k in Trainset]
#The actual ROI of movies
trainROI = [Trainset[k]['AROI'] for k in Trainset]

#The testing features
testfeatures = [Testset[k]['Features'] for k in Testset]
#The test ROI
testROI = [Testset[k]['AROI'] for k in Testset]

R2List = OrderedDict()
R2List['TrainROI'] = []
R2List['TestROI'] = []

for i in range(numTests):
    classifier = BaggingRegressor(base_estimator=DecisionTreeRegressor(),
                                  n_estimators=numTrees,
                                  max_samples=int(0.5*numSamples),
                                  max_features=int(1))

    classifier.fit(trainfeatures, trainROI)
    predictROI = {}
    predictROI['Training'] = classifier.predict(trainfeatures)
    predictROI['Test'] = classifier.predict(testfeatures)

    R2 = {}
    R2['Train'] = r2_score(trainROI, predictROI['Training'])
    R2['Test'] = r2_score(testROI, predictROI['Test'])

    R2List['TrainROI'].append(R2['Train'])
    R2List['TestROI'].append(R2['Test'])

print 'Best Train ROI: ', max(R2List['TrainROI'])
print 'Best Test ROI: ', max(R2List['TestROI'])
