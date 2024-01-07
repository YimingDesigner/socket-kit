from socket_kit import socket
from socket_kit import vision

client = socket.createClient("localhost", 9999)
capture = vision.createCapture()

while True:
    try:
        ret, frame = capture.read()
        message = socket.packFrame(frame)
        client.sendall(message)
    except: break

client.close()