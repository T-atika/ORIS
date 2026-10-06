import socket
import threading
import protocol as proto

HOST = "0.0.0.0"
PORT = 5555

tasks = []
tasks_lock = threading.Lock()

def handle_client(sock, addr):
    try:
        while True:
            msg = proto.recv_message(sock)
            if msg is None:
                break

            command, payload = msg
            if command == "ADDT":
                text = payload.decode("utf-8", errors="replace").strip()
                if not text:
                    proto.send_message(sock, "ERRO", "задача не может быть пустой".encode("utf-8"))
                    continue
                with tasks_lock:
                    tasks.append({"text": text, "done": False})
                proto.send_message(sock, "OK", "Задача добавлена".encode("utf-8"))
            elif command == "LIST":
                with tasks_lock:
                    lines = []
                    for i, task in enumerate(tasks, start=1):
                        done = "[ ]"
                        if task["done"]:
                            done = "[x]"
                        lines.append(f"{i}. {done} {task['text']}")
                    res = "\n".join(lines) if lines else "Список пока пуст"
                proto.send_message(sock, "LIST", res.encode("utf-8"))
            elif command == "QUIT":
                proto.send_message(sock, "OK", b"* bye")
                break
            elif command == "DELT":
                task_number = payload.decode("utf-8", errors="replace")
                try:
                    num = int(task_number)
                except ValueError:
                    proto.send_message(sock, "ERRO", "Номер должен быть числом".encode("utf-8"))
                    continue
                send_error = False
                with tasks_lock:
                    if num < 1 or num > len(tasks):
                        err_msg = f"Задачи с номером {num} не существует"
                        send_error = True
                    else:
                        tasks.pop(num-1)
                        msg = f"задача {task_number} удалена"
                if not send_error:
                    proto.send_message(sock, "OK", msg.encode("utf-8"))
                else:
                    proto.send_message(sock, "ERRO", err_msg.encode("utf-8"))
            elif command == "DONE":
                task_number = payload.decode("utf-8", errors="replace")
                try:
                    num = int(task_number)
                except ValueError:
                    proto.send_message(sock, "ERRO", "Номер должен быть числом".encode("utf-8"))
                    continue
                send_error = False
                with tasks_lock:
                    if num < 1 or num > len(tasks):
                        err_msg = f"Задачи с номером {num} не существует"
                        send_error = True
                    elif not tasks[num-1]["done"]:
                        tasks[num-1]["done"] = True
                        msg = f"задача {task_number} выполнена"
                    else:
                        msg = f"задача {task_number} уже выполнена"
                if not send_error:
                    proto.send_message(sock, "OK", msg.encode("utf-8"))
                else:
                    proto.send_message(sock, "ERRO", err_msg.encode("utf-8"))
            else:
                proto.send_message(sock, "ERRO", f"unknown command {command}".encode("utf-8"))

    except ConnectionResetError:
        print(f"[!] {addr} - соединение сброшено (RST)")
    except BrokenPipeError:
        print(f"[!] {addr} - не удалось отправить, соединение разорвано")
    finally:
        sock.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"[*] сервер слушает {HOST}:{PORT}")
        while True:
            client_sock, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] сервер остановлен")
