"""
This module handle all function regarding bot actions including parsing telegram
update data, sending telegram message, handling command and input, etc
"""
import os, json, time, traceback
from datetime import datetime

import requests
from dotenv import load_dotenv
load_dotenv()

import poster

TELEGRAM_TOKEN=os.getenv('TELEGRAM_TOKEN')

EMOJI_SUCCESS = "\U0001F44C"
EMOJI_FAILED = "\U0001F61F"

root_bot_url = 'https://api.telegram.org/bot{}'.format(TELEGRAM_TOKEN)
root_bot_file_url = 'https://api.telegram.org/file/bot{}'.format(TELEGRAM_TOKEN)

processed=[]
start_time = time.time()

def run_command(path, data=None):
    global root_bot_url
    req = requests.get(url=root_bot_url+path, data=data)
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
    download_url = root_bot_file_url + '/' + file_path
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

def post_report_single(username, fields, image_data):
    """ send a single report """
    print('sending report for ' + username)
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

    files = {
        'evidenceTask' : image_data['content'],
    }

    auth_token = poster.get_token(username, username)
    res = poster.post_report(auth_token, fields, files)
    print('ok')
    return True

def process_report(telegram_item, fields, image_data):
    """ process parsing result from our telegram processor"""
    print('>>> PROCESSING REPORT >>>')
    print('Fields:', fields, 'File type:', image_data['type'])

    if 'peserta' in fields:
        result_msg = "Results:\n" 
        for username in fields['peserta']:
            status = EMOJI_SUCCESS
            try:
                result = post_report_single(username, fields, image_data)
            except Exception as e:
                print(e)
                traceback.print_exc() 
                status = '{} ({})'.format(EMOJI_FAILED, e)
            result_msg += "- {} {}\n".format(username, status) 

        run_command('/sendMessage', {
            'chat_id': telegram_item['message']['chat']['id'],
            'text': result_msg,
            'reply_to_message_id': telegram_item['message']['message_id']
        })

def process_error(telegram_item, msg):
    """ process (and may be notify) error encountered """
    print('error:', msg)
    run_command('/sendMessage', {
        'chat_id': telegram_item['message']['chat']['id'],
        'text': 'Error: '+msg,
        'reply_to_message_id': telegram_item['message']['message_id']
    })

def action_lapor(item):
    """ action for /lapor command """
    # parse input
    if 'caption' in item['message']:
        input_text = item['message']['caption']
    elif 'text' in item['message']:
        input_text = item['message']['text']

    lines = input_text.split("\n")
    first_params = lines[0][7:].split('|') # split with '|' start from after '/lapor'
    if len(first_params) != 2 :
        process_error(item, 'Mismatched format')
        return

    data = {
        'projectName': first_params[0].strip(),
        'nameTask': first_params[1].strip(),
    }
    # parsing options params
    for line in lines[1:]:
        val = [ l.strip() for l in line.split(sep=':', maxsplit=1) ]
        if len(val) > 1 and len(val[1]) > 0: # only process lines which contain field_name & content
            field_name = val[0].lower()
            content = val[1]
            if field_name == 'peserta':
                data[field_name] = [ name.strip() for name in content.split(',') ]
            else:
                data[field_name] = content

    if 'photo' in item['message']:
        image_data = process_images(item['message']['photo'])
        process_report(item, data, image_data)
    # if this message is replying to a photo
    elif 'reply_to_message' in item['message']:
        if 'photo' in item['message']['reply_to_message']:
            image_data = process_images(item['message']['reply_to_message']['photo'])
            process_report(item, data, image_data)
    else:
        process_error(item, 'No photo data in this input!')

def action_about(telegram_item):
    """ action for /about command """
    # banyak karakter yang perlu di escape agar lolos parsing markdown di telegram. ref: https://core.telegram.org/bots/api#markdownv2-style
    msg = """Halo\! Aku adalah JDSBot\. Aku ditugaskan untuk membantu melakukan rekap laporan harian\. Silahkan ketik chat `/help` untuk melihat command\-command yang bisa aku lakukan\! """
    run_command('/sendMessage', {
        'chat_id': telegram_item['message']['chat']['id'],
        'text': msg,
        'parse_mode': 'MarkdownV2',
    })

