"""Canonical, immutable contracts for the editorial content asset registry.

R3A foundation. This module declares the *expression/presentation* contract for
reviewed editorial content assets. It deliberately holds NO meaning authority:
every asset's ``meaning_authority`` must remain ``"none"``. Meaning stays with
chart placement keys / SHOU semantic owners; presentation stays with declared
card/slide contracts; this layer only classifies reviewed editorial expression.

Pure data + enums. No runtime side effects, no imports from mobile, no SHOU
selection, no public payload attachment.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

# ── Allowed enums (task section C) ────────────────────────────────────────────
CONTENT_KINDS: frozenset[str] = frozenset({
    "planet_sign",
    "planet_house",
    "ascendant_sign",
    "aspect",
    "ruler_tone",
    "trait_line",
    "shadow_line",
    "gift_line",
    "supporting_copy",
    "synthesis_narrative",
    "mobile_fallback",
    "internal_preview",
})

CLASSIFICATIONS: frozenset[str] = frozenset({
    "FREE_MODULAR_READY",
    "FREE_MODULAR_NEEDS_EDIT",
    "PREMIUM_SYNTHESIS_ONLY",
    "SUPPORTING_COPY_ONLY",
    "DUPLICATE_OR_SUPERSEDED",
    "UNSAFE_OR_UNSUPPORTED",
    "MISSING_OWNER",
    "UNKNOWN",
})

PRESENTATION_MODES: frozenset[str] = frozenset({
    "single_card",
    "multi_slide",
    "long_read",
})

SLIDE_ROLES: frozenset[str] = frozenset({
    "recognition",
    "lived_pattern",
    "mechanism",
    "tension",
    "capacity",
    "context",
    "origin",
    "proof",
})

MEANING_AUTHORITIES: frozenset[str] = frozenset({"none"})
EXPRESSION_AUTHORITIES: frozenset[str] = frozenset(
    {"editorial_library", "supporting_copy", "superseded", "none"}
)
PRESENTATION_AUTHORITIES: frozenset[str] = frozenset({"asset_contract", "none"})

# Classifications that may never be part of the narrow Free launch.
NON_LAUNCH_CLASSIFICATIONS: frozenset[str] = frozenset({
    "DUPLICATE_OR_SUPERSEDED",
    "UNSAFE_OR_UNSUPPORTED",
    "MISSING_OWNER",
    "UNKNOWN",
})

# content_kinds that represent SHOU/internal-preview or mobile mock surfaces and
# therefore must never be declared Free editorial truth / canonical meaning.
INTERNAL_PREVIEW_KINDS: frozenset[str] = frozenset({"internal_preview"})
MOBILE_FALLBACK_KINDS: frozenset[str] = frozenset({"mobile_fallback"})


@dataclass(frozen=True)
class AssetSource:
    path: str
    symbol_or_family: str
    content_hash: str | None = None


@dataclass(frozen=True)
class AssetAuthority:
    meaning_authority: str
    expression_authority: str
    presentation_authority: str


@dataclass(frozen=True)
class AssetPresentation:
    mode: str
    min_slides: int
    max_slides: int
    allowed_roles: Tuple[str, ...]


@dataclass(frozen=True)
class EditorialContentAssetV1:
    """Immutable editorial content asset contract (one audited family)."""

    asset_id: str
    registry_version: str
    locale: str
    version: str
    content_kind: str
    primary_key: str
    domain: str
    source: AssetSource
    authority: AssetAuthority
    classification: str
    is_primary_owner: bool
    launch_eligible: bool
    allowed_tiers: Tuple[str, ...]
    allowed_surfaces: Tuple[str, ...]
    prohibited_surfaces: Tuple[str, ...]
    presentation: AssetPresentation
    status: str
    supersedes: Tuple[str, ...] = field(default_factory=tuple)
    notes: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RegistryValidationResult:
    ok: bool
    errors: Tuple[str, ...]
    checked: int


@dataclass(frozen=True)
class RegistrySummary:
    classified_asset_count: int
    free_ready_asset_count: int
    premium_only_asset_count: int
    unknown_unowned_asset_count: int
    slide_mode_distribution: Tuple[Tuple[str, int], ...]
    classification_distribution: Tuple[Tuple[str, int], ...]
    launch_eligible_count: int


def asset_from_mapping(data: dict) -> EditorialContentAssetV1:
    """Build an immutable asset from a registry JSON mapping (no mutation)."""
    src = data["source"]
    auth = data["authority"]
    pres = data["presentation"]
    return EditorialContentAssetV1(
        asset_id=str(data["asset_id"]),
        registry_version=str(data["registry_version"]),
        locale=str(data["locale"]),
        version=str(data.get("version", "v1")),
        content_kind=str(data["content_kind"]),
        primary_key=str(data["primary_key"]),
        domain=str(data["domain"]),
        source=AssetSource(
            path=str(src["path"]),
            symbol_or_family=str(src["symbol_or_family"]),
            content_hash=src.get("content_hash"),
        ),
        authority=AssetAuthority(
            meaning_authority=str(auth["meaning_authority"]),
            expression_authority=str(auth["expression_authority"]),
            presentation_authority=str(auth["presentation_authority"]),
        ),
        classification=str(data["classification"]),
        is_primary_owner=bool(data["is_primary_owner"]),
        launch_eligible=bool(data["launch_eligible"]),
        allowed_tiers=tuple(data["allowed_tiers"]),
        allowed_surfaces=tuple(data["allowed_surfaces"]),
        prohibited_surfaces=tuple(data["prohibited_surfaces"]),
        presentation=AssetPresentation(
            mode=str(pres["mode"]),
            min_slides=int(pres["min_slides"]),
            max_slides=int(pres["max_slides"]),
            allowed_roles=tuple(pres["allowed_roles"]),
        ),
        status=str(data["status"]),
        supersedes=tuple(data.get("supersedes", ())),
        notes=tuple(data.get("notes", ())),
    )
