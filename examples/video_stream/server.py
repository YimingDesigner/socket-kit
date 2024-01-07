from socket_kit import socket
from socket_kit import vision

server = socket.createServer("localhost", 9999)

message = b""
while True:
    client, address = server.accept()
    print("Connected with", address)

    while True:
        frame, message = socket.receiveFrame(client, message=message)
        shown = vision.showFrame("frame", frame)
        if not shown: break;

    client.close()