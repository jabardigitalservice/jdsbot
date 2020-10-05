from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv
from pathlib import Path
import os, requests
import models.bot as bot
import models.groupware as groupware
import models.user as user
env_path = Path(__file__).parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

ROOT_API_URL = os.getenv('ROOT_API_URL')
ATTENDANCE_API_URL = ROOT_API_URL+'/attendance/checkin/'

def action_checkin(item, peserta=None):
    # define date format output i am get hours and minute
    fmt = '%Y-%m-%d %H:%M:%i'
    # define indonesia timezone default asia/jakarta
    jakarta = timezone('Asia/Jakarta')
    # localized datetime now
    loc_dt = datetime.now(jakarta)

    idDateFormat = loc_dt.strftime(fmt)

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
    
    try:
        notes = first_params[3].strip()
    except IndexError:
        message = None
        location = None
        notes = ""

    data = {
        'date': idDateFormat,
        'location': first_params[2].strip().upper(),
        'message': first_params[1].strip().upper(),
        'note': notes,
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
    
    msg = first_params[0].strip()+" Berhasil Melakukan absensi "+bot.EMOJI_SUCCESS

    errors = []
    if req.status_code >= 300:
        errors.append("Groupware status code : {}\n\nMohon maaf, sedang ada ganguan pada sistem groupware. Silahkan coba lagi setelah beberapa saat".format(req.status_code))
        msg = ''.join([
            "\n- " + str(e)
            for e in errors
        ])
        return bot.process_error(item, msg)
    else:
        return bot.reply_message(item, msg)