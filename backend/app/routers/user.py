"""User routes placeholder."""
from __future__ import annotations

from flask import Blueprint, jsonify

user_bp = Blueprint("user", __name__, url_prefix="/api/users")


@user_bp.route("", methods=["GET"])
def list_users():
    return jsonify({"users": []})
