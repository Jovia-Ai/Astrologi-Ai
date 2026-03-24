from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

from .contracts import (
    PERSONALITY_IMPRINT_DOMINANT_LIBRARY_INDEX_TR,
    PERSONALITY_IMPRINT_SELECTION_LOGIC,
)

ANGULAR_HOUSES = {1, 4, 7, 10}
LUMINARIES = {"Sun", "Moon"}
PERSONAL_PLANETS = {"Mercury", "Venus", "Mars"}

ASPECT_KEY_ALIASES = {
    "conjunction": "conj",
    "conj": "conj",
    "square": "square",
    "trine": "trine",
    "opposition": "opposite",
    "opposite": "opposite",
    "opp": "opposite",
    "sextile": "sextile",
}


def _safe_house(value: Any) -> int | None:
    try:
        house = int(value)
    except (TypeError, ValueError):
        return None
    return house if 1 <= house <= 12 else None


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _planet_weight(planet: str) -> float:
    weights = PERSONALITY_IMPRINT_SELECTION_LOGIC["priority_weights"]
    if planet in LUMINARIES:
        return float(weights["luminaries"])
    if planet in PERSONAL_PLANETS:
        return float(weights["personal_planets"])
    return 1.0


def _placement_key(planet: str, house: int | None) -> str:
    return f"{planet.strip().lower()}_house_{house}"


def _aspect_keys(planet1: str, planet2: str, aspect: str) -> List[str]:
    aspect_key = ASPECT_KEY_ALIASES.get(str(aspect or "").strip().lower(), "")
    if not aspect_key:
        return []
    left = str(planet1 or "").strip().lower()
    right = str(planet2 or "").strip().lower()
    if not left or not right:
        return []
    return [f"{left}_{aspect_key}_{right}", f"{right}_{aspect_key}_{left}"]


def _sort_key(candidate: Mapping[str, Any]) -> tuple[float, float, float]:
    return (
        float(candidate.get("score") or 0.0),
        float(candidate.get("tie_breaker") or 0.0),
        float(candidate.get("exactness") or 0.0),
    )


def _dedupe_sorted(candidates: Sequence[Mapping[str, Any]], limit: int) -> List[Dict[str, Any]]:
    selected: List[Dict[str, Any]] = []
    seen_keys: set[str] = set()
    for candidate in sorted(candidates, key=_sort_key, reverse=True):
        key = str(candidate.get("key") or "").strip()
        if not key or key in seen_keys:
            continue
        seen_keys.add(key)
        selected.append(dict(candidate))
        if len(selected) >= limit:
            break
    return selected


def collect_house_candidates(
    planets: Sequence[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    importance = natal_graph.get("importance") if isinstance(natal_graph.get("importance"), Mapping) else {}
    candidates: List[Dict[str, Any]] = []
    for payload in planets:
        if not isinstance(payload, Mapping):
            continue
        planet = str(payload.get("planet") or "").strip()
        house = _safe_house(payload.get("house"))
        if not planet or house is None:
            continue
        key = _placement_key(planet, house)
        library_entry = PERSONALITY_IMPRINT_DOMINANT_LIBRARY_INDEX_TR.get(key)
        if not library_entry:
            continue
        score = _planet_weight(planet)
        if house in ANGULAR_HOUSES:
            score *= float(PERSONALITY_IMPRINT_SELECTION_LOGIC["priority_weights"]["angular_houses"])
        candidates.append(
            {
                "key": key,
                "score": round(score, 4),
                "tie_breaker": float(importance.get(planet) or 0.0),
                "exactness": 0.0,
                "entry": dict(library_entry),
                "source": {
                    "type": "house_placement",
                    "planet": planet,
                    "house": house,
                    "importance": float(importance.get(planet) or 0.0),
                },
            }
        )
    return candidates


def collect_aspect_candidates(
    aspects: Sequence[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    importance = natal_graph.get("importance") if isinstance(natal_graph.get("importance"), Mapping) else {}
    exact_max_orb = float(PERSONALITY_IMPRINT_SELECTION_LOGIC["exact_aspect_max_orb"])
    exact_weight = float(PERSONALITY_IMPRINT_SELECTION_LOGIC["priority_weights"]["exact_aspects"])
    candidates: List[Dict[str, Any]] = []

    for payload in aspects:
        if not isinstance(payload, Mapping):
            continue
        planet1 = str(payload.get("planet1") or "").strip()
        planet2 = str(payload.get("planet2") or "").strip()
        aspect = str(payload.get("type") or payload.get("aspect") or "").strip()
        if not planet1 or not planet2 or not aspect:
            continue
        matched_key = ""
        for key in _aspect_keys(planet1, planet2, aspect):
            if key in PERSONALITY_IMPRINT_DOMINANT_LIBRARY_INDEX_TR:
                matched_key = key
                break
        if not matched_key:
            continue
        orb = _safe_float(payload.get("orb"))
        score = max(_planet_weight(planet1), _planet_weight(planet2))
        if orb is not None and orb <= exact_max_orb:
            score *= exact_weight
        if orb is None:
            exactness = 0.0
        else:
            exactness = round(max(0.0, (exact_max_orb - min(orb, exact_max_orb)) / exact_max_orb), 4)
        tie_breaker = max(float(importance.get(planet1) or 0.0), float(importance.get(planet2) or 0.0))
        candidates.append(
            {
                "key": matched_key,
                "score": round(score, 4),
                "tie_breaker": round(tie_breaker, 4),
                "exactness": exactness,
                "entry": dict(PERSONALITY_IMPRINT_DOMINANT_LIBRARY_INDEX_TR[matched_key]),
                "source": {
                    "type": "aspect",
                    "planet1": planet1,
                    "planet2": planet2,
                    "aspect": aspect,
                    "orb": orb,
                    "importance": {
                        planet1: float(importance.get(planet1) or 0.0),
                        planet2: float(importance.get(planet2) or 0.0),
                    },
                },
            }
        )
    return candidates


def select_personality_imprint_entries(
    *,
    planets: Sequence[Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
) -> Dict[str, Any]:
    house_candidates = collect_house_candidates(planets, natal_graph)
    aspect_candidates = collect_aspect_candidates(aspects, natal_graph)
    ranked_candidates = _dedupe_sorted(
        [*house_candidates, *aspect_candidates],
        len(house_candidates) + len(aspect_candidates),
    )

    selected_houses = _dedupe_sorted(
        house_candidates,
        int(PERSONALITY_IMPRINT_SELECTION_LOGIC["top_house_placements"]),
    )
    selected_aspects = _dedupe_sorted(
        aspect_candidates,
        int(PERSONALITY_IMPRINT_SELECTION_LOGIC["top_aspects"]),
    )
    selected = sorted([*selected_houses, *selected_aspects], key=_sort_key, reverse=True)
    selected_keys = {str(item.get("key") or "") for item in selected}
    extras = [
        dict(item)
        for item in ranked_candidates
        if str(item.get("key") or "") not in selected_keys
    ]

    return {
        "selected": selected,
        "extras": extras,
        "ranked": ranked_candidates,
        "debug": {
            "selection_logic": PERSONALITY_IMPRINT_SELECTION_LOGIC,
            "house_candidates": house_candidates,
            "aspect_candidates": aspect_candidates,
            "selected_keys": [str(item.get("key") or "") for item in selected],
            "extra_keys": [str(item.get("key") or "") for item in extras],
        },
    }
