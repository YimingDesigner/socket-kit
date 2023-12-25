# socket-kit

`socket-kit` is a utility with concise and more fluent code in socket programming. It handles the job of creating server/client, database operations, transferring data and file over network, as well as OpenCV support.

## Server and Client

```python
import socket_kit

server = createServer("192.168.31.138", 9990, clientNum=3)
server = createdLocalhostServer(9990, clientNum=3)
server = createdLocalIPServer(9990, clientNum=3)
client = createClient("192.168.31.138", 9990)
```

## Database

### Database Side

```python
import socket_kit

database = socket_kit.MySQLDatabase("database_name", host="localhost" username="root", password="password")

database.createTable("table_name", """
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
""")

database.createUserTabel()
database.createUser("username", "password")
```

### Server Side

```python
import socket_kit

if socket_kit.userAuthenticate(client, database):
    print("Connected with", address)
else: continue
```

### Client Side

```python
import socket_kit

socket_kit.userLogin(client, "username", "password")
# login in CLI
socket_kit.userLoginCLI(client)
```

## Data Transfer

To concentrate on data transfer, the code below will ignore the concept of server/client, because the sender/receiver can appear at both depending on your requirement.

### Sender

```python
import socket_kit

# send pure data
data = b""
message = socket_kit.packData(data)
client.sendall(message)

# send file
message = socket_kit.packFile("movieFile.mp4")
client.sendall(message)

# send frame (OpenCV)
message = socket_cv.packFrame(frame)
client.sendall(message)
```

### Receiver

```python
import socket_kit

# receive pure data
data = socket_kit.receiveData(client)

# receive file
socket_kit.receiveFile("savedFile.mp4", client)

# receive frame (OpenCV)
frame = socket_kit.receiveFrame(client)
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

## OpenCV

```python
import socket_kit

capture = socket_kit.createCapture()

# default .mp4 with Codec H264
writer = socket_kit.createWriter(capture, "saveMovie.mp4")
socket_kit.saveFrameToMovie(frame, writer)

socket_kit.saveFrameToPhoto(frame, "saveMovie.png")

socket_kit.showFrame("frame", frame)
```

