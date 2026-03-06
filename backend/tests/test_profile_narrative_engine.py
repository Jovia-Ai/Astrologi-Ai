from app.natal.narrative.profile_narrative_engine import build_profile_narrative
from app.natal.narrative.signature_engine import normalize_facts
from app.natal.natal_graph import build_natal_graph


def _chart_a() -> dict:
    return {
        "birth_datetime": "1996-12-28T07:10:00+02:00",
        "location": {"city": "Istanbul, TR"},
        "house_positions": {
            "1": {"sign": "Capricorn"},
            "2": {"sign": "Aquarius"},
            "3": {"sign": "Pisces"},
            "4": {"sign": "Aries"},
            "5": {"sign": "Taurus"},
            "6": {"sign": "Gemini"},
            "7": {"sign": "Cancer"},
            "8": {"sign": "Leo"},
            "9": {"sign": "Virgo"},
            "10": {"sign": "Libra"},
            "11": {"sign": "Scorpio"},
            "12": {"sign": "Sagittarius"},
        },
        "angles": {
            "ascendant_sign": "Capricorn",
            "midheaven_sign": "Libra",
        },
    }


def _planets_a() -> list[dict]:
    return [
        {"planet": "Sun", "sign": "Capricorn", "house": 1},
        {"planet": "Moon", "sign": "Leo", "house": 8},
        {"planet": "Mercury", "sign": "Capricorn", "house": 1},
        {"planet": "Venus", "sign": "Sagittarius", "house": 12},
        {"planet": "Mars", "sign": "Virgo", "house": 9},
        {"planet": "Jupiter", "sign": "Capricorn", "house": 1},
        {"planet": "Saturn", "sign": "Aries", "house": 3},
        {"planet": "Uranus", "sign": "Aquarius", "house": 1},
        {"planet": "Neptune", "sign": "Capricorn", "house": 1},
        {"planet": "Pluto", "sign": "Sagittarius", "house": 11},
        {"planet": "Chiron", "sign": "Libra", "house": 10},
        {"planet": "Fortune", "sign": "Taurus", "house": 5},
        {"planet": "Ascendant", "sign": "Capricorn", "house": 1, "is_point": True},
        {"planet": "Midheaven", "sign": "Libra", "house": 10, "is_point": True},
    ]


def _aspects_a() -> list[dict]:
    return [
        {"planet1": "Sun", "planet2": "Saturn", "aspect": "Square", "orb": 5.59},
        {"planet1": "Moon", "planet2": "Venus", "aspect": "Trine", "orb": 0.24},
        {"planet1": "Mars", "planet2": "Saturn", "aspect": "Opposition", "orb": 3.23},
        {"planet1": "Mars", "planet2": "Jupiter", "aspect": "Trine", "orb": 3.63},
        {"planet1": "Mars", "planet2": "Neptune", "aspect": "Trine", "orb": 1.24},
        {"planet1": "Jupiter", "planet2": "Neptune", "aspect": "Conjunction", "orb": 2.39},
        {"planet1": "Jupiter", "planet2": "Midheaven", "aspect": "Square", "orb": 0.99},
        {"planet1": "Neptune", "planet2": "Midheaven", "aspect": "Square", "orb": 1.4},
    ]


def _chart_b() -> dict:
    return {
        "birth_datetime": "1993-06-10T19:45:00+03:00",
        "location": {"city": "Ankara, TR"},
        "house_positions": {
            "1": {"sign": "Leo"},
            "2": {"sign": "Virgo"},
            "3": {"sign": "Libra"},
            "4": {"sign": "Scorpio"},
            "5": {"sign": "Sagittarius"},
            "6": {"sign": "Capricorn"},
            "7": {"sign": "Aquarius"},
            "8": {"sign": "Pisces"},
            "9": {"sign": "Aries"},
            "10": {"sign": "Taurus"},
            "11": {"sign": "Gemini"},
            "12": {"sign": "Cancer"},
        },
        "angles": {
            "ascendant_sign": "Leo",
            "midheaven_sign": "Taurus",
        },
    }


