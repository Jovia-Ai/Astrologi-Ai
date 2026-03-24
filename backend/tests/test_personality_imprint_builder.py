from app.natal.personality_imprint import build_personality_imprint
from app.natal.personality_imprint.contracts import (
    PERSONALITY_IMPRINT_DOMINANT_LIBRARY_INDEX_TR,
)


def _chart() -> dict:
    return {
        "birth_datetime": "1996-12-28T07:10:00+02:00",
        "location": {"city": "Istanbul, TR"},
    }


def _planets() -> list[dict]:
    return [
        {"planet": "Sun", "sign": "Capricorn", "house": 10},
        {"planet": "Moon", "sign": "Leo", "house": 8},
        {"planet": "Mercury", "sign": "Capricorn", "house": 3},
        {"planet": "Venus", "sign": "Sagittarius", "house": 12},
        {"planet": "Uranus", "sign": "Aquarius", "house": 1},
        {"planet": "Saturn", "sign": "Aries", "house": 3},
        {"planet": "Jupiter", "sign": "Capricorn", "house": 9},
        {"planet": "Neptune", "sign": "Capricorn", "house": 1},
    ]


def _aspects() -> list[dict]:
    return [
        {"planet1": "Sun", "planet2": "Uranus", "type": "Conjunction", "orb": 1.2},
        {"planet1": "Moon", "planet2": "Saturn", "type": "Opposition", "orb": 0.6},
        {"planet1": "Sun", "planet2": "Jupiter", "type": "Trine", "orb": 3.4},
        {"planet1": "Venus", "planet2": "Neptune", "type": "Trine", "orb": 2.4},
    ]


def _natal_graph() -> dict:
    return {
        "importance": {
            "Sun": 0.88,
            "Moon": 0.91,
            "Mercury": 0.74,
            "Venus": 0.72,
            "Uranus": 0.82,
            "Saturn": 0.84,
            "Jupiter": 0.68,
            "Neptune": 0.7,
        }
    }


def _natal_graph_with_asc_ruler() -> dict:
    graph = _natal_graph()
    graph["house_rulers"] = {
        "1": {
            "cusp_sign": "Capricorn",
            "primary_ruler": "Saturn",
            "primary_ruler_pos": {"house": 3, "sign": "Aries"},
        }
    }
    return graph


def _v2_planets() -> list[dict]:
    return [
        {"planet": "Moon", "sign": "Cancer", "house": 4},
        {"planet": "Venus", "sign": "Libra", "house": 7},
        {"planet": "Uranus", "sign": "Aquarius", "house": 11},
        {"planet": "Mercury", "sign": "Pisces", "house": 1},
        {"planet": "Neptune", "sign": "Sagittarius", "house": 9},
    ]


def _v2_aspects() -> list[dict]:
    return [
        {"planet1": "Mercury", "planet2": "Neptune", "type": "Square", "orb": 0.8},
        {"planet1": "Venus", "planet2": "Uranus", "type": "Square", "orb": 1.1},
        {"planet1": "Moon", "planet2": "Venus", "type": "Conjunction", "orb": 2.2},
    ]


def _v2_natal_graph() -> dict:
    return {
        "importance": {
            "Moon": 0.74,
            "Venus": 0.88,
            "Uranus": 0.61,
            "Mercury": 0.93,
            "Neptune": 0.57,
        }
    }


def _v3_planets() -> list[dict]:
    return [
        {"planet": "Mars", "sign": "Aquarius", "house": 1},
        {"planet": "Uranus", "sign": "Aquarius", "house": 1},
        {"planet": "Moon", "sign": "Aries", "house": 6},
    ]


def _v3_aspects() -> list[dict]:
    return [
        {"planet1": "Mars", "planet2": "Uranus", "type": "Conjunction", "orb": 0.9},
    ]


def _v3_natal_graph() -> dict:
    return {
        "importance": {
            "Mars": 0.95,
            "Uranus": 0.83,
            "Moon": 0.42,
        }
    }


