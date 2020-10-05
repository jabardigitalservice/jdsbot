"""
This module handle all function regarding bot actions including parsing telegram
update data, sending telegram message, handling command and input, etc
"""
import os, json, time, traceback, re
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv
load_dotenv()

import models.groupware as groupware
import models.bot as bot
import models.user as user
import models.db as db
import models.chat_history as chat_history
import controllers.checkin as checkin

GROUPWARE_WEB_URL=os.getenv('GROUPWARE_WEB_URL')

processed=[]
START_TIME = time.time()

# timezone for Asia/Jakarta (UTC+7)
TIMEZONE = timezone(timedelta(hours=7))

def setup():
    """ iniate bot_controller """
    user.load_user_data()
    os.environ['TZ'] = 'Asia/Jakarta'
    auth_token = user.get_user_token(os.getenv('TEST_USER'))
    groupware.load_project_list(auth_token)

    print('PROJECT_LIST:', groupware.PROJECT_LIST)
    print('user.ALIAS:', user.ALIAS)

def action_lapor(item, peserta=None):
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
        bot.process_error(item, 'Wrong format')
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
                data[field_name] = [
                    name.strip()
                    for name in re.split(',|\ ', content)
                    if len(name.strip()) > 0
                ]
            else:
                data[field_name] = content

    if 'photo' in item['message']:
        image_data = bot.process_images(item['message']['photo'])
    # if this message is replying to a photo
    elif 'reply_to_message' in item['message'] \
    and 'photo' in item['message']['reply_to_message']:
            image_data = bot.process_images(item['message']['reply_to_message']['photo'])
    else:
        bot.process_error(item, 'No photo data in this input!')
        return None

    return bot.process_report(item, data, image_data, peserta=peserta, save_history=(peserta is None))

def action_about(telegram_item):
    """ action for /about command """
    # banyak karakter yang perlu di escape agar lolos parsing markdown di telegram. ref: https://core.telegram.org/bots/api#markdownv2-style
    msg = """Halo\! Aku adalah {}\. Aku ditugaskan untuk membantu melakukan rekap evidence gambar, nama proyek, dan nama task laporan harian otomatis ke aplikasi digiteam groupware\. Silahkan ketik di kolom chat `/help` untuk melihat command\-command yang bisa aku lakukan\! """.format(bot.BOT_NICKNAME)
    return bot.reply_message(telegram_item, msg, is_markdown=True)

def action_whatsnew(telegram_item):
    """ action for /whatsnew command """
    # banyak karakter yang perlu di escape agar lolos parsing markdown di telegram. ref: https://core.telegram.org/bots/api#markdownv2-style
    msg = """Update per 25 September 2020:
\- Beberapa perubahan pesan error untuk peserta yang kosong dan salah format
\- Command baru `/tambah` untuk menambahkan peserta di laporan yang sudah disubmit
"""
    return bot.reply_message(telegram_item, msg, is_markdown=True)

