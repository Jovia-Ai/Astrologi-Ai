from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.narrative.voice_guardrails_tr import validate_life_chapter_selected_meaning


class ChapterType(str, Enum):
    SATURN_RETURN = "saturn_return"
    JUPITER_RETURN = "jupiter_return"
    NODAL_RETURN = "nodal_return"
    NODAL_ACTIVATION = "nodal_activation"
    PROFECTION_YEAR = "profection_year"
    PROGRESSED_LUNATION = "progressed_lunation"
    SOLAR_RETURN_THEME = "solar_return_theme"
    OUTER_PLANET_ANGLE_HIT = "outer_planet_angle_hit"
    ECLIPSE_ACTIVATION = "eclipse_activation"
    MAJOR_TRANSIT_CHAPTER = "major_transit_chapter"
    STRUCTURAL_NATAL_CHAPTER = "structural_natal_chapter"


class ChapterPriority(str, Enum):
    LIFE_CHAPTER = "life_chapter"
    MAJOR_PERIOD = "major_period"
    SUPPORTING_PERIOD = "supporting_period"


class ChapterConfidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ChapterPhase(str, Enum):
    APPROACHING = "approaching"
    FIRST_PASS = "first_pass"
    RETROGRADE_REVIEW = "retrograde_review"
    FINAL_PASS = "final_pass"
    INTEGRATING = "integrating"
    BACKGROUND = "background"


