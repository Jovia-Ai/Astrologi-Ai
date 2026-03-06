from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

Body = Literal[
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "node",
    "lilith",
    "chiron",
    "vertex",
    "fortune",
    "asc",
    "mc",
]

AspectName = Literal[
    "conjunction",
    "opposition",
    "trine",
    "square",
    "sextile",
    "quincunx",
]


@dataclass(frozen=True)
class ChartBody:
    body: Body
    longitude: float  # 0..360
    sign: str
    deg_in_sign: float
    formatted: str
    house: Optional[int] = None  # 1..12 if available


@dataclass(frozen=True)
class ChartAngle:
    body: Literal["asc", "mc"]
    longitude: float
    formatted: str


@dataclass(frozen=True)
class HouseCusp:
    house: int  # 1..12
    longitude: float
    formatted: str


@dataclass(frozen=True)
class AspectHit:
    a_body: Body
    b_body: Body
    aspect: AspectName
    orb_deg: float
    orb_text: str
    tightness: float  # 0..1
    intensity: Optional[float] = None
    friction: Optional[float] = None
    flow: Optional[float] = None


@dataclass(frozen=True)
class OverlayHit:
    body: Body
    longitude: float
    formatted: str
    in_house: int


@dataclass(frozen=True)
class ChartMeta:
    kind: str  # "natal" | "synastry" | "composite" | ...
    technique: Optional[str] = None
    reference_date: Optional[str] = None  # YYYY-MM-DD
    tz: Optional[str] = None
    notes: Optional[Dict[str, str]] = None


@dataclass(frozen=True)
class NormalizedChart:
    meta: ChartMeta
    bodies: List[ChartBody]
    angles: List[ChartAngle]
    houses: List[HouseCusp]
    aspects: List[AspectHit]
    overlays: Optional[Dict[str, List[OverlayHit]]] = None
