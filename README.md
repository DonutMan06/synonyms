![synonyms_picture](https://github.com/DonutMan06/DonutMan06/blob/main/syno.png)

# synonyms
Some basic tools to play with a given french thesaurus
The thesaurus comes from [grammalecte](https://grammalecte.net/download.php?prj=fr) under the LGPL licence.

This project can compute the shortest path between any two given french word<sup>[1](#myf1)</sup>. For example, how can we link a king ("roi" in french) to a bird ("oiseau" in french) ?

```
python > shortest_path("roi", "oiseau")
Path length : 5
roi -> autocrate -> chef -> coq -> oiseau
```
You can see that the french word "coq" (which means "rooster") is the keystone between "king" and "bird" since it can be related to the both words. That's an automatic way to find ambiguity in the words. Many other examples can be obtained with this function.

What are the top-5 french words that are defined by the biggest synonyms set ?
```
python > print(ps.tail(5)[::-1])
trouble    186
délicat    184
fort       184
fin        176
vif        161
dtype: int64
```

The main results obtained by using this project are presented on [my personal blog](https://donutblog.fr/litterature/tous-les-mots-sont-freres/) (but it's in french).

## Installation

Clone this project and create a new Python virtual environment, activate it and install the dependancies of this project (mainly scientific stuff like numpy, scipy, pandas and matplotlib)

```
$ python -m venv /path/to/virtualenv/
$ source /path/to/virtualenv/bin/activate
$ cd /path/to/synonyms/
$ pip install -r requirements.txt
```

Then you need to download the thesaurus and convert it to a useable Python format

```
$ cd /path/to/synonyms/
$ mkdir - p ./data/{step0,step1}
$ make matrix
```

## Usage

All the data are stored in the `./data` directory
All the code (both scripts and modules) are stored in the `./synonymns` directory

Here is a brief description of each part of the project

### create_matrix

This should be launched only once by the Makefile (but it could also be run manually).
The aim of this very simple Python script is :
1. to read and parse the initial thesaurus file
2. to automatically find and delete irrelevant synonyms (basically all the synonyms that are not in the dictionary keys)
3. to convert the final structure into a Scipy COO sparse matrix format

### matrix_computation

This is also an another basic Python script that illustrates the issue of time computation when handling sparse matrix of different densities. The bigger the matrix density is, the bigger the time computation grows. Of course it follows a non-linear scheme.

### simple_dijkstra

This is a canonical implementation of the Dijkstra's algorithm of shortest path computation.
Even if this will not be directly used for our study (because Scipy provides optimized Dijkstra's algorithm on sparse matrix), it is a good tool for manipulating the algorithm (which basically remains the same)

### synonyms

The main part of the project. Here are defined all the functions that are used in the Blog article.

This module starts by loading and computing three different structures that are used by the other functions :
1. graph which is the sparse matrix that represents the adjacency matrix of our thesaurus
2. names which is the list of the entries of our thesaurus
3. table which is a dictionary that gives the rank of any given entry

We describe hereafter the prototype of three main functions : `definitions_length()`, `shortest_path()` and `compute_syno_set()`

#### definitions_length

Function prototype : `definitions_length(graph)`

This function returns the number of neighbours of each node of the graph. That is to say, for each word in the dictionary, this functions returns the number of synonyms.


#### shortest_path

Function prototype : `shortest_path(word1, word2)`

This function computes and prints the shortest path from word1 to word2.

It does nothing if either word1 or word2 does not belong to the graph

#### compute_syno_set

Function prototype : `compute_syno_set(graph, word, itermax=20)`

This functions explicitly constructs the growing sets of order-k synonyms of a given word up to iteration max number (defaut : 20).
The output of this function can be used to plot the way the size of the order-k synonyms set grows with k (see for example the picture at the begining of this README.md)


## Limitations and known issues

First of all this french thesaurus has not been updated from a long time and suffers from several [known issues](https://grammalecte.net/documentationthes.php?prj=fr); the biggest appears to be the **lack of disambiguity for polysemic words**. We can understand our shortest_path() function as a way to spot these kind of ambiguities. But one can checks that either the [CNRTL french thesaurus](https://www.cnrtl.fr/synonymie/coq) itself does not make any difference between the different meanings of the word "coq". By the way, as far as I searched the Net, Grammelecte appeared to be the ONLY free (as in freedom) french dictionary; and despite this disambiguity issue, I think that the main results presented here are still interesting.

Secondly, the **sparse matrix computation** appeared to be very time consuming as the matrix density grows. At some point, it may eventually becomes bigger than the time needed for regular matrix computation. This currently prevents us from computing iterations on the graph above order 2. This is not truly limitative since other functions has been developped to skirt this issue (see for example `compute_syno_set()`). I think about one or two ideas in order to accelerate the processing but I must confess that I didn't had the time to check that in depth yet.

Finally, an interesting improvement may be the **use of weighting**. As you can see in the [CNRTL french thesaurus](https://www.cnrtl.fr/synonymie/coq), each synonym is given with a likelihood weight. Currently, the weight are not provided by the Grammalecte thesaurus and the Dijkstra's algortihm does not process them anyway. But this feature can be easily added (as long as the entry thesaurus provides the weight). The improvement can be added in the `shortest_path()` function, in which the `unweighted` parameter of the `sparse.csgraph.dijkstra()` should be switched from `False` to `True`

```
def shortest_path(word1, word2):
  [...]
    (dist_matrix, predecessors) = \
    sparse.csgraph.dijkstra(graph, directed=True, return_predecessors=True,
                            indices=[ind1], limit=limit,
                            unweighted=False, min_only=False)
  [...]
```                            

## Thanks
I would like to thanks Frédéric Labbé and the other people involved in [Grammalecte](http://www.dicollecte.org/thesaurus.php?prj=fr) for sharing under LGPL licence the french thesaurus used here.

<a name="myf1">1</a>: for the reference behind the choice of the words chosen for the example, [click here](https://www.imdb.com/title/tt0079820/) :)
