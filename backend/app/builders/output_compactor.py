"""Compact user-facing output transformation."""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from app.engine.tone_profile import load_tone_config
from app.helpers.normalize import normalize_planet_key, normalize_sign_key
from app.narrative.editorial_render_policy import render_fragment_line, select_rhythm_family


DOMAIN_ORDER_LIMIT = 3
HIGHLIGHT_TEXT_LIMIT = 420
SUMMARY_LIMIT = 600
EVIDENCE_LIMIT = 2
MICRO_INSIGHT_LIMIT = 2


def build_user_compact(
    fragments_by_domain: Mapping[str, Mapping[str, Any]],
    *,
    phase2_snapshot: Mapping[str, Any] | None = None,
    tone_profile: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    seed = _compact_seed(fragments_by_domain, phase2_snapshot or {})
    domains = _build_domains(fragments_by_domain, phase2_snapshot or {}, seed=seed)
    micro_insights = _build_micro_insights(fragments_by_domain, domains, seed=seed)
    payload: Dict[str, Any] = {
        "profile": "user_compact",
        "domains": domains,
        "micro_insights": micro_insights,
        "meta": {"max_domains": DOMAIN_ORDER_LIMIT, "policy_version": "tasnif_v3"},
    }
    if tone_profile:
        payload["tone_profile"] = tone_profile
    return payload


def _build_domains(
    fragments_by_domain: Mapping[str, Mapping[str, Any]],
    phase2_snapshot: Mapping[str, Any],
    *,
    seed: str,
) -> List[Dict[str, Any]]:
    domain_scores = _domain_scores(fragments_by_domain, phase2_snapshot)
    ordered_domains = [domain for domain, _ in domain_scores][:DOMAIN_ORDER_LIMIT]
    domains: List[Dict[str, Any]] = []
    used_families: list[str] = []
    for domain in ordered_domains:
        entry = fragments_by_domain.get(domain)
        if not isinstance(entry, Mapping):
            continue
        slots = entry.get("slots") or {}
        if not isinstance(slots, Mapping):
            continue
        family = select_rhythm_family(seed, "user_compact", domain, used_families)
        highlights = _build_highlights(domain, slots, family=family)
        summary = _build_summary(highlights)
        signals = _build_signals(slots)
        domains.append(
            {
                "domain": domain,
                "title": _title_for_domain(domain),
                "summary": summary,
                "highlights": highlights,
                "signals": signals,
            }
        )
        used_families.append(family)
    return domains


def _domain_scores(
    fragments_by_domain: Mapping[str, Mapping[str, Any]],
    phase2_snapshot: Mapping[str, Any],
) -> List[Tuple[str, float]]:
    felt_map = _felt_intensity_map_from_snapshot(phase2_snapshot)
    if felt_map:
        ordered = sorted(felt_map.items(), key=lambda item: item[1], reverse=True)
        return ordered
    scores: List[Tuple[str, float]] = []
    for domain, entry in fragments_by_domain.items():
        if not isinstance(entry, Mapping):
            continue
        slots = entry.get("slots") or {}
        if not isinstance(slots, Mapping):
            continue
        total = 0.0
        for fragment in slots.values():
            if not isinstance(fragment, Mapping):
                continue
            total += _salience_score(fragment)
        scores.append((domain, total))
    scores.sort(key=lambda item: item[1], reverse=True)
    return scores


def _felt_intensity_map_from_snapshot(phase2_snapshot: Mapping[str, Any]) -> Dict[str, float]:
    slots = phase2_snapshot.get("slots") or {}
    accepted = slots.get("accepted") if isinstance(slots, Mapping) else None
    if not isinstance(accepted, list):
        return {}
    felt_totals: Counter[str] = Counter()
    for entry in accepted:
        if not isinstance(entry, Mapping):
            continue
        felt_map = entry.get("felt_intensity_map")
        if not isinstance(felt_map, Mapping):
            continue
        for domain, value in felt_map.items():
            try:
                felt_totals[str(domain)] += float(value)
            except (TypeError, ValueError):
                continue
    if not felt_totals:
        return {}
    return {domain: float(score) for domain, score in felt_totals.items()}


def _build_highlights(domain: str, slots: Mapping[str, Any], *, family: str) -> List[Dict[str, Any]]:
    highlights: List[Dict[str, Any]] = []
    used_signatures: set[Tuple[str, str, str, str, str, str]] = set()

    recognition = _pick_fragment(domain, slots, ["cause"], used_signatures)
    experienced = _pick_fragment(domain, slots, ["mechanism", "effect", "cause"], used_signatures)
    potential = _pick_fragment(domain, slots, ["potential", "effect"], used_signatures)
    shadow = _pick_fragment(domain, slots, ["shadow"], used_signatures)

    if recognition:
        highlights.append(
            _format_highlight("Recognition", recognition, domain=domain, family=family, safe=False)
        )
    if experienced:
        highlights.append(
            _format_highlight("Experienced Reality", experienced, domain=domain, family=family, safe=False)
        )
    if potential:
        highlights.append(
            _format_highlight("Potential", potential, domain=domain, family=family, safe=False)
        )
    if shadow:
        highlights.append(
            _format_highlight("Shadow", shadow, domain=domain, family=family, safe=True)
        )

    return highlights


def _pick_fragment(
    domain: str,
    slots: Mapping[str, Any],
    slot_order: Sequence[str],
    used_signatures: set[Tuple[str, str, str, str, str, str]],
) -> Mapping[str, Any] | None:
    candidates: List[Tuple[float, Mapping[str, Any], Tuple[str, str, str, str, str, str]]] = []
    for slot in slot_order:
        fragment = slots.get(slot)
        if not isinstance(fragment, Mapping):
            continue
        signature = _signature(domain, slot, fragment)
        if signature in used_signatures:
            continue
        score = _salience_score(fragment)
        candidates.append((score, fragment, signature))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (-item[0], _fragment_text(item[1])))
    _, fragment, signature = candidates[0]
    used_signatures.add(signature)
    return fragment


