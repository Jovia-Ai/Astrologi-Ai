from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.narrative.voice_guardrails_tr import validate_life_chapter_selected_meaning
from app.transit.narrative import daily_selection
from app.transit.narrative.astrolog_narrative_engine import PeriodStoryContext, build_period_story
from app.transit.narrative.life_chapter_contract import ChapterPhase, LifeChapter
from app.transit.narrative.life_chapter_detector import detect_active_life_chapter
from app.transit.narrative.selection import select_event_ids

_FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "life_chapter"


def _base_event(**overrides):
    event = {
        "event_id": "evt-base",
        "event_family": "aspect_event",
        "event_subtype": "square",
        "start_at": "2026-05-01",
        "exact_at": ["2026-05-03T00:00:00"],
        "end_at": "2026-05-10",
        "chapter_opening": False,
        "structural_significance": 0.34,
        "precision_signal": 0.44,
    }
    event.update(overrides)
    return event


def _load_fixture(group: str, name: str) -> dict:
    path = _FIXTURE_ROOT / group / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_state_with_overlap():
    return _load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")["canonical_natal_state"]


def _canonical_state_without_overlap():
    return {
        "bodies": [
            {"body": "Saturn", "sign": "Aries", "house": 3},
            {"body": "North Node", "sign": "Libra", "house": 9},
            {"body": "South Node", "sign": "Libra", "house": 9},
        ],
        "house_cusps": [
            {"house": 1, "sign": "Capricorn"},
            {"house": 2, "sign": "Aquarius"},
            {"house": 3, "sign": "Pisces"},
            {"house": 4, "sign": "Aries"},
            {"house": 5, "sign": "Taurus"},
            {"house": 6, "sign": "Gemini"},
            {"house": 7, "sign": "Cancer"},
            {"house": 8, "sign": "Leo"},
            {"house": 9, "sign": "Virgo"},
            {"house": 10, "sign": "Libra"},
            {"house": 11, "sign": "Scorpio"},
            {"house": 12, "sign": "Sagittarius"},
        ],
    }


def _canonical_state_direction_missing():
    return {
        "bodies": [
            {"body": "North Node", "sign": "Aries", "house": 3},
        ]
    }


def _story_ctx():
    return PeriodStoryContext(
        period_core={
            "featured_events": [
                {
                    "event_id": "evt_story",
                    "transit_body": "Neptune",
                    "aspect": "square",
                    "natal_point": "ASC",
                    "strength": 0.95,
                    "orb_deg": 0.2,
                    "phase": "exactish",
                    "bucket": "long",
                    "tags": ["self", "pressure"],
                    "houses": {"transit_in_natal_house": 3, "natal_point_house": None},
                }
            ]
        },
        chart_snapshot={},
        natal_promise={},
    )


def _selection_natal() -> dict:
    return {
        "bodies": [
            {"body": "Sun", "lon": 276.75, "sign": "Capricorn", "house": 1},
            {"body": "Mercury", "lon": 287.36, "sign": "Capricorn", "house": 1},
            {"body": "Mars", "lon": 177.93, "sign": "Virgo", "house": 9},
            {"body": "Saturn", "lon": 1.15, "sign": "Aries", "house": 3},
            {"body": "Neptune", "lon": 296.69, "sign": "Capricorn", "house": 1},
            {"body": "Pluto", "lon": 244.25, "sign": "Sagittarius", "house": 11},
            {"body": "Uranus", "lon": 303.06, "sign": "Aquarius", "house": 1},
        ],
        "angles": {
            "ASC": {"point": "ASC", "sign": "Capricorn"},
            "MC": {"point": "MC", "sign": "Libra"},
            "DSC": {"point": "DSC", "sign": "Cancer"},
            "IC": {"point": "IC", "sign": "Aries"},
        },
        "house_cusps": [
            {"house": 1, "sign": "Capricorn"},
            {"house": 2, "sign": "Aquarius"},
            {"house": 3, "sign": "Pisces"},
            {"house": 4, "sign": "Aries"},
            {"house": 5, "sign": "Taurus"},
            {"house": 6, "sign": "Gemini"},
            {"house": 7, "sign": "Cancer"},
            {"house": 8, "sign": "Leo"},
            {"house": 9, "sign": "Virgo"},
            {"house": 10, "sign": "Libra"},
            {"house": 11, "sign": "Scorpio"},
            {"house": 12, "sign": "Sagittarius"},
        ],
    }


