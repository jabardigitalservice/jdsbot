import re
import models.bot as bot
import models.chat_history as chat_history
from controllers.lapor import action_lapor


def action_tambah(telegram_item):
    """ tambah peserta ke laporan yg sudah ada """
    if "reply_to_message" not in telegram_item["message"]:
        bot.process_error(
            telegram_item, "Command tambah harus me-reply command lapor sebelumnya"
        )
        return None

    history = chat_history.get(
        chat_id=telegram_item["message"]["chat"]["id"],
        message_id=telegram_item["message"]["reply_to_message"]["message_id"],
    )

    if history is None:
        bot.process_error(
            telegram_item,
            "Maaf command yang di reply bermasalah. Silahkan coba lagi atau gunakan command lapor",
        )
        return None

    peserta = re.split(",|\ ", telegram_item["message"]["text"])
    peserta = [name for name in peserta[1:] if len(name.strip()) > 0]
    item = history["content"]

    return action_lapor(item, peserta)
