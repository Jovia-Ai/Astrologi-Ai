from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pytest

from app.api.routes import transits
from app.core.config import settings
from app.transit.narrative.canonical_natal_activation import build_canonical_period_spine
from app.transit.narrative.deep_archetype_engine import build_active_event_cards, build_period_core
from app.transit.narrative.life_chapter_detector import detect_active_life_chapter
from app.transit.present.public_builder import build_public_response


_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "life_chapter"


def _load_fixture(group: str, name: str) -> dict:
    return json.loads((_FIXTURE_ROOT / group / f"{name}.json").read_text(encoding="utf-8"))


def _fixture_report(fixture: dict, *, events: list[dict] | None = None) -> dict:
    return {
        "locale": "tr",
        "metrics": {"pressure_index": 0.61, "support_index": 0.43},
        "natal": fixture["canonical_natal_state"],
        "display": {"items": events or fixture["transit_events"]},
    }


def _fixture_event_cards(events: list[dict]) -> list[dict]:
    return [
        {
            "event_id": str(event.get("event_id") or ""),
            "story_score": 0.95 - idx * 0.05,
            "selection_index": idx,
            "selection_mode": "fixture",
            "chapter_role": {"role": "builder"},
        }
        for idx, event in enumerate(events)
        if str(event.get("event_id") or "").strip()
    ]


def _emit_active_life_chapter(group: str, name: str) -> tuple[dict, dict]:
    fixture = _load_fixture(group, name)
    detected = detect_active_life_chapter(
        canonical_natal_state=fixture["canonical_natal_state"],
        transit_events=fixture["transit_events"],
    )
    chapter = dict(detected["active_life_chapter"] or {})
    assert chapter
    return fixture, chapter


@lru_cache(maxsize=4)
def _route_case(transit_date: str) -> dict:
    request = transits.TransitRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        birth_latitude=41.0082,
        birth_longitude=28.9784,
        birth_timezone="Europe/Istanbul",
        transit_date=transit_date,
        transit_time="12:00",
        transit_place="Istanbul, TR",
        transit_latitude=41.0082,
        transit_longitude=28.9784,
        transit_timezone="Europe/Istanbul",
        locale="tr",
    )
    response = transits._build_transits_engine_response(request)
    response, canonical_natal_state = transits._attach_internal_period_reasoning_state(request, response)
    event_cards = build_active_event_cards(response, max_cards=5)
    canonical_period_spine = (
        build_canonical_period_spine(
            canonical_state=canonical_natal_state,
            period_event_cards=event_cards,
        )
        if canonical_natal_state is not None
        else {}
    )
    period_core = build_period_core(
        response,
        event_cards=event_cards,
        locale="tr",
        canonical_period_spine=canonical_period_spine,
        active_life_chapter=response.get("_active_life_chapter"),
        canonical_natal_state=canonical_natal_state,
        include_adaptive_card_contexts=True,
    )
    public_payload = build_public_response(response, include_debug_artifacts=False)
    return {
        "response": response,
        "canonical_natal_state": canonical_natal_state,
        "event_cards": event_cards,
        "canonical_period_spine": canonical_period_spine,
        "period_core": period_core,
        "public_payload": public_payload,
    }


def _contexts(period_core: dict) -> tuple[dict, dict]:
    bundle = dict(period_core.get("_adaptive_cards_context") or {})
    return (
        dict(bundle.get("period_card_context") or {}),
        dict(bundle.get("natal_context_for_period_cards") or {}),
    )


def test_period_card_context_links_to_semantic_owner() -> None:
    case = _route_case("2026-04-22")
    period_core = case["period_core"]
    period_ctx, _ = _contexts(period_core)

    assert period_ctx["version"] == "period_card_context_v1"
    assert period_ctx["owner_ref"]["semantic_focus_source"] == period_core["semantic_focus"]["source"]
    assert period_ctx["owner_ref"]["selected_meaning"] == period_core["semantic_focus"]["selected_meaning"]
    assert period_ctx["primary_meaning"]["primary_domain"] == period_core["semantic_focus"]["primary_domain"]
    assert period_ctx["source_owner"]["chapter_priority_applied"] is False


def test_period_card_context_evidence_items_reference_featured_events() -> None:
    case = _route_case("2026-04-22")
    period_core = case["period_core"]
    period_ctx, _ = _contexts(period_core)

    featured_ids = {
        str(item.get("event_id") or "").strip()
        for item in (period_core.get("featured_events") or [])
        if isinstance(item, dict)
    }
    evidence_items = period_ctx["evidence_items"]
    assert evidence_items
    assert {item["event_id"] for item in evidence_items} <= featured_ids
    assert all(item["event_id"] for item in evidence_items)
    assert all("selection_mode" in item["debug_refs"] for item in evidence_items)


def test_natal_context_uses_only_canonical_sources() -> None:
    case = _route_case("2026-03-04")
    _, natal_ctx = _contexts(case["period_core"])

    assert natal_ctx["version"] == "natal_context_for_period_cards_v1"
    assert natal_ctx["semantic_owner_ref"]["selected_meaning"] == case["period_core"]["semantic_focus"]["selected_meaning"]
    assert "profile_v8" not in natal_ctx["debug"]["authority_inputs"]
    assert "personality_imprint" not in natal_ctx["debug"]["authority_inputs"]
    assert "meaning_graph.activation_hooks" in natal_ctx["debug"]["authority_inputs"]
    assert "profile_v8" in natal_ctx["debug"]["blocked_authority_inputs"]


