from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.builders.phrase_mapper import (
    build_claim,
    default_phrase_map_config,
    infer_meaning_key,
    infer_rule_group,
)


def test_infer_rule_group_in_prefix() -> None:
    assert infer_rule_group(["venus_in_house_5"]) == "venus_core"


def test_meaning_key_from_rulegroup() -> None:
    cfg = default_phrase_map_config()
    key = infer_meaning_key(
        "identity",
        "mechanism",
        "sun",
        "capricorn",
        1,
        "control_core",
        cfg,
    )
    assert key == "control_need"


def test_fallback_payload_not_empty() -> None:
    cfg = default_phrase_map_config()
    claim = build_claim(
        {
            "trigger": {"planet": "mars", "sign": "aries", "house": 3},
            "source_rule_ids": ["unknown_rule"],
            "text": "raw",
        },
        domain="identity",
        slot="mechanism",
        salience=0.3,
        cfg=cfg,
    )
    assert claim.payload


def test_claim_signature_stable() -> None:
    cfg = default_phrase_map_config()
    claim = build_claim(
        {
            "trigger": {"planet": "sun", "sign": "capricorn", "house": 1},
            "source_rule_ids": ["sun_in_capricorn"],
            "text": "raw",
        },
        domain="identity",
        slot="mechanism",
        salience=0.7,
        cfg=cfg,
    )
    assert claim.signature
