# # server.py
# from flask import Flask, request
# from flask_socketio import SocketIO, emit
#
# app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*")
#
# @app.route('/')
# def index():
#     return "Socket.IO server is running!"
#
# @socketio.on('get_ip')
# def handle_get_ip():
#     client_ip = request.remote_addr  # Get the client's IP address
#     emit('ip_response', {'ip': client_ip})  # Emit the IP back to the client
#
# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0', port=5000)

# server.py
from flask import Flask, request
from flask_socketio import SocketIO, emit
import socket

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    return "Socket.IO server is running!"


@socketio.on('get_ip')
def handle_get_ip():
    server_ip = socket.gethostbyname(socket.gethostname())  # Get the server's IP address
    client_ip = request.remote_addr  # Get the client's IP address
    emit('ip_response', {'server_ip': server_ip, 'client_ip': client_ip})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)

# the ip address i am showing from server side is my original private address that is locally assigned by my network.
# but this ip is not visible for other because other will only see public ip address.
