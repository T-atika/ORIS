import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'playlist_maker.db')


def init_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            description TEXT,
            track_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            playlist_id INTEGER NOT NULL,
            FOREIGN KEY (playlist_id) REFERENCES playlists(id)
        )
    ''')

    hash1 = generate_password_hash("123")
    hash2 = generate_password_hash("123")

    cursor.execute('''
        INSERT INTO users (username, password_hash) VALUES (?, ?)
    ''', ('alice', hash1))

    cursor.execute('''
        INSERT INTO users (username, password_hash) VALUES (?, ?)
    ''', ('bob', hash2))

    playlists_data = [
        ('Chill Vibes', 'Lo-Fi', 'Спокойная музыка для учёбы', 42, '2024-01-15', 1),
        ('Workout Energy', 'Rock', 'Мощный рок для тренировок', 15, '2024-02-20', 1),
        ('Evening Jazz', 'Jazz', 'Классический джаз для вечера', 28, '2024-03-10', 1)
    ]
    cursor.executemany('''
        INSERT INTO playlists (title, genre, description, track_count, created_at, user_id) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', playlists_data)

    tracks_data = [
        ('Midnight City', 'M83', 1),
        ('Intro', 'The xx', 1),
        ('Thunderstruck', 'AC/DC', 2),
        ('Back in Black', 'AC/DC', 2),
        ('Take Five', 'Dave Brubeck', 3),
        ('So What', 'Miles Davis', 3)
    ]
    cursor.executemany('''
        INSERT INTO tracks (title, artist, playlist_id) 
        VALUES (?, ?, ?)
    ''', tracks_data)

    db.commit()
    db.close()
    print("База данных создана")


if __name__ == '__main__':
    init_db()