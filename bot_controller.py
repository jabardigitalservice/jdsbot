"""
This module handle all function regarding bot actions including parsing telegram
update data, sending telegram message, handling command and input, etc
"""
import os, json, time, traceback
from datetime import datetime

import requests
from dotenv import load_dotenv
load_dotenv()

import models.groupware as groupware
import models.bot as bot
import models.user as user

processed=[]
START_TIME = time.time()

def setup():
    """ iniate bot_controller """
    user.load_user_data()

def action_lapor(item):
    """ action for /lapor command """
    # parse input
    if 'caption' in item['message']:
        input_text = item['message']['caption']
    elif 'text' in item['message']:
        input_text = item['message']['text']

    lines = input_text.split("\n")
    first_params = lines[0]
    first_params = first_params[first_params.find(' ')+1 :] # start from after first ' '
    first_params = first_params.split('|') # split with '|' 
    if len(first_params) != 2 :
        bot.process_error(item, 'Mismatched format')
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
        image_data = bot.process_images(item['message']['photo'])
        return bot.process_report(item, data, image_data)
    # if this message is replying to a photo
    elif 'reply_to_message' in item['message'] \
    and 'photo' in item['message']['reply_to_message']:
            image_data = bot.process_images(item['message']['reply_to_message']['photo'])
            return bot.process_report(item, data, image_data)
    else:
        bot.process_error(item, 'No photo data in this input!')
        return None

def action_about(telegram_item):
    """ action for /about command """
    # banyak karakter yang perlu di escape agar lolos parsing markdown di telegram. ref: https://core.telegram.org/bots/api#markdownv2-style
    msg = """Halo\! Aku adalah {}\. Aku ditugaskan untuk membantu melakukan rekap evidence gambar, nama proyek, dan nama task laporan harian otomatis ke aplikasi digiteam groupware\. Silahkan ketik di kolom chat `/help` untuk melihat command\-command yang bisa aku lakukan\! """.format(bot.BOT_NICKNAME)
    return bot.run_command('/sendMessage', {
        'chat_id': telegram_item['message']['chat']['id'],
        'text': msg,
        'parse_mode': 'MarkdownV2',
    })

def action_whatsnew(telegram_item):
    """ action for /whatsnew command """
    # banyak karakter yang perlu di escape agar lolos parsing markdown di telegram. ref: https://core.telegram.org/bots/api#markdownv2-style
    msg = """Update per 30 Agutus 2020:
\- Ada 2 command baru: `/whatsnew` dan `/setalias`
  \- `/whatsnew` memberikan informasi fitur\-fitur atau perubahan\-perubahanyang baru ditambahkan
  \- `/setalias` : Daripada menyebutkan nama username groupware yang belum tentu semua orang hafal, kini kita bisa mendaftarkan akun telegram masing-masing agar dapat ditambahkan dengan mention akun telegram selain dengan akun groupware. Cara menambahkannya adalah dengan memanggil command `/setalias <akun groupware> | <akun telegram>`. Contoh: `/setalias abdurrahman.shofy | @abdurrahman_shofy`
"""
    return bot.run_command('/sendMessage', {
        'chat_id': telegram_item['message']['chat']['id'],
        'text': msg,
        'parse_mode': 'MarkdownV2',
    })

def action_help(telegram_item):
    """ action for /help command """
    msg = """Command\-command yang tersedia:

\- `/help` : menampilkan command\-command cara untuk menggunakan bot ini
\- `/about` : menampilkan penjelasan tentang bot ini
\- `/lapor` : Mengirimkan laporan ke aplikasi digiteam groupware JDS

Cara menggunakan command `/lapor`:
1\. Post dulu gambar evidence nya ke telegram,
2\. Reply gambar tersebut dengan format command seperti berikut :

```
/lapor <nama_project_di_groupware> | <nama_kegiatan>
Peserta: <user_groupware_1> , <user_groupware_2>
```

Keterangan Opsi\-Opsi:
\- `<nama_project_di_groupware>` : isi dengan nama proyek yang ada di aplikasi digiteam groupware\. Harus persis sama besar kecil dan spasinya dengan yang ada di aplikasi digiteam groupware\.
\- `<nama_kegiatan>` : isi dengan nama tugas yang dikerjakan di project tersebut\. bisa diisi dengan teks yang panjang\.
\- `Peserta`: yang digunakan adalah username yang digiteam groupware\. Username groupware diambil dari username gmail yang digunakan di aplikasi digiteam groupware\, misal email `jdsitdev@gmail.com` maka username yang digunakan adalah `jdsitdev`\.

Keterangan tambahan :
\- Semua hasil input di bot telegram ini bisa di edit lagi melalui akun digiteam groupware masing2
\- Kami sudah menyiapkan nilai default untuk Atribut lain\. Silahkan langsung dapat di sesuaikan value atribut lain ini di aplikasi groupware
\- Saat ini kita tengah mengembangkan agar semua atribut ini dapat diisi semua via telegram

Contoh Reply command:
```
/lapor Aplikasi SAPA JDS | Experiment telegram x groupware dari handphone
Peserta: rizkiadam01
```

    """
    return bot.run_command('/sendMessage', {
        'chat_id': telegram_item['message']['chat']['id'],
        'text': msg,
        'parse_mode': 'MarkdownV2',
    })

def action_setalias(telegram_item):
    """ action for /whatsnew command """
    # parse input
    if 'text' in telegram_item['message']:
        input_text = telegram_item['message']['text']

    input_text = input_text.split(' ', maxsplit=1)[1] # start from after first ' '
    val = input_text.split('|')
    res, msg = user.set_alias(val[0].strip(), val[1].strip() )

    print('hasil setalias:', res, msg)

    bot.run_command('/sendMessage', {
        'chat_id': telegram_item['message']['chat']['id'],
        'text': msg,
        'reply_to_message_id': telegram_item['message']['message_id'],
    })

    return None if not res else res

def process_telegram_input(item):
    """ process a single telegram update item 
    Return
    ------
    mixed:
        None is ignoring message
    """
    if 'message' not in item :
        print('update contain no message, ignoring...')
        return None

    print('receiving input :', item['message'])
    print('time: {} message_id: {}'.format(
        item['message']['date'],
        item['message']['message_id']
    ))

    if item['message']['date'] < START_TIME :
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
        '/start' : action_about,
        '/about' : action_about,
        '/help' : action_help,
        '/whatsnew' : action_whatsnew,
        '/setalias' : action_setalias,
    }
    command = input_text.split(' ', maxsplit=1)[0]
    sub_command = command.split('@')
    if len(sub_command) > 1:
        if sub_command[1].upper() != bot.BOT_USERNAME:
            print('command not for this bot, ignoring...')
            return None
        command = sub_command[0]

    if command in available_commands :
        return available_commands[command](item)
    else:
        # bot.process_error(item, "Unknown command '{}'".format(command))
        print("Unknown command '{}'. ignoring...".format(command))
        return None

def loop_updates(updates):
    """ loop through all update from telegram's getUpdates endpoint """
    global processed

    for item in updates:
        if 'message' in item and 'text' in item['message'] \
        and item['message']['message_id'] not in processed \
        and item['message']['date'] < START_TIME \
        :
            processed.append(item['message']['message_id'])
            process_telegram_input(item)

if __name__ == '__main__':
    import sys
    sleep_interval = 3 if len(sys.argv) < 2 else sys.argv[1]

    while True:
        res = bot.run_command('/getUpdates')
        loop_updates(res['result'])
        time.sleep(3)
