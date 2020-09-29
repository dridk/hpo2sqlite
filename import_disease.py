#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from operator import itemgetter
import os
from model import *
import sys
from peewee import *
from tqdm import tqdm


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i : i + n]


#  disease
#  http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/phenotype_annotation.tab
disease_file = str(sys.argv[1])


db = SqliteDatabase("hpo.db")
db.create_tables([Diseases, Disease_has_Terms], safe=False)


ids = set()
diseases = []

print("save diseases")
with open(disease_file, "r") as file:
    with db.transaction() as txn:
        for line in file:
            if line.startswith("#"):
                continue
            row = line.rstrip().split("\t")

            database_id = row[0]
            name = row[1]

            if database_id not in ids:
                ids.add(database_id)
                diseases.append({"database_id": database_id, "name": name})



with db.atomic():
    Diseases.insert_many(diseases).execute()

    # disease = Diseases()
    # disease.source = row[0]
    # disease.source_id = int(row[1])
    # disease.name = row[2]
    # disease.term = hpo[row[4]]
    # disease.evidence = row[6]

    # disease.save()


# save all hpo in memory map
hpo = {}
for term in Terms.select():
    hpo[term.hpo] = term

# save all disease in memory map
diseases = {}
for disease in Diseases.select():
    diseases[disease.database_id] = disease


print("save diseases relation")
relations = []
with open(disease_file, "r") as file:
    with db.transaction() as txn:
        for line in file:
            if line.startswith("#"):
                continue
            row = line.rstrip().split("\t")

            disease_id = diseases[row[0]].id
            hpo_id = hpo[row[3]].id
            qualifier = not (row[2] == "NOT")
            evidence = row[5]
            aspect = row[10]

            relations.append(
                {
                    "disease": disease_id,
                    "term": hpo_id,
                    "qualifier": qualifier,
                    "evidence": evidence,
                    "aspect": aspect,
                }
            )


with db.atomic():
    for relation in tqdm(list(chunks(relations, 100))):
        Disease_has_Terms.insert_many(relation).execute()


# Compute diseases frequency
print("Compute diseases count per terms")

terms = []
for term in tqdm(Terms.select()):
    count = db.execute_sql(f"""SELECT  COUNT(DISTINCT d.disease_id) as count FROM nodes 
        INNER JOIN (SELECT left, right, term_id FROM nodes WHERE term_id = {term.id}) as root ON nodes.left >= root.left AND nodes.right <= root.right 
        INNER JOIN disease_has_terms d ON d.term_id = nodes.term_id""").fetchone()[0]
    term.disease_count = count 
    terms.append(term)

Terms.bulk_update(terms, fields=[Terms.disease_count])


print("done")

# Common ancestor
# #SELECT * FROM nodes 
# WHERE 
# nodes.left < (SELECT MIN(left) FROM nodes WHERE nodes.term_id IN (SELECT terms.id FROM terms WHERE hpo IN ('HP:0007838', 'HP:0007687'))) 
# AND 
# nodes.right > (SELECT MAX(right) FROM nodes WHERE nodes.term_id IN (SELECT terms.id FROM terms WHERE hpo IN ('HP:0007838', 'HP:0007687'))) 
# ORDER BY left DESC LIMIT 1