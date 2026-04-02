from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

from app.natal.narrative.natal_selection_config import get_natal_selection_v3_config

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

_SLOT_BY_HOUSE = {
    1: "primary_identity_spine",
    2: "primary_identity_spine",
    3: "secondary_balancing_line",
    4: "shadow_protection_line",
    5: "work_visibility_line",
    6: "secondary_balancing_line",
    7: "relational_line",
    8: "relational_line",
    9: "secondary_balancing_line",
    10: "work_visibility_line",
    11: "work_visibility_line",
    12: "shadow_protection_line",
}

_HOUSE_PRIMITIVE_HINTS = {
    1: ["self_definition", "visible_presence"],
    2: ["self_definition", "inner_structure"],
    3: ["mental_structuring", "tone_sensitivity", "systems_thinking"],
    4: ["recharge_through_home", "family_self_reliance"],
    5: ["creation_luck", "visible_presence"],
    6: ["methodical_drive", "systems_thinking"],
    7: ["relational_security", "graceful_affection"],
    8: ["intimacy_depth", "emotional_threshold", "transformative_bonding"],
    9: ["meaningful_expansion", "big_picture_vision", "methodical_drive"],
    10: ["public_refinement", "visible_presence"],
    11: ["network_luck", "public_refinement"],
    12: ["backstage_creation", "emotional_threshold", "recharge_through_home"],
}

_PLANET_PRIMITIVE_HINTS = {
    "Sun": ["self_definition", "visible_presence"],
    "Moon": ["intimacy_depth", "emotional_threshold", "recharge_through_home"],
    "Mercury": ["mental_structuring", "tone_sensitivity", "systems_thinking"],
    "Venus": ["graceful_affection", "relational_security"],
    "Mars": ["methodical_drive", "push_pull_drive"],
    "Jupiter": ["meaningful_expansion", "creation_luck", "network_luck"],
    "Saturn": ["inner_structure", "inner_critic"],
    "Uranus": ["originality_drive"],
    "Neptune": ["backstage_creation", "big_picture_vision"],
    "Pluto": ["transformative_bonding", "intimacy_depth"],
    "Ascendant": ["self_definition"],
    "Midheaven": ["public_refinement", "visible_presence"],
}

_ASPECT_COMBINATION_HINTS = {
    frozenset({"Sun", "Uranus"}): ["originality_drive", "self_definition"],
    frozenset({"Mercury", "Uranus"}): ["mental_structuring", "originality_drive"],
    frozenset({"Sun", "Saturn"}): ["inner_structure", "inner_critic"],
    frozenset({"Mars", "Saturn"}): ["push_pull_drive", "methodical_drive"],
    frozenset({"Moon", "Pluto"}): ["intimacy_depth", "transformative_bonding"],
    frozenset({"Venus", "Neptune"}): ["graceful_affection", "backstage_creation"],
    frozenset({"Jupiter", "Sun"}): ["meaningful_expansion", "visible_presence"],
}

