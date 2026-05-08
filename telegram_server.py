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
    range_header = request.headers.get('Range', None)
    
    with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        msg = client.get_messages(CHANNEL, ids=msg_id)
        file_size = msg.media.document.size
        
        start = 0
        end = file_size - 1
        
        if range_header:
            parts = range_header.replace('bytes=', '').split('-')
            start = int(parts[0])
            end = int(parts[1]) if parts[1] else min(start + 1024*1024, file_size - 1)
        
        chunk_size = end - start + 1
        
        def generate():
            with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as c:
                msg = c.get_messages(CHANNEL, ids=msg_id)
                for chunk in c.iter_download(msg.media, offset=start, limit=chunk_size, chunk_size=512*1024):
                    yield chunk
        
        headers = {
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(chunk_size),
            'Content-Type': 'video/mp4',
        }
        
        return Response(generate(), 206 if range_header else 200, headers=headers, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
