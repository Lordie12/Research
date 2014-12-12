# -*- coding: utf-8 -*-
"""
Created on Sat Dec  6 12:58:06 2014

@author: Lanfear
"""

from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import BaggingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from collections import OrderedDict
from numpy import mean, var
from json import load
import csv

TrainPath = ('/Users/Lanfear/Desktop/Research/CLuuData/'
             'CLuuResults/FinalTrainSet1stDim.csv')
HoldoutPath = ('/Users/Lanfear/Desktop/Research/CLuuData/CLuuResults/'
               'FinalHoldoutSet.csv')
TrainCos = ('/Users/Lanfear/Desktop/TrainCosine.txt')
HoldoutCos = ('/Users/Lanfear/Desktop/HoldoutCosine.txt')

numTrees = 50
# Number of tests carried out
numTests = 2000
# Can be optimized for R2, MSE, MAE or Var
optimize_for = 'R2'
# Use cosine distance or not?
include_cosine = False


def parse_csv(path):
    '''
    Parses a csv file and returns a dictionary of movies
    '''
    movierawdata = list(csv.reader(open(path, 'rU'), dialect=csv.excel_tab,
                        delimiter=','))[1:]
    tempDict = OrderedDict()
    for row in movierawdata:
        tempDict[row[0]] = {}
        tempDict[row[0]]['Year'] = int(row[1])
        tempDict[row[0]]['Genre'] = str(row[2])
        tempDict[row[0]]['AROI'] = float(row[6])
        tempDict[row[0]]['Features'] = row[8:]
    return tempDict


def parse_cosine(path):
    return load(open(path, 'r'))

Trainset = parse_csv(TrainPath)
Testset = parse_csv(HoldoutPath)
TrainCosine = parse_cosine(TrainCos)
HoldoutCosine = parse_cosine(HoldoutCos)
AvgTrain = mean([TrainCosine[k]['cos'] for k in TrainCosine])
AvgHoldout = mean([HoldoutCosine[k]['cos'] for k in HoldoutCosine])

numSamples = len(Trainset)

# Append the 45th cosine similarity index if include_cosine is true
if (include_cosine is True):
    for key in TrainCosine.keys():
        Trainset[key]['Features'].append(str(TrainCosine[key]['cos']))
    for key in Trainset.keys():
        if (len(Trainset[key]['Features']) < 45):
            Trainset[key]['Features'].append(str(AvgTrain))

    for key in HoldoutCosine.keys():
        Testset[key]['Features'].append(str(HoldoutCosine[key]['cos']))
    for key in Testset.keys():
        if (len(Testset[key]['Features']) < 45):
            Testset[key]['Features'].append(str(AvgHoldout))


# The training features
trainfeatures = [Trainset[k]['Features'] for k in Trainset]

# The actual ROI of movies
trainROI = [Trainset[k]['AROI'] for k in Trainset]

# The testing features
testfeatures = [Testset[k]['Features'] for k in Testset]

# The test ROI
testROI = [Testset[k]['AROI'] for k in Testset]

R2List = OrderedDict()
# R2List['TrainROI'] = []
R2List['TestR2'] = []

MeanList = OrderedDict()
MeanList['TrainMean'] = mean(trainROI)
MeanList['TestMean'] = mean(testROI)
MeanList['PredictMean'] = []

VarList = OrderedDict()
VarList['TrainVar'] = var(trainROI)
VarList['TestVar'] = var(testROI)
VarList['PredictVar'] = []

MSEList = OrderedDict()
MSEList['TestMSE'] = []

MAEList = OrderedDict()
MAEList['TestMAE'] = []

print 'Test optimized for', optimize_for
print 'Running Tests '
for i in range(numTests):
    classifier = BaggingRegressor(base_estimator=DecisionTreeRegressor(),
                                  n_estimators=numTrees,
                                  max_samples=int(0.5*numSamples),
                                  max_features=int(1))

    classifier.fit(trainfeatures, trainROI)
    # Compute the predicted ROIs and store them in an array
    predictROI = classifier.predict(testfeatures)

    # Compute statistical metrics ROI, MSE, MAE, Mean and Variance
    R2List['TestR2'].append(r2_score(testROI, predictROI))
    MSEList['TestMSE'].append(mean_squared_error(testROI, predictROI))
    MAEList['TestMAE'].append(mean_absolute_error(testROI, predictROI))
    MeanList['PredictMean'].append(mean(predictROI))
    VarList['PredictVar'].append(var(predictROI))

# print 'Best Test ROI: ', max(R2List['TestROI'])
# print 'Best Test MSE: ', min(MSEList['TestMSE'])
# print 'Best Test MAE: ', min(MAEList['TestMAE'])
# print 'Test Means: ', MeanList['TestMean']
# print 'Test Variance: ', VarList['TestVar']

if (optimize_for == 'R2'):
    currIndex = R2List['TestR2'].index(max(R2List['TestR2']))
elif (optimize_for == 'MSE'):
    currIndex = MSEList['TestMSE'].index(min(MSEList['TestMSE']))
elif (optimize_for == 'MAE'):
    currIndex = MAEList['TestMAE'].index(min(MAEList['TestMAE']))
elif (optimize_for == 'Var'):
    currIndex = VarList['PredictVar'].index(max(VarList['PredictVar']))

print 'Train Means    : ', MeanList['TrainMean']
print 'Train Var      : ', VarList['TrainVar']
print 'Test Mean      : ', MeanList['TestMean']
print 'Test Var       : ', VarList['TestVar']
print 'Mean R2        :', mean(R2List['TestR2'])
print 'R2             : ', R2List['TestR2'][currIndex]
print 'MSE            : ', MSEList['TestMSE'][currIndex]
print 'MAE            : ', MAEList['TestMAE'][currIndex]
print 'Prediction Mean: ', MeanList['PredictMean'][currIndex]
print 'Prediction Var : ', VarList['PredictVar'][currIndex]
