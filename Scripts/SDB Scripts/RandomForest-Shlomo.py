#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  6 12:58:06 2014

@author: Lanfear
"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.cross_validation import KFold
from collections import OrderedDict
from numpy import mean, var
from json import load
from numpy.random import rand
# from random import sample
import csv

TrainPath = ('/Users/Lanfear/Desktop/Research/CLuuData/'
             'CLuuResults/FinalTrainSet1stDim.csv')
HoldoutPath = ('/Users/Lanfear/Desktop/Research/CLuuData/CLuuResults/'
               'FinalHoldoutSet.csv')
TrainCos = ('/Users/Lanfear/Desktop/Research/CLuuData/'
            'CLuuResults/TrainCosine.txt')
HoldoutCos = ('/Users/Lanfear/Desktop/Research/CLuuData/'
              'CLuuResults/HoldoutCosine.txt')


numTrees = 50
# Number of tests carried out
numTests = 1
# Can be optimized for R2, MSE, MAE or Var
optimize_for = 'R2'
# Use cosine distance or not?
include_cosine = True
# Use genres or not?
include_genre = False
# Do we select a random subset of features?
select_rand_feature = True
# Do we cross validate this or not?
cross_v = True

if include_cosine is True:
    num_feats = 45
else:
    num_feats = 44


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
        tempDict[row[0]]['PROI'] = float(row[7])
        tempDict[row[0]]['Features'] = row[8:len(row) - 1]
    return tempDict


def parse_cosine(path):
    return load(open(path, 'r'))


def create_rand_feat_index():
    '''
    Create a randomly generated set of numbers
    which will be used to index into the feature
    vector thus selecting a random subset of the
    features
    '''
    num_feat = int(rand() * 100) % num_feats
    feat_index = []
    for i in range(num_feat):
        rand_num = (int(rand() * 100) % num_feats)

        while rand_num in feat_index:
            rand_num = (int(rand() * 100) % num_feats)
        feat_index.append(rand_num)

    return sorted(feat_index)

# Random set of features of at least size 10 #
# feat_index = []
f_index = [0, 1, 4, 6, 9, 10, 17, 22, 23, 27, 30, 32, 36, 37, 40, 41, 42, 44]
# while len(feat_index) <= 10:
#     feat_index = create_rand_feat_index()
# print f_index
######################################################


def create_rand_feat(Trainset, feat_index):
    '''
    This is where the features are trimmed according
    to the randomly generated feature index list
    '''
    return [list(map(float, [Trainset[d]['Features'][i]
            for i in feat_index])) for d in Trainset]


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

# The training and testing features
if select_rand_feature is True:
    trainfeatures = create_rand_feat(Trainset, f_index)
    testfeatures = create_rand_feat(Testset, f_index)
else:
    trainfeatures = [Trainset[k]['Features'] for k in Trainset]
    testfeatures = [Testset[k]['Features'] for k in Testset]

# The actual ROI of movies
trainROI = [Trainset[k]['AROI'] for k in Trainset]

# The test ROI
testROI = [Testset[k]['AROI'] for k in Testset]

# Shlomo Dec. 14
if (include_genre is True):
    traingenre = [Trainset[k]['Genre'] for k in Trainset]
    testgenre = [Testset[k]['Genre'] for k in Testset]
    allgenre = traingenre + testgenre
    allgenre = LabelEncoder().fit_transform(allgenre)
    traingenre = allgenre[: len(traingenre)]
    testgenre = allgenre[len(traingenre):]
    [trainfeatures[i].append(traingenre[i]) for i in range(len(traingenre))]
    [testfeatures[i].append(testgenre[i]) for i in range(len(testgenre))]


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

max_d = 5
mss = 2

newTrain = trainfeatures
newTrainROI = trainROI

if cross_v is True:
    kfold = KFold(len(trainfeatures), n_folds=10, shuffle=True)

print 'Running Tests '

for i in range(numTests):
    classifier = RandomForestRegressor(n_estimators=numTrees,
                                       max_depth=max_d,
                                       min_samples_split=mss)

    if cross_v is True:
        for train, test in kfold:
            trainfeatures = [newTrain[k] for k in train]
            trainROI = [newTrainROI[k] for k in train]
            testfeatures = [newTrain[k] for k in test]
            testROI = [newTrainROI[k] for k in test]

    classifier.fit(trainfeatures, trainROI)

    # Compute the predicted ROIs and store them in an array
    predictROI = classifier.predict(testfeatures)

    # for i, k in enumerate(Testset):
        # print str(k) + ',', Testset[k]['AROI'],\
            # ',', Testset[k]['PROI'], ',', predictROI[i]

    # Compute statistical metrics ROI, MSE, MAE, Mean and Variance
    R2List['TestR2'].append(r2_score(testROI, predictROI))
    MSEList['TestMSE'].append(mean_squared_error(testROI, predictROI))
    MAEList['TestMAE'].append(mean_absolute_error(testROI, predictROI))
    MeanList['PredictMean'].append(mean(predictROI))
    VarList['PredictVar'].append(var(predictROI))


# print 'Best Test ROI: ', max(R2List['TestROI'])
print 'Best Test MSE: ', min(MSEList['TestMSE'])
print 'Best Test MAE: ', min(MAEList['TestMAE'])
print 'Test Means: ', MeanList['TestMean']
print 'Test Variance: ', VarList['TestVar']

# if (optimize_for == 'R2'):
#    currIndex = R2List['TestR2'].index(max(R2List['TestR2']))
# elif (optimize_for == 'MSE'):
#    currIndex = MSEList['TestMSE'].index(min(MSEList['TestMSE']))
# elif (optimize_for == 'MAE'):
#    currIndex = MAEList['TestMAE'].index(min(MAEList['TestMAE']))
# elif (optimize_for == 'Var'):
#    currIndex = VarList['PredictVar'].index(max(VarList['PredictVar']))


print 'include_cosine : ', str(include_cosine)
print 'include_genre  : ', str(include_genre)

# print 'Train Means    : ', MeanList['TrainMean']
# print 'Train Var      : ', VarList['TrainVar']
# print 'Test Mean      : ', MeanList['TestMean']
# print 'Test Var       : ', VarList['TestVar']
print 'R2 Mean         :', mean(R2List['TestR2'])
print 'R2 Var          :', var(R2List['TestR2'])
# print 'R2             : ', R2List['TestR2'][currIndex]
# print 'MSE            : ', MSEList['TestMSE'][currIndex]
# print 'MAE            : ', MAEList['TestMAE'][currIndex]
# print 'Prediction Mean: ', MeanList['PredictMean'][currIndex]
# print 'Prediction Var : ', VarList['PredictVar'][currIndex]
