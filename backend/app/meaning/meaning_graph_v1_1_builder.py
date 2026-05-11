from __future__ import annotations

import re
from hashlib import sha1
from typing import Any, Dict, List, Mapping, Sequence

LAYER_TAXONOMY = (
    "recognition",
    "cause",
    "mechanism",
    "effect",
    "shadow",
    "potential",
)

NODE_TYPE_ENUM = (
    "narrative",
    "signal",
    "guidance",
    "quality",
    "reference",
)

DOMAIN_TAXONOMY = (
    "identity",
    "relationships",
    "career",
    "mind",
    "emotional",
    "inner_world",
    "life_direction",
    "general",
)

_DOMAIN_ALIASES = {
    "identity": "identity",
    "kimlik": "identity",
    "self": "identity",
    "benlik": "identity",
    "relations": "relationships",
    "relationship": "relationships",
    "relationships": "relationships",
    "iliski": "relationships",
    "career": "career",
    "kariyer": "career",
    "is": "career",
    "mind": "mind",
    "zihin": "mind",
    "mental": "mind",
    "emotion": "emotional",
    "emotional": "emotional",
    "duygu": "emotional",
    "inner": "inner_world",
    "inner_world": "inner_world",
    "golge": "inner_world",
    "shadow": "inner_world",
    "direction": "life_direction",
    "life_direction": "life_direction",
    "yon": "life_direction",
    "purpose": "life_direction",
}

_SUPPORTED_SOURCE_FAMILIES = (
    "core_story_ui",
    "user_compact",
    "personality_imprint",
    "supporting_threads",
)

_CONTRAST_RE = re.compile(r"\b(ama|ancak|but)\b", flags=re.IGNORECASE)

_LAYER_CUES: dict[str, tuple[str, ...]] = {
    "recognition": (
        "kimlik",
        "benlik",
        "sen ",
        "you are",
        "dogal",
        "dogasi",
    ),
    "cause": (
        "cunku",
        "bu yuzden",
        "temel",
        "koken",
        "gecmis",
        "learned",
    ),
    "mechanism": (
        "nasil",
        "isler",
        "mekan",
        "ritim",
        "uzerinden",
        "calis",
        "process",
    ),
    "effect": (
        "gorunur",
        "insanlar",
        "hissed",
        "disari",
        "etki",
        "yansi",
        "response",
    ),
    "shadow": (
        "golge",
        "risk",
        "zorland",
        "tetik",
        "bazen",
        "kayg",
        "kopus",
    ),
    "potential": (
        "potansiyel",
        "hediye",
        "gelis",
        "guclu taraf",
        "build",
        "growth",
        "kapasite",
    ),
}

_GUIDANCE_CUES = ("oner", "dene", "practice", "try", "adim", "yap", "use this")
_QUALITY_CUES = ("confidence", "uncertainty", "quality", "kalite", "guvenilirlik", "belirsizlik")
_GUIDANCE_GROWTH_CUES = ("potansiyel", "kapasite", "growth", "gelisim", "gelistir", "gelisebilir", "buyume")
_REFERENCE_PATH_MARKERS = (
    "proof_raw",
    "chips",
    "support_keys",
    "tags",
    "drivers",
    "evidence",
    "astro_sources",
)
_PURE_REFERENCE_ASTRO_CUES = (
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "asc",
    "mc",
    "north node",
    "gunes",
    "ay",
    "merkur",
    "yukselen",
    "koc",
    "boga",
    "ikizler",
    "yengec",
    "aslan",
    "basak",
    "terazi",
    "akrep",
    "yay",
    "oglak",
    "kova",
    "balik",
    "ev",
    "square",
    "trine",
    "opposition",
    "conjunction",
    "sextile",
)
_PURE_REFERENCE_NON_MEANING_CUES = (
    "sen ",
    "you ",
    "hissed",
    "yarat",
    "ister",
    "olur",
    "olursun",
    "bazen",
    "ihtiyac",
    "goster",
    "etki",
    "kayg",
)


