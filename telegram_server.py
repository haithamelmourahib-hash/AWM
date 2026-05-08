from telethon import TelegramClient
from telethon.tl.types import InputChannel
from flask import Flask, jsonify, request
from flask_cors import CORS
import os, asyncio

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
CHANNEL = os.environ['CHANNEL_ID']
SESSION = os.environ['SESSION_STRING']

app = Flask(__name__)
CORS(app)
client = TelegramClient('session', API_ID, API_HASH)

@app.route('/video/<int:msg_id>')
async def get_video(msg_id):
    await client.connect()
    msg = await client.get_messages(CHANNEL, ids=msg_id)
    url = await client.download_media(msg, file=bytes)
    return jsonify({'url': f'data:video/mp4;base64,{url.hex()}'})

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

