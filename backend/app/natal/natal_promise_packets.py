from __future__ import annotations

import copy
import os
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from .promise_archetype_registry_sprint1 import (
    REGISTRY_VERSION,
    get_natal_promise_archetype_registry_sprint1,
)

PACKET_VERSION = "natal_promise_packets_v1"
_SCORING_VERSION = "sprint1_context_scoring_v1"
_ENABLED_VALUES = {"1", "true", "yes", "on"}
_PACKET_SOURCE_TYPES = {
    "exact_registry",
    "composed_semantic",
    "generic_fallback",
    "discovery_scaffold",
    "legacy_graph",
}
_GENERIC_PACKET_IDS = {
    "identity_identity",
    "relationship_relationships",
    "career_career_visibility",
    "mind_mind_system",
}
_BANNED_PHRASES = {
    "micro insight",
    "potansiyel",
    "gölge",
    "potansiyel birlikte çalışır",
    "etki çizgisi devreye girer",
    "genel yaşamda gölge tonu",
    "bu çizgi senden kolay kolay kaybolmaz",
    "kimlik modelin aktive oluyor",
    "zihinsel süreçlerin yeniden yapılanıyor",
}
_DOMAIN_ALIASES = {
    "mind": "mind",
    "communication": "communication",
    "identity": "identity",
    "behavior_reflex": "behavior_reflex",
    "inner_world": "inner_world",
    "spirituality": "spirituality",
    "emotional_world": "emotional_world",
    "home_family": "home_family",
    "roots": "home_family",
    "relationship": "relationship",
    "relationships": "relationship",
    "love": "love",
    "emotional_depth": "emotional_depth",
    "career": "career",
    "visibility": "visibility",
    "creativity": "creativity",
    "money_self_worth": "money_self_worth",
    "self_worth": "money_self_worth",
    "community": "community",
    "learning": "mind",
    "body": "identity",
    "service": "identity",
    "responsibility": "career",
    "action": "action",
    "daily_life": "action",
    "axis_tension": "axis_tension",
    "community": "community",
    "vision": "community",
}
_PROMISE_TYPE_ALIASES = {
    "gift": "gift",
    "shadow_or_friction": "shadow_or_friction",
    "wound_to_gift": "wound_to_gift",
    "need": "need",
    "drive": "drive",
    "mind_style": "mind_style",
    "love_style": "love_style",
    "career_signature": "career_signature",
    "behavior_reflex": "behavior_reflex",
    "mind_identity": "mind_identity",
    "identity_style": "identity_style",
    "social_mind_style": "social_mind_style",
    "roots_transformation": "roots_transformation",
    "home_family_signature": "home_family_signature",
    "creative_emotional_style": "creative_emotional_style",
    "creative_signature": "creative_signature",
    "career_friction_to_power": "career_friction_to_power",
    "relationship_need": "relationship_need",
    "identity_action_style": "identity_action_style",
    "action_friction_to_strength": "action_friction_to_strength",
    "inner_pressure_to_maturity": "inner_pressure_to_maturity",
    "emotional_home_signature": "emotional_home_signature",
    "career_mind_signature": "career_mind_signature",
    "axis_tension": "axis_tension",
    "collective_identity": "collective_identity",
    "community_signature": "community_signature",
    "relationship_wound_to_gift": "relationship_wound_to_gift",
    "career_love_style": "career_love_style",
    "life_direction_axis": "life_direction_axis",
}
_DOMAIN_TYPE_FALLBACKS = {
    "mind": {"mind_style": 0.28, "gift": 0.12},
    "communication": {"mind_style": 0.22, "behavior_reflex": 0.12},
    "identity": {"behavior_reflex": 0.2, "gift": 0.08},
    "behavior_reflex": {"behavior_reflex": 0.24, "mind_style": 0.12},
    "inner_world": {"need": 0.2, "wound_to_gift": 0.18, "behavior_reflex": 0.08},
    "spirituality": {"need": 0.18, "wound_to_gift": 0.14},
    "emotional_world": {"need": 0.18, "gift": 0.12, "creative_emotional_style": 0.1},
    "home_family": {"roots_transformation": 0.28, "home_family_signature": 0.24, "need": 0.1},
    "relationship": {"love_style": 0.22, "need": 0.18},
    "love": {"love_style": 0.26, "gift": 0.12},
    "emotional_depth": {"need": 0.18, "love_style": 0.18},
    "career": {"career_signature": 0.26, "wound_to_gift": 0.12},
    "visibility": {"career_signature": 0.22, "wound_to_gift": 0.14},
    "creativity": {"creative_signature": 0.24, "creative_emotional_style": 0.2, "gift": 0.18, "career_signature": 0.1},
    "money_self_worth": {"behavior_reflex": 0.16, "love_style": 0.12, "gift": 0.1},
    "community": {"mind_style": 0.16, "gift": 0.12},
    "action": {"identity_action_style": 0.24, "action_friction_to_strength": 0.22, "behavior_reflex": 0.12},
    "axis_tension": {"axis_tension": 0.28, "life_direction_axis": 0.18, "wound_to_gift": 0.1},
    "learning": {"mind_style": 0.18, "gift": 0.1},
    "body": {"wound_to_gift": 0.18, "behavior_reflex": 0.1},
    "service": {"wound_to_gift": 0.16, "gift": 0.1},
}
_PROMISE_TYPE_LAYER = {
    "gift": "potential",
    "shadow_or_friction": "shadow",
    "wound_to_gift": "shadow",
    "need": "mechanism",
    "drive": "effect",
    "mind_style": "mechanism",
    "love_style": "effect",
    "career_signature": "effect",
    "behavior_reflex": "mechanism",
    "mind_identity": "mechanism",
    "identity_style": "mechanism",
    "social_mind_style": "mechanism",
    "roots_transformation": "shadow",
    "home_family_signature": "cause",
    "creative_emotional_style": "effect",
    "creative_signature": "effect",
    "career_friction_to_power": "shadow",
    "relationship_need": "mechanism",
    "identity_action_style": "mechanism",
    "action_friction_to_strength": "shadow",
    "inner_pressure_to_maturity": "shadow",
    "emotional_home_signature": "cause",
    "career_mind_signature": "effect",
    "axis_tension": "shadow",
    "collective_identity": "mechanism",
    "community_signature": "effect",
    "relationship_wound_to_gift": "shadow",
    "career_love_style": "effect",
    "life_direction_axis": "mechanism",
}


@dataclass
class ComposedSemanticCandidateV1:
    id: str
    family: str
    subtype: str
    source_type: str
    domain: str
    promise_type: str
    domain_reason: list[str]
    public_job: str
    confidence: float
    confidence_tier: str
    chart_facts_match: bool
    technical_anchors: list[str]
    source_evidence_ids: list[str]
    evidence_trace: dict[str, Any]
    direct_meaning: str
    lived_scene: str
    lived_scene_atoms: list[str]
    gift: str
    inner_tension: str
    growth_direction: str
    avoid_readings: list[str]
    projection_hints: dict[str, Any]
    scoring_breakdown: dict[str, float]
    matched_archetypes: list[str]
    public_eligibility: dict[str, Any]
    meta: dict[str, Any]


def _env_enabled(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in _ENABLED_VALUES


_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PHASE3_ORIGIN_HINT_DENYLIST: tuple[str, ...] = (
    "neutral_or_gift_only_signature",
    "generic_fallback_packet",
    "debug_only_family",
    "exactness_only_without_owner_route",
    "non_owner_broad_category_summary",
    "generic_relationship_friction_without_trust_owner",
    "weak_global_or_generational_only_anchor",
)


def _relationship_hidden_private_love_phase3_internal_metadata_enabled() -> bool:
    return _env_enabled(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PHASE3_INTERNAL_METADATA"
    )


def _relationship_hidden_private_love_origin_hint_assessment(
    *,
    subtype: str,
    source_type: str,
    domain_reason: Sequence[str],
    technical_anchors: Sequence[str],
    subtype_default_fallback: bool,
    non_public_discovery: bool,
) -> dict[str, Any]:
    reasons_lower = {str(item or "").strip().lower() for item in domain_reason if str(item or "").strip()}
    anchors_lower = [str(item or "").strip().lower() for item in technical_anchors if str(item or "").strip()]
    has_personal_or_angle_anchor = any(
        marker in anchor
        for anchor in anchors_lower
        for marker in ("venüs", "venus", "moon", "sun", "asc", "dsc", "yükselen")
    )
    has_owner_route = "12h hidden-love signature" in reasons_lower and has_personal_or_angle_anchor

    deny_reasons: list[str] = []
    if subtype != "hidden_private_love":
        deny_reasons.append("non_owner_broad_category_summary")
    if source_type == "generic_fallback" or subtype_default_fallback:
        deny_reasons.append("generic_fallback_packet")
    if source_type == "discovery_scaffold":
        deny_reasons.append("debug_only_family")
    if not has_owner_route:
        deny_reasons.append("exactness_only_without_owner_route")
    if not has_personal_or_angle_anchor:
        deny_reasons.append("weak_global_or_generational_only_anchor")

    allow_reasons: list[str] = []
    if subtype == "hidden_private_love":
        allow_reasons.append("hidden_private_signature")
    if has_owner_route:
        allow_reasons.append("owner_hidden_private_route")
    if has_personal_or_angle_anchor:
        allow_reasons.append("personalized_anchor_present")

    return {
        "eligible": bool(allow_reasons) and not deny_reasons,
        "allow_reasons": allow_reasons,
        "deny_reasons": deny_reasons,
        "deny_catalog": list(_RELATIONSHIP_HIDDEN_PRIVATE_LOVE_PHASE3_ORIGIN_HINT_DENYLIST),
    }


def _build_relationship_hidden_private_love_phase3_internal_metadata(
    *,
    source_type: str,
    domain_reason: Sequence[str],
    technical_anchors: Sequence[str],
    subtype_default_fallback: bool,
    non_public_discovery: bool,
) -> dict[str, Any]:
    origin_hint = _relationship_hidden_private_love_origin_hint_assessment(
        subtype="hidden_private_love",
        source_type=source_type,
        domain_reason=domain_reason,
        technical_anchors=technical_anchors,
        subtype_default_fallback=subtype_default_fallback,
        non_public_discovery=non_public_discovery,
    )
    return {
        "pilot_family": "hidden_private_deep_read",
        "slide_profile": "pattern_to_gift",
        "status": "pilot_scoped_approval_pending_section_13_2",
        "phase_boundary": "internal_metadata_only",
        "role_bindings": {
            "origin_hint": {
                "surface_role": "hidden_mechanism",
                "eligible": origin_hint["eligible"],
                "allow_reasons": list(origin_hint["allow_reasons"]),
                "deny_reasons": list(origin_hint["deny_reasons"]),
            },
            "gift": {"surface_role": "gift_in_silence", "source_field": "gift"},
            "shadow": {"surface_role": "protective_pattern", "source_field": "shadow_or_friction"},
            "integration": {"surface_role": "safe_visibility", "source_field": "growth_direction"},
        },
        "map_trace": [
            "private_scene<=lived_scene",
            "hidden_mechanism<=origin_hint",
            "protective_pattern<=shadow_or_friction",
            "gift_in_silence<=gift",
            "safe_visibility<=growth_direction",
        ],
        "deselected_trace": [
            "identity_polarity=pending",
            "held_plurality=pending",
            "emotional_base=pending",
            "phase4_renderer=not_enabled",
        ],
        "scope_guards": [
            "pilot_only_hidden_private",
            "no_public_output_change",
            "no_global_taxonomy_promotion",
        ],
    }


def build_natal_promise_packets_v1(
    *,
    sections_v2: Sequence[Mapping[str, Any]] | None,
    supporting_threads: Sequence[Mapping[str, Any]] | None,
    meaning_graph_v1_1: Mapping[str, Any] | None = None,
    planets: Sequence[Mapping[str, Any]] | None = None,
    aspects: Sequence[Mapping[str, Any]] | None = None,
    natal_graph_compact: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    meta_info: Mapping[str, Any] | None = None,
    locale: str = "tr",
    mode: str = "selected",
) -> Dict[str, Any]:
    normalized_mode = str(mode or "selected").strip().lower() or "selected"
    registry = get_natal_promise_archetype_registry_sprint1()
    entries = registry.get("entries") if isinstance(registry.get("entries"), Mapping) else {}
    # v0.3: chart-correctness filter. Registry entries whose ids encode a
    # specific placement (validated by ``_CHART_FACT_VALIDATORS``) and that do
    # not match the current chart MUST NOT bleed their voice_seeds / direct
    # meaning into other packets via the text-based ``_match_registry`` path.
    # Drop them from the entry view used by section / thread candidates; the
    # chart-signature pipeline still cannot fire them because
    # ``_chart_variant_supported`` guards every entry.
    entries = _filter_entries_against_chart(
        entries,
        planets=planets,
        natal_graph_compact=natal_graph_compact,
    )
    sections = [dict(item) for item in sections_v2 or [] if isinstance(item, Mapping)]
    threads = [dict(item) for item in supporting_threads or [] if isinstance(item, Mapping)]
    thread_lookup = _thread_lookup(threads)
    candidates: list[dict[str, Any]] = []
    used_thread_ids: set[str] = set()

    for section in sections:
        thread = _best_thread_for_section(section=section, thread_lookup=thread_lookup)
        if thread:
            thread_id = str(thread.get("id") or "").strip()
            if thread_id:
                used_thread_ids.add(thread_id)
        candidate = _build_candidate(
            seed=section,
            thread=thread,
            registry_entries=entries,
            locale=locale,
            auxiliary=False,
        )
        if candidate:
            candidates.append(candidate)
        candidates.extend(
            _build_auxiliary_candidates(
                seed=section,
                thread=thread,
                registry_entries=entries,
                locale=locale,
            )
        )
        if normalized_mode == "candidate_inventory":
            candidates.extend(
                _build_candidate_inventory_variants(
                    seed=section,
                    thread=thread,
                    registry_entries=entries,
                    locale=locale,
                )
            )

    for thread in threads:
        thread_id = str(thread.get("id") or "").strip()
        if thread_id and thread_id in used_thread_ids:
            continue
        candidate = _build_candidate(
            seed=thread,
            thread=thread,
            registry_entries=entries,
            locale=locale,
            auxiliary=True,
        )
        if candidate:
            candidates.append(candidate)
        if normalized_mode == "candidate_inventory":
            candidates.extend(
                _build_candidate_inventory_variants(
                    seed=thread,
                    thread=thread,
                    registry_entries=entries,
                    locale=locale,
                )
            )

    chart_signature_candidates = _build_chart_signature_candidates(
        registry_entries=entries,
        planets=planets,
        aspects=aspects,
        natal_graph_compact=natal_graph_compact,
        metadata=metadata,
        meta_info=meta_info,
        locale=locale,
        mode=normalized_mode,
    )
    candidates.extend(chart_signature_candidates)
    if normalized_mode == "candidate_inventory":
        candidates.extend(
            _build_v0_6_discovery_candidates(
                planets=planets,
                aspects=aspects,
                natal_graph_compact=natal_graph_compact,
                locale=locale,
                existing_candidates=candidates,
            )
        )
        if _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9"):
            candidates.extend(
                _build_v0_9_composed_semantic_candidates(
                    planets=planets,
                    aspects=aspects,
                    natal_graph_compact=natal_graph_compact,
                    metadata=metadata,
                    meta_info=meta_info,
                    locale=locale,
                    existing_candidates=candidates,
                )
            )

    packets = _merge_candidates(candidates)
    packets = _dedupe_packets(packets, mode=normalized_mode)
    packets.sort(key=lambda item: (-_safe_float(item.get("strength"), 0.0), str(item.get("id") or "")))
    if normalized_mode == "selected":
        packets = _select_packet_inventory(packets)
        packets = _backfill_selected_packet_inventory(
            packets,
            registry_entries=entries,
            planets=planets,
            aspects=aspects,
            natal_graph_compact=natal_graph_compact,
            metadata=metadata,
            meta_info=meta_info,
            locale=locale,
        )
    # Bug 5 (Adana audit): packet ids that encode a specific placement (e.g.
    # ``moon_leo_8h_deep_proud_heart``, ``capricorn_asc_sun_1h_...``) get
    # picked up from a registry whose match logic is title- and text-based,
    # not chart-fact-based. When the actual chart placement does NOT match
    # the placement encoded in the id, the user-facing copy is still
    # chart-correct (anchors come from chart data) but the packet id itself
    # becomes a misleading debugging label. We annotate each packet with a
    # ``chart_facts_match: bool`` flag so debug consumers can spot the
    # mismatch; we deliberately do NOT rename the id to keep blast radius
    # minimal (cluster plans and tests already key on the existing id).
    _annotate_chart_facts_match(packets, planets=planets, natal_graph_compact=natal_graph_compact)
    _annotate_packet_source_types(packets)
    return {
        "version": PACKET_VERSION,
        "registry_version": REGISTRY_VERSION,
        "registry_authority": str(registry.get("authority") or ""),
        "locale": str(locale or "tr"),
        "packets": packets,
        "meta": {
            "mode": normalized_mode,
            "scoring_version": _SCORING_VERSION,
            "candidate_count": len(candidates),
            "packet_count": len(packets),
            "gift_forward_count": sum(1 for packet in packets if str(packet.get("promise_type")) in {"gift", "love_style", "mind_style", "mind_identity"}),
        },
    }


def _thread_lookup(threads: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for thread in threads:
        section_id = str(thread.get("section_id") or "").strip()
        title = str(thread.get("title") or "").strip()
        if section_id:
            out[section_id].append(dict(thread))
        if title:
            out[_normalize_text(title)].append(dict(thread))
    return out


def _best_thread_for_section(
    *,
    section: Mapping[str, Any],
    thread_lookup: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any] | None:
    section_id = str(section.get("id") or "").strip()
    if section_id and isinstance(thread_lookup.get(section_id), Sequence):
        items = [dict(item) for item in thread_lookup.get(section_id) or [] if isinstance(item, Mapping)]
        if items:
            return items[0]
    title_key = _normalize_text(str(section.get("title") or ""))
    if title_key and isinstance(thread_lookup.get(title_key), Sequence):
        items = [dict(item) for item in thread_lookup.get(title_key) or [] if isinstance(item, Mapping)]
        if items:
            return items[0]
    return None


def _build_candidate(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    registry_entries: Mapping[str, Mapping[str, Any]],
    locale: str,
    auxiliary: bool,
    forced_matches: Sequence[Mapping[str, Any]] | None = None,
    forced_domain: str | None = None,
    variant_suffix: str = "",
) -> dict[str, Any] | None:
    title = str(seed.get("title") or "").strip()
    if not title:
        return None
    text_bundle = _collect_text_bundle(seed=seed, thread=thread)
    category_support = _best_category_support(seed=seed, thread=thread)
    evidence_entries = _collect_evidence(seed=seed, thread=thread)
    if auxiliary and not _strong_auxiliary_seed(seed=seed, text_bundle=text_bundle, category_support=category_support):
        return None
    if forced_matches is not None:
        matches = [dict(item) for item in forced_matches if isinstance(item, Mapping)]
    else:
        matches = _match_registry(
            registry_entries=registry_entries,
            title=title,
            text_bundle=text_bundle,
            category_support=category_support,
            seed=seed,
            thread=thread,
        )
    if auxiliary and not matches and not evidence_entries:
        return None

    domain = forced_domain or _resolve_domain(seed=seed, thread=thread, matches=matches)
    strength, scoring_breakdown = _score_candidate(
        domain=domain,
        category_support=category_support,
        matches=matches,
        seed=seed,
        thread=thread,
        text_bundle=text_bundle,
    )
    if auxiliary and strength < 0.56:
        return None
    if not auxiliary and strength < 0.44:
        return None

    promise_type = _resolve_promise_type(
        domain=domain,
        matches=matches,
        category_support=category_support,
        seed=seed,
    )
    technical_anchors = _technical_anchors(seed=seed, thread=thread, category_support=category_support, matches=matches)
    source_evidence_ids = _source_evidence_ids(seed=seed, thread=thread, evidence_entries=evidence_entries)
    direct_meaning = _resolve_direct_meaning(seed=seed, matches=matches)
    lived_scene = _resolve_lived_scene(seed=seed, thread=thread, matches=matches)
    gift = _resolve_packet_field("gift", seed=seed, thread=thread, matches=matches, fallback=direct_meaning)
    shadow = _resolve_shadow(seed=seed, thread=thread, category_support=category_support, matches=matches)
    inner_tension = _resolve_inner_tension(seed=seed, thread=thread, category_support=category_support, matches=matches)
    growth = _resolve_growth(seed=seed, thread=thread, matches=matches)
    voice_candidates = _voice_seed_candidates(
        seed=seed,
        thread=thread,
        matches=matches,
        direct_meaning=direct_meaning,
        lived_scene=lived_scene,
        gift=gift,
        shadow_or_friction=shadow,
        growth_direction=growth,
    )
    voice_seeds = _rank_voice_seeds(voice_candidates)
    theme_key = _theme_key(domain=domain, matches=matches, category_support=category_support, seed=seed)
    if not voice_seeds:
        voice_seeds = [_ensure_sentence(direct_meaning or title)]

    return {
        "id": _candidate_id(domain=domain, matches=matches, seed=seed, variant_suffix=variant_suffix),
        "theme_key": theme_key,
        "domain": domain,
        "promise_type": promise_type,
        "source_type": _initial_candidate_source_type(
            packet_id=_candidate_id(domain=domain, matches=matches, seed=seed, variant_suffix=variant_suffix),
            matches=matches,
        ),
        "strength": round(max(0.0, min(1.0, strength)), 4),
        "technical_anchors": technical_anchors,
        "source_evidence_ids": source_evidence_ids,
        "direct_meaning": direct_meaning,
        "lived_scene": lived_scene,
        "gift": gift,
        "shadow_or_friction": shadow,
        "inner_tension": inner_tension,
        "growth_direction": growth,
        "voice_seeds": voice_seeds,
        "avoid_phrases": sorted(_BANNED_PHRASES),
        "source_category_ids": _collect_source_ids(seed=seed, thread=thread, key="category_id"),
        "source_thread_ids": _collect_source_ids(seed=seed, thread=thread, key="thread_id"),
        "source_section_ids": _collect_source_ids(seed=seed, thread=thread, key="section_id"),
        "projection_hints": {
            "surfaces": ["profile_top", "profile_deep"],
            "priority": round(max(0.01, strength), 4),
            "auxiliary": auxiliary,
            "opening_strategy": _opening_strategy(promise_type),
        },
        "scoring_breakdown": scoring_breakdown,
        "matched_archetypes": [str(match.get("id") or "").strip() for match in matches if str(match.get("id") or "").strip()],
        "matched_archetype_summaries": [
            {
                "id": str(match.get("id") or "").strip(),
                "score": round(_safe_float(match.get("score"), 0.0), 4),
                "promise_type": str(match.get("promise_type") or "").strip(),
            }
            for match in matches[:4]
            if str(match.get("id") or "").strip()
        ],
        "meta": {
            "title": title,
            "locale": locale,
            "auxiliary": auxiliary,
            "evidence_count": len(evidence_entries),
            "variant_suffix": variant_suffix,
            "source_type": _initial_candidate_source_type(
                packet_id=_candidate_id(domain=domain, matches=matches, seed=seed, variant_suffix=variant_suffix),
                matches=matches,
            ),
        },
    }


def _build_candidate_inventory_variants(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    registry_entries: Mapping[str, Mapping[str, Any]],
    locale: str,
) -> list[dict[str, Any]]:
    title = str(seed.get("title") or "").strip()
    if not title:
        return []
    text_bundle = _collect_text_bundle(seed=seed, thread=thread)
    category_support = _best_category_support(seed=seed, thread=thread)
    matches = _match_registry(
        registry_entries=registry_entries,
        title=title,
        text_bundle=text_bundle,
        category_support=category_support,
        seed=seed,
        thread=thread,
    )
    out: list[dict[str, Any]] = []
    seen_variant_keys: set[str] = set()
    for match in _material_inventory_matches(matches, seed=seed, thread=thread):
        for forced_domain, variant_suffix in _inventory_domains_for_match(
            match=match,
            seed=seed,
            thread=thread,
            category_support=category_support,
        ):
            variant_key = f"{str(match.get('id') or '').strip()}::{forced_domain}::{variant_suffix}"
            if not forced_domain or variant_key in seen_variant_keys:
                continue
            candidate = _build_candidate(
                seed=seed,
                thread=thread,
                registry_entries=registry_entries,
                locale=locale,
                auxiliary=False,
                forced_matches=[match],
                forced_domain=forced_domain,
                variant_suffix=variant_suffix,
            )
            if not candidate:
                continue
            if not _allow_candidate_inventory_variant(candidate, match=match, forced_domain=forced_domain):
                continue
            candidate_meta = dict(candidate.get("meta")) if isinstance(candidate.get("meta"), Mapping) else {}
            candidate_meta["inventory_variant"] = "match"
            candidate_meta["match_id"] = str(match.get("id") or "").strip()
            candidate["meta"] = candidate_meta
            out.append(candidate)
            seen_variant_keys.add(variant_key)
    return out


def _build_chart_signature_candidates(
    *,
    registry_entries: Mapping[str, Mapping[str, Any]],
    planets: Sequence[Mapping[str, Any]] | None,
    aspects: Sequence[Mapping[str, Any]] | None,
    natal_graph_compact: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
    meta_info: Mapping[str, Any] | None,
    locale: str,
    mode: str,
) -> list[dict[str, Any]]:
    if str(mode or "selected").strip().lower() != "candidate_inventory":
        return []
    planet_map = {
        str(item.get("planet") or item.get("name") or "").strip().lower(): dict(item)
        for item in planets or []
        if isinstance(item, Mapping) and str(item.get("planet") or item.get("name") or "").strip()
    }
    if not planet_map:
        return []
    aspect_entries = [dict(item) for item in aspects or [] if isinstance(item, Mapping)]
    house_rulers = (
        natal_graph_compact.get("house_rulers")
        if isinstance(natal_graph_compact, Mapping) and isinstance(natal_graph_compact.get("house_rulers"), Mapping)
        else {}
    )
    dominant_loops = (
        natal_graph_compact.get("dominant_loops")
        if isinstance(natal_graph_compact, Mapping) and isinstance(natal_graph_compact.get("dominant_loops"), Sequence)
        else []
    )
    dominant_planets = (
        meta_info.get("dominant_planets")
        if isinstance(meta_info, Mapping) and isinstance(meta_info.get("dominant_planets"), Sequence)
        else []
    )
    dominant_planet_names = {
        str((item or {}).get("planet") or "").strip().lower()
        for item in dominant_planets
        if isinstance(item, Mapping)
    }
    variants = [
        {
            "match_id": "moon_trine_venus_emotional_warmth",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "İlişkide sıcaklık ve yumuşatma",
            "proof_raw": "Moon trine Venus",
            "chips": ["Ay 8. ev", "Venüs 12. ev", "Moon trine Venus"],
            "scene": "Gergin bir anda bile sevdiğin kişiye daha yumuşak ve iyi gelen bir yerden dönmek.",
            "salience": 0.86,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("Moon trine Venus", "Moon:Venus:trine", 0.94, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("7th house ruler route", "house:7->ruler:Moon->house:8", 0.82, source_type="ruler_route"),
                _support_anchor("Venus conjunction Vertex", "Venus:Vertex:conjunction", 0.76, source_type="aspect"),
            ],
        },
        {
            "match_id": "saturn_sextile_uranus_structured_originality",
            "forced_domain": "mind",
            "variant_suffix": "chart_exact",
            "title": "Zihinde yapı ve özgünlük",
            "proof_raw": "Saturn sextile Uranus",
            "chips": ["Satürn 3. ev", "Uranüs 1. ev", "Saturn sextile Uranus"],
            "scene": "Yeni bir fikri hızla çalışır bir sisteme çevirebilmek.",
            "salience": 0.9,
            "confidence": 0.95,
            "primary_anchor": _support_anchor("Saturn sextile Uranus", "Saturn:Uranus:sextile", 0.95, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("1th house ruler route", "house:1->ruler:Saturn->house:3", 0.84, source_type="ruler_route"),
                _support_anchor("Mercury conjunction Jupiter", "Mercury:Jupiter:conjunction", 0.74, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("structured originality", "structured_originality", 0.86)],
        },
        {
            "match_id": "saturn_sextile_uranus_structured_originality",
            "forced_domain": "identity",
            "variant_suffix": "identity_chart_exact",
            "title": "Kimlikte kontrollü özgünlük",
            "proof_raw": "Saturn sextile Uranus",
            "chips": ["Yükselen Oğlak", "Uranüs 1. ev", "Saturn sextile Uranus"],
            "scene": "Dışarıda kontrollü kalırken içeride daha özgün bir çizgiyi taşımak.",
            "salience": 0.78,
            "confidence": 0.88,
            "primary_anchor": _support_anchor("Saturn sextile Uranus", "Saturn:Uranus:sextile", 0.9, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Ascendant Capricorn", "planet:Ascendant:sign:Capricorn", 0.8, source_type="angle"),
            ],
        },
        {
            "match_id": "saturn_trine_pluto_deep_resilience",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Baskı altında dayanıklılık",
            "proof_raw": "Saturn trine Pluto",
            "chips": ["Saturn trine Pluto", "Sun square Saturn", "Mars opposite Saturn"],
            "scene": "Baskı arttığında dağılmak yerine daha kontrollü ve dayanıklı kalmak.",
            "salience": 0.82,
            "confidence": 0.9,
            "primary_anchor": _support_anchor("Saturn trine Pluto", "Saturn:Pluto:trine", 0.91, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Sun square Saturn", "Sun:Saturn:square", 0.78, source_type="aspect"),
                _support_anchor("Mars opposition Saturn", "Mars:Saturn:opposition", 0.8, source_type="aspect"),
            ],
            "contradiction_signature": _support_anchor("pressure vs resilience", "pressure_vs_resilience", 0.83, source_type="contradiction_signature"),
            "repeated_motifs": [_support_motif("deep resilience", "deep_resilience", 0.84)],
        },
        {
            "match_id": "mercury_conjunct_jupiter_big_mind",
            "forced_domain": "mind",
            "variant_suffix": "chart_exact",
            "title": "Büyük resim zihni",
            "proof_raw": "Mercury conjunction Jupiter",
            "chips": ["Merkür 1. ev", "Jüpiter 1. ev", "Mercury conjunction Jupiter"],
            "scene": "Parçaları bir araya getirip daha büyük resmi kurmak.",
            "salience": 0.76,
            "confidence": 0.87,
            "primary_anchor": _support_anchor("Mercury conjunction Jupiter", "Mercury:Jupiter:conjunction", 0.87, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("3th house ruler route", "house:3->ruler:Jupiter->house:1", 0.8, source_type="ruler_route"),
            ],
        },
        {
            "match_id": "chiron_conjunct_mc_visibility_wound_to_voice",
            "forced_domain": "career",
            "variant_suffix": "chart_exact",
            "title": "Görünürlükte hassasiyet ve ses",
            "proof_raw": "Chiron conjunct MC",
            "chips": ["Chiron 10. ev", "MC Terazi", "Chiron conjunct MC"],
            "scene": "Görünmeden önce fazladan hazırlanmak ama zamanla bunu sese çevirmek.",
            "salience": 0.8,
            "confidence": 0.9,
            "primary_anchor": _support_anchor("Chiron conjunct MC", "Chiron:Midheaven:conjunction", 0.92, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Jupiter square Midheaven", "Jupiter:Midheaven:square", 0.74, source_type="aspect"),
                _support_anchor("Neptune square Midheaven", "Neptune:Midheaven:square", 0.74, source_type="aspect"),
            ],
        },
        {
            "match_id": "moon_leo_8h_deep_proud_heart",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "Yakınlıkta güven mimarisi",
            "proof_raw": "Ay · 8. ev · Aslan",
            "chips": ["7. ev Yengeç", "Ay 8. ev", "Aslan"],
            "scene": "Bir bağ içeri gerçekten oturana kadar duyguyu tam açmamak.",
            "salience": 0.88,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("7th house ruler route", "house:7->ruler:Moon->house:8", 0.93, source_type="ruler_route"),
            "supporting_combo": [
                _support_anchor("Moon trine Venus", "Moon:Venus:trine", 0.8, source_type="aspect"),
            ],
        },
        {
            "match_id": "venus_sagittarius_12h_hidden_expansive_love",
            "forced_domain": "career",
            "variant_suffix": "chart_exact",
            "title": "Görünürlükte içeride olgunlaşan üretim",
            "proof_raw": "Venüs · 12. ev · Yay",
            "chips": ["MC Terazi", "Venüs 12. ev", "Yay"],
            "scene": "Bir üretimi paylaşmadan önce içeride rafine etmek istemek.",
            "salience": 0.84,
            "confidence": 0.92,
            "primary_anchor": _support_anchor("10th house ruler route", "house:10->ruler:Venus->house:12", 0.93, source_type="ruler_route"),
            "supporting_combo": [
                _support_anchor("Jupiter square Midheaven", "Jupiter:Midheaven:square", 0.72, source_type="aspect"),
                _support_anchor("Neptune square Midheaven", "Neptune:Midheaven:square", 0.72, source_type="aspect"),
            ],
        },
        {
            "match_id": "venus_sagittarius_12h_hidden_expansive_love",
            "forced_domain": "relationship",
            "variant_suffix": "relationship_chart_exact",
            "title": "İlişkide gizli ve içeride büyüyen sevgi",
            "proof_raw": "Venüs · 12. ev · Yay",
            "chips": ["Venüs 12. ev", "Yay", "Moon trine Venus"],
            "scene": "Sevginin önce kendi içinde uzun süre büyümesi ve kolay açılmaması.",
            "salience": 0.8,
            "confidence": 0.89,
            "primary_anchor": _support_anchor("Venus in house 12", "planet:Venus:house:12", 0.88, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Moon trine Venus", "Moon:Venus:trine", 0.8, source_type="aspect"),
                _support_anchor("Venus conjunction Vertex", "Venus:Vertex:conjunction", 0.76, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("hidden devotion", "hidden_devotion", 0.82)],
        },
        {
            "match_id": "capricorn_asc_sun_1h_composed_self_construction",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Kimlikte öz-kurulum",
            "proof_raw": "Yükselen · Oğlak · Güneş 1. ev",
            "chips": ["Yükselen Oğlak", "Güneş 1. ev", "Satürn 3. ev"],
            "scene": "Dışarıda güçlü, toparlı ve kendi çizgisini koruyan görünmek istemek.",
            "salience": 0.9,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("1th house ruler route", "house:1->ruler:Saturn->house:3", 0.92, source_type="ruler_route"),
            "supporting_combo": [
                _support_anchor("Sun conjunction Ascendant", "Sun:Ascendant:conjunction", 0.86, source_type="aspect"),
                _support_anchor("Saturn square Ascendant", "Saturn:Ascendant:square", 0.82, source_type="aspect"),
            ],
        },
        {
            "match_id": "saturn_3h_aries_speech_decision_language",
            "forced_domain": "mind",
            "variant_suffix": "chart_exact",
            "title": "Zihinde söz ve karar dili",
            "proof_raw": "Satürn · 3. ev · Koç",
            "chips": ["Satürn 3. ev", "Koç", "Merkür 1. ev"],
            "scene": "Cümleyi hem tartıp hem hızlı netleştirmek.",
            "salience": 0.88,
            "confidence": 0.93,
            "primary_anchor": _support_anchor("Saturn in house 3 Aries", "planet:Saturn:house:3:sign:Aries", 0.93, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Mercury conjunction Jupiter", "Mercury:Jupiter:conjunction", 0.76, source_type="aspect"),
                _support_anchor("1th house ruler route", "house:1->ruler:Saturn->house:3", 0.84, source_type="ruler_route"),
            ],
        },
        # ---- v0.3 addendum (additive) ----
        {
            "match_id": "libra_asc_venus_chart_ruler",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Dışarıda denge, içeride seçicilik",
            "proof_raw": "Yükselen · Terazi · Venüs yönetici",
            "chips": ["Yükselen Terazi", "Venüs yönetici", "Sosyal sezgi"],
            "scene": "Bir ortama girdiğinde önce tonu okuyup içeride seçici davranmak.",
            "salience": 0.9,
            "confidence": 0.93,
            "primary_anchor": _support_anchor("Ascendant Libra", "planet:Ascendant:sign:Libra", 0.93, source_type="angle"),
            "supporting_combo": [
                _support_anchor("Chart ruler Venus", "chart_ruler:Venus", 0.85, source_type="ruler_route"),
            ],
        },
        {
            "match_id": "venus_virgo_11h_selective_social_care",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "İlişkide seçici ve emek veren sevgi",
            "proof_raw": "Venüs · 11. ev · Başak",
            "chips": ["Venüs 11. ev", "Başak", "Seçici sevgi"],
            "scene": "Yakınlıkta kalite, emek ve tutarlılık aramak.",
            "salience": 0.86,
            "confidence": 0.92,
            "primary_anchor": _support_anchor("Venus in Virgo 11H", "planet:Venus:sign:Virgo:house:11", 0.92, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Mercury conjunction Venus", "Mercury:Venus:conjunction", 0.78, source_type="aspect"),
            ],
        },
        {
            "match_id": "sun_virgo_12h_quiet_inner_self",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Perde arkasında işleyen kimlik",
            "proof_raw": "Güneş · 12. ev · Başak",
            "chips": ["Güneş 12. ev", "Başak", "Sessiz analiz"],
            "scene": "Görünür olmadan önce içeride düzeltmek ve işe yarar hale getirmek.",
            "salience": 0.88,
            "confidence": 0.93,
            "primary_anchor": _support_anchor("Sun in Virgo 12H", "planet:Sun:sign:Virgo:house:12", 0.93, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Sun opposition Jupiter", "Sun:Jupiter:opposition", 0.76, source_type="aspect"),
            ],
        },
        {
            "match_id": "mercury_virgo_12h_private_analytical_mind",
            "forced_domain": "mind",
            "variant_suffix": "chart_exact",
            "title": "İçeride çalışan analitik zihin",
            "proof_raw": "Merkür · 12. ev · Başak",
            "chips": ["Merkür 12. ev", "Başak", "Sessiz analiz"],
            "scene": "Bir konuşmadan sonra söylenenleri içeride tekrar tekrar ayrıştırmak.",
            "salience": 0.88,
            "confidence": 0.93,
            "primary_anchor": _support_anchor("Mercury in Virgo 12H", "planet:Mercury:sign:Virgo:house:12", 0.93, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Mercury conjunction Venus", "Mercury:Venus:conjunction", 0.8, source_type="aspect"),
                _support_anchor("Moon square Mercury", "Moon:Mercury:square", 0.78, source_type="aspect"),
            ],
        },
        {
            "match_id": "moon_gemini_9h_curious_mind",
            "forced_domain": "mind",
            "variant_suffix": "chart_exact",
            "title": "Duyguyu düşünerek işleyen zihin",
            "proof_raw": "Ay · 9. ev · İkizler",
            "chips": ["Ay 9. ev", "İkizler", "Merak"],
            "scene": "Hissettiğin şeyi anlamlandırmadan tam rahatlayamamak.",
            "salience": 0.9,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("Moon in Gemini 9H", "planet:Moon:sign:Gemini:house:9", 0.94, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Moon square Mercury", "Moon:Mercury:square", 0.8, source_type="aspect"),
            ],
        },
        {
            "match_id": "moon_square_mercury_emotion_mind_friction",
            "forced_domain": "mind",
            "variant_suffix": "chart_exact",
            "title": "Duygu ile düşünce arasında gerilim",
            "proof_raw": "Ay kare Merkür",
            "chips": ["Ay kare Merkür", "Hızlı iç konuşma"],
            "scene": "Bir şeyi hissederken hemen anlatmaya çalışmak ama kelimenin oturmaması.",
            "salience": 0.82,
            "confidence": 0.9,
            "primary_anchor": _support_anchor("Moon square Mercury", "Moon:Mercury:square", 0.9, source_type="aspect"),
            "supporting_combo": [],
        },
        {
            "match_id": "moon_square_venus_need_affection_friction",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "İhtiyaç ile sevgi dili arasında gerilim",
            "proof_raw": "Ay kare Venüs",
            "chips": ["Ay kare Venüs", "Değer görme"],
            "scene": "Sevildiğin halde tam rahatlamamak veya küçük bir ilgisizlikte değerin sorgulandığını hissetmek.",
            "salience": 0.82,
            "confidence": 0.9,
            "primary_anchor": _support_anchor("Moon square Venus", "Moon:Venus:square", 0.9, source_type="aspect"),
            "supporting_combo": [],
        },
        {
            "match_id": "moon_opposite_pluto_emotional_intensity_control",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "Duygunun derinliği ve kontrol",
            "proof_raw": "Ay karşıt Plüton",
            "chips": ["Ay karşıt Plüton", "Yoğun duygu"],
            "scene": "Bir konuyu kapattığını sanıp içeride hâlâ taşımak.",
            "salience": 0.84,
            "confidence": 0.9,
            "primary_anchor": _support_anchor("Moon opposition Pluto", "Moon:Pluto:opposition", 0.9, source_type="aspect"),
            "supporting_combo": [],
        },
        {
            "match_id": "mercury_conjunct_venus_refined_relational_language",
            "forced_domain": "communication",
            "variant_suffix": "chart_exact",
            "title": "Düşünce ve sevgi dilinde zarafet",
            "proof_raw": "Merkür kavuşum Venüs",
            "chips": ["Merkür kavuşum Venüs", "Zarif dil"],
            "scene": "Bir şeyi sert söylemek yerine daha güzel bir dille anlatmaya çalışmak.",
            "salience": 0.82,
            "confidence": 0.9,
            "primary_anchor": _support_anchor("Mercury conjunction Venus", "Mercury:Venus:conjunction", 0.9, source_type="aspect"),
            "supporting_combo": [],
        },
        {
            "match_id": "mercury_square_pluto_deep_mind_pressure",
            "forced_domain": "mind",
            "variant_suffix": "chart_exact",
            "title": "Derin ve baskılı zihin",
            "proof_raw": "Merkür kare Plüton",
            "chips": ["Merkür kare Plüton", "Derin düşünce"],
            "scene": "Bir konuşmadaki alt anlamı yakalamaya çalışmak ve takılıp kalmak.",
            "salience": 0.8,
            "confidence": 0.89,
            "primary_anchor": _support_anchor("Mercury square Pluto", "Mercury:Pluto:square", 0.89, source_type="aspect"),
            "supporting_combo": [],
        },
        {
            "match_id": "venus_square_pluto_intense_love",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "Yoğun çekim ve dönüşen sevgi",
            "proof_raw": "Venüs kare Plüton",
            "chips": ["Venüs kare Plüton", "Yoğun çekim"],
            "scene": "Birine çekildiğinde bunu sıradan bir hoşlanma gibi yaşamamak.",
            "salience": 0.88,
            "confidence": 0.93,
            "primary_anchor": _support_anchor("Venus square Pluto", "Venus:Pluto:square", 0.93, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Moon square Venus", "Moon:Venus:square", 0.78, source_type="aspect"),
            ],
        },
        {
            "match_id": "mars_leo_11h_warm_visible_drive",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "İlişkide sıcak ve cesur hareket",
            "proof_raw": "Mars · 11. ev · Aslan",
            "chips": ["Mars 11. ev", "Aslan", "7. ev Koç"],
            "scene": "Yakınlıkta sıcaklık ve heyecan hızlı yükselebilir; kendi rengini göstermek önemli.",
            "salience": 0.9,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("Mars in Leo 11H", "planet:Mars:sign:Leo:house:11", 0.94, source_type="placement"),
            "supporting_combo": [
                _support_anchor("7th house in Aries", "house:7:sign:Aries", 0.84, source_type="placement"),
                _support_anchor("Mars opposition Uranus", "Mars:Uranus:opposition", 0.86, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("warm visible drive", "warm_visible_drive", 0.86)],
        },
        {
            "match_id": "mars_leo_11h_warm_visible_drive",
            "forced_domain": "community",
            "variant_suffix": "community_chart_exact",
            "title": "Toplulukta yaratıcı ve görünür hareket",
            "proof_raw": "Mars · 11. ev · Aslan",
            "chips": ["Mars 11. ev", "Aslan", "Topluluk"],
            "scene": "Bir grubun içinde kaybolmak değil, kendi rengini göstermek istemek.",
            "salience": 0.84,
            "confidence": 0.9,
            "primary_anchor": _support_anchor("Mars in Leo 11H", "planet:Mars:sign:Leo:house:11", 0.9, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Mars opposition Uranus", "Mars:Uranus:opposition", 0.82, source_type="aspect"),
            ],
        },
        {
            "match_id": "mars_opposite_uranus_freedom_in_action",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "Yakınlıkta özgürlük ve elektrik",
            "proof_raw": "Mars karşıt Uranüs",
            "chips": ["Mars karşıt Uranüs", "Özgürlük ihtiyacı"],
            "scene": "Sıkıştığını hissettiğinde bir anda uzaklaşma isteğinin yükselmesi.",
            "salience": 0.88,
            "confidence": 0.93,
            "primary_anchor": _support_anchor("Mars opposition Uranus", "Mars:Uranus:opposition", 0.93, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Mars in Leo 11H", "planet:Mars:sign:Leo:house:11", 0.82, source_type="placement"),
            ],
        },
        {
            "match_id": "mars_square_chiron_tender_courage",
            "forced_domain": "behavior_reflex",
            "variant_suffix": "chart_exact",
            "title": "Kırılgan cesaret",
            "proof_raw": "Mars kare Chiron",
            "chips": ["Mars kare Chiron", "Kırılgan cesaret"],
            "scene": "Kendini ortaya koymak hassas bir yerden geçebilir.",
            "salience": 0.8,
            "confidence": 0.89,
            "primary_anchor": _support_anchor("Mars square Chiron", "Mars:Chiron:square", 0.89, source_type="aspect"),
            "supporting_combo": [],
        },
        {
            "match_id": "mc_cancer_moon_gemini_9h_teaching_voice",
            "forced_domain": "career",
            "variant_suffix": "chart_exact",
            "title": "Koruyucu ve anlatan public ses",
            # Adana audit polish (#1): the previous proof_raw was a
            # chip-fragment ("MC Yengeç · Ay 9. ev İkizler") that the
            # projection renderer surfaced as the first chip AND as part of
            # the auto-built anchor sentence. Splitting it into two real
            # chips ("MC Yengeç" and "Ay 9. ev İkizler") keeps the three
            # rendered chip slots non-overlapping
            # (Kariyer / MC Yengeç / Ay 9. ev İkizler) and gives the
            # bespoke body opener clean inputs to work from.
            "proof_raw": "MC Yengeç",
            "chips": ["Ay 9. ev İkizler", "Anlatma"],
            "scene": "Görünür olduğunda insanlara sadece bilgi değil, güven hissi de vermek.",
            "salience": 0.9,
            "confidence": 0.93,
            "primary_anchor": _support_anchor("10th house ruler route", "house:10->ruler:Moon->house:9", 0.93, source_type="ruler_route"),
            "supporting_combo": [
                _support_anchor("Moon in Gemini 9H", "planet:Moon:sign:Gemini:house:9", 0.86, source_type="placement"),
            ],
        },
        {
            "match_id": "saturn_taurus_8h_steady_public_maturity",
            "forced_domain": "career",
            "variant_suffix": "chart_exact",
            "title": "Yavaş olgunlaşan dayanıklılık",
            "proof_raw": "Satürn · 8. ev · Boğa",
            "chips": ["Satürn 8. ev", "Boğa", "Public maturity"],
            "scene": "Görünür olmadan önce temelin sağlam olduğundan emin olmak.",
            "salience": 0.84,
            "confidence": 0.9,
            "primary_anchor": _support_anchor("Saturn in Taurus 8H", "planet:Saturn:sign:Taurus:house:8", 0.9, source_type="placement"),
            "supporting_combo": [],
        },
        {
            "match_id": "sun_opposite_jupiter_service_expansion_tension",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Fayda ile büyüme arasında gerilim",
            "proof_raw": "Güneş karşıt Jüpiter",
            "chips": ["Güneş karşıt Jüpiter", "Sınır ve genişleme"],
            "scene": "Bir işi küçük tutman gerekirken onu büyütmek istemek.",
            "salience": 0.78,
            "confidence": 0.88,
            "primary_anchor": _support_anchor("Sun opposition Jupiter", "Sun:Jupiter:opposition", 0.88, source_type="aspect"),
            "supporting_combo": [],
        },
        {
            "match_id": "neptune_4h_soft_inner_presence",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Yumuşak iç dünya, sezgisel varlık",
            "proof_raw": "Neptün · 4. ev",
            "chips": ["Neptün 4. ev", "Sezgisel varlık"],
            "scene": "Bir ortama girdiğinde insanların senin yumuşak veya sakinleştirici tarafını hissetmesi.",
            "salience": 0.78,
            "confidence": 0.88,
            "primary_anchor": _support_anchor("Neptune in house 4", "planet:Neptune:house:4", 0.88, source_type="placement"),
            "supporting_combo": [],
        },
        # ---- v0.4 addendum (additive) ----
        {
            "match_id": "gemini_asc_venus_1h_social_relational_presence",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Sosyal ve ilişkisel ilk izlenim",
            "proof_raw": "Yükselen · İkizler · Venüs 1. ev",
            "chips": ["Yükselen İkizler", "Venüs 1. ev", "İkizler"],
            "scene": "Bir ortama girdiğinde hızlıca temas kuracak bir ton bulmak.",
            "salience": 0.9,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("Ascendant Gemini", "planet:Ascendant:sign:Gemini", 0.94, source_type="angle"),
            "supporting_combo": [
                _support_anchor("Venus in Gemini 1H", "planet:Venus:sign:Gemini:house:1", 0.92, source_type="placement"),
                _support_anchor("Venus trine Mars", "Venus:Mars:trine", 0.82, source_type="aspect"),
            ],
        },
        {
            "match_id": "sun_aries_12h_hidden_private_fire",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "İçeride çalışan özel ateş",
            "proof_raw": "Güneş · 12. ev · Koç",
            "chips": ["Güneş 12. ev", "Koç", "Özel ateş"],
            "scene": "Bir şeye gerçekten yönelmeden önce bunu uzun süre kendi içinde taşımak.",
            "salience": 0.88,
            "confidence": 0.93,
            "primary_anchor": _support_anchor("Sun in Aries 12H", "planet:Sun:sign:Aries:house:12", 0.93, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Sun square Jupiter", "Sun:Jupiter:square", 0.78, source_type="aspect"),
                _support_anchor("Sun square Pluto", "Sun:Pluto:square", 0.8, source_type="aspect"),
            ],
        },
        {
            "match_id": "aquarius_mc_mars_conjunct_mc_visible_freedom_drive",
            "forced_domain": "career",
            "variant_suffix": "chart_exact",
            "title": "Kariyerde görünür hareket ve özgürlük",
            "proof_raw": "MC Kova · Mars kavuşum MC",
            "chips": ["MC Kova", "Mars kavuşum MC", "Uranüs kare MC"],
            "scene": "Bir işte beklemekten çok harekete geçerek yol açmak istemek.",
            "salience": 0.92,
            "confidence": 0.95,
            "primary_anchor": _support_anchor("Mars conjunct Midheaven", "Mars:Midheaven:conjunction", 0.95, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Uranus square Midheaven", "Uranus:Midheaven:square", 0.9, source_type="aspect"),
                _support_anchor("Mars in Aquarius 10H", "planet:Mars:sign:Aquarius:house:10", 0.9, source_type="placement"),
            ],
        },
        {
            "match_id": "venus_trine_mars_relational_attraction_signal",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "Yakınlıkta sıcak çekim",
            "proof_raw": "Venüs üçgen Mars",
            "chips": ["Venüs üçgen Mars", "Çekim", "Sıcak yaklaşım"],
            "scene": "Birine yaklaşırken bunu yalnızca sözle değil tonunla ve enerjinle de hissettirmek.",
            "salience": 0.86,
            "confidence": 0.92,
            "primary_anchor": _support_anchor("Venus trine Mars", "Venus:Mars:trine", 0.92, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Venus in Gemini 1H", "planet:Venus:sign:Gemini:house:1", 0.82, source_type="placement"),
            ],
        },
        {
            "match_id": "venus_trine_saturn_trust_bond",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "Yakınlıkta güven ve sadakat",
            "proof_raw": "Venüs üçgen Satürn",
            "chips": ["Venüs üçgen Satürn", "Güven", "Tutarlılık"],
            "scene": "Bir bağın sadece heyecanlı değil, güvenilir de olmasına önem vermek.",
            "salience": 0.88,
            "confidence": 0.93,
            "primary_anchor": _support_anchor("Venus trine Saturn", "Venus:Saturn:trine", 0.93, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Saturn in Aquarius 9H", "planet:Saturn:sign:Aquarius:house:9", 0.82, source_type="placement"),
            ],
        },
        {
            "match_id": "moon_scorpio_6h_emotional_routine_sensitivity",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "Günlük ritimde yoğun duygusal hassasiyet",
            "proof_raw": "Ay · 6. ev · Akrep",
            "chips": ["Ay 6. ev", "Akrep", "Duygusal ritim"],
            "scene": "Rutinindeki küçük bir değişimin içeride sandığından daha çok yer kaplaması.",
            "salience": 0.84,
            "confidence": 0.91,
            "primary_anchor": _support_anchor("Moon in Scorpio 6H", "planet:Moon:sign:Scorpio:house:6", 0.91, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Moon trine Neptune", "Moon:Neptune:trine", 0.84, source_type="aspect"),
                _support_anchor("Moon sextile Pluto", "Moon:Pluto:sextile", 0.8, source_type="aspect"),
            ],
        },
        {
            "match_id": "mercury_sextile_9h_capricorn_aquarius_intellectual_authority",
            "forced_domain": "mind",
            "variant_suffix": "chart_exact",
            "title": "İnançta ve fikirde zihinsel otorite",
            "proof_raw": "Merkür sekstil Jüpiter/Satürn/Plüton · 9. ev stelyumu",
            "chips": ["Merkür sekstil Jüpiter", "Merkür sekstil Satürn", "9. ev omurgası"],
            "scene": "Bir düşünceyi daha büyük bir çerçeveye oturtmadan rahatlayamamak.",
            "salience": 0.9,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("Mercury sextile Saturn", "Mercury:Saturn:sextile", 0.94, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Mercury sextile Jupiter", "Mercury:Jupiter:sextile", 0.9, source_type="aspect"),
                _support_anchor("Mercury sextile Pluto", "Mercury:Pluto:sextile", 0.9, source_type="aspect"),
                _support_anchor("Jupiter Saturn Pluto in 9H", "planets:Jupiter,Saturn,Pluto:house:9", 0.88, source_type="placement"),
            ],
        },
    ]
    variants.extend(_v0_5_chart_signature_variants())
    variants.extend(_v0_7_chart_signature_variants())
    variants.extend(_v0_8_chart_signature_variants())
    out: list[dict[str, Any]] = []
    for variant in variants:
        match_id = str(variant.get("match_id") or "").strip()
        match = registry_entries.get(match_id)
        if not isinstance(match, Mapping):
            continue
        if not _chart_variant_supported(
            variant=variant,
            planet_map=planet_map,
            aspects=aspect_entries,
            house_rulers=house_rulers,
            dominant_loops=dominant_loops,
            dominant_planet_names=dominant_planet_names,
        ):
            continue
        scored_match = dict(match)
        scored_match["score"] = _chart_variant_match_score(variant=variant, aspects=aspect_entries)
        seed = {
            "id": f"chart_seed::{match_id}::{variant.get('forced_domain') or 'generic'}",
            "title": str(variant.get("title") or match_id),
            "subtitle": str(match.get("direct_meaning") or ""),
            "body": _chart_seed_body(match=match, variant=variant),
            "micro": str(variant.get("scene") or ""),
            "proof_raw": str(variant.get("proof_raw") or ""),
            "chips": list(variant.get("chips") or []),
            "detail_blocks": [str(variant.get("scene") or "")] if str(variant.get("scene") or "").strip() else [],
            "category_support": {
                "support_version": "natal_promise_chart_signature_v1",
                "family": str(variant.get("forced_domain") or ""),
                "category_id": f"chart_signature::{match_id}::{variant.get('variant_suffix') or 'base'}",
                "primary_anchor": dict(variant.get("primary_anchor") or {}),
                "supporting_combo": [dict(item) for item in (variant.get("supporting_combo") or []) if isinstance(item, Mapping)],
                "hidden_support": [dict(item) for item in (variant.get("hidden_support") or []) if isinstance(item, Mapping)],
                "contradiction_signature": dict(variant.get("contradiction_signature") or {}),
                "repeated_motifs": [dict(item) for item in (variant.get("repeated_motifs") or []) if isinstance(item, Mapping)],
                "salience": _safe_float(variant.get("salience"), 0.78),
                "confidence": _safe_float(variant.get("confidence"), 0.88),
            },
        }
        candidate = _build_candidate(
            seed=seed,
            thread=None,
            registry_entries=registry_entries,
            locale=locale,
            auxiliary=False,
            forced_matches=[scored_match],
            forced_domain=str(variant.get("forced_domain") or ""),
            variant_suffix=str(variant.get("variant_suffix") or ""),
        )
        if candidate:
            meta = dict(candidate.get("meta")) if isinstance(candidate.get("meta"), Mapping) else {}
            meta["inventory_variant"] = "chart_signature"
            meta["match_id"] = match_id
            candidate["meta"] = meta
            out.append(candidate)
    return out


def _build_v0_6_discovery_candidates(
    *,
    planets: Sequence[Mapping[str, Any]] | None,
    aspects: Sequence[Mapping[str, Any]] | None,
    natal_graph_compact: Mapping[str, Any] | None,
    locale: str,
    existing_candidates: Sequence[Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    planet_map = {
        str(item.get("planet") or item.get("name") or "").strip().lower(): dict(item)
        for item in planets or []
        if isinstance(item, Mapping) and str(item.get("planet") or item.get("name") or "").strip()
    }
    if not planet_map:
        return []
    house_rulers = (
        natal_graph_compact.get("house_rulers")
        if isinstance(natal_graph_compact, Mapping) and isinstance(natal_graph_compact.get("house_rulers"), Mapping)
        else {}
    )
    existing_ids = {
        str(item.get("id") or "").strip().lower()
        for item in existing_candidates or []
        if isinstance(item, Mapping) and str(item.get("id") or "").strip()
    }
    exact_chart_ids = {
        packet_id
        for packet_id in existing_ids
        if "chart_exact" in packet_id and not packet_id.startswith("discovery_")
    }
    if len(exact_chart_ids) >= 8:
        return []
    out: list[dict[str, Any]] = []

    asc_sign = _asc_sign(metadata_like=planet_map, house_rulers=house_rulers)
    dsc_sign = _house_cusp_sign(house_rulers, 7)
    mc_sign = _house_cusp_sign(house_rulers, 10)
    ic_sign = _house_cusp_sign(house_rulers, 4)
    sun_item = _lookup_planet_entry(planet_map, "sun")
    moon_item = _lookup_planet_entry(planet_map, "moon")
    mercury_item = _lookup_planet_entry(planet_map, "mercury")
    venus_item = _lookup_planet_entry(planet_map, "venus")
    mars_item = _lookup_planet_entry(planet_map, "mars")

    if (
        asc_sign
        and sun_item
        and not _candidate_ids_contain(
            existing_ids,
            "asc_",
            "chart_ruler",
            "hidden_value_identity",
            "warm_visibility_belonging",
            "self_construction",
            "collective_identity",
        )
    ):
        chart_ruler = _sign_ruler(asc_sign)
        ruler_item = _lookup_planet_entry(planet_map, chart_ruler) if chart_ruler else {}
        if ruler_item:
            out.append(
                _build_discovery_packet(
                    packet_id="discovery_identity_asc_chart_ruler_sun_composed",
                    domain="identity",
                    promise_type="identity_style",
                    strength=0.72 + (0.03 if int(ruler_item.get("house") or 0) in {1, 10, 11} else 0.0),
                    title="Kimlik hattı aday keşfi",
                    direct_meaning="Yükselen, yönetici gezegen ve Güneş birlikte temel kimlik hattını taşıyor.",
                    lived_scene="Kimliğin yalnızca tek bir temadan değil; yükselenin, yöneticin ve Güneş hattının birlikte çalışmasından kuruluyor.",
                    gift="Kimlik hattının ana omurgasını daha net ayırabilmek.",
                    shadow="Mevcut registry bu kimlik kombinasyonunu henüz doğrudan sahiplenmiyor olabilir.",
                    growth="ASC-yönetici-Güneş zincirini daha spesifik arketiplere ayırmak.",
                    technical_anchors=[
                        f"ASC {asc_sign.title()}",
                        _planet_chip(chart_ruler, ruler_item),
                        _planet_chip("sun", sun_item),
                    ],
                    evidence_ids=[
                        f"discovery:identity:asc:{asc_sign}",
                        f"discovery:identity:ruler:{chart_ruler}:{int(ruler_item.get('house') or 0)}",
                        f"discovery:identity:sun:{str(sun_item.get('sign') or '').strip().lower()}:{int(sun_item.get('house') or 0)}",
                    ],
                    locale=locale,
                    discovery_domain="identity",
                    discovery_kind="composed_candidate",
                    coverage_topic="identity_route",
                )
            )

    relationship_support = 0.0
    if dsc_sign:
        relationship_support += 0.34
    relationship_ruler = _sign_ruler(dsc_sign)
    relationship_ruler_item = _lookup_planet_entry(planet_map, relationship_ruler) if relationship_ruler else {}
    if relationship_ruler_item:
        relationship_support += 0.24
    if any(int((item or {}).get("house") or 0) in {5, 7, 8, 12} for item in (venus_item, mars_item, moon_item)):
        relationship_support += 0.18
    if _has_any_aspect(aspects, [("Moon", "Venus"), ("Venus", "Mars"), ("Moon", "Pluto"), ("Venus", "Pluto"), ("Venus", "Jupiter")]):
        relationship_support += 0.14
    if (
        relationship_support >= 0.58
        and not _candidate_ids_contain(
            existing_ids,
            "dsc_",
            "trust_",
            "harmony_wound_depth",
            "relationship_power_depth",
            "affection_gift",
            "private_love",
            "attraction_signal",
            "trust_bond",
            "freedom_responsibility_sensitivity",
        )
    ):
        out.append(
            _build_discovery_packet(
                packet_id="discovery_relationship_dsc_ruler_signature_composed",
                domain="relationship",
                promise_type="relationship_need",
                strength=min(0.86, 0.62 + relationship_support * 0.18),
                title="İlişki hattı aday keşfi",
                direct_meaning="DSC, yöneticisi ve ilişki imzaları birlikte ayrı bir ilişki hattı kuruyor.",
                lived_scene="İlişkilerde denge, eşik, yakınlık ve güven dili sadece tek bir Venüs cümlesine indirgenemeyebilir.",
                gift="İlişki hattını DSC-yönetici-imza kombinasyonuyla daha doğru okumak.",
                shadow="Mevcut registry bu ilişki kombinasyonunu henüz yeterince ayrıştırmıyor olabilir.",
                growth="DSC, yönetici gezegen ve ilişki imzalarını ayrı bir packet ailesine dönüştürmek.",
                technical_anchors=[
                    f"DSC {dsc_sign.title()}" if dsc_sign else "",
                    _planet_chip(relationship_ruler, relationship_ruler_item),
                    _planet_chip("venus", venus_item),
                    _planet_chip("moon", moon_item),
                ],
                evidence_ids=[
                    f"discovery:relationship:dsc:{dsc_sign}",
                    f"discovery:relationship:ruler:{relationship_ruler}:{int((relationship_ruler_item or {}).get('house') or 0)}",
                ]
                + _relationship_signature_evidence(aspects=aspects, venus_item=venus_item, mars_item=mars_item, moon_item=moon_item),
                locale=locale,
                discovery_domain="relationship",
                discovery_kind="composed_candidate",
                coverage_topic="relationship_route",
            )
        )

    career_support = 0.0
    if mc_sign:
        career_support += 0.34
    career_ruler = _sign_ruler(mc_sign)
    career_ruler_item = _lookup_planet_entry(planet_map, career_ruler) if career_ruler else {}
    if career_ruler_item:
        career_support += 0.24
    tenth_house_planets = _house_planet_names(planet_map, 10)
    if tenth_house_planets:
        career_support += min(0.24, 0.08 * len(tenth_house_planets))
    if (
        career_support >= 0.58
        and not _candidate_ids_contain(
            existing_ids,
            "mc_",
            "public_voice",
            "public_style",
            "invisible_preparation",
            "steady_public_drive",
            "public_power_roots_tension",
            "healing_voice",
        )
    ):
        out.append(
            _build_discovery_packet(
                packet_id="discovery_career_mc_ruler_tenth_house_composed",
                domain="career",
                promise_type="career_signature",
                strength=min(0.88, 0.62 + career_support * 0.18),
                title="Kariyer hattı aday keşfi",
                direct_meaning="MC, yöneticisi ve 10. ev yerleşimleri birlikte kariyer/public rol hattı kuruyor.",
                lived_scene="Görünür rol, kariyer dili ve dış dünyadaki konum birden fazla teknik imzayla taşınıyor olabilir.",
                gift="Kariyer hattını MC-yönetici-10. ev birlikte okumak.",
                shadow="Mevcut registry bu kariyer imzasını henüz tek bir spesifik packet altında toplamıyor olabilir.",
                growth="MC yöneticisi ve 10. ev yığılmalarını daha spesifik packet ailelerine ayırmak.",
                technical_anchors=[
                    f"MC {mc_sign.title()}" if mc_sign else "",
                    _planet_chip(career_ruler, career_ruler_item),
                    *[f"{planet.title()} · 10. ev" for planet in tenth_house_planets[:3]],
                ],
                evidence_ids=[
                    f"discovery:career:mc:{mc_sign}",
                    f"discovery:career:ruler:{career_ruler}:{int((career_ruler_item or {}).get('house') or 0)}",
                    *[f"discovery:career:10h:{planet}" for planet in tenth_house_planets[:4]],
                ],
                locale=locale,
                discovery_domain="career",
                discovery_kind="composed_candidate",
                coverage_topic="career_route",
            )
        )

    emotional_anchors = [_planet_chip("moon", moon_item)]
    emotional_evidence = [
        f"discovery:emotional:moon:{str((moon_item or {}).get('sign') or '').strip().lower()}:{int((moon_item or {}).get('house') or 0)}"
    ] if moon_item else []
    if moon_item and not _candidate_ids_contain(existing_ids, "home_security_roots", "private_emotional", "emotional_routine_sensitivity", "moon_"):
        moon_house = int(moon_item.get("house") or 0)
        if moon_house in {3, 4} and ic_sign:
            emotional_anchors.append(f"IC {ic_sign.title()}")
            emotional_evidence.append(f"discovery:emotional:ic:{ic_sign}")
        for aspect_entry in _top_aspect_refs(aspects, planet="Moon", limit=2):
            emotional_anchors.append(aspect_entry["label"])
            emotional_evidence.append(aspect_entry["ref"])
        emotional_domain = "home_family" if moon_house in {3, 4} else "emotional_world"
        emotional_type = "emotional_home_signature" if emotional_domain == "home_family" else "need"
        out.append(
            _build_discovery_packet(
                packet_id="discovery_emotional_moon_signature_composed",
                domain=emotional_domain,
                promise_type=emotional_type,
                strength=0.7 + (0.05 if moon_house in {3, 4, 5, 8, 12} else 0.0),
                title="Duygusal ritim aday keşfi",
                direct_meaning="Ay'ın yerleşimi ve açıları ayrı bir duygusal ritim hattı taşıyor.",
                lived_scene="Duygusal ritim, yalnızca genel bir ilişki ya da kariyer fallback'i altında kalmaması gereken bağımsız bir eksen olabilir.",
                gift="Ay imzasını doğrudan aday envantere taşımak.",
                shadow="Mevcut registry Ay hattını bu kombinasyonda yeterince spesifik işlemiyor olabilir.",
                growth="Ay burç/ev/açı kombinasyonlarını daha net packet ailelerine ayırmak.",
                technical_anchors=emotional_anchors,
                evidence_ids=emotional_evidence,
                locale=locale,
                discovery_domain="emotional",
                discovery_kind="composed_candidate",
                coverage_topic="moon_signature",
            )
        )

    mercury_aspect_refs = _top_aspect_refs(aspects, planet="Mercury", limit=2)
    mind_support = 0.0
    if mercury_item:
        mind_support += 0.34
        if int(mercury_item.get("house") or 0) in {3, 9}:
            mind_support += 0.18
    if any(_planet_in_house(planet_map, name, 3) or _planet_in_house(planet_map, name, 9) for name in ("sun", "mercury", "jupiter", "pluto")):
        mind_support += 0.14
    if mercury_aspect_refs:
        mind_support += 0.16
    if _planet_has_major_aspect(aspects, "Uranus", "Mercury"):
        mind_support += 0.08
    if (
        mercury_item
        and mind_support >= 0.56
        and not _candidate_ids_contain(
            existing_ids,
            "mind_",
            "social_emotional_intelligence",
            "speech_decision_language",
            "deep_speech",
            "social_intuition_mind",
            "deep_mind_pressure",
            "big_mind",
            "public_voice_strategic_mind",
        )
    ):
        out.append(
            _build_discovery_packet(
                packet_id="discovery_mind_mercury_axis_composed",
                domain="mind",
                promise_type="mind_style",
                strength=min(0.86, 0.62 + mind_support * 0.18),
                title="Zihin hattı aday keşfi",
                direct_meaning="Merkür, 3H/9H ekseni ve baskın açıları birlikte ayrı bir zihin hattı kuruyor.",
                lived_scene="Zihin tonu, öğrenme biçimi ve karar dili yalnızca genel bir mind fallback'i altında kalmaması gereken kadar belirgin olabilir.",
                gift="Merkür eksenini bağımsız aday envantere taşımak.",
                shadow="Mevcut registry bu zihinsel kombinasyonu henüz yeterince spesifik paketlemiyor olabilir.",
                growth="Merkür-3H/9H-Uranüs/açı kombinasyonlarını daha net packet ailelerine ayırmak.",
                technical_anchors=[
                    _planet_chip("mercury", mercury_item),
                    *[item["label"] for item in mercury_aspect_refs],
                ],
                evidence_ids=[
                    f"discovery:mind:mercury:{str(mercury_item.get('sign') or '').strip().lower()}:{int(mercury_item.get('house') or 0)}",
                    *[item["ref"] for item in mercury_aspect_refs],
                ],
                locale=locale,
                discovery_domain="mind",
                discovery_kind="composed_candidate",
                coverage_topic="mercury_signature",
            )
        )

    active_houses = _significant_house_counts(planet_map)
    if (
        active_houses.get(4, 0) >= 2
        and not _candidate_ids_contain(existing_ids, "home_security_roots", "roots_inner_security", "private_emotional")
    ):
        out.append(
            _build_discovery_packet(
                packet_id="discovery_house_4h_ic_concentration_gap",
                domain="home_family",
                promise_type="home_family_signature",
                strength=0.7 + min(0.1, 0.03 * active_houses.get(4, 0)),
                title="4H/IC yoğunluğu kapsama boşluğu",
                direct_meaning="4. ev/IC yoğunluğu var ama buna sahip çıkan yeterince spesifik bir packet görünmüyor.",
                lived_scene="Ev, kökler ve iç güvenlik hattı bu chartta ayrı bir kapsama isteyebilir.",
                gift="4. ev/IC yoğunluğunu debug seviyesinde görünür kılmak.",
                shadow="Bu eksen generic fallback altında eriyebilir.",
                growth="4H/IC yoğunlukları için daha kaliteli arketip ailesi eklemek.",
                technical_anchors=[
                    f"IC {ic_sign.title()}" if ic_sign else "",
                    *[f"{planet.title()} · 4. ev" for planet in _house_planet_names(planet_map, 4)[:3]],
                ],
                evidence_ids=[
                    f"discovery:house:4:count:{active_houses.get(4, 0)}",
                    *[f"discovery:house:4:{planet}" for planet in _house_planet_names(planet_map, 4)[:4]],
                ],
                locale=locale,
                discovery_domain="emotional",
                discovery_kind="coverage_gap",
                coverage_topic="house_4h_ic",
            )
        )
    if active_houses.get(5, 0) >= 2 and not _candidate_ids_contain(existing_ids, "5h", "structured_imagination", "serious_heart_creative_form"):
        out.append(
            _build_discovery_packet(
                packet_id="discovery_house_5h_concentration_gap",
                domain="creativity",
                promise_type="creative_signature",
                strength=0.68 + min(0.1, 0.03 * active_houses.get(5, 0)),
                title="5H yoğunluğu kapsama boşluğu",
                direct_meaning="5. ev yoğunluğu var ama buna sahip çıkan yeterince spesifik bir packet görünmüyor.",
                lived_scene="Yaratıcılık, romantik ifade ve oyun alanı chartta daha belirgin olabilir.",
                gift="5. ev yoğunluğunu debug seviyesinde görünür kılmak.",
                shadow="5H yoğunluğu generic relationship ya da mind fallback'ine dağılabilir.",
                growth="5H yoğunlukları için daha kaliteli arketip ailesi eklemek.",
                technical_anchors=[f"{planet.title()} · 5. ev" for planet in _house_planet_names(planet_map, 5)[:4]],
                evidence_ids=[
                    f"discovery:house:5:count:{active_houses.get(5, 0)}",
                    *[f"discovery:house:5:{planet}" for planet in _house_planet_names(planet_map, 5)[:4]],
                ],
                locale=locale,
                discovery_domain="emotional",
                discovery_kind="coverage_gap",
                coverage_topic="house_5h",
            )
        )
    if active_houses.get(12, 0) >= 2 and not _candidate_ids_contain(existing_ids, "12h", "private_pressure", "inner_world_saturation", "private_maturity", "hidden_action", "private_will"):
        out.append(
            _build_discovery_packet(
                packet_id="discovery_house_12h_concentration_gap",
                domain="inner_world",
                promise_type="need",
                strength=0.7 + min(0.1, 0.03 * active_houses.get(12, 0)),
                title="12H yoğunluğu kapsama boşluğu",
                direct_meaning="12. ev yoğunluğu var ama buna sahip çıkan yeterince spesifik bir packet görünmüyor.",
                lived_scene="İç dünya, perde arkası hazırlık veya görünmeyen süreçler chartta daha fazla yer tutabilir.",
                gift="12. ev yoğunluğunu debug seviyesinde görünür kılmak.",
                shadow="12H içeriği generic shadow ya da career fallback'ine dağılabilir.",
                growth="12H yoğunlukları için daha kaliteli arketip ailesi eklemek.",
                technical_anchors=[f"{planet.title()} · 12. ev" for planet in _house_planet_names(planet_map, 12)[:4]],
                evidence_ids=[
                    f"discovery:house:12:count:{active_houses.get(12, 0)}",
                    *[f"discovery:house:12:{planet}" for planet in _house_planet_names(planet_map, 12)[:4]],
                ],
                locale=locale,
                discovery_domain="emotional",
                discovery_kind="coverage_gap",
                coverage_topic="house_12h",
            )
        )
    if _axis_support(planet_map, left=2, right=8) >= 1.2:
        out.append(
            _build_discovery_packet(
                packet_id="discovery_axis_2h_8h_gap",
                domain="money_self_worth",
                promise_type="need",
                strength=0.72,
                title="2H/8H ekseni kapsama boşluğu",
                direct_meaning="2H/8H ekseni aktif ama buna sahip çıkan yeterince spesifik bir packet görünmüyor.",
                lived_scene="Değer, paylaşım, kaynak ve derin bağ ekseni chartta bağımsız bir okuma isteyebilir.",
                gift="2H/8H eksenini debug seviyesinde görünür kılmak.",
                shadow="Bu eksen generic relationship ya da career fallback'ine dağılabilir.",
                growth="2H/8H ekseni için daha kaliteli arketip ailesi eklemek.",
                technical_anchors=[
                    *[f"{planet.title()} · 2. ev" for planet in _house_planet_names(planet_map, 2)[:2]],
                    *[f"{planet.title()} · 8. ev" for planet in _house_planet_names(planet_map, 8)[:3]],
                ],
                evidence_ids=[
                    f"discovery:axis:2h8h:left:{active_houses.get(2, 0)}",
                    f"discovery:axis:2h8h:right:{active_houses.get(8, 0)}",
                ],
                locale=locale,
                discovery_domain="relationship",
                discovery_kind="coverage_gap",
                coverage_topic="axis_2h_8h",
            )
        )
    if _axis_support(planet_map, left=3, right=9) >= 1.2:
        out.append(
            _build_discovery_packet(
                packet_id="discovery_axis_3h_9h_gap",
                domain="mind",
                promise_type="mind_style",
                strength=0.72,
                title="3H/9H ekseni kapsama boşluğu",
                direct_meaning="3H/9H ekseni aktif ama buna sahip çıkan yeterince spesifik bir packet görünmüyor.",
                lived_scene="Öğrenme, anlatım, fikir kurma ve perspektif hattı chartta ayrı bir okuma isteyebilir.",
                gift="3H/9H eksenini debug seviyesinde görünür kılmak.",
                shadow="Bu eksen generic career ya da relationship fallback'ine dağılabilir.",
                growth="3H/9H ekseni için daha kaliteli arketip ailesi eklemek.",
                technical_anchors=[
                    *[f"{planet.title()} · 3. ev" for planet in _house_planet_names(planet_map, 3)[:2]],
                    *[f"{planet.title()} · 9. ev" for planet in _house_planet_names(planet_map, 9)[:3]],
                ],
                evidence_ids=[
                    f"discovery:axis:3h9h:left:{active_houses.get(3, 0)}",
                    f"discovery:axis:3h9h:right:{active_houses.get(9, 0)}",
                ],
                locale=locale,
                discovery_domain="mind",
                discovery_kind="coverage_gap",
                coverage_topic="axis_3h_9h",
            )
        )

    out.extend(
        _build_discovery_aspect_candidates(
            aspects=aspects,
            existing_ids=existing_ids,
            locale=locale,
        )
    )
    return [packet for packet in out if packet.get("id")]


def _build_discovery_packet(
    *,
    packet_id: str,
    domain: str,
    promise_type: str,
    strength: float,
    title: str,
    direct_meaning: str,
    lived_scene: str,
    gift: str,
    shadow: str,
    growth: str,
    technical_anchors: Sequence[str],
    evidence_ids: Sequence[str],
    locale: str,
    discovery_domain: str,
    discovery_kind: str,
    coverage_topic: str,
) -> dict[str, Any]:
    return {
        "id": packet_id,
        "theme_key": packet_id,
        "domain": domain,
        "promise_type": promise_type,
        "source_type": "discovery_scaffold",
        "strength": round(max(0.01, min(0.95, strength)), 4),
        "technical_anchors": [str(item).strip() for item in technical_anchors if str(item).strip()],
        "source_evidence_ids": [str(item).strip() for item in evidence_ids if str(item).strip()],
        "direct_meaning": direct_meaning,
        "lived_scene": lived_scene,
        "gift": gift,
        "shadow_or_friction": shadow,
        "inner_tension": shadow,
        "growth_direction": growth,
        "voice_seeds": [direct_meaning],
        "avoid_phrases": sorted(_BANNED_PHRASES),
        "source_category_ids": [packet_id],
        "source_thread_ids": [],
        "source_section_ids": [packet_id],
        "projection_hints": {
            "surfaces": ["debug_only"],
            "priority": round(max(0.01, min(0.95, strength)), 4),
            "auxiliary": False,
            "opening_strategy": "debug_only",
        },
        "scoring_breakdown": {
            "discovery_v0_6": round(max(0.01, min(0.95, strength)), 4),
            "coverage_gap": 1.0 if discovery_kind == "coverage_gap" else 0.0,
        },
        "matched_archetypes": [],
        "matched_archetype_summaries": [],
        "meta": {
            "title": title,
            "locale": locale,
            "auxiliary": False,
            "variant_suffix": "discovery_v0_6",
            "inventory_variant": "discovery_v0_6",
            "v0_6_discovery": True,
            "non_public_discovery": True,
            "debug_only": True,
            "source_type": "discovery_scaffold",
            "discovery_kind": discovery_kind,
            "discovery_domain": discovery_domain,
            "coverage_topic": coverage_topic,
        },
    }


def _build_v0_9_composed_semantic_candidates(
    *,
    planets: Sequence[Mapping[str, Any]] | None,
    aspects: Sequence[Mapping[str, Any]] | None,
    natal_graph_compact: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
    meta_info: Mapping[str, Any] | None,
    locale: str,
    existing_candidates: Sequence[Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    planet_map = {
        str(item.get("planet") or item.get("name") or "").strip().lower(): dict(item)
        for item in planets or []
        if isinstance(item, Mapping) and str(item.get("planet") or item.get("name") or "").strip()
    }
    if not planet_map:
        return []
    house_rulers = (
        natal_graph_compact.get("house_rulers")
        if isinstance(natal_graph_compact, Mapping) and isinstance(natal_graph_compact.get("house_rulers"), Mapping)
        else {}
    )
    existing_ids = {
        str(item.get("id") or "").strip().lower()
        for item in existing_candidates or []
        if isinstance(item, Mapping) and str(item.get("id") or "").strip()
    }
    out: list[dict[str, Any]] = []
    identity_candidate = _build_identity_route_candidates(
        planet_map=planet_map,
        aspects=aspects,
        house_rulers=house_rulers,
        locale=locale,
        existing_ids=existing_ids,
    )
    if identity_candidate:
        out.append(identity_candidate)
    career_candidate = _build_career_route_candidates(
        planet_map=planet_map,
        aspects=aspects,
        house_rulers=house_rulers,
        locale=locale,
        existing_ids=existing_ids,
    )
    if career_candidate:
        out.append(career_candidate)
    # v0.9b families — each gated by its own master flag (default false).
    # Both stay strictly debug-only in v0.9b.0; they do not enter any public
    # surface, do not widen the composed_detail_renderer allowlist, and do
    # not touch the registry.
    if _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_RELATIONSHIP_ROUTE_V0_9B"):
        relationship_candidate = _build_relationship_route_candidates(
            planet_map=planet_map,
            aspects=aspects,
            house_rulers=house_rulers,
            locale=locale,
            existing_ids=existing_ids,
        )
        if relationship_candidate:
            out.append(relationship_candidate)
            existing_ids.add(str(relationship_candidate.get("id") or "").strip().lower())
    if _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_MOON_SIGNATURE_V0_9B"):
        moon_candidate = _build_moon_signature_candidates(
            planet_map=planet_map,
            aspects=aspects,
            house_rulers=house_rulers,
            locale=locale,
            existing_ids=existing_ids,
        )
        if moon_candidate:
            out.append(moon_candidate)
            existing_ids.add(str(moon_candidate.get("id") or "").strip().lower())
    if _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_MERCURY_SIGNATURE_V0_9C"):
        mercury_candidate = _build_mercury_signature_candidates(
            planet_map=planet_map,
            aspects=aspects,
            house_rulers=house_rulers,
            locale=locale,
            existing_ids=existing_ids,
            career_candidate=career_candidate,
        )
        if mercury_candidate:
            out.append(mercury_candidate)
            existing_ids.add(str(mercury_candidate.get("id") or "").strip().lower())
    # v0.10 axis_2h_8h — flag-gated, debug-only first cut.
    if _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_AXIS_2H_8H_V0_10"):
        axis_candidate = _build_axis_2h_8h_candidates(
            planet_map=planet_map,
            aspects=aspects,
            house_rulers=house_rulers,
            locale=locale,
            existing_ids=existing_ids,
        )
        if axis_candidate:
            out.append(axis_candidate)
            existing_ids.add(str(axis_candidate.get("id") or "").strip().lower())
    _apply_v0_9b_cross_family_moon_ownership(out)
    return out


def _apply_v0_9b_cross_family_moon_ownership(candidates: list[dict[str, Any]]) -> None:
    """v0.9b.0.1 cross-family Moon ownership rule.

    When a ``relationship_route`` candidate consumed Moon evidence (i.e.
    its subtype is Moon-anchored — ``emotional_need_affection`` or
    ``intimacy_depth`` — and ``evidence_trace.cross_family_overlap`` is
    non-empty), AND a ``moon_signature`` candidate also exists on the
    same chart, compare confidences:

      * if ``moon.confidence >= relationship.confidence + 0.05`` → mark
        the relationship candidate as Moon-evidence-owned-by-moon. The
        candidate stays debug-visible in this v0.9b.0.1 pass; the
        metadata gates **future** renderer / detail eligibility, not the
        current trace emission.
      * otherwise → relationship retains ownership.

    The moon candidate always self-owns its evidence (it is the canonical
    Moon family).

    This is a metadata-only pass. No surface routing, scoring, or
    eligibility flag is mutated beyond the relationship card's
    ``public_eligibility.detail_eligible`` (which already defaults to
    False in v0.9b.0; we extend its ``reason_codes`` and add an explicit
    ``moon_evidence_owned_elsewhere`` block-tag so v0.9b.1+ renderer
    gates can refuse promotion).
    """
    relationship = next(
        (p for p in candidates if str(p.get("family") or "") == "relationship_route"),
        None,
    )
    moon = next(
        (p for p in candidates if str(p.get("family") or "") == "moon_signature"),
        None,
    )

    if moon is not None:
        moon_meta = moon.get("meta") if isinstance(moon.get("meta"), Mapping) else {}
        moon_meta = dict(moon_meta)
        moon_meta["moon_evidence_owned_by"] = "moon_signature"
        moon["meta"] = moon_meta

    if relationship is None:
        return

    trace = relationship.get("evidence_trace") if isinstance(relationship.get("evidence_trace"), Mapping) else {}
    overlap = trace.get("cross_family_overlap") if isinstance(trace.get("cross_family_overlap"), Sequence) else []
    relationship_consumes_moon = bool(overlap)
    rel_meta = dict(relationship.get("meta") if isinstance(relationship.get("meta"), Mapping) else {})

    if not relationship_consumes_moon:
        rel_meta["moon_evidence_owned_by"] = "relationship_route"
        relationship["meta"] = rel_meta
        return

    if moon is None:
        # Relationship trace claims Moon overlap but no moon_signature
        # candidate exists on this chart — relationship keeps ownership.
        rel_meta["moon_evidence_owned_by"] = "relationship_route"
        rel_meta["cross_family_moon_ownership_outcome"] = "relationship_solo"
        relationship["meta"] = rel_meta
        return

    rel_confidence = _safe_float(relationship.get("confidence"), 0.0)
    moon_confidence = _safe_float(moon.get("confidence"), 0.0)
    moon_wins = moon_confidence >= rel_confidence + 0.05

    if moon_wins:
        rel_meta["moon_evidence_owned_by"] = "moon_signature"
        rel_meta["cross_family_moon_ownership_outcome"] = "moon_takes_ownership"
        rel_meta["moon_ownership_confidence_delta"] = round(
            moon_confidence - rel_confidence, 4
        )
        # Future-eligibility block: keep current public_eligibility shape
        # (already debug-only in v0.9b.0) but mark the candidate so a
        # later renderer/detail gate can refuse it on this axis.
        elig = dict(relationship.get("public_eligibility") if isinstance(relationship.get("public_eligibility"), Mapping) else {})
        reason_codes = list(elig.get("reason_codes") or [])
        if "moon_evidence_owned_elsewhere" not in reason_codes:
            reason_codes.append("moon_evidence_owned_elsewhere")
        elig["reason_codes"] = reason_codes
        elig["future_renderer_eligibility_blocked"] = True
        # public_main / public_support / detail eligibility unchanged from
        # v0.9b.0 defaults — debug-only stays debug-only.
        elig.setdefault("detail_eligible", False)
        elig.setdefault("public_support_eligible", False)
        elig.setdefault("public_main_eligible", False)
        relationship["public_eligibility"] = elig
        # Mirror into meta.public_eligibility for the cluster plan ledger
        # path that reads from meta.
        meta_elig = dict(rel_meta.get("public_eligibility") or {})
        meta_elig.update(elig)
        rel_meta["public_eligibility"] = meta_elig
    else:
        rel_meta["moon_evidence_owned_by"] = "relationship_route"
        rel_meta["cross_family_moon_ownership_outcome"] = "relationship_retains_ownership"
        rel_meta["moon_ownership_confidence_delta"] = round(
            moon_confidence - rel_confidence, 4
        )

    relationship["meta"] = rel_meta


def _build_identity_route_candidates(
    *,
    planet_map: Mapping[str, Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]] | None,
    house_rulers: Mapping[str, Any],
    locale: str,
    existing_ids: set[str],
) -> dict[str, Any] | None:
    packet_id = "composed_identity_route_v0_9a"
    if packet_id in existing_ids:
        return None
    asc_sign = _asc_sign(metadata_like=planet_map, house_rulers=house_rulers)
    sun_item = _lookup_planet_entry(planet_map, "sun")
    if not asc_sign or not sun_item:
        return None
    chart_ruler = _sign_ruler(asc_sign)
    ruler_item = _lookup_planet_entry(planet_map, chart_ruler)
    if not chart_ruler or not ruler_item:
        return None
    asc_strength = 0.25 if asc_sign else 0.0
    ruler_house = int(ruler_item.get("house") or 0)
    sun_house = int(sun_item.get("house") or 0)
    ruler_strength = 0.2 + (0.1 if ruler_house in {1, 4, 7, 10, 11} else 0.0)
    sun_strength = 0.12 + (0.08 if sun_house in {1, 4, 7, 10, 11} else 0.0)
    first_house_amplification = min(0.1, 0.03 * len(_house_planet_names(planet_map, 1)))
    coherence_bonus = 0.05 if ruler_house in {1, 10, 11} or sun_house in {1, 10, 11} else 0.0
    confidence = round(min(0.94, asc_strength + ruler_strength + sun_strength + first_house_amplification + coherence_bonus), 4)
    if confidence < 0.6:
        return None
    if ruler_house in {7} or sun_house in {7}:
        subtype = "relational_identity_spine"
        lived_scene = "Kendini ortaya koyarken çoğu zaman tek başına değil, başkalarıyla kurduğun ilişki içinde pozisyon alıyorsun."
        atoms = [
            "bir ortama girerken karşı tarafın tonunu da hesaba katman",
            "kendini anlatırken ilişki dengesini korumaya çalışman",
        ]
    elif ruler_house in {4, 12} or sun_house in {4, 12}:
        subtype = "private_identity_spine"
        lived_scene = "Kimliğin dışarıya açık bir tavır kadar, içeride nasıl toparlandığın ve kendini nerede güvende hissettiğin üzerinden de kuruluyor."
        atoms = [
            "dışarıdan önce içeride toparlanman gereken an",
            "kendini göstermeden önce geri çekilip yönünü ayarlaman",
        ]
    elif ruler_house in {10} or sun_house in {10}:
        subtype = "controlled_identity_spine"
        lived_scene = "Kendini gösterme biçimin görünürlük, sorumluluk veya ciddiye alınma ihtiyacıyla birlikte çalışabiliyor."
        atoms = [
            "görünür olurken tonunu dikkatle ayarlaman",
            "kendini anlatırken aynı anda konumunu da koruman",
        ]
    elif ruler_house in {1, 5, 11} or sun_house in {1, 5, 11}:
        subtype = "direct_identity_spine"
        lived_scene = "Kendini ortaya koyarken yönün daha hızlı belirginleşiyor; tavrın dışarıda daha çabuk okunuyor."
        atoms = [
            "ilk tepkiyi verirken kendi tonunun hemen görünmesi",
            "bir grupta duruşunun hızlıca fark edilmesi",
        ]
    else:
        subtype = "mediated_identity_spine"
        lived_scene = "Kimlik hattın tek bir dış tavırdan değil, yöneticinin düştüğü hayat sahnesi üzerinden dolaylı biçimde kuruluyor."
        atoms = [
            "önce içinde tartıp sonra tavır alman",
            "kimliğinin doğrudan değil bir hayat alanı üzerinden görünmesi",
        ]
    direct_meaning = "ASC, yönetici gezegen ve Güneş birlikte kimlik hattını tek bir genel fallback'ten daha spesifik biçimde taşıyor."
    gift = "Kimlik çizgisini yalnız burç etiketiyle değil, gerçek yönlendiren rota üzerinden ayırabilmek."
    inner_tension = "Dışarıda görünen tavrınla, kimliğini gerçekten hangi yaşam sahnesinde kurduğun her zaman aynı yerden çalışmayabilir."
    growth = "Kimlik hattını yükselen, yönetici gezegen ve Güneş arasında kurulan omurgadan okumak."
    domain_reason = [
        "ASC route",
        "chart ruler route",
        "Sun identity anchor",
    ]
    if _house_planet_names(planet_map, 1):
        domain_reason.append("1H amplification")
    technical_anchors = [
        f"ASC {asc_sign.title()}",
        _planet_chip(chart_ruler, ruler_item),
        _planet_chip("sun", sun_item),
    ]
    source_evidence_ids = [
        f"composed:identity:asc:{asc_sign}",
        f"composed:identity:ruler:{chart_ruler}:{str(ruler_item.get('sign') or '').strip().lower()}:{ruler_house}",
        f"composed:identity:sun:{str(sun_item.get('sign') or '').strip().lower()}:{sun_house}",
    ]
    evidence_trace = {
        "primitive_facts": {
            "placements": [
                {"planet": "Sun", "sign": str(sun_item.get("sign") or ""), "house": sun_house},
                {"planet": chart_ruler.title(), "sign": str(ruler_item.get("sign") or ""), "house": ruler_house},
            ],
            "angles": [{"angle": "ASC", "sign": asc_sign.title()}],
        },
        "discovery_routes": ["identity_route"],
        "family_inputs": ["ASC", "chart_ruler", "Sun"],
        "subtype_inputs": [subtype],
    }
    return _composed_candidate_to_packet(
        ComposedSemanticCandidateV1(
            id=packet_id,
            family="identity_route",
            subtype=subtype,
            source_type="composed_semantic",
            domain="identity",
            promise_type="identity_style",
            domain_reason=domain_reason,
            public_job="debug_only",
            confidence=confidence,
            confidence_tier=_confidence_tier(confidence),
            chart_facts_match=True,
            technical_anchors=[item for item in technical_anchors if item],
            source_evidence_ids=source_evidence_ids,
            evidence_trace=evidence_trace,
            direct_meaning=direct_meaning,
            lived_scene=lived_scene,
            lived_scene_atoms=atoms,
            gift=gift,
            inner_tension=inner_tension,
            growth_direction=growth,
            avoid_readings=[
                "Do not reduce identity to ASC sign only.",
                "Do not let generic identity fallback own this route by default.",
            ],
            projection_hints={
                "surfaces": ["debug_only"],
                "priority": confidence,
                "auxiliary": False,
                "opening_strategy": "debug_only",
            },
            scoring_breakdown={
                "asc_strength": round(asc_strength, 4),
                "chart_ruler_strength": round(ruler_strength, 4),
                "sun_alignment_strength": round(sun_strength, 4),
                "first_house_amplification": round(first_house_amplification, 4),
                "coherence_bonus": round(coherence_bonus, 4),
            },
            matched_archetypes=[],
            public_eligibility={
                "debug_eligible": True,
                "detail_eligible": False,
                "public_support_eligible": False,
                "public_main_eligible": False,
                "reason_codes": ["v0_9a_debug_only", "public_main_flag_required"],
            },
            meta={
                "title": "Kimlik rotası composed semantic adayı",
                "locale": locale,
                "auxiliary": False,
                "inventory_variant": "composed_semantic_v0_9a",
                "v0_9_composed": True,
                "v0_9_family": "identity_route",
                "debug_only": True,
                "non_public_discovery": True,
                "source_type": "composed_semantic",
            },
        )
    )


def _build_career_route_candidates(
    *,
    planet_map: Mapping[str, Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]] | None,
    house_rulers: Mapping[str, Any],
    locale: str,
    existing_ids: set[str],
) -> dict[str, Any] | None:
    packet_id = "composed_career_route_v0_9a"
    if packet_id in existing_ids:
        return None
    mc_sign = _house_cusp_sign(house_rulers, 10)
    if not mc_sign:
        return None
    career_ruler = _sign_ruler(mc_sign)
    ruler_item = _lookup_planet_entry(planet_map, career_ruler)
    if not career_ruler or not ruler_item:
        return None
    tenth_house_planets = _house_planet_names(planet_map, 10)
    if not tenth_house_planets and int(ruler_item.get("house") or 0) not in {1, 10, 11, 12}:
        return None
    mc_strength = 0.25
    ruler_house = int(ruler_item.get("house") or 0)
    ruler_strength = 0.18 + (0.12 if ruler_house in {1, 10, 11, 12} else 0.0)
    tenth_support = min(0.2, 0.08 * len(tenth_house_planets))
    has_mercury_public_anchor = any(name in tenth_house_planets for name in ("mercury",)) or (
        career_ruler == "mercury" and ruler_house in {10, 11}
    )
    has_saturn_public_anchor = any(name in tenth_house_planets for name in ("saturn",)) or (
        career_ruler == "saturn" and ruler_house in {10, 11, 12}
    )
    has_creative_public_anchor = any(name in tenth_house_planets for name in ("venus", "neptune"))
    has_action_public_anchor = any(name in tenth_house_planets for name in ("mars",)) or (
        career_ruler == "mars" and ruler_house in {10, 11}
    )
    has_hidden_preparation_signature = ruler_house == 12 or any(
        _planet_in_house(planet_map, item, 12) for item in ("sun", "venus", "neptune", "saturn")
    )
    has_visible_career_anchor = bool(tenth_house_planets) or ruler_house in {10, 11}

    public_planet_support = 0.0
    subtype_specific_bonus = 0.0
    subtype_penalty = 0.0
    if has_mercury_public_anchor:
        subtype = "public_voice"
        public_planet_support += 0.14
        subtype_specific_bonus += 0.06
        lived_scene = "Dış dünyada yalnız ne yaptığın değil, nasıl konuştuğun ve nasıl konum aldığın da görünür hale geliyor."
        atoms = [
            "bir toplantıda söz aldığında tonunun ağırlık taşıması",
            "ne söylediğinin dışarıdaki rolünü güçlendirmesi",
        ]
    elif has_saturn_public_anchor:
        subtype = "authority_responsibility"
        public_planet_support += 0.14
        subtype_specific_bonus += 0.05
        lived_scene = "Sorumluluk aldığında veya görünür bir rol üstlendiğinde ciddiyetin ve yük taşıma biçimin öne çıkabiliyor."
        atoms = [
            "sorumluluk geldiğinde tonunun ciddileşmesi",
            "görünür olurken ağırlığı da üstlenmen",
        ]
    elif has_creative_public_anchor:
        subtype = "creative_visibility"
        public_planet_support += 0.14
        subtype_specific_bonus += 0.05
        lived_scene = "Görünür rolün yalnız işlevle değil, üslup, estetik ve algı yönetimiyle de kurulabiliyor."
        atoms = [
            "bir şeyi nasıl sunduğunun en az içeriği kadar önemli olması",
            "görünürlüğü biçim ve etkiyle birlikte taşıman",
        ]
    elif has_action_public_anchor:
        subtype = "action_initiative"
        public_planet_support += 0.14
        subtype_specific_bonus += 0.05
        lived_scene = "Kariyer hattında hareket, girişim ve dışarıda pozisyon alma biçimin daha belirgin çalışıyor."
        atoms = [
            "işte hamle yaparken görünür olman",
            "dış dünyada hızla pozisyon alman",
        ]
    elif has_hidden_preparation_signature and has_visible_career_anchor:
        subtype = "invisible_preparation_before_visibility"
        public_planet_support += 0.12
        subtype_specific_bonus += 0.06
        lived_scene = "Görünür rolünden önce uzun bir hazırlık, perde arkası işleme ya da içerde kurma ihtiyacı çalışabiliyor."
        atoms = [
            "bir işi göstermeden önce içeride uzun süre hazırlaman",
            "görünür olmadan önce zemini sessizce kurman",
        ]
    else:
        subtype = "strategic_role"
        public_planet_support += 0.02
        subtype_penalty += 0.05
        lived_scene = "Kariyer hattın yalnız görünürlük değil, nerede ve nasıl konum alacağını stratejik biçimde seçme ihtiyacını da taşıyor."
        atoms = [
            "hangi rolde görünmenin daha doğru olacağını tartman",
            "dışarıdaki konumunu stratejik biçimde kurman",
        ]
    coherence_bonus = 0.05 if ruler_house in {10, 11, 12} or len(tenth_house_planets) >= 2 else 0.0
    confidence = round(
        min(
            0.94,
            max(
                0.0,
                mc_strength
                + ruler_strength
                + tenth_support
                + public_planet_support
                + subtype_specific_bonus
                + coherence_bonus
                - subtype_penalty,
            ),
        ),
        4,
    )
    if confidence < 0.6:
        return None
    public_voice_detail_rollout_enabled = (
        _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9")
        and _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT")
        and _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT")
    )
    visible_public_anchor_count = _career_visible_public_anchor_count(
        career_ruler=career_ruler,
        ruler_house=ruler_house,
        tenth_house_planets=tenth_house_planets,
    )
    direct_meaning = "MC, yöneticisi ve görünür rol hattı birlikte kariyer temasını generic visibility fallback'ten daha spesifik biçimde taşıyor."
    gift = "Kariyer/public rol hattını MC ve yöneticisi üzerinden daha net ayırabilmek."
    inner_tension = "Görünür olmak, sorumluluk almak ve gerçekten hangi rolde görünmek istediğin her zaman aynı hızla çözülmeyebilir."
    growth = "Kariyer hattını yalnız görünürlük olarak değil, MC-yönetici-10. ev rotası olarak okumak."
    domain_reason = [
        "MC route",
        "MC ruler involved",
    ]
    if tenth_house_planets:
        domain_reason.append("10H planet")
    technical_anchors = [
        f"MC {mc_sign.title()}",
        _planet_chip(career_ruler, ruler_item),
        *[f"{planet.title()} · 10. ev" for planet in tenth_house_planets[:3]],
    ]
    source_evidence_ids = [
        f"composed:career:mc:{mc_sign}",
        f"composed:career:ruler:{career_ruler}:{str(ruler_item.get('sign') or '').strip().lower()}:{ruler_house}",
        *[f"composed:career:10h:{planet}" for planet in tenth_house_planets[:4]],
    ]
    evidence_trace = {
        "primitive_facts": {
            "placements": [
                {"planet": career_ruler.title(), "sign": str(ruler_item.get("sign") or ""), "house": ruler_house},
                *[
                    {
                        "planet": planet.title(),
                        "sign": str((_lookup_planet_entry(planet_map, planet) or {}).get("sign") or ""),
                        "house": 10,
                    }
                    for planet in tenth_house_planets[:4]
                ],
            ],
            "angles": [{"angle": "MC", "sign": mc_sign.title()}],
        },
        "discovery_routes": ["career_route"],
        "family_inputs": ["MC", "MC_ruler", "10H_planets"],
        "subtype_inputs": [subtype],
    }
    public_voice_detail_intrinsic_eligible = _public_voice_detail_intrinsic_eligibility(
        subtype=subtype,
        confidence=confidence,
        confidence_tier=_confidence_tier(confidence),
        chart_facts_match=True,
        domain_reason=domain_reason,
        evidence_trace=evidence_trace,
        lived_scene=lived_scene,
        has_mercury_public_anchor=has_mercury_public_anchor,
        career_ruler=career_ruler,
        ruler_house=ruler_house,
        tenth_house_planets=tenth_house_planets,
        visible_public_anchor_count=visible_public_anchor_count,
    )
    public_voice_detail_eligible = (
        public_voice_detail_rollout_enabled
        and public_voice_detail_intrinsic_eligible
    )
    return _composed_candidate_to_packet(
        ComposedSemanticCandidateV1(
            id=packet_id,
            family="career_route",
            subtype=subtype,
            source_type="composed_semantic",
            domain="career",
            promise_type="career_signature",
            domain_reason=domain_reason,
            public_job="debug_only",
            confidence=confidence,
            confidence_tier=_confidence_tier(confidence),
            chart_facts_match=True,
            technical_anchors=[item for item in technical_anchors if item],
            source_evidence_ids=source_evidence_ids,
            evidence_trace=evidence_trace,
            direct_meaning=direct_meaning,
            lived_scene=lived_scene,
            lived_scene_atoms=atoms,
            gift=gift,
            inner_tension=inner_tension,
            growth_direction=growth,
            avoid_readings=[
                "Do not reduce career route to generic visibility.",
                "Do not let raw career fallback own this route by default.",
            ],
            projection_hints={
                "surfaces": ["debug_only"],
                "priority": confidence,
                "auxiliary": False,
                "opening_strategy": "debug_only",
            },
            scoring_breakdown={
                "mc_route_strength": round(mc_strength, 4),
                "mc_ruler_strength": round(ruler_strength, 4),
                "tenth_house_support": round(tenth_support, 4),
                "public_planet_support": round(public_planet_support, 4),
                "subtype_specific_bonus": round(subtype_specific_bonus, 4),
                "subtype_penalty": round(subtype_penalty, 4),
                "subtype_coherence": round(coherence_bonus, 4),
            },
            matched_archetypes=[],
            public_eligibility={
                "debug_eligible": True,
                "detail_eligible": public_voice_detail_eligible,
                "public_support_eligible": False,
                "public_main_eligible": False,
                "reason_codes": [
                    "v0_9a_debug_only",
                    "public_main_flag_required",
                    *(
                        ["public_voice_detail_rollout_enabled"]
                        if public_voice_detail_eligible
                        else ["public_voice_detail_rollout_disabled_or_ineligible"]
                    ),
                ],
            },
            meta={
                "title": "Kariyer rotası composed semantic adayı",
                "locale": locale,
                "auxiliary": False,
                "inventory_variant": "composed_semantic_v0_9a",
                "v0_9_composed": True,
                "v0_9_family": "career_route",
                "debug_only": True,
                "non_public_discovery": True,
                "source_type": "composed_semantic",
                "public_voice_detail_rollout_candidate": subtype == "public_voice",
                "public_voice_detail_intrinsic_eligible": public_voice_detail_intrinsic_eligible,
                "visible_public_anchor_count": visible_public_anchor_count,
                "has_mercury_public_anchor": has_mercury_public_anchor,
            },
        )
    )


# ---------------------------------------------------------------------------
# v0.9b composed-semantic families: relationship_route + moon_signature
# ---------------------------------------------------------------------------
#
# Debug-only first cut. Both families:
#   * are gated by their own master flag (default false),
#   * always emit ``public_job="debug_only"``,
#   * always emit ``public_main_eligible=False`` and
#     ``public_support_eligible=False`` in v0.9b.0,
#   * never widen the ``composed_detail_renderer`` allowlist —
#     ``detail_eligible`` is only set to True when the shared
#     ``ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT`` flag is on,
#     and even then the renderer's variant signature gate refuses to render
#     these families (Phase B's allowlist is career-only).
#
# Cross-family overlap on Moon evidence is recorded in
# ``evidence_trace.cross_family_overlap`` so the cluster plan ledger can
# expose it for audit without changing public output.

_FIRE_SIGNS: frozenset[str] = frozenset({"aries", "leo", "sagittarius"})
_EARTH_SIGNS: frozenset[str] = frozenset({"taurus", "virgo", "capricorn"})
_AIR_SIGNS: frozenset[str] = frozenset({"gemini", "libra", "aquarius"})
_WATER_SIGNS: frozenset[str] = frozenset({"cancer", "scorpio", "pisces"})

_HARD_ASPECT_TYPES: tuple[str, ...] = ("square", "opposition")
_SOFT_ASPECT_TYPES: tuple[str, ...] = ("trine", "sextile")


def _has_any_aspect_type(
    aspects: Sequence[Mapping[str, Any]] | None,
    planet1: str,
    planet2: str,
    aspect_types: Sequence[str],
) -> bool:
    for aspect_type in aspect_types:
        if _has_aspect(aspects or [], planet1, planet2, aspect_type):
            return True
    return False


def _build_relationship_route_candidates(
    *,
    planet_map: Mapping[str, Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]] | None,
    house_rulers: Mapping[str, Any],
    locale: str,
    existing_ids: set[str],
) -> dict[str, Any] | None:
    packet_id = "composed_relationship_route_v0_9b"
    if packet_id in existing_ids:
        return None

    dsc_sign = _house_cusp_sign(house_rulers, 7)
    if not dsc_sign:
        return None
    dsc_ruler = _sign_ruler(dsc_sign)
    dsc_ruler_item = _lookup_planet_entry(planet_map, dsc_ruler) if dsc_ruler else {}
    if not dsc_ruler or not dsc_ruler_item:
        return None

    venus_item = _lookup_planet_entry(planet_map, "venus")
    mars_item = _lookup_planet_entry(planet_map, "mars")
    moon_item = _lookup_planet_entry(planet_map, "moon")
    sun_item = _lookup_planet_entry(planet_map, "sun")
    saturn_item = _lookup_planet_entry(planet_map, "saturn")
    uranus_item = _lookup_planet_entry(planet_map, "uranus")
    neptune_item = _lookup_planet_entry(planet_map, "neptune")
    pluto_item = _lookup_planet_entry(planet_map, "pluto")

    seventh_house_planets = _house_planet_names(planet_map, 7)
    eighth_house_planets = _house_planet_names(planet_map, 8)
    fifth_house_planets = _house_planet_names(planet_map, 5)
    twelfth_house_planets = _house_planet_names(planet_map, 12)
    eleventh_house_planets = _house_planet_names(planet_map, 11)

    mars_house = int(mars_item.get("house") or 0)
    mars_sign = str(mars_item.get("sign") or "").strip().lower()
    relationship_route_is_mars_led = dsc_sign in {"aries", "scorpio"} or dsc_ruler == "mars"
    mars_activation_gate = bool(
        relationship_route_is_mars_led
        and mars_item
        and mars_house in {1, 6, 10, 12}
    )

    if (
        not seventh_house_planets
        and int(dsc_ruler_item.get("house") or 0) not in {1, 5, 7, 8, 11, 12}
        and not mars_activation_gate
    ):
        return None

    dsc_ruler_house = int(dsc_ruler_item.get("house") or 0)
    dsc_ruler_sign = str(dsc_ruler_item.get("sign") or "").strip().lower()
    venus_house = int(venus_item.get("house") or 0)
    venus_sign = str(venus_item.get("sign") or "").strip().lower()
    mars_retrograde = bool(mars_item.get("retrograde"))
    moon_house = int(moon_item.get("house") or 0)
    moon_sign = str(moon_item.get("sign") or "").strip().lower()
    chiron_item = _lookup_planet_entry(planet_map, "chiron")
    chiron_house = int(chiron_item.get("house") or 0)
    mars_direct_activation_partners = [
        partner
        for partner in ("saturn", "uranus", "neptune", "chiron")
        if _has_any_aspect_type(aspects, "mars", partner, _HARD_ASPECT_TYPES)
    ]
    mars_direct_activation_hard_count = len(mars_direct_activation_partners)

    # ---- Subtype scoring channels ----
    subtype_signals: dict[str, float] = {}

    def _bump(subtype: str, amount: float) -> None:
        subtype_signals[subtype] = subtype_signals.get(subtype, 0.0) + amount

    # trust_steadiness
    if dsc_ruler_sign in _EARTH_SIGNS:
        _bump("trust_steadiness", 0.10)
    if dsc_ruler_house in {4, 10}:
        _bump("trust_steadiness", 0.08)
    if "venus" in seventh_house_planets or "saturn" in seventh_house_planets:
        _bump("trust_steadiness", 0.10)
    if _has_any_aspect_type(aspects, "venus", "saturn", _SOFT_ASPECT_TYPES):
        _bump("trust_steadiness", 0.06)
    if "mercury" in seventh_house_planets:
        _bump("trust_steadiness", 0.04)

    # attraction_warmth
    if venus_house in {5, 7}:
        _bump("attraction_warmth", 0.12)
    if venus_sign in _FIRE_SIGNS:
        _bump("attraction_warmth", 0.06)
    if int(sun_item.get("house") or 0) == 5:
        _bump("attraction_warmth", 0.06)
    if _has_any_aspect_type(aspects, "venus", "mars", _SOFT_ASPECT_TYPES):
        _bump("attraction_warmth", 0.06)

    # boundary_conflict
    if mars_house in {7, 8}:
        _bump("boundary_conflict", 0.12)
    if _has_any_aspect_type(aspects, "mars", "saturn", _HARD_ASPECT_TYPES):
        _bump("boundary_conflict", 0.10)
    if _has_any_aspect_type(aspects, dsc_ruler, "mars", _HARD_ASPECT_TYPES):
        _bump("boundary_conflict", 0.08)
    if mars_sign in {"aries", "cancer", "libra", "capricorn"} and "mars" in seventh_house_planets:
        _bump("boundary_conflict", 0.04)

    # direct_relational_activation
    if (
        relationship_route_is_mars_led
        and mars_item
        and mars_direct_activation_hard_count > 0
        and (mars_house in {1, 6, 10, 12} or mars_sign in {"aries", "scorpio"})
    ):
        if dsc_ruler == "mars":
            _bump("direct_relational_activation", 0.08)
        if mars_sign in {"aries", "scorpio"}:
            _bump("direct_relational_activation", 0.08)
        if mars_house in {1, 6, 10, 12}:
            _bump("direct_relational_activation", 0.06)
        if mars_house == 6:
            _bump("direct_relational_activation", 0.06)
        elif mars_house in {1, 10, 12}:
            _bump("direct_relational_activation", 0.03)
        _bump(
            "direct_relational_activation",
            min(0.15, 0.06 + (0.03 * max(0, mars_direct_activation_hard_count - 1))),
        )
        if mars_retrograde:
            _bump("direct_relational_activation", 0.02)

    # intimacy_depth
    intimacy_8h_planets = [p for p in eighth_house_planets if p in {"venus", "mars", "pluto", "moon"}]
    if intimacy_8h_planets:
        _bump("intimacy_depth", 0.06 + 0.04 * min(len(intimacy_8h_planets), 3))
    if _has_any_aspect_type(aspects, "venus", "pluto", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES):
        _bump("intimacy_depth", 0.08)
    if dsc_ruler_house == 8:
        _bump("intimacy_depth", 0.06)
    if "moon" in eighth_house_planets:
        _bump("intimacy_depth", 0.04)

    # emotional_need_affection
    if moon_house in {7, 8}:
        _bump("emotional_need_affection", 0.12)
    if _has_any_aspect_type(aspects, "venus", "moon", _SOFT_ASPECT_TYPES + _HARD_ASPECT_TYPES):
        _bump("emotional_need_affection", 0.08)
    if dsc_sign in {"cancer", "pisces"}:
        _bump("emotional_need_affection", 0.06)
    if moon_sign in _WATER_SIGNS and seventh_house_planets:
        _bump("emotional_need_affection", 0.04)

    # hidden_private_love
    twelfth_significators = [p for p in twelfth_house_planets if p in {"venus", "mars"}]
    if twelfth_significators:
        _bump("hidden_private_love", 0.10 + 0.04 * len(twelfth_significators))
    if dsc_ruler_house == 12:
        _bump("hidden_private_love", 0.08)
    if int(neptune_item.get("house") or 0) in {5, 7, 8}:
        _bump("hidden_private_love", 0.06)
    if dsc_sign == "pisces":
        _bump("hidden_private_love", 0.04)

    # freedom_space
    if int(uranus_item.get("house") or 0) in {7, 8}:
        _bump("freedom_space", 0.12)
    if mars_sign in _AIR_SIGNS and seventh_house_planets:
        _bump("freedom_space", 0.06)
    if dsc_ruler_house == 11:
        _bump("freedom_space", 0.08)
    if int(sun_item.get("house") or 0) == 11 or int(venus_item.get("house") or 0) == 11:
        _bump("freedom_space", 0.04)
    if str((_lookup_planet_entry(planet_map, "uranus") or {}).get("sign") or "").strip().lower() == "aquarius":
        _bump("freedom_space", 0.04)

    # wound_to_gift
    if chiron_house in {5, 7, 8}:
        _bump("wound_to_gift", 0.12)
    if _has_any_aspect_type(aspects, "saturn", "venus", _HARD_ASPECT_TYPES):
        _bump("wound_to_gift", 0.08)
    if _has_any_aspect_type(aspects, "saturn", "moon", _HARD_ASPECT_TYPES):
        _bump("wound_to_gift", 0.06)
    if dsc_ruler_house == 12 and _has_any_aspect_type(aspects, dsc_ruler, "saturn", _HARD_ASPECT_TYPES):
        _bump("wound_to_gift", 0.04)

    # Pick the strongest subtype (margin >= 0.04 over runner-up). Otherwise
    # default to ``trust_steadiness`` with a fallback penalty.
    ordered = sorted(subtype_signals.items(), key=lambda kv: kv[1], reverse=True)
    # v0.9b.0.1 calibration: relationship_route trust_steadiness fallback
    # previously landed at conf 0.65-0.79 because the base scoring floor
    # (~0.40) plus the weak 0.06/0.08 penalty left too much room above
    # the 0.60 publishable threshold. Bumped to 0.12 (margin-fail) and
    # 0.15 (no signal) to push default-fallback candidates closer to or
    # below the debug-only floor.
    #
    # ``is_subtype_default_fallback_path`` tracks whether the *path*
    # chosen was the default fallback (not just whether penalty > 0).
    # The downstream metric uses this flag, not the penalty value —
    # otherwise the split-evidence penalty below would mislabel genuine
    # top-scoring trust_steadiness candidates as fallback.
    is_subtype_default_fallback_path = False
    if not ordered or ordered[0][1] <= 0.0:
        subtype = "trust_steadiness"
        subtype_penalty = 0.15
        subtype_bonus = 0.0
        is_subtype_default_fallback_path = True
    else:
        top_subtype, top_score = ordered[0]
        runner_up_score = ordered[1][1] if len(ordered) > 1 else 0.0
        if top_score - runner_up_score < 0.04:
            subtype = "trust_steadiness"
            subtype_penalty = 0.12
            subtype_bonus = 0.0
            is_subtype_default_fallback_path = True
        else:
            subtype = top_subtype
            subtype_penalty = 0.0
            subtype_bonus = min(0.05, top_score / 4.0)

    # ---- Confidence scoring ----
    dsc_route_strength = 0.25
    dsc_ruler_strength = 0.14 + (0.06 if dsc_ruler_house in {1, 5, 7, 8, 10, 11} else 0.0)
    venus_support = 0.0
    mars_support = 0.0
    mars_activation_support = 0.0
    moon_support = 0.0
    if subtype_signals.get("attraction_warmth", 0.0) >= 0.06 and venus_item:
        venus_support = min(0.15, subtype_signals.get("attraction_warmth", 0.0))
    elif venus_house in {5, 7, 8}:
        venus_support = 0.08
    if subtype == "direct_relational_activation" and mars_item:
        mars_support = min(0.12, subtype_signals.get("direct_relational_activation", 0.0) * 0.24)
        mars_activation_support = min(
            0.10,
            (0.04 if mars_house in {1, 6, 10, 12} else 0.0)
            + (0.03 if mars_house == 6 else 0.0)
            + min(0.03, 0.01 * mars_direct_activation_hard_count),
        )
    elif subtype_signals.get("boundary_conflict", 0.0) >= 0.06 and mars_item:
        mars_support = min(0.15, subtype_signals.get("boundary_conflict", 0.0))
    elif mars_house in {7, 8}:
        mars_support = 0.07
    if subtype_signals.get("emotional_need_affection", 0.0) >= 0.06 and moon_item:
        moon_support = min(0.10, subtype_signals.get("emotional_need_affection", 0.0))
    elif moon_house in {7, 8}:
        moon_support = 0.05
    house_scene_support = min(
        0.10,
        0.03 * len(seventh_house_planets)
        + 0.02 * len(eighth_house_planets)
        + 0.01 * len(fifth_house_planets),
    )
    contradiction_coherence = 0.0
    # split-evidence penalty: if Venus / Mars / Moon evidence points at
    # disjoint subtypes (each > 0.06) the signal is incoherent — apply
    # an additional penalty.
    family_signal_subtypes = {
        "venus": "attraction_warmth" if venus_house in {5, 7} else None,
        "mars": (
            "direct_relational_activation"
            if relationship_route_is_mars_led
            and mars_house in {1, 6, 10, 12}
            and mars_direct_activation_hard_count > 0
            else "boundary_conflict" if mars_house in {7, 8} else None
        ),
        "moon": "emotional_need_affection" if moon_house in {7, 8} else None,
    }
    distinct_directions = {v for v in family_signal_subtypes.values() if v} - {None}
    if len(distinct_directions) >= 2 and subtype not in distinct_directions:
        subtype_penalty = max(subtype_penalty, 0.05)

    confidence = round(
        min(
            0.94,
            max(
                0.0,
                dsc_route_strength
                + dsc_ruler_strength
                + venus_support
                + mars_support
                + mars_activation_support
                + moon_support
                + house_scene_support
                + contradiction_coherence
                + subtype_bonus
                - subtype_penalty,
            ),
        ),
        4,
    )
    if confidence < 0.6:
        return None

    # ---- TR copy seeds per subtype ----
    subtype_copy = {
        "trust_steadiness": (
            "İlişki hattında güven, süreklilik ve karşı tarafın istikrarı sende öne çıkıyor.",
            ["zamanla kurulan güvene yaslanman", "ilişkide istikrar arayışın"],
        ),
        "direct_relational_activation": (
            "Birine yaklaştığında, belirsizliği uzun süre taşımak sana kolay gelmeyebilir.",
            [
                "ilişkide içindeki cevabı daha açık göstermeye ihtiyaç duyabilirsin",
                "yakınlık arttığında nerede durduğunu daha görünür kılmak isteyebilirsin",
            ],
        ),
        "attraction_warmth": (
            "İlişkide çekim, sıcaklık ve karşılıklı keyif sende daha belirgin çalışıyor.",
            ["karşı tarafla sıcak temas kurman", "ilişkide oyunculuk ve estetiğin önemi"],
        ),
        "boundary_conflict": (
            "İlişki hattında sınır, çatışma ve istek farklılıkları sende daha görünür biçimde çalışıyor.",
            ["ilişkide sınır çekmen gereken anlar", "isteğin ve karşı tarafın isteğinin ayrışması"],
        ),
        "intimacy_depth": (
            "İlişkide yüzeyin altındaki derinlik, paylaşım ve dönüşüm sende belirgin biçimde çalışıyor.",
            ["yüzeyden değil derinlikten temas etmen", "ilişkide karşılıklı dönüşüm yaşanması"],
        ),
        "emotional_need_affection": (
            "İlişki hattında duygusal ihtiyacın, bağlanma ve şefkat arayışın öne çıkıyor.",
            ["karşı tarafın varlığında güvende hissetme ihtiyacın", "ilişkide şefkat aramanın merkez olması"],
        ),
        "hidden_private_love": (
            "İlişki hattının önemli bir kısmı gizli, özel ya da içeride yaşanan bir alanda kuruluyor.",
            ["dışarıya açmadığın özel bir bağ alanın", "ilişkinin görünür değil korunan tarafının ağır basması"],
        ),
        "freedom_space": (
            "İlişki hattında özgürlük, alan ve sıradışılık ihtiyacın belirgin biçimde çalışıyor.",
            ["alan ihtiyacının ilişki kadar önemli olması", "ilişkide alışılmamış biçimlerin sana daha doğal gelmesi"],
        ),
        "wound_to_gift": (
            "İlişki hattında eski bir yara ya da hassas nokta sonradan gerçek bir armağana dönüşebiliyor.",
            ["bir kez kırılan yerin sonra güçlü bir bağ alanına dönmesi", "ilişkide şifa ve onarımın merkezde olması"],
        ),
    }
    lived_scene, atoms = subtype_copy[subtype]

    direct_meaning = "DSC, yöneticisi ve Venüs/Mars/Ay birlikte ilişki hattını generic ilişki fallback'ten daha spesifik biçimde taşıyor."
    gift = "İlişki hattını yalnız 'ilişki' etiketiyle değil, DSC-yönetici-Venüs/Mars/Ay rotası üzerinden ayırabilmek."
    inner_tension = "Karşı tarafla kurduğun bağda nelerin sıcak, nelerin sınır ve nelerin derin olduğu her zaman aynı tonla çalışmayabilir."
    growth = "İlişki hattını yedi-evi-yönetici-significator rotası olarak okumak."
    if subtype == "direct_relational_activation":
        direct_meaning = "Yakınlık sende bazen beklemeyi değil, içindeki cevabı daha açık göstermeyi ister."
        gift = "Bir bağın içinde kendini saklamadan, ne istediğini daha dürüst ve zamanında gösterebilmek."
        inner_tension = "Bir yanın ortamı bozmamak isterken, başka bir yanın içinden geçen şeyi daha fazla saklamak istemeyebilir."
        growth = "İçinden geçeni bastırmadan, ama bağı da aceleye sıkıştırmadan daha açık söyleyebilmek."

    domain_reason: list[str] = [
        "DSC route",
        "DSC ruler involved",
    ]
    if seventh_house_planets:
        domain_reason.append("7H planet")
    if subtype == "direct_relational_activation" and mars_house == 6:
        domain_reason.append("6H daily/action route")
    if subtype == "attraction_warmth" or venus_house in {5, 7}:
        domain_reason.append("Venus relationship signature")
    if subtype in {"boundary_conflict", "direct_relational_activation"} or mars_house in {7, 8}:
        domain_reason.append("Mars boundary/desire signature")
    if subtype == "emotional_need_affection" or moon_house in {7, 8}:
        domain_reason.append("Moon attachment signature")
    if subtype == "intimacy_depth":
        domain_reason.append("8H intimacy signature")
    if subtype == "hidden_private_love":
        domain_reason.append("12H hidden-love signature")
    if subtype == "freedom_space":
        domain_reason.append("Uranus freedom signature")
    if subtype == "wound_to_gift":
        domain_reason.append("Chiron wound-to-gift signature")

    technical_anchors = [f"DSC {dsc_sign.title()}"]
    if subtype == "direct_relational_activation" and mars_item:
        mars_anchor = f"Mars {mars_sign.title()} {mars_house}H"
        if mars_retrograde:
            mars_anchor += " Rx"
        technical_anchors.append(mars_anchor)
        technical_anchors.extend(f"Mars square {partner.title()}" for partner in mars_direct_activation_partners)
    else:
        technical_anchors.append(_planet_chip(dsc_ruler, dsc_ruler_item))
    technical_anchors.extend(
        [_planet_chip(planet, _lookup_planet_entry(planet_map, planet)) for planet in seventh_house_planets[:3]]
    )
    source_evidence_ids = [
        f"composed:relationship:dsc:{dsc_sign}",
        f"composed:relationship:ruler:{dsc_ruler}:{dsc_ruler_sign}:{dsc_ruler_house}",
        *[f"composed:relationship:7h:{planet}" for planet in seventh_house_planets[:4]],
    ]
    if subtype == "direct_relational_activation":
        source_evidence_ids.extend(
            [f"composed:relationship:mars_hard_aspect:{partner}" for partner in mars_direct_activation_partners]
        )

    cross_family_overlap: list[str] = []
    moon_used_by_relationship = (
        subtype in {"emotional_need_affection", "intimacy_depth"}
        and bool(moon_item)
    )
    if moon_used_by_relationship:
        cross_family_overlap.append("moon_evidence_shared_with_moon_signature")

    evidence_trace = {
        "primitive_facts": {
            "placements": [
                {"planet": dsc_ruler.title(), "sign": dsc_ruler_sign, "house": dsc_ruler_house},
                *(
                    [{"planet": "Venus", "sign": venus_sign, "house": venus_house}]
                    if venus_item
                    else []
                ),
                *(
                    [{"planet": "Mars", "sign": mars_sign, "house": mars_house, "retrograde": mars_retrograde}]
                    if mars_item
                    else []
                ),
                *(
                    [{"planet": "Moon", "sign": moon_sign, "house": moon_house}]
                    if moon_item
                    else []
                ),
            ],
            "angles": [{"angle": "DSC", "sign": dsc_sign.title()}],
            "aspects": [
                {"planet1": "Mars", "planet2": partner.title(), "type": "square"}
                for partner in mars_direct_activation_partners
            ],
        },
        "discovery_routes": ["relationship_route"],
        "family_inputs": ["DSC", "DSC_ruler", "Venus", "Mars", "Moon", "7H_planets"],
        "subtype_inputs": [subtype],
        "subtype_signal_scores": {k: round(v, 4) for k, v in subtype_signals.items()},
        "cross_family_overlap": cross_family_overlap,
    }

    detail_support_flag_enabled = (
        _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT")
    )
    detail_eligible = detail_support_flag_enabled and confidence >= 0.7
    phase3_internal_meta = None
    if (
        subtype == "hidden_private_love"
        and _relationship_hidden_private_love_phase3_internal_metadata_enabled()
    ):
        phase3_internal_meta = _build_relationship_hidden_private_love_phase3_internal_metadata(
            source_type="composed_semantic",
            domain_reason=domain_reason,
            technical_anchors=technical_anchors,
            subtype_default_fallback=is_subtype_default_fallback_path,
            non_public_discovery=True,
        )

    return _composed_candidate_to_packet(
        ComposedSemanticCandidateV1(
            id=packet_id,
            family="relationship_route",
            subtype=subtype,
            source_type="composed_semantic",
            domain="relationship",
            promise_type="relationship_signature",
            domain_reason=domain_reason,
            public_job="debug_only",
            confidence=confidence,
            confidence_tier=_confidence_tier(confidence),
            chart_facts_match=True,
            technical_anchors=[item for item in technical_anchors if item],
            source_evidence_ids=source_evidence_ids,
            evidence_trace=evidence_trace,
            direct_meaning=direct_meaning,
            lived_scene=lived_scene,
            lived_scene_atoms=atoms,
            gift=gift,
            inner_tension=inner_tension,
            growth_direction=growth,
            avoid_readings=[
                "Do not reduce relationship route to generic 'relationship' label.",
                "Do not let raw relationship fallback own this route by default.",
            ],
            projection_hints={
                "surfaces": ["debug_only"],
                "priority": confidence,
                "auxiliary": False,
                "opening_strategy": "debug_only",
            },
            scoring_breakdown={
                "dsc_route_strength": round(dsc_route_strength, 4),
                "dsc_ruler_strength": round(dsc_ruler_strength, 4),
                "venus_support": round(venus_support, 4),
                "mars_support": round(mars_support, 4),
                "mars_activation_support": round(mars_activation_support, 4),
                "moon_support": round(moon_support, 4),
                "house_scene_support": round(house_scene_support, 4),
                "contradiction_coherence": round(contradiction_coherence, 4),
                "subtype_bonus": round(subtype_bonus, 4),
                "subtype_penalty": round(subtype_penalty, 4),
            },
            matched_archetypes=[],
            public_eligibility={
                "debug_eligible": True,
                "detail_eligible": detail_eligible,
                "public_support_eligible": False,
                "public_main_eligible": False,
                "reason_codes": [
                    "v0_9b_debug_only",
                    "public_main_flag_required",
                    *(
                        ["v0_9b_detail_support_flag_enabled"]
                        if detail_eligible
                        else ["v0_9b_detail_support_flag_disabled_or_low_confidence"]
                    ),
                ],
            },
            meta={
                "title": "İlişki rotası composed semantic adayı",
                "locale": locale,
                "auxiliary": False,
                "inventory_variant": "composed_semantic_v0_9b",
                "v0_9_composed": True,
                "v0_9_family": "relationship_route",
                "debug_only": True,
                "non_public_discovery": True,
                "source_type": "composed_semantic",
                "subtype_default_fallback": is_subtype_default_fallback_path,
                "cross_family_overlap": cross_family_overlap,
                **(
                    {"deep_read_phase3": phase3_internal_meta}
                    if phase3_internal_meta is not None
                    else {}
                ),
            },
        )
    )


def _build_moon_signature_candidates(
    *,
    planet_map: Mapping[str, Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]] | None,
    house_rulers: Mapping[str, Any],
    locale: str,
    existing_ids: set[str],
) -> dict[str, Any] | None:
    packet_id = "composed_moon_signature_v0_9b"
    if packet_id in existing_ids:
        return None

    moon_item = _lookup_planet_entry(planet_map, "moon")
    if not moon_item:
        return None
    moon_sign = str(moon_item.get("sign") or "").strip().lower()
    moon_house = int(moon_item.get("house") or 0)
    if not moon_sign or moon_house <= 0:
        return None

    moon_ruler = _sign_ruler(moon_sign)
    moon_ruler_item = _lookup_planet_entry(planet_map, moon_ruler) if moon_ruler else {}
    if not moon_ruler or not moon_ruler_item:
        return None
    moon_ruler_house = int(moon_ruler_item.get("house") or 0)

    ic_sign = _house_cusp_sign(house_rulers, 4)
    fourth_house_planets = _house_planet_names(planet_map, 4)
    sixth_house_planets = _house_planet_names(planet_map, 6)
    eighth_house_planets = _house_planet_names(planet_map, 8)
    twelfth_house_planets = _house_planet_names(planet_map, 12)
    fifth_house_planets = _house_planet_names(planet_map, 5)

    # ---- Subtype scoring channels ----
    subtype_signals: dict[str, float] = {}

    def _bump(subtype: str, amount: float) -> None:
        subtype_signals[subtype] = subtype_signals.get(subtype, 0.0) + amount

    # home_inner_security
    if moon_house == 4:
        _bump("home_inner_security", 0.18)
    if moon_ruler_house == 4:
        _bump("home_inner_security", 0.10)
    if fourth_house_planets:
        _bump("home_inner_security", 0.04 + 0.02 * min(len(fourth_house_planets), 3))
    if ic_sign == "cancer":
        _bump("home_inner_security", 0.04)

    # daily_sensitivity
    if moon_house == 6:
        _bump("daily_sensitivity", 0.18)
    if _has_any_aspect_type(aspects, "moon", "mercury", _SOFT_ASPECT_TYPES + _HARD_ASPECT_TYPES):
        _bump("daily_sensitivity", 0.06)
    if "mercury" in sixth_house_planets:
        _bump("daily_sensitivity", 0.04)
    if moon_sign == "virgo":
        _bump("daily_sensitivity", 0.04)

    # creative_emotional_expression
    if moon_house == 5:
        _bump("creative_emotional_expression", 0.18)
    if moon_ruler_house == 5:
        _bump("creative_emotional_expression", 0.10)
    if _has_any_aspect_type(aspects, "moon", "venus", _SOFT_ASPECT_TYPES) and fifth_house_planets:
        _bump("creative_emotional_expression", 0.06)
    if moon_sign in {"leo", "pisces"} and moon_house == 5:
        _bump("creative_emotional_expression", 0.04)

    # intimacy_depth (Moon flavor)
    if moon_house == 8:
        _bump("intimacy_depth", 0.18)
    if _has_any_aspect_type(aspects, "moon", "pluto", _SOFT_ASPECT_TYPES + _HARD_ASPECT_TYPES):
        _bump("intimacy_depth", 0.08)
    if moon_sign == "scorpio":
        _bump("intimacy_depth", 0.06)
    if moon_ruler_house == 8:
        _bump("intimacy_depth", 0.04)

    # private_emotional_processing
    if moon_house == 12:
        _bump("private_emotional_processing", 0.18)
    if _has_any_aspect_type(aspects, "moon", "neptune", _SOFT_ASPECT_TYPES + _HARD_ASPECT_TYPES):
        _bump("private_emotional_processing", 0.06)
    if moon_ruler_house == 12:
        _bump("private_emotional_processing", 0.06)
    if moon_sign == "pisces":
        _bump("private_emotional_processing", 0.04)

    ordered = sorted(subtype_signals.items(), key=lambda kv: kv[1], reverse=True)
    # v0.9b.0.1 calibration: moon_signature emotional_rhythm fallback
    # previously landed up to 0.73 (e.g. fix07_aries_libra_nodes). Same
    # base-scoring floor problem as relationship. Penalty bumped to 0.12
    # (margin-fail) and 0.15 (no signal).
    is_subtype_default_fallback_path = False
    if not ordered or ordered[0][1] <= 0.0:
        subtype = "emotional_rhythm"
        subtype_penalty = 0.15
        subtype_bonus = 0.0
        is_subtype_default_fallback_path = True
    else:
        top_subtype, top_score = ordered[0]
        runner_up_score = ordered[1][1] if len(ordered) > 1 else 0.0
        if top_score - runner_up_score < 0.04:
            subtype = "emotional_rhythm"
            subtype_penalty = 0.12
            subtype_bonus = 0.0
            is_subtype_default_fallback_path = True
        else:
            subtype = top_subtype
            subtype_penalty = 0.0
            subtype_bonus = min(0.05, top_score / 4.0)

    # ---- Confidence scoring ----
    moon_sign_strength = 0.10 if moon_sign in (_WATER_SIGNS | {"cancer"}) else 0.07
    moon_house_scene = 0.12 + (0.06 if moon_house in {1, 4, 5, 6, 7, 8, 10, 12} else 0.0)
    moon_ruler_route = 0.10 + (0.08 if moon_ruler_house in {1, 4, 5, 6, 7, 8, 10, 12} else 0.0)
    aspect_support = 0.0
    for partner in ("sun", "venus", "mars", "saturn", "pluto", "neptune", "uranus"):
        if _has_any_aspect_type(aspects, "moon", partner, _SOFT_ASPECT_TYPES + _HARD_ASPECT_TYPES):
            aspect_support += 0.04
    aspect_support = min(0.20, aspect_support)
    reinforcement_support = min(
        0.15,
        0.03 * len(fourth_house_planets)
        + 0.02 * len(sixth_house_planets)
        + 0.02 * len(eighth_house_planets)
        + 0.02 * len(twelfth_house_planets)
        + 0.02 * len(fifth_house_planets),
    )
    subtype_coherence = min(0.10, max(0.0, ordered[0][1] if ordered else 0.0) / 2.0)

    confidence = round(
        min(
            0.94,
            max(
                0.0,
                moon_sign_strength
                + moon_house_scene
                + moon_ruler_route
                + aspect_support
                + reinforcement_support
                + subtype_coherence
                + subtype_bonus
                - subtype_penalty,
            ),
        ),
        4,
    )
    if confidence < 0.6:
        return None

    subtype_copy = {
        "emotional_rhythm": (
            "Duygusal ritmin Ay'ın burcu ve evi üzerinden belirleniyor ve günlük tonun bu hatta yaslanıyor.",
            ["günlük duygusal ritminin tutarlı bir tona yaslanması", "duyguların sende bir ritim kurarak çalışması"],
        ),
        "home_inner_security": (
            "Duygusal güvenliğin ev, aile, IC ve içeride toparlandığın özel alan üzerinden kuruluyor.",
            ["içeride sakinleşmeye ihtiyacın", "ev ve aile alanının duygusal omurga olması"],
        ),
        "daily_sensitivity": (
            "Duygusal hattın günlük rutin, beden, iş ve gündelik düzen üzerinden kendini gösteriyor.",
            ["rutinin değişmesinin duygusal etkisi", "gündelik küçük şeylerin sende büyük yer kaplaması"],
        ),
        "creative_emotional_expression": (
            "Duygusal hattın yaratıcı ifade, oyunculuk ve dışa vurulan kişisel bir alan üzerinden çalışıyor.",
            ["duyguyu yaratıcı bir biçime dökmen", "kendini ifade etmenin duygusal denge kurması"],
        ),
        "intimacy_depth": (
            "Duygusal hattın yüzeyin altındaki yoğunluk, paylaşım ve dönüşüm üzerinden çalışıyor.",
            ["yüzeyde değil derinde temas etme ihtiyacın", "duygusal dönüşümlerin sende belirgin olması"],
        ),
        "private_emotional_processing": (
            "Duygusal hattın geri çekilip işleme, sezgi ve özel alan üzerinden çalışıyor.",
            ["duyguyu yalnız işlemen", "kalabalıktan sonra geri çekilme ihtiyacın"],
        ),
    }
    lived_scene, atoms = subtype_copy[subtype]

    direct_meaning = "Ay'ın burcu, evi, yöneticisi ve aspekt rotası birlikte duygusal hattı generic duygu fallback'ten daha spesifik biçimde taşıyor."
    gift = "Duygusal hattı yalnız Ay burcuyla değil, Ay'ın gerçek yaşam sahnesi üzerinden ayırabilmek."
    inner_tension = "Duygusal ritmin, ihtiyaç duyduğun zemin ve seni gerçekten besleyen sahnenin aynı yerden çalışmayabileceği zamanlar var."
    growth = "Duygusal hattı Ay burcu, evi, yöneticisi ve reinforcement rotaları üzerinden okumak."

    domain_reason: list[str] = ["Moon need signature", "Moon house scene", "Moon ruler route"]
    if subtype == "home_inner_security":
        domain_reason.append("IC/4H reinforcement")
    if subtype == "daily_sensitivity":
        domain_reason.append("6H daily-rhythm route")
    if subtype == "intimacy_depth":
        domain_reason.append("8H intimacy route")
    if subtype == "private_emotional_processing":
        domain_reason.append("12H private-processing route")
    if subtype == "creative_emotional_expression":
        domain_reason.append("5H creative-emotional route")
    if _has_any_aspect_type(aspects, "moon", "sun", _SOFT_ASPECT_TYPES + _HARD_ASPECT_TYPES):
        domain_reason.append("Moon-luminary aspect")

    technical_anchors = [
        _planet_chip("moon", moon_item),
        _planet_chip(moon_ruler, moon_ruler_item),
    ]
    if ic_sign:
        technical_anchors.append(f"IC {ic_sign.title()}")
    technical_anchors.extend(
        f"{planet.title()} · 4. ev" for planet in fourth_house_planets[:2]
    )

    source_evidence_ids = [
        f"composed:moon:sign:{moon_sign}",
        f"composed:moon:house:{moon_house}",
        f"composed:moon:ruler:{moon_ruler}:{str(moon_ruler_item.get('sign') or '').strip().lower()}:{moon_ruler_house}",
    ]

    cross_family_overlap: list[str] = []
    if subtype in {"intimacy_depth"}:
        cross_family_overlap.append("moon_evidence_shared_with_relationship_route")

    evidence_trace = {
        "primitive_facts": {
            "placements": [
                {"planet": "Moon", "sign": moon_sign, "house": moon_house},
                {
                    "planet": moon_ruler.title(),
                    "sign": str(moon_ruler_item.get("sign") or ""),
                    "house": moon_ruler_house,
                },
            ],
            "angles": [{"angle": "IC", "sign": ic_sign.title()}] if ic_sign else [],
        },
        "discovery_routes": ["moon_signature"],
        "family_inputs": ["Moon_sign", "Moon_house", "Moon_ruler", "Moon_aspects", "IC_4H_reinforcement"],
        "subtype_inputs": [subtype],
        "subtype_signal_scores": {k: round(v, 4) for k, v in subtype_signals.items()},
        "cross_family_overlap": cross_family_overlap,
    }

    detail_support_flag_enabled = _env_enabled(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9B_DETAIL_SUPPORT"
    )
    detail_eligible = detail_support_flag_enabled and confidence >= 0.7

    return _composed_candidate_to_packet(
        ComposedSemanticCandidateV1(
            id=packet_id,
            family="moon_signature",
            subtype=subtype,
            source_type="composed_semantic",
            domain="emotional_world",
            promise_type="moon_signature",
            domain_reason=domain_reason,
            public_job="debug_only",
            confidence=confidence,
            confidence_tier=_confidence_tier(confidence),
            chart_facts_match=True,
            technical_anchors=[item for item in technical_anchors if item],
            source_evidence_ids=source_evidence_ids,
            evidence_trace=evidence_trace,
            direct_meaning=direct_meaning,
            lived_scene=lived_scene,
            lived_scene_atoms=atoms,
            gift=gift,
            inner_tension=inner_tension,
            growth_direction=growth,
            avoid_readings=[
                "Do not reduce moon signature to Moon sign only.",
                "Do not let generic emotional fallback own this route by default.",
            ],
            projection_hints={
                "surfaces": ["debug_only"],
                "priority": confidence,
                "auxiliary": False,
                "opening_strategy": "debug_only",
            },
            scoring_breakdown={
                "moon_sign_strength": round(moon_sign_strength, 4),
                "moon_house_scene": round(moon_house_scene, 4),
                "moon_ruler_route": round(moon_ruler_route, 4),
                "aspect_support": round(aspect_support, 4),
                "reinforcement_support": round(reinforcement_support, 4),
                "subtype_coherence": round(subtype_coherence, 4),
                "subtype_bonus": round(subtype_bonus, 4),
                "subtype_penalty": round(subtype_penalty, 4),
            },
            matched_archetypes=[],
            public_eligibility={
                "debug_eligible": True,
                "detail_eligible": detail_eligible,
                "public_support_eligible": False,
                "public_main_eligible": False,
                "reason_codes": [
                    "v0_9b_debug_only",
                    "public_main_flag_required",
                    *(
                        ["v0_9b_detail_support_flag_enabled"]
                        if detail_eligible
                        else ["v0_9b_detail_support_flag_disabled_or_low_confidence"]
                    ),
                ],
            },
            meta={
                "title": "Ay imzası composed semantic adayı",
                "locale": locale,
                "auxiliary": False,
                "inventory_variant": "composed_semantic_v0_9b",
                "v0_9_composed": True,
                "v0_9_family": "moon_signature",
                "debug_only": True,
                "non_public_discovery": True,
                "source_type": "composed_semantic",
                "subtype_default_fallback": is_subtype_default_fallback_path,
                "cross_family_overlap": cross_family_overlap,
            },
        )
    )


# ---------------------------------------------------------------------------
# v0.9c composed-semantic family: mercury_signature
#
# Debug-only first cut with two subtypes:
#   * speech_identity_spine
#   * structured_disruptive_mind
#
# Constraints:
#   * emit at most one Mercury candidate per chart
#   * no generic Mercury fallback subtype
#   * runner-up subtype metadata is captured when the lead margin is < 0.04
#   * public_job stays debug_only; no detail/public lane in v0.9c.0
# ---------------------------------------------------------------------------


def _build_mercury_signature_candidates(
    *,
    planet_map: Mapping[str, Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]] | None,
    house_rulers: Mapping[str, Any],
    locale: str,
    existing_ids: set[str],
    career_candidate: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    packet_id = "composed_mercury_signature_v0_9c"
    if packet_id in existing_ids:
        return None

    mercury_item = _lookup_planet_entry(planet_map, "mercury")
    if not mercury_item:
        return None
    mercury_sign = str(mercury_item.get("sign") or "").strip().lower()
    mercury_house = int(mercury_item.get("house") or 0)
    if not mercury_sign or mercury_house <= 0:
        return None

    sun_item = _lookup_planet_entry(planet_map, "sun")
    saturn_item = _lookup_planet_entry(planet_map, "saturn")
    uranus_item = _lookup_planet_entry(planet_map, "uranus")
    asc_sign = _asc_sign(metadata_like=planet_map, house_rulers=house_rulers)
    mc_sign = _house_cusp_sign(house_rulers, 10)
    third_sign = _house_cusp_sign(house_rulers, 3)
    ninth_sign = _house_cusp_sign(house_rulers, 9)
    chart_ruler = _sign_ruler(asc_sign) if asc_sign else ""
    third_ruler = _sign_ruler(third_sign) if third_sign else ""
    ninth_ruler = _sign_ruler(ninth_sign) if ninth_sign else ""
    career_ruler = _sign_ruler(mc_sign) if mc_sign else ""

    third_ruler_item = _lookup_planet_entry(planet_map, third_ruler) if third_ruler else {}
    ninth_ruler_item = _lookup_planet_entry(planet_map, ninth_ruler) if ninth_ruler else {}
    career_ruler_item = _lookup_planet_entry(planet_map, career_ruler) if career_ruler else {}

    sun_house = int(sun_item.get("house") or 0)
    saturn_house = int(saturn_item.get("house") or 0)
    uranus_house = int(uranus_item.get("house") or 0)
    saturn_sign = str(saturn_item.get("sign") or "").strip().lower()
    uranus_sign = str(uranus_item.get("sign") or "").strip().lower()
    third_ruler_house = int(third_ruler_item.get("house") or 0)
    ninth_ruler_house = int(ninth_ruler_item.get("house") or 0)
    career_ruler_house = int(career_ruler_item.get("house") or 0)

    third_house_planets = _house_planet_names(planet_map, 3)
    ninth_house_planets = _house_planet_names(planet_map, 9)
    eleventh_house_planets = _house_planet_names(planet_map, 11)
    tenth_house_planets = _house_planet_names(planet_map, 10)
    mercury_aspect_refs = _top_aspect_refs(aspects, planet="Mercury", limit=4)

    mercury_sun_conjunction = _has_aspect(aspects or [], "Mercury", "Sun", "Conjunction")
    mercury_asc_conjunction = _has_aspect(aspects or [], "Mercury", "Ascendant", "Conjunction")
    mercury_saturn_aspect = _has_any_aspect_type(aspects, "Mercury", "Saturn", _SOFT_ASPECT_TYPES + _HARD_ASPECT_TYPES)
    mercury_uranus_aspect = _has_any_aspect_type(aspects, "Mercury", "Uranus", _SOFT_ASPECT_TYPES + _HARD_ASPECT_TYPES)
    mercury_midheaven_aspect = _has_any_aspect_type(aspects, "Mercury", "Midheaven", _SOFT_ASPECT_TYPES + _HARD_ASPECT_TYPES)
    mercury_chart_ruler = chart_ruler == "mercury"
    mercury_mind_house = mercury_house in {3, 9, 11}
    mercury_on_identity_spine = mercury_house == 1 or mercury_sun_conjunction or mercury_asc_conjunction or mercury_chart_ruler

    third_route_is_mercurial = third_ruler == "mercury"
    ninth_route_is_mercurial = ninth_ruler == "mercury"
    saturn_on_mind_route = saturn_house in {3, 9} or third_sign == "capricorn" or ninth_sign == "capricorn"
    uranus_on_mind_route = uranus_house in {3, 9} or third_sign == "aquarius" or ninth_sign == "aquarius"
    saturn_route_owner_active = third_ruler == "saturn" or ninth_ruler == "saturn"
    uranus_route_owner_active = third_ruler == "uranus" or ninth_ruler == "uranus"
    mind_route_support_present = (
        mercury_mind_house
        or third_route_is_mercurial
        or ninth_route_is_mercurial
        or bool(third_house_planets)
        or bool(ninth_house_planets)
    )

    subtype_signals: dict[str, float] = {}

    def _bump(subtype: str, amount: float) -> None:
        subtype_signals[subtype] = subtype_signals.get(subtype, 0.0) + amount

    speech_self_link_strength = 0.0
    if mercury_house == 1:
        speech_self_link_strength += 0.14
    if mercury_sun_conjunction:
        speech_self_link_strength += 0.12
    if mercury_asc_conjunction:
        speech_self_link_strength += 0.12
    if mercury_chart_ruler:
        speech_self_link_strength += 0.10

    speech_mind_route_strength = 0.0
    if mercury_house in {3, 9}:
        speech_mind_route_strength += 0.10
    elif mercury_house == 11:
        speech_mind_route_strength += 0.06
    if third_route_is_mercurial:
        speech_mind_route_strength += 0.08
    if ninth_route_is_mercurial:
        speech_mind_route_strength += 0.08
    if len(mercury_aspect_refs) >= 1:
        speech_mind_route_strength += 0.04

    if speech_self_link_strength > 0.0 and speech_mind_route_strength > 0.0:
        _bump("speech_identity_spine", speech_self_link_strength + speech_mind_route_strength)
        if mercury_sun_conjunction and mercury_asc_conjunction:
            _bump("speech_identity_spine", 0.04)
    speech_combined_bonus = 0.0
    if speech_self_link_strength >= 0.22 and speech_mind_route_strength >= 0.12:
        speech_combined_bonus = 0.06
    elif speech_self_link_strength >= 0.12 and speech_mind_route_strength >= 0.18:
        speech_combined_bonus = 0.04

    structural_signal = 0.0
    if mercury_saturn_aspect:
        structural_signal += 0.12
    if mercury_sign == "capricorn":
        structural_signal += 0.10
    if saturn_house in {3, 9}:
        structural_signal += 0.12
    if saturn_route_owner_active:
        structural_signal += 0.08
    if third_sign == "capricorn" or ninth_sign == "capricorn":
        structural_signal += 0.08
    if saturn_sign == "capricorn" and (saturn_house in {3, 9} or mercury_saturn_aspect):
        structural_signal += 0.04

    disruptive_signal = 0.0
    if mercury_uranus_aspect:
        disruptive_signal += 0.12
    if mercury_sign == "aquarius":
        disruptive_signal += 0.10
    if uranus_house in {3, 9}:
        disruptive_signal += 0.12
    if uranus_route_owner_active:
        disruptive_signal += 0.08
    if third_sign == "aquarius" or ninth_sign == "aquarius":
        disruptive_signal += 0.08
    if uranus_sign == "aquarius" and (uranus_house in {3, 9} or mercury_uranus_aspect):
        disruptive_signal += 0.04

    if structural_signal > 0.0 and disruptive_signal > 0.0:
        _bump("structured_disruptive_mind", structural_signal + disruptive_signal)
        if saturn_house in {3, 9} and uranus_house in {3, 9}:
            _bump("structured_disruptive_mind", 0.26)
        if third_sign in {"capricorn", "aquarius"} and ninth_sign in {"capricorn", "aquarius"}:
            _bump("structured_disruptive_mind", 0.08)
        if mercury_on_identity_spine:
            _bump("structured_disruptive_mind", 0.06)

    ordered = sorted(subtype_signals.items(), key=lambda kv: (-kv[1], kv[0]))
    if not ordered or ordered[0][1] <= 0.0:
        return None

    subtype, top_score = ordered[0]
    runner_up_subtype = ordered[1][0] if len(ordered) > 1 else ""
    runner_up_score = ordered[1][1] if len(ordered) > 1 else 0.0
    runner_up_score_delta = round(top_score - runner_up_score, 4) if runner_up_subtype else 0.0

    public_anchor_count = 0
    if mercury_house == 10:
        public_anchor_count += 1
    if "mercury" in tenth_house_planets:
        public_anchor_count += 1
    if mercury_midheaven_aspect:
        public_anchor_count += 1
    if career_ruler == "mercury" and career_ruler_house in {10, 11}:
        public_anchor_count += 1

    independent_mind_support_count = 0
    if mercury_on_identity_spine:
        independent_mind_support_count += 1
    if mercury_mind_house:
        independent_mind_support_count += 1
    if third_route_is_mercurial or ninth_route_is_mercurial:
        independent_mind_support_count += 1
    if saturn_on_mind_route:
        independent_mind_support_count += 1
    if uranus_on_mind_route:
        independent_mind_support_count += 1
    if len(mercury_aspect_refs) >= 1:
        independent_mind_support_count += 1

    career_overlap_penalty = 0.0
    career_overlap_guard = ""
    career_subtype = str((career_candidate or {}).get("subtype") or "").strip().lower()
    career_confidence = _safe_float((career_candidate or {}).get("confidence"), 0.0)
    public_voice_overlap_delta = 0.0
    if career_subtype == "public_voice" and public_anchor_count >= 1:
        public_voice_overlap_delta = round(career_confidence, 4)

    mercury_presence = 0.20
    self_link_support = min(0.18, speech_self_link_strength)
    mind_route_support = min(
        0.18,
        speech_mind_route_strength
        + (0.03 if saturn_on_mind_route else 0.0)
        + (0.03 if uranus_on_mind_route else 0.0),
    )
    aspect_support = min(0.10, 0.03 * len(mercury_aspect_refs))
    subtype_coherence = min(0.16, top_score / 3.0)
    speech_stack_support = 0.0
    if subtype == "speech_identity_spine":
        speech_stack_support = min(0.08, speech_combined_bonus)
    structure_disruption_support = 0.0
    if subtype == "structured_disruptive_mind":
        structure_disruption_support = min(0.12, (structural_signal + disruptive_signal) / 4.0)
    base_confidence = (
        mercury_presence
        + self_link_support
        + mind_route_support
        + aspect_support
        + subtype_coherence
        + speech_stack_support
        + structure_disruption_support
    )
    if (
        career_subtype == "public_voice"
        and public_anchor_count >= 1
        and independent_mind_support_count <= 3
        and career_confidence >= (base_confidence + 0.18)
    ):
        career_overlap_penalty = 0.02
        career_overlap_guard = "career_route_primary"

    confidence = round(
        min(
            0.94,
            max(
                0.0,
                base_confidence
                - career_overlap_penalty,
            ),
        ),
        4,
    )
    if confidence < 0.6:
        return None

    if subtype == "speech_identity_spine":
        lived_scene = "Kendini çoğu zaman ne söylediğin kadar, o cümleyi hangi tonla kurduğun üzerinden de gösterirsin."
        atoms = [
            "bir cümleyi kurarken tonunu özellikle seçmen",
            "ne söyleyeceğini kadar nasıl söyleyeceğini de tartman",
        ]
        direct_meaning = "Merkür, kimlik hattına değen düşünce ve konuşma biçimini generic mind fallback'ten daha spesifik taşıyor."
        gift = "Düşünce ve konuşma biçiminin kimlikte nasıl görünür olduğunu ayırabilmek."
        inner_tension = "Kendini anlatma biçimin, doğrudan kimlik ifadesiyle düşünceyi düzenleme ihtiyacını aynı anda taşıyabilir."
        growth = "Merkür'ün söz, ton ve karar dili üzerinden kurduğu omurgayı daha bilinçli kullanmak."
        domain_reason = [
            "Mercury thought/speech route",
            "Mercury self-link",
        ]
        if mercury_house in {3, 9, 11}:
            domain_reason.append("3H/9H/11H mind-route support")
        if third_route_is_mercurial or ninth_route_is_mercurial:
            domain_reason.append("Mercury-owned 3H/9H route")
    else:
        lived_scene = "Zihnin bir yandan cümleyi doğru yere oturtmak isterken, başka bir yandan alışılmış bağlantıyı bir anda kırabilir."
        atoms = [
            "bir fikri önce iskelete oturtup sonra beklenmedik bir açıyla çevirmen",
            "cümleyi kurarken hem düzeni hem sıçramayı aynı anda taşıman",
        ]
        direct_meaning = "Merkür hattı, yapı kuran ve bağlantıyı beklenmedik biçimde kıran zihinsel işleyişi tek bir generic mind etiketinden daha net taşıyor."
        gift = "Yapı ile sıçrama arasındaki zihinsel ritmi ayırabilmek."
        inner_tension = "Zihnin bir yanıyla düzen kurmak isterken, başka bir yanıyla eski bağlantıyı kırıp yeni bir hat açabilir."
        growth = "Satürnce yapı ile Uranüsçe kopuşun aynı zihinsel hatta nasıl birlikte çalıştığını görmek."
        domain_reason = [
            "Mercury thought/speech route",
            "Saturn structure on mind route",
            "Uranus disruption on mind route",
        ]
        if mercury_on_identity_spine:
            domain_reason.append("speech-identity spillover stays mind-owned")

    technical_anchors = [_planet_chip("mercury", mercury_item)]
    if subtype == "speech_identity_spine":
        if mercury_sun_conjunction:
            technical_anchors.append("Mercury conjunction Sun")
        if mercury_asc_conjunction:
            technical_anchors.append("Mercury conjunction Ascendant")
        if mercury_chart_ruler:
            technical_anchors.append("Mercury chart ruler")
    else:
        if saturn_house in {3, 9}:
            technical_anchors.append(_planet_chip("saturn", saturn_item))
        if uranus_house in {3, 9}:
            technical_anchors.append(_planet_chip("uranus", uranus_item))
        if mercury_saturn_aspect:
            technical_anchors.append("Mercury major aspect Saturn")
        if mercury_uranus_aspect:
            technical_anchors.append("Mercury major aspect Uranus")
    technical_anchors.extend(item["label"] for item in mercury_aspect_refs[:2])
    technical_anchors = [item for item in technical_anchors if item]

    source_evidence_ids = [
        f"composed:mercury:sign:{mercury_sign}",
        f"composed:mercury:house:{mercury_house}",
    ]
    if third_sign:
        source_evidence_ids.append(f"composed:mercury:3h_cusp:{third_sign}")
    if ninth_sign:
        source_evidence_ids.append(f"composed:mercury:9h_cusp:{ninth_sign}")
    if mercury_sun_conjunction:
        source_evidence_ids.append("composed:mercury:self_link:sun_conjunction")
    if mercury_asc_conjunction:
        source_evidence_ids.append("composed:mercury:self_link:asc_conjunction")
    if saturn_on_mind_route:
        source_evidence_ids.append("composed:mercury:structure:saturn_route")
    if uranus_on_mind_route:
        source_evidence_ids.append("composed:mercury:disruption:uranus_route")

    evidence_trace = {
        "primitive_facts": {
            "placements": [
                {"planet": "Mercury", "sign": mercury_sign, "house": mercury_house, "retrograde": bool(mercury_item.get("retrograde"))},
                *(
                    [{"planet": "Sun", "sign": str(sun_item.get("sign") or "").strip().lower(), "house": sun_house}]
                    if sun_item
                    else []
                ),
                *(
                    [{"planet": "Saturn", "sign": saturn_sign, "house": saturn_house}]
                    if saturn_item
                    else []
                ),
                *(
                    [{"planet": "Uranus", "sign": uranus_sign, "house": uranus_house}]
                    if uranus_item
                    else []
                ),
            ],
            "angles": [
                *([{"angle": "ASC", "sign": asc_sign.title()}] if asc_sign else []),
                *([{"angle": "MC", "sign": mc_sign.title()}] if mc_sign else []),
            ],
        },
        "discovery_routes": ["mercury_signature"],
        "family_inputs": ["Mercury", "3H_9H_route", "Mercury_self_link", "Saturn_structure", "Uranus_disruption"],
        "subtype_inputs": [subtype],
        "subtype_signal_scores": {k: round(v, 4) for k, v in subtype_signals.items()},
        "career_overlap_guard": career_overlap_guard,
        "career_subtype_at_overlap_check": career_subtype or "",
        "cross_family_overlap": [],
    }

    meta = {
        "title": "Merkür imzası composed semantic adayı",
        "locale": locale,
        "auxiliary": False,
        "inventory_variant": "composed_semantic_v0_9c",
        "v0_9_composed": True,
        "v0_9_family": "mercury_signature",
        "v0_9c_composed": True,
        "debug_only": True,
        "non_public_discovery": True,
        "source_type": "composed_semantic",
        "career_overlap_guard": career_overlap_guard or "none",
        "public_anchor_count": public_anchor_count,
        "independent_mind_support_count": independent_mind_support_count,
    }
    if runner_up_subtype and runner_up_score_delta < 0.04:
        meta["runner_up_subtype"] = runner_up_subtype
        meta["runner_up_score"] = round(runner_up_score, 4)
        meta["runner_up_score_delta"] = runner_up_score_delta

    return _composed_candidate_to_packet(
        ComposedSemanticCandidateV1(
            id=packet_id,
            family="mercury_signature",
            subtype=subtype,
            source_type="composed_semantic",
            domain="mind",
            promise_type="mind_style",
            domain_reason=domain_reason,
            public_job="debug_only",
            confidence=confidence,
            confidence_tier=_confidence_tier(confidence),
            chart_facts_match=True,
            technical_anchors=technical_anchors,
            source_evidence_ids=source_evidence_ids,
            evidence_trace=evidence_trace,
            direct_meaning=direct_meaning,
            lived_scene=lived_scene,
            lived_scene_atoms=atoms,
            gift=gift,
            inner_tension=inner_tension,
            growth_direction=growth,
            avoid_readings=[
                "Do not reduce mercury signature to generic intelligence.",
                "Do not let career/public-role meaning take ownership of this route.",
                "Do not solve MC-Cancer public voice or 9H belief sensitivity here.",
            ],
            projection_hints={
                "surfaces": ["debug_only"],
                "priority": confidence,
                "auxiliary": False,
                "opening_strategy": "debug_only",
            },
            scoring_breakdown={
                "speech_self_link_strength": round(speech_self_link_strength, 4),
                "speech_mind_route_strength": round(speech_mind_route_strength, 4),
                "structural_signal": round(structural_signal, 4),
                "disruptive_signal": round(disruptive_signal, 4),
                "public_anchor_count": round(float(public_anchor_count), 4),
                "independent_mind_support_count": round(float(independent_mind_support_count), 4),
                "speech_combined_bonus": round(speech_combined_bonus, 4),
                "speech_stack_support": round(speech_stack_support, 4),
                "career_overlap_penalty": round(career_overlap_penalty, 4),
                "career_public_voice_confidence": round(career_confidence, 4),
                "career_public_voice_overlap_delta": round(max(0.0, career_confidence - base_confidence), 4),
                "subtype_coherence": round(subtype_coherence, 4),
                "structure_disruption_support": round(structure_disruption_support, 4),
            },
            matched_archetypes=[],
            public_eligibility={
                "debug_eligible": True,
                "detail_eligible": False,
                "public_support_eligible": False,
                "public_main_eligible": False,
                "reason_codes": [
                    "v0_9c_debug_only",
                    "public_main_flag_required",
                    "detail_rollout_not_enabled_in_v0_9c",
                ],
            },
            meta=meta,
        )
    )


# ---------------------------------------------------------------------------
# v0.10 composed-semantic family: axis_2h_8h
#
# Debug-only first cut. Turns the previously discovery-only
# `discovery_axis_2h_8h_gap` signal into a properly-typed composed
# candidate with seven subtypes:
#
#   self_worth_foundation
#   shared_trust_exchange
#   dependency_autonomy_tension
#   intimacy_resource_fusion
#   value_transformation
#   resource_boundary
#   embodied_security
#
# Gates are identical in shape to v0.9b families:
#   * master flag default-false (ENABLE_NATAL_COMPOSED_SEMANTICS_AXIS_2H_8H_V0_10)
#   * always emits public_job="debug_only"
#   * always emits public_main_eligible=False / public_support_eligible=False
#   * detail_eligible flips True only when the shared detail-support flag
#     (ENABLE_NATAL_COMPOSED_SEMANTICS_AXIS_2H_8H_DETAIL_SUPPORT) is also on
#   * confidence floor 0.60, cap 0.94
#   * fallback subtype `self_worth_foundation` carries the calibrated
#     default-fallback penalty (0.12 margin-fail / 0.15 no-signal)
# ---------------------------------------------------------------------------


def _build_axis_2h_8h_candidates(
    *,
    planet_map: Mapping[str, Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]] | None,
    house_rulers: Mapping[str, Any],
    locale: str,
    existing_ids: set[str],
) -> dict[str, Any] | None:
    packet_id = "composed_axis_2h_8h_v0_10"
    if packet_id in existing_ids:
        return None

    two_h_cusp_sign = _house_cusp_sign(house_rulers, 2)
    eight_h_cusp_sign = _house_cusp_sign(house_rulers, 8)
    if not two_h_cusp_sign and not eight_h_cusp_sign:
        return None

    two_h_ruler = _sign_ruler(two_h_cusp_sign) if two_h_cusp_sign else ""
    eight_h_ruler = _sign_ruler(eight_h_cusp_sign) if eight_h_cusp_sign else ""
    two_h_ruler_item = _lookup_planet_entry(planet_map, two_h_ruler) if two_h_ruler else {}
    eight_h_ruler_item = _lookup_planet_entry(planet_map, eight_h_ruler) if eight_h_ruler else {}
    two_h_ruler_house = int(two_h_ruler_item.get("house") or 0) if two_h_ruler_item else 0
    eight_h_ruler_house = int(eight_h_ruler_item.get("house") or 0) if eight_h_ruler_item else 0
    two_h_ruler_sign = str(two_h_ruler_item.get("sign") or "").strip().lower() if two_h_ruler_item else ""

    two_h_planets = _house_planet_names(planet_map, 2)
    eight_h_planets = _house_planet_names(planet_map, 8)

    north_node_item = _lookup_planet_entry(planet_map, "north node")
    north_node_house = int(north_node_item.get("house") or 0) if north_node_item else 0
    south_node_house = ((north_node_house - 1 + 6) % 12) + 1 if north_node_house else 0

    sun_item = _lookup_planet_entry(planet_map, "sun")
    moon_item = _lookup_planet_entry(planet_map, "moon")
    sun_house = int(sun_item.get("house") or 0) if sun_item else 0
    moon_house = int(moon_item.get("house") or 0) if moon_item else 0

    two_h_activated = (
        bool(two_h_planets)
        or north_node_house == 2
        or south_node_house == 2
        or eight_h_ruler_house == 2
    )
    eight_h_activated = (
        bool(eight_h_planets)
        or north_node_house == 8
        or south_node_house == 8
        or two_h_ruler_house == 8
    )
    if not (two_h_activated or eight_h_activated):
        return None

    # ---- Supporting-signal tally (gate: >= 2 unless Sun/Moon/Node on axis) ----
    supporting_signals: list[str] = []
    if two_h_planets:
        supporting_signals.append("2h_planet")
    if eight_h_planets:
        supporting_signals.append("8h_planet")
    if north_node_house in {2, 8}:
        supporting_signals.append("node_on_axis")
    if two_h_ruler_house == 8 and two_h_ruler:
        supporting_signals.append("2h_ruler_in_8h")
    if eight_h_ruler_house == 2 and eight_h_ruler:
        supporting_signals.append("8h_ruler_in_2h")
    if sun_house in {2, 8}:
        supporting_signals.append("luminary_on_axis_sun")
    if moon_house in {2, 8}:
        supporting_signals.append("luminary_on_axis_moon")
    if two_h_ruler and _has_any_aspect_type(
        aspects, two_h_ruler, "pluto", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        supporting_signals.append("2h_ruler_pluto_aspect")
    if eight_h_ruler and _has_any_aspect_type(
        aspects, eight_h_ruler, "pluto", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        supporting_signals.append("8h_ruler_pluto_aspect")

    # v0.10.0.1: extend "load-bearing planet on axis" gate to include
    # Pluto and Saturn — these planets ARE the axis's primary
    # transformation / boundary significators, so their presence on the
    # axis should single-handedly satisfy the supporting-signal gate.
    luminary_or_node_on_axis = (
        sun_house in {2, 8}
        or moon_house in {2, 8}
        or north_node_house in {2, 8}
        or "pluto" in two_h_planets
        or "pluto" in eight_h_planets
        or "saturn" in two_h_planets
        or "saturn" in eight_h_planets
    )
    if len(supporting_signals) < 2 and not luminary_or_node_on_axis:
        return None

    # ---- Subtype scoring channels ----
    subtype_signals: dict[str, float] = {}

    def _bump(subtype: str, amount: float) -> None:
        subtype_signals[subtype] = subtype_signals.get(subtype, 0.0) + amount

    # self_worth_foundation — own ground, own value.
    # v0.10.0.1: relax the "8H empty" requirement to "2H heavier than 8H"
    # so charts with any 8H content still qualify when 2H is the
    # dominant pole. Multi-planet 2H stelliums get an explicit bonus.
    if two_h_planets and len(two_h_planets) > len(eight_h_planets):
        _bump("self_worth_foundation", 0.12)
    if two_h_planets and not eight_h_planets:
        _bump("self_worth_foundation", 0.08)
    if len(two_h_planets) >= 2:
        _bump("self_worth_foundation", 0.06)
    for sig in ("sun", "moon", "venus", "jupiter", "saturn"):
        if sig in two_h_planets:
            _bump("self_worth_foundation", 0.04)
            break
    if two_h_ruler_house in {1, 2, 4, 10, 11}:
        _bump("self_worth_foundation", 0.06)
    if north_node_house == 2:
        _bump("self_worth_foundation", 0.04)

    # shared_trust_exchange — BOTH sides activated by direct planets,
    # balanced. v0.10.0.1: reduced the Node-on-axis bonus from 0.10 to
    # 0.04 (Node + heavy opposite pole is primarily the
    # dependency_autonomy_tension signal; shared_trust still picks up a
    # small Node sensitivity for charts where the Node isn't carrying
    # the dependency reading).
    if two_h_planets and eight_h_planets:
        _bump("shared_trust_exchange", 0.14)
    elif two_h_activated and eight_h_activated:
        _bump("shared_trust_exchange", 0.08)
    if north_node_house in {2, 8}:
        _bump("shared_trust_exchange", 0.04)
    if two_h_ruler_house == 8 or eight_h_ruler_house == 2:
        _bump("shared_trust_exchange", 0.08)

    # dependency_autonomy_tension — Node on one pole, weight on the other.
    # v0.10.0.1: stronger weight when Node + opposite-pole significator
    # (Venus / Mars / Saturn / Pluto / Jupiter) is present — previously
    # the channel was overtaken by shared_trust_exchange on these charts.
    eight_h_planet_count = len(eight_h_planets)
    two_h_planet_count = len(two_h_planets)
    if north_node_house == 2 and (eight_h_planet_count >= 2 or sun_house == 8 or moon_house == 8):
        _bump("dependency_autonomy_tension", 0.20)
    if north_node_house == 2 and any(p in eight_h_planets for p in ("venus", "mars", "saturn", "pluto", "jupiter")):
        _bump("dependency_autonomy_tension", 0.08)
    if north_node_house == 8 and (two_h_planet_count >= 2 or sun_house == 2 or moon_house == 2):
        _bump("dependency_autonomy_tension", 0.18)
    if north_node_house == 8 and any(p in two_h_planets for p in ("venus", "mars", "saturn", "pluto", "jupiter")):
        _bump("dependency_autonomy_tension", 0.08)
    if _has_aspect(aspects or [], "sun", "north node", "opposition") and sun_house in {2, 8}:
        _bump("dependency_autonomy_tension", 0.06)
    if _has_aspect(aspects or [], "moon", "north node", "opposition") and moon_house in {2, 8}:
        _bump("dependency_autonomy_tension", 0.04)

    # intimacy_resource_fusion — 8H planets, esp. Venus/Mars/Moon/Pluto;
    # water on axis; Venus/Mars/Moon-Pluto contacts; aspects to 8H ruler.
    # v0.10.0.1: base bump raised from 0.06 to 0.10, and Mars-Pluto /
    # Moon-Pluto contacts now contribute (previously only Venus-Pluto).
    intimacy_8h = [p for p in eight_h_planets if p in {"venus", "mars", "moon", "pluto"}]
    if intimacy_8h:
        _bump(
            "intimacy_resource_fusion",
            0.10 + 0.04 * min(len(intimacy_8h), 3),
        )
    if _has_any_aspect_type(
        aspects, "venus", "pluto", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("intimacy_resource_fusion", 0.06)
    if _has_any_aspect_type(
        aspects, "mars", "pluto", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("intimacy_resource_fusion", 0.04)
    if _has_any_aspect_type(
        aspects, "moon", "pluto", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("intimacy_resource_fusion", 0.04)
    if eight_h_ruler and any(
        _has_any_aspect_type(
            aspects, sig, eight_h_ruler, _SOFT_ASPECT_TYPES + _HARD_ASPECT_TYPES
        )
        for sig in ("venus", "mars", "moon")
    ):
        _bump("intimacy_resource_fusion", 0.04)
    if eight_h_cusp_sign in _WATER_SIGNS:
        _bump("intimacy_resource_fusion", 0.04)

    # value_transformation — Pluto on axis or ruling the axis; aspects
    # to axis ruler / luminary; Scorpio on 2H/8H cusp.
    # v0.10.0.1: expanded detection — Pluto ruling 2H/8H now contributes
    # explicitly; Pluto-ruler / Pluto-luminary contacts no longer require
    # a hard aspect; Scorpio cusp now contributes a small bump.
    pluto_item = _lookup_planet_entry(planet_map, "pluto")
    pluto_house = int(pluto_item.get("house") or 0) if pluto_item else 0
    if "pluto" in two_h_planets or "pluto" in eight_h_planets:
        _bump("value_transformation", 0.16)
    if two_h_ruler == "pluto" or eight_h_ruler == "pluto":
        _bump("value_transformation", 0.10)
        if pluto_house in {1, 4, 7, 8, 10, 11}:
            _bump("value_transformation", 0.04)
    if two_h_ruler and _has_any_aspect_type(
        aspects, two_h_ruler, "pluto", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("value_transformation", 0.08)
    if eight_h_ruler and _has_any_aspect_type(
        aspects, eight_h_ruler, "pluto", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("value_transformation", 0.08)
    if sun_house in {2, 8} and _has_any_aspect_type(
        aspects, "sun", "pluto", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("value_transformation", 0.06)
    if moon_house in {2, 8} and _has_any_aspect_type(
        aspects, "moon", "pluto", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("value_transformation", 0.06)
    if two_h_cusp_sign == "scorpio" or eight_h_cusp_sign == "scorpio":
        _bump("value_transformation", 0.06)
    if _has_aspect(aspects or [], "jupiter", "pluto", "square") and (
        sun_house in {2, 8} or "jupiter" in eight_h_planets or "jupiter" in two_h_planets
    ):
        _bump("value_transformation", 0.04)

    # resource_boundary — Saturn on axis; Saturn rules 2H/8H; Saturn
    # aspects to axis ruler; Saturn-Venus/Saturn-Moon in 2H/8H context.
    # v0.10.0.1: explicit aspect-to-axis-ruler bumps; Capricorn/Aquarius
    # cusp + Saturn-on-axis combo gets an additional small bump.
    if "saturn" in two_h_planets or "saturn" in eight_h_planets:
        _bump("resource_boundary", 0.16)
    if two_h_ruler == "saturn" or eight_h_ruler == "saturn":
        _bump("resource_boundary", 0.08)
    if two_h_ruler and two_h_ruler != "saturn" and _has_any_aspect_type(
        aspects, "saturn", two_h_ruler, _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("resource_boundary", 0.06)
    if eight_h_ruler and eight_h_ruler != "saturn" and _has_any_aspect_type(
        aspects, "saturn", eight_h_ruler, _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("resource_boundary", 0.06)
    if ("venus" in two_h_planets or "venus" in eight_h_planets) and _has_any_aspect_type(
        aspects, "saturn", "venus", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("resource_boundary", 0.06)
    if ("moon" in two_h_planets or "moon" in eight_h_planets) and _has_any_aspect_type(
        aspects, "saturn", "moon", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("resource_boundary", 0.06)
    if ("saturn" in two_h_planets or "saturn" in eight_h_planets) and (
        two_h_cusp_sign in {"capricorn", "aquarius"}
        or eight_h_cusp_sign in {"capricorn", "aquarius"}
    ):
        _bump("resource_boundary", 0.04)
    # Generic Saturn-Venus / Saturn-Moon contact (lower weight, kept for
    # backward compatibility with charts where the contact is present but
    # neither planet sits on the axis).
    if _has_any_aspect_type(
        aspects, "saturn", "venus", _HARD_ASPECT_TYPES + _SOFT_ASPECT_TYPES
    ):
        _bump("resource_boundary", 0.02)
    if _has_any_aspect_type(aspects, "saturn", "moon", _HARD_ASPECT_TYPES):
        _bump("resource_boundary", 0.02)

    # embodied_security — earth on 2H, earth ruler, body/material
    # support from Venus/Moon/Saturn in 2H. No Pluto-crisis ingredient on
    # the axis, no 8H heat.
    # v0.10.0.1: explicit Venus/Moon/Saturn-in-2H bumps + 2H-ruler-in-
    # stable-earth-house bump.
    if two_h_cusp_sign in _EARTH_SIGNS:
        _bump("embodied_security", 0.12)
    if two_h_cusp_sign == "taurus":
        _bump("embodied_security", 0.06)
    if two_h_ruler_sign in _EARTH_SIGNS:
        _bump("embodied_security", 0.06)
    for sig in ("venus", "moon", "saturn"):
        if sig in two_h_planets:
            _bump("embodied_security", 0.04)
    if two_h_ruler_sign in _EARTH_SIGNS and two_h_ruler_house in {2, 4, 10}:
        _bump("embodied_security", 0.04)
    if not eight_h_planets and "pluto" not in two_h_planets and two_h_planets:
        _bump("embodied_security", 0.04)

    # ---- Subtype selection (margin >= 0.04 vs runner-up) ----
    # v0.10.0.1: margin-fail fallback only fires when the top subtype's
    # signal is weak (< 0.15). When the top score is genuinely high but
    # the runner-up is close, we trust the winning subtype — otherwise
    # legitimate close-call winners (e.g. fix04's self_worth path with
    # signal ~0.26) were being misclassified as "default fallback" with
    # the penalty applied.
    ordered = sorted(subtype_signals.items(), key=lambda kv: kv[1], reverse=True)
    is_subtype_default_fallback_path = False
    if not ordered or ordered[0][1] <= 0.0:
        subtype = "self_worth_foundation"
        subtype_penalty = 0.15
        subtype_bonus = 0.0
        is_subtype_default_fallback_path = True
    else:
        top_subtype, top_score = ordered[0]
        runner_up_score = ordered[1][1] if len(ordered) > 1 else 0.0
        if top_score - runner_up_score < 0.04 and top_score < 0.15:
            subtype = "self_worth_foundation"
            subtype_penalty = 0.12
            subtype_bonus = 0.0
            is_subtype_default_fallback_path = True
        else:
            subtype = top_subtype
            subtype_penalty = 0.0
            subtype_bonus = min(0.05, top_score / 4.0)

    # ---- Confidence scoring ----
    two_h_activation_score = 0.05 if two_h_activated else 0.0
    if two_h_planets:
        two_h_activation_score += min(0.10, 0.04 * len(two_h_planets))
    eight_h_activation_score = 0.05 if eight_h_activated else 0.0
    if eight_h_planets:
        eight_h_activation_score += min(0.15, 0.05 * len(eight_h_planets))
    node_on_axis_score = 0.20 if north_node_house in {2, 8} else 0.0
    luminary_on_axis_score = 0.0
    if sun_house in {2, 8}:
        luminary_on_axis_score += 0.10
    if moon_house in {2, 8}:
        luminary_on_axis_score += 0.06
    luminary_on_axis_score = min(0.15, luminary_on_axis_score)
    significator_on_axis_score = 0.0
    for sig in ("venus", "mars", "saturn", "pluto", "jupiter"):
        if sig in two_h_planets or sig in eight_h_planets:
            significator_on_axis_score += 0.04
    significator_on_axis_score = min(0.15, significator_on_axis_score)
    ruler_route_score = 0.0
    if two_h_ruler_house == 8:
        ruler_route_score += 0.06
    if eight_h_ruler_house == 2:
        ruler_route_score += 0.06
    ruler_route_score = min(0.10, ruler_route_score)
    hard_aspect_to_axis_score = 0.0
    for ruler in (two_h_ruler, eight_h_ruler):
        if ruler and _has_any_aspect_type(aspects, ruler, "pluto", _HARD_ASPECT_TYPES):
            hard_aspect_to_axis_score += 0.04
        if ruler and _has_any_aspect_type(aspects, ruler, "saturn", _HARD_ASPECT_TYPES):
            hard_aspect_to_axis_score += 0.03
    hard_aspect_to_axis_score = min(0.10, hard_aspect_to_axis_score)
    subtype_coherence = min(0.05, (ordered[0][1] if ordered else 0.0) / 4.0)

    confidence = round(
        min(
            0.94,
            max(
                0.0,
                two_h_activation_score
                + eight_h_activation_score
                + node_on_axis_score
                + luminary_on_axis_score
                + significator_on_axis_score
                + ruler_route_score
                + hard_aspect_to_axis_score
                + subtype_coherence
                + subtype_bonus
                - subtype_penalty,
            ),
        ),
        4,
    )
    if confidence < 0.6:
        return None

    # ---- TR copy seeds (debug-only; never reaches a public surface) ----
    subtype_copy = {
        "self_worth_foundation": (
            "Kendi değerin ve kaynakların bu hattın merkezinde yer alıyor; sahip olduğun zeminden taşınan bir güven biçimi var.",
            ["kendi ihtiyaçlarını net tanıman", "değer hissini içeride kurman"],
        ),
        "shared_trust_exchange": (
            "Derin bağlar ve ortak alanlar seni güçlü biçimde etkileyebilir; ama gelişim yönün bu yoğunluğun içinde kendi değerini ve zeminini koruyabilmekten geçer.",
            ["paylaşırken kendini kaybetmemen", "güven ve yakınlık alanında kendi ihtiyacını ayırman"],
        ),
        "dependency_autonomy_tension": (
            "Bir yanın derin bağ kurmak isterken, başka bir yanın kendi değerini ve sınırını daha net tutmaya çalışabilir.",
            ["başkasının duygusuna karışırken kendi ihtiyacını ayırman", "ortak alanda kendi zeminini koruman"],
        ),
        "intimacy_resource_fusion": (
            "Yakınlık ve ortak kaynaklar bu hatta birbirine bağlı çalışıyor; bir bağ derinleştiğinde paylaşılan alan da hareketleniyor.",
            ["yakınlık ve paylaşımın birlikte yoğunlaşması", "güveni açtığında ortak alanın da derinleşmesi"],
        ),
        "value_transformation": (
            "Kendi değerin sabit bir nokta değil; kriz, paylaşım veya derin bağ deneyimleriyle dönüşerek netleşiyor.",
            ["değer hissinin deneyimle yeniden kurulması", "yoğun bağdan sonra kendi zeminini yeniden tanıman"],
        ),
        "resource_boundary": (
            "Bu hat sana nerede verip, nerede aldığını ve neyin senin neyin ortak olduğunu daha net ayırmayı öğretiyor.",
            ["paylaşım sınırını net çekmen", "verirken ve alırken ölçüyü koruyabilmen"],
        ),
        "embodied_security": (
            "Güven duygusu sende bedenle, sağlam zeminle ve tutarlı bir maddi/duygusal alanla birlikte çalışıyor.",
            ["istikrarın güven kaynağı olması", "değeri somut zemin üzerinden hissetmen"],
        ),
    }
    lived_scene, atoms = subtype_copy[subtype]

    direct_meaning = "İkinci ve sekizinci ev rotaları birlikte kendi değer, paylaşım ve güven hattını generic 'para/kaynak' okumasından daha spesifik biçimde taşıyor."
    gift = "Derin bağ ve ortak alan içinde kendi zeminini koruyabilme kapasitesi; paylaşımı kaybolmadan yapabilmek."
    inner_tension = "Bir yanın derinleşmek ve paylaşmak isterken, başka bir yanın kendi değerini ve sınırını daha net taşımaya çağırabilir."
    growth = "Paylaşırken kendini kaybetmeden, güven ve yakınlığı kendi zemininle birlikte kurmak."

    domain_reason: list[str] = []
    if two_h_planets or north_node_house == 2 or eight_h_ruler_house == 2:
        domain_reason.append("2H activation")
    if eight_h_planets or north_node_house == 8 or two_h_ruler_house == 8:
        domain_reason.append("8H activation")
    if north_node_house in {2, 8}:
        domain_reason.append("Node on 2H/8H axis")
    if two_h_ruler_house == 8:
        domain_reason.append("2H ruler in 8H")
    if eight_h_ruler_house == 2:
        domain_reason.append("8H ruler in 2H")
    if sun_house in {2, 8}:
        domain_reason.append("Sun on 2H/8H axis")
    if "pluto" in two_h_planets or "pluto" in eight_h_planets:
        domain_reason.append("Pluto on 2H/8H axis")
    if "saturn" in two_h_planets or "saturn" in eight_h_planets:
        domain_reason.append("Saturn on 2H/8H axis")

    technical_anchors: list[str] = []
    if two_h_cusp_sign:
        technical_anchors.append(f"2H cusp {two_h_cusp_sign.title()}")
    if eight_h_cusp_sign:
        technical_anchors.append(f"8H cusp {eight_h_cusp_sign.title()}")
    if two_h_ruler and two_h_ruler_item:
        technical_anchors.append(_planet_chip(two_h_ruler, two_h_ruler_item))
    if eight_h_ruler and eight_h_ruler_item:
        technical_anchors.append(_planet_chip(eight_h_ruler, eight_h_ruler_item))
    for planet in two_h_planets[:3]:
        technical_anchors.append(f"{planet.title()} · 2. ev")
    for planet in eight_h_planets[:3]:
        technical_anchors.append(f"{planet.title()} · 8. ev")
    if north_node_house in {2, 8} and north_node_item:
        technical_anchors.append(_planet_chip("north node", north_node_item))

    source_evidence_ids = [
        f"composed:axis_2h_8h:2h_cusp:{two_h_cusp_sign}",
        f"composed:axis_2h_8h:8h_cusp:{eight_h_cusp_sign}",
        *[f"composed:axis_2h_8h:2h:{planet}" for planet in two_h_planets[:4]],
        *[f"composed:axis_2h_8h:8h:{planet}" for planet in eight_h_planets[:4]],
    ]

    evidence_trace = {
        "primitive_facts": {
            "placements": [
                *(
                    [
                        {
                            "planet": planet.title(),
                            "sign": str(
                                (_lookup_planet_entry(planet_map, planet) or {}).get("sign") or ""
                            ),
                            "house": 2,
                        }
                        for planet in two_h_planets[:4]
                    ]
                ),
                *(
                    [
                        {
                            "planet": planet.title(),
                            "sign": str(
                                (_lookup_planet_entry(planet_map, planet) or {}).get("sign") or ""
                            ),
                            "house": 8,
                        }
                        for planet in eight_h_planets[:4]
                    ]
                ),
                *(
                    [
                        {
                            "planet": "North Node",
                            "sign": str(north_node_item.get("sign") or ""),
                            "house": north_node_house,
                        }
                    ]
                    if north_node_house in {2, 8} and north_node_item
                    else []
                ),
            ],
            "angles": [],
        },
        "discovery_routes": ["axis_2h_8h"],
        "family_inputs": [
            "2H_cusp",
            "8H_cusp",
            "2H_ruler",
            "8H_ruler",
            "2H_planets",
            "8H_planets",
            "Node_axis",
            "luminary_on_axis",
        ],
        "subtype_inputs": [subtype],
        "subtype_signal_scores": {k: round(v, 4) for k, v in subtype_signals.items()},
        "supporting_signals": supporting_signals,
        "cross_family_overlap": [],
    }

    detail_support_flag_enabled = _env_enabled(
        "ENABLE_NATAL_COMPOSED_SEMANTICS_AXIS_2H_8H_DETAIL_SUPPORT"
    )
    detail_eligible = detail_support_flag_enabled and confidence >= 0.75

    return _composed_candidate_to_packet(
        ComposedSemanticCandidateV1(
            id=packet_id,
            family="axis_2h_8h",
            subtype=subtype,
            source_type="composed_semantic",
            domain="value_resource_axis",
            promise_type="axis_2h_8h_signature",
            domain_reason=domain_reason,
            public_job="debug_only",
            confidence=confidence,
            confidence_tier=_confidence_tier(confidence),
            chart_facts_match=True,
            technical_anchors=[item for item in technical_anchors if item],
            source_evidence_ids=source_evidence_ids,
            evidence_trace=evidence_trace,
            direct_meaning=direct_meaning,
            lived_scene=lived_scene,
            lived_scene_atoms=atoms,
            gift=gift,
            inner_tension=inner_tension,
            growth_direction=growth,
            avoid_readings=[
                "Do not collapse this axis into 'para sorunu' / 'maddi kriz' readings.",
                "Do not assert dependency or trauma without exact chart evidence.",
                "Do not let generic 'özdeğerin önemlidir' copy own this axis.",
                "Do not reduce 2H/8H meaning to relationship-only framing.",
            ],
            projection_hints={
                "surfaces": ["debug_only"],
                "priority": confidence,
                "auxiliary": False,
                "opening_strategy": "debug_only",
            },
            scoring_breakdown={
                "two_h_activation": round(two_h_activation_score, 4),
                "eight_h_activation": round(eight_h_activation_score, 4),
                "node_on_axis": round(node_on_axis_score, 4),
                "luminary_on_axis": round(luminary_on_axis_score, 4),
                "significator_on_axis": round(significator_on_axis_score, 4),
                "ruler_route": round(ruler_route_score, 4),
                "hard_aspect_to_axis": round(hard_aspect_to_axis_score, 4),
                "subtype_coherence": round(subtype_coherence, 4),
                "subtype_bonus": round(subtype_bonus, 4),
                "subtype_penalty": round(subtype_penalty, 4),
            },
            matched_archetypes=[],
            public_eligibility={
                "debug_eligible": True,
                "detail_eligible": detail_eligible,
                "public_support_eligible": False,
                "public_main_eligible": False,
                "reason_codes": [
                    "v0_10_debug_only",
                    "public_main_flag_required",
                    *(
                        ["v0_10_axis_2h_8h_detail_support_flag_enabled"]
                        if detail_eligible
                        else ["v0_10_axis_2h_8h_detail_support_flag_disabled_or_low_confidence"]
                    ),
                ],
            },
            meta={
                "title": "2.ev / 8.ev ekseni composed semantic adayı",
                "locale": locale,
                "auxiliary": False,
                "inventory_variant": "composed_semantic_v0_10",
                "v0_9_composed": True,
                "v0_9_family": "axis_2h_8h",
                "v0_10_composed": True,
                "debug_only": True,
                "non_public_discovery": True,
                "source_type": "composed_semantic",
                "subtype_default_fallback": is_subtype_default_fallback_path,
                "supporting_signal_count": len(supporting_signals),
            },
        )
    )


def _career_visible_public_anchor_count(
    *,
    career_ruler: str,
    ruler_house: int,
    tenth_house_planets: Sequence[str],
) -> int:
    anchors: set[str] = set()
    if career_ruler == "mercury" and ruler_house in {10, 11}:
        anchors.add("mc_ruler_mercury_public")
    for planet in tenth_house_planets:
        clean = str(planet).strip().lower()
        if clean:
            anchors.add(f"10h_{clean}")
    return len(anchors)


def _public_voice_detail_intrinsic_eligibility(
    *,
    subtype: str,
    confidence: float,
    confidence_tier: str,
    chart_facts_match: bool,
    domain_reason: Sequence[str],
    evidence_trace: Mapping[str, Any],
    lived_scene: str,
    has_mercury_public_anchor: bool,
    career_ruler: str,
    ruler_house: int,
    tenth_house_planets: Sequence[str],
    visible_public_anchor_count: int,
) -> bool:
    if subtype != "public_voice":
        return False
    if confidence_tier != "high" or _safe_float(confidence, 0.0) < 0.88:
        return False
    if not chart_facts_match:
        return False
    required_domain_reason = {"MC route", "MC ruler involved", "10H planet"}
    if not required_domain_reason.issubset({str(item).strip() for item in domain_reason}):
        return False
    family_inputs = {
        str(item).strip()
        for item in (
            evidence_trace.get("family_inputs")
            if isinstance(evidence_trace.get("family_inputs"), Sequence)
            else []
        )
        if str(item).strip()
    }
    if not {"MC", "MC_ruler", "10H_planets"}.issubset(family_inputs):
        return False
    if not (
        has_mercury_public_anchor
        and (
            ("mercury" == str(career_ruler).strip().lower() and ruler_house in {10, 11})
            or any(str(planet).strip().lower() == "mercury" for planet in tenth_house_planets)
        )
    ):
        return False
    if visible_public_anchor_count < 2:
        return False
    lived_scene_lower = str(lived_scene or "").strip().lower()
    if not any(token in lived_scene_lower for token in ("konuş", "konum", "söz", "dış dünyada", "görünür")):
        return False
    if "yalnız görünürlük" in lived_scene_lower and "konuş" not in lived_scene_lower and "konum" not in lived_scene_lower:
        return False
    return True


def _composed_candidate_to_packet(candidate: ComposedSemanticCandidateV1) -> dict[str, Any]:
    payload = asdict(candidate)
    payload["theme_key"] = candidate.id
    payload["strength"] = round(max(0.01, min(0.95, candidate.confidence)), 4)
    payload["shadow_or_friction"] = candidate.inner_tension
    payload["voice_seeds"] = [candidate.direct_meaning]
    payload["avoid_phrases"] = sorted(_BANNED_PHRASES)
    payload["source_category_ids"] = [candidate.id]
    payload["source_thread_ids"] = []
    payload["source_section_ids"] = [candidate.id]
    meta = dict(candidate.meta)
    meta["confidence_tier"] = candidate.confidence_tier
    meta["public_eligibility"] = dict(candidate.public_eligibility)
    meta["domain_reason"] = list(candidate.domain_reason)
    meta["lived_scene_atoms"] = list(candidate.lived_scene_atoms)
    payload["meta"] = meta
    payload["matched_archetype_summaries"] = []
    return payload


def _confidence_tier(confidence: float) -> str:
    score = _safe_float(confidence, 0.0)
    if score >= 0.8:
        return "high"
    if score >= 0.65:
        return "medium"
    return "low"


def _lookup_planet_entry(
    planet_map: Mapping[str, Mapping[str, Any]],
    planet: str | None,
) -> dict[str, Any]:
    planet_key = str(planet or "").strip().lower()
    if not planet_key:
        return {}
    aliases = {
        "north node": ("north node", "northnode", "true node", "mean node", "node", "kuzey ay düğümü"),
        "south node": ("south node", "southnode", "güney ay düğümü"),
    }.get(planet_key, (planet_key,))
    return next((dict(planet_map.get(alias) or {}) for alias in aliases if planet_map.get(alias)), {})


def _sign_ruler(sign: str) -> str:
    return {
        "aries": "mars",
        "taurus": "venus",
        "gemini": "mercury",
        "cancer": "moon",
        "leo": "sun",
        "virgo": "mercury",
        "libra": "venus",
        "scorpio": "pluto",
        "sagittarius": "jupiter",
        "capricorn": "saturn",
        "aquarius": "uranus",
        "pisces": "neptune",
    }.get(str(sign or "").strip().lower(), "")


def _planet_chip(planet: str | None, item: Mapping[str, Any] | None) -> str:
    if not planet or not isinstance(item, Mapping) or not item:
        return ""
    sign = str(item.get("sign") or "").strip()
    house = int(item.get("house") or 0)
    return f"{str(planet).title()} · {sign} · {house}. ev"


def _candidate_ids_contain(existing_ids: set[str], *needles: str) -> bool:
    lowered_needles = [str(needle or "").strip().lower() for needle in needles if str(needle or "").strip()]
    if not lowered_needles:
        return False
    return any(any(needle in packet_id for needle in lowered_needles) for packet_id in existing_ids)


def _planet_in_house(
    planet_map: Mapping[str, Mapping[str, Any]],
    planet: str,
    house: int,
) -> bool:
    item = _lookup_planet_entry(planet_map, planet)
    return int(item.get("house") or 0) == int(house)


def _house_planet_names(
    planet_map: Mapping[str, Mapping[str, Any]],
    house: int,
) -> list[str]:
    names: list[str] = []
    for name, item in planet_map.items():
        if name in {"ascendant", "midheaven", "ic", "descendant", "fortune", "vertex"}:
            continue
        if int((item or {}).get("house") or 0) != int(house):
            continue
        clean = str(name or "").strip().lower()
        if clean and clean not in names:
            names.append(clean)
    return names


def _significant_house_counts(planet_map: Mapping[str, Mapping[str, Any]]) -> dict[int, int]:
    counts: dict[int, int] = defaultdict(int)
    keep = {
        "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
        "uranus", "neptune", "pluto", "chiron", "north node", "true node", "mean node", "node",
    }
    for name, item in planet_map.items():
        clean = str(name or "").strip().lower()
        if clean not in keep:
            continue
        house = int((item or {}).get("house") or 0)
        if house > 0:
            counts[house] += 1
    return counts


def _axis_support(
    planet_map: Mapping[str, Mapping[str, Any]],
    *,
    left: int,
    right: int,
) -> float:
    left_names = _house_planet_names(planet_map, left)
    right_names = _house_planet_names(planet_map, right)
    score = 0.2 * len(left_names) + 0.2 * len(right_names)
    if left_names and right_names:
        score += 0.6
    if any(name in {"venus", "jupiter", "pluto", "chiron", "north node", "true node", "mean node", "node"} for name in [*left_names, *right_names]):
        score += 0.4
    return score


def _top_aspect_refs(
    aspects: Sequence[Mapping[str, Any]] | None,
    *,
    planet: str,
    limit: int,
) -> list[dict[str, str]]:
    target = str(planet or "").strip().lower()
    out: list[dict[str, str]] = []
    rows = sorted(
        [dict(item) for item in aspects or [] if isinstance(item, Mapping)],
        key=lambda item: (_safe_float(item.get("orb"), 99.0), str(item.get("planet1") or ""), str(item.get("planet2") or "")),
    )
    for entry in rows:
        p1 = str(entry.get("planet1") or "").strip().lower()
        p2 = str(entry.get("planet2") or "").strip().lower()
        if target not in {p1, p2}:
            continue
        aspect_type = str(entry.get("type") or entry.get("aspect") or "").strip().title()
        if aspect_type.lower() not in {"conjunction", "opposition", "square", "trine", "sextile"}:
            continue
        orb = _safe_float(entry.get("orb"), 99.0)
        if orb > 5.0:
            continue
        other = p2 if p1 == target else p1
        out.append(
            {
                "label": f"{planet.title()} {aspect_type} {other.title()}",
                "ref": f"{planet.title()}:{other.title()}:{aspect_type.lower()}",
            }
        )
        if len(out) >= limit:
            break
    return out


def _has_any_aspect(
    aspects: Sequence[Mapping[str, Any]] | None,
    pairs: Sequence[tuple[str, str]],
) -> bool:
    return any(_planet_has_major_aspect(aspects, left, right) for left, right in pairs)


def _planet_has_major_aspect(
    aspects: Sequence[Mapping[str, Any]] | None,
    left: str,
    right: str,
) -> bool:
    for entry in aspects or []:
        if not isinstance(entry, Mapping):
            continue
        p1 = str(entry.get("planet1") or "").strip().lower()
        p2 = str(entry.get("planet2") or "").strip().lower()
        if {p1, p2} != {str(left).strip().lower(), str(right).strip().lower()}:
            continue
        aspect_type = str(entry.get("type") or entry.get("aspect") or "").strip().lower()
        if aspect_type in {"conjunction", "opposition", "square", "trine", "sextile"}:
            return True
    return False


def _relationship_signature_evidence(
    *,
    aspects: Sequence[Mapping[str, Any]] | None,
    venus_item: Mapping[str, Any] | None,
    mars_item: Mapping[str, Any] | None,
    moon_item: Mapping[str, Any] | None,
) -> list[str]:
    out: list[str] = []
    for planet, item in (("venus", venus_item), ("mars", mars_item), ("moon", moon_item)):
        if isinstance(item, Mapping) and item:
            house = int(item.get("house") or 0)
            if house in {5, 7, 8, 12}:
                out.append(f"discovery:relationship:{planet}:{house}")
    for pair in (("Moon", "Venus"), ("Venus", "Mars"), ("Moon", "Pluto"), ("Venus", "Pluto"), ("Venus", "Jupiter")):
        if _planet_has_major_aspect(aspects, *pair):
            out.append(f"discovery:relationship:aspect:{pair[0].lower()}:{pair[1].lower()}")
    return out


def _build_discovery_aspect_candidates(
    *,
    aspects: Sequence[Mapping[str, Any]] | None,
    existing_ids: set[str],
    locale: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    rows = sorted(
        [dict(item) for item in aspects or [] if isinstance(item, Mapping)],
        key=lambda item: (_safe_float(item.get("orb"), 99.0), str(item.get("planet1") or ""), str(item.get("planet2") or "")),
    )
    for entry in rows:
        p1 = str(entry.get("planet1") or "").strip().lower()
        p2 = str(entry.get("planet2") or "").strip().lower()
        aspect_type = str(entry.get("type") or entry.get("aspect") or "").strip().lower()
        orb = _safe_float(entry.get("orb"), 99.0)
        if orb > 2.5 or aspect_type not in {"conjunction", "opposition", "square", "trine", "sextile"}:
            continue
        if {"moon", "venus"} == {p1, p2} and not _candidate_ids_contain(existing_ids, "moon_trine_venus", "affection_gift"):
            out.append(
                _build_discovery_packet(
                    packet_id=f"discovery_aspect_{p1}_{aspect_type}_{p2}_gap",
                    domain="relationship",
                    promise_type="love_style",
                    strength=0.69,
                    title="Sıkı ilişki açısı kapsama boşluğu",
                    direct_meaning="Sıkı bir ilişki açısı var ama buna sahip çıkan yeterince spesifik bir packet görünmüyor.",
                    lived_scene="Ay-Venüs hattı chartta kendi başına ayrı bir sıcaklık ya da yakınlık dili kurabilir.",
                    gift="Sıkı ilişki açısını debug seviyesinde görünür kılmak.",
                    shadow="Bu açı generic ilişki fallback'ine dağılabilir.",
                    growth="Sıkı Ay-Venüs açısı için daha net bir arketip ailesi eklemek.",
                    technical_anchors=[f"{p1.title()} {aspect_type.title()} {p2.title()}"],
                    evidence_ids=[f"discovery:aspect:{p1}:{aspect_type}:{p2}"],
                    locale=locale,
                    discovery_domain="relationship",
                    discovery_kind="coverage_gap",
                    coverage_topic="tight_aspect_relationship",
                )
            )
        elif {"moon", "pluto"} == {p1, p2} and not _candidate_ids_contain(existing_ids, "moon_opposite_pluto", "deep_mind_pressure"):
            out.append(
                _build_discovery_packet(
                    packet_id=f"discovery_aspect_{p1}_{aspect_type}_{p2}_gap",
                    domain="emotional_world",
                    promise_type="need",
                    strength=0.69,
                    title="Sıkı duygusal derinlik açısı kapsama boşluğu",
                    direct_meaning="Sıkı bir Moon-Pluto açısı var ama buna sahip çıkan yeterince spesifik bir packet görünmüyor.",
                    lived_scene="Ay-Plüton hattı sosyal ya da duygusal derinliği ayrı bir baskı/yoğunluk hattı olarak çalıştırabilir.",
                    gift="Sıkı Moon-Pluto açısını debug seviyesinde görünür kılmak.",
                    shadow="Bu açı generic shadow ya da relationship fallback'ine dağılabilir.",
                    growth="Moon-Pluto sıkı açıları için daha net bir arketip ailesi eklemek.",
                    technical_anchors=[f"{p1.title()} {aspect_type.title()} {p2.title()}"],
                    evidence_ids=[f"discovery:aspect:{p1}:{aspect_type}:{p2}"],
                    locale=locale,
                    discovery_domain="emotional",
                    discovery_kind="coverage_gap",
                    coverage_topic="tight_aspect_emotional_depth",
                )
            )
        elif {"sun", "mercury"} == {p1, p2} and not _candidate_ids_contain(existing_ids, "social_emotional_intelligence", "mind_", "big_mind"):
            out.append(
                _build_discovery_packet(
                    packet_id=f"discovery_aspect_{p1}_{aspect_type}_{p2}_gap",
                    domain="mind",
                    promise_type="mind_style",
                    strength=0.68,
                    title="Sıkı zihin açısı kapsama boşluğu",
                    direct_meaning="Sıkı bir Sun-Mercury açısı var ama buna sahip çıkan yeterince spesifik bir packet görünmüyor.",
                    lived_scene="Kimlik ve zihin hattı birbirine yakın çalışıyor olabilir.",
                    gift="Sıkı Sun-Mercury açısını debug seviyesinde görünür kılmak.",
                    shadow="Bu açı generic mind fallback'ine dağılabilir.",
                    growth="Sıkı Sun-Mercury açıları için daha net bir arketip ailesi eklemek.",
                    technical_anchors=[f"{p1.title()} {aspect_type.title()} {p2.title()}"],
                    evidence_ids=[f"discovery:aspect:{p1}:{aspect_type}:{p2}"],
                    locale=locale,
                    discovery_domain="mind",
                    discovery_kind="coverage_gap",
                    coverage_topic="tight_aspect_mind",
                )
            )
        if len(out) >= 2:
            break
    return out


def _build_auxiliary_candidates(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    registry_entries: Mapping[str, Mapping[str, Any]],
    locale: str,
) -> list[dict[str, Any]]:
    category_support = _best_category_support(seed=seed, thread=thread)
    items = []
    for key in ("supporting_combo", "hidden_support"):
        values = category_support.get(key) if isinstance(category_support.get(key), Sequence) else []
        for value in values:
            if isinstance(value, Mapping):
                items.append(dict(value))
    out: list[dict[str, Any]] = []
    seen_match_ids: set[str] = set()
    for item in items:
        label = str(item.get("label") or "").strip()
        if not label:
            continue
        pseudo_seed = dict(seed)
        pseudo_seed["title"] = str(seed.get("title") or "").strip()
        pseudo_seed["micro"] = str(seed.get("micro") or "").strip()
        pseudo_seed["proof_raw"] = str(seed.get("proof_raw") or "").strip()
        pseudo_seed["chips"] = list(seed.get("chips") or [])
        pseudo_seed["detail_blocks"] = list(seed.get("detail_blocks") or [])
        pseudo_seed["auxiliary_anchor"] = item
        pseudo_support = copy.deepcopy(category_support)
        pseudo_support["primary_anchor"] = dict(item)
        pseudo_support["supporting_combo"] = list(category_support.get("supporting_combo") or [])
        candidate = _build_candidate(
            seed=pseudo_seed,
            thread=thread,
            registry_entries=registry_entries,
            locale=locale,
            auxiliary=True,
        )
        if candidate:
            match_ids = [str(value).strip() for value in candidate.get("matched_archetypes") or [] if str(value).strip()]
            dedupe_key = match_ids[0] if match_ids else _normalize_text(label)
            if dedupe_key in seen_match_ids:
                continue
            seen_match_ids.add(dedupe_key)
            candidate["id"] = f"{candidate.get('id')}_aux"
            candidate["theme_key"] = f"{candidate.get('theme_key')}::aux::{_normalize_text(label)}"
            # Domain-family compatibility filter (Adana audit §5): if this
            # aux's resolved registry family disagrees with the seed section's
            # family, strip cross-domain chips / scene / direct_meaning that
            # were inherited from the seed at packet-build time. If the filter
            # leaves nothing in-domain, mark the aux for suppression from
            # public surfaces (debug / transit_activation remain available).
            primary_match: Mapping[str, Any] | None = None
            for raw_match in candidate.get("matched_archetype_summaries") or []:
                if isinstance(raw_match, Mapping):
                    # ``matched_archetype_summaries`` only carries id/score; we
                    # need the registry-family info, which lives on the
                    # full match dict. Use the lookup-by-id helper below.
                    match_id = str(raw_match.get("id") or "").strip()
                    if match_id:
                        primary_match = registry_entries.get(match_id) or registry_entries.get(_normalize_text(match_id))
                        if primary_match:
                            break
            filtered_candidate, _, _ = _filter_aux_for_domain_compatibility(
                candidate=candidate,
                seed=seed,
                thread=thread,
                match=primary_match,
            )
            out.append(filtered_candidate)
    return out[:2]


def _material_inventory_matches(
    matches: Sequence[Mapping[str, Any]],
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    identity_signal = _has_identity_inventory_signal(seed=seed, thread=thread)
    for match in matches:
        match_id = str(match.get("id") or "").strip()
        score = _safe_float(match.get("score"), 0.0)
        if score >= 0.72:
            out.append(dict(match))
            continue
        if identity_signal and match_id in {
            "capricorn_asc_sun_1h_composed_self_construction",
            "saturn_sextile_uranus_structured_originality",
            "saturn_3h_aries_speech_decision_language",
        }:
            out.append(dict(match))
    return out


def _inventory_domains_for_match(
    *,
    match: Mapping[str, Any],
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    category_support: Mapping[str, Any],
) -> list[tuple[str, str]]:
    primary_domain = _inventory_primary_domain(match=match, seed=seed, thread=thread)
    variants: list[tuple[str, str]] = [(primary_domain, "")]
    if _has_identity_inventory_signal(seed=seed, thread=thread):
        match_id = str(match.get("id") or "").strip()
        if match_id == "saturn_sextile_uranus_structured_originality" and primary_domain != "identity":
            variants.append(("identity", "identity_overlay"))
        elif match_id == "saturn_3h_aries_speech_decision_language" and primary_domain != "identity":
            variants.append(("behavior_reflex", "behavior_reflex_overlay"))
    if _has_career_inventory_signal(seed=seed, thread=thread, category_support=category_support):
        match_id = str(match.get("id") or "").strip()
        if match_id == "venus_sagittarius_12h_hidden_expansive_love" and primary_domain != "career":
            variants.append(("career", "career_overlay"))
    deduped: list[tuple[str, str]] = []
    seen: set[str] = set()
    for domain, suffix in variants:
        key = f"{domain}::{suffix}"
        if domain and key not in seen:
            deduped.append((domain, suffix))
            seen.add(key)
    return deduped


def _inventory_primary_domain(
    *,
    match: Mapping[str, Any],
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
) -> str:
    match_id = str(match.get("id") or "").strip()
    title = _normalize_text(str(seed.get("title") or (thread or {}).get("title") or ""))
    if "ilişki" in title or "duygusal derinlik" in title:
        if match_id in {
            "moon_trine_venus_emotional_warmth",
            "moon_leo_8h_deep_proud_heart",
            "venus_sagittarius_12h_hidden_expansive_love",
        }:
            return "relationship"
    if "görünür" in title or "kariyer" in title:
        if match_id in {
            "venus_sagittarius_12h_hidden_expansive_love",
            "chiron_conjunct_mc_visibility_wound_to_voice",
        }:
            return "career"
    if "zihin" in title or "eylem" in title:
        if match_id == "capricorn_asc_sun_1h_composed_self_construction":
            return "identity"
        if match_id == "saturn_3h_aries_speech_decision_language":
            return "mind"
    domains = [str(item).strip().lower() for item in (match.get("domains") or []) if str(item).strip()]
    for domain in domains:
        normalized = _DOMAIN_ALIASES.get(domain)
        if normalized:
            return normalized
    return _resolve_domain(seed=seed, thread=thread, matches=[match])


def _allow_candidate_inventory_variant(
    candidate: Mapping[str, Any],
    *,
    match: Mapping[str, Any],
    forced_domain: str,
) -> bool:
    strength = _safe_float(candidate.get("strength"), 0.0)
    match_id = str(match.get("id") or "").strip()
    if strength >= 0.58:
        return True
    if match_id == "capricorn_asc_sun_1h_composed_self_construction" and forced_domain == "identity":
        return strength >= 0.46
    if match_id in {
        "saturn_sextile_uranus_structured_originality",
        "saturn_3h_aries_speech_decision_language",
    } and forced_domain in {"identity", "behavior_reflex"}:
        return strength >= 0.5
    return False


def _has_identity_inventory_signal(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
) -> bool:
    chips = " ".join(str(item).strip() for item in (seed.get("chips") or []) if str(item).strip()).lower()
    evidence = " ".join(
        str((item or {}).get("source_ref") or "")
        for item in ((thread or {}).get("evidence") or [])
        if isinstance(item, Mapping)
    ).lower()
    return "yükselen oğlak" in chips or "house:1->ruler" in evidence or "ascendant" in evidence


def _has_career_inventory_signal(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    category_support: Mapping[str, Any],
) -> bool:
    title = _normalize_text(str(seed.get("title") or (thread or {}).get("title") or ""))
    if "gorunur" in title or "kariyer" in title:
        return True
    primary_anchor = category_support.get("primary_anchor") if isinstance(category_support.get("primary_anchor"), Mapping) else {}
    source_ref = str(primary_anchor.get("source_ref") or "").strip().lower()
    return "house:10->ruler" in source_ref or "midheaven" in source_ref


def _support_anchor(label: str, source_ref: str, score: float, *, source_type: str) -> dict[str, Any]:
    return {
        "kind": "anchor" if source_type in {"placement", "ruler_route", "angle"} else "supporting_combo",
        "label": label,
        "source_type": source_type,
        "source_ref": source_ref,
        "score": round(score, 4),
    }


def _support_motif(label: str, source_ref: str, score: float) -> dict[str, Any]:
    return {
        "kind": "motif",
        "label": label,
        "source_type": "motif",
        "source_ref": source_ref,
        "score": round(score, 4),
    }


def _v0_5_chart_signature_variants() -> list[dict[str, Any]]:
    return [
        {
            "match_id": "taurus_asc_venus_12h_hidden_value_identity",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Kimlikte saklı değer ve sessiz çekim",
            "proof_raw": "Yükselen Boğa · Venüs 12. ev Boğa",
            "chips": ["Yükselen Boğa", "Venüs · 12. ev · Boğa", "Venüs ASC yakın"],
            "scene": "Bir şeyi gerçekten sevdiğinde bunu hemen göstermeyip önce içeride taşımak.",
            "salience": 0.94,
            "confidence": 0.96,
            "primary_anchor": _support_anchor("Ascendant Taurus", "planet:Ascendant:sign:Taurus", 0.95, source_type="angle"),
            "supporting_combo": [
                _support_anchor("Venus in Taurus 12H", "planet:Venus:sign:Taurus:house:12", 0.96, source_type="placement"),
                _support_anchor("Venus conjunction Ascendant", "Venus:Ascendant:conjunction", 0.92, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("hidden value identity", "hidden_value_identity", 0.88)],
        },
        {
            "match_id": "venus_taurus_12h_private_love_inner_beauty",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "İlişkide içeride büyüyen sevgi",
            "proof_raw": "Venüs · 12. ev · Boğa",
            "chips": ["Venüs · 12. ev · Boğa", "Sessiz sevgi", "Duyusal güven"],
            "scene": "Birine bağlandığında bunu önce içinde koruyup daha yavaş görünür kılmak.",
            "salience": 0.9,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("Venus in Taurus 12H", "planet:Venus:sign:Taurus:house:12", 0.95, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Venus conjunction Ascendant", "Venus:Ascendant:conjunction", 0.9, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("private love", "private_love", 0.84)],
        },
        {
            "match_id": "venus_12h_conjunct_asc_soft_hidden_magnetism",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Kimlikte sessiz magnetizma",
            "proof_raw": "Venüs kavuşum ASC · 12. ev",
            "chips": ["Venüs ASC kavuşumu", "Venüs 12. ev", "Sessiz çekim"],
            "scene": "Çok şey göstermeden de ortamda iz bırakmak.",
            "salience": 0.86,
            "confidence": 0.92,
            "primary_anchor": _support_anchor("Venus conjunction Ascendant", "Venus:Ascendant:conjunction", 0.93, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Venus in house 12", "planet:Venus:house:12", 0.88, source_type="placement"),
            ],
        },
        {
            "match_id": "mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation",
            "forced_domain": "career",
            "variant_suffix": "chart_exact",
            "title": "Kariyerde görünmeyen hazırlık ve sessiz olgunlaşma",
            "proof_raw": "MC Oğlak · Satürn 12. ev Balık",
            "chips": ["MC Oğlak", "Satürn · 12. ev · Balık", "Perde arkası emek"],
            "scene": "Görünür olmadan önce içeride uzun süre prova yapmak.",
            "salience": 0.94,
            "confidence": 0.96,
            "primary_anchor": _support_anchor("10th house ruler route", "house:10->ruler:Saturn->house:12", 0.96, source_type="ruler_route"),
            "supporting_combo": [
                _support_anchor("Midheaven Capricorn", "house:10:cusp_sign:Capricorn", 0.93, source_type="angle"),
                _support_anchor("Saturn in Pisces 12H", "planet:Saturn:sign:Pisces:house:12", 0.94, source_type="placement"),
            ],
            "repeated_motifs": [_support_motif("invisible preparation", "invisible_preparation", 0.9)],
        },
        {
            "match_id": "saturn_pisces_12h_private_maturity_boundary_sensitivity",
            "forced_domain": "inner_world",
            "variant_suffix": "chart_exact",
            "title": "İç dünyada sessiz yük ve olgunlaşma",
            "proof_raw": "Satürn · 12. ev · Balık",
            "chips": ["Satürn · 12. ev · Balık", "Sınır hassasiyeti", "Sessiz sorumluluk"],
            "scene": "Bazı yükleri kimse anlamadan içeride taşımak.",
            "salience": 0.88,
            "confidence": 0.93,
            "primary_anchor": _support_anchor("Saturn in Pisces 12H", "planet:Saturn:sign:Pisces:house:12", 0.94, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Saturn sextile Neptune", "Saturn:Neptune:sextile", 0.84, source_type="aspect"),
            ],
        },
        {
            "match_id": "dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "İlişkide güven eşiği ve sessiz arzu",
            "proof_raw": "DSC Akrep · Mars 12. ev Balık",
            "chips": ["7. ev Akrep", "Mars · 12. ev · Balık", "Güven eşiği"],
            "scene": "Birine yaklaşmak isteyip aynı anda kendini korumaya almak.",
            "salience": 0.94,
            "confidence": 0.96,
            "primary_anchor": _support_anchor("7th house ruler route", "house:7->ruler:Mars->house:12", 0.96, source_type="ruler_route"),
            "supporting_combo": [
                _support_anchor("7th cusp Scorpio", "house:7:cusp_sign:Scorpio", 0.92, source_type="angle"),
                _support_anchor("Mars in Pisces 12H", "planet:Mars:sign:Pisces:house:12", 0.94, source_type="placement"),
            ],
            "repeated_motifs": [_support_motif("trust threshold", "trust_threshold", 0.88)],
        },
        {
            "match_id": "pluto_7h_relationship_power_depth",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "İlişkide güç ve dönüşüm derinliği",
            "proof_raw": "Plüton 7. ev",
            "chips": ["Plüton 7. ev", "Yoğun karşılaşma", "Dönüşen bağ"],
            "scene": "Bazı ilişkilerin kapanmış görünse bile içeride uzun süre iz bırakması.",
            "salience": 0.84,
            "confidence": 0.9,
            "primary_anchor": _support_anchor("Pluto in house 7", "planet:Pluto:house:7", 0.9, source_type="placement"),
            "supporting_combo": [
                _support_anchor("7th cusp Scorpio", "house:7:cusp_sign:Scorpio", 0.82, source_type="angle"),
            ],
        },
        {
            "match_id": "mars_pisces_12h_hidden_action_soft_drive",
            "forced_domain": "inner_world",
            "variant_suffix": "chart_exact",
            "title": "İç dünyada sessiz hareket ve yumuşak itki",
            "proof_raw": "Mars · 12. ev · Balık",
            "chips": ["Mars · 12. ev · Balık", "Sessiz çaba", "Sezgisel aksiyon"],
            "scene": "Ne istediğini hemen açmadan önce içeride uzun süre sezmek.",
            "salience": 0.86,
            "confidence": 0.91,
            "primary_anchor": _support_anchor("Mars in Pisces 12H", "planet:Mars:sign:Pisces:house:12", 0.92, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Mars sextile Midheaven", "Mars:Midheaven:sextile", 0.84, source_type="aspect"),
            ],
        },
        {
            "match_id": "sun_mars_pisces_12h_private_will_and_hidden_drive",
            "forced_domain": "inner_world",
            "variant_suffix": "chart_exact",
            "title": "İç dünyada özel irade ve saklı cesaret",
            "proof_raw": "Güneş kavuşum Mars · 12. ev Balık",
            "chips": ["Güneş-Mars kavuşumu", "12. ev Balık", "Sessiz mücadele"],
            "scene": "Başkaları fark etmeden içeride çoktan karar almış olmak.",
            "salience": 0.9,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("Sun conjunction Mars", "Sun:Mars:conjunction", 0.95, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Sun in Pisces 12H", "planet:Sun:sign:Pisces:house:12", 0.9, source_type="placement"),
                _support_anchor("Mars in Pisces 12H", "planet:Mars:sign:Pisces:house:12", 0.9, source_type="placement"),
            ],
        },
        {
            "match_id": "pisces_12h_stellium_inner_world_saturation",
            "forced_domain": "inner_world",
            "variant_suffix": "chart_exact",
            "title": "Haritada güçlü iç dünya doygunluğu",
            "proof_raw": "12. ev yoğunluğu",
            "chips": ["12. ev yoğunluğu", "Balık vurgusu", "Görünmeyen süreçler"],
            "scene": "Karar, arzu ve sorumlulukların önce sessiz bir alanda şekillenmesi.",
            "salience": 0.96,
            "confidence": 0.97,
            "primary_anchor": _support_anchor("12th house saturation", "house:12:saturation", 0.97, source_type="ruler_route"),
            "supporting_combo": [
                _support_anchor("Sun in house 12", "planet:Sun:house:12", 0.9, source_type="placement"),
                _support_anchor("Mars in house 12", "planet:Mars:house:12", 0.9, source_type="placement"),
                _support_anchor("Saturn in house 12", "planet:Saturn:house:12", 0.9, source_type="placement"),
                _support_anchor("Venus in house 12", "planet:Venus:house:12", 0.9, source_type="placement"),
            ],
            "repeated_motifs": [_support_motif("inner world saturation", "inner_world_saturation", 0.92)],
        },
        {
            "match_id": "mercury_pisces_11h_social_intuition_mind",
            "forced_domain": "mind",
            "variant_suffix": "chart_exact",
            "title": "Zihinde sosyal sezgi ve atmosfer okuma",
            "proof_raw": "Merkür · 11. ev · Balık",
            "chips": ["Merkür · 11. ev · Balık", "Sosyal sezgi", "Atmosfer okuma"],
            "scene": "Bir grubun içinde söylenmeyen şeyi hızlıca hissetmek.",
            "salience": 0.86,
            "confidence": 0.91,
            "primary_anchor": _support_anchor("Mercury in Pisces 11H", "planet:Mercury:sign:Pisces:house:11", 0.92, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Mercury sextile Ascendant", "Mercury:Ascendant:sextile", 0.82, source_type="aspect"),
            ],
        },
        {
            "match_id": "uranus_square_asc_venus_unsettled_outer_signal",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Kimlikte sakin tonun altında elektrik",
            "proof_raw": "Uranüs kare ASC · Venüs kare Uranüs",
            "chips": ["Uranüs kare ASC", "Venüs kare Uranüs", "Özgürlük ihtiyacı"],
            "scene": "Yakınlık fazla sabitlendiğinde bir anda alan ihtiyacının yükselmesi.",
            "salience": 0.82,
            "confidence": 0.89,
            "primary_anchor": _support_anchor("Uranus square Ascendant", "Uranus:Ascendant:square", 0.94, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Venus square Uranus", "Venus:Uranus:square", 0.92, source_type="aspect"),
                _support_anchor("Ascendant Taurus", "planet:Ascendant:sign:Taurus", 0.8, source_type="angle"),
            ],
        },
    ]


def _v0_7_chart_signature_variants() -> list[dict[str, Any]]:
    return [
        {
            "match_id": "leo_asc_sun_cancer_11h_warm_visibility_belonging",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Kimlikte sıcak görünürlük ve aitlik",
            "proof_raw": "Yükselen Aslan · Güneş 11. ev Yengeç",
            "chips": ["Yükselen Aslan", "Güneş · 11. ev · Yengeç", "Aitlik"],
            "scene": "Kendini en çok ait hissettiğin çevrelerde tam açmak.",
            "salience": 0.94,
            "confidence": 0.96,
            "primary_anchor": _support_anchor("Ascendant Leo", "planet:Ascendant:sign:Leo", 0.95, source_type="angle"),
            "supporting_combo": [
                _support_anchor("Sun in Cancer 11H", "planet:Sun:sign:Cancer:house:11", 0.94, source_type="placement"),
                _support_anchor("Sun trine Jupiter", "Sun:Jupiter:trine", 0.86, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("warm visibility belonging", "warm_visibility_belonging", 0.88)],
        },
        {
            "match_id": "sun_mercury_cancer_11h_social_emotional_intelligence",
            "forced_domain": "mind",
            "variant_suffix": "chart_exact",
            "title": "Zihinde sosyal-duygusal zeka",
            "proof_raw": "Güneş-Merkür kavuşumu · 11. ev Yengeç",
            "chips": ["Güneş-Merkür", "11. ev Yengeç", "Sosyal zeka"],
            "scene": "Bir çevrede kimin neye ihtiyaç duyduğunu hızlıca sezmek.",
            "salience": 0.9,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("Sun conjunct Mercury", "Sun:Mercury:conjunction", 0.96, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Sun in Cancer 11H", "planet:Sun:sign:Cancer:house:11", 0.9, source_type="placement"),
                _support_anchor("Mercury in Cancer 11H", "planet:Mercury:sign:Cancer:house:11", 0.9, source_type="placement"),
                _support_anchor("Mercury trine Jupiter", "Mercury:Jupiter:trine", 0.84, source_type="aspect"),
            ],
        },
        {
            "match_id": "pluto_node_scorpio_4h_roots_inner_security_transformation",
            "forced_domain": "home_family",
            "variant_suffix": "chart_exact",
            "title": "Köklerde iç güvenliği dönüştüren yoğunluk",
            "proof_raw": "Plüton + Kuzey Ay Düğümü · 4. ev · Akrep",
            "chips": ["Plüton 4. ev", "KAD 4. ev", "Akrep kökler"],
            "scene": "Köklerden gelen yoğunluğu dönüştürerek kendi iç alanını yeniden kurmak.",
            "salience": 0.96,
            "confidence": 0.97,
            "primary_anchor": _support_anchor("Pluto in Scorpio 4H", "planet:Pluto:sign:Scorpio:house:4", 0.96, source_type="placement"),
            "supporting_combo": [
                _support_anchor("North Node in Scorpio 4H", "planet:North Node:sign:Scorpio:house:4", 0.94, source_type="placement"),
                _support_anchor("IC Scorpio", "house:4:cusp_sign:Scorpio", 0.9, source_type="angle"),
                _support_anchor("Mars opposite Pluto", "Mars:Pluto:opposition", 0.88, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("roots inner security transformation", "roots_inner_security_transformation", 0.92)],
        },
        {
            "match_id": "ic_scorpio_pluto_node_private_emotional_inheritance",
            "forced_domain": "home_family",
            "variant_suffix": "chart_exact",
            "title": "Köklerde özel duygusal miras",
            "proof_raw": "IC Akrep · Plüton/KAD 4. ev",
            "chips": ["IC Akrep", "Plüton/KAD 4. ev", "Duygusal miras"],
            "scene": "Aile içinde söylenmeyenleri bile güçlü hissetmek.",
            "salience": 0.86,
            "confidence": 0.92,
            "primary_anchor": _support_anchor("IC Scorpio", "house:4:cusp_sign:Scorpio", 0.9, source_type="angle"),
            "supporting_combo": [
                _support_anchor("Pluto in Scorpio 4H", "planet:Pluto:sign:Scorpio:house:4", 0.9, source_type="placement"),
                _support_anchor("North Node in Scorpio 4H", "planet:North Node:sign:Scorpio:house:4", 0.88, source_type="placement"),
            ],
        },
        {
            "match_id": "moon_capricorn_5h_serious_heart_creative_form",
            "forced_domain": "creativity",
            "variant_suffix": "chart_exact",
            "title": "Yaratıcılıkta ciddi kalp ve form ihtiyacı",
            "proof_raw": "Ay · 5. ev · Oğlak",
            "chips": ["Ay · 5. ev · Oğlak", "Yaratıcı form", "Ciddi kalp"],
            "scene": "Kalpten gelen şeyi bile önce yapılandırmak.",
            "salience": 0.84,
            "confidence": 0.91,
            "primary_anchor": _support_anchor("Moon in Capricorn 5H", "planet:Moon:sign:Capricorn:house:5", 0.93, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Moon sextile Pluto", "Moon:Pluto:sextile", 0.82, source_type="aspect"),
            ],
        },
        {
            "match_id": "moon_uranus_neptune_capricorn_5h_structured_imagination",
            "forced_domain": "creativity",
            "variant_suffix": "chart_exact",
            "title": "Yaratıcılıkta yapı isteyen özgün hayal gücü",
            "proof_raw": "Ay/Uranüs/Neptün · 5. ev · Oğlak",
            "chips": ["Ay-Uranüs-Neptün", "5. ev Oğlak", "Yapılı ilham"],
            "scene": "Hayal gücünü ciddiye alınan bir yapı içinde göstermek istemek.",
            "salience": 0.94,
            "confidence": 0.96,
            "primary_anchor": _support_anchor("Moon in Capricorn 5H", "planet:Moon:sign:Capricorn:house:5", 0.94, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Uranus in Capricorn 5H", "planet:Uranus:sign:Capricorn:house:5", 0.9, source_type="placement"),
                _support_anchor("Neptune in Capricorn 5H", "planet:Neptune:sign:Capricorn:house:5", 0.9, source_type="placement"),
                _support_anchor("Moon conjunct Uranus", "Moon:Uranus:conjunction", 0.88, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("structured imagination", "structured_imagination", 0.9)],
        },
        {
            "match_id": "mc_taurus_mars_10h_steady_public_drive",
            "forced_domain": "career",
            "variant_suffix": "chart_exact",
            "title": "Kariyerde yavaş ama güçlü görünür hareket",
            "proof_raw": "MC Boğa · Mars 10. ev Boğa",
            "chips": ["MC Boğa", "Mars · 10. ev · Boğa", "Somut etki"],
            "scene": "Dış dünyada gücünü sözle değil, yaptığı işle göstermek.",
            "salience": 0.95,
            "confidence": 0.97,
            "primary_anchor": _support_anchor("Mars conjunct Midheaven", "Mars:Midheaven:conjunction", 0.94, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Midheaven Taurus", "house:10:cusp_sign:Taurus", 0.93, source_type="angle"),
                _support_anchor("Mars in Taurus 10H", "planet:Mars:sign:Taurus:house:10", 0.96, source_type="placement"),
            ],
            "repeated_motifs": [_support_motif("steady public drive", "steady_public_drive", 0.9)],
        },
        {
            "match_id": "mars_opposite_pluto_public_power_roots_tension",
            "forced_domain": "career",
            "variant_suffix": "chart_exact",
            "title": "Kariyerde public güç ve kök gerilimi",
            "proof_raw": "Mars karşıt Plüton · 10H/4H",
            "chips": ["Mars karşıt Plüton", "10H/4H aksı", "Güç gerilimi"],
            "scene": "Ev veya iç güvenlik tetiklendiğinde dışarıdaki duruşun sertleşmesi.",
            "salience": 0.88,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("Mars opposite Pluto", "Mars:Pluto:opposition", 0.95, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Mars in Taurus 10H", "planet:Mars:sign:Taurus:house:10", 0.9, source_type="placement"),
                _support_anchor("Pluto in Scorpio 4H", "planet:Pluto:sign:Scorpio:house:4", 0.9, source_type="placement"),
            ],
        },
        {
            "match_id": "aquarius_dsc_saturn_pisces_7h_freedom_responsibility_sensitivity",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "İlişkide özgürlük, sorumluluk ve hassas sınır",
            "proof_raw": "DSC Kova · Satürn 7. ev Balık",
            "chips": ["7. ev Kova", "Satürn · 7. ev · Balık", "Şefkatli sınır"],
            "scene": "Yakınlıkta hem kendi alanını korumak hem de güvenilir bir bağ aramak.",
            "salience": 0.9,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("7th cusp Aquarius", "house:7:cusp_sign:Aquarius", 0.92, source_type="angle"),
            "supporting_combo": [
                _support_anchor("Saturn in Pisces 7H", "planet:Saturn:sign:Pisces:house:7", 0.94, source_type="placement"),
            ],
            "repeated_motifs": [_support_motif("freedom responsibility sensitivity", "freedom_responsibility_sensitivity", 0.88)],
        },
        {
            "match_id": "venus_leo_12h_hidden_romantic_pride",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "İlişkide içte büyüyen romantik gurur",
            "proof_raw": "Venüs · 12. ev · Aslan",
            "chips": ["Venüs · 12. ev · Aslan", "Özel hissetme", "Gizli romantizm"],
            "scene": "Romantik duyguyu içeride büyütüp dışarıda daha kontrollü göstermek.",
            "salience": 0.86,
            "confidence": 0.92,
            "primary_anchor": _support_anchor("Venus in Leo 12H", "planet:Venus:sign:Leo:house:12", 0.94, source_type="placement"),
        },
        {
            "match_id": "jupiter_scorpio_3h_deep_speech_psychological_learning",
            "forced_domain": "mind",
            "variant_suffix": "chart_exact",
            "title": "Zihinde derin konuşma ve psikolojik öğrenme",
            "proof_raw": "Jüpiter · 3. ev · Akrep",
            "chips": ["Jüpiter · 3. ev · Akrep", "Derin konuşma", "Psikolojik öğrenme"],
            "scene": "Bir cümlenin altında saklı olanı hızlıca sezmek.",
            "salience": 0.84,
            "confidence": 0.91,
            "primary_anchor": _support_anchor("Jupiter in Scorpio 3H", "planet:Jupiter:sign:Scorpio:house:3", 0.93, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Sun trine Jupiter", "Sun:Jupiter:trine", 0.82, source_type="aspect"),
                _support_anchor("Mercury trine Jupiter", "Mercury:Jupiter:trine", 0.82, source_type="aspect"),
            ],
        },
        {
            "match_id": "chiron_virgo_1h_visible_sensitivity_self_correction",
            "forced_domain": "identity",
            "variant_suffix": "chart_exact",
            "title": "Kimlikte görünür hassasiyet ve kendini düzeltme",
            "proof_raw": "Chiron · 1. ev · Başak",
            "chips": ["Chiron · 1. ev · Başak", "Görünür hassasiyet", "Kendini düzeltme"],
            "scene": "Kendini göstermeden önce yeterince iyi mi diye düşünmek.",
            "salience": 0.82,
            "confidence": 0.9,
            "primary_anchor": _support_anchor("Chiron in Virgo 1H", "planet:Chiron:sign:Virgo:house:1", 0.92, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Sun sextile Chiron", "Sun:Chiron:sextile", 0.82, source_type="aspect"),
            ],
        },
    ]


def _v0_8_chart_signature_variants() -> list[dict[str, Any]]:
    return [
        {
            "match_id": "aries_asc_mars_libra_6h_action_through_balance",
            "forced_domain": "action",
            "variant_suffix": "chart_exact",
            "title": "Eylemde cesaret ve denge",
            "proof_raw": "Yükselen Koç · Mars 6. ev Terazi",
            "chips": ["Yükselen Koç", "Mars · 6. ev · Terazi", "Dengeyle hareket"],
            "scene": "Hızlı tepkiyle adil kalma ihtiyacının aynı anda çalışması.",
            "salience": 0.96,
            "confidence": 0.97,
            "primary_anchor": _support_anchor("Ascendant Aries", "planet:Ascendant:sign:Aries", 0.95, source_type="angle"),
            "supporting_combo": [
                _support_anchor("Mars in Libra 6H", "planet:Mars:sign:Libra:house:6", 0.96, source_type="placement"),
                _support_anchor("1st house ruler route", "house:1->ruler:Mars->house:6", 0.95, source_type="ruler_route"),
            ],
            "repeated_motifs": [_support_motif("action through balance", "action_through_balance", 0.9)],
        },
        {
            "match_id": "mars_opposite_saturn_action_restraint_inner_brake",
            "forced_domain": "action",
            "variant_suffix": "chart_exact",
            "title": "Eylemde hız ve iç fren",
            "proof_raw": "Mars karşıt Satürn",
            "chips": ["Mars karşıt Satürn", "Hız ve fren", "Kontrollü aksiyon"],
            "scene": "Bir şeyi hemen yapmak isterken içerden frene basmak.",
            "salience": 0.9,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("Mars opposite Saturn", "Mars:Saturn:opposition", 0.94, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Mars in Libra 6H", "planet:Mars:sign:Libra:house:6", 0.9, source_type="placement"),
                _support_anchor("Saturn in Aries 12H", "planet:Saturn:sign:Aries:house:12", 0.9, source_type="placement"),
            ],
            "repeated_motifs": [_support_motif("action restraint", "action_restraint", 0.88)],
        },
        {
            "match_id": "saturn_aries_12h_private_pressure_hidden_self_control",
            "forced_domain": "inner_world",
            "variant_suffix": "chart_exact",
            "title": "İçte tutulan cesaret ve görünmeyen baskı",
            "proof_raw": "Satürn · 12. ev · Koç",
            "chips": ["Satürn · 12. ev · Koç", "Gizli baskı", "İç kontrol"],
            "scene": "Bazı mücadeleleri dışarıdan görünmeden, kendi içinde vermek.",
            "salience": 0.9,
            "confidence": 0.94,
            "primary_anchor": _support_anchor("Saturn in Aries 12H", "planet:Saturn:sign:Aries:house:12", 0.95, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Mars opposite Saturn", "Mars:Saturn:opposition", 0.9, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("private pressure", "private_pressure", 0.88)],
        },
        {
            "match_id": "moon_cancer_ic_home_security_roots",
            "forced_domain": "home_family",
            "variant_suffix": "chart_exact",
            "title": "Köklerde iç güvenlik ve duygusal merkez",
            "proof_raw": "Ay Yengeç · IC Yengeç",
            "chips": ["Ay · Yengeç", "IC Yengeç", "İç güvenlik"],
            "scene": "İçeride güvende hissetmediğinde dışarıdaki duruşun da etkilenmesi.",
            "salience": 0.98,
            "confidence": 0.98,
            "primary_anchor": _support_anchor("Moon in Cancer near IC", "planet:Moon:sign:Cancer:house:3", 0.96, source_type="placement"),
            "supporting_combo": [
                _support_anchor("IC Cancer", "house:4:cusp_sign:Cancer", 0.96, source_type="angle"),
                _support_anchor("Moon opposite Mercury", "Moon:Mercury:opposition", 0.9, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("home security roots", "home_security_roots", 0.94)],
        },
        {
            "match_id": "mercury_capricorn_mc_public_voice_strategic_mind",
            "forced_domain": "career",
            "variant_suffix": "chart_exact",
            "title": "Public ses ve stratejik zihin",
            "proof_raw": "Merkür Oğlak · MC Oğlak",
            "chips": ["Merkür · 10. ev · Oğlak", "MC Oğlak", "Public voice"],
            "scene": "İnsanların sadece yaptığın işi değil, onu nasıl anlattığını da fark etmesi.",
            "salience": 0.98,
            "confidence": 0.98,
            "primary_anchor": _support_anchor("Mercury in Capricorn 10H", "planet:Mercury:sign:Capricorn:house:10", 0.96, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Midheaven Capricorn", "house:10:cusp_sign:Capricorn", 0.96, source_type="angle"),
                _support_anchor("Moon opposite Mercury", "Moon:Mercury:opposition", 0.9, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("public voice strategic mind", "public_voice_strategic_mind", 0.94)],
        },
        {
            "match_id": "moon_mercury_ic_mc_private_security_public_voice_axis",
            "forced_domain": "axis_tension",
            "variant_suffix": "chart_exact",
            "title": "İç güvenlik ve public söz aksı",
            "proof_raw": "Ay-IC · Merkür-MC · karşıtlık",
            "chips": ["Ay-Merkür karşıtlığı", "IC/MC aksı", "Özel alan ve dış rol"],
            "scene": "İçeride duygusal olarak etkilenmişken dışarıda net konuşmak zorunda kalmak.",
            "salience": 0.99,
            "confidence": 0.98,
            "primary_anchor": _support_anchor("Moon opposite Mercury", "Moon:Mercury:opposition", 0.96, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("IC Cancer", "house:4:cusp_sign:Cancer", 0.94, source_type="angle"),
                _support_anchor("Midheaven Capricorn", "house:10:cusp_sign:Capricorn", 0.94, source_type="angle"),
                _support_anchor("Moon in Cancer", "planet:Moon:sign:Cancer", 0.92, source_type="placement"),
                _support_anchor("Mercury in Capricorn 10H", "planet:Mercury:sign:Capricorn:house:10", 0.92, source_type="placement"),
            ],
            "repeated_motifs": [_support_motif("private security public voice axis", "private_security_public_voice_axis", 0.96)],
        },
        {
            "match_id": "sun_aquarius_11h_collective_identity_future_networks",
            "forced_domain": "community",
            "variant_suffix": "chart_exact",
            "title": "Topluluk içinde geleceğe dönük kimlik",
            "proof_raw": "Güneş · 11. ev · Kova",
            "chips": ["Güneş · 11. ev · Kova", "Kolektif kimlik", "Gelecek fikri"],
            "scene": "Bir grup içinde farklı bir fikir veya yeni bir bakış getirmek.",
            "salience": 0.94,
            "confidence": 0.96,
            "primary_anchor": _support_anchor("Sun in Aquarius 11H", "planet:Sun:sign:Aquarius:house:11", 0.96, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Sun conjunct Jupiter", "Sun:Jupiter:conjunction", 0.86, source_type="aspect"),
                _support_anchor("Sun conjunct Uranus", "Sun:Uranus:conjunction", 0.82, source_type="aspect"),
            ],
            "repeated_motifs": [_support_motif("collective identity", "collective_identity", 0.9)],
        },
        {
            "match_id": "aquarius_11h_future_collective_signal",
            "forced_domain": "community",
            "variant_suffix": "chart_exact",
            "title": "Geleceğe dönük kolektif sinyal",
            "proof_raw": "11. ev Kova vurgusu",
            "chips": ["11. ev", "Kova", "Kolektif vizyon"],
            "scene": "Bir fikrin tek başına değil, bir topluluk içinde anlam kazanması.",
            "salience": 0.86,
            "confidence": 0.92,
            "primary_anchor": _support_anchor("Sun in Aquarius 11H", "planet:Sun:sign:Aquarius:house:11", 0.9, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Uranus in Aquarius 11H", "planet:Uranus:sign:Aquarius:house:11", 0.86, source_type="placement"),
                _support_anchor("11th house ruler route", "house:11->ruler:Saturn->house:12", 0.82, source_type="ruler_route"),
            ],
        },
        {
            "match_id": "capricorn_10h_mercury_venus_neptune_public_style_responsibility",
            "forced_domain": "career",
            "variant_suffix": "chart_exact",
            "title": "Public rolde söz, üslup ve sorumluluk",
            "proof_raw": "Merkür/Venüs/Neptün · 10. ev · Oğlak",
            "chips": ["10. ev Oğlak", "Merkür-Venüs-Neptün", "Public stil"],
            "scene": "Bir şeyi sunarken hem düzgün, hem güzel, hem de güvenilir görünmesini istemek.",
            "salience": 0.92,
            "confidence": 0.95,
            "primary_anchor": _support_anchor("Mercury in Capricorn 10H", "planet:Mercury:sign:Capricorn:house:10", 0.94, source_type="placement"),
            "supporting_combo": [
                _support_anchor("Venus in Capricorn 10H", "planet:Venus:sign:Capricorn:house:10", 0.92, source_type="placement"),
                _support_anchor("Neptune in Capricorn 10H", "planet:Neptune:sign:Capricorn:house:10", 0.9, source_type="placement"),
                _support_anchor("Midheaven Capricorn", "house:10:cusp_sign:Capricorn", 0.9, source_type="angle"),
            ],
            "repeated_motifs": [_support_motif("public style responsibility", "public_style_responsibility", 0.88)],
        },
        {
            "match_id": "libra_dsc_chiron_scorpio_7h_harmony_wound_depth",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "İlişkide uyum, yara ve derinlik",
            "proof_raw": "DSC Terazi · Chiron 7. ev Akrep",
            "chips": ["7. ev Terazi", "Chiron · 7. ev · Akrep", "Güven ve derinlik"],
            "scene": "Uyumlu kalmak isterken içeride daha derin bir güven sorusu hissetmek.",
            "salience": 0.94,
            "confidence": 0.96,
            "primary_anchor": _support_anchor("7th cusp Libra", "house:7:cusp_sign:Libra", 0.94, source_type="angle"),
            "supporting_combo": [
                _support_anchor("Chiron in Scorpio 7H", "planet:Chiron:sign:Scorpio:house:7", 0.94, source_type="placement"),
                _support_anchor("7th house ruler route", "house:7->ruler:Venus->house:10", 0.88, source_type="ruler_route"),
            ],
            "repeated_motifs": [_support_motif("harmony wound depth", "harmony_wound_depth", 0.9)],
        },
        {
            "match_id": "venus_capricorn_10h_public_love_style_responsibility",
            "forced_domain": "relationship",
            "variant_suffix": "chart_exact",
            "title": "İlişkide public değer ve sorumluluk",
            "proof_raw": "Venüs · 10. ev · Oğlak",
            "chips": ["Venüs · 10. ev · Oğlak", "Public değer", "Ciddi sevgi dili"],
            "scene": "Bir bağın sadece his değil, davranış ve emekle kanıtlanmasını istemek.",
            "salience": 0.88,
            "confidence": 0.93,
            "primary_anchor": _support_anchor("Venus in Capricorn 10H", "planet:Venus:sign:Capricorn:house:10", 0.94, source_type="placement"),
            "supporting_combo": [
                _support_anchor("7th house ruler route", "house:7->ruler:Venus->house:10", 0.9, source_type="ruler_route"),
            ],
        },
        {
            "match_id": "libra_aries_6h_12h_service_action_axis",
            "forced_domain": "axis_tension",
            "variant_suffix": "chart_exact",
            "title": "Günlük denge ve gizli aksiyon baskısı",
            "proof_raw": "Mars Terazi 6H · Satürn Koç 12H",
            "chips": ["Mars 6. ev Terazi", "Satürn 12. ev Koç", "6H/12H aksı"],
            "scene": "Adil ve uyumlu kalırken kendi pozisyonunu da korumak.",
            "salience": 0.86,
            "confidence": 0.92,
            "primary_anchor": _support_anchor("Mars opposite Saturn", "Mars:Saturn:opposition", 0.9, source_type="aspect"),
            "supporting_combo": [
                _support_anchor("Mars in Libra 6H", "planet:Mars:sign:Libra:house:6", 0.9, source_type="placement"),
                _support_anchor("Saturn in Aries 12H", "planet:Saturn:sign:Aries:house:12", 0.9, source_type="placement"),
            ],
        },
    ]


def _chart_seed_body(*, match: Mapping[str, Any], variant: Mapping[str, Any]) -> str:
    parts: list[str] = []
    direct = str(match.get("direct_meaning") or "").strip()
    if direct:
        parts.append(_ensure_sentence(direct))
    scene = str(variant.get("scene") or "").strip()
    if scene:
        parts.append(_ensure_sentence(scene))
    gift = str(match.get("gift") or "").strip()
    if gift:
        parts.append(_ensure_sentence(gift))
    growth = str(match.get("growth_direction") or "").strip()
    if growth:
        parts.append(_ensure_sentence(growth))
    return " ".join(parts)


def _chart_variant_supported(
    *,
    variant: Mapping[str, Any],
    planet_map: Mapping[str, Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    house_rulers: Mapping[str, Any],
    dominant_loops: Sequence[Mapping[str, Any]],
    dominant_planet_names: set[str],
) -> bool:
    match_id = str(variant.get("match_id") or "").strip()
    if match_id == "moon_trine_venus_emotional_warmth":
        return _has_aspect(aspects, "Moon", "Venus", "Trine")
    if match_id == "saturn_sextile_uranus_structured_originality":
        return _has_aspect(aspects, "Saturn", "Uranus", "Sextile")
    if match_id == "saturn_trine_pluto_deep_resilience":
        return _has_aspect(aspects, "Saturn", "Pluto", "Trine")
    if match_id == "mercury_conjunct_jupiter_big_mind":
        return _has_aspect(aspects, "Mercury", "Jupiter", "Conjunction")
    if match_id == "chiron_conjunct_mc_visibility_wound_to_voice":
        return _has_aspect(aspects, "Chiron", "Midheaven", "Conjunction")
    if match_id == "moon_leo_8h_deep_proud_heart":
        return _planet_in_sign_house(planet_map, "moon", "Leo", 8)
    if match_id == "venus_sagittarius_12h_hidden_expansive_love":
        return _planet_in_sign_house(planet_map, "venus", "Sagittarius", 12)
    if match_id == "capricorn_asc_sun_1h_composed_self_construction":
        return _asc_sign(metadata_like=planet_map, house_rulers=house_rulers) == "capricorn" and int((planet_map.get("sun") or {}).get("house") or 0) == 1
    if match_id == "saturn_3h_aries_speech_decision_language":
        return _planet_in_sign_house(planet_map, "saturn", "Aries", 3)
    # ---- v0.3 chart-fact guards ----
    if match_id == "libra_asc_venus_chart_ruler":
        return _asc_sign(metadata_like=planet_map, house_rulers=house_rulers) == "libra"
    if match_id == "venus_virgo_11h_selective_social_care":
        return _planet_in_sign_house(planet_map, "venus", "Virgo", 11)
    if match_id == "sun_virgo_12h_quiet_inner_self":
        return _planet_in_sign_house(planet_map, "sun", "Virgo", 12)
    if match_id == "mercury_virgo_12h_private_analytical_mind":
        return _planet_in_sign_house(planet_map, "mercury", "Virgo", 12)
    if match_id == "moon_gemini_9h_curious_mind":
        return _planet_in_sign_house(planet_map, "moon", "Gemini", 9)
    if match_id == "moon_square_mercury_emotion_mind_friction":
        return _has_aspect(aspects, "Moon", "Mercury", "Square")
    if match_id == "moon_square_venus_need_affection_friction":
        return _has_aspect(aspects, "Moon", "Venus", "Square")
    if match_id == "moon_opposite_pluto_emotional_intensity_control":
        return _has_aspect(aspects, "Moon", "Pluto", "Opposition")
    if match_id == "mercury_conjunct_venus_refined_relational_language":
        return _has_aspect(aspects, "Mercury", "Venus", "Conjunction")
    if match_id == "mercury_square_pluto_deep_mind_pressure":
        return _has_aspect(aspects, "Mercury", "Pluto", "Square")
    if match_id == "venus_square_pluto_intense_love":
        return _has_aspect(aspects, "Venus", "Pluto", "Square")
    if match_id == "mars_leo_11h_warm_visible_drive":
        return _planet_in_sign_house(planet_map, "mars", "Leo", 11)
    if match_id == "mars_opposite_uranus_freedom_in_action":
        return _has_aspect(aspects, "Mars", "Uranus", "Opposition")
    if match_id == "mars_square_chiron_tender_courage":
        return _has_aspect(aspects, "Mars", "Chiron", "Square")
    if match_id == "mc_cancer_moon_gemini_9h_teaching_voice":
        # MC sign cancer + Moon in Gemini 9H (Cancer-MC routes to Moon as ruler).
        h10 = house_rulers.get("10") if isinstance(house_rulers.get("10"), Mapping) else {}
        mc_sign = str(h10.get("cusp_sign") or "").strip().lower()
        if mc_sign != "cancer":
            return False
        return _planet_in_sign_house(planet_map, "moon", "Gemini", 9)
    if match_id == "saturn_taurus_8h_steady_public_maturity":
        return _planet_in_sign_house(planet_map, "saturn", "Taurus", 8)
    if match_id == "sun_opposite_jupiter_service_expansion_tension":
        return _has_aspect(aspects, "Sun", "Jupiter", "Opposition")
    if match_id == "neptune_4h_soft_inner_presence":
        item = planet_map.get("neptune") or {}
        return int(item.get("house") or 0) == 4
    # ---- v0.4 chart-fact guards ----
    if match_id == "gemini_asc_venus_1h_social_relational_presence":
        return (
            _asc_sign(metadata_like=planet_map, house_rulers=house_rulers) == "gemini"
            and _planet_in_sign_house(planet_map, "venus", "Gemini", 1)
        )
    if match_id == "sun_aries_12h_hidden_private_fire":
        return _planet_in_sign_house(planet_map, "sun", "Aries", 12)
    if match_id == "aquarius_mc_mars_conjunct_mc_visible_freedom_drive":
        return (
            _planet_in_sign_house(planet_map, "mars", "Aquarius", 10)
            and _has_aspect(aspects, "Mars", "Midheaven", "Conjunction")
            and _has_aspect(aspects, "Uranus", "Midheaven", "Square")
        )
    if match_id == "venus_trine_mars_relational_attraction_signal":
        return (
            _has_aspect(aspects, "Venus", "Mars", "Trine")
            and _planet_in_sign_house(planet_map, "venus", "Gemini", 1)
            and _planet_in_sign_house(planet_map, "mars", "Aquarius", 10)
        )
    if match_id == "venus_trine_saturn_trust_bond":
        return (
            _has_aspect(aspects, "Venus", "Saturn", "Trine")
            and _planet_in_sign_house(planet_map, "venus", "Gemini", 1)
            and _planet_in_sign_house(planet_map, "saturn", "Aquarius", 9)
        )
    if match_id == "moon_scorpio_6h_emotional_routine_sensitivity":
        return _planet_in_sign_house(planet_map, "moon", "Scorpio", 6)
    if match_id == "mercury_sextile_9h_capricorn_aquarius_intellectual_authority":
        return (
            _has_aspect(aspects, "Mercury", "Jupiter", "Sextile")
            and _has_aspect(aspects, "Mercury", "Saturn", "Sextile")
            and _has_aspect(aspects, "Mercury", "Pluto", "Sextile")
            and int((planet_map.get("jupiter") or {}).get("house") or 0) == 9
            and int((planet_map.get("saturn") or {}).get("house") or 0) == 9
            and int((planet_map.get("pluto") or {}).get("house") or 0) == 9
        )
    # ---- v0.5 chart-fact guards ----
    if match_id == "taurus_asc_venus_12h_hidden_value_identity":
        return (
            _asc_sign(metadata_like=planet_map, house_rulers=house_rulers) == "taurus"
            and _planet_in_sign_house(planet_map, "venus", "Taurus", 12)
        )
    if match_id == "venus_taurus_12h_private_love_inner_beauty":
        return _planet_in_sign_house(planet_map, "venus", "Taurus", 12)
    if match_id == "venus_12h_conjunct_asc_soft_hidden_magnetism":
        return (
            int((planet_map.get("venus") or {}).get("house") or 0) == 12
            and _has_aspect(aspects, "Venus", "Ascendant", "Conjunction")
        )
    if match_id == "mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation":
        return (
            _house_cusp_sign(house_rulers, 10) == "capricorn"
            and _planet_in_sign_house(planet_map, "saturn", "Pisces", 12)
        )
    if match_id == "saturn_pisces_12h_private_maturity_boundary_sensitivity":
        return _planet_in_sign_house(planet_map, "saturn", "Pisces", 12)
    if match_id == "dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire":
        return (
            _house_cusp_sign(house_rulers, 7) == "scorpio"
            and _planet_in_sign_house(planet_map, "mars", "Pisces", 12)
        )
    if match_id == "pluto_7h_relationship_power_depth":
        return int((planet_map.get("pluto") or {}).get("house") or 0) == 7
    if match_id == "mars_pisces_12h_hidden_action_soft_drive":
        return _planet_in_sign_house(planet_map, "mars", "Pisces", 12)
    if match_id == "sun_mars_pisces_12h_private_will_and_hidden_drive":
        return (
            _has_aspect(aspects, "Sun", "Mars", "Conjunction")
            and _planet_in_sign_house(planet_map, "sun", "Pisces", 12)
            and _planet_in_sign_house(planet_map, "mars", "Pisces", 12)
        )
    if match_id == "pisces_12h_stellium_inner_world_saturation":
        return _planet_count_in_house(planet_map, 12, planets={"sun", "mars", "saturn", "venus"}) >= 3
    if match_id == "mercury_pisces_11h_social_intuition_mind":
        return _planet_in_sign_house(planet_map, "mercury", "Pisces", 11)
    if match_id == "uranus_square_asc_venus_unsettled_outer_signal":
        return (
            _has_aspect(aspects, "Uranus", "Ascendant", "Square")
            and _has_aspect(aspects, "Venus", "Uranus", "Square")
        )
    # ---- v0.7 chart-fact guards ----
    if match_id == "leo_asc_sun_cancer_11h_warm_visibility_belonging":
        return (
            _asc_sign(metadata_like=planet_map, house_rulers=house_rulers) == "leo"
            and _planet_in_sign_house(planet_map, "sun", "Cancer", 11)
        )
    if match_id == "sun_mercury_cancer_11h_social_emotional_intelligence":
        return (
            _has_aspect(aspects, "Sun", "Mercury", "Conjunction")
            and _planet_in_sign_house(planet_map, "sun", "Cancer", 11)
            and _planet_in_sign_house(planet_map, "mercury", "Cancer", 11)
        )
    if match_id == "pluto_node_scorpio_4h_roots_inner_security_transformation":
        return (
            _planet_in_sign_house(planet_map, "pluto", "Scorpio", 4)
            and _planet_in_sign_house(planet_map, "north node", "Scorpio", 4)
        )
    if match_id == "ic_scorpio_pluto_node_private_emotional_inheritance":
        return (
            _house_cusp_sign(house_rulers, 4) == "scorpio"
            and _planet_in_sign_house(planet_map, "pluto", "Scorpio", 4)
            and _planet_in_sign_house(planet_map, "north node", "Scorpio", 4)
        )
    if match_id == "moon_capricorn_5h_serious_heart_creative_form":
        return _planet_in_sign_house(planet_map, "moon", "Capricorn", 5)
    if match_id == "moon_uranus_neptune_capricorn_5h_structured_imagination":
        return (
            _planet_in_sign_house(planet_map, "moon", "Capricorn", 5)
            and _planet_in_sign_house(planet_map, "uranus", "Capricorn", 5)
            and _planet_in_sign_house(planet_map, "neptune", "Capricorn", 5)
        )
    if match_id == "mc_taurus_mars_10h_steady_public_drive":
        return (
            _house_cusp_sign(house_rulers, 10) == "taurus"
            and _planet_in_sign_house(planet_map, "mars", "Taurus", 10)
            and _has_aspect(aspects, "Mars", "Midheaven", "Conjunction")
        )
    if match_id == "mars_opposite_pluto_public_power_roots_tension":
        return (
            _has_aspect(aspects, "Mars", "Pluto", "Opposition")
            and _planet_in_sign_house(planet_map, "mars", "Taurus", 10)
            and _planet_in_sign_house(planet_map, "pluto", "Scorpio", 4)
        )
    if match_id == "aquarius_dsc_saturn_pisces_7h_freedom_responsibility_sensitivity":
        return (
            _house_cusp_sign(house_rulers, 7) == "aquarius"
            and _planet_in_sign_house(planet_map, "saturn", "Pisces", 7)
        )
    if match_id == "venus_leo_12h_hidden_romantic_pride":
        return _planet_in_sign_house(planet_map, "venus", "Leo", 12)
    if match_id == "jupiter_scorpio_3h_deep_speech_psychological_learning":
        return _planet_in_sign_house(planet_map, "jupiter", "Scorpio", 3)
    if match_id == "chiron_virgo_1h_visible_sensitivity_self_correction":
        return _planet_in_sign_house(planet_map, "chiron", "Virgo", 1)
    # ---- v0.8 chart-fact guards ----
    if match_id == "aries_asc_mars_libra_6h_action_through_balance":
        return (
            _asc_sign(metadata_like=planet_map, house_rulers=house_rulers) == "aries"
            and _planet_in_sign_house(planet_map, "mars", "Libra", 6)
        )
    if match_id == "mars_opposite_saturn_action_restraint_inner_brake":
        return (
            _has_aspect(aspects, "Mars", "Saturn", "Opposition")
            and _planet_in_sign_house(planet_map, "mars", "Libra", 6)
            and _planet_in_sign_house(planet_map, "saturn", "Aries", 12)
        )
    if match_id == "saturn_aries_12h_private_pressure_hidden_self_control":
        return _planet_in_sign_house(planet_map, "saturn", "Aries", 12)
    if match_id == "moon_cancer_ic_home_security_roots":
        return (
            _planet_in_sign_house(planet_map, "moon", "Cancer", 3)
            and _house_cusp_sign(house_rulers, 4) == "cancer"
        )
    if match_id == "mercury_capricorn_mc_public_voice_strategic_mind":
        return (
            _planet_in_sign_house(planet_map, "mercury", "Capricorn", 10)
            and _house_cusp_sign(house_rulers, 10) == "capricorn"
        )
    if match_id == "moon_mercury_ic_mc_private_security_public_voice_axis":
        return (
            _has_aspect(aspects, "Moon", "Mercury", "Opposition")
            and _planet_in_sign_house(planet_map, "moon", "Cancer", 3)
            and _planet_in_sign_house(planet_map, "mercury", "Capricorn", 10)
            and _house_cusp_sign(house_rulers, 4) == "cancer"
            and _house_cusp_sign(house_rulers, 10) == "capricorn"
        )
    if match_id == "sun_aquarius_11h_collective_identity_future_networks":
        return _planet_in_sign_house(planet_map, "sun", "Aquarius", 11)
    if match_id == "aquarius_11h_future_collective_signal":
        return (
            _planet_in_sign_house(planet_map, "sun", "Aquarius", 11)
            and _planet_in_sign_house(planet_map, "uranus", "Aquarius", 11)
        )
    if match_id == "capricorn_10h_mercury_venus_neptune_public_style_responsibility":
        return (
            _planet_in_sign_house(planet_map, "mercury", "Capricorn", 10)
            and _planet_in_sign_house(planet_map, "venus", "Capricorn", 10)
            and _planet_in_sign_house(planet_map, "neptune", "Capricorn", 10)
        )
    if match_id == "libra_dsc_chiron_scorpio_7h_harmony_wound_depth":
        return (
            _house_cusp_sign(house_rulers, 7) == "libra"
            and _planet_in_sign_house(planet_map, "chiron", "Scorpio", 7)
        )
    if match_id == "venus_capricorn_10h_public_love_style_responsibility":
        return _planet_in_sign_house(planet_map, "venus", "Capricorn", 10)
    if match_id == "libra_aries_6h_12h_service_action_axis":
        return (
            _has_aspect(aspects, "Mars", "Saturn", "Opposition")
            and _planet_in_sign_house(planet_map, "mars", "Libra", 6)
            and _planet_in_sign_house(planet_map, "saturn", "Aries", 12)
        )
    return False


def _chart_variant_match_score(
    *,
    variant: Mapping[str, Any],
    aspects: Sequence[Mapping[str, Any]],
) -> float:
    match_id = str(variant.get("match_id") or "").strip()
    if match_id == "moon_trine_venus_emotional_warmth":
        return _aspect_match_score(aspects, "Moon", "Venus", "Trine", default=0.92)
    if match_id == "saturn_sextile_uranus_structured_originality":
        return _aspect_match_score(aspects, "Saturn", "Uranus", "Sextile", default=0.9)
    if match_id == "saturn_trine_pluto_deep_resilience":
        return _aspect_match_score(aspects, "Saturn", "Pluto", "Trine", default=0.88)
    if match_id == "mercury_conjunct_jupiter_big_mind":
        return _aspect_match_score(aspects, "Mercury", "Jupiter", "Conjunction", default=0.82)
    if match_id == "chiron_conjunct_mc_visibility_wound_to_voice":
        return _aspect_match_score(aspects, "Chiron", "Midheaven", "Conjunction", default=0.86)
    # v0.3 aspect-based score lookups (placement-based ones fall through to 0.9).
    if match_id == "moon_square_mercury_emotion_mind_friction":
        return _aspect_match_score(aspects, "Moon", "Mercury", "Square", default=0.88)
    if match_id == "moon_square_venus_need_affection_friction":
        return _aspect_match_score(aspects, "Moon", "Venus", "Square", default=0.88)
    if match_id == "moon_opposite_pluto_emotional_intensity_control":
        return _aspect_match_score(aspects, "Moon", "Pluto", "Opposition", default=0.88)
    if match_id == "mercury_conjunct_venus_refined_relational_language":
        return _aspect_match_score(aspects, "Mercury", "Venus", "Conjunction", default=0.88)
    if match_id == "mercury_square_pluto_deep_mind_pressure":
        return _aspect_match_score(aspects, "Mercury", "Pluto", "Square", default=0.87)
    if match_id == "venus_square_pluto_intense_love":
        return _aspect_match_score(aspects, "Venus", "Pluto", "Square", default=0.9)
    if match_id == "mars_opposite_uranus_freedom_in_action":
        return _aspect_match_score(aspects, "Mars", "Uranus", "Opposition", default=0.9)
    if match_id == "mars_square_chiron_tender_courage":
        return _aspect_match_score(aspects, "Mars", "Chiron", "Square", default=0.86)
    if match_id == "sun_opposite_jupiter_service_expansion_tension":
        return _aspect_match_score(aspects, "Sun", "Jupiter", "Opposition", default=0.86)
    # v0.4 aspect-based score lookups.
    if match_id == "aquarius_mc_mars_conjunct_mc_visible_freedom_drive":
        return _aspect_match_score(aspects, "Mars", "Midheaven", "Conjunction", default=0.94)
    if match_id == "venus_trine_mars_relational_attraction_signal":
        return _aspect_match_score(aspects, "Venus", "Mars", "Trine", default=0.9)
    if match_id == "venus_trine_saturn_trust_bond":
        return _aspect_match_score(aspects, "Venus", "Saturn", "Trine", default=0.9)
    # v0.5 aspect-based score lookups.
    if match_id == "venus_12h_conjunct_asc_soft_hidden_magnetism":
        return _aspect_match_score(aspects, "Venus", "Ascendant", "Conjunction", default=0.91)
    if match_id == "sun_mars_pisces_12h_private_will_and_hidden_drive":
        return _aspect_match_score(aspects, "Sun", "Mars", "Conjunction", default=0.93)
    if match_id == "uranus_square_asc_venus_unsettled_outer_signal":
        return _aspect_match_score(aspects, "Uranus", "Ascendant", "Square", default=0.93)
    # v0.7 aspect-based score lookups.
    if match_id == "sun_mercury_cancer_11h_social_emotional_intelligence":
        return _aspect_match_score(aspects, "Sun", "Mercury", "Conjunction", default=0.94)
    if match_id == "mc_taurus_mars_10h_steady_public_drive":
        return _aspect_match_score(aspects, "Mars", "Midheaven", "Conjunction", default=0.94)
    if match_id == "mars_opposite_pluto_public_power_roots_tension":
        return _aspect_match_score(aspects, "Mars", "Pluto", "Opposition", default=0.93)
    if match_id == "moon_uranus_neptune_capricorn_5h_structured_imagination":
        return _aspect_match_score(aspects, "Moon", "Uranus", "Conjunction", default=0.91)
    # v0.8 aspect-based score lookups.
    if match_id == "mars_opposite_saturn_action_restraint_inner_brake":
        return _aspect_match_score(aspects, "Mars", "Saturn", "Opposition", default=0.92)
    if match_id == "moon_mercury_ic_mc_private_security_public_voice_axis":
        return _aspect_match_score(aspects, "Moon", "Mercury", "Opposition", default=0.94)
    if match_id == "libra_aries_6h_12h_service_action_axis":
        return _aspect_match_score(aspects, "Mars", "Saturn", "Opposition", default=0.9)
    return 0.9


def _aspect_match_score(
    aspects: Sequence[Mapping[str, Any]],
    planet1: str,
    planet2: str,
    aspect_type: str,
    *,
    default: float,
) -> float:
    for entry in aspects:
        if not isinstance(entry, Mapping):
            continue
        p1 = str(entry.get("planet1") or "").strip().lower()
        p2 = str(entry.get("planet2") or "").strip().lower()
        typ = str(entry.get("type") or entry.get("aspect") or "").strip().lower()
        if {p1, p2} != {planet1.lower(), planet2.lower()} or typ != aspect_type.lower():
            continue
        orb = _safe_float(entry.get("orb"), 6.0)
        return round(max(0.72, min(0.98, 0.98 - (orb * 0.035))), 4)
    return round(default, 4)


def _has_aspect(
    aspects: Sequence[Mapping[str, Any]],
    planet1: str,
    planet2: str,
    aspect_type: str,
) -> bool:
    for entry in aspects:
        if not isinstance(entry, Mapping):
            continue
        p1 = str(entry.get("planet1") or "").strip().lower()
        p2 = str(entry.get("planet2") or "").strip().lower()
        typ = str(entry.get("type") or entry.get("aspect") or "").strip().lower()
        if {p1, p2} == {planet1.lower(), planet2.lower()} and typ == aspect_type.lower():
            return True
    return False


def _planet_in_sign_house(
    planet_map: Mapping[str, Mapping[str, Any]],
    planet: str,
    sign: str,
    house: int,
) -> bool:
    planet_key = planet.lower()
    aliases = {
        "north node": ("north node", "northnode", "true node", "mean node", "node", "kuzey ay düğümü"),
        "south node": ("south node", "southnode", "south node", "güney ay düğümü"),
    }.get(planet_key, (planet_key,))
    item = next((planet_map.get(alias) for alias in aliases if planet_map.get(alias)), {}) or {}
    return (
        str(item.get("sign") or "").strip().lower() == sign.lower()
        and int(item.get("house") or 0) == int(house)
    )


# Bug 5: packet ids whose placement encoding can be cross-checked against the
# chart. Each entry maps a base packet id (the registry archetype id) to a
# validator that returns True when the chart actually has that placement.
# When the validator returns False we set ``chart_facts_match: False`` on the
# packet.
_CHART_FACT_VALIDATORS: dict[str, dict[str, Any]] = {
    "moon_leo_8h_deep_proud_heart": {
        "kind": "planet_in_sign_house",
        "planet": "moon",
        "sign": "leo",
        "house": 8,
    },
    "venus_sagittarius_12h_hidden_expansive_love": {
        "kind": "planet_in_sign_house",
        "planet": "venus",
        "sign": "sagittarius",
        "house": 12,
    },
    "saturn_3h_aries_speech_decision_language": {
        "kind": "planet_in_sign_house",
        "planet": "saturn",
        "sign": "aries",
        "house": 3,
    },
    "capricorn_asc_sun_1h_composed_self_construction": {
        "kind": "asc_with_planet",
        "asc_sign": "capricorn",
        "planet": "sun",
        "house": 1,
    },
    # v0.3 placement-encoded packets — validated to guard against false-positive
    # firings on charts that lack the encoded placement.
    "libra_asc_venus_chart_ruler": {
        "kind": "asc_sign",
        "asc_sign": "libra",
    },
    "venus_virgo_11h_selective_social_care": {
        "kind": "planet_in_sign_house",
        "planet": "venus",
        "sign": "virgo",
        "house": 11,
    },
    "sun_virgo_12h_quiet_inner_self": {
        "kind": "planet_in_sign_house",
        "planet": "sun",
        "sign": "virgo",
        "house": 12,
    },
    "mercury_virgo_12h_private_analytical_mind": {
        "kind": "planet_in_sign_house",
        "planet": "mercury",
        "sign": "virgo",
        "house": 12,
    },
    "moon_gemini_9h_curious_mind": {
        "kind": "planet_in_sign_house",
        "planet": "moon",
        "sign": "gemini",
        "house": 9,
    },
    "mars_leo_11h_warm_visible_drive": {
        "kind": "planet_in_sign_house",
        "planet": "mars",
        "sign": "leo",
        "house": 11,
    },
    "saturn_taurus_8h_steady_public_maturity": {
        "kind": "planet_in_sign_house",
        "planet": "saturn",
        "sign": "taurus",
        "house": 8,
    },
    "neptune_4h_soft_inner_presence": {
        "kind": "planet_in_house",
        "planet": "neptune",
        "house": 4,
    },
    # v0.4 placement-encoded packets.
    "gemini_asc_venus_1h_social_relational_presence": {
        "kind": "asc_with_planet_in_sign_house",
        "asc_sign": "gemini",
        "planet": "venus",
        "sign": "gemini",
        "house": 1,
    },
    "sun_aries_12h_hidden_private_fire": {
        "kind": "planet_in_sign_house",
        "planet": "sun",
        "sign": "aries",
        "house": 12,
    },
    "moon_scorpio_6h_emotional_routine_sensitivity": {
        "kind": "planet_in_sign_house",
        "planet": "moon",
        "sign": "scorpio",
        "house": 6,
    },
    # Aspect-first chart-signature variants that still encode hard placement
    # assumptions in their ids / chips / override copy. Keep them available for
    # debug/transit use, but mark ``chart_facts_match=False`` unless the full
    # placement frame really matches.
    "saturn_sextile_uranus_structured_originality": {
        "kind": "all_of",
        "filter_registry_entry": False,
        "validators": [
            {
                "kind": "asc_sign",
                "asc_sign": "capricorn",
            },
            {
                "kind": "planet_in_sign_house",
                "planet": "saturn",
                "sign": "aries",
                "house": 3,
            },
            {
                "kind": "planet_in_house",
                "planet": "uranus",
                "house": 1,
            },
        ],
    },
    # v0.5 placement-encoded packets.
    "taurus_asc_venus_12h_hidden_value_identity": {
        "kind": "asc_with_planet_in_sign_house",
        "asc_sign": "taurus",
        "planet": "venus",
        "sign": "taurus",
        "house": 12,
    },
    "venus_taurus_12h_private_love_inner_beauty": {
        "kind": "planet_in_sign_house",
        "planet": "venus",
        "sign": "taurus",
        "house": 12,
    },
    "mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation": {
        "kind": "house_cusp_sign_with_planet_in_sign_house",
        "house": 10,
        "cusp_sign": "capricorn",
        "planet": "saturn",
        "sign": "pisces",
        "planet_house": 12,
    },
    "saturn_pisces_12h_private_maturity_boundary_sensitivity": {
        "kind": "planet_in_sign_house",
        "planet": "saturn",
        "sign": "pisces",
        "house": 12,
    },
    "dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire": {
        "kind": "house_cusp_sign_with_planet_in_sign_house",
        "house": 7,
        "cusp_sign": "scorpio",
        "planet": "mars",
        "sign": "pisces",
        "planet_house": 12,
    },
    "pluto_7h_relationship_power_depth": {
        "kind": "planet_in_house",
        "planet": "pluto",
        "house": 7,
    },
    "mars_pisces_12h_hidden_action_soft_drive": {
        "kind": "planet_in_sign_house",
        "planet": "mars",
        "sign": "pisces",
        "house": 12,
    },
    "sun_mars_pisces_12h_private_will_and_hidden_drive": {
        "kind": "all_of",
        "validators": [
            {
                "kind": "planet_in_sign_house",
                "planet": "sun",
                "sign": "pisces",
                "house": 12,
            },
            {
                "kind": "planet_in_sign_house",
                "planet": "mars",
                "sign": "pisces",
                "house": 12,
            },
        ],
    },
    "pisces_12h_stellium_inner_world_saturation": {
        "kind": "planets_in_house_count",
        "house": 12,
        "planets": ["sun", "mars", "saturn", "venus"],
        "min_count": 3,
    },
    "mercury_pisces_11h_social_intuition_mind": {
        "kind": "planet_in_sign_house",
        "planet": "mercury",
        "sign": "pisces",
        "house": 11,
    },
    # v0.7 placement-encoded packets.
    "leo_asc_sun_cancer_11h_warm_visibility_belonging": {
        "kind": "asc_with_planet_in_sign_house",
        "asc_sign": "leo",
        "planet": "sun",
        "sign": "cancer",
        "house": 11,
    },
    "sun_mercury_cancer_11h_social_emotional_intelligence": {
        "kind": "all_of",
        "validators": [
            {"kind": "planet_in_sign_house", "planet": "sun", "sign": "cancer", "house": 11},
            {"kind": "planet_in_sign_house", "planet": "mercury", "sign": "cancer", "house": 11},
        ],
    },
    "pluto_node_scorpio_4h_roots_inner_security_transformation": {
        "kind": "all_of",
        "validators": [
            {"kind": "planet_in_sign_house", "planet": "pluto", "sign": "scorpio", "house": 4},
            {"kind": "planet_in_sign_house", "planet": "north node", "sign": "scorpio", "house": 4},
        ],
    },
    "ic_scorpio_pluto_node_private_emotional_inheritance": {
        "kind": "all_of",
        "validators": [
            {"kind": "house_cusp_sign", "house": 4, "sign": "scorpio"},
            {"kind": "planet_in_sign_house", "planet": "pluto", "sign": "scorpio", "house": 4},
            {"kind": "planet_in_sign_house", "planet": "north node", "sign": "scorpio", "house": 4},
        ],
    },
    "moon_capricorn_5h_serious_heart_creative_form": {
        "kind": "planet_in_sign_house",
        "planet": "moon",
        "sign": "capricorn",
        "house": 5,
    },
    "moon_uranus_neptune_capricorn_5h_structured_imagination": {
        "kind": "all_of",
        "validators": [
            {"kind": "planet_in_sign_house", "planet": "moon", "sign": "capricorn", "house": 5},
            {"kind": "planet_in_sign_house", "planet": "uranus", "sign": "capricorn", "house": 5},
            {"kind": "planet_in_sign_house", "planet": "neptune", "sign": "capricorn", "house": 5},
        ],
    },
    "mc_taurus_mars_10h_steady_public_drive": {
        "kind": "house_cusp_sign_with_planet_in_sign_house",
        "house": 10,
        "cusp_sign": "taurus",
        "planet": "mars",
        "sign": "taurus",
        "planet_house": 10,
    },
    "mars_opposite_pluto_public_power_roots_tension": {
        "kind": "all_of",
        "validators": [
            {"kind": "planet_in_sign_house", "planet": "mars", "sign": "taurus", "house": 10},
            {"kind": "planet_in_sign_house", "planet": "pluto", "sign": "scorpio", "house": 4},
        ],
    },
    "aquarius_dsc_saturn_pisces_7h_freedom_responsibility_sensitivity": {
        "kind": "house_cusp_sign_with_planet_in_sign_house",
        "house": 7,
        "cusp_sign": "aquarius",
        "planet": "saturn",
        "sign": "pisces",
        "planet_house": 7,
    },
    "venus_leo_12h_hidden_romantic_pride": {
        "kind": "planet_in_sign_house",
        "planet": "venus",
        "sign": "leo",
        "house": 12,
    },
    "jupiter_scorpio_3h_deep_speech_psychological_learning": {
        "kind": "planet_in_sign_house",
        "planet": "jupiter",
        "sign": "scorpio",
        "house": 3,
    },
    "chiron_virgo_1h_visible_sensitivity_self_correction": {
        "kind": "planet_in_sign_house",
        "planet": "chiron",
        "sign": "virgo",
        "house": 1,
    },
    # v0.8 placement-encoded packets.
    "aries_asc_mars_libra_6h_action_through_balance": {
        "kind": "all_of",
        "validators": [
            {"kind": "asc_sign", "asc_sign": "aries"},
            {"kind": "planet_in_sign_house", "planet": "mars", "sign": "libra", "house": 6},
        ],
    },
    "mars_opposite_saturn_action_restraint_inner_brake": {
        "kind": "all_of",
        "validators": [
            {"kind": "planet_in_sign_house", "planet": "mars", "sign": "libra", "house": 6},
            {"kind": "planet_in_sign_house", "planet": "saturn", "sign": "aries", "house": 12},
        ],
    },
    "saturn_aries_12h_private_pressure_hidden_self_control": {
        "kind": "planet_in_sign_house",
        "planet": "saturn",
        "sign": "aries",
        "house": 12,
    },
    "moon_cancer_ic_home_security_roots": {
        "kind": "all_of",
        "validators": [
            {"kind": "planet_in_sign_house", "planet": "moon", "sign": "cancer", "house": 3},
            {"kind": "house_cusp_sign", "house": 4, "sign": "cancer"},
        ],
    },
    "mercury_capricorn_mc_public_voice_strategic_mind": {
        "kind": "all_of",
        "validators": [
            {"kind": "planet_in_sign_house", "planet": "mercury", "sign": "capricorn", "house": 10},
            {"kind": "house_cusp_sign", "house": 10, "sign": "capricorn"},
        ],
    },
    "moon_mercury_ic_mc_private_security_public_voice_axis": {
        "kind": "all_of",
        "validators": [
            {"kind": "planet_in_sign_house", "planet": "moon", "sign": "cancer", "house": 3},
            {"kind": "planet_in_sign_house", "planet": "mercury", "sign": "capricorn", "house": 10},
            {"kind": "house_cusp_sign", "house": 4, "sign": "cancer"},
            {"kind": "house_cusp_sign", "house": 10, "sign": "capricorn"},
        ],
    },
    "sun_aquarius_11h_collective_identity_future_networks": {
        "kind": "planet_in_sign_house",
        "planet": "sun",
        "sign": "aquarius",
        "house": 11,
    },
    "aquarius_11h_future_collective_signal": {
        "kind": "all_of",
        "validators": [
            {"kind": "planet_in_sign_house", "planet": "sun", "sign": "aquarius", "house": 11},
            {"kind": "planet_in_sign_house", "planet": "uranus", "sign": "aquarius", "house": 11},
        ],
    },
    "capricorn_10h_mercury_venus_neptune_public_style_responsibility": {
        "kind": "all_of",
        "validators": [
            {"kind": "planet_in_sign_house", "planet": "mercury", "sign": "capricorn", "house": 10},
            {"kind": "planet_in_sign_house", "planet": "venus", "sign": "capricorn", "house": 10},
            {"kind": "planet_in_sign_house", "planet": "neptune", "sign": "capricorn", "house": 10},
        ],
    },
    "libra_dsc_chiron_scorpio_7h_harmony_wound_depth": {
        "kind": "all_of",
        "validators": [
            {"kind": "house_cusp_sign", "house": 7, "sign": "libra"},
            {"kind": "planet_in_sign_house", "planet": "chiron", "sign": "scorpio", "house": 7},
        ],
    },
    "venus_capricorn_10h_public_love_style_responsibility": {
        "kind": "planet_in_sign_house",
        "planet": "venus",
        "sign": "capricorn",
        "house": 10,
    },
    "libra_aries_6h_12h_service_action_axis": {
        "kind": "all_of",
        "validators": [
            {"kind": "planet_in_sign_house", "planet": "mars", "sign": "libra", "house": 6},
            {"kind": "planet_in_sign_house", "planet": "saturn", "sign": "aries", "house": 12},
        ],
    },
}


def _filter_entries_against_chart(
    entries: Mapping[str, Mapping[str, Any]],
    *,
    planets: Sequence[Mapping[str, Any]] | None,
    natal_graph_compact: Mapping[str, Any] | None,
) -> dict[str, Mapping[str, Any]]:
    """Drop placement-encoded registry entries that don't match the chart.

    Only entries listed in ``_CHART_FACT_VALIDATORS`` are eligible for
    filtering — others (e.g. trine/sextile gift archetypes whose match logic
    is purely label-based) are always kept. When the chart cannot be
    determined (no planets payload), the registry is returned unchanged so
    test fixtures that build packets from sections alone still work.
    """

    if not isinstance(entries, Mapping):
        return {}
    if not planets:
        return {key: value for key, value in entries.items() if isinstance(value, Mapping)}
    planet_map = {
        str(item.get("planet") or item.get("name") or "").strip().lower(): dict(item)
        for item in planets or []
        if isinstance(item, Mapping) and str(item.get("planet") or item.get("name") or "").strip()
    }
    if not planet_map:
        return {key: value for key, value in entries.items() if isinstance(value, Mapping)}
    house_rulers = (
        natal_graph_compact.get("house_rulers")
        if isinstance(natal_graph_compact, Mapping) and isinstance(natal_graph_compact.get("house_rulers"), Mapping)
        else {}
    )
    out: dict[str, Mapping[str, Any]] = {}
    for key, value in entries.items():
        if not isinstance(value, Mapping):
            continue
        validator = _CHART_FACT_VALIDATORS.get(key)
        if validator is None or validator.get("filter_registry_entry") is False:
            out[key] = value
            continue
        if _evaluate_chart_fact_validator(
            validator=validator,
            planet_map=planet_map,
            house_rulers=house_rulers,
        ):
            out[key] = value
        # else: chart doesn't match the encoded placement, drop entry.
    return out


def _annotate_chart_facts_match(
    packets: Sequence[Mapping[str, Any]],
    *,
    planets: Sequence[Mapping[str, Any]] | None,
    natal_graph_compact: Mapping[str, Any] | None,
) -> None:
    """Set ``chart_facts_match`` on each packet whose id encodes a placement.

    Mutates ``packets`` in place. Packets whose id does not encode a checkable
    placement are left untouched (no field added). Packets whose chart facts
    do not match the encoded placement get ``chart_facts_match: False``;
    matching packets get ``chart_facts_match: True``. This is purely a
    debugging flag — copy and cluster grouping are untouched.
    """

    planet_map = {
        str(item.get("planet") or item.get("name") or "").strip().lower(): dict(item)
        for item in planets or []
        if isinstance(item, Mapping) and str(item.get("planet") or item.get("name") or "").strip()
    }
    if not planet_map:
        return
    house_rulers = (
        natal_graph_compact.get("house_rulers")
        if isinstance(natal_graph_compact, Mapping) and isinstance(natal_graph_compact.get("house_rulers"), Mapping)
        else {}
    )
    for packet in packets:
        if not isinstance(packet, Mapping):
            continue
        base_id = _base_packet_id(packet)
        validator = _CHART_FACT_VALIDATORS.get(base_id)
        if validator is None:
            continue
        matched = _evaluate_chart_fact_validator(
            validator=validator,
            planet_map=planet_map,
            house_rulers=house_rulers,
        )
        # ``packets`` items are dicts (built upstream); mutate in place.
        if isinstance(packet, dict):
            packet["chart_facts_match"] = bool(matched)


def _evaluate_chart_fact_validator(
    *,
    validator: Mapping[str, Any],
    planet_map: Mapping[str, Mapping[str, Any]],
    house_rulers: Mapping[str, Any],
) -> bool:
    kind = str(validator.get("kind") or "").strip()
    if kind == "planet_in_sign_house":
        return _planet_in_sign_house(
            planet_map,
            str(validator.get("planet") or ""),
            str(validator.get("sign") or ""),
            int(validator.get("house") or 0),
        )
    if kind == "asc_with_planet":
        asc_sign = _asc_sign(metadata_like=planet_map, house_rulers=house_rulers)
        expected_asc = str(validator.get("asc_sign") or "").strip().lower()
        if asc_sign != expected_asc:
            return False
        planet_name = str(validator.get("planet") or "").lower()
        planet_house = int((planet_map.get(planet_name) or {}).get("house") or 0)
        return planet_house == int(validator.get("house") or 0)
    if kind == "asc_sign":
        asc_sign = _asc_sign(metadata_like=planet_map, house_rulers=house_rulers)
        expected_asc = str(validator.get("asc_sign") or "").strip().lower()
        return asc_sign == expected_asc
    if kind == "asc_with_planet_in_sign_house":
        asc_sign = _asc_sign(metadata_like=planet_map, house_rulers=house_rulers)
        expected_asc = str(validator.get("asc_sign") or "").strip().lower()
        if asc_sign != expected_asc:
            return False
        return _planet_in_sign_house(
            planet_map,
            str(validator.get("planet") or ""),
            str(validator.get("sign") or ""),
            int(validator.get("house") or 0),
        )
    if kind == "planet_in_house":
        planet_name = str(validator.get("planet") or "").lower()
        return int((planet_map.get(planet_name) or {}).get("house") or 0) == int(validator.get("house") or 0)
    if kind == "house_cusp_sign":
        return _house_cusp_sign(house_rulers, int(validator.get("house") or 0)) == str(validator.get("sign") or "").strip().lower()
    if kind == "house_cusp_sign_with_planet_in_sign_house":
        if _house_cusp_sign(house_rulers, int(validator.get("house") or 0)) != str(validator.get("cusp_sign") or "").strip().lower():
            return False
        return _planet_in_sign_house(
            planet_map,
            str(validator.get("planet") or ""),
            str(validator.get("sign") or ""),
            int(validator.get("planet_house") or 0),
        )
    if kind == "planet_aspect":
        return _has_aspect(
            validator.get("_aspects") or [],
            str(validator.get("planet1") or ""),
            str(validator.get("planet2") or ""),
            str(validator.get("aspect_type") or ""),
        )
    if kind == "planets_in_house_count":
        planets = {
            str(item).strip().lower()
            for item in (validator.get("planets") or [])
            if str(item).strip()
        }
        return _planet_count_in_house(planet_map, int(validator.get("house") or 0), planets=planets) >= int(validator.get("min_count") or 0)
    if kind == "all_of":
        for child in validator.get("validators") or []:
            if not isinstance(child, Mapping):
                continue
            child_dict = dict(child)
            if child_dict.get("kind") == "planet_aspect":
                child_dict["_aspects"] = validator.get("_aspects") or []
            if not _evaluate_chart_fact_validator(
                validator=child_dict,
                planet_map=planet_map,
                house_rulers=house_rulers,
            ):
                return False
        return True
    return True


def _asc_sign(*, metadata_like: Mapping[str, Mapping[str, Any]], house_rulers: Mapping[str, Any]) -> str:
    house1 = house_rulers.get("1") if isinstance(house_rulers.get("1"), Mapping) else {}
    cusp_sign = str(house1.get("cusp_sign") or "").strip().lower()
    if cusp_sign:
        return cusp_sign
    asc = metadata_like.get("ascendant") or {}
    return str(asc.get("sign") or "").strip().lower()


def _house_cusp_sign(house_rulers: Mapping[str, Any], house: int) -> str:
    item = house_rulers.get(str(house)) if isinstance(house_rulers.get(str(house)), Mapping) else {}
    return str(item.get("cusp_sign") or "").strip().lower()


def _planet_count_in_house(
    planet_map: Mapping[str, Mapping[str, Any]],
    house: int,
    *,
    planets: set[str] | None = None,
) -> int:
    allowed = {str(item).strip().lower() for item in (planets or set()) if str(item).strip()}
    count = 0
    for planet_name, item in planet_map.items():
        if allowed and planet_name not in allowed:
            continue
        if int(item.get("house") or 0) == int(house):
            count += 1
    return count


def _best_category_support(*, seed: Mapping[str, Any], thread: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if isinstance(seed.get("category_support"), Mapping):
        return seed.get("category_support") or {}
    if isinstance(thread, Mapping) and isinstance(thread.get("category_support"), Mapping):
        return thread.get("category_support") or {}
    return {}


def _collect_text_bundle(*, seed: Mapping[str, Any], thread: Mapping[str, Any] | None) -> dict[str, Any]:
    thread_subtitle = str(thread.get("one_liner") or "").strip() if isinstance(thread, Mapping) else ""
    thread_body = str(thread.get("body") or "").strip() if isinstance(thread, Mapping) else ""
    thread_paragraph = str(thread.get("paragraph") or "").strip() if isinstance(thread, Mapping) else ""
    thread_micro = str(thread.get("micro") or "").strip() if isinstance(thread, Mapping) else ""
    thread_detail_blocks = (
        thread.get("detail_blocks")
        if isinstance(thread, Mapping) and isinstance(thread.get("detail_blocks"), Sequence)
        else []
    )
    seed_detail_blocks = seed.get("detail_blocks") if isinstance(seed.get("detail_blocks"), Sequence) else []
    return {
        "subtitle": str(seed.get("subtitle") or seed.get("one_liner") or thread_subtitle).strip(),
        "body": str(seed.get("body") or thread_body).strip(),
        "paragraph": thread_paragraph,
        "micro": str(seed.get("micro") or thread_micro).strip(),
        "detail_blocks": [
            str(item).strip()
            for item in (seed_detail_blocks or thread_detail_blocks)
            if str(item).strip()
        ],
    }


def _collect_evidence(*, seed: Mapping[str, Any], thread: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for raw in [*(seed.get("evidence") or []), *((thread or {}).get("evidence") or [])]:
        if isinstance(raw, Mapping):
            out.append(dict(raw))
    return out


def _strong_auxiliary_seed(
    *,
    seed: Mapping[str, Any],
    text_bundle: Mapping[str, Any],
    category_support: Mapping[str, Any],
) -> bool:
    anchors = _technical_anchors(seed=seed, thread=None, category_support=category_support, matches=[])
    scene = ""
    details = text_bundle.get("detail_blocks") if isinstance(text_bundle.get("detail_blocks"), Sequence) else []
    if details:
        scene = str(details[0] or "").strip()
    return bool(anchors and (scene or str(text_bundle.get("micro") or "").strip() or str(text_bundle.get("subtitle") or "").strip()))


def _match_registry(
    *,
    registry_entries: Mapping[str, Mapping[str, Any]],
    title: str,
    text_bundle: Mapping[str, Any],
    category_support: Mapping[str, Any],
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    search_space = " ".join(
        [
            title,
            str(text_bundle.get("subtitle") or ""),
            str(text_bundle.get("body") or ""),
            str(text_bundle.get("paragraph") or ""),
            str(text_bundle.get("micro") or ""),
            str(seed.get("proof_raw") or ""),
            " ".join(str(item) for item in (seed.get("chips") or [])),
        ]
    )
    normalized_space = _normalize_text(search_space)
    support_entries: list[dict[str, Any]] = []
    for key in ("primary_anchor", "supporting_combo", "hidden_support", "repeated_motifs"):
        values = category_support.get(key)
        if isinstance(values, Mapping):
            support_entries.append(dict(values))
        elif isinstance(values, Sequence):
            support_entries.extend(dict(item) for item in values if isinstance(item, Mapping))
    matches: list[dict[str, Any]] = []
    for key, entry in registry_entries.items():
        if not isinstance(entry, Mapping):
            continue
        score = 0.0
        match_spec = entry.get("match") if isinstance(entry.get("match"), Mapping) else {}
        labels = [str(item).strip() for item in match_spec.get("labels") or [] if str(item).strip()]
        refs = [str(item).strip() for item in match_spec.get("source_refs") or [] if str(item).strip()]
        proof_raw_needles = [str(item).strip() for item in match_spec.get("proof_raw_contains") or [] if str(item).strip()]
        chip_needles = [str(item).strip() for item in match_spec.get("chip_contains") or [] if str(item).strip()]
        for support in support_entries:
            label = str(support.get("label") or "").strip()
            source_ref = str(support.get("source_ref") or "").strip()
            if label in labels:
                score += 0.42 + (_safe_float(support.get("score"), 0.0) * 0.18)
            if source_ref in refs:
                score += 0.4 + (_safe_float(support.get("score"), 0.0) * 0.16)
        proof_raw = str(seed.get("proof_raw") or "").strip()
        chips = [str(item).strip() for item in (seed.get("chips") or []) if str(item).strip()]
        for needle in proof_raw_needles:
            if needle and needle in proof_raw:
                score += 0.36
        for needle in chip_needles:
            if any(needle and needle in chip for chip in chips):
                score += 0.18
        if labels and any(_normalize_text(label) in normalized_space for label in labels):
            score += 0.16
        if proof_raw_needles and any(_normalize_text(needle) in normalized_space for needle in proof_raw_needles):
            score += 0.14
        if score <= 0.0:
            continue
        matches.append(
            {
                **dict(entry),
                "registry_key": key,
                "score": round(score, 4),
            }
        )
    matches.sort(key=lambda item: (-_safe_float(item.get("score"), 0.0), str(item.get("id") or "")))
    return matches[:5]


_DOMAIN_FAMILY_MAP = {
    "mind": "mind",
    "communication": "mind",
    "identity": "identity",
    "behavior_reflex": "identity",
    "inner_world": "inner_world",
    "spirituality": "inner_world",
    "home_family": "home_family",
    "roots": "home_family",
    "relationship": "relationship",
    "love": "relationship",
    "emotional_depth": "relationship",
    # ``emotional_world`` is the inner emotional life domain (e.g. mind/feeling
    # friction packets list it), not the interpersonal ``relationship`` family.
    # Keep it distinct so it does NOT unlock relationship-section domain bleed.
    "emotional_world": "emotional_world",
    "career": "career",
    "visibility": "career",
    "creativity": "creativity",
    "money_self_worth": "identity",
    "self_worth": "identity",
    "community": "community",
    "learning": "mind",
    "body": "identity",
    "service": "identity",
}


def _registry_domain_families(match: Mapping[str, Any]) -> set[str]:
    """Return the set of domain-families declared by an archetype's registry entry."""
    if not isinstance(match, Mapping):
        return set()
    raw_domains = match.get("domains") if isinstance(match.get("domains"), Sequence) else []
    families: set[str] = set()
    for domain in raw_domains:
        clean = str(domain or "").strip().lower()
        family = _DOMAIN_FAMILY_MAP.get(clean)
        if family:
            families.add(family)
    return families


def _section_domain_family(
    *,
    seed: Mapping[str, Any] | None,
    thread: Mapping[str, Any] | None,
) -> str:
    """Return the dominant domain family of the source section/thread that an
    auxiliary candidate was built from. Uses the same title/section-id heuristic
    as ``_resolve_domain`` (without the registry-family gate, since here we
    explicitly want the *seed-side* family — i.e. where chips and detail_blocks
    came from)."""
    seed_map = dict(seed or {})
    thread_map = dict(thread or {})
    section_id = str(seed_map.get("id") or "").strip().lower()
    title = _normalize_text(str(seed_map.get("title") or ""))
    thread_title = _normalize_text(str(thread_map.get("title") or ""))
    legacy_id = str(seed_map.get("legacy_id") or "").strip().lower()
    if (
        "relationship" in section_id
        or "relationships" in section_id
        or "duygusal derinlik" in title
        or "ilişki" in title
        or "ilişki" in thread_title
        or "relationships_depth" in legacy_id
    ):
        return "relationship"
    if (
        "career" in section_id
        or "görünür" in title
        or "kariyer" in title
        or "görünür" in thread_title
        or "kariyer" in thread_title
    ):
        return "career"
    if (
        "mind" in section_id
        or "zihin" in title
        or "iletişim" in title
        or "zihin" in thread_title
    ):
        return "mind"
    if "identity" in section_id or "identity_mechanics" in legacy_id:
        return "identity"
    return ""


# Token-keyed anchor family classifier. Used by the aux-domain compatibility
# filter to decide whether a single chip / proof_raw label belongs to the same
# domain family as the auxiliary packet's resolved registry family.
#
# Each entry lists case-insensitive tokens that, when present in the anchor
# label, mark it as belonging to that family. Token order is irrelevant; the
# first matched family wins (no double-tagging). Tokens are deliberately
# narrow — e.g. ``7. ev`` is a relationship token because in Turkish natal
# rendering the 7th house is the partnership angle; ``moon-mercury``-style
# aspect labels are mind tokens because that aspect is the canonical
# cognitive-friction signature.
_ANCHOR_FAMILY_TOKENS: dict[str, tuple[str, ...]] = {
    "mind": (
        "moon square mercury",
        "moon:mercury",
        "ay kare merkür",
        "moon trine mercury",
        "mercury conjunction venus",
        "merkür kavuşum venüs",
        "merkür · 12",
        "mercury in virgo",
        "moon in gemini",
        "ay · 9",
        "moon gemini",
        "9. ev",
        "9th house",
        "12. ev",
        "merkür",
        "mercury",
    ),
    "relationship": (
        "7. ev",
        "7th house",
        "mars · 11",
        "mars 11",
        "mars in leo",
        "mars leo",
        "venus square pluto",
        "venüs kare plüton",
        "moon square venus",
        "ay kare venüs",
        "mars opposite uranus",
        "mars karşıt uranüs",
        "venus conjunction vertex",
        "house:7",
        "house:8->ruler",
        "11. ev",
        "11th house",
    ),
    "career": (
        "mc",
        "midheaven",
        "10. ev",
        "10th house",
        "saturn in taurus",
        "satürn · 8",
        "saturn taurus 8h",
        "saturn 8h",
        "house:10->ruler",
        "kariyer",
    ),
    "identity": (
        "ascendant",
        "yükselen",
        "asc",
        "1. ev",
        "1th house",
        "1st house",
        "chart ruler",
        "sun in virgo",
        "güneş · 12",
        "house:1->ruler",
    ),
}


_TR_SIGN_NAMES_SET = {
    "koç",
    "boğa",
    "ikizler",
    "yengeç",
    "aslan",
    "başak",
    "terazi",
    "akrep",
    "yay",
    "oğlak",
    "kova",
    "balık",
}


def _is_bare_sign_label(anchor: str) -> bool:
    raw = " ".join(str(anchor or "").split()).strip().lower()
    return raw in _TR_SIGN_NAMES_SET


def _looks_like_motif_chip(anchor: str) -> bool:
    """Return True for the title-cased section-narrative motif labels that
    sections append to their ``chips`` tail (``Dönüştürücü Bağ``,
    ``Çevre Akışı``, ``İçgörü``...). They don't encode a chart anchor and
    leaking them into a cross-domain aux card just adds noise."""
    raw = " ".join(str(anchor or "").split()).strip()
    if not raw:
        return True
    motif_labels = {
        "dönüştürücü bağ",
        "çevre akışı",
        "içgörü",
        "topluluk",
        "public maturity",
        "yoğun çekim",
        "sosyal sezgi",
    }
    return raw.lower() in motif_labels


def _anchor_family(anchor_text: str) -> str:
    """Infer the domain family of a single anchor/chip label by token match.

    Returns the family key (``"mind"``, ``"relationship"``, ``"career"``,
    ``"identity"``) or ``""`` when the anchor is ambiguous (e.g. bare sign
    names like ``"Aslan"`` or ``"Koç"``)."""
    if not anchor_text:
        return ""
    lowered = str(anchor_text).strip().lower()
    if not lowered:
        return ""
    # ``moon square mercury`` and ``moon square venus`` both contain "moon" and
    # "square" — disambiguate by checking the more-specific token first.
    for family in ("mind", "relationship", "career", "identity"):
        for token in _ANCHOR_FAMILY_TOKENS[family]:
            if token in lowered:
                return family
    return ""


def _text_contains_relationship_marker(text: str) -> bool:
    """Return True when a body / lived_scene / inner_tension string carries
    explicit relationship-section markers (``ilişkide``, ``yakınlıkta``,
    ``bağ kurmak`` etc.). Used to detect copy that was inherited from a
    relationship section's ``detail_blocks`` and routed into a non-relationship
    aux packet."""
    if not text:
        return False
    lowered = _normalize_text(str(text))
    if not lowered:
        return False
    markers = (
        "iliskide",
        "iliskinin",
        "yakinlikta",
        "bag kurmak",
        "bag kurdugun",
        "sevgide",
        "partner",
    )
    return any(marker in lowered for marker in markers)


def _filter_aux_for_domain_compatibility(
    *,
    candidate: Mapping[str, Any],
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    match: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], bool, bool]:
    """Filter an auxiliary candidate's section-inherited anchors / body
    snippets when the section's family conflicts with the resolved registry
    family. Returns ``(filtered_candidate, mismatch_applied, should_suppress)``.

    The §7.g domain-fit fix corrected the base-packet domain resolution so a
    mind/cognitive archetype matched under a relationship-titled section no
    longer wins the relationship public_main. But the `_aux` variant of the
    same packet was still inheriting `technical_anchors` (chips), `lived_scene`
    (body opener), and `direct_meaning` (teaser) from the relationship section
    seed — leaving a Zihin (mind) card whose body opens with Mars Leo 11H / 7.
    ev Koç anchors and contains relationship-only lines. This filter removes
    those cross-domain bleeds.

    Generic rule (NOT hard-coded to ``moon_square_mercury``): the filter fires
    on any aux whose section family disagrees with its registry family,
    keyed off ``_DOMAIN_FAMILY_MAP``."""
    seed_family = _section_domain_family(seed=seed, thread=thread)
    if not seed_family or not isinstance(match, Mapping):
        return dict(candidate), False, False
    registry_families = _registry_domain_families(match)
    if not registry_families:
        return dict(candidate), False, False
    if seed_family in registry_families:
        return dict(candidate), False, False
    # Mismatch detected. Compute the aux's "own" family. Prefer concrete
    # render families (``mind``/``identity``/``career``/``relationship``) over
    # the abstract ``emotional_world`` family — the latter is only listed by
    # mind/feeling-friction archetypes alongside ``mind`` and shouldn't be the
    # primary anchor-family signal.
    family_priority = ("mind", "relationship", "career", "identity", "emotional_world")
    own_family = next(
        (fam for fam in family_priority if fam in registry_families),
        next(iter(sorted(registry_families))),
    )
    filtered = dict(candidate)

    # 1) Filter ``technical_anchors``: drop any chip whose inferred family
    # belongs to the conflicting seed family. Also drop:
    #   - bare sign labels (``Aslan``, ``Koç``...) — they read awkwardly as
    #     chips without any planet/house context;
    #   - bare motif labels from the section's ``chips`` tail (e.g.
    #     ``Dönüştürücü Bağ``, ``Çevre Akışı``) which encode the section's
    #     own narrative theme rather than a chart anchor;
    #   - raw ``ruler route`` labels (``8th house ruler route``) which leak
    #     the section's house-ruler index into the wrong domain card.
    # Then prepend the match's registry-supplied label(s) so the resulting
    # chip pool reflects the aux's own (mind/identity/career) anchor identity.
    raw_anchors = candidate.get("technical_anchors") if isinstance(candidate.get("technical_anchors"), Sequence) else []
    kept_anchors: list[str] = []
    has_compatible_anchor = False
    for anchor in raw_anchors:
        clean = str(anchor).strip()
        if not clean:
            continue
        if _is_bare_sign_label(clean):
            continue
        lowered = clean.lower()
        if "ruler route" in lowered:
            continue
        if _looks_like_motif_chip(clean):
            continue
        anchor_fam = _anchor_family(clean)
        if anchor_fam == seed_family and anchor_fam != own_family:
            continue
        kept_anchors.append(clean)
        if anchor_fam == own_family:
            has_compatible_anchor = True
    # Prepend match-side labels (e.g. "Moon square Mercury") so the chip list
    # carries an explicit own-family anchor.
    match_labels: list[str] = []
    match_spec = match.get("match") if isinstance(match.get("match"), Mapping) else {}
    for label in (match_spec.get("labels") if isinstance(match_spec.get("labels"), Sequence) else []) or []:
        clean_label = str(label).strip()
        if clean_label and clean_label not in match_labels and clean_label not in kept_anchors:
            match_labels.append(clean_label)
    if match_labels:
        kept_anchors = [*match_labels, *kept_anchors]
        if not has_compatible_anchor:
            has_compatible_anchor = True
    filtered["technical_anchors"] = kept_anchors[:6]

    # 2) Filter ``lived_scene``: when the inherited scene came from the seed
    # section's detail_blocks (the typical bleed path) it contains explicit
    # relationship/career/identity-section copy that does not belong here.
    # Replace with a registry-provided ``lived_scenes[0]`` from the match when
    # available; otherwise blank.
    inherited_scene = str(candidate.get("lived_scene") or "").strip()
    if inherited_scene and (
        _text_contains_relationship_marker(inherited_scene)
        if seed_family == "relationship"
        else False
    ):
        replacement = ""
        for scene in (match.get("lived_scenes") if isinstance(match.get("lived_scenes"), Sequence) else []) or []:
            clean_scene = str(scene).strip()
            if clean_scene and not _text_contains_relationship_marker(clean_scene):
                replacement = _ensure_sentence(clean_scene)
                break
        filtered["lived_scene"] = replacement
    else:
        # Generic seed-domain detection covers more than just "relationship"
        # markers (e.g. career-section bleeds). For other family conflicts we
        # blank ``lived_scene`` whenever the inherited string can be traced to
        # seed.detail_blocks (which the resolver uses first), unless the match
        # supplies its own scene that we prefer.
        for scene in (match.get("lived_scenes") if isinstance(match.get("lived_scenes"), Sequence) else []) or []:
            clean_scene = str(scene).strip()
            if clean_scene:
                filtered["lived_scene"] = _ensure_sentence(clean_scene)
                break

    # 3) Filter ``direct_meaning``: prefer the registry's mind-domain meaning
    # when the inherited one carries relationship markers.
    inherited_direct = str(candidate.get("direct_meaning") or "").strip()
    if inherited_direct and seed_family == "relationship" and _text_contains_relationship_marker(inherited_direct):
        registry_direct = str(match.get("direct_meaning") or "").strip()
        if registry_direct:
            filtered["direct_meaning"] = _ensure_sentence(registry_direct)
        else:
            filtered["direct_meaning"] = ""

    # 4) Rebuild ``voice_seeds`` to drop any seed-scoped sentence carrying
    # cross-domain markers. We keep registry-supplied seeds plus the (possibly
    # rewritten) direct_meaning / lived_scene.
    new_seeds: list[str] = []
    for raw_seed in candidate.get("voice_seeds") or []:
        clean = _ensure_sentence(str(raw_seed).strip())
        if not clean:
            continue
        if seed_family == "relationship" and _text_contains_relationship_marker(clean):
            continue
        new_seeds.append(clean)
    if not new_seeds:
        for raw_seed in (match.get("voice_seeds") if isinstance(match.get("voice_seeds"), Sequence) else []) or []:
            clean = _ensure_sentence(str(raw_seed).strip())
            if clean:
                new_seeds.append(clean)
    filtered["voice_seeds"] = new_seeds

    # 5) Decide whether to suppress this aux from public_main / public_support
    # / detail. When the filter has stripped everything and we have no in-
    # domain anchors AND no in-domain body content, the aux cannot render
    # without re-introducing cross-domain bleed. Mark it for suppression while
    # preserving debug / transit_activation visibility.
    has_body_content = bool(
        filtered.get("lived_scene")
        or filtered.get("direct_meaning")
        or filtered.get("voice_seeds")
    )
    should_suppress = not (has_compatible_anchor or has_body_content)

    # Flag the candidate's meta so downstream layers can audit.
    meta = dict(filtered.get("meta") or {})
    meta["aux_domain_mismatch_filtered"] = True
    meta["aux_section_family"] = seed_family
    meta["aux_registry_family"] = own_family
    if should_suppress:
        meta["aux_should_suppress_from_public"] = True
    filtered["meta"] = meta
    return filtered, True, should_suppress


def _resolve_domain(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    matches: Sequence[Mapping[str, Any]],
) -> str:
    section_id = str(seed.get("id") or "").strip().lower()
    title = _normalize_text(str(seed.get("title") or ""))
    # v0.3 bug fix: title-based fast paths must only fire when the matched
    # archetype actually declares a compatible primary domain. Otherwise a
    # mind/cognitive archetype (e.g. ``moon_square_mercury_emotion_mind_friction``)
    # picked up under a relationship-titled section ends up tagged as a
    # ``relationship`` packet, which lets it become the main of a
    # ``relationship_*`` cluster downstream.
    registry_families = _registry_domain_families(matches[0]) if matches else set()
    if "mind" in section_id or "zihin" in title:
        if not registry_families or "mind" in registry_families:
            return "mind"
    if "relationship" in section_id or "duygusal derinlik" in title or "ilişki" in title:
        if not registry_families or "relationship" in registry_families:
            return "relationship"
    if "career" in section_id or "görünür" in title or "kariyer" in title:
        if not registry_families or "career" in registry_families:
            return "career"
    if matches:
        domains = matches[0].get("domains") if isinstance(matches[0].get("domains"), Sequence) else []
        for domain in domains:
            normalized = _DOMAIN_ALIASES.get(str(domain).strip().lower())
            if normalized:
                return normalized
    if isinstance(thread, Mapping):
        thread_title = _normalize_text(str(thread.get("title") or ""))
        if "ilişki" in thread_title and (not registry_families or "relationship" in registry_families):
            return "relationship"
        if "kariyer" in thread_title and (not registry_families or "career" in registry_families):
            return "career"
    return "identity"


def _score_candidate(
    *,
    domain: str,
    category_support: Mapping[str, Any],
    matches: Sequence[Mapping[str, Any]],
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    text_bundle: Mapping[str, Any],
) -> tuple[float, dict[str, float]]:
    salience = _safe_float(category_support.get("salience"), 0.0)
    confidence = _safe_float(category_support.get("confidence"), 0.0)
    aspect_strength = sum(_safe_float(item.get("score"), 0.0) for item in _support_items(category_support, kinds={"supporting_combo"})) / max(1, len(_support_items(category_support, kinds={"supporting_combo"})))
    hidden_strength = sum(_safe_float(item.get("score"), 0.0) for item in _support_items(category_support, keys={"hidden_support"})) / max(1, len(_support_items(category_support, keys={"hidden_support"})))
    primary_anchor = category_support.get("primary_anchor") if isinstance(category_support.get("primary_anchor"), Mapping) else {}
    primary_anchor_score = _safe_float(primary_anchor.get("score"), 0.0)
    contradiction = category_support.get("contradiction_signature") if isinstance(category_support.get("contradiction_signature"), Mapping) else {}
    contradiction_score = _safe_float(contradiction.get("score"), 0.0)
    repeated_motif_count = len(category_support.get("repeated_motifs") or []) if isinstance(category_support.get("repeated_motifs"), Sequence) else 0
    match_score = max((_safe_float(item.get("score"), 0.0) for item in matches), default=0.0)
    luminary_bonus = 0.0
    technical = " ".join(_technical_anchors(seed=seed, thread=None, category_support=category_support, matches=matches))
    if any(token in technical for token in ("Moon", "Ay", "Sun", "Güneş", "Venus", "Venüs")):
        luminary_bonus = 0.08
    angularity_bonus = 0.0
    if re.search(r"\b(1|4|7|10)(th)? house\b", str(primary_anchor.get("label") or ""), flags=re.IGNORECASE):
        angularity_bonus = 0.08
    if any(needle in technical for needle in ("Yükselen", "Ascendant", "MC", "Midheaven", "7. ev", "8. ev")):
        angularity_bonus = max(angularity_bonus, 0.06)
    chart_ruler_bonus = 0.0
    if "house:1->ruler" in str(primary_anchor.get("source_ref") or "") or any("Yükselen" in anchor for anchor in _technical_anchors(seed=seed, thread=None, category_support=category_support, matches=matches)):
        chart_ruler_bonus = 0.08
    house_chain_bonus = 0.08 if str(primary_anchor.get("source_type") or "") == "ruler_route" else 0.0
    repeated_bonus = min(0.1, repeated_motif_count * 0.03)
    nonempty_text_fields = 0
    for key in ("subtitle", "body", "paragraph", "micro"):
        if str(text_bundle.get(key) or "").strip():
            nonempty_text_fields += 1
    detail_blocks = text_bundle.get("detail_blocks") if isinstance(text_bundle.get("detail_blocks"), Sequence) else []
    if detail_blocks:
        nonempty_text_fields += 1
    text_richness_bonus = min(0.18, nonempty_text_fields * 0.045)
    anchor_count = len(_technical_anchors(seed=seed, thread=thread, category_support=category_support, matches=matches))
    anchor_bonus = min(0.14, anchor_count * 0.04)
    thread_bonus = 0.08 if isinstance(thread, Mapping) and thread else 0.0
    domain_signal_bonus = 0.06 if domain in {"mind", "relationship", "career"} else 0.03
    score = (
        salience * 0.18
        + confidence * 0.18
        + primary_anchor_score * 0.14
        + aspect_strength * 0.12
        + hidden_strength * 0.06
        + contradiction_score * 0.08
        + match_score * 0.18
        + luminary_bonus
        + angularity_bonus
        + chart_ruler_bonus
        + house_chain_bonus
        + repeated_bonus
        + text_richness_bonus
        + anchor_bonus
        + thread_bonus
        + domain_signal_bonus
    )
    return round(score, 4), {
        "salience": round(salience, 4),
        "confidence": round(confidence, 4),
        "primary_anchor": round(primary_anchor_score, 4),
        "aspect_strength": round(aspect_strength, 4),
        "hidden_strength": round(hidden_strength, 4),
        "contradiction": round(contradiction_score, 4),
        "archetype": round(match_score, 4),
        "luminary_bonus": round(luminary_bonus, 4),
        "angularity_bonus": round(angularity_bonus, 4),
        "chart_ruler_bonus": round(chart_ruler_bonus, 4),
        "house_chain_bonus": round(house_chain_bonus, 4),
        "repeated_bonus": round(repeated_bonus, 4),
        "text_richness_bonus": round(text_richness_bonus, 4),
        "anchor_bonus": round(anchor_bonus, 4),
        "thread_bonus": round(thread_bonus, 4),
        "domain_signal_bonus": round(domain_signal_bonus, 4),
    }


def _resolve_promise_type(
    *,
    domain: str,
    matches: Sequence[Mapping[str, Any]],
    category_support: Mapping[str, Any],
    seed: Mapping[str, Any],
) -> str:
    scores: dict[str, float] = defaultdict(float)
    for match in matches:
        promise_type = _PROMISE_TYPE_ALIASES.get(str(match.get("promise_type") or "").strip().lower(), "")
        if promise_type:
            scores[promise_type] += 0.34 + (_safe_float(match.get("score"), 0.0) * 0.24)
        for preferred in match.get("preferred_types") or []:
            normalized = _PROMISE_TYPE_ALIASES.get(str(preferred).strip().lower(), "")
            if normalized:
                scores[normalized] += 0.12
    for key, value in (_DOMAIN_TYPE_FALLBACKS.get(domain) or {}).items():
        scores[key] += value
    contradiction = category_support.get("contradiction_signature") if isinstance(category_support.get("contradiction_signature"), Mapping) else {}
    contradiction_score = _safe_float(contradiction.get("score"), 0.0)
    if contradiction_score >= 0.62:
        scores["wound_to_gift"] += 0.15
        scores["shadow_or_friction"] += 0.08
    if domain == "relationship":
        scores["love_style"] += 0.12
        scores["need"] += 0.1
    if domain == "mind":
        scores["mind_style"] += 0.12
        scores["mind_identity"] += 0.1
    if any(str(match.get("id") or "") == "moon_trine_venus_emotional_warmth" for match in matches):
        scores["love_style"] += 0.4
        scores["gift"] += 0.22
    if any(str(match.get("id") or "") == "saturn_sextile_uranus_structured_originality" for match in matches):
        scores["mind_style"] += 0.34
        scores["mind_identity"] += 0.22
        scores["gift"] += 0.16
    if any(str(match.get("id") or "") == "chiron_conjunct_mc_visibility_wound_to_voice" for match in matches):
        scores["wound_to_gift"] += 0.36
        scores["career_signature"] += 0.16
    if any(str(match.get("id") or "") == "moon_leo_8h_deep_proud_heart" for match in matches):
        scores["love_style"] += 0.14
        scores["need"] += 0.12
    if any(str(match.get("id") or "") == "saturn_3h_aries_speech_decision_language" for match in matches):
        scores["mind_style"] += 0.16
    if any(str(match.get("id") or "") == "venus_sagittarius_12h_hidden_expansive_love" for match in matches):
        scores["career_signature"] += 0.34
        scores["love_style"] += 0.08
    if not scores:
        return "gift"
    winner = max(scores.items(), key=lambda item: (item[1], item[0]))[0]
    return winner


def _technical_anchors(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    category_support: Mapping[str, Any],
    matches: Sequence[Mapping[str, Any]],
) -> list[str]:
    out: list[str] = []
    proof_raw = str(seed.get("proof_raw") or "").strip()
    if proof_raw:
        out.append(proof_raw)
    for chip in seed.get("chips") or []:
        clean = str(chip).strip()
        if clean:
            out.append(clean)
    if isinstance(category_support.get("primary_anchor"), Mapping):
        label = str(category_support.get("primary_anchor", {}).get("label") or "").strip()
        if label:
            out.append(label)
    for key in ("supporting_combo", "hidden_support"):
        values = category_support.get(key) if isinstance(category_support.get(key), Sequence) else []
        for value in values:
            label = str(value.get("label") or "").strip() if isinstance(value, Mapping) else ""
            if label:
                out.append(label)
    for match in matches:
        for label in (match.get("match") or {}).get("labels") or []:
            clean = str(label).strip()
            if clean:
                out.append(clean)
    deduped: list[str] = []
    for item in out:
        if item and item not in deduped:
            deduped.append(item)
    return deduped[:6]


def _source_evidence_ids(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    evidence_entries: Sequence[Mapping[str, Any]],
) -> list[str]:
    out: list[str] = []
    for entry in evidence_entries:
        source_ref = str(entry.get("source_ref") or "").strip()
        label = str(entry.get("label") or "").strip()
        key = source_ref or label
        if key and key not in out:
            out.append(key)
    if not out:
        section_id = str(seed.get("id") or "").strip()
        if section_id:
            out.append(f"section:{section_id}")
        thread_id = str((thread or {}).get("id") or "").strip()
        if thread_id:
            out.append(f"thread:{thread_id}")
    return out[:8]


def _resolve_direct_meaning(seed: Mapping[str, Any], matches: Sequence[Mapping[str, Any]]) -> str:
    for match in matches:
        value = str(match.get("direct_meaning") or "").strip()
        if value:
            modifier = _context_modified_meaning(seed=seed, match=match, default=value)
            return _ensure_sentence(modifier)
    subtitle = str(seed.get("subtitle") or seed.get("one_liner") or "").strip()
    if subtitle:
        return _ensure_sentence(subtitle)
    body = str(seed.get("body") or "").strip()
    lines = _split_sentences(body, max_sentences=1)
    if lines:
        return lines[0]
    return _ensure_sentence(str(seed.get("title") or ""))


def _context_modified_meaning(*, seed: Mapping[str, Any], match: Mapping[str, Any], default: str) -> str:
    modifiers = match.get("context_modifiers") if isinstance(match.get("context_modifiers"), Mapping) else {}
    proof_map = modifiers.get("proof_raw_contains") if isinstance(modifiers.get("proof_raw_contains"), Mapping) else {}
    proof_raw = str(seed.get("proof_raw") or "").strip()
    for needle, payload in proof_map.items():
        if str(needle).strip() and str(needle).strip() in proof_raw and isinstance(payload, Mapping):
            modified = str(payload.get("direct_meaning") or "").strip()
            if modified:
                return modified
    return default


def _resolve_lived_scene(seed: Mapping[str, Any], thread: Mapping[str, Any] | None, matches: Sequence[Mapping[str, Any]]) -> str:
    details = [str(item).strip() for item in (seed.get("detail_blocks") or []) if str(item).strip()]
    if not details and isinstance(thread, Mapping):
        details = [str(item).strip() for item in (thread.get("detail_blocks") or []) if str(item).strip()]
    if details:
        return _ensure_sentence(details[0])
    micro = str(seed.get("micro") or (thread or {}).get("micro") or "").strip()
    if micro:
        return _ensure_sentence(micro)
    for match in matches:
        scenes = match.get("lived_scenes") if isinstance(match.get("lived_scenes"), Sequence) else []
        for scene in scenes:
            clean = str(scene).strip()
            if clean:
                return _ensure_sentence(clean)
    return ""


def _resolve_packet_field(
    field: str,
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    matches: Sequence[Mapping[str, Any]],
    fallback: str = "",
) -> str:
    for match in matches:
        value = str(match.get(field) or "").strip()
        if value:
            return _normalize_packet_field_text(value)
    body = str(seed.get("body") or (thread or {}).get("body") or "").strip()
    lines = _split_sentences(body, max_sentences=3)
    for line in lines:
        normalized = _normalize_text(line)
        if field == "gift" and any(token in normalized for token in ("güçlü", "hediye", "saygı", "sıcak", "açığa çıkar")):
            return _normalize_packet_field_text(line)
    return _normalize_packet_field_text(fallback) if fallback else ""


def _resolve_shadow(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    category_support: Mapping[str, Any],
    matches: Sequence[Mapping[str, Any]],
) -> str:
    contradiction = category_support.get("contradiction_signature") if isinstance(category_support.get("contradiction_signature"), Mapping) else {}
    label = str(contradiction.get("label") or "").strip()
    if label:
        contradiction_line = _humanize_contradiction(label)
        for match in matches:
            value = str(match.get("shadow_or_friction") or "").strip()
            if value:
                return _combine_packet_fragments(
                    value,
                    contradiction_line,
                    connector="Bazen de",
                )
        return _normalize_packet_field_text(contradiction_line)
    value = _resolve_packet_field("shadow_or_friction", seed=seed, thread=thread, matches=matches)
    if value:
        return value
    body = str(seed.get("body") or (thread or {}).get("body") or "").strip()
    for line in _split_sentences(body, max_sentences=5):
        normalized = _normalize_text(line)
        if any(token in normalized for token in ("zorlandığında", "bazen", "korku", "çekil", "sert", "yük")):
            return line
    return ""


def _resolve_inner_tension(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    category_support: Mapping[str, Any],
    matches: Sequence[Mapping[str, Any]],
) -> str:
    for match in matches:
        value = str(match.get("inner_tension") or "").strip()
        if value:
            return _ensure_sentence(value)
    contradiction = category_support.get("contradiction_signature") if isinstance(category_support.get("contradiction_signature"), Mapping) else {}
    label = str(contradiction.get("label") or "").strip()
    if label:
        return _ensure_sentence(_humanize_contradiction(label))
    body = str(seed.get("body") or (thread or {}).get("body") or "").strip()
    for line in _split_sentences(body, max_sentences=5):
        if "Bir yanın" in line or "bir yanın" in line:
            return line
    return ""


def _resolve_growth(seed: Mapping[str, Any], thread: Mapping[str, Any] | None, matches: Sequence[Mapping[str, Any]]) -> str:
    value = _resolve_packet_field("growth_direction", seed=seed, thread=thread, matches=matches)
    if value:
        return value
    detail_blocks = [str(item).strip() for item in (seed.get("detail_blocks") or (thread or {}).get("detail_blocks") or []) if str(item).strip()]
    for block in detail_blocks:
        normalized = _normalize_text(block)
        if any(token in normalized for token in ("öğrenmeye geldiğin", "öğretiyor", "öğreniyorsun", "olgunlaştığında")):
            return _ensure_sentence(block)
    body = str(seed.get("body") or "").strip()
    for line in _split_sentences(body, max_sentences=5):
        normalized = _normalize_text(line)
        if any(token in normalized for token in ("öğren", "olgun", "dönüş", "geliş")):
            return line
    return ""


def _voice_seed_candidates(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    matches: Sequence[Mapping[str, Any]],
    direct_meaning: str,
    lived_scene: str,
    gift: str,
    shadow_or_friction: str,
    growth_direction: str,
) -> list[str]:
    out: list[str] = []
    for match in matches:
        for item in match.get("voice_seeds") or []:
            clean = _ensure_sentence(str(item).strip())
            if clean:
                out.append(clean)
    if direct_meaning:
        out.append(_ensure_sentence(direct_meaning))
    if lived_scene:
        out.append(_ensure_sentence(lived_scene))
    subtitle = str(seed.get("subtitle") or seed.get("one_liner") or (thread or {}).get("one_liner") or "").strip()
    if subtitle:
        out.append(_ensure_sentence(subtitle))
    if gift:
        out.append(_ensure_sentence(gift))
    deduped: list[str] = []
    seen: set[str] = set()
    for item in out:
        key = _normalize_text(item)
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _rank_voice_seeds(candidates: Sequence[str]) -> list[str]:
    scored: list[tuple[tuple[float, int], str]] = []
    for text in candidates:
        clean = _ensure_sentence(text)
        if not clean:
            continue
        lowered = _normalize_text(clean)
        penalty = 0.0
        for banned in _BANNED_PHRASES:
            if banned in lowered:
                penalty += 1.0
        clarity = 0.35 if 28 <= len(clean) <= 120 else 0.18
        natural = 0.2 if any(token in lowered for token in ("sen", "kalbin", "zihin", "sevgi", "güç", "görün")) else 0.08
        specificity = 0.18 if any(token in lowered for token in ("olabilir", "isteyebilir", "kalbin", "zihnin", "gücün")) else 0.08
        screenshot = 0.16 if len(clean) <= 110 else 0.06
        abstraction_penalty = 0.12 if any(token in lowered for token in ("süreç", "aktifleş", "potansiyel", "gölge")) else 0.0
        score = clarity + natural + specificity + screenshot - penalty - abstraction_penalty
        scored.append(((round(score, 4), -len(clean)), clean))
    scored.sort(key=lambda item: (-item[0][0], item[0][1], item[1]))
    deduped: list[str] = []
    seen: set[str] = set()
    for _, item in scored:
        key = _normalize_text(item)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped[:4]


def _theme_key(
    *,
    domain: str,
    matches: Sequence[Mapping[str, Any]],
    category_support: Mapping[str, Any],
    seed: Mapping[str, Any],
) -> str:
    if matches:
        return f"{domain}:{str(matches[0].get('id') or '').strip()}"
    contradiction = category_support.get("contradiction_signature") if isinstance(category_support.get("contradiction_signature"), Mapping) else {}
    if contradiction:
        return f"{domain}:contradiction:{str(contradiction.get('source_ref') or contradiction.get('label') or '').strip()}"
    primary_anchor = category_support.get("primary_anchor") if isinstance(category_support.get("primary_anchor"), Mapping) else {}
    if primary_anchor:
        return f"{domain}:anchor:{str(primary_anchor.get('source_ref') or primary_anchor.get('label') or '').strip()}"
    return f"{domain}:{str(seed.get('id') or seed.get('title') or '').strip()}"


def _candidate_id(
    *,
    domain: str,
    matches: Sequence[Mapping[str, Any]],
    seed: Mapping[str, Any],
    variant_suffix: str = "",
) -> str:
    suffix = f"_{_normalize_text(variant_suffix).replace(' ', '_')}" if str(variant_suffix).strip() else ""
    if matches:
        base = str(matches[0].get("id") or "").strip() or f"{domain}_{_normalize_text(str(seed.get('id') or seed.get('title') or 'packet'))}"
        return f"{base}{suffix}"
    return f"{domain}_{_normalize_text(str(seed.get('id') or seed.get('title') or 'packet'))}{suffix}"


def _collect_source_ids(
    *,
    seed: Mapping[str, Any],
    thread: Mapping[str, Any] | None,
    key: str,
) -> list[str]:
    out: list[str] = []
    if key == "category_id":
        category_support = _best_category_support(seed=seed, thread=thread)
        category_id = str(category_support.get("category_id") or "").strip()
        if category_id:
            out.append(category_id)
    elif key == "thread_id":
        thread_id = str((thread or {}).get("id") or "").strip()
        if thread_id:
            out.append(thread_id)
    elif key == "section_id":
        section_id = str(seed.get("id") or "").strip()
        if section_id:
            out.append(section_id)
        linked = str((thread or {}).get("section_id") or "").strip()
        if linked and linked not in out:
            out.append(linked)
    return out


def _merge_candidates(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        key = str(candidate.get("theme_key") or candidate.get("id") or "").strip()
        if not key:
            continue
        grouped[key].append(dict(candidate))
    out: list[dict[str, Any]] = []
    for key, items in grouped.items():
        items.sort(key=lambda item: (-_safe_float(item.get("strength"), 0.0), str(item.get("id") or "")))
        merged = copy.deepcopy(items[0])
        merged["source_category_ids"] = _merge_lists(items, "source_category_ids")
        merged["source_thread_ids"] = _merge_lists(items, "source_thread_ids")
        merged["source_section_ids"] = _merge_lists(items, "source_section_ids")
        merged["source_evidence_ids"] = _merge_lists(items, "source_evidence_ids")
        merged["technical_anchors"] = _merge_lists(items, "technical_anchors")
        merged["voice_seeds"] = _rank_voice_seeds(_merge_lists(items, "voice_seeds"))
        merged["matched_archetypes"] = _merge_lists(items, "matched_archetypes")
        merged["strength"] = round(min(1.0, max(_safe_float(item.get("strength"), 0.0) for item in items) + (0.04 * max(0, len(items) - 1))), 4)
        out.append(merged)
    return out


def _dedupe_packets(packets: Sequence[Mapping[str, Any]], *, mode: str = "selected") -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    by_headline: dict[str, str] = {}
    candidate_inventory_mode = str(mode or "selected").strip().lower() == "candidate_inventory"
    chart_signature_bases = {
        _base_packet_id(packet)
        for packet in packets
        if _is_chart_signature_packet(packet)
    }
    ordered = sorted(
        [dict(packet) for packet in packets if isinstance(packet, Mapping)],
        key=lambda item: (-_safe_float(item.get("strength"), 0.0), str(item.get("id") or "")),
    )
    for packet in ordered:
        packet_id = str(packet.get("id") or "").strip()
        headline = _normalize_text(str((packet.get("voice_seeds") or [""])[0] if packet.get("voice_seeds") else packet.get("direct_meaning") or ""))
        dedupe_id = packet_id
        if candidate_inventory_mode:
            if chart_signature_bases and not _is_chart_signature_packet(packet) and _base_packet_id(packet) in chart_signature_bases:
                continue
            dedupe_id = "|".join(
                [
                    packet_id,
                    str(packet.get("domain") or "").strip(),
                    str(packet.get("promise_type") or "").strip(),
                    str(packet.get("theme_key") or "").strip(),
                ]
            )
        if dedupe_id and dedupe_id in by_id:
            continue
        if headline and headline in by_headline and str(mode or "selected").strip().lower() != "candidate_inventory":
            continue
        if dedupe_id:
            by_id[dedupe_id] = packet
        if headline:
            by_headline[headline] = packet_id or headline
    return list(by_id.values())


def _base_packet_id(packet: Mapping[str, Any]) -> str:
    packet_id = str(packet.get("id") or "").strip()
    suffixes = (
        "_identity_chart_exact",
        "_relationship_chart_exact",
        "_aux",
        "_identity_overlay",
        "_behavior_reflex_overlay",
        "_career_overlay",
        "_chart_exact",
    )
    for suffix in suffixes:
        if not packet_id.endswith(suffix):
            continue
        candidate = packet_id[: -len(suffix)]
        if candidate in _CHART_FACT_VALIDATORS:
            return candidate
    for suffix in suffixes:
        if packet_id.endswith(suffix):
            return packet_id[: -len(suffix)]
    return packet_id


def _packet_source_type(packet: Mapping[str, Any]) -> str:
    explicit = str(packet.get("source_type") or "").strip()
    if explicit in _PACKET_SOURCE_TYPES:
        return explicit
    meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
    meta_explicit = str(meta.get("source_type") or "").strip()
    if meta_explicit in _PACKET_SOURCE_TYPES:
        return meta_explicit
    packet_id = str(packet.get("id") or "").strip()
    if bool(meta.get("v0_6_discovery")) or bool(meta.get("non_public_discovery")):
        return "discovery_scaffold"
    if packet_id in _GENERIC_PACKET_IDS:
        return "generic_fallback"
    if str(meta.get("inventory_variant") or "").strip() == "chart_signature":
        return "exact_registry"
    if any(str(value).strip() for value in (packet.get("matched_archetypes") or []) if str(value).strip()):
        return "exact_registry"
    return "legacy_graph"


def _initial_candidate_source_type(
    *,
    packet_id: str,
    matches: Sequence[Mapping[str, Any]],
) -> str:
    if str(packet_id or "").strip() in _GENERIC_PACKET_IDS:
        return "generic_fallback"
    if any(str(match.get("id") or "").strip() for match in matches if isinstance(match, Mapping)):
        return "exact_registry"
    return "legacy_graph"


def _annotate_packet_source_types(packets: Sequence[Mapping[str, Any]]) -> None:
    for packet in packets:
        if not isinstance(packet, dict):
            continue
        source_type = _packet_source_type(packet)
        packet["source_type"] = source_type
        meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
        packet_meta = dict(meta)
        packet_meta["source_type"] = source_type
        packet["meta"] = packet_meta


def _is_chart_signature_packet(packet: Mapping[str, Any]) -> bool:
    meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
    if str(meta.get("inventory_variant") or "").strip() == "chart_signature":
        return True
    return "_chart_exact" in str(packet.get("id") or "")


def _select_packet_inventory(packets: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not packets:
        return []
    selected: list[dict[str, Any]] = []
    domain_counts: dict[str, int] = defaultdict(int)
    gift_forward_seen = False
    for packet in packets:
        promise_type = str(packet.get("promise_type") or "").strip()
        domain = str(packet.get("domain") or "").strip()
        if len(selected) >= 6:
            break
        if domain and domain_counts.get(domain, 0) >= 2 and _safe_float(packet.get("strength"), 0.0) < 0.9:
            continue
        selected.append(dict(packet))
        if domain:
            domain_counts[domain] += 1
        if promise_type in {"gift", "love_style", "mind_style", "mind_identity"}:
            gift_forward_seen = True
    if not gift_forward_seen:
        for packet in packets:
            if str(packet.get("promise_type") or "").strip() in {"gift", "love_style", "mind_style", "mind_identity"}:
                if packet not in selected:
                    selected = [dict(packet), *selected[:5]]
                break
    return selected[:6]


def _backfill_selected_packet_inventory(
    packets: Sequence[Mapping[str, Any]],
    *,
    registry_entries: Mapping[str, Mapping[str, Any]],
    planets: Sequence[Mapping[str, Any]] | None,
    aspects: Sequence[Mapping[str, Any]] | None,
    natal_graph_compact: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None,
    meta_info: Mapping[str, Any] | None,
    locale: str,
) -> list[dict[str, Any]]:
    selected = [dict(packet) for packet in packets if isinstance(packet, Mapping)]
    if len(selected) >= 4:
        return selected[:6]
    if not any(str(packet.get("id") or "").strip() == "relationship_relationships" for packet in selected):
        return selected[:6]
    chart_candidates = _build_chart_signature_candidates(
        registry_entries=registry_entries,
        planets=planets,
        aspects=aspects,
        natal_graph_compact=natal_graph_compact,
        metadata=metadata,
        meta_info=meta_info,
        locale=locale,
        mode="candidate_inventory",
    )
    if not chart_candidates:
        return selected[:6]
    chart_candidates = _dedupe_packets(chart_candidates, mode="candidate_inventory")
    relationship_specific = [
        packet
        for packet in chart_candidates
        if str(packet.get("domain") or "").strip() == "relationship"
        and str(packet.get("id") or "").strip() != "relationship_relationships"
    ]
    if len(relationship_specific) < 2:
        return selected[:6]
    chart_exact_domains = {
        str(packet.get("domain") or "").strip()
        for packet in chart_candidates
        if str(packet.get("domain") or "").strip()
    }
    if (len(chart_candidates) + len(selected)) < 10 or len(chart_exact_domains) < 4:
        return selected[:6]
    selected_ids = {str(packet.get("id") or "").strip() for packet in selected}
    selected_domains = {str(packet.get("domain") or "").strip() for packet in selected if str(packet.get("domain") or "").strip()}
    missing_domain_candidates = [
        packet
        for packet in chart_candidates
        if str(packet.get("id") or "").strip() not in selected_ids
        and str(packet.get("domain") or "").strip()
        and str(packet.get("domain") or "").strip() not in selected_domains
    ]
    if not missing_domain_candidates:
        return selected[:6]
    domain_priority = {"identity": 0, "mind": 1, "relationship": 2, "career": 3}
    missing_domain_candidates.sort(
        key=lambda item: (
            domain_priority.get(str(item.get("domain") or "").strip(), 9),
            -_safe_float(item.get("strength"), 0.0),
            str(item.get("id") or ""),
        )
    )
    selected.append(dict(missing_domain_candidates[0]))
    return selected[:6]


def _merge_lists(items: Sequence[Mapping[str, Any]], key: str) -> list[str]:
    out: list[str] = []
    for item in items:
        values = item.get(key) if isinstance(item.get(key), Sequence) and not isinstance(item.get(key), (str, bytes)) else []
        for value in values:
            clean = str(value).strip()
            if clean and clean not in out:
                out.append(clean)
    return out


def _opening_strategy(promise_type: str) -> str:
    if promise_type == "gift":
        return "gift_forward"
    if promise_type == "wound_to_gift":
        return "sensitivity_to_gift"
    if promise_type == "shadow_or_friction":
        return "friction_to_growth"
    if promise_type in {"love_style", "need"}:
        return "need_or_emotional_scene"
    return "direct_meaning_first"


def _support_items(
    category_support: Mapping[str, Any],
    *,
    kinds: set[str] | None = None,
    keys: set[str] | None = None,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if keys:
        for key in keys:
            values = category_support.get(key) if isinstance(category_support.get(key), Sequence) else []
            for value in values:
                if isinstance(value, Mapping):
                    out.append(dict(value))
    else:
        for key in ("supporting_combo", "hidden_support"):
            values = category_support.get(key) if isinstance(category_support.get(key), Sequence) else []
            for value in values:
                if not isinstance(value, Mapping):
                    continue
                if kinds and str(value.get("kind") or "").strip() not in kinds:
                    continue
                out.append(dict(value))
    return out


def _humanize_contradiction(label: str) -> str:
    normalized = _normalize_text(label)
    if "pressure vs resilience" in normalized:
        return "Bazen de baskı ile dayanıklılık arasındaki çekişme daha belirgin hale gelebilir."
    if "structured originality" in normalized or "structure vs originality" in normalized:
        return "Bir yanın düzen kurmak isterken, başka bir yanın daha farklı ve özgür bir yol arıyor olabilir."
    if "composure vs internal pressure" in normalized:
        return "Dışarıda toplu görünürken, içeride baskıyı daha yoğun taşıyor olabilirsin."
    if "speed vs control" in normalized:
        return "Bir yanın hızlanmak isterken, başka bir yanın her şeyi yeniden kontrol etmek isteyebilir."
    if "closeness vs threshold" in normalized:
        return "Yakınlık istediğin halde, gerçekten açılmadan önce içerde bir eşik daha çalışıyor olabilir."
    return label.strip()


_CONTINUATION_LOWERCASE_WORDS: frozenset[str] = frozenset(
    {
        # Turkish particles / connectors that are valid lowercase tokens
        # immediately before a capitalized continuation word. Inserting a
        # sentence boundary after them would corrupt the sentence
        # (audit P0: "Bazen de Dışarıda..." → "Bazen de. Dışarıda...").
        "de",
        "da",
        "ki",
        "ile",
        "ve",
        "ya",
    }
)


def _normalize_packet_field_text(text: str) -> str:
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return ""

    def _insert_sentence_boundary(match: "re.Match[str]") -> str:
        preceding_word = match.group(1)
        whitespace = match.group(2)
        next_capital = match.group(3)
        # Continuation particles (de / da / ki / ile / ve / ya) must not be
        # treated as sentence enders — the next capitalized word is a noun
        # the particle attaches to, not a new sentence.
        if preceding_word.lower() in _CONTINUATION_LOWERCASE_WORDS:
            return f"{preceding_word}{whitespace}{next_capital}"
        return f"{preceding_word}.{whitespace}{next_capital}"

    clean = re.sub(
        r"(\b[a-zçğıöşü]+)(\s+)([A-ZİÖÜÇĞŞ])",
        _insert_sentence_boundary,
        clean,
    )
    # Drop residual standalone "Bazen de." / "bazen de." fragments that may
    # have been seeded upstream (e.g. cached `shadow_or_friction` strings
    # produced before this normalizer learned to skip the connector). The
    # fragment is removed only when it stands alone as a full sentence; the
    # connector "Bazen de" followed by real continuation text is preserved.
    clean = re.sub(r"(?<![A-Za-zÇĞİıÖŞÜçğöşü0-9])[Bb]azen de\.\s*", "", clean)
    clean = re.sub(r"\s+([,;:.!?])", r"\1", clean)
    clean = re.sub(r"([,;:.!?])([^\s])", r"\1 \2", clean)
    clean = re.sub(r"\s{2,}", " ", clean).strip()
    return _ensure_sentence(clean)


def _combine_packet_fragments(primary: str, secondary: str, *, connector: str) -> str:
    first = " ".join(str(primary or "").split()).strip().rstrip(".")
    second = " ".join(str(secondary or "").split()).strip().rstrip(".")
    if not first:
        return _normalize_packet_field_text(second)
    if not second:
        return _normalize_packet_field_text(first)
    joined = f"{first}. {connector} {second}"
    return _normalize_packet_field_text(joined)


def _normalize_text(text: str) -> str:
    clean = " ".join(str(text or "").split()).strip().lower()
    return clean


def _split_sentences(text: str, *, max_sentences: int) -> list[str]:
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return []
    pieces = [piece.strip() for piece in re.split(r"(?<=[.!?])\s+", clean) if piece.strip()]
    return [_ensure_sentence(piece) for piece in pieces[: max(0, max_sentences)] if piece.strip()]


def _ensure_sentence(text: str) -> str:
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return ""
    return clean if clean.endswith((".", "!", "?")) else f"{clean}."


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
