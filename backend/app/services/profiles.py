"""Profile persistence helpers."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Mapping

from app.services.supabase import supabase


def serialise_profile(document: Mapping[str, Any]) -> Dict[str, Any]:
    """Ensure Supabase payloads use ISO strings for datetimes."""
    result = dict(document)
    for key in ("created_at", "updated_at"):
        value = result.get(key)
        if isinstance(value, datetime):
            result[key] = value.isoformat()
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


def fetch_profile_by_email(email: str) -> Dict[str, Any] | None:
    response = supabase.table("profiles").select("*").eq("email", email).limit(1).execute()
    data = response.data or []
    return data[0] if data else None


def upsert_profile_record(profile_payload: Mapping[str, Any]) -> Dict[str, Any]:
    response = (
        supabase.table("profiles")
        .upsert(profile_payload, on_conflict="email")
        .execute()
    )
    data = response.data or []
    if data:
        return data[0]
    return dict(profile_payload)


def save_birth_data(user_id: str, birth_date: str, birth_time: str, timezone: str, place: str, lat: float, lon: float):
    response = supabase.table("birth_data").insert(
        {
            "user_id": user_id,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "timezone": timezone,
            "place": place,
            "latitude": lat,
            "longitude": lon,
        }
    ).execute()
    return response.data
