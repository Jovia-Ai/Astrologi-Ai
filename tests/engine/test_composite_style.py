"\"\"\"CompositeEngine style coverage\"\"\""

from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.engine.composite_engine import CompositeEngine


def test_sign_style_gemini_not_generic() -> None:
    style = CompositeEngine()._sign_style("Gemini")
    assert style["cognitive"] == "quick"
    assert style["expression"] == "verbal"


def test_house_context_ninth_not_placeholder() -> None:
    context = CompositeEngine()._house_context(9)
    assert context["identity"] == "meaning_seeking"
    assert context["expression"] == "broadcasting"
