from __future__ import annotations

import json
import os
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.engine.tone_apply import apply_tone
from app.engine.tone_profile import ToneProfile, DEFAULT_CONFIG, CONFIG_PATH

from tests.approval.test_narrative_snapshots import _build_payload, _chart_samples


BANNED_SHADOW = ("asla", "kesin", "mutlaka", "tehdit", "korkun", "korkut", "sen boylesin")


def _selected_signature_set(fragments: dict) -> set[tuple]:
    signatures: set[tuple] = set()
    for domain, entry in fragments.items():
        slots = entry.get("slots") or {}
        for slot_name, fragment in slots.items():
            if not isinstance(fragment, dict):
                continue
            text = fragment.get("text")
            supporting = fragment.get("supporting_facts") or []
            supporting_texts = tuple(
                item.get("text") for item in supporting if isinstance(item, dict)
            )
            signatures.add((domain, slot_name, text, supporting_texts))
    return signatures


def test_selected_slots_signature_set_same_with_tone_toggle() -> None:
    chart = _chart_samples()["taurus_cancer"]
    payload_on = _build_payload(chart, tone_enabled=True)
    payload_off = _build_payload(chart, tone_enabled=False)

    signatures_on = _selected_signature_set(payload_on.get("fragments") or {})
    signatures_off = _selected_signature_set(payload_off.get("fragments") or {})
    assert signatures_on == signatures_off


def test_shadow_safety_blacklist_low_certainty() -> None:
    tone = ToneProfile(
        directness=0.3,
        warmth=0.7,
        intensity=0.6,
        certainty=0.2,
        tempo=0.4,
        distance=0.6,
    )
    text = apply_tone("baskiyi artirabilecek bir esik", tone, section="shadow").lower()
    assert all(banned not in text for banned in BANNED_SHADOW)


def test_certainty_thresholds_parametrized(tmp_path: Path) -> None:
    config = dict(DEFAULT_CONFIG)
    config["tone_thresholds"] = {
        "certainty_hi": 0.65,
        "certainty_mid": 0.4,
        "directness_hi": 0.65,
        "warmth_hi": 0.65,
        "tempo_hi": 0.65,
        "distance_hi": 0.6,
    }
    config_path = tmp_path / "tone.yaml"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    import app.engine.tone_profile as tone_profile_module
    original = CONFIG_PATH
    try:
        tone_profile_module.CONFIG_PATH = config_path
        tone_profile_module.load_tone_config.cache_clear()
        tone = ToneProfile(
            directness=0.4,
            warmth=0.5,
            intensity=0.4,
            certainty=0.65,
            tempo=0.4,
            distance=0.6,
        )
        text = apply_tone("Bu harita, kimlik alaninda bir tema anlatir.", tone, section="recognition")
        assert "bazen" not in text.lower()
    finally:
        tone_profile_module.CONFIG_PATH = original
        tone_profile_module.load_tone_config.cache_clear()


def test_env_override_merges_over_yaml(tmp_path: Path) -> None:
    config = dict(DEFAULT_CONFIG)
    config["tone_defaults"] = {"warmth_bias": 0.2, "uncertainty_default": 0.1}
    config_path = tmp_path / "tone.yaml"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    import app.engine.tone_profile as tone_profile_module
    original = CONFIG_PATH
    original_env = os.environ.get("JOVIA_TONE_CONFIG")
    try:
        tone_profile_module.CONFIG_PATH = config_path
        os.environ["JOVIA_TONE_CONFIG"] = json.dumps({"tone_defaults": {"warmth_bias": 0.9}})
        tone_profile_module.load_tone_config.cache_clear()
        merged = tone_profile_module.load_tone_config()
        assert merged["tone_defaults"]["warmth_bias"] == 0.9
        assert merged["tone_defaults"]["uncertainty_default"] == 0.1
    finally:
        tone_profile_module.CONFIG_PATH = original
        tone_profile_module.load_tone_config.cache_clear()
        if original_env is None:
            os.environ.pop("JOVIA_TONE_CONFIG", None)
        else:
            os.environ["JOVIA_TONE_CONFIG"] = original_env
