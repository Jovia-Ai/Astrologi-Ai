import json

from app.routers import health


def test_health_check_includes_cache_summary(monkeypatch) -> None:
    monkeypatch.setattr(health, "_supabase_healthcheck", lambda: (True, "Supabase connection healthy."))
    monkeypatch.setattr(
        health,
        "_cache_healthcheck",
        lambda: (
            True,
            {
                "selected_backend": "layered",
                "active_backend": "layered",
                "strict_mode": True,
                "redis_configured": True,
                "redis_ready": True,
                "fallback_active": False,
                "fail_fast_expected": True,
                "readiness_ok": True,
                "status": "ready",
                "reason": None,
            },
        ),
    )

    payload = health.health_check()

    assert payload["status"] == "ok"
    assert payload["supabase"] is True
    assert payload["cache"]["selected_backend"] == "layered"
    assert payload["cache"]["redis_ready"] is True


def test_health_check_degrades_when_cache_is_not_ready(monkeypatch) -> None:
    monkeypatch.setattr(health, "_supabase_healthcheck", lambda: (True, "Supabase connection healthy."))
    monkeypatch.setattr(
        health,
        "_cache_healthcheck",
        lambda: (
            False,
            {
                "selected_backend": "layered",
                "active_backend": "memory",
                "strict_mode": False,
                "redis_configured": False,
                "redis_ready": False,
                "fallback_active": True,
                "fail_fast_expected": False,
                "readiness_ok": False,
                "status": "fallback",
                "reason": "redis_url_missing",
            },
        ),
    )

    payload = health.health_check()

    assert payload["status"] == "degraded"
    assert payload["cache"]["fallback_active"] is True
    assert payload["cache"]["reason"] == "redis_url_missing"


def test_readiness_check_returns_503_when_cache_is_not_ready(monkeypatch) -> None:
    monkeypatch.setattr(health, "_supabase_healthcheck", lambda: (True, "Supabase connection healthy."))
    monkeypatch.setattr(
        health,
        "_cache_healthcheck",
        lambda: (
            False,
            {
                "selected_backend": "redis",
                "active_backend": "memory",
                "strict_mode": False,
                "redis_configured": False,
                "redis_ready": False,
                "fallback_active": True,
                "fail_fast_expected": False,
                "readiness_ok": False,
                "status": "fallback",
                "reason": "redis_url_missing",
            },
        ),
    )

    response = health.readiness_check()
    payload = json.loads(response.body)

    assert response.status_code == 503
    assert payload["status"] == "degraded"
    assert payload["cache"]["selected_backend"] == "redis"
    assert payload["cache"]["fallback_active"] is True
