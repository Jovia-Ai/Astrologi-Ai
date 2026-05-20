from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Mapping, Sequence

from app.engine.tone_profile import ToneProfile
from app.helpers.domain_normalizer import canon_domain


CORE_STORY_SECTIONS = [
    ("inner_core", "identity"),
    ("emotions", "psychology"),
    ("mind", "mind"),
    ("relationships", "relationships"),
]


def build_core_story_plan(
    phase2_snapshot: Mapping[str, Any],
    meta_info: Mapping[str, Any],
    tone_profile: Mapping[str, Any] | ToneProfile | None,
    upper_meaning_gate: Mapping[str, Any] | None,
    dynamic_insights: Mapping[str, Any] | None = None,
    composite_meanings: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    sections: list[Dict[str, Any]] = []
    missing_slots: list[str] = []
    fallback_used: list[str] = []
    blocked_sections: list[str] = []
    slot_empty_reasons: Dict[str, str] = {}
    fallback_sources: Dict[str, str] = {}
    by_domain_slot, by_domain = _index_phase2_accepted(phase2_snapshot)
    accepted_domains = sorted(by_domain.keys()) if by_domain else sorted(phase2_snapshot.keys())

    headline_ref = _headline_ref(composite_meanings)
    spine_refs = _paragraph_spine_refs(dynamic_insights)

    for section_id, domain in CORE_STORY_SECTIONS:
        slots: Dict[str, Any] = {}
        if by_domain_slot:
            for slot_name in ("cause", "mechanism", "effect", "shadow", "potential"):
                frag = by_domain_slot.get((domain, slot_name))
                if isinstance(frag, Mapping):
                    slots[slot_name] = frag
        else:
            domain_entry = phase2_snapshot.get(domain) or {}
            slots = domain_entry.get("slots") or {}
            if not isinstance(slots, Mapping):
                slots = {}
        filled, used_fallback, missing, reasons, sources = _fill_section_slots(slots, domain)
        sentence_target = _sentence_target(section_id)
        sentences = _build_section_sentences(
            domain,
            slots,
            by_domain.get(domain) or [],
            target_count=sentence_target,
        )
        if missing:
            missing_slots.extend([f"{domain}.{slot}" for slot in missing])
        if used_fallback:
            fallback_used.extend([f"{domain}.{slot}" for slot in used_fallback])
        for slot, reason in reasons.items():
            slot_empty_reasons[f"{domain}.{slot}"] = reason
        for slot, source in sources.items():
            fallback_sources[f"{domain}.{slot}"] = source
        if not filled:
            blocked_sections.append(section_id)
        sections.append(
            {
                "id": section_id,
                "section_id": section_id,
                "domain": domain,
                "required": True,
                "slots": filled,
                "headline": headline_ref if section_id == "inner_core" else None,
                "spine": spine_refs.get(section_id),
                "sentences": sentences,
                "fallback_used": bool(used_fallback),
                "missing_slots": missing,
            }
        )

    upper_enabled = bool((upper_meaning_gate or {}).get("enabled"))
    upper_payload = {
        "enabled": upper_enabled,
        "reasons": (upper_meaning_gate or {}).get("reasons") or [],
        "fragment_ids": [],
    }
    engine_version = "core_story.v1"

    spines = _build_core_story_spines(dynamic_insights)
    selected_spines = _spines_by_section(spines)
    spine_debug = _spine_debug(dynamic_insights, spines)
    composite_selected = _select_composite_meanings(composite_meanings)
    used_fragments = _collect_used_fragments(sections)
    plan = {
        "schema_version": "narrative_plan.v1",
        "plan_id": _core_story_plan_id(sections, upper_payload, engine_version, composite_selected),
        "sections": sections,
        "upper_meaning": upper_payload,
        "spines": spines,
        "composite_meanings": {"selected": composite_selected},
        "tone_profile": tone_profile if isinstance(tone_profile, Mapping) else None,
        "data_quality": {
            "fallback_used": fallback_used,
            "missing_slots": missing_slots,
            "blocked_sections": blocked_sections,
        },
        "engine_version": engine_version,
        "debug": {
            "slot_empty_reasons": slot_empty_reasons,
            "fallback_sources": fallback_sources,
            "upper_meaning_reasons": upper_payload["reasons"],
            "phase2_domains": accepted_domains,
            "max_domains": 3,
            "selected_spines": selected_spines,
            "spine_scores": spine_debug,
            "composite_meanings": composite_selected,
            "used_fragments": used_fragments,
        },
    }
    return plan


def _build_core_story_spines(dynamic_insights: Mapping[str, Any] | None) -> list[Dict[str, Any]]:
    if not dynamic_insights:
        return []
    selected = dynamic_insights.get("selected")
    if not isinstance(selected, list):
        return []
    candidates: list[Dict[str, Any]] = []
    for entry in selected:
        if not isinstance(entry, Mapping):
            continue
        insight_id = entry.get("insight_id")
        strength = _safe_float(entry.get("strength"))
        instance_id = entry.get("instance_id") or ""
        themes = entry.get("themes") or []
        story_spine = entry.get("story_spine") or {}
        candidates.append(
            {
                "spine_id": insight_id,
                "strength": strength,
                "instance_id": instance_id,
                "themes": themes,
                "kind": entry.get("kind"),
                "title": entry.get("title"),
                "story_spine": story_spine,
            }
        )

    def _sort_key(item: Mapping[str, Any]) -> tuple:
        return (
            -_safe_float(item.get("strength")),
            str(item.get("spine_id") or ""),
            str(item.get("instance_id") or ""),
        )

    p1_candidates = [
        item
        for item in candidates
        if _map_spine_paragraph(item.get("themes") or []) == 1
        and (item.get("story_spine") or {}).get("p1")
    ]
    p3_candidates = [
        item
        for item in candidates
        if _map_spine_paragraph(item.get("themes") or []) == 3
        and (item.get("story_spine") or {}).get("p3")
    ]
    p1_candidates.sort(key=_sort_key)
    p3_candidates.sort(key=_sort_key)

    spines_out: list[Dict[str, Any]] = []
    if p1_candidates:
        chosen = p1_candidates[0]
        spines_out.append(
            {
                "spine_id": chosen.get("spine_id"),
                "instance_id": chosen.get("instance_id"),
                "paragraph": 1,
                "strength": chosen.get("strength"),
                "themes": chosen.get("themes"),
                "kind": chosen.get("kind"),
                "title": chosen.get("title"),
            }
        )
    if p3_candidates:
        chosen = next(
            (item for item in p3_candidates if item.get("spine_id") != (spines_out[0]["spine_id"] if spines_out else None)),
            p3_candidates[0],
        )
        spines_out.append(
            {
                "spine_id": chosen.get("spine_id"),
                "instance_id": chosen.get("instance_id"),
                "paragraph": 3,
                "strength": chosen.get("strength"),
                "themes": chosen.get("themes"),
                "kind": chosen.get("kind"),
                "title": chosen.get("title"),
            }
        )
    return spines_out[:2]


def _map_spine_paragraph(themes: Sequence[str]) -> int | None:
    theme_set = {str(theme) for theme in themes if theme}
    if theme_set.intersection({"identity", "mind"}):
        return 1
    if theme_set.intersection({"relationships", "psychology"}):
        return 3
    return None


def _spines_by_section(spines: Sequence[Mapping[str, Any]]) -> Dict[str, List[str]]:
    by_section: Dict[str, List[str]] = {}
    for spine in spines:
        spine_id = spine.get("spine_id")
        paragraph = spine.get("paragraph")
        if not spine_id or paragraph is None:
            continue
        section = "inner_core" if paragraph == 1 else "relationships" if paragraph == 3 else "emotions"
        by_section.setdefault(section, []).append(str(spine_id))
    return by_section


def _select_composite_meanings(
    composite_meanings: Mapping[str, Any] | None,
) -> List[Dict[str, Any]]:
    if not composite_meanings:
        return []
    selected = composite_meanings.get("selected")
    if not isinstance(selected, list):
        return []
    results: List[Dict[str, Any]] = []
    for entry in selected:
        if not isinstance(entry, Mapping):
            continue
        meaning_id = entry.get("meaning_id")
        instance_id = entry.get("instance_id")
        if meaning_id and instance_id:
            results.append({"meaning_id": meaning_id, "instance_id": instance_id})
    return results


def _collect_used_fragments(sections: Sequence[Mapping[str, Any]]) -> Dict[str, List[str]]:
    used: Dict[str, List[str]] = {}
    for section in sections:
        section_id = section.get("section_id")
        slots = section.get("slots") if isinstance(section, Mapping) else None
        if not section_id or not isinstance(slots, Mapping):
            continue
        for slot_entry in slots.values():
            if not isinstance(slot_entry, Mapping):
                continue
            fragment_id = slot_entry.get("fragment_id")
            if not fragment_id:
                continue
            used.setdefault(str(section_id), []).append(str(fragment_id))
        sentences = section.get("sentences") if isinstance(section, Mapping) else None
        if isinstance(sentences, list):
            for entry in sentences:
                if not isinstance(entry, Mapping):
                    continue
                fragment_id = entry.get("fragment_id")
                if fragment_id:
                    used.setdefault(str(section_id), []).append(str(fragment_id))
    return used


def _headline_ref(composite_meanings: Mapping[str, Any] | None) -> Dict[str, str] | None:
    if not composite_meanings:
        return None
    selected = composite_meanings.get("selected")
    if not isinstance(selected, list) or not selected:
        return None
    first = selected[0]
    if not isinstance(first, Mapping):
        return None
    meaning_id = first.get("meaning_id")
    instance_id = first.get("instance_id")
    if meaning_id and instance_id:
        return {"cm_id": str(meaning_id), "instance_id": str(instance_id)}
    return None


def _paragraph_spine_refs(dynamic_insights: Mapping[str, Any] | None) -> Dict[str, Dict[str, str]]:
    refs: Dict[str, Dict[str, str]] = {}
    if not dynamic_insights:
        return refs
    selected = dynamic_insights.get("selected")
    if not isinstance(selected, list):
        return refs
    by_paragraph: Dict[str, list[Mapping[str, Any]]] = {"p1": [], "p2": [], "p3": []}
    for entry in selected:
        if not isinstance(entry, Mapping):
            continue
        story = entry.get("story_spine") or {}
        if story.get("p1"):
            by_paragraph["p1"].append(entry)
        if story.get("p2"):
            by_paragraph["p2"].append(entry)
        if story.get("p3"):
            by_paragraph["p3"].append(entry)
    for key, section_id in (("p1", "inner_core"), ("p2", "emotions"), ("p3", "relationships")):
        candidates = sorted(
            by_paragraph.get(key) or [],
            key=lambda item: (-_safe_float(item.get("strength")), str(item.get("insight_id") or ""), str(item.get("instance_id") or "")),
        )
        if candidates:
            best = candidates[0]
            insight_id = best.get("insight_id")
            instance_id = best.get("instance_id")
            if insight_id and instance_id:
                refs[section_id] = {"insight_id": str(insight_id), "instance_id": str(instance_id)}
    return refs


def _sentence_target(section_id: str) -> int:
    if section_id == "inner_core":
        return 4
    if section_id == "relationships":
        return 3
    return 3


def _role_for_slot(slot: str) -> str:
    mapping = {
        "cause": "claim",
        "mechanism": "mechanism",
        "effect": "outer",
        "shadow": "shadow",
        "potential": "growth",
    }
    return mapping.get(slot, "explain")


def _build_section_sentences(
    domain: str,
    slots: Mapping[str, Any],
    accepted_domain: Sequence[Mapping[str, Any]],
    *,
    target_count: int,
) -> List[Dict[str, Any]]:
    sentences: List[Dict[str, Any]] = []
    used_ids: set[str] = set()

    def add_fragment(fragment: Mapping[str, Any], slot_name: str, role: str) -> None:
        fragment_id = _fragment_id_from_fragment(fragment)
        if not fragment_id or fragment_id in used_ids:
            return
        sentences.append(
            {
                "fragment_id": fragment_id,
                "domain": domain,
                "slot": slot_name,
                "role": role,
            }
        )
        used_ids.add(fragment_id)

    for slot_name in ("cause", "mechanism", "effect", "shadow", "potential"):
        fragment = slots.get(slot_name)
        if isinstance(fragment, Mapping):
            add_fragment(fragment, slot_name, _role_for_slot(slot_name))
        if len(sentences) >= target_count:
            return sentences[:target_count]

    for slot_name in ("cause", "mechanism", "effect", "shadow", "potential"):
        fragment = slots.get(slot_name)
        if not isinstance(fragment, Mapping):
            continue
        supporting = fragment.get("supporting_facts") or []
        for support in supporting:
            if not isinstance(support, Mapping):
                continue
            if support.get("slot") != slot_name:
                continue
            add_fragment(support, slot_name, _role_for_slot(slot_name))
            if len(sentences) >= target_count:
                return sentences[:target_count]

    for slot_name in ("mechanism", "effect"):
        fragment = slots.get(slot_name)
        if isinstance(fragment, Mapping):
            add_fragment(fragment, slot_name, _role_for_slot(slot_name))
        if len(sentences) >= target_count:
            return sentences[:target_count]

    if accepted_domain:
        ordered = sorted(
            accepted_domain,
            key=lambda frag: (-_safe_float(frag.get("salience_score")), str(frag.get("fragment_id") or "")),
        )
        for frag in ordered:
            slot_name = frag.get("slot") or frag.get("type")
            if not slot_name:
                continue
            add_fragment(frag, str(slot_name), _role_for_slot(str(slot_name)))
            if len(sentences) >= target_count:
                break

    return sentences[:target_count]


def _spine_debug(
    dynamic_insights: Mapping[str, Any] | None,
    spines: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    if not dynamic_insights:
        return []
    selected = dynamic_insights.get("selected")
    if not isinstance(selected, list):
        return []
    selected_by_id = {}
    for entry in selected:
        if not isinstance(entry, Mapping):
            continue
        insight_id = entry.get("insight_id")
        if insight_id:
            selected_by_id[str(insight_id)] = entry
    debug_entries: List[Dict[str, Any]] = []
    for spine in spines:
        spine_id = spine.get("spine_id")
        if not spine_id:
            continue
        entry = selected_by_id.get(str(spine_id)) or {}
        debug_entries.append(
            {
                "spine_id": spine_id,
                "instance_id": entry.get("instance_id"),
                "strength": entry.get("strength"),
                "score_breakdown": (entry.get("debug") or {}).get("score_breakdown"),
            }
        )
    return debug_entries


def _index_phase2_accepted(
    phase2_snapshot: Mapping[str, Any],
) -> tuple[Dict[tuple[str, str], Dict[str, Any]], Dict[str, list[Dict[str, Any]]]]:
    accepted = ((phase2_snapshot.get("slots") or {}).get("accepted") or [])
    by_domain_slot: Dict[tuple[str, str], Dict[str, Any]] = {}
    by_domain: Dict[str, list[Dict[str, Any]]] = {}
    if not isinstance(accepted, list):
        return by_domain_slot, by_domain
    for item in accepted:
        if not isinstance(item, Mapping):
            continue
        frag = item.get("best") if "best" in item else item
        if not isinstance(frag, Mapping):
            continue
        domain = canon_domain(frag.get("domain") or frag.get("category"))
        slot = frag.get("slot") or frag.get("type")
        if not domain or not slot:
            continue
        by_domain.setdefault(domain, []).append(dict(frag))
        key = (domain, str(slot))
        if key not in by_domain_slot:
            by_domain_slot[key] = dict(frag)
        else:
            if _is_better_fragment(dict(frag), by_domain_slot[key]):
                by_domain_slot[key] = dict(frag)
    return by_domain_slot, by_domain


def _is_better_fragment(candidate: Mapping[str, Any], current: Mapping[str, Any]) -> bool:
    return _fragment_sort_key(candidate) > _fragment_sort_key(current)


def _fragment_sort_key(fragment: Mapping[str, Any]) -> tuple[float, float, str]:
    score = _safe_float(fragment.get("salience_score"))
    trigger_rank = _safe_float(fragment.get("trigger_rank"))
    fragment_id = _fragment_id_from_fragment(fragment) or ""
    return (score, trigger_rank, fragment_id)


def _fill_section_slots(
    slots: Mapping[str, Any],
    domain: str,
) -> tuple[Dict[str, Dict[str, Any]], list[str], list[str], Dict[str, str], Dict[str, str]]:
    filled: Dict[str, Dict[str, Any]] = {}
    fallback_used: list[str] = []
    missing: list[str] = []
    reasons: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    used_ids: set[str] = set()
    for slot in ("cause", "mechanism", "effect", "shadow", "potential"):
        fragment = slots.get(slot)
        fragment_id = _fragment_id_from_fragment(fragment)
        if not fragment_id:
            fragment_id = _fallback_fragment_key(fragment, domain=domain, slot=slot)
        if fragment_id and fragment_id not in used_ids:
            filled[slot] = {"fragment_id": fragment_id}
            used_ids.add(fragment_id)
        else:
            missing.append(slot)
            if fragment_id and fragment_id in used_ids:
                reasons[slot] = "duplicate_fragment"
            else:
                reasons[slot] = "missing_primary"
    if missing:
        filled, fallback_used, missing, fallback_reasons, fallback_sources = _fallback_from_supporting(
            slots, filled, missing, used_ids
        )
        for slot, reason in fallback_reasons.items():
            reasons[slot] = reason
        sources.update(fallback_sources)
    return filled, fallback_used, missing, reasons, sources


def _fallback_from_supporting(
    slots: Mapping[str, Any],
    filled: Dict[str, Dict[str, Any]],
    missing: list[str],
    used_ids: set[str],
) -> tuple[Dict[str, Dict[str, Any]], list[str], list[str], Dict[str, str], Dict[str, str]]:
    used_fallback: list[str] = []
    still_missing: list[str] = []
    reasons: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    for slot in missing:
        candidates: list[Mapping[str, Any]] = []
        for fragment in slots.values():
            if not isinstance(fragment, Mapping):
                continue
            for supporting in fragment.get("supporting_facts") or []:
                if not isinstance(supporting, Mapping):
                    continue
                if supporting.get("slot") != slot:
                    continue
                candidates.append(supporting)
        if not candidates:
            still_missing.append(slot)
            reasons[slot] = "no_supporting_candidates"
            continue
        candidates.sort(
            key=lambda entry: _safe_float(entry.get("salience_score")),
            reverse=True,
        )
        picked = next(
            (entry for entry in candidates if _fragment_id_from_fragment(entry) not in used_ids),
            None,
        )
        if not picked:
            still_missing.append(slot)
            reasons[slot] = "supporting_duplicate_only"
            continue
        fragment_id = _fragment_id_from_fragment(picked)
        if fragment_id:
            filled[slot] = {"fragment_id": fragment_id, "fallback_used": True}
            used_fallback.append(slot)
            used_ids.add(fragment_id)
            sources[slot] = fragment_id
        else:
            still_missing.append(slot)
            reasons[slot] = "supporting_missing_fragment_id"
    return filled, used_fallback, still_missing, reasons, sources


def _fragment_id_from_fragment(fragment: Any) -> str | None:
    if not isinstance(fragment, Mapping):
        return None
    return (
        fragment.get("fragment_id")
        or fragment.get("fragment_ref")
        or fragment.get("id")
    )


def _fallback_fragment_key(fragment: Any, *, domain: str, slot: str) -> str | None:
    if not isinstance(fragment, Mapping):
        return None
    text = (
        fragment.get("text")
        or fragment.get("_semantic_text")
        or fragment.get("normalized_text")
        or fragment.get("original_text")
        or ""
    )
    normalized_text = " ".join(str(text).strip().split())
    if not normalized_text:
        return None
    canonical_domain = canon_domain(domain) or domain
    raw = f"{canonical_domain}:{slot}:{normalized_text}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{canonical_domain}:{slot}:{digest}"


def _core_story_plan_id(
    sections: Sequence[Mapping[str, Any]],
    upper: Mapping[str, Any],
    engine_version: str,
    composite_selected: Sequence[Mapping[str, Any]] | None = None,
) -> str:
    payload = {
        "schema_version": "narrative_plan.v1",
        "engine_version": engine_version,
        "sections": sections,
        "upper_meaning": upper,
        "composite_meanings": composite_selected or [],
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
