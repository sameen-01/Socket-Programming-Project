Socket Programming Project
==========================

Project Title:
--------------
Multi-Client Chat and File Transfer System (Python TCP Socket Programming)

Author:
-------
Sameen Dharia  
Wilfrid Laurier University — Computer Science  

Overview:
---------
This project implements a multi-client communication system using Python’s built-in socket library.
It allows multiple clients to connect simultaneously to a central server, send and receive chat messages,
and transfer text data over a TCP connection. The system was developed as part of a networking and systems
programming project to explore client-server architectures, concurrency, and message handling.

Features:
---------
- Multi-client support (multiple clients can connect and communicate concurrently)
- Real-time message broadcasting across all connected users
- Reliable delivery of messages using TCP protocol
- Automatic handling of client connections and disconnections
- Graceful error recovery and socket cleanup
- Simple and intuitive command-line interface for clients
- Lightweight design using only Python standard libraries

System Architecture:
--------------------
The project consists of two main components:

1. **Server (SERVERSIDE.py)**
   - Accepts incoming client connections on a defined port.
   - Spawns a dedicated thread for each connected client.
   - Manages message routing and broadcasting between clients.
   - Handles disconnections and removes inactive clients automatically.

2. **Client (CLIENTSIDE.py)**
   - Connects to the server using a TCP socket.
   - Sends and receives messages in real-time.
   - Displays broadcasted messages from other connected users.
   - Supports manual exit and clean socket closure.

Technical Stack:
----------------
- Language: Python 3
- Libraries: socket, threading, sys, time
- Protocol: TCP (Transmission Control Protocol)

How to Run:
-----------
1. **Start the server first:**
   - Open a terminal in the project folder.
   - Run:
        python SERVERSIDE.py
   - The server will start listening on the configured host (e.g., 127.0.0.1) and port (e.g., 5555).

2. **Launch one or more clients:**
   - Open additional terminal windows.
   - Run:
        python CLIENTSIDE.py
   - When prompted, enter your name or ID to join the session.

3. **Chat or send messages:**
   - Type messages into the client window.
   - All connected users will receive the broadcast messages in real time.

Example Run:
------------
Terminal 1 (Server):
    [SERVER STARTED]
    Connection established with client_01
    Connection established with client_02
    Broadcast: client_01: Hello everyone!

Terminal 2 (Client 1):
    Connected to server at 127.0.0.1:5555
    >> Hello everyone!
    [Message delivered to all clients]

Terminal 3 (Client 2):
    Connected to server
    Received: client_01: Hello everyone!

Error Handling:
---------------
- Detects unexpected client disconnections and closes sockets safely.
- Prevents race conditions by synchronizing access to the client list.
- Displays status messages for successful sends/receives and connection states.

Future Improvements:
--------------------
- Add file transfer capabilities (upload/download).
- Implement user authentication and message encryption.
- Create a GUI client using Tkinter or PyQt for improved usability.
- Add server logging and client IP tracking.
- Introduce private messaging and chatroom channels.

Version:
--------
v1.0 — November 2025

License:
--------
This project is open-source and free for educational use.
