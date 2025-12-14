from flask import Blueprint, request, jsonify
from models.user_model import create_user, get_user_by_email

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    create_user(
        data["name"],
        data["email"],
        data["password"]
    )

    return jsonify({"message": "Register berhasil"}), 201


# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = get_user_by_email(data["email"])

    if user and user["password"] == data["password"]:
        return jsonify({"message": "Login berhasil", "user": user})

    return jsonify({"message": "Email atau password salah"}), 401
