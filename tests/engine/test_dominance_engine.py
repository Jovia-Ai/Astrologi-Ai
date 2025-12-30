from __future__ import annotations

from pathlib import Path

from app.engine.dominance_engine import DominanceEngine
from app.engine.pattern_engine import PatternEmphasisEngine


def test_dominance_engine_prefers_angular_and_dignity() -> None:
    engine = DominanceEngine()
    planets = [
        {"planet": "Sun", "sign": "Leo", "house": 1},
        {"planet": "Venus", "sign": "Virgo", "house": 6},
    ]

    result = engine.compute(
        planets=planets,
        houses=None,
        aspects=[],
        meta_info={"house_clusters": {}},
    )
    dominant = result["dominant_planets"]
    assert dominant
    assert dominant[0]["planet"] == "sun"
    assert "angular_house" in dominant[0]["reasons"]
    assert "dignity" in dominant[0]["reasons"]


def test_dominance_engine_angular_beats_dignity_only() -> None:
    engine = DominanceEngine()
    planets = [
        {"planet": "Mars", "sign": "Cancer", "house": 10},
        {"planet": "Venus", "sign": "Libra", "house": 2},
    ]
    aspects = [
        {"planet1": "Mars", "planet2": "Moon", "type": "square", "orb": 1.0},
    ]

    result = engine.compute(
        planets=planets,
        houses=None,
        aspects=aspects,
        meta_info={"house_clusters": {}},
    )
    dominant = result["dominant_planets"]
    assert dominant
    assert dominant[0]["planet"] == "mars"


def test_dominance_engine_missing_rules_returns_empty(tmp_path: Path) -> None:
    engine = DominanceEngine(rules_root=str(tmp_path))
    result = engine.compute(
        planets=[],
        houses=None,
        aspects=[],
        meta_info={},
    )
    assert result["dominant_planets"] == []


def test_pattern_engine_uses_dominant_planet_first() -> None:
    meta_info = {
        "dominant_planets": [{"planet": "sun", "score": 4.0, "reasons": ["angular_house"]}],
        "dominant_elements": {"Fire": 4},
    }
    dominance = PatternEmphasisEngine._derive_dominance(meta_info)
    assert dominance == "planet:sun"
