from datetime import datetime

import models.groupware as groupware
import models.bot as bot
import models.user as user

def action_cekabsensi(telegram_item):
    """ action for /cekabsensi command """
    now = datetime.now()
    attendance_list = user.get_users_attendance(now.strftime('%Y-%m-%d'))
    attendance_msg = ''

    divisi = None
    input_data = telegram_item['message']['text'].strip().split(' ')
    if len(input_data) > 1 :
        divisi = input_data[1].lower()
        attendance_list = [
            row
            for row
            in attendance_list
            if row[4][:2].lower() == divisi[:2]
        ]

    row_num = 1
    for row in sorted(attendance_list):
        if not row[3]:
            attendance_msg += "{}. {} ({})\n".format(
                row_num,
                row[1],
                row[2]
            )

            row_num += 1

    if (len(attendance_msg) > 1):
        msg = """
Halo DigiTeam! Presensi kehadiran dan laporan harianmu adalah tanggung jawab sekaligus syarat untuk administrasi penggajian.

Berikut nama-nama yang belum Check In hari ini ({}/{}).

{}

Yuk, maksimalkan aplikasi DigiTeam untuk mudahkan pekerjaanmu!

Semangat dan sehat selalu! Hatur nuhun!
    """.format(
            now.strftime('%d-%m-%Y'),
            now.strftime('%H:%M'),
            attendance_msg
        )
    else:
        msg = """

Yeaaay, presensi hari ini ({}) sudah lengkap! {} orang sudah mengisi presensi hari ini.

Terima kasih banyak buat dedikasi dan kontribusi Digiteam semua untuk mengakselerasi digitalisasi di Jawa Barat. Tetap jaga iman, imun & aman, ya, teman-teman  🥳🥳🥳
    """.format(
            now.strftime('%d-%m-%Y'),
            len(attendance_list)
        )

    if divisi is None:
        msg = "#INFOABSENSI" + msg
    else:
        msg = f"#INFOABSENSI DIVISI {divisi.upper()}" + msg

    return bot.reply_message(telegram_item, msg)