def build_meaning_graph_v1_1(
    *,
    core_story_ui: Mapping[str, Any] | None,
    user_compact: Mapping[str, Any] | None,
    personality_imprint: Mapping[str, Any] | None,
    supporting_threads: Sequence[Mapping[str, Any]] | None,
    locale: str = "tr",
) -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []

    _extract_core_story_ui_nodes(core_story_ui, nodes=nodes, evidence=evidence)
    _extract_user_compact_nodes(user_compact, nodes=nodes, evidence=evidence)
    _extract_personality_imprint_nodes(personality_imprint, nodes=nodes, evidence=evidence)
    _extract_supporting_thread_nodes(supporting_threads, nodes=nodes, evidence=evidence)

    mapped_families = sorted(
        {
            str(node.get("source_family") or "").strip()
            for node in nodes
            if str(node.get("source_family") or "").strip()
        }
    )
    missing_families = [family for family in _SUPPORTED_SOURCE_FAMILIES if family not in mapped_families]

    return {
        "version": "meaning_graph_v1_1",
        "canonical_intent": True,
        "nodes": nodes,
        "evidence": evidence,
        "meta": {
            "locale": str(locale or "tr"),
            "node_count": len(nodes),
            "evidence_count": len(evidence),
            "mapped_source_families": mapped_families,
            "missing_source_families": missing_families,
            "mapping_completeness": "partial",
        },
    }


def _extract_core_story_ui_nodes(
    core_story_ui: Mapping[str, Any] | None,
    *,
    nodes: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
) -> None:
    if not isinstance(core_story_ui, Mapping):
        return

    headline = _as_text(core_story_ui.get("headline"))
    summary = _as_text(core_story_ui.get("text")) or headline
    if not summary:
        return

    domain = _normalize_domain(headline)
    layers = _select_layers(summary, title=headline or "Core Story", fallback_layers=("recognition", "effect"))
    node = _make_node(
        source_family="core_story_ui",
        source_path="public.core_story_ui.text",
        title=headline or "Core Story",
        summary=summary,
        domain=domain,
        layers=layers,
        node_type=_classify_node_type(
            summary,
            source_path="public.core_story_ui.text",
            title=headline or "Core Story",
        ),
    )
    _add_text_evidence(
        node=node,
        source_family="core_story_ui",
        source_path="public.core_story_ui.text",
        snippet=summary,
        weight=0.92,
        kind="text",
        evidence=evidence,
    )

    drivers = core_story_ui.get("drivers") if isinstance(core_story_ui.get("drivers"), list) else []
    for index, raw in enumerate(drivers):
        if isinstance(raw, Mapping):
            _add_structured_evidence(
                node=node,
                source_family="core_story_ui",
                source_path=f"public.core_story_ui.drivers[{index}]",
                structured_payload=dict(raw),
                weight=0.58,
                kind="signal_driver",
                evidence=evidence,
            )
        else:
            text = _as_text(raw)
            if text:
                _add_text_evidence(
                    node=node,
                    source_family="core_story_ui",
                    source_path=f"public.core_story_ui.drivers[{index}]",
                    snippet=text,
                    weight=0.48,
                    kind="reference",
                    evidence=evidence,
                )
    nodes.append(node)