def _selection_events() -> list[dict]:
    return [
        {
            "event_id": "evt_neptune_asc",
            "scope": "transit_to_angles",
            "transit_body": "Neptune",
            "aspect": "square",
            "natal_point": "ASC",
            "strength": 0.972,
            "orb_deg": 0.17,
            "phase": "exactish",
            "bucket": "long",
            "tags": ["self", "pressure", "friction"],
            "houses": {"transit_in_natal_house": 3, "natal_point_house": None},
            "polarity": "hard",
        },
        {
            "event_id": "evt_uranus_mars",
            "scope": "transit_to_natal",
            "transit_body": "Uranus",
            "aspect": "trine",
            "natal_point": "Mars",
            "strength": 0.965,
            "orb_deg": 0.21,
            "phase": "applying",
            "bucket": "long",
            "tags": ["career", "support", "flow"],
            "houses": {"transit_in_natal_house": 5, "natal_point_house": 9},
            "polarity": "soft",
        },
        {
            "event_id": "evt_saturn_sun",
            "scope": "transit_to_natal",
            "transit_body": "Saturn",
            "aspect": "square",
            "natal_point": "Sun",
            "strength": 0.85,
            "orb_deg": 0.80,
            "phase": "applying",
            "bucket": "long",
            "tags": ["self", "pressure", "friction"],
            "houses": {"transit_in_natal_house": 3, "natal_point_house": 1},
            "polarity": "hard",
        },
    ]


def _daily_raw_event():
    return {
        "event_id": "evt_daily",
        "transit_body": "Mercury",
        "natal_point": "Sun",
        "aspect": "opposition",
        "bucket": "short",
        "phase": "exactish",
        "orb_deg": 0.2,
        "event_family": "aspect_event",
        "event_subtype": "",
        "houses": {"transit_in_natal_house": 3, "natal_point_house": 3},
        "ranking": {"tier": "main", "weight": 1.2, "exact_in_days": 1},
        "timing": {
            "peak_date_utc": "2026-03-10T09:00:00+00:00",
            "entry_date_utc": "2026-03-09T09:00:00+00:00",
        },
    }


def _daily_context(item: dict) -> dict:
    house = item["houses"]["natal_point_house"]
    return {
        "card": {
            "event_id": item["event_id"],
            "transit_body": item["transit_body"],
            "natal_point": item["natal_point"],
            "aspect": item["aspect"],
            "bucket": item["bucket"],
            "phase": item["phase"],
            "horizon": "daily",
            "orb_deg": item["orb_deg"],
            "timing": dict(item.get("timing") or {}),
            "derived_context": {"natal_target": {"house": house}},
            "scene": {"outcome_house": house, "start_house": house},
            "natal_promise": {"score": 0.74},
            "tags": {"exact_in_days": 1, "intensity": 0.68},
        },
        "selected_day_context": {
            "labels": ["mind"],
            "top_event_ids": [item["event_id"]],
            "critical_reasons": [],
            "signals_count": 2,
        },
        "config": daily_selection.load_daily_selection_config(),
    }


def _emit_from_fixture(group: str, name: str) -> LifeChapter:
    fixture = _load_fixture(group, name)
    result = detect_active_life_chapter(
        canonical_natal_state=fixture["canonical_natal_state"],
        transit_events=fixture["transit_events"],
    )
    assert result["active_life_chapter"] is not None
    return LifeChapter(**result["active_life_chapter"])


def test_detector_returns_empty_result_without_chapter_signals() -> None:
    result = detect_active_life_chapter(
        canonical_natal_state=None,
        transit_events=[],
        solar_year_frame=None,
        structural_chapter_rail=None,
    )

    assert result["active_life_chapter"] is None
    assert result["candidates"] == []
    assert result["debug"]["candidate_count"] == 0
    assert result["debug"]["candidate_source_ids"] == []


