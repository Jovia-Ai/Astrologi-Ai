"""Shared Supabase auth dependencies for API routes."""
from __future__ import annotations

import logging

from fastapi import Header, HTTPException
from pydantic import BaseModel

from app.services.supabase import supabase

logger = logging.getLogger(__name__)


class AuthenticatedSupabaseUser(BaseModel):
    """Authenticated Supabase user context."""

    id: str
    email: str | None = None
    full_name: str | None = None


def get_required_supabase_user(
    authorization: str | None = Header(default=None),
) -> AuthenticatedSupabaseUser:
    """Resolve the current Supabase user from the bearer token."""

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing auth token.")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing auth token.")

    try:
        user_res = supabase.auth.get_user(token)
    except Exception as exc:  # pragma: no cover - external auth validation
        logger.warning("Supabase token validation failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid token.") from exc

    if not user_res or not user_res.user:
        raise HTTPException(status_code=401, detail="Invalid token.")

    user = user_res.user
    metadata = user.user_metadata or {}
    full_name = (
        str(metadata.get("full_name") or "").strip()
        or str(metadata.get("name") or "").strip()
        or (str(user.email or "").split("@", 1)[0] if user.email else None)
    )
    return AuthenticatedSupabaseUser(
        id=user.id,
        email=user.email,
        full_name=full_name,
    )
