#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  6 12:58:06 2014

@author: Lanfear
"""
import csv
import numpy as np

from json import load
from collections import OrderedDict
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

TrainPath = '/Users/Lanfear/Desktop/Project/FinalTrain.csv'
HoldoutPath = '/Users/Lanfear/Desktop/Project/FinalHoldout.csv'

# Hyperparameters #
numTrees = 50
max_d = 5
mss = 2
###################

# Selection variable for train and holdout sets
# Size of the training set and the holdout sets
premute_train_test = True
TrainSize = 75
HoldoutSize = 36
###############################################


def parse_csv(path):
    '''
    Parses a csv file and returns a dictionary of movies
    '''

    movierawdata = list(csv.reader(open(path, 'rU'), dialect=csv.excel_tab,
                        delimiter=','))[1:]

    # Creates a dictionary of movies and features,
    # Used in the train set as well as the holdout set
    tempDict = OrderedDict()
    for row in movierawdata:
        tempDict[row[0]] = {}
        tempDict[row[0]]['Year'] = int(row[1])
        tempDict[row[0]]['Genre'] = str(row[2])
        tempDict[row[0]]['AROI'] = float(row[6])
        tempDict[row[0]]['PROI'] = float(row[7])
        # 45 Features including cosine, from column 8 till the end
        tempDict[row[0]]['Features'] = row[8:len(row)]
    return tempDict


def parse_cosine(path):
    return load(open(path, 'r'))


f_index = [0, 1, 4, 6, 9, 10, 17, 22, 23, 27, 30, 32, 36, 37, 40, 41, 42, 44]


def create_rand_feat(Trainset, feat_index):
    '''
    This is where the features are trimmed according
    to the randomly generated feature index list
    '''
    return [list(map(float, [Trainset[d]['Features'][i]
            for i in feat_index])) for d in Trainset]


Trainset = parse_csv(TrainPath)
Testset = parse_csv(HoldoutPath)


newTrain = OrderedDict()
newTest = OrderedDict()
# Train and testset are permuted here, to change the training
# and holdout sets as per a random setting
if premute_train_test is True:
    # Generate a randomly shuffled list of indices
    k = list(range(len(Trainset) + len(Testset)))
    np.random.shuffle(k)
    for count, i in enumerate(k):
        item = None
        if i <= 74:
            item = Trainset.items()[i]
            # Take the data from the Trainset
        else:
            # Take the data from the Testset
            item = Testset.items()[i - 75]

        if count <= TrainSize - 1:
            newTrain[item[0]] = item[1]
        else:
            newTest[item[0]] = item[1]

    Trainset = newTrain
    Testset = newTest

    print 'Movies in Training Set: ', Trainset.keys()
    print '\nMovies in Holdout Set:', Testset.keys()

#############################################################


# The actual ROI of movies
trainROI = [Trainset[k]['AROI'] for k in Trainset]
# The test ROI
testROI = [Testset[k]['AROI'] for k in Testset]

# Original With Cosine, Original without Cosine, Reduced with Cosine
testTypes = {'OWC': 'PredOrigWithCosine.csv',
             'OWtC': 'PredOrigWithoutCosine.csv',
             'RWC': 'PredReducedWithCosine.csv'}


classifier = RandomForestRegressor(n_estimators=numTrees,
                                   max_depth=max_d,
                                   min_samples_split=mss)

for i in testTypes:
    # Cosine features are included by default in the FinalTrain.csv last column
    # So we will remove them if we are not using the cosine features
    if i == 'OWtC':
        trainfeatures = [Trainset[k]['Features'][:-1] for k in Trainset]
        testfeatures = [Testset[k]['Features'][:-1] for k in Testset]
    elif i == 'OWC':
        # Cosine already included by default
        trainfeatures = [Trainset[k]['Features'] for k in Trainset]
        testfeatures = [Testset[k]['Features'] for k in Testset]
    else:
        trainfeatures = create_rand_feat(Trainset, f_index)
        testfeatures = create_rand_feat(Testset, f_index)

    print 'Running random forest ensemble for', testTypes[i].split('.')[0]

    f = open(testTypes[i], 'w')
    # Write the file header
    f.write('Name, AROI, CROI, MYROI\n')

    classifier.fit(trainfeatures, trainROI)
    # Compute the predicted ROIs and store them in an array
    predictROI = classifier.predict(testfeatures)

    # Write the results to a csv file with the name of the test
    print 'Writing the results to a csv file in the current directory'
    for i, k in enumerate(Testset):
        f.write(str(k) + ',' + str(Testset[k]['AROI']) +
                ',' + str(Testset[k]['PROI']) + ',' + str(predictROI[i])
                + '\n')

    # Write it to the corresponding csv file
    print 'R2:' + str(round(r2_score(testROI, predictROI), 6))
    print 'MSE:' + str(round(mean_squared_error(testROI, predictROI), 6))
    print 'MAE:' + str(round(mean_absolute_error(testROI, predictROI), 6))
    print

    f.close()
