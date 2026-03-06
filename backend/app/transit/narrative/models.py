from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

BlockType = Literal[
    "alert",
    "daily_energy",
    "core_theme",
    "challenge",
    "support",
    "long_term",
    "clarity",
    "best_time_primary",
    "best_time_list",
    "event_list_preview",
]
Horizon = Literal["day", "week", "month", "year"]


@dataclass
class CopyBundle:
    title: str
    short: str
    medium: str
    long: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "short": self.short,
            "medium": self.medium,
            "long": self.long,
        }


@dataclass
class UIBlock:
    id: str
    type: BlockType
    horizon: Horizon
    intensity: float
    domains: List[str] = field(default_factory=list)
    copy: CopyBundle = field(default_factory=lambda: CopyBundle("", "", "", ""))
    why: List[str] = field(default_factory=list)
    cta: Optional[Dict[str, Any]] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "horizon": self.horizon,
            "intensity": round(max(0.0, min(1.0, float(self.intensity or 0.0))), 3),
            "domains": self.domains,
            "copy": self.copy.to_dict(),
            "why": self.why,
        }
        if self.cta:
            payload["cta"] = self.cta
        if self.meta:
            payload["meta"] = self.meta
        return payload
