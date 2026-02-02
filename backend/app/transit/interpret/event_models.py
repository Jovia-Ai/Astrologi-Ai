from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

ObjType = Literal["planet", "axis", "point"]


@dataclass(frozen=True)
class EventObj:
    key: str
    type: ObjType
    house: Optional[int] = None


@dataclass(frozen=True)
class EventTiming:
    is_peak: bool
    orb_deg: float
    is_applying: Optional[bool] = None
    peak_date: Optional[str] = None
    peak_ts: Optional[int] = None


@dataclass(frozen=True)
class LabelFull:
    mechanism: str
    advice: str


@dataclass(frozen=True)
class EventLabel:
    short: str
    where: Optional[str]
    short_plus: Optional[str] = None
    full: Optional[LabelFull] = None


@dataclass(frozen=True)
class EventMeta:
    id: str
    a: EventObj
    aspect: str
    b: EventObj
    timing: EventTiming
    label: Optional[EventLabel] = None
    context: Optional[Dict[str, Any]] = None
