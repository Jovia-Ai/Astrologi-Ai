from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from app.builders.semantic_normalizer import normalize_slot_text
from app.helpers.meta_detectors import normalize_node_alias, normalize_planet_key
from app.helpers.domain_normalizer import canon_domain, canonical_domains


SLOT_INTENTS: Dict[str, str] = {
    "cause": "core_identity",
    "mechanism": "stabilizer",
    "effect": "tension_source",
    "shadow": "tension_source",
    "potential": "growth_path",
}

SIMILARITY_THRESHOLD = 0.7
CANONICAL_DOMAIN_SET = set(canonical_domains())
DEFAULT_SALIENCE_WEIGHTS = {
    "orb": 0.2,
    "dominance": 0.25,
    "axis": 0.15,
    "house": 0.1,
    "pattern": 0.2,
    "domain": 0.1,
}
DEFAULT_DOMAIN_PRIORITY = 0.5


def select_phase2_fragments(
    fragments_by_domain: Mapping[str, Mapping[str, List[Dict[str, Any]]]],
    composites: Sequence[Mapping[str, Any]],
    meta_info: Mapping[str, Any],
    domain_regulators: Mapping[str, Dict[str, Any]] | None = None,
    axis_activation: Mapping[str, Any] | None = None,
    *,
    max_domains: int = 3,
) -> Dict[str, Dict[str, Any]]:
    chart_ruler = _detect_chart_ruler(meta_info)
    stellium_planets = _detect_stellium_planets(meta_info)
    domain_priorities = _aggregate_composite_priorities(composites)

    reduced: Dict[str, Dict[str, Any]] = {}
    domain_text_tokens: Dict[str, List[set[str]]] = {}
    diversity_state = {
        "planets": Counter(),
        "houses": Counter(),
        "rule_groups": Counter(),
        "texts": [],
    }
    normalized_fragments = _canonicalize_fragment_map(fragments_by_domain)
    for domain, slots in normalized_fragments.items():
        domain_key = domain
        tokens = domain_text_tokens.setdefault(domain_key, [])
        reduced_slots: Dict[str, Dict[str, Any] | None] = {}
        for slot in ("cause", "mechanism", "effect", "shadow", "potential"):
            candidates = slots.get(slot) or []
            candidates = _dedupe_and_score_candidates(
                candidates,
                domain=domain_key,
                slot=slot,
                meta_info=meta_info,
                axis_activation=axis_activation,
                domain_priority=_clamp_domain_priority(
                    domain_priorities.get(domain_key, DEFAULT_DOMAIN_PRIORITY)
                ),
            )
            reduced_slots[slot] = _select_fragment_by_priority(
                candidates,
                chart_ruler=chart_ruler,
                stellium_planets=stellium_planets,
                composite_priority=_clamp_domain_priority(
                    domain_priorities.get(domain_key, DEFAULT_DOMAIN_PRIORITY)
                ),
                slot=slot,
                existing_tokens=tokens,
                diversity_state=diversity_state,
            )
            fragment = reduced_slots[slot]
            if fragment:
                fragment_tokens = _fragment_text_tokens(fragment, slot)
                if fragment_tokens:
                    tokens.append(fragment_tokens)
        _ensure_required_slots(
            domain_key,
            slots,
            reduced_slots,
            _clamp_domain_priority(domain_priorities.get(domain_key, DEFAULT_DOMAIN_PRIORITY)),
            tokens,
            meta_info,
            axis_activation,
            diversity_state,
        )
        anchor = reduced_slots.get("cause")
        reduced[domain_key] = {"slots": reduced_slots, "anchor": anchor}
        _update_diversity_state(diversity_state, [fragment for fragment in reduced_slots.values() if isinstance(fragment, Mapping)])
    if max_domains and len(reduced) > max_domains:
        reduced, compressed = _select_focus_domains(reduced, max_domains=max_domains)
        if compressed:
            reduced["__compressed_domains__"] = {"items": compressed}
    return reduced


