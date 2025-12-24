#!/usr/bin/env python3

"""Quick runner that feeds the locked identity slot descriptors into the validator-driven narrative builder."""

from pathlib import Path
from types import SimpleNamespace
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

APP_MODULE = types.ModuleType("app")
APP_MODULE.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = APP_MODULE

from app.builders.narrative_builder import JoviaSemanticNarrativeBuilder

LOCKED_IDENTITY_SLOTS = {
    "core_wound": "yetersizlik hissine bağlı içsel baskı",
    "inner_tension": "kontrol ihtiyacı ile görünür olma arzusu arasındaki gerilim",
    "behavioral_reflex": "öz-değeri performans üzerinden dengeleme eğilimi",
    "emotional_cost": "sürekli kendini izleme ve yargılama yükü",
    "awareness_key": "kusursuzluk yerine yeterliliğe alan açma farkındalığı",
    "growth_potential": "sorumluluğu öz-değerle hizalayabilen liderlik tonu",
}

SLOT_MAPPING = {
    "cause": "core_wound",
    "mechanism": "inner_tension",
    "effect": "behavioral_reflex",
    "shadow": "emotional_cost",
}


def _build_combined_potential() -> str:
    """Combine the awareness key and growth potential so the skeleton can narrate both scenes."""
    awareness = LOCKED_IDENTITY_SLOTS.get("awareness_key")
    growth = LOCKED_IDENTITY_SLOTS.get("growth_potential")
    parts = [part for part in (awareness, growth) if part]
    return " ve ".join(parts)


def _build_identity_fragments() -> dict:
    slots: dict[str, dict[str, str]] = {}
    for slot_name, descriptor_key in SLOT_MAPPING.items():
        descriptor = LOCKED_IDENTITY_SLOTS.get(descriptor_key)
        if not descriptor:
            continue
        slots[slot_name] = {"text": descriptor}
    potential_text = _build_combined_potential()
    if potential_text:
        slots["potential"] = {"text": potential_text}
    anchor = slots.get("cause")
    return {"identity": {"slots": slots, "anchor": anchor}}


def _build_builder_context(fragments: dict) -> SimpleNamespace:
    return SimpleNamespace(
        composites=[],
        patterns={},
        upper_meanings=[],
        meta_info={},
        dispositor_flow={},
        axis_activation={"axis_tension": "medium"},
        guidance={"active_domains": ["identity"]},
        fragments=fragments,
        regulations={"identity": {"tension_type": "visibility_vs_control"}},
        activation_sensitivity={},
    )


def main() -> None:
    fragments = _build_identity_fragments()
    context = _build_builder_context(fragments)
    builder = JoviaSemanticNarrativeBuilder(context)
    narrative = builder.build()
    print(narrative.get("identity", "No identity narrative produced."))


if __name__ == "__main__":
    main()
