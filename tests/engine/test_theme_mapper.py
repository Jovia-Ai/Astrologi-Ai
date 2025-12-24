"""Tests for the deterministic theme mapper engine."""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from engine.theme_mapper import ThemeMapper, ThemeResolutionError


def _build_signal(
    signal_id: str,
    score: float,
    aspect_type: str,
    involves: Sequence[str],
    slot: str,
) -> dict[str, object]:
    return {
        "signal_id": signal_id,
        "signal_score": score,
        "aspect_type": aspect_type,
        "involves": involves,
        "axis_candidates": ["1-7"],
        "focus_object": "frame",
        "slot_candidates": [slot],
        "trigger_tags": ["high"],
        "life_stage": "mid",
        "provenance": ["rule_x"],
    }


def test_theme_mapper_resolves_priority_rule() -> None:
    mapper = ThemeMapper()
    signals = [
        _build_signal("intimacy", 0.7, "hard", ["Moon"], "cause"),
        _build_signal("desire", 0.6, "hard", ["Mars"], "effect"),
    ]
    resolved = mapper.map_signals("hash123", signals)
    assert resolved["theme"] == "intimacy_trust"


def test_theme_mapper_weak_fallback_triggers() -> None:
    mapper = ThemeMapper()
    weak_signal = _build_signal("security", 0.1, "hard", ["Mars"], "effect")
    resolved = mapper.map_signals("hash-fallback", [weak_signal])
    assert resolved["theme"] == "meaning_belief"


def test_theme_mapper_raises_if_no_candidates() -> None:
    mapper = ThemeMapper()
    try:
        mapper.map_signals("empty", [])
    except ThemeResolutionError as exc:
        assert "No theme" in str(exc)
