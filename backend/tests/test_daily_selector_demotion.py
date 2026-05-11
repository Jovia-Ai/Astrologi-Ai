from app.transit.narrative import daily_selection


def _raw_event(
    event_id: str,
    *,
    transit_body: str,
    natal_point: str,
    aspect: str,
    bucket: str,
    phase: str,
    orb_deg: float,
    house: int,
    exact_in_days: int = 1,
) -> dict:
    return {
        "event_id": event_id,
        "transit_body": transit_body,
        "natal_point": natal_point,
        "aspect": aspect,
        "bucket": bucket,
        "phase": phase,
        "orb_deg": orb_deg,
        "event_family": "aspect_event",
        "houses": {"transit_in_natal_house": house, "natal_point_house": house},
        "ranking": {"tier": "main", "weight": 1.1, "exact_in_days": exact_in_days},
        "timing": {
            "peak_date_utc": "2026-03-10T09:00:00+00:00",
            "entry_date_utc": "2026-03-09T09:00:00+00:00",
        },
    }


def _card(item: dict) -> dict:
    house = item["houses"]["natal_point_house"]
    return {
        "event_id": item["event_id"],
        "transit_body": item["transit_body"],
        "natal_point": item["natal_point"],
        "aspect": item["aspect"],
        "bucket": item["bucket"],
        "phase": item["phase"],
        "horizon": "daily" if item["bucket"] == "short" else "period",
        "orb_deg": item["orb_deg"],
        "timing": dict(item.get("timing") or {}),
        "derived_context": {"natal_target": {"house": house}},
        "scene": {"start_house": house, "outcome_house": house},
        "natal_promise": {"score": 0.4},
        "tags": {"exact_in_days": (item.get("ranking") or {}).get("exact_in_days", 1)},
    }


def _period_spine(**overrides) -> dict:
    base = {
        "version": "canonical_period_spine_v1",
        "source": "canonical_natal_activation_v1",
        "hook_id": "hook:relationship",
        "target_node_id": "promise_build_safe_intimacy",
        "primary_domain": "relationship",
        "spine_lines": ["relational_line"],
    }
    base.update(overrides)
    return base


def test_hook_matched_event_becomes_primary_trigger_over_surfaceable_legacy_pick() -> None:
    surfaceable = _raw_event(
        "evt_surface",
        transit_body="Moon",
        natal_point="Mercury",
        aspect="square",
        bucket="short",
        phase="exact",
        orb_deg=0.05,
        house=3,
        exact_in_days=0,
    )
    hooked = _raw_event(
        "evt_hooked",
        transit_body="Saturn",
        natal_point="Venus",
        aspect="opposition",
        bucket="short",
        phase="applying",
        orb_deg=1.4,
        house=7,
        exact_in_days=1,
    )

    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[surfaceable, hooked],
        event_cards=[_card(surfaceable), _card(hooked)],
        selected_date="2026-03-10",
        selected_day_context={"labels": ["mind"], "top_event_ids": ["evt_surface"]},
        natal={},
        event_v2_by_id={},
        canonical_natal_activation_by_event={
            "evt_hooked": {
                "matched_hook_ids": ["hook:relationship"],
                "target_node_ids": ["promise_build_safe_intimacy"],
                "activation_score": 0.0,
            },
            "evt_surface": {
                "matched_hook_ids": [],
                "target_node_ids": [],
                "activation_score": 0.0,
            },
        },
        canonical_period_spine=_period_spine(),
    )

    trigger_selection = result["daily_selection"]["trigger_selection"]

    assert result["daily_event_cards"][0]["event_id"] == "evt_surface"
    assert trigger_selection["primary_trigger_event_id"] == "evt_hooked"
    assert trigger_selection["debug"]["legacy_primary_event_id"] == "evt_surface"
    assert trigger_selection["debug"]["mismatch"] is True
    assert trigger_selection["debug"]["mismatch_reason"] == "legacy_selected_highest_surfaceability_candidate_selected_period_hook_match"
    assert "evt_surface" in trigger_selection["suppressed_event_ids"]
    candidate_by_id = {item["event_id"]: item for item in trigger_selection["candidates"]}
    assert candidate_by_id["evt_hooked"]["role"] == "primary_trigger"
    assert candidate_by_id["evt_hooked"]["matched_spine_line"] == "relational_line"
    assert candidate_by_id["evt_surface"]["role"] == "suppressed"


