from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.helpers.normalize import normalize_planet_key, normalize_token
from app.helpers.placement_utils import extract_planet_signs


def test_normalize_token_handles_hyphen_and_spaces() -> None:
    assert normalize_token(" Black Moon-Lilith ") == "black_moon_lilith"


def test_normalize_planet_key_preserves_hyphen() -> None:
    assert normalize_planet_key("Black Moon-Lilith") == "black_moon-lilith"


def test_extract_planet_signs_filters_house_tokens() -> None:
    placements = ["Sun_in_Leo", "Moon_in_1st_house"]
    assert extract_planet_signs(placements) == {"sun": "leo"}


def test_extract_planet_signs_keeps_last_planet() -> None:
    placements = ["Mars_in_Aries", "Mars_in_Taurus"]
    assert extract_planet_signs(placements) == {"mars": "taurus"}
