#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
import os
from model import *
import sys
from peewee import *

#  Gene to phenotypes
#  http://compbio.charite.de/jenkins/job/hpo.annotations.monthly/lastSuccessfulBuild/artifact/annotation/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt
gene_file = str(sys.argv[1])


db = SqliteDatabase("hpo.db")

try:
    db.create_tables([Genes, Term_has_Genes])
except:
    pass


# save all hpo in memory map
hpo = {}
for term in Terms.select():
    hpo[term.hpo] = term


# Load all genes
genes = set()
print("create genes tables")
with open(gene_file, "r") as file:
    next(file)
    for line in file:
        row = line.rstrip().split("\t")
        # entrezid / gene symbole
        genes.add((int(row[2]), row[3]))


data_source = [{"entrez_id": i[0], "name": i[1]} for i in genes]

with db.atomic():
    Genes.insert_many(data_source)

    # for data_dict in data_source:
    #    Genes.create(**data_dict)


# save all hpo in memory map
genes = {}
for gene in Genes.select():
    genes[gene.name] = gene


# Save hpo_has_gene
hpo_genes = []
print("create hpo_has_gene tables")

with open(gene_file, "r") as file:
    next(file)
    for line in file:
        row = line.rstrip().split("\t")
        gene = genes[row[3]]
        term = hpo[row[0]]

        hpo_genes.append({"term": term.id, "gene": gene.id})


with db.atomic():
    Genes_has_Terms.insert_many(hpo_genes)
