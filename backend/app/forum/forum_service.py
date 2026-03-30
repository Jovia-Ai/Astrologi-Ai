"""Forum business logic — reads/writes via Supabase."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.forum.forum_models import (
    ForumPostCreate,
    ForumPostDetailResponse,
    ForumPostListResponse,
    ForumPostResponse,
    ForumReplyCreate,
    ForumReplyResponse,
    VALID_CATEGORIES,
)
from app.services.supabase import supabase

logger = logging.getLogger(__name__)

_POSTS_TABLE = "forum_posts"
_REPLIES_TABLE = "forum_replies"
_LIKES_TABLE = "forum_post_likes"


def _row_to_post(row: Dict[str, Any], current_user_id: Optional[str] = None) -> ForumPostResponse:
    liked = False
    if current_user_id:
        try:
            like_res = (
                supabase.table(_LIKES_TABLE)
                .select("id")
                .eq("post_id", row["id"])
                .eq("user_id", current_user_id)
                .execute()
            )
            liked = bool(like_res.data)
        except Exception:
            pass
    return ForumPostResponse(
        id=row["id"],
        user_id=row["user_id"],
        user_display_name=row.get("user_display_name") or "Anonim",
        user_sun_sign=row.get("user_sun_sign") or "",
        user_rising_sign=row.get("user_rising_sign") or "",
        category=row.get("category") or "genel",
        title=row.get("title") or "",
        body=row.get("body") or "",
        active_transit=row.get("active_transit"),
        like_count=int(row.get("like_count") or 0),
        reply_count=int(row.get("reply_count") or 0),
        created_at=_parse_dt(row.get("created_at")),
        is_liked_by_me=liked,
    )


def _row_to_reply(row: Dict[str, Any]) -> ForumReplyResponse:
    return ForumReplyResponse(
        id=row["id"],
        post_id=row["post_id"],
        user_id=row["user_id"],
        user_display_name=row.get("user_display_name") or "Anonim",
        user_sun_sign=row.get("user_sun_sign") or "",
        body=row.get("body") or "",
        like_count=int(row.get("like_count") or 0),
        created_at=_parse_dt(row.get("created_at")),
    )


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def list_posts(
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user_id: Optional[str] = None,
) -> ForumPostListResponse:
    query = (
        supabase.table(_POSTS_TABLE)
        .select("*")
        .eq("is_deleted", False)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
    )
    if category and category != "all" and category in VALID_CATEGORIES:
        query = query.eq("category", category)

    result = query.execute()
    rows: List[Dict[str, Any]] = result.data or []
    posts = [_row_to_post(r, current_user_id) for r in rows]

    count_query = supabase.table(_POSTS_TABLE).select("id", count="exact").eq("is_deleted", False)
    if category and category != "all" and category in VALID_CATEGORIES:
        count_query = count_query.eq("category", category)
    count_result = count_query.execute()
    total = count_result.count or len(rows)

    return ForumPostListResponse(
        posts=posts,
        total=total,
        has_more=(offset + limit) < total,
    )


def get_post_detail(post_id: str, current_user_id: Optional[str] = None) -> Optional[ForumPostDetailResponse]:
    post_res = supabase.table(_POSTS_TABLE).select("*").eq("id", post_id).eq("is_deleted", False).execute()
    if not post_res.data:
        return None
    post = _row_to_post(post_res.data[0], current_user_id)

    replies_res = (
        supabase.table(_REPLIES_TABLE)
        .select("*")
        .eq("post_id", post_id)
        .order("created_at", desc=False)
        .execute()
    )
    replies = [_row_to_reply(r) for r in (replies_res.data or [])]
    return ForumPostDetailResponse(post=post, replies=replies)


def create_post(
    payload: ForumPostCreate,
    user_id: str,
    user_display_name: str,
    user_sun_sign: str,
    user_rising_sign: str,
) -> ForumPostResponse:
    category = payload.category if payload.category in VALID_CATEGORIES else "genel"
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "user_display_name": user_display_name,
        "user_sun_sign": user_sun_sign,
        "user_rising_sign": user_rising_sign,
        "category": category,
        "title": payload.title.strip(),
        "body": payload.body.strip(),
        "active_transit": payload.active_transit,
        "like_count": 0,
        "reply_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_deleted": False,
    }
    result = supabase.table(_POSTS_TABLE).insert(row).execute()
    return _row_to_post(result.data[0], user_id)


def toggle_like(post_id: str, user_id: str) -> Dict[str, Any]:
    existing = (
        supabase.table(_LIKES_TABLE)
        .select("id")
        .eq("post_id", post_id)
        .eq("user_id", user_id)
        .execute()
    )
    if existing.data:
        supabase.table(_LIKES_TABLE).delete().eq("post_id", post_id).eq("user_id", user_id).execute()
        _decrement_like_count(post_id)
        liked = False
    else:
        supabase.table(_LIKES_TABLE).insert({"id": str(uuid.uuid4()), "post_id": post_id, "user_id": user_id}).execute()
        _increment_like_count(post_id)
        liked = True

    post_res = supabase.table(_POSTS_TABLE).select("like_count").eq("id", post_id).execute()
    like_count = int((post_res.data[0].get("like_count") or 0)) if post_res.data else 0
    return {"liked": liked, "like_count": like_count}


def create_reply(
    post_id: str,
    payload: ForumReplyCreate,
    user_id: str,
    user_display_name: str,
    user_sun_sign: str,
) -> ForumReplyResponse:
    row = {
        "id": str(uuid.uuid4()),
        "post_id": post_id,
        "user_id": user_id,
        "user_display_name": user_display_name,
        "user_sun_sign": user_sun_sign,
        "body": payload.body.strip(),
        "like_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = supabase.table(_REPLIES_TABLE).insert(row).execute()
    _increment_reply_count(post_id)
    return _row_to_reply(result.data[0])


def get_active_transit_label() -> str:
    """Return today's most prominent transit label from existing sky_events data."""
    try:
        from app.sky_events.service import get_sky_now_feed  # type: ignore

        feed = get_sky_now_feed(
            now=datetime.now(timezone.utc),
            tz="Europe/Istanbul",
            limit=1,
        )
        if feed.hero:
            return (
                feed.hero.short_title_tr
                or feed.hero.title_tr
                or "Kolektif transit aktif"
            )
        if feed.items:
            first = feed.items[0]
            return first.short_title_tr or first.title_tr or "Kolektif transit aktif"
    except Exception as exc:
        logger.debug("Could not load active transit: %s", exc)
    return "Gokyuzu hareketli"


