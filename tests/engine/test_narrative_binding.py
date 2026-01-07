from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.builders.narrative_binding import build_narrative
from app.builders.upper_meaning_gate import build_upper_meaning_output
from app.engine.tone_profile import ToneProfile


def _fragment(
    text: str,
    *,
    planet: str = "sun",
    sign: str = "leo",
    house: int = 1,
    rule_id: str = "rule_1",
    salience: float = 0.5,
) -> dict[str, object]:
    return {
        "text": text,
        "planet": planet,
        "trigger": {"planet": planet, "sign": sign, "house": house, "type": "planet"},
        "source_rule_ids": [rule_id],
        "salience_score": salience,
    }


def _base_meta() -> dict[str, object]:
    return {
        "dominant_domains": [{"domain": "identity", "score": 1.0}],
        "meta_summary_text": "Bu sistemde identity alani yogun calisiyor.",
        "pressure_index": 0.8,
        "support_index": 0.3,
    }


def _base_meta_info() -> dict[str, object]:
    return {
        "planet_houses": {"sun": 1},
        "dominant_planets": [],
        "dominant_elements": {},
        "chart_ruler": "sun",
    }


def _base_axis() -> dict[str, object]:
    return {"active_axes": ["1-7"], "axis_tension": "high"}


def test_narrative_identity_not_empty() -> None:
    phase2 = {
        "identity": {
            "slots": {
                "mechanism": _fragment("kimlikte kontrollu ton calisir", rule_id="rule_mech"),
                "cause": _fragment("erken sorumluluk yuklenmesi", rule_id="rule_cause"),
                "effect": _fragment("guclu durus etkisi", rule_id="rule_effect"),
                "potential": _fragment("istikrar kapasitesi", rule_id="rule_potential"),
                "shadow": _fragment("katilasma riski", rule_id="rule_shadow"),
            }
        }
    }
    focus = [{"label": "Kontrollu kimlik + yuksek gerilim", "domain": "identity"}]
    tone = ToneProfile(0.6, 0.5, 0.5, 0.6, 0.5, 0.5)
    narrative = build_narrative(
        _base_meta(),
        focus,
        phase2,
        None,
        tone,
        meta_info=_base_meta_info(),
        axis_activation=_base_axis(),
    )
    identity = narrative["domains"]["identity"]
    assert identity["text"].strip()
    types = [section["type"] for section in identity["sections"]]
    assert types == ["recognition", "experienced", "potential", "shadow"]
    assert identity["text"].count("Sunu fark etmek iyi gelebilir") <= 1
    assert ", ," not in identity["text"]
    assert ". ," not in identity["text"]
    experienced = next(
        section for section in identity["sections"] if section["type"] == "experienced"
    )
    assert len(experienced["text"].split("\n\n")) >= 2
    lines = [line.strip() for line in experienced["text"].split("\n\n") if line.strip()]
    assert len(lines) == len(set(lines))
    recognition = next(
        section for section in identity["sections"] if section["type"] == "recognition"
    )
    assert "dışarıdan" in recognition["text"].lower()
    assert "ama içeride" in recognition["text"].lower()


def test_selection_gate_respects_budget() -> None:
    supporting = []
    for idx in range(10):
        supporting.append(
            {
                "text": f"mekanizma_{idx}",
                "trigger": {"planet": "sun", "sign": "leo", "house": 1, "type": "planet"},
                "source_rule_ids": [f"rule_{idx}"],
                "salience_score": 0.3 + idx * 0.01,
            }
        )
    fragment = _fragment("mekanizma_ana", rule_id="rule_main")
    fragment["supporting_facts"] = supporting
    phase2 = {"identity": {"slots": {"mechanism": fragment}}}
    narrative = build_narrative(
        _base_meta(),
        [{"label": "Kontrollu kimlik", "domain": "identity"}],
        phase2,
        None,
        {"tone": "firm"},
        meta_info=_base_meta_info(),
        axis_activation=_base_axis(),
    )
    selected = narrative["domains"]["identity"]["debug"]["selected"]
    assert len(selected) <= 8
    mechanism_count = sum(1 for item in selected if item["slot"] == "mechanism")
    assert mechanism_count >= 3


def test_dedup_signature_removes_duplicates() -> None:
    fragment = _fragment("mekanizma_ana", rule_id="dup_rule")
    fragment["supporting_facts"] = [
        {
            "text": "mekanizma_ana_2",
            "trigger": fragment["trigger"],
            "source_rule_ids": ["dup_rule"],
            "salience_score": 0.9,
        }
    ]
    phase2 = {"identity": {"slots": {"mechanism": fragment}}}
    narrative = build_narrative(
        _base_meta(),
        [{"label": "Kontrollu kimlik", "domain": "identity"}],
        phase2,
        None,
        {"tone": "firm"},
        meta_info=_base_meta_info(),
        axis_activation=_base_axis(),
    )
    selected = narrative["domains"]["identity"]["debug"]["selected"]
    signatures = {item["signature"] for item in selected}
    assert len(signatures) == len(selected)


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
        dispositor_flow={},
        latent_potential={},
        potential_count=0,
        axis_activation={},
    )
    assert result["enabled"] is False
    assert "capacity_low" in result["reasons"]


def test_narrative_does_not_contain_raw_slot_text() -> None:
    raw_text = "RAW_SLOT_TEXT_SHOULD_NOT_APPEAR"
    phase2 = {
        "identity": {
            "slots": {
                "mechanism": _fragment(raw_text, rule_id="rule_mech"),
                "effect": _fragment("guclu durus etkisi", rule_id="rule_effect"),
            }
        }
    }
    narrative = build_narrative(
        _base_meta(),
        [{"label": "Kontrollu kimlik", "domain": "identity"}],
        phase2,
        None,
        {"tone": "firm"},
        meta_info=_base_meta_info(),
        axis_activation=_base_axis(),
    )
    identity = narrative["domains"]["identity"]
    assert raw_text not in identity["text"]
