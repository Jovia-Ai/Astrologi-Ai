from __future__ import annotations

import os
from typing import Any, Dict, Mapping

from app.narrative.narrative_contract_v2 import build_contract_descriptor_v2
from app.meaning.meaning_graph_builder import build_meaning_graph_v1
from app.meaning.meaning_graph_v1_1_builder import build_meaning_graph_v1_1
from app.meaning.projection_shadow_v1_builder import (
    build_profile_narrative_projection_v1,
    build_profile_v8_projection_v1,
)
from app.narrative.humanize_tr import (
    clean_public_block_tr,
    cleanup_tr_punctuation,
    humanize_compact_item,
    humanize_natal_core_story_tr,
    humanize_natal_layer_tr,
    humanize_tr_text,
    sentence_safe_clamp,
)
from app.natal.narrative.aspect_bundle_selector import select_aspect_bundles
from app.natal.natal_promise_cluster_plan import build_natal_promise_cluster_plan_v1
from app.natal.natal_promise_packets import build_natal_promise_packets_v1
from app.natal.profile_v8_payload_builder import build_profile_and_full_map_v8_payload
from app.natal.profile_insights import build_profile_insight_modules
from app.natal.profile_detail_editorial import (
    build_editorial_detail_blocks_for_imprint_entry,
    build_editorial_detail_blocks_for_profile_block,
    build_editorial_detail_blocks_for_thread,
)
from app.natal.narrative.phrase_lib_tr_profile import humanize_public_chips, soft_public_astro_hint
from .public_models import (
    PublicFlags,
    PublicMetaSummary,
    PublicNarrativeAnchor,
    PublicNatalView,
)

_ENABLED_VALUES = {"1", "true", "yes", "on"}


