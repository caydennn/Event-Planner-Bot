import datetime
import psycopg2
import os
from os.path import join, dirname
from dotenv import load_dotenv
import pytz
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_NAME = os.environ.get("DB_NAME") 
DB_USER = os.environ.get("DB_USER") 
DB_PASS = os.environ.get("DB_PASS") 
DB_HOST = os.environ.get("DB_HOST") 
DB_PORT = os.environ.get("DB_PORT")  

def connect():
    try: 
        conn = psycopg2.connect(database = DB_NAME, user = DB_USER,
                            password = DB_PASS, host = DB_HOST, port = DB_PORT)

        print ('Database connected succcessfully')
        return conn

    except Exception as e:
        print (e)
        print ("Error connecting to database")

def create_table():
    try:
        conn = connect()
        cur = conn.cursor()
     
    
        conn.commit()
        conn.close()
        # print("Table Created")
        print("Table Altered")

    
    except Exception as e:
        print (e)
        print ("Error Creating Table")

def list_tables():
    try:
        conn = connect()
        cur = conn.cursor()
        sql_command = """ SELECT * FROM information_schema.tables WHERE table_schema='public'"""
        cur.execute(sql_command)
        rows = cur.fetchall()
        
        print ("List of Tables: ")
        for data in rows:
            print(data[2])

        conn.commit()
        conn.close()
    except Exception as e:
        print (e)
        print ("Error listing tables")

def list_all_food_data():
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("""
        SELECT groupnames.group_id, groupnames.group_title, groupfood.food_place
        FROM groupnames INNER JOIN groupfood ON (groupnames.group_id = groupfood.group_id)
        """)

        print ("List of ALL Food Data with Group Names: ")
        rows = cur.fetchall()
        for data in rows:
            print(data) 

        conn.commit()
        conn.close()

    except Exception as e:
        print (e)
        print ("Error listing food data")

# Returns a list of all the food places for that group
def get_group_food_data(group_id):
    food_place_list = []
    try: 
        conn = connect()
        cur = conn.cursor()
        sql_command = """SELECT groupfood.food_place
                        FROM groupfood 
                        WHERE group_id = {}""".format(group_id)
        cur.execute(sql_command)
        rows = cur.fetchall()
    
        for data in rows:
            food_place_list.append(data[0])
        print ("List of food ", food_place_list)
          # update the last modified time for the group
        now = datetime.datetime.now()
        now = now.astimezone(pytz.timezone('Asia/Singapore'))
        update_group_last_modified(group_id, now)
        conn.commit()
        conn.close()
        return food_place_list
    except Exception as e:
        print(e)
        print ("Error getting group food data")
        
def rename_column(tablename, oldname, newname):
    try:
        conn = connect()
        cur = conn.cursor()
        sql_command = """
        ALTER TABLE {}
        RENAME COLUMN '{}' TO '{}'
        """.format(tablename, oldname, newname)
        cur.execute(sql_command)
        conn.commit()
        conn.close()
        print("Column {} renamed to {} in table {}".format(oldname, newname, tablename))
    
    except Exception as e:
        print (e)
        print ("Error renaming column")

def insert_group_data(group_id, group_title):
    try:
        table_name = "groupnames"
        conn = connect()
        cur = conn.cursor()
        # create an sql command that also tracks the time the group was created
        # sql_command = """ INSERT INTO {} VALUES (%s, %s, %s)""".format(table_name)
        # cur.execute(sql_command, (group_id, group_title, datetime.datetime.now()))
        

        sql_command = """ INSERT INTO {} VALUES (%s, %s)""".format(table_name)
        cur.execute(sql_command, (group_id, group_title))
          # update the last modified time for the group
        now = datetime.datetime.now()
        now = now.astimezone(pytz.timezone('Asia/Singapore'))
        update_group_last_modified(group_id, now)
        conn.commit()
        conn.close()
        print("Group Data for {} inserted successfully".format(group_title))
    except Exception as e:
        print (e)
        print ("Error inserting group data")

