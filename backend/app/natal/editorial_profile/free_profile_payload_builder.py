"""Free V1 editorial profile payload builder (R4).

Resolves the deterministic placement plan through the registry/adapter/projection
(R3A/R3B/R3C) into an ownership-safe additive payload. Omits unresolved keys with
typed diagnostics; never substitutes, borrows, or generates prose. No SHOU, no
Premium, no LLM.
"""
from __future__ import annotations

from typing import Any, Sequence

from .free_profile_plan_builder import build_free_placement_plan
from .free_profile_payload_contracts import (
    CONTENT_SOURCE,
    PROFILE_VERSION,
    PUBLIC_BLOCK_ROLES,
    SELECTION_MODE,
    FreeChip,
    FreeContentBlock,
    FreeEditorialCard,
    FreeEditorialProfile,
    FreeOwnership,
    FreeProfileDiagnostics,
    KeyOmission,
)
from .shadow_card_contracts import ShadowEditorialCard, ShadowProjectionFailure
from .shadow_card_projection import project_shadow_card

# Failure reasons that mean the editorial content is absent (omission, not block).
_MISSING_REASONS = frozenset({"ASSET_NOT_FOUND", "CONTENT_INCOMPLETE"})


def _card_id(planet: str, placement_type: str, primary_key: str) -> str:
    if placement_type == "planet_sign":
        value = primary_key[len(planet) + 1:]
        return f"free.{planet}.sign.{value}"
    value = primary_key.split("_house_", 1)[1]
    return f"free.{planet}.house.{value}"


def _chips_from_title(title: str, primary_key: str) -> tuple[FreeChip, ...]:
    # exact placement chips drawn only from this asset's own label_tr
    parts = title.strip().split(" ", 1)
    chips = [FreeChip(label=parts[0], source=primary_key)]
    if len(parts) > 1 and parts[1].strip():
        chips.append(FreeChip(label=parts[1].strip(), source=primary_key))
    return tuple(chips)


def _content_blocks(card: ShadowEditorialCard) -> tuple[FreeContentBlock, ...]:
    blocks = []
    for b in card.content.blocks:
        if b.role not in PUBLIC_BLOCK_ROLES:
            continue  # excludes origin / background_hint from public Free V1
        blocks.append(FreeContentBlock(role=b.role, text=b.text, source_field=b.source_field))
    return tuple(blocks)


def build_free_editorial_profile(
    planets: Sequence[Any], *, locale: str = "tr-TR"
) -> FreeEditorialProfile:
    plan = build_free_placement_plan(planets)
    cards: list[FreeEditorialCard] = []
    requested: list[str] = []
    resolved: list[str] = []
    missing: list[KeyOmission] = []
    blocked: list[KeyOmission] = []

    for plan_card in plan.cards:
        key = plan_card.primary_key
        requested.append(key)
        # Universal Free eligibility surface is "identity"; domain is a separate
        # presentation bucket assigned by the plan.
        result = project_shadow_card(key, tier="free", surface="identity")
        if isinstance(result, ShadowProjectionFailure):
            omission = KeyOmission(primary_key=key, reason=result.reason)
            if result.reason in _MISSING_REASONS:
                missing.append(omission)
            else:
                blocked.append(omission)
            continue
        resolved.append(key)
        cards.append(FreeEditorialCard(
            card_id=_card_id(plan_card.planet, plan_card.placement_type, key),
            ordinal=plan_card.ordinal,
            domain=plan_card.domain,
            planet=plan_card.planet,
            placement_type=plan_card.placement_type,
            primary_key=key,
            asset_id=result.asset_id,
            title=result.content.title,
            summary=result.content.summary,
            content_blocks=_content_blocks(result),
            chips=_chips_from_title(result.content.title, key),
            ownership=FreeOwnership(
                meaning_owner=f"natal_placement:{key}",
                expression_owner=result.asset_id,
                presentation_owner=PROFILE_VERSION,
                status="aligned",
            ),
        ))

    # Re-ordinalize the resolved cards to a contiguous 0..n sequence (omissions removed).
    cards = [
        _replace_ordinal(c, i) for i, c in enumerate(cards)
    ]
    return FreeEditorialProfile(
        version=PROFILE_VERSION,
        locale=locale,
        content_source=CONTENT_SOURCE,
        selection_mode=SELECTION_MODE,
        cards=tuple(cards),
        diagnostics=FreeProfileDiagnostics(
            requested_keys=tuple(requested),
            resolved_keys=tuple(resolved),
            missing_keys=tuple(missing),
            blocked_keys=tuple(blocked),
            fallback_used=False,
        ),
    )


def _replace_ordinal(card: FreeEditorialCard, ordinal: int) -> FreeEditorialCard:
    import dataclasses
    return dataclasses.replace(card, ordinal=ordinal)


def build_free_editorial_profile_public(
    planets: Sequence[Any] | None, *, locale: str = "tr-TR"
) -> dict | None:
    """Public additive dict for attachment; None when no planet facts present."""
    if not planets:
        return None
    profile = build_free_editorial_profile(planets, locale=locale)
    return profile.to_public_dict()["editorial_profile"]
