from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal

LensKey = Literal[
    "general",
    "relationship",
    "marriage",
    "business",
    "career",
    "money",
    "health",
    "home",
]

IntentKey = str
TagKey = str


@dataclass(frozen=True)
class RuleAdd:
    domains: List[str] = field(default_factory=list)
    intents: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    weight: float = 0.0
    priority: int = 0


@dataclass(frozen=True)
class Rule:
    match: str
    add: RuleAdd


@dataclass
class LensEvidence:
    event_ids: List[str] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)


@dataclass
class LensEnrichment:
    domains: List[str] = field(default_factory=list)
    intents: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    weight_sum: float = 0.0
    priority: int = 0
    evidence: LensEvidence = field(default_factory=LensEvidence)


@dataclass
class ScoredLens:
    score_by_lens: Dict[str, float] = field(default_factory=dict)
    score_by_intent: Dict[str, float] = field(default_factory=dict)
