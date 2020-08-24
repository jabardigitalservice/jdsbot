import os

import requests
from dotenv import load_dotenv
load_dotenv()

root_url = os.getenv('API_ROOT_URL')
IS_DEBUG=(os.getenv('IS_DEBUG', 'false').lower() == 'true')
project_list = None

def get_token(username, password):
    """ dapetin token dari username & password """
    req = requests.post(url=root_url+'/auth/login/', data={
        'username': username,
        'password': password,
    })

    if req.status_code < 300:
        res = req.json()
        return res['auth_token']
    else:
        raise Exception('Error response: ' + req.text)

def get_project_list(auth_token):
    """ dapetin list nama project & id nya """
    headers = {
        'Authorization': 'Bearer ' + auth_token,
    }
    req = requests.get(url=root_url+'/project/?limit=100&pageSize=100', headers=headers)

    if req.status_code < 300:
        raw_response = req.json()
        return {row['projectName']:row['_id'] for row in raw_response['results']}
    else:
        raise Exception('Error response: ' + req.text)

def post_report(auth_token, data, files):
    """ post laporan """
    global project_list
    if project_list is None:
        project_list = get_project_list(auth_token)

    if data['projectName'] not in project_list:
        raise Exception("projectName '{}' not found".format(data['projectName']))
    else:
        data['projectId'] = project_list[data['projectName']]

    data['dateTask'] = '{}T00:00:00.000Z'.format(data['dateTask'])

    headers = {
        'Authorization': 'Bearer ' + auth_token,
    }

    if IS_DEBUG:
        print('sending input to groupware with data:', data)

    target_url = root_url+'/logbook/'
    req = requests.post(url=target_url, headers=headers, files=files, data=data)

    if req.status_code < 300:
        raw_response = req.json()
        return raw_response
    else:
        raise Exception('Error response: ' + req.text)

if __name__ == '__main__':
    TEST_USER = os.getenv('TEST_USER')
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



