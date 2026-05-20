"""Bind meta, composites, slots, and upper meaning into a single narrative."""
from __future__ import annotations

import hashlib
import json
import re
import string
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from app.engine.tone_apply import apply_tone
from app.engine.tone_profile import ToneProfile
from app.helpers.domain_normalizer import canon_domain
from app.helpers.normalize import normalize_node_alias, normalize_planet_key
from app.builders.phrase_mapper import Claim, build_claim, default_phrase_map_config
from app.narrative.style_packs.tr_v26 import STYLE_PACK_TR_V26, pick_identity_plan_tokens

# V26 dead branch removed 2026-05-20 per matrix §7.2b + S2.2 trace
# audit. `build_narrative`, the `build_domain_narrative_v26` import,
# and the `StylePackV26TR` import were unused at runtime (no callsites
# repo-wide; verified in `docs/system/audits/v26_trace_audit.md`).
# The LIVE V26 symbols (`build_core_story_plan` here, `render_core_story`
# in `narrative_renderer_v26.py`) remain — they are on the canonical
# natal `/interpret` runtime path and are consumed via
# `PublicNatalView.core_story`, `profile_v8.identity_axis_body`
# fallback, and the `core_story_ui` + `data_quality` builders.


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


def _domain_order(meta: Mapping[str, Any], phase2_slots: Mapping[str, Mapping[str, Any]]) -> list[str]:
    ordered: list[str] = []
    for entry in meta.get("dominant_domains") or []:
        if isinstance(entry, Mapping) and entry.get("domain"):
            ordered.append(str(entry.get("domain")))
    for domain in phase2_slots.keys():
        if domain not in ordered:
            ordered.append(str(domain))
    return ordered


def _domain_slots(phase2_slots: Mapping[str, Mapping[str, Any]], domain: str) -> Mapping[str, Any]:
    if not phase2_slots:
        return {}
    entry = phase2_slots.get(domain)
    if isinstance(entry, Mapping):
        return entry.get("slots") or {}
    return {}


def _build_recognition(pack: Mapping[str, Any], tokens: Mapping[str, Any]) -> str:
    templates = pack.get("recognition_templates") or []
    paragraphs = _render_template_paragraphs(templates, tokens)
    return _join_paragraphs(paragraphs)


def _build_experienced(pack: Mapping[str, Any], tokens: Mapping[str, Any]) -> str:
    templates = pack.get("experienced_templates") or []
    paragraphs = _render_template_paragraphs(templates, tokens)
    return _join_paragraphs(paragraphs)


def _build_potential(pack: Mapping[str, Any], tokens: Mapping[str, Any]) -> str:
    templates = pack.get("potential_templates") or []
    paragraphs = _render_template_paragraphs(templates, tokens)
    return _join_paragraphs(paragraphs)


def _build_shadow(pack: Mapping[str, Any], tokens: Mapping[str, Any]) -> str:
    templates = pack.get("shadow_templates") or []
    paragraphs = _render_template_paragraphs(templates, tokens)
    return _join_paragraphs(paragraphs)


def _build_upper(
    upper_meaning: Mapping[str, Any] | None,
    pack: Mapping[str, Any],
    tokens: Mapping[str, Any],
) -> str:
    if not upper_meaning:
        return ""
    templates = pack.get("upper_meaning_templates") or []
    paragraphs = _render_template_paragraphs(templates, tokens)
    return _join_paragraphs(paragraphs)


def _selected_text(selected: Sequence[Mapping[str, Any]], slot_name: str) -> str:
    for item in selected:
        if item.get("slot") == slot_name:
            return str(item.get("text") or "")
    return ""


def _resolve_tone_profile(
    profile: Mapping[str, Any] | ToneProfile | None,
    meta_summary: Mapping[str, Any],
    meta_info: Mapping[str, Any],
) -> ToneProfile:
    if isinstance(profile, ToneProfile):
        return _apply_meta_tone(profile, meta_summary, meta_info)
    if isinstance(profile, Mapping):
        required = {"directness", "warmth", "intensity", "certainty", "tempo", "distance"}
        if required.issubset(profile.keys()):
            return _apply_meta_tone(
                ToneProfile(
                    directness=float(profile.get("directness") or 0.5),
                    warmth=float(profile.get("warmth") or 0.55),
                    intensity=float(profile.get("intensity") or 0.5),
                    certainty=float(profile.get("certainty") or 0.55),
                    tempo=float(profile.get("tempo") or 0.5),
                    distance=float(profile.get("distance") or 0.5),
                ),
                meta_summary,
                meta_info,
            )
        tone = str(profile.get("tone") or "").lower()
        if tone == "firm":
            base = ToneProfile(0.65, 0.45, 0.7, 0.7, 0.6, 0.55)
        elif tone == "soft":
            base = ToneProfile(0.4, 0.7, 0.4, 0.5, 0.45, 0.55)
        else:
            base = ToneProfile(0.5, 0.55, 0.5, 0.55, 0.5, 0.5)
        return _apply_meta_tone(base, meta_summary, meta_info)
    base = ToneProfile(0.5, 0.55, 0.5, 0.55, 0.5, 0.5)
    return _apply_meta_tone(base, meta_summary, meta_info)


def _apply_tone_safe(text: str, tone: ToneProfile, section: str) -> str:
    if not text:
        return ""
    return apply_tone(text, tone, section=section)


def _domain_title(domain: str) -> str:
    return domain.replace("_", " ").title()


