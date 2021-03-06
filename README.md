# hpo2sqlite
This script convert [HPO ontology](http://human-phenotype-ontology.github.io/) to a sqlite database as a tree according the [nested set model](https://en.wikipedia.org/wiki/Nested_set_model). 
It takes [HPO obo file](http://purl.obolibrary.org/obo/hp.obo) as argument and construct a tree with [networkx](https://networkx.github.io/).
The Tree is visited to compute left and right index and the tree is stored into a sqlite database using [peewee](http://docs.peewee-orm.com/en/latest/) ORM model.
There are two main table: Terms and Nodes.

## Dependencies 
You need python3 with the following modules

```
pip install networkx
pip install obonet 
pip install peewee 
pip install tqdm
```

## Run 
Download hpo obo file from http://purl.obolibrary.org/obo/hp.obo and run the script as follow
```
python import_hpo_obo.py hp.obo
```

 ## Import gene and disease 
 ```
 wget http://compbio.charite.de/jenkins/job/hpo.annotations.current/lastSuccessfulBuild/artifact/current/phenotype.hpoa
 python import_disease.py phenotype.hpoa
 ```
 
 ```
 wget http://compbio.charite.de/jenkins/job/hpo.annotations/lastSuccessfulBuild/artifact/util/annotation/phenotype_to_genes.txt
 python import_gene.py phenotype_to_genes.txt
```

### Table Terms 
Terms contains each unique HPO term with name and definition. 

| fields     | description                  |
|------------|------------------------------|
| id         | INTEGER "3"                  |
| hpo        | TEXT "HP:0000012"            |
| name       | TEXT "Urinary urgency"       |
| definition | TEXT "Urinary urgency is ..."|
| comment    | TEXT                         |


### Table Nodes 
Nodes table contains the HPO ontology as a Tree. Because hpo ontology is a Directed Acyclic Graph, the tree contains duplicate elements. Each node refere to his HPO terms from the term_id field.

| fields     | description                      |
|------------|----------------------------------|
| id         | INTEGER (primary key)            |
| left       | INTEGER (left index)             |
| right      | INTEGER (right index)            |
| depth      | INTEGER (depth of the node)      |
| term_id    | INTEGER (term_id)                |

## Query example 
### Children selection
Select all children of HPO term HP:0012632 (Abnormal intraocular pressure)

#### Step by step example
```
# Get the term id
SELECT id FROM terms WHERE hpo = "HP:0012632" // get 9124
# Get the node left and right 
SELECT left,right FROM nodes WHERE term_id=9124 //get 99982 and 99987
# Select all children nodes
SELECT * FROM nodes WHERE left > 99982 AND right < 99987
```
All steps can be summarized in one query : 

```
SELECT terms.hpo, terms.name FROM nodes
INNER JOIN (SELECT left, right FROM nodes WHERE term_id = (SELECT id FROM terms WHERE hpo = "HP:0012632")) as root ON nodes.left > root.left AND nodes.right < root.right     
INNER JOIN terms ON  terms.id = nodes.term_id
```

You can specify the depth if you only want to first level childs. 

```
SELECT terms.hpo, terms.name FROM nodes
INNER JOIN (SELECT left, right FROM nodes WHERE term_id = (SELECT id FROM terms WHERE hpo = "HP:0012632")) as root ON nodes.left > root.left AND nodes.right < root.right  AND (nodes.depth - root.depth) < 2
INNER JOIN terms ON  terms.id = nodes.term_id
```
