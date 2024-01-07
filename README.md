# socket-kit

`socket-kit` is a utility with concise and more fluent code in socket programming. It handles the job of creating server/client, database operations, transferring data and file over network, as well as OpenCV support.

## Socket

```python
from socket_kit import socket

server = socket.createServer("192.168.31.138", 9990, clientNum=3)
server = socket.createdLocalIPServer(9990, clientNum=3)

client = socket.createClient("192.168.31.138", 9990)
```

### Pack and Send Message

```python
from socket_kit import socket

message = socket.packData("Hello".encode())
message = socket.packFile("movieFile.mp4")
message = socket.packFrame(frame, format=".jpg", quality=95)

client.sendall(message)
```

### Receive Message

```python
data, remainedMessage = receiveData(client, message=b"", bufferSize=4096)
frame, remainedMessage = receiveFrame(client, message=b"", bufferSize=4096)
# use original file name if left "saveFile" blank
filePath, remainedMessage = receiveFile(client, "path/save/folder", saveFile="", message: bytes = b"", bufferSize: int = 4096)
```

## Database

### Database Side

```python
from socket_kit import database

database = socket_kit.MySQLDatabase("database_name", host="localhost" username="root", password="password")

database.createTable("table_name", """
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
""")

database.createUserTabel()
database.createUser("username", "password")
# create user with token is actually normal create user
# username = "_token_"
token = socket_kit.randomToken()
database.createUserWithToken(token)
```

### Server Side

```python
from socket_kit import database

if socket_kit.userAuthenticate(client, database):
    print("Connected with", address)
else: continue
```

### Client Side

```python
from socket_kit import database

socket_kit.userLogin(client, "username", "password")
socket_kit.userLoginWithToken(client, "token")
# login in CLI
socket_kit.userLoginCLI(client)
```

### Stream Receiver

```python
message = b""
while True:
    # receive stream pure data
    data, message = socket_kit.receiveStreamData(message, client)
    # receive stream frame (OpenCV)
    frame, message = socket_kit.receiveStreamFrame(message, client)
```

## Vision (OpenCV)

```python
from socket_kit import vision

capture = vision.createCapture()

# default .mp4 with Codec H264
writer = vision.createWriter(capture, "saveMovie.mp4")
vision.saveFrameToMovie(frame, writer)

vision.saveFrameToPhoto(frame, "saveMovie.png")

shown = vision.showFrame("frame", frame)
if not shown: break
```

