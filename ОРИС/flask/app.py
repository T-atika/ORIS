import itertools
import json
import os
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

NOTES_FILE = "notes.json"


def load_notes():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_notes(notes_list):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes_list, f, indent=4, ensure_ascii=False)


notes = load_notes()
max_id = max((n["id"] for n in notes), default=0)
note_ids = itertools.count(max_id + 1)


def find_note(note_id):
    return next((n for n in notes if n["id"] == note_id), None)


@app.get("/")
def index():
    return "<h1>Гостевая книга</h1>"


@app.post("/notes")
def create_note():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="request body must be JSON object"), 400
    if "author" not in data or not isinstance(data["author"], str) or not data["author"].strip():
        return jsonify(error="field 'author' (non-empty string) is required"), 400
    if not isinstance(data.get("text"), str) or not data["text"].strip():
        return jsonify(error="field 'text' (non-empty string) is required"), 400

    note = {
        "id": next(note_ids),
        "author": data["author"].strip(),
        "text": data["text"].strip(),
        "likes": 0
    }
    notes.append(note)
    save_notes(notes)
    return jsonify(note), 201


@app.post("/notes/<int:note_id>/like")
def like_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    note["likes"] = note.get("likes", 0) + 1
    save_notes(notes)
    return jsonify(note), 200


@app.put("/notes/<int:note_id>")
def update_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="request body must be JSON object"), 400
    if "author" not in data or not isinstance(data["author"], str) or not data["author"].strip():
        return jsonify(error="field 'author' (non-empty string) is required"), 400
    if "text" not in data or not isinstance(data["text"], str) or not data["text"].strip():
        return jsonify(error="field 'text' (non-empty string) is required"), 400
    note["author"] = data["author"].strip()
    note["text"] = data["text"].strip()
    save_notes(notes)
    return jsonify(note), 200


@app.get("/notes")
def list_notes():
    author = request.args.get("author")
    sort_by = request.args.get("sort", "id")
    if sort_by not in ["id", "likes"]:
        return jsonify(error="sort must be 'id' or 'likes'"), 400
    order = request.args.get("order", "asc")
    if order not in ["asc", "desc"]:
        return jsonify(error="order must be 'asc' or 'desc'"), 400
    try:
        limit = int(request.args.get("limit", "10"))
        if limit < 1 or limit > 100:
            return jsonify(error="limit must be between 1 and 100"), 400
    except ValueError:
        return jsonify(error="limit must be integer"), 400
    try:
        offset = int(request.args.get("offset", "0"))
        if offset < 0:
            return jsonify(error="offset must be >= 0"), 400
    except ValueError:
        return jsonify(error="offset must be integer"), 400

    result = notes
    if author is not None:
        result = [n for n in notes if n["author"] == author]
    result.sort(key=lambda x: x.get(sort_by, 0), reverse=(order == "desc"))
    result = result[offset:offset + limit]
    return jsonify(result), 200


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    return jsonify(note)


@app.patch("/notes/<int:note_id>")
def patch_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="request body must be JSON object"), 400
    if "text" in data:
        if not isinstance(data["text"], str) or not data["text"].strip():
            return jsonify(error="field 'text' (non-empty string) is required"), 400
        note["text"] = data["text"].strip()
        save_notes(notes)
    return jsonify(note), 200


@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    notes.remove(note)
    save_notes(notes)
    return "", 204


@app.get("/authors")
def get_authors_stats():
    stats = {}
    for n in notes:
        author = n["author"]
        if author not in stats:
            stats[author] = {"author": author, "notes": 0, "likes": 0}
        stats[author]["notes"] += 1
        stats[author]["likes"] += n.get("likes", 0)
    result = list(stats.values())
    result.sort(key=lambda x: x["author"])
    return jsonify(result), 200


@app.delete("/notes")
def delete_notes_by_author():
    global notes
    author = request.args.get("author")
    if not author or not author.strip():
        return jsonify(error="parameter 'author' is required and must be non-empty"), 400
    author = author.strip()
    deleted_count = sum(1 for n in notes if n["author"] == author)
    notes = [n for n in notes if n["author"] != author]
    save_notes(notes)
    return jsonify({"deleted": deleted_count}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify(error="not found"), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(error="method not allowed"), 405


if __name__ == "__main__":
    app.run(debug=True)