def _domain_title_from_focus(domain: str, focus_composites: Sequence[Mapping[str, Any]]) -> str:
    titles = {
        "identity": "Senin Dünyanın İç Çekirdeği",
        "psychology": "Duyguların Nasıl Çalışıyor?",
        "mind": "Zihnin Nasıl Hareket Ediyor?",
        "relationships": "İlişki Tarafında Sen",
        "career": "Dış Dünyada Yönün",
    }
    return titles.get(domain.lower(), _style_pack(domain).get("title") or _domain_title(domain))


def _style_pack(domain: str) -> Mapping[str, Any]:
    return STYLE_PACK_TR_V26.get(domain) or STYLE_PACK_TR_V26.get("identity") or {}


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


def _render_template_paragraphs(
    templates: Sequence[Sequence[str]],
    tokens: Mapping[str, Any],
) -> list[str]:
    context = _SafeDict(tokens)
    paragraphs: list[str] = []
    for block in templates:
        lines: list[str] = []
        for line in block:
            if not line:
                continue
            rendered = line.format_map(context).strip()
            if rendered:
                lines.append(rendered)
        if lines:
            paragraph = " ".join(lines).strip()
            paragraphs.append(_limit_paragraph_sentences(paragraph))
    return paragraphs


def _join_paragraphs(paragraphs: Sequence[str]) -> str:
    cleaned = [para for para in paragraphs if para]
    if not cleaned:
        return ""
    return "\n\n".join(cleaned)


def _plan_tokens(
    domain: str,
    mapped_items: Sequence[object],
    meta: Mapping[str, Any],
    axis_activation: Mapping[str, Any],
) -> Dict[str, Any]:
    if domain != "identity":
        return {}
    primary_intent, secondary_intent = _top_intents(mapped_items)
    pressure_index = _safe_float(meta.get("pressure_index"))
    support_index = _safe_float(meta.get("support_index"))
    axes = axis_activation.get("active_axes") or []
    axis = axes[0] if axes else None
    return pick_identity_plan_tokens(
        pressure_index=pressure_index,
        support_index=support_index,
        primary_intent=primary_intent,
        secondary_intent=secondary_intent,
        axis=axis,
    )


def normalize_text(text: str) -> str:
    lowered = text.lower()
    trimmed = lowered.strip().strip(string.punctuation)
    return " ".join(trimmed.split())


def _dedup_slots(
    domain: str,
    slots: Mapping[str, Any],
    meta_info: Mapping[str, Any],
    axis_activation: Mapping[str, Any],
) -> tuple[list[Dict[str, Any]], list[Dict[str, Any]]]:
    max_total = 8
    slot_caps = {
        "mechanism": 4,
        "cause": 2,
        "effect": 2,
        "potential": 2,
        "shadow": 1,
    }
    selected: Dict[str, Dict[str, Any]] = {}
    suppressed: list[Dict[str, Any]] = []
    for slot_name, fragment in slots.items():
        if not isinstance(fragment, Mapping):
            continue
        candidates = [_cast_fragment(domain, slot_name, fragment, meta_info, axis_activation)]
        for supporting in fragment.get("supporting_facts") or []:
            if isinstance(supporting, Mapping):
                candidates.append(_cast_fragment(domain, slot_name, supporting, meta_info, axis_activation))
        for candidate in candidates:
            signature = candidate["signature"]
            current = selected.get(signature)
            if not current or candidate.get("salience_score", 0.0) > current.get("salience_score", 0.0):
                if current:
                    suppressed.append({**current, "reason": "dedup"})
                selected[signature] = candidate
            else:
                suppressed.append({**candidate, "reason": "dedup"})
    chosen = list(selected.values())
    chosen, suppressed = _apply_slot_budget(chosen, suppressed, slot_caps, max_total)
    return chosen, suppressed


def _apply_slot_budget(
    selected: Sequence[Mapping[str, Any]],
    suppressed: list[Dict[str, Any]],
    slot_caps: Mapping[str, int],
    max_total: int,
) -> tuple[list[Dict[str, Any]], list[Dict[str, Any]]]:
    grouped: Dict[str, list[Dict[str, Any]]] = {}
    for item in selected:
        slot = str(item.get("slot") or "")
        grouped.setdefault(slot, []).append(dict(item))
    for items in grouped.values():
        items.sort(key=lambda entry: entry.get("salience_score", 0.0), reverse=True)

    mechanism_min = 3
    if len(grouped.get("mechanism", [])) < mechanism_min and grouped.get("cause"):
        promoted = grouped["cause"].pop(0)
        promoted["slot"] = "mechanism"
        promoted["mechanism_promoted"] = True
        promoted["reason"] = "promoted_from_cause"
        grouped.setdefault("mechanism", []).append(promoted)
        if not grouped["cause"]:
            grouped.pop("cause", None)

    final: list[Dict[str, Any]] = []
    mechanism_items = grouped.get("mechanism", [])
    final.extend(mechanism_items[: slot_caps.get("mechanism", 0)])
    for item in mechanism_items[slot_caps.get("mechanism", 0) :]:
        suppressed.append({**item, "reason": "budget"})

    cause_items = grouped.get("cause", [])
    cause_cap = 2 if len(cause_items) >= 2 else 1
    final.extend(cause_items[:cause_cap])
    for item in cause_items[cause_cap:]:
        suppressed.append({**item, "reason": "budget"})

    shadow_items = grouped.get("shadow", [])
    final.extend(shadow_items[: slot_caps.get("shadow", 0)])
    for item in shadow_items[slot_caps.get("shadow", 0) :]:
        suppressed.append({**item, "reason": "budget"})

    effects = grouped.get("effect", [])
    potentials = grouped.get("potential", [])
    if effects or potentials:
        combined_cap = 2
        picked: list[Dict[str, Any]] = []
        if effects:
            picked.append(effects[0])
        if potentials and len(picked) < combined_cap:
            picked.append(potentials[0])
        remaining = effects[1:] + potentials[1:]
        if len(picked) < combined_cap and remaining:
            remaining.sort(key=lambda entry: entry.get("salience_score", 0.0), reverse=True)
            needed = combined_cap - len(picked)
            picked.extend(remaining[:needed])
            remaining = remaining[needed:]
        final.extend(picked[:combined_cap])
        for item in remaining:
            suppressed.append({**item, "reason": "budget"})

    final.sort(key=lambda entry: entry.get("salience_score", 0.0), reverse=True)
    if len(final) > max_total:
        overflow = final[max_total:]
        final = final[:max_total]
        for item in overflow:
            suppressed.append({**item, "reason": "budget_total"})
    return final, suppressed


