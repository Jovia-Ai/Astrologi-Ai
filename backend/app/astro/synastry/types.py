from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PartnerChart:
    positions: Dict[str, float]


@dataclass
class PartnerPayload:
    chart: PartnerChart


@dataclass
class SynastryAnalyzeOptions:
    include_debug: bool = False
    bodies: Optional[List[str]] = None


@dataclass
class SynastryAnalyzePayload:
    partner_a: PartnerPayload
    partner_b: PartnerPayload
    options: Optional[SynastryAnalyzeOptions] = None