def _select_fragment_by_priority(
    candidates: Sequence[Dict[str, Any]],
    *,
    chart_ruler: Optional[str],
    stellium_planets: Sequence[str],
    composite_priority: float,
    slot: str,
    existing_tokens: Sequence[set[str]] | None = None,
    diversity_state: Mapping[str, Any] | None = None,
) -> Dict[str, Any] | None:
    if not candidates:
        return None

    entries = list(enumerate(candidates))
    filtered_entries = _exclude_similar_entries(entries, existing_tokens, slot)
    if not filtered_entries:
        return None
    overall_best = _resolve_best_fragment(filtered_entries, composite_priority, diversity_state=diversity_state)
    overall_score = _effective_fragment_score(overall_best, composite_priority, diversity_state) if overall_best else -999.0

    priority_matchers = (
        lambda fragment: _matches_planet(fragment, "sun"),
        lambda fragment: _matches_planet(fragment, "moon"),
        lambda fragment: _matches_chart_ruler(fragment, chart_ruler),
        lambda fragment: _matches_stellium(fragment, stellium_planets),
    )

    for matcher in priority_matchers:
        subset = [(idx, fragment) for idx, fragment in filtered_entries if matcher(fragment)]
        if not subset:
            continue
        best = _resolve_best_fragment(subset, composite_priority, diversity_state=diversity_state)
        if best and _effective_fragment_score(best, composite_priority, diversity_state) >= overall_score - 0.015:
            return _format_fragment_output(best, slot)

    return _format_fragment_output(overall_best, slot) if overall_best else None


def _resolve_best_fragment(
    entries: Sequence[Tuple[int, Dict[str, Any]]],
    composite_priority: float,
    *,
    diversity_state: Mapping[str, Any] | None = None,
) -> Dict[str, Any] | None:
    best_fragment: Dict[str, Any] | None = None
    best_key: Tuple[float, int, str] | None = None

    for _, fragment in entries:
        score = _fragment_priority_score(fragment, composite_priority) - _diversity_penalty(fragment, diversity_state)
        trigger_rank = _trigger_type_rank(fragment)
        fragment_id = str(fragment.get("fragment_id") or "")
        current_key = (score, trigger_rank, fragment_id)
        if best_fragment is None or current_key > best_key:
            best_fragment = fragment
            best_key = current_key

    return best_fragment


def _effective_fragment_score(
    fragment: Mapping[str, Any] | None,
    composite_priority: float,
    diversity_state: Mapping[str, Any] | None,
) -> float:
    if not isinstance(fragment, Mapping):
        return -999.0
    return _fragment_priority_score(dict(fragment), composite_priority) - _diversity_penalty(fragment, diversity_state)


def _fragment_priority_score(fragment: Dict[str, Any], fallback: float) -> float:
    for key in ("salience_score", "priority_score", "score"):
        value = fragment.get(key)
        numeric = _coerce_float(value)
        if numeric is not None:
            return numeric
    return fallback




def _trigger_type_rank(fragment: Dict[str, Any]) -> int:
    trigger = fragment.get("trigger") or {}
    trigger_type = str(trigger.get("type") or "").strip().lower()
    if trigger_type == "planet":
        return 2
    if trigger_type == "planet_house":
        return 1
    return 0


def _matches_planet(fragment: Dict[str, Any], target: str) -> bool:
    if not target:
        return False
    planet = _extract_planet(fragment)
    return planet == target


def _matches_chart_ruler(fragment: Dict[str, Any], ruler: Optional[str]) -> bool:
    if not ruler:
        return False
    return _extract_planet(fragment) == ruler


def _matches_stellium(fragment: Dict[str, Any], stellium_planets: Sequence[str]) -> bool:
    planet = _extract_planet(fragment)
    return bool(planet and planet in stellium_planets)


def _extract_planet(fragment: Dict[str, Any]) -> str:
    trigger = fragment.get("trigger") or {}
    raw_planet = trigger.get("planet") or trigger.get("planet1") or fragment.get("planet")
    if raw_planet is None:
        return ""
    normalized = normalize_node_alias(normalize_planet_key(raw_planet))
    return normalized


