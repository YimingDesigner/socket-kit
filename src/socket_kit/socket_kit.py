import socket
import struct
import pickle
import cv2, numpy
import hashlib
import mysql.connector
from time import sleep
import logging

# Server, Client

def createServer(IP: str, port: int, clientNum: int = 3) -> socket.socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created. Binding to IP", IP)
    server.bind((IP, port))
    server.listen(clientNum)
    print("Server start at ", IP)
    print("Waiting for connection...")
    return server

def createdLocalhostServer(port: int, clientNum: int = 3) -> socket.socket:
    server = createServer("localhost", port, clientNum)
    return server

def createdLocalIPServer(port: int, clientNum: int = 3) -> socket.socket:
    localIP = socket.gethostbyname(socket.gethostname())
    server = createServer(localIP, port, clientNum)
    return server

def createClient(serverIP: str, port: int) -> socket.socket:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((serverIP, port))
    print("Connected to server ", serverIP)
    return client

# Database and Authentication

class MySQLDatabase:
    def __init__(self, databaseName: str, host: str = "localhost", username: str = "root", password: str = "") -> None:
        self.host = host
        self.username = username
        self.password = password
        self.databaseName = databaseName

    def connect(self):
        connection = mysql.connector.connect(
            host = self.host,
            user = self.username,
            password = self.password,
            database = self.databaseName
        )
        return connection

    def createTable(self, title: str, fields: str):
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {title} ( {fields} )")

    def createUserTabel(self, title: str = "userdata"):
        self.createTable(title, """
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        """)

    def createUser(self, username: str, password: str):
        connection = self.connect()
        cursor = connection.cursor()
        password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO userdata (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()

    def userAuthenticate(self, username: str, password: str) -> bool:
        connection = self.connect()
        cursor = connection.cursor()
        password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT * FROM userdata WHERE username = %s AND password = %s", (username, password))
        if cursor.fetchall():
            return True
        else:
            return False

def userAuthenticate(client: socket.socket, database: MySQLDatabase) -> bool:
    isAuthenticated = False
    while not isAuthenticated:
        try:
            client.send("Username: ".encode())
            username = client.recv(1024).decode()
            client.send("Password: ".encode())
            password = client.recv(1024).decode()

            if database.userAuthenticate(username, password):
                client.send("success".encode())
                sleep(0.1)
                client.send("Login successfully.".encode())
                isAuthenticated = True
            else:
                client.send("failed".encode())
                sleep(0.1)
                client.send("Login failed. Please try again.".encode())
                sleep(1)
        except Exception as error:
            logging.exception(error)
            return False
    return True

def userLogin(client: socket.socket, username: str, password: str):
    message = client.recv(1024).decode()
    client.send(username.encode())
    message = client.recv(1024).decode()
    client.send(password.encode())

    isLogin = client.recv(1024).decode()
    print(client.recv(1024).decode())
    
    if isLogin == "success":
        return True
    else:
        return False

def userLoginCLI(client: socket.socket):
    isLogin = "failed"
    while isLogin != "success":
        message = client.recv(1024).decode()
        username = input(message).encode()
        client.send(username)
        message = client.recv(1024).decode()
        password = input(message).encode()
        client.send(password)

        isLogin = client.recv(1024).decode()
        print(client.recv(1024).decode())

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
    with open(filePath, "rb") as file:
        data = file.read()
        message = packData(data)
        return message

def receiveStreamData(message: bytes, client: socket.socket, bufferSize: int = 4096) -> (bytes, bytes):
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

def receiveStreamFrame(message: bytes, client: socket.socket, bufferSize: int = 4096) -> (numpy.array, bytes):
    data, remainedMessage = receiveStreamData(message, client, bufferSize)
    buffer = pickle.loads(data)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    return frame, remainedMessage

def receiveData(client: socket.socket, bufferSize: int = 4096) -> bytes:
    data, remainedMessage = receiveStreamData(b"", client, bufferSize)
    return data

def receiveFrame(client: socket.socket, bufferSize: int = 4096) -> numpy.array:
    data = receiveData(client, bufferSize)
    buffer = pickle.loads(data)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    return frame

def receiveFile(savePath: str, client: socket.socket, bufferSize: int = 4096):
    data = receiveData(client, bufferSize)
    with open(savePath, "wb") as file:
        file.write(data)

# OpenCV

def createCapture(cameraNum: int = 0, frameWidth: float = None, frameHeight: float = None, frameRate: float = None) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(cameraNum)
    if frameWidth != None: capture.set(cv2.CV_CAP_PROP_FRAME_WIDTH, int(frameWidth))
    if frameHeight != None: capture.set(cv2.CV_CAP_PROP_FRAME_HEIGHT, int(frameHeight))
    if frameRate != None: capture.set(cv2.CAP_PROP_FPS, int(frameRate))
    if not capture.isOpened(): raise Exception("No camera found or cannot be opened.")
    return capture

def createWriter(capture: cv2.VideoCapture, fileName: str) -> cv2.VideoWriter:
    frameWidth = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frameHeight = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frameRate = int(capture.get(cv2.CAP_PROP_FPS))
    fileName = fileName
    writer = cv2.VideoWriter(fileName, cv2.VideoWriter_fourcc(*"H264"), frameRate, (frameWidth, frameHeight))
    print("Writer created at", fileName, "with", frameWidth, "*", frameHeight, frameRate, "fps")
    return writer

def saveFrameToPhoto(frame: numpy.array, savePhotoName: str):
    cv2.imwrite(savePhotoName, frame)

def saveFrameToMovie(frame: numpy.array, writer: cv2.VideoWriter):
    writer.write(frame)

def showFrame(title: str, frame: numpy.array) -> bool:
    cv2.imshow(title, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyWindow(title)
        cv2.waitKey(1)
        return False
    return True