def _cast_fragment(
    domain: str,
    slot: str,
    fragment: Mapping[str, Any],
    meta_info: Mapping[str, Any],
    axis_activation: Mapping[str, Any],
) -> Dict[str, Any]:
    text = fragment.get("text") or fragment.get("_semantic_text") or ""
    trigger = fragment.get("trigger") or {}
    planet = fragment.get("planet") or trigger.get("planet") or trigger.get("planet1") or ""
    salience_score = _compute_salience(fragment, domain, meta_info, axis_activation)
    signature = _fragment_signature(domain, slot, fragment)
    return {
        "domain": domain,
        "slot": slot,
        "text": _clean_text(text),
        "normalized_text": normalize_text(str(text)),
        "signature": signature,
        "salience_score": salience_score,
        "trigger": trigger,
        "source_rule_ids": fragment.get("source_rule_ids") or [],
        "planet": str(planet).lower().strip() if planet else "",
    }


def _fragment_signature(domain: str, slot: str, fragment: Mapping[str, Any]) -> str:
    trigger = fragment.get("trigger") or {}
    planet = _normalize_planet(fragment.get("planet") or trigger.get("planet") or trigger.get("planet1"))
    sign = str(trigger.get("sign") or "").lower().strip()
    house = trigger.get("house")
    house_value = "" if house is None else str(house).strip()
    rule_group = _rule_group(fragment.get("source_rule_ids"))
    return "|".join([domain, slot, planet, sign, house_value, rule_group])


def _rule_group(value: Any) -> str:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        rule_id = next((str(item) for item in value if item), "")
    else:
        rule_id = str(value or "")
    rule_id = rule_id.strip().lower()
    if not rule_id:
        return ""
    if "_in_" in rule_id:
        prefix = rule_id.split("_in_", 1)[0]
        return f"{prefix}_core"
    return rule_id


def _compute_salience(
    fragment: Mapping[str, Any],
    domain: str,
    meta_info: Mapping[str, Any],
    axis_activation: Mapping[str, Any],
) -> float:
    orb_strength = _orb_strength(fragment, meta_info)
    dominance = _dominance_score(fragment, meta_info)
    axis_weight = _axis_weight(fragment, meta_info, axis_activation)
    house_weight = _house_weight(fragment, meta_info)
    pattern_bonus = _pattern_bonus(fragment, axis_activation)
    domain_priority = _domain_priority(domain)

    return (
        0.25 * orb_strength
        + 0.20 * dominance
        + 0.20 * axis_weight
        + 0.10 * house_weight
        + 0.15 * pattern_bonus
        + 0.10 * domain_priority
    )


def _orb_strength(fragment: Mapping[str, Any], meta_info: Mapping[str, Any]) -> float:
    trigger = fragment.get("trigger") or {}
    trigger_type = str(trigger.get("type") or "").lower()
    if trigger_type == "aspect":
        orb = trigger.get("orb") if trigger.get("orb") is not None else fragment.get("orb")
        if orb is None:
            orb = _find_orb(fragment, meta_info)
        try:
            orb_value = float(orb)
        except (TypeError, ValueError):
            return 0.4
        return 1.0 - min(orb_value, 8.0) / 8.0
    return 0.4


def _find_orb(fragment: Mapping[str, Any], meta_info: Mapping[str, Any]) -> float | None:
    trigger = fragment.get("trigger") or {}
    planet1 = _normalize_planet(trigger.get("planet1") or trigger.get("planet"))
    planet2 = _normalize_planet(trigger.get("planet2"))
    aspect_type = str(trigger.get("aspect") or trigger.get("type") or "").lower()
    if not (planet1 and planet2 and aspect_type):
        return None
    aspects = meta_info.get("aspects_list") or []
    for aspect in aspects:
        p1 = _normalize_planet(aspect.get("planet1") or aspect.get("planet"))
        p2 = _normalize_planet(aspect.get("planet2") or aspect.get("target"))
        atype = str(aspect.get("type") or aspect.get("aspect") or "").lower()
        if {p1, p2} == {planet1, planet2} and atype == aspect_type:
            orb = aspect.get("orb")
            try:
                return float(orb)
            except (TypeError, ValueError):
                return None
    return None


