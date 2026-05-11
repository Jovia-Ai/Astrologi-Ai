from __future__ import annotations

import json
from pathlib import Path

from app.api.routes import transits
from app.transit.narrative.deep_archetype_engine import build_period_core
from app.transit.narrative.life_chapter_detector import detect_active_life_chapter
from app.transit.narrative.period_semantic_focus import resolve_period_semantic_focus


_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "life_chapter"


def _load_fixture(group: str, name: str) -> dict:
    path = _FIXTURE_ROOT / group / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _emit_active_life_chapter(group: str, name: str) -> tuple[dict, dict]:
    fixture = _load_fixture(group, name)
    result = detect_active_life_chapter(
        canonical_natal_state=fixture["canonical_natal_state"],
        transit_events=fixture["transit_events"],
    )
    assert result["active_life_chapter"] is not None
    return fixture, dict(result["active_life_chapter"])


def _minimal_spine(event_id: str, *, primary_domain: str = "communication_learning") -> dict:
    return {
        "source": "canonical_natal_activation_v1",
        "target_node_id": "promise_focus",
        "spine_lines": ["growth_integration_line"],
        "matched_event_ids": [event_id],
        "primary_domain": primary_domain,
    }


def _minimal_policy() -> dict:
    return {
        "version": "period_voice_policy_v1",
        "meaning_intent": "integration_invitation",
        "higher_meaning": "growth_integration_default_meaning",
        "reason_line_seed": "growth_integration_default_reason",
        "valence_mode": "steady",
        "intensity_mode": "dense",
        "manifestation_context": {
            "life_scene": "paylaşılan duygusal alan",
            "primary_house": 8,
            "context_seed": "shared/private territory",
        },
    }


def _fixture_report(fixture: dict) -> dict:
    return {
        "locale": "tr",
        "metrics": {"pressure_index": 0.61, "support_index": 0.43},
        "natal": fixture["canonical_natal_state"],
        "display": {"items": fixture["transit_events"]},
    }


def test_resolver_prefers_life_chapter_semantic_focus_for_aries_3rd() -> None:
    fixture, chapter = _emit_active_life_chapter("saturn_return", "aries_3rd_with_south_node_overlap")
    event_id = fixture["transit_events"][0]["event_id"]

    result = resolve_period_semantic_focus(
        canonical_period_spine=_minimal_spine(event_id),
        active_life_chapter=chapter,
        period_voice_policy=_minimal_policy(),
        manifestation_context=_minimal_policy()["manifestation_context"],
        selected_events=fixture["transit_events"],
        period_core_seed={"featured_events": fixture["transit_events"]},
        canonical_natal_state=fixture["canonical_natal_state"],
        debug=True,
    )

    assert result.source == "life_chapter"
    assert result.selected_meaning == "speech_authority"
    assert result.meaning_family == "speech_authority_maturation"
    assert "generic communication difficulty" in result.suppressed_meanings
    assert "sibling conflict prediction" in result.suppressed_meanings
    assert any("active_life_chapter" in reason for reason in result.why_this_meaning)
    assert result.confidence >= 0.60


def test_resolver_prefers_life_chapter_for_cancer_8th() -> None:
    fixture, chapter = _emit_active_life_chapter("saturn_return", "cancer_8th_water_emotional")
    event_id = fixture["transit_events"][0]["event_id"]

    result = resolve_period_semantic_focus(
        canonical_period_spine=_minimal_spine(event_id, primary_domain="emotional_security"),
        active_life_chapter=chapter,
        period_voice_policy=_minimal_policy(),
        manifestation_context=_minimal_policy()["manifestation_context"],
        selected_events=fixture["transit_events"],
        period_core_seed={"featured_events": fixture["transit_events"]},
        canonical_natal_state=fixture["canonical_natal_state"],
        debug=True,
    )

    assert result.source == "life_chapter"
    assert result.selected_meaning == "shared_emotional_territory"
    assert result.meaning_family == "shared_trust_maturation"
    assert result.primary_domain in {"shared_depth", "trust_transformation"}
    assert "trust_axis_anchor" in (result.scene_translation_request or {})
    assert "shared_vs_private_contrast" in (result.scene_translation_request or {})
    scene_payload = json.dumps(result.scene_translation_request or {}, ensure_ascii=False)
    assert any(token in scene_payload for token in ("mahrem", "ortak", "trust", "shared"))


def test_resolver_prefers_life_chapter_for_nodal_activation_directional_logic() -> None:
    fixture = _load_fixture("nodal", "nn_aries_sn_libra")
    result = detect_active_life_chapter(
        canonical_natal_state=fixture["canonical_natal_state"],
        transit_events=[
            {
                "event_id": "evt_nodal_activation",
                "event_family": "cycle_event",
                "event_subtype": "nodal_opposition",
                "start_at": "2026-05-01",
                "exact_at": ["2026-05-03T00:00:00"],
                "end_at": "2026-05-10",
                "chapter_opening": True,
                "structural_significance": 0.9,
                "precision_signal": 0.86,
                "current_phase": "exact",
                "source_bodies": ["North Node"],
                "target_points": ["North Node"],
                "target_houses": [3],
            }
        ],
    )
    chapter = dict(result["active_life_chapter"] or {})
    assert chapter

    semantic_focus = resolve_period_semantic_focus(
        canonical_period_spine={},
        active_life_chapter=chapter,
        period_voice_policy=_minimal_policy(),
        manifestation_context=_minimal_policy()["manifestation_context"],
        selected_events=[],
        period_core_seed={},
        canonical_natal_state=fixture["canonical_natal_state"],
        debug=True,
    )

    assert semantic_focus.source == "life_chapter"
    assert semantic_focus.selected_meaning == "directional_self_definition"
    assert "generic self/other balance" in semantic_focus.suppressed_meanings
    assert "fated relationship drama" in semantic_focus.suppressed_meanings
    assert "başkalarına göre ayar verme" in str(semantic_focus.debug.get("raw_selected_meaning_text") or "")


