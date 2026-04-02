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
    event_family: str = "aspect_event",
    event_subtype: str = "",
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
        "event_family": event_family,
        "event_subtype": event_subtype,
        "houses": {"transit_in_natal_house": house, "natal_point_house": house},
        "ranking": {"tier": "main", "weight": 1.2, "exact_in_days": exact_in_days},
        "timing": {
            "peak_date_utc": "2026-03-10T09:00:00+00:00",
            "entry_date_utc": "2026-03-09T09:00:00+00:00",
        },
    }


def _materialized_card(item: dict) -> dict:
    house = item["houses"]["natal_point_house"]
    horizon = "daily" if item.get("bucket") == "short" else "period"
    exact_in_days = ((item.get("ranking") or {}).get("exact_in_days")) if isinstance(item.get("ranking"), dict) else 1
    return {
        "event_id": item["event_id"],
        "transit_body": item["transit_body"],
        "natal_point": item["natal_point"],
        "aspect": item["aspect"],
        "bucket": item["bucket"],
        "phase": item["phase"],
        "horizon": horizon,
        "orb_deg": item["orb_deg"],
        "timing": dict(item.get("timing") or {}),
        "derived_context": {"natal_target": {"house": house}},
        "scene": {"outcome_house": house, "start_house": house},
        "natal_promise": {"score": 0.74},
        "tags": {"exact_in_days": exact_in_days, "intensity": 0.68},
    }


def _context(item: dict, *, labels=None, top_event_ids=None) -> dict:
    return {
        "card": _materialized_card(item),
        "selected_day_context": {
            "labels": labels or [],
            "top_event_ids": top_event_ids or [],
            "critical_reasons": [],
            "signals_count": 2,
        },
        "config": daily_selection.load_daily_selection_config(),
    }


def test_strength_score_prefers_fast_planet_when_other_factors_match() -> None:
    fast = _raw_event(
        "evt_fast",
        transit_body="Moon",
        natal_point="Mercury",
        aspect="square",
        bucket="short",
        phase="exactish",
        orb_deg=0.4,
        house=3,
    )
    slow = _raw_event(
        "evt_slow",
        transit_body="Saturn",
        natal_point="Mercury",
        aspect="square",
        bucket="short",
        phase="exactish",
        orb_deg=0.4,
        house=3,
    )

    fast_score = daily_selection.compute_strength_score(fast, "2026-03-10", _context(fast))
    slow_score = daily_selection.compute_strength_score(slow, "2026-03-10", _context(slow))

    assert fast_score > slow_score


def test_strength_score_preserves_exact_applying_separating_order() -> None:
    exact = _raw_event(
        "evt_exact",
        transit_body="Mars",
        natal_point="Sun",
        aspect="conjunction",
        bucket="short",
        phase="exact",
        orb_deg=0.2,
        house=1,
        exact_in_days=0,
    )
    applying = _raw_event(
        "evt_applying",
        transit_body="Mars",
        natal_point="Sun",
        aspect="conjunction",
        bucket="short",
        phase="applying",
        orb_deg=0.2,
        house=1,
        exact_in_days=1,
    )
    separating = _raw_event(
        "evt_separating",
        transit_body="Mars",
        natal_point="Sun",
        aspect="conjunction",
        bucket="short",
        phase="separating",
        orb_deg=0.2,
        house=1,
        exact_in_days=3,
    )

    assert daily_selection.compute_strength_score(exact, "2026-03-10", _context(exact)) > daily_selection.compute_strength_score(
        applying,
        "2026-03-10",
        _context(applying),
    )
    assert daily_selection.compute_strength_score(applying, "2026-03-10", _context(applying)) > daily_selection.compute_strength_score(
        separating,
        "2026-03-10",
        _context(separating),
    )


def test_strength_score_applies_lunation_family_boost() -> None:
    base = _raw_event(
        "evt_base",
        transit_body="Sun",
        natal_point="Moon",
        aspect="conjunction",
        bucket="long",
        phase="exactish",
        orb_deg=0.3,
        house=4,
    )
    lunation = dict(base)
    lunation["event_id"] = "evt_lunation_boost"
    lunation["event_family"] = "lunation_trigger"
    lunation["event_subtype"] = "new_moon"

    assert daily_selection.compute_strength_score(lunation, "2026-03-10", _context(lunation)) > daily_selection.compute_strength_score(
        base,
        "2026-03-10",
        _context(base),
    )


