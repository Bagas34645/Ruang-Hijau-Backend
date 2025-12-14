from flask import Blueprint, request, jsonify
from models.event_model import (
    get_all_events, add_event, update_event, delete_event
)

event_bp = Blueprint("event", __name__, url_prefix="/event")


# GET SEMUA EVENT
@event_bp.route("/", methods=["GET"])
def get_events():
    return jsonify(get_all_events())


# ADD EVENT
@event_bp.route("/add", methods=["POST"])
def add_event_route():
    data = request.json

    add_event(
        data["title"],
        data["description"],
        data["date"],
        data["location"]
    )

    return jsonify({"message": "Event berhasil ditambahkan"})


# UPDATE EVENT
@event_bp.route("/update/<int:id>", methods=["PUT"])
def update_event_route(id):
    data = request.json

    update_event(
        id,
        data["title"],
        data["description"],
        data["date"],
        data["location"]
    )

    return jsonify({"message": "Event berhasil diperbarui"})


# DELETE EVENT
@event_bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_event_route(id):
    delete_event(id)
    return jsonify({"message": "Event terhapus"})
