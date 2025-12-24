"""Tests covering the deterministic phase-2 selector contract."""

from __future__ import annotations

import math
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from engine.phase2_selector import Phase2Selector


def _build_signal(theme: str, slot: str, weight: float, domain: str, axis: str) -> dict[str, object]:
    return {
        "signal_id": f"{theme}-{slot}",
        "theme": theme,
        "signal_score": weight,
        "experienced_weight": weight,
        "domain_candidates": [domain],
        "axis_candidates": [axis],
        "focus_object": "focus",
        "slot_candidates": [slot],
        "activation_type": "active",
        "trigger_tags": ["high"],
        "provenance": [{"type": "rule", "ref_id": slot}],
    }


def test_phase2_selector_returns_anchor_slots() -> None:
    selector = Phase2Selector()
    signals = [
        _build_signal("visibility_pressure", "cause", 0.7, "identity", "1-7"),
        _build_signal("security_vs_autonomy", "mechanism", 0.6, "psychology", "2-8"),
        _build_signal("emotion_vs_structure", "effect", 0.5, "relationships", "4-10"),
    ]
    slots = selector.select_phase2_slots("chart-hash", signals)
    assert any(slot["slot"] in {"cause", "mechanism"} for slot in slots)


def test_phase2_selector_micro_insight_when_no_anchor() -> None:
    selector = Phase2Selector()
    signals = [
        _build_signal("growth_resilience", "effect", 0.4, "identity", "3-9"),
    ]
    slots = selector.select_phase2_slots("hash-two", signals)
    assert len(slots) == 1
    assert slots[0]["slot"] == "micro_insight"


def test_phase2_selector_reports_felt_intensity() -> None:
    selector = Phase2Selector()
    signals = [
        _build_signal("visibility_pressure", "cause", 0.7, "identity", "1-7"),
        _build_signal("security_vs_autonomy", "mechanism", 0.6, "psychology", "4-10"),
        _build_signal("emotion_vs_structure", "effect", 0.5, "relationships", "2-8"),
    ]
    slots = selector.select_phase2_slots("chart-hash", signals)
    assert slots
    felt_map = slots[0].get("felt_intensity_map") or {}
    assert len(felt_map) >= 2
    total = math.fsum(felt_map.values())
    assert math.isclose(total, 1.0, rel_tol=1e-6)
