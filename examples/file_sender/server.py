from socket_kit import socket

server = socket.createServer("localhost", 9999)

message = b""
while True:
    client, address = server.accept()
    print("Connected with", address)

    saveFolder = "/Users/yimingliu/Developer/Python Packages/socket-kit/examples/file_sender/testFolder"
    filePath, message = socket.receiveFile(client, saveFolder=saveFolder, saveFile="myFile.txt", message=message)
    print(f"Received file saved to \"{filePath}\".")

    client.close()