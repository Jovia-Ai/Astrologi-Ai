from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Mapping, Sequence

from app.helpers.meta_detectors import normalize_node_alias, normalize_planet_key

TYPE_NAMES = ("cause", "mechanism", "effect", "shadow", "potential")
SEMANTIC_SIMILARITY_THRESHOLD = 0.7
MOON_BASE_COMPOSITE = "psychology_moon_base"


def composite_to_fragments(
    composites: Sequence[Mapping[str, Any]],
    rules_output: Mapping[str, Mapping[str, List[Dict[str, Any]]]],
    meta_info: Mapping[str, Any],
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    fragments: Dict[str, Dict[str, Dict[str, Any]]] = {}
    domain_map: Dict[str, List[Mapping[str, Any]]] = {}

    for comp in composites:
        raw_domain = comp.get("domain")
        domains: List[str] = []
        if isinstance(raw_domain, str) and raw_domain.strip():
            domains.append(raw_domain.strip().lower())
        raw_domains = comp.get("domains")
        if isinstance(raw_domains, Sequence) and not isinstance(raw_domains, str):
            for entry in raw_domains:
                if isinstance(entry, str) and entry.strip():
                    domains.append(entry.strip().lower())
        for key in domains:
            domain_map.setdefault(key, []).append(comp)

    for domain, comps in domain_map.items():
        merged = _merge_composites(comps)
        slots, anchor = _select_domain_fragments(
            domain,
            merged,
            interpretation=rules_output,
            meta_info=meta_info,
        )
        entry: Dict[str, Dict[str, Any]] = {"slots": slots}
        if anchor:
            entry["anchor"] = anchor
            entry["narrative_anchor"] = anchor.get("trigger", {})
            fragments[domain] = entry
    return fragments


def _merge_composites(composites: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    merged_sources: List[str] = []
    composite_ids: List[str] = []
    for comp in composites:
        sources = comp.get("sources") or []
        if isinstance(sources, Sequence):
            merged_sources.extend(str(item) for item in sources if item)
        comp_id = comp.get("composite_id")
        if isinstance(comp_id, str) and comp_id.strip():
            composite_ids.append(comp_id.strip())
    return {"sources": merged_sources, "composite_ids": composite_ids}


def _select_domain_fragments(
    domain: str,
    composite: Mapping[str, Any],
    *,
    interpretation: Mapping[str, Mapping[str, List[Dict[str, Any]]]],
    meta_info: Mapping[str, Any],
) -> tuple[Dict[str, Dict[str, Any]], Dict[str, Any] | None]:
    selected: Dict[str, Dict[str, Any]] = {}
    domain_entries = interpretation.get(domain, {})
    candidates = _build_candidate_list(domain_entries, composite, meta_info)
    if not candidates:
        return selected, None

    trigger_usage: Counter[str] = Counter(entry["trigger_id"] for entry in candidates)
    for entry in candidates:
        if trigger_usage[entry["trigger_id"]] > 1:
            entry["score"] -= 4

    sorted_candidates = sorted(
        candidates,
        key=lambda x: (
            -int(x["source_match"]),
            -x["score"],
            -int(x["is_sun_moon"]),
        ),
    )

    anchor_candidate = _select_anchor(sorted_candidates, domain)
    anchor_trigger = anchor_candidate["fragment"].get("trigger") if anchor_candidate else {}
    anchor_info: Dict[str, Any] | None = None

    used_slots: set[str] = set()
    used_triggers: set[str] = set()
    selected_planets: set[str] = set()
    source_composite_ids = list(composite.get("composite_ids") or [])
    selected_texts: List[str] = []
    for slot in TYPE_NAMES:
        entry = _pick_slot_entry(sorted_candidates, slot, used_triggers, anchor_trigger)
        if not entry:
            continue
        normalized_text = _normalize_sentence(entry["fragment"]["text"])
        if not normalized_text:
            continue
        if _is_semantically_similar(normalized_text, selected_texts):
            continue
        selected[slot] = {
            "text": normalized_text,
            "fragment_ref": entry["trigger_id"],
            "trigger": entry["fragment"].get("trigger", {}),
            "planet": entry.get("planet"),
            "score": entry["score"],
            "source_composite_ids": source_composite_ids,
            "source_rule_ids": entry["fragment"].get("source_rule_ids", []) or [],
            "source_triggers": entry["fragment"].get("source_triggers", []) or [],
        }
        if slot == "cause" and (anchor_candidate and entry["trigger_id"] == anchor_candidate["trigger_id"]):
            anchor_info = selected[slot]
        used_slots.add(slot)
        used_triggers.add(entry["trigger_id"])
        selected_planets.add(entry.get("planet") or "")
        selected_texts.append(normalized_text)

    if not anchor_info and "cause" in selected:
        anchor_info = selected["cause"]
    if anchor_info:
        anchor_trigger = anchor_info.get("trigger", anchor_trigger)

    return selected, anchor_info


def _pick_slot_entry(
    candidates: List[Dict[str, Any]],
    slot: str,
    used_triggers: set[str],
    anchor_trigger: Mapping[str, Any],
) -> Dict[str, Any] | None:
    preference = {
        "mechanism": {"moon", "mercury"},
        "effect": {"moon", "mercury", "jupiter"},
        "shadow": {"saturn", "lilith"},
        "potential": {"node", "jupiter"},
    }

    filtered = [
        entry
        for entry in candidates
        if entry["slot"] == slot and entry["trigger_id"] not in used_triggers
    ]
    if not filtered:
        return None

    filtered.sort(key=lambda entry: entry["score"], reverse=True)
    top_score = filtered[0]["score"]
    contenders = [
        entry for entry in filtered if abs(entry["score"] - top_score) < 0.01
    ]

    def tie_break_key(entry: Dict[str, Any]) -> tuple[int, int, int, int, int]:
        candidate_trigger = entry["fragment"].get("trigger", {})
        candidate_planet = normalize_node_alias(
            normalize_planet_key(candidate_trigger.get("planet"))
        )
        preference_bonus = 1 if slot in preference and candidate_planet in preference[slot] else 0
        anchor_bonus = 1 if _shares_anchor(candidate_trigger, anchor_trigger) else 0
        moon_bonus = 1 if candidate_planet == "moon" and MOON_BASE_COMPOSITE in entry.get("composite_ids", set()) else 0
        return (
            preference_bonus,
            anchor_bonus,
            moon_bonus,
            int(entry["is_sun_moon"]),
            int(entry["source_match"]),
        )

    return max(contenders, key=tie_break_key)


def _shares_anchor(trigger: Mapping[str, Any], anchor: Mapping[str, Any]) -> bool:
    if not trigger or not anchor:
        return False
    trigger_planet = normalize_node_alias(normalize_planet_key(trigger.get("planet")))
    anchor_planet = normalize_node_alias(normalize_planet_key(anchor.get("planet")))
    if trigger_planet and anchor_planet and trigger_planet == anchor_planet:
        return True
    trigger_house = trigger.get("house")
    anchor_house = anchor.get("house")
    if trigger_house and anchor_house and trigger_house == anchor_house:
        return True
    return False


def _select_anchor(candidates: List[Dict[str, Any]], domain: str) -> Dict[str, Any] | None:
    cause_candidates = [c for c in candidates if c["slot"] == "cause"]
    if not cause_candidates:
        return None
    if domain.lower() == "identity":
        for candidate in cause_candidates:
            planet = normalize_node_alias(normalize_planet_key(candidate["fragment"].get("trigger", {}).get("planet")))
            if planet == "sun":
                return candidate
    return sorted(
        cause_candidates,
        key=lambda x: (
            -int(x["is_sun_moon"]),
            -x["score"],
            -int(x["source_match"]),
        ),
    )[0]


def _build_candidate_list(
    domain_entries: Mapping[str, List[Dict[str, Any]]],
    composite: Mapping[str, Any],
    meta_info: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    source_triggers = _parse_sources(composite.get("sources") or [])
    composite_ids = set(str(cid).strip() for cid in composite.get("composite_ids") or [])
    for slot, fragments in domain_entries.items():
        for fragment in fragments or []:
            if not isinstance(fragment, Mapping):
                continue
            fragment_trigger = fragment.get("trigger") or {}
            trigger_id = _trigger_identifier(fragment_trigger)
            score = _base_fragment_score(fragment_trigger, meta_info)
            source_match = _matches_any_source(fragment_trigger, source_triggers)
            planet_name = normalize_node_alias(normalize_planet_key(fragment_trigger.get("planet")))
            candidates.append(
                {
                    "fragment": fragment,
                    "slot": slot,
                    "score": score + (5 if source_match else 0),
                    "source_match": source_match,
                    "trigger_id": trigger_id,
                    "is_sun_moon": _is_sun_or_moon(fragment_trigger),
                    "planet": planet_name,
                    "composite_ids": composite_ids,
                }
            )
    return candidates


def _is_semantically_similar(candidate: str, selected_texts: Sequence[str]) -> bool:
    candidate_tokens = _token_set(candidate)
    if not candidate_tokens:
        return False
    for existing in selected_texts:
        existing_tokens = _token_set(existing)
        if not existing_tokens:
            continue
        union_size = len(candidate_tokens | existing_tokens)
        if union_size == 0:
            continue
        overlap = len(candidate_tokens & existing_tokens)
        if overlap / union_size >= SEMANTIC_SIMILARITY_THRESHOLD:
            return True
    return False


def _token_set(text: str) -> set[str]:
    return {token for token in re.findall(r"\w+", text.lower()) if token}


def _base_fragment_score(trigger: Mapping[str, Any], meta_info: Mapping[str, Any]) -> int:
    score = _planet_weight(trigger.get("planet") or trigger.get("planet1"))
    if trigger.get("house"):
        score += _house_weight(trigger["house"])
        if trigger["house"] == 12 and meta_info.get("house_counts", {}).get(12, 0) >= 2:
            score += 1
        if trigger["house"] in meta_info.get("stelliums", {}):
            score += 3
    return score


def _planet_weight(value: Any) -> int:
    planet = normalize_node_alias(normalize_planet_key(value))
    if not planet:
        return 1
    weights = {
        "sun": 5,
        "moon": 4,
        "ascendant": 4,
        "mercury": 3,
        "venus": 3,
        "mars": 3,
        "jupiter": 2,
        "saturn": 2,
        "uranus": 1,
        "neptune": 1,
        "pluto": 1,
        "node": 1,
        "lilith": 1,
    }
    return weights.get(planet, 1)


def _house_weight(house: Any) -> int:
    try:
        value = int(house)
    except (TypeError, ValueError):
        return 0
    house_weights = {
        1: 3,
        4: 3,
        7: 3,
        10: 3,
        2: 2,
        5: 2,
        8: 2,
        11: 2,
        3: 1,
        6: 1,
        9: 1,
        12: 1,
    }
    return house_weights.get(value, 0)


def _trigger_identifier(trigger: Mapping[str, Any]) -> str:
    keys = [
        trigger.get("type", ""),
        trigger.get("planet", ""),
        str(trigger.get("house", "")),
        trigger.get("aspect", ""),
        trigger.get("planet1", ""),
        trigger.get("planet2", ""),
    ]
    return "|".join(str(key).lower() for key in keys if key)


def _parse_sources(sources: Sequence[str]) -> List[Dict[str, Any]]:
    parsed = []
    for source in sources:
        if not isinstance(source, str):
            continue
        normalized = source.lower()
        planet = normalize_node_alias(normalize_planet_key(normalized.split("_", 1)[0]))
        house = None
        sign = None
        if "house" in normalized:
            for part in normalized.split("_"):
                if part.endswith("th") or part.isdigit():
                    digits = "".join(ch for ch in part if ch.isdigit())
                    if digits:
                        house = int(digits)
                        break
        for sign_name in {
            "aries",
            "taurus",
            "gemini",
            "cancer",
            "leo",
            "virgo",
            "libra",
            "scorpio",
            "sagittarius",
            "capricorn",
            "aquarius",
            "pisces",
        }:
            if sign_name in normalized:
                sign = sign_name
                break
        parsed.append({"planet": planet, "house": house, "sign": sign})
    return parsed


def _matches_any_source(trigger: Mapping[str, Any], sources: List[Dict[str, Any]]) -> bool:
    trigger_planet = normalize_node_alias(normalize_planet_key(trigger.get("planet")))
    trigger_house = trigger.get("house")
    trigger_sign = trigger.get("sign")
    for source in sources:
        if source.get("planet") and source["planet"] != trigger_planet:
            continue
        if source.get("house") and trigger_house != source["house"]:
            continue
        if source.get("sign") and trigger_sign != source["sign"]:
            continue
        return True
    return False


def _is_sun_or_moon(trigger: Mapping[str, Any]) -> bool:
    planet = normalize_node_alias(normalize_planet_key(trigger.get("planet")))
    return planet in {"sun", "moon"}


def _normalize_sentence(text: Any) -> str:
    if not text:
        return ""
    return " ".join(str(text).strip().split())
