from socket_kit import socket
from os import listdir

client = socket.createClient("localhost", 9999)

folder = "/Users/yimingliu/Developer/Python Packages/socket-kit/examples/file_sender"
fileNames = [f for f in listdir(folder)]
for fileName in fileNames:
    message = socket.packFile(folder + "/" + fileName)
    client.sendall(message)
    print(f"File \"{fileName}\" send successfully.")

client.close()