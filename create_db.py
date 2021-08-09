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
            try:
                if (e in contents.keys() and len(contents[e]) > 0 and type(contents[e][0]) == dict):
                    columns[e] = "json []"
                elif '{' in str(contents[e]):
                    columns[e] = "json []"
                else:
                    print(f'list not found to contain dict. content: {contents[e]}')
                    columns[e] = "varchar array"
            except Exception as f:
                columns[e] = "varchar array"
                print(f"key:{e},type:{columns[e]},exception:{f})")
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
        #REMOVE ID REF
        qstring.replace(' id ', ' iid ') 
        dbconn.execute(qstring)

    except Exception as e:
        print(e)
        pass

def create_item_table_manual(dbconn):
    qstring = """create table nwdb.item (guid serial primary key, type varchar, typeName varchar, iid varchar, name varchar, description varchar, icon varchar, tier numeric, rarity numeric, perks json[], perkbuckets json[], baseDamage numeric, staggerDamage numeric, gearscore numeric, gearscoremin numeric, gearscoremax numeric, weight numeric, level numeric, bop boolean, boe boolean,durability numeric, itemclass varchar[], nameditem boolean, critchance numeric, critdamagemultiplier numeric, blockstaminadamage numeric, blockstability numeric, statuseffects varchar[],craftingrecipesoutput json[], craftingrecipesinput json[], attributescale json[], questrewards json[], itemtype varchar);"""
    dbconn.execute(qstring)

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
                        columns[key]="'{\""+str(contents[key]).replace('\'','\"')[1:-1]+"\"}'"
                        #columns[key] = "'"+str(contents[key]).replace('{','\{').replace('}','\}').replace("\'","\\\"")+"'"
                        pass
                    else:
                        #columns[key]="'"+str(contents[key])+"'" 
                        columns[key] = "'"+str(contents[key]).replace("\'","\\\"").replace('[]','{}').replace('[','{').replace(']','}')+"'"
                        pass
            insertstring="INSERT INTO nwdb."+tablename+" ("
            for e in columns.keys():
                if e == 'id':
                    e='iid'
                insertstring+=" "+e+", "
            insertstring = insertstring[:-2]
            insertstring+=") VALUES ("
            for e in columns.keys():
                insertstring+=" "+str(columns[e])+", "
            insertstring= insertstring[:-2]
            insertstring+=");"
            print(insertstring)
            try:
                dbconn.execute(insertstring)
            except Exception as e:
                print(e)

if __name__ == "__main__":
    dbconn = postgresql.open(f'pq://{dbuser}:{dbpass}@{dbhost}:{dbport}/postgres')
    #create_database(dbconn)
    dbconn = postgresql.open(f'pq://{dbuser}:{dbpass}@{dbhost}:{dbport}/nwdb')
    
    #create_table(dbconn, "item","/Users/ljs/Projects/new-world-buddy/nwdb.info/db/item")
    create_table(dbconn, "recipe","/Users/ljs/Projects/new-world-buddy/nwdb.info/db/recipe")
    #create_item_table_manual(dbconn)
    populate_table(dbconn,"recipe","/Users/ljs/Projects/new-world-buddy/nwdb.info/db/recipe")
    #populate_table(dbconn,"item","/Users/ljs/Projects/new-world-buddy/nwdb.info/db/item")

