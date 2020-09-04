"""
This module handle all function regarding bot actions including parsing telegram
update data, sending telegram message, handling command and input, etc
"""
import os, json, traceback
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

import models.groupware as groupware
import models.user as user

TELEGRAM_TOKEN=os.getenv('TELEGRAM_TOKEN')

BOT_USERNAME=os.getenv('BOT_USERNAME').upper()
BOT_NICKNAME=os.getenv('BOT_NICKNAME', BOT_USERNAME).upper()

EMOJI_SUCCESS = "\U0001F44C"
EMOJI_FAILED = "\U0001F61F"

ROOT_BOT_URL = 'https://api.telegram.org/bot{}'.format(TELEGRAM_TOKEN)
ROOT_BOT_FILE_URL = 'https://api.telegram.org/file/bot{}'.format(TELEGRAM_TOKEN)

def run_command(path, data=None):
    """ run a single telegram API command """
    global ROOT_BOT_URL
    req = requests.get(url=ROOT_BOT_URL+path, data=data)
    if req.status_code < 300:
        return req.json()
    else:
        raise Exception('Error: ' + req.text)

def get_file(file_id):
    """ return file type & binary content of a file in telegram

    Returns
    -------
    dict:
        type: string of file extension (jpg,doc,txt, etc)
        content: binary data of the file content

    Example
    -------

    ```
    res = get_file('1234abcd')
    with open('test.png', 'wb') as f:
        f.write(res['content'])
    ```

    Reference
    ---------
    - https://stackabuse.com/download-files-with-python/

    """

    file_data = run_command('/getFile', { 'file_id': file_id })
    file_path = file_data['result']['file_path']
    download_url = ROOT_BOT_FILE_URL + '/' + file_path
    res = requests.get(url=download_url)
    return {
        'type' : file_path.split('.')[-1],
        'content': res.content,
    }

def process_images(photo_list):
    """ process photo list objects from telegram API """
    largest_photo = max(photo_list, key=lambda k: k['file_size'])
    # print('largest_photo', largest_photo)

    return get_file(largest_photo['file_id'])

def post_report_single(username, input_fields, image_data):
    """ send a single report """
    print('sending report for ' + username)
    fields = json.loads(json.dumps(input_fields)) # clone fields to avoid changing source values
    field_aliases = {
        'tanggal': 'dateTask',
        'kesulitan' : 'difficultyTask',
        'penyelenggara': 'organizerTask',
        'tugasutama': 'isMainTask',
        'lokasi': 'workPlace',
        'lampiran': 'documentTask',
    }

    for field in field_aliases:
        if field in fields:
            fields[field_aliases[field]] = fields[field]

    defaults_values = {
        'dateTask' : datetime.now().strftime('%Y-%m-%d'),
        'difficultyTask': 3,
        'organizerTask' : 'PLD',
        'isMainTask' : 'true',
        'isDocumentLink' : 'true',
        'workPlace' : 'WFH',
        'documentTask': 'null',
    }
    for field in defaults_values:
        if field not in fields:
            fields[field] = defaults_values[field]

    fields['dateTask'] += groupware.TIMESTAMP_TRAIL_FORMAT

    files = {
        'evidenceTask' : image_data['content'],
    }

    auth_token = user.get_user_token(username)
    res = groupware.post_report(auth_token, fields, files)
    print('ok')
    return True

def process_report(telegram_item, fields, image_data):
    """ process parsing result from our telegram processor"""
    print('>>> PROCESSING REPORT >>>')
    print('Fields:', fields, 'File type:', image_data['type'])

    if 'peserta' in fields:
        result_msg = "Results:\n"
        for username in fields['peserta']:
            status = ' | Berhasil ' + EMOJI_SUCCESS
            try:
                result = post_report_single(username, fields, image_data)
            except Exception as e:
                print(e)
                print(traceback.print_exc())
                status = ' | Gagal - {}'.format(e)
            result_msg += "- {} {}\n".format(username, status)

        run_command('/sendMessage', {
            'chat_id': telegram_item['message']['chat']['id'],
            'text': result_msg,
            'reply_to_message_id': telegram_item['message']['message_id']
        })

    return True

def process_error(telegram_item, e):
    """ process (and may be notify) error encountered """
    msg = str(e)
    print('error:', msg)
    return run_command('/sendMessage', {
        'chat_id': telegram_item['message']['chat']['id'],
        'text': 'Error: '+msg,
        'reply_to_message_id': telegram_item['message']['message_id']
    })
