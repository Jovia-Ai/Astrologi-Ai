from app.api.routes import natal_interpretation
from app.services.performance.cache_store import InMemoryCacheStore


def _request(**overrides):
    payload = {
        "birth_date": "1996-12-28",
        "birth_time": "07:10",
        "birth_place": "Istanbul, TR",
        "locale": "tr",
        "summary_only": True,
    }
    payload.update(overrides)
    return natal_interpretation.NatalInterpretationRequest(**payload)


def test_interpret_ui_cache_key_changes_with_locale() -> None:
    request_tr = _request(locale="tr")
    request_en = _request(locale="en")

    key_tr = natal_interpretation._interpret_ui_cache_key(
        request_tr,
        debug=False,
        include_debug=False,
        include_full_profile=False,
        profile_engine=None,
    )
    key_en = natal_interpretation._interpret_ui_cache_key(
        request_en,
        debug=False,
        include_debug=False,
        include_full_profile=False,
        profile_engine=None,
    )

    assert key_tr != key_en


def test_interpret_ui_cache_key_changes_with_birth_data() -> None:
    request_a = _request(birth_date="1996-12-28")
    request_b = _request(birth_date="1996-12-29")

    key_a = natal_interpretation._interpret_ui_cache_key(
        request_a,
        debug=False,
        include_debug=False,
        include_full_profile=False,
        profile_engine=None,
    )
    key_b = natal_interpretation._interpret_ui_cache_key(
        request_b,
        debug=False,
        include_debug=False,
        include_full_profile=False,
        profile_engine=None,
    )

    assert key_a != key_b


def test_interpret_ui_cache_key_changes_with_full_profile_toggle() -> None:
    request = _request()
    key_lazy = natal_interpretation._interpret_ui_cache_key(
        request,
        debug=False,
        include_debug=False,
        include_full_profile=False,
        profile_engine=None,
    )
    key_full = natal_interpretation._interpret_ui_cache_key(
        request,
        debug=False,
        include_debug=False,
        include_full_profile=True,
        profile_engine=None,
    )
    assert key_lazy != key_full


def test_interpret_ui_repeat_summary_only_request_hits_cache(monkeypatch) -> None:
    monkeypatch.setattr(
        natal_interpretation,
        "default_cache_store",
        InMemoryCacheStore(),
    )
    calls = {"count": 0}

    def fake_build_summary_only_public_payload(request):
        calls["count"] += 1
        return (
            {
                "public": {
                    "locale": request.locale or "tr",
                    "core_story": "Cached summary",
                    "core_story_ui": {
                        "headline": "Cached headline",
                        "text": "Cached summary",
                    },
                    "profile_fast": {"sun_sign": "Capricorn"},
                    "summary_mode": "summary_only",
                }
            },
            {"chart_compute_ms": 10.0, "serialization_ms": 1.0},
        )

    monkeypatch.setattr(
        natal_interpretation,
        "_build_summary_only_public_payload",
        fake_build_summary_only_public_payload,
    )

    request = _request()
    first = natal_interpretation.interpret_natal_chart_ui(request)
    second = natal_interpretation.interpret_natal_chart_ui(request)

    assert calls["count"] == 1
    assert first == second
    assert second["public"]["summary_mode"] == "summary_only"


def test_interpret_ui_cache_failure_bypasses_without_breaking_route(monkeypatch) -> None:
    class FailingCacheStore:
        def get(self, key, *, now=None):
            raise RuntimeError("cache get failed")

        def set(self, key, value, *, ttl_seconds, stale_ttl_seconds=0, now=None):
            raise RuntimeError("cache set failed")

    monkeypatch.setattr(
        natal_interpretation,
        "default_cache_store",
        FailingCacheStore(),
    )

    monkeypatch.setattr(
        natal_interpretation,
        "_build_summary_only_public_payload",
        lambda request: (
            {
                "public": {
                    "locale": request.locale or "tr",
                    "core_story": "Fallback summary",
                    "core_story_ui": {
                        "headline": "Fallback headline",
                        "text": "Fallback summary",
                    },
                    "summary_mode": "summary_only",
                }
            },
            {"chart_compute_ms": 8.0, "serialization_ms": 1.0},
        ),
    )

    response = natal_interpretation.interpret_natal_chart_ui(_request())

    assert response["public"]["core_story_ui"]["headline"] == "Fallback headline"
    assert response["public"]["summary_mode"] == "summary_only"
