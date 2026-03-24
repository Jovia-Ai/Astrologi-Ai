from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.sky_events.models import SkyEventPersonalizationRequest
from app.sky_events.service import (
    get_sky_archive,
    get_sky_event_detail,
    get_sky_feed,
    get_sky_now_feed,
    personalize_sky_event,
)
from app.transit.astro_event_v2 import personalize_global_event

router = APIRouter(tags=["sky"])


def _parse_at(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "validation_error",
                "message": "at must be a valid ISO datetime.",
            },
        ) from exc


def _parse_types(value: Optional[str]) -> list[str] | None:
    if not value:
        return None
    parts = [part.strip() for part in value.split(",") if part.strip()]
    return parts or None


def _sky_event_bridge_seed(event: object) -> dict:
    bodies = list(getattr(event, "bodies", []) or [])
    return {
        "event_id": getattr(event, "id", ""),
        "event_family": "global_sky_event",
        "event_subtype": getattr(event, "event_type", ""),
        "source_bodies": bodies,
        "target_points": [],
        "target_houses": [],
        "start_at": getattr(event, "starts_at", ""),
        "exact_at": [getattr(event, "exact_at", "")] if getattr(event, "exact_at", "") else [],
        "end_at": getattr(event, "ends_at", ""),
        "collective_interest_score": float(getattr(event, "cultural_interest_score", 0.0) or 0.0) / 100.0,
    }


@router.get("/sky/now")
def sky_now(
    tz: str = Query("Europe/Istanbul"),
    limit: int = Query(4, ge=1, le=12),
    types: str | None = Query(None, description="comma-separated event types"),
    at: str | None = Query(None, description="ISO datetime for deterministic previews"),
    debug: int = Query(0),
) -> dict:
    payload = get_sky_now_feed(
        now=_parse_at(at),
        tz=tz,
        limit=limit,
        event_types=_parse_types(types),
        debug=bool(debug),
    )
    return payload.model_dump()


@router.get("/sky/feed")
def sky_feed(
    tz: str = Query("Europe/Istanbul"),
    limit: int = Query(8, ge=1, le=24),
    window: str = Query("now", description="now | week"),
    types: str | None = Query(None, description="comma-separated event types"),
    at: str | None = Query(None, description="ISO datetime for deterministic previews"),
    debug: int = Query(0),
) -> dict:
    payload = get_sky_feed(
        now=_parse_at(at),
        tz=tz,
        limit=limit,
        event_types=_parse_types(types),
        window=window,
        debug=bool(debug),
    )
    return payload.model_dump()


@router.get("/sky/events/{id_or_slug}")
def sky_event_detail(
    id_or_slug: str,
    tz: str = Query("Europe/Istanbul"),
    at: str | None = Query(None, description="ISO datetime for deterministic previews"),
    debug: int = Query(0),
) -> dict:
    try:
        payload = get_sky_event_detail(
            id_or_slug=id_or_slug,
            now=_parse_at(at),
            tz=tz,
            debug=bool(debug),
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail={"error": "sky_event_not_found", "message": str(exc)}) from exc
    return payload.model_dump()


@router.post("/sky/events/{id_or_slug}/personalize")
def sky_event_personalize(
    id_or_slug: str,
    request: SkyEventPersonalizationRequest,
    tz: str = Query("Europe/Istanbul"),
    at: str | None = Query(None, description="ISO datetime for deterministic previews"),
) -> dict:
    anchor = _parse_at(at)
    try:
        payload = personalize_sky_event(
            id_or_slug=id_or_slug,
            request=request,
            now=anchor,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail={"error": "sky_event_not_found", "message": str(exc)}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"error": "validation_error", "message": str(exc)}) from exc
    out = payload.model_dump()
    try:
        detail = get_sky_event_detail(
            id_or_slug=id_or_slug,
            now=anchor,
            tz=tz,
            debug=False,
        )
        out["astro_event_v2"] = personalize_global_event(
            global_event=_sky_event_bridge_seed(detail.event),
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            birth_place=request.birth_place,
            transit_place=request.birth_place,
            transit_date=str(detail.event.exact_at or "")[:10],
        )
    except Exception:
        pass
    return out


@router.get("/sky/archive")
def sky_archive(
    date_from: date = Query(...),
    date_to: date = Query(...),
    tz: str = Query("Europe/Istanbul"),
    limit: int = Query(50, ge=1, le=100),
    types: str | None = Query(None, description="comma-separated event types"),
    debug: int = Query(0),
) -> dict:
    if date_from > date_to:
        raise HTTPException(
            status_code=422,
            detail={"error": "validation_error", "message": "date_from must be earlier than or equal to date_to."},
        )
    payload = get_sky_archive(
        date_from=date_from,
        date_to=date_to,
        tz=tz,
        limit=limit,
        event_types=_parse_types(types),
        debug=bool(debug),
    )
    return payload.model_dump()
