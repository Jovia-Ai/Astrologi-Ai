from app.natal.natal_graph import build_natal_graph
from app.natal.supporting_threads_builder import build_supporting_threads


def _sample_chart() -> dict:
    return {
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


def test_build_natal_graph_generates_house_rulers_and_loop() -> None:
    graph = build_natal_graph(
        chart_data=_sample_chart(),
        planets=_sample_planets(),
        aspects=_sample_aspects(),
    )

    assert graph["house_rulers"]["1"]["primary_ruler"] == "Saturn"
    assert graph["house_rulers"]["2"]["co_ruler"] == "Uranus"
    signatures = [entry["signature"] for entry in graph["dominant_loops"]]
    assert "Saturn→Mars→Mercury" in signatures


def test_supporting_threads_builder_returns_ui_threads() -> None:
    chart = _sample_chart()
    graph = build_natal_graph(chart_data=chart, planets=_sample_planets(), aspects=_sample_aspects())
    threads = build_supporting_threads(chart_data=chart, planets=_sample_planets(), natal_graph=graph)

    assert threads
    ids = {t.get("id") for t in threads}
    assert "identity_mechanics" in ids
    assert "relationships_depth" in ids
    assert all(t.get("paragraph") for t in threads)
    assert all(t.get("body") for t in threads)
    assert all(t.get("micro") for t in threads)
    assert all("ritim hızın çarpanı" not in str(t.get("one_liner") or "").lower() for t in threads)
    assert all("yayınlanabilir iyi seviyesi" not in str(t.get("paragraph") or "").lower() for t in threads)
    assert all("görünürlük adımları" not in str(t.get("paragraph") or "").lower() for t in threads)
    assert all(" senden" not in str(t.get("micro") or "").lower() for t in threads)
    assert all("çok tipik" not in str(t.get("micro") or "").lower() for t in threads)
    assert all("vurgusu belirsizliği" not in str(t.get("body") or "").lower() for t in threads)
    assert "Satürn 3. evde ve Koç'ta" in str(threads[0].get("body") or "")
