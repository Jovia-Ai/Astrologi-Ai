"""Tests for strain/resilience score derivation."""
from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.helpers.strain_resilience import build_strain_resilience


def test_strain_score_tracks_pressure() -> None:
    result = build_strain_resilience(
        pressure_support={"pressure_index": 0.92, "support_index": 0.2},
        meaning_weighting={},
        aspect_mechanics={},
    )
    assert result["strain"]["score"] >= 0.9
    assert result["resilience"]["score"] <= 0.3


def test_resilience_score_tracks_support() -> None:
    result = build_strain_resilience(
        pressure_support={"pressure_index": 0.1, "support_index": 0.88},
        meaning_weighting={},
        aspect_mechanics={},
    )
    assert result["resilience"]["score"] >= 0.85
    assert result["strain"]["score"] <= 0.2