def _planets_b() -> list[dict]:
    return [
        {"planet": "Sun", "sign": "Gemini", "house": 11},
        {"planet": "Moon", "sign": "Pisces", "house": 8},
        {"planet": "Mercury", "sign": "Gemini", "house": 11},
        {"planet": "Venus", "sign": "Cancer", "house": 12},
        {"planet": "Mars", "sign": "Leo", "house": 1},
        {"planet": "Jupiter", "sign": "Libra", "house": 3},
        {"planet": "Saturn", "sign": "Aquarius", "house": 7},
        {"planet": "Uranus", "sign": "Capricorn", "house": 6},
        {"planet": "Neptune", "sign": "Capricorn", "house": 6},
        {"planet": "Pluto", "sign": "Scorpio", "house": 4},
        {"planet": "Fortune", "sign": "Gemini", "house": 11},
        {"planet": "Ascendant", "sign": "Leo", "house": 1, "is_point": True},
        {"planet": "Midheaven", "sign": "Taurus", "house": 10, "is_point": True},
    ]


def _aspects_b() -> list[dict]:
    return [
        {"planet1": "Moon", "planet2": "Venus", "aspect": "Trine", "orb": 0.9},
        {"planet1": "Fortune", "planet2": "Jupiter", "aspect": "Trine", "orb": 1.2},
        {"planet1": "Mars", "planet2": "Ascendant", "aspect": "Conjunction", "orb": 2.0},
    ]


def _graph(chart: dict, planets: list[dict], aspects: list[dict]) -> dict:
    return build_natal_graph(chart_data=chart, planets=planets, aspects=aspects)


def _chart_c() -> dict:
    return {
        "birth_datetime": "1988-02-14T05:20:00+03:00",
        "location": {"city": "Izmir, TR"},
        "house_positions": {
            "1": {"sign": "Scorpio"},
            "2": {"sign": "Sagittarius"},
            "3": {"sign": "Capricorn"},
            "4": {"sign": "Aquarius"},
            "5": {"sign": "Pisces"},
            "6": {"sign": "Aries"},
            "7": {"sign": "Taurus"},
            "8": {"sign": "Gemini"},
            "9": {"sign": "Cancer"},
            "10": {"sign": "Leo"},
            "11": {"sign": "Virgo"},
            "12": {"sign": "Libra"},
        },
        "angles": {
            "ascendant_sign": "Scorpio",
            "midheaven_sign": "Leo",
        },
    }


def _planets_c() -> list[dict]:
    return [
        {"planet": "Sun", "sign": "Aquarius", "house": 4},
        {"planet": "Moon", "sign": "Aquarius", "house": 4},
        {"planet": "Mercury", "sign": "Capricorn", "house": 3, "retrograde": True},
        {"planet": "Venus", "sign": "Pisces", "house": 5},
        {"planet": "Mars", "sign": "Cancer", "house": 9},
        {"planet": "Jupiter", "sign": "Taurus", "house": 7},
        {"planet": "Saturn", "sign": "Capricorn", "house": 3},
        {"planet": "Uranus", "sign": "Sagittarius", "house": 2},
        {"planet": "Neptune", "sign": "Capricorn", "house": 3},
        {"planet": "Chiron", "sign": "Leo", "house": 10},
        {"planet": "Fortune", "sign": "Pisces", "house": 5},
        {"planet": "Ascendant", "sign": "Scorpio", "house": 1, "is_point": True},
        {"planet": "Midheaven", "sign": "Leo", "house": 10, "is_point": True},
    ]


def _aspects_c() -> list[dict]:
    return [
        {"planet1": "Mars", "planet2": "Neptune", "aspect": "Trine", "orb": 1.8},
        {"planet1": "Moon", "planet2": "Venus", "aspect": "Sextile", "orb": 1.5},
        {"planet1": "Saturn", "planet2": "Mercury", "aspect": "Conjunction", "orb": 1.1},
        {"planet1": "Fortune", "planet2": "Jupiter", "aspect": "Conjunction", "orb": 2.2},
    ]


