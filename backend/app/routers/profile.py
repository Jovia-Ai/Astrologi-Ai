"""Profile CRUD routes."""
from __future__ import annotations

import logging
from datetime import datetime

from flask import Blueprint, jsonify, request

from app.services.profiles import (
    extract_profile_payload,
    fetch_profile_by_email,
    serialise_profile,
    upsert_profile_record,
    validate_profile_payload,
)

profile_bp = Blueprint("profile", __name__, url_prefix="/api")
logger = logging.getLogger(__name__)


@profile_bp.route("/profile", methods=["GET", "OPTIONS"])
def get_profile():
    if request.method == "OPTIONS":
        return "", 204

    email = request.args.get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "email parametresi gereklidir."}), 400

    try:
        document = fetch_profile_by_email(email)
        if not document:
            return jsonify({"error": "Profil bulunamadı."}), 404
        return jsonify(serialise_profile(document))
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Profile lookup failed: %s", exc)
        return jsonify({"error": "Profil alınamadı."}), 500


@profile_bp.route("/profile", methods=["POST", "PUT", "OPTIONS"])
def upsert_profile():
    if request.method == "OPTIONS":
        return "", 204

    payload = request.get_json(force=True) or {}
    profile_payload = extract_profile_payload(payload)
    errors = validate_profile_payload(profile_payload)
    if errors:
        return jsonify({"errors": errors}), 400

    if request.method == "POST":
        profile_payload["created_at"] = datetime.utcnow()

    try:
        updated_document = upsert_profile_record(profile_payload)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Profile save failed: %s", exc)
        return jsonify({"error": "Profil kaydedilemedi."}), 500

    return jsonify(serialise_profile(updated_document or profile_payload)), 200
