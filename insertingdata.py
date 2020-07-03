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
    with open('data.json') as json_data:
        # use load() rather than loads() for json data
        # convert the json into a dict 
        info_dict = json.load(json_data)

        # conver dict to string
        # score_str = json.dumps(score_dict)
        
    
    
    cur = conn.cursor()
    table_name = "groupinfo"
    for key, info in info_dict.items():
        group_id = key 
        group_title = info['group_title']
        if group_title == "None":
            group_title = None 
        raw_food_places = info['food_places']
        food_places = ' '.join(raw_food_places)
        # json.dumps(raw_food_places)
        # print(type(food_places))

        sql_command = """ INSERT INTO {} (group_id, group_title, food_places)
        VALUES (%s, %s, %s) """.format(table_name) 
    # sql_command = """ INSERT INTO {} (id) VALUES {}""".format(table_name)
    # sql_string = "INSERT INTO {0} (info) VALUES ('{1}') ".format(table_name, score_str )

        cur.execute(sql_command, (group_id, group_title, food_places))
    conn.commit()
    print("Data inserted successfully")
    conn.close()

    
except Exception as e:
    print (e)
    print ("Database not connected")