def test_profile_narrative_is_deterministic_for_same_chart() -> None:
    chart = _chart_a()
    graph = _graph(chart, _planets_a(), _aspects_a())
    first = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")
    second = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")

    assert first["profile_public"] == second["profile_public"]
    assert first["profile_public"]["engine_version"] == "profile_narrative_v1"
    assert first["profile_public"]["blocks"]
    assert len(first["profile_public"]["blocks"]) == 7


def test_profile_narrative_debug_has_evidence_for_every_public_block() -> None:
    chart = _chart_a()
    graph = _graph(chart, _planets_a(), _aspects_a())
    payload = build_profile_narrative(chart, graph, include_debug=True, engine_override="signature")

    public_blocks = payload["profile_public"]["blocks"]
    debug_blocks = payload["profile_internal"]["blocks_debug"]
    assert len(public_blocks) == 7
    assert len(debug_blocks) == 7
    debug_by_id = {block["id"]: block for block in debug_blocks}

    for block in public_blocks:
        debug_block = debug_by_id[block["id"]]
        if not debug_block.get("fallback_reason"):
            assert len(debug_block["evidence"]) >= 2
        assert debug_block["engine"] == "signature"
        assert debug_block["template_id"]
        assert debug_block["template_variant_id"]
        assert debug_block["seed_material"]
        assert debug_block["selected_template_index"] in {0, 1}
        assert debug_block["primary_signature_id"]


def test_profile_narrative_seeds_and_bodies_change_across_different_charts() -> None:
    chart_a = _chart_a()
    graph_a = _graph(chart_a, _planets_a(), _aspects_a())
    chart_b = _chart_b()
    graph_b = _graph(chart_b, _planets_b(), _aspects_b())
    chart_c = _chart_c()
    graph_c = _graph(chart_c, _planets_c(), _aspects_c())

    facts_a = normalize_facts(chart_a, graph_a)
    facts_b = normalize_facts(chart_b, graph_b)
    facts_c = normalize_facts(chart_c, graph_c)
    payload_a = build_profile_narrative(chart_a, graph_a, include_debug=True, engine_override="signature")
    payload_b = build_profile_narrative(chart_b, graph_b, include_debug=True, engine_override="signature")
    payload_c = build_profile_narrative(chart_c, graph_c, include_debug=True, engine_override="signature")

    assert facts_a["seed"] != facts_b["seed"]
    assert facts_a["seed"] != facts_c["seed"]
    assert facts_b["seed"] != facts_c["seed"]
    bodies_a = {block["id"]: block["body"] for block in payload_a["profile_public"]["blocks"]}
    bodies_b = {block["id"]: block["body"] for block in payload_b["profile_public"]["blocks"]}
    bodies_c = {block["id"]: block["body"] for block in payload_c["profile_public"]["blocks"]}
    assert any(bodies_a.get(block_id) != bodies_b.get(block_id) for block_id in set(bodies_a) & set(bodies_b))
    assert any(bodies_a.get(block_id) != bodies_c.get(block_id) for block_id in set(bodies_a) & set(bodies_c))


def test_profile_narrative_legacy_override_keeps_schema() -> None:
    chart = _chart_b()
    graph = _graph(chart, _planets_b(), _aspects_b())
    payload = build_profile_narrative(chart, graph, include_debug=True, engine_override="legacy")

    blocks = payload["profile_public"]["blocks"]
    debug_blocks = payload["profile_internal"]["blocks_debug"]
    assert len(blocks) == 7
    assert len(debug_blocks) == 7
    assert all({"id", "headline", "teaser", "body", "chips"} <= set(block.keys()) for block in blocks)
    assert all(block.get("engine") == "legacy" for block in debug_blocks)
