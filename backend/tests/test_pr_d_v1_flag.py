from __future__ import annotations

import json
from pathlib import Path

from app.core.config import settings
from app.transit.narrative.deep_archetype_engine import build_period_core
from app.transit.narrative.life_chapter_detector import detect_active_life_chapter


_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "life_chapter"


def _load_fixture(group: str, name: str) -> dict:
    return json.loads((_FIXTURE_ROOT / group / f"{name}.json").read_text(encoding="utf-8"))


def _minimal_spine(event_id: str, *, primary_domain: str) -> dict:
    return {
        "source": "canonical_natal_activation_v1",
        "target_node_id": "promise_focus",
        "spine_lines": ["growth_integration_line"],
        "matched_event_ids": [event_id],
        "primary_domain": primary_domain,
    }


def _fixture_report(fixture: dict, *, events: list[dict] | None = None) -> dict:
    return {
        "locale": "tr",
        "metrics": {"pressure_index": 0.61, "support_index": 0.43},
        "natal": fixture["canonical_natal_state"],
        "display": {"items": events or fixture["transit_events"]},
    }


def _event_cards(events: list[dict]) -> list[dict]:
    return [
        {
            "event_id": event["event_id"],
            "story_score": 0.95 - idx * 0.05,
            "selection_index": idx,
            "chapter_role": {"role": "builder"},
        }
        for idx, event in enumerate(events)
    ]


def _assert_period_surfaces(period_core: dict) -> None:
    assert period_core["period_reading_v1"]["version"] == "period_reading_v1"
    assert isinstance(period_core["period_reading_v1"]["blocks"], list)
    assert 3 <= len(period_core["period_reading_v1"]["blocks"]) <= 4
    assert "\n\n".join(block["text"] for block in period_core["period_reading_v1"]["blocks"]) == period_core["period_reading_v1"]["full_text"]
    for key in (
        "period_opening",
        "big_picture",
        "mechanism",
        "growth_edge",
        "relational_or_life_expression",
        "what_it_builds",
        "core_story",
        "upper_meaning",
    ):
        assert isinstance(period_core.get(key), str) and str(period_core.get(key)).strip()


def _emit_active_life_chapter(group: str, name: str) -> tuple[dict, dict]:
    fixture = _load_fixture(group, name)
    detected = detect_active_life_chapter(
        canonical_natal_state=fixture["canonical_natal_state"],
        transit_events=fixture["transit_events"],
    )
    chapter = dict(detected["active_life_chapter"] or {})
    assert chapter
    return fixture, chapter


def _build_core_from_fixture(
    *,
    fixture: dict,
    active_life_chapter: dict | None,
    canonical_period_spine: dict,
) -> dict:
    return build_period_core(
        _fixture_report(fixture),
        event_cards=_event_cards(fixture["transit_events"]),
        locale="tr",
        canonical_period_spine=canonical_period_spine,
        active_life_chapter=active_life_chapter,
        canonical_natal_state=fixture["canonical_natal_state"],
    )


def test_life_chapter_priority_flag_defaults_false() -> None:
    assert settings.life_chapter_priority_enabled is False


def test_flag_off_regression_keeps_guided_cases_without_priority(monkeypatch) -> None:
    monkeypatch.setattr(settings, "life_chapter_priority_enabled", False)
    cases = [
        ("saturn_return", "aries_3rd_with_south_node_overlap", "communication_learning"),
        ("saturn_return", "cancer_8th_water_emotional", "emotional_security"),
        ("nodal", "nn_aries_sn_libra", "identity"),
    ]

    for group, name, primary_domain in cases:
        fixture, chapter = _emit_active_life_chapter(group, name)
        period_core = _build_core_from_fixture(
            fixture=fixture,
            active_life_chapter=chapter,
            canonical_period_spine=_minimal_spine(fixture["transit_events"][0]["event_id"], primary_domain=primary_domain),
        )
        _assert_period_surfaces(period_core)
        assert period_core["semantic_focus"]["source"] == "life_chapter"
        assert period_core["chapter_priority"]["enabled"] is False
        assert period_core["chapter_priority"]["applied"] is False
        assert period_core["chapter_priority"]["reason"] == "flag_disabled"


def test_flag_on_applies_chapter_priority_for_aries_saturn_return(monkeypatch) -> None:
    monkeypatch.setattr(settings, "life_chapter_priority_enabled", True)
    fixture, chapter = _emit_active_life_chapter("saturn_return", "aries_3rd_with_south_node_overlap")

    period_core = _build_core_from_fixture(
        fixture=fixture,
        active_life_chapter=chapter,
        canonical_period_spine=_minimal_spine(fixture["transit_events"][0]["event_id"], primary_domain="communication_learning"),
    )

    _assert_period_surfaces(period_core)
    assert period_core["semantic_focus"]["source"] == "life_chapter"
    assert period_core["chapter_priority"]["applied"] is True
    assert period_core["chapter_priority"]["chapter_type"] == "saturn_return"
    assert period_core["chapter_priority"]["event_cards_role"] == "evidence_support"
    assert all(event.get("semantic_role") == "evidence_support" for event in period_core["featured_events"])
    assert all(event.get("semantic_owner") == "life_chapter" for event in period_core["featured_events"])


