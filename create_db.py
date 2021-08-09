import postgresql
import os
import json

dbhost = os.environ['DBHOST']
dbport = os.environ['DBPORT']
dbuser = os.environ['NWDBUSER']
dbpass = os.environ['NWDBPASS']

def get_tables(directory):
    subfolders = [f.name for f in os.scandir(directory) if f.is_dir()]
    return subfolders

def create_database(dbconn):
    try:
        dbconn.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    except:
        pass
    try:
        dbconn.execute('CREATE DATABASE nwdb OWNER '+dbuser+';')
    except:
        print("Unable to create database")

def create_table(dbconn, tablename,path):
    #create a list of columns for the table 
    columns = {}
    #get the fields from a json file in the folder
    for e in os.listdir(path):
        if e.endswith(".json"):
            with open(path+'/'+e) as f:
                contents = json.load(f)["data"]

            for key in contents:
                if type(contents[key]) != dict:
                    columns[key] = type(contents[key])
    #turn column keypairs into postgres query string
    columnstring = ""
    for e in columns.keys():
        if columns[e] == int:
            columns[e] = "numeric"
        elif columns[e] == list:
            columns[e] = "varchar array"
        elif columns[e] == str:
            columns[e] = "varchar"
        elif columns[e] == bool:
            columns[e] = "boolean"
        else:
            columns[e] = "varchar"
        columnstring+=f" {e} {columns[e]}, "
    columnstring = columnstring[:-2]
    try:
        dbconn.execute('CREATE SCHEMA nwdb;')
    except:
        pass
    try:
        qstring = 'CREATE TABLE nwdb.'+tablename+' (guid serial primary key,'
        qstring+=columnstring
        qstring+=");"
        dbconn.execute(qstring)

    except Exception as e:
        print(e)
        pass

def populate_table(dbconn, tablename,path):
    #get the fields from a json file in the folder
    for e in os.listdir(path):
        columns = {}
        if e.endswith(".json"):
            with open(path+'/'+e) as f:
                contents = json.load(f)["data"]
            for key in contents:
                if type(contents[key]) != int and type(contents[key]) != bool:
                    if '{' in str(contents[key]):
                        columns[key] = "'"+str(contents[key]).replace('{','\{').replace('}','\}').replace("\'","\\\"")+"'"
                    else:
                        columns[key] = "'"+str(contents[key]).replace("\'","\\\"").replace('[]','{}').replace('[','{').replace(']','}')+"'"
            insertstring="INSERT INTO nwdb."+tablename+" ("
            for e in columns.keys():
                insertstring+=" "+e+", "
            insertstring = insertstring[:-2]
            insertstring+=") VALUES ("
            for e in columns.keys():
                insertstring+=" "+str(columns[e])+", "
            insertstring= insertstring[:-2]
            insertstring+=");"
            print(insertstring)
            print("%%%%%\n\n\n\%%%%%%")
            try:
                dbconn.execute(insertstring)
            except Exception as e:
                print(e)

if __name__ == "__main__":
    dbconn = postgresql.open(f'pq://{dbuser}:{dbpass}@{dbhost}:{dbport}/postgres')
    #create_database(dbconn)
    dbconn = postgresql.open(f'pq://{dbuser}:{dbpass}@{dbhost}:{dbport}/nwdb')
    
    create_table(dbconn, "item","/Users/ljs/Projects/new-world-buddy/nwdb.info/db/item")
    populate_table(dbconn,"item","/Users/ljs/Projects/new-world-buddy/nwdb.info/db/item")

