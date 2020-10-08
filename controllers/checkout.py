from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv
from pathlib import Path
import os, requests, json
import models.bot as bot
import models.groupware as groupware
import models.user as user
env_path = Path(__file__).parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

ROOT_API_URL = os.getenv('ROOT_API_URL')
ATTENDANCE_API_URL = ROOT_API_URL+'/attendance/checkout/'

def action_checkout(item, peserta=None):
    """ action for /checkout command """
    # parse input
    if 'caption' in item['message']:
        input_text = item['message']['caption']
    elif 'text' in item['message']:
        input_text = item['message']['text']

    lines = input_text.split("\n")
    first_params = lines[0]
    first_params = first_params[first_params.find(' ')+1 :] # start from after first ' '
    first_params = first_params.split('|') # split with '|
    
    if len(first_params) != 1 :
        bot.process_error(item, 'Wrong format')
        return

    data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
    }

    data['date'] += groupware.TIMESTAMP_TRAIL_FORMAT
    getToken = user.get_user_token(first_params[0].strip())
    req = requests.post(
        url=ATTENDANCE_API_URL,
        headers={
            'Authorization': 'Bearer ' + getToken,
        },
        data=data
    )
    
    msg = first_params[0].strip()+" Berhasil Melakukan checkout "+bot.EMOJI_SUCCESS
    responseMessage = json.loads(req.text)
    if req.status_code >= 300:
        errors = "Groupware status code : {} \n\nMohon maaf, ".format(req.status_code) + first_params[0].strip() + " " + responseMessage["message"]
        return bot.process_error(item, errors)
    else:
        return bot.reply_message(item, msg)
