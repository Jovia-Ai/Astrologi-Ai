"""Profile persistence helpers."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping

from app.services.supabase import supabase, supabase_admin

_ARCHETYPE_TABLE = "archetype_profiles"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_mapping(value: Any) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "model_dump"):
        payload = value.model_dump(exclude_none=True)
        if isinstance(payload, Mapping):
            return dict(payload)
    if hasattr(value, "dict"):
        payload = value.dict(exclude_none=True)
        if isinstance(payload, Mapping):
            return dict(payload)
    return {}


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=lambda item: item.isoformat() if isinstance(item, datetime) else str(item),
    )


def serialise_profile(document: Mapping[str, Any]) -> Dict[str, Any]:
    """Ensure Supabase payloads use ISO strings for datetimes."""
    result = dict(document)
    for key in ("created_at", "updated_at", "computed_at"):
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


def save_astro_settings(user_id: str, house_system: str, zodiac_type: str):
    response = (
        supabase.table("astro_settings")
        .upsert(
            {
                "user_id": user_id,
                "house_system": house_system,
                "zodiac_type": zodiac_type,
            },
            on_conflict="user_id",
        )
        .execute()
    )
    return response.data


def get_astro_settings(user_id: str):
    response = (
        supabase.table("astro_settings")
        .select("*")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    return response.data


def get_profile(user_id: str) -> Dict[str, Any] | None:
    try:
        response = (
            supabase.table("profiles")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )
        return response.data
    except Exception:
        return None


def create_profile(data: Mapping[str, Any]) -> Dict[str, Any]:
    response = supabase.table("profiles").insert(dict(data)).execute()
    payload = response.data
    if isinstance(payload, list):
        return payload[0]
    return payload


def update_profile(user_id: str, data: Mapping[str, Any]) -> Dict[str, Any] | None:
    response = (
        supabase.table("profiles")
        .update(dict(data))
        .eq("id", user_id)
        .execute()
    )
    payload = response.data
    if isinstance(payload, list) and payload:
        return payload[0]
    if isinstance(payload, dict) and payload:
        return payload
    return get_profile(user_id)


def get_settings(user_id: str) -> Dict[str, Any] | None:
    try:
        response = (
            supabase.table("astro_settings")
            .select("*")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return response.data
    except Exception:
        return None


def create_settings(data: Mapping[str, Any]) -> Dict[str, Any]:
    response = supabase.table("astro_settings").insert(dict(data)).execute()
    payload = response.data
    if isinstance(payload, list):
        return payload[0]
    return payload


def update_settings(user_id: str, data: Mapping[str, Any]) -> Dict[str, Any] | None:
    response = (
        supabase.table("astro_settings")
        .update(dict(data))
        .eq("user_id", user_id)
        .execute()
    )
    payload = response.data
    if isinstance(payload, list) and payload:
        return payload[0]
    if isinstance(payload, dict) and payload:
        return payload
    return get_settings(user_id)


def build_archetype_birth_hash(*, birth_date: str, birth_time: str, birth_place: str) -> str:
    seed = "|".join(
        [
            str(birth_date or "").strip(),
            str(birth_time or "").strip(),
            str(birth_place or "").strip().lower(),
        ]
    )
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def build_archetype_answers_hash(
    *,
    answers: List[Any] | None = None,
    test_scores: Mapping[str, Any] | None = None,
    context_scores: Mapping[str, Any] | None = None,
) -> str | None:
    normalized_answers = []
    for answer in answers or []:
        payload = _to_mapping(answer)
        if payload:
            normalized_answers.append(payload)
    normalized_scores = dict(test_scores or {})
    normalized_context = dict(context_scores or {})
    if not normalized_answers and not normalized_scores and not normalized_context:
        return None
    stable_payload = {
        "answers": sorted(
            normalized_answers,
            key=lambda item: (
                str(item.get("item_id") or ""),
                str(item.get("archetype_id") or ""),
                str(item.get("value") or ""),
            ),
        ),
        "context_scores": normalized_context,
        "test_scores": normalized_scores,
    }
    return hashlib.sha256(_stable_json(stable_payload).encode("utf-8")).hexdigest()


def get_current_archetype_profile(user_id: str) -> Dict[str, Any] | None:
    try:
        response = (
            supabase_admin.table(_ARCHETYPE_TABLE)
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
    except Exception:
        return None
    payload = response.data or []
    if isinstance(payload, list):
        row = payload[0] if payload else None
    else:
        row = payload
    if not isinstance(row, Mapping):
        return None
    return serialise_profile(row)


def upsert_current_archetype_profile(document: Mapping[str, Any]) -> Dict[str, Any]:
    payload = dict(document)
    now = _utc_now()
    payload["updated_at"] = now
    payload.setdefault("computed_at", now)
    response = (
        supabase_admin.table(_ARCHETYPE_TABLE)
        .upsert(payload, on_conflict="user_id")
        .execute()
    )
    data = response.data or []
    if isinstance(data, list) and data:
        return serialise_profile(data[0])
    if isinstance(data, Mapping) and data:
        return serialise_profile(data)
    return serialise_profile(payload)
