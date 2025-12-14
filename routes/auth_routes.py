from flask import Blueprint, request, jsonify
from db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
    """, (data["name"], data["email"], data["password"]))

    db.commit()
    return jsonify({"message": "Register berhasil"}), 201


# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM users WHERE email=%s AND password=%s
    """, (data["email"], data["password"]))

    user = cursor.fetchone()

    if user:
        return jsonify({"message": "Login berhasil", "user": user})
    else:
        return jsonify({"message": "Email atau password salah"}), 401