def test_period_continuation_does_not_force_primary_trigger_without_hook_match() -> None:
    daily_event = _raw_event(
        "evt_daily",
        transit_body="Moon",
        natal_point="Mercury",
        aspect="trine",
        bucket="short",
        phase="exactish",
        orb_deg=0.2,
        house=3,
    )

    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[daily_event],
        event_cards=[_card(daily_event)],
        selected_date="2026-03-10",
        selected_day_context={"labels": ["mind"], "top_event_ids": ["evt_daily"]},
        natal={},
        event_v2_by_id={},
        canonical_natal_activation_by_event={
            "evt_daily": {
                "matched_hook_ids": ["hook:mind"],
                "target_node_ids": ["promise_clear_expression"],
                "activation_score": 0.0,
            }
        },
        canonical_period_spine=_period_spine(hook_id="hook:career", target_node_id="promise_mature_visibility", spine_lines=["work_visibility_line"]),
    )

    trigger_selection = result["daily_selection"]["trigger_selection"]

    assert trigger_selection["primary_trigger_event_id"] is None
    assert trigger_selection["support_event_ids"] == ["evt_daily"]
    assert trigger_selection["debug"]["period_continuation"] is True
    assert trigger_selection["debug"]["mismatch_reason"] == "canonical_period_continuation_does_not_force_daily_trigger"


def test_no_period_spine_uses_legacy_daily_flavor_authority() -> None:
    daily_event = _raw_event(
        "evt_daily",
        transit_body="Mercury",
        natal_point="Sun",
        aspect="opposition",
        bucket="short",
        phase="exactish",
        orb_deg=0.2,
        house=3,
    )

    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[daily_event],
        event_cards=[_card(daily_event)],
        selected_date="2026-03-10",
        selected_day_context={},
        natal={},
        event_v2_by_id={},
        canonical_natal_activation_by_event={},
        canonical_period_spine={},
    )

    trigger_selection = result["daily_selection"]["trigger_selection"]

    assert result["daily_event_cards"][0]["event_id"] == "evt_daily"
    assert trigger_selection["authority"] == "legacy_daily_flavor_no_period_spine"
    assert trigger_selection["primary_trigger_event_id"] == "evt_daily"
    assert trigger_selection["debug"]["mismatch"] is False


def test_empty_event_pool_does_not_force_trigger() -> None:
    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[],
        event_cards=[],
        selected_date="2026-03-10",
        selected_day_context={},
        natal={},
        event_v2_by_id={},
        canonical_natal_activation_by_event={},
        canonical_period_spine=_period_spine(),
    )

    trigger_selection = result["daily_selection"]["trigger_selection"]

    assert result["daily_event_cards"] == []
    assert trigger_selection["primary_trigger_event_id"] is None
    assert trigger_selection["support_event_ids"] == []
    assert trigger_selection["suppressed_event_ids"] == []
    assert trigger_selection["candidates"] == []


def test_trigger_selection_is_deterministic() -> None:
    daily_event = _raw_event(
        "evt_hooked",
        transit_body="Saturn",
        natal_point="Venus",
        aspect="opposition",
        bucket="short",
        phase="applying",
        orb_deg=1.4,
        house=7,
    )
    kwargs = {
        "raw_events": [daily_event],
        "event_cards": [_card(daily_event)],
        "selected_date": "2026-03-10",
        "selected_day_context": {},
        "natal": {},
        "event_v2_by_id": {},
        "canonical_natal_activation_by_event": {
            "evt_hooked": {
                "matched_hook_ids": ["hook:relationship"],
                "target_node_ids": ["promise_build_safe_intimacy"],
                "activation_score": 0.0,
            }
        },
        "canonical_period_spine": _period_spine(),
    }

    first = daily_selection.select_daily_and_period_event_cards(**kwargs)["daily_selection"]["trigger_selection"]
    second = daily_selection.select_daily_and_period_event_cards(**kwargs)["daily_selection"]["trigger_selection"]

    assert first == second
