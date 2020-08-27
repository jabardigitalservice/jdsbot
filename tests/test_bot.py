import os
import json
import unittest
import time
from datetime import datetime

import poster, bot

class TestPoster(unittest.TestCase):
    def setUp(self):
        os.putenv('IS_DEBUG', 'false')
        self.testuser = os.getenv('TEST_USER')

        poster.LOGBOOK_API_URL = 'https://httpbin.org/anything'

        self.default_data = {
            'message': {
                'date': time.time(),
                'message_id': 1234,
                'chat': {
                    'id': 1234,
                },
            }
        }

    def test_empty_message(self):
        item = {}
        self.assertIsNone(bot.process_telegram_input(item))

    def test_about_random_date_past(self):
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

if __name__ == '__main__':
    unittest.main()