def action_help(telegram_item):
    """ action for /help command """
    msg = """Command\-command yang tersedia:

\- `/help` : menampilkan command\-command cara untuk menggunakan bot ini
\- `/about` : menampilkan penjelasan tentang bot ini
\- `/lapor` : Mengirimkan laporan ke aplikasi digiteam groupware JDS
\- `/tambah` : Menambahkan user yang mungkin belum tersebut di laporan yang sudah tersubmit dengan command `/lapor`
\- `/whatsnew` memberikan informasi fitur\-fitur atau perubahan\-perubahanyang baru ditambahkan
\- `/setalias` : Mengubah alias username telegram untuk salah satu username DigiTeam
\- `/listproject` : Menampilkan list semua project yang ada di DigiTeam saat ini
\- `/cekabsensi` : Menampilkan daftar user yang belum check\-in di groupware hari ini
\- `/checkin` : Untuk melakukan absensi

Cara menggunakan command `/lapor`:
1\. Post dulu gambar evidence nya ke telegram,
2\. Reply gambar tersebut dengan format command seperti berikut :

```
/lapor <nama_project_di_groupware> | <nama_kegiatan>
Peserta: <user_groupware_1> , <user_groupware_2>
```

Cara menggunakan command `/checkin`:
```
/checkin <username atau alias> | <jenis kehadiran> | <tipe> | <keterangan optional>
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
    return bot.reply_message(telegram_item, msg, is_markdown=True)

def action_setalias(telegram_item):
    """ action for /whatsnew command """
    # parse input
    if 'text' in telegram_item['message']:
        input_text = telegram_item['message']['text']

    try:
        input_text = input_text.split(' ', maxsplit=1)[1] # start from after first ' '
        val = input_text.split('|')
        res, msg = user.set_alias(val[0].strip(), val[1].strip() )
    except Exception as e:
        print(e)
        print(traceback.print_exc())
        bot.process_error(telegram_item, e)
        return None

    print('hasil setalias:', res, msg)

    bot.reply_message(telegram_item, msg, is_direct_reply=True)

    return None if not res else res

def action_listproject(telegram_item):
    """ action for /listproject command """
    # banyak karakter yang perlu di escape agar lolos parsing markdown di telegram. ref: https://core.telegram.org/bots/api#markdownv2-style
    msg = "List project\-project di aplikasi DigiTeam saat ini:\n"

    key_list = sorted(list(groupware.PROJECT_LIST.keys()))
    for item in key_list:
        msg += "\- `{}`\n".format(groupware.PROJECT_LIST[item]['originalName'])

    return bot.reply_message(telegram_item, msg, is_markdown=True)

def action_reload(telegram_item):
    """ action for /reload_data command """
    if db.CONNECTION is not None:
        db.CONNECTION.close()

    try:
        setup()
    except Exception as e:
        print(e)
        print(traceback.print_exc())
        bot.process_error(telegram_item, e)
        return None

    return bot.reply_message(telegram_item, 'reload success')

def action_cekabsensi(telegram_item):
    """ action for /cekabsensi command """
    global GROUPWARE_WEB_URL

    now = datetime.now(TIMEZONE)
    attendance_list = user.get_users_attendance(now.strftime('%Y-%m-%d'))
    attendance_msg = ''

    row_num = 1
    for row in sorted(attendance_list):
        if not row[3]:
            attendance_msg += "{}. {} ({})\n".format(
                row_num,
                row[0],
                row[2]
            )

            row_num += 1

    msg = """#INFOABSENSI

Halo-halo digiteam,
Berikut nama-nama yang belum checkin kehadiran hari ini ({} sampai dengan pukul {}) :
{}
Yuk ditunggu buat checkin langsung di aplikasi digiteam ya {}. Terimakasih & Tetap Semangat ❤""".format(
    now.strftime('%Y-%m-%d'), 
    now.strftime('%H:%M'), 
    attendance_msg,
    GROUPWARE_WEB_URL)

    return bot.reply_message(telegram_item, msg)

def action_ngobrol(telegram_item):
    """ chat sebagai bot telegram """
    pecah2 = telegram_item['message']['text'].split(' ', maxsplit=2)

    return bot.run_command('/sendMessage', {
        'chat_id': pecah2[1],
        'text': pecah2[2],
    })

def action_tambah(telegram_item):
    """ tambah peserta ke laporan yg sudah ada """
    if 'reply_to_message' not in telegram_item['message']:
        bot.process_error(telegram_item, 'Command tambah harus me-reply command lapor sebelumnya')
        return None

    history = chat_history.get(
        chat_id=telegram_item['message']['chat']['id'],
        message_id=telegram_item['message']['reply_to_message']['message_id'])

    if history is None:
        bot.process_error(telegram_item, 'Maaf command yang di reply bermasalah. Silahkan coba lagi atau gunakan command lapor')
        return None

    peserta = re.split(',|\ ', telegram_item['message']['text'])
    peserta = [ 
        name
        for name in peserta[1:]
        if len(name.strip()) > 0
    ]
    item = history['content']

    return action_lapor(item, peserta)

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
        '/listproject': action_listproject,
        '/reload_data': action_reload,
        '/cekabsensi': action_cekabsensi,
        '/ngobrol' : action_ngobrol,
        '/tambah' : action_tambah,
        '/checkin' : checkin.action_checkin,
    }
    command = input_text.split(' ', maxsplit=1)[0].strip()
    if command[0] != '/':
        print("First word ({}) is not a command (beginning with '/'). ignoring...".format(command))
        return None

    sub_command = command.split('@')
    if len(sub_command) > 1:
        if sub_command[1].upper() != bot.BOT_USERNAME:
            print('command not for this bot, ignoring...')
            return None
        command = sub_command[0]

    command = command.lower()
    if command not in available_commands :
        bot.process_error(item, "Unknown command '{}'".format(command))
        return None

    try:
        res = available_commands[command](item)
    except Exception as e:
        bot.process_error(item, e)
        return None

    return res

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