def _extract_user_compact_nodes(
    user_compact: Mapping[str, Any] | None,
    *,
    nodes: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
) -> None:
    if not isinstance(user_compact, Mapping):
        return

    domains = user_compact.get("domains") if isinstance(user_compact.get("domains"), list) else []
    for index, raw_domain in enumerate(domains):
        if not isinstance(raw_domain, Mapping):
            continue
        summary = _as_text(raw_domain.get("summary"))
        if not summary:
            continue
        domain_value = _normalize_domain(_as_text(raw_domain.get("domain")))
        title = _as_text(raw_domain.get("title")) or domain_value.title()
        source_path = f"public.user_compact.domains[{index}]"
        layers = _select_layers(summary, title=title, fallback_layers=("mechanism", "effect"))
        node = _make_node(
            source_family="user_compact",
            source_path=f"{source_path}.summary",
            title=title,
            summary=summary,
            domain=domain_value,
            layers=layers,
            node_type=_classify_node_type(summary, source_path=f"{source_path}.summary", title=title),
        )
        _add_text_evidence(
            node=node,
            source_family="user_compact",
            source_path=f"{source_path}.summary",
            snippet=summary,
            weight=0.86,
            kind="text",
            evidence=evidence,
        )
        highlights = raw_domain.get("highlights") if isinstance(raw_domain.get("highlights"), list) else []
        for hi, highlight in enumerate(highlights):
            if isinstance(highlight, Mapping):
                text = _as_text(highlight.get("text")) or _as_text(highlight.get("summary"))
                if text:
                    _add_text_evidence(
                        node=node,
                        source_family="user_compact",
                        source_path=f"{source_path}.highlights[{hi}]",
                        snippet=text,
                        weight=0.44,
                        kind="text",
                        evidence=evidence,
                    )
            else:
                text = _as_text(highlight)
                if text:
                    _add_text_evidence(
                        node=node,
                        source_family="user_compact",
                        source_path=f"{source_path}.highlights[{hi}]",
                        snippet=text,
                        weight=0.4,
                        kind="signal",
                        evidence=evidence,
                    )
        nodes.append(node)

    micro_insights = user_compact.get("micro_insights") if isinstance(user_compact.get("micro_insights"), list) else []
    for index, raw_micro in enumerate(micro_insights):
        if not isinstance(raw_micro, Mapping):
            continue
        text = _as_text(raw_micro.get("text"))
        if not text:
            continue
        domain_value = _normalize_domain(_as_text(raw_micro.get("domain")))
        source_path = f"public.user_compact.micro_insights[{index}]"
        layers = _select_layers(text, fallback_layers=("effect", "recognition"))
        node = _make_node(
            source_family="user_compact",
            source_path=f"{source_path}.text",
            title="Micro Insight",
            summary=text,
            domain=domain_value,
            layers=layers,
            node_type=_classify_node_type(text, source_path=f"{source_path}.text", title="Micro Insight"),
        )
        _add_text_evidence(
            node=node,
            source_family="user_compact",
            source_path=f"{source_path}.text",
            snippet=text,
            weight=0.78,
            kind="text",
            evidence=evidence,
        )
        raw_evidence = raw_micro.get("evidence") if isinstance(raw_micro.get("evidence"), list) else []
        for ei, evd in enumerate(raw_evidence):
            if isinstance(evd, Mapping):
                _add_structured_evidence(
                    node=node,
                    source_family="user_compact",
                    source_path=f"{source_path}.evidence[{ei}]",
                    structured_payload=dict(evd),
                    weight=0.5,
                    kind="signal_driver",
                    evidence=evidence,
                )
        nodes.append(node)


def _extract_personality_imprint_nodes(
    personality_imprint: Mapping[str, Any] | None,
    *,
    nodes: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
) -> None:
    if not isinstance(personality_imprint, Mapping):
        return

    groups = (
        ("entries", personality_imprint.get("entries")),
        ("support_entries", personality_imprint.get("support_entries")),
        ("extra_entries", personality_imprint.get("extra_entries")),
    )
    for group_name, entries in groups:
        if not isinstance(entries, list):
            continue
        for index, raw_entry in enumerate(entries):
            if not isinstance(raw_entry, Mapping):
                continue

            label = _as_text(raw_entry.get("label_tr")) or _as_text(raw_entry.get("key")) or "Imprint"
            domain_value = _normalize_domain(
                " ".join(
                    [
                        label,
                        _as_text(raw_entry.get("kind")),
                        _as_text(raw_entry.get("aura")),
                        _as_text(raw_entry.get("trait")),
                    ]
                )
            )
            base_path = f"public.personality_imprint.{group_name}[{index}]"

            _append_personality_node(
                nodes=nodes,
                evidence=evidence,
                source_path=f"{base_path}.trait",
                source_family="personality_imprint",
                domain_value=domain_value,
                label=label,
                text=_as_text(raw_entry.get("trait")) or _as_text(raw_entry.get("aura")),
                fallback_layers=("effect", "recognition"),
                raw_entry=raw_entry,
            )
            _append_personality_node(
                nodes=nodes,
                evidence=evidence,
                source_path=f"{base_path}.shadow",
                source_family="personality_imprint",
                domain_value=domain_value,
                label=f"{label} Shadow",
                text=_as_text(raw_entry.get("shadow")),
                fallback_layers=("shadow", "effect"),
                raw_entry=raw_entry,
            )
            _append_personality_node(
                nodes=nodes,
                evidence=evidence,
                source_path=f"{base_path}.gift",
                source_family="personality_imprint",
                domain_value=domain_value,
                label=f"{label} Potential",
                text=_as_text(raw_entry.get("gift")),
                fallback_layers=("potential", "effect"),
                raw_entry=raw_entry,
            )


