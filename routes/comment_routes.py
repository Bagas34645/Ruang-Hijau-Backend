from flask import Blueprint, request, jsonify
from db import get_db

comment_bp = Blueprint("comment", __name__, url_prefix="/comment")

@comment_bp.route("/<int:post_id>", methods=["GET"])
def get_comments(post_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM comments WHERE post_id=%s", (post_id,))
    comments = cursor.fetchall()
    return jsonify(comments)

@comment_bp.route("/add", methods=["POST"])
def add_comment():
    data = request.json
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO comments (post_id, user_id, text)
        VALUES (%s, %s, %s)
    """, (data["post_id"], data["user_id"], data["text"]))

    db.commit()
    return jsonify({"message": "Komentar ditambahkan"})