def _coerce_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _aggregate_composite_priorities(composites: Sequence[Mapping[str, Any]]) -> Dict[str, float]:
    priorities: Dict[str, float] = {}
    for comp in composites:
        domain = comp.get("domain")
        if not isinstance(domain, str) or not domain.strip():
            continue
        key = canon_domain(domain)
        if not key:
            continue
        score = _coerce_float(comp.get("priority_score"))
        if score is None:
            score = 0.0
        score = _clamp_domain_priority(score)
        existing = priorities.get(key, 0.0)
        if score > existing:
            priorities[key] = score
    return priorities


def _clamp_domain_priority(value: float) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return DEFAULT_DOMAIN_PRIORITY
    if numeric < 0.0:
        return 0.0
    if numeric > 1.0:
        return 1.0
    return numeric


def _canonicalize_fragment_map(
    fragments: Mapping[str, Mapping[str, List[Dict[str, Any]]]]
) -> Dict[str, Mapping[str, List[Dict[str, Any]]]]:
    normalized: Dict[str, Mapping[str, List[Dict[str, Any]]]] = {}
    deferred: List[Tuple[str, Mapping[str, List[Dict[str, Any]]]]] = []
    for domain, entry in fragments.items():
        canonical = canon_domain(domain)
        if not canonical:
            continue
        if canonical in normalized:
            continue
        cleaned = str(domain or "").strip().lower()
        if canonical in CANONICAL_DOMAIN_SET and canonical == cleaned:
            normalized[canonical] = entry
        else:
            deferred.append((canonical, entry))
    for canonical, entry in deferred:
        normalized.setdefault(canonical, entry)
    return normalized


def _ensure_required_slots(
    domain: str,
    slots: Mapping[str, Sequence[Dict[str, Any]]],
    reduced_slots: Dict[str, Dict[str, Any] | None],
    composite_priority: float,
    tokens: List[set[str]],
    meta_info: Mapping[str, Any],
    axis_activation: Mapping[str, Any] | None,
    diversity_state: Mapping[str, Any] | None,
) -> None:
    required = ("cause", "mechanism", "potential")
    for slot in required:
        if reduced_slots.get(slot):
            continue
        candidates = slots.get(slot) or []
        candidates = _dedupe_and_score_candidates(
            candidates,
            domain=domain,
            slot=slot,
            meta_info=meta_info,
            axis_activation=axis_activation,
            domain_priority=_clamp_domain_priority(composite_priority),
        )
        fallback, reason = _fallback_fragment_for_slot(slot, candidates, composite_priority)
        if not fallback:
            continue
        fallback["selection_reason"] = "fallback_required_slot"
        fallback["why_empty"] = reason or "no_reason"
        reduced_slots[slot] = fallback
        if tokens is not None:
            fragment_tokens = _fragment_text_tokens(fallback, slot)
            if fragment_tokens:
                tokens.append(fragment_tokens)


def _fragment_text_tokens(fragment: Mapping[str, Any], slot: str) -> set[str] | None:
    if not fragment:
        return None
    text = fragment.get("text")
    normalized = normalize_slot_text(text, slot)
    if not normalized and text:
        normalized = str(text).strip()
    if not normalized:
        return None
    tokens = _tokens_from_text(normalized)
    return tokens if tokens else None


def _tokens_from_text(text: str) -> set[str]:
    return {token for token in re.findall(r"\w+", text.lower()) if token}