def _append_personality_node(
    *,
    nodes: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
    source_path: str,
    source_family: str,
    domain_value: str,
    label: str,
    text: str,
    fallback_layers: Sequence[str],
    raw_entry: Mapping[str, Any],
) -> None:
    if not text:
        return
    node = _make_node(
        source_family=source_family,
        source_path=source_path,
        title=label,
        summary=text,
        domain=domain_value,
        layers=_select_layers(text, title=label, fallback_layers=fallback_layers),
        node_type=_classify_node_type(text, source_path=source_path, title=label),
    )
    _add_text_evidence(
        node=node,
        source_family=source_family,
        source_path=source_path,
        snippet=text,
        weight=0.74,
        kind="text",
        evidence=evidence,
    )

    tags = [str(tag).strip() for tag in (raw_entry.get("tags") or []) if str(tag).strip()]
    support_keys = [str(key).strip() for key in (raw_entry.get("support_keys") or []) if str(key).strip()]
    drive = _as_text(raw_entry.get("drive"))
    background_hint = _as_text(raw_entry.get("background_hint"))

    if tags:
        _add_structured_evidence(
            node=node,
            source_family=source_family,
            source_path=f"{source_path}.tags",
            structured_payload={"tags": tags},
            weight=0.32,
            kind="reference",
            evidence=evidence,
        )
    if support_keys:
        _add_structured_evidence(
            node=node,
            source_family=source_family,
            source_path=f"{source_path}.support_keys",
            structured_payload={"support_keys": support_keys},
            weight=0.35,
            kind="reference",
            evidence=evidence,
        )
    if drive:
        _add_text_evidence(
            node=node,
            source_family=source_family,
            source_path=f"{source_path}.drive",
            snippet=drive,
            weight=0.42,
            kind="signal",
            evidence=evidence,
        )
    if background_hint:
        _add_text_evidence(
            node=node,
            source_family=source_family,
            source_path=f"{source_path}.background_hint",
            snippet=background_hint,
            weight=0.46,
            kind="reference",
            evidence=evidence,
        )
    nodes.append(node)


def _extract_supporting_thread_nodes(
    supporting_threads: Sequence[Mapping[str, Any]] | None,
    *,
    nodes: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
) -> None:
    if not isinstance(supporting_threads, Sequence):
        return
    for index, raw_thread in enumerate(supporting_threads):
        if not isinstance(raw_thread, Mapping):
            continue
        summary = (
            _as_text(raw_thread.get("paragraph"))
            or _as_text(raw_thread.get("body"))
            or _as_text(raw_thread.get("one_liner"))
        )
        if not summary:
            continue
        title = _as_text(raw_thread.get("title")) or _as_text(raw_thread.get("id")) or "Thread"
        source_path = f"public.supporting_threads[{index}]"
        domain_value = _normalize_domain(f"{title} {summary}")
        layers = _select_layers(summary, title=title, fallback_layers=("cause", "mechanism"))
        node = _make_node(
            source_family="supporting_threads",
            source_path=f"{source_path}.paragraph",
            title=title,
            summary=summary,
            domain=domain_value,
            layers=layers,
            node_type=_classify_node_type(summary, source_path=f"{source_path}.paragraph", title=title),
        )
        _add_text_evidence(
            node=node,
            source_family="supporting_threads",
            source_path=f"{source_path}.paragraph",
            snippet=summary,
            weight=0.79,
            kind="text",
            evidence=evidence,
        )
        proof_raw = _as_text(raw_thread.get("proof_raw"))
        if proof_raw:
            _add_structured_evidence(
                node=node,
                source_family="supporting_threads",
                source_path=f"{source_path}.proof_raw",
                structured_payload={"proof_raw": proof_raw},
                weight=0.57,
                kind="reference",
                evidence=evidence,
            )
        chips = raw_thread.get("chips") if isinstance(raw_thread.get("chips"), list) else []
        chips_clean = [str(chip).strip() for chip in chips if str(chip).strip()]
        if chips_clean:
            _add_structured_evidence(
                node=node,
                source_family="supporting_threads",
                source_path=f"{source_path}.chips",
                structured_payload={"chips": chips_clean},
                weight=0.5,
                kind="signal",
                evidence=evidence,
            )
        nodes.append(node)