def test_today_score_prefers_selected_date_proximity_and_calendar_salience() -> None:
    near_event = _raw_event(
        "evt_near",
        transit_body="Mercury",
        natal_point="Sun",
        aspect="opposition",
        bucket="short",
        phase="exactish",
        orb_deg=0.2,
        house=3,
    )
    far_event = dict(near_event)
    far_event["event_id"] = "evt_far"
    far_event["timing"] = {
        "peak_date_utc": "2026-03-18T09:00:00+00:00",
        "entry_date_utc": "2026-03-17T09:00:00+00:00",
    }
    near_context = _context(near_event, labels=["mind"], top_event_ids=["evt_near"])
    far_context = _context(far_event, labels=["mind"], top_event_ids=[])

    assert daily_selection.compute_today_score(near_event, "2026-03-10", near_context) > daily_selection.compute_today_score(
        far_event,
        "2026-03-10",
        far_context,
    )


def test_narrative_score_prefers_clear_house_and_guidance() -> None:
    clear = _raw_event(
        "evt_clear",
        transit_body="Mercury",
        natal_point="Sun",
        aspect="opposition",
        bucket="short",
        phase="exactish",
        orb_deg=0.2,
        house=3,
    )
    vague = _raw_event(
        "evt_vague",
        transit_body="Neptune",
        natal_point="Sun",
        aspect="sextile",
        bucket="long",
        phase="separating",
        orb_deg=2.8,
        house=12,
        exact_in_days=3,
    )

    assert daily_selection.compute_narrative_score(clear, "2026-03-10", _context(clear)) > daily_selection.compute_narrative_score(
        vague,
        "2026-03-10",
        _context(vague),
    )


def test_delta_salience_prefers_peak_today_event() -> None:
    peak_today = _raw_event(
        "evt_peak_today",
        transit_body="Mercury",
        natal_point="Sun",
        aspect="opposition",
        bucket="short",
        phase="exact",
        orb_deg=0.2,
        house=3,
        exact_in_days=0,
    )
    peak_today["timing"] = {
        "peak_date_utc": "2026-03-10T09:00:00+00:00",
        "entry_date_utc": "2026-03-09T09:00:00+00:00",
    }
    far_flat = _raw_event(
        "evt_far_flat",
        transit_body="Mercury",
        natal_point="Sun",
        aspect="opposition",
        bucket="long",
        phase="separating",
        orb_deg=1.9,
        house=3,
        exact_in_days=4,
    )
    far_flat["timing"] = {
        "peak_date_utc": "2026-03-16T09:00:00+00:00",
        "entry_date_utc": "2026-03-02T09:00:00+00:00",
        "exit_date_utc": "2026-03-18T09:00:00+00:00",
    }

    assert daily_selection.compute_delta_salience_score(
        peak_today,
        "2026-03-10",
        _context(peak_today),
    ) > daily_selection.compute_delta_salience_score(
        far_flat,
        "2026-03-10",
        _context(far_flat),
    )


def test_experience_clustering_collapses_similar_rows() -> None:
    evt_a = _raw_event(
        "evt_cluster_a",
        transit_body="Mercury",
        natal_point="Sun",
        aspect="opposition",
        bucket="short",
        phase="exactish",
        orb_deg=0.3,
        house=3,
    )
    evt_b = _raw_event(
        "evt_cluster_b",
        transit_body="Mercury",
        natal_point="Moon",
        aspect="opposition",
        bucket="short",
        phase="applying",
        orb_deg=0.5,
        house=3,
    )
    evt_c = _raw_event(
        "evt_distinct",
        transit_body="Venus",
        natal_point="MC",
        aspect="trine",
        bucket="short",
        phase="exactish",
        orb_deg=0.4,
        house=10,
    )

    selection = daily_selection.select_daily_and_period_event_cards(
        raw_events=[evt_a, evt_b, evt_c],
        event_cards=[_materialized_card(evt_a), _materialized_card(evt_b), _materialized_card(evt_c)],
        selected_date="2026-03-10",
        selected_day_context={"labels": ["mind", "career"], "top_event_ids": ["evt_cluster_a"]},
        natal=None,
        event_v2_by_id={},
    )

    clusters = selection["daily_selection"]["selection_v3"]["experience_clusters"]
    assert any(cluster["cluster_size"] == 2 for cluster in clusters)
    assert any((card.get("cluster_size") or 0) >= 2 for card in selection["daily_event_cards"])


