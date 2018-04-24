#!/usr/bin/env python
# -*- coding: utf-8 -*-
import networkx as nx 
import obonet as obo 
from collections import defaultdict
from operator import itemgetter
from peewee import * 


# Create Sqlite model 

db = SqliteDatabase("hpo.db")

class HPO(Model):
    name   = CharField()
    hpo_id = CharField()
    left   = IntegerField()
    right  = IntegerField()

    class Meta:
        database = db 


db.connect()
db.create_tables([HPO])


# Get hpo obo and create a directed graph 
print("Download obo hpo")
obograph = nx.DiGraph(obo.read_obo("http://purl.obolibrary.org/obo/hp.obo"))

# Convert Dag To Tree ( create duplicate)
print("Convert HPO DAG to Tree")
obotree = nx.dag_to_branching(obograph)

# Create dict["HPO_TERM"] =[UUID,UUID....]
sources = defaultdict(set)
for v, source in obotree.nodes(data='source'):
    sources[source].add(v)

for source, nodes in sources.items():
    for v in nodes:
        obotree.node[v].update(obograph.node[source])


# Deap First search transversal 
# Create SQL statement for a nested set model
# see https://en.wikipedia.org/wiki/Nested_set_model
print("Compute left and right border")
index = 0
for i in nx.dfs_labeled_edges(obotree):
    
    # i contains label node A , label node B, direction
    node_name_1   = i[0]
    node_name_2   = i[1] 
    sens          = i[2]

    if sens == "forward":
            obotree.node[node_name_2].update({"left": index})


    if sens == "reverse":
            obotree.node[node_name_2].update({"right": index})

    index+=1


# Generate SQL 
print("Insert HPO in SQLITE database")
with db.transaction() as txn:
    for i in obotree:
        item = HPO()
        item.name   = obotree.node[i]["name"]
        item.hpo_id = obotree.node[i]["source"]
        item.left   = obotree.node[i]["left"]
        item.right  = obotree.node[i]["right"]
        print("save {} ".format(item.hpo_id))
        item.save()


