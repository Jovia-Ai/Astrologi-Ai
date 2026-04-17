"""User routes placeholder."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.auth.supabase_auth import (
    AuthenticatedSupabaseUser,
    get_required_supabase_user,
)
from app.services.users import delete_user_account

router = APIRouter(prefix="/api/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.get("")
def list_users():
    return {"users": []}


@router.delete("/me")
def delete_current_user(
    current_user: AuthenticatedSupabaseUser = Depends(get_required_supabase_user),
):
    try:
        result = delete_user_account(current_user.id)
        return {
            "ok": True,
            "user_id": result.user_id,
            "warnings": list(result.warnings),
        }
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - external auth/storage specifics
        logger.exception("Failed to delete account for user %s", current_user.id)
        raise HTTPException(
            status_code=500,
            detail="Unable to delete account.",
        ) from exc