def test_selection_exposes_selection_v3_meta_and_chapter_roles() -> None:
    event = _raw_event(
        "evt_structural",
        transit_body="Saturn",
        natal_point="MC",
        aspect="conjunction",
        bucket="long",
        phase="exactish",
        orb_deg=0.4,
        house=10,
        exact_in_days=0,
    )
    selection = daily_selection.select_daily_and_period_event_cards(
        raw_events=[event],
        event_cards=[_materialized_card(event)],
        selected_date="2026-03-10",
        selected_day_context={"labels": ["career"], "top_event_ids": ["evt_structural"]},
        natal=None,
        event_v2_by_id={
            "evt_structural": {
                "event_family": "station_event",
                "importance_tier": "high",
                "significance_score": 0.8,
                "lasting_change_score": 0.82,
                "chapter_opening": 0.44,
                "repeat_pass_count": 1,
                "is_structural": True,
            }
        },
    )

    selection_v3 = selection["daily_selection"]["selection_v3"]["feature_vectors"]["evt_structural"]
    assert selection_v3["meaning"]["house_domain"] == "career"
    assert selection_v3["chapter_role"]["role"] in {"builder", "peak", "opener"}
    assert selection["period_event_cards"][0]["chapter_role"]["role"] in {"builder", "peak", "opener"}
    assert "experience_clusters" in selection["daily_selection"]["selection_v3"]


def test_narrative_score_rewards_specific_actionable_copy() -> None:
    event = _raw_event(
        "evt_quality",
        transit_body="Mercury",
        natal_point="Sun",
        aspect="opposition",
        bucket="short",
        phase="exactish",
        orb_deg=0.2,
        house=3,
    )
    rich_preview = {
        "felt_line_tr": "Söylemek isteyip aynı anda geri çekilebilirsin bugün.",
        "why_it_feels_this_way_tr": "Zihin tarafında iki ayrı eğilim aynı anda çalışıyor.",
        "guidance_micro_tr": "İlk cümleyi hemen gönderme; niyetini netleştir.",
        "house_touchpoint_tr": "zihin ve iletişim",
        "aspect_mode": "polarity",
        "tone_face": "growth",
    }
    generic_preview = {
        "felt_line_tr": "Bugün biraz farklı hissedebilirsin.",
        "why_it_feels_this_way_tr": "Bazı etkiler seni zorlayabilir.",
        "guidance_micro_tr": "Acele etme.",
        "house_touchpoint_tr": "zihin ve iletişim",
        "aspect_mode": "polarity",
        "tone_face": "shadow",
    }

    rich_score = daily_selection.compute_narrative_score(
        event,
        "2026-03-10",
        {
            "config": daily_selection.load_daily_selection_config(),
            "card": _materialized_card(event),
            "preview": rich_preview,
        },
    )
    generic_score = daily_selection.compute_narrative_score(
        event,
        "2026-03-10",
        {
            "config": daily_selection.load_daily_selection_config(),
            "card": _materialized_card(event),
            "preview": generic_preview,
        },
    )

    assert rich_score > generic_score


def test_daily_selection_uses_personalization_tie_break() -> None:
    natal = {
        "bodies": [
            {"body": "Sun", "house": 10},
            {"body": "Moon", "house": 10},
            {"body": "Mercury", "house": 10},
            {"body": "Venus", "house": 7},
        ]
    }
    career = _raw_event(
        "evt_career_pref",
        transit_body="Mercury",
        natal_point="Sun",
        aspect="opposition",
        bucket="short",
        phase="exactish",
        orb_deg=0.4,
        house=10,
    )
    home = _raw_event(
        "evt_home_pref",
        transit_body="Mercury",
        natal_point="Sun",
        aspect="opposition",
        bucket="short",
        phase="exactish",
        orb_deg=0.4,
        house=4,
    )

    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[career, home],
        event_cards=[_materialized_card(career), _materialized_card(home)],
        selected_date="2026-03-10",
        selected_day_context={},
        natal=natal,
        event_v2_by_id={},
    )

    score_breakdown = result["daily_selection"]["score_breakdown"]
    assert score_breakdown["evt_career_pref"]["personalization_score"] > score_breakdown["evt_home_pref"]["personalization_score"]
    assert result["daily_event_cards"][0]["event_id"] == "evt_career_pref"


