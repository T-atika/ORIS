import socket
import struct

MAX_MESSAGE_SIZE = 10 * 1024 * 1024
COMMAND_SIZE = 4
LEN_SIZE = 4
HEADER_SIZE = 8

CMD_JOIN = b"JOIN"
CMD_TEXT = b"TEXT"
CMD_QUIT = b"QUIT"
CMD_LIST = b"LIST"
CMD_ERROR = b"ERRO"

def recv_exact(sock, size):
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("connection closed before all data was received")
        data.extend(chunk)
    return bytes(data)

def send_message(sock, command: str, payload: bytes):
    cmd_byt = command.encode("ascii")
    if len(cmd_byt) != COMMAND_SIZE:
        raise ValueError(f"command must be {COMMAND_SIZE} bytes")

    if len(payload) > MAX_MESSAGE_SIZE:
        raise ValueError(f"payload so long")

    header = cmd_byt + struct.pack("!I", len(payload))
    sock.sendall(header + payload)


def recv_message(sock):
    header = recv_exact(sock, HEADER_SIZE)
    if not header:
        return None

    message_len = struct.unpack("!I", header[COMMAND_SIZE:])[0]
    command = header[:COMMAND_SIZE].decode("ascii")

    if message_len > MAX_MESSAGE_SIZE:
        raise ValueError(f"message too long")

    payload = recv_exact(sock, message_len) if message_len  > 0 else b""
    return command, payload