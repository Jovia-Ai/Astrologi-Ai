from __future__ import annotations

import re
from typing import Any, Dict, Mapping, Sequence

from .natal_selection_config import get_natal_selection_v3_config


_SLOT_ORDER = [
    "primary_identity_spine",
    "secondary_balancing_line",
    "relational_line",
    "work_visibility_line",
    "shadow_protection_line",
]

_SLOT_FAMILY = {
    "primary_identity_spine": "identity",
    "secondary_balancing_line": "identity",
    "relational_line": "relational",
    "work_visibility_line": "visibility",
    "shadow_protection_line": "shadow",
}

_SLOT_ALIASES = {
    "primary_identity_spine": [
        "kimlik",
        "duruş",
        "merkez",
        "benlik",
        "yön",
        "netlik",
        "özgünlük",
    ],
    "secondary_balancing_line": [
        "zihin",
        "denge",
        "ritim",
        "tempo",
        "yapı",
        "sistem",
        "çerçeve",
        "kontrol",
    ],
    "relational_line": [
        "ilişki",
        "yakınlık",
        "güven",
        "bağ",
        "mahremiyet",
        "sadakat",
        "şefkat",
    ],
    "work_visibility_line": [
        "kariyer",
        "iş",
        "görünürlük",
        "etki",
        "üretim",
        "başarı",
        "sahne",
        "network",
        "çevre",
    ],
    "shadow_protection_line": [
        "gölge",
        "korunma",
        "eşik",
        "geri",
        "çekilme",
        "iç",
        "yük",
        "baskı",
        "ev",
        "güven",
    ],
}

_PROFILE_BLOCK_SLOT = {
    "identity_aura": "primary_identity_spine",
    "mind_voice": "secondary_balancing_line",
    "drive_rhythm": "secondary_balancing_line",
    "love_depth": "relational_line",
    "career_visibility": "work_visibility_line",
    "home_roots": "shadow_protection_line",
    "luck_creation": "work_visibility_line",
}

_SECTION_SLOT = {
    "mind_system": "secondary_balancing_line",
    "identity_mechanics": "secondary_balancing_line",
    "relationships": "relational_line",
    "relationships_depth": "relational_line",
    "career_visibility": "work_visibility_line",
}

_PRIMITIVE_ALIASES = {
    "self_definition": ["kimlik", "duruş", "merkez", "benlik", "yön", "netlik", "güneş", "yükselen"],
    "visible_presence": ["görünürlük", "sahne", "etki", "parlamak", "tanınmak", "görünür", "mc"],
    "inner_structure": ["yapı", "çerçeve", "omurga", "disiplin", "ölçü", "kontrol", "satürn"],
    "originality_drive": ["özgün", "farklı", "bağımsız", "ayrışan", "kendi", "uranüs", "uranus"],
    "big_picture_vision": ["vizyon", "ufuk", "anlam", "büyük", "resim", "keşif", "jüpiter", "jupiter"],
    "tone_sensitivity": ["ton", "kelime", "ifade", "yanlış", "anlaşılma", "cümle", "merkür", "mercury"],
    "systems_thinking": ["sistem", "bağlantı", "kurgu", "mimari", "örüntü", "toparlamak"],
    "inner_critic": ["eleştirmen", "standart", "hata", "yük", "baskı", "yetersiz", "satürn", "saturn"],
    "push_pull_drive": ["git", "gel", "hız", "fren", "tempo", "dur", "çek", "kararsız"],
    "methodical_drive": ["yöntem", "plan", "adım", "ölçmek", "düzen", "ritim"],
    "mental_structuring": ["zihin", "zihnin", "düşünce", "netlik", "toplamak", "tasnif", "merkür", "mercury"],
    "intimacy_depth": ["yakınlık", "derinlik", "mahremiyet", "güven", "bağ", "yoğun", "ay", "moon"],
    "relational_security": ["güven", "istikrar", "tutarlılık", "sadakat", "zemin", "şefkat"],
    "graceful_affection": ["zarafet", "uyum", "sevgi", "tatlı", "yumuşak", "venüs", "venus"],
    "transformative_bonding": ["dönüşüm", "yoğunluk", "kriz", "dönüştürücü", "plüton", "pluto"],
    "emotional_threshold": ["eşik", "kolay", "açılmamak", "temkin", "korunma", "geri", "çekilme"],
    "public_refinement": ["kalite", "rafine", "ince", "ayar", "görünürlük", "sunum", "mc"],
    "visibility_sensitivity": ["görünürlük", "göz", "önünde", "hassasiyet", "sahne", "hazır"],
    "backstage_creation": ["perde", "arkası", "hazırlık", "içerde", "içeride", "görünmeden", "taslak"],
    "recharge_through_home": ["ev", "iç", "alan", "toparlanma", "dinlenme", "yuva"],
    "family_self_reliance": ["kendi", "kendine", "yük", "tek", "başına", "aile", "dayanmak"],
    "creation_luck": ["yaratıcılık", "üretim", "akış", "şans", "oyun", "deneme"],
    "network_luck": ["network", "çevre", "ekip", "arkadaşlık", "sosyal", "bağlam"],
    "meaningful_expansion": ["anlam", "büyüme", "genişleme", "ufuk", "keşif", "vizyon"],
}

