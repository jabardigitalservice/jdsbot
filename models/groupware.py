import os
import re
import json
import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

ROOT_API_URL = os.getenv('ROOT_API_URL')
LOGBOOK_API_URL = ROOT_API_URL+'/logbook/'
LOGIN_API_URL = ROOT_API_URL+'/auth/login/'
PROJECT_LIST_API_URL = ROOT_API_URL+'/project/?limit=100&pageSize=100'

TIMESTAMP_TRAIL_FORMAT = 'T00:00:00.000Z'
IS_DEBUG=(os.getenv('IS_DEBUG', 'false').lower() == 'true')
PROJECT_LIST = None

def get_token(username, password):
    """ dapetin token dari username & password """
    req = requests.post(url=LOGIN_API_URL, data={
        'username': username,
        'password': password,
    })
    res = req.json()

    if req.status_code < 300:
        if IS_DEBUG:
            print('get token response:', req.text)
        return res['auth_token']
    else:
        msg = res['detail'] if 'detail' in res else req.text
        raise Exception(msg)

def load_project_list(auth_token):
    """ dapetin list nama project & id nya """
    global PROJECT_LIST

    headers = {
        'Authorization': 'Bearer ' + auth_token,
    }
    req = requests.get(url=PROJECT_LIST_API_URL, headers=headers)

    if req.status_code < 300:
        raw_response = req.json()
        PROJECT_LIST =  {
            row['projectName'].strip().lower() : {
                'id': row['_id'].strip() ,
                'originalName': row['projectName'].strip(),
            }
            for row in raw_response['results']
        }
    else:
        raise Exception('Error response: ' + req.text)

def get_attendance(auth_token, date=None):
    """ get list of attendace from /attendance endpoint """
    if date is None:
        date = str(datetime.date.today())

    headers = {
        'Authorization': 'Bearer ' + auth_token,
    }

    api_url = ROOT_API_URL+'/attendance/?limit=200&pageSize=200&date={}'.format(date)
    req = requests.get(
        url=api_url, 
        headers=headers
    )

    if req.status_code >= 300:
        raise Exception('Error response: ' + req.text)

    raw_response = req.json()
    return raw_response['results']

def validate_report(raw_data):
    """ Validate report data
    Returns
    -------
    list of Exception for all caught error. empty string for no error
    """
    global PROJECT_LIST

    data = json.loads(json.dumps(raw_data))
    errors = []

    # dateTask validation
    if 'dateTask' not in data or len(data['dateTask'].strip()) < 1:
        errors.append(ValueError('dateTask field cannot be empty'))
    elif not re.match("^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d\dZ$",data['dateTask']):
        errors.append(ValueError('dateTask format mismatch'))

    # project name validation
    if 'projectName' not in data or len(data['projectName'].strip()) < 1:
        errors.append(ValueError('projectName field cannot be empty'))
    else:
        original_project_name = data['projectName']
        data['projectName'] = data['projectName'].lower()
        if PROJECT_LIST is None:
            load_project_list(auth_token)

        if data['projectName'] not in PROJECT_LIST:
            errors.append(ValueError("projectName '{}' not found".format(original_project_name)))

    return errors

def post_report(auth_token, data, files):
    """ post laporan """
    global PROJECT_LIST

    data['projectName'] = data['projectName'].lower()
    data['projectId'] = PROJECT_LIST[data['projectName']]['id']
    data['projectName'] = PROJECT_LIST[data['projectName']]['originalName'] # replace projectName with original name

    headers = {
        'Authorization': 'Bearer ' + auth_token,
    }

    if IS_DEBUG:
        print('sending input to groupware with data:', data)

    req = requests.post(url=LOGBOOK_API_URL, headers=headers, files=files, data=data)
    if IS_DEBUG:
        print('request body:', req.request.body)

    if req.status_code < 300:
        raw_response = req.json()
        if IS_DEBUG:
            print('response', raw_response)
        return raw_response
    else:
        raise Exception('Error response: ' + req.text)

if __name__ == '__main__':
    TEST_USER = os.getenv('TEST_USER', 'testuser')
    auth_token = get_token(TEST_USER, TEST_USER)
    print('auth_token :', auth_token)

    from datetime import datetime

    data = {
        'dateTask' : datetime.now().strftime('%Y-%m-%d'), #2020-08-23T00:00:00.000Z
        # 'projectId' : '', # UID project, dapat dr endpoint /project/?limit=100&pageSize=100
        'projectName' : 'Sapawarga', # project nam (from db)
        'nameTask': 'Contoh',
        'difficultyTask': 3, # integer 1-5
        'organizerTask' : 'PLD',
        'isMainTask' : 'true', #bool
        'isDocumentLink' : 'true', #bool
        'workPlace' : 'WFH',
        'documentTask': 'null', # url
    }

    files={
        'evidenceTask' : ('test.png', open('test.png', 'rb'), 'image/png'), # upload evidence
    }

    print(post_report(auth_token, data, files))



