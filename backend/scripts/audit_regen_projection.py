"""Regression-check helper for the Adana / Istanbul P0 audits.

Reads an existing user-compact debug artifact and rebuilds the
``profile_narrative_projection_v1`` + ``profile_v8_projection_v1`` payloads
from the cluster plan + packet payloads embedded in the artifact, then
prints a short JSON-shaped summary that the audit doc consumes.

Usage:
    PYTHONPATH=backend backend/venv/bin/python \
        backend/scripts/audit_regen_projection.py \
        backend/tests/_artifacts/natal_interpret_full_1998-09-12_07-30_adana_user_compact_debug.json

Notes:
- This script is deliberately read-only and standalone. It does NOT need
  network or Swiss Ephemeris access — the artifact already carries every
  intermediate payload required by the projection builder.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def _read_artifact(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _walk(payload, *, key: str):
    """Yield every value under ``key`` anywhere in the artifact tree."""
    if isinstance(payload, dict):
        if key in payload:
            yield payload[key]
        for value in payload.values():
            yield from _walk(value, key=key)
    elif isinstance(payload, list):
        for item in payload:
            yield from _walk(item, key=key)


def _find_first(payload, predicate):
    if isinstance(payload, dict):
        if predicate(payload):
            return payload
        for value in payload.values():
            found = _find_first(value, predicate)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for item in payload:
            found = _find_first(item, predicate)
            if found is not None:
                return found
    return None


def _summarise_projection(projection: dict) -> dict:
    public = projection.get("profile_public") or {}
    core_blocks = list(public.get("core_blocks") or [])
    extra_blocks = list(public.get("extra_blocks") or [])
    headlines_core = [str(b.get("headline") or "") for b in core_blocks]
    headlines_extra = [str(b.get("headline") or "") for b in extra_blocks]
    mid_word_pattern = re.compile(r"[a-zçğıöşüâîû]…(?:\s|$)", flags=re.IGNORECASE)
    midword_hits = []
    for block in [*core_blocks, *extra_blocks]:
        for field in ("teaser", "body"):
            value = str(block.get(field) or "")
            if mid_word_pattern.search(value):
                midword_hits.append({
                    "block_id": block.get("id"),
                    "node_id": block.get("node_id"),
                    "field": field,
                    "tail": value[-60:],
                })
    long_headlines = []
    for block in [*core_blocks, *extra_blocks]:
        headline = str(block.get("headline") or "")
        if len(headline) > 200:
            long_headlines.append({
                "block_id": block.get("id"),
                "node_id": block.get("node_id"),
                "length": len(headline),
                "head": headline[:80],
            })
    decomposed_hits = []
    for block in [*core_blocks, *extra_blocks]:
        for field in ("headline", "teaser", "body", "micro"):
            value = str(block.get(field) or "")
            if re.search(r"[.!?:;]\s+i̇", value):
                decomposed_hits.append({
                    "block_id": block.get("id"),
                    "field": field,
                    "fragment": value[
                        max(0, value.find("i̇") - 20) : value.find("i̇") + 20
                    ],
                })
    duplicate_headlines = sorted(
        h for h in set(headlines_core + headlines_extra)
        if (headlines_core + headlines_extra).count(h) > 1
    )
    aux_duplicates = []
    core_packet_ids = {
        str(b.get("node_id") or "").replace("promise::", "") for b in core_blocks
    }
    for block in extra_blocks:
        pid = str(block.get("node_id") or "").replace("promise::", "")
        if pid.endswith("_aux") and pid[: -len("_aux")] in core_packet_ids:
            aux_duplicates.append(pid)
    return {
        "core_count": len(core_blocks),
        "extra_count": len(extra_blocks),
        "headlines_core": headlines_core,
        "headlines_extra": headlines_extra,
        "duplicate_headlines": duplicate_headlines,
        "long_headlines": long_headlines,
        "midword_hits": midword_hits,
        "post_colon_decomposed_hits": decomposed_hits,
        "aux_duplicates_in_extra": aux_duplicates,
    }


def _summarise_v8(v8: dict) -> dict:
    hero = v8.get("hero") or {}
    identity_axis = v8.get("identity_axis") or {}
    insight_strip = list(v8.get("insight_strip") or [])
    differentiators = list(v8.get("differentiators") or [])
    return {
        "hero_headline_length": len(str(hero.get("headline") or "")),
        "identity_axis_headline_length": len(str(identity_axis.get("headline") or "")),
        "insight_strip_titles": [str(item.get("title") or "") for item in insight_strip],
        "differentiator_headlines": [
            {"length": len(str(item.get("headline") or "")), "head": str(item.get("headline") or "")[:80]}
            for item in differentiators
        ],
    }


def regen_for_artifact(artifact_path: Path) -> dict:
    from app.meaning.projection_shadow_v1_builder import (
        build_profile_narrative_projection_v1,
        build_profile_v8_projection_v1,
    )
    from app.natal.natal_promise_packets import build_natal_promise_packets_v1
    from app.natal.natal_promise_cluster_plan import build_natal_promise_cluster_plan_v1

    artifact = _read_artifact(artifact_path)

    sections = list(_walk(artifact, key="sections_v2"))
    threads = list(_walk(artifact, key="supporting_threads"))
    planets = artifact.get("planets") or list(_walk(artifact, key="planets"))[0]
    aspects = artifact.get("aspects") or list(_walk(artifact, key="aspects"))[0]
    metadata = artifact.get("metadata") or {}
    natal_graph_compact = (
        artifact.get("natal_graph_compact")
        or next(iter(_walk(artifact, key="natal_graph_compact")), {})
    )
    meta_info = artifact.get("meta_info") or {}

    sections_payload = sections[0] if sections else []
    threads_payload = threads[0] if threads else []

    # Build with debug=candidate_inventory to mirror the audit-time flag set.
    packets_inventory = build_natal_promise_packets_v1(
        sections_v2=sections_payload,
        supporting_threads=threads_payload,
        planets=planets,
        aspects=aspects,
        natal_graph_compact=natal_graph_compact,
        metadata=metadata,
        meta_info=meta_info,
        locale="tr",
        mode="candidate_inventory",
    )
    packets_selected = build_natal_promise_packets_v1(
        sections_v2=sections_payload,
        supporting_threads=threads_payload,
        planets=planets,
        aspects=aspects,
        natal_graph_compact=natal_graph_compact,
        metadata=metadata,
        meta_info=meta_info,
        locale="tr",
        mode="selected",
    )
    cluster_plan = build_natal_promise_cluster_plan_v1(packets_inventory.get("packets") or [])

    # The projection consumer wants the "selected" packet payload alongside
    # the cluster plan; that mirrors what the public builder does.
    narrative = build_profile_narrative_projection_v1(
        meaning_graph_v1_1={
            "version": "meaning_graph_v1_1",
            "nodes": [],
            "evidence": [],
        },
        natal_promise_packets_v1=packets_selected,
        natal_promise_cluster_plan_v1=cluster_plan,
        include_packet_debug=True,
    )
    v8 = build_profile_v8_projection_v1(
        meaning_graph_v1_1={
            "version": "meaning_graph_v1_1",
            "nodes": [],
            "evidence": [],
        },
        natal_promise_packets_v1=packets_selected,
        natal_promise_cluster_plan_v1=cluster_plan,
        include_packet_debug=True,
    )

    # Chart-fact match flags on selected packets (Bug 5).
    chart_facts_flags = []
    for packet in packets_selected.get("packets") or []:
        if "chart_facts_match" in packet:
            chart_facts_flags.append(
                {
                    "packet_id": packet.get("id"),
                    "chart_facts_match": packet["chart_facts_match"],
                }
            )

    return {
        "artifact": str(artifact_path.name),
        "narrative": _summarise_projection(narrative),
        "v8": _summarise_v8(v8),
        "chart_facts_flags": chart_facts_flags,
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: audit_regen_projection.py <artifact.json> [more.json ...]", file=sys.stderr)
        return 2
    out = []
    for path_str in argv[1:]:
        out.append(regen_for_artifact(Path(path_str)))
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
