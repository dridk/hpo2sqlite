from peewee import *
import os

# Create Sqlite model

db = SqliteDatabase("hpo.db")


class Terms(Model):
    hpo = CharField()
    name = CharField()
    definition = CharField(default=None)
    comment = CharField(default=None)
    disease_count = IntegerField()

    class Meta:
        database = db


class Nodes(Model):
    name = CharField()
    left = IntegerField()
    right = IntegerField()
    depth = IntegerField()
    parent = ForeignKeyField("self", null=True)
    term = ForeignKeyField(Terms)

    class Meta:
        database = db


class Informations(Model):
    hpo_version = CharField()
    hpo_md5 = CharField()
    saved_by = CharField()
    version = CharField()

    class Meta:
        database = db


class Genes(Model):
    entrez_id = IntegerField()
    name = CharField()

    class Meta:
        database = db


class Genes_has_Terms(Model):
    term = ForeignKeyField(Terms)
    gene = ForeignKeyField(Genes)

    class Meta:
        database = db


class Diseases(Model):
    database_id = CharField()
    name = CharField()

    class Meta:
        database = db


class Disease_has_Terms(Model):
    term = ForeignKeyField(Terms)
    disease = ForeignKeyField(Diseases)
    qualifier = BooleanField()
    evidence = CharField()
    aspect = CharField(max_length=1)

    class Meta:
        database = db


def create_database_shema():
    db.connect()
    db.create_tables([Nodes, Terms, Informations])
    return db
