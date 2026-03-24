from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

from .contracts import (
    PERSONALITY_IMPRINT_ASC_RULER_LIBRARY_INDEX_TR,
    PERSONALITY_IMPRINT_SELECTION_LOGIC,
    PERSONALITY_IMPRINT_SIGN_LIBRARY_INDEX_TR,
)

LUMINARIES = {"Sun", "Moon"}
PERSONAL_PLANETS = {"Mercury", "Venus", "Mars"}


def _planet_weight(planet: str) -> float:
    weights = PERSONALITY_IMPRINT_SELECTION_LOGIC["priority_weights"]
    if planet in LUMINARIES:
        return float(weights["luminaries"])
    if planet in PERSONAL_PLANETS:
        return float(weights["personal_planets"])
    return 1.0


def _norm_sign(sign: Any) -> str:
    return str(sign or "").strip().lower()


def _sign_key(planet: str, sign: Any) -> str:
    return f"{str(planet or '').strip().lower()}_{_norm_sign(sign)}"


def _sort_key(candidate: Mapping[str, Any]) -> tuple[float, float]:
    return (
        float(candidate.get("score") or 0.0),
        float(candidate.get("tie_breaker") or 0.0),
    )


def collect_sign_candidates(
    planets: Sequence[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    importance = natal_graph.get("importance") if isinstance(natal_graph.get("importance"), Mapping) else {}
    candidates: List[Dict[str, Any]] = []
    for payload in planets:
        if not isinstance(payload, Mapping):
            continue
        planet = str(payload.get("planet") or "").strip()
        sign = payload.get("sign")
        if not planet or not sign:
            continue
        key = _sign_key(planet, sign)
        entry = PERSONALITY_IMPRINT_SIGN_LIBRARY_INDEX_TR.get(key)
        if not entry:
            continue
        candidates.append(
            {
                "key": key,
                "score": round(_planet_weight(planet), 4),
                "tie_breaker": round(float(importance.get(planet) or 0.0), 4),
                "entry": dict(entry),
                "source": {
                    "type": "sign_placement",
                    "planet": planet,
                    "sign": sign,
                    "importance": float(importance.get(planet) or 0.0),
                },
            }
        )
    return candidates


def _house_ruler_payload(natal_graph: Mapping[str, Any], house: int) -> Mapping[str, Any]:
    house_rulers = natal_graph.get("house_rulers") if isinstance(natal_graph.get("house_rulers"), Mapping) else {}
    payload = house_rulers.get(str(house))
    if isinstance(payload, Mapping):
        return payload
    compact = natal_graph.get("compact") if isinstance(natal_graph.get("compact"), Mapping) else {}
    compact_rulers = compact.get("house_rulers") if isinstance(compact.get("house_rulers"), Mapping) else {}
    payload = compact_rulers.get(str(house))
    return payload if isinstance(payload, Mapping) else {}


def collect_asc_ruler_candidates(natal_graph: Mapping[str, Any]) -> List[Dict[str, Any]]:
    importance = natal_graph.get("importance") if isinstance(natal_graph.get("importance"), Mapping) else {}
    house1 = _house_ruler_payload(natal_graph, 1)
    ruler = str(house1.get("primary_ruler") or "").strip()
    if not ruler:
        return []
    key = f"asc_ruler_{ruler.lower()}"
    entry = PERSONALITY_IMPRINT_ASC_RULER_LIBRARY_INDEX_TR.get(key)
    if not entry:
        return []
    ruler_pos = house1.get("primary_ruler_pos") if isinstance(house1.get("primary_ruler_pos"), Mapping) else {}
    return [
        {
            "key": key,
            "score": round(_planet_weight(ruler), 4),
            "tie_breaker": round(float(importance.get(ruler) or 0.0), 4),
            "entry": dict(entry),
            "source": {
                "type": "asc_ruler_tone",
                "planet": ruler,
                "house": ruler_pos.get("house") or house1.get("primary_house"),
                "sign": ruler_pos.get("sign"),
                "cusp_sign": house1.get("cusp_sign"),
            },
        }
    ]


def _related_planets(dominant_candidate: Mapping[str, Any]) -> List[str]:
    source = dominant_candidate.get("source") if isinstance(dominant_candidate.get("source"), Mapping) else {}
    kind = str(source.get("type") or "").strip().lower()
    if kind == "house_placement":
        planet = str(source.get("planet") or "").strip()
        return [planet] if planet else []
    if kind == "aspect":
        planets = [
            str(source.get("planet1") or "").strip(),
            str(source.get("planet2") or "").strip(),
        ]
        return [planet for planet in planets if planet]
    return []


def build_signature_bundles(
    *,
    dominant_candidates: Sequence[Mapping[str, Any]],
    planets: Sequence[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
) -> Dict[str, Any]:
    sign_candidates = collect_sign_candidates(planets, natal_graph)
    asc_ruler_candidates = collect_asc_ruler_candidates(natal_graph)
    sign_candidates_by_planet: Dict[str, List[Dict[str, Any]]] = {}
    for candidate in sign_candidates:
        source = candidate.get("source") if isinstance(candidate.get("source"), Mapping) else {}
        planet = str(source.get("planet") or "").strip()
        if not planet:
            continue
        sign_candidates_by_planet.setdefault(planet, []).append(candidate)
    for items in sign_candidates_by_planet.values():
        items.sort(key=_sort_key, reverse=True)

    support_entries_by_key: Dict[str, Dict[str, Any]] = {}
    bundles: List[Dict[str, Any]] = []
    max_support = int(PERSONALITY_IMPRINT_SELECTION_LOGIC["max_sign_support_per_bundle"])
    append_asc_ruler = bool(PERSONALITY_IMPRINT_SELECTION_LOGIC.get("append_asc_ruler_tone_to_bundles"))
    top_asc_ruler = max(asc_ruler_candidates, key=_sort_key, default=None)

    for dominant in dominant_candidates:
        dominant_key = str(dominant.get("key") or "").strip()
        if not dominant_key:
            continue
        related_planets = _related_planets(dominant)
        support_keys: List[str] = []
        for planet in related_planets:
            for candidate in sign_candidates_by_planet.get(planet) or []:
                key = str(candidate.get("key") or "").strip()
                if not key or key in support_keys:
                    continue
                support_keys.append(key)
                support_entries_by_key.setdefault(key, dict(candidate.get("entry") or {}))
                if len(support_keys) >= max_support:
                    break
            if len(support_keys) >= max_support:
                break
        if append_asc_ruler and isinstance(top_asc_ruler, Mapping):
            asc_key = str(top_asc_ruler.get("key") or "").strip()
            if asc_key and asc_key not in support_keys:
                support_keys.append(asc_key)
                support_entries_by_key.setdefault(asc_key, dict(top_asc_ruler.get("entry") or {}))
        bundles.append(
            {
                "id": dominant_key,
                "dominant_key": dominant_key,
                "dominant_kind": ((dominant.get("entry") or {}) if isinstance(dominant.get("entry"), Mapping) else {}).get("kind"),
                "related_planets": related_planets,
                "support_keys": support_keys,
            }
        )

    support_entries = sorted(
        support_entries_by_key.values(),
        key=lambda item: str(item.get("key") or ""),
    )
    return {
        "support_entries": support_entries,
        "bundles": bundles,
        "debug": {
            "sign_candidates": sign_candidates,
            "asc_ruler_candidates": asc_ruler_candidates,
            "bundle_support_map": {
                str(bundle["dominant_key"]): list(bundle["support_keys"])
                for bundle in bundles
            },
        },
    }