def _format_highlight(label: str, fragment: Mapping[str, Any], *, domain: str, family: str, safe: bool) -> Dict[str, Any]:
    role_map = {
        "Recognition": "recognition",
        "Experienced Reality": "experienced",
        "Potential": "potential",
        "Shadow": "shadow",
    }
    evidence_text = _primary_evidence_text(fragment)
    text = render_fragment_line(
        _fragment_text(fragment),
        family=family,
        role=role_map.get(label, "experienced"),
        evidence_text=evidence_text,
        mode="background" if safe else "core",
    )
    text = _truncate_text(text, HIGHLIGHT_TEXT_LIMIT)
    evidence = _build_evidence(fragment)
    highlight: Dict[str, Any] = {
        "label": label,
        "text": text,
        "evidence": evidence,
    }
    if safe:
        highlight["safety"] = True
    return highlight


def _build_summary(highlights: Sequence[Mapping[str, Any]]) -> str:
    parts: List[str] = []
    for item in highlights:
        text = item.get("text")
        if isinstance(text, str) and text.strip():
            parts.append(_ensure_sentence(text.strip()))
        if len(parts) >= 3:
            break
    summary = " ".join(parts)
    return _truncate_text(summary, SUMMARY_LIMIT)


def _build_signals(slots: Mapping[str, Any]) -> Dict[str, Any]:
    count = 0
    axes: Counter[str] = Counter()
    themes: Counter[str] = Counter()
    for fragment in slots.values():
        if not isinstance(fragment, Mapping):
            continue
        count += 1
        trigger = fragment.get("trigger") or {}
        axis = trigger.get("axis")
        if axis:
            axes[str(axis)] += 1
        theme = fragment.get("theme") or fragment.get("theme_id")
        if theme:
            themes[str(theme)] += 1
        supporting = fragment.get("supporting_facts") or []
        if isinstance(supporting, Iterable):
            for item in supporting:
                if not isinstance(item, Mapping):
                    continue
                count += 1
    return {
        "count": count,
        "top_axes": [item[0] for item in axes.most_common(2)],
        "top_themes": [item[0] for item in themes.most_common(2)],
    }


def _build_micro_insights(
    fragments_by_domain: Mapping[str, Mapping[str, Any]],
    domains: Sequence[Mapping[str, Any]],
    *,
    seed: str,
) -> List[Dict[str, Any]]:
    selected_domains = {entry.get("domain") for entry in domains}
    insights: List[Dict[str, Any]] = []
    candidates: List[Tuple[str, Mapping[str, Any]]] = []
    used_families: list[str] = []
    for domain, entry in fragments_by_domain.items():
        slots = entry.get("slots") if isinstance(entry, Mapping) else None
        if not isinstance(slots, Mapping):
            continue
        fragment = slots.get("micro_insight") or slots.get("cause")
        if not isinstance(fragment, Mapping):
            continue
        candidates.append((domain, fragment))
    for domain, fragment in candidates:
        if len(insights) >= MICRO_INSIGHT_LIMIT:
            break
        if domain in selected_domains and any(d not in selected_domains for d, _ in candidates):
            continue
        family = select_rhythm_family(seed, "user_compact_micro", domain, used_families)
        insights.append(
            {
                "text": _truncate_text(
                    render_fragment_line(
                        _fragment_text(fragment),
                        family=family,
                        role="experienced",
                        evidence_text=_primary_evidence_text(fragment),
                    ),
                    HIGHLIGHT_TEXT_LIMIT,
                ),
                "domain": domain,
                "evidence": _build_evidence(fragment),
            }
        )
        used_families.append(family)
    return insights


