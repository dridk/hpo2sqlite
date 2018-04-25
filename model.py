from peewee import * 
import os 

# Create Sqlite model 

db = SqliteDatabase("hpo.db")

class Terms(Model):
    hpo        = CharField()
    name       = CharField()
    definition = CharField(default = None)
    comment    = CharField(default = None) 
    class Meta:
        database = db 


class Nodes(Model):
    name      = CharField()
    left      = IntegerField()
    right     = IntegerField()
    depth     = IntegerField()
    parent_id = IntegerField()
    term      = ForeignKeyField(Terms)

    class Meta:
        database = db 


class Informations(Model):
    hpo_version = CharField()
    hpo_md5     = CharField()
    saved_by    = CharField()
    version     = CharField()

    class Meta:
        database = db 


def create_database_shema():
    db.connect()
    db.create_tables([Nodes,Terms,Informations])
    return db