def _infer_layers_from_text(text: str, *, title: str = "") -> dict[str, float]:
    lowered = _normalize_text(text)
    if not lowered:
        return {}
    scores = {layer: 0.0 for layer in LAYER_TAXONOMY}
    for layer, cues in _LAYER_CUES.items():
        for cue in cues:
            if cue in lowered:
                scores[layer] += 1.0

    if _CONTRAST_RE.search(lowered):
        scores["shadow"] += 0.8
        scores["effect"] += 0.5
        scores["mechanism"] += 0.4
    if ";" in text or len(_split_sentences(text)) >= 2:
        scores["mechanism"] += 0.25
        scores["effect"] += 0.25
    normalized_title = _normalize_text(title)
    if "shadow" in normalized_title:
        scores["shadow"] += 2.4
    if "potential" in normalized_title:
        scores["potential"] += 2.4
    return {layer: value for layer, value in scores.items() if value > 0}


def _select_layers(text: str, *, title: str = "", fallback_layers: Sequence[str]) -> List[Dict[str, Any]]:
    inferred = _infer_layers_from_text(text, title=title)
    if not inferred:
        inferred = {layer: max(0.1, 1.0 - i * 0.1) for i, layer in enumerate(fallback_layers)}

    contrast = _CONTRAST_RE.search(_normalize_text(text)) is not None
    ranked = sorted(inferred.items(), key=lambda item: item[1], reverse=True)
    sentence_count = len(_split_sentences(text))
    atomic = sentence_count <= 1 and len(_normalize_text(text).split()) <= 12

    if contrast:
        selected = _pick_contrast_pair(ranked)
    elif atomic:
        selected = ranked[:1]
    else:
        selected = ranked[:2]
        if len(ranked) >= 3 and ranked[2][1] >= max(1.8, ranked[1][1] * 0.85):
            selected = ranked[:3]

    return _normalize_layers(selected)


def _pick_contrast_pair(ranked: list[tuple[str, float]]) -> list[tuple[str, float]]:
    score_map = {layer: score for layer, score in ranked}
    effect_shadow = score_map.get("effect", 0.0) + score_map.get("shadow", 0.0)
    mechanism_effect = score_map.get("mechanism", 0.0) + score_map.get("effect", 0.0)

    if effect_shadow >= mechanism_effect and score_map.get("shadow", 0.0) > 0:
        return [("effect", score_map.get("effect", 0.1)), ("shadow", score_map.get("shadow", 0.1))]
    if mechanism_effect > 0:
        return [("mechanism", score_map.get("mechanism", 0.1)), ("effect", score_map.get("effect", 0.1))]
    return ranked[:2] if len(ranked) >= 2 else ranked[:1]