_CONTRADICTION_ALIASES = {
    "visibility_vs_private_preparation": ["görünürlük", "hazırlık", "perde", "arkası", "hazır", "prova"],
    "closeness_vs_threshold": ["yakınlık", "güven", "eşik", "açılmak", "mahremiyet", "temkin"],
    "structure_vs_originality": ["yapı", "çerçeve", "özgün", "bağımsız", "farklı"],
    "composure_vs_internal_pressure": ["kontrollü", "ölçülü", "baskı", "yük", "iç", "gerilim"],
    "speed_vs_control": ["hız", "fren", "ölçmek", "beklemek", "tempo", "kontrol"],
}

_SURFACE_WEIGHTS = {
    "core_story_ui": 1.0,
    "profile_narrative": 1.0,
    "sections_v2": 0.92,
    "supporting_threads": 0.86,
    "personality_imprint": 0.94,
}

_STOPWORDS = {
    "ve",
    "ile",
    "bu",
    "bir",
    "da",
    "de",
    "gibi",
    "için",
    "çok",
    "daha",
    "ama",
    "hem",
    "sen",
    "sende",
    "senin",
    "olan",
    "olarak",
    "kadar",
    "anda",
    "şeyi",
    "şey",
    "olanı",
    "orada",
    "burada",
}


def _clamp01(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def _safe_avg(values: Sequence[float]) -> float:
    cleaned = [float(value) for value in values if value is not None]
    if not cleaned:
        return 0.0
    return sum(cleaned) / len(cleaned)


def _semantic_tokens(text: Any) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]+", str(text or "").lower())
        if len(token) >= 2 and token not in _STOPWORDS
    }


