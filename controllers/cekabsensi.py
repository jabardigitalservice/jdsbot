from datetime import datetime

import models.groupware as groupware
import models.bot as bot
import models.user as user


def action_cekabsensi(telegram_item):
    """ action for /cekabsensi command """
    now = datetime.now()
    attendance_list = user.get_users_attendance(now.strftime("%Y-%m-%d"))
    attendance_msg = ""

    row_num = 1
    for row in sorted(attendance_list):
        if not row[3]:
            attendance_msg += "{}. {} ({})\n".format(row_num, row[0], row[2])

            row_num += 1

    msg = """#INFOABSENSI
Halo DigiTeam! Presensi kehadiran dan laporan harianmu adalah tanggung jawab sekaligus syarat untuk administrasi penggajian.

Berikut nama yang belum Check In hari ini ({}/{}).

{}

Yuk, maksimalkan aplikasi DigiTeam untuk mudahkan pekerjaanmu!

Semangat dan sehat selalu! Hatur nuhun!
""".format(
        now.strftime("%d-%m-%Y"), now.strftime("%H:%M"), attendance_msg
    )

    return bot.reply_message(telegram_item, msg)
