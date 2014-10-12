# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 14:19:55 2014

@author: Lanfear
"""
from CA import CA
from sklearn import tree
from pickle import load
import matplotlib.pylab as plt

filepath = '/Users/Lanfear/Desktop/Research/Scenematrices/Bruce-Almighty_g2.mat'
X = load(open(filepath, 'r'))

ca = CA(X['sceneVector'].T)
res = ca.ComputeCA()

print res
'''
plt.ion()
plt.plot(res[:, 1])
plt.show()
'''