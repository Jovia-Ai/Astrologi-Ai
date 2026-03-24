from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.builders.phase2_selector import select_phase2_fragments


def _fragment(
    *,
    text: str,
    planet: str,
    house: int,
    rule_id: str,
    fragment_id: str,
) -> dict[str, object]:
    return {
        "fragment_id": fragment_id,
        "text": text,
        "trigger": {"type": "planet_house", "planet": planet, "house": house},
        "source_rule_ids": [rule_id],
    }


def test_phase2_selector_avoids_reusing_same_source_when_valid_alternative_exists() -> None:
    fragments = {
        "identity": {
            "cause": [
                _fragment(
                    text="Kimliğinin merkezinde görünürlük ve ağırlık kurma ihtiyacı var",
                    planet="Sun",
                    house=1,
                    rule_id="sun_in_house_1",
                    fragment_id="identity-sun",
                ),
                _fragment(
                    text="Kimliğinde duygusal uyum arayışı da belirgin",
                    planet="Moon",
                    house=4,
                    rule_id="moon_in_house_4",
                    fragment_id="identity-moon",
                ),
            ],
            "mechanism": [],
            "effect": [],
            "shadow": [],
            "potential": [],
        },
        "psychology": {
            "cause": [
                _fragment(
                    text="Psikolojik temelde yine görünürlük baskısı çalışıyor",
                    planet="Sun",
                    house=1,
                    rule_id="sun_in_house_1",
                    fragment_id="psychology-sun",
                ),
                _fragment(
                    text="İç dünyanda güvenli alan kurma ihtiyacı büyüyor",
                    planet="Moon",
                    house=4,
                    rule_id="moon_in_house_4",
                    fragment_id="psychology-moon",
                ),
            ],
            "mechanism": [],
            "effect": [],
            "shadow": [],
            "potential": [],
        },
    }
    meta_info = {
        "dominant_planets": [
            {"planet": "sun", "score": 1.0},
            {"planet": "moon", "score": 0.95},
        ],
        "chart_ruler": "sun",
        "stellium_planets": [],
        "planet_signs": {"sun": "leo", "moon": "cancer"},
        "planet_houses": {"sun": 1, "moon": 4},
    }

    selected = select_phase2_fragments(fragments, [], meta_info, None, None, max_domains=0)

    identity_cause = selected["identity"]["slots"]["cause"]
    psychology_cause = selected["psychology"]["slots"]["cause"]

    assert identity_cause["trigger"]["planet"] == "Sun"
    assert psychology_cause["trigger"]["planet"] == "Moon"
