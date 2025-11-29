"""Health check routes."""
from __future__ import annotations

from flask import Blueprint, jsonify

from app.services.supabase import supabase

health_bp = Blueprint("health", __name__, url_prefix="/api")


def _supabase_healthcheck() -> tuple[bool, str]:
    try:
        supabase.table("profiles").select("*").limit(1).execute()
        return True, "Supabase connection healthy."
    except Exception as exc:  # pragma: no cover - network specific
        return False, str(exc)


@health_bp.route("/health", methods=["GET"])
def health_check():
    supabase_ok, supabase_msg = _supabase_healthcheck()
    return jsonify(
        {
            "status": "ok" if supabase_ok else "degraded",
            "supabase": supabase_ok,
            "supabase_message": supabase_msg,
        }
    )
