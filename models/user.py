""" Model for table user 
Currently only support MySQL
"""
import os
from pathlib import Path

import sqlalchemy
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv('DATABASE_URL')

USER_TABLE_DEFINITION = """
# ONLY FOR MYSQL
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username CHAR(100),
    password CHAR(100),
    alias CHAR(100)
)
"""

# global variables to store user data
engine=None
db=None
PASSWORD = {}
ALIAS = {}

def get_engine():
    global engine
    if engine is None:
        engine = sqlalchemy.create_engine(DATABASE_URL)
    return engine

def get_db():
    global db
    if db is None:
        db = get_engine().connect()
    return db

def db_exec(*args):
    # with engine.connect() as db:
    return get_db().execute(*args)

def get_user_list():
    global USER_LIST
    global PASSWORD
    global ALIAS

    res = db_exec('SELECT * FROM user')

    USER_LIST = [ row for row in res ]
    return USER_LIST

def load_user_data():
    USER_LIST = get_user_list()
    PASSWORD = { row[0]:row[1] for row in USER_LIST }
    ALIAS = { row[2]:row[0] for row in USER_LIST }

def add_alias(username, new_alias):
    if new_alias in ALIAS:
        return (False, 'Alias already exists')
    elif username not in USER_LIST:
        return (False, 'Unknown username')
    else:
        res = db_exec('UPDATE user SET alias = % WHERE username = ?', new_alias, username)

        load_user_data()
        return (True, 'success')