def test_detector_extracts_saturn_return_candidate_from_mock_event() -> None:
    result = detect_active_life_chapter(
        canonical_natal_state=None,
        transit_events=[
            _base_event(
                event_id="evt-saturn-return",
                event_family="cycle_event",
                event_subtype="saturn_return",
                chapter_opening=False,
                structural_significance=0.52,
                precision_signal=0.28,
            )
        ],
    )

    assert result["active_life_chapter"] is None
    assert len(result["candidates"]) == 1
    candidate = result["candidates"][0]
    assert candidate["chapter_type"] == "saturn_return"
    assert candidate["signal_type"] == "saturn_return"
    assert candidate["source_signal_id"] == "evt-saturn-return"


def test_high_confidence_saturn_return_emits_active_life_chapter() -> None:
    chapter = _emit_from_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    assert chapter.chapter_type.value == "saturn_return"
    assert chapter.phase in set(ChapterPhase)
    assert chapter.debug["node_overlap"]["has_overlap"] is True
    assert "node_overlap" in chapter.debug["source_signal_types"]


def test_low_confidence_saturn_return_does_not_emit_active_life_chapter() -> None:
    result = detect_active_life_chapter(
        canonical_natal_state=_canonical_state_without_overlap(),
        transit_events=[
            _base_event(
                event_id="evt-saturn-low",
                event_family="cycle_event",
                event_subtype="saturn_return",
                chapter_opening=False,
                structural_significance=0.52,
                precision_signal=0.24,
                current_phase="background",
                source_bodies=["Saturn"],
                target_points=["Saturn"],
                target_houses=[3],
            )
        ],
    )

    assert result["active_life_chapter"] is None
    assert len(result["candidates"]) == 1


def test_saturn_return_selected_meaning_is_not_cookbook() -> None:
    chapter = _emit_from_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    assert "responsibility" not in chapter.selected_meaning.lower()
    assert "maturity" not in chapter.selected_meaning.lower()
    assert validate_life_chapter_selected_meaning(chapter.selected_meaning) == []


def test_saturn_return_evidence_includes_return_and_natal_context() -> None:
    chapter = _emit_from_fixture("saturn_return", "leo_10th_career_identity")
    roles = {entry.role for entry in chapter.evidence}
    assert "return" in roles
    assert "natal_context" in roles


def test_saturn_return_evidence_includes_node_overlap_when_present() -> None:
    chapter = _emit_from_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    roles = {entry.role for entry in chapter.evidence}
    assert "axis_overlap" in roles
    assert {"return", "natal_context", "semantic_focus_support", "suppression_guard"} <= roles


def test_saturn_return_suppressed_readings_includes_generic_difficulty() -> None:
    chapter = _emit_from_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    readings = {entry.reading for entry in chapter.suppressed_readings}
    assert "generic communication difficulty" in readings
    assert "generic burden / heaviness" in readings


def test_saturn_return_semantic_focus_primary_is_speech_authority_for_aries_3rd() -> None:
    chapter = _emit_from_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    assert chapter.semantic_focus.primary == "speech_authority"
    assert "mental_reflex_maturation" in chapter.semantic_focus.secondary
    assert "sibling conflict prediction" in chapter.semantic_focus.not_this


def test_saturn_return_renderer_handoff_carries_chapter_weight_and_contrast() -> None:
    chapter = _emit_from_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    assert chapter.renderer_handoff.chapter_weight == "not ordinary transit; long-cycle maturation"
    assert "hızlı cevap vermek" in chapter.renderer_handoff.core_contrast
    assert "kısa mesajlar" in chapter.renderer_handoff.human_scene
    assert chapter.natal_architecture_anchor.label == "identity_as_construction_project"
    assert chapter.chapter_claim_strength == "foundational long-cycle chapter"
    assert chapter.scene_priority[0].priority == "primary"


def test_saturn_return_suppressed_surface_readings_include_shallow_fallbacks() -> None:
    chapter = _emit_from_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    readings = {entry.reading for entry in chapter.suppressed_surface_readings}
    assert "generic communication difficulty" in readings
    assert "sibling conflict prediction" in readings


def test_high_confidence_nodal_return_emits_active_life_chapter() -> None:
    chapter = _emit_from_fixture("nodal", "nn_aries_sn_libra")
    assert chapter.chapter_type.value == "nodal_return"
    assert chapter.selected_meaning


def test_nodal_return_directional_meaning_when_direction_known() -> None:
    chapter = _emit_from_fixture("nodal", "nn_aries_sn_libra")
    assert "başkalarına göre ayar verme" in chapter.selected_meaning
    assert "daha doğrudan yön" in chapter.selected_meaning