def _is_too_similar(candidate: set[str], existing_tokens: Sequence[set[str]]) -> bool:
    if not candidate or not existing_tokens:
        return False
    for tokens in existing_tokens:
        if not tokens:
            continue
        if _jaccard_similarity(candidate, tokens) >= SIMILARITY_THRESHOLD:
            return True
    return False


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def _exclude_similar_entries(
    entries: Sequence[Tuple[int, Mapping[str, Any]]],
    existing_tokens: Sequence[set[str]] | None,
    slot: str,
) -> List[Tuple[int, Mapping[str, Any]]]:
    if not existing_tokens:
        return list(entries)
    filtered: List[Tuple[int, Mapping[str, Any]]] = []
    for entry in entries:
        fragment = entry[1]
        tokens = _fragment_text_tokens(fragment, slot)
        if tokens and _is_too_similar(tokens, existing_tokens):
            continue
        filtered.append(entry)
    return filtered


def _detect_chart_ruler(meta_info: Mapping[str, Any]) -> Optional[str]:
    ruler = meta_info.get("chart_ruler")
    return str(ruler).lower() if ruler else None


def _detect_stellium_planets(meta_info: Mapping[str, Any]) -> Sequence[str]:
    planets = meta_info.get("stellium_planets") or []
    normalized: List[str] = []
    for planet in planets:
        if planet:
            normalized_planet = normalize_node_alias(normalize_planet_key(planet))
            if normalized_planet:
                normalized.append(normalized_planet)
    return normalized


def _fallback_fragment_for_slot(
    slot: str,
    candidates: Sequence[Dict[str, Any]],
    composite_priority: float,
) -> tuple[Dict[str, Any] | None, str | None]:
    if not candidates:
        return None, "no_candidates"
    entries = list(enumerate(candidates))
    best = _resolve_best_fragment(entries, composite_priority)
    if not best:
        return None, "no_best_candidate"
    return _format_fragment_output(best, slot), "similarity_filtered"


def _format_fragment_output(fragment: Dict[str, Any], slot: str) -> Dict[str, Any]:
    return {
        "text": fragment.get("text"),
        "trigger": fragment.get("trigger"),
        "intent": SLOT_INTENTS.get(slot, "unknown"),
        "salience_score": fragment.get("salience_score"),
        "supporting_facts": fragment.get("supporting_facts") or [],
    }


def _dedupe_and_score_candidates(
    candidates: Sequence[Dict[str, Any]],
    *,
    domain: str,
    slot: str,
    meta_info: Mapping[str, Any],
    axis_activation: Mapping[str, Any] | None,
    domain_priority: float,
) -> List[Dict[str, Any]]:
    if not candidates:
        return []
    enriched: List[Dict[str, Any]] = []
    for fragment in candidates:
        if not isinstance(fragment, Mapping):
            continue
        copied = dict(fragment)
        components = _salience_components(copied, meta_info, axis_activation)
        components["domain_priority"] = domain_priority
        active_components, effective_weights = _effective_salience_weights(
            copied, DEFAULT_SALIENCE_WEIGHTS
        )
        salience = _apply_salience_weights(components, active_components, effective_weights)
        copied["salience_score"] = round(salience, 4)
        copied["salience_breakdown"] = {
            "orb_strength": round(components["orb_strength"], 4),
            "dominance": round(components["dominance"], 4),
            "axis_weight_raw": round(components["axis_weight_raw"], 4),
            "axis_weight": round(components["axis_weight"], 4),
            "house_weight": round(components["house_weight"], 4),
            "pattern_bonus": round(components["pattern_bonus"], 4),
            "domain_priority": round(domain_priority, 4),
            "weights": dict(DEFAULT_SALIENCE_WEIGHTS),
            "active_components": list(active_components),
            "effective_weights": {key: round(value, 4) for key, value in effective_weights.items()},
            "final": round(salience, 4),
        }
        enriched.append(copied)

    grouped: Dict[Tuple[str, str, str, str, str, str], Dict[str, Any]] = {}
    for fragment in enriched:
        signature = _fragment_signature(fragment, domain=domain, slot=slot, meta_info=meta_info)
        entry = grouped.get(signature)
        if not entry:
            grouped[signature] = {
                "best": fragment,
                "supporting": [],
            }
            continue
        best = entry["best"]
        if _fragment_priority_score(fragment, 0.0) > _fragment_priority_score(best, 0.0):
            entry["supporting"].append(best)
            entry["best"] = fragment
        else:
            entry["supporting"].append(fragment)

    deduped: List[Dict[str, Any]] = []
    for entry in grouped.values():
        best = entry["best"]
        supporting = entry["supporting"]
        if supporting:
            summaries = [_supporting_fact_summary(item) for item in supporting]
            summaries.sort(
                key=lambda item: _coerce_float(item.get("salience_score")) or 0.0,
                reverse=True,
            )
            best["supporting_facts_full"] = list(summaries)
            best["supporting_facts"] = summaries[:5]
        deduped.append(best)
    return deduped


