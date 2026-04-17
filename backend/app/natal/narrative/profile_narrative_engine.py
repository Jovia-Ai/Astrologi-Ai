from __future__ import annotations

import hashlib
import logging
import os
from typing import Any, Dict, Mapping, Optional

from .natal_selection_config import get_natal_selection_v3_config
from .profile_narrative_engine_legacy import build_profile_narrative_legacy
from .profile_narrative_engine_signature import build_profile_narrative_signature

logger = logging.getLogger(__name__)


_PROFILE_BLOCK_SLOT = {
    "identity_aura": "primary_identity_spine",
    "mind_voice": "secondary_balancing_line",
    "drive_rhythm": "secondary_balancing_line",
    "love_depth": "relational_line",
    "career_visibility": "work_visibility_line",
    "home_roots": "shadow_protection_line",
    "luck_creation": "work_visibility_line",
}


def _default_seed_key(chart: Dict[str, Any]) -> str:
    birth = chart.get("birth_datetime") or chart.get("birthDateTime") or chart.get("birth_datetime_iso") or ""
    location = chart.get("location") if isinstance(chart.get("location"), dict) else {}
    city = location.get("city", "") or (chart.get("birth") or {}).get("place", "")
    angles = chart.get("angles") if isinstance(chart.get("angles"), dict) else {}
    asc = angles.get("ascendant_sign", "") or angles.get("asc_sign", "")
    mc = angles.get("midheaven_sign", "") or angles.get("mc_sign", "")
    return f"{birth}|{city}|{asc}|{mc}"