def _dominance_score(fragment: Mapping[str, Any], meta_info: Mapping[str, Any]) -> float:
    planet = _normalize_planet(
        fragment.get("planet")
        or (fragment.get("trigger") or {}).get("planet")
        or (fragment.get("trigger") or {}).get("planet1")
    )
    if not planet:
        return 0.0
    dominant = meta_info.get("dominant_planets") or []
    for entry in dominant:
        if not isinstance(entry, Mapping):
            continue
        if _normalize_planet(entry.get("planet")) == planet:
            return _clamp(_safe_float(entry.get("score")) or 0.0)

    score = 0.0
    planet_houses = meta_info.get("planet_houses") or {}
    house = planet_houses.get(planet)
    if house in {1, 8, 10}:
        score += 0.1
    chart_ruler = _normalize_planet(meta_info.get("chart_ruler"))
    if planet in {"sun", "moon"} or (chart_ruler and planet == chart_ruler):
        score += 0.15
    return _clamp(score)


def _axis_weight(
    fragment: Mapping[str, Any],
    meta_info: Mapping[str, Any],
    axis_activation: Mapping[str, Any],
) -> float:
    active_axes = [str(axis) for axis in axis_activation.get("active_axes") or []]
    if not active_axes:
        return 0.0
    dominant_axis = active_axes[0]
    house = _resolve_house(fragment, meta_info)
    axis = _axis_for_house(house)
    if not axis:
        return 0.0
    if axis == dominant_axis:
        return 0.25
    if axis in active_axes:
        return 0.15
    return 0.0


def _house_weight(fragment: Mapping[str, Any], meta_info: Mapping[str, Any]) -> float:
    house = _resolve_house(fragment, meta_info)
    if house in {1, 4, 7, 10}:
        return 0.2
    if house in {2, 5, 8, 11}:
        return 0.1
    if house in {3, 6, 9, 12}:
        return 0.05
    return 0.0


def _pattern_bonus(fragment: Mapping[str, Any], axis_activation: Mapping[str, Any]) -> float:
    trigger = fragment.get("trigger") or {}
    aspect_type = str(trigger.get("aspect") or trigger.get("type") or "").lower()
    bonus = 0.0
    if aspect_type in {"square", "opposition"}:
        bonus += 0.15
    elif aspect_type in {"trine", "sextile"}:
        bonus += 0.05
    if str(axis_activation.get("axis_tension") or "").lower() == "high":
        bonus += 0.15
    return bonus


def _domain_priority(domain: str) -> float:
    normalized = domain.lower()
    if normalized == "identity":
        return 1.0
    if normalized in {"psychology", "mind", "relationships"}:
        return 0.9
    if normalized == "career":
        return 0.7
    return 0.6


def _resolve_house(fragment: Mapping[str, Any], meta_info: Mapping[str, Any]) -> int | None:
    trigger = fragment.get("trigger") or {}
    house = trigger.get("house")
    if house is None:
        planet = _normalize_planet(fragment.get("planet") or trigger.get("planet") or trigger.get("planet1"))
        house = (meta_info.get("planet_houses") or {}).get(planet)
    try:
        return int(house)
    except (TypeError, ValueError):
        return None


def _axis_for_house(house: int | None) -> str | None:
    if house in {1, 7}:
        return "1-7"
    if house in {4, 10}:
        return "4-10"
    if house in {2, 8}:
        return "2-8"
    if house in {3, 9}:
        return "3-9"
    return None


def _normalize_planet(value: Any) -> str:
    return normalize_node_alias(normalize_planet_key(value))


def _slot_ratios(selected: Sequence[Mapping[str, Any]]) -> Dict[str, float]:
    totals: Dict[str, int] = {slot: 0 for slot in ("cause", "mechanism", "effect", "shadow", "potential")}
    for item in selected:
        slot = str(item.get("slot") or "")
        if slot in totals:
            totals[slot] += 1
    total_count = sum(totals.values()) or 1
    return {slot: round(value / total_count, 3) for slot, value in totals.items()}


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _apply_meta_tone(
    tone: ToneProfile,
    meta_summary: Mapping[str, Any],
    meta_info: Mapping[str, Any],
) -> ToneProfile:
    directness = tone.directness
    warmth = tone.warmth
    intensity = tone.intensity
    certainty = tone.certainty
    tempo = tone.tempo
    distance = tone.distance

    pressure = _safe_float(meta_summary.get("pressure_index"))
    support = _safe_float(meta_summary.get("support_index"))
    if pressure >= 0.75 and support <= 0.4:
        warmth = _clamp(warmth + 0.1)
        intensity = _clamp(intensity - 0.1)

    dominant_planets = meta_info.get("dominant_planets") or []
    dominant_list = {str(entry.get("planet")).lower() for entry in dominant_planets if isinstance(entry, Mapping)}
    chart_ruler = str(meta_info.get("chart_ruler") or "").lower()
    if "saturn" in dominant_list or chart_ruler == "saturn":
        directness = _clamp(directness + 0.15)
        warmth = _clamp(warmth - 0.1)
    if dominant_list:
        directness = _clamp(directness + 0.05)

    dominant_elements = meta_info.get("dominant_elements") or {}
    if "Air" in dominant_elements or "air" in dominant_elements or "mercury" in dominant_list:
        tempo = _clamp(tempo + 0.15)

    return ToneProfile(
        directness=directness,
        warmth=warmth,
        intensity=intensity,
        certainty=certainty,
        tempo=tempo,
        distance=distance,
    )


