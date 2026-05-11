from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence
import re
import unicodedata


@dataclass(frozen=True)
class PeriodSemanticEvidence:
    role: str
    source: str
    label: str
    detail: str | None = None
    weight: float | None = None


@dataclass(frozen=True)
class PeriodSemanticFocusResult:
    version: str = "period_semantic_focus_v1"
    selected_meaning: str = "period_focus_unspecified"
    meaning_family: str | None = None
    primary_domain: str | None = None
    secondary_domains: list[str] = field(default_factory=list)
    why_this_meaning: list[str] = field(default_factory=list)
    evidence: list[PeriodSemanticEvidence] = field(default_factory=list)
    suppressed_meanings: list[str] = field(default_factory=list)
    confidence: float = 0.35
    source: str = "unknown"
    scene_translation_request: dict[str, Any] | None = None
    voice_register_hints: dict[str, Any] | None = None
    debug: dict[str, Any] = field(default_factory=dict)

    def to_debug_dict(self, *, include_evidence: bool = False) -> dict[str, Any]:
        payload = {
            "version": self.version,
            "selected_meaning": self.selected_meaning,
            "meaning_family": self.meaning_family,
            "primary_domain": self.primary_domain,
            "secondary_domains": list(self.secondary_domains),
            "why_this_meaning": list(self.why_this_meaning),
            "suppressed_meanings": list(self.suppressed_meanings),
            "confidence": self.confidence,
            "source": self.source,
            "evidence_count": len(self.evidence),
            "scene_translation_request": dict(self.scene_translation_request or {}),
            "voice_register_hints": dict(self.voice_register_hints or {}),
            "debug": dict(self.debug),
        }
        if include_evidence:
            payload["evidence"] = [asdict(item) for item in self.evidence]
        return payload


def resolve_period_semantic_focus(
    *,
    canonical_period_spine: Any | None,
    active_life_chapter: Any | None,
    period_voice_policy: Any | None,
    manifestation_context: Any | None,
    selected_events: Sequence[Any] | None,
    period_core_seed: Mapping[str, Any] | None,
    canonical_natal_state: Any | None = None,
    debug: bool = False,
) -> PeriodSemanticFocusResult:
    chapter = active_life_chapter if isinstance(active_life_chapter, Mapping) else {}
    spine = canonical_period_spine if isinstance(canonical_period_spine, Mapping) else {}
    policy = period_voice_policy if isinstance(period_voice_policy, Mapping) else {}
    scene = manifestation_context if isinstance(manifestation_context, Mapping) else {}
    events = [item for item in (selected_events or []) if isinstance(item, Mapping)]
    core_seed = period_core_seed if isinstance(period_core_seed, Mapping) else {}

    debug_fields: dict[str, Any] = {
        "used_fields": [],
        "missing_fields": [],
        "canonical_natal_state_present": canonical_natal_state is not None,
        "period_core_seed_keys": sorted(str(key) for key in core_seed.keys()),
    }

    chapter_result = _from_life_chapter(chapter, debug_fields=debug_fields)
    if chapter_result is not None:
        return _with_supporting_context(
            chapter_result,
            spine=spine,
            policy=policy,
            scene=scene,
            events=events,
            debug_fields=debug_fields,
        )

    spine_result = _from_canonical_period_spine(spine, debug_fields=debug_fields)
    if spine_result is not None:
        return _with_supporting_context(
            spine_result,
            spine=spine,
            policy=policy,
            scene=scene,
            events=events,
            debug_fields=debug_fields,
        )

    policy_result = _from_period_voice_policy(policy, debug_fields=debug_fields)
    if policy_result is not None:
        return _with_supporting_context(
            policy_result,
            spine=spine,
            policy=policy,
            scene=scene,
            events=events,
            debug_fields=debug_fields,
        )

    event_result = _from_selected_events(events, debug_fields=debug_fields)
    if event_result is not None:
        return _with_supporting_context(
            event_result,
            spine=spine,
            policy=policy,
            scene=scene,
            events=events,
            debug_fields=debug_fields,
        )

    return PeriodSemanticFocusResult(
        selected_meaning="period_focus_unspecified",
        confidence=0.35,
        source="unknown",
        debug=debug_fields if debug else {"used_fields": [], "missing_fields": debug_fields.get("missing_fields") or []},
    )


