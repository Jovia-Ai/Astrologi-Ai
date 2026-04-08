from app.natal.narrative.core_story_tr_natal import build_core_story_ui
from app.natal.natal_graph import build_natal_graph


def _sample_chart() -> dict:
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


def _sample_planets() -> list[dict]:
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
        {"planet": "North Node", "sign": "Libra", "house": 9},
    ]


def _sample_aspects() -> list[dict]:
    return [
        {"planet1": "Saturn", "planet2": "Ascendant", "aspect": "Square", "orb": 0.03},
        {"planet1": "Moon", "planet2": "Venus", "aspect": "Trine", "orb": 0.24},
        {"planet1": "Mars", "planet2": "Saturn", "aspect": "Opposition", "orb": 3.23},
    ]


def test_core_story_ui_is_deterministic_and_clamped() -> None:
    chart = _sample_chart()
    planets = _sample_planets()
    graph = build_natal_graph(chart_data=chart, planets=planets, aspects=_sample_aspects())

    first = build_core_story_ui(chart_data=chart, planets=planets, natal_graph=graph)
    second = build_core_story_ui(chart_data=chart, planets=planets, natal_graph=graph)

    assert first == second
    assert isinstance(first.get("headline"), str) and first.get("headline")
    assert isinstance(first.get("text"), str) and first.get("text")
    assert len(first["text"]) <= 520
    assert isinstance(first.get("drivers"), list)
    assert "İyi çalıştığında" in first["text"]
    assert "gölgesinde" in first["text"]
    assert any((item.get("key") or "") == "asc_ruler_sign" for item in first["drivers"])