def _env_enabled(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in _ENABLED_VALUES


def _allowlist_meaning_weighting(value: Any) -> Dict[str, Any]:
    allowed = {
        "primary_theme",
        "secondary_theme",
        "upper_meaning_allowed",
        "pressure_index",
        "support_index",
        "confidence",
        "load_state",
    }
    payload = value if isinstance(value, dict) else {}
    return {key: payload.get(key) for key in allowed if key in payload}


def build_public_natal_view(
    response: Dict[str, Any],
    *,
    locale: str = "tr",
    include_debug: bool = False,
    include_full_profile: bool = False,
) -> Dict[str, Any]:
    meta = response.get("meta") or {}
    narrative_anchor = response.get("narrative_anchor") or {}
    meaning_weighting = response.get("meaning_weighting") or {}

    dynamic_insights_enabled = bool(response.get("dynamic_insights")) or bool(
        _env_enabled("ENABLE_DYNAMIC_INSIGHTS")
    )
    promise_projection_enabled = _env_enabled("ENABLE_NATAL_PROMISE_PROJECTION_V1")
    promise_packet_debug_enabled = include_debug or _env_enabled("ENABLE_NATAL_PROMISE_PACKET_DEBUG")
    raw_sections_v2 = [dict(item) for item in response.get("sections_v2") or [] if isinstance(item, Mapping)]
    raw_supporting_threads = [dict(item) for item in response.get("supporting_threads") or [] if isinstance(item, Mapping)]

    compact = _humanize_user_compact(response.get("user_compact"))
    upper_meaning = _humanize_upper_meaning(response.get("upper_meaning_selected"))

    raw_core_story = response.get("core_story")
    core_story = (
        humanize_natal_core_story_tr(str(raw_core_story))
        if isinstance(raw_core_story, str) and raw_core_story.strip()
        else raw_core_story
    )
    core_story_ui = _humanize_core_story_ui(response.get("core_story_ui"))

    personality_imprint = _humanize_personality_imprint(
        response.get("personality_imprint"),
        include_debug=include_debug,
    )
    supporting_threads = _humanize_supporting_threads(response.get("supporting_threads"))
    narrative_v2 = _build_narrative_v2(response, include_debug=include_debug)
    profile_narrative: Dict[str, Any] | None = None
    sections_v2: list[dict[str, Any]] = []
    profile_v8: Dict[str, Any] | None = None
    full_map_v8: Dict[str, Any] | None = None
    if include_full_profile:
        profile_insight_modules = build_profile_insight_modules(
            moon_sign=_extract_planet_sign(response.get("planets"), "Moon"),
        )
        profile_narrative = _humanize_profile_narrative(
            response.get("profile_narrative"),
            include_debug=include_debug,
            supporting_threads=supporting_threads,
            personality_imprint=personality_imprint,
            narrative_v2=narrative_v2,
            insight_modules=profile_insight_modules,
        )
        sections_v2 = _humanize_sections_v2(response.get("sections_v2"))
        profile_v8, full_map_v8 = build_profile_and_full_map_v8_payload(
            response=response,
            profile_narrative=profile_narrative or {},
            sections_v2=sections_v2,
            supporting_threads=supporting_threads,
            narrative_v2=narrative_v2 or {},
            personality_imprint=personality_imprint or {},
        )
    meaning_graph = build_meaning_graph_v1(
        core_story_ui=core_story_ui if isinstance(core_story_ui, Mapping) else None,
        user_compact=compact if isinstance(compact, Mapping) else None,
        personality_imprint=personality_imprint if isinstance(personality_imprint, Mapping) else None,
        supporting_threads=supporting_threads,
        locale=locale or "tr",
    )
    meaning_graph_v1_1 = build_meaning_graph_v1_1(
        core_story_ui=core_story_ui if isinstance(core_story_ui, Mapping) else None,
        user_compact=compact if isinstance(compact, Mapping) else None,
        personality_imprint=personality_imprint if isinstance(personality_imprint, Mapping) else None,
        supporting_threads=supporting_threads,
        locale=locale or "tr",
    )
    packet_sections_source = raw_sections_v2 or sections_v2
    packet_threads_source = raw_supporting_threads or supporting_threads
    packet_meaning_graph_v1_1 = build_meaning_graph_v1_1(
        core_story_ui=response.get("core_story_ui") if isinstance(response.get("core_story_ui"), Mapping) else None,
        user_compact=response.get("user_compact") if isinstance(response.get("user_compact"), Mapping) else None,
        personality_imprint=response.get("personality_imprint") if isinstance(response.get("personality_imprint"), Mapping) else None,
        supporting_threads=packet_threads_source,
        locale=locale or "tr",
    )
    natal_promise_packets_v1 = build_natal_promise_packets_v1(
        sections_v2=packet_sections_source,
        supporting_threads=packet_threads_source,
        meaning_graph_v1_1=packet_meaning_graph_v1_1,
        planets=response.get("planets") if isinstance(response.get("planets"), list) else None,
        aspects=response.get("aspects") if isinstance(response.get("aspects"), list) else None,
        natal_graph_compact=response.get("natal_graph_compact") if isinstance(response.get("natal_graph_compact"), Mapping) else None,
        metadata=response.get("metadata") if isinstance(response.get("metadata"), Mapping) else None,
        meta_info=response.get("meta_info") if isinstance(response.get("meta_info"), Mapping) else None,
        locale=locale or "tr",
    )
    natal_promise_packets_v1_candidate_inventory = build_natal_promise_packets_v1(
        sections_v2=packet_sections_source,
        supporting_threads=packet_threads_source,
        meaning_graph_v1_1=packet_meaning_graph_v1_1,
        planets=response.get("planets") if isinstance(response.get("planets"), list) else None,
        aspects=response.get("aspects") if isinstance(response.get("aspects"), list) else None,
        natal_graph_compact=response.get("natal_graph_compact") if isinstance(response.get("natal_graph_compact"), Mapping) else None,
        metadata=response.get("metadata") if isinstance(response.get("metadata"), Mapping) else None,
        meta_info=response.get("meta_info") if isinstance(response.get("meta_info"), Mapping) else None,
        locale=locale or "tr",
        mode="candidate_inventory",
    )
    natal_promise_cluster_plan_v1 = build_natal_promise_cluster_plan_v1(
        natal_promise_packets_v1_candidate_inventory.get("packets"),
        locale=locale or "tr",
    )
    profile_narrative_projection_v1 = build_profile_narrative_projection_v1(
        meaning_graph_v1_1=meaning_graph_v1_1,
        natal_promise_packets_v1=natal_promise_packets_v1 if promise_projection_enabled else None,
        natal_promise_cluster_plan_v1=natal_promise_cluster_plan_v1 if promise_projection_enabled else None,
        include_packet_debug=promise_packet_debug_enabled,
    )
    profile_v8_projection_v1 = build_profile_v8_projection_v1(
        meaning_graph_v1_1=meaning_graph_v1_1,
        natal_promise_packets_v1=natal_promise_packets_v1 if promise_projection_enabled else None,
        natal_promise_cluster_plan_v1=natal_promise_cluster_plan_v1 if promise_projection_enabled else None,
        include_packet_debug=promise_packet_debug_enabled,
    )

    public = PublicNatalView(
        locale=locale or "tr",
        core_story=core_story,
        core_story_ui=core_story_ui,
        user_compact=compact,
        upper_meaning=upper_meaning,
        theme_scores=response.get("theme_scores"),
        meta_summary=PublicMetaSummary(
            pressure_index=meta.get("pressure_index"),
            support_index=meta.get("support_index"),
            uncertainty=None,
        ),
        meaning_weighting=_allowlist_meaning_weighting(meaning_weighting),
        data_quality_summary=(response.get("data_quality") or {}).get("summary"),
        narrative_anchor=PublicNarrativeAnchor(
            domain=narrative_anchor.get("domain"),
        ),
        natal_graph_compact=_allowlist_natal_graph(response.get("natal_graph_compact")),
        personality_imprint=personality_imprint,
        profile_narrative=profile_narrative,
        profile_v8=profile_v8,
        full_map_v8=full_map_v8,
        meaning_graph=meaning_graph,
        meaning_graph_v1_1=meaning_graph_v1_1,
        profile_narrative_projection_v1=profile_narrative_projection_v1,
        profile_v8_projection_v1=profile_v8_projection_v1,
        sections_v2=sections_v2,
        supporting_threads=supporting_threads,
        narrative_v2=narrative_v2,
        flags=PublicFlags(
            dynamic_insights_enabled=dynamic_insights_enabled,
            premium_mode=bool(response.get("premium_mode")),
        ),
    )
    return public.model_dump()


def _humanize_user_compact(value: Any) -> Dict[str, Any] | None:
    compact = value if isinstance(value, dict) else None
    if not compact:
        return compact
    out = dict(compact)
    domains = out.get("domains") if isinstance(out.get("domains"), list) else []
    normalized_domains = []
    for domain in domains:
        if not isinstance(domain, dict):
            continue
        normalized = humanize_compact_item(domain)
        highlights = normalized.get("highlights") if isinstance(normalized.get("highlights"), list) else []
        normalized["highlights"] = [
            humanize_compact_item(item) if isinstance(item, dict) else item for item in highlights
        ]
        normalized_domains.append(normalized)
    out["domains"] = normalized_domains

    micro = out.get("micro_insights") if isinstance(out.get("micro_insights"), list) else []
    out["micro_insights"] = [
        humanize_compact_item(item) if isinstance(item, dict) else item for item in micro
    ]
    return out


def _humanize_upper_meaning(value: Any) -> Dict[str, Any] | None:
    payload = value if isinstance(value, dict) else None
    if not payload:
        return payload
    out = dict(payload)
    for key in ("title", "condition", "how_to_use", "message"):
        raw = out.get(key)
        if isinstance(raw, str) and raw.strip():
            out[key] = humanize_tr_text(raw, max_sentences=3)
    lines = out.get("lines")
    if isinstance(lines, list):
        out["lines"] = [humanize_tr_text(str(line), max_sentences=2) for line in lines if str(line).strip()]
    return out


def _allowlist_natal_graph(value: Any) -> Dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    allowed = {"house_rulers", "dominant_loops", "importance"}
    return {key: value.get(key) for key in allowed if key in value}


def _humanize_supporting_threads(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        for key, max_sentences in (("one_liner", 2), ("paragraph", 5), ("body", 5), ("micro", 2)):
            raw = entry.get(key)
            if isinstance(raw, str) and raw.strip():
                entry[key] = humanize_natal_layer_tr(raw, max_sentences=max_sentences, layer="thread")
        out.append(entry)
    return out


def _humanize_sections_v2(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        for key, max_sentences in (("subtitle", 2), ("body", 5), ("micro", 2)):
            raw = entry.get(key)
            if isinstance(raw, str) and raw.strip():
                entry[key] = humanize_natal_layer_tr(raw, max_sentences=max_sentences, layer="section")
        out.append(entry)
    return out


_PROFILE_BLOCK_FAMILY_BY_ID = {
    "identity_aura": "self_definition",
    "mind_voice": "mind_mechanics",
    "drive_rhythm": "desire_style",
    "love_depth": "intimacy_guard",
    "career_visibility": "visible_power",
    "home_roots": "retreat_recharge",
    "luck_creation": "creative_channel",
}

_PROFILE_BUNDLE_FAMILY_BY_TYPE = {
    "contradiction_bundle": "contradiction_core",
    "emotional_regulation_bundle": "protection_pattern",
    "mental_style_bundle": "mind_mechanics",
    "relational_pattern_bundle": "intimacy_guard",
    "angle_identity_bundle": "outer_inner_split",
    "pressure_growth_bundle": "control_vs_flow",
    "soft_capacity_bundle": "creative_channel",
    "personal_core_bundle": "self_definition",
}

_PROFILE_EDITORIAL_TITLES = {
    "outer_inner_split": "Dışarıdan ve içeriden",
    "mind_mechanics": "Zihnin nasıl çalışıyor",
    "protection_pattern": "Kendini nasıl koruyorsun",
    "intimacy_guard": "Yakınlık sende nasıl açılıyor",
    "visible_power": "Dışarıya verdiğin iz",
    "control_vs_flow": "Tutma ve bırakma dengesi",
    "creative_channel": "Fırsatın aktığı yer",
    "self_definition": "Sende kolay tanınan çizgi",
    "contradiction_core": "İçeride iki yönün nasıl çalışıyor",
}


def _extract_planet_sign(value: Any, target_planet: str) -> str:
    planets = value if isinstance(value, list) else []
    target = target_planet.strip().lower()
    for item in planets:
        if not isinstance(item, Mapping):
            continue
        label = str(item.get("planet") or item.get("name") or "").strip().lower()
        if label != target:
            continue
        sign = str(item.get("sign") or item.get("zodiac_sign") or "").strip()
        if sign:
            return sign
    return ""


def _editorial_profile_title(family: str, *, fallback: str = "Sende öne çıkan taraf") -> str:
    return _PROFILE_EDITORIAL_TITLES.get(family, fallback)


def _editorial_phrase_list(values: list[str], *, limit: int = 3) -> str:
    cleaned = [
        cleanup_tr_punctuation(str(item).strip())
        for item in values[:limit]
        if str(item).strip()
    ]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} ve {cleaned[1]}"
    return f"{', '.join(cleaned[:-1])} ve {cleaned[-1]}"


def _editorial_bundle_teaser(*, family: str, recognition: list[str], gifts: list[str], reflex: list[str]) -> str:
    lead = _editorial_phrase_list(recognition, limit=2)
    if not lead:
        lead = _editorial_phrase_list(gifts, limit=2)
    if not lead:
        lead = _editorial_phrase_list(reflex, limit=2)
    if not lead:
        return _editorial_profile_title(family)

    return {
        "mind_mechanics": f"Zihninde ilk öne çıkan şey çoğu zaman {lead} oluyor.",
        "intimacy_guard": f"Yakınlıkta önce {lead} tarafın devreye giriyor.",
        "creative_channel": f"Akışın en çok {lead} olduğunda güçleniyor.",
        "outer_inner_split": f"İnsanlar sende önce {lead} tarafını hissediyor.",
        "visible_power": f"İnsanlar sende önce {lead} tarafını fark ediyor.",
        "control_vs_flow": f"İçinde aynı anda {lead} çalışan bir denge var.",
        "protection_pattern": f"Zorlandığında ilk devreye {lead} tarafın giriyor.",
        "contradiction_core": f"İçinde aynı anda {lead} isteyen iki yön var.",
        "self_definition": f"İnsanların sende ilk fark ettiği şey çoğu zaman {lead} oluyor.",
    }.get(family, f"Sende en çok {lead} tarafı öne çıkıyor.")


def _editorial_bundle_body(
    *,
    family: str,
    recognition: list[str],
    gifts: list[str],
    reflex: list[str],
    domains: list[str],
) -> str:
    domain_text = _editorial_phrase_list(domains, limit=2)
    recognition_text = _editorial_phrase_list(recognition, limit=3)
    gift_text = _editorial_phrase_list(gifts, limit=2)
    reflex_text = _editorial_phrase_list(reflex, limit=2)

    sentences: list[str] = []
    if domain_text:
        domain_templates = {
            "mind_mechanics": f"Bu tema en çok {domain_text} alanında kendini gösteriyor.",
            "intimacy_guard": f"Bu tema en çok {domain_text} alanında hissediliyor.",
            "creative_channel": f"Bu akış en çok {domain_text} alanında açılıyor.",
            "visible_power": f"Bu görünürlük çizgisi en çok {domain_text} alanında belirginleşiyor.",
        }
        sentences.append(
            domain_templates.get(
                family,
                f"Bu tema en çok {domain_text} alanında kendini gösteriyor.",
            )
        )
    if recognition_text:
        sentences.append(f"İnsanların sende ilk fark ettiği şey çoğu zaman {recognition_text} oluyor.")
    if gift_text:
        sentences.append(f"Dengede olduğunda sende en çok {gift_text} öne çıkıyor.")
    if reflex_text:
        sentences.append(f"Zorlandığında ise {reflex_text} tarafın öne çıkabiliyor.")

    if not sentences:
        return _editorial_profile_title(family)
    return " ".join(sentences)


def _editorial_bundle_micro(*, gifts: list[str], reflex: list[str]) -> str:
    gift_text = _editorial_phrase_list(gifts, limit=1)
    reflex_text = _editorial_phrase_list(reflex, limit=1)
    if reflex_text:
        return f"Zorlandığında {reflex_text} tarafın daha hızlı öne çıkabilir."
    if gift_text:
        return f"Dengede olduğunda sende en çok {gift_text} öne çıkıyor."
    return ""


def _humanize_profile_narrative(
    value: Any,
    *,
    include_debug: bool = False,
    supporting_threads: list[dict[str, Any]] | None = None,
    personality_imprint: dict[str, Any] | None = None,
    narrative_v2: dict[str, Any] | None = None,
    insight_modules: list[dict[str, Any]] | None = None,
) -> Dict[str, Any] | None:
    payload = value if isinstance(value, dict) else {}
    if not payload and not insight_modules:
        return None
    public_payload = payload.get("profile_public") if isinstance(payload.get("profile_public"), dict) else {}
    blocks = public_payload.get("blocks") if isinstance(public_payload.get("blocks"), list) else []
    normalized_blocks: list[dict[str, Any]] = []
    for item in blocks:
        if not isinstance(item, dict):
            continue
        entry = dict(item)
        block_id = str(entry.get("id") or "").strip()
        headline = entry.get("headline")
        if isinstance(headline, str) and headline.strip():
            entry["headline"] = _soft_word_clamp(humanize_tr_text(headline, max_sentences=2), 34)
        teaser = entry.get("teaser")
        if isinstance(teaser, str) and teaser.strip():
            entry["teaser"] = _soft_word_clamp(humanize_tr_text(teaser, max_sentences=2), 140)
        body = entry.get("body")
        if isinstance(body, str) and body.strip():
            entry["body"] = sentence_safe_clamp(humanize_tr_text(body, max_sentences=4), max_chars=520, max_sentences=4)
        micro = entry.get("micro")
        if isinstance(micro, str):
            entry["micro"] = sentence_safe_clamp(humanize_tr_text(micro, max_sentences=2), max_chars=160, max_sentences=2) if micro.strip() else ""
        astro_hint = entry.get("astro_hint")
        entry["astro_hint"] = (
            _soft_word_clamp(
                soft_public_astro_hint(block_id, str(astro_hint or "").strip()),
                72,
            )
            if isinstance(astro_hint, str) and astro_hint.strip()
            else soft_public_astro_hint(block_id, "")
        )
        astro_sources = entry.get("astro_sources") if isinstance(entry.get("astro_sources"), list) else []
        entry["astro_sources"] = [
            cleanup_tr_punctuation(str(item).strip())
            for item in astro_sources
            if str(item).strip()
        ][:3]
        entry["chips"] = humanize_public_chips(
            block_id,
            entry.get("chips") if isinstance(entry.get("chips"), list) else [],
        )
        normalized_blocks.append(clean_public_block_tr(entry))
    v3_payload = _build_profile_narrative_v3(
        normalized_blocks,
        supporting_threads=supporting_threads or [],
        personality_imprint=personality_imprint or {},
        narrative_v2=narrative_v2 or {},
    )
    out: Dict[str, Any] = {
        "profile_public": {
            "engine_version": public_payload.get("engine_version"),
            "blocks": normalized_blocks,
            "insight_modules": [
                dict(item)
                for item in (insight_modules or [])
                if isinstance(item, dict)
            ],
            **v3_payload,
        }
    }
    if include_debug and isinstance(payload.get("profile_internal"), dict):
        out["profile_internal"] = payload.get("profile_internal")
    return out


def _build_profile_narrative_v3(
    normalized_blocks: list[dict[str, Any]],
    *,
    supporting_threads: list[dict[str, Any]],
    personality_imprint: dict[str, Any],
    narrative_v2: dict[str, Any],
) -> dict[str, Any]:
    thread_detail_blocks_by_family = _supporting_thread_detail_blocks_by_family(
        supporting_threads,
    )
    candidate_blocks: list[dict[str, Any]] = [
        _augment_profile_block(
            block,
            family=_PROFILE_BLOCK_FAMILY_BY_ID.get(str(block.get("id") or "").strip(), "identity"),
            emphasis="candidate",
            origin="profile_block",
        )
        for block in normalized_blocks
    ]

    boosted_families = {
        _PROFILE_BUNDLE_FAMILY_BY_TYPE.get(
            str(bundle.get("bundle_type") or "").strip(),
            "",
        )
        for bundle in _selected_bundles_from_v2(narrative_v2)
    }
    boosted_families.update(
        _profile_family_for_thread(
            str(thread.get("section_id") or thread.get("id") or "").strip(),
            str(thread.get("title") or "").strip(),
        )
        for thread in supporting_threads
    )
    boosted_families.discard("")

    identity_block = next(
        (
            block
            for block in candidate_blocks
            if str(block.get("id") or "").strip() == "identity_aura"
        ),
        None,
    )
    remaining_blocks = [
        block for block in candidate_blocks if block is not identity_block
    ]
    remaining_blocks.sort(
        key=lambda block: _score_profile_block_for_v3(
            block,
            boosted_families=boosted_families,
        ),
        reverse=True,
    )

    core_blocks = []
    if identity_block is not None:
        core_blocks.append(
            _augment_profile_block(
                identity_block,
                family=str(identity_block.get("family") or "self_definition"),
                emphasis="core",
                origin=str(identity_block.get("origin") or "profile_block"),
            )
        )
    for block in remaining_blocks[: max(0, 4 - len(core_blocks))]:
        core_blocks.append(
            _augment_profile_block(
                block,
                family=str(block.get("family") or "identity"),
                emphasis="core",
                origin=str(block.get("origin") or "profile_block"),
            )
        )

    core_ids = {str(block.get("id") or "").strip() for block in core_blocks}
    extra_blocks: list[dict[str, Any]] = [
        _augment_profile_block(
            block,
            family=str(block.get("family") or "identity"),
            emphasis="extra",
            origin=str(block.get("origin") or "profile_block"),
        )
        for block in candidate_blocks
        if str(block.get("id") or "").strip() not in core_ids
    ]

    for bundle in _selected_bundles_from_v2(narrative_v2)[:2]:
        synthesized = _bundle_as_profile_block(bundle)
        if synthesized:
            extra_blocks.append(synthesized)

    for thread in supporting_threads[:3]:
        synthesized = _thread_as_profile_block(thread)
        if synthesized:
            extra_blocks.append(synthesized)

    extra_blocks = _dedupe_profile_cards(extra_blocks)[:6]

    detail_cards: list[dict[str, Any]] = []
    for block in [*core_blocks, *extra_blocks]:
        detail_cards.append(
            _detail_card_from_profile_block(
                block,
                supporting_thread_detail_blocks=thread_detail_blocks_by_family.get(
                    str(block.get("family") or "").strip(),
                    [],
                ),
            )
        )

    for entry in _personality_imprint_detail_cards(personality_imprint)[:4]:
        detail_cards.append(entry)

    detail_cards = _dedupe_profile_cards(detail_cards)[:12]

    return {
        "schema_version": "profile_narrative_public_v3",
        "core_blocks": core_blocks,
        "extra_blocks": extra_blocks,
        "detail_cards": detail_cards,
    }


def _augment_profile_block(
    block: Mapping[str, Any],
    *,
    family: str,
    emphasis: str,
    origin: str,
) -> dict[str, Any]:
    out = dict(block)
    card_key = str(out.get("card_key") or "").strip() or f"{str(out.get('id') or 'block').strip()}_detail"
    out["family"] = family
    out["emphasis"] = emphasis
    out["origin"] = origin
    out["card_key"] = card_key
    return out


def _score_profile_block_for_v3(
    block: Mapping[str, Any],
    *,
    boosted_families: set[str],
) -> int:
    family = str(block.get("family") or "").strip()
    astro_sources = block.get("astro_sources") if isinstance(block.get("astro_sources"), list) else []
    chips = block.get("chips") if isinstance(block.get("chips"), list) else []
    score = 0
    score += min(len(astro_sources), 3) * 4
    score += min(len(chips), 4) * 2
    if str(block.get("astro_hint") or "").strip():
        score += 2
    if family in boosted_families:
        score += 5
    return score


def _selected_bundles_from_v2(narrative_v2: dict[str, Any]) -> list[dict[str, Any]]:
    selector = narrative_v2.get("aspect_bundle_selector")
    if not isinstance(selector, dict):
        return []
    selected = selector.get("selected_bundles")
    if not isinstance(selected, list):
        return []
    return [item for item in selected if isinstance(item, dict)]


def _bundle_as_profile_block(bundle: Mapping[str, Any]) -> dict[str, Any] | None:
    bundle_type = str(bundle.get("bundle_type") or "").strip()
    bundle_id = str(bundle.get("bundle_id") or "").strip() or bundle_type or "bundle"
    recognition = [cleanup_tr_punctuation(str(item).strip()) for item in (bundle.get("recognition_tags") or []) if str(item).strip()]
    gifts = [cleanup_tr_punctuation(str(item).strip()) for item in (bundle.get("gift_tags") or []) if str(item).strip()]
    reflex = [cleanup_tr_punctuation(str(item).strip()) for item in (bundle.get("reflex_tags") or []) if str(item).strip()]
    domains = [cleanup_tr_punctuation(str(item).strip()) for item in (bundle.get("domains") or []) if str(item).strip()]
    if not recognition and not gifts and not reflex:
        return None
    family = _PROFILE_BUNDLE_FAMILY_BY_TYPE.get(bundle_type, "inner_layer")
    title = _editorial_profile_title(family)
    entry = {
        "id": f"bundle_{bundle_id}",
        "headline": title,
        "teaser": _editorial_bundle_teaser(
            family=family,
            recognition=recognition,
            gifts=gifts,
            reflex=reflex,
        ),
        "subtitle": "",
        "body": _editorial_bundle_body(
            family=family,
            recognition=recognition,
            gifts=gifts,
            reflex=reflex,
            domains=domains,
        ),
        "micro": _editorial_bundle_micro(gifts=gifts, reflex=reflex),
        "astro_hint": "",
        "astro_sources": [
            cleanup_tr_punctuation(str(item).strip())
            for item in (bundle.get("astro_sources") or [])
            if str(item).strip()
        ][:3],
        "chips": domains[:3] or gifts[:3],
        "family": family,
        "emphasis": "extra",
        "origin": "narrative_v2_bundle",
        "card_key": f"{bundle_id}_detail",
    }
    return clean_public_block_tr(entry)


def _thread_as_profile_block(thread: Mapping[str, Any]) -> dict[str, Any] | None:
    title = cleanup_tr_punctuation(str(thread.get("title") or "").strip())
    teaser = cleanup_tr_punctuation(str(thread.get("one_liner") or "").strip())
    body = cleanup_tr_punctuation(str(thread.get("paragraph") or thread.get("body") or "").strip())
    if not title or not teaser:
        return None
    section_id = str(thread.get("section_id") or thread.get("id") or "").strip()
    family = _profile_family_for_thread(section_id, title)
    entry = {
        "id": str(thread.get("id") or section_id or title).strip(),
        "headline": title,
        "teaser": teaser,
        "subtitle": "",
        "body": body,
        "micro": cleanup_tr_punctuation(str(thread.get("micro") or "").strip()),
        "astro_hint": "",
        "astro_sources": [],
        "chips": [cleanup_tr_punctuation(str(item).strip()) for item in (thread.get("chips") or []) if str(item).strip()][:3],
        "detail_blocks": build_editorial_detail_blocks_for_thread(thread),
        "family": family,
        "emphasis": "extra",
        "origin": "supporting_thread",
        "card_key": f"{str(thread.get('id') or section_id or 'thread').strip()}_detail",
    }
    return clean_public_block_tr(entry)


def _profile_family_for_thread(section_id: str, title: str) -> str:
    label = f"{section_id} {title}".lower()
    if "mind" in label or "zihin" in label:
        return "mind_mechanics"
    if "identity" in label or "kimlik" in label:
        return "outer_inner_split"
    if (
        "career" in label
        or "kariyer" in label
        or "görünür" in label
        or "gorunur" in label
        or "iş" in label
        or "is" in label
    ):
        return "visible_power"
    if "home" in label or "kök" in label or "ev" in label:
        return "retreat_recharge"
    if "relation" in label or "iliş" in label or "yakın" in label:
        return "intimacy_guard"
    return "inner_layer"


def _supporting_thread_detail_blocks_by_family(
    supporting_threads: list[dict[str, Any]],
) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for thread in supporting_threads:
        if not isinstance(thread, Mapping):
            continue
        family = _profile_family_for_thread(
            str(thread.get("section_id") or thread.get("id") or "").strip(),
            str(thread.get("title") or "").strip(),
        )
        if not family or family in out:
            continue
        detail_blocks = build_editorial_detail_blocks_for_thread(thread)
        if detail_blocks:
            out[family] = detail_blocks
    return out


def _detail_card_from_profile_block(
    block: Mapping[str, Any],
    *,
    supporting_thread_detail_blocks: list[str] | None = None,
) -> dict[str, Any]:
    detail_blocks = build_editorial_detail_blocks_for_profile_block(
        block,
        supporting_blocks=supporting_thread_detail_blocks,
    )
    return {
        "card_key": str(block.get("card_key") or "").strip() or f"{str(block.get('id') or 'block').strip()}_detail",
        "id": str(block.get("id") or "").strip(),
        "family": str(block.get("family") or "").strip(),
        "origin": str(block.get("origin") or "").strip(),
        "eyebrow": str(block.get("headline") or "").strip(),
        "title": str(block.get("headline") or "").strip(),
        "summary": str(block.get("teaser") or "").strip(),
        "body": str(block.get("body") or "").strip(),
        "micro": str(block.get("micro") or "").strip(),
        "detail_blocks": detail_blocks,
        "chips": list(block.get("chips") or [])[:4],
        "astro_sources": list(block.get("astro_sources") or [])[:3],
    }


def _personality_imprint_detail_cards(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    entries = payload.get("entries") if isinstance(payload.get("entries"), list) else []
    extra_entries = payload.get("extra_entries") if isinstance(payload.get("extra_entries"), list) else []
    support_entries = payload.get("support_entries") if isinstance(payload.get("support_entries"), list) else []
    support_entries_by_key = {
        str(item.get("key") or "").strip(): item
        for item in support_entries
        if isinstance(item, dict) and str(item.get("key") or "").strip()
    }
    cards: list[dict[str, Any]] = []
    for item in [*entries, *extra_entries]:
        if not isinstance(item, dict):
            continue
        title = cleanup_tr_punctuation(str(item.get("label_tr") or "").strip())
        if not title:
            continue
        family = {
            "aspect": "contradiction_core",
            "house_placement": "placement_signature",
            "sign_placement": "tone_signature",
        }.get(str(item.get("kind") or "").strip(), "placement_signature")
        detail_blocks = build_editorial_detail_blocks_for_imprint_entry(
            item,
            support_entries_by_key=support_entries_by_key,
        )
        body = "\n\n".join(detail_blocks)
        if not body:
            continue
        cards.append(
            {
                "card_key": f"{str(item.get('key') or title).strip()}_detail",
                "id": str(item.get("key") or "").strip(),
                "family": family,
                "origin": "personality_imprint",
                "eyebrow": "Kişilik izi",
                "title": title,
                "summary": cleanup_tr_punctuation(str(item.get("aura") or item.get("trait") or title).strip()),
                "body": body,
                "micro": "",
                "detail_blocks": detail_blocks,
                "chips": [cleanup_tr_punctuation(str(tag).strip()) for tag in (item.get("tags") or []) if str(tag).strip()][:4],
                "astro_sources": [],
            }
        )
    return cards


def _dedupe_profile_cards(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        key = str(item.get("card_key") or item.get("id") or item.get("title") or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _humanize_personality_imprint(value: Any, *, include_debug: bool = False) -> Dict[str, Any] | None:
    payload = value if isinstance(value, dict) else None
    if not payload:
        return None
    def _normalize_imprint_entry(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "key": str(item.get("key") or "").strip(),
            "kind": str(item.get("kind") or "").strip(),
            "label_tr": cleanup_tr_punctuation(str(item.get("label_tr") or "").strip()),
            "tags": [
                cleanup_tr_punctuation(str(tag).strip())
                for tag in (item.get("tags") or [])
                if str(tag).strip()
            ],
            "aura": cleanup_tr_punctuation(str(item.get("aura") or "").strip()),
            "trait": cleanup_tr_punctuation(str(item.get("trait") or "").strip()),
            "drive": cleanup_tr_punctuation(str(item.get("drive") or "").strip()),
            "shadow": cleanup_tr_punctuation(str(item.get("shadow") or "").strip()),
            "background_hint": cleanup_tr_punctuation(str(item.get("background_hint") or "").strip()),
            "gift": cleanup_tr_punctuation(str(item.get("gift") or "").strip()),
            "support_keys": [
                str(key).strip()
                for key in (item.get("support_keys") or [])
                if str(key).strip()
            ],
        }
    out: Dict[str, Any] = {
        "engine_version": payload.get("engine_version"),
        "library_version": payload.get("library_version"),
        "locale": payload.get("locale") or "tr",
        "headline": cleanup_tr_punctuation(str(payload.get("headline") or "").strip()),
        "render_shape": payload.get("render_shape") if isinstance(payload.get("render_shape"), dict) else {},
        "entries": [],
        "extra_entries": [],
        "support_entries": [],
        "bundles": [],
        "extra_bundles": [],
    }
    entries = payload.get("entries") if isinstance(payload.get("entries"), list) else []
    for item in entries:
        if not isinstance(item, dict):
            continue
        out["entries"].append(_normalize_imprint_entry(item))
    extra_entries = payload.get("extra_entries") if isinstance(payload.get("extra_entries"), list) else []
    for item in extra_entries:
        if not isinstance(item, dict):
            continue
        out["extra_entries"].append(_normalize_imprint_entry(item))
    support_entries = payload.get("support_entries") if isinstance(payload.get("support_entries"), list) else []
    for item in support_entries:
        if not isinstance(item, dict):
            continue
        out["support_entries"].append(_normalize_imprint_entry(item))
    def _normalize_bundle(item: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(item.get("id") or "").strip(),
            "dominant_key": str(item.get("dominant_key") or "").strip(),
            "dominant_kind": str(item.get("dominant_kind") or "").strip(),
            "related_planets": [
                str(planet).strip()
                for planet in (item.get("related_planets") or [])
                if str(planet).strip()
            ],
            "support_keys": [
                str(key).strip()
                for key in (item.get("support_keys") or [])
                if str(key).strip()
            ],
        }
    bundles = payload.get("bundles") if isinstance(payload.get("bundles"), list) else []
    for item in bundles:
        if not isinstance(item, dict):
            continue
        out["bundles"].append(_normalize_bundle(item))
    extra_bundles = payload.get("extra_bundles") if isinstance(payload.get("extra_bundles"), list) else []
    for item in extra_bundles:
        if not isinstance(item, dict):
            continue
        out["extra_bundles"].append(_normalize_bundle(item))
    if include_debug and isinstance(payload.get("selection_debug"), dict):
        out["selection_debug"] = payload.get("selection_debug")
    return out


def _soft_word_clamp(text: str, preferred_max_chars: int) -> str:
    clean = cleanup_tr_punctuation(str(text or "").strip())
    if not clean or len(clean) <= preferred_max_chars:
        return clean
    words = clean.split()
    best = ""
    current: list[str] = []
    for word in words:
        tentative = " ".join(current + [word]).strip()
        if len(tentative) > preferred_max_chars:
            break
        current.append(word)
        best = tentative
    return best or clean


def _humanize_core_story_ui(value: Any) -> Dict[str, Any] | None:
    payload = value if isinstance(value, dict) else None
    if not payload:
        return None
    out = dict(payload)
    headline = out.get("headline")
    if isinstance(headline, str) and headline.strip():
        out["headline"] = humanize_tr_text(headline, max_sentences=2)
    text = out.get("text")
    if isinstance(text, str) and text.strip():
        out["text"] = humanize_tr_text(text, max_sentences=5)
    return out


def _build_narrative_v2(response: Dict[str, Any], *, include_debug: bool) -> Dict[str, Any]:
    descriptor = build_contract_descriptor_v2()
    bundles = select_aspect_bundles(response)
    payload: Dict[str, Any] = {
        "contract_version": descriptor["contract_version"],
        "aspect_bundle_selector": bundles,
    }
    if include_debug:
        payload.update(
            {
                "section_priority_matrix": descriptor.get("section_priority_matrix"),
                "field_sets": descriptor.get("field_sets"),
                "hook_families": descriptor.get("hook_families"),
                "fallback_rules": descriptor.get("fallback_rules"),
                "migration_map": descriptor.get("migration_map"),
            }
        )
    return payload
