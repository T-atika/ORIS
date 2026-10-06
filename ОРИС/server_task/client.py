import socket
import threading
import protocol as proto

HOST = "127.0.0.1"
PORT = 5555


def listen_loop(sock, stop_event):
    while not stop_event.is_set():
        try:
            msg = proto.recv_message(sock)
        except (ConnectionResetError, OSError):
            msg = None
        if msg is None:
            print("\n[!] соединение с сервером потеряно")
            stop_event.set()
            break
        command, payload = msg
        text = payload.decode("utf-8", errors="replace")
        if command == "LIST":
            print(f"\n[TO-DO LIST]\n{text}\n> ", end="")
        elif command == "ERRO":
            print(f"\n[ошибка] {text}\n> ", end="")
        elif command == "OK":
            print(f"\n[OK] {text}\n> ", end="")
        else:
            print(f"\n{text}\n> ", end="")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))
    except (ConnectionRefusedError, OSError) as e:
        print(f"Не удалось подключиться: {e}")
        return

    stop_event = threading.Event()
    threading.Thread(target=listen_loop, args=(sock, stop_event), daemon=True).start()

    print("Команды: /list, /quit, /done <number>, /add <text>, /delt <number>.")
    try:
        while not stop_event.is_set():
            line = input("> ")
            if line == "/quit":
                proto.send_message(sock, "QUIT")
                break
            elif line == "/list":
                proto.send_message(sock, "LIST")
            elif line.startswith("/add"):
                parts = line.split(" ", 1)
                if len(parts) != 2:
                    print("[!]: /add <text>")
                    continue
                new_task = parts[1].strip()
                if not new_task:
                    print("[!]: TEXT IS NULL")
                    continue
                proto.send_message(sock, "ADDT", new_task.encode())
            elif line.startswith("/delt"):
                parts = line.split(" ", 1)
                if len(parts) != 2:
                    print("[!]: /delt <number>")
                    continue
                try:
                    task_number = int(parts[1])
                    proto.send_message(sock, "DELT", str(task_number).encode("utf-8"))
                except ValueError:
                    print("Номер должен быть числом")
            elif line.startswith("/done"):
                parts = line.split(" ", 1)
                if len(parts) != 2:
                    print("[!]: /done <number>")
                    continue
                try:
                    task_number = int(parts[1])
                    proto.send_message(sock, "DONE", str(task_number).encode("utf-8"))
                except ValueError:
                    print("Номер должен быть числом")
            elif line.startswith("/"):
                print("Неизвестная команда. Команды: /list, /quit, /done <number>, /add <text>, /delt <number>.")
            elif line.strip():
                print("Комада должна начинаться с /")
    except (EOFError, KeyboardInterrupt, BrokenPipeError, OSError):
        pass
    finally:
        stop_event.set()
        sock.close()


if __name__ == "__main__":
    main()