def _diversity_penalty(fragment: Mapping[str, Any], diversity_state: Mapping[str, Any] | None) -> float:
    if not diversity_state:
        return 0.0
    penalty = 0.0
    trigger = fragment.get("trigger") or {}
    planet = _extract_planet(dict(fragment))
    if planet:
        penalty += min(0.1, float((diversity_state.get("planets") or {}).get(planet, 0)) * 0.04)
    house = trigger.get("house")
    if house is not None:
        penalty += min(0.06, float((diversity_state.get("houses") or {}).get(str(house), 0)) * 0.03)
    rule_group = _rule_id_group(fragment.get("source_rule_ids"))
    if rule_group:
        penalty += min(0.06, float((diversity_state.get("rule_groups") or {}).get(rule_group, 0)) * 0.03)
    tokens = _fragment_text_tokens(fragment, fragment.get("type") or fragment.get("slot") or "")
    for prior in diversity_state.get("texts") or []:
        if not tokens or not prior:
            continue
        overlap = _jaccard_similarity(tokens, prior)
        if overlap >= 0.52:
            penalty += min(0.08, overlap * 0.1)
            break
    return min(0.18, penalty)


def _update_diversity_state(diversity_state: Mapping[str, Any], fragments: Sequence[Mapping[str, Any]]) -> None:
    planets = diversity_state.get("planets")
    houses = diversity_state.get("houses")
    rule_groups = diversity_state.get("rule_groups")
    texts = diversity_state.get("texts")
    if not isinstance(planets, Counter) or not isinstance(houses, Counter) or not isinstance(rule_groups, Counter) or not isinstance(texts, list):
        return
    for fragment in fragments:
        trigger = fragment.get("trigger") or {}
        planet = _extract_planet(dict(fragment))
        if planet:
            planets[planet] += 1
        house = trigger.get("house")
        if house is not None:
            houses[str(house)] += 1
        rule_group = _rule_id_group(fragment.get("source_rule_ids"))
        if rule_group:
            rule_groups[rule_group] += 1
        tokens = _fragment_text_tokens(fragment, fragment.get("intent") or fragment.get("type") or fragment.get("slot") or "")
        if tokens:
            texts.append(tokens)


def _supporting_fact_summary(fragment: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "text": fragment.get("text"),
        "slot": fragment.get("type") or fragment.get("slot"),
        "trigger": fragment.get("trigger"),
        "source_rule_ids": fragment.get("source_rule_ids") or [],
        "salience_score": fragment.get("salience_score"),
        "fragment_id": fragment.get("fragment_id"),
    }


def _fragment_signature(
    fragment: Mapping[str, Any],
    *,
    domain: str,
    slot: str,
    meta_info: Mapping[str, Any],
) -> Tuple[str, str, str, str, str, str]:
    trigger = fragment.get("trigger") or {}
    planet = _extract_planet(fragment)
    sign = str(trigger.get("sign") or _planet_sign_from_meta(planet, meta_info) or "").lower().strip()
    house_value = trigger.get("house")
    if house_value is None:
        house_value = _planet_house_from_meta(planet, meta_info)
    house = "" if house_value is None else str(house_value).strip()
    rule_id_group = _rule_id_group(fragment.get("source_rule_ids"))
    return (domain, slot, planet, sign, house, rule_id_group)