def _from_life_chapter(
    chapter: Mapping[str, Any],
    *,
    debug_fields: dict[str, Any],
) -> PeriodSemanticFocusResult | None:
    if not chapter:
        debug_fields["missing_fields"].append("active_life_chapter")
        return None

    confidence_token = str(chapter.get("confidence") or "").strip().lower()
    raw_confidence = chapter.get("confidence")
    if hasattr(raw_confidence, "value"):
        confidence_token = str(getattr(raw_confidence, "value") or "").strip().lower()
    confidence_numeric = {"low": 0.45, "medium": 0.6, "high": 0.8}.get(confidence_token, 0.0)
    semantic_focus = chapter.get("semantic_focus") if isinstance(chapter.get("semantic_focus"), Mapping) else {}
    renderer_handoff = chapter.get("renderer_handoff") if isinstance(chapter.get("renderer_handoff"), Mapping) else {}
    has_anchor = bool(
        str(chapter.get("selected_meaning") or "").strip()
        or str(chapter.get("selected_meaning_family") or "").strip()
        or str(semantic_focus.get("primary") or "").strip()
        or renderer_handoff
    )
    if confidence_numeric < 0.6 or not has_anchor:
        debug_fields["missing_fields"].append("active_life_chapter.high_confidence_anchor")
        return None

    debug_fields["used_fields"].append("active_life_chapter")
    selected_meaning = (
        str(semantic_focus.get("primary") or "").strip()
        or str(chapter.get("selected_meaning_family") or "").strip()
        or _normalize_semantic_label(str(chapter.get("selected_meaning") or "").strip())
        or "period_focus_unspecified"
    )
    meaning_family = str(chapter.get("selected_meaning_family") or "").strip() or None
    domain_ownership = (
        chapter.get("domain_ownership") if isinstance(chapter.get("domain_ownership"), Mapping) else {}
    )
    primary_domain = (
        str(domain_ownership.get("primary_domain") or "").strip()
        or str(chapter.get("domain") or "").strip()
        or None
    )
    secondary_domains = _dedupe_strings(
        list(domain_ownership.get("secondary_domains") or [])
        + list(chapter.get("shared_domain_priority") or [])
        + list(semantic_focus.get("secondary") or [])
    )
    why_this_meaning = [
        "active_life_chapter provided semantic_focus",
        "life_chapter confidence is high enough to anchor selected meaning",
    ]
    evidence = _chapter_evidence(chapter)
    suppressed_meanings = _chapter_suppressed_meanings(chapter)
    scene_translation_request = _chapter_scene_translation_request(chapter)
    voice_register_hints = (
        dict(chapter.get("voice_hints") or {}) if isinstance(chapter.get("voice_hints"), Mapping) else None
    )

    return PeriodSemanticFocusResult(
        selected_meaning=selected_meaning,
        meaning_family=meaning_family,
        primary_domain=primary_domain,
        secondary_domains=secondary_domains,
        why_this_meaning=why_this_meaning,
        evidence=evidence,
        suppressed_meanings=suppressed_meanings,
        confidence=0.35 + 0.25,
        source="life_chapter",
        scene_translation_request=scene_translation_request,
        voice_register_hints=voice_register_hints,
        debug={
            "raw_selected_meaning_text": str(chapter.get("selected_meaning") or "").strip(),
            "chapter_type": str(chapter.get("chapter_type") or "").strip(),
            "chapter_phase": str(chapter.get("phase") or "").strip(),
            "renderer_handoff_keys": sorted(str(key) for key in renderer_handoff.keys()),
            "semantic_focus_primary": str(semantic_focus.get("primary") or "").strip(),
            "selected_meaning_family": meaning_family or "",
        },
    )


