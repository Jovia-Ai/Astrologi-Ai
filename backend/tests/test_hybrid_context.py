from app.transit.narrative.hybrid_context import build_hybrid_event_context


def _natal_snapshot() -> dict:
    return {
        "bodies": [
            {"body": "Sun", "lon": 276.75, "sign": "Capricorn", "house": 1},
            {"body": "Moon", "lon": 133.94, "sign": "Leo", "house": 8},
            {"body": "Mercury", "lon": 287.36, "sign": "Capricorn", "house": 1, "rx": True},
            {"body": "Venus", "lon": 253.71, "sign": "Sagittarius", "house": 12},
            {"body": "Mars", "lon": 177.93, "sign": "Virgo", "house": 9},
            {"body": "Jupiter", "lon": 294.29, "sign": "Capricorn", "house": 1},
            {"body": "Saturn", "lon": 1.15, "sign": "Aries", "house": 3},
            {"body": "Uranus", "lon": 303.06, "sign": "Aquarius", "house": 1},
            {"body": "Neptune", "lon": 296.69, "sign": "Capricorn", "house": 1},
            {"body": "Pluto", "lon": 244.25, "sign": "Sagittarius", "house": 11},
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


def _event() -> dict:
    return {
        "event_id": "evt_uranus_mars",
        "transit_body": "Uranus",
        "natal_point": "Mars",
        "aspect": "trine",
        "phase": "applying",
        "bucket": "long",
        "houses": {"transit_in_natal_house": 9},
        "ranking": {"tier": "main", "weight": 1.3},
    }


def test_hybrid_context_target_house_matches_snapshot() -> None:
    out = build_hybrid_event_context(_event(), _natal_snapshot(), natal_promise={"score": 0.8})
    target = out["natal_context_pack"]["target"]
    assert target["planet"] == "Mars"
    assert target["house"] == 9
    assert target["sign_tr"] == "Başak"
    rulership_houses = out["natal_context_pack"]["rulership_houses"]
    houses = [entry["house"] for entry in rulership_houses]
    assert 4 in houses
    assert 11 in houses


def test_hybrid_connected_points_deterministic() -> None:
    natal = _natal_snapshot()
    event = _event()
    a = build_hybrid_event_context(event, natal, natal_promise={"score": 0.8})
    b = build_hybrid_event_context(event, natal, natal_promise={"score": 0.8})
    assert a["connected_points"] == b["connected_points"]


def test_hybrid_connected_points_whitelist() -> None:
    out = build_hybrid_event_context(_event(), _natal_snapshot(), natal_promise={"score": 0.8})
    text = " ".join(str(item.get("value") or "") for item in out["connected_points"]).lower()
    for banned in ("south node", "north node", "lilith", "vertex", "fortune", "chiron"):
        assert banned not in text


def test_angle_target_keeps_angle_and_adds_angle_ruler() -> None:
    event = {
        "event_id": "evt_neptune_asc",
        "transit_body": "Neptune",
        "natal_point": "ASC",
        "aspect": "square",
        "phase": "applying",
        "bucket": "long",
        "orb_deg": 0.9,
        "houses": {"transit_in_natal_house": 3},
        "ranking": {"tier": "main", "weight": 1.2},
    }
    out = build_hybrid_event_context(event, _natal_snapshot(), natal_promise={"score": 0.7})
    target = out["natal_context_pack"]["target"]
    assert target["planet"] == "ASC"
    assert target["house"] == 1
    angle_rulers = [p for p in out["connected_points"] if p.get("kind") == "angle_ruler"]
    assert angle_rulers
    assert angle_rulers[0]["value"] == "Saturn"
    angle_ctx = out.get("derived_context", {}).get("angle", {})
    assert angle_ctx.get("name") == "ASC"
    assert angle_ctx.get("sign") == "Capricorn"
    assert angle_ctx.get("ruler") == "Saturn"
    assert angle_ctx.get("ruler_house") == 3
    assert angle_ctx.get("ruler_sign") == "Aries"
