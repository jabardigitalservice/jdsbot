""" Model for table user 
Currently only support MySQL
"""
import os
import datetime
from pathlib import Path

import sqlalchemy
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

# ONLY FOR MYSQL
db_meta = sqlalchemy.MetaData()
USER_TABLE_DEFINITION = sqlalchemy.Table(
    "users",
    db_meta,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String(100)),
    sqlalchemy.Column("password", sqlalchemy.String(100)),
    sqlalchemy.Column("alias", sqlalchemy.String(100)),
)

# global variables
ENGINE = None
CONNECTION = None


def get_engine(new=False):
    global ENGINE

    if new:
        return sqlalchemy.create_engine(DATABASE_URL)

    if ENGINE is None:
        ENGINE = sqlalchemy.create_engine(DATABASE_URL)
    return ENGINE


def get_conn(new=False):
    global CONNECTION

    if new:
        return get_engine(new=True).connect()

    if CONNECTION is None or CONNECTION.closed:
        CONNECTION = get_engine().connect()
    return CONNECTION


def db_exec(*args):
    return get_conn().execute(*args)


def execute(raw_query, args=None, once=False):
    """run sql command with slalchemy features
    Params
    ------
    once: bool
        execute with on-time connection
    """
    query = sqlalchemy.text(raw_query)

    conn = get_conn(new=once)
    if args is not None:
        return conn.execute(query, **args)
    else:
        return conn.execute(query)

    conn.commit()
    conn.close()
