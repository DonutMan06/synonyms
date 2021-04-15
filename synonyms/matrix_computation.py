#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 20:56:56 2021

@author: donutman

This Python script illustrates some issues related with sparse matrix time
computation. More specifically, it shows how the matrix multiplication
time grows as the matrix density increases.

This SHOULD NOT be used as a module

"""

import numpy as np
from scipy import sparse
from timeit import timeit
from matplotlib import rc, pyplot as plt

if __name__ == '__main__':
        
    ## STEP 1 ##
    # We assess the computation time for sparse matrix multiplication
    # as a function of the density of the matrix
    
    N = 36000   # Matrix size
    repeat = 1  # Number of iteration for statistics purpose
    fs = 22     # Fontsize for plot

    # Global fontsize for plots
    rc('xtick', labelsize=fs) 
    rc('ytick', labelsize=fs) 
    #rc('text', usetex=True)
    
    # This vector contains the matrix density (number of '1' values)
    # and will be looped
    n = np.floor(np.logspace(0,7,7+1)).astype(int)
    
    R = np.zeros((len(n), repeat)) # Result vector (time in s)
    
    
    for (rank, kn) in enumerate(n):
        
        print('- Testing for number of 1 = %d' % kn)
        
        for kr  in range(repeat):
            I = np.random.randint(0, N, kn)
            J = np.random.randint(0, N, kn)
            V = [True]*kn
            
            M = sparse.csr_matrix((V, (I,J)), shape=(N, N), dtype=bool)
            
            # We assess the dot product execution time
            print('Accessing to R[%d][%d]' % (rank, kr))
            R[rank][kr] = timeit(stmt = "M.dot(M)", globals=globals(), number=1)
    
    
    mean_values = R.mean(axis=1)
    #std_values = R.std(axis=1) # This may be used iif repeat >= 3
    
    
    # Figure 1
    plt.figure()
    plt.plot(n, mean_values,
                 lw=3, c='k', ls='-', marker='+', ms=15, mew=3)
    
    plt.gca().set_xscale("log")
    plt.gca().set_yscale("log")
    plt.grid(color=[.7, .7, .7])
    plt.xlabel('Number of non-zero values', fontsize=fs)
    plt.ylabel('Execution time in s', fontsize=fs)
    plt.title('Complexity of sparse matrix multiplication', fontsize=fs)
    
    
    ## STEP 2 ##
    # We perform the same operation as step 1 but
    # 1 - for a smaller matrix size (1000 instead of 36000)
    # 2 - we compare the performance of sparse matrix multiplication
    #     with the dot product of regular matrix
    # 3 - the matrices are not more filled with 1 but instead we introduce two
    #     random matrices with integers coefficients
    
    N = 1000; # Matrix size
    
    # This vector contains the matrix density (number of '1' values)
    # and will be looped    
    n = np.linspace(1,N*N,25).astype(int) # Number of ones
    
    t_sparse = np.zeros(len(n)) # Computation time vector for sparse matrix
    t_dense  = np.zeros(len(n)) # Computation time vector for regular matrix
                          
    for (rank, kn) in enumerate(n):
        print("%d/%d" % (rank, len(n)))
        I = np.random.randint(0, N, kn)
        J = np.random.randint(0, N, kn)
        V = np.random.randint(0, N, kn)
        
        M_sparse_1 = sparse.csr_matrix((V, (I,J)), shape=(N, N), dtype=bool)  
        M_dense_1  = M_sparse.todense()
         
        I = np.random.randint(0, N, kn)
        J = np.random.randint(0, N, kn)
        V = np.random.randint(0, N, kn)
        
        M_sparse_2 = sparse.csr_matrix((V, (I,J)), shape=(N, N), dtype=bool)  
        M_dense_2  = M_sparse.todense()
        
        
        t_sparse[rank] = timeit(stmt = "M_sparse_1.dot(M_sparse_2)", globals = globals(), number=1)
        t_dense[rank] = timeit(stmt = "M_dense_1.dot(M_dense_2)", globals = globals(), number=1)
    
    # Figure 2   
    plt.figure()
    plt.plot(n/(N*N)*100, t_sparse, lw=2, c='r', label='sparse')
    plt.plot(n/(N*N)*100, t_dense, lw=2, c='b', label='dense')
    plt.gca().legend(fontsize=fs)
    plt.grid(color=[.7, .7, .7])
    plt.xlabel('Number of non-zero values (percent of total size)', fontsize=fs)
    plt.ylabel('Execution time in s', fontsize=fs)
    plt.title('Complexity of sparse vs dense matrix multiplication', fontsize=fs)
