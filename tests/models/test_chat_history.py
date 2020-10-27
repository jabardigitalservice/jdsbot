import os
import json
import random
import unittest
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import sqlalchemy

import models.db as db
import models.chat_history as chat_history


class TestChatHistory(unittest.TestCase):
    def setUp(self):
        self.testuser = os.getenv("TEST_USER")
        TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///unittest.db")
        db.DATABASE_URL = TEST_DATABASE_URL

        chat_history.create_table()

    def test_insert_select(self):
        chat_id_test = "12345"
        message_id_test = "12345"

        res = chat_history.insert(
            chat_id=chat_id_test,
            message_id=message_id_test,
            content={
                "message": {
                    "id": "test",
                }
            },
        )
        self.assertIsNotNone(res)

        res = chat_history.get(chat_id=chat_id_test, message_id=message_id_test)
        self.assertIsNotNone(res)
        print("get result:", res)

        self.assertTrue(isinstance(res["content"], dict))

    def tearDown(self):
        db.db_exec("DROP TABLE chat_history")


if __name__ == "__main__":
    unittest.main()
