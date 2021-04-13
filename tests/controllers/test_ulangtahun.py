import unittest
import os
from pathlib import Path

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

import controllers.ulangtahun as ulangtahun

class TestGroupware(unittest.TestCase):
    def setUp(self):
        self.test_chat_id = os.getenv('TEST_CHAT_ID')

    def test_send(self):
        self.assertTrue(True)

        data = {
            'message' : {
                'chat': {
                    'id': self.test_chat_id,
                }
            }
        }

        ulangtahun.action(data)

if __name__ == '__main__':
    unittest.main()
