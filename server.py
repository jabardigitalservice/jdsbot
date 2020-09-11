import json

from flask import Flask, request, jsonify
app = Flask(__name__)

import bot_controller
bot_controller.setup()

@app.route('/')
def index():
    return "ok"

@app.route('/', methods=['POST'])
def process_telegram():
    input_data = json.loads(request.data)
    bot_controller.process_telegram_input(input_data)
    return 'ok'

@app.route('/cekabsensi', methods=['POST'])
def cek_status():
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

