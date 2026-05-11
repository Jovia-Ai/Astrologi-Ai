import json
from pathlib import Path

from app.transit.narrative.astrolog_narrative_engine import (
    PeriodStoryContext,
    build_period_story,
)
from app.transit.narrative.deep_archetype_engine import build_period_core
from app.transit.narrative.life_chapter_detector import detect_active_life_chapter
from app.transit.narrative.period_semantic_focus import resolve_period_semantic_focus


_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "life_chapter"
_ALLOWED_BLOCK_ROLES = {"hook", "unfolding", "growth", "closer"}


def _load_fixture(group: str, name: str) -> dict:
    return json.loads((_FIXTURE_ROOT / group / f"{name}.json").read_text(encoding="utf-8"))


def _event(
    *,
    event_id: str,
    transit_body: str,
    natal_point: str,
    house: int,
    story_score: float = 0.95,
) -> dict:
    return {
        "event_id": event_id,
        "transit_body": transit_body,
        "aspect": "conjunction",
        "natal_point": natal_point,
        "strength": 0.95,
        "orb_deg": 0.2,
        "phase": "exactish",
        "bucket": "long",
        "domains": ["mind", "identity"],
        "houses": {"transit_in_natal_house": house, "natal_point_house": house},
        "chapter_role": {"role": "builder"},
        "story_score": story_score,
        "selection_index": 0,
    }


def _build_life_chapter_period_core(
    *,
    group: str,
    name: str,
    event: dict,
    primary_domain: str,
    spine_lines: list[str],
) -> dict:
    fixture = _load_fixture(group, name)
    detector = detect_active_life_chapter(
        canonical_natal_state=fixture["canonical_natal_state"],
        transit_events=fixture["transit_events"],
    )
    active = detector["active_life_chapter"]
    assert active
    report = {
        "display": {"items": [event]},
        "metrics": {"pressure_index": 0.61, "support_index": 0.48},
        "natal": fixture["canonical_natal_state"],
    }
    event_cards = [
        {
            "event_id": event["event_id"],
            "story_score": event["story_score"],
            "selection_index": event["selection_index"],
            "chapter_role": {"role": "builder"},
        }
    ]
    return build_period_core(
        report,
        event_cards=event_cards,
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_focus",
            "spine_lines": spine_lines,
            "matched_event_ids": [event["event_id"]],
            "primary_domain": primary_domain,
        },
        active_life_chapter=active,
        canonical_natal_state=fixture["canonical_natal_state"],
    )


def _assert_period_reading_contract(period_core: dict) -> None:
    reading = period_core.get("period_reading_v1") if isinstance(period_core.get("period_reading_v1"), dict) else period_core
    assert reading["version"] == "period_reading_v1"
    assert isinstance(reading["blocks"], list)
    assert 3 <= len(reading["blocks"]) <= 4
    assert "\n\n".join(block["text"] for block in reading["blocks"]) == reading["full_text"]
    for block in reading["blocks"]:
        assert block["role"] in _ALLOWED_BLOCK_ROLES
        assert isinstance(block["text"], str) and block["text"].strip()


def test_period_reading_v1_exists_for_guided_tier1_cases() -> None:
    aries = _build_life_chapter_period_core(
        group="saturn_return",
        name="aries_3rd_with_south_node_overlap",
        event=_event(
            event_id="evt-saturn-return-aries-3",
            transit_body="Saturn",
            natal_point="Saturn",
            house=3,
        ),
        primary_domain="communication_learning",
        spine_lines=["growth_integration_line"],
    )
    cancer = _build_life_chapter_period_core(
        group="saturn_return",
        name="cancer_8th_water_emotional",
        event=_event(
            event_id="evt-saturn-return-cancer-8",
            transit_body="Saturn",
            natal_point="Saturn",
            house=8,
        ),
        primary_domain="emotional_security",
        spine_lines=["relational_line"],
    )
    nodal = _build_life_chapter_period_core(
        group="nodal",
        name="nn_aries_sn_libra",
        event=_event(
            event_id="evt-nodal-return-aries",
            transit_body="North Node",
            natal_point="North Node",
            house=3,
        ),
        primary_domain="identity",
        spine_lines=["primary_identity_line"],
    )

    for period_core in (aries, cancer, nodal):
        _assert_period_reading_contract(period_core)

    assert aries["semantic_focus"]["source"] == "life_chapter"
    assert cancer["semantic_focus"]["source"] == "life_chapter"
    assert nodal["semantic_focus"]["source"] == "life_chapter"