_SLOT_FAMILY = {
    "primary_identity_spine": "identity",
    "secondary_balancing_line": "identity",
    "relational_line": "relational",
    "work_visibility_line": "visibility",
    "shadow_protection_line": "shadow",
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


def _migration_mode(explicit_mode: str | None) -> str:
    if explicit_mode in {"legacy", "shadow", "active"}:
        return str(explicit_mode)
    config = get_natal_selection_v3_config()
    phase_flags = config.get("phase_flags") if isinstance(config.get("phase_flags"), Mapping) else {}
    if bool(phase_flags.get("surface_migration_enabled")):
        return "active"
    return "legacy"


def _slot_contracts(master_selector: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    identity_spine = (
        master_selector.get("identity_spine")
        if isinstance(master_selector, Mapping) and isinstance(master_selector.get("identity_spine"), Mapping)
        else {}
    )
    contracts: Dict[str, Dict[str, Any]] = {}
    for slot, payload in (identity_spine or {}).items():
        if not isinstance(payload, Mapping):
            continue
        contracts[str(slot)] = {
            "slot": str(slot),
            "line_id": str(payload.get("line_id") or ""),
            "label": str(payload.get("label") or ""),
            "source_primitives": [str(item) for item in payload.get("source_primitives") or [] if str(item).strip()],
            "counterweights": [str(item) for item in payload.get("counterweights") or [] if str(item).strip()],
            "confidence": float(payload.get("confidence") or 0.0),
        }
    return contracts


def _candidate_slot(candidate: Mapping[str, Any]) -> str | None:
    source = candidate.get("source") if isinstance(candidate.get("source"), Mapping) else {}
    kind = str(source.get("type") or "").strip().lower()
    if kind == "house_placement":
        return _SLOT_BY_HOUSE.get(_safe_house(source.get("house")))
    if kind == "aspect":
        planets = {
            str(source.get("planet1") or "").strip(),
            str(source.get("planet2") or "").strip(),
        }
        if {"Moon", "Venus", "Pluto"} & planets:
            return "relational_line"
        if {"Midheaven", "Sun", "Jupiter"} & planets:
            return "work_visibility_line"
        if {"Saturn", "Moon", "Neptune"} & planets:
            return "shadow_protection_line"
        if {"Mercury", "Uranus", "Mars"} & planets:
            return "secondary_balancing_line"
        if {"Sun", "Ascendant"} & planets:
            return "primary_identity_spine"
    return None


def _candidate_primitives(candidate: Mapping[str, Any]) -> list[str]:
    source = candidate.get("source") if isinstance(candidate.get("source"), Mapping) else {}
    kind = str(source.get("type") or "").strip().lower()
    primitives: list[str] = []
    if kind == "house_placement":
        house = _safe_house(source.get("house"))
        primitives.extend(_HOUSE_PRIMITIVE_HINTS.get(house or -1, []))
        primitives.extend(_PLANET_PRIMITIVE_HINTS.get(str(source.get("planet") or "").strip(), []))
    elif kind == "aspect":
        planet1 = str(source.get("planet1") or "").strip()
        planet2 = str(source.get("planet2") or "").strip()
        primitives.extend(_PLANET_PRIMITIVE_HINTS.get(planet1, []))
        primitives.extend(_PLANET_PRIMITIVE_HINTS.get(planet2, []))
        primitives.extend(_ASPECT_COMBINATION_HINTS.get(frozenset({planet1, planet2}), []))
    deduped: list[str] = []
    for primitive_id in primitives:
        if primitive_id and primitive_id not in deduped:
            deduped.append(primitive_id)
    return deduped[:4]


def _candidate_family(slot: str | None) -> str:
    return _SLOT_FAMILY.get(str(slot or ""), "identity")


def _rerank_candidates(
    candidates: Sequence[Mapping[str, Any]],
    *,
    contracts: Mapping[str, Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    config = get_natal_selection_v3_config()
    weights = (
        (config.get("weights") or {}).get("surface_migration_v1")
        if isinstance(config.get("weights"), Mapping)
        else {}
    )
    reranked: List[Dict[str, Any]] = []
    for candidate in candidates:
        item = dict(candidate)
        slot = _candidate_slot(item)
        contract = contracts.get(str(slot)) if slot and isinstance(contracts.get(str(slot)), Mapping) else {}
        derived_primitives = _candidate_primitives(item)
        target_primitives = {str(value) for value in contract.get("source_primitives") or [] if str(value).strip()}
        counterweights = {str(value) for value in contract.get("counterweights") or [] if str(value).strip()}
        direct_matches = [primitive_id for primitive_id in derived_primitives if primitive_id in target_primitives]
        counter_matches = [primitive_id for primitive_id in derived_primitives if primitive_id in counterweights]
        slot_bonus = float(weights.get("imprint_slot_bonus") or 0.16) if slot and contract else 0.0
        primitive_bonus = float(weights.get("imprint_primitive_bonus") or 0.18) * (
            len(direct_matches) / max(len(derived_primitives), 1)
        )
        counterweight_bonus = float(weights.get("imprint_counterweight_bonus") or 0.08) * (
            len(counter_matches) / max(len(derived_primitives), 1)
        )
        combination_bonus = 0.0
        if len(direct_matches) >= 2:
            combination_bonus += float(weights.get("imprint_combination_bonus") or 0.10)
        if str((item.get("source") or {}).get("type") or "") == "aspect" and (direct_matches or counter_matches):
            combination_bonus += float(item.get("exactness") or 0.0) * 0.05
        family_bonus = 0.0
        if not direct_matches and slot and contract:
            family_bonus = 0.04 if _candidate_family(slot) in {"identity", "visibility"} else 0.02
        confidence_bonus = float(contract.get("confidence") or 0.0) * 0.04 if direct_matches or counter_matches else 0.0
        selection_score = float(item.get("score") or 0.0) + slot_bonus + primitive_bonus + counterweight_bonus + combination_bonus + family_bonus + confidence_bonus
        item["legacy_score"] = round(float(item.get("score") or 0.0), 4)
        item["score"] = round(selection_score, 4)
        item["selection_score"] = round(selection_score, 4)
        item["spine_slot"] = slot
        item["spine_line_id"] = str(contract.get("line_id") or "")
        item["derived_primitives"] = derived_primitives
        item["direct_matches"] = direct_matches
        item["counterweight_matches"] = counter_matches
        item["spine_bonus"] = round(slot_bonus + primitive_bonus + counterweight_bonus + combination_bonus + confidence_bonus, 4)
        reranked.append(item)
    return reranked


def select_personality_imprint_entries(
    *,
    planets: Sequence[Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
    master_selector: Mapping[str, Any] | None = None,
    migration_mode: str | None = None,
) -> Dict[str, Any]:
    resolved_mode = _migration_mode(migration_mode)
    contracts = _slot_contracts(master_selector)

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

    debug: Dict[str, Any] = {
        "selection_logic": PERSONALITY_IMPRINT_SELECTION_LOGIC,
        "house_candidates": house_candidates,
        "aspect_candidates": aspect_candidates,
        "selected_keys": [str(item.get("key") or "") for item in selected],
        "extra_keys": [str(item.get("key") or "") for item in extras],
    }

    if contracts and resolved_mode in {"shadow", "active"}:
        ranked_shadow = _dedupe_sorted(
            _rerank_candidates([*house_candidates, *aspect_candidates], contracts=contracts),
            len(house_candidates) + len(aspect_candidates),
        )
        shadow_houses = _dedupe_sorted(
            _rerank_candidates(house_candidates, contracts=contracts),
            int(PERSONALITY_IMPRINT_SELECTION_LOGIC["top_house_placements"]),
        )
        shadow_aspects = _dedupe_sorted(
            _rerank_candidates(aspect_candidates, contracts=contracts),
            int(PERSONALITY_IMPRINT_SELECTION_LOGIC["top_aspects"]),
        )
        shadow_selected = sorted([*shadow_houses, *shadow_aspects], key=_sort_key, reverse=True)
        shadow_keys = {str(item.get("key") or "") for item in shadow_selected}
        shadow_extras = [
            dict(item)
            for item in ranked_shadow
            if str(item.get("key") or "") not in shadow_keys
        ]
        debug["spine_migration"] = {
            "mode": resolved_mode,
            "target_slots": {
                slot: str((contract or {}).get("line_id") or "")
                for slot, contract in contracts.items()
            },
            "shadow_selected_keys": [str(item.get("key") or "") for item in shadow_selected],
            "shadow_top_keys": [str(item.get("key") or "") for item in ranked_shadow[:6]],
            "rank_shifts": [
                {
                    "key": str(item.get("key") or ""),
                    "legacy_rank": legacy_index + 1,
                    "shadow_rank": next(
                        (
                            shadow_index + 1
                            for shadow_index, shadow_item in enumerate(ranked_shadow)
                            if str(shadow_item.get("key") or "") == str(item.get("key") or "")
                        ),
                        0,
                    ),
                }
                for legacy_index, item in enumerate(ranked_candidates[:10])
            ],
        }
        if resolved_mode == "active":
            selected = shadow_selected
            extras = shadow_extras
            ranked_candidates = ranked_shadow
            debug["selected_keys"] = [str(item.get("key") or "") for item in selected]
            debug["extra_keys"] = [str(item.get("key") or "") for item in extras]

    return {
        "selected": selected,
        "extras": extras,
        "ranked": ranked_candidates,
        "debug": debug,
    }
