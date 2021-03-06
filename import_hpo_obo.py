#!/usr/bin/env python
# -*- coding: utf-8 -*-
import networkx as nx 
import obonet as obo 
import pickle
from collections import defaultdict
from operator import itemgetter
import os
import model 
import hashlib
import datetime
import sys

# =========================================================================================

def read_obo_version(obofile):
    with open(obofile,"r") as file:
        for line in file:
            if line.startswith("data-version"):
                return line.split(":")[1].strip()



def dag_from_obo(obofile):
    """ Return a directed acyclic graph from obo ontology """
    return nx.DiGraph(obo.read_obo(obofile)).reverse()


def tree_from_dag(dag):
    """ Transform DAG into Tree by splitting node with multiple parents. It takes a while """ 
    return nx.dag_to_branching(obograph)


def visit_tree(tree):
    """ 
    Visit node tree and assign left and right index according Nested set algorithm 
    https://en.wikipedia.org/wiki/Nested_set_model
    """ 
    index  = 0
    depth  = 0
    parent = None
    for i in nx.dfs_labeled_edges(tree):
        node_name_1   = i[0]
        node_name_2   = i[1] 
        sens          = i[2]


        if sens == "forward":
            depth+=1
            parent = node_name_1
            tree.nodes[node_name_2].update({"left": index, "depth":depth, "parent": parent})

        if sens == "reverse":
            depth-=1
            tree.nodes[node_name_2].update({"right": index, "depth":depth})

        index+=1

    return tree 

# =========================================================================================
if __name__ == "__main__":


	obo_filename = str(sys.argv[1]) 



	print("loading obo ", obo_filename)
	#obograph = pickle.load(open("obograph.pickle","rb"))
	obograph = dag_from_obo("http://purl.obolibrary.org/obo/hp.obo")

	print("converting dag to tree. It can takes a while ...")
	#obotree  = pickle.load(open("obotree.pickle","rb"))
	obotree  = tree_from_dag(obograph)

	# Compute border
	print("Visiting tree")
	tree = visit_tree(obotree)


	model.create_database_shema()


	model.Informations( hpo_version = read_obo_version(obo_filename), 
	                    hpo_md5     = hashlib.md5(open(obo_filename,'rb').read()).hexdigest(),
	                    saved_by    = "Sacha Schutz",
	                    version     =  str(datetime.datetime.now())
	                  ).save()



	# Store all terms 
	print("Storing terms")
	all_terms = dict()

	with model.db.transaction() as txn:
	    for node in obograph.nodes(data=True):
	        term            = model.Terms()
	        term.hpo        = node[0] 
	        term.name       = node[1].get("name")
	        term.definition = node[1].get("def","")
	        term.comment    = node[1].get("comment","")
	        
	        term.save()

	        all_terms[term.hpo] = term


	# Compute SQL 
	print("Storing nodes")
	with model.db.transaction() as txn:
	    for i in obotree.nodes(data=True):
	        item           = model.Nodes()
	        item.name      = i[0]
	        item.left      = i[1]["left"]
	        item.right     = i[1]["right"]
	        item.depth     = i[1]["depth"]
	        item.term      = all_terms[i[1]["source"]]

	        try:
	        	item.parent = model.Nodes.get(model.Nodes.name == i[1]["parent"])
	        except:
	        	print("cannot store with item.parent=", i[1]["parent"])


	        item.save()


