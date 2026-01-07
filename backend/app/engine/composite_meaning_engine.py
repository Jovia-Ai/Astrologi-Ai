from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence


class CompositeMeaningEngineV1:
    def build_composite_meanings_v1(
        self,
        *,
        composites: Sequence[Mapping[str, Any]],
        theme_scores: Mapping[str, Any] | None,
        dynamic_insights: Mapping[str, Any] | None,
        debug: bool = False,
    ) -> Dict[str, Any]:
        return build_composite_meanings_v1(
            composites=composites,
            theme_scores=theme_scores,
            dynamic_insights=dynamic_insights,
            debug=debug,
        )


def build_composite_meanings_v1(
    *,
    composites: Sequence[Mapping[str, Any]],
    theme_scores: Mapping[str, Any] | None,
    dynamic_insights: Mapping[str, Any] | None,
    debug: bool = False,
) -> Dict[str, Any]:
    templates_by_id = _load_composite_templates()
    selected: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    candidates: List[Dict[str, Any]] = []
    for composite in composites or []:
        if not isinstance(composite, Mapping):
            continue
        composite_id = str(composite.get("composite_id") or "").strip()
        if not composite_id:
            continue
        template = templates_by_id.get(composite_id)
        strength = _clamp01(_safe_float(composite.get("priority_score"), fallback=0.5))
        sources = (template or {}).get("sources") or composite.get("sources") or []
        domains = _normalize_domains((template or {}).get("domains") or composite.get("domains") or composite.get("domain"))
        if not template:
            legacy_text = str(composite.get("base_interpretation") or "").strip()
            if not legacy_text:
                rejected.append({"composite_id": composite_id, "reason": "no_mapping"})
                continue
            meaning_id = f"cm.legacy.{composite_id}.v1"
            instance_id = _instance_id(meaning_id, composite_id, sources)
            narrative = {
                "headline": legacy_text,
                "p1_bridge": "",
                "p2_bridge": "",
                "p3_bridge": "",
            }
        else:
            meaning_id = template.get("meaning_id") or ""
            instance_id = _instance_id(meaning_id, composite_id, sources)
            narrative = template.get("templates") or {}

        entry = {
            "meaning_id": meaning_id,
            "instance_id": instance_id,
            "composite_id": composite_id,
            "domains": domains,
            "strength": round(strength, 3),
            "evidence": {
                "source_composites": [
                    {
                        "composite_id": composite_id,
                        "priority_score": strength,
                        "sources": list(sources),
                    }
                ]
            },
            "narrative": {
                "headline": narrative.get("headline") or "",
                "p1_bridge": narrative.get("p1_bridge") or "",
                "p2_bridge": narrative.get("p2_bridge") or "",
                "p3_bridge": narrative.get("p3_bridge") or "",
            },
        }
        if debug:
            entry["debug"] = {
                "domain_rank": _domain_rank(domains),
                "theme_scores": theme_scores or {},
                "dynamic_insights_present": bool(dynamic_insights),
            }
        candidates.append(entry)

    ranked = sorted(
        candidates,
        key=lambda item: (
            -_safe_float(item.get("strength"), fallback=0.0),
            _domain_rank(item.get("domains")),
            str(item.get("meaning_id") or ""),
            str(item.get("instance_id") or ""),
        ),
    )
    selected = ranked[:2]

    selected_ids = {item.get("composite_id") for item in selected}
    for entry in ranked[2:]:
        composite_id = entry.get("composite_id")
        if composite_id and composite_id not in selected_ids:
            rejected.append({"composite_id": composite_id, "reason": "lower_ranked"})

    payload: Dict[str, Any] = {
        "schema_version": "cm.v1",
        "engine_version": "cm.v1",
        "selected": selected,
        "rejected": rejected,
    }
    if debug:
        payload["debug"] = {
            "candidates": len(candidates),
            "selected": len(selected),
            "rejected": len(rejected),
            "used_composite_ids": [str(item.get("composite_id")) for item in composites if isinstance(item, Mapping)],
            "used_meaning_ids": [str(item.get("meaning_id")) for item in selected if item.get("meaning_id")],
        }
    return payload


def _load_composite_templates() -> Dict[str, Dict[str, Any]]:
    base_dir = Path(__file__).resolve().parents[1] / "data" / "astro_rules" / "composite"
    templates: Dict[str, Dict[str, Any]] = {}
    if not base_dir.exists():
        return templates
    for file_path in sorted(base_dir.glob("*.json")):
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, Mapping):
            continue
        composite_id = str(payload.get("composite_id") or "").strip()
        if not composite_id:
            continue
        meaning_block = payload.get("meaning") if isinstance(payload.get("meaning"), Mapping) else {}
        meaning_id = meaning_block.get("meaning_id") or payload.get("meaning_id")
        templates_payload = meaning_block.get("templates") or payload.get("templates") or {}
        templates[composite_id] = {
            "composite_id": composite_id,
            "meaning_id": meaning_id,
            "domains": payload.get("domains"),
            "sources": payload.get("sources") or [],
            "templates": templates_payload,
        }
    return templates


def _normalize_domains(value: Any) -> List[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence):
        return [str(item) for item in value if item]
    return []


def _domain_rank(domains: Any) -> int:
    domain_order = [
        "identity",
        "psychology",
        "emotional",
        "relationships",
        "mind",
        "career",
        "direction",
        "karma",
    ]
    domain_list = _normalize_domains(domains)
    best = len(domain_order) + 1
    for domain in domain_list:
        try:
            idx = domain_order.index(domain)
        except ValueError:
            idx = len(domain_order)
        if idx < best:
            best = idx
    return best


def _instance_id(meaning_id: str, composite_id: str, sources: Sequence[str]) -> str:
    joined = "|".join(sorted(str(source) for source in sources if source))
    raw = f"{meaning_id}|{composite_id}|{joined}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _safe_float(value: Any, *, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(fallback)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value
