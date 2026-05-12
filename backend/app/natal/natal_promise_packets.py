from __future__ import annotations

import copy
import re
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from .promise_archetype_registry_sprint1 import (
    REGISTRY_VERSION,
    get_natal_promise_archetype_registry_sprint1,
)

PACKET_VERSION = "natal_promise_packets_v1"
_SCORING_VERSION = "sprint1_context_scoring_v1"
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
    "responsibility": "career",
    "action": "inner_world",
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
}
_DOMAIN_TYPE_FALLBACKS = {
    "mind": {"mind_style": 0.28, "gift": 0.12},
    "communication": {"mind_style": 0.22, "behavior_reflex": 0.12},
    "identity": {"behavior_reflex": 0.2, "gift": 0.08},
    "behavior_reflex": {"behavior_reflex": 0.24, "mind_style": 0.12},
    "inner_world": {"need": 0.2, "wound_to_gift": 0.18, "behavior_reflex": 0.08},
    "spirituality": {"need": 0.18, "wound_to_gift": 0.14},
    "relationship": {"love_style": 0.22, "need": 0.18},
    "love": {"love_style": 0.26, "gift": 0.12},
    "emotional_depth": {"need": 0.18, "love_style": 0.18},
    "career": {"career_signature": 0.26, "wound_to_gift": 0.12},
    "visibility": {"career_signature": 0.22, "wound_to_gift": 0.14},
    "creativity": {"gift": 0.18, "career_signature": 0.1},
    "money_self_worth": {"behavior_reflex": 0.16, "love_style": 0.12, "gift": 0.1},
    "community": {"mind_style": 0.16, "gift": 0.12},
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
    item = planet_map.get(planet.lower()) or {}
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
    "relationship": "relationship",
    "love": "relationship",
    "emotional_depth": "relationship",
    # ``emotional_world`` is the inner emotional life domain (e.g. mind/feeling
    # friction packets list it), not the interpersonal ``relationship`` family.
    # Keep it distinct so it does NOT unlock relationship-section domain bleed.
    "emotional_world": "emotional_world",
    "career": "career",
    "visibility": "career",
    "creativity": "career",
    "money_self_worth": "identity",
    "self_worth": "identity",
    "community": "community",
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


def _normalize_packet_field_text(text: str) -> str:
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return ""
    clean = re.sub(r"([a-zçğıöşü])\s+([A-ZİÖÜÇĞŞ])", r"\1. \2", clean)
    clean = re.sub(r"\s+([,;:.!?])", r"\1", clean)
    clean = re.sub(r"([,;:.!?])([^\s])", r"\1 \2", clean)
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
