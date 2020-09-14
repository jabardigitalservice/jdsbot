""" Model for table user 
Currently only support MySQL
"""
import os
import datetime
from pathlib import Path

import sqlalchemy
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

import models.db as db
import models.groupware as groupware

# global variables to store user data
PASSWORD = {}
ALIAS = {}

def create_table():
    DB_META = sqlalchemy.MetaData()
    USER_TABLE_DEFINITION = sqlalchemy.Table(
       'users', DB_META, 
       sqlalchemy.Column('id', sqlalchemy.Integer, primary_key = True), 
       sqlalchemy.Column('username', sqlalchemy.String(100)), 
       sqlalchemy.Column('password', sqlalchemy.String(100)), 
       sqlalchemy.Column('alias', sqlalchemy.String(100)), 
    )
    DB_META.create_all(db.get_engine())

def get_user_list():
    res = db.db_exec('SELECT username, password, alias FROM users')

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
    res_find_user = db.get_conn().execute(
        query_find_user, 
        username=username).fetchall()
    print('res_find_user', res_find_user)
    if len(res_find_user) < 1:
        return (False, 'User not found')

    query_update = sqlalchemy.text("""
        UPDATE users 
        SET alias = :alias 
        WHERE username = :username""")
    res = db.get_conn().execute(
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

def get_users_attendance(date=None):
    """ get list of user with its attendence """
    global ALIAS
    global PASSWORD

    auth_token = get_user_token(os.getenv('TEST_USER'))
    ALIAS_INV = {v:k for k, v in ALIAS.items()}

    attendance_list = groupware.get_attendance(auth_token, date)
    attendance_list = {
        row['username'] : row['fullname']
        for row in attendance_list
    }

    results= []
    for username in PASSWORD:
        if username in attendance_list:
            results.append([
                username,
                attendance_list[username],
                ALIAS_INV[username],
                True,
            ])
        else:
            results.append([
                username,
                None,
                ALIAS_INV[username],
                False,
            ])

    return results

