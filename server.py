import os, json

from passlib.hash import pbkdf2_sha256

from flask import Flask, request, jsonify, abort
app = Flask(__name__)

import bot_controller
bot_controller.setup()

def verify_token(token):
    """ verifiy access token """
    if not pbkdf2_sha256.verify(token, os.getenv('TOKEN_SECRET')):
        abort(401)

@app.route('/')
def index():
    return "ok"

@app.route('/telegram/<token>', methods=['POST'])
def process_telegram(token=None):
    verify_token(token)

    input_data = json.loads(request.data)
    bot_controller.process_telegram_input(input_data)
    return 'ok'

@app.route('/cekabsensi/<token>', methods=['POST'])
def cek_status(token=None):
    verify_token(token)

    data = {
        'message' : {
            'chat': {
                'id': os.getenv('MAIN_CHAT_ID')
            }
        }
    }
    bot_controller.action_cekabsensi(data)
    return 'ok'

if __name__ == "__main__":
    app.run()

