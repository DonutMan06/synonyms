#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 00:09:39 2021

@author: donutman

This Python script will read the grammalecte french thesaurus stored in
the ./data/step0/ directory, process it a little bit (see below)
and save it in a sparse matrix format under the ./data/step1/ directory

This SHOULD NOT be used as a module

Assumption
----------
The thesaurus is stored in the following filename :
    ./data/step0/thes_fr.dat

Please use 'make matrix' to automatically download and extract the thesaurus


Steps of the algorithm
----------------------

Step 1 : we read the input file and parse the data in a dictionnary structure
Step 2 : we go through the dictionnary and delete synonyms that are NOT
an entry of the dictionnary itself (self consistency check)
Step 3 : conversion to numpy sparse matrix in COO format (fileout1)
as well as a list of the thesaurus keys (fileout2)

Link : https://grammalecte.net/home.php?prj=fr

"""

from scipy import sparse
from numpy import savez

def print_entry(name, syno_list):
    """this function prints out an entry of the thesaurus"""
    print("- %s : %s" %  (name, ' - '.join(syno_list) ) )
    
# Pathnames
filein = './data/step0/thes_fr.dat'
fileout1 = './data/step1/thesaurus_matrix'
fileout2 = './data/step1/thesaurus_entries'


if __name__ == '__main__':
    
    d = {} # empty dictionnary
    name = ""
    syno_list = []
    
    
    # STEP 1 : we read the input file and parse the data in a dictionnary structure
       
    with open(filein, mode='rt', encoding='utf-8') as f:
        next(f) # we skip first line
        for line in f:
            line = line.rstrip('\n')
            if not line.startswith('('): # we read a new entry !
                # First, we need to add the previous entry into our dictionnary
                # But only if name is not empty !
                if not name=="":
                    #print_entry(name, syno_list)
                    d[name] = syno_list
                    syno_list = []
                    
                (name, _) = line.split('|')
            else:
                syno_list_tmp = line.split('|')
                del syno_list_tmp[0]
                syno_list = syno_list + syno_list_tmp
    
    # Now that we read all the entries we need to add the last entry
    d[name] = syno_list
    
    
    
    # STEP 2 : we go through the dictionnary and delete synonyms that are NOT
    # an entry of the dictionnary itself (self consistency check)
         
    d2 = {} # empty dictionnary
    
    for (name, syno_list) in d.items():
        syno_list_2 = [syno for syno in syno_list if syno in d.keys()]
        deleted_words = set(syno_list).symmetric_difference(set(syno_list_2))
        
        if len(deleted_words)>0:
            pass
            # uncomment the following line to see which words are deleted
            #print('- Deleted entries for "%s" : %s' % ( name, " - ".join(deleted_words) ))
        d2[name] = syno_list_2
    
    
    # STEP 3 : Now we want to convert all that in a sparse matrix
    
    keys = tuple(sorted(d2.keys()))
    Nentries = len(keys)
    indices = range(Nentries)
    
    # Construction of I,J,V vectors in COO format
    
    I = []; J = []; V = [];
    
    t = {n:k for (k, n) in enumerate(keys)}
    
    for (name, syno_list) in d2.items():
        rank_key = t[name]
        rank_values = [t[n] for n in syno_list]
        if len(rank_values)>0: # This should always be the case, but we check
            I.extend([rank_key]*len(rank_values))
            J.extend(rank_values)
    
    
    V = [1]*len(I)
    M = sparse.coo_matrix((V, (I,J)), shape=(Nentries, Nentries), dtype=bool)
    
    
    sparse.save_npz(fileout1, M)
    savez(fileout2, names=keys)
