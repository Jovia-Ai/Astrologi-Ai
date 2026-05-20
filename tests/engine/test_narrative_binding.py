from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.builders.upper_meaning_gate import build_upper_meaning_output


def test_upper_meaning_gate_off_when_low_capacity() -> None:
    upper_meanings = [
        {
            "composite_id": "comp_1",
            "upper_meaning": [
                "growth axis",
                "mastery potential",
                "Basarisiz Calisma Formu: dusus. Evrilmis Formu: yukselis.",
            ],
        }
    ]
    result = build_upper_meaning_output(
        upper_meanings,
        pressure_index=0.8,
        support_index=0.1,
        capacity_score=0.1,
        integration_score=0.1,
        dispositor_flow={},
        latent_potential={},
        potential_count=0,
        axis_activation={},
    )
    assert result["enabled"] is False
    assert "capacity_low" in result["reasons"]
