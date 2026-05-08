from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from flask import Flask, Response, request
from flask_cors import CORS
import os

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
    def generate():
        with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
            msg = client.get_messages(CHANNEL, ids=msg_id)
            for chunk in client.iter_download(msg.media, chunk_size=512*1024):
                yield chunk
    return Response(generate(), mimetype='video/mp4', headers={
        'Accept-Ranges': 'bytes',
        'Content-Disposition': 'inline'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