def _rule_id_group(value: Any) -> str:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        rule_id = next((str(item) for item in value if item), "")
    else:
        rule_id = str(value or "")
    rule_id = rule_id.strip().lower()
    if not rule_id:
        return ""
    if "_in_" in rule_id:
        return rule_id.split("_in_", 1)[0]
    return rule_id


def _compute_salience_score(
    fragment: Mapping[str, Any],
    *,
    domain_priority: float,
    meta_info: Mapping[str, Any],
    axis_activation: Mapping[str, Any] | None,
    weights: Mapping[str, float] | None = None,
) -> float:
    weights = weights or DEFAULT_SALIENCE_WEIGHTS
    components = _salience_components(fragment, meta_info, axis_activation)
    components["domain_priority"] = domain_priority
    active_components, effective_weights = _effective_salience_weights(fragment, weights)
    return _apply_salience_weights(components, active_components, effective_weights)


def _salience_components(
    fragment: Mapping[str, Any],
    meta_info: Mapping[str, Any],
    axis_activation: Mapping[str, Any] | None,
) -> Dict[str, float]:
    dominance = _dominance_score(fragment, meta_info)
    axis_weight_raw = _axis_activation_weight(fragment, meta_info, axis_activation)
    axis_effective = axis_weight_raw * (1.0 - dominance)
    return {
        "orb_strength": _orb_strength(fragment, meta_info),
        "dominance": dominance,
        "axis_weight": axis_effective,
        "axis_weight_raw": axis_weight_raw,
        "house_weight": _house_focus_weight(fragment, meta_info),
        "pattern_bonus": _pattern_bonus(fragment, meta_info),
    }


def _effective_salience_weights(
    fragment: Mapping[str, Any],
    weights: Mapping[str, float],
) -> tuple[list[str], Dict[str, float]]:
    trigger = fragment.get("trigger") or {}
    trigger_type = str(trigger.get("type") or "").strip().lower()
    if trigger_type == "aspect":
        active = ["orb", "dominance", "axis", "pattern", "domain"]
    elif trigger_type == "planet_house":
        active = ["dominance", "axis", "house", "domain"]
    else:
        active = ["dominance", "axis", "domain"]
    active_sum = sum(weights.get(key, 0.0) for key in active)
    if active_sum <= 0.0:
        return active, {key: 0.0 for key in active}
    return active, {key: weights.get(key, 0.0) / active_sum for key in active}


def _apply_salience_weights(
    components: Mapping[str, float],
    active_components: Sequence[str],
    effective_weights: Mapping[str, float],
) -> float:
    component_map = {
        "orb": "orb_strength",
        "dominance": "dominance",
        "axis": "axis_weight",
        "house": "house_weight",
        "pattern": "pattern_bonus",
        "domain": "domain_priority",
    }
    score = 0.0
    for key in active_components:
        component_key = component_map.get(key)
        if not component_key:
            continue
        score += effective_weights.get(key, 0.0) * components.get(component_key, 0.0)
    return score


def _orb_strength(fragment: Mapping[str, Any], meta_info: Mapping[str, Any]) -> float:
    trigger = fragment.get("trigger") or {}
    trigger_type = str(trigger.get("type") or "").lower()
    if trigger_type != "aspect":
        return 0.0
    aspects = meta_info.get("aspects_list") or []
    planet1 = normalize_node_alias(normalize_planet_key(trigger.get("planet1")))
    planet2 = normalize_node_alias(normalize_planet_key(trigger.get("planet2")))
    aspect_type = str(trigger.get("aspect") or "").lower()
    if not (planet1 and planet2 and aspect_type):
        return 0.0
    orb = None
    for aspect in aspects:
        p1 = normalize_node_alias(normalize_planet_key(aspect.get("planet1") or aspect.get("planet")))
        p2 = normalize_node_alias(normalize_planet_key(aspect.get("planet2") or aspect.get("target")))
        atype = str(aspect.get("type") or aspect.get("aspect") or "").lower()
        if {p1, p2} == {planet1, planet2} and atype == aspect_type:
            orb = aspect.get("orb")
            break
    if not isinstance(orb, (int, float)):
        return 0.0
    strength = 1.0 - min(float(orb) / 5.0, 1.0)
    return max(0.0, strength)


