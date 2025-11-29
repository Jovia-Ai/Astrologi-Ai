"""Profile CRUD routes."""
from __future__ import annotations

import logging
from datetime import datetime

from flask import Blueprint, jsonify, request

try:
    from pymongo import ReturnDocument
except ImportError:  # pragma: no cover - optional dependency
    class ReturnDocument:
        AFTER = True

from backend.db import MongoUnavailable
from app.services.profiles import (
    extract_profile_payload,
    get_profile_collection,
    serialise_profile,
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
        collection = get_profile_collection()
        document = collection.find_one({"email": email})
        if not document:
            return jsonify({"error": "Profil bulunamadı."}), 404
        return jsonify(serialise_profile(document))
    except MongoUnavailable as exc:
        logger.warning("Profile lookup skipped - Mongo unavailable: %s", exc)
        return jsonify({"error": str(exc)}), 503
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
        collection = get_profile_collection()
        updated_document = collection.find_one_and_update(
            {"email": profile_payload["email"]},
            {"$set": profile_payload},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        if updated_document is None:
            updated_document = collection.find_one({"email": profile_payload["email"]})
    except MongoUnavailable as exc:
        logger.warning("Profile save skipped - Mongo unavailable: %s", exc)
        return jsonify({"error": str(exc)}), 503
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Profile save failed: %s", exc)
        return jsonify({"error": "Profil kaydedilemedi."}), 500

    return jsonify(serialise_profile(updated_document or profile_payload)), 200
