#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 14:53:09 2021

@author: donutman

This module provides a very simple Dijkstra implementation from scratch
to illustrate the behaviour of more complex algorithms used by numpy.sparse

Usage
-----

As a main call, it will compute a canonical example of minization
over a simple symmetric graph given by Wikipedia
Link : https://fr.wikipedia.org/wiki/Algorithme_de_Dijkstra


As a module, the following functions are provided

Functions
---------

check_symmetry(graph)
    checks if the graph is symmetric (aka NOT oriented)
    
dijkstra(graph, nodes, node_start, node_end)
    computes the shortest path for a given graph from node_start to node_end


"""

import numpy as np

def check_symmetry(graph):
    '''
    This function checks that the graph is NOT oriented

    Parameters
    ----------
    graph : dictionary
        {node : {neighbour_1 : distance_1, ..., neighbour_n : distance_n}}
        a python dictionary that describes the graph
        (see example in the main section below)

    Returns
    -------
    result : boolean
        True if the graph is symmetric (aka NOT oriented), False otherwise

    '''
    result = True
    for (node, links) in graph.items():
        for (child_node, length) in links.items():
            child_length = graph[child_node]
            if (not node in child_length) and child_length[node] != length:
                result=False
                break
        if result ==  False:
            break
    return result


def _find_min(Q, d):
    '''
    This *internal* function returns among the node list Q
    the node that minimize the distance d wrt the node_start

    Parameters
    ----------
    Q : str list
        the nodes list in which the minimun has to be found
    d : dictionary {node : distance}
        for each node, the distance with the node_start is stored here
        if not computed yet, it is assumed to be set to np.inf

    Returns
    -------
    node : str
        the node for which the minimum distance wrt to the node_start
        has been found

    '''
    mini = np.inf
    node = -1
    for s in Q:
        if d[s] < mini:
            mini = d[s]
            node = s
    return node

def _update_distance(node1, node2, d, pred, graph):
    '''
    This *internal* function updates the distance vector
    if the distance computed at a given iteration are smaller
    than the ones stored in the distance vector

    Parameters
    ----------
    node1 : str
        the node processed at a given iteration of the Dijkstra algorithm
    node2 : str
        one of the node1 neighbours
    d : dictionary {node : distance}
        for each node, the distance with the node_start is stored here
        if not computed yet, it is assumed to be set to np.inf
    pred : str list
        predecessor vector that ultimately creates a path from node_start
        to node_end
    graph : dictionary
        {node : {neighbour_1 : distance_1, ..., neighbour_n : distance_n}}
        a python dictionary that describes the graph
        (see example in the main section below)

    Returns
    -------
    None.

    '''
    if d[node2] > d[node1] + graph[node1][node2]:
        d[node2] = d[node1] + graph[node1][node2]
        pred[node2] = node1

def dijkstra(graph, nodes, node_start, node_end):
    '''
    This is the main function of this module
    For a given graph and list of node, it computes the shortest path
    from node_start to node_end.
    The graph can be oriented or not, it will work in both cases.
    This function returns nothing but just prints the shortest path
    as an illustration of how the Dijkstra algorithm works.

    Parameters
    ----------
    graph : dictionary
        {node : {neighbour_1 : distance_1, ..., neighbour_n : distance_n}}
        a python dictionary that describes the graph
        (see example in the main section below)
    nodes : str list
        The list of nodes name. This should not be mandatory as it can be
        derived from the graph variable. It will eventually be removed
        in a future release.
    node_start : str
        the name of the starting node
    node_end : str
        the name of the ending node

    Returns
    -------
    None.

    '''
    
    # Initialization
    Q = nodes
    
    n = len(nodes)
    d = dict( zip(nodes, [np.inf]*n) )
    d[node_start] = 0
    
    pred = {}
    
    while len(Q) > 0:
        node1 = _find_min(Q, d)
        Q.remove(node1)
        
        for node2 in graph[node1].keys():
            _update_distance(node1, node2, d, pred, graph)
    
    
    # Now we print the shortest path from node_start to node_end
    A = []
    node = node_end
    
    while node != node_start:
        A += node
        node = pred[node]
    
    A+=node_start

    print('-'.join(A))
    

if __name__ == '__main__':
    
    # We illustrate the module execution through an example given on Wikipedia
    # https://fr.wikipedia.org/wiki/Algorithme_de_Dijkstra
    
    graph = {
        "A" : {"B":85, "C":217, "E":173},
        "B" : {"A":85, "F":80},
        "C" : {"A":217, "G":186, "H":103},
        "D" : {"H":183},
        "E" : {"A":173, "J":502},
        "F" : {"B":80, "I":250},
        "G" : {"C":186},
        "H" : {"C":103, "D":183, "J":167},
        "I" : {"F":250, "J":84},
        "J" : {"I":84, "H":167, "E":502},}
    
    nodes = list(graph.keys())
    
    # We check that the graph is symmetric (i.e. NOT oriented)
    print(check_symmetry(graph))
    
    dijsktra(graph, nodes, "A", "J")




