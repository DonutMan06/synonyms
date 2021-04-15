#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 20:48:14 2021

@author: donutman

This module provides the main functions used for french thesaurus study


Usage
-----

As a main call, it will compute and plot the different cases described in the article
TBD

As a module, it will export the following functions

Functions
---------


Assumption
----------

The dictionary is stored in sparse matrix COO format in the following file
../data/step1/thesaurus_matrix.npz

The dictionary index is stored in the following file
../data/step1/thesaurus_entries.npz

These two files are created by
$ make matrix

You can also run directly the create_matrix.py script

"""

from scipy import sparse
import numpy as np
from matplotlib import rc, pyplot as plt
import pandas as pd

# Global fontsize for plots
_fontsize = 22

rc('xtick', labelsize=_fontsize) 
rc('ytick', labelsize=_fontsize) 


# We load/compute the main strucutres that are used : graph, names and table
# graph is the sparse matrix that represents the adjacency matrix of our thesaurus
# names is the list of the entries of our thesaurus
# table is a dictionary that gives the rank of any given entry

graph = sparse.load_npz('../data/step1/thesaurus_matrix.npz')
names = np.load('../data/step1/thesaurus_entries.npz')['names']

table = {n:k for (k, n) in enumerate(names)}


def shortest_path(word1, word2):
    '''
    This function computes and prints the shortest path from word1 to word2.
    It does nothing if either word1 or word2 does not belong to the graph

    Parameters
    ----------
    word1 : str
        starting node for shortest path computation
    word2 : str
        ending node for shortest path computation

    Returns
    -------
    None.

    '''
    if (not word1 in names):
        print('Error : %s does not belong to the dictionary' % word1)
        return
    
    if (not word2 in names):
        print('Error : %s does not belong to the dictionary' % word2)
        return
    
    ind1 = table[word1]
    ind2 = table[word2]
    
    limit = 100 # We do not compute path above 100 heaps
    
    (dist_matrix, predecessors) = \
    sparse.csgraph.dijkstra(graph, directed=True, return_predecessors=True,
                            indices=[ind1], limit=limit,
                            unweighted=True, min_only=False)
    
    
    path_length = dist_matrix[0][ind2]
    
    if path_length == np.inf:
        print('Path length : above %d heap limit value' % limit)
    else:
        print('Path length : %d' % path_length)
        path_names = [];
        while ind2 != ind1:
            path_names.append(names[ind2])
            ind2 = predecessors[0][ind2]
        
        path_names.append(names[ind1])
        path_names.reverse()
        print(' -> '.join(path_names))
            
def definitions_length(graph):
    '''
    This function returns the number of neighbours of each node of the graph
    That is to say, for each word in the dictionary, this functions returns
    the number of synonyms

    Parameters
    ----------
    graph : sparse matrix (in COO format, but other formats might work as well)
        the adjecency matrix that describes the thesaurus

    Returns
    -------
    int list
        the kth word of the thesaurus is defined with output[k] synonyms'''
    return np.array(graph.sum(1))


def get_next(graph):
    '''
    This function returns the next order of a given graph
    If graph is the initial sparse matrix, and e_k = [0, ..., 0, 1, 0, ..., 0]
    then graph*e_k returns the list of synonyms of word e_k
    and get_next_(graph)*e_k return the list of synonyms of synonyms of word e_k
    and so on...
    Please note that this function becomes slower as the matrix density grows !
    (see matrix_computation.py script for an analysis of this effect)

    Parameters
    ----------
    graph : sparse matrix
        COO is usually used but other formats should work as well as far as
        the .dot() method is available
        the adjecency matrix that describes the thesaurus of a given order

    Returns
    -------
    sparse matrix in the same format as input
        the adjecency matrix that describes the thesaurus of the next order

    '''
    # This does not work since it element wise 
    #return graph.multiply(graph)
    
    return graph.dot(graph)


def print_synonyms(word, graph, order):
    '''
    This function prints the synonyms of a given order for the given word
    Please notice that this still need some improvements since the time
    computation for the graph^order is extremely large for order >= 2

    Parameters
    ----------
    word  : str
        the word that you want to compute the order-k synonyms list
    graph : sparse matrix (in COO format, but other formats might work as well)
        the adjecency matrix that describes the thesaurus
    order : int
        the order of the synonyms to be computed
        0 means the direct synonyms of the given word
        1 means the synonyms of the direct synonyms of the given word
        etc...
        Please note that actually only order 0 and 1 should be used

    Returns
    -------
    None.

    '''
    if (not word in names):
        print('Error : %s does not belong to the dictionary' % word)
        return
    
    # Initialization of the matrix
    M = graph
    
    for k in range(order):
        print('Multiplication order %d...' % k)
        M = get_next(M)
    
    # We trasnform M in ndarray format in order to access elements
    M = M.toarray()
    
    ind = table[word]
    
    ind_syno = np.where(M[ind,:])[0]
    
    for k in ind_syno:
        print(names[k])

def sp_unique(sp_matrix, axis=0):
    '''
    This function returns a sparse matrix with the unique rows (axis=0)
    or columns (axis=1) of an input sparse matrix sp_matrix.
    This is still experimental but we might use it in the future in order
    to reduce the computation time needed for computing the order-k synonyms
    list.

    Parameters
    ----------
    sp_matrix : sparse matrix (in any format COO, CSR, LIL etc...)
        the initial sparse matrix
    axis : int, optional
        The axis along which the unique vectors are to be computed.
        The default is 0.

    Returns
    -------
    ret : sparse matrix in the same format as sparse_matrix input
        A sparse matrix equal to sparse_matrix input but redundant rows
        (axis=0) or redundant columns (axis=1) have been removed

    '''
    if axis == 1:
        sp_matrix = sp_matrix.T

    old_format = sp_matrix.getformat()
    dt = np.dtype(sp_matrix)
    ncols = sp_matrix.shape[1]

    if old_format != 'lil':
        sp_matrix = sp_matrix.tolil()

    _, ind = np.unique(sp_matrix.data + sp_matrix.rows, return_index=True)
    rows = sp_matrix.rows[ind]
    data = sp_matrix.data[ind]
    nrows_uniq = data.shape[0]

    sp_matrix = sparse.lil_matrix((nrows_uniq, ncols), dtype=dt)  #  or sp_matrix.resize(nrows_uniq, ncols)
    sp_matrix.data = data
    sp_matrix.rows = rows

    ret = sp_matrix.asformat(old_format)
    if axis == 1:
        ret = ret.T        
    return ret


def compute_syno_set(graph, word, itermax=20):
    '''
    This functions explicitly constructs the growing sets of order-k synonyms
    of a given word up to iteration max number (defaut : 20).
    Notice that it is a little bit faster than print_synonyms() because
    we do not compute the entire matrix multiplication but only on the
    relevant rows.

    Parameters
    ----------
    graph : sparse matrix (in COO format, but other formats might work as well)
        the adjecency matrix that describes the thesaurus
    word  : str
        the initial word that will be used as a seed for our incremental
        order-k synonyms list
    itermax : int, optional
        the computation will stop after itermax iteration. The default is 20.
        Preliminary tests have shown that around 10 iterations seems to be
        sufficient for getting an invariant set. Or in other word, it seems
        that order-11 synonyms list of any given word is equal to order-10
        synonyms list (this have been verified over a few random words but
        we can't say it is true for ANY word in the thesaurus...)

    Returns
    -------
    iteration_vect : int list
        this is just a range vector [1, 2, ..., n] of the iteration
        (used mainly for plotting)
    size_set_vect : int list
        size_set_vect[k] contains the cardinality of order-k synonyms list

    '''
    if (not word in names):
        print('Error : %s does not belong to the dictionary' % word)
        return
    
    M = graph.todense()
    
    ind = table[word]
    syno_set = set([ind])
    size_set = 1
    iteration = 1
    
    size_set_vect = [size_set]
    iteration_vect = [iteration]
    
    same_size = False
    
    while (same_size==False) and (iteration < itermax):
        print('Iteration %d...' % iteration)
        # We construct the set
        for k in syno_set:
            line = np.array(M[k][:]).flatten()
            new_syno = np.where(line==True)[0]
            syno_set = syno_set.union(set(new_syno))
        
        if len(syno_set) == size_set:
            same_size = True
        
        size_set = len(syno_set)
        
        size_set_vect.append(size_set)
        iteration += 1
        
         
    iteration_vect = range(0, iteration)
        
    return (iteration_vect, size_set_vect)
        

if __name__ == '__main__':
    
    # Some example of shortest_path usage
    shortest_path("marionnette", "enfant")    
    shortest_path("poisson", "chat")
    shortest_path("chat", "poisson")
    
    # Computation of definitions length and conversion to a pandas Series
    p = definitions_length(graph)
    ps = pd.Series(data=p[:,0], index=names)
    
    # Histogram plot
    plt.close('all')
    
    legend = 'min : %d, mean : %3.1f, max = %d' % (p.min(), p.mean(), p.max())
    n, bins, patches = plt.hist(x=p, bins=range(p.max()), color=[1,0,0], 
                                alpha=0.7, label=legend)
    
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Definition length', fontsize=_fontsize)
    plt.ylabel('Frequency', fontsize=_fontsize)
    plt.title('Number of synonyms', fontsize=_fontsize)
    leg = plt.gca().legend(fontsize=_fontsize)
    maxdef = n.max()

    # Sort of ps pandas Series
    ps.sort_values(inplace=True)
    ps = ps[ps>0]
    
    # The first ten entries
    print('\n--> The first 10 entries')
    print(ps.head(10))
    
    # The last ten entries
    print('\n--> the last ten entries')
    print(ps.tail(10)[::-1])
        
    
    # Iterate for a given word
    
    (x, y) = compute_syno_set(graph, "active")
    
    plt.figure()
    plt.plot(x, y, 'r-+')
    
    
    # This still need some work....
    for order in range(3):
        pass
        #print('\n --> Order %d' % order)
        #print_synonyms("manger", graph, order)
        
    
    # print('Computing order graphs...')
    # order_graph = [graph.tocsr()]
    # for k in range(10):
    #     print(k)
    #     order_graph.append(get_next(order_graph[k]))
    
    # print('The plots stuff...')
    # plt.figure()
    # for order in range(3):
    #     syno_sets, syno_sets_length, nsets = compute_syno_set(order_graph[order])
        
    #     print('There are %d sets of order-%d synonyms' % (nsets, order))
    #     plt.subplot(1,3, order+1)
    #     plt.hist(x=syno_sets_length, color=[1,0,0])
    #     plt.xlabel('Syno sets length')
    #     plt.title('Order %d' % order)
        