import json
import socket
import struct
import sys
from queue import Queue

from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


HOST = "127.0.0.1"
PORT = 50505


class NetCom:
    def __init__(self, sock):
        self.sock = sock

    @staticmethod
    def _recv_exact(sock, size):
        chunks = []
        received = 0
        while received < size:
            chunk = sock.recv(size - received)
            if not chunk:
                return None
            chunks.append(chunk)
            received += len(chunk)
        return b"".join(chunks)

    def recv(self):
        header = self._recv_exact(self.sock, 4)
        if header is None:
            return None

        payload_size = struct.unpack("!I", header)[0]
        payload = self._recv_exact(self.sock, payload_size)
        if payload is None:
            return None

        return json.loads(payload.decode("utf-8"))

    def send(self, message):
        payload = json.dumps(message, ensure_ascii=False).encode("utf-8")
        header = struct.pack("!I", len(payload))
        self.sock.sendall(header + payload)


class ReceiveThread(QThread):
    message_received = pyqtSignal(dict)
    disconnected = pyqtSignal(str)

    def __init__(self, net):
        super().__init__()
        self.net = net

    def run(self):
        try:
            while True:
                message = self.net.recv()
                if message is None:
                    self.disconnected.emit("Соденение закрыто сервером")
                    break
                self.message_received.emit(message)
        except (ConnectionResetError, OSError, BrokenPipeError) as e:
            self.disconnected.emit(f"Потеря соединения: {e}")


class SendThread(QThread):
    def __init__(self, net):
        super().__init__()
        self.net = net
        self.queue = Queue()

    def send(self, message):
        self.queue.put(message)

    def run(self):
        while True:
            message = self.queue.get()
            if message is None:
                break

            self.net.send(message)

    def stop(self):
        self.queue.put(None)
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self, net):
        super().__init__()
        self.net = net

        self.setWindowTitle("PyQt6 network chat")
        self.resize(560, 420)

        self.history = QTextEdit()
        self.history.setReadOnly(True)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ваше имя")

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message…")

        self.send_button = QPushButton("Send")
        self.clear_button = QPushButton("Clear history")
        self.status_label = QLabel("Статус: Connected")
        self.status_label.setStyleSheet("color: green")

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Name"))
        top_row.addWidget(self.input_name)
        top_row.addStretch()
        top_row.addWidget(self.clear_button)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input)
        input_row.addWidget(self.send_button)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.history)
        layout.addLayout(top_row)
        layout.addLayout(input_row)

        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

        self.send_button.clicked.connect(self.on_send_clicked)
        self.input.returnPressed.connect(self.on_send_clicked)
        self.clear_button.clicked.connect(self.on_clear_his)

        self.receive_thread = ReceiveThread(self.net)
        self.receive_thread.message_received.connect(self.handle_message)
        self.receive_thread.start()
        self.receive_thread.disconnected.connect(self.on_disconnected)

        self.send_thread = SendThread(self.net)
        self.send_thread.start()

        self.handle_message({
            "type": "system",
            "text": "Подключение установлено"
        })
        self.handle_message({
            "type": "system",
            "text": "Добро пожаловать в чат!"
        })

    def on_disconnected(self, reason: str):
        self.status_label.setText("Статус: Disconnected")
        self.status_label.setStyleSheet("color: red")
        self.input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.history.append(f"Система: {reason}")

    def on_send_clicked(self):
        text = self.input.text().strip()
        if not text:
            return
        username = self.input_name.text().strip()
        if not username:
            username = "User"

        self.send_thread.send({
            "type": "chat",
            "username": username,
            "text": text,
        })

        self.input.clear()

    def handle_message(self, message):
        if message.get("type") == "chat":
            username = message.get("username")
            text = message.get("text", "")
            self.history.append(f"{username}: {text}")
        elif message.get("type") == "system":
            text = message.get("text", "")
            self.history.append(f"System: {text}")
        else:
            print("Неизвестный тип сообщения")

    def on_clear_his(self):
        self.history.clear()

    def closeEvent(self, event):
        self.send_thread.stop()

        try:
            self.net.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        self.receive_thread.quit()
        self.receive_thread.wait()
        try:
            self.net.sock.close()
        except OSError:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except OSError as exc:
        print(f"Could not connect to server at {HOST}:{PORT}: {exc}")
        print("Run server.py first, then start main.py.")
        return

    net = NetCom(sock)
    window = MainWindow(net)
    window.show()

    exit_code = app.exec()

    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    sock.close()
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