def _from_canonical_period_spine(
    spine: Mapping[str, Any],
    *,
    debug_fields: dict[str, Any],
) -> PeriodSemanticFocusResult | None:
    if not spine:
        debug_fields["missing_fields"].append("canonical_period_spine")
        return None

    spine_lines = spine.get("spine_lines") if isinstance(spine.get("spine_lines"), list) else []
    selected_meaning = (
        str(spine.get("selected_meaning") or "").strip()
        or str(spine.get("matched_hook") or "").strip()
        or str(spine.get("theme") or "").strip()
        or str(spine_lines[0] or "").strip() if spine_lines else ""
    )
    if not selected_meaning:
        debug_fields["missing_fields"].append("canonical_period_spine.meaning_seed")
        return None

    debug_fields["used_fields"].append("canonical_period_spine")
    evidence = []
    if spine_lines:
        evidence.append(
            PeriodSemanticEvidence(
                role="spine_line",
                source="canonical_period_spine",
                label=str(spine_lines[0]),
                detail="spine line selected from canonical period spine",
            )
        )
    if str(spine.get("target_node_id") or "").strip():
        evidence.append(
            PeriodSemanticEvidence(
                role="natal_hook",
                source="canonical_period_spine",
                label=str(spine.get("target_node_id") or ""),
                detail="canonical period spine target node",
            )
        )
    return PeriodSemanticFocusResult(
        selected_meaning=_normalize_semantic_label(selected_meaning) or selected_meaning,
        meaning_family=str(spine.get("primary_domain") or "").strip() or None,
        primary_domain=str(spine.get("primary_domain") or "").strip() or None,
        secondary_domains=_dedupe_strings(spine.get("supporting_domains") or []),
        why_this_meaning=["canonical_period_spine matched natal activation hook"],
        evidence=evidence,
        suppressed_meanings=[],
        confidence=0.35 + 0.15,
        source="canonical_period_spine",
        debug={
            "raw_selected_meaning_source": selected_meaning,
            "spine_lines": list(spine_lines),
        },
    )


def _from_period_voice_policy(
    policy: Mapping[str, Any],
    *,
    debug_fields: dict[str, Any],
) -> PeriodSemanticFocusResult | None:
    if not policy:
        debug_fields["missing_fields"].append("period_voice_policy")
        return None

    selected_meaning = (
        str(policy.get("meaning_intent") or "").strip()
        or str(policy.get("higher_meaning") or "").strip()
        or str(policy.get("reason_line_seed") or "").strip()
    )
    if not selected_meaning:
        debug_fields["missing_fields"].append("period_voice_policy.meaning_seed")
        return None

    debug_fields["used_fields"].append("period_voice_policy")
    manifestation_context = (
        policy.get("manifestation_context") if isinstance(policy.get("manifestation_context"), Mapping) else {}
    )
    evidence = [
        PeriodSemanticEvidence(
            role="policy_intent",
            source="period_voice_policy",
            label=str(policy.get("meaning_intent") or selected_meaning),
            detail="period voice policy meaning intent",
        )
    ]
    if str(policy.get("reason_line_seed") or "").strip():
        evidence.append(
            PeriodSemanticEvidence(
                role="reason_seed",
                source="period_voice_policy",
                label=str(policy.get("reason_line_seed") or ""),
                detail="reason line seed from policy",
            )
        )
    return PeriodSemanticFocusResult(
        selected_meaning=_normalize_semantic_label(selected_meaning) or selected_meaning,
        meaning_family=str(policy.get("meaning_intent") or "").strip() or None,
        primary_domain=str(manifestation_context.get("life_scene") or "").strip() or None,
        secondary_domains=[],
        why_this_meaning=["period_voice_policy provided meaning intent fallback"],
        evidence=evidence,
        suppressed_meanings=_dedupe_strings(policy.get("avoid_tags") or []),
        confidence=0.35,
        source="period_voice_policy",
        scene_translation_request=dict(manifestation_context or {}) or None,
        voice_register_hints={
            "valence_mode": str(policy.get("valence_mode") or "").strip(),
            "intensity_mode": str(policy.get("intensity_mode") or "").strip(),
            "rhetorical_frame": str(policy.get("rhetorical_frame") or "").strip() or None,
        },
        debug={"raw_selected_meaning_source": selected_meaning},
    )


def _from_selected_events(
    events: Sequence[Mapping[str, Any]],
    *,
    debug_fields: dict[str, Any],
) -> PeriodSemanticFocusResult | None:
    if not events:
        debug_fields["missing_fields"].append("selected_events")
        return None

    dominant = dict(events[0])
    labels = [
        str(dominant.get("event_subtype") or "").strip(),
        str(dominant.get("transit_body") or dominant.get("body") or "").strip().lower(),
        str(dominant.get("aspect") or "").strip().lower(),
        str(dominant.get("natal_point") or "").strip().lower(),
    ]
    selected_meaning = _normalize_semantic_label("_".join(token for token in labels if token))
    if not selected_meaning:
        selected_meaning = "selected_event_fallback"
    debug_fields["used_fields"].append("selected_events")
    return PeriodSemanticFocusResult(
        selected_meaning=selected_meaning,
        primary_domain=_event_primary_domain(dominant),
        secondary_domains=_dedupe_strings(dominant.get("domains") or []),
        why_this_meaning=["selected events support the same domain"],
        evidence=[
            PeriodSemanticEvidence(
                role="selected_event",
                source="selected_events",
                label=str(dominant.get("event_id") or selected_meaning),
                detail=str(dominant.get("transit_body") or ""),
            )
        ],
        suppressed_meanings=[],
        confidence=0.35,
        source="selected_event_fallback",
        debug={"fallback_event_id": str(dominant.get("event_id") or "")},
    )


