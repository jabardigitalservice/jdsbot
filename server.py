import os, json

from passlib.hash import pbkdf2_sha256

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks

app = FastAPI()

import controllers.main as main_controller
import controllers.cekabsensi as cekabsensi
import controllers.healthcheck as healthcheck
main_controller.setup()

def verify_token(token):
    """ verifiy access token """
    if not pbkdf2_sha256.verify(token, os.getenv('TOKEN_SECRET')):
        raise HTTPException(status_code=401, detail="Not Authorized")

@app.get('/')
def index():
    return healthcheck.run()

@app.post('/telegram/{token}')
async def process_telegram(request: Request, background_tasks: BackgroundTasks, token=None):
    verify_token(token)

    input_data = await request.json()
    background_tasks.add_task(main_controller.process_telegram_input, input_data)
    return 'ok'

@app.post('/cekabsensi/{token}')
async def cek_absensi(request: Request, background_tasks: BackgroundTasks, token=None):
    verify_token(token)

    # if today is a holiday, skip
    if main_controller.is_today_holiday():
        return 'ok'

    data = {
        'message' : {
            'chat': {
                'id': os.getenv('MAIN_CHAT_ID')
            }
        }
    }
    background_tasks.add_task(cekabsensi.action_cekabsensi, data)
    return 'ok'

@app.post('/ulangtahun/{token}')
async def ulangtahun(request: Request, background_tasks: BackgroundTasks, token=None):
    verify_token(token)

    data = {
        'message' : {
            'chat': {
                'id': os.getenv('MAIN_CHAT_ID')
            }
        }
    }
    background_tasks.add_task(cekabsensi.action_cekabsensi, data)
    return 'ok'

