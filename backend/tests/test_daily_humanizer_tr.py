from app.transit.narrative.daily_humanizer_tr import generate_daily_from_event


def _event(*, aspect: str, house: int, transit_body: str = "Mercury") -> dict:
    horizon = "daily" if aspect in {"square", "opposition"} else "period"
    return {
        "event_id": f"evt_{aspect}_{house}",
        "transit_body": transit_body,
        "natal_point": "Sun",
        "aspect": aspect,
        "bucket": "short" if horizon == "daily" else "long",
        "phase": "exactish",
        "horizon": horizon,
        "derived_context": {"natal_target": {"house": house}},
        "scene": {"outcome_house": house, "start_house": house},
        "natal_promise": {"score": 0.74},
    }


def test_square_and_opposition_use_distinct_template_families() -> None:
    square = generate_daily_from_event(_event(aspect="square", house=3), score=0.81)
    opposition = generate_daily_from_event(_event(aspect="opposition", house=3), score=0.81)

    assert square["aspect_mode"] == "friction"
    assert opposition["aspect_mode"] == "polarity"
    assert square["felt_line_tr"] != opposition["felt_line_tr"]
    assert square["why_it_feels_this_way_tr"] != opposition["why_it_feels_this_way_tr"]
    assert "zihnin ve konuşma halin" == square["house_touchpoint_tr"]
    assert "zihnin ve konuşma halin" == opposition["house_touchpoint_tr"]


def test_trine_and_sextile_use_distinct_template_families() -> None:
    trine = generate_daily_from_event(_event(aspect="trine", house=10, transit_body="Sun"), score=0.77)
    sextile = generate_daily_from_event(_event(aspect="sextile", house=10, transit_body="Sun"), score=0.77)

    assert trine["aspect_mode"] == "flow"
    assert sextile["aspect_mode"] == "opening"
    assert trine["felt_line_tr"] != sextile["felt_line_tr"]
    assert trine["why_it_feels_this_way_tr"] != sextile["why_it_feels_this_way_tr"]
    assert "yönün ve görünürlüğün" == trine["house_touchpoint_tr"]


def test_house_anchor_visibility_and_period_fallback_flags() -> None:
    out = generate_daily_from_event(
        _event(aspect="conjunction", house=7, transit_body="Venus"),
        score=0.66,
        is_period_derived=True,
        force_daily_horizon=True,
    )
    merged = " ".join(
        [
            out["felt_line_tr"].lower(),
            out["why_it_feels_this_way_tr"].lower(),
            out["guidance_micro_tr"].lower(),
        ]
    )

    assert out["horizon"] == "daily"
    assert out["source_horizon"] == "period"
    assert out["today_facing_fallback"] is True
    assert out["is_period_derived"] is True
    assert any(token in merged for token in ("karşı", "arada", "denge", "mesafe"))
    for banned in ("mercury", "venus", "square", "trine", "sextile", "opposition", "conjunction", "transit", "orb"):
        assert banned not in merged


def test_relationship_lens_uses_venus_affinity_before_house_only_language() -> None:
    out = generate_daily_from_event(
        {
            "event_id": "evt_rel_venus_12",
            "transit_body": "Sun",
            "natal_point": "Venus",
            "aspect": "trine",
            "bucket": "medium",
            "phase": "exactish",
            "horizon": "period",
            "houses": {
                "transit_in_natal_house": 3,
                "natal_point_house": 12,
            },
            "scene": {"start_house": 3, "outcome_house": 12},
            "derived_context": {
                "natal_target": {
                    "house": 12,
                    "rulership_houses": [5, 10],
                }
            },
            "natal_promise": {"score": 0.9},
        },
        score=0.88,
        lens="relationship",
    )

    assert out["semantic_core"]["target_affinity"] == "relationships"
    assert out["semantic_core"]["target_house_domain"] == "inner"
    assert out["semantic_core"]["source_house_domain"] == "mind"
    assert out["domain_scores"]["relationships"] > out["domain_scores"]["inner"]
    assert out["lens_projection"]["primary_domain"] == "relationships"
    assert "Yakınlık" in out["felt_line_tr"]
    assert "İçe çekildiğin yerde" not in out["felt_line_tr"]
