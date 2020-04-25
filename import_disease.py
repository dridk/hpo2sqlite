#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from operator import itemgetter
import os
from model import *
import sys
from peewee import * 

# disease 
# http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/phenotype_annotation.tab
disease_file = str(sys.argv[1]) 


db = SqliteDatabase("hpo.db")
db.create_tables([Diseases])


# save all hpo in memory map
hpo = {}
for term in Terms.select():
	hpo[term.hpo] = term



with open(disease_file, "r") as file:
	with db.transaction() as txn:
		for line in file:
			if line.startswith("#"):
				continue
			row  = line.rstrip().split('\t')

			disease = Diseases()
			disease.source     = row[0]
			disease.source_id  = int(row[1])
			disease.name       = row[2]
			disease.term 	   = hpo[row[4]]
			disease.evidence   = row[6]

			disease.save()


	