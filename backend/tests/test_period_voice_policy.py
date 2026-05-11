from app.transit.narrative.period_voice_policy import build_period_voice_policy


def test_period_voice_policy_maps_work_visibility_saturn_to_responsibility() -> None:
    policy = build_period_voice_policy(
        canonical_period_spine={
            "spine_lines": ["work_visibility_line"],
            "target_node_id": "promise_mature_visibility",
            "matched_event_ids": ["evt_saturn_mc"],
        },
        matched_events=[
            {
                "event_id": "evt_saturn_mc",
                "transit_body": "Saturn",
                "aspect": "conjunction",
                "natal_point": "MC",
            }
        ],
        chapter_role="builder",
        canonical_backing_node_ids=["promise_mature_visibility"],
    )

    assert policy["mechanism_lens"] == "work_visibility_line.responsibility"
    assert policy["psychological_process"] == "work_visibility_responsibility_process"
    assert policy["higher_meaning"] == "work_visibility_responsibility_meaning"
    assert policy["reason_line_allowed"] is True
    assert policy["reason_line_seed"] == "work_visibility_responsibility_reason"
    assert policy["meaning_intent"] == "responsibility_selection"
    assert policy["rhetorical_frame"] == "sorting"
    assert policy["upper_meaning_seed"] == "work_visibility_responsibility_meaning"
    assert policy["frame_seed"] == "responsibility_selection.sorting"
    assert policy["manifestation_context"]["primary_house"] == 10
    assert policy["manifestation_context"]["source"] in {"angle", "event_house", "target_planet_house"}
    assert policy["debug"]["event_nature"] == "responsibility"
    assert policy["debug"]["event_nature_source"] == "spine_line_context"
    assert policy["debug"]["match_level"] == "exact"
    assert policy["debug"]["manifestation_context"]["life_scene"]
    assert "generic_hat_copy" in policy["avoid_tags"]


def test_period_voice_policy_keeps_reason_line_off_without_backing() -> None:
    policy = build_period_voice_policy(
        canonical_period_spine={
            "spine_lines": ["work_visibility_line"],
            "matched_event_ids": ["evt_mars_mc"],
        },
        matched_events=[
            {
                "event_id": "evt_mars_mc",
                "transit_body": "Mars",
                "aspect": "trine",
                "natal_point": "MC",
            }
        ],
        chapter_role="opener",
        canonical_backing_node_ids=[],
    )

    assert policy["mechanism_lens"] == "work_visibility_line.courage"
    assert policy["reason_line_allowed"] is False
    assert policy["reason_line_seed"] == ""
    assert policy["psychological_process"] == "work_visibility_courage_process"


def test_period_voice_policy_maps_shadow_pluto_to_control() -> None:
    policy = build_period_voice_policy(
        canonical_period_spine={
            "spine_lines": ["shadow_protection_line"],
            "target_node_id": "contradiction_control_vs_surrender",
            "matched_event_ids": ["evt_pluto"],
        },
        matched_events=[
            {
                "event_id": "evt_pluto",
                "transit_body": "Pluto",
                "aspect": "square",
                "natal_point": "Moon",
            }
        ],
        chapter_role="release",
        canonical_backing_node_ids=["contradiction_control_vs_surrender"],
    )

    assert policy["mechanism_lens"] == "shadow_protection_line.control"
    assert policy["psychological_process"] == "shadow_protection_control_process"
    assert policy["growth_edge"] == "shadow_protection_control_edge"
    assert policy["debug"]["chapter_role"] == "release"


def test_period_voice_policy_is_deterministic_for_same_inputs() -> None:
    kwargs = {
        "canonical_period_spine": {
            "spine_lines": ["relational_line"],
            "target_node_id": "promise_safe_intimacy",
            "matched_event_ids": ["evt_venus"],
        },
        "matched_events": [
            {
                "event_id": "evt_venus",
                "transit_body": "Venus",
                "aspect": "trine",
                "natal_point": "Moon",
            }
        ],
        "chapter_role": "peak",
        "canonical_backing_node_ids": ["promise_safe_intimacy"],
    }

    assert build_period_voice_policy(**kwargs) == build_period_voice_policy(**kwargs)


