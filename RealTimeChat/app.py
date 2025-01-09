from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Store connected users
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('broadcast_message')
def handle_broadcast_message(data):
    emit('receive_message', {
        'username': data['username'], 
        'message': data['message']
    }, broadcast=True)

@socketio.on('private_message')
def handle_private_message(data):
    recipient = data['recipient']
    if recipient in users:
        emit('receive_private_message', {
            'sender': data['username'],
            'message': data['message']
        }, room=users[recipient])

@socketio.on('register_username')
def handle_username_registration(username):
    users[username] = request.sid

if __name__ == '__main__':
    socketio.run(app, debug=True)
