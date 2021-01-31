"""
- measurement protocol docs: https://developers.google.com/analytics/devguides/collection/protocol/v1/devguide
- parameter references: https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters
"""
import os, hashlib, uuid
from pathlib import Path

import requests
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent /  '.env'
load_dotenv(dotenv_path=env_path)

GOOGLE_ANALYTIC_TRACKING_ID=os.getenv('GOOGLE_ANALYTIC_TRACKING_ID')
GOOGLE_ANALYTIC_API_URL='https://www.google-analytics.com/collect'
GOOGLE_ANALYTIC_DEBUG_URL='https://www.google-analytics.com/debug/collect'

def log_analytics(data, is_debug=False):
    """ send google analytic data """
    data['v']=1             # Version.
    data['tid']=GOOGLE_ANALYTIC_TRACKING_ID  # Tracking ID / Property ID.
    data['ds']='telegram_bot' # data source

    url = GOOGLE_ANALYTIC_API_URL \
        if not is_debug else \
        GOOGLE_ANALYTIC_DEBUG_URL

    r = requests.post(url, data)
    if r.status_code >= 300:
        raise ValueError('google analytic api return status code {}'.format(r.status_code))

    return True if not is_debug else r.text

def log_user_checkin(username, result=None, is_debug=False):
    data = {
        't': 'event',         # Event hit type
        'uid': hashlib.sha1(username.encode()).hexdigest(),  # user ID.
        'ec': 'kehadiran',        # Event Category. Required.
        'ea': 'checkin',         # Event Action. Required.
    }
    if result is not None:
        data['el'] = result      # Event label.
    return log_analytics(data, is_debug)

def log_command_call(command, is_debug=False):
    data = {
        't': 'pageview',         # Event hit type
        'uid': str(uuid.uuid4()),  # user ID.
        'dp': command,         # page. in our case, command.
        # 'dh': mydemo.com   // Document hostname.
        # 'dt': homepage     // Title.
    }
    return log_analytics(data, is_debug)

if __name__ == '__main__':
    res = log_user_checkin('abdurrahman.shofy', is_debug=True)
    print('result:',res)

    res = log_command_call('/help', is_debug=True)
    print('result:',res)
