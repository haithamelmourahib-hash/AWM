from telethon import TelegramClient
from telethon.sessions import StringSession
from flask import Flask, Response, request
from flask_cors import CORS
import os, asyncio

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
CHANNEL = int(os.environ['CHANNEL_ID'])
SESSION = os.environ['SESSION_STRING']

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return 'OK'

@app.route('/video/<int:msg_id>')
def get_video(msg_id):
    async def generate():
        client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
        await client.connect()
        msg = await client.get_messages(CHANNEL, ids=msg_id)
        async for chunk in client.iter_download(msg.media):
            yield chunk
        await client.disconnect()
    return Response(generate(), mimetype='video/mp4', headers={
        'Accept-Ranges': 'bytes',
        'Content-Disposition': 'inline'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
