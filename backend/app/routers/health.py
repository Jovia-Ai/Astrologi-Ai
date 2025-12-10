"""Health check routes."""
from __future__ import annotations

from fastapi import APIRouter

from app.services.supabase import supabase

router = APIRouter(prefix="/api", tags=["health"])


def _supabase_healthcheck() -> tuple[bool, str]:
    try:
        supabase.table("profiles").select("*").limit(1).execute()
        return True, "Supabase connection healthy."
    except Exception as exc:  # pragma: no cover - network specific
        return False, str(exc)


@router.get("/health")
def health_check():
    supabase_ok, supabase_msg = _supabase_healthcheck()
    return {
        "status": "ok" if supabase_ok else "degraded",
        "supabase": supabase_ok,
        "supabase_message": supabase_msg,
    }
