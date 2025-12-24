from __future__ import annotations

import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from app.builders.semantic_normalizer import normalize_slot_text
from app.helpers.meta_detectors import normalize_node_alias, normalize_planet_key


SLOT_INTENTS: Dict[str, str] = {
    "cause": "core_identity",
    "mechanism": "stabilizer",
    "effect": "tension_source",
    "shadow": "tension_source",
    "potential": "growth_path",
}

SIMILARITY_THRESHOLD = 0.7


def select_phase2_fragments(
    fragments_by_domain: Mapping[str, Mapping[str, List[Dict[str, Any]]]],
    composites: Sequence[Mapping[str, Any]],
    meta_info: Mapping[str, Any],
    domain_regulators: Mapping[str, Dict[str, Any]] | None = None,
) -> Dict[str, Dict[str, Any]]:
    chart_ruler = _detect_chart_ruler(meta_info)
    stellium_planets = _detect_stellium_planets(meta_info)
    domain_priorities = _aggregate_composite_priorities(composites)

    reduced: Dict[str, Dict[str, Any]] = {}
    domain_text_tokens: Dict[str, List[set[str]]] = {}
    for domain, slots in fragments_by_domain.items():
        domain_key = domain.lower()
        tokens = domain_text_tokens.setdefault(domain_key, [])
        reduced_slots: Dict[str, Dict[str, Any] | None] = {}
        for slot in ("cause", "mechanism", "effect", "shadow", "potential"):
            candidates = slots.get(slot) or []
            reduced_slots[slot] = _select_fragment_by_priority(
                candidates,
                chart_ruler=chart_ruler,
                stellium_planets=stellium_planets,
                composite_priority=domain_priorities.get(domain_key, 0.0),
                slot=slot,
                existing_tokens=tokens,
            )
            fragment = reduced_slots[slot]
            if fragment:
                fragment_tokens = _fragment_text_tokens(fragment, slot)
                if fragment_tokens:
                    tokens.append(fragment_tokens)
        anchor = reduced_slots.get("cause")
        reduced[domain_key] = {"slots": reduced_slots, "anchor": anchor}
    return reduced


def _select_fragment_by_priority(
    candidates: Sequence[Dict[str, Any]],
    *,
    chart_ruler: Optional[str],
    stellium_planets: Sequence[str],
    composite_priority: float,
    slot: str,
    existing_tokens: Sequence[set[str]] | None = None,
) -> Dict[str, Any] | None:
    if not candidates:
        return None

    entries = list(enumerate(candidates))
    filtered_entries = _exclude_similar_entries(entries, existing_tokens, slot)
    if not filtered_entries:
        return None

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
        best = _resolve_best_fragment(subset, composite_priority)
        if best:
            return _format_fragment_output(best, slot)

    final_best = _resolve_best_fragment(filtered_entries, composite_priority)
    return _format_fragment_output(final_best, slot) if final_best else None


def _resolve_best_fragment(
    entries: Sequence[Tuple[int, Dict[str, Any]]],
    composite_priority: float,
) -> Dict[str, Any] | None:
    best_fragment: Dict[str, Any] | None = None
    best_key: Tuple[float, int] | None = None

    for _, fragment in entries:
        score = _fragment_priority_score(fragment, composite_priority)
        trigger_rank = _trigger_type_rank(fragment)
        current_key = (score, trigger_rank)
        if best_fragment is None or current_key > best_key:
            best_fragment = fragment
            best_key = current_key

    return best_fragment


def _fragment_priority_score(fragment: Dict[str, Any], fallback: float) -> float:
    for key in ("priority_score", "score"):
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
        key = domain.strip().lower()
        score = _coerce_float(comp.get("priority_score"))
        if score is None:
            score = 0.0
        existing = priorities.get(key, 0.0)
        if score > existing:
            priorities[key] = score
    return priorities


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


def _format_fragment_output(fragment: Dict[str, Any], slot: str) -> Dict[str, Any]:
    return {
        "text": fragment.get("text"),
        "trigger": fragment.get("trigger"),
        "intent": SLOT_INTENTS.get(slot, "unknown"),
    }
