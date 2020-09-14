import os
import json
import unittest
from pathlib import Path
from datetime import datetime

import models.groupware as groupware

class TestGroupware(unittest.TestCase):
    def setUp(self):
        os.putenv('IS_DEBUG', 'false')
        testuser = os.getenv('TEST_USER')

        groupware.LOGBOOK_API_URL = 'https://httpbin.org/anything'
        self.auth_token = groupware.get_token(testuser, testuser)

        self.default_data = {
            'dateTask' : datetime.now().strftime('%Y-%m-%dT00:00:00.000Z'),
            'projectName' : 'Riset', # project nam (from db)
            'nameTask': 'Contoh',
            'difficultyTask': 3, # integer 1-5
            'organizerTask' : 'PLD',
            'isMainTask' : 'true', #bool
            'isDocumentLink' : 'true', #bool
            'workPlace' : 'WFH',
            'documentTask': 'null', # url
        }

        self.default_file_path = Path(__file__).parent.parent / 'single-pixel.png'

        groupware.load_project_list(self.auth_token)

    def test_normal_input(self):
        with open(self.default_file_path, 'rb') as f:
            groupware.post_report(
                self.auth_token,
                self.default_data,
                { 'evidenceTask': f}
            )

    def test_project_name_random(self):
        data = json.loads(json.dumps(self.default_data))
        data['projectName'] = 'randomprojectskldfjlsdfjsd'

        with self.assertRaises(Exception):
            with open(self.default_file_path, 'rb') as f:
                groupware.post_report(
                    self.auth_token,
                    data,
                    { 'evidenceTask': f}
                )

    def test_project_name_random_case(self):
        data = json.loads(json.dumps(self.default_data))
        data['projectName'] = 'SaPaWarGa'

        with open(self.default_file_path, 'rb') as f:
            groupware.post_report(
                self.auth_token,
                data,
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
            res = groupware.validate_report(data)
            self.assertTrue(len(res) > 0)


if __name__ == '__main__':
    unittest.main()
