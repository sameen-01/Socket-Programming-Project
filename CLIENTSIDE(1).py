import socket, os

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "EXIT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

def _send(sock: socket.socket, text: str):
    data = text.encode(FORMAT)
    header = str(len(data)).encode(FORMAT)
    header = header + b' ' * (HEADER - len(header))
    sock.sendall(header); sock.sendall(data)

def _recv_string(sock: socket.socket) -> str:
    header = sock.recv(HEADER)
    if not header:
        return ""
    try:
        length = int(header.decode(FORMAT).strip())
    except ValueError:
        return ""
    data = b''
    while len(data) < length:
        chunk = sock.recv(min(4096, length - len(data)))
        if not chunk:
            break
        data += chunk
    try:
        return data.decode(FORMAT)
    except UnicodeDecodeError:
        return ""

def _recv_bytes(sock: socket.socket) -> bytes:
    header = sock.recv(HEADER)
    if not header:
        return b""
    try:
        length = int(header.decode(FORMAT).strip())
    except ValueError:
        return b""
    data = b''
    while len(data) < length:
        chunk = sock.recv(min(4096, length - len(data)))
        if not chunk:
            break
        data += chunk
    return data

def _safe_close(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass
    sock.close()

def main():
    name = input("Enter your name: ").strip() or "anonymous"
    downloads = os.path.join(os.path.dirname(__file__), "downloads")
    os.makedirs(downloads, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(ADDR)

    # send name first (point 8 precondition)
    _send(sock, name)

    # read welcome
    try:
        welcome = _recv_string(sock)
    except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, OSError):
        print("Client list full")
        _safe_close(sock)
        return

    # client list full
    if not welcome:
        print("Client list full")
        _safe_close(sock)
        return
    if "server busy" in welcome.lower() or "client list full" in welcome.lower():
        print(welcome)  
        _safe_close(sock)
        return

    # normal path
    print(welcome)

    while True:
        msg = input("Enter message (list | status | get <file> | <filename> | exit): ").strip()
        if not msg:
            continue

        _send(sock, msg)

        reply = _recv_string(sock)
        if not reply:
            print("Connection closed by server.")
            break

        # file transfer
        if reply.startswith("FILE "):
            try:
                _, fname, size_str = reply.split(maxsplit=2)
                size = int(size_str)
            except Exception:
                print("Malformed FILE header from server.")
                continue
            print(f"Receiving '{fname}' ({size} bytes)...")
            saved = 0
            path = os.path.join(downloads, fname)
            with open(path, "wb") as f:
                while saved < size:
                    chunk = _recv_bytes(sock)
                    if not chunk:
                        break
                    f.write(chunk)
                    saved += len(chunk)
            print(f"Saved to {path}")
            continue

        print(reply)

        if msg.lower() == "exit" or msg.upper() == DISCONNECT_MESSAGE:
            break

    sock.close()

if __name__ == "__main__":
    main()
