"""Health check routes."""
from __future__ import annotations

from flask import Blueprint, jsonify

from backend.db import mongo_healthcheck

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.route("/health", methods=["GET"])
def health_check():
    mongo_ok, mongo_msg = mongo_healthcheck()
    return jsonify(
        {
            "status": "ok",
            "mongo": mongo_ok,
            "mongo_message": mongo_msg,
        }
    )
