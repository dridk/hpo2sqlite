#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
import os
from model import *
import sys
from peewee import * 

# Gene to phenotypes 
# http://compbio.charite.de/jenkins/job/hpo.annotations.monthly/lastSuccessfulBuild/artifact/annotation/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt
gene_file = str(sys.argv[1]) 


db = SqliteDatabase("hpo.db")

try:
	db.create_tables([Genes,Term_has_Genes])
except:
	pass


# save all hpo in memory map
hpo = {}
for term in Terms.select():
	hpo[term.hpo] = term


# Load all genes 
genes = set()

with open(gene_file, "r") as file:
	next(file)
	for line in file:
		row  = line.rstrip().split('\t')

		genes.add((int(row[0]), row[1]))


data_source = [ {"entrez_id": i[0], "name":i[1]}for i in genes]

print("save gene")
with db.atomic():
	for data_dict in data_source:
		Genes.create(**data_dict)


# save all hpo in memory map
genes = {}
for gene in Genes.select():
	genes[gene.name] = gene


# Save hpo_has_gene 
hpo_genes = []
print("save hpo has gene")

with open(gene_file, "r") as file:
	next(file)
	for line in file:
		row  = line.rstrip().split('\t')

		gene    = genes[row[1]]
		term    = hpo[row[3]]

		hpo_genes.append({"term":term, "gene":gene})


with db.atomic():
    for item in hpo_genes:
        Term_has_Genes.create(**item)