def test_nodal_direction_aries_libra_distinct() -> None:
    aries = _emit_from_fixture("nodal", "nn_aries_sn_libra")
    libra = _emit_from_fixture("nodal", "nn_libra_sn_aries")
    assert aries.selected_meaning != libra.selected_meaning
    assert "doğrudan yön" in aries.selected_meaning
    assert "ilişki ve eşgüdüm" in libra.selected_meaning


def test_nodal_activation_no_generic_balance_when_direction_missing() -> None:
    result = detect_active_life_chapter(
        canonical_natal_state=_canonical_state_direction_missing(),
        transit_events=[
            _base_event(
                event_id="evt-nodal-opposition",
                event_family="cycle_event",
                event_subtype="nodal_opposition",
                chapter_opening=True,
                structural_significance=0.9,
                precision_signal=0.82,
                current_phase="exact",
                source_bodies=["North Node"],
                target_points=["North Node"],
                target_houses=[3],
            )
        ],
    )
    chapter = LifeChapter(**result["active_life_chapter"])
    assert "ben/biz dengesi" not in chapter.selected_meaning
    assert any(entry.reading == "generic self/other balance" for entry in chapter.suppressed_readings)


def test_nodal_activation_lowers_confidence_when_direction_missing() -> None:
    result = detect_active_life_chapter(
        canonical_natal_state=_canonical_state_direction_missing(),
        transit_events=[
            _base_event(
                event_id="evt-nodal-opposition",
                event_family="cycle_event",
                event_subtype="nodal_opposition",
                chapter_opening=True,
                structural_significance=0.9,
                precision_signal=0.82,
                current_phase="exact",
                source_bodies=["North Node"],
                target_points=["North Node"],
                target_houses=[3],
            )
        ],
    )
    chapter = LifeChapter(**result["active_life_chapter"])
    assert chapter.confidence.value in {"low", "medium"}


def test_nodal_return_renderer_handoff_is_directional_when_direction_known() -> None:
    chapter = _emit_from_fixture("nodal", "nn_aries_sn_libra")
    assert chapter.semantic_focus.primary == "directional_self_definition"
    assert "başkalarına göre ayar verme" in chapter.renderer_handoff.chart_specific_anchor
    assert "generic self/other balance" in chapter.renderer_handoff.avoid_readings


def test_nodal_activation_direction_missing_keeps_generic_balance_suppressed() -> None:
    result = detect_active_life_chapter(
        canonical_natal_state=_canonical_state_direction_missing(),
        transit_events=[
            _base_event(
                event_id="evt-nodal-opposition",
                event_family="cycle_event",
                event_subtype="nodal_opposition",
                chapter_opening=True,
                structural_significance=0.9,
                precision_signal=0.82,
                current_phase="exact",
                source_bodies=["North Node"],
                target_points=["North Node"],
                target_houses=[3],
            )
        ],
    )
    chapter = LifeChapter(**result["active_life_chapter"])
    readings = {entry.reading for entry in chapter.suppressed_surface_readings}
    assert "generic self/other balance" in readings


def test_phase_source_and_reason_in_debug() -> None:
    chapter = _emit_from_fixture("saturn_return", "leo_10th_career_identity")
    assert chapter.debug["phase_source"]
    assert chapter.debug["phase_reason"]


def test_confidence_rationale_in_debug() -> None:
    chapter = _emit_from_fixture("saturn_return", "cancer_8th_water_emotional")
    assert "confidence" in chapter.debug["confidence_rationale"]


def test_selected_meaning_passes_voice_guardrails() -> None:
    for group, name in [
        ("saturn_return", "aries_3rd_with_south_node_overlap"),
        ("saturn_return", "cancer_8th_water_emotional"),
        ("saturn_return", "leo_10th_career_identity"),
        ("nodal", "nn_aries_sn_libra"),
        ("nodal", "nn_libra_sn_aries"),
    ]:
        chapter = _emit_from_fixture(group, name)
        assert validate_life_chapter_selected_meaning(chapter.selected_meaning) == []


