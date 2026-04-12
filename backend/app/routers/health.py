"""Health check routes."""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.services.performance.cache_store import get_cache_health_status
from app.services.supabase import supabase

router = APIRouter(prefix="/api", tags=["health"])


def _supabase_healthcheck() -> tuple[bool, str]:
    try:
        supabase.table("profiles").select("*").limit(1).execute()
        return True, "Supabase connection healthy."
    except Exception as exc:  # pragma: no cover - network specific
        return False, str(exc)


def _cache_healthcheck() -> tuple[bool, dict[str, object]]:
    cache_status = get_cache_health_status()
    return bool(cache_status.get("readiness_ok")), cache_status


@router.get("/health")
def health_check():
    supabase_ok, supabase_msg = _supabase_healthcheck()
    cache_ok, cache_status = _cache_healthcheck()
    return {
        "status": "ok" if supabase_ok and cache_ok else "degraded",
        "supabase": supabase_ok,
        "supabase_message": supabase_msg,
        "cache": cache_status,
    }


@router.get("/readiness")
def readiness_check():
    supabase_ok, supabase_msg = _supabase_healthcheck()
    cache_ok, cache_status = _cache_healthcheck()
    ready = supabase_ok and cache_ok
    payload = {
        "status": "ok" if ready else "degraded",
        "supabase": supabase_ok,
        "supabase_message": supabase_msg,
        "cache": cache_status,
    }
    return JSONResponse(status_code=200 if ready else 503, content=payload)