def _normalize_layers(selected: Sequence[tuple[str, float]]) -> List[Dict[str, Any]]:
    unique: List[tuple[str, float]] = []
    seen: set[str] = set()
    for layer, score in selected:
        if layer not in LAYER_TAXONOMY or layer in seen:
            continue
        seen.add(layer)
        unique.append((layer, max(0.01, float(score))))
    if not unique:
        unique = [("recognition", 1.0)]
    unique = unique[:3]

    total = sum(score for _, score in unique)
    normalized = []
    running = 0.0
    for index, (layer, score) in enumerate(unique):
        if index < len(unique) - 1:
            weight = round(score / total, 3)
            running += weight
        else:
            weight = round(max(0.0, 1.0 - running), 3)
        normalized.append({"layer": layer, "weight": weight})
    normalized.sort(key=lambda item: float(item.get("weight") or 0.0), reverse=True)
    return normalized


def _classify_node_type(text: str, *, source_path: str, title: str = "") -> str:
    lowered = _normalize_text(text)
    sentence_count = len(_split_sentences(text))
    token_count = len(lowered.split())

    if _is_non_meaning_reference(text, source_path=source_path):
        return "reference"
    if any(cue in lowered for cue in _QUALITY_CUES):
        return "quality"
    if _looks_like_guidance(lowered, title=title):
        return "guidance"
    if sentence_count >= 2 or _CONTRAST_RE.search(lowered) or token_count >= 13:
        return "narrative"
    return "signal"


def _is_non_meaning_reference(text: str, *, source_path: str) -> bool:
    normalized_path = _normalize_text(source_path)
    if any(marker in normalized_path for marker in _REFERENCE_PATH_MARKERS):
        return True

    lowered = _normalize_text(text)
    token_count = len(lowered.split())
    if not lowered or token_count > 10:
        return False

    astro_hits = sum(1 for cue in _PURE_REFERENCE_ASTRO_CUES if cue in lowered)
    has_separator = any(sep in text for sep in ("·", "|", "/", "→", ":"))
    has_meaning_cue = any(cue in lowered for cue in _PURE_REFERENCE_NON_MEANING_CUES)
    return astro_hits >= 2 and has_separator and not has_meaning_cue


def _looks_like_guidance(lowered_text: str, *, title: str) -> bool:
    title_norm = _normalize_text(title)
    return any(cue in lowered_text for cue in _GUIDANCE_CUES) or any(
        cue in lowered_text or cue in title_norm for cue in _GUIDANCE_GROWTH_CUES
    )


def _make_node(
    *,
    source_family: str,
    source_path: str,
    title: str,
    summary: str,
    domain: str,
    layers: List[Dict[str, Any]],
    node_type: str,
) -> Dict[str, Any]:
    normalized_type = node_type if node_type in NODE_TYPE_ENUM else "signal"
    primary_layer = (
        str(max(layers, key=lambda item: float(item.get("weight") or 0.0)).get("layer") or "recognition")
        if layers
        else "recognition"
    )
    dedupe_fingerprint = _dedupe_fingerprint(summary, domain, layers)
    node_id = _stable_id(
        "mgv11_node",
        source_family,
        normalized_type,
        domain,
        title,
        summary,
        dedupe_fingerprint,
    )
    short_text = _short_text(summary)
    return {
        "node_id": node_id,
        "node_type": normalized_type,
        "title": title,
        "summary": summary,
        "layers": layers,
        "primary_layer": primary_layer,
        "domain": domain,
        "source_family": source_family,
        "source_path": source_path,
        "evidence_ids": [],
        "projection_hints": {
            "surfaces": _infer_surfaces(normalized_type, layers),
            "priority": _projection_priority(normalized_type, layers),
            "short_text": short_text if short_text != summary else None,
        },
        "temporal_scope": None,
        "dedupe_fingerprint": dedupe_fingerprint,
    }


def _projection_priority(node_type: str, layers: Sequence[Mapping[str, Any]]) -> float:
    if not layers:
        return 0.5
    top_weight = max(float(item.get("weight") or 0.0) for item in layers)
    type_boost = {
        "narrative": 0.2,
        "signal": 0.1,
        "guidance": 0.18,
        "quality": 0.08,
        "reference": 0.05,
    }.get(node_type, 0.0)
    return round(min(1.0, max(0.05, top_weight + type_boost)), 3)