def test_personality_imprint_selects_top_entries_deterministically() -> None:
    first = build_personality_imprint(
        planets=_planets(),
        aspects=_aspects(),
        natal_graph=_natal_graph(),
        include_debug=True,
    )
    second = build_personality_imprint(
        planets=_planets(),
        aspects=_aspects(),
        natal_graph=_natal_graph(),
        include_debug=True,
    )

    assert first == second
    assert first["engine_version"] == "personality_imprint_v1"
    assert first["render_shape"]["headline"] == "Kişilik İmzası"
    assert first["render_shape"]["subfields"] == ["aura", "trait", "drive"]
    assert first["render_shape"]["optional_subfield"] == "shadow"

    entries = first["entries"]
    assert [entry["key"] for entry in entries] == [
        "moon_opposite_saturn",
        "sun_conj_uranus",
        "sun_house_10",
        "moon_house_8",
    ]
    assert {"venus_house_12", "venus_trine_neptune", "sun_trine_jupiter"}.issubset(
        {entry["key"] for entry in first["extra_entries"]}
    )
    assert len(entries) == 4
    assert all(entry["aura"] for entry in entries)
    assert all(entry["trait"] for entry in entries)
    assert all(entry["drive"] for entry in entries)
    assert all(entry["shadow"] for entry in entries)

    debug = first["selection_debug"]
    assert debug["selected_keys"] == [entry["key"] for entry in entries]
    assert len(debug["house_candidates"]) >= 4
    assert len(debug["aspect_candidates"]) >= 3


def test_personality_imprint_selects_v2_house_and_aspect_entries() -> None:
    payload = build_personality_imprint(
        planets=_v2_planets(),
        aspects=_v2_aspects(),
        natal_graph=_v2_natal_graph(),
        include_debug=True,
    )

    entries = payload["entries"]
    assert [entry["key"] for entry in entries] == [
        "moon_conj_venus",
        "moon_house_4",
        "mercury_square_neptune",
        "mercury_house_1",
    ]
    assert payload["library_version"] == "personality_imprint_library_tr_v6"
    assert [entry["support_keys"] for entry in entries] == [
        ["moon_cancer", "venus_libra"],
        ["moon_cancer"],
        ["mercury_pisces"],
        ["mercury_pisces"],
    ]
    assert [entry["key"] for entry in payload["extra_entries"]] == [
        "venus_square_uranus",
        "venus_house_7",
        "uranus_house_11",
    ]
    assert [entry["key"] for entry in payload["support_entries"]] == [
        "mercury_pisces",
        "moon_cancer",
        "venus_libra",
    ]
    assert payload["bundles"][0]["dominant_key"] == "moon_conj_venus"
    assert payload["bundles"][0]["support_keys"] == ["moon_cancer", "venus_libra"]
    assert {"moon_house_4", "venus_house_7", "mercury_house_1"}.issubset(
        {candidate["key"] for candidate in payload["selection_debug"]["house_candidates"]}
    )
    assert {"moon_conj_venus", "mercury_square_neptune", "venus_square_uranus"}.issubset(
        {candidate["key"] for candidate in payload["selection_debug"]["aspect_candidates"]}
    )
    assert {"moon_cancer", "venus_libra", "mercury_pisces"}.issubset(
        {candidate["key"] for candidate in payload["selection_debug"]["sign_candidates"]}
    )


def test_personality_imprint_uses_sign_support_as_bundle_layer() -> None:
    payload = build_personality_imprint(
        planets=_v3_planets(),
        aspects=_v3_aspects(),
        natal_graph=_v3_natal_graph(),
        include_debug=True,
    )

    assert [entry["key"] for entry in payload["entries"]] == [
        "mars_conj_uranus",
        "mars_house_1",
        "uranus_house_1",
    ]
    assert [entry["key"] for entry in payload["extra_entries"]] == []
    assert [entry["key"] for entry in payload["support_entries"]] == ["mars_aquarius"]

    bundle_map = {bundle["dominant_key"]: bundle["support_keys"] for bundle in payload["bundles"]}
    assert bundle_map["mars_conj_uranus"] == ["mars_aquarius"]
    assert bundle_map["mars_house_1"] == ["mars_aquarius"]
    assert bundle_map["uranus_house_1"] == []
    assert "mars_aquarius" not in [entry["key"] for entry in payload["entries"]]
    assert {"mars_aquarius", "moon_aries"}.issubset(
        {candidate["key"] for candidate in payload["selection_debug"]["sign_candidates"]}
    )


