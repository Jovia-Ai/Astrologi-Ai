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


def _contrast_chart() -> dict:
    return {
        "house_positions": {
            "1": {"sign": "Gemini"},
            "2": {"sign": "Cancer"},
            "3": {"sign": "Leo"},
            "4": {"sign": "Virgo"},
            "5": {"sign": "Libra"},
            "6": {"sign": "Scorpio"},
            "7": {"sign": "Sagittarius"},
            "8": {"sign": "Capricorn"},
            "9": {"sign": "Aquarius"},
            "10": {"sign": "Pisces"},
            "11": {"sign": "Aries"},
            "12": {"sign": "Taurus"},
        },
        "angles": {
            "ascendant_sign": "Gemini",
            "midheaven_sign": "Pisces",
        },
    }


def _contrast_planets() -> list[dict]:
    return [
        {"planet": "Sun", "sign": "Pisces", "house": 10},
        {"planet": "Moon", "sign": "Libra", "house": 5},
        {"planet": "Mercury", "sign": "Pisces", "house": 12, "retrograde": True},
        {"planet": "Venus", "sign": "Aquarius", "house": 11},
        {"planet": "Mars", "sign": "Cancer", "house": 2},
        {"planet": "Jupiter", "sign": "Aquarius", "house": 11},
        {"planet": "Saturn", "sign": "Gemini", "house": 1},
        {"planet": "Uranus", "sign": "Aquarius", "house": 9},
        {"planet": "Neptune", "sign": "Capricorn", "house": 8},
        {"planet": "Pluto", "sign": "Sagittarius", "house": 7},
        {"planet": "North Node", "sign": "Taurus", "house": 12},
    ]


def _contrast_aspects() -> list[dict]:
    return [
        {"planet1": "Mercury", "planet2": "Saturn", "aspect": "Square", "orb": 1.12},
        {"planet1": "Mercury", "planet2": "Jupiter", "aspect": "Sextile", "orb": 1.84},
        {"planet1": "Jupiter", "planet2": "Venus", "aspect": "Conjunction", "orb": 2.03},
        {"planet1": "Jupiter", "planet2": "Sun", "aspect": "Sextile", "orb": 2.41},
        {"planet1": "Moon", "planet2": "Venus", "aspect": "Trine", "orb": 1.47},
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
    mind_thread = next(t for t in threads if t.get("id") == "identity_mechanics")
    mind_blocks = mind_thread.get("detail_blocks") or []
    assert len(mind_blocks) >= 6
    assert any("Çünkü senin yöneticin Satürn Koç'ta ve 3. evde." in str(block) for block in mind_blocks)
    rel_thread = next(t for t in threads if t.get("id") == "relationships_depth")
    detail_blocks = rel_thread.get("detail_blocks") or []
    assert len(detail_blocks) >= 6
    assert any("şefkat, aidiyet ve gerçek duygusal sıcaklık" in str(block) for block in detail_blocks)
    assert any("özel hissetmek" in str(block) and "görülmediğinde kırılmak" in str(block) for block in detail_blocks)
    assert any("Ay 8. evde olduğu için" in str(block) for block in detail_blocks)
    assert any("Ay Aslan'da olduğu için" in str(block) for block in detail_blocks)
    career_thread = next(t for t in threads if t.get("id") == "career_visibility")
    career_blocks = career_thread.get("detail_blocks") or []
    assert len(career_blocks) >= 6
    assert any("denge, estetik ve ilişki zekası" in str(block) for block in career_blocks)
    assert any("üretimde vizyon, cesaret ve büyük resmi taşıyabilme" in str(block) for block in career_blocks)
    assert any("Venüs 12. evde ve Yay'da" in str(block) for block in career_blocks)


def test_supporting_threads_builder_varies_slide_text_across_different_charts() -> None:
    chart_a = _sample_chart()
    graph_a = build_natal_graph(chart_data=chart_a, planets=_sample_planets(), aspects=_sample_aspects())
    threads_a = build_supporting_threads(chart_data=chart_a, planets=_sample_planets(), natal_graph=graph_a)

    chart_b = _contrast_chart()
    graph_b = build_natal_graph(chart_data=chart_b, planets=_contrast_planets(), aspects=_contrast_aspects())
    threads_b = build_supporting_threads(chart_data=chart_b, planets=_contrast_planets(), natal_graph=graph_b)

    mind_a = next(t for t in threads_a if t.get("id") == "identity_mechanics")
    mind_b = next(t for t in threads_b if t.get("id") == "identity_mechanics")
    assert "Satürn Koç'ta ve 3. evde" in str((mind_a.get("detail_blocks") or [""])[0])
    assert "Merkür Balık'ta ve 12. evde" in str((mind_b.get("detail_blocks") or [""])[0])
    assert "ikinci bir iç editör" in " ".join(str(item) for item in (mind_b.get("detail_blocks") or []))

    rel_a = next(t for t in threads_a if t.get("id") == "relationships_depth")
    rel_b = next(t for t in threads_b if t.get("id") == "relationships_depth")
    assert rel_a.get("detail_blocks") != rel_b.get("detail_blocks")

    career_a = next(t for t in threads_a if t.get("id") == "career_visibility")
    career_b = next(t for t in threads_b if t.get("id") == "career_visibility")
    assert career_a.get("detail_blocks") != career_b.get("detail_blocks")
    assert 6 <= len(career_a.get("detail_blocks") or []) <= 7
    assert 6 <= len(career_b.get("detail_blocks") or []) <= 7
