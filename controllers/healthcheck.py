import json
import traceback
from fastapi import HTTPException

import models.db as db
import models.bot as bot
import models.groupware as groupware

def run():
    """ get healtcheck status of Digiteam Telegram Bot """
    try:
        db_status = db.is_db_connected()
        groupware_api_status = groupware.is_groupware_api_reachable()
        telegram_status = bot.run_command('/getwebhookinfo')

        return {
            'webserver': {
                'ok': True,
                'message': None,
            },
            'database': {
                'ok': db_status[0],
                'message': db_status[1],
            },
            'groupware_api': {
                'ok': groupware_api_status[0],
                'message': groupware_api_status[1],
            },
            'telegram': {
                'ok': telegram_status['ok'],
                'message': json.dumps(telegram_status['result']),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, message=json.dumps({
            'err_msg': str(e),
            'traceback': traceback.format_exc(),
        }))