def _dominance_score(fragment: Mapping[str, Any], meta_info: Mapping[str, Any]) -> float:
    planet = _extract_planet(fragment)
    if not planet:
        return 0.0
    dominant = meta_info.get("dominant_planets") or []
    scores: Dict[str, float] = {}
    for item in dominant:
        if not isinstance(item, Mapping):
            continue
        name = str(item.get("planet") or "").lower().strip()
        score = _coerce_float(item.get("score")) or 0.0
        if name:
            scores[name] = max(scores.get(name, 0.0), score)
    if not scores:
        return 0.0
    max_score = max(scores.values()) or 0.0
    if max_score <= 0.0:
        return 0.0
    return min(1.0, scores.get(planet, 0.0) / max_score)


def _axis_activation_weight(
    fragment: Mapping[str, Any],
    meta_info: Mapping[str, Any],
    axis_activation: Mapping[str, Any] | None,
) -> float:
    if not axis_activation:
        return 0.0
    active_axes = axis_activation.get("active_axes") or []
    if not active_axes:
        return 0.0
    axis_signs: Dict[str, set[str]] = {
        "1-7": {"aries", "libra"},
        "4-10": {"cancer", "capricorn"},
        "2-8": {"taurus", "scorpio"},
        "3-9": {"gemini", "sagittarius"},
    }
    planet = _extract_planet(fragment)
    sign = _planet_sign_from_meta(planet, meta_info)
    if not sign:
        return 0.0
    active_signs: set[str] = set()
    for axis in active_axes:
        signs = axis_signs.get(str(axis))
        if signs:
            active_signs |= signs
    if not active_signs:
        return 0.0
    return _axis_affinity_weight(sign, active_signs)


def _axis_affinity_weight(sign: str, active_signs: set[str]) -> float:
    if sign in active_signs:
        return 1.0
    element = _sign_element(sign)
    modality = _sign_modality(sign)
    for axis_sign in active_signs:
        if element and element == _sign_element(axis_sign):
            return 0.7
        if modality and modality == _sign_modality(axis_sign):
            return 0.5
        if _share_ruler(sign, axis_sign):
            return 0.3
    return 0.1


def _sign_element(sign: str) -> str | None:
    return {
        "aries": "fire",
        "leo": "fire",
        "sagittarius": "fire",
        "taurus": "earth",
        "virgo": "earth",
        "capricorn": "earth",
        "gemini": "air",
        "libra": "air",
        "aquarius": "air",
        "cancer": "water",
        "scorpio": "water",
        "pisces": "water",
    }.get(sign)


def _sign_modality(sign: str) -> str | None:
    return {
        "aries": "cardinal",
        "cancer": "cardinal",
        "libra": "cardinal",
        "capricorn": "cardinal",
        "taurus": "fixed",
        "leo": "fixed",
        "scorpio": "fixed",
        "aquarius": "fixed",
        "gemini": "mutable",
        "virgo": "mutable",
        "sagittarius": "mutable",
        "pisces": "mutable",
    }.get(sign)


def _share_ruler(sign: str, axis_sign: str) -> bool:
    rulers = _sign_rulers(sign)
    axis_rulers = _sign_rulers(axis_sign)
    return bool(rulers and axis_rulers and rulers & axis_rulers)


def _sign_rulers(sign: str) -> set[str]:
    return {
        "aries": {"mars"},
        "taurus": {"venus"},
        "gemini": {"mercury"},
        "cancer": {"moon"},
        "leo": {"sun"},
        "virgo": {"mercury"},
        "libra": {"venus"},
        "scorpio": {"mars", "pluto"},
        "sagittarius": {"jupiter"},
        "capricorn": {"saturn"},
        "aquarius": {"saturn", "uranus"},
        "pisces": {"jupiter", "neptune"},
    }.get(sign, set())


