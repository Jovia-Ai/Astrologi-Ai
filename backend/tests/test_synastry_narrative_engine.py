import sys
import types
import re


def _chart_a() -> dict:
    return {
        "planets": {
            "Sun": {"longitude": 276.75, "sign": "Capricorn", "house": 1},
            "Moon": {"longitude": 133.95, "sign": "Leo", "house": 8},
            "Mercury": {"longitude": 287.37, "sign": "Capricorn", "house": 1},
            "Venus": {"longitude": 253.71, "sign": "Sagittarius", "house": 12},
            "Mars": {"longitude": 177.93, "sign": "Virgo", "house": 9},
            "Jupiter": {"longitude": 294.30, "sign": "Capricorn", "house": 1},
            "Saturn": {"longitude": 1.16, "sign": "Aries", "house": 3},
            "Uranus": {"longitude": 303.06, "sign": "Aquarius", "house": 1},
            "Neptune": {"longitude": 296.69, "sign": "Capricorn", "house": 1},
            "Pluto": {"longitude": 244.26, "sign": "Sagittarius", "house": 11},
            "Node": {"longitude": 182.69, "sign": "Libra", "house": 9},
            "Lilith": {"longitude": 141.0, "sign": "Leo", "house": 8},
            "Chiron": {"longitude": 209.89, "sign": "Libra", "house": 10},
            "Fortune": {"longitude": 53.99, "sign": "Taurus", "house": 5},
        },
        "houses": {
            "1": 271.1868,
            "2": 310.2653,
            "3": 351.8247,
            "4": 25.2852,
            "5": 50.4481,
            "6": 71.1931,
            "7": 91.1868,
            "8": 130.2653,
            "9": 171.8247,
            "10": 205.2852,
            "11": 230.4481,
            "12": 251.1931,
        },
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
            "ascendant": 271.1868,
            "midheaven": 205.2851,
            "ascendant_sign": "Capricorn",
            "midheaven_sign": "Libra",
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Saturn", "aspect": "square", "orb": 5.59},
            {"planet1": "Moon", "planet2": "Venus", "aspect": "trine", "orb": 0.24},
            {"planet1": "Mars", "planet2": "Saturn", "aspect": "opposition", "orb": 3.23},
            {"planet1": "Mars", "planet2": "Neptune", "aspect": "trine", "orb": 1.24},
            {"planet1": "Jupiter", "planet2": "Neptune", "aspect": "conjunction", "orb": 2.39},
            {"planet1": "Jupiter", "planet2": "Midheaven", "aspect": "square", "orb": 0.99},
            {"planet1": "Neptune", "planet2": "Midheaven", "aspect": "square", "orb": 1.40},
        ],
    }


def _chart_b() -> dict:
    return {
        "planets": {
            "Sun": {"longitude": 169.22, "sign": "Virgo", "house": 12},
            "Moon": {"longitude": 67.6, "sign": "Gemini", "house": 9},
            "Mercury": {"longitude": 157.2, "sign": "Virgo", "house": 12},
            "Venus": {"longitude": 156.65, "sign": "Virgo", "house": 11},
            "Mars": {"longitude": 134.26, "sign": "Leo", "house": 11},
            "Jupiter": {"longitude": 353.58, "sign": "Pisces", "house": 6},
            "Saturn": {"longitude": 32.99, "sign": "Taurus", "house": 8},
            "Uranus": {"longitude": 309.34, "sign": "Aquarius", "house": 5},
            "Neptune": {"longitude": 299.61, "sign": "Capricorn", "house": 4},
            "Pluto": {"longitude": 245.5, "sign": "Sagittarius", "house": 3},
            "Node": {"longitude": 151.36, "sign": "Virgo", "house": 11},
            "Lilith": {"longitude": 210.19, "sign": "Scorpio", "house": 2},
            "Chiron": {"longitude": 225.61, "sign": "Scorpio", "house": 2},
            "Fortune": {"longitude": 81.5, "sign": "Gemini", "house": 9},
        },
        "houses": {
            "1": 183.1246,
            "2": 210.0251,
            "3": 240.5744,
            "4": 273.4906,
            "5": 306.3426,
            "6": 336.6655,
            "7": 3.1246,
            "8": 30.0251,
            "9": 60.5744,
            "10": 93.4906,
            "11": 126.3426,
            "12": 156.6655,
        },
        "house_positions": {
            "1": {"sign": "Libra"},
            "2": {"sign": "Scorpio"},
            "3": {"sign": "Sagittarius"},
            "4": {"sign": "Capricorn"},
            "5": {"sign": "Aquarius"},
            "6": {"sign": "Pisces"},
            "7": {"sign": "Aries"},
            "8": {"sign": "Taurus"},
            "9": {"sign": "Gemini"},
            "10": {"sign": "Cancer"},
            "11": {"sign": "Leo"},
            "12": {"sign": "Virgo"},
        },
        "angles": {
            "ascendant": 183.1246,
            "midheaven": 93.4906,
            "ascendant_sign": "Libra",
            "midheaven_sign": "Cancer",
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Mercury", "aspect": "conjunction", "orb": 0.20},
            {"planet1": "Venus", "planet2": "Mars", "aspect": "conjunction", "orb": 7.61},
            {"planet1": "Saturn", "planet2": "Neptune", "aspect": "trine", "orb": 3.38},
            {"planet1": "Neptune", "planet2": "Midheaven", "aspect": "opposition", "orb": 26.12},
        ],
    }