def _limit_paragraph_sentences(text: str) -> str:
    sentences = [part.strip() for part in text.split(".") if part.strip()]
    if not sentences:
        return ""
    clipped = sentences[:3]
    return ". ".join(clipped) + "."


def _rewrite_repeated_verbs(text: str) -> str:
    replacements = {
        "calisir": "ilerler",
        "belirir": "gorusur",
        "olur": "seklinir",
        "cikar": "netlesir",
    }
    tokens = text.split()
    seen: set[str] = set()
    for idx, token in enumerate(tokens):
        key = token.strip(",.").lower()
        if key in replacements and key in seen:
            suffix = ""
            if token.endswith("."):
                suffix = "."
            elif token.endswith(","):
                suffix = ","
            tokens[idx] = replacements[key] + suffix
        seen.add(key)
    return " ".join(tokens)


def _normalize_paragraphs(text: str) -> str:
    if not text:
        return text
    paragraphs = [para.strip() for para in text.split("\n\n") if para.strip()]
    normalized = [_normalize_paragraph(para) for para in paragraphs]
    return "\n\n".join(normalized)


def _normalize_paragraph(text: str) -> str:
    cleaned = text
    cleaned = cleaned.replace("Cunku ", "Çünkü ").replace("cunku ", "çünkü ")
    cleaned = cleaned.replace(", ,", ", ")
    cleaned = cleaned.replace(". ,", ". ")
    cleaned = cleaned.replace("Golge", "Gölge")
    cleaned = cleaned.replace("gorunebilir", "görünebilir")
    cleaned = cleaned.replace("degil", "değil")
    cleaned = re.sub(r"\bGenelde,\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"Şunu fark etmek iyi gelebilir:", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"Nazik bir girişle,", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"Nazik bir not olarak,", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bÇünkü\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bBunun sonucu\b,?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bBu harita\b,?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bBu sistemde\b,?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bOdak mekanizma:\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bKisa destek olarak\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bIkinci eksen olarak\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"hissi ortaya cikar", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"kapasitesi acik kalir", "", cleaned, flags=re.IGNORECASE)
    for token in ("calisir", "netlesir", "eslik eder", "belirginlesir", "desteklenir", "yone acilir"):
        cleaned = re.sub(rf"\b{token}\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = " ".join(cleaned.split())
    return cleaned


def _limit_word_count(text: str, limit: int) -> str:
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]).rstrip(".") + "."


def _micro_insight_text(selected: Sequence[Mapping[str, Any]]) -> str:
    for item in selected:
        if item.get("slot") == "micro_insight" or item.get("micro_insight"):
            return _clean_text(item.get("text"))
    return ""


def _mechanism_to_lived(text: str) -> str:
    lowered = text.lower()
    if _contains_any(lowered, ("kontrol", "disiplin", "guven", "istikrar")):
        return "hayata daha ciddi ve kontrollü basliyorsun. Once saglamlastirmak istiyorsun."
    if _contains_any(lowered, ("gorun", "kabul", "guc", "gorunurluk")):
        return "gorulmek senin icin onemli. Iceride bunu cok hissediyorsun ama disariya her zaman gostermiyorsun."
    if _contains_any(lowered, ("duygu", "sindir", "yavas", "derin")):
        return "duygularin hizli akmiyor; derinde calisiyor. Kirildiginda hemen belli etmeyebilirsin."
    if _contains_any(lowered, ("iliski", "bag", "sadelik", "saglam temel")):
        return "kolay bag kurmuyorsun. Bag kurdugunda derinlesiyorsun."
    cleaned = _mechanism_phrase(text)
    return f"temel ihtiyac: {cleaned}."


def _mechanism_phrase(text: str) -> str:
    lowered = text.lower()
    if _contains_any(lowered, ("kontrol", "disiplin", "istikrar")):
        return "kontrol isteyen"
    if _contains_any(lowered, ("gorun", "kabul", "guc", "gorunurluk")):
        return "gorunmek isteyen"
    if _contains_any(lowered, ("duygu", "sindir", "yavas", "derin")):
        return "duygulari derinden tasiyan"
    if _contains_any(lowered, ("iliski", "bag", "sadelik", "saglam temel")):
        return "bag kurarken temkinli"
    return _clean_text(text)


