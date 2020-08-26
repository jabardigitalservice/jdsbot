import os
import json
import unittest
from datetime import datetime

import poster

class TestPoster(unittest.TestCase):
    def setUp(self):
        os.putenv('IS_DEBUG', 'false')
        testuser = os.getenv('TEST_USER')
        self.auth_token = poster.get_token(testuser, testuser)

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

        parent_path = os.path.dirname(os.path.abspath(__file__))
        self.default_file_path = os.path.join(parent_path, 'single-pixel.png')

    def test_normal_input(self):
        with open(self.default_file_path, 'rb') as f:
            poster.post_report(
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
                    poster.post_report(
                        self.auth_token,
                        data,
                        { 'evidenceTask': f}
                    )


if __name__ == '__main__':
    unittest.main()