def test_overlap_merges_into_single_chapter() -> None:
    result = detect_active_life_chapter(
        canonical_natal_state=_canonical_state_with_overlap(),
        transit_events=[
            _load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")["transit_events"][0],
            _base_event(
                event_id="evt-nodal-opposition",
                event_family="cycle_event",
                event_subtype="nodal_opposition",
                start_at="2026-02-15",
                exact_at=["2026-05-11T00:00:00"],
                end_at="2026-08-30",
                chapter_opening=True,
                structural_significance=0.9,
                precision_signal=0.83,
                current_phase="exact",
                source_bodies=["North Node"],
                target_points=["North Node"],
                target_houses=[3],
            ),
        ],
    )
    chapter = LifeChapter(**result["active_life_chapter"])
    assert chapter.chapter_type.value == "saturn_return"
    assert chapter.debug["merge_reason"]
    assert any(entry.role == "axis_overlap" for entry in chapter.evidence)


def test_hierarchy_picks_saturn_return_over_nodal_return() -> None:
    result = detect_active_life_chapter(
        canonical_natal_state=_canonical_state_without_overlap(),
        transit_events=[
            _load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")["transit_events"][0],
            _load_fixture("nodal", "nn_aries_sn_libra")["transit_events"][0],
        ],
    )
    chapter = LifeChapter(**result["active_life_chapter"])
    assert chapter.chapter_type.value == "saturn_return"
    assert "per Tier-1 hierarchy" in chapter.debug["selection_reason"]


def test_suppressed_candidates_in_debug() -> None:
    result = detect_active_life_chapter(
        canonical_natal_state=_canonical_state_without_overlap(),
        transit_events=[
            _load_fixture("saturn_return", "leo_10th_career_identity")["transit_events"][0],
            _load_fixture("nodal", "nn_aries_sn_libra")["transit_events"][0],
        ],
    )
    chapter = LifeChapter(**result["active_life_chapter"])
    assert chapter.debug["suppressed_candidates"]


def test_structural_candidate_debug_carries_three_part_pressure_handoff() -> None:
    result = detect_active_life_chapter(
        canonical_natal_state=None,
        transit_events=[],
        structural_chapter_rail={
            "id": "structural:t_square",
            "shape": "t_square",
            "apex_house": 4,
            "release_point": "home_space",
        },
        debug=True,
    )
    candidate = result["candidates"][0]
    debug = candidate["debug"]
    assert debug["semantic_focus"]["primary"] == "three_part_pressure_system"
    assert "apex_release_point" in debug["semantic_focus"]["secondary"]
    assert "üç parçalı basınç sistemi" in debug["renderer_handoff"]["chart_specific_anchor"]
    assert debug["structural_pressure_model"] == "three_part_pressure_system"
    assert debug["readiness_status"] == "not_ready"


def test_core_question_is_open_ended() -> None:
    chapter = _emit_from_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    lower = chapter.core_question.lower()
    assert not lower.endswith(" mı?")
    assert not lower.endswith(" mi?")
    assert "nasıl" in lower


def test_core_question_is_natal_specific() -> None:
    chapter = _emit_from_fixture("saturn_return", "cancer_8th_water_emotional")
    assert "8." in chapter.core_question or "Yengeç" in chapter.core_question


def test_core_question_passes_voice_guardrails() -> None:
    chapter = _emit_from_fixture("saturn_return", "leo_10th_career_identity")
    assert validate_life_chapter_selected_meaning(chapter.core_question.rstrip("?")) == []


@pytest.mark.parametrize(
    "text",
    [
        "Bu dönem yeni bir başlangıç olabilir.",
        "Yeni kapılar açılıyor.",
        "Bu chapter değişim getirecek.",
        "Bu süreçte zorlanabilirsin.",
        "Belki şunu fark edersin...",
        "Hayatın değişiyor.",
        "İlişkilerinde dönüşüm yaşanıyor.",
        "Kariyerinde ilerleme olacak.",
        "Evren sana şunu söylüyor.",
        "Yıldızlar şunu işaret ediyor.",
        "Saturn sana öğretiyor.",
    ],
)
def test_subtle_prediction_patterns_rejected(text: str) -> None:
    assert validate_life_chapter_selected_meaning(text)


def test_saturn_return_aries_3rd_fixture() -> None:
    fixture = _load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    chapter = _emit_from_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    for token in fixture["expected_substrings"]:
        assert token in chapter.selected_meaning


