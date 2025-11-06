import socket, threading, os, datetime
from test.support.threading_helper import catch_threading_exception

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "EXIT"  # also accept "exit"
MAX_CLIENTS = 3

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

# in-memory cache of clients for the current session
# {id: {"name": str, "addr": (ip,port), "connected": str, "finished": str, "status": "connected"/"disconnected"}}
clients_cache = {}
client_count = 0
lock = threading.Lock()

# Server-side file repository
REPO_DIR = os.path.join(os.path.dirname(__file__), "repo")
os.makedirs(REPO_DIR, exist_ok=True)

def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _send(conn: socket.socket, text: str):
    data = text.encode(FORMAT)
    header = str(len(data)).encode(FORMAT)
    header = header + b' ' * (HEADER - len(header))
    conn.sendall(header); conn.sendall(data)

def _send_bytes(conn: socket.socket, payload: bytes):
    header = str(len(payload)).encode(FORMAT)
    header = header + b' ' * (HEADER - len(header))
    conn.sendall(header); conn.sendall(payload)

def _recv_string(conn: socket.socket) -> str:
    header = conn.recv(HEADER)
    if not header:
        return ""
    try:
        length = int(header.decode(FORMAT).strip())
    except ValueError:
        return ""
    data = b''
    while len(data) < length:
        chunk = conn.recv(min(4096, length - len(data)))
        if not chunk:
            break
        data += chunk
    try:
        return data.decode(FORMAT)
    except UnicodeDecodeError:
        return ""

def _list_repo():
    try:
        return sorted([f for f in os.listdir(REPO_DIR) if os.path.isfile(os.path.join(REPO_DIR, f))])
    except FileNotFoundError:
        return []

def _handle_file_request(conn: socket.socket, filename: str):
    path = os.path.join(REPO_DIR, filename)
    if not os.path.isfile(path):
        _send(conn, f"ERROR: file '{filename}' not found")
        return
    size = os.path.getsize(path)
    # tell client a file is coming (keeps your length-prefix protocol)
    _send(conn, f"FILE {filename} {size}")
    with open(path, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            _send_bytes(conn, chunk)

def _cache_snapshot() -> str:
    lines = ["id\tname\taddr\tconnected\tfinished\tstatus"]
    with lock:
        for cid, info in sorted(clients_cache.items()):
            lines.append(
                f"{cid}\t{info.get('name','?')}\t{info['addr'][0]}:{info['addr'][1]}"
                f"\t{info['connected']}\t{info.get('finished','')}\t{info['status']}"
            )
    return "\n".join(lines)

def handle_client(conn: socket.socket, addr, client_id: int):
    try:
        # 1) client sends its name right after connecting
        name = _recv_string(conn) or f"client{client_id:02d}"
        with lock:
            clients_cache[client_id] = {
                "name": name, "addr": addr, "connected": _now(),
                "finished": "", "status": "connected"
            }

        _send(conn, f"Welcome {name}! You are client{client_id:02d}. "
                    f"Commands: list | status | get <file> | <filename> | exit")

        while True:
            msg = _recv_string(conn)
            if not msg:
                break
            cmd = msg.strip()

            # 10) exit (accept both 'exit' and DISCONNECT_MESSAGE)
            if cmd.lower() == "exit" or cmd.upper() == DISCONNECT_MESSAGE:
                _send(conn, "Goodbye ACK")
                break

            # 9) status (server returns cache content)
            if cmd.lower() == "status":
                _send(conn, _cache_snapshot())
                continue

            # 11) list files
            if cmd.lower() == "list":
                files = _list_repo()
                _send(conn, "\n".join(files) if files else "(repo is empty)")
                continue

            # 11) get file (either 'get <file>' or just '<file>')
            parts = cmd.split(maxsplit=1)
            if parts[0].lower() == "get" and len(parts) == 2:
                _handle_file_request(conn, parts[1])
                continue
            if cmd in _list_repo():
                _handle_file_request(conn, cmd)
                continue

            # 8) echo with ACK
            _send(conn, f"{msg} ACK")
    

    finally:
        with lock:
            if client_id in clients_cache:
                clients_cache[client_id]["finished"] = _now()
                clients_cache[client_id]["status"] = "disconnected"
        conn.close()

def start():
    global client_count
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server on {ADDR[0]}:{ADDR[1]} | repo: {REPO_DIR}")

    while True:
        conn, addr = server.accept()

        # 6) cap concurrent clients
        with lock:
            active = sum(1 for v in clients_cache.values() if v.get("status") != "disconnected")
            if active >= MAX_CLIENTS:
                try:
                    _send(conn, "Server busy: max clients reached. Try again later.")
                except Exception:
                    pass
                conn.close()
                continue
            client_count += 1
            cid = client_count

        thread = threading.Thread(target=handle_client, args=(conn, addr, cid), daemon=True)
        thread.start()
        print(f"[ACTIVE CONNECTIONS] ~{threading.active_count() - 1}")

if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start()
