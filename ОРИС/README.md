# Чат на сокетах

Формат сообщения: COMMAND (4 байта ASCII) + LENGTH (4 байта, struct.pack("!I")) + DATA (LENGTH байт UTF-8). Максимум payload — 10 МБ.

Команды: JOIN <username> — регистрация; TEXT <message> — рассылка всем остальным; LIST — список пользователей; QUIT — выход; ERRO <reason> — ответ сервера на ошибку.

Запуск: python server.py (127.0.0.1:10000), затем python client.py <username> в отдельных терминалах.