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

        user.db_exec(user.USER_TABLE_DEFINITION)

    def test_insert_select(self):
        random_id = random.randrange(1,1000)
        user.db_exec("""
            INSERT INTO 
            user(id, username, password) 
            VALUES(%s, %s, %s)""",
            random_id, 'test_user', 'test_password')
        res = [ 
            row for row 
            in user.db_exec('SELECT * FROM user WHERE id = %s', random_id) 
        ]
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][1], 'test_user')

    def test_auth_custom_alias(self):
        test_alias = 'dummy_alias'
        user.db_exec('INSERT INTO user (username, password, alias) VALUES (%s, %s, %s)', self.testuser, self.testuser, test_alias)
        user.load_user_data()
        self.assertIsNotNone(user.get_user_token(test_alias))
        user.db_exec('DELETE FROM user WHERE ((username = %s))', self.testuser)

    def test_auth_custom_password(self):
        test_password = 'dummy_password'
        user.db_exec('INSERT INTO user (username, password) VALUES (%s, %s)', self.testuser, test_password)
        user.load_user_data()
        with self.assertRaises(Exception):
            user.get_user_token(self.testuser)
        user.db_exec('DELETE FROM user WHERE ((username = %s))', self.testuser)
        user.load_user_data()

    def setDown(self):
        user.db_exec('DROP TABLE user')

if __name__ == '__main__':
    unittest.main()
