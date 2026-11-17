from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

playlists = [
    {
        "id": 1,
        "title": "Chill Vibes",
        "genre": "some genre",
        "description": "Спокойная музыка",
        "track_count": 42
    },
    {
        "id": 2,
        "title": "Workout Energy",
        "genre": "Rock",
        "description": "рок для тренировок",
        "track_count": 15
    },
    {
        "id": 3,
        "title": "Jazz",
        "genre": "Jazz",
        "description": "Классический джаз",
        "track_count": 28
    }
]


@app.route("/")
def index():
    return render_template("index.html", playlists=playlists)


@app.route("/playlists/<int:playlist_id>")
def detail(playlist_id):
    playlist = next((p for p in playlists if p["id"] == playlist_id), None)

    if not playlist:
        return "Плейлист не найден", 404

    return render_template("detail.html", playlist=playlist)


@app.route("/playlists/add", methods=["GET", "POST"])
def add_playlist():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        genre = request.form.get("genre", "").strip()
        description = request.form.get("description", "").strip()
        track_count_text = request.form.get("track_count", "").strip()

        errors = []

        if not title:
            errors.append("Название плейлиста обязательно")
        if not genre:
            errors.append("Жанр обязателен")

        track_count = 0
        try:
            track_count = int(track_count_text)
            if track_count < 1:
                errors.append("Количество треков должно быть больше 0")
        except ValueError:
            errors.append("Количество треков должно быть целым числом")

        if errors:
            return render_template(
                "add.html",
                errors=errors,
                title=title,
                genre=genre,
                description=description,
                track_count=track_count_text
            )

        new_playlist = {
            "id": len(playlists) + 1,
            "title": title,
            "genre": genre,
            "description": description,
            "track_count": track_count
        }
        playlists.append(new_playlist)

        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/playlists/<int:playlist_id>/edit", methods=["GET", "POST"])
def edit_playlist(playlist_id):
    playlist = next((p for p in playlists if p["id"] == playlist_id), None)

    if not playlist:
        return "Плейлист не найден", 404

    if request.method == "GET":
        return render_template("edit.html", playlist=playlist)

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


        track_count = 0
        try:
            track_count = int(track_count_text)
            if track_count < 1:
                errors.append("Количество треков должно быть больше 0")
        except ValueError:
            errors.append("Количество треков должно быть целым числом")

        if errors:
            return render_template(
                "edit.html",
                playlist=playlist,
                errors=errors,
                title=title,
                genre=genre,
                description=description,
                track_count=track_count_text,
                created_at=created_at,
            )

        playlist["title"] = title
        playlist["genre"] = genre
        playlist["description"] = description
        playlist["track_count"] = track_count
        playlist["created_at"] = created_at

        return redirect(url_for("detail", playlist_id=playlist_id))


@app.route("/playlists/<int:playlist_id>/delete", methods=["POST"])
def delete_playlist(playlist_id):
    playlist = next((p for p in playlists if p["id"] == playlist_id), None)

    if not playlist:
        return "Плейлист не найден", 404

    playlists.remove(playlist)

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)