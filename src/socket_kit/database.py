import socket
import mysql.connector
import hashlib
import random, string
from time import sleep
import logging

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
            password VARCHAR(255) NOT NULL,
            note VARCHAR(65535)
        """)

    def createUser(self, username: str, password: str):
        connection = self.connect()
        cursor = connection.cursor()
        password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO userdata (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()
    
    def createUserWithToken(self, token: str):
        connection = self.connect()
        cursor = connection.cursor()
        token = hashlib.sha256(token.encode()).hexdigest()
        cursor.execute("INSERT INTO userdata (username, password) VALUES (%s, %s)", ("_token_", token))
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

def randomToken(k: int = 16) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=k))

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

def userLogin(client: socket.socket, username: str, password: str) -> bool:
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

def userLoginWithToken(client: socket.socket, token: str) -> bool:
    return userLogin(client, "_token_", token)

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