def test_saturn_return_cancer_8th_fixture() -> None:
    fixture = _load_fixture("saturn_return", "cancer_8th_water_emotional")
    chapter = _emit_from_fixture("saturn_return", "cancer_8th_water_emotional")
    for token in fixture["expected_substrings"]:
        assert token in chapter.selected_meaning


def test_saturn_return_cancer_8th_handoff_does_not_default_to_generic_emotional_regulation() -> None:
    chapter = _emit_from_fixture("saturn_return", "cancer_8th_water_emotional")
    assert chapter.semantic_focus.primary == "shared_emotional_territory"
    assert "trust_under_pressure" in chapter.semantic_focus.secondary
    assert chapter.domain_ownership.primary_domain == "trust_transformation"
    assert "generic emotional regulation" in chapter.semantic_focus.not_this
    assert "mahrem konuşmalar" in chapter.renderer_handoff.human_scene
    assert "shared_burden" in chapter.shared_domain_priority
    assert "emotional_exchange" in chapter.shared_domain_priority
    assert chapter.trust_axis_anchor
    assert chapter.shared_vs_private_contrast
    readings = {entry.reading for entry in chapter.suppressed_surface_readings}
    assert "oversensitivity cliché" in readings
    assert "self-care simplification" in readings
    assert "generic vulnerability language" in readings


def test_saturn_return_cancer_8th_evidence_roles_include_house_context() -> None:
    chapter = _emit_from_fixture("saturn_return", "cancer_8th_water_emotional")
    roles = {entry.role for entry in chapter.evidence}
    assert {"return", "natal_context", "house_context", "semantic_focus_support", "suppression_guard"} <= roles


def test_structural_candidate_is_explicitly_excluded_from_pr_d_v1_scope() -> None:
    result = detect_active_life_chapter(
        canonical_natal_state=None,
        transit_events=[],
        structural_chapter_rail={
            "id": "structural:t_square",
            "shape": "t_square",
            "apex_house": 4,
            "release_point": "home_space",
        },
        debug=True,
    )
    candidate = result["candidates"][0]
    assert candidate["chapter_type"] == "structural_natal_chapter"
    assert candidate["debug"]["excluded_from_pr_d_v1"] is True
    assert candidate["debug"]["future_candidate_pr"] == "PR-C.4"


def test_saturn_return_leo_10th_fixture() -> None:
    fixture = _load_fixture("saturn_return", "leo_10th_career_identity")
    chapter = _emit_from_fixture("saturn_return", "leo_10th_career_identity")
    for token in fixture["expected_substrings"]:
        assert token in chapter.selected_meaning


def test_nodal_return_distinct_fixture_outputs() -> None:
    aries = _emit_from_fixture("nodal", "nn_aries_sn_libra")
    libra = _emit_from_fixture("nodal", "nn_libra_sn_aries")
    assert aries.selected_meaning != libra.selected_meaning


def test_no_period_prose_change() -> None:
    before = build_period_story(_story_ctx())
    detect_active_life_chapter(
        canonical_natal_state=_canonical_state_with_overlap(),
        transit_events=_load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")["transit_events"],
        debug=True,
    )
    after = build_period_story(_story_ctx())

    assert before.period_opening == after.period_opening
    assert before.big_picture == after.big_picture
    assert before.mechanism == after.mechanism


def test_no_selection_priority_change() -> None:
    events = _selection_events()
    before, meta_before = select_event_ids(events, max_cards=5, natal=_selection_natal())
    detect_active_life_chapter(
        canonical_natal_state=_canonical_state_with_overlap(),
        transit_events=_load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")["transit_events"],
    )
    after, meta_after = select_event_ids(events, max_cards=5, natal=_selection_natal())
    assert [item["event_id"] for item in before] == [item["event_id"] for item in after]
    assert meta_before["selected_ids"] == meta_after["selected_ids"]


def test_no_daily_change() -> None:
    event = _daily_raw_event()
    before = daily_selection.compute_strength_score(event, "2026-03-10", _daily_context(event))
    detect_active_life_chapter(
        canonical_natal_state=_canonical_state_with_overlap(),
        transit_events=_load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")["transit_events"],
    )
    after = daily_selection.compute_strength_score(event, "2026-03-10", _daily_context(event))
    assert before == after
