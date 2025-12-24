"""Tests for the conflict vector builder diagnostics."""

from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from engine.conflict_vector_builder import ConflictVectorBuilder


def _build_slot(
    slot_id: str,
    *,
    aspect_type: str = "hard",
    focus: str = "chart_ruler",
    activation: str = "life_stage_bound",
    domain: str = "identity",
    axis: str = "1-7",
    weight: float = 0.6,
    tags: list[str] | None = None,
    provenance: list[dict[str, str]] | None = None,
    stellium: bool = False,
    dispositor_supportive: bool = False,
    axis_balanced: bool = False,
    slot_name: str = "cause",
) -> dict[str, object]:
    return {
        "signal_id": slot_id,
        "theme": "boundary",
        "domain": domain,
        "axis": axis,
        "slot": slot_name,
        "focus_object": focus,
        "experienced_weight": weight,
        "activation_type": activation,
        "trigger_tags": tags or ["hard"],
        "provenance": provenance or [{"type": "rule", "ref_id": slot_id}],
        "aspect_type": aspect_type,
        "orb": 2.0,
        "stellium_core": stellium,
        "dispositor_loop_supportive": dispositor_supportive,
        "axis_balanced": axis_balanced,
    }


def test_conflict_vector_builder_basic() -> None:
    builder = ConflictVectorBuilder()
    slots = [
        _build_slot("hard-cause", tags=["hard", "tight_orb"], stellium=True, slot_name="cause"),
        _build_slot(
            "soft-effect",
            aspect_type="soft",
            activation="constant",
            tags=["soft"],
            slot_name="effect",
            focus="stellium_core",
            domain="relationships",
            axis="4-10",
            weight=0.4,
            dispositor_supportive=True,
            axis_balanced=True,
            provenance=[{"type": "rule", "ref_id": "soft-rule"}],
        ),
    ]
    bundle = builder.build(slots)["conflict_bundle"]
    assert isinstance(bundle["pressure_index"], float)
    assert bundle["net_vector"] == bundle["pressure_index"] - bundle["support_index"]
    assert bundle["component_breakdown"]["hardness"] > 0.0
    assert bundle["ssl_components"]["repetition_across_domains"] >= 0.0
    assert len(bundle["provenance_summary"]) <= 3
    context = bundle.get("vector_context", {})
    assert context.get("dominant_domain") in {"identity", "relationships"}
    assert context.get("dominant_axis") in {"1-7", "4-10"}
    assert context.get("focus_centrality_tier") in {"low", "mid", "high"}


def test_conflict_vector_builder_applies_pressure_guard() -> None:
    builder = ConflictVectorBuilder()
    slots = [
        _build_slot("guard-cause", weight=0.2, tags=["hard"]),
        _build_slot("guard-effect", slot_name="effect", tags=["soft"], domain="identity"),
    ]
    conflict = builder.build(slots)["conflict_bundle"]
    assert conflict["pressure_index"] <= 0.7
    assert "vector_context" in conflict


def test_conflict_vector_builder_high_load_flag() -> None:
    builder = ConflictVectorBuilder()
    slots = [
        _build_slot("load-cause", weight=0.9, tags=["hard"], slot_name="cause"),
        _build_slot("load-effect", weight=0.8, tags=["soft"], slot_name="effect", axis_balanced=True),
    ]
    conflict = builder.build(slots)["conflict_bundle"]
    assert conflict["high_load_high_capacity"] is True
