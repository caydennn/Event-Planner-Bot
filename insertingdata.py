import psycopg2
import os
from os.path import join, dirname
from dotenv import load_dotenv
import pandas as pd
import json
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_NAME = os.environ.get("DB_NAME") 
DB_USER = os.environ.get("DB_USER") 
DB_PASS = os.environ.get("DB_PASS") 
DB_HOST = os.environ.get("DB_HOST") 
DB_PORT = os.environ.get("DB_PORT")  

try:
    conn = psycopg2.connect(database = DB_NAME, user = DB_USER,
                    password = DB_PASS, host = DB_HOST, port = DB_PORT)

    print ('Database connected succcessfully')
    

   
    
    
    cur = conn.cursor()
    table_name = "groupfood"
    
    #SELECT group_id FROM groupnames WHERE group_title='EFF0RT'
    
    sql_command = """ INSERT INTO {}
    VALUES (( SELECT group_id FROM groupnames WHERE group_title='EFF0RT' ),'MYFOODPLACE')""".format(table_name)
    # VALUES (%s, %s, %s) """.format(table_name) 
    # sql_command = """ INSERT INTO {} (id) VALUES {}""".format(table_name)
    # sql_string = "INSERT INTO {0} (info) VALUES ('{1}') ".format(table_name, score_str )

    # cur.execute(sql_command, (group_id, group_title, food_places))
    cur.execute(sql_command)
    conn.commit()
    print("Data inserted successfully")
    conn.close()

    
except Exception as e:
    print (e)
    print ("Database not connected")