"""Profile and astro settings endpoints."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.models.profile import ProfileCreate, ProfileUpdate
from app.models.settings import AstroSettingsCreate, AstroSettingsUpdate
from app.services.profiles import (
    create_profile,
    create_settings,
    get_profile as fetch_profile,
    get_settings,
    update_profile,
    update_settings,
)

router = APIRouter(prefix="/api", tags=["profiles"])
logger = logging.getLogger(__name__)


@router.get("/profile/{user_id}")
def get_profile(user_id: str):
    record = fetch_profile(user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"status": "ok", "data": record}


@router.post("/profile", status_code=201)
def create_profile_route(payload: ProfileCreate):
    try:
        created = create_profile(payload.dict())
        return {"status": "ok", "data": created}
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to create profile: %s", exc)
        raise HTTPException(status_code=500, detail="Unable to create profile") from exc


@router.patch("/profile/{user_id}")
def update_profile_route(user_id: str, payload: ProfileUpdate):
    updates = payload.dict(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    try:
        updated = update_profile(user_id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail="Profile not found")
        return {"status": "ok", "data": updated}
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to update profile: %s", exc)
        raise HTTPException(status_code=500, detail="Unable to update profile") from exc


@router.get("/settings/{user_id}")
def get_astro_settings_route(user_id: str):
    record = get_settings(user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Astro settings not found")
    return {"status": "ok", "data": record}


@router.post("/settings", status_code=201)
def create_astro_settings_route(payload: AstroSettingsCreate):
    try:
        created = create_settings(payload.dict())
        return {"status": "ok", "data": created}
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to create astro settings: %s", exc)
        raise HTTPException(status_code=500, detail="Unable to create astro settings") from exc


@router.patch("/settings/{user_id}")
def update_astro_settings_route(user_id: str, payload: AstroSettingsUpdate):
    updates = payload.dict(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    try:
        updated = update_settings(user_id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail="Astro settings not found")
        return {"status": "ok", "data": updated}
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to update astro settings: %s", exc)
        raise HTTPException(status_code=500, detail="Unable to update astro settings") from exc