def _increment_like_count(post_id: str) -> None:
    try:
        supabase.rpc("increment_forum_like", {"p_post_id": post_id}).execute()
        return
    except Exception:
        pass
    post_res = supabase.table(_POSTS_TABLE).select("like_count").eq("id", post_id).limit(1).execute()
    current = int((post_res.data[0].get("like_count") or 0)) if post_res.data else 0
    supabase.table(_POSTS_TABLE).update({"like_count": current + 1}).eq("id", post_id).execute()


def _decrement_like_count(post_id: str) -> None:
    try:
        supabase.rpc("decrement_forum_like", {"p_post_id": post_id}).execute()
        return
    except Exception:
        pass
    post_res = supabase.table(_POSTS_TABLE).select("like_count").eq("id", post_id).limit(1).execute()
    current = int((post_res.data[0].get("like_count") or 0)) if post_res.data else 0
    supabase.table(_POSTS_TABLE).update({"like_count": max(0, current - 1)}).eq("id", post_id).execute()


def _increment_reply_count(post_id: str) -> None:
    try:
        supabase.rpc("increment_forum_reply", {"p_post_id": post_id}).execute()
        return
    except Exception:
        pass
    post_res = supabase.table(_POSTS_TABLE).select("reply_count").eq("id", post_id).limit(1).execute()
    current = int((post_res.data[0].get("reply_count") or 0)) if post_res.data else 0
    supabase.table(_POSTS_TABLE).update({"reply_count": current + 1}).eq("id", post_id).execute()