def test_personality_imprint_adds_solar_jupiter_saturn_sign_support_and_asc_ruler_tone() -> None:
    payload = build_personality_imprint(
        planets=_planets(),
        aspects=_aspects(),
        natal_graph=_natal_graph_with_asc_ruler(),
        include_debug=True,
    )

    support_entries = {entry["key"]: entry for entry in payload["support_entries"]}
    support_map = {bundle["dominant_key"]: bundle["support_keys"] for bundle in payload["bundles"]}
    debug = payload["selection_debug"]

    assert {"sun_capricorn", "saturn_aries", "asc_ruler_saturn"}.issubset(support_entries.keys())
    assert support_entries["asc_ruler_saturn"]["kind"] == "asc_ruler_tone"
    assert support_map["moon_opposite_saturn"] == ["moon_leo", "saturn_aries", "asc_ruler_saturn"]
    assert support_map["sun_conj_uranus"] == ["sun_capricorn", "asc_ruler_saturn"]
    assert support_map["sun_house_10"] == ["sun_capricorn", "asc_ruler_saturn"]
    assert {"saturn_house_3", "mercury_house_3", "venus_trine_neptune", "sun_trine_jupiter"}.issubset(
        {entry["key"] for entry in payload["extra_entries"]}
    )
    assert {"sun_capricorn", "jupiter_capricorn", "saturn_aries"}.issubset(
        {candidate["key"] for candidate in debug["sign_candidates"]}
    )
    assert [candidate["key"] for candidate in debug["asc_ruler_candidates"]] == ["asc_ruler_saturn"]


def test_priority_house_batch_is_available_with_extended_fields() -> None:
    planets = (
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    )
    houses = (1, 7, 8, 10, 12)
    expected_keys = {f"{planet}_house_{house}" for house in houses for planet in planets}

    assert expected_keys.issubset(PERSONALITY_IMPRINT_DOMINANT_LIBRARY_INDEX_TR.keys())

    venus_house_12 = PERSONALITY_IMPRINT_DOMINANT_LIBRARY_INDEX_TR["venus_house_12"]
    assert venus_house_12["background_hint"] == "Yakınlık alanında temkinli olmayı erken dönemde öğrenmiş olabilirsin."
    assert venus_house_12["gift"] == "Bu yerleşim sende çok ince bir sezgi, saf bir sadakat ve ruha dokunan bir sevgi yaratır."
    assert venus_house_12["tags"] == ["gizli", "ince", "ruhsal"]


def test_support_house_batch_is_available_and_preserves_existing_tags() -> None:
    planets = (
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    )
    houses = (2, 4, 5, 11)
    expected_keys = {f"{planet}_house_{house}" for house in houses for planet in planets}

    assert expected_keys.issubset(PERSONALITY_IMPRINT_DOMINANT_LIBRARY_INDEX_TR.keys())

    mercury_house_2 = PERSONALITY_IMPRINT_DOMINANT_LIBRARY_INDEX_TR["mercury_house_2"]
    assert mercury_house_2["gift"] == "Bu yerleşim sende yerinde karar, pratik akıl ve güven veren bir düşünce yapısı yaratır."
    assert mercury_house_2["tags"] == []

    venus_house_5 = PERSONALITY_IMPRINT_DOMINANT_LIBRARY_INDEX_TR["venus_house_5"]
    assert venus_house_5["aura"] == "Sende romantik, tatlı ve dikkat çeken bir çekim var."
    assert venus_house_5["tags"] == ["romantik", "çekici", "oyuncu"]

    saturn_house_11 = PERSONALITY_IMPRINT_DOMINANT_LIBRARY_INDEX_TR["saturn_house_11"]
    assert saturn_house_11["background_hint"] == (
        "Arkadaşlık ya da aidiyet alanında erken dönemde mesafe ya da hayal kırıklığı yaşamış olabilirsin."
    )
