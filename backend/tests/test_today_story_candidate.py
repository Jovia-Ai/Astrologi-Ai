from app.transit.narrative.today_story_candidate import build_today_story_candidate


def _period_spine(**overrides):
    base = {
        "version": "canonical_period_spine_v1",
        "source": "canonical_natal_activation_v1",
        "hook_id": "hook:relationship",
        "target_node_id": "promise_build_safe_intimacy",
        "domains": ["relationship"],
        "primary_domain": "relationship",
        "spine_lines": ["relational_line"],
    }
    base.update(overrides)
    return base


def _daily_event(**overrides):
    base = {
        "event_id": "evt_daily",
        "transit_body": "Saturn",
        "aspect": "opposition",
        "natal_point": "Venus",
        "horizon": "daily",
        "chapter_role": {"role": "builder"},
    }
    base.update(overrides)
    return base


def test_period_spine_matching_daily_trigger_builds_period_triggered_today() -> None:
    candidate = build_today_story_candidate(
        canonical_period_spine=_period_spine(),
        daily_event_cards=[_daily_event(), _daily_event(event_id="evt_support", transit_body="Moon")],
        period_event_cards=[],
        daily_selection={
            "natal_activation_context": {
                "matched_event_ids": ["evt_daily"],
                "top_hook_ids": ["hook:relationship"],
            }
        },
    )

    assert candidate["story_type"] == "period_triggered_today"
    assert candidate["primary_period_spine_id"] == "hook:relationship"
    assert candidate["primary_spine_line"] == "relational_line"
    assert candidate["primary_trigger_event_id"] == "evt_daily"
    assert candidate["support_event_ids"] == ["evt_support"]
    assert candidate["event_nature"] == "boundary"
    assert candidate["mechanism_lens"] == "relational_line.boundary"
    assert candidate["growth_edge"] == "relational_boundary_edge"
    assert candidate["reason_line_allowed"] is True
    assert candidate["reason_line_seed"] == "relational_boundary_reason"
    assert candidate["debug"]["activation_hook_match"] is True
    assert candidate["debug"]["period_spine_source"] == "canonical_natal_activation_v1"
    assert candidate["debug"]["suppressed_daily_events"] == ["evt_support"]


def test_trigger_selection_primary_can_drive_today_story_candidate() -> None:
    candidate = build_today_story_candidate(
        canonical_period_spine=_period_spine(),
        daily_event_cards=[_daily_event(event_id="evt_legacy", transit_body="Moon")],
        period_event_cards=[],
        daily_selection={
            "trigger_selection": {
                "primary_trigger_event_id": "evt_canonical",
                "support_event_ids": ["evt_legacy"],
                "suppressed_event_ids": ["evt_surface"],
                "candidates": [
                    {
                        "event_id": "evt_canonical",
                        "role": "primary_trigger",
                        "debug": {
                            "event_snapshot": {
                                "event_id": "evt_canonical",
                                "transit_body": "Saturn",
                                "aspect": "opposition",
                                "natal_point": "Venus",
                                "chapter_role": {"role": "builder"},
                            }
                        },
                    }
                ],
            }
        },
    )

    assert candidate["story_type"] == "period_triggered_today"
    assert candidate["primary_trigger_event_id"] == "evt_canonical"
    assert candidate["support_event_ids"] == ["evt_legacy"]
    assert candidate["event_nature"] == "boundary"
    assert candidate["debug"]["selected_trigger_reason"] == "daily_trigger_selection_primary"
    assert candidate["debug"]["suppressed_daily_events"] == ["evt_surface"]


def test_period_spine_without_trigger_builds_period_continuation() -> None:
    candidate = build_today_story_candidate(
        canonical_period_spine=_period_spine(
            hook_id="hook:career",
            target_node_id="promise_mature_visibility",
            spine_lines=["work_visibility_line"],
        ),
        daily_event_cards=[_daily_event(event_id="evt_daily")],
        period_event_cards=[_daily_event(event_id="evt_period", horizon="period", transit_body="Saturn")],
        daily_selection={
            "natal_activation_context": {
                "matched_event_ids": ["evt_daily"],
                "top_hook_ids": ["hook:relationship"],
            }
        },
    )

    assert candidate["story_type"] == "period_continuation"
    assert candidate["primary_trigger_event_id"] == "evt_period"
    assert candidate["event_nature"] == "responsibility"
    assert candidate["debug"]["activation_hook_match"] is False
    assert candidate["debug"]["selected_trigger_reason"] == "canonical_period_spine_without_daily_trigger"
    assert candidate["debug"]["suppressed_daily_events"] == ["evt_daily"]