def _compact_seed(
    fragments_by_domain: Mapping[str, Mapping[str, Any]],
    phase2_snapshot: Mapping[str, Any],
) -> str:
    accepted = (((phase2_snapshot.get("slots") or {}).get("accepted")) if isinstance(phase2_snapshot.get("slots"), Mapping) else None) or []
    accepted_ids = [
        str(item.get("fragment_id") or item.get("slot") or item.get("domain") or "")
        for item in accepted
        if isinstance(item, Mapping)
    ]
    if accepted_ids:
        return "|".join(accepted_ids[:12])
    return "|".join(sorted(str(key) for key in fragments_by_domain.keys()))


def _primary_evidence_text(fragment: Mapping[str, Any]) -> str:
    supporting = fragment.get("supporting_facts") or []
    if isinstance(supporting, Iterable):
        for item in supporting:
            if not isinstance(item, Mapping):
                continue
            text = str(item.get("text") or "").strip()
            if text:
                return text
    evidence = fragment.get("evidence") or []
    if isinstance(evidence, Iterable):
        for item in evidence:
            if not isinstance(item, Mapping):
                continue
            text = str(item.get("summary") or item.get("text") or "").strip()
            if text:
                return text
    return ""


def _build_evidence(fragment: Mapping[str, Any]) -> List[Dict[str, Any]]:
    evidence: List[Tuple[float, Dict[str, Any], Tuple[str, str, str, str, str, str]]] = []
    supporting = fragment.get("supporting_facts") or []
    if isinstance(supporting, Iterable):
        for item in supporting:
            if not isinstance(item, Mapping):
                continue
            signature = _signature(
                fragment.get("domain") or "",
                fragment.get("type") or "",
                item,
            )
            evidence.append((_salience_score(item), _format_evidence(item), signature))
    evidence.sort(key=lambda item: (-item[0], item[1].get("ref") or ""))
    seen: set[Tuple[str, str, str, str, str, str]] = set()
    output: List[Dict[str, Any]] = []
    for _, item, signature in evidence:
        if signature in seen:
            continue
        seen.add(signature)
        output.append(item)
        if len(output) >= EVIDENCE_LIMIT:
            break
    return output


def _format_evidence(fragment: Mapping[str, Any]) -> Dict[str, Any]:
    trigger = fragment.get("trigger") or {}
    source_rule_ids = fragment.get("source_rule_ids") or []
    ref = ""
    if isinstance(source_rule_ids, Sequence) and not isinstance(source_rule_ids, (str, bytes)):
        ref = str(source_rule_ids[0]) if source_rule_ids else ""
    elif source_rule_ids:
        ref = str(source_rule_ids)
    item = {
        "ref": ref,
        "type": trigger.get("type") or "unknown",
    }
    salience = fragment.get("salience_score")
    if salience is not None:
        item["salience"] = salience
    summary = fragment.get("text")
    if summary:
        item["summary"] = _truncate_text(str(summary), 140)
    return item


def _signature(
    domain: str,
    slot_type: str,
    fragment: Mapping[str, Any],
) -> Tuple[str, str, str, str, str, str]:
    trigger = fragment.get("trigger") or {}
    planet = normalize_planet_key(trigger.get("planet") or trigger.get("planet1") or fragment.get("planet"))
    sign = normalize_sign_key(trigger.get("sign"))
    house_value = trigger.get("house")
    house = "" if house_value is None else str(house_value).strip()
    rule_group = _rule_id_group(fragment.get("source_rule_ids"))
    return (str(domain), str(slot_type), planet, sign, house, rule_group)


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


def _fragment_text(fragment: Mapping[str, Any]) -> str:
    text = fragment.get("text") or fragment.get("_semantic_text")
    if not text:
        return ""
    return " ".join(str(text).strip().split())


def _salience_score(fragment: Mapping[str, Any]) -> float:
    try:
        return float(fragment.get("salience_score") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _apply_shadow_template(text: str) -> str:
    template = (load_tone_config().get("shadow_safety") or {}).get("template")
    if isinstance(template, str) and "{shadow_text}" in template:
        return template.format(shadow_text=text)
    return (
        "Golge tarafinda bu, "
        f"{text} baskisini hissettirebilir; bu bir suc degil, sadece bir yuklenme alanidir."
    )


def _truncate_text(text: str, limit: int) -> str:
    cleaned = " ".join(text.strip().split())
    if len(cleaned) <= limit:
        return cleaned
    truncated = cleaned[:limit].rsplit(" ", 1)[0]
    return f"{truncated}..."


def _ensure_sentence(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return ""
    if cleaned[-1] not in ".!?":
        return f"{cleaned}."
    return cleaned


def _title_for_domain(domain: str) -> str:
    return " ".join(part.capitalize() for part in domain.split("_") if part)
