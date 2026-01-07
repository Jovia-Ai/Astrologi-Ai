from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

import re

from app.builders.narrative_binding import build_narrative


def _fragment(text: str, rule_id: str) -> dict[str, object]:
    return {
        "text": text,
        "trigger": {"planet": "sun", "sign": "leo", "house": 1, "type": "planet"},
        "source_rule_ids": [rule_id],
        "salience_score": 0.6,
    }


def test_narrative_voice_invariants() -> None:
    phase2 = {
        "identity": {
            "slots": {
                "mechanism": _fragment("kontrol ve istikrar ihtiyaci", "rule_mech"),
                "cause": _fragment("erken sorumluluk hissi", "rule_cause"),
                "effect": _fragment("guclu durus", "rule_effect"),
                "shadow": _fragment("kasilma", "rule_shadow"),
            }
        }
    }
    narrative = build_narrative(
        {"dominant_domains": [{"domain": "identity", "score": 1.0}]},
        [{"label": "Kontrol + istikrar", "domain": "identity"}],
        phase2,
        None,
        {"tone": "firm"},
        meta_info={"planet_houses": {"sun": 1}},
        axis_activation={"active_axes": ["1-7"], "axis_tension": "high"},
    )
    identity = narrative["domains"]["identity"]
    text = identity["text"]
    forbidden = [
        "Genelde",
        "Sunu fark etmek iyi gelebilir",
        "Bu harita",
        "Bunun sonucu",
        "kisa destek",
        "Ikinci eksen",
        "kapasitesi acik kalir",
        "yuklenme",
        "baskisini hissettirebilir",
    ]
    for token in forbidden:
        assert token.lower() not in text.lower()
    assert re.search(r"\bacik\b", text.lower()) is None
    assert identity["title"] == "Senin Dünyanın İç Çekirdeği"
    sections = identity["sections"]
    assert sections
    assert "dışarıdan" in sections[0]["text"].lower()
