"""Forum API endpoints — /api/forum/"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.forum import forum_service as svc
from app.forum.forum_models import (
    ActiveTransitResponse,
    ForumPostCreate,
    ForumPostDetailResponse,
    ForumPostListResponse,
    ForumPostResponse,
    ForumReplyCreate,
    ForumReplyResponse,
)

router = APIRouter(prefix="/api/forum", tags=["forum"])
logger = logging.getLogger(__name__)


def _get_user(authorization: Optional[str] = Header(default=None)) -> dict:
    """Validate Supabase JWT and return user metadata."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing auth token.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        from app.services.supabase import supabase  # noqa: WPS433
        user_res = supabase.auth.get_user(token)
        if not user_res or not user_res.user:
            raise HTTPException(status_code=401, detail="Invalid token.")
        user = user_res.user
        metadata = user.user_metadata or {}
        profile_res = (
            supabase.table("profiles")
            .select("full_name")
            .eq("id", user.id)
            .limit(1)
            .execute()
        )
        profile_row = (profile_res.data or [{}])[0]
        display_name = (
            profile_row.get("full_name")
            or metadata.get("display_name")
            or metadata.get("full_name")
            or "Anonim"
        )
        return {
            "id": user.id,
            "display_name": display_name,
            "sun_sign": metadata.get("sun_sign") or "",
            "rising_sign": metadata.get("rising_sign") or "",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Token verification failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid token.") from exc


def _get_optional_user(authorization: Optional[str] = Header(default=None)) -> Optional[str]:
    """Return user_id if auth header present and valid, else None."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    try:
        token = authorization.split(" ", 1)[1].strip()
        from app.services.supabase import supabase  # noqa: WPS433
        user_res = supabase.auth.get_user(token)
        if user_res and user_res.user:
            return user_res.user.id
    except Exception:
        pass
    return None


@router.get("/posts", response_model=ForumPostListResponse)
def list_posts(
    category: str = Query(default="all"),
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    current_user_id: Optional[str] = Depends(_get_optional_user),
):
    try:
        return svc.list_posts(
            category=category,
            limit=limit,
            offset=offset,
            current_user_id=current_user_id,
        )
    except Exception as exc:
        logger.exception("Failed to list forum posts")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/posts/{post_id}", response_model=ForumPostDetailResponse)
def get_post(
    post_id: str,
    current_user_id: Optional[str] = Depends(_get_optional_user),
):
    result = svc.get_post_detail(post_id, current_user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Post bulunamadı.")
    return result


@router.post("/posts", response_model=ForumPostResponse, status_code=201)
def create_post(
    payload: ForumPostCreate,
    user: dict = Depends(_get_user),
):
    try:
        return svc.create_post(
            payload=payload,
            user_id=user["id"],
            user_display_name=user["display_name"],
            user_sun_sign=user["sun_sign"],
            user_rising_sign=user["rising_sign"],
        )
    except Exception as exc:
        logger.exception("Failed to create forum post")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/posts/{post_id}/like")
def toggle_like(
    post_id: str,
    user: dict = Depends(_get_user),
):
    try:
        return svc.toggle_like(post_id=post_id, user_id=user["id"])
    except Exception as exc:
        logger.exception("Failed to toggle like")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/posts/{post_id}/replies", response_model=ForumReplyResponse, status_code=201)
def add_reply(
    post_id: str,
    payload: ForumReplyCreate,
    user: dict = Depends(_get_user),
):
    detail = svc.get_post_detail(post_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Post bulunamadı.")
    try:
        return svc.create_reply(
            post_id=post_id,
            payload=payload,
            user_id=user["id"],
            user_display_name=user["display_name"],
            user_sun_sign=user["sun_sign"],
        )
    except Exception as exc:
        logger.exception("Failed to add reply")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/active-transit", response_model=ActiveTransitResponse)
def active_transit():
    label = svc.get_active_transit_label()
    return ActiveTransitResponse(label=label)
