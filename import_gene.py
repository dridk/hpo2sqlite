#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
import os
from model import *
import sys
from peewee import *
from tqdm import tqdm

#  Gene to phenotypes
#  http://compbio.charite.de/jenkins/job/hpo.annotations.monthly/lastSuccessfulBuild/artifact/annotation/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt
gene_file = str(sys.argv[1])


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i : i + n]


db = SqliteDatabase("hpo.db")

try:
    db.create_tables([Genes, Genes_has_Terms],safe=False)
except:
    print("cannot create tables")


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
    Genes.insert_many(data_source).execute()

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
    for items in tqdm(list(chunks(hpo_genes, 100))):
        Genes_has_Terms.insert_many(items).execute()
