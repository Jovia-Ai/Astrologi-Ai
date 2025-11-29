"""Profile persistence helpers."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Mapping

from backend.db import MongoUnavailable, ensure_mongo_connection

from app.core.config import settings


def get_profile_collection():
    if not settings.mongo_uri:
        raise MongoUnavailable("MongoDB yapılandırılmadı.")
    client = ensure_mongo_connection(retries=3, delay=1.0, revalidate=False)
    return client[settings.mongo_db_name][settings.profile_collection]


def serialise_profile(document: Mapping[str, Any]) -> Dict[str, Any]:
    result = dict(document)
    identifier = result.pop("_id", None)
    if identifier is not None:
        result["id"] = str(identifier)
    created_at = result.get("created_at")
    if isinstance(created_at, datetime):
        result["created_at"] = created_at.isoformat()
    updated_at = result.get("updated_at")
    if isinstance(updated_at, datetime):
        result["updated_at"] = updated_at.isoformat()
    return result


def extract_profile_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    first_name = str(payload.get("firstName") or "").strip()
    last_name = str(payload.get("lastName") or "").strip()
    email = str(payload.get("email") or "").strip().lower()

    profile_payload: Dict[str, Any] = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "date": payload.get("date"),
        "time": payload.get("time"),
        "city": payload.get("city"),
        "chart": payload.get("chart"),
        "updated_at": datetime.utcnow(),
    }
    return profile_payload


def validate_profile_payload(profile_payload: Mapping[str, Any]) -> List[str]:
    errors = []
    if not profile_payload.get("firstName"):
        errors.append("firstName gereklidir.")
    if not profile_payload.get("lastName"):
        errors.append("lastName gereklidir.")
    email = profile_payload.get("email")
    if not email:
        errors.append("email gereklidir.")
    elif "@" not in str(email):
        errors.append("Geçerli bir email giriniz.")
    for key in ("date", "time", "city"):
        if not profile_payload.get(key):
            errors.append(f"{key} alanı gereklidir.")
    return errors
