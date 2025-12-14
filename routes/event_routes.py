from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from db import get_db

event_bp = Blueprint("event", __name__, url_prefix="/events")


@event_bp.route("", methods=["GET"])
def get_events():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    return jsonify(events)


def _ensure_uploads_dir():
    uploads = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(uploads, exist_ok=True)
    return uploads


@event_bp.route("add", methods=["POST"])
def add_event():
    # Accept multipart/form-data (with optional file 'image')
    db = get_db()
    cursor = db.cursor()

    title = request.form.get('title')
    description = request.form.get('description')
    date = request.form.get('date')
    location = request.form.get('location')
    image_filename = None

    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            uploads = _ensure_uploads_dir()
            filename = secure_filename(file.filename)
            save_path = os.path.join(uploads, filename)
            file.save(save_path)
            image_filename = filename

    cursor.execute("""
        INSERT INTO events (title, description, date, location, image)
        VALUES (%s, %s, %s, %s, %s)
    """, (title, description, date, location, image_filename))

    db.commit()
    return jsonify({"message": "Event berhasil ditambahkan"})


@event_bp.route("/update/<int:id>", methods=["PUT"])
def update_event(id):
    # For simplicity this expects JSON payload for updates
    data = request.json
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE events SET title=%s, description=%s, date=%s, location=%s
        WHERE id=%s
    """, (data["title"], data["description"], data["date"], data["location"], id))

    db.commit()
    return jsonify({"message": "Event berhasil diperbarui"})


@event_bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_event(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM events WHERE id=%s", (id,))
    db.commit()
    return jsonify({"message": "Event terhapus"})
