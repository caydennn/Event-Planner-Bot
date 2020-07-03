import psycopg2
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_NAME = os.environ.get("DB_NAME") 
DB_USER = os.environ.get("DB_USER") 
DB_PASS = os.environ.get("DB_PASS") 
DB_HOST = os.environ.get("DB_HOST") 
DB_PORT = os.environ.get("DB_PORT")  

def create_table():

    try:
        conn = psycopg2.connect(database = DB_NAME, user = DB_USER,
                        password = DB_PASS, host = DB_HOST, port = DB_PORT)

        print ('Database connected succcessfully')
        cur = conn.cursor()
        # cur.execute("DROP TABLE IF EXISTS groupinfo")
        # cur.execute("""

        # CREATE TABLE GroupInfo (
        # group_id serial NOT NULL PRIMARY KEY,
        # group_title VARCHAR(255),
        # food_places json,
        # activities json)
        

        # """)
        cur.execute("""
        
        CREATE TABLE 
        """)

        cur.execute("""
        ALTER TABLE GroupInfo
        ALTER COLUMN activities TYPE VARCHAR(255)
        """)

        conn.commit()
        # print("Table Created")
        print("Table Altered")

    
    except Exception as e:
        print (e)
        print ("Database not connected")