def test_selector_uses_raw_pool_not_only_period_cards(monkeypatch) -> None:
    raw_daily = _raw_event(
        "evt_daily",
        transit_body="Moon",
        natal_point="Mercury",
        aspect="square",
        bucket="short",
        phase="exactish",
        orb_deg=0.2,
        house=3,
    )
    raw_period = _raw_event(
        "evt_period",
        transit_body="Saturn",
        natal_point="Sun",
        aspect="trine",
        bucket="long",
        phase="applying",
        orb_deg=1.7,
        house=10,
    )
    monkeypatch.setattr(daily_selection, "build_event_card", lambda item, context=None: _materialized_card(dict(item)))

    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[raw_daily, raw_period],
        event_cards=[_materialized_card(raw_period)],
        selected_date="2026-03-10",
        selected_day_context={"top_event_ids": ["evt_daily"]},
        natal={},
        event_v2_by_id={},
    )

    assert result["daily_event_cards"][0]["event_id"] == "evt_daily"
    assert result["period_event_cards"][0]["event_id"] == "evt_period"
    assert result["daily_selection"]["used_period_fallback"] is False


def test_selector_can_promote_high_score_period_event_into_daily(monkeypatch) -> None:
    raw_period = _raw_event(
        "evt_high_period",
        transit_body="Moon",
        natal_point="ASC",
        aspect="opposition",
        bucket="long",
        phase="exact",
        orb_deg=0.1,
        house=1,
        exact_in_days=0,
    )
    monkeypatch.setattr(daily_selection, "build_event_card", lambda item, context=None: _materialized_card(dict(item)))

    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[raw_period],
        event_cards=[],
        selected_date="2026-03-10",
        selected_day_context={},
        natal={},
        event_v2_by_id={},
    )

    card = result["daily_event_cards"][0]
    assert card["event_id"] == "evt_high_period"
    assert card["horizon"] == "daily"
    assert card["is_period_derived"] is True
    assert result["daily_selection"]["used_period_fallback"] is False


def test_selector_prioritizes_explicit_lunation_boost(monkeypatch) -> None:
    lunation = _raw_event(
        "evt_lunation",
        transit_body="Sun",
        natal_point="Moon",
        aspect="conjunction",
        bucket="long",
        phase="exactish",
        orb_deg=0.3,
        house=4,
        event_family="lunation_trigger",
        event_subtype="full_moon",
        exact_in_days=0,
    )
    other = _raw_event(
        "evt_other",
        transit_body="Mars",
        natal_point="Mercury",
        aspect="square",
        bucket="short",
        phase="exactish",
        orb_deg=0.4,
        house=3,
    )
    monkeypatch.setattr(daily_selection, "build_event_card", lambda item, context=None: _materialized_card(dict(item)))

    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[other, lunation],
        event_cards=[],
        selected_date="2026-03-10",
        selected_day_context={},
        natal={},
        event_v2_by_id={},
    )

    assert result["daily_event_cards"][0]["event_id"] == "evt_lunation"


def test_rerank_penalizes_same_house_repetition(monkeypatch) -> None:
    a = _raw_event(
        "evt_a",
        transit_body="Moon",
        natal_point="Mercury",
        aspect="square",
        bucket="short",
        phase="exactish",
        orb_deg=0.2,
        house=3,
    )
    b = _raw_event(
        "evt_b",
        transit_body="Mars",
        natal_point="Sun",
        aspect="opposition",
        bucket="short",
        phase="separating",
        orb_deg=1.4,
        house=3,
        exact_in_days=3,
    )
    c = _raw_event(
        "evt_c",
        transit_body="Venus",
        natal_point="Moon",
        aspect="trine",
        bucket="short",
        phase="exact",
        orb_deg=0.1,
        house=7,
        exact_in_days=0,
    )
    monkeypatch.setattr(daily_selection, "build_event_card", lambda item, context=None: _materialized_card(dict(item)))

    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[a, b, c],
        event_cards=[],
        selected_date="2026-03-10",
        selected_day_context={},
        natal={},
        event_v2_by_id={},
    )

    ids = [card["event_id"] for card in result["daily_event_cards"]]
    assert "evt_a" in ids
    assert "evt_c" in ids


