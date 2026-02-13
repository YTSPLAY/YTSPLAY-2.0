# app.py - Чат для Render.com
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Чат</title>
    <script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif;
            background: #1a1a2e;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            width: 100%;
            max-width: 500px;
            height: 90vh;
            background: #16213e;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #0f3460;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .login-box {
            background: #0f3460;
            padding: 30px;
            border-radius: 10px;
            margin: 20px;
        }
        #username {
            width: 100%;
            padding: 15px;
            margin-bottom: 15px;
            border: 2px solid #e94560;
            border-radius: 5px;
            background: #1a1a2e;
            color: white;
        }
        #joinBtn {
            width: 100%;
            padding: 15px;
            background: #e94560;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .chat-header {
            background: #0f3460;
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
        }
        .messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            background: #1a1a2e;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
            max-width: 80%;
            word-break: break-word;
        }
        .my-message {
            background: #0f3460;
            color: white;
            margin-left: auto;
        }
        .other-message {
            background: #16213e;
            color: white;
        }
        .system-message {
            background: #533483;
            color: white;
            text-align: center;
        }
        .input-area {
            display: flex;
            padding: 15px;
            background: #0f3460;
            gap: 10px;
        }
        #messageInput {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 5px;
            background: #1a1a2e;
            color: white;
        }
        #sendBtn {
            padding: 12px 20px;
            background: #e94560;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>💬 Чат онлайн</h2>
            <p>Работает 24/7</p>
        </div>
        
        <div id="loginScreen">
            <div class="login-box">
                <h3 style="color:white;">👋 Вход</h3>
                <input type="text" id="username" placeholder="Твое имя">
                <button id="joinBtn">Войти</button>
            </div>
        </div>
        
        <div id="chatScreen" class="hidden" style="height:100%; display:none; flex-direction:column;">
            <div class="chat-header">
                <span id="userDisplay"></span>
                <span>● Онлайн</span>
            </div>
            <div id="messages" class="messages"></div>
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Сообщение...">
                <button id="sendBtn">→</button>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let currentUser = '';
        
        document.getElementById('joinBtn').onclick = function() {
            const name = document.getElementById('username').value.trim();
            if (!name) return alert('Введи имя!');
            
            currentUser = name;
            socket.emit('join', currentUser);
            
            document.getElementById('loginScreen').style.display = 'none';
            document.getElementById('chatScreen').style.display = 'flex';
            document.getElementById('userDisplay').innerText = 'Вы: ' + currentUser;
        };
        
        document.getElementById('sendBtn').onclick = function() {
            const msg = document.getElementById('messageInput').value.trim();
            if (msg) {
                socket.emit('message', {user: currentUser, text: msg});
                document.getElementById('messageInput').value = '';
            }
        };
        
        document.getElementById('messageInput').onkeypress = function(e) {
            if (e.key === 'Enter') document.getElementById('sendBtn').click();
        };
        
        socket.on('message', function(data) {
            const div = document.createElement('div');
            div.className = 'message';
            
            if (data.user === 'system') {
                div.className += ' system-message';
                div.innerText = data.text;
            } else if (data.user === currentUser) {
                div.className += ' my-message';
                div.innerText = 'Вы: ' + data.text;
            } else {
                div.className += ' other-message';
                div.innerText = data.user + ': ' + data.text;
            }
            
            document.getElementById('messages').appendChild(div);
            document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
        });
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return HTML

@socketio.on('join')
def join(username):
    users[request.sid] = username
    emit('message', {'user': 'system', 'text': f'👋 {username} присоединился'}, broadcast=True)

@socketio.on('message')
def message(data):
    emit('message', data, broadcast=True)

@socketio.on('disconnect')
def disconnect():
    if request.sid in users:
        emit('message', {'user': 'system', 'text': f'👋 {users[request.sid]} покинул чат'}, broadcast=True)
        del users[request.sid]

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
