#!/usr/bin/env python3

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PILOT_PATH = ROOT / "backend" / "app" / "pilot" / "identity_language.py"
spec = importlib.util.spec_from_file_location("pilot.identity_language", PILOT_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules["pilot.identity_language"] = module
spec.loader.exec_module(module)  # type: ignore
build_identity_pilot = module.build_identity_pilot

PHASE2_SAMPLE = {
    "slots": {
        "cause": {"text": "özgün bir iç ses olduğun", "intent": "origin"},
        "mechanism": {"text": "dengeyi sürekli olarak yeniden kurmaya", "intent": "regulation"},
        "effect": {"text": "sessiz ama kararlı bir duruş", "intent": "externalization"},
        "shadow": {"text": "fazla kontrolü kaybetme korkusu", "intent": "overcompensation"},
        "potential": {"text": "yeniden doğmuş bir çarpıcı güç", "intent": "integration"},
    }
}

REGULATION_SAMPLE = {
    "tension_type": "visibility_vs_control",
    "regulation_axis": "expression ↔ containment",
    "energy_pressure": 0.78,
    "slot_weights": {"mechanism": 0.23, "effect": 0.26, "shadow": 0.32, "potential": 0.19},
    "slot_permissions": ["mechanism", "shadow", "potential"],
}

if __name__ == "__main__":
    narrative = build_identity_pilot(PHASE2_SAMPLE["slots"], REGULATION_SAMPLE)
    print(narrative)