def test_rerank_penalizes_same_aspect_mode_repetition(monkeypatch) -> None:
    a = _raw_event(
        "evt_mode_a",
        transit_body="Moon",
        natal_point="Mercury",
        aspect="square",
        bucket="short",
        phase="exactish",
        orb_deg=0.2,
        house=3,
    )
    b = _raw_event(
        "evt_mode_b",
        transit_body="Mars",
        natal_point="Sun",
        aspect="square",
        bucket="short",
        phase="exactish",
        orb_deg=0.22,
        house=1,
    )
    c = _raw_event(
        "evt_mode_c",
        transit_body="Venus",
        natal_point="Moon",
        aspect="sextile",
        bucket="short",
        phase="exactish",
        orb_deg=0.18,
        house=7,
    )
    monkeypatch.setattr(daily_selection, "build_event_card", lambda item, context=None: _materialized_card(dict(item)))

    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[a, b, c],
        event_cards=[],
        selected_date="2026-03-10",
        selected_day_context={},
        natal={},
        event_v2_by_id={},
    )

    aspect_modes = [card["aspect_mode"] for card in result["daily_event_cards"]]
    assert "friction" in aspect_modes
    assert "opening" in aspect_modes


def test_selector_balance_does_not_return_only_shadow_when_flow_option_is_close(monkeypatch) -> None:
    shadow = _raw_event(
        "evt_shadow",
        transit_body="Moon",
        natal_point="Mercury",
        aspect="square",
        bucket="short",
        phase="exactish",
        orb_deg=0.2,
        house=3,
    )
    flow = _raw_event(
        "evt_flow",
        transit_body="Venus",
        natal_point="Moon",
        aspect="trine",
        bucket="short",
        phase="exactish",
        orb_deg=0.24,
        house=7,
    )
    another_shadow = _raw_event(
        "evt_shadow_2",
        transit_body="Mars",
        natal_point="Sun",
        aspect="opposition",
        bucket="short",
        phase="exactish",
        orb_deg=0.23,
        house=1,
    )
    monkeypatch.setattr(daily_selection, "build_event_card", lambda item, context=None: _materialized_card(dict(item)))

    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[shadow, flow, another_shadow],
        event_cards=[],
        selected_date="2026-03-10",
        selected_day_context={},
        natal={},
        event_v2_by_id={},
    )

    tone_faces = [card["tone_face"] for card in result["daily_event_cards"]]
    assert "flow" in tone_faces or "growth" in tone_faces


def test_fallback_prefers_higher_narrative_quality_when_no_true_daily_candidate(monkeypatch) -> None:
    config = dict(daily_selection.load_daily_selection_config())
    thresholds = dict(config.get("thresholds") or {})
    thresholds["high_score_candidate_min"] = 1.5
    config["thresholds"] = thresholds
    monkeypatch.setattr(daily_selection, "load_daily_selection_config", lambda: config)

    weak_period = _raw_event(
        "evt_weak_period",
        transit_body="Neptune",
        natal_point="Sun",
        aspect="sextile",
        bucket="long",
        phase="separating",
        orb_deg=2.9,
        house=12,
        exact_in_days=4,
    )
    strong_narrative_period = _raw_event(
        "evt_story_period",
        transit_body="Mercury",
        natal_point="Sun",
        aspect="opposition",
        bucket="long",
        phase="separating",
        orb_deg=1.6,
        house=3,
        exact_in_days=4,
    )
    strong_narrative_period["timing"] = {
        "peak_date_utc": "2026-03-14T09:00:00+00:00",
        "entry_date_utc": "2026-03-13T09:00:00+00:00",
    }
    monkeypatch.setattr(daily_selection, "build_event_card", lambda item, context=None: _materialized_card(dict(item)))

    result = daily_selection.select_daily_and_period_event_cards(
        raw_events=[weak_period, strong_narrative_period],
        event_cards=[],
        selected_date="2026-03-10",
        selected_day_context={},
        natal={},
        event_v2_by_id={},
    )

    assert result["daily_selection"]["used_period_fallback"] is True
    assert result["daily_event_cards"][0]["event_id"] == "evt_story_period"
