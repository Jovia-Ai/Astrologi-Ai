from app.transit.narrative.selection import select_event_ids


def _natal_snapshot() -> dict:
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


def _events() -> list[dict]:
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
            "event_id": "evt_neptune_dsc",
            "scope": "transit_to_angles",
            "transit_body": "Neptune",
            "aspect": "square",
            "natal_point": "DSC",
            "strength": 0.971,
            "orb_deg": 0.20,
            "phase": "exactish",
            "bucket": "long",
            "tags": ["relationships", "pressure", "friction"],
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
        {
            "event_id": "evt_jupiter_mercury",
            "scope": "transit_to_natal",
            "transit_body": "Jupiter",
            "aspect": "opposition",
            "natal_point": "Mercury",
            "strength": 0.65,
            "orb_deg": 2.09,
            "phase": "separating",
            "bucket": "medium",
            "tags": ["self", "pressure", "tension"],
            "houses": {"transit_in_natal_house": 7, "natal_point_house": 1},
            "polarity": "hard",
        },
        {
            "event_id": "evt_pluto_ic",
            "scope": "transit_to_angles",
            "transit_body": "Pluto",
            "aspect": "sextile",
            "natal_point": "IC",
            "strength": 0.72,
            "orb_deg": 0.95,
            "phase": "applying",
            "bucket": "long",
            "tags": ["home", "support", "opportunity"],
            "houses": {"transit_in_natal_house": 1, "natal_point_house": None},
            "polarity": "soft",
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
            "polarity": "hard",
        },
    ]


def test_selection_is_deterministic() -> None:
    events = _events()
    a, meta_a = select_event_ids(events, max_cards=5, natal=_natal_snapshot())
    b, meta_b = select_event_ids(events, max_cards=5, natal=_natal_snapshot())
    assert [x["event_id"] for x in a] == [x["event_id"] for x in b]
    assert meta_a["selected_ids"] == meta_b["selected_ids"]
    assert meta_a["cluster_keys"] == meta_b["cluster_keys"]
    assert meta_a["salience"] == meta_b["salience"]


def test_selection_constraints_and_diversity() -> None:
    selected, meta = select_event_ids(_events(), max_cards=5, natal=_natal_snapshot())
    assert len(selected) <= 5
    signatures = {
        (e["transit_body"].lower(), e["aspect"].lower(), e["natal_point"].upper())
        for e in selected
    }
    assert len(signatures) == len(selected)
    domains = set()
    for item in selected:
        scope = item.get("scope")
        point = str(item.get("natal_point") or "").upper()
        if scope == "transit_to_angles" and point == "ASC":
            domains.add("identity")
        elif scope == "transit_to_angles" and point == "DSC":
            domains.add("relationships")
        elif item.get("houses", {}).get("natal_point_house") in {3, 9}:
            domains.add("mind")
        elif item.get("houses", {}).get("natal_point_house") in {10, 11}:
            domains.add("career")
        elif scope == "transit_to_angles" and point == "IC":
            domains.add("home")
    assert len(domains) >= 3
    assert len(set(meta.get("cluster_keys", {}).values())) == len(selected)


def test_selection_includes_uranus_trine_mars_when_present() -> None:
    selected, _meta = select_event_ids(_events(), max_cards=5, natal=_natal_snapshot())
    ids = {item["event_id"] for item in selected}
    assert "evt_uranus_mars" in ids


def test_selection_coverage_guarantees() -> None:
    selected, _meta = select_event_ids(_events(), max_cards=5, natal=_natal_snapshot())
    assert any(str(item.get("scope") or "") == "transit_to_angles" for item in selected)
    assert any(
        (item.get("houses", {}).get("natal_point_house") in {3, 9})
        for item in selected
        if isinstance(item.get("houses"), dict)
    )
    assert any(str(item.get("transit_body") or "").lower() in {"uranus", "pluto"} for item in selected)


def test_selection_excludes_blocked_public_points() -> None:
    events = _events() + [
        {
            "event_id": "evt_fortune_blocked",
            "scope": "transit_to_natal",
            "transit_body": "Fortune",
            "aspect": "square",
            "natal_point": "Sun",
            "strength": 0.99,
            "orb_deg": 0.2,
            "phase": "applying",
            "bucket": "long",
            "tags": ["self", "pressure"],
            "houses": {"transit_in_natal_house": 1, "natal_point_house": 1},
            "polarity": "hard",
        },
        {
            "event_id": "evt_vertex_blocked",
            "scope": "transit_to_natal",
            "transit_body": "Saturn",
            "aspect": "square",
            "natal_point": "Vertex",
            "strength": 0.99,
            "orb_deg": 0.2,
            "phase": "applying",
            "bucket": "long",
            "tags": ["self", "pressure"],
            "houses": {"transit_in_natal_house": 1, "natal_point_house": 1},
            "polarity": "hard",
        },
    ]
    selected, _meta = select_event_ids(events, max_cards=5, natal=_natal_snapshot())
    ids = {item["event_id"] for item in selected}
    assert "evt_fortune_blocked" not in ids
    assert "evt_vertex_blocked" not in ids