def test_period_voice_policy_changes_for_same_spine_line_with_different_event_nature() -> None:
    spine = {
        "spine_lines": ["work_visibility_line"],
        "target_node_id": "promise_visibility",
    }
    courage = build_period_voice_policy(
        canonical_period_spine={**spine, "matched_event_ids": ["evt_mars"]},
        matched_events=[{"event_id": "evt_mars", "transit_body": "Mars", "aspect": "trine"}],
        chapter_role="opener",
        canonical_backing_node_ids=["promise_visibility"],
    )
    responsibility = build_period_voice_policy(
        canonical_period_spine={**spine, "matched_event_ids": ["evt_saturn"]},
        matched_events=[{"event_id": "evt_saturn", "transit_body": "Saturn", "aspect": "conjunction"}],
        chapter_role="opener",
        canonical_backing_node_ids=["promise_visibility"],
    )

    assert courage["mechanism_lens"] == "work_visibility_line.courage"
    assert responsibility["mechanism_lens"] == "work_visibility_line.responsibility"
    assert courage["psychological_process"] != responsibility["psychological_process"]


def test_period_voice_policy_reads_saturn_as_boundary_in_relational_line() -> None:
    policy = build_period_voice_policy(
        canonical_period_spine={
            "spine_lines": ["relational_line"],
            "target_node_id": "promise_safe_intimacy",
            "matched_event_ids": ["evt_saturn_venus"],
        },
        matched_events=[
            {
                "event_id": "evt_saturn_venus",
                "transit_body": "Saturn",
                "aspect": "conjunction",
                "natal_point": "Venus",
            }
        ],
        chapter_role="builder",
        canonical_backing_node_ids=["promise_safe_intimacy"],
    )

    assert policy["mechanism_lens"] == "relational_line.boundary"
    assert policy["psychological_process"] == "relational_boundary_process"
    assert policy["meaning_intent"] == "trust_calibration"
    assert policy["rhetorical_frame"] == "calibration"
    assert policy["debug"]["event_nature_source"] == "spine_line_context"


def test_period_voice_policy_maps_neptune_shadow_to_dissolution() -> None:
    policy = build_period_voice_policy(
        canonical_period_spine={
            "spine_lines": ["shadow_protection_line"],
            "target_node_id": "contradiction_boundary_blur",
            "matched_event_ids": ["evt_neptune"],
        },
        matched_events=[
            {
                "event_id": "evt_neptune",
                "transit_body": "Neptune",
                "aspect": "square",
                "natal_point": "ASC",
            }
        ],
        chapter_role="release",
        canonical_backing_node_ids=["contradiction_boundary_blur"],
    )

    assert policy["mechanism_lens"] == "shadow_protection_line.dissolution"
    assert policy["growth_edge"] == "shadow_protection_dissolution_edge"


def test_period_voice_policy_maps_uranus_growth_to_change() -> None:
    policy = build_period_voice_policy(
        canonical_period_spine={
            "spine_lines": ["growth_integration_line"],
            "target_node_id": "promise_integrated_direction",
            "matched_event_ids": ["evt_uranus"],
        },
        matched_events=[
            {
                "event_id": "evt_uranus",
                "transit_body": "Uranus",
                "aspect": "trine",
                "natal_point": "Mars",
            }
        ],
        chapter_role="integrator",
        canonical_backing_node_ids=["promise_integrated_direction"],
    )

    assert policy["mechanism_lens"] == "growth_integration_line.change"
    assert policy["what_it_builds"] == "growth_integration_change_build"


def test_period_voice_policy_returns_seed_values_not_final_copy() -> None:
    policy = build_period_voice_policy(
        canonical_period_spine={
            "spine_lines": ["work_visibility_line"],
            "target_node_id": "promise_visibility",
            "matched_event_ids": ["evt_mars"],
        },
        matched_events=[{"event_id": "evt_mars", "transit_body": "Mars", "aspect": "trine"}],
        chapter_role="opener",
        canonical_backing_node_ids=["promise_visibility"],
    )

    for key in ("psychological_process", "higher_meaning", "growth_edge", "what_it_builds", "reason_line_seed"):
        assert " " not in policy[key]
        assert policy[key].startswith("work_visibility_courage_")


def test_period_voice_policy_rotates_frame_when_recent_session_used_same_one() -> None:
    policy = build_period_voice_policy(
        canonical_period_spine={
            "spine_lines": ["work_visibility_line"],
            "target_node_id": "promise_mature_visibility",
            "matched_event_ids": ["evt_saturn_mc"],
        },
        matched_events=[
            {
                "event_id": "evt_saturn_mc",
                "transit_body": "Saturn",
                "aspect": "conjunction",
                "natal_point": "MC",
            }
        ],
        chapter_role="builder",
        canonical_backing_node_ids=["promise_mature_visibility"],
        recent_rhetorical_frames=["sorting"],
    )

    assert policy["meaning_intent"] == "responsibility_selection"
    assert policy["rhetorical_frame"] == "threshold"
    assert policy["debug"]["frame_debug"]["rotation_applied"] is True
