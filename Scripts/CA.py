# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 22:44:23 2014

@author: Lanfear
"""

import numpy as np
from numpy.linalg import svd
 
class CA(object):
    """Simple corresondence analysis.   
    Notes
    -----
    The implementation follows that presented in 'Correspondence
    Analysis in R, with Two- and Three-dimensional Graphics: The ca
    Package,' Journal of Statistical Software, May 2007, Volume 20,
    Issue 3.
    """
    def __init__(self, ct):
        self.rows = ct.index.values if hasattr(ct, 'index') else None
        self.cols = ct.columns.values if hasattr(ct, 'columns') else None
        
        # contingency table
        N = np.matrix(ct, dtype=float)
 
        # correspondence matrix from contingency table
        P = N / N.sum()
 
        # row and column marginal totals of P as vectors
        r = P.sum(axis = 1)
        c = P.sum(axis = 0).T
 
        # diagonal matrices of row/column sums
        D_r_rsq = np.diag(1./ np.sqrt(r.A1))
        D_c_rsq = np.diag(1./ np.sqrt(c.A1))
 
        # the matrix of standarized residuals
        S = D_r_rsq * (P - r * c.T) * D_c_rsq
 
        # compute the SVD
        U, D_a, V = svd(S, full_matrices=False)
        D_a = np.asmatrix(np.diag(D_a))
        V = V.T
 
        # principal coordinates of rows
        F = D_r_rsq * U * D_a
 
        # principal coordinates of columns
        G = D_c_rsq * V * D_a
 
        # standard coordinates of rows
        X = D_r_rsq * U
 
        # standard coordinates of columns
        Y = D_c_rsq * V
 
        # the total variance of the data matrix
        inertia = sum([(P[i,j] - r[i,0] * c[j,0])**2 / (r[i,0] * c[j,0])
                       for i in range(N.shape[0])
                       for j in range(N.shape[1])])
 
        self.F = F.A
        self.G = G.A
        self.X = X.A
        self.Y = Y.A
        self.inertia = inertia
        self.eigenvals = np.diag(D_a)**2
        P = self.X
        Del = D_a
        F = np.around(P * Del, decimals=4)
        print F
        
        
X = np.array([[7836, 13112, 6026],
                  [53655, 102383, 42413],
                  [115615, 184541, 59226],
                  [161926, 340479, 62754],
                  [38177, 105101, 12670],
                  [46371, 58367, 14299]])
    
CA(X)