def _with_supporting_context(
    base: PeriodSemanticFocusResult,
    *,
    spine: Mapping[str, Any],
    policy: Mapping[str, Any],
    scene: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
    debug_fields: dict[str, Any],
) -> PeriodSemanticFocusResult:
    confidence = base.confidence
    evidence = list(base.evidence)
    why = list(base.why_this_meaning)
    secondary_domains = list(base.secondary_domains)
    scene_request = dict(base.scene_translation_request or {})
    voice_hints = dict(base.voice_register_hints or {})

    if spine:
        confidence += 0.15
        if "canonical_period_spine" not in why and base.source != "canonical_period_spine":
            why.append("canonical_period_spine matched natal activation hook")
        if not any(item.source == "canonical_period_spine" for item in evidence):
            target_node = str(spine.get("target_node_id") or "").strip()
            if target_node:
                evidence.append(
                    PeriodSemanticEvidence(
                        role="natal_hook",
                        source="canonical_period_spine",
                        label=target_node,
                        detail="supporting canonical natal activation hook",
                    )
                )

    if scene:
        confidence += 0.10
        why.append("manifestation_context mapped dominant house to lived scene")
        scene_request = {
            **dict(scene),
            **scene_request,
        }
        life_scene = str(scene.get("life_scene") or "").strip()
        if life_scene and life_scene not in secondary_domains:
            secondary_domains.append(life_scene)

    event_domains = _event_domains(events)
    if event_domains:
        confidence += 0.10
        why.append("selected events support same domain")
        for domain in event_domains:
            if domain not in secondary_domains and domain != base.primary_domain:
                secondary_domains.append(domain)
        top_event = events[0]
        top_event_id = str(top_event.get("event_id") or "").strip()
        if top_event_id:
            evidence.append(
                PeriodSemanticEvidence(
                    role="selected_event",
                    source="selected_events",
                    label=top_event_id,
                    detail=f"{top_event.get('transit_body') or ''} {top_event.get('aspect') or ''} {top_event.get('natal_point') or ''}".strip(),
                )
            )

    if policy:
        manifestation_context = (
            policy.get("manifestation_context") if isinstance(policy.get("manifestation_context"), Mapping) else {}
        )
        if not scene_request and manifestation_context:
            scene_request = dict(manifestation_context)
        if not voice_hints:
            voice_hints = {
                "valence_mode": str(policy.get("valence_mode") or "").strip(),
                "intensity_mode": str(policy.get("intensity_mode") or "").strip(),
                "rhetorical_frame": str(policy.get("rhetorical_frame") or "").strip() or None,
            }

    if not scene_request:
        scene_request = None
    if not voice_hints:
        voice_hints = None

    return PeriodSemanticFocusResult(
        version=base.version,
        selected_meaning=base.selected_meaning,
        meaning_family=base.meaning_family,
        primary_domain=base.primary_domain,
        secondary_domains=_dedupe_strings(secondary_domains),
        why_this_meaning=_dedupe_strings(why),
        evidence=_dedupe_evidence(evidence),
        suppressed_meanings=_dedupe_strings(base.suppressed_meanings),
        confidence=max(0.0, min(0.95, confidence)),
        source=base.source,
        scene_translation_request=scene_request,
        voice_register_hints=voice_hints,
        debug={**dict(base.debug), **debug_fields},
    )


