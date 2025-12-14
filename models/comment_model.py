from flask import Blueprint, request, jsonify
from models.comment_model import get_comments_by_post, add_comment

comment_bp = Blueprint("comment", __name__, url_prefix="/comment")


# GET KOMENTAR DI POST
@comment_bp.route("/<int:post_id>", methods=["GET"])
def get_comments_route(post_id):
    return jsonify(get_comments_by_post(post_id))


# ADD KOMENTAR
@comment_bp.route("/add", methods=["POST"])
def add_comment_route():
    data = request.json

    add_comment(
        data["post_id"],
        data["user_id"],
        data["text"]
    )

    return jsonify({"message": "Komentar berhasil ditambahkan"})
