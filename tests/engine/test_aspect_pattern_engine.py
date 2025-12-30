from __future__ import annotations

from app.engine.aspect_pattern_engine import AspectPatternEngine


def test_detects_t_square() -> None:
    engine = AspectPatternEngine(orb_threshold=3.0)
    planets = {
        "Sun": {"degree": 0.0},
        "Moon": {"degree": 180.0},
        "Mars": {"degree": 90.0},
    }
    aspects = [
        {"planet1": "Sun", "planet2": "Moon", "type": "opposition", "orb": 1.0},
        {"planet1": "Sun", "planet2": "Mars", "type": "square", "orb": 1.0},
        {"planet1": "Moon", "planet2": "Mars", "type": "square", "orb": 1.0},
    ]

    result = engine.compute(aspects=aspects, planets=planets, meta_info=None)
    patterns = result["aspect_patterns"]
    assert any(pattern["pattern"] == "t_square" for pattern in patterns)


def test_detects_grand_trine() -> None:
    engine = AspectPatternEngine(orb_threshold=3.0)
    planets = {
        "Sun": {"degree": 0.0},
        "Moon": {"degree": 120.0},
        "Mars": {"degree": 240.0},
    }
    aspects = [
        {"planet1": "Sun", "planet2": "Moon", "type": "trine", "orb": 0.5},
        {"planet1": "Sun", "planet2": "Mars", "type": "trine", "orb": 0.5},
        {"planet1": "Moon", "planet2": "Mars", "type": "trine", "orb": 0.5},
    ]

    result = engine.compute(aspects=aspects, planets=planets, meta_info=None)
    patterns = result["aspect_patterns"]
    assert any(pattern["pattern"] == "grand_trine" for pattern in patterns)


def test_detects_yod_from_quincunx_degrees() -> None:
    engine = AspectPatternEngine(orb_threshold=3.0)
    planets = {
        "Sun": {"degree": 0.0},
        "Moon": {"degree": 60.0},
        "Mars": {"degree": 210.0},
    }
    aspects = [
        {"planet1": "Sun", "planet2": "Moon", "type": "sextile", "orb": 1.0},
    ]

    result = engine.compute(aspects=aspects, planets=planets, meta_info=None)
    patterns = result["aspect_patterns"]
    assert any(pattern["pattern"] == "yod" for pattern in patterns)


def test_detects_kite() -> None:
    engine = AspectPatternEngine(orb_threshold=3.0)
    planets = {
        "Sun": {"degree": 0.0},
        "Moon": {"degree": 120.0},
        "Mars": {"degree": 240.0},
        "Venus": {"degree": 180.0},
    }
    aspects = [
        {"planet1": "Sun", "planet2": "Moon", "type": "trine", "orb": 1.0},
        {"planet1": "Sun", "planet2": "Mars", "type": "trine", "orb": 1.0},
        {"planet1": "Moon", "planet2": "Mars", "type": "trine", "orb": 1.0},
        {"planet1": "Sun", "planet2": "Venus", "type": "opposition", "orb": 1.0},
    ]

    result = engine.compute(aspects=aspects, planets=planets, meta_info=None)
    patterns = result["aspect_patterns"]
    assert any(pattern["pattern"] == "kite" for pattern in patterns)
