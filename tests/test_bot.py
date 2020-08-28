import os
import json
import unittest
import time
from datetime import datetime

import bot_controller as bot
import models.groupware as groupware
import models.bot as bot_model

class TestBot(unittest.TestCase):
    def setUp(self):
        os.putenv('IS_DEBUG', 'false')
        self.test_user = os.getenv('TEST_USER')
        self.test_message_id = os.getenv('TEST_MESSAGE_ID')
        self.test_chat_id = os.getenv('TEST_CHAT_ID')
        self.test_photo_file_id = os.getenv('TEST_PHOTO_FILE_ID')

        groupware.LOGBOOK_API_URL = 'https://httpbin.org/anything'

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
        item['message']['text'] = '/about@'+bot_model.BOT_NAME
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
        item['message']['reply_to_message'] = None
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

    @unittest.skip(""" sekarang ini mekanisme exception projectName not found tidak mendukung 
    unittest karena perlu di capture tanpa di raise ulang agar bisa didapatkan 
    error message. perlu mekanisme validasi sebelum send satu2 per username agar 
    tidak berulang dan bisa dipisah dari validasi auth per user """)
    def test_lapor_random_project_name(self):
        item = json.loads(json.dumps(self.default_data))
        item['message']['text'] = '/lapor asl|unittest\npeserta:' + self.test_user
        with self.assertRaises(Exception):
            bot.process_telegram_input(item)

if __name__ == '__main__':
    unittest.main()
