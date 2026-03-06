from app.transit.narrative.coverage import build_period_coverage


def _events_subset() -> list[dict]:
    return [
        {
            "event_id": "evt_neptune_asc",
            "scope": "transit_to_angles",
            "transit_body": "Neptune",
            "aspect": "square",
            "natal_point": "ASC",
            "strength": 0.97,
            "orb_deg": 0.17,
            "phase": "exactish",
            "bucket": "long",
            "tags": ["self", "pressure", "friction"],
            "houses": {"transit_in_natal_house": 3, "natal_point_house": None},
        },
        {
            "event_id": "evt_neptune_dsc",
            "scope": "transit_to_angles",
            "transit_body": "Neptune",
            "aspect": "square",
            "natal_point": "DSC",
            "strength": 0.96,
            "orb_deg": 0.17,
            "phase": "exactish",
            "bucket": "long",
            "tags": ["relationships", "pressure", "friction"],
            "houses": {"transit_in_natal_house": 3, "natal_point_house": None},
        },
        {
            "event_id": "evt_uranus_mars",
            "scope": "transit_to_natal",
            "transit_body": "Uranus",
            "aspect": "trine",
            "natal_point": "Mars",
            "strength": 0.96,
            "orb_deg": 0.21,
            "phase": "applying",
            "bucket": "long",
            "tags": ["career", "support", "flow"],
            "houses": {"transit_in_natal_house": 5, "natal_point_house": 9},
        },
        {
            "event_id": "evt_moon_chiron",
            "scope": "transit_to_natal",
            "transit_body": "Moon",
            "aspect": "square",
            "natal_point": "Chiron",
            "strength": 0.91,
            "orb_deg": 0.53,
            "phase": "separating",
            "bucket": "short",
            "tags": ["career", "pressure", "friction"],
            "houses": {"transit_in_natal_house": 7, "natal_point_house": 10},
        },
        {
            "event_id": "evt_venus_mars",
            "scope": "transit_to_natal",
            "transit_body": "Venus",
            "aspect": "opposition",
            "natal_point": "Mars",
            "strength": 0.08,
            "orb_deg": 5.5,
            "phase": "applying",
            "bucket": "medium",
            "tags": ["career", "pressure", "tension"],
            "houses": {"transit_in_natal_house": 3, "natal_point_house": 9},
        },
    ]


def test_coverage_counts_and_domains() -> None:
    events = _events_subset()
    selected_ids = {"evt_neptune_asc", "evt_uranus_mars", "evt_moon_chiron"}
    coverage = build_period_coverage(events, selected_ids, now_date="2026-02-28", tz="Europe/Istanbul")

    assert coverage["counts"]["total"] == 5
    assert coverage["counts"]["long"] == 3
    assert coverage["counts"]["medium"] == 1
    assert coverage["counts"]["short"] == 1
    assert coverage["domain_coverage"]["identity"]["hits"] >= 1
    assert coverage["domain_coverage"]["relationships"]["hits"] >= 1
    assert coverage["domain_coverage"]["mind"]["hits"] >= 1


def test_coverage_skipped_reasons_present() -> None:
    events = _events_subset()
    selected_ids = {"evt_neptune_asc", "evt_uranus_mars"}
    coverage = build_period_coverage(events, selected_ids, now_date="2026-02-28", tz="Europe/Istanbul")
    skipped = coverage["skipped_due_to_dedup"]
    assert isinstance(skipped, list)
    assert skipped
    assert any(entry.get("reason") for entry in skipped)
