import models.bot as bot

msg = {}
msg['default'] = """Command\-command yang tersedia:

\- `/help` : menampilkan command\-command cara untuk menggunakan bot ini
\- `/about` : menampilkan penjelasan tentang bot ini
\- `/lapor` : Mengirimkan laporan ke aplikasi digiteam groupware JDS
\- `/tambah` : Menambahkan user yang mungkin belum tersebut di laporan yang sudah tersubmit dengan command `/lapor`
\- `/whatsnew` memberikan informasi fitur\-fitur atau perubahan\-perubahanyang baru ditambahkan
\- `/setalias` : Mengubah alias username telegram untuk salah satu username DigiTeam
\- `/listproject` : Menampilkan list semua project yang ada di DigiTeam saat ini
\- `/cekabsensi` : Menampilkan daftar user yang belum check\-in di groupware hari ini
\- `/checkin` : Untuk melakukan absensi
\- `/checkout` : Untuk melakukan checkout absensi

Untuk mendapatkan bantuan detail dari command\-command di atas, silahkan gunakan command `/help <nama_command` \. contoh: `/help lapor`
"""

msg['lapor'] = """
Cara menggunakan command `/lapor`:
1\. Post dulu gambar evidence nya ke telegram,
2\. Reply gambar tersebut dengan format command seperti berikut :

```
/lapor <nama_project_di_groupware> | <nama_kegiatan>
tanggal : isi dengan tanggal dengan format '1945-08-17'. Default hari ini
kesulitan : isi dengan angka 1-5. Default 3
penyelenggara : penyelenggara, Defaultnya 'PLD'
tugasUtama : isi dengan true/false. Defaultnya true
lokasi : isi lokasi mengerjakan task tersebut, defaultnya 'WFH',
lampiran: isi dengan url lampiran. defaultnya kosong. Saat ini untuk lampiran hanya mendukung berbentuk url
peserta: <user_digiteam_1> <user_digiteam_2>
```
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-

Contoh Reply nya sebagai berikut ya :

```
/lapor Digiteam | Experiment telegram x groupware
tanggal: 2020-08-26
kesulitan: 5
penyelenggara: PLD
tugasUtama: false
lokasi: Command Center Jabar
lampiran: https://groupware.digitalservice.id/#/report
peserta: rizkiadam01 @abdurrahman_adianto @ArifWicakSon
```

\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-

Keterangan :
1\. Semua atribut hasil input di bot telegram ini bisa di edit lagi melalui akun digiteam di web masing\-masing
2\. Atribut yang wajib diisi adalah `<nama_project_di_groupware>`\, `<nama_kegiatan>` \& `<nama peserta>`\. Selain atribut tersebut optional untuk diisi

"""

msg['tambah'] = """
Cara menggunakan command `/tambah`:

Reply command `/lapor` yang ingin ditambahkan pesertanya dengan command berikut:
```
/tambah <nama peserta 1> <nama peserta 2> <seterusnya...>
```
daftar peserta dipisahkan dengan spasi atau koma
"""

msg['checkin'] = """
Cara menggunakan command `/checkin`:
```
/checkin <username atau alias> | <jenis kehadiran>
```
Catatan
1\. Untuk jenis kehadiran hanya bisa hadir saja
"""

msg['checkout'] = """
Cara menggunakan command `/checkout`:
```
/checkout <username atau alias>
```
"""

msg['listproject'] = """
Cara menggunakan command `/listproject`:

Cukup panggil command `/listproject`
"""

def action_help(telegram_item):
    """ action for /help command """
    input_words = telegram_item['message']['text'].split(' ')
    pre_msg = ''

    if len(input_words) < 2 :
        command = 'default'
    else:
        command = input_words[1].lower()

    if command not in msg:
        pre_msg = 'Help untuk command `{}` tidak ditemukan\. '.format(command)
        command = 'default'

    # create 2 column keyboard layout
    keyboard=[]
    i = 0
    for cmd in msg.keys():
        if cmd == 'default':
            continue
        if i%2 == 0 :
            keyboard.append([])
        keyboard[i//2].append({ 'text': '/help ' + cmd })
        i = i + 1

    keyboard_data = None if command != 'default' else {
        'reply_markup' : {
            # create 2 row keyboard layout
            'keyboard': keyboard,
            'one_time_keyboard' : True,
            'selective': False,
            'resize_keyboard': True,
        },
    }

    return bot.reply_message(
        telegram_item,
        pre_msg + msg[command],
        is_markdown=True,
        is_direct_reply=True,
        custom_data=keyboard_data
    )
