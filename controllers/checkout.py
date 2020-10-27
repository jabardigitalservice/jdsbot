from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv
from pathlib import Path
import os, requests, json
import models.bot as bot
import models.groupware as groupware
import models.user as user

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

ROOT_API_URL = os.getenv("ROOT_API_URL")
CHECKOUT_URL = ROOT_API_URL + "/attendance/checkout/"


def action_checkout(item):
    """ action for /checkout command """
    # parse input
    if "caption" in item["message"]:
        input_text = item["message"]["caption"]
    elif "text" in item["message"]:
        input_text = item["message"]["text"]

    lines = input_text.split("\n")
    first_params = lines[0]
    first_params = first_params[
        first_params.find(" ") + 1 :
    ]  # start from after first ' '
    first_params = first_params.split("|")  # split with '|'

    if len(first_params) != 1:
        bot.process_error(item, "Wrong format")
        return

    current_time = datetime.now(timezone("Asia/Jakarta"))
    current_time_utc = current_time.astimezone(timezone("UTC"))

    checkoutDateTimeFormat = current_time_utc.strftime("%Y-%m-%dT%H:%M:%I.000Z")
    dateNow = current_time.strftime("%Y-%m-%d")
    hourMinuteNow = current_time.strftime("%H:%M")

    username = first_params[0].strip()

    data = {
        "date": checkoutDateTimeFormat,
    }

    getToken = user.get_user_token(username)

    req = requests.post(
        url=CHECKOUT_URL,
        headers={
            "Authorization": "Bearer " + getToken,
        },
        data=data,
    )

    msg = "%s | Checkout Pukul %s %s" % (username, hourMinuteNow, bot.EMOJI_SUCCESS)
    responseMessage = json.loads(req.text)

    if req.status_code >= 300:
        errors = "%s | Checkout Gagal | %s %s " % (
            username,
            responseMessage["message"],
            bot.EMOJI_FAILED,
        )
        return bot.process_error(item, errors)
    else:
        return bot.reply_message(item, msg)