def test_flag_on_applies_chapter_priority_for_cancer_saturn_return(monkeypatch) -> None:
    monkeypatch.setattr(settings, "life_chapter_priority_enabled", True)
    fixture, chapter = _emit_active_life_chapter("saturn_return", "cancer_8th_water_emotional")

    period_core = _build_core_from_fixture(
        fixture=fixture,
        active_life_chapter=chapter,
        canonical_period_spine=_minimal_spine(fixture["transit_events"][0]["event_id"], primary_domain="emotional_security"),
    )

    _assert_period_surfaces(period_core)
    assert period_core["chapter_priority"]["applied"] is True
    assert period_core["chapter_priority"]["chapter_type"] == "saturn_return"
    assert period_core["chapter_priority"]["event_cards_role"] == "evidence_support"
    assert period_core["semantic_focus"]["selected_meaning"] == "shared_emotional_territory"
    assert period_core["semantic_focus"]["primary_domain"] in {"shared_depth", "trust_transformation"}


def test_flag_on_applies_chapter_priority_for_nodal_activation(monkeypatch) -> None:
    monkeypatch.setattr(settings, "life_chapter_priority_enabled", True)
    fixture = _load_fixture("nodal", "nn_aries_sn_libra")
    events = [
        {
            "event_id": "evt-nodal-activation",
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
    ]
    detected = detect_active_life_chapter(
        canonical_natal_state=fixture["canonical_natal_state"],
        transit_events=events,
    )
    chapter = dict(detected["active_life_chapter"] or {})
    assert chapter

    period_core = build_period_core(
        _fixture_report(fixture, events=events),
        event_cards=_event_cards(events),
        locale="tr",
        canonical_period_spine=_minimal_spine(events[0]["event_id"], primary_domain="identity"),
        active_life_chapter=chapter,
        canonical_natal_state=fixture["canonical_natal_state"],
    )

    _assert_period_surfaces(period_core)
    assert period_core["chapter_priority"]["applied"] is True
    assert period_core["chapter_priority"]["chapter_type"] == "nodal_activation"
    assert "generic self/other balance" not in period_core["period_reading_v1"]["full_text"].lower()


def test_structural_t_square_remains_excluded_even_when_flag_enabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "life_chapter_priority_enabled", True)
    fixture = _load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    active_life_chapter = {
        "chapter_id": "lc:structural:t_square",
        "chapter_type": "structural_natal_chapter",
        "confidence": "high",
        "selected_meaning": "Üç parçalı basınç sistemi",
        "selected_meaning_family": "three_part_pressure_system",
        "semantic_focus": {
            "primary": "three_part_pressure_system",
            "secondary": ["apex_release_point"],
            "not_this": ["generic stress reading"],
        },
        "renderer_handoff": {
            "human_scene": "basıncın en çok yüzeye çıktığı kişisel alan",
            "core_contrast": "alarm okumak ile kurduğu kası görmek",
            "chart_specific_anchor": "üç parçalı basınç sistemi",
            "avoid_readings": ["generic stress reading"],
        },
        "domain_ownership": {
            "primary_domain": "identity_pressure",
            "secondary_domains": ["integration"],
        },
    }

    period_core = _build_core_from_fixture(
        fixture=fixture,
        active_life_chapter=active_life_chapter,
        canonical_period_spine=_minimal_spine(fixture["transit_events"][0]["event_id"], primary_domain="communication_learning"),
    )

    _assert_period_surfaces(period_core)
    assert period_core["semantic_focus"]["source"] == "life_chapter"
    assert period_core["chapter_priority"]["applied"] is False
    assert period_core["chapter_priority"]["reason"] == "excluded_chapter_type"


def test_no_chapter_fallback_stays_valid_when_flag_enabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "life_chapter_priority_enabled", True)
    fixture = _load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")

    period_core = _build_core_from_fixture(
        fixture=fixture,
        active_life_chapter=None,
        canonical_period_spine=_minimal_spine(fixture["transit_events"][0]["event_id"], primary_domain="communication_learning"),
    )

    _assert_period_surfaces(period_core)
    assert period_core["chapter_priority"]["applied"] is False
    assert period_core["chapter_priority"]["reason"] == "no_active_life_chapter"
    assert period_core["semantic_focus"]["source"] in {"canonical_period_spine", "period_voice_policy", "selected_event_fallback"}

