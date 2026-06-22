"""Read-only access to the editorial content asset registry (R3A).

Dormant in R3A: this module is not imported by any runtime/public/mobile
consumer. It only loads and exposes the canonical registry JSON. No mutation,
no runtime side effects, no SHOU semantic selection, no public payload
attachment, no imports from mobile.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from functools import lru_cache
from typing import Tuple

from .content_asset_contracts import (
    EditorialContentAssetV1,
    RegistrySummary,
    RegistryValidationResult,
    asset_from_mapping,
)
from .content_asset_validator import validate_assets

# backend/app/natal/editorial_profile/ -> backend/
_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_REGISTRY_PATH = os.path.join(
    _BACKEND_ROOT, "content", "editorial", "free_v1", "content_asset_registry_tr_v1.json"
)


def registry_path() -> str:
    return _REGISTRY_PATH


@lru_cache(maxsize=1)
def _load_raw() -> dict:
    with open(_REGISTRY_PATH, encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def load_registry() -> Tuple[EditorialContentAssetV1, ...]:
    """Return all assets in deterministic (asset_id) order. Immutable tuple."""
    raw = _load_raw()
    assets = [asset_from_mapping(item) for item in raw["assets"]]
    assets.sort(key=lambda a: a.asset_id)
    return tuple(assets)


def get_asset(asset_id: str) -> EditorialContentAssetV1 | None:
    for asset in load_registry():
        if asset.asset_id == asset_id:
            return asset
    return None


def find_assets(primary_key: str, tier: str) -> Tuple[EditorialContentAssetV1, ...]:
    return tuple(
        a
        for a in load_registry()
        if a.primary_key == primary_key and tier in a.allowed_tiers
    )


def validate_registry() -> RegistryValidationResult:
    return validate_assets(load_registry(), repo_root=_repo_root())


def registry_summary() -> RegistrySummary:
    assets = load_registry()
    classification = Counter(a.classification for a in assets)
    modes = Counter(a.presentation.mode for a in assets)
    return RegistrySummary(
        classified_asset_count=len(assets),
        free_ready_asset_count=classification.get("FREE_MODULAR_READY", 0),
        premium_only_asset_count=classification.get("PREMIUM_SYNTHESIS_ONLY", 0),
        unknown_unowned_asset_count=(
            classification.get("MISSING_OWNER", 0) + classification.get("UNKNOWN", 0)
        ),
        slide_mode_distribution=tuple(sorted(modes.items())),
        classification_distribution=tuple(sorted(classification.items())),
        launch_eligible_count=sum(1 for a in assets if a.launch_eligible),
    )


def _repo_root() -> str:
    # backend/ -> repo root
    return os.path.abspath(os.path.join(_BACKEND_ROOT, ".."))