def test_period_reading_v1_preserves_semantic_anchors_for_guided_cases() -> None:
    aries = _build_life_chapter_period_core(
        group="saturn_return",
        name="aries_3rd_with_south_node_overlap",
        event=_event(
            event_id="evt-saturn-return-aries-3",
            transit_body="Saturn",
            natal_point="Saturn",
            house=3,
        ),
        primary_domain="communication_learning",
        spine_lines=["growth_integration_line"],
    )
    cancer = _build_life_chapter_period_core(
        group="saturn_return",
        name="cancer_8th_water_emotional",
        event=_event(
            event_id="evt-saturn-return-cancer-8",
            transit_body="Saturn",
            natal_point="Saturn",
            house=8,
        ),
        primary_domain="emotional_security",
        spine_lines=["relational_line"],
    )
    nodal = _build_life_chapter_period_core(
        group="nodal",
        name="nn_aries_sn_libra",
        event=_event(
            event_id="evt-nodal-return-aries",
            transit_body="North Node",
            natal_point="North Node",
            house=3,
        ),
        primary_domain="identity",
        spine_lines=["primary_identity_line"],
    )

    assert any(token in aries["period_reading_v1"]["full_text"].lower() for token in ("söz", "konuş", "cevap", "cümle"))
    assert any(token in cancer["period_reading_v1"]["full_text"].lower() for token in ("paylaş", "ortak", "birlikte", "yük", "güven"))
    assert any(token in nodal["period_reading_v1"]["full_text"].lower() for token in ("yön", "doğrudan", "ayar", "onay"))


def test_period_reading_v1_legacy_fields_remain_populated_from_same_story_build() -> None:
    ctx = PeriodStoryContext(
        period_core={"featured_events": [_event(event_id="evt_plain", transit_body="Saturn", natal_point="Mercury", house=3)]},
        chart_snapshot={},
        natal_promise={},
    )
    first = build_period_story(ctx)
    second = build_period_story(ctx)

    assert first.period_reading_v1 == second.period_reading_v1
    assert first.period_opening == second.period_opening
    assert first.mechanism == second.mechanism
    assert first.growth_edge == second.growth_edge
    assert first.what_it_builds == second.what_it_builds
    _assert_period_reading_contract(first.period_reading_v1)


def test_period_reading_v1_is_universal_even_without_life_chapter() -> None:
    ctx = PeriodStoryContext(
        period_core={"featured_events": [_event(event_id="evt_fallback", transit_body="Mars", natal_point="ASC", house=1)]},
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_identity_direction",
            "spine_lines": ["primary_identity_line"],
            "matched_event_ids": ["evt_fallback"],
        },
    )
    out = build_period_story(ctx)

    _assert_period_reading_contract(out.period_reading_v1)
    assert out.debug["composer_mode"] in {"legacy_fallback", "semantic_focus_guided"}
    assert "Asıl omurga" not in out.period_reading_v1["full_text"]
    assert "Bu en çok" not in out.period_reading_v1["full_text"]


def test_period_reading_v1_avoids_banned_scaffold_phrases_for_guided_cases() -> None:
    fixture = _load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    detector = detect_active_life_chapter(
        canonical_natal_state=fixture["canonical_natal_state"],
        transit_events=fixture["transit_events"],
    )
    active = detector["active_life_chapter"]
    semantic_focus = resolve_period_semantic_focus(
        canonical_period_spine={
            "source": "canonical_natal_activation_v1",
            "target_node_id": "promise_focus",
            "spine_lines": ["growth_integration_line"],
            "matched_event_ids": ["evt-saturn-return-aries-3"],
            "primary_domain": "communication_learning",
        },
        active_life_chapter=active,
        period_voice_policy={},
        manifestation_context=None,
        selected_events=[_event(event_id="evt-saturn-return-aries-3", transit_body="Saturn", natal_point="Saturn", house=3)],
        period_core_seed={"featured_events": [_event(event_id="evt-saturn-return-aries-3", transit_body="Saturn", natal_point="Saturn", house=3)]},
        canonical_natal_state=fixture["canonical_natal_state"],
        debug=True,
    )
    out = build_period_story(
        PeriodStoryContext(
            period_core={"featured_events": [_event(event_id="evt-saturn-return-aries-3", transit_body="Saturn", natal_point="Saturn", house=3)]},
            chart_snapshot=fixture["canonical_natal_state"],
            natal_promise={},
            active_life_chapter=active,
            semantic_focus_result=semantic_focus,
        )
    )
    full_text = out.period_reading_v1["full_text"]

    for banned in ("Asıl omurga", "aynı şey değil", "aynı yerde durmuyor", "Bu en çok", "Bunun altında şu fark çalışıyor"):
        assert banned not in full_text