def test_trigger_selection_without_primary_builds_period_continuation() -> None:
    candidate = build_today_story_candidate(
        canonical_period_spine=_period_spine(),
        daily_event_cards=[_daily_event(event_id="evt_support")],
        period_event_cards=[_daily_event(event_id="evt_period", horizon="period", transit_body="Saturn")],
        daily_selection={
            "trigger_selection": {
                "primary_trigger_event_id": None,
                "support_event_ids": ["evt_support"],
                "suppressed_event_ids": [],
                "candidates": [],
            }
        },
    )

    assert candidate["story_type"] == "period_continuation"
    assert candidate["primary_trigger_event_id"] == "evt_period"
    assert candidate["support_event_ids"] == ["evt_support"]
    assert candidate["debug"]["selected_trigger_reason"] == "daily_trigger_selection_period_continuation"


def test_no_period_spine_daily_event_builds_daily_flavor() -> None:
    candidate = build_today_story_candidate(
        canonical_period_spine={},
        daily_event_cards=[_daily_event()],
        period_event_cards=[],
        daily_selection={},
    )

    assert candidate["story_type"] == "daily_flavor"
    assert candidate["primary_period_spine_id"] is None
    assert candidate["primary_trigger_event_id"] == "evt_daily"
    assert candidate["reason_line_allowed"] is False
    assert candidate["debug"]["selected_trigger_reason"] == "no_period_spine_daily_event_available"


def test_no_period_spine_no_daily_event_builds_quiet_day() -> None:
    candidate = build_today_story_candidate(
        canonical_period_spine={},
        daily_event_cards=[],
        period_event_cards=[],
        daily_selection={},
    )

    assert candidate["story_type"] == "quiet_day"
    assert candidate["primary_trigger_event_id"] is None
    assert candidate["support_event_ids"] == []
    assert candidate["debug"]["selected_trigger_reason"] == "no_period_spine_no_daily_event"


def test_no_backing_keeps_reason_line_off_even_when_period_triggered() -> None:
    candidate = build_today_story_candidate(
        canonical_period_spine=_period_spine(target_node_id="", backing_node_ids=[]),
        daily_event_cards=[_daily_event()],
        period_event_cards=[],
        daily_selection={
            "natal_activation_context": {
                "matched_event_ids": ["evt_daily"],
                "top_hook_ids": ["hook:relationship"],
            }
        },
    )

    assert candidate["story_type"] == "period_triggered_today"
    assert candidate["natal_backing_node_ids"] == []
    assert candidate["reason_line_allowed"] is False
    assert candidate["reason_line_seed"] is None


def test_same_spine_line_different_event_nature_changes_policy_seed() -> None:
    courage_candidate = build_today_story_candidate(
        canonical_period_spine=_period_spine(
            hook_id="hook:career",
            target_node_id="promise_mature_visibility",
            primary_domain="career_visibility",
            spine_lines=["work_visibility_line"],
        ),
        daily_event_cards=[_daily_event(transit_body="Mars", aspect="trine", natal_point="Sun")],
        period_event_cards=[],
        daily_selection={
            "natal_activation_context": {
                "matched_event_ids": ["evt_daily"],
                "top_hook_ids": ["hook:career"],
            }
        },
    )
    responsibility_candidate = build_today_story_candidate(
        canonical_period_spine=_period_spine(
            hook_id="hook:career",
            target_node_id="promise_mature_visibility",
            primary_domain="career_visibility",
            spine_lines=["work_visibility_line"],
        ),
        daily_event_cards=[_daily_event(transit_body="Saturn", aspect="trine", natal_point="Sun")],
        period_event_cards=[],
        daily_selection={
            "natal_activation_context": {
                "matched_event_ids": ["evt_daily"],
                "top_hook_ids": ["hook:career"],
            }
        },
    )

    assert courage_candidate["event_nature"] == "courage"
    assert responsibility_candidate["event_nature"] == "responsibility"
    assert courage_candidate["mechanism_lens"] == "work_visibility_line.courage"
    assert responsibility_candidate["mechanism_lens"] == "work_visibility_line.responsibility"
    assert courage_candidate["growth_edge"] != responsibility_candidate["growth_edge"]


def test_exceptional_event_wins_before_period_trigger() -> None:
    candidate = build_today_story_candidate(
        canonical_period_spine=_period_spine(),
        daily_event_cards=[
            _daily_event(event_id="evt_eclipse", event_family="eclipse_trigger"),
            _daily_event(event_id="evt_daily"),
        ],
        period_event_cards=[],
        daily_selection={
            "natal_activation_context": {
                "matched_event_ids": ["evt_daily"],
                "top_hook_ids": ["hook:relationship"],
            }
        },
    )

    assert candidate["story_type"] == "exceptional_event"
    assert candidate["primary_trigger_event_id"] == "evt_eclipse"
    assert candidate["debug"]["selected_trigger_reason"] == "exceptional_event"
