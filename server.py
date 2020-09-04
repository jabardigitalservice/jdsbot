import json

from flask import Flask, request, jsonify
app = Flask(__name__)

import bot_controller
bot_controller.setup()

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/', methods=['POST'])
def process_telegram():
    input_data = json.loads(request.data)
    bot_controller.process_telegram_input(input_data)
    return 'ok'

if __name__ == "__main__":
    app.run()