def action_help(telegram_item):
    """ action for /help command """
    msg = """Command\-command yang tersedia:

    \- `/help` : menampilkan pesan ini
    \- `/about` : menampilkan penjelasan tentang bot ini
    \- `/lapor` : Mengirimkan laporan groupware JDS\. Cara menggunakan:

        \- siapkan gambar evidence yang akan digunakan\. kemudian chat di grup ini dengan format caption seperti ini: 
        ```
        /lapor <nama_project_di_groupware> | <nama_kegiatan>
        Opsi1: isiopsi1
        Opsi2: isiopsi2
        Opsi3: isiopsi3
        Peserta: <user_groupware_1> , <user_groupware_2>
        ```
        \- atau bisa juga post dulu gambar evidence nya, kemudian reply gambar tersebut dengan format di atas
        \- untuk Opsi\-opsi semuanya adalah opsional dengan pilihan sebagai berikut:
            \- `Tanggal` : isi dengan tanggal dengan format '1945\-08\-17'\. default hari ini
            \- `Kesulitan` : isi dengan angka 1\-5\. default 3
            \- `Penyelenggara` : penyelenggara, defaultnya 'PLD'
            \- `TugasUtama` : isi dengan `true`/`false`\. defaultnya `true`
            \- `Lokasi` : defaultnya 'WFH',
            \- `Lampiran`: isi dengan url lampiran\. defaultnya kosong
        \- Untuk peserta, yang digunakan adalah username groupware\. Username groupware diambil dari username gmail yang digunakan di groupware, misal email `jdsitdev@gmail.com` maka username yang digunakan adalah `jdsitdev`\.
        \- saat ini untuk lampiran hanya mendukung berbentuk url \(blm support upload lampiran\)
        \- semua hasil input groupware bisa di edit lagi melalui akun groupware masing2
        
    \- `/tambah` :  \(COMING SOON\) Menambahkan peserta ke isian laporan yang udah ada\. Cara menggunakan cukup dengan reply pesan laporan sebelumnya dengan format berikut: `/tambah <user_groupware_1> , <user_groupware_2>`

    """
    run_command('/sendMessage', {
        'chat_id': telegram_item['message']['chat']['id'],
        'text': msg,
        'parse_mode': 'MarkdownV2',
    })

def process_telegram_input(item):
    """ process a single telegram update item """
    print('receiving input :', item['message'])
    print('time: {} message_id: {}'.format(
        item['message']['date'], 
        item['message']['message_id']
    ))

    if item['message']['date'] < start_time :
        print('old message, ignoring...')
        return None

    if 'caption' in item['message']:
        input_text = item['message']['caption']
    elif 'text' in item['message']:
        input_text = item['message']['text']
    else:
        print('message contain no text, ignoring...')
        return None

    print('receiving input :', input_text)

    available_commands = {
        '/lapor' : action_lapor,
        '/about' : action_about,
        '/help' : action_help,
    }
    command = input_text.split(' ')[0]

    if command in available_commands :
        available_commands[command](item)
    else:
        # process_error(item, "Unknown command '{}'".format(command))
        print("Unknown command '{}'. ignoring...".format(command))

def loop_updates(updates):
    """ loop through all update from telegram's getUpdates endpoint """
    global processed

    for item in updates:
        if 'message' in item and 'text' in item['message'] \
        and item['message']['message_id'] not in processed \
        and item['message']['date'] < start_time \
        :
            processed.append(item['message']['message_id'])
            process_telegram_input(item)

if __name__ == '__main__':
    import sys
    sleep_interval = 3 if len(sys.argv) < 2 else sys.argv[1]

    while True:
        res = run_command('/getUpdates')
        loop_updates(res['result'])
        time.sleep(3)
