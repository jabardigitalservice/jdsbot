""" Model for table user 
Currently only support MySQL
"""
import os
from pathlib import Path

import sqlalchemy
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

import models.groupware as groupware

DATABASE_URL = os.getenv('DATABASE_URL')

# ONLY FOR MYSQL
db_meta = sqlalchemy.MetaData()
USER_TABLE_DEFINITION = sqlalchemy.Table(
   'users', db_meta, 
   sqlalchemy.Column('id', sqlalchemy.Integer, primary_key = True), 
   sqlalchemy.Column('username', sqlalchemy.String(100)), 
   sqlalchemy.Column('password', sqlalchemy.String(100)), 
   sqlalchemy.Column('alias', sqlalchemy.String(100)), 
)
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
    res = db_exec('SELECT username, password, alias FROM users')

    return [ row for row in res ]

def load_user_data():
    global PASSWORD
    global ALIAS

    USER_LIST = get_user_list()
    PASSWORD = { row[0]:row[1] for row in USER_LIST }
    ALIAS = { row[2]:row[0] for row in USER_LIST }

def set_alias(username, new_alias):
    global ALIAS

    print('set alias for : username', username, 'new_alias', new_alias)
    if new_alias in ALIAS:
        return (False, 'Alias already exists')

    query_find_user = sqlalchemy.text("""
        SELECT * 
        FROM users 
        WHERE username = :username""")
    res_find_user = get_db().execute(
        query_find_user, 
        username=username).fetchall()
    print('res_find_user', res_find_user)
    if len(res_find_user) < 1:
        return (False, 'User not found')

    query_update = sqlalchemy.text("""
        UPDATE users 
        SET alias = :alias 
        WHERE username = :username""")
    res = get_db().execute(
        query_update,
        alias=new_alias, 
        username=username)

    load_user_data()
    return (True, 'success')

def get_user_token(username):
    global ALIAS
    global PASSWORD

    if username in ALIAS:
        username = ALIAS[username]

    if username in PASSWORD:
        password = PASSWORD[username]
    else:
        password = username

    return groupware.get_token(username, password)
