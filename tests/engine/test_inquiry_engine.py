from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.engine.inquiry_engine import InquiryEngine


def test_inquiry_engine_high_load_reason() -> None:
    engine = InquiryEngine()
    composites = [{"composite_id": "comp_1"}]
    emphasis = {"comp_1": {"priority_score": 0.7, "planet_load_level": "high"}}

    result = engine.select_focus(composites, emphasis)

    assert result["focus_composites"]
    assert result["focus_composites"][0]["reason"] == "high_load"
