# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 14:19:55 2014

@author: Lanfear
"""

from ca import CA
from pickle import load

filepath = '/Users/Lanfear/Desktop/Research/Scenematrices/13days_g2.mat'
X = load(open(filepath, 'r'))
print X


