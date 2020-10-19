import models.bot as bot

msg = {}
msg['help'] = "menampilkan command\-command cara untuk menggunakan bot ini"
msg['about'] = "menampilkan penjelasan tentang bot ini"
msg['tambah'] = "Menambahkan user yang mungkin belum tersebut di laporan yang sudah tersubmit dengan command `/lapor`"
msg['whatsnew'] = "mberikan informasi fitur\-fitur atau perubahan\-perubahanyang baru ditambahkan"
msg['setalias'] = "Mengubah alias username telegram untuk salah satu username DigiTeam"
msg['listproject'] = "Menampilkan list semua project yang ada di DigiTeam saat ini"
msg['cekabsensi'] = "Menampilkan daftar user yang belum check\-in di groupware hari ini"

msg['lapor'] = """
Mengirimkan laporan ke aplikasi digiteam groupware JDS"

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

msg['checkin'] = """
Untuk melakukan checkin absensi

Cara menggunakan command `/checkin`:
```
/checkin <username atau alias> | <jenis kehadiran>
```
Catatan
1\. Untuk jenis kehadiran hanya bisa hadir saja
"""

msg['checkout'] = """
Untuk melakukan checkout absensi

Cara menggunakan command `/checkout`:
```
/checkout <username atau alias>
```
"""

def action_help(telegram_item):
    """ action for /help command """

    input_words = telegram_item['message']['text'].split(' ')

    keyboard_data =  {
        'reply_markup' : {
            'inline_keyboard': [
                [ { 'text': cmd, 'callback_data':'help|'+cmd }]
                for cmd in msg
            ],
        },
    }

    if len(input_words) > 1:
        command = input_words[1].lower()
        if command not in msg:
            return bot.reply_message(
                telegram_item,
                'Maaf, help untuk command `{}` tidak ditemukan'.format(command),
                is_markdown=True,
                is_direct_reply=True,
            )
        else:
            return bot.reply_message(
                telegram_item,
                msg[command],
                is_markdown=True,
                is_direct_reply=True,
            )
    else:
        # default: display help button list
        return bot.reply_message(
            telegram_item,
            "Silahkan pilih salah satu tombol di bawah:\n",
            custom_data=keyboard_data
        )

def inline_callback_handler(item):
    input_words = item['callback_query']['data'].split('|')

    bot.run_command('/editMessageText', {
        'chat_id': item['callback_query']['message']['chat']['id'],
        'message_id': item['callback_query']['message']['message_id'],
        'parse_mode': 'MarkdownV2',
        'text': "Command `/{}`: \n{}".format(
            input_words[1],
            msg[input_words[1]]
        ),
    })

    bot.run_command('/answerCallbackQuery', {
        'callback_query_id': item['callback_query']['id'],
    })

    return True