def _hash_int(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _select_engine(seed_key: str, engine_override: Optional[str]) -> str:
    if engine_override in {"signature", "legacy"}:
        return str(engine_override)

    env_engine = (os.getenv("PROFILE_NARRATIVE_ENGINE") or "").strip().lower()
    if env_engine in {"signature", "legacy"}:
        return env_engine

    try:
        pct = int(os.getenv("PROFILE_NARRATIVE_ROLLOUT_PCT") or "100")
    except ValueError:
        pct = 100
    pct = max(0, min(100, pct))
    if pct >= 100:
        return "signature"
    if pct <= 0:
        return "legacy"
    return "signature" if (_hash_int(seed_key) % 100) < pct else "legacy"


def _surface_migration_mode(*, include_debug: bool, explicit_mode: Optional[str]) -> str:
    if explicit_mode in {"legacy", "shadow", "active"}:
        return str(explicit_mode)
    config = get_natal_selection_v3_config()
    phase_flags = config.get("phase_flags") if isinstance(config.get("phase_flags"), Mapping) else {}
    if bool(phase_flags.get("surface_migration_enabled")):
        return "active"
    if include_debug and bool(phase_flags.get("surface_migration_debug_only", True)):
        return "shadow"
    return "legacy"


def _profile_block_spine_contract(master_selector: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    identity_spine = (
        master_selector.get("identity_spine")
        if isinstance(master_selector, Mapping) and isinstance(master_selector.get("identity_spine"), Mapping)
        else {}
    )
    contracts: Dict[str, Dict[str, Any]] = {}
    for block_id, slot in _PROFILE_BLOCK_SLOT.items():
        payload = identity_spine.get(slot) if isinstance(identity_spine.get(slot), Mapping) else {}
        if not payload:
            continue
        contracts[block_id] = {
            "slot": slot,
            "line_id": str(payload.get("line_id") or ""),
            "label": str(payload.get("label") or ""),
            "source_primitives": list(payload.get("source_primitives") or []),
            "counterweights": list(payload.get("counterweights") or []),
            "contradiction_ids": list(payload.get("contradiction_ids") or []),
            "confidence": float(payload.get("confidence") or 0.0),
        }
    return contracts


def _signature_debug_map(payload: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    internal = payload.get("profile_internal") if isinstance(payload.get("profile_internal"), Mapping) else {}
    blocks = internal.get("blocks_debug") if isinstance(internal.get("blocks_debug"), list) else []
    return {
        str(block.get("id") or ""): dict(block)
        for block in blocks
        if isinstance(block, Mapping) and str(block.get("id") or "").strip()
    }


def _profile_spine_shadow_diff(
    base_payload: Mapping[str, Any],
    shadow_payload: Mapping[str, Any],
) -> Dict[str, Any]:
    base_map = _signature_debug_map(base_payload)
    shadow_map = _signature_debug_map(shadow_payload)
    changed_blocks = []
    for block_id, shadow_block in shadow_map.items():
        base_block = base_map.get(block_id, {})
        base_signature = str(base_block.get("primary_signature_id") or "")
        shadow_signature = str(shadow_block.get("primary_signature_id") or "")
        if base_signature == shadow_signature and float(shadow_block.get("spine_alignment_bonus") or 0.0) <= float(base_block.get("spine_alignment_bonus") or 0.0):
            continue
        changed_blocks.append(
            {
                "block_id": block_id,
                "legacy_signature_id": base_signature,
                "shadow_signature_id": shadow_signature,
                "legacy_spine_alignment_bonus": float(base_block.get("spine_alignment_bonus") or 0.0),
                "shadow_spine_alignment_bonus": float(shadow_block.get("spine_alignment_bonus") or 0.0),
                "target_slot": shadow_block.get("spine_target_slot"),
                "target_line_id": shadow_block.get("spine_target_line_id"),
            }
        )
    return {
        "changed_blocks": changed_blocks,
        "shadow_primary_signatures": {
            block_id: str(block.get("primary_signature_id") or "")
            for block_id, block in shadow_map.items()
        },
    }


def build_profile_narrative(
    chart: Dict[str, Any],
    natal_graph: Dict[str, Any],
    include_debug: bool = False,
    locale: str = "tr",
    engine_override: Optional[str] = None,
    seed_key: Optional[str] = None,
    master_selector: Mapping[str, Any] | None = None,
    migration_mode: Optional[str] = None,
) -> Dict[str, Any]:
    seed_material = seed_key or _default_seed_key(chart)
    engine_pre_force = _select_engine(seed_material, engine_override)
    engine = engine_pre_force
    legacy_force_promoted = False
    if engine == "legacy" and not include_debug:
        engine = "signature"
        legacy_force_promoted = True
    resolved_migration_mode = _surface_migration_mode(
        include_debug=include_debug,
        explicit_mode=migration_mode,
    )
    block_spine_contract = _profile_block_spine_contract(master_selector)
    logger.info(
        "profile_narrative_engine_selection",
        extra={
            "profile_narrative_engine": engine,
            "profile_narrative_engine_pre_force": engine_pre_force,
            "profile_narrative_legacy_force_promoted": legacy_force_promoted,
            "profile_narrative_engine_override_present": engine_override is not None,
            "profile_narrative_seed_key_hash": hashlib.sha256(seed_material.encode("utf-8")).hexdigest()[:12],
            "profile_narrative_migration_mode": resolved_migration_mode,
            "profile_narrative_include_debug": include_debug,
        },
    )

    if engine == "legacy":
        out = build_profile_narrative_legacy(
            chart,
            natal_graph,
            include_debug=include_debug,
            seed_key=seed_material,
            locale=locale,
        )
        if include_debug and block_spine_contract:
            internal = out.get("profile_internal") if isinstance(out.get("profile_internal"), dict) else {}
            internal["spine_migration"] = {
                "mode": resolved_migration_mode,
                "engine": engine,
                "status": "legacy_engine_no_spine_rerank",
                "target_contracts": block_spine_contract,
                "changed_blocks": [],
            }
            out["profile_internal"] = internal
    else:
        out = build_profile_narrative_signature(
            chart,
            natal_graph,
            include_debug=include_debug,
            seed_key=seed_material,
            locale=locale,
            block_spine_contract=block_spine_contract if resolved_migration_mode == "active" else None,
        )
        if include_debug and block_spine_contract:
            internal = out.get("profile_internal") if isinstance(out.get("profile_internal"), dict) else {}
            if resolved_migration_mode == "shadow":
                shadow_payload = build_profile_narrative_signature(
                    chart,
                    natal_graph,
                    include_debug=True,
                    seed_key=seed_material,
                    locale=locale,
                    block_spine_contract=block_spine_contract,
                )
                internal["spine_migration"] = {
                    "mode": "shadow",
                    "engine": engine,
                    "target_contracts": block_spine_contract,
                    **_profile_spine_shadow_diff(out, shadow_payload),
                }
            else:
                internal["spine_migration"] = {
                    "mode": resolved_migration_mode,
                    "engine": engine,
                    "target_contracts": block_spine_contract,
                    "changed_blocks": [],
                }
            out["profile_internal"] = internal

    if include_debug:
        internal = out.get("profile_internal") if isinstance(out.get("profile_internal"), dict) else {}
        blocks = internal.get("blocks_debug") if isinstance(internal.get("blocks_debug"), list) else []
        for block in blocks:
            if not isinstance(block, dict):
                continue
            block.setdefault("engine", engine)
            block.setdefault("seed_material", seed_material)
            block.setdefault("migration_mode", resolved_migration_mode)
        internal.setdefault(
            "engine_telemetry",
            {
                "engine": engine,
                "engine_pre_force": engine_pre_force,
                "legacy_force_promoted": legacy_force_promoted,
                "migration_mode": resolved_migration_mode,
                "engine_override_present": engine_override is not None,
            },
        )
        out["profile_internal"] = internal

    return out
