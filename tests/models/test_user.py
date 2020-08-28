import os
import json
import random
import unittest
from pathlib import Path

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

import models.user as user

class TestUser(unittest.TestCase):
    def setUp(self):
        TEST_DATABASE_URL=os.getenv('TEST_DATABASE_URL', 'sqlite:///unittest.db')
        os.putenv('DATABASE_URL', TEST_DATABASE_URL)

        user.db_exec(user.USER_TABLE_DEFINITION)

    def test_insert_select(self):
        random_id = random.randrange(1,1000)
        user.db_exec("""
            INSERT INTO 
            user(id, username, password) 
            VALUES(?, ?, ?)""",
            random_id, 'test_user', 'test_password')
        res = [ 
            row for row 
            in user.db_exec('SELECT * FROM user WHERE id = ?', random_id) 
        ]
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][1], 'test_user')

    def setDown(self):
        user.db_exec('DROP TABLE user')

if __name__ == '__main__':
    unittest.main()
