from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, Optional

from .profile_narrative_engine_legacy import build_profile_narrative_legacy
from .profile_narrative_engine_signature import build_profile_narrative_signature


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


def build_profile_narrative(
    chart: Dict[str, Any],
    natal_graph: Dict[str, Any],
    include_debug: bool = False,
    locale: str = "tr",
    engine_override: Optional[str] = None,
    seed_key: Optional[str] = None,
) -> Dict[str, Any]:
    seed_material = seed_key or _default_seed_key(chart)
    engine = _select_engine(seed_material, engine_override)

    if engine == "legacy":
        out = build_profile_narrative_legacy(
            chart,
            natal_graph,
            include_debug=include_debug,
            seed_key=seed_material,
            locale=locale,
        )
    else:
        out = build_profile_narrative_signature(
            chart,
            natal_graph,
            include_debug=include_debug,
            seed_key=seed_material,
            locale=locale,
        )

    if include_debug:
        internal = out.get("profile_internal") if isinstance(out.get("profile_internal"), dict) else {}
        blocks = internal.get("blocks_debug") if isinstance(internal.get("blocks_debug"), list) else []
        for block in blocks:
            if not isinstance(block, dict):
                continue
            block.setdefault("engine", engine)
            block.setdefault("seed_material", seed_material)
        out["profile_internal"] = internal

    return out
