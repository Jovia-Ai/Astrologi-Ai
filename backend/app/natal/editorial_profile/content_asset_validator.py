"""Read-only validator for the editorial content asset registry (R3A).

Implements the 14 required invariants (task section E). Pure function over a
sequence of immutable assets; returns a RegistryValidationResult. No mutation,
no runtime side effects.
"""
from __future__ import annotations

import os
from collections import defaultdict
from typing import Iterable, Sequence

from .content_asset_contracts import (
    CLASSIFICATIONS,
    CONTENT_KINDS,
    EditorialContentAssetV1,
    INTERNAL_PREVIEW_KINDS,
    MOBILE_FALLBACK_KINDS,
    NON_LAUNCH_CLASSIFICATIONS,
    PRESENTATION_MODES,
    RegistryValidationResult,
    SLIDE_ROLES,
)

# Repo root: this file is backend/app/natal/editorial_profile/content_asset_validator.py
# parents[4] == repo root (worktree).
_REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)


def _source_exists(asset: EditorialContentAssetV1) -> bool:
    return os.path.exists(os.path.join(_REPO_ROOT, asset.source.path))


def validate_assets(
    assets: Sequence[EditorialContentAssetV1],
    *,
    repo_root: str | None = None,
) -> RegistryValidationResult:
    root = os.path.abspath(repo_root) if repo_root else _REPO_ROOT
    errors: list[str] = []

    # ── Enum / shape sanity (foundation for the rest) ────────────────────────
    for a in assets:
        if a.classification not in CLASSIFICATIONS:
            errors.append(f"{a.asset_id}: unknown classification {a.classification!r}")
        if a.content_kind not in CONTENT_KINDS:
            errors.append(f"{a.asset_id}: unknown content_kind {a.content_kind!r}")
        if a.presentation.mode not in PRESENTATION_MODES:
            errors.append(f"{a.asset_id}: unknown presentation.mode {a.presentation.mode!r}")
        for role in a.presentation.allowed_roles:
            if role not in SLIDE_ROLES:
                errors.append(f"{a.asset_id}: unknown slide role {role!r}")

    # 1. duplicate asset_id
    seen: dict[str, int] = defaultdict(int)
    for a in assets:
        seen[a.asset_id] += 1
    for asset_id, n in seen.items():
        if n > 1:
            errors.append(f"INV1 duplicate asset_id: {asset_id} x{n}")

    # 2. duplicate canonical primary ownership for same tier/surface unless versioned
    owners: dict[tuple[str, str, str], list[EditorialContentAssetV1]] = defaultdict(list)
    for a in assets:
        if not a.is_primary_owner:
            continue
        for tier in a.allowed_tiers:
            for surface in a.allowed_surfaces:
                owners[(a.primary_key, tier, surface)].append(a)
    for key, group in owners.items():
        if len(group) > 1:
            versions = {a.version for a in group}
            if len(versions) != len(group):
                ids = ", ".join(sorted(a.asset_id for a in group))
                errors.append(
                    f"INV2 duplicate canonical primary ownership for {key} "
                    f"without distinct versions: {ids}"
                )

    for a in assets:
        # 3. FREE_MODULAR_READY without exactly one primary key
        if a.classification == "FREE_MODULAR_READY":
            if not a.primary_key.strip() or not a.is_primary_owner:
                errors.append(f"INV3 {a.asset_id}: FREE_MODULAR_READY without one primary key/owner")

        # 4. Free asset with meaning_authority != none
        if "free" in a.allowed_tiers and a.authority.meaning_authority != "none":
            errors.append(
                f"INV4 {a.asset_id}: free asset has meaning_authority "
                f"{a.authority.meaning_authority!r} (must be none)"
            )

        # 5. PREMIUM_SYNTHESIS_ONLY asset in allowed_tiers == ['free']
        if a.classification == "PREMIUM_SYNTHESIS_ONLY" and "free" in a.allowed_tiers:
            errors.append(f"INV5 {a.asset_id}: PREMIUM_SYNTHESIS_ONLY is Free-eligible")

        # 6. MISSING_OWNER / UNKNOWN marked launch-eligible
        if a.classification in {"MISSING_OWNER", "UNKNOWN"} and a.launch_eligible:
            errors.append(f"INV6 {a.asset_id}: {a.classification} marked launch_eligible")

        # 7. single_card with more than one slide
        if a.presentation.mode == "single_card" and a.presentation.max_slides > 1:
            errors.append(
                f"INV7 {a.asset_id}: single_card with max_slides {a.presentation.max_slides}"
            )

        # 8. multi_slide with <1 or >3 slides for Free
        if a.presentation.mode == "multi_slide" and "free" in a.allowed_tiers:
            if a.presentation.min_slides < 1 or a.presentation.max_slides > 3:
                errors.append(
                    f"INV8 {a.asset_id}: Free multi_slide out of 1..3 "
                    f"({a.presentation.min_slides}..{a.presentation.max_slides})"
                )

        # 9. long_read assigned to the narrow Free launch
        if a.presentation.mode == "long_read" and a.launch_eligible:
            errors.append(f"INV9 {a.asset_id}: long_read marked launch_eligible (Free launch)")

        # 10. overlapping allowed/prohibited surfaces
        overlap = set(a.allowed_surfaces) & set(a.prohibited_surfaces)
        if overlap:
            errors.append(f"INV10 {a.asset_id}: surfaces overlap {sorted(overlap)}")

        # 11. source paths that do not exist
        if not os.path.exists(os.path.join(root, a.source.path)):
            errors.append(f"INV11 {a.asset_id}: source path missing {a.source.path}")

        # 12. SHOU renderer / internal-preview output declared Free editorial truth
        is_internal = (
            a.content_kind in INTERNAL_PREVIEW_KINDS
            or "internal_preview" in a.source.path
            or "shou_renderer" in a.source.path
            or "internal_typed_guidance_renderer" in a.source.path
        )
        if is_internal and (
            a.launch_eligible
            or "free" in a.allowed_tiers
            or a.authority.expression_authority == "editorial_library"
        ):
            errors.append(
                f"INV12 {a.asset_id}: SHOU/internal-preview source declared Free editorial truth"
            )

        # 13. mobile fallback / mock copy declared as canonical meaning
        is_mobile_fallback = (
            a.content_kind in MOBILE_FALLBACK_KINDS or a.source.path.startswith("mobile/")
        )
        if is_mobile_fallback and (
            a.authority.meaning_authority != "none" or a.is_primary_owner
        ):
            errors.append(
                f"INV13 {a.asset_id}: mobile fallback/mock declared canonical meaning/primary"
            )

        # 14. supporting-copy asset acting as primary owner
        if (
            a.authority.expression_authority == "supporting_copy"
            or a.classification == "SUPPORTING_COPY_ONLY"
        ) and a.is_primary_owner:
            errors.append(f"INV14 {a.asset_id}: supporting-copy asset acting as primary owner")

    return RegistryValidationResult(
        ok=not errors,
        errors=tuple(errors),
        checked=len(list(assets)),
    )
