import os
import json
import random
import unittest
from pathlib import Path

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

import sqlalchemy

import models.user as user

class TestUser(unittest.TestCase):
    def setUp(self):
        self.testuser = os.getenv('TEST_USER')
        TEST_DATABASE_URL=os.getenv('TEST_DATABASE_URL', 'sqlite:///unittest.db')
        user.DATABASE_URL = TEST_DATABASE_URL

        user.db_meta.create_all(user.get_engine())

    def test_insert_select(self):
        random_id = random.randrange(1,1000)
        query_insert = sqlalchemy.text("""
            INSERT INTO 
            users(id, username, password) 
            VALUES(:id, :username, :password)""")
        query_select = sqlalchemy.text('SELECT * FROM users WHERE id = :id')
        user.get_db().execute(query_insert,
            id=random_id, 
            username='test_user', 
            password='test_password')
        res = [ 
            row for row 
            in user.get_db().execute(query_select, id=random_id) 
        ]
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][1], 'test_user')

    def test_auth_custom_alias(self):
        test_alias = 'dummy_alias'
        query_insert = sqlalchemy.text('INSERT INTO users (username, password) VALUES (:username, :password)')
        user.get_db().execute(query_insert, 
            username=self.testuser, 
            password=self.testuser)
        user.load_user_data()

        # make sure alias not exists yet
        self.assertIsNotNone(user.get_user_token(self.testuser))
        with self.assertRaises(Exception):
            user.get_user_token(test_alias)

        # test adding alias
        user.set_alias(self.testuser, test_alias)
        self.assertIsNotNone(user.get_user_token(test_alias))

        query_delete = sqlalchemy.text('DELETE FROM users WHERE ((username = :username))')
        user.get_db().execute(query_delete, username=self.testuser)

    def test_auth_alias_unknown_user(self):
        res = user.set_alias('random_user', 'random_alias')
        self.assertFalse(res[0])

    def test_auth_duplicate_alias(self):
        test_alias = 'dummy_alias'
        query_insert = sqlalchemy.text('INSERT INTO users (username, password, alias) VALUES (:username, :password, :alias)')
        user.get_db().execute(query_insert, 
            username=self.testuser, 
            password=self.testuser,
            alias=test_alias)
        user.load_user_data()

        # make sure alias exists
        self.assertIsNotNone(user.get_user_token(test_alias))

        # test adding alias
        res = user.set_alias(self.testuser, test_alias)
        self.assertFalse(res[0])

        query_delete = sqlalchemy.text('DELETE FROM users WHERE ((username = :username))')
        user.get_db().execute(query_delete, username=self.testuser)

    def test_auth_custom_password(self):
        test_password = 'dummy_password'
        query_insert = sqlalchemy.text('INSERT INTO users (username, password) VALUES (:username, :password)')
        user.get_db().execute(query_insert, username=self.testuser, password=test_password)
        user.load_user_data()
        with self.assertRaises(Exception):
            user.get_user_token(self.testuser)
        query_delete = sqlalchemy.text('DELETE FROM users WHERE ((username = :username))')
        user.get_db().execute(query_delete, username=self.testuser)
        user.load_user_data()

    def tearDown(self):
        user.db_exec('DROP TABLE users')

if __name__ == '__main__':
    unittest.main()
