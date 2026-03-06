from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

ChartKind = Literal[
    "natal",
    "synastry",
    "composite",
    "davison",
    "transit",
    "transit_overlay",
    "progressed_natal",
    "progressed_composite",
    "progressed_synastry",
]

Technique = Literal["secondary_progression", "solar_arc"]


@dataclass(frozen=True)
class ChartInputRef:
    name: str  # "partner_a" | "partner_b" etc.
    data: Dict[str, Any]  # your existing birth input or precomputed chart input


@dataclass(frozen=True)
class ChartRequest:
    kind: ChartKind
    tz: str
    date: Optional[str] = None  # YYYY-MM-DD (for transits/progressions)
    technique: Optional[Technique] = None
    a: Optional[ChartInputRef] = None
    b: Optional[ChartInputRef] = None
    options: Optional[Dict[str, Any]] = None
