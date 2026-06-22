"""Immutable Free V1 editorial profile payload contracts (R4)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

PROFILE_VERSION = "free_editorial_profile_v1"
CONTENT_SOURCE = "reviewed_legacy_editorial_assets"
SELECTION_MODE = "deterministic_exact_placement"

# Free V1 public block roles (origin / background_hint excluded from public payload).
PUBLIC_BLOCK_ROLES: Tuple[str, ...] = ("recognition", "mechanism", "tension", "capacity")


@dataclass(frozen=True)
class FreeContentBlock:
    role: str
    text: str
    source_field: str


@dataclass(frozen=True)
class FreeChip:
    label: str
    source: str


@dataclass(frozen=True)
class FreeOwnership:
    meaning_owner: str
    expression_owner: str
    presentation_owner: str
    status: str


@dataclass(frozen=True)
class FreeEditorialCard:
    card_id: str
    ordinal: int
    domain: str
    planet: str
    placement_type: str
    primary_key: str
    asset_id: str
    title: str
    summary: str
    content_blocks: Tuple[FreeContentBlock, ...]
    chips: Tuple[FreeChip, ...]
    ownership: FreeOwnership


@dataclass(frozen=True)
class KeyOmission:
    primary_key: str
    reason: str


@dataclass(frozen=True)
class FreeProfileDiagnostics:
    requested_keys: Tuple[str, ...]
    resolved_keys: Tuple[str, ...]
    missing_keys: Tuple[KeyOmission, ...]
    blocked_keys: Tuple[KeyOmission, ...]
    fallback_used: bool


@dataclass(frozen=True)
class FreeEditorialProfile:
    version: str
    locale: str
    content_source: str
    selection_mode: str
    cards: Tuple[FreeEditorialCard, ...]
    diagnostics: FreeProfileDiagnostics

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "editorial_profile": {
                "version": self.version,
                "locale": self.locale,
                "content_source": self.content_source,
                "selection_mode": self.selection_mode,
                "cards": [
                    {
                        "card_id": c.card_id,
                        "ordinal": c.ordinal,
                        "domain": c.domain,
                        "planet": c.planet,
                        "placement_type": c.placement_type,
                        "primary_key": c.primary_key,
                        "asset_id": c.asset_id,
                        "title": c.title,
                        "summary": c.summary,
                        "content_blocks": [
                            {"role": b.role, "text": b.text, "source_field": b.source_field}
                            for b in c.content_blocks
                        ],
                        "chips": [{"label": ch.label, "source": ch.source} for ch in c.chips],
                        "ownership": {
                            "meaning_owner": c.ownership.meaning_owner,
                            "expression_owner": c.ownership.expression_owner,
                            "presentation_owner": c.ownership.presentation_owner,
                            "status": c.ownership.status,
                        },
                    }
                    for c in self.cards
                ],
                "diagnostics": {
                    "requested_keys": list(self.diagnostics.requested_keys),
                    "resolved_keys": list(self.diagnostics.resolved_keys),
                    "missing_keys": [
                        {"primary_key": o.primary_key, "reason": o.reason}
                        for o in self.diagnostics.missing_keys
                    ],
                    "blocked_keys": [
                        {"primary_key": o.primary_key, "reason": o.reason}
                        for o in self.diagnostics.blocked_keys
                    ],
                    "fallback_used": self.diagnostics.fallback_used,
                },
            }
        }
