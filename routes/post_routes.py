from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from db import get_db

post_bp = Blueprint("post", __name__, url_prefix="/post")


@post_bp.route("/", methods=["GET"])
def get_posts():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM posts ORDER BY created_at DESC")
    posts = cursor.fetchall()
    return jsonify(posts)


def _ensure_uploads_dir():
    uploads = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(uploads, exist_ok=True)
    return uploads


@post_bp.route("/add", methods=["POST"])
def add_post():
    # Support multipart/form-data with optional file 'image'
    db = get_db()
    cursor = db.cursor()

    user_id = request.form.get('user_id') or request.form.get('userId')
    content = request.form.get('content') or request.form.get('text')
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
        INSERT INTO posts (user_id, text, image)
        VALUES (%s, %s, %s)
    """, (user_id, content, image_filename))

    db.commit()
    return jsonify({"message": "Post berhasil ditambahkan"})