def _house_focus_weight(fragment: Mapping[str, Any], meta_info: Mapping[str, Any]) -> float:
    trigger = fragment.get("trigger") or {}
    house = trigger.get("house")
    if house is None:
        planet = _extract_planet(fragment)
        house = _planet_house_from_meta(planet, meta_info)
    if house is None:
        return 0.0
    house_clusters = meta_info.get("house_clusters") or {}
    try:
        house_value = int(house)
    except (TypeError, ValueError):
        return 0.0
    cluster_size = house_clusters.get(house_value, 0)
    if cluster_size <= 1:
        return 0.0
    if cluster_size == 2:
        return 0.33
    if cluster_size == 3:
        return 0.67
    return 1.0


def _pattern_bonus(fragment: Mapping[str, Any], meta_info: Mapping[str, Any]) -> float:
    patterns = meta_info.get("aspect_patterns") or []
    if not patterns:
        return 0.0
    planets = _fragment_planets(fragment)
    if not planets:
        return 0.0
    bonus = 0.0
    for pattern in patterns:
        if not isinstance(pattern, Mapping):
            continue
        participants = pattern.get("planets") or []
        score = _coerce_float(pattern.get("score")) or 0.0
        if any(planet in participants for planet in planets):
            bonus = max(bonus, min(1.0, score))
    return bonus


def _fragment_planets(fragment: Mapping[str, Any]) -> List[str]:
    trigger = fragment.get("trigger") or {}
    planets = []
    for key in ("planet", "planet1", "planet2"):
        value = trigger.get(key) or fragment.get(key)
        if value:
            normalized = normalize_node_alias(normalize_planet_key(value))
            if normalized and normalized not in planets:
                planets.append(normalized)
    return planets


def _planet_sign_from_meta(planet: str, meta_info: Mapping[str, Any]) -> str | None:
    if not planet:
        return None
    signs = meta_info.get("planet_signs") or {}
    sign = signs.get(planet)
    return str(sign).lower().strip() if sign else None


def _planet_house_from_meta(planet: str, meta_info: Mapping[str, Any]) -> int | None:
    if not planet:
        return None
    houses = meta_info.get("planet_houses") or {}
    house = houses.get(planet)
    if house is None:
        return None
    try:
        return int(house)
    except (TypeError, ValueError):
        return None


def _select_focus_domains(
    reduced: Mapping[str, Mapping[str, Any]],
    *,
    max_domains: int,
) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    scored: List[Tuple[str, float]] = []
    for domain, entry in reduced.items():
        slots = entry.get("slots") or {}
        scores = [
            _coerce_float(fragment.get("salience_score"))
            for fragment in slots.values()
            if isinstance(fragment, Mapping) and fragment.get("salience_score") is not None
        ]
        scores = [score for score in scores if score is not None]
        if scores:
            scores.sort(reverse=True)
            domain_score = sum(scores[:2])
        else:
            domain_score = 0.0
        scored.append((domain, domain_score))
    scored.sort(key=lambda item: item[1], reverse=True)
    selected = {domain for domain, _ in scored[:max_domains]}
    compressed: List[Dict[str, Any]] = []
    for domain, entry in reduced.items():
        if domain in selected:
            continue
        slots = entry.get("slots") or {}
        best_slot = None
        best_score = -1.0
        for slot_name, fragment in slots.items():
            if not isinstance(fragment, Mapping):
                continue
            score = _coerce_float(fragment.get("salience_score")) or 0.0
            if score > best_score:
                best_score = score
                best_slot = (slot_name, fragment)
        if best_slot:
            slot_name, fragment = best_slot
            compressed.append(
                {
                    "domain": domain,
                    "slot": slot_name,
                    "text": fragment.get("text"),
                    "salience_score": fragment.get("salience_score"),
                }
            )
    selected_map = {domain: dict(reduced[domain]) for domain in reduced if domain in selected}
    return selected_map, compressed


from app.builders.phase2_selector_engine import Phase2SelectionError, Phase2Selector
