from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "super_secret_key_for_playlist_maker"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'playlist_maker.db')


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def get_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    return user


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = get_user()
        if user is None:
            return redirect(url_for("login"))
        return view(user, *args, **kwargs)
    return wrapped_view


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        password_confirm = request.form.get("password_confirm", "").strip()

        errors = []

        if not username:
            errors.append("Логин обязателен")
        if not password:
            errors.append("Пароль обязателен")
        if password != password_confirm:
            errors.append("Пароли не совпадают")

        if errors:
            return render_template(
                "register.html",
                errors=errors,
                username=username,
            )

        db = get_db()
        existing_user = db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()

        if existing_user:
            db.close()
            return render_template(
                "register.html",
                errors=["Пользователь с таким логином уже существует"],
                username=username,
            )

        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        db.commit()
        db.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        errors = []

        if not username or not password:
            errors.append("Логин и пароль обязательны")

        if errors:
            return render_template("login.html", errors=errors, username=username)

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        db.close()

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template(
                "login.html",
                errors=["Неверный логин или пароль"],
                username=username,
            )

        session["user_id"] = user["id"]
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/")
def index():
    db = get_db()
    user_id = session.get("user_id")

    if user_id:
        playlists = db.execute(
            "SELECT * FROM playlists WHERE user_id = ? ORDER BY id",
            (user_id,)
        ).fetchall()
    else:
        playlists = []

    db.close()
    return render_template("index.html", playlists=playlists)


@app.route("/playlists/<int:playlist_id>")
def detail(playlist_id):
    db = get_db()
    playlist = db.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,)).fetchone()

    if not playlist:
        db.close()
        return "Плейлист не найден", 404

    tracks = db.execute('''
            SELECT tracks.title, tracks.artist 
            FROM tracks
            JOIN playlists ON tracks.playlist_id = playlists.id
            WHERE playlists.id = ?
        ''', (playlist_id,)).fetchall()

    db.close()

    return render_template("detail.html", playlist=playlist, tracks=tracks)


@app.route("/playlists/add", methods=["GET", "POST"])
@login_required
def add_playlist(user):
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        genre = request.form.get("genre", "").strip()
        description = request.form.get("description", "").strip()
        track_count_text = request.form.get("track_count", "").strip()
        created_at = request.form.get("created_at", "").strip()

        errors = []

        if not title:
            errors.append("Название плейлиста обязательно")
        if not genre:
            errors.append("Жанр обязателен")
        if not created_at:
            errors.append("Дата создания обязательна")

        track_count = 0

        if errors:
            return render_template(
                "add.html",
                errors=errors,
                title=title,
                genre=genre,
                description=description,
                track_count=track_count_text,
                created_at=created_at,
            )

        db = get_db()
        db.execute('''
            INSERT INTO playlists (title, genre, description, track_count, created_at, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, genre, description, track_count, created_at, user["id"]))
        db.commit()
        db.close()

        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/playlists/<int:playlist_id>/edit", methods=["GET", "POST"])
@login_required
def edit_playlist(user, playlist_id):  # ← user ПЕРВЫЙ
    db = get_db()
    playlist = db.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,)).fetchone()

    if not playlist or playlist["user_id"] != user["id"]:
        db.close()
        return "Доступ запрещен или плейлист не найден", 403

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        genre = request.form.get("genre", "").strip()
        description = request.form.get("description", "").strip()
        created_at = request.form.get("created_at", "").strip()

        errors = []

        if not title:
            errors.append("Название плейлиста обязательно")
        if not genre:
            errors.append("Жанр обязателен")
        if not created_at:
            errors.append("Дата создания обязательна")

        if errors:
            db.close()
            return render_template(
                "edit.html",
                playlist=playlist,
                errors=errors,
                title=title,
                genre=genre,
                description=description,
                created_at=created_at,
            )

        db.execute('''
            UPDATE playlists 
            SET title = ?, genre = ?, description = ?, created_at = ?
            WHERE id = ?
        ''', (title, genre, description, created_at, playlist_id))
        db.commit()
        db.close()

        return redirect(url_for("detail", playlist_id=playlist_id))

    db.close()
    return render_template("edit.html", playlist=playlist)


@app.route("/playlists/<int:playlist_id>/delete", methods=["POST"])
@login_required
def delete_playlist(user, playlist_id):
    db = get_db()
    playlist = db.execute("SELECT id, user_id FROM playlists WHERE id = ?", (playlist_id,)).fetchone()

    if not playlist or playlist["user_id"] != user["id"]:
        db.close()
        return "Доступ запрещен или плейлист не найден", 403

    db.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
    db.commit()
    db.close()

    return redirect(url_for("index"))


@app.route("/playlists/<int:playlist_id>/add_track", methods=["POST"])
@login_required
def add_track(user, playlist_id):
    db = get_db()

    playlist = db.execute(
        "SELECT id, user_id, track_count FROM playlists WHERE id = ?",
        (playlist_id,)
    ).fetchone()

    if not playlist or playlist["user_id"] != user["id"]:
        db.close()
        return "Доступ запрещен или плейлист не найден", 403

    track_title = request.form.get("track_title", "").strip()
    track_artist = request.form.get("track_artist", "").strip()

    if track_title and track_artist:
        db.execute('''
            INSERT INTO tracks (title, artist, playlist_id) 
            VALUES (?, ?, ?)
        ''', (track_title, track_artist, playlist_id))

        db.execute('''
            UPDATE playlists SET track_count = track_count + 1 WHERE id = ?
        ''', (playlist_id,))

        db.commit()

    db.close()
    return redirect(url_for("detail", playlist_id=playlist_id))


if __name__ == "__main__":
    app.run(debug=True)