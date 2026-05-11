from __future__ import annotations

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


def build_meaning_graph_v1(
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

    ranked_nodes = []
    for index, node in enumerate(nodes, start=1):
        ranked_nodes.append({**node, "rank": index})

    mapped_families = sorted(
        {
            str(node.get("source_family") or "").strip()
            for node in ranked_nodes
            if str(node.get("source_family") or "").strip()
        }
    )
    missing_families = [family for family in _SUPPORTED_SOURCE_FAMILIES if family not in mapped_families]

    return {
        "version": "meaning_graph_v1",
        "canonical": True,
        "locale": str(locale or "tr"),
        "taxonomy": {
            "layers": list(LAYER_TAXONOMY),
            "domains": list(DOMAIN_TAXONOMY),
        },
        "nodes": ranked_nodes,
        "evidence": evidence,
        "meta": {
            "node_count": len(ranked_nodes),
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

    domain = _normalize_domain(_as_text(headline))
    node_id = _stable_id("mgv1_node", "core_story_ui", "recognition", domain, headline, summary)
    source_path = "public.core_story_ui"
    evidence_ids: List[str] = []
    _add_text_evidence(
        node_id=node_id,
        source_family="core_story_ui",
        source_path="public.core_story_ui.text",
        snippet=summary,
        weight=0.9,
        evidence=evidence,
        evidence_ids=evidence_ids,
    )
    drivers = core_story_ui.get("drivers") if isinstance(core_story_ui.get("drivers"), list) else []
    for index, item in enumerate(drivers):
        text = _as_text(item)
        if not text:
            continue
        _add_text_evidence(
            node_id=node_id,
            source_family="core_story_ui",
            source_path=f"public.core_story_ui.drivers[{index}]",
            snippet=text,
            weight=0.5,
            evidence=evidence,
            evidence_ids=evidence_ids,
        )

    nodes.append(
        {
            "node_id": node_id,
            "layer": "recognition",
            "domain": domain,
            "source_family": "core_story_ui",
            "source_path": source_path,
            "title": headline or "Core Story",
            "summary": summary,
            "confidence": 0.8,
            "tags": [text for text in (_as_text(item) for item in drivers) if text][:5],
            "evidence_ids": evidence_ids,
            "mapping_status": "mapped",
        }
    )


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
        domain_value = _normalize_domain(_as_text(raw_domain.get("domain")))
        title = _as_text(raw_domain.get("title")) or domain_value.title()
        summary = _as_text(raw_domain.get("summary"))
        if not summary:
            continue
        node_id = _stable_id(
            "mgv1_node",
            "user_compact",
            "mechanism",
            domain_value,
            title,
            summary,
            str(index),
        )
        source_path = f"public.user_compact.domains[{index}]"
        evidence_ids: List[str] = []
        _add_text_evidence(
            node_id=node_id,
            source_family="user_compact",
            source_path=f"{source_path}.summary",
            snippet=summary,
            weight=0.85,
            evidence=evidence,
            evidence_ids=evidence_ids,
        )
        highlights = raw_domain.get("highlights") if isinstance(raw_domain.get("highlights"), list) else []
        for hi, highlight in enumerate(highlights):
            if isinstance(highlight, Mapping):
                text = _as_text(highlight.get("text")) or _as_text(highlight.get("summary"))
            else:
                text = _as_text(highlight)
            if not text:
                continue
            _add_text_evidence(
                node_id=node_id,
                source_family="user_compact",
                source_path=f"{source_path}.highlights[{hi}]",
                snippet=text,
                weight=0.45,
                evidence=evidence,
                evidence_ids=evidence_ids,
            )
        nodes.append(
            {
                "node_id": node_id,
                "layer": "mechanism",
                "domain": domain_value,
                "source_family": "user_compact",
                "source_path": source_path,
                "title": title,
                "summary": summary,
                "confidence": 0.7,
                "tags": [],
                "evidence_ids": evidence_ids,
                "mapping_status": "mapped",
            }
        )

    micro_insights = (
        user_compact.get("micro_insights") if isinstance(user_compact.get("micro_insights"), list) else []
    )
    for index, raw_micro in enumerate(micro_insights):
        if not isinstance(raw_micro, Mapping):
            continue
        text = _as_text(raw_micro.get("text"))
        if not text:
            continue
        domain_value = _normalize_domain(_as_text(raw_micro.get("domain")))
        node_id = _stable_id(
            "mgv1_node",
            "user_compact",
            "effect",
            domain_value,
            text,
            str(index),
        )
        source_path = f"public.user_compact.micro_insights[{index}]"
        evidence_ids: List[str] = []
        _add_text_evidence(
            node_id=node_id,
            source_family="user_compact",
            source_path=f"{source_path}.text",
            snippet=text,
            weight=0.75,
            evidence=evidence,
            evidence_ids=evidence_ids,
        )
        nodes.append(
            {
                "node_id": node_id,
                "layer": "effect",
                "domain": domain_value,
                "source_family": "user_compact",
                "source_path": source_path,
                "title": "Micro Insight",
                "summary": text,
                "confidence": 0.64,
                "tags": [],
                "evidence_ids": evidence_ids,
                "mapping_status": "mapped",
            }
        )


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
            domain_value = _normalize_domain(" ".join([label, _as_text(raw_entry.get("kind")), _as_text(raw_entry.get("aura"))]))
            source_path = f"public.personality_imprint.{group_name}[{index}]"
            tags = [str(tag).strip() for tag in (raw_entry.get("tags") or []) if str(tag).strip()]
            _append_personality_node(
                nodes=nodes,
                evidence=evidence,
                source_path=source_path,
                domain_value=domain_value,
                label=label,
                layer="effect",
                text=_as_text(raw_entry.get("trait")) or _as_text(raw_entry.get("aura")),
                key_suffix="effect",
                tags=tags,
            )
            _append_personality_node(
                nodes=nodes,
                evidence=evidence,
                source_path=source_path,
                domain_value=domain_value,
                label=label,
                layer="shadow",
                text=_as_text(raw_entry.get("shadow")),
                key_suffix="shadow",
                tags=tags,
            )
            _append_personality_node(
                nodes=nodes,
                evidence=evidence,
                source_path=source_path,
                domain_value=domain_value,
                label=label,
                layer="potential",
                text=_as_text(raw_entry.get("gift")),
                key_suffix="potential",
                tags=tags,
            )


def _append_personality_node(
    *,
    nodes: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
    source_path: str,
    domain_value: str,
    label: str,
    layer: str,
    text: str,
    key_suffix: str,
    tags: List[str],
) -> None:
    if not text:
        return
    node_id = _stable_id(
        "mgv1_node",
        "personality_imprint",
        layer,
        domain_value,
        label,
        text,
        key_suffix,
    )
    evidence_ids: List[str] = []
    _add_text_evidence(
        node_id=node_id,
        source_family="personality_imprint",
        source_path=source_path,
        snippet=text,
        weight=0.7,
        evidence=evidence,
        evidence_ids=evidence_ids,
    )
    nodes.append(
        {
            "node_id": node_id,
            "layer": layer,
            "domain": domain_value,
            "source_family": "personality_imprint",
            "source_path": source_path,
            "title": label,
            "summary": text,
            "confidence": 0.72,
            "tags": tags[:6],
            "evidence_ids": evidence_ids,
            "mapping_status": "mapped",
        }
    )


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
        title = _as_text(raw_thread.get("title")) or _as_text(raw_thread.get("id")) or "Thread"
        summary = (
            _as_text(raw_thread.get("paragraph"))
            or _as_text(raw_thread.get("body"))
            or _as_text(raw_thread.get("one_liner"))
        )
        if not summary:
            continue
        domain = _normalize_domain(" ".join([title, summary]))
        source_path = f"public.supporting_threads[{index}]"
        node_id = _stable_id(
            "mgv1_node",
            "supporting_threads",
            "cause",
            domain,
            title,
            summary,
            str(index),
        )
        evidence_ids: List[str] = []
        _add_text_evidence(
            node_id=node_id,
            source_family="supporting_threads",
            source_path=source_path,
            snippet=summary,
            weight=0.72,
            evidence=evidence,
            evidence_ids=evidence_ids,
        )
        nodes.append(
            {
                "node_id": node_id,
                "layer": "cause",
                "domain": domain,
                "source_family": "supporting_threads",
                "source_path": source_path,
                "title": title,
                "summary": summary,
                "confidence": 0.66,
                "tags": [],
                "evidence_ids": evidence_ids,
                "mapping_status": "mapped",
            }
        )


def _add_text_evidence(
    *,
    node_id: str,
    source_family: str,
    source_path: str,
    snippet: str,
    weight: float,
    evidence: List[Dict[str, Any]],
    evidence_ids: List[str],
) -> None:
    text = _as_text(snippet)
    if not text:
        return
    evidence_id = _stable_id("mgv1_evd", node_id, source_family, source_path, text)
    evidence_ids.append(evidence_id)
    evidence.append(
        {
            "evidence_id": evidence_id,
            "node_id": node_id,
            "source_family": source_family,
            "source_path": source_path,
            "kind": "text",
            "snippet": text,
            "weight": round(max(0.0, min(1.0, float(weight))), 3),
            "mapping_status": "mapped",
        }
    )


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_domain(value: str) -> str:
    tokens = [token.lower() for token in value.replace("-", " ").replace("/", " ").split() if token.strip()]
    for token in tokens:
        if token in _DOMAIN_ALIASES:
            return _DOMAIN_ALIASES[token]
    lowered = value.lower().strip()
    if lowered in _DOMAIN_ALIASES:
        return _DOMAIN_ALIASES[lowered]
    return "general"


def _stable_id(prefix: str, *parts: str) -> str:
    payload = "|".join(str(part or "").strip() for part in parts)
    digest = sha1(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"

