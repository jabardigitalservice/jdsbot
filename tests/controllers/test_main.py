import os
import json
import unittest
import time
from datetime import datetime
from pathlib import Path

import sqlalchemy
import requests

import models.db as db
import models.groupware as groupware
import models.user as user
import models.chat_history as chat_history
import models.bot as bot_model

import controllers.main as main_controller


class TestBot(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        os.putenv("IS_DEBUG", "false")
        self.test_user = os.getenv("TEST_USER")
        self.test_chat_id = os.getenv("TEST_CHAT_ID")

        # setup test database
        TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///unittest.db")
        db.DATABASE_URL = TEST_DATABASE_URL
        user.create_table()
        chat_history.create_table()

        groupware.LOGBOOK_API_URL = "https://httpbin.org/anything"

        # send dummy data to replied to
        image_file_path = Path(__file__).parent.parent / "single-pixel.png"
        req = requests.post(
            url=bot_model.ROOT_BOT_URL + "/sendPhoto",
            files={"photo": open(image_file_path, "rb")},
            data={"chat_id": self.test_chat_id},
        )
        image_data = req.json()
        largest_photo = max(image_data["result"]["photo"], key=lambda k: k["file_size"])
        self.test_message_id = image_data["result"]["message_id"]
        self.test_photo_file_id = largest_photo["file_id"]

        self.default_data = {
            "message": {
                "date": datetime(
                    2030, 12, 31
                ).timestamp(),  # make sure time is in the future
                "message_id": self.test_message_id,
                "chat": {
                    "id": self.test_chat_id,
                },
                "reply_to_message": {
                    "photo": [
                        {
                            "file_id": self.test_photo_file_id,
                            "file_size": 123,
                        },
                    ],
                },
            }
        }

        # insert username to user table
        query_insert = sqlalchemy.text(
            """
            INSERT INTO
            users(username, password)
            VALUES(:username, :password)"""
        )
        db.get_conn().execute(
            query_insert, username=self.test_user, password=self.test_user
        )

        main_controller.setup()

    @classmethod
    def tearDownClass(self):
        db.db_exec("DROP TABLE users")

    def test_empty_message(self):
        item = {}
        self.assertIsNone(main_controller.process_telegram_input(item))

    def test_random_command(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/notarealcommand"
        self.assertIsNone(main_controller.process_telegram_input(item))

    def test_about_normal(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/about"
        self.assertIsNotNone(main_controller.process_telegram_input(item))

    def test_about_mention_this_bot(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/about@" + bot_model.BOT_USERNAME
        self.assertIsNotNone(main_controller.process_telegram_input(item))

    def test_about_mention_other_bot(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/about@otherbot"
        self.assertIsNone(main_controller.process_telegram_input(item))

    def test_about_date_past(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/about"
        item["message"]["date"] = datetime(2000, 12, 31).timestamp()
        self.assertIsNone(main_controller.process_telegram_input(item))

    def test_about_random_chat_id(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/about"
        item["message"]["chat"]["id"] = "asal"
        with self.assertRaises(Exception):
            main_controller.process_telegram_input(item)

    def test_lapor_normal_with_text(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/lapor Riset|unittest\npeserta:" + self.test_user
        self.assertIsNotNone(main_controller.process_telegram_input(item))

    def test_lapor_normal_with_caption(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["photo"] = item["message"]["reply_to_message"]["photo"]
        del item["message"]["reply_to_message"]
        item["message"]["caption"] = "/lapor Riset|unittest\npeserta:" + self.test_user
        self.assertIsNotNone(main_controller.process_telegram_input(item))

    def test_lapor_without_reply(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/lapor Riset|unittest\npeserta:" + self.test_user
        del item["message"]["reply_to_message"]
        self.assertIsNone(main_controller.process_telegram_input(item))

    def test_lapor_empty_peserta(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/lapor Riset|unittest"
        self.assertIsNone(main_controller.process_telegram_input(item))

    def test_lapor_reply_no_photo(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/lapor Riset|unittest\npeserta:" + self.test_user
        del item["message"]["reply_to_message"]["photo"]
        self.assertIsNone(main_controller.process_telegram_input(item))

    def test_set_alias_normal(self):
        # set alias
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/setalias {}|@random_alias".format(self.test_user)
        self.assertIsNotNone(main_controller.process_telegram_input(item))

        # test /lapor with alias
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/lapor Riset|unittest\npeserta: @random_alias"
        self.assertIsNotNone(main_controller.process_telegram_input(item))

        # test set alias already exist
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/setalias random.user|@random_alias"
        self.assertIsNone(main_controller.process_telegram_input(item))

    def test_set_alias_normal_case_insensitive(self):
        # set alias
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/setalias {}|@random_alias_2".format(self.test_user)
        self.assertIsNotNone(main_controller.process_telegram_input(item))

        # test /lapor with alias
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/lapor Riset|unittest\npeserta: @RANDOM_ALIAS_2"
        self.assertIsNotNone(main_controller.process_telegram_input(item))

    def test_set_alias_random_user(self):
        # set alias
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/setalias random.user|@random_alias"
        self.assertIsNone(main_controller.process_telegram_input(item))

    def test_lapor_random_project_name(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/lapor asl|unittest\npeserta:" + self.test_user
        self.assertIsNone(main_controller.process_telegram_input(item))

    def test_cekabsensi(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/cekabsensi"
        self.assertIsNotNone(main_controller.process_telegram_input(item))

    def test_command_tambah_normal(self):
        # first create normal laporan
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/lapor Riset|unittest\npeserta:" + self.test_user
        res = main_controller.process_telegram_input(item)
        self.assertIsNotNone(res)

        # run actual tambah command
        item_tambah = json.loads(json.dumps(self.default_data))
        item_tambah["message"]["text"] = "/tambah " + self.test_user
        item_tambah["message"]["reply_to_message"]["message_id"] = item["message"][
            "message_id"
        ]
        self.assertIsNotNone(main_controller.process_telegram_input(item_tambah))

    def test_command_tambah_random_command(self):
        item_tambah = json.loads(json.dumps(self.default_data))
        item_tambah["message"]["text"] = "/tambah " + self.test_user
        item_tambah["message"]["reply_to_message"]["message_id"] = 0
        self.assertIsNone(main_controller.process_telegram_input(item_tambah))

    @unittest.skip(
        """ Untuk testing username not found sejauh ini belum ditemukan
    format testing yang baik karena dalam 1 kali submisi bisa ada bbrp user
    sekaligus yang dilaporkan sehingga sulit ditentukan jika hanya sebagian user
    saja yang gagal apakah kasus tersebut gagal secara keseluruhan atau tidak
    """
    )
    def test_lapor_random_user(self):
        item = json.loads(json.dumps(self.default_data))
        item["message"]["text"] = "/lapor Riset|unittest\npeserta: random_user"
        self.assertIsNone(main_controller.process_telegram_input(item))


if __name__ == "__main__":
    unittest.main()
