import os
import json
import unittest
from pathlib import Path
from datetime import datetime

import models.groupware as groupware
import models.user as user

class TestGroupware(unittest.TestCase):
    def setUp(self):
        os.putenv('IS_DEBUG', 'false')
        self.testuser = os.getenv('TEST_USER')
        TEST_DATABASE_URL=os.getenv('TEST_DATABASE_URL', 'sqlite:///unittest.db')

        # setup test database
        user.DATABASE_URL = TEST_DATABASE_URL
        user.db_exec(user.USER_TABLE_DEFINITION)

        groupware.LOGBOOK_API_URL = 'https://httpbin.org/anything'
        self.auth_token = groupware.get_token(self.testuser)

        self.default_data = {
            'dateTask' : datetime.now().strftime('%Y-%m-%dT00:00:00.000Z'),
            'projectName' : 'Sapawarga', # project nam (from db)
            'nameTask': 'Contoh',
            'difficultyTask': 3, # integer 1-5
            'organizerTask' : 'PLD',
            'isMainTask' : 'true', #bool
            'isDocumentLink' : 'true', #bool
            'workPlace' : 'WFH',
            'documentTask': 'null', # url
        }

        self.default_file_path = Path(__file__).parent.parent / 'single-pixel.png'

    def test_auth_custom_alias(self):
        test_alias = 'dummy_alias'
        user.db_exec('INSERT INTO user (username, password, alias) VALUES (%s, %s, %s)', self.testuser, self.testuser, test_alias)
        user.load_user_data()
        self.assertIsNotNone(groupware.get_token(test_alias))
        user.db_exec('DELETE FROM user WHERE ((username = %s))', self.testuser)

    def test_auth_custom_password(self):
        test_password = 'dummy_password'
        user.db_exec('INSERT INTO user (username, password) VALUES (%s, %s)', self.testuser, test_password)
        user.load_user_data()
        with self.assertRaises(Exception):
            groupware.get_token(self.testuser)
        user.db_exec('DELETE FROM user WHERE ((username = %s))', self.testuser)
        user.load_user_data()

    def test_normal_input(self):
        with open(self.default_file_path, 'rb') as f:
            groupware.post_report(
                self.auth_token,
                self.default_data,
                { 'evidenceTask': f}
            )

    def test_validate_dateTask(self):
        data = json.loads(json.dumps(self.default_data))

        wrong_values = [
            '',
            '12-12-12',
            '123-23',
        ]
        for i in wrong_values:
            data['dateTask'] = i
            with self.assertRaises(ValueError):
                with open(self.default_file_path, 'rb') as f:
                    groupware.post_report(
                        self.auth_token,
                        data,
                        { 'evidenceTask': f}
                    )


if __name__ == '__main__':
    unittest.main()
