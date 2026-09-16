import socket
import threading
import sys

from protocol import send_message, recv_message

HOST = "127.0.0.1"
PORT = 10000


def listen_server(sock):
    try:
        while True:
            msg = recv_message(sock)
            if msg is None:
                print("Connection closed")
                break

            command, payload = msg
            text = payload.decode("utf-8", errors="replace")

            if command == "TEXT":
                print(f"\n{text}")
            elif command == "ERRO":
                print(f"[ERROR] {text}")
            else:
                print(f"Unknown command from server: {command}")

    except ConnectionResetError:
        print("Connection reset by server")
    except OSError as e:
        print(f"Connection error: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <username>")
        return

    username = sys.argv[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Server is unavailable")
        return

    try:
        send_message(sock, "JOIN", username.encode("utf-8"))

        listener = threading.Thread(target=listen_server, args=(sock,), daemon=True)
        listener.start()

        while True:
            try:
                line = input()
            except EOFError:
                break

            line = line.strip()
            if not line:
                continue

            if line.upper() == "LIST":
                send_message(sock, "LIST", b"")
            elif line.upper() == "QUIT":
                send_message(sock, "QUIT", b"")
                break
            else:
                send_message(sock, "TEXT", line.encode("utf-8"))

    except BrokenPipeError:
        print("Cannot send: connection is broken")
    except ConnectionResetError:
        print("Connection was reset")
    except OSError as e:
        print(f"OS error: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()