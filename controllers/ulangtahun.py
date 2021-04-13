from datetime import datetime
import random

import models.bot as bot
import models.user as user

pantun = [
"""Sakitnya parah digigit lebah
Obatnya luka dikasih madu
Tak ada kata yang lebih indah
Selain peluk cium di hari ultahmu""",

"""Ibu-ibu nonton dangdutan
Adik kecil sukanya nonton kartun
Pantes aja jempolku kedutan
Ternyata kamu lagi ulang tahun""",

"""Terbang ke Eropa singgah di Norwegia
Berjalan ke timur sampai bandara
Kepada sahabat yang sedang bahagia
Moga panjang umur dan sejahtera""",

"""Tak Gendong lagunya Mbah Surip,
Demi Waktu lagunya Pasha Ungu,
Selamat ulang tahun sobat karip,
Selamat menua dan sukses selalu.""",

"""Pergi sekolah naik sepeda,
Pulangnya pas pukul satu,
Dari hati yang penuh cinta,
Kita ucapkan selamet ultah buat kamu""",

"""Aku mungkin tak berada di sisi kamu, merayakan hari istimewamu bersama. Tapi aku ingin kamu tahu bahwa, namamu selalu ada di doa ku!""",

"""Alam menginginkanmu untuk merayakan dan menghargai hidupmu tiap tahun. Karena itu ia memberimu hari ulang tahun.""",

"""Kita semua pernah menjadi lilin ulang tahun untuk orang yang kita cintai.
Menerangi
Menemani
Merayakan
Lalu ditiup hingga mati.
Dan kemudian orang-orang disekitarnya bahagia.
Ya, Hidup adalah tentang legacy""",

"""Jangan pernah ada kata putus asa dan menyerah. Temukan ratusan bahkan ribuan alasan untuk terus berjuang. Selamat naik level kawanku, See you on Top""",
]


def action(telegram_item):
    """ action for /ulangtahun command """
    now = datetime.now()

    list_msg = "\n".join([
        str(idx+1) + \
            f". {item[0]}" + \
            (f"({item[2]})" if item[2] is not None else "") + \
            f" - {item[1]}"
        for idx, item
        in enumerate(user.get_users_by_birthday(now))
    ])

    msg = """"{}"

Yeaaay, Happy Anniversary hari ini ({}) buat :
{}

Semoga sehat selalu, dimudahkan rezekinya, dilancarkan setiap urusannya, dan semakin ngabreet. Wish you all the best 🥳🎂❤️
    """.format(
            random.choice(pantun),
            now.strftime('%d-%m-%Y'),
            list_msg,
        )

    return bot.reply_message(telegram_item,  msg)