def _contains_any(text: str, keywords: Sequence[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _top_intent_pairs(mapped: Sequence[object]) -> tuple[str, str] | None:
    scored: dict[str, float] = {}
    for item in mapped:
        voice = getattr(item, "voice", None)
        if voice != "inner_state":
            continue
        intent = str(getattr(item, "intent", "") or "")
        if not intent or intent == "unknown":
            continue
        score = float(getattr(item, "salience", 0.0) or 0.0)
        scored[intent] = max(scored.get(intent, 0.0), score)
    if len(scored) < 2:
        return None
    ranked = sorted(scored.items(), key=lambda item: item[1], reverse=True)
    return _intent_phrase(ranked[0][0]), _intent_phrase(ranked[1][0])


def _intent_phrase(intent: str) -> str:
    mapping = {
        "visibility": "gorunmek ister",
        "control": "kontrolu tutmak ister",
        "security": "guvende kalmak ister",
        "depth": "derinlesmek ister",
    }
    return mapping.get(intent, "daha net kalmak ister")


def _inner_question(mapped: Sequence[object]) -> str:
    intents = {str(getattr(item, "intent", "") or "") for item in mapped}
    if "visibility" in intents or "depth" in intents:
        return "gorunur olsam bile kendimi kaybeder miyim"
    if "control" in intents:
        return "kontrolu ne zaman gevsetmeliyim"
    return ""


def _potential_growth_sentence(text: str) -> str:
    lowered = text.lower()
    if "guven" in lowered:
        return "Guveni disaridan almak zorunda degilsin; iceride kurdukca merkezleniyorsun."
    if "gorun" in lowered or "gorunurluk" in lowered:
        return "Gorunur olmakla “kontrolu kaybetmek” ayni sey degil."
    return ""


def _shadow_risk_sentence(text: str) -> str:
    lowered = text.lower()
    if "sahiplen" in lowered:
        return "kendi icinde celiski yaratabilir"
    if "kiskan" in lowered:
        return "iliskilerde gereksiz gerilime donebilir"
    return ""


def _mechanism_inner_voice(text: str) -> list[str]:
    lowered = text.lower()
    lines: list[str] = []
    if _contains_any(lowered, ("guven", "istikrar")):
        lines.append("Bos konusmayi sevmezsin; once saglamlastirmak istersin.")
    if _contains_any(lowered, ("kontrol", "disiplin")):
        lines.append("Hazir olayim, saglam olayim diye kendini siki tutan bir yanin var.")
    if _contains_any(lowered, ("gorunur", "one atil", "gorunurluk")):
        lines.append("Bir yanin gorulmek ister; bir yanin “dagilmayayim” diye frene basar.")
    if _contains_any(lowered, ("tempo", "yavas", "emin")):
        lines.append("Senin ilerleyisin hizli degil; ama kalici.")
    if not lines:
        cleaned = _mechanism_phrase(text)
        lines.append(f"Temel ihtiyac: {cleaned}.")
    return lines


def _mechanism_conflict_line(first: str, second: str) -> str:
    if not first:
        return ""
    if second:
        return f"Bir yanin {first}; ote yandan {second}."
    return f"Bir yanin {first}; ote yandan kendini daha icte tutmak istiyorsun."


def _dedupe_lines(lines: Sequence[str], *, limit: int) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for line in lines:
        normalized = line.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        output.append(normalized)
        if len(output) >= limit:
            break
    return output


def _collect_slot_texts(selected: Sequence[Mapping[str, Any]], slot: str) -> list[str]:
    texts: list[str] = []
    for item in selected:
        if item.get("slot") == slot:
            text = _clean_text(item.get("text"))
            if text:
                texts.append(text)
    return texts


def _core_style_from_text(text: str) -> tuple[str, bool, bool]:
    lowered = text.lower()
    has_control = _contains_any(lowered, ("guven", "istikrar", "disiplin", "kontrol"))
    has_visibility = _contains_any(
        lowered, ("gorunur", "one atil", "guc", "guc", "hissettirme")
    )
    if has_control:
        return "ciddiyetle ve kontrollu", has_control, has_visibility
    if has_visibility:
        return "guclu durmaya calisan", has_control, has_visibility
    return "saglam bir yerden", has_control, has_visibility


def _outer_perception(selected: Sequence[Mapping[str, Any]]) -> str:
    candidates = _collect_slot_texts(selected, "effect") + _collect_slot_texts(selected, "potential")
    for sentence in candidates:
        lowered = sentence.lower()
        if "algilanirsin" in lowered or "algılanırsın" in lowered:
            return sentence
        if "gorunursun" in lowered or "görünürsün" in lowered:
            return sentence
        if "insanlar" in lowered:
            return sentence
    return "Insanlar seni cogu zaman sakin, kararli ve dayanikli biri gibi gorur."


def _inner_counterforce(has_control: bool, has_visibility: bool) -> str:
    if has_control and has_visibility:
        return "Icinde hem kontrolu tutmak isteyen hem de daha sahici, daha canli bir taraf var."
    return "Icinde bunu yumusatmak isteyen bir taraf da var."


def _apply_genelde_rule(
    sections: Sequence[Mapping[str, Any]],
    tone: ToneProfile,
    domain: str,
    used_domains: set[str],
) -> list[Dict[str, Any]]:
    if tone.certainty >= 0.55:
        return [dict(section) for section in sections]
    output: list[Dict[str, Any]] = []
    used = domain in used_domains
    for section in sections:
        text = str(section.get("text") or "")
        if not text:
            output.append(dict(section))
            continue
        cleaned = text
        if section.get("type") == "recognition" and not used and not cleaned.lower().startswith("genelde,"):
            cleaned = f"Genelde, {cleaned}"
            used = True
        elif section.get("type") != "recognition" and cleaned.lower().startswith("genelde,"):
            cleaned = cleaned[len("genelde,") :].lstrip()
        output.append({**section, "text": cleaned})
    if used:
        used_domains.add(domain)
    return output


def _apply_softener_rule(
    sections: Sequence[Mapping[str, Any]],
    tone: ToneProfile,
    domain: str,
    used_domains: set[str],
) -> list[Dict[str, Any]]:
    if tone.warmth < 0.65:
        return [dict(section) for section in sections]
    output: list[Dict[str, Any]] = []
    used = domain in used_domains
    for section in sections:
        text = str(section.get("text") or "")
        if not text:
            output.append(dict(section))
            continue
        if section.get("type") == "experienced" and not used:
            paragraphs = text.split("\n\n")
            if paragraphs:
                if not paragraphs[0].lower().startswith("sunu fark etmek iyi gelebilir:"):
                    paragraphs[0] = f"Sunu fark etmek iyi gelebilir: {paragraphs[0]}"
                used = True
            text = "\n\n".join(paragraphs)
        output.append({**section, "text": text})
    if used:
        used_domains.add(domain)
    return output


def _normalize_sections(sections: Sequence[Mapping[str, Any]]) -> list[Dict[str, Any]]:
    normalized: list[Dict[str, Any]] = []
    for section in sections:
        text = str(section.get("text") or "")
        normalized.append({**section, "text": _normalize_paragraphs(text)})
    return normalized


def _drop_forbidden_sections(
    sections: Sequence[Mapping[str, Any]]
) -> tuple[list[Dict[str, Any]], list[Dict[str, Any]]]:
    dropped: list[Dict[str, Any]] = []
    cleaned_sections: list[Dict[str, Any]] = []
    for section in sections:
        text = str(section.get("text") or "")
        if not text:
            cleaned_sections.append(dict(section))
            continue
        cleaned_text, dropped_sentences = _drop_forbidden_sentences(text)
        if dropped_sentences:
            dropped.append({"type": section.get("type"), "sentences": dropped_sentences})
        cleaned_sections.append({**section, "text": cleaned_text})
    return cleaned_sections, dropped


def _drop_forbidden_sentences(text: str) -> tuple[str, list[str]]:
    paragraphs = [para.strip() for para in text.split("\n\n") if para.strip()]
    dropped: list[str] = []
    kept_paragraphs: list[str] = []
    for paragraph in paragraphs:
        sentences = [sent.strip() for sent in paragraph.split(".") if sent.strip()]
        kept_sentences = []
        for sentence in sentences:
            if _contains_forbidden(sentence):
                dropped.append(sentence)
                continue
            kept_sentences.append(sentence)
        if kept_sentences:
            kept_paragraphs.append(". ".join(kept_sentences) + ".")
    return "\n\n".join(kept_paragraphs), dropped


def _contains_forbidden(text: str) -> bool:
    lowered = text.lower()
    phrases = [
        "bu alanda temel ihtiyac",
        "da devreye giriyor",
        "baskisini hissettirebilir",
        "yuklenme alanidir",
        "hem de icte bir denge var",
    ]
    for phrase in phrases:
        if phrase in lowered:
            return True
    words = _tokenize_words(lowered)
    if "acik" in words:
        return True
    return False


def _tokenize_words(text: str) -> list[str]:
    return re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", text)


def _top_intents(mapped_items: Sequence[object]) -> tuple[str, str]:
    scored: dict[str, float] = {}
    for item in mapped_items:
        intent = str(getattr(item, "intent", "") or "")
        if not intent or intent == "generic":
            continue
        salience = float(getattr(item, "salience", 0.0) or 0.0)
        scored[intent] = max(scored.get(intent, 0.0), salience)
    ranked = sorted(scored.items(), key=lambda entry: entry[1], reverse=True)
    if not ranked:
        return "generic", "generic"
    if len(ranked) == 1:
        return ranked[0][0], "generic"
    return ranked[0][0], ranked[1][0]


def _identity_sections_from_payload(
    payload: Mapping[str, Any],
    tone: ToneProfile,
) -> list[Dict[str, Any]]:
    sections_payload = payload.get("sections") or {}
    order = ["Recognition", "Experienced", "Potential", "Shadow", "Upper Meaning"]
    sections: list[Dict[str, Any]] = []
    for key in order:
        paragraphs = sections_payload.get(key) or []
        if not paragraphs:
            continue
        text = "\n\n".join([p for p in paragraphs if p]).strip()
        if not text:
            continue
        section_type = key.lower().replace(" ", "_")
        toned = _apply_tone_safe(text, tone, section_type)
        sections.append({"type": section_type, "text": toned})
    return sections


# -----------------------------
# v2.6 claim-based rendering helpers
# -----------------------------


def _build_style_context(
    meta_summary: Mapping[str, Any],
    axis_activation: Mapping[str, Any],
    domain: str,
) -> Dict[str, Any]:
    pressure = _safe_float(meta_summary.get("pressure_index"))
    support = _safe_float(meta_summary.get("support_index"))
    axis = meta_summary.get("dominant_axis")
    if not axis and axis_activation:
        axis = axis_activation.get("dominant_axis") or axis_activation.get("axis")
    if pressure >= 0.75:
        tone_word = "guclu"
    elif pressure >= 0.55:
        tone_word = "kontrollu"
    else:
        tone_word = "temkinli"
    return {
        "domain": domain,
        "pressure_index": pressure,
        "support_index": support,
        "axis": axis,
        "tone_word": tone_word,
        "used_connectors": set(),
        "meta_summary_text": meta_summary.get("meta_summary_text") or "",
    }


def _select_focus_claims(claims: Sequence[Claim], *, limit: int = 2) -> list[Claim]:
    if not claims:
        return []
    ranked = sorted(claims, key=lambda claim: claim.salience, reverse=True)
    return ranked[:limit]


def _section_from_paragraphs(
    section_type: str,
    paragraphs: Sequence[str],
    tone: ToneProfile,
) -> Dict[str, Any]:
    text = "\n\n".join([para for para in paragraphs if para]).strip()
    if not text:
        return {"type": section_type, "text": ""}
    return {"type": section_type, "text": _apply_tone_safe(text, tone, section_type)}


def _apply_section_tone(section: Mapping[str, Any], tone: ToneProfile) -> Dict[str, Any]:
    text = str(section.get("text") or "")
    if not text:
        return {"type": section.get("type"), "text": ""}
    section_type = str(section.get("type") or "")
    return {"type": section_type, "text": _apply_tone_safe(text, tone, section_type)}


# -----------------------------
# helpers: short-safe sentences
# -----------------------------


def _norm_space(s: str) -> str:
    s = (s or "").replace("  ", " ").strip()
    s = s.replace(" ,", ",").replace(" .", ".").replace("..", ".")
    return s


def _cap_sentences(text: str, max_sentences: int = 3) -> str:
    t = _norm_space(text)
    if not t:
        return t
    parts = [p.strip() for p in t.split(".") if p.strip()]
    if len(parts) <= max_sentences:
        return t if t.endswith(".") else t + "."
    cut = ". ".join(parts[:max_sentences]).strip()
    return cut + "."


def _join_sentences(lines: List[str]) -> str:
    lines = [_norm_space(x) for x in lines if _norm_space(x)]
    if not lines:
        return ""
    out = " ".join(lines)
    out = _norm_space(out)
    if out and out[-1] not in ".!?":
        out += "."
    return out


def _pick_top_intents(mapped_items: List[Dict[str, Any]]) -> Tuple[str, str]:
    if not mapped_items:
        return ("control", "authenticity")

    items = sorted(mapped_items, key=lambda x: float(x.get("salience", 0.0)), reverse=True)

    intents: List[str] = []
    for it in items:
        intent = (it.get("intent") or "").strip()
        if not intent:
            continue
        if intent not in intents:
            intents.append(intent)
        if len(intents) >= 2:
            break

    if len(intents) == 0:
        return ("control", "authenticity")
    if len(intents) == 1:
        if intents[0] in ("control", "security"):
            return (intents[0], "authenticity")
        return (intents[0], "control")
    return (intents[0], intents[1])


# -----------------------------
# v2.6 identity renderer
# -----------------------------


def render_identity_v26(
    *,
    meta_summary: Dict[str, Any],
    axis_activation: Optional[Dict[str, Any]] = None,
    mapped_items: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    pack = STYLE_PACK_TR_V26["identity"]

    pressure = float((meta_summary or {}).get("pressure_index") or 0.5)
    support = float((meta_summary or {}).get("support_index") or 0.5)

    axis = None
    axis = (meta_summary or {}).get("dominant_axis") or None
    if not axis and axis_activation:
        axis = axis_activation.get("dominant_axis") or axis_activation.get("axis") or None

    primary_intent, secondary_intent = _pick_top_intents(mapped_items or [])

    tokens = pick_identity_plan_tokens(
        pressure_index=pressure,
        support_index=support,
        primary_intent=primary_intent,
        secondary_intent=secondary_intent,
        axis=axis,
    )

    rec_templates = pack["recognition_templates"]
    rec_para_1 = _join_sentences([t.format(**tokens) for t in rec_templates[0]])
    rec_para_2 = _join_sentences([t.format(**tokens) for t in rec_templates[1]])

    rec_para_1 = _cap_sentences(rec_para_1, 3)
    rec_para_2 = _cap_sentences(rec_para_2, 3)

    exp_templates = pack["experienced_templates"]
    exp_paras: List[str] = []
    for block in exp_templates:
        p = _join_sentences([t.format(**tokens) for t in block])
        p = _cap_sentences(p, 3)
        if p:
            exp_paras.append(p)
    exp_paras = exp_paras[:3]

    pot_templates = pack["potential_templates"]
    pot_para = _join_sentences([t.format(**tokens) for t in pot_templates[0]])
    pot_para = _cap_sentences(pot_para, 3)

    shadow_para = ""
    if pressure >= 0.35:
        sh_templates = pack["shadow_templates"]
        shadow_para = _join_sentences([t.format(**tokens) for t in sh_templates[0]])
        shadow_para = _cap_sentences(shadow_para, 2)

    um_templates = pack["upper_meaning_templates"]
    upper_para = _join_sentences([t.format(**tokens) for t in um_templates[0]])
    upper_para = _cap_sentences(upper_para, 3)

    sections: Dict[str, List[str]] = {
        "Recognition": [rec_para_1, rec_para_2],
        "Experienced": exp_paras,
        "Potential": [pot_para],
    }
    if shadow_para:
        sections["Shadow"] = [shadow_para]
    else:
        sections["Shadow"] = []

    sections["Upper Meaning"] = []

    blocks: List[str] = []
    blocks.extend([p for p in sections["Recognition"] if p])
    blocks.extend([p for p in sections["Experienced"] if p])
    blocks.extend([p for p in sections["Potential"] if p])
    blocks.extend([p for p in sections.get("Shadow", []) if p])

    full_text = "\n\n".join([b for b in blocks if b]).strip()

    return {
        "title": pack["title"],
        "sections": sections,
        "text": full_text,
        "debug": {
            "primary_intent": primary_intent,
            "secondary_intent": secondary_intent,
            "axis_used": axis,
            "pressure_index": pressure,
            "support_index": support,
        },
        "_upper_meaning_preview": upper_para,
    }