def _infer_surfaces(node_type: str, layers: Sequence[Mapping[str, Any]]) -> list[str]:
    layer_set = {str(item.get("layer") or "") for item in layers}
    surfaces: list[str] = []
    if "effect" in layer_set or node_type == "signal":
        surfaces.append("home")
    if "recognition" in layer_set or "mechanism" in layer_set:
        surfaces.append("profile_top")
    if "shadow" in layer_set or "cause" in layer_set or node_type == "narrative":
        surfaces.append("profile_deep")
    if node_type in {"guidance", "reference"}:
        surfaces.append("explainability")
    if not surfaces:
        surfaces = ["profile_deep"]
    ordered: list[str] = []
    for surface in surfaces:
        if surface not in ordered:
            ordered.append(surface)
    return ordered[:4]


def _add_text_evidence(
    *,
    node: Dict[str, Any],
    source_family: str,
    source_path: str,
    snippet: str,
    weight: float,
    kind: str,
    evidence: List[Dict[str, Any]],
) -> None:
    text = _as_text(snippet)
    if not text:
        return
    evidence_id = _stable_id("mgv11_evd", node["node_id"], source_family, source_path, kind, text)
    node.setdefault("evidence_ids", []).append(evidence_id)
    evidence.append(
        {
            "evidence_id": evidence_id,
            "node_id": node["node_id"],
            "kind": kind,
            "source_family": source_family,
            "source_path": source_path,
            "weight": round(max(0.0, min(1.0, float(weight))), 3),
            "text_payload": text,
            "structured_payload": None,
        }
    )


def _add_structured_evidence(
    *,
    node: Dict[str, Any],
    source_family: str,
    source_path: str,
    structured_payload: Mapping[str, Any],
    weight: float,
    kind: str,
    evidence: List[Dict[str, Any]],
) -> None:
    payload = dict(structured_payload)
    if not payload:
        return
    normalized_payload = _normalize_text(str(payload))
    evidence_id = _stable_id("mgv11_evd", node["node_id"], source_family, source_path, kind, normalized_payload)
    node.setdefault("evidence_ids", []).append(evidence_id)
    evidence.append(
        {
            "evidence_id": evidence_id,
            "node_id": node["node_id"],
            "kind": kind,
            "source_family": source_family,
            "source_path": source_path,
            "weight": round(max(0.0, min(1.0, float(weight))), 3),
            "text_payload": None,
            "structured_payload": payload,
        }
    )


def _dedupe_fingerprint(summary: str, domain: str, layers: Sequence[Mapping[str, Any]]) -> str:
    normalized_text = _normalize_text(summary)
    normalized_domain = _normalize_domain(domain)
    layer_vector = sorted(
        (
            f"{str(item.get('layer') or '').strip()}:{round(float(item.get('weight') or 0.0), 3):.3f}"
            for item in layers
            if str(item.get("layer") or "").strip()
        )
    )
    payload = "|".join([normalized_text, normalized_domain, ",".join(layer_vector)])
    return _stable_id("mgv11_dfp", payload)


def _split_sentences(text: str) -> list[str]:
    raw = [part.strip() for part in re.split(r"[.!?;]+", str(text or "")) if part.strip()]
    return raw


def _short_text(text: str, limit: int = 120) -> str:
    source = _as_text(text)
    if len(source) <= limit:
        return source
    clipped = source[:limit].rsplit(" ", 1)[0].strip()
    return f"{clipped}..." if clipped else source[:limit].strip()


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_domain(value: str) -> str:
    raw = _normalize_text(value).replace("-", " ").replace("/", " ")
    tokens = [token for token in raw.split() if token]
    for token in tokens:
        if token in _DOMAIN_ALIASES:
            return _DOMAIN_ALIASES[token]
    if raw in _DOMAIN_ALIASES:
        return _DOMAIN_ALIASES[raw]
    return "general"


def _normalize_text(value: str) -> str:
    lowered = str(value or "").lower().strip()
    lowered = lowered.replace("ı", "i").replace("İ", "i")
    lowered = lowered.replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def _stable_id(prefix: str, *parts: str) -> str:
    payload = "|".join(str(part or "").strip() for part in parts)
    digest = sha1(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"
