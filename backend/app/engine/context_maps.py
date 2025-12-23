"""House context lookup for structural signal derivation."""
from __future__ import annotations

from typing import Dict

HOUSE_CONTEXT: Dict[int, Dict[str, str]] = {
    1: {"identity": "self_driven", "emotion": "immediate", "expression": "personal"},
    2: {"identity": "values_based", "emotion": "security_seek", "expression": "possessive"},
    3: {"identity": "curious", "emotion": "mentalized", "expression": "communicative"},
    4: {"identity": "rooted", "emotion": "private", "expression": "protective"},
    5: {"identity": "creative", "emotion": "playful", "expression": "performative"},
    6: {"identity": "service_oriented", "emotion": "practical", "expression": "helpful"},
    7: {"identity": "relational", "emotion": "reflective", "expression": "cooperative"},
    8: {"identity": "transforming", "emotion": "intense", "expression": "guarded"},
    9: {"identity": "meaning_seeking", "emotion": "explorative", "expression": "broadcasting"},
    10: {"identity": "visible", "emotion": "disciplined", "expression": "authoritative"},
    11: {"identity": "community", "emotion": "idealistic", "expression": "networked"},
    12: {"identity": "hidden", "emotion": "internalized", "expression": "private"},
}

DEFAULT_CONTEXT: Dict[str, str] = {"identity": "general", "emotion": "balanced", "expression": "neutral"}
