from flask import Blueprint, request, jsonify
from models.post_model import get_all_posts, add_post, delete_post

post_bp = Blueprint("post", __name__, url_prefix="/post")


# GET SEMUA POST
@post_bp.route("/", methods=["GET"])
def get_posts_route():
    return jsonify(get_all_posts())


# ADD POST
@post_bp.route("/add", methods=["POST"])
def add_post_route():
    data = request.json

    add_post(
        data["user_id"],
        data["content"],
        data.get("image")  # bisa kosong
    )

    return jsonify({"message": "Post berhasil dibuat"})


# DELETE POST
@post_bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_post_route(id):
    delete_post(id)
    return jsonify({"message": "Post terhapus"})
