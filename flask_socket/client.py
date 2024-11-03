# # client.py
# import socketio
#
# # Create a Socket.IO client instance
# sio = socketio.Client()
#
# # Define the event handler for receiving the IP response
# @sio.on('ip_response')
# def on_ip_response(data):
#     print("Your IP address is:", data['ip'])
#     sio.disconnect()  # Disconnect after receiving the response
#
# # Connect to the server
# sio.connect('http://localhost:5000')
#
# # Emit the event to request the IP
# sio.emit('get_ip')
#
# # Keep the client running to receive the response
# sio.wait()
# client.py
import socketio

# Create a Socket.IO client instance
sio = socketio.Client()

# Define the event handler for receiving the IP response
@sio.on('ip_response')
def on_ip_response(data):
    print("Server IP address is:", data['server_ip'])
    print("Your IP address is:", data['client_ip'])
    sio.disconnect()  # Disconnect after receiving the response

# Connect to the server
sio.connect('http://localhost:5000')

# Emit the event to request the IP
sio.emit('get_ip')

# Keep the client running to receive the response
sio.wait()
