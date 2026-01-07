from __future__ import annotations

import sys
import types
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.builders.narrative_builder import JoviaSemanticNarrativeBuilder
from app.engine.tone_apply import apply_tone
from app.engine.tone_profile import ToneProfile, compute_tone, DEFAULT_CONFIG, CONFIG_PATH


def test_tone_profile_upper_meaning_softens() -> None:
    base = compute_tone(
        {"energy_pressure": "high"},
        {"upper_meaning_allowed": True},
        {"score": 0.8},
        {"strain": 0.7, "resilience": 0.7, "uncertainty": 0.2},
    )
    softened = compute_tone(
        {"energy_pressure": "high"},
        {"upper_meaning_allowed": True},
        {"score": 0.8},
        {"strain": 0.7, "resilience": 0.7, "uncertainty": 0.2, "upper_meaning_used": True},
    )
    assert softened.intensity <= base.intensity
    assert softened.tempo <= base.tempo
    assert softened.warmth >= base.warmth


def test_apply_tone_certainty_low_adds_hedge() -> None:
    tone = ToneProfile(
        directness=0.4,
        warmth=0.5,
        intensity=0.4,
        certainty=0.2,
        tempo=0.4,
        distance=0.6,
    )
    text = "Bu harita, kimlik alaninda bir tema anlatir."
    toned = apply_tone(text, tone, section="recognition")
    assert toned
    assert "Bazen" not in toned


def test_apply_tone_certainty_high_strips_hedge() -> None:
    tone = ToneProfile(
        directness=0.4,
        warmth=0.5,
        intensity=0.4,
        certainty=0.9,
        tempo=0.4,
        distance=0.6,
    )
    text = "Bazen, bu yapi genelde boyle olabilir."
    toned = apply_tone(text, tone, section="experienced")
    assert "olabilir" not in toned.lower()


def test_apply_tone_shadow_uses_safe_template() -> None:
    tone = ToneProfile(
        directness=0.3,
        warmth=0.8,
        intensity=0.4,
        certainty=0.5,
        tempo=0.4,
        distance=0.6,
    )
    toned = apply_tone("denge kaybi riski", tone, section="shadow")
    assert "suc degil" in toned.lower()
    assert "denge kaybi riski" in toned.lower()


def test_apply_tone_directness_second_person() -> None:
    tone = ToneProfile(
        directness=0.8,
        warmth=0.4,
        intensity=0.4,
        certainty=0.6,
        tempo=0.4,
        distance=0.4,
    )
    toned = apply_tone("Bu harita, kimlik alaninda bir tema anlatir.", tone, section="recognition")
    assert toned.lower().startswith("senin haritan")


def test_tone_determinism() -> None:
    args = (
        {"energy_pressure": "medium"},
        {"upper_meaning_allowed": False},
        {"score": 0.4},
        {"strain": 0.2, "resilience": 0.5, "uncertainty": 0.3},
    )
    first = compute_tone(*args).to_dict()
    second = compute_tone(*args).to_dict()
    assert first == second


def test_tone_does_not_change_slot_selection() -> None:
    fragments = {
        "identity": {
            "slots": {
                "cause": {"text": "bir neden", "fragment_ref": "f1"},
                "mechanism": {"text": "bir mekanizma", "fragment_ref": "f2"},
                "effect": {"text": "bir etki", "fragment_ref": "f3"},
                "shadow": {"text": "bir golge", "fragment_ref": "f4"},
            }
        }
    }
    engine_result = SimpleNamespace(
        fragments=fragments,
        guidance={},
        regulations={},
        meaning_weighting={},
        meta_info={},
        axis_activation={},
        expression_profile={},
        composites=[],
        patterns={},
        upper_meanings=[],
        dispositor_flow={},
        activation_sensitivity={},
        narrative_anchor={},
        tone_enabled=True,
    )
    builder = JoviaSemanticNarrativeBuilder(engine_result)
    builder.build()
    selected_with_tone = dict(builder.narrative_debug_selected_slots)

    engine_result.tone_enabled = False
    builder_no_tone = JoviaSemanticNarrativeBuilder(engine_result)
    builder_no_tone.build()
    selected_without_tone = dict(builder_no_tone.narrative_debug_selected_slots)

    assert selected_with_tone == selected_without_tone


def test_tone_low_certainty_softens_templates() -> None:
    tone = ToneProfile(
        directness=0.4,
        warmth=0.5,
        intensity=0.4,
        certainty=0.2,
        tempo=0.4,
        distance=0.6,
    )
    text = "Deneyim duzeyinde, bir sey baskin bir psikolojik akistir."
    toned = apply_tone(text, tone, section="experienced")
    assert "akistir" not in toned.lower()
    assert "olabilir" in toned.lower()


def test_tone_config_fallback_on_bad_file(tmp_path: Path) -> None:
    bad_path = tmp_path / "tone.yaml"
    bad_path.write_text("not-json", encoding="utf-8")
    original = CONFIG_PATH
    try:
        import app.engine.tone_profile as tone_profile_module
        tone_profile_module.CONFIG_PATH = bad_path
        tone_profile_module.load_tone_config.cache_clear()
        config = tone_profile_module.load_tone_config()
        assert config == DEFAULT_CONFIG
    finally:
        tone_profile_module.CONFIG_PATH = original
        tone_profile_module.load_tone_config.cache_clear()