def _load_synastry_analysis_module():
    sys.modules["app.main"] = types.SimpleNamespace(app=None, create_app=None)
    fake_builder = types.ModuleType("app.astro.chart_engine.builder")
    fake_builder.build_natal_chart = lambda payload: payload["chart"]
    sys.modules["app.astro.chart_engine.builder"] = fake_builder
    sys.modules.pop("app.services.synastry_analysis", None)
    from app.services import synastry_analysis  # type: ignore

    return synastry_analysis


def test_synastry_narrative_blocks_exist_and_are_ordered(monkeypatch) -> None:
    synastry_analysis = _load_synastry_analysis_module()

    def fake_build_partner_chart(partner: dict) -> dict:
        return _chart_a() if partner.get("name") == "Person A" else _chart_b()

    monkeypatch.setattr(synastry_analysis, "_build_partner_chart", fake_build_partner_chart)
    out = synastry_analysis.analyze_synastry(
        {
            "partner_a": {"name": "Person A"},
            "partner_b": {"name": "Person B"},
            "options": {"include_debug": True},
        }
    )

    blocks = out["public"]["narrative"]["blocks"]
    block_ids = [block["id"] for block in blocks]

    assert block_ids == [
        "what_you_open_in_them",
        "what_they_open_in_you",
        "main_rooms_of_relationship",
        "growth_axis",
        "comfort_vs_trigger",
        "long_term_shape",
    ]
    assert all({"id", "headline", "teaser", "body", "chips", "micro"} <= set(block.keys()) for block in blocks)
    assert out["debug"]["narrative_debug"]["blocks_debug"]
    assert all("template_id" in block for block in out["debug"]["narrative_debug"]["blocks_debug"])


def test_synastry_narrative_is_partner_specific_and_deterministic(monkeypatch) -> None:
    synastry_analysis = _load_synastry_analysis_module()

    def fake_build_partner_chart(partner: dict) -> dict:
        return _chart_a() if partner.get("name") == "Person A" else _chart_b()

    monkeypatch.setattr(synastry_analysis, "_build_partner_chart", fake_build_partner_chart)
    payload = {
        "partner_a": {"name": "Person A"},
        "partner_b": {"name": "Person B"},
        "options": {"include_debug": True},
    }

    first = synastry_analysis.analyze_synastry(payload)
    second = synastry_analysis.analyze_synastry(payload)

    assert first["public"]["narrative"] == second["public"]["narrative"]
    outbound = first["public"]["narrative"]["blocks"][0]
    inbound = first["public"]["narrative"]["blocks"][1]

    assert "güven" in outbound["headline"].lower() or "kök" in outbound["headline"].lower()
    assert "güven" in outbound["teaser"].lower() or "kök" in outbound["teaser"].lower()
    assert "iç" in outbound["body"].lower()
    assert "mahremiyet" in inbound["headline"].lower() or "yoğunluk" in inbound["headline"].lower()
    assert outbound["headline"] != inbound["headline"]


def test_synastry_narrative_copy_is_less_mechanical_and_less_repetitive(monkeypatch) -> None:
    synastry_analysis = _load_synastry_analysis_module()

    def fake_build_partner_chart(partner: dict) -> dict:
        return _chart_a() if partner.get("name") == "Person A" else _chart_b()

    monkeypatch.setattr(synastry_analysis, "_build_partner_chart", fake_build_partner_chart)
    out = synastry_analysis.analyze_synastry(
        {
            "partner_a": {"name": "Person A"},
            "partner_b": {"name": "Person B"},
            "options": {"include_debug": True},
        }
    )

    forbidden = ("vitrin", "sprint", "çıktı", "rota", "upgrade", "kalibrasyon", "workflow", "tampon", "aktivasyon")
    blocks = out["public"]["narrative"]["blocks"]

    for block in blocks:
        teaser = block["teaser"].lower()
        body = block["body"].lower()
        micro = block["micro"].lower()
        joined = " ".join((teaser, body, micro))
        assert not any(word in joined for word in forbidden)
        assert teaser not in body
        assert micro not in body
        assert len(set(re.findall(r"[a-zçğıöşü]+", body))) >= 12
