# -*- coding: utf-8 -*-
"""
Created on Sat Dec  6 12:58:06 2014

@author: Lanfear
"""

from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import BaggingRegressor
from sklearn.metrics import r2_score
from collections import OrderedDict
from random import uniform
from math import sin, cos, pi, sqrt

numTrees = 50
numTests = 1000
numSamples = 100
numTestSamples = 20
weightw1 = 2
weightw2 = 3


def randSin():
    return sin(uniform(0, 180) * pi / 180)


def randCos():
    return cos(uniform(0, 180) * pi / 180)


def EuclidDist(v1, v2, w):
    return sqrt((w - v1) ** 2 + (w - v2) ** 2)


def weightedAvg(w1, w2):
    '''
    Features of the tree are the sine function, the cosine function
    and a EuclidDist between the point and these two functions.
    The prediction result is the weighted average of the two input
    functions i.e., res is the result
    '''
    F1 = randSin()
    F2 = randCos()
    WeightedAvg = (w1 * F1 + w2 * F2) / float(w1 + w2)
    F3 = EuclidDist(F1, F2, WeightedAvg)
    return {'F1': F1, 'F2': F2, 'F3': F3,
            'Res': WeightedAvg}


def GenSamples(Samples):
    SampleSet = []
    for i in xrange(Samples):
        res = weightedAvg(weightw1, weightw2)
        SampleSet.append(res)
    return SampleSet


def extractFeatures(inputList):
    return [[k['F1'], k['F2'], k['F3']] for k in inputList]


def extractPred(inputList):
    return [k['Res'] for k in inputList]


def runTests():

    # Generate the training samples, extract training features and target
    trainSamples = GenSamples(numSamples)
    trainFeatures = extractFeatures(trainSamples)
    trainPred = extractPred(trainSamples)

    # Generate the test samples, extracr test features and target
    testSamples = GenSamples(numTestSamples)
    testFeatures = extractFeatures(testSamples)
    testPred = extractPred(testSamples)

    R2List = OrderedDict()
    R2List['TrainROI'] = []
    R2List['TestROI'] = []
    print 'Running Tests: '
    for i in range(numTests):
        # Bootstrap is True by default i.e., sampling with replacement
        # Bootstrap features is False by default i.e., all features used
        classifier = BaggingRegressor(base_estimator=DecisionTreeRegressor(),
                                      n_estimators=numTrees,
                                      max_samples=int(0.5*numSamples),
                                      max_features=int(1))

        classifier.fit(trainFeatures, trainPred)
        predictROI = {}
        predictROI['Training'] = classifier.predict(trainFeatures)
        predictROI['Test'] = classifier.predict(testFeatures)

        R2 = {}
        R2['Train'] = r2_score(trainPred, predictROI['Training'])
        R2['Test'] = r2_score(testPred, predictROI['Test'])

        R2List['TrainROI'].append(R2['Train'])
        R2List['TestROI'].append(R2['Test'])

    print 'Best Train ROI: ', max(R2List['TrainROI'])
    print 'Best Test ROI: ', max(R2List['TestROI'])

if __name__ == '__main__':
    runTests()