def _text_blob(*parts: Any) -> str:
    values: list[str] = []
    for part in parts:
        if isinstance(part, str):
            value = part.strip()
            if value:
                values.append(value)
        elif isinstance(part, Sequence) and not isinstance(part, (str, bytes, bytearray)):
            for item in part:
                if isinstance(item, str) and item.strip():
                    values.append(item.strip())
    return " ".join(values).strip()


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _primitive_entries(primitive_scores: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    items = primitive_scores.get("primitive_scores") if isinstance(primitive_scores, Mapping) else []
    return {
        str(item.get("primitive_id") or ""): dict(item)
        for item in items
        if isinstance(item, Mapping) and str(item.get("primitive_id") or "").strip()
    }


def _contradiction_entries(contradiction_signatures: Mapping[str, Any] | None) -> Dict[str, Dict[str, Any]]:
    items = contradiction_signatures.get("signatures") if isinstance(contradiction_signatures, Mapping) else []
    return {
        str(item.get("id") or ""): dict(item)
        for item in items
        if isinstance(item, Mapping) and str(item.get("id") or "").strip()
    }


def _primitive_category_alignment(
    primitive_ids: Sequence[str],
    primitive_lookup: Mapping[str, Mapping[str, Any]],
    slot: str,
) -> float:
    if not primitive_ids:
        return 0.0
    family = _SLOT_FAMILY.get(slot, "identity")
    values = []
    for primitive_id in primitive_ids:
        entry = primitive_lookup.get(str(primitive_id)) if isinstance(primitive_lookup.get(str(primitive_id)), Mapping) else {}
        category = str(entry.get("category") or "")
        if category == family:
            values.append(1.0)
        elif family == "shadow" and category in {"shadow", "compensation", "regulation"}:
            values.append(0.82)
        elif family == "identity" and category in {"identity", "regulation"}:
            values.append(0.78)
        elif family == "visibility" and category in {"visibility", "identity"}:
            values.append(0.76)
        else:
            values.append(0.0)
    return _safe_avg(values)


def _infer_primitives(text: str, primitive_lookup: Mapping[str, Mapping[str, Any]]) -> list[str]:
    tokens = _semantic_tokens(text)
    scored: list[tuple[float, str]] = []
    for primitive_id in primitive_lookup:
        alias_tokens = {
            alias_token
            for alias in _PRIMITIVE_ALIASES.get(str(primitive_id), [])
            for alias_token in _semantic_tokens(alias)
        }
        overlap = _jaccard(tokens, alias_tokens)
        if overlap <= 0.0:
            continue
        scored.append((overlap, str(primitive_id)))
    scored.sort(key=lambda item: (-float(item[0]), item[1]))
    return [primitive_id for score, primitive_id in scored[:3] if score >= 0.12]


def _profile_slot(block_id: str) -> str | None:
    slot = _PROFILE_BLOCK_SLOT.get(str(block_id))
    return str(slot) if slot else None


def _section_slot(block_id: str) -> str | None:
    slot = _SECTION_SLOT.get(str(block_id))
    return str(slot) if slot else None


def _imprint_slot(key: str, text: str) -> str | None:
    match = re.search(r"_house_(\d+)", str(key))
    if match:
        house = int(match.group(1))
        if house == 1:
            return "primary_identity_spine"
        if house in {3, 6, 9}:
            return "secondary_balancing_line"
        if house in {7, 8}:
            return "relational_line"
        if house in {10, 11}:
            return "work_visibility_line"
        if house in {4, 12}:
            return "shadow_protection_line"
    tokens = _semantic_tokens(text)
    if {"ilişki", "yakınlık", "mahremiyet"} & tokens:
        return "relational_line"
    if {"görünürlük", "kariyer", "başarı", "etki"} & tokens:
        return "work_visibility_line"
    if {"ev", "yuva", "korunma", "eşik"} & tokens:
        return "shadow_protection_line"
    if {"zihin", "ifade", "sistem", "yöntem"} & tokens:
        return "secondary_balancing_line"
    if {"kimlik", "duruş", "özgün", "benlik"} & tokens:
        return "primary_identity_spine"
    return None


def _slot_contracts(
    master_selector: Mapping[str, Any],
    primitive_lookup: Mapping[str, Mapping[str, Any]],
    contradiction_lookup: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    contracts: Dict[str, Dict[str, Any]] = {}
    identity_spine = master_selector.get("identity_spine") if isinstance(master_selector.get("identity_spine"), Mapping) else {}
    for slot in _SLOT_ORDER:
        payload = identity_spine.get(slot) if isinstance(identity_spine.get(slot), Mapping) else {}
        source_primitives = [str(item) for item in payload.get("source_primitives") or [] if str(item).strip()]
        contradiction_ids = [str(item) for item in payload.get("contradiction_ids") or [] if str(item).strip()]
        tokens = set(_SLOT_ALIASES.get(slot, []))
        tokens |= _semantic_tokens(payload.get("label"))
        tokens |= _semantic_tokens(payload.get("line_id"))
        for primitive_id in source_primitives + [str(item) for item in payload.get("counterweights") or []]:
            tokens |= {
                alias_token
                for alias in _PRIMITIVE_ALIASES.get(primitive_id, [])
                for alias_token in _semantic_tokens(alias)
            }
        contradiction_tokens: set[str] = set()
        contradiction_primitives: set[str] = set()
        for contradiction_id in contradiction_ids:
            contradiction = (
                contradiction_lookup.get(contradiction_id)
                if isinstance(contradiction_lookup.get(contradiction_id), Mapping)
                else {}
            )
            contradiction_tokens |= {
                alias_token
                for alias in _CONTRADICTION_ALIASES.get(contradiction_id, [])
                for alias_token in _semantic_tokens(alias)
            }
            contradiction_tokens |= _semantic_tokens(contradiction.get("editorial_label"))
            contradiction_primitives |= {
                str(item)
                for item in contradiction.get("source_primitives") or []
                if str(item).strip()
            }
        contracts[slot] = {
            "slot": slot,
            "label": str(payload.get("label") or ""),
            "line_id": str(payload.get("line_id") or ""),
            "family": _SLOT_FAMILY.get(slot, "identity"),
            "source_primitives": source_primitives,
            "counterweights": [str(item) for item in payload.get("counterweights") or [] if str(item).strip()],
            "contradiction_ids": contradiction_ids,
            "tokens": tokens | contradiction_tokens,
            "contradiction_tokens": contradiction_tokens,
            "contradiction_primitives": sorted(contradiction_primitives),
            "confidence": float(payload.get("confidence") or 0.0),
        }
    return contracts


def _extract_profile_blocks(
    payload: Mapping[str, Any],
    primitive_lookup: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    public = payload.get("profile_public") if isinstance(payload.get("profile_public"), Mapping) else {}
    blocks = public.get("blocks") if isinstance(public.get("blocks"), Sequence) else []
    internal = payload.get("profile_internal") if isinstance(payload.get("profile_internal"), Mapping) else {}
    debug_blocks = internal.get("blocks_debug") if isinstance(internal.get("blocks_debug"), Sequence) else []
    debug_by_id = {
        str(item.get("id") or ""): dict(item)
        for item in debug_blocks
        if isinstance(item, Mapping) and str(item.get("id") or "").strip()
    }
    extracted: list[dict[str, Any]] = []
    for block in blocks:
        if not isinstance(block, Mapping):
            continue
        block_id = str(block.get("id") or "").strip()
        debug_block = debug_by_id.get(block_id, {})
        text = _text_blob(
            block.get("headline"),
            block.get("teaser"),
            block.get("body"),
            block.get("micro"),
            block.get("astro_hint"),
            block.get("chips") or [],
        )
        primitive_ids = [
            str(item)
            for item in (
                list(debug_block.get("selected_spine_primitive_ids") or [])
                + list(debug_block.get("selected_tone_primitive_ids") or [])
                + list(debug_block.get("selected_spark_primitive_ids") or [])
            )
            if str(item).strip()
        ]
        if not primitive_ids:
            primitive_ids = _infer_primitives(text, primitive_lookup)
        extracted.append(
            {
                "surface": "profile_narrative",
                "block_id": block_id or "profile_block",
                "target_slot": _profile_slot(block_id),
                "primitive_ids": list(dict.fromkeys(primitive_ids)),
                "text": text,
                "tokens": _semantic_tokens(text),
                "surface_weight": _SURFACE_WEIGHTS["profile_narrative"],
                "is_extra": False,
            }
        )
    return extracted


def _extract_core_story_blocks(
    payload: Mapping[str, Any],
    primitive_lookup: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if not payload:
        return []
    text = _text_blob(
        payload.get("headline"),
        payload.get("text"),
        [str((item or {}).get("value") or "") for item in payload.get("drivers") or [] if isinstance(item, Mapping)],
    )
    primitive_ids = _infer_primitives(text, primitive_lookup)
    return [
        {
            "surface": "core_story_ui",
            "block_id": "core_story_ui",
            "target_slot": "primary_identity_spine",
            "primitive_ids": primitive_ids,
            "text": text,
            "tokens": _semantic_tokens(text),
            "surface_weight": _SURFACE_WEIGHTS["core_story_ui"],
            "is_extra": False,
        }
    ]


def _extract_sections_blocks(
    payload: Sequence[Mapping[str, Any]],
    primitive_lookup: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    extracted: list[dict[str, Any]] = []
    for section in payload or []:
        if not isinstance(section, Mapping):
            continue
        block_id = str(section.get("id") or section.get("legacy_id") or "").strip() or "section"
        text = _text_blob(
            section.get("title"),
            section.get("subtitle"),
            section.get("body"),
            section.get("micro"),
            section.get("chips") or [],
        )
        extracted.append(
            {
                "surface": "sections_v2",
                "block_id": block_id,
                "target_slot": _section_slot(block_id) or _section_slot(str(section.get("legacy_id") or "")),
                "primitive_ids": _infer_primitives(text, primitive_lookup),
                "text": text,
                "tokens": _semantic_tokens(text),
                "surface_weight": _SURFACE_WEIGHTS["sections_v2"],
                "is_extra": False,
            }
        )
    return extracted


def _extract_supporting_thread_blocks(
    payload: Sequence[Mapping[str, Any]],
    primitive_lookup: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    extracted: list[dict[str, Any]] = []
    for thread in payload or []:
        if not isinstance(thread, Mapping):
            continue
        section_id = str(thread.get("section_id") or thread.get("id") or "").strip() or "thread"
        text = _text_blob(
            thread.get("title"),
            thread.get("one_liner"),
            thread.get("paragraph"),
            thread.get("body"),
            thread.get("micro"),
            thread.get("chips") or [],
        )
        extracted.append(
            {
                "surface": "supporting_threads",
                "block_id": str(thread.get("id") or section_id),
                "target_slot": _section_slot(section_id),
                "primitive_ids": _infer_primitives(text, primitive_lookup),
                "text": text,
                "tokens": _semantic_tokens(text),
                "surface_weight": _SURFACE_WEIGHTS["supporting_threads"],
                "is_extra": False,
            }
        )
    return extracted


def _extract_personality_imprint_blocks(
    payload: Mapping[str, Any],
    primitive_lookup: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    extracted: list[dict[str, Any]] = []
    for field_name, is_extra in (("entries", False), ("extra_entries", True)):
        items = payload.get(field_name) if isinstance(payload.get(field_name), Sequence) else []
        for item in items:
            if not isinstance(item, Mapping):
                continue
            key = str(item.get("key") or "").strip() or field_name
            text = _text_blob(
                item.get("label_tr"),
                item.get("aura"),
                item.get("trait"),
                item.get("drive"),
                item.get("shadow"),
                item.get("tags") or [],
                item.get("support_keys") or [],
            )
            primitive_ids = _infer_primitives(f"{key} {text}", primitive_lookup)
            extracted.append(
                {
                    "surface": "personality_imprint",
                    "block_id": key,
                    "target_slot": _imprint_slot(key, text),
                    "primitive_ids": primitive_ids,
                    "text": text,
                    "tokens": _semantic_tokens(text),
                    "surface_weight": _SURFACE_WEIGHTS["personality_imprint"] * (0.88 if is_extra else 1.0),
                    "is_extra": is_extra,
                }
            )
    return extracted


def _extract_surface_blocks(
    surfaces: Mapping[str, Any],
    primitive_lookup: Mapping[str, Mapping[str, Any]],
) -> Dict[str, list[dict[str, Any]]]:
    extracted: Dict[str, list[dict[str, Any]]] = {}
    if isinstance(surfaces.get("core_story_ui"), Mapping):
        extracted["core_story_ui"] = _extract_core_story_blocks(
            surfaces.get("core_story_ui") or {},
            primitive_lookup,
        )
    if isinstance(surfaces.get("profile_narrative"), Mapping):
        extracted["profile_narrative"] = _extract_profile_blocks(
            surfaces.get("profile_narrative") or {},
            primitive_lookup,
        )
    if isinstance(surfaces.get("personality_imprint"), Mapping):
        extracted["personality_imprint"] = _extract_personality_imprint_blocks(
            surfaces.get("personality_imprint") or {},
            primitive_lookup,
        )
    if isinstance(surfaces.get("sections_v2"), Sequence):
        extracted["sections_v2"] = _extract_sections_blocks(
            surfaces.get("sections_v2") or [],
            primitive_lookup,
        )
    if isinstance(surfaces.get("supporting_threads"), Sequence):
        extracted["supporting_threads"] = _extract_supporting_thread_blocks(
            surfaces.get("supporting_threads") or [],
            primitive_lookup,
        )
    return extracted


def _score_block_for_slot(
    block: Mapping[str, Any],
    *,
    slot: str,
    contract: Mapping[str, Any],
    primitive_lookup: Mapping[str, Mapping[str, Any]],
    arbitrator_weights: Mapping[str, Any],
) -> Dict[str, Any]:
    block_primitives = {str(item) for item in block.get("primitive_ids") or [] if str(item).strip()}
    contract_primitives = {str(item) for item in contract.get("source_primitives") or [] if str(item).strip()}
    counterweights = {str(item) for item in contract.get("counterweights") or [] if str(item).strip()}
    contradiction_primitives = {str(item) for item in contract.get("contradiction_primitives") or [] if str(item).strip()}
    tokens = block.get("tokens") if isinstance(block.get("tokens"), set) else set(block.get("tokens") or [])
    contract_tokens = contract.get("tokens") if isinstance(contract.get("tokens"), set) else set(contract.get("tokens") or [])
    contradiction_tokens = contract.get("contradiction_tokens") if isinstance(contract.get("contradiction_tokens"), set) else set(contract.get("contradiction_tokens") or [])

    direct_overlap = _jaccard(block_primitives, contract_primitives)
    counterweight_overlap = _jaccard(block_primitives, counterweights) * 0.55
    contradiction_overlap = _jaccard(block_primitives, contradiction_primitives)
    category_alignment = _primitive_category_alignment(list(block_primitives), primitive_lookup, slot)
    primitive_alignment = max(direct_overlap, counterweight_overlap, category_alignment * 0.72)
    text_alignment = _jaccard(tokens, contract_tokens)
    contradiction_alignment = max(
        contradiction_overlap,
        _jaccard(tokens, contradiction_tokens),
    )
    if block.get("target_slot"):
        slot_alignment = 1.0 if str(block.get("target_slot")) == slot else 0.0
    else:
        slot_alignment = 0.42
    surface_role = float(block.get("surface_weight") or 0.0) if str(block.get("target_slot") or "") == slot else 0.0

    score = _clamp01(
        primitive_alignment * float(arbitrator_weights.get("primitive_alignment_weight") or 0.36)
        + text_alignment * float(arbitrator_weights.get("text_alignment_weight") or 0.24)
        + slot_alignment * float(arbitrator_weights.get("slot_alignment_weight") or 0.16)
        + contradiction_alignment * float(arbitrator_weights.get("contradiction_alignment_weight") or 0.14)
        + surface_role * float(arbitrator_weights.get("surface_role_weight") or 0.10)
    )
    return {
        "score": round(score, 4),
        "primitive_alignment": round(primitive_alignment, 4),
        "text_alignment": round(text_alignment, 4),
        "slot_alignment": round(slot_alignment, 4),
        "contradiction_alignment": round(contradiction_alignment, 4),
        "surface_role": round(surface_role, 4),
    }


def _surface_decision(consistency_score: float, conflict_count: int, block_count: int) -> str:
    if not block_count:
        return "no_content"
    if consistency_score >= 0.68 and conflict_count == 0:
        return "coherent"
    if consistency_score >= 0.54 and conflict_count <= 1:
        return "mostly_coherent"
    if consistency_score >= 0.40:
        return "mixed"
    return "fragmented"


def arbitrate_natal_layers(
    *,
    master_selector: Mapping[str, Any] | None = None,
    surfaces: Mapping[str, Any] | None = None,
    primitive_scores: Mapping[str, Any] | None = None,
    contradiction_signatures: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    config = get_natal_selection_v3_config()
    phase_flags = config.get("phase_flags") if isinstance(config.get("phase_flags"), Mapping) else {}
    enabled = bool(phase_flags.get("layer_arbitration_enabled"))
    debug_only = bool(phase_flags.get("layer_arbitration_debug_only", True))
    weights = (config.get("weights") or {}).get("layer_arbitrator_v1") if isinstance(config.get("weights"), Mapping) else {}
    master_payload = master_selector if isinstance(master_selector, Mapping) else {}
    surface_payload = surfaces if isinstance(surfaces, Mapping) else {}
    primitive_lookup = _primitive_entries(primitive_scores)
    contradiction_lookup = _contradiction_entries(contradiction_signatures)
    contracts = _slot_contracts(master_payload, primitive_lookup, contradiction_lookup)
    extracted = _extract_surface_blocks(surface_payload, primitive_lookup)

    if not any(contracts.get(slot, {}).get("source_primitives") for slot in _SLOT_ORDER):
        return {
            "engine_version": "layer_arbitrator_v1",
            "enabled": enabled,
            "mode": "active" if enabled else ("shadow" if debug_only else "disabled"),
            "scores": {},
            "rejected_or_demoted_blocks": [],
            "debug": {
                "status": "missing_master_selector",
                "extracted_surfaces": {surface: len(blocks) for surface, blocks in extracted.items()},
            },
        }

    scores: Dict[str, Dict[str, Any]] = {}
    rejected_or_demoted_blocks: list[dict[str, Any]] = []
    debug_blocks: Dict[str, list[dict[str, Any]]] = {}
    decision_counts = {"keep": 0, "keep_with_note": 0, "rewrite_to_spine": 0, "demote_to_support": 0}
    conflict_margin = float(weights.get("conflict_margin") or 0.12)
    keep_threshold = float(weights.get("keep_threshold") or 0.58)
    rewrite_threshold = float(weights.get("rewrite_threshold") or 0.40)
    demote_threshold = float(weights.get("demote_threshold") or 0.28)

    for surface_name, blocks in extracted.items():
        block_results: list[dict[str, Any]] = []
        for block in blocks:
            slot_breakdown = {
                slot: _score_block_for_slot(
                    block,
                    slot=slot,
                    contract=contracts.get(slot, {}),
                    primitive_lookup=primitive_lookup,
                    arbitrator_weights=weights,
                )
                for slot in _SLOT_ORDER
            }
            ranked_slots = sorted(
                slot_breakdown.items(),
                key=lambda item: (-float(item[1].get("score") or 0.0), item[0]),
            )
            best_slot, best_breakdown = ranked_slots[0]
            target_slot = str(block.get("target_slot") or "") or best_slot
            target_breakdown = slot_breakdown.get(target_slot) or best_breakdown
            target_score = float(target_breakdown.get("score") or 0.0)
            best_score = float(best_breakdown.get("score") or 0.0)
            conflict = bool(
                block.get("target_slot")
                and best_slot != target_slot
                and (best_score - target_score) >= conflict_margin
            )

            if target_score >= keep_threshold and not conflict:
                action = "keep"
                reason = "aligned_with_spine"
            elif conflict and best_score >= keep_threshold:
                action = "demote_to_support" if surface_name in {"sections_v2", "supporting_threads"} or bool(block.get("is_extra")) else "rewrite_to_spine"
                reason = "stronger_alignment_elsewhere"
            elif target_score < demote_threshold and (surface_name in {"sections_v2", "supporting_threads", "personality_imprint"} or bool(block.get("is_extra"))):
                action = "demote_to_support"
                reason = "low_target_alignment"
            elif target_score < rewrite_threshold:
                action = "rewrite_to_spine"
                reason = "weak_target_alignment"
            else:
                action = "keep_with_note"
                reason = "partial_alignment"

            decision_counts[action] += 1
            result = {
                "surface": surface_name,
                "block_id": str(block.get("block_id") or ""),
                "target_slot": target_slot,
                "best_slot": best_slot,
                "score": round(target_score, 4),
                "best_score": round(best_score, 4),
                "action": action,
                "reason": reason,
                "conflict": conflict,
                "source_primitives": list(block.get("primitive_ids") or []),
                "slot_breakdown": {
                    slot: {
                        **breakdown,
                        "line_id": str((contracts.get(slot) or {}).get("line_id") or ""),
                    }
                    for slot, breakdown in slot_breakdown.items()
                },
            }
            block_results.append(result)
            if action in {"rewrite_to_spine", "demote_to_support"}:
                rejected_or_demoted_blocks.append(
                    {
                        "surface": surface_name,
                        "block_id": result["block_id"],
                        "target_slot": target_slot,
                        "best_slot": best_slot,
                        "action": action,
                        "reason": reason,
                        "score": result["score"],
                        "best_score": result["best_score"],
                        "source_primitives": result["source_primitives"],
                    }
                )

        consistency_score = round(_safe_avg([float(item.get("score") or 0.0) for item in block_results]), 4)
        keep_rate = round(
            _safe_avg([
                1.0 if str(item.get("action")) in {"keep", "keep_with_note"} else 0.0
                for item in block_results
            ]),
            4,
        )
        conflict_count = sum(1 for item in block_results if item.get("conflict"))
        scores[surface_name] = {
            "consistency_score": consistency_score,
            "keep_rate": keep_rate,
            "conflict_count": conflict_count,
            "block_count": len(block_results),
            "decision": _surface_decision(consistency_score, conflict_count, len(block_results)),
            "top_slots": [
                {
                    "block_id": str(item.get("block_id") or ""),
                    "target_slot": str(item.get("target_slot") or ""),
                    "best_slot": str(item.get("best_slot") or ""),
                    "score": float(item.get("score") or 0.0),
                    "action": str(item.get("action") or ""),
                }
                for item in block_results[:6]
            ],
        }
        debug_blocks[surface_name] = block_results

    overall_score = round(_safe_avg([float(item.get("consistency_score") or 0.0) for item in scores.values()]), 4)
    return {
        "engine_version": "layer_arbitrator_v1",
        "enabled": enabled,
        "mode": "active" if enabled else ("shadow" if debug_only else "disabled"),
        "scores": {
            **scores,
            "overall": {
                "consistency_score": overall_score,
                "surface_count": len(scores),
                "decision": _surface_decision(
                    overall_score,
                    sum(int(item.get("conflict_count") or 0) for item in scores.values()),
                    len(scores),
                ),
            },
        },
        "rejected_or_demoted_blocks": rejected_or_demoted_blocks,
        "debug": {
            "contracts": {
                slot: {
                    "line_id": str(contract.get("line_id") or ""),
                    "label": str(contract.get("label") or ""),
                    "source_primitives": list(contract.get("source_primitives") or []),
                    "contradiction_ids": list(contract.get("contradiction_ids") or []),
                }
                for slot, contract in contracts.items()
            },
            "surface_blocks": debug_blocks,
            "decision_counts": decision_counts,
            "extracted_surfaces": {surface: len(items) for surface, items in extracted.items()},
        },
    }
