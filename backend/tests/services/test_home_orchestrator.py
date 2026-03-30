from __future__ import annotations

import importlib
from datetime import date as date_type, datetime, timedelta, timezone

from app.core.config import settings
from app.services.performance.cache_keys import build_home_deep_key, build_home_fast_key
from app.services.performance.cache_store import InMemoryCacheStore
from app.services.performance.home_orchestrator import HomeOrchestrator, HomeRequestContext

home_orchestrator_module = importlib.import_module("app.services.performance.home_orchestrator")


def _context() -> HomeRequestContext:
    return HomeRequestContext(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        target_date=date_type(2026, 3, 21),
        tz="Europe/Istanbul",
        locale="tr",
        user_id="user-123",
    )


def test_home_fast_uses_cache_on_second_call(monkeypatch) -> None:
    orchestrator = HomeOrchestrator(cache_store=InMemoryCacheStore())
    context = _context()
    calls = {"count": 0}

    def fake_compute_payload(*, mode, context, now, timer):
        calls["count"] += 1
        return {
            "headline": f"{mode} headline",
            "summary": "summary",
            "highlights": [],
            "energy": {},
            "cta": {},
        }

    monkeypatch.setattr(orchestrator, "_compute_payload", fake_compute_payload)
    monkeypatch.setattr(settings, "enable_home_fast_cache", True)
    monkeypatch.setattr(settings, "enable_timing_logs", False)

    anchor = datetime(2026, 3, 21, 9, 0, tzinfo=timezone.utc)
    first = orchestrator.get_fast(context, now=anchor)
    second = orchestrator.get_fast(context, now=anchor + timedelta(minutes=5))

    assert first["cache_status"] == "miss"
    assert second["cache_status"] == "hit"
    assert first["headline"] == second["headline"]
    assert calls["count"] == 1


def test_home_fast_serves_stale_and_schedules_refresh(monkeypatch) -> None:
    orchestrator = HomeOrchestrator(cache_store=InMemoryCacheStore())
    context = _context()
    scheduled: list[str] = []

    monkeypatch.setattr(settings, "enable_home_fast_cache", True)
    monkeypatch.setattr(settings, "enable_stale_while_revalidate", True)
    monkeypatch.setattr(settings, "enable_timing_logs", False)

    config_hash = "testhash"
    cache_key = build_home_fast_key(subject_key=context.subject_key, day=context.target_date, config_hash=config_hash)
    monkeypatch.setattr(home_orchestrator_module, "build_home_cache_config_hash", lambda: config_hash)

    stale_anchor = datetime(2026, 3, 21, 8, 0, tzinfo=timezone.utc)
    orchestrator._cache_store.set(
        cache_key,
        {
            "headline": "stale headline",
            "summary": "stale summary",
            "highlights": [],
            "energy": {},
            "cta": {},
            "generated_at": stale_anchor.isoformat(),
            "payload_version": "v1",
        },
        ttl_seconds=60,
        stale_ttl_seconds=3600,
        now=stale_anchor,
    )

    def fake_schedule_home_refresh(*, name, task, enabled):
        scheduled.append(name)
        return True

    def fail_compute_payload(*args, **kwargs):
        raise AssertionError("stale response should not recompute inline")

    monkeypatch.setattr(home_orchestrator_module, "schedule_home_refresh", fake_schedule_home_refresh)
    monkeypatch.setattr(orchestrator, "_compute_payload", fail_compute_payload)

    response = orchestrator.get_fast(context, now=stale_anchor + timedelta(minutes=2))

    assert response["cache_status"] == "stale"
    assert response["headline"] == "stale headline"
    assert scheduled


def test_home_deep_warms_fast_cache(monkeypatch) -> None:
    orchestrator = HomeOrchestrator(cache_store=InMemoryCacheStore())
    context = _context()
    monkeypatch.setattr(settings, "enable_home_fast_cache", True)
    monkeypatch.setattr(settings, "enable_home_deep_cache", True)
    monkeypatch.setattr(settings, "enable_timing_logs", False)

    config_hash = "warmhash"
    monkeypatch.setattr(home_orchestrator_module, "build_home_cache_config_hash", lambda: config_hash)

    def fake_compute_payload(*, mode, context, now, timer):
        return {
            "preview": {
                "headline": "fast preview",
                "summary": "summary",
                "highlights": [],
                "energy": {},
                "cta": {},
            },
            "sections": [],
            "expanded_cards": [],
            "guidance": [],
            "story_hooks": [],
            "context": {},
        }

    monkeypatch.setattr(orchestrator, "_compute_payload", fake_compute_payload)

    anchor = datetime(2026, 3, 21, 10, 0, tzinfo=timezone.utc)
    response = orchestrator.get_deep(context, now=anchor)

    fast_key = build_home_fast_key(subject_key=context.subject_key, day=context.target_date, config_hash=config_hash)
    fast_lookup = orchestrator._cache_store.get(fast_key, now=anchor + timedelta(minutes=1))
    deep_key = build_home_deep_key(subject_key=context.subject_key, day=context.target_date, config_hash=config_hash)
    deep_lookup = orchestrator._cache_store.get(deep_key, now=anchor + timedelta(minutes=1))

    assert response["cache_status"] == "miss"
    assert fast_lookup.status == "hit"
    assert deep_lookup.status == "hit"
    assert fast_lookup.entry is not None
    assert fast_lookup.entry.value["headline"] == "fast preview"


def test_home_fast_prefers_editorial_core_story_over_upper_meaning() -> None:
    orchestrator = HomeOrchestrator(cache_store=InMemoryCacheStore())

    payload = orchestrator._assemble_fast_payload(
        natal_public={"core_story_ui": {"headline": "Kimlik", "text": "Sessiz ama net bir yön hissi kuruluyor."}},
        transit_payload={
            "public": {
                "period_core": {
                    "title": "Aktif tema",
                    "upper_meaning": "Daha soyut bir üst anlam cümlesi.",
                    "core_story": "Bu dönem mesele hız değil; daha anlaşılır görünmek.",
                },
                "event_cards": [],
            }
        },
        sky_payload={"summary_tr": "Gökyüzünde teknik bir açıklama."},
    )

    assert payload["summary"] == "Bu dönem mesele hız değil; daha anlaşılır görünmek."


def test_home_editorializes_collective_aspect_summary() -> None:
    orchestrator = HomeOrchestrator(cache_store=InMemoryCacheStore())

    summary = orchestrator._editorialize_sky_summary(
        {
            "short_title_tr": "Güneş-Satürn kavuşumu",
            "summary_tr": "Güneş ile Satürn arasındaki kavuşum, kolektif atmosferde görünürlük ile yapı kurma başlıklarını aynı anda hareketlendirebilir.",
            "badge_tr": "Aktif",
        }
    )

    assert summary == "güneş-satürn kavuşumu şu sıralar kolektif ritimde daha görünür çalışıyor."