def _chapter_evidence(chapter: Mapping[str, Any]) -> list[PeriodSemanticEvidence]:
    evidence_items = chapter.get("evidence") if isinstance(chapter.get("evidence"), list) else []
    out: list[PeriodSemanticEvidence] = []
    for item in evidence_items:
        if not isinstance(item, Mapping):
            continue
        out.append(
            PeriodSemanticEvidence(
                role=str(item.get("role") or "support"),
                source="life_chapter",
                label=str(item.get("factor") or ""),
                detail=str(item.get("explanation") or "").strip() or None,
            )
        )
    renderer_handoff = chapter.get("renderer_handoff") if isinstance(chapter.get("renderer_handoff"), Mapping) else {}
    anchor = str(renderer_handoff.get("chart_specific_anchor") or "").strip()
    if anchor:
        out.append(
            PeriodSemanticEvidence(
                role="renderer_anchor",
                source="life_chapter.renderer_handoff",
                label=anchor,
                detail=str(renderer_handoff.get("chapter_weight") or "").strip() or None,
            )
        )
    return out


def _chapter_suppressed_meanings(chapter: Mapping[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("suppressed_readings", "suppressed_surface_readings"):
        items = chapter.get(key) if isinstance(chapter.get(key), list) else []
        for item in items:
            if isinstance(item, Mapping):
                reading = str(item.get("reading") or "").strip()
                if reading:
                    out.append(reading)
    semantic_focus = chapter.get("semantic_focus") if isinstance(chapter.get("semantic_focus"), Mapping) else {}
    for item in semantic_focus.get("not_this") or []:
        token = str(item or "").strip()
        if token:
            out.append(token)
    renderer_handoff = chapter.get("renderer_handoff") if isinstance(chapter.get("renderer_handoff"), Mapping) else {}
    for item in renderer_handoff.get("avoid_readings") or []:
        token = str(item or "").strip()
        if token:
            out.append(token)
    return _dedupe_strings(out)


def _chapter_scene_translation_request(chapter: Mapping[str, Any]) -> dict[str, Any] | None:
    handoff = chapter.get("renderer_handoff") if isinstance(chapter.get("renderer_handoff"), Mapping) else {}
    scene_priority = chapter.get("scene_priority") if isinstance(chapter.get("scene_priority"), list) else []
    if not handoff and not scene_priority:
        return None
    payload: dict[str, Any] = {
        "human_scene": str(handoff.get("human_scene") or "").strip(),
        "core_contrast": str(handoff.get("core_contrast") or "").strip(),
        "chapter_weight": str(handoff.get("chapter_weight") or "").strip(),
        "chart_specific_anchor": str(handoff.get("chart_specific_anchor") or "").strip(),
        "voice_register": str(handoff.get("voice_register") or "").strip(),
        "avoid_readings": _dedupe_strings(handoff.get("avoid_readings") or []),
        "scene_priority": [dict(item) for item in scene_priority if isinstance(item, Mapping)],
    }
    shared_domain_priority = _dedupe_strings(chapter.get("shared_domain_priority") or [])
    if shared_domain_priority:
        payload["shared_domain_priority"] = shared_domain_priority
    trust_axis_anchor = str(chapter.get("trust_axis_anchor") or "").strip()
    if trust_axis_anchor:
        payload["trust_axis_anchor"] = trust_axis_anchor
    contrast = str(chapter.get("shared_vs_private_contrast") or "").strip()
    if contrast:
        payload["shared_vs_private_contrast"] = contrast
    return payload


def _event_domains(events: Sequence[Mapping[str, Any]]) -> list[str]:
    domains: list[str] = []
    for item in events:
        for domain in item.get("domains") or []:
            token = str(domain or "").strip()
            if token:
                domains.append(token)
        primary = _event_primary_domain(item)
        if primary:
            domains.append(primary)
    return _dedupe_strings(domains)


def _event_primary_domain(event: Mapping[str, Any]) -> str | None:
    domains = event.get("domains")
    if isinstance(domains, list) and domains:
        token = str(domains[0] or "").strip()
        if token:
            return token
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    house = houses.get("transit_in_natal_house") or houses.get("natal_point_house")
    if house is not None:
        return f"house_{house}"
    return None


def _normalize_semantic_label(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_text).strip("_").lower()
    slug = re.sub(r"_+", "_", slug)
    return slug[:96]


def _dedupe_strings(values: Sequence[Any]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        token = str(value or "").strip()
        if token and token not in seen:
            seen.add(token)
            out.append(token)
    return out


def _dedupe_evidence(values: Sequence[PeriodSemanticEvidence]) -> list[PeriodSemanticEvidence]:
    out: list[PeriodSemanticEvidence] = []
    seen: set[tuple[str, str, str]] = set()
    for item in values:
        key = (item.role, item.source, item.label)
        if item.label and key not in seen:
            seen.add(key)
            out.append(item)
    return out