class ActivatedNatalFactor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["planet", "angle", "node", "house", "ruler", "promise"]
    id: str

    @field_validator("id")
    @classmethod
    def _validate_id(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("activated_natal_factors[].id must be non-empty")
        return token


class LifeChapterEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    factor: str
    role: str
    explanation: str

    @field_validator("factor", "role", "explanation")
    @classmethod
    def _validate_text(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("evidence fields must be non-empty")
        return token

    @field_validator("role")
    @classmethod
    def _validate_role(cls, value: str) -> str:
        token = str(value or "").strip()
        allowed = {
            "return",
            "activation",
            "natal_context",
            "axis_overlap",
            "semantic_focus_support",
            "suppression_guard",
            "house_context",
            "dispositor_context",
            "pattern_structure",
        }
        if token not in allowed:
            raise ValueError(f"evidence.role must be one of {sorted(allowed)}")
        return token


class SuppressedReading(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reading: str
    reason: str

    @field_validator("reading", "reason")
    @classmethod
    def _validate_text(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("suppressed_readings fields must be non-empty")
        return token


class LifeChapterSemanticFocus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary: str
    secondary: list[str] = Field(default_factory=list)
    not_this: list[str] = Field(default_factory=list)

    @field_validator("primary")
    @classmethod
    def _validate_primary(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("semantic_focus.primary must be non-empty")
        return token


class LifeChapterDomainOwnership(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary_domain: str
    secondary_domains: list[str] = Field(default_factory=list)
    rationale: str

    @field_validator("primary_domain", "rationale")
    @classmethod
    def _validate_required_text(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("domain_ownership fields must be non-empty")
        return token


class LifeChapterRendererHandoff(BaseModel):
    model_config = ConfigDict(extra="forbid")

    human_scene: str
    core_contrast: str
    chapter_weight: str
    chart_specific_anchor: str
    voice_register: str
    avoid_readings: list[str] = Field(default_factory=list)

    @field_validator("human_scene", "core_contrast", "chapter_weight", "chart_specific_anchor", "voice_register")
    @classmethod
    def _validate_required_text(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("renderer_handoff fields must be non-empty")
        return token


class LifeChapterVoiceHints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    valence_mode: str
    intensity_mode: str
    rhetorical_frame: str | None = None
    tone: str | None = None

    @field_validator("valence_mode", "intensity_mode")
    @classmethod
    def _validate_required_text(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("voice_hints valence/intensity must be non-empty")
        return token

    @field_validator("rhetorical_frame", "tone")
    @classmethod
    def _validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        token = str(value).strip()
        return token or None


class LifeChapterNatalArchitectureAnchor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    human: str
    evidence: list[str] = Field(default_factory=list)

    @field_validator("label", "human")
    @classmethod
    def _validate_required_text(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("natal_architecture_anchor fields must be non-empty")
        return token

    @model_validator(mode="after")
    def _validate_evidence(self) -> "LifeChapterNatalArchitectureAnchor":
        if not self.evidence:
            raise ValueError("natal_architecture_anchor.evidence must be present and non-empty")
        return self


class LifeChapterScenePriorityItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene: str
    priority: Literal["primary", "secondary", "supporting"]

    @field_validator("scene")
    @classmethod
    def _validate_scene(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("scene_priority[].scene must be non-empty")
        return token


class LifeChapterTimeWindow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: str
    peak: str | None = None
    end: str

    @field_validator("start", "end")
    @classmethod
    def _validate_required(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("time_window.start/end must be non-empty")
        return token

    @field_validator("peak")
    @classmethod
    def _validate_optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        token = str(value).strip()
        return token or None


class LifeChapter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal["life_chapter_v1"] = "life_chapter_v1"
    chapter_id: str
    chapter_type: ChapterType
    domain: str
    spine_line: str | None = None
    time_window: LifeChapterTimeWindow
    phase: ChapterPhase
    activated_natal_factors: list[ActivatedNatalFactor] = Field(default_factory=list)
    core_question: str
    selected_meaning: str
    selected_meaning_family: str
    semantic_focus: LifeChapterSemanticFocus
    domain_ownership: LifeChapterDomainOwnership
    natal_architecture_anchor: LifeChapterNatalArchitectureAnchor
    scene_priority: list[LifeChapterScenePriorityItem]
    chapter_claim_strength: str
    shared_domain_priority: list[str] = Field(default_factory=list)
    trust_axis_anchor: str | None = None
    shared_vs_private_contrast: str | None = None
    structural_pressure_model: str | None = None
    apex_release_point: str | None = None
    renderer_handoff: LifeChapterRendererHandoff
    evidence: list[LifeChapterEvidence]
    suppressed_readings: list[SuppressedReading]
    suppressed_surface_readings: list[SuppressedReading]
    voice_hints: LifeChapterVoiceHints
    priority: ChapterPriority
    confidence: ChapterConfidence
    debug: dict[str, Any] = Field(default_factory=dict)

    @field_validator("chapter_id", "domain", "core_question", "selected_meaning_family", "chapter_claim_strength")
    @classmethod
    def _validate_required_text(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("required text field must be non-empty")
        return token

    @field_validator("spine_line")
    @classmethod
    def _validate_spine_line(cls, value: str | None) -> str | None:
        if value is None:
            return None
        token = str(value).strip()
        return token or None

    @field_validator("trust_axis_anchor", "shared_vs_private_contrast", "structural_pressure_model", "apex_release_point")
    @classmethod
    def _validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        token = str(value).strip()
        return token or None

    @field_validator("selected_meaning")
    @classmethod
    def _validate_selected_meaning(cls, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            raise ValueError("selected_meaning must be non-empty")
        issues = validate_life_chapter_selected_meaning(token)
        if issues:
            codes = ", ".join(issue["code"] for issue in issues)
            raise ValueError(f"selected_meaning failed life chapter guardrails: {codes}")
        return token

    @model_validator(mode="after")
    def _validate_required_lists(self) -> "LifeChapter":
        if not self.evidence:
            raise ValueError("evidence must be present and non-empty")
        if not self.suppressed_readings:
            raise ValueError("suppressed_readings must be present and non-empty")
        if not self.suppressed_surface_readings:
            raise ValueError("suppressed_surface_readings must be present and non-empty")
        if not self.scene_priority:
            raise ValueError("scene_priority must be present and non-empty")
        return self
