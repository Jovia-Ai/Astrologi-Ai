from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .evidence import EvidenceLayer, EvidenceRole

PromiseDomain = Literal[
    "identity",
    "emotional_security",
    "relationship",
    "money_self_worth",
    "communication_learning",
    "career_visibility",
    "home_family",
    "desire_conflict",
    "health_rhythm",
    "spiritual_meaning",
    "growth_shadow",
]

Centrality = Literal["core", "major", "supporting", "minor"]
ContradictionCentrality = Literal["primary", "secondary", "minor"]
Stability = Literal["lifelong", "developmental", "situational"]
NodeStatus = Literal["active", "shadow", "suppressed"]
CharacterPatternType = Literal[
    "temperament",
    "defense",
    "attachment_style",
    "expression_style",
    "ambition_style",
    "regulation_style",
    "visibility_style",
]
SpineLineKey = Literal[
    "primary_identity_line",
    "emotional_regulation_line",
    "relational_line",
    "work_visibility_line",
    "shadow_protection_line",
    "growth_integration_line",
]
PlanetConditionType = Literal[
    "domicile_condition",
    "angularity_condition",
    "visibility_condition",
    "retrograde_condition",
    "luminary_condition",
]
RouteStrength = Literal["primary", "secondary", "supporting"]
AspectPatternType = Literal[
    "stellium",
    "t_square",
    "grand_trine",
    "kite",
    "opposition_bridge",
    "conjunction_cluster",
]


class NatalEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    factor: str
    technical: str
    humanized: str
    layer: EvidenceLayer
    role: EvidenceRole
    source: str | None = None
    weight: float | None = None
    source_ref: str | None = None


class NatalPromiseNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    domain: PromiseDomain
    theme: str
    centrality: Centrality
    stability: Stability
    evidence: list[NatalEvidence]
    psychological_pattern: str
    potential: str
    shadow: str | None = None
    growth_path: str
    linked_character_patterns: list[str] = Field(default_factory=list)
    linked_contradictions: list[str] = Field(default_factory=list)
    status: NodeStatus = "active"


class CharacterPatternNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    pattern_type: CharacterPatternType
    title: str
    description: str
    evidence: list[NatalEvidence]
    linked_promises: list[str] = Field(default_factory=list)
    linked_contradictions: list[str] = Field(default_factory=list)
    status: NodeStatus = "active"


class ContradictionNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    polarity_a: str
    polarity_b: str
    centrality: ContradictionCentrality
    evidence: list[NatalEvidence]
    integration_path: str
    linked_promises: list[str] = Field(default_factory=list)
    status: NodeStatus = "active"


class PlanetConditionNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    planet: str
    condition_type: PlanetConditionType
    summary: str
    evidence: list[NatalEvidence]
    linked_promises: list[str] = Field(default_factory=list)
    linked_patterns: list[str] = Field(default_factory=list)
    status: NodeStatus = "active"


class DispositorRouteNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    origin: str
    terminal: str
    route: list[str]
    strength: RouteStrength
    summary: str
    evidence: list[NatalEvidence]
    linked_promises: list[str] = Field(default_factory=list)
    status: NodeStatus = "active"


class HouseRulerRouteNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    house_key: str
    ruler: str
    target_house: int | None = None
    summary: str
    evidence: list[NatalEvidence]
    linked_promises: list[str] = Field(default_factory=list)
    status: NodeStatus = "active"


class AspectPatternNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    pattern_type: AspectPatternType
    summary: str
    participating_bodies: list[str] = Field(default_factory=list)
    evidence: list[NatalEvidence]
    linked_promises: list[str] = Field(default_factory=list)
    linked_contradictions: list[str] = Field(default_factory=list)
    status: NodeStatus = "active"


class ChartSpineLine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: SpineLineKey
    node_id: str | None = None
    title: str | None = None
    summary: str | None = None
    evidence: list[NatalEvidence] = Field(default_factory=list)
    linked_node_ids: list[str] = Field(default_factory=list)
    source_candidates: list[str] = Field(default_factory=list)


class ChartSpine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary_identity_line: ChartSpineLine = Field(
        default_factory=lambda: ChartSpineLine(key="primary_identity_line")
    )
    emotional_regulation_line: ChartSpineLine = Field(
        default_factory=lambda: ChartSpineLine(key="emotional_regulation_line")
    )
    relational_line: ChartSpineLine = Field(
        default_factory=lambda: ChartSpineLine(key="relational_line")
    )
    work_visibility_line: ChartSpineLine = Field(
        default_factory=lambda: ChartSpineLine(key="work_visibility_line")
    )
    shadow_protection_line: ChartSpineLine = Field(
        default_factory=lambda: ChartSpineLine(key="shadow_protection_line")
    )
    growth_integration_line: ChartSpineLine = Field(
        default_factory=lambda: ChartSpineLine(key="growth_integration_line")
    )


class CanonicalStructuralState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    planet_conditions: list[PlanetConditionNode] = Field(default_factory=list)
    dispositor_routes: list[DispositorRouteNode] = Field(default_factory=list)
    house_ruler_routes: list[HouseRulerRouteNode] = Field(default_factory=list)
    aspect_patterns: list[AspectPatternNode] = Field(default_factory=list)


class CanonicalDebugTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    legacy_sources_used: list[str] = Field(default_factory=list)
    source_trace: dict[str, list[str]] = Field(default_factory=dict)
    evidence_count: int = 0
    suppressed_candidates: list[dict[str, Any]] = Field(default_factory=list)
    conflicting_evidence: list[dict[str, Any]] = Field(default_factory=list)
    fallback_used: bool = False
    legacy_branch_overlap: list[dict[str, Any]] = Field(default_factory=list)
    golden_expectation_misses: list[dict[str, Any]] = Field(default_factory=list)


class CanonicalNatalStateV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chart_id: str
    engine_version: str = "natal-core-v1"
    schema_version: str = "canonical_natal_state_v1"
    house_system: str = "placidus"
    model: str = "hybrid_psychological_classical"
    structural_state: CanonicalStructuralState = Field(default_factory=CanonicalStructuralState)
    core_promises: list[NatalPromiseNode] = Field(default_factory=list)
    character_patterns: list[CharacterPatternNode] = Field(default_factory=list)
    contradictions: list[ContradictionNode] = Field(default_factory=list)
    chart_spine: ChartSpine = Field(default_factory=ChartSpine)
    meaning_graph: dict[str, Any] = Field(default_factory=dict)
    debug: CanonicalDebugTrace | None = None