def test_no_blocked_sources_as_authority() -> None:
    case = _route_case("2026-04-22")
    period_ctx, natal_ctx = _contexts(case["period_core"])

    assert "period_reading_v1" not in period_ctx["debug"]["authority_inputs"]
    assert "composer_plan" not in period_ctx["debug"]["authority_inputs"]
    assert "period_reading_v1" in period_ctx["debug"]["framing_only_inputs"]
    assert "composer_plan" in period_ctx["debug"]["framing_only_inputs"]
    assert "blocks[]" in period_ctx["debug"]["blocked_authority_inputs"]
    assert "daily_synthesis.body" in period_ctx["debug"]["blocked_authority_inputs"]
    assert "best_times.score_by_intent" in period_ctx["debug"]["blocked_authority_inputs"]
    assert "profile_v8" in natal_ctx["debug"]["blocked_authority_inputs"]
    assert "meaning_graph_v1_1" in natal_ctx["debug"]["blocked_authority_inputs"]


def test_period_reading_v1_is_framing_only_not_reparsed() -> None:
    case = _route_case("2026-04-22")
    period_core = case["period_core"]
    period_ctx, _ = _contexts(period_core)

    assert period_ctx["period_reading_ref"]["full_text"] == period_core["period_reading_v1"]["full_text"]
    assert period_ctx["debug"]["period_reading_reparsed_for_evidence"] is False
    assert period_ctx["debug"]["composer_plan_reparsed_for_evidence"] is False
    assert period_ctx["owner_ref"]["selected_meaning"] != period_ctx["period_reading_ref"]["full_text"]


def test_missing_optional_inputs_do_not_crash() -> None:
    fixture = _load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    minimal_events = fixture["transit_events"][:1]
    period_core = build_period_core(
        _fixture_report(fixture, events=minimal_events),
        event_cards=[{"event_id": str(minimal_events[0].get("event_id") or ""), "selection_index": 0}],
        locale="tr",
        canonical_period_spine={},
        active_life_chapter=None,
        canonical_natal_state=None,
        include_adaptive_card_contexts=True,
    )
    period_ctx, natal_ctx = _contexts(period_core)

    assert period_ctx["manifestation_context"] is None
    assert period_ctx["natal_activation_ref"] is None
    assert natal_ctx["chart_id"] is None
    assert natal_ctx["event_natal_links"]


def test_chapter_priority_context_orbits_chapter_owner(monkeypatch) -> None:
    monkeypatch.setattr(settings, "life_chapter_priority_enabled", True)
    fixture, chapter = _emit_active_life_chapter("saturn_return", "cancer_8th_water_emotional")
    period_core = build_period_core(
        _fixture_report(fixture),
        event_cards=_fixture_event_cards(fixture["transit_events"]),
        locale="tr",
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_focus",
            "spine_lines": ["growth_integration_line"],
            "matched_event_ids": [str(fixture["transit_events"][0]["event_id"])],
            "primary_domain": "emotional_security",
        },
        active_life_chapter=chapter,
        canonical_natal_state=fixture["canonical_natal_state"],
        include_adaptive_card_contexts=True,
    )
    period_ctx, natal_ctx = _contexts(period_core)

    assert period_core["chapter_priority"]["applied"] is True
    assert period_ctx["source_owner"]["chapter_priority_applied"] is True
    assert period_ctx["source_owner"]["chapter_type"] == "saturn_return"
    assert natal_ctx["life_chapter_bridge"]["renderer_handoff"] is not None


def test_non_lifechapter_context_stays_evidence_guided() -> None:
    case = _route_case("2026-04-22")
    period_ctx, natal_ctx = _contexts(case["period_core"])

    assert period_ctx["source_owner"]["chapter_priority_applied"] is False
    assert period_ctx["owner_ref"]["semantic_focus_source"] in {
        "period_voice_policy",
        "canonical_period_spine",
        "selected_event_fallback",
    }
    assert natal_ctx["life_chapter_bridge"]["renderer_handoff"] is None


def test_no_public_payload_leak_without_debug_gate() -> None:
    case = _route_case("2026-04-22")
    public_period_core = dict(case["public_payload"].get("period_core") or {})

    assert "_adaptive_cards_context" not in public_period_core
    assert "period_reading_v1" in public_period_core

    narrative_payload = transits._build_narrative_public_payload(
        transits.TransitNarrativeRequest(
            birth_date="1996-12-28",
            birth_time="07:10",
            birth_place="Istanbul, TR",
            birth_latitude=41.0082,
            birth_longitude=28.9784,
            birth_timezone="Europe/Istanbul",
            start="2026-04-22",
            end="2026-04-22",
            tz="Europe/Istanbul",
            transit_place="Istanbul, TR",
            transit_latitude=41.0082,
            transit_longitude=28.9784,
            transit_timezone="Europe/Istanbul",
            selected_date="2026-04-22",
            include_best_times=False,
            locale="tr",
            debug=False,
        ),
        transits.date_type.fromisoformat("2026-04-22"),
    )
    assert "_adaptive_cards_context" not in dict(narrative_payload.get("period_core") or {})
