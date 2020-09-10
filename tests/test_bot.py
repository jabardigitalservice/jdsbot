import os
import json
import unittest
import time
from datetime import datetime
from pathlib import Path

import sqlalchemy
import requests

import models.groupware as groupware
import models.user as user
import models.bot as bot_model

import bot_controller as bot

class TestBot(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        os.putenv('IS_DEBUG', 'false')
        self.test_user = os.getenv('TEST_USER')
        self.test_chat_id = os.getenv('TEST_CHAT_ID')

        # setup test database
        TEST_DATABASE_URL=os.getenv('TEST_DATABASE_URL', 'sqlite:///unittest.db')
        user.DATABASE_URL = TEST_DATABASE_URL
        user.db_meta.create_all(user.get_engine())

        groupware.LOGBOOK_API_URL = 'https://httpbin.org/anything'

        # send dummy data to replied to
        image_file_path = Path(__file__).parent / 'single-pixel.png'
        req = requests.post(
            url=bot_model.ROOT_BOT_URL + '/sendPhoto',
            files = { 'photo': open(image_file_path, 'rb') },
            data = { 'chat_id': self.test_chat_id }
        )
        image_data = req.json()
        largest_photo = max(image_data['result']['photo'], key=lambda k: k['file_size'])
        self.test_message_id = image_data['result']['message_id']
        self.test_photo_file_id = largest_photo['file_id']

        self.default_data = {
            'message': {
                'date': datetime(2030, 12, 31).timestamp(), # make sure time is in the future
                'message_id': self.test_message_id,
                'chat': {
                    'id': self.test_chat_id,
                },
                'reply_to_message': {
                    'photo': [
                        {
                            'file_id': self.test_photo_file_id,
                            'file_size': 123,
                        },
                    ],
                },
            }
        }

        bot.setup()

    @classmethod
    def tearDownClass(self):
        user.db_exec('DROP TABLE users')

    def test_empty_message(self):
        item = {}
        self.assertIsNone(bot.process_telegram_input(item))

    def test_random_command(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/notarealcommand'
        self.assertIsNone(bot.process_telegram_input(item))

    def test_about_normal(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/about'
        self.assertIsNotNone(bot.process_telegram_input(item))

    def test_about_mention_this_bot(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/about@'+bot_model.BOT_USERNAME
        self.assertIsNotNone(bot.process_telegram_input(item))

    def test_about_mention_other_bot(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/about@otherbot'
        self.assertIsNone(bot.process_telegram_input(item))

    def test_about_date_past(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/about'
        item['message']['date'] = datetime(2000, 12, 31).timestamp()
        self.assertIsNone(bot.process_telegram_input(item))

    def test_about_random_chat_id(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/about'
        item['message']['chat']['id'] = 'asal'
        with self.assertRaises(Exception):
            bot.process_telegram_input(item)

    def test_lapor_normal_with_text(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/lapor Riset|unittest\npeserta:' + self.test_user
        self.assertIsNotNone(bot.process_telegram_input(item))

    def test_lapor_normal_with_caption(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['photo'] = item['message']['reply_to_message']['photo']
        del item['message']['reply_to_message']
        item['message']['caption'] = '/lapor Riset|unittest\npeserta:' + self.test_user
        self.assertIsNotNone(bot.process_telegram_input(item))

    def test_lapor_without_reply(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/lapor Riset|unittest\npeserta:' + self.test_user
        del item['message']['reply_to_message']
        self.assertIsNone(bot.process_telegram_input(item))

    def test_lapor_reply_no_photo(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/lapor Riset|unittest\npeserta:' + self.test_user
        del item['message']['reply_to_message']['photo']
        self.assertIsNone(bot.process_telegram_input(item))

    def test_set_alias_normal(self):
        # insert username to user table
        query_insert = sqlalchemy.text("""
            INSERT INTO 
            users(username, password) 
            VALUES(:username, :password)""")
        user.get_db().execute(query_insert,
            username=self.test_user, 
            password=self.test_user)

        # set alias
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/setalias {}|@random_alias'.format(self.test_user)
        self.assertIsNotNone(bot.process_telegram_input(item))

        # test /lapor with alias
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/lapor Riset|unittest\npeserta: @random_alias'
        self.assertIsNotNone(bot.process_telegram_input(item))

    def test_set_alias_random_user(self):
        # set alias
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/setalias random.user|@random_alias'
        self.assertIsNone(bot.process_telegram_input(item))

    def test_lapor_random_project_name(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/lapor asl|unittest\npeserta:' + self.test_user
        self.assertIsNone(bot.process_telegram_input(item))

    def test_cekabsensi(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/cekabsensi'
        self.assertIsNotNone(bot.process_telegram_input(item))

    @unittest.skip(""" Untuk testing username not found sejauh ini belum ditemukan
    format testing yang baik karena dalam 1 kali submisi bisa ada bbrp user 
    sekaligus yang dilaporkan sehingga sulit ditentukan jika hanya sebagian user
    saja yang gagal apakah kasus tersebut gagal secara keseluruhan atau tidak
    """)
    def test_lapor_random_user(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/lapor Riset|unittest\npeserta: random_user'
        self.assertIsNone(bot.process_telegram_input(item))

if __name__ == '__main__':
    unittest.main()