def test_resolver_falls_back_to_canonical_period_spine() -> None:
    result = resolve_period_semantic_focus(
        canonical_period_spine=_minimal_spine("evt_spine", primary_domain="identity"),
        active_life_chapter=None,
        period_voice_policy={},
        manifestation_context=None,
        selected_events=[],
        period_core_seed={},
        canonical_natal_state=None,
        debug=True,
    )

    assert result.source == "canonical_period_spine"
    assert result.selected_meaning != "period_focus_unspecified"
    assert any(item.source == "canonical_period_spine" for item in result.evidence)


def test_resolver_falls_back_to_period_voice_policy() -> None:
    result = resolve_period_semantic_focus(
        canonical_period_spine=None,
        active_life_chapter=None,
        period_voice_policy=_minimal_policy(),
        manifestation_context=_minimal_policy()["manifestation_context"],
        selected_events=[],
        period_core_seed={},
        canonical_natal_state=None,
        debug=True,
    )

    assert result.source == "period_voice_policy"
    assert result.meaning_family == "integration_invitation"
    assert result.selected_meaning != "period_focus_unspecified"


def test_resolver_safe_unknown_fallback() -> None:
    result = resolve_period_semantic_focus(
        canonical_period_spine=None,
        active_life_chapter=None,
        period_voice_policy=None,
        manifestation_context=None,
        selected_events=[],
        period_core_seed={},
        canonical_natal_state=None,
        debug=True,
    )

    assert result.source == "unknown"
    assert result.selected_meaning == "period_focus_unspecified"
    assert result.confidence <= 0.40


def test_build_period_core_debug_reflects_life_chapter_semantic_focus() -> None:
    fixture, chapter = _emit_active_life_chapter("saturn_return", "aries_3rd_with_south_node_overlap")
    period_core = build_period_core(
        _fixture_report(fixture),
        event_cards=fixture["transit_events"],
        locale="tr",
        canonical_period_spine=_minimal_spine(fixture["transit_events"][0]["event_id"]),
        active_life_chapter=chapter,
        canonical_natal_state=fixture["canonical_natal_state"],
    )

    assert period_core["semantic_focus"]["source"] == "life_chapter"
    assert period_core["_period_story_debug"]["semantic_focus"]["source"] == "life_chapter"


def test_attach_internal_period_reasoning_state_injects_active_life_chapter(monkeypatch) -> None:
    fixture = _load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    request = transits.TransitRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        transit_date="2026-05-05",
        transit_time="12:00",
        transit_place="Istanbul, TR",
        locale="tr",
    )
    monkeypatch.setattr(
        transits,
        "_try_build_canonical_natal_state_for_transits",
        lambda _request: fixture["canonical_natal_state"],
    )
    response, canonical_state = transits._attach_internal_period_reasoning_state(
        request,
        {
            "display": {"items": fixture["transit_events"]},
            "solar_year_frame": {},
            "event_engine_v2": {},
        },
    )

    assert canonical_state == fixture["canonical_natal_state"]
    assert response["_active_life_chapter"]["chapter_type"] == "saturn_return"


def test_attach_internal_period_reasoning_state_detects_real_chart_saturn_return_on_2026_03_04() -> None:
    request = transits.TransitRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        transit_date="2026-03-04",
        transit_time="12:00",
        transit_place="Istanbul, TR",
        locale="tr",
    )
    core_response = transits._build_transits_engine_response(
        request,
        include_window_report=True,
        include_period_space=True,
        include_multi_event_payload=True,
    )

    response, canonical_state = transits._attach_internal_period_reasoning_state(request, core_response)

    assert canonical_state is not None
    assert response["_active_life_chapter"]["chapter_type"] == "saturn_return"
    assert response["_active_life_chapter"]["chapter_id"].startswith("lc:saturn_return:")


def test_attach_internal_period_reasoning_state_keeps_2026_04_22_outside_saturn_return() -> None:
    request = transits.TransitRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        transit_date="2026-04-22",
        transit_time="12:00",
        transit_place="Istanbul, TR",
        locale="tr",
    )
    core_response = transits._build_transits_engine_response(
        request,
        include_window_report=True,
        include_period_space=True,
        include_multi_event_payload=True,
    )

    response, _ = transits._attach_internal_period_reasoning_state(request, core_response)

    chapter = response.get("_active_life_chapter")
    assert not isinstance(chapter, dict) or chapter.get("chapter_type") != "saturn_return"
