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
    with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        msg = client.get_messages(CHANNEL, ids=msg_id)
        file_size = msg.media.document.size
        
        range_header = request.headers.get('Range')
        
        if range_header:
            byte_start = int(range_header.split('=')[1].split('-')[0])
            byte_end = file_size - 1
            
            def generate():
                downloaded = 0
                for chunk in client.iter_download(msg.media, offset=byte_start, chunk_size=512*1024):
                    if isinstance(chunk, bytes):
                        yield chunk
                        downloaded += len(chunk)
                        if byte_start + downloaded >= byte_end:
                            break
            
            headers = {
                'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(byte_end - byte_start + 1),
                'Content-Type': 'video/mp4',
            }
            return Response(generate(), 206, headers=headers)
        else:
            def generate():
                for chunk in client.iter_download(msg.media, chunk_size=512*1024):
                    if isinstance(chunk, bytes):
                        yield chunk
            
            return Response(generate(), mimetype='video/mp4', headers={
                'Content-Length': str(file_size),
                'Accept-Ranges': 'bytes'
            })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