def remove_group_data(group_id):
    try: 
        table_name = "groupnames"
        conn = connect()
        cur = conn.cursor()
        cur.execute("""
        DELETE FROM {0} 
        WHERE {0}.group_id =%s
        """.format(table_name), (group_id,) )

        conn.commit()
        conn.close()
        print("Group data removed for id {}".format(group_id))
    except Exception as e:
        print (e)
        print ("Error removing GROUP data")
        
        
        
def update_group_last_modified(group_id, timestamp):
    try:
        table_name = "groupnames"
        conn = connect()
        cur = conn.cursor()
        sql_command = """
        UPDATE {}
        SET last_modified = %s
        WHERE group_id = %s
        """.format(table_name)
        cur.execute(sql_command, (timestamp, group_id))
        conn.commit()
        conn.close()
        print("Group Last Modified updated for id {}".format(group_id))
    except Exception as e:
        print (e)
        print ("Error updating group last modified")

def insert_food_data(group_id, food_place):
    try:
        table_name = "groupfood"
        conn = connect()
        cur = conn.cursor()
        sql_command = """INSERT INTO {}
        VALUES (%s, %s)
        """.format(table_name)
        # VALUES (( SELECT group_id FROM groupnames WHERE group_title = %s), %s) 
        # Create an sql query that also tracks the time the food place was added


        cur.execute(sql_command, (group_id, food_place))

        # update the last modified time for the group
        now = datetime.datetime.now()
        now = now.astimezone(pytz.timezone('Asia/Singapore'))
        update_group_last_modified(group_id, now)
        conn.commit()
        print ("FOOD Data inserted successfully")
        conn.close()

    except Exception as e:
        print (e)
        print ("Error inserting food data")
        return False

def remove_food_data(group_id: str, food_place: str):
    try:
        table_name = "groupfood"
        food_place = food_place.upper()
        conn = connect()
        cur = conn.cursor()
        sql_command = """DELETE FROM {0}
        WHERE ({0}.group_id =%s AND UPPER({0}.food_place) = %s)""".format(table_name) #! 
        
        cur.execute(sql_command, (group_id, food_place))
        
        # update the last modified time for the group
        now = datetime.datetime.now()
        now = now.astimezone(pytz.timezone('Asia/Singapore'))
        update_group_last_modified(group_id, now)
        conn.commit()
        print ("Data removed successfully")
        conn.close()

    except Exception as e:
        print (e)
        print ("Error removing food data")
# Function to check whether a group ID exists inside the main table (groupnames)
def check_id_exist(groupid):
    try:
        table_name = "groupnames"
        conn = connect()
        cur = conn.cursor()
        # sql_command = """SELECT EXISTS (SELECT 1 FROM {} WHERE group_id = %s)""".format(table_name)
        sql_command = """SELECT 1 FROM {} WHERE group_id = %s""".format(table_name)

        cur.execute(sql_command, (groupid, ))
   

        return cur.fetchone() is not None
        

    except Exception as e:
        print (e)
        print ("Error checking existence of group {}".format(groupid))


def remove_food_null():
    try:
        table_name = "groupfood"
        conn = connect()
        cur = conn.cursor()
        sql_command = """DELETE FROM {0}
        WHERE ({0}.group_id is NULL )""".format(table_name)
        #  AND {0}.food_place = null)
        cur.execute(sql_command)
        conn.commit()
        print ("NULL FOOD Data removed successfully")
        conn.close()

    except Exception as e:
        print (e)
        print ("Error removing NULL FOOD data")

def change_data_type():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
    ALTER TABLE groupnames
    ALTER COLUMN group_id TYPE numeric
    """)

    cur.execute("""
    ALTER TABLE groupfood
    ALTER COLUMN group_id TYPE numeric
    """)
    print("data type changed successfully")
    conn.commit()
    conn.close()
# change_data_type()
# insert_food_data("EFF0RT", "TEST Macs")
# list_food_data()
# get_group_food_data(-295040317)
# remove_food_data(-295040317, "Louis Burger Place xd")
# list_all_food_data()
# remove_food_null()
# remove_group_data(-1001157055978)