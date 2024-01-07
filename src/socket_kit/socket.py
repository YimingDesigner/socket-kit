import socket
import struct
import pickle
import cv2, numpy
from os import path

# Server, Client

def createServer(IP: str, port: int, clientNum: int = 3) -> socket.socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Socket created. Binding to IP \"{IP}\"")
    server.bind((IP, port))
    server.listen(clientNum)
    print(f"Server start at \"{IP}\"")
    print("Waiting for connection...")
    return server

def createdLocalIPServer(port: int, clientNum: int = 3) -> socket.socket:
    localIP = socket.gethostbyname(socket.gethostname())
    server = createServer(localIP, port, clientNum)
    return server

def createClient(serverIP: str, port: int) -> socket.socket:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((serverIP, port))
    print(f"Connected to server \"{serverIP}\"")
    return client

# Data Transfer

def packData(data: bytes) -> bytes:
    size = struct.pack("Q", len(data))
    message = size + data
    return message

def packFrame(frame: numpy.arange, format: str = ".jpg", quality: int = 95) -> bytes:
    encodeParams = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    ret, buffer = cv2.imencode(format, frame, encodeParams)
    if ret:
        frameData = pickle.dumps(buffer)
        message = packData(frameData)
        return message
    else: return b""

def packFile(filePath: str) -> bytes:
    fileName = path.basename(filePath)
    nameMessage = packData(fileName.encode())
    with open(filePath, "rb") as file:
        data = file.read()
        message = packData(data)
        return nameMessage + message

def receiveData(client: socket.socket, message: bytes = b"", bufferSize: int = 4096) -> tuple[bytes, bytes]:
    sizeSize = struct.calcsize("Q")

    while len(message) < sizeSize:
        packet = client.recv(bufferSize)
        if not packet: Exception("No enough data. Maybe message transferring is broken.")
        message += packet
    size = message[:sizeSize]
    message = message[sizeSize:]

    size = struct.unpack("Q", size)[0]

    while len(message) < size:
        packet = client.recv(bufferSize)
        if not packet: Exception("No enough data. Maybe message transferring is broken.")
        message += packet
    data = message[:size]
    remainedMessage = message[size:]

    return data, remainedMessage

def receiveFrame(client: socket.socket, message: bytes = b"", bufferSize: int = 4096) -> tuple[numpy.array, bytes]:
    data, remainedMessage = receiveData(client, message=message, bufferSize=bufferSize)
    buffer = pickle.loads(data)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    return frame, remainedMessage

def receiveFile(client: socket.socket, saveFolder: str, saveFile: str = "", message: bytes = b"", bufferSize: int = 4096) -> tuple[str, bytes]:
    nameData, remainedMessage = receiveData(client, message=message, bufferSize=bufferSize)
    if saveFile == "": fileName = nameData.decode()
    else: fileName = saveFile
    
    data, remainedMessage = receiveData(client, message=remainedMessage, bufferSize=bufferSize)
    with open(saveFolder + "/" + fileName, "wb") as file:
        file.write(data)
    return (saveFolder + "/" + fileName), remainedMessage
