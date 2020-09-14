import json

import sqlalchemy

import models.db as db

def create_table():
    DB_META = sqlalchemy.MetaData()
    USER_TABLE_DEFINITION = sqlalchemy.Table(
       'chat_history', DB_META, 
       sqlalchemy.Column('id', sqlalchemy.Integer, primary_key = True), 
       sqlalchemy.Column('chat_id', sqlalchemy.String(100)), 
       sqlalchemy.Column('message_id', sqlalchemy.String(100)), 
       sqlalchemy.Column('content', sqlalchemy.JSON), 
    )
    DB_META.create_all(db.get_engine())

def insert(chat_id, message_id, content):
    insert_content = content \
        if isinstance(content,str) else \
        json.dumps(content)
    query_insert = sqlalchemy.text("""
        INSERT INTO chat_history 
        (chat_id, message_id, content) 
        VALUES (:chat_id, :message_id, :content)""")
    res = db.get_conn().execute(
        query_insert,
        chat_id=chat_id, 
        message_id=message_id,
        content=insert_content)

    return res

def get(chat_id=None, message_id=None):
    query_select = sqlalchemy.text("""
        SELECT * FROM chat_history 
        WHERE chat_id = :chat_id AND
        message_id = :message_id""")
    res = db.get_conn().execute(
        query_select,
        chat_id=chat_id, 
        message_id=message_id).fetchone()

    res = dict(res)

    if isinstance(res['content'],str):
        res['content'] = json.loads(res['content'])

    return res
