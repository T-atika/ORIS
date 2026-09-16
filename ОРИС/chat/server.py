import socket
import threading

from protocol import send_message, recv_message, CMD_JOIN, CMD_LIST, CMD_QUIT, CMD_TEXT, CMD_ERROR

HOST = '127.0.0.1'
PORT = 10000

clients = {}
clients_lock = threading.Lock()

def broadcast(sender, message):
    sender_name = clients.get(sender, "???")
    payload = f"[{sender_name}] {message}".encode("utf-8")
    with clients_lock:
        targets = list(clients.keys())

    for conn in targets:
        if conn is sender:
            continue
        try:
            send_message(conn, "TEXT", payload)
        except ConnectionResetError:
            print(f"[!] broadcast: connection reset for {clients.get(conn, '?')}")
        except BrokenPipeError:
            print(f"[!] broadcast: broken pipe for {clients.get(conn, '?')}")
        except OSError as e:
            print(f"[!] broadcast: OS error for {clients.get(conn, '?')}: {e}")



def handle_client(conn, addr):
    username = None
    try:
        msg = recv_message(conn)
        if msg is None:
            return
        command, payload = msg

        if command != "JOIN":
            send_message(conn, "ERRO", b"First command must be JOIN")
            return

        username = payload.decode("utf-8").strip()
        if not username:
            send_message(conn, "ERRO", b"Username cannot be empty")
            return

        with clients_lock:
            clients[conn] = username

        print(f"[+] {username} connected from {addr}")

        while True:
            msg = recv_message(conn)
            if msg is None:
                break

            command, payload = msg
            handle_command(conn, username, command, payload)

    except ConnectionResetError:
        print(f"[!] {addr} connection reset")
    except BrokenPipeError:
        print(f"[!] {addr} broken pipe")
    except OSError as e:
        print(f"[!] {addr} OS error: {e}")
    finally:
        with clients_lock:
            was_registered = conn in clients
            clients.pop(conn, None)

        if was_registered and username:
            print(f"[-] {username} disconnected")
            broadcast_system(f"{username} left the chat")

        conn.close()


def handle_command(conn, username, command, payload):
    if command == "TEXT":
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            send_message(conn, "ERRO", b"TEXT payload must be valid UTF-8")
            return True
        broadcast(conn, text)
        return True

    elif command == "LIST":
        with clients_lock:
            names = list(clients.values())
        listing = "\n".join(names).encode("utf-8") if names else b"(no users)"
        send_message(conn, "TEXT", listing)
        return True

    elif command == "QUIT":
        send_message(conn, "TEXT", b"Bye!")
        return False

    else:
        msg = f"Unknown command: {command!r}. Allowed: JOIN, TEXT, LIST, QUIT"
        send_message(conn, "ERRO", msg.encode("utf-8"))
        return True


def broadcast_system(text: str):
    payload = f"[SERVER]: {text}".encode("utf-8")
    with clients_lock:
        targets = list(clients.keys())
    for conn in targets:
        try:
            send_message(conn, "TEXT", payload)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening")

    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            )
            t.start()
    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        server.close()


if __name__ == "__main__":
    main()