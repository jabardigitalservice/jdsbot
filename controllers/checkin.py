from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import os, requests, json
import models.bot as bot
import models.groupware as groupware
import models.user as user
env_path = Path(__file__).parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

ROOT_API_URL = os.getenv('ROOT_API_URL')
CHECKIN_URL = ROOT_API_URL+'/attendance/checkin/'

def action_checkin(item, peserta=None):
    """ action for /checkin command """
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

    dateNow = datetime.now().strftime('%Y-%m-%d')
    HoursNow = datetime.now().strftime('%H')
    MinuteNow = datetime.now().strftime('%M')
    SecondNow = datetime.now().strftime('%S')
    formatDate = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    username = first_params[0].strip()
    location = first_params[1].strip().upper()

    data = {
        'date': formatDate,
        'location': location,
        'message': "HADIR",
        'note': "",
    }

    getToken = user.get_user_token(username)

    req = requests.post(
        url=CHECKIN_URL,
        headers={
            'Authorization': 'Bearer ' + getToken,
        },
        data=data
    )

    msg = "%s | HADIR %s Pukul %s %s %s" % (username, dateNow ,HoursNow + ":"+MinuteNow, bot.EMOJI_SUCCESS, location)
    responseMessage = json.loads(req.text)
    
    if req.status_code >= 300:
        errors = "%s Checkin Gagal | %s %s " % (username, responseMessage["message"], bot.EMOJI_FAILED)
        return bot.process_error(item, errors)
    else:
        return bot.reply_message(item, msg)
