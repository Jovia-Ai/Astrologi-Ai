from __future__ import annotations

import copy
import hashlib
import os
import re
from typing import Any, Dict, List, Mapping, MutableMapping, Sequence

from app.narrative.editorial_render_policy import (
    editorialize_micro,
    editorialize_teaser,
    opening_key,
    quality_issues,
)
from app.natal.profile_detail_editorial import (
    build_editorial_detail_blocks_for_profile_block,
)

_PROJECTION_SOURCE = "meaning_graph_v1_1"
_BODY_MAX_SENTENCES = 4
_BODY_MIN_SENTENCES = 3
_NARRATIVE_PATTERNS: tuple[str, ...] = (
    "contrast",
    "tension",
    "inner_state",
    "relational",
    "growth",
)

_DOMAIN_LABELS: dict[str, str] = {
    "identity": "kimlik",
    "mind": "zihin",
    "relationships": "ilişkiler",
    "relationship": "ilişkiler",
    "life_direction": "yaşam yönü",
    "emotional": "duygusal alan",
    "general": "genel yaşam",
    "career": "kariyer",
}

_DOMAIN_LOCATIVE_LABELS: dict[str, str] = {
    "identity": "kimlikte",
    "mind": "zihinde",
    "relationships": "ilişkilerde",
    "relationship": "ilişkilerde",
    "life_direction": "yaşam yönünde",
    "emotional": "duygusal alanda",
    "general": "genel yaşamda",
    "career": "kariyerde",
}

_LAYER_LABELS: dict[str, str] = {
    "recognition": "tanınma",
    "cause": "kök neden",
    "mechanism": "işleyiş",
    "effect": "etki",
    "shadow": "gölge",
    "potential": "potansiyel",
}

_POLICY_SOFT_DUPLICATE_THRESHOLD = 0.72
_POLICY_MAX_SOFT_DUPLICATES = 1
_POLICY_SIMILARITY_PENALTY_WEIGHT = 0.24
_POLICY_SOFT_DUPLICATE_PENALTY = 0.14
_POLICY_STRICT_DUPLICATE_PENALTY = 0.27
_POLICY_DOMAIN_SOFT_CAP_PENALTY = 0.18
_POLICY_LAYER_SOFT_CAP_PENALTY = 0.14
_POLICY_OPENING_REPEAT_PENALTY = 0.08
_POLICY_PHRASE_REPEAT_THRESHOLD = 0.34
_POLICY_PHRASE_REPEAT_PENALTY = 0.12
_POLICY_V8_SHADOW_PENALTY = 0.1
_POLICY_V8_SHADOW_PENALTY_SCALE = 0.5
_POLICY_V8_SHADOW_PENALTY_SHARE_CAP = 0.5
_POLICY_V8_SHADOW_PENALTY_MIN_RETENTION = 0.5
_V8_REQUIRED_UNIQUE_SLOTS = 8
_V8_SHADOW_MIN_COUNT = 1
_V8_SHADOW_MAX_COUNT = 2
_POLICY_LAYER_BONUS: dict[str, float] = {
    "shadow": 1.0,
    "effect": 0.95,
    "mechanism": 0.7,
    "potential": 0.68,
    "cause": 0.5,
    "recognition": 0.45,
}
_SIMILARITY_STOPWORDS: set[str] = {
    "ve",
    "ama",
    "ancak",
    "ile",
    "bir",
    "bu",
    "de",
    "da",
    "ic",
    "dis",
    "gibi",
    "daha",
    "cok",
    "en",
}
_SELECTION_DEBUG_ENV = "ENABLE_PROJECTION_SELECTION_DEBUG"
_LAST_SELECTION_DEBUG: dict[str, Any] = {}


def get_last_projection_selection_debug() -> dict[str, Any]:
    return copy.deepcopy(_LAST_SELECTION_DEBUG)


def clear_last_projection_selection_debug() -> None:
    _LAST_SELECTION_DEBUG.clear()


def _selection_debug_enabled(selection_debug: MutableMapping[str, Any] | None) -> bool:
    if selection_debug is not None:
        return True
    raw = os.getenv(_SELECTION_DEBUG_ENV, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _selection_debug_container(
    *,
    selection_debug: MutableMapping[str, Any] | None,
    projection_name: str,
) -> MutableMapping[str, Any] | None:
    if not _selection_debug_enabled(selection_debug):
        return None
    container = selection_debug if selection_debug is not None else {}
    container.setdefault("projection", projection_name)
    container.setdefault("enabled_by", "caller" if selection_debug is not None else "env")
    container.setdefault("branches", {})
    return container


def _commit_selection_debug(container: Mapping[str, Any] | None) -> None:
    if not isinstance(container, Mapping):
        return
    _LAST_SELECTION_DEBUG.clear()
    _LAST_SELECTION_DEBUG.update(copy.deepcopy(dict(container)))


def _ensure_selection_debug_branch(
    debug: MutableMapping[str, Any] | None,
    branch: str,
) -> MutableMapping[str, Any] | None:
    if debug is None:
        return None
    branches = debug.get("branches")
    if not isinstance(branches, MutableMapping):
        branches = {}
        debug["branches"] = branches
    branch_data = branches.get(branch)
    if not isinstance(branch_data, MutableMapping):
        branch_data = {
            "selected_node_ids": [],
            "candidate_score_decomposition": [],
            "reason_counters": {},
            "duplicate_fingerprint_hits": 0,
            "near_duplicate_hits": 0,
            "domain_cap_hits": 0,
            "layer_cap_hits": 0,
            "underfill_relaxation_used": False,
        }
        branches[branch] = branch_data
    return branch_data


def _inc_reason_counter(debug_branch: MutableMapping[str, Any] | None, reason: str, value: int = 1) -> None:
    if debug_branch is None or not reason:
        return
    counters = debug_branch.get("reason_counters")
    if not isinstance(counters, MutableMapping):
        counters = {}
        debug_branch["reason_counters"] = counters
    counters[reason] = int(counters.get(reason, 0)) + int(value)


def _inc_debug_metric(debug_branch: MutableMapping[str, Any] | None, metric: str, value: int = 1) -> None:
    if debug_branch is None or not metric:
        return
    debug_branch[metric] = int(debug_branch.get(metric, 0)) + int(value)


def build_profile_narrative_projection_v1(
    *,
    meaning_graph_v1_1: Mapping[str, Any] | None,
    natal_promise_packets_v1: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
    natal_promise_cluster_plan_v1: Mapping[str, Any] | None = None,
    include_packet_debug: bool = False,
    selection_debug: MutableMapping[str, Any] | None = None,
) -> Dict[str, Any]:
    debug = _selection_debug_container(
        selection_debug=selection_debug,
        projection_name="profile_narrative_projection_v1",
    )
    graph = meaning_graph_v1_1 if isinstance(meaning_graph_v1_1, Mapping) else {}
    graph_version = str(graph.get("version") or "")
    raw_nodes = _sorted_nodes(graph)
    evidence_map = _evidence_map(graph)
    nodes = _normalized_projection_nodes(raw_nodes, evidence_map)
    packet_payload = _coerce_packet_payload(natal_promise_packets_v1)
    cluster_payload = _coerce_cluster_plan_payload(natal_promise_cluster_plan_v1)
    cluster_context = _cluster_packet_payloads(cluster_payload)
    packet_nodes = _packet_projection_nodes(packet_payload)
    packet_count = len(packet_nodes)
    legacy_nodes = list(nodes)
    cluster_main_nodes = _packet_projection_nodes(cluster_context["public_main_payload"])
    cluster_support_nodes = _packet_projection_nodes(cluster_context["support_payload"])
    cluster_detail_nodes = _packet_projection_nodes(cluster_context["detail_payload"])
    cluster_main_count = len(cluster_main_nodes)

    if cluster_main_count >= 3:
        core_nodes = cluster_main_nodes[:4]
        used_core_ids = {str(item.get("node_id") or "").strip() for item in core_nodes}
        # Bug 1: when extra-source pool contains the `_aux` mirror of a packet
        # whose parent cluster is already represented in core_blocks, skip it.
        # Otherwise extra_blocks end up as duplicate-headline cards (see Adana
        # audit). Empty extra_blocks is preferable to duplicate cards;
        # downstream renderers and the carousel handle the empty case.
        core_packet_ids = {
            _node_packet_id(node) for node in core_nodes if _node_packet_id(node)
        }
        guaranteed_extra_nodes = [
            node for node in cluster_main_nodes[4:]
            if str(node.get("node_id") or "").strip() not in used_core_ids
            and not (
                _is_aux_packet_id(_node_packet_id(node))
                and _aux_base_packet_id(_node_packet_id(node)) in core_packet_ids
            )
        ]
        guaranteed_extra_ids = {str(item.get("node_id") or "").strip() for item in guaranteed_extra_nodes}
        extra_source = [
            *[
                node for node in cluster_support_nodes
                if str(node.get("node_id") or "").strip() not in used_core_ids
                and str(node.get("node_id") or "").strip() not in guaranteed_extra_ids
                and not (
                    _is_aux_packet_id(_node_packet_id(node))
                    and _aux_base_packet_id(_node_packet_id(node)) in core_packet_ids
                )
            ],
            *[
                node for node in cluster_detail_nodes
                if str(node.get("node_id") or "").strip() not in used_core_ids
                and str(node.get("node_id") or "").strip() not in guaranteed_extra_ids
                and not (
                    _is_aux_packet_id(_node_packet_id(node))
                    and _aux_base_packet_id(_node_packet_id(node)) in core_packet_ids
                )
            ],
        ]
        picked_extra_nodes = _pick_nodes(
            extra_source,
            preferred_surfaces=("profile_deep", "profile_top", "explainability"),
            limit=max(0, 6 - len(guaranteed_extra_nodes)),
            enforce_domain_diversity=True,
            max_same_domain=3,
            max_same_layer=3,
            profile_kind="narrative",
            selection_debug_branch=_ensure_selection_debug_branch(debug, "narrative_extra_cluster"),
        )
        extra_nodes = [*guaranteed_extra_nodes, *picked_extra_nodes]
    elif cluster_main_count > 0:
        core_nodes = list(cluster_main_nodes)
        used_core_ids = {str(item.get("node_id") or "").strip() for item in core_nodes}
        packet_fill_source = [
            node
            for node in packet_nodes
            if str(node.get("node_id") or "").strip() not in used_core_ids
        ]
        packet_fill = _pick_nodes(
            packet_fill_source,
            preferred_surfaces=("profile_top", "profile_deep"),
            limit=max(0, 4 - len(core_nodes)),
            enforce_domain_diversity=True,
            max_same_domain=3,
            max_same_layer=3,
            profile_kind="narrative",
            selection_debug_branch=_ensure_selection_debug_branch(debug, "narrative_core_packet_fill"),
        )
        core_nodes.extend(packet_fill)
        used_ids = {str(node.get("node_id") or "").strip() for node in core_nodes}
        legacy_fill = _pick_nodes(
            [
                node
                for node in legacy_nodes
                if str(node.get("node_id") or "").strip() not in used_ids
            ],
            preferred_surfaces=("profile_top", "profile_deep"),
            limit=max(0, 4 - len(core_nodes)),
            enforce_domain_diversity=True,
            max_same_domain=3,
            max_same_layer=3,
            profile_kind="narrative",
            selection_debug_branch=_ensure_selection_debug_branch(debug, "narrative_core_legacy_fill"),
        )
        core_nodes.extend(legacy_fill)
        used_ids = {str(node.get("node_id") or "").strip() for node in core_nodes}
        # Bug 1 (hybrid fallback path): same aux-mirror suppression as the
        # full-cluster path above so empty support/detail layers never produce
        # duplicate-headline cards.
        core_packet_ids_hybrid = {
            _node_packet_id(node) for node in core_nodes if _node_packet_id(node)
        }

        def _not_core_aux(node: Mapping[str, Any]) -> bool:
            pid = _node_packet_id(node)
            return not (_is_aux_packet_id(pid) and _aux_base_packet_id(pid) in core_packet_ids_hybrid)

        extra_source = [
            *[
                node for node in cluster_support_nodes
                if str(node.get("node_id") or "").strip() not in used_ids
                and _not_core_aux(node)
            ],
            *[
                node for node in cluster_detail_nodes
                if str(node.get("node_id") or "").strip() not in used_ids
                and _not_core_aux(node)
            ],
            *[
                node for node in packet_nodes
                if str(node.get("node_id") or "").strip() not in used_ids
                and _not_core_aux(node)
            ],
            *[
                node for node in legacy_nodes
                if str(node.get("node_id") or "").strip() not in used_ids
            ],
        ]
        extra_nodes = _pick_nodes(
            extra_source,
            preferred_surfaces=("profile_deep", "profile_top", "explainability"),
            limit=6,
            enforce_domain_diversity=True,
            max_same_domain=3,
            max_same_layer=3,
            profile_kind="narrative",
            selection_debug_branch=_ensure_selection_debug_branch(debug, "narrative_extra_cluster_hybrid"),
        )
    elif packet_count >= 3:
        core_nodes = _pick_nodes(
            packet_nodes,
            preferred_surfaces=("profile_top", "profile_deep"),
            limit=4,
            enforce_domain_diversity=True,
            max_same_domain=3,
            max_same_layer=3,
            profile_kind="narrative",
            selection_debug_branch=_ensure_selection_debug_branch(debug, "narrative_core"),
        )
        extra_nodes_source = [
            node
            for node in packet_nodes
            if str(node.get("node_id") or "").strip() not in {str(item.get("node_id") or "").strip() for item in core_nodes}
        ]
        extra_nodes = _pick_nodes(
            extra_nodes_source,
            preferred_surfaces=("profile_deep", "profile_top", "explainability"),
            limit=6,
            enforce_domain_diversity=True,
            max_same_domain=3,
            max_same_layer=3,
            profile_kind="narrative",
            selection_debug_branch=_ensure_selection_debug_branch(debug, "narrative_extra"),
        )
    elif packet_count > 0:
        packet_core = _pick_nodes(
            packet_nodes,
            preferred_surfaces=("profile_top", "profile_deep"),
            limit=min(4, packet_count),
            enforce_domain_diversity=True,
            max_same_domain=3,
            max_same_layer=3,
            profile_kind="narrative",
            selection_debug_branch=_ensure_selection_debug_branch(debug, "narrative_core"),
        )
        used_packet_ids = {str(node.get("node_id") or "").strip() for node in packet_core}
        legacy_remaining = [
            node
            for node in legacy_nodes
            if str(node.get("node_id") or "").strip()
            and str(node.get("node_id") or "").strip() not in used_packet_ids
        ]
        legacy_core = _pick_nodes(
            legacy_remaining,
            preferred_surfaces=("profile_top", "profile_deep"),
            limit=max(0, 4 - len(packet_core)),
            enforce_domain_diversity=True,
            max_same_domain=3,
            max_same_layer=3,
            profile_kind="narrative",
            selection_debug_branch=_ensure_selection_debug_branch(debug, "narrative_core_legacy_fill"),
        )
        core_nodes = [*packet_core, *legacy_core]
        used_ids = {str(node.get("node_id") or "").strip() for node in core_nodes}
        extra_pool = [
            *[node for node in packet_nodes if str(node.get("node_id") or "").strip() not in used_ids],
            *[node for node in legacy_nodes if str(node.get("node_id") or "").strip() not in used_ids],
        ]
        extra_nodes = _pick_nodes(
            extra_pool,
            preferred_surfaces=("profile_deep", "profile_top", "explainability"),
            limit=6,
            enforce_domain_diversity=True,
            max_same_domain=3,
            max_same_layer=3,
            profile_kind="narrative",
            selection_debug_branch=_ensure_selection_debug_branch(debug, "narrative_extra"),
        )
    else:
        core_nodes = _pick_nodes(
            nodes,
            preferred_surfaces=("profile_top", "profile_deep"),
            limit=4,
            enforce_domain_diversity=True,
            max_same_domain=3,
            max_same_layer=3,
            profile_kind="narrative",
            selection_debug_branch=_ensure_selection_debug_branch(debug, "narrative_core"),
        )
        used_ids = {str(node.get("node_id") or "").strip() for node in core_nodes}
        used_fingerprints = {
            _node_dedupe_fingerprint(node)
            for node in core_nodes
            if _node_dedupe_fingerprint(node)
        }
        remaining_nodes = [
            node
            for node in nodes
            if str(node.get("node_id") or "").strip()
            and str(node.get("node_id") or "").strip() not in used_ids
            and (
                not _node_dedupe_fingerprint(node)
                or _node_dedupe_fingerprint(node) not in used_fingerprints
            )
        ]
        extra_nodes = _pick_nodes(
            remaining_nodes,
            preferred_surfaces=("profile_deep", "profile_top", "explainability"),
            limit=6,
            enforce_domain_diversity=True,
            max_same_domain=3,
            max_same_layer=3,
            profile_kind="narrative",
            selection_debug_branch=_ensure_selection_debug_branch(debug, "narrative_extra"),
        )

    used_block_ids: set[str] = set()
    used_openings: list[str] = []
    used_bodies: list[str] = []
    core_blocks = [
        _profile_block_from_node(
            node=node,
            emphasis="core",
            used_block_ids=used_block_ids,
            used_openings=used_openings,
            used_bodies=used_bodies,
        )
        for node in core_nodes
    ]
    extra_blocks = [
        _profile_block_from_node(
            node=node,
            emphasis="extra",
            used_block_ids=used_block_ids,
            used_openings=used_openings,
            used_bodies=used_bodies,
        )
        for node in extra_nodes
    ]
    blocks = [*core_blocks, *extra_blocks]
    detail_cards = [_detail_card_from_block(block) for block in blocks[:12]]
    _commit_selection_debug(debug)

    return {
        "version": "profile_narrative_projection_v1",
        "source_graph_version": (
            str(cluster_payload.get("version") or graph_version)
            if cluster_main_count > 0
            else graph_version
        ),
        "source_graph": (
            "natal_promise_cluster_plan_v1"
            if cluster_main_count > 0
            else ("natal_promise_packets_v1" if packet_count > 0 else _PROJECTION_SOURCE)
        ),
        "profile_public": {
            "schema_version": "profile_narrative_projection_v1",
            "blocks": blocks,
            "core_blocks": core_blocks,
            "extra_blocks": extra_blocks,
            "detail_cards": detail_cards,
        },
        "traceability": {
            "node_count": len(nodes),
            "evidence_count": len(evidence_map),
            "packet_count": packet_count,
            "cluster_public_main_count": cluster_main_count,
            **(
                {
                    "natal_promise_packets_v1": packet_payload,
                }
                if include_packet_debug and packet_count > 0
                else {}
            ),
            **(
                {
                    "natal_promise_cluster_plan_v1": cluster_payload,
                }
                if include_packet_debug and cluster_main_count > 0
                else {}
            ),
        },
    }


def build_profile_v8_projection_v1(
    *,
    meaning_graph_v1_1: Mapping[str, Any] | None,
    natal_promise_packets_v1: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
    natal_promise_cluster_plan_v1: Mapping[str, Any] | None = None,
    include_packet_debug: bool = False,
    selection_debug: MutableMapping[str, Any] | None = None,
) -> Dict[str, Any]:
    debug = _selection_debug_container(
        selection_debug=selection_debug,
        projection_name="profile_v8_projection_v1",
    )
    graph = meaning_graph_v1_1 if isinstance(meaning_graph_v1_1, Mapping) else {}
    graph_version = str(graph.get("version") or "")
    raw_nodes = _sorted_nodes(graph)
    evidence_map = _evidence_map(graph)
    nodes = _normalized_projection_nodes(raw_nodes, evidence_map)
    packet_payload = _coerce_packet_payload(natal_promise_packets_v1)
    cluster_payload = _coerce_cluster_plan_payload(natal_promise_cluster_plan_v1)
    cluster_context = _cluster_packet_payloads(cluster_payload)
    packet_nodes = _packet_projection_nodes(packet_payload)
    packet_count = len(packet_nodes)
    cluster_main_nodes = _packet_projection_nodes(cluster_context["v8_primary_payload"])
    cluster_support_nodes = _packet_projection_nodes(cluster_context["support_payload"])
    cluster_detail_nodes = _packet_projection_nodes(cluster_context["detail_payload"])
    cluster_main_count = len(_packet_projection_nodes(cluster_context["public_main_payload"]))
    if cluster_main_count >= 3:
        nodes = [*cluster_main_nodes, *cluster_support_nodes, *cluster_detail_nodes]
    elif cluster_main_count > 0:
        used_cluster_ids = {str(node.get("node_id") or "").strip() for node in [*cluster_main_nodes, *cluster_support_nodes, *cluster_detail_nodes]}
        packet_fill = [
            node
            for node in packet_nodes
            if str(node.get("node_id") or "").strip() not in used_cluster_ids
        ]
        legacy_fill = [
            node
            for node in nodes
            if str(node.get("node_id") or "").strip() not in used_cluster_ids
        ]
        nodes = [*cluster_main_nodes, *cluster_support_nodes, *cluster_detail_nodes, *packet_fill, *legacy_fill]
    elif packet_count >= 3:
        nodes = packet_nodes
    elif packet_count > 0:
        used_packet_ids = {str(node.get("node_id") or "").strip() for node in packet_nodes}
        legacy_fill = [
            node
            for node in nodes
            if str(node.get("node_id") or "").strip()
            and str(node.get("node_id") or "").strip() not in used_packet_ids
        ]
        nodes = [*packet_nodes, *legacy_fill]
    unique_node_capacity = len({_node_id(node) for node in nodes if _node_id(node)})
    allow_cross_slot_duplicates = unique_node_capacity < _V8_REQUIRED_UNIQUE_SLOTS
    used_slot_ids: set[str] = set()

    hero_candidates = _pick_nodes(
        _hero_tuned_v8_pool(
            _selection_pool_for_v8(
                all_nodes=nodes,
                used_slot_ids=used_slot_ids,
                allow_cross_slot_duplicates=allow_cross_slot_duplicates,
            )
        ),
        preferred_surfaces=("profile_top", "home", "profile_deep"),
        limit=1,
        max_same_domain=2,
        max_same_layer=2,
        profile_kind="v8",
        max_shadow_nodes=_V8_SHADOW_MAX_COUNT,
        selection_debug_branch=_ensure_selection_debug_branch(debug, "v8_hero"),
    )
    hero_node = hero_candidates[0] if hero_candidates else (nodes[0] if nodes else {})
    hero_node_id = _node_id(hero_node)
    if hero_node_id:
        used_slot_ids.add(hero_node_id)

    identity_pool = _selection_pool_for_v8(
        all_nodes=nodes,
        used_slot_ids=used_slot_ids,
        allow_cross_slot_duplicates=allow_cross_slot_duplicates,
    )
    # v8 identity_axis preference (per docs/system/adana_cluster_plan_audit_after_v0_3_final.md
    # §4 + §5): when ANY identity-family cluster exists in the plan, the
    # identity_axis surface must surface one — even if that cluster only sits
    # at detail tier — instead of falling back to a mind-family packet.
    # Hero / identity_axis must come from distinct clusters: we honour that
    # by excluding the hero's source cluster id from the identity-family
    # candidate set before falling back to the legacy layer-preference pick.
    hero_cluster_id = _node_cluster_id(hero_node)
    identity_node = _pick_identity_axis_node(
        pool=identity_pool,
        hero_cluster_id=hero_cluster_id,
    )
    if not identity_node:
        # No identity-family cluster available anywhere in the plan (or every
        # identity-family cluster is the same one the hero already consumed).
        # Fall back to the legacy recognition/mechanism layer preference so
        # that profiles without an identity cluster keep the prior surface.
        identity_node = (
            _pick_first(
                identity_pool,
                preferred_layers=("recognition", "mechanism"),
            )
            or (identity_pool[0] if identity_pool else hero_node)
        )
    identity_node_id = _node_id(identity_node)
    if identity_node_id:
        used_slot_ids.add(identity_node_id)

    insight_nodes = _pick_nodes(
        _selection_pool_for_v8(
            all_nodes=nodes,
            used_slot_ids=used_slot_ids,
            allow_cross_slot_duplicates=allow_cross_slot_duplicates,
        ),
        preferred_surfaces=("profile_top", "home"),
        limit=3,
        max_same_domain=2,
        max_same_layer=2,
        profile_kind="v8",
        max_shadow_nodes=_V8_SHADOW_MAX_COUNT,
        selection_debug_branch=_ensure_selection_debug_branch(debug, "v8_insight_strip"),
    )
    _top_up_v8_slots(
        selected_nodes=insight_nodes,
        all_nodes=nodes,
        used_slot_ids=used_slot_ids,
        target=3,
        allow_cross_slot_duplicates=allow_cross_slot_duplicates,
    )
    used_slot_ids.update(
        {
            _node_id(node)
            for node in insight_nodes
            if _node_id(node)
        }
    )

    used_insight_ids = {str(node.get("node_id") or "").strip() for node in insight_nodes}
    used_insight_fingerprints = {
        _node_dedupe_fingerprint(node)
        for node in insight_nodes
        if _node_dedupe_fingerprint(node)
    }
    differentiator_pool = [
        node
        for node in _selection_pool_for_v8(
            all_nodes=nodes,
            used_slot_ids=used_slot_ids,
            allow_cross_slot_duplicates=allow_cross_slot_duplicates,
        )
        if str(node.get("node_id") or "").strip() not in used_insight_ids
        and (
            not _node_dedupe_fingerprint(node)
            or _node_dedupe_fingerprint(node) not in used_insight_fingerprints
        )
    ]
    differentiator_nodes = _pick_nodes(
        differentiator_pool,
        preferred_surfaces=("profile_deep",),
        limit=3,
        max_same_domain=2,
        max_same_layer=2,
        profile_kind="v8",
        max_shadow_nodes=_V8_SHADOW_MAX_COUNT,
        selection_debug_branch=_ensure_selection_debug_branch(debug, "v8_differentiators"),
    )
    _top_up_v8_slots(
        selected_nodes=differentiator_nodes,
        all_nodes=differentiator_pool,
        used_slot_ids=used_slot_ids,
        target=3,
        allow_cross_slot_duplicates=allow_cross_slot_duplicates,
        blocked_fingerprints=used_insight_fingerprints,
    )
    if len(differentiator_nodes) < 3:
        needed = 3 - len(differentiator_nodes)
        used_diff_ids = {str(node.get("node_id") or "").strip() for node in differentiator_nodes}
        topup_pool = [
            node
            for node in _selection_pool_for_v8(
                all_nodes=nodes,
                used_slot_ids=used_slot_ids,
                allow_cross_slot_duplicates=allow_cross_slot_duplicates,
            )
            if str(node.get("node_id") or "").strip()
            and str(node.get("node_id") or "").strip() not in used_diff_ids
        ]
        topup_nodes = _pick_nodes(
            topup_pool,
            preferred_surfaces=("profile_deep", "profile_top", "home"),
            limit=needed,
            max_same_domain=2,
            max_same_layer=2,
            profile_kind="v8",
            max_shadow_nodes=_V8_SHADOW_MAX_COUNT,
            selection_debug_branch=_ensure_selection_debug_branch(debug, "v8_differentiator_topup"),
        )
        differentiator_nodes.extend(topup_nodes)
    _top_up_v8_slots(
        selected_nodes=differentiator_nodes,
        all_nodes=nodes,
        used_slot_ids=used_slot_ids,
        target=3,
        allow_cross_slot_duplicates=allow_cross_slot_duplicates,
        blocked_fingerprints=used_insight_fingerprints,
    )
    if len(differentiator_nodes) < 3:
        used_diff_ids = {str(node.get("node_id") or "").strip() for node in differentiator_nodes}
        for node in nodes:
            node_id = str(node.get("node_id") or "").strip()
            if not node_id or node_id in used_diff_ids:
                continue
            differentiator_nodes.append(dict(node))
            used_diff_ids.add(node_id)
            if len(differentiator_nodes) >= 3:
                break
    if not differentiator_nodes:
        differentiator_nodes = nodes[:3]
    _enforce_v8_shadow_floor_and_cap(
        insight_nodes=insight_nodes,
        differentiator_nodes=differentiator_nodes,
        all_nodes=nodes,
        reserved_slot_ids={node_id for node_id in (hero_node_id, identity_node_id) if node_id},
        allow_cross_slot_duplicates=allow_cross_slot_duplicates,
        min_shadow_nodes=_V8_SHADOW_MIN_COUNT,
        max_shadow_nodes=_V8_SHADOW_MAX_COUNT,
    )
    _commit_selection_debug(debug)

    return {
        "version": "profile_v8_projection_v1",
        "source_graph_version": (
            str(cluster_payload.get("version") or graph_version)
            if cluster_main_count > 0
            else graph_version
        ),
        "source_graph": (
            "natal_promise_cluster_plan_v1"
            if cluster_main_count > 0
            else ("natal_promise_packets_v1" if packet_count > 0 else _PROJECTION_SOURCE)
        ),
        "hero": _hero_from_node(node=hero_node),
        "identity_axis": _section_from_node(
            node=identity_node,
            eyebrow="Kimlik Ekseni",
        ),
        "insight_strip": [
            _insight_cell_from_node(node=node)
            for node in insight_nodes
        ],
        "differentiators": [
            _differentiator_from_node(node=node)
            for node in differentiator_nodes
        ],
        "traceability": {
            "node_count": len(nodes),
            "evidence_count": len(evidence_map),
            "packet_count": packet_count,
            "cluster_public_main_count": cluster_main_count,
            **(
                {
                    "natal_promise_packets_v1": packet_payload,
                }
                if include_packet_debug and packet_count > 0
                else {}
            ),
            **(
                {
                    "natal_promise_cluster_plan_v1": cluster_payload,
                }
                if include_packet_debug and cluster_main_count > 0
                else {}
            ),
        },
    }


def _sorted_nodes(graph: Mapping[str, Any]) -> List[Dict[str, Any]]:
    raw_nodes = graph.get("nodes") if isinstance(graph.get("nodes"), Sequence) else []
    nodes = [dict(item) for item in raw_nodes if isinstance(item, Mapping)]
    nodes.sort(
        key=lambda item: (
            -_policy_score_node(item, seen_domains=set()),
            -_node_priority(item),
            -_top_layer_weight(item),
            -_node_evidence_count(item),
            str(item.get("node_id") or ""),
        )
    )
    return nodes


def _evidence_map(graph: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    raw_evidence = graph.get("evidence") if isinstance(graph.get("evidence"), Sequence) else []
    out: Dict[str, Dict[str, Any]] = {}
    for entry in raw_evidence:
        if not isinstance(entry, Mapping):
            continue
        evidence_id = str(entry.get("evidence_id") or "").strip()
        if not evidence_id:
            continue
        out[evidence_id] = dict(entry)
    return out


def _normalized_projection_nodes(
    nodes: Sequence[Mapping[str, Any]],
    evidence_map: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for node in nodes:
        normalized = _normalize_projection_node(node, evidence_map)
        if normalized:
            out.append(normalized)
    return out


def _coerce_packet_payload(
    payload: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None,
) -> dict[str, Any]:
    if isinstance(payload, Mapping):
        packets = payload.get("packets") if isinstance(payload.get("packets"), Sequence) else []
        return {
            **dict(payload),
            "packets": [dict(item) for item in packets if isinstance(item, Mapping)],
        }
    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        return {
            "version": "natal_promise_packets_v1",
            "packets": [dict(item) for item in payload if isinstance(item, Mapping)],
        }
    return {"version": "natal_promise_packets_v1", "packets": []}


def _coerce_cluster_plan_payload(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return {"version": "natal_promise_cluster_plan_v1", "clusters": [], "surface_plan": {}, "candidate_packets": []}
    clusters = payload.get("clusters") if isinstance(payload.get("clusters"), Sequence) else []
    candidate_packets = payload.get("candidate_packets") if isinstance(payload.get("candidate_packets"), Sequence) else []
    surface_plan = payload.get("surface_plan") if isinstance(payload.get("surface_plan"), Mapping) else {}
    suppressed = payload.get("suppressed_packets") if isinstance(payload.get("suppressed_packets"), Sequence) else []
    anchor_usage = payload.get("anchor_usage") if isinstance(payload.get("anchor_usage"), Sequence) else []
    focus_map = payload.get("focus_map") if isinstance(payload.get("focus_map"), Sequence) else []
    return {
        **dict(payload),
        "clusters": [dict(item) for item in clusters if isinstance(item, Mapping)],
        "candidate_packets": [dict(item) for item in candidate_packets if isinstance(item, Mapping)],
        "surface_plan": dict(surface_plan),
        "suppressed_packets": [dict(item) for item in suppressed if isinstance(item, Mapping)],
        "anchor_usage": [dict(item) for item in anchor_usage if isinstance(item, Mapping)],
        "focus_map": [dict(item) for item in focus_map if isinstance(item, Mapping)],
    }


def _cluster_packet_payloads(cluster_payload: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    packet_lookup = {
        str(packet.get("id") or "").strip(): dict(packet)
        for packet in (cluster_payload.get("candidate_packets") or [])
        if isinstance(packet, Mapping) and str(packet.get("id") or "").strip()
    }
    cluster_lookup = {
        str(cluster.get("id") or "").strip(): dict(cluster)
        for cluster in (cluster_payload.get("clusters") or [])
        if isinstance(cluster, Mapping) and str(cluster.get("id") or "").strip()
    }
    surface_plan = cluster_payload.get("surface_plan") if isinstance(cluster_payload.get("surface_plan"), Mapping) else {}
    main_cluster_ids = [
        str(item).strip()
        for item in (surface_plan.get("public_main_cluster_ids") or [])
        if str(item).strip()
    ]
    support_cluster_ids = [
        str(item).strip()
        for item in (surface_plan.get("public_support_cluster_ids") or [])
        if str(item).strip()
    ]
    detail_cluster_ids = [
        str(item).strip()
        for item in (surface_plan.get("detail_cluster_ids") or [])
        if str(item).strip()
    ]
    suppressed = {
        str(item.get("packet_id") or "").strip(): dict(item)
        for item in (cluster_payload.get("suppressed_packets") or [])
        if isinstance(item, Mapping) and str(item.get("packet_id") or "").strip()
    }
    support_main_packet_ids = {
        str((cluster_lookup.get(cluster_id) or {}).get("main_packet_id") or "").strip()
        for cluster_id in support_cluster_ids
        if str((cluster_lookup.get(cluster_id) or {}).get("main_packet_id") or "").strip()
    }
    detail_main_packet_ids = {
        str((cluster_lookup.get(cluster_id) or {}).get("main_packet_id") or "").strip()
        for cluster_id in detail_cluster_ids
        if str((cluster_lookup.get(cluster_id) or {}).get("main_packet_id") or "").strip()
    }
    deferred_main_packet_ids = support_main_packet_ids | detail_main_packet_ids

    public_main_packets: list[dict[str, Any]] = []
    support_packets: list[dict[str, Any]] = []
    detail_packets: list[dict[str, Any]] = []
    v8_primary_packets: list[dict[str, Any]] = []
    seen_main: set[str] = set()
    seen_support: set[str] = set()
    seen_detail: set[str] = set()

    for cluster_id in main_cluster_ids:
        cluster = cluster_lookup.get(cluster_id)
        if not cluster:
            continue
        packet = _cluster_main_packet_copy(
            cluster=cluster,
            packet_lookup=packet_lookup,
        )
        if packet is None:
            continue
        packet_id = str(packet.get("id") or "").strip()
        if packet_id and packet_id not in seen_main:
            public_main_packets.append(packet)
            seen_main.add(packet_id)

    hero_main_order = sorted(
        [cluster_lookup[cluster_id] for cluster_id in main_cluster_ids if cluster_id in cluster_lookup],
        key=lambda cluster: (-_cluster_v8_hero_priority(cluster, packet_lookup), str(cluster.get("id") or "")),
    )
    for cluster in hero_main_order:
        packet = _cluster_main_packet_copy(
            cluster=cluster,
            packet_lookup=packet_lookup,
            priority_bonus=0.08,
        )
        if packet is None:
            continue
        packet_id = str(packet.get("id") or "").strip()
        if packet_id and packet_id not in {str(item.get("id") or "").strip() for item in v8_primary_packets}:
            v8_primary_packets.append(packet)

    for cluster_id in [*main_cluster_ids, *support_cluster_ids]:
        cluster = cluster_lookup.get(cluster_id)
        if not cluster:
            continue
        for packet in _cluster_support_packets(cluster=cluster, packet_lookup=packet_lookup):
            packet_id = str(packet.get("id") or "").strip()
            if packet_id in deferred_main_packet_ids:
                continue
            if not packet_id or packet_id in seen_main or packet_id in seen_support:
                continue
            support_packets.append(packet)
            seen_support.add(packet_id)
        if cluster_id in support_cluster_ids:
            main_packet = _cluster_main_packet_copy(
                cluster=cluster,
                packet_lookup=packet_lookup,
                priority_bonus=0.02,
            )
            if main_packet is not None:
                packet_id = str(main_packet.get("id") or "").strip()
                if packet_id and packet_id not in seen_main and packet_id not in seen_support:
                    support_packets.append(main_packet)
                    seen_support.add(packet_id)

    for cluster_id in detail_cluster_ids:
        cluster = cluster_lookup.get(cluster_id)
        if not cluster:
            continue
        main_packet = _cluster_main_packet_copy(
            cluster=cluster,
            packet_lookup=packet_lookup,
            priority_bonus=-0.03,
        )
        if main_packet is None:
            continue
        packet_id = str(main_packet.get("id") or "").strip()
        if packet_id and packet_id not in seen_main and packet_id not in seen_support and packet_id not in seen_detail:
            detail_packets.append(main_packet)
            seen_detail.add(packet_id)

    for cluster_id in [*support_cluster_ids, *detail_cluster_ids]:
        cluster = cluster_lookup.get(cluster_id)
        if not cluster:
            continue
        for packet in _cluster_support_packets(cluster=cluster, packet_lookup=packet_lookup):
            packet_id = str(packet.get("id") or "").strip()
            if packet_id in deferred_main_packet_ids:
                continue
            if not packet_id or packet_id in seen_main or packet_id in seen_support or packet_id in seen_detail:
                continue
            detail_packets.append(packet)
            seen_detail.add(packet_id)

    for packet_id, suppression in suppressed.items():
        keep_for = suppression.get("keep_for") if isinstance(suppression.get("keep_for"), Sequence) else []
        if "detail" not in {str(item).strip() for item in keep_for}:
            continue
        packet = packet_lookup.get(packet_id)
        if not packet or packet_id in seen_main or packet_id in seen_support or packet_id in seen_detail:
            continue
        detail_packets.append(_copy_packet_with_cluster_priority(packet, cluster=None, priority_bonus=-0.05, explicit_anchor_allowed=False))
        seen_detail.add(packet_id)

    return {
        "public_main_payload": {"version": "natal_promise_packets_v1", "packets": public_main_packets},
        "support_payload": {"version": "natal_promise_packets_v1", "packets": support_packets},
        "detail_payload": {"version": "natal_promise_packets_v1", "packets": detail_packets},
        "v8_primary_payload": {"version": "natal_promise_packets_v1", "packets": v8_primary_packets},
    }


def _cluster_main_packet_copy(
    *,
    cluster: Mapping[str, Any],
    packet_lookup: Mapping[str, Mapping[str, Any]],
    priority_bonus: float = 0.0,
) -> dict[str, Any] | None:
    packet_id = str(cluster.get("main_packet_id") or "").strip()
    packet = packet_lookup.get(packet_id)
    if not packet:
        return None
    member = _cluster_member(cluster, packet_id)
    return _copy_packet_with_cluster_priority(
        packet,
        cluster=cluster,
        priority_bonus=0.12 + priority_bonus,
        explicit_anchor_allowed=bool((member or {}).get("explicit_anchor_allowed", True)),
    )


def _cluster_support_packets(
    *,
    cluster: Mapping[str, Any],
    packet_lookup: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    main_packet_id = str(cluster.get("main_packet_id") or "").strip()
    for member in cluster.get("packet_members") or []:
        if not isinstance(member, Mapping):
            continue
        packet_id = str(member.get("packet_id") or "").strip()
        if not packet_id or packet_id == main_packet_id:
            continue
        packet = packet_lookup.get(packet_id)
        if not packet:
            continue
        role = str(member.get("cluster_role") or "").strip()
        priority_bonus = 0.04 if role == "secondary_anchor" else -0.02
        out.append(
            _copy_packet_with_cluster_priority(
                packet,
                cluster=cluster,
                priority_bonus=priority_bonus,
                explicit_anchor_allowed=bool(member.get("explicit_anchor_allowed", True)),
            )
        )
    return out


def _cluster_member(cluster: Mapping[str, Any], packet_id: str) -> Mapping[str, Any] | None:
    for member in cluster.get("packet_members") or []:
        if not isinstance(member, Mapping):
            continue
        if str(member.get("packet_id") or "").strip() == packet_id:
            return member
    return None


def _copy_packet_with_cluster_priority(
    packet: Mapping[str, Any],
    *,
    cluster: Mapping[str, Any] | None,
    priority_bonus: float,
    explicit_anchor_allowed: bool,
) -> dict[str, Any]:
    out = copy.deepcopy(dict(packet))
    hints = dict(out.get("projection_hints")) if isinstance(out.get("projection_hints"), Mapping) else {}
    base_priority = _safe_float(hints.get("priority"), _safe_float(out.get("strength"), 0.0))
    cluster_priority = _safe_float((cluster or {}).get("public_card_priority"), 0.0)
    hints["priority"] = round(max(base_priority, cluster_priority) + priority_bonus, 4)
    out["projection_hints"] = hints
    if not explicit_anchor_allowed:
        out["technical_anchors"] = []
    if cluster:
        out["cluster_context"] = {
            "cluster_id": str(cluster.get("id") or "").strip(),
            "domain_family": str(cluster.get("domain_family") or "").strip(),
            "target_surface_role": str(cluster.get("target_surface_role") or "").strip(),
            "public_card_priority": _safe_float(cluster.get("public_card_priority"), 0.0),
        }
    return out


def _cluster_v8_hero_priority(
    cluster: Mapping[str, Any],
    packet_lookup: Mapping[str, Mapping[str, Any]],
) -> float:
    score = _safe_float(cluster.get("public_card_priority"), 0.0)
    domain_family = str(cluster.get("domain_family") or "").strip()
    main_packet_id = str(cluster.get("main_packet_id") or "").strip()
    packet = packet_lookup.get(main_packet_id) or {}
    promise_type = str(packet.get("promise_type") or "").strip()
    if domain_family in {"mind", "identity"}:
        score += 0.32
    elif domain_family == "career":
        score += 0.1
    elif domain_family == "relationship":
        score -= 0.12
    if promise_type in {"mind_style", "mind_identity", "behavior_reflex"}:
        score += 0.18
    elif promise_type == "career_signature":
        score += 0.08
    elif promise_type in {"love_style", "need"}:
        score -= 0.14
    return score


def _packet_projection_nodes(packet_payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    packets = packet_payload.get("packets") if isinstance(packet_payload.get("packets"), Sequence) else []
    out: list[dict[str, Any]] = []
    for index, packet in enumerate(packets):
        if not isinstance(packet, Mapping):
            continue
        packet_id = str(packet.get("id") or "").strip()
        if not packet_id:
            continue
        promise_type = str(packet.get("promise_type") or "").strip()
        priority = _safe_float((packet.get("projection_hints") or {}).get("priority"), _safe_float(packet.get("strength"), 0.0))
        domain = str(packet.get("domain") or "").strip() or "general"
        headline = _best_packet_headline(packet)
        summary = _packet_public_direct_meaning(packet) or str(packet.get("lived_scene") or headline or "").strip()
        evidence = _packet_evidence_entries(packet)
        node = {
            "node_id": f"promise::{packet_id}",
            "node_type": "narrative",
            "title": headline,
            "headline": headline,
            "summary": summary,
            "layers": [
                {"layer": _packet_primary_layer(packet), "weight": 0.65},
                {"layer": "effect", "weight": 0.35},
            ],
            "primary_layer": _packet_primary_layer(packet),
            "domain": domain,
            "source_family": "natal_promise_packets_v1",
            "source_path": f"public.natal_promise_packets_v1[{index}]",
            "evidence_ids": [
                str(item.get("evidence_id") or "").strip()
                for item in evidence
                if str(item.get("evidence_id") or "").strip()
            ],
            "evidence": evidence,
            "projection_hints": {
                "surfaces": list((packet.get("projection_hints") or {}).get("surfaces") or ["profile_top", "profile_deep"]),
                "priority": priority + 0.24,
            },
            "dedupe_fingerprint": str(packet.get("theme_key") or packet_id).strip() or packet_id,
            "natal_promise_packet": dict(packet),
            "promise_type": promise_type,
            "strength": _safe_float(packet.get("strength"), 0.0),
        }
        out.append(node)
    return out


def _packet_evidence_entries(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for index, anchor in enumerate(packet.get("technical_anchors") or []):
        clean = str(anchor).strip()
        if not clean:
            continue
        out.append(
            {
                "evidence_id": f"{str(packet.get('id') or 'packet').strip()}::anchor::{index}",
                "kind": "reference",
                "source_family": "natal_promise_packets_v1",
                "source_path": f"packet.technical_anchors[{index}]",
                "weight": 0.6,
                "text": _public_anchor_chip(clean),
            }
        )
        if len(out) >= 2:
            break
    return out


def _packet_primary_layer(packet: Mapping[str, Any]) -> str:
    promise_type = str(packet.get("promise_type") or "").strip()
    if promise_type in {"shadow_or_friction", "wound_to_gift"}:
        return "shadow"
    if promise_type in {"mind_style", "mind_identity", "need", "behavior_reflex"}:
        return "mechanism"
    if promise_type in {"gift", "love_style", "career_signature", "drive"}:
        return "effect"
    return "effect"


def _best_packet_headline(packet: Mapping[str, Any]) -> str:
    override = _packet_copy_override(packet)
    if override.get("headline"):
        return str(override.get("headline") or "").strip()
    seeds = packet.get("voice_seeds") if isinstance(packet.get("voice_seeds"), Sequence) else []
    cleaned_seeds = [str(seed).strip() for seed in seeds if str(seed).strip()]
    if cleaned_seeds:
        index = _packet_variant_index(packet=packet, salt="headline", modulo=len(cleaned_seeds))
        return cleaned_seeds[index]
    return str(packet.get("direct_meaning") or packet.get("lived_scene") or packet.get("id") or "Profil Özü").strip()


def _fallback_short_headline(
    *,
    packet: Mapping[str, Any] | None,
    node: Mapping[str, Any],
    family: str,
) -> str:
    """Pick a single-sentence headline candidate when the primary slot was
    contaminated with body-length copy. Walks packet fields known to hold
    short copy, then falls back to a short slice of the summary."""
    candidates: list[str] = []
    if packet:
        override = _packet_copy_override(packet)
        if isinstance(override, Mapping):
            candidates.append(str(override.get("teaser") or "").strip())
        for seed in packet.get("voice_seeds") or []:
            candidates.append(str(seed or "").strip())
        candidates.append(str(packet.get("lived_scene_short") or "").strip())
        candidates.append(str(packet.get("direct_meaning") or "").strip())
        candidates.append(str(packet.get("lived_scene") or "").strip())
    summary = str(node.get("summary") or "").strip()
    if summary:
        candidates.append(summary)
    for candidate in candidates:
        clipped = _clip_to_headline(candidate)
        if clipped:
            return clipped
    return ""


def _packet_public_direct_meaning(packet: Mapping[str, Any]) -> str:
    override = _packet_copy_override(packet)
    if override.get("teaser"):
        return str(override.get("teaser") or "").strip()
    return str(packet.get("direct_meaning") or "").strip()


def _normalize_projection_node(
    node: Mapping[str, Any],
    evidence_map: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    node_id = str(node.get("node_id") or "").strip()
    if not node_id:
        return {}
    summary = _clean_projection_text(str(node.get("summary") or "").strip())
    title = _clean_projection_title(str(node.get("title") or "").strip()) or "Meaning"
    layers = _normalize_layer_vector(node)
    evidence_ids = _node_evidence_ids(node, evidence_map)
    evidence = _normalize_evidence_entries(evidence_ids=evidence_ids, evidence_map=evidence_map)
    domain = str(node.get("domain") or "").strip() or "general"
    primary_layer = str(node.get("primary_layer") or "").strip()
    if not primary_layer and layers:
        primary_layer = str(layers[0].get("layer") or "").strip()
    return {
        **dict(node),
        "node_id": node_id,
        "headline": title,
        "summary": summary,
        "domain": domain,
        "primary_layer": primary_layer,
        "layers": layers,
        "evidence_ids": evidence_ids,
        "evidence": evidence,
    }


def _normalize_layer_vector(node: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_layers = node.get("layers") if isinstance(node.get("layers"), Sequence) else []
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in raw_layers:
        if not isinstance(entry, Mapping):
            continue
        layer = str(entry.get("layer") or "").strip()
        if not layer or layer in seen:
            continue
        seen.add(layer)
        out.append(
            {
                "layer": layer,
                "weight": max(0.0, min(1.0, _safe_float(entry.get("weight"), 0.0))),
            }
        )
    if not out:
        primary = str(node.get("primary_layer") or "").strip()
        if primary:
            out.append({"layer": primary, "weight": 1.0})
    out.sort(key=lambda item: -_safe_float(item.get("weight"), 0.0))
    return out[:3]


def _normalize_evidence_entries(
    *,
    evidence_ids: Sequence[str],
    evidence_map: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for evidence_id in evidence_ids:
        entry = evidence_map.get(str(evidence_id))
        if not isinstance(entry, Mapping):
            continue
        text = _evidence_text(entry)
        out.append(
            {
                "evidence_id": str(evidence_id),
                "kind": str(entry.get("kind") or "").strip(),
                "source_family": str(entry.get("source_family") or "").strip(),
                "source_path": str(entry.get("source_path") or "").strip(),
                "weight": _safe_float(entry.get("weight"), 0.0),
                "text": text,
            }
        )
    return out


def _node_priority(node: Mapping[str, Any]) -> float:
    projection_hints = node.get("projection_hints") if isinstance(node.get("projection_hints"), Mapping) else {}
    return float(projection_hints.get("priority") or 0.0)


def _top_layer_weight(node: Mapping[str, Any]) -> float:
    layers = node.get("layers") if isinstance(node.get("layers"), Sequence) else []
    weights: list[float] = []
    for layer in layers:
        if not isinstance(layer, Mapping):
            continue
        weights.append(float(layer.get("weight") or 0.0))
    return max(weights) if weights else 0.0


def _node_surfaces(node: Mapping[str, Any]) -> list[str]:
    projection_hints = node.get("projection_hints") if isinstance(node.get("projection_hints"), Mapping) else {}
    surfaces = projection_hints.get("surfaces") if isinstance(projection_hints.get("surfaces"), Sequence) else []
    return [str(surface).strip() for surface in surfaces if str(surface).strip()]


def _pick_nodes(
    nodes: Sequence[Mapping[str, Any]],
    *,
    preferred_surfaces: Sequence[str],
    limit: int,
    enforce_domain_diversity: bool = False,
    max_same_domain: int | None = None,
    max_same_layer: int | None = None,
    max_shadow_nodes: int | None = None,
    profile_kind: str = "",
    selection_debug_branch: MutableMapping[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    preferred = []
    fallback = []
    preferred_set = {str(surface).strip() for surface in preferred_surfaces if str(surface).strip()}
    for node in nodes:
        node_id = str(node.get("node_id") or "").strip()
        if not node_id:
            continue
        if preferred_set.intersection(_node_surfaces(node)):
            preferred.append(dict(node))
        else:
            fallback.append(dict(node))
    ordered = [*preferred, *fallback]
    target = max(0, limit)
    if target <= 0:
        return []

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    seen_domains: set[str] = set()
    seen_fingerprints: set[str] = set()
    selected_summary_features: list[dict[str, Any]] = []
    selected_openings: dict[str, int] = {}
    selected_domain_counts: dict[str, int] = {}
    selected_layer_counts: dict[str, int] = {}
    selected_shadow_count = 0
    soft_duplicate_count = 0
    selected_layer_penalty_totals: dict[str, float] = {
        "shadow_penalty_sum": 0.0,
        "layer_penalty_sum": 0.0,
    }

    stages: list[dict[str, bool]] = [
        {"enforce_domain": enforce_domain_diversity, "allow_soft_duplicates": False},
        {"enforce_domain": False, "allow_soft_duplicates": False},
        {"enforce_domain": False, "allow_soft_duplicates": True},
    ]
    for stage_index, stage in enumerate(stages):
        while len(selected) < target:
            candidate, used_soft_duplicate, chosen_penalties = _select_best_candidate(
                ordered=ordered,
                selected_ids=selected_ids,
                seen_domains=seen_domains,
                seen_fingerprints=seen_fingerprints,
                selected_summary_features=selected_summary_features,
                selected_openings=selected_openings,
                selected_domain_counts=selected_domain_counts,
                selected_layer_counts=selected_layer_counts,
                enforce_domain=stage["enforce_domain"],
                allow_soft_duplicates=stage["allow_soft_duplicates"],
                can_use_soft_duplicate=soft_duplicate_count < _POLICY_MAX_SOFT_DUPLICATES,
                max_same_domain=max_same_domain,
                max_same_layer=max_same_layer,
                max_shadow_nodes=max_shadow_nodes,
                selected_shadow_count=selected_shadow_count,
                selected_layer_penalty_totals=selected_layer_penalty_totals,
                profile_kind=profile_kind,
                selection_debug_branch=selection_debug_branch,
                stage_index=stage_index,
            )
            if not isinstance(candidate, Mapping):
                _inc_reason_counter(selection_debug_branch, f"no_candidate_stage_{stage_index}")
                break
            node = dict(candidate)
            node_id = str(node.get("node_id") or "").strip()
            if not node_id:
                break
            selected.append(node)
            selected_ids.add(node_id)
            fingerprint = _node_dedupe_fingerprint(node)
            if fingerprint:
                seen_fingerprints.add(fingerprint)
            domain = str(node.get("domain") or "").strip()
            if domain:
                seen_domains.add(domain)
                selected_domain_counts[domain] = selected_domain_counts.get(domain, 0) + 1
            primary_layer = _primary_layer(node)
            if primary_layer:
                selected_layer_counts[primary_layer] = selected_layer_counts.get(primary_layer, 0) + 1
                if primary_layer == "shadow":
                    selected_shadow_count += 1
            features = _summary_features(node=node)
            selected_summary_features.append(features)
            opening = str(features.get("opening") or "").strip()
            if opening:
                selected_openings[opening] = selected_openings.get(opening, 0) + 1
            if isinstance(chosen_penalties, Mapping):
                selected_layer_penalty_totals["shadow_penalty_sum"] += float(chosen_penalties.get("shadow_penalty") or 0.0)
                selected_layer_penalty_totals["layer_penalty_sum"] += float(chosen_penalties.get("layer_penalty") or 0.0)
            if used_soft_duplicate:
                soft_duplicate_count += 1
            if stage_index > 0 and selection_debug_branch is not None:
                selection_debug_branch["underfill_relaxation_used"] = True
            if selection_debug_branch is not None:
                selected_node_ids = selection_debug_branch.get("selected_node_ids")
                if not isinstance(selected_node_ids, list):
                    selected_node_ids = []
                    selection_debug_branch["selected_node_ids"] = selected_node_ids
                selected_node_ids.append(node_id)
                _inc_reason_counter(selection_debug_branch, "accepted")
        if len(selected) >= target:
            break
    return selected[:target]


def _select_best_candidate(
    *,
    ordered: Sequence[Mapping[str, Any]],
    selected_ids: set[str],
    seen_domains: set[str],
    seen_fingerprints: set[str],
    selected_summary_features: Sequence[Mapping[str, Any]],
    selected_openings: Mapping[str, int],
    selected_domain_counts: Mapping[str, int],
    selected_layer_counts: Mapping[str, int],
    enforce_domain: bool,
    allow_soft_duplicates: bool,
    can_use_soft_duplicate: bool,
    max_same_domain: int | None,
    max_same_layer: int | None,
    max_shadow_nodes: int | None,
    selected_shadow_count: int,
    selected_layer_penalty_totals: Mapping[str, float],
    profile_kind: str,
    selection_debug_branch: MutableMapping[str, Any] | None,
    stage_index: int,
) -> tuple[dict[str, Any] | None, bool, dict[str, float] | None]:
    candidates: list[tuple[tuple[Any, ...], dict[str, Any], bool]] = []
    for raw_node in ordered:
        node = dict(raw_node)
        node_id = str(node.get("node_id") or "").strip()
        if not node_id:
            _inc_reason_counter(selection_debug_branch, "missing_node_id")
            continue
        if node_id in selected_ids:
            _inc_reason_counter(selection_debug_branch, "already_selected_id")
            continue

        fingerprint = _node_dedupe_fingerprint(node)
        if fingerprint and fingerprint in seen_fingerprints:
            _inc_reason_counter(selection_debug_branch, "duplicate_fingerprint")
            _inc_debug_metric(selection_debug_branch, "duplicate_fingerprint_hits")
            continue

        domain = str(node.get("domain") or "").strip()
        if enforce_domain and domain and domain in seen_domains:
            _inc_reason_counter(selection_debug_branch, "domain_enforced_skip")
            continue
        candidate_layer = _primary_layer(node)
        if (
            str(profile_kind or "").strip().lower() == "v8"
            and candidate_layer == "shadow"
            and max_shadow_nodes is not None
            and max_shadow_nodes >= 0
            and selected_shadow_count >= max_shadow_nodes
        ):
            _inc_reason_counter(selection_debug_branch, "shadow_cap_skip")
            continue

        features = _summary_features(node=node)
        similarity = _max_summary_similarity(
            features,
            selected_summary_features,
        )
        if similarity > _POLICY_SOFT_DUPLICATE_THRESHOLD:
            _inc_debug_metric(selection_debug_branch, "near_duplicate_hits")
        is_soft_duplicate = similarity > _POLICY_SOFT_DUPLICATE_THRESHOLD and can_use_soft_duplicate
        similarity_penalty = _similarity_penalty(
            similarity=similarity,
            allow_soft_duplicates=allow_soft_duplicates,
            can_use_soft_duplicate=can_use_soft_duplicate,
        )

        base_score = _policy_score_node(node, seen_domains=seen_domains)
        domain_penalty = _domain_soft_cap_penalty(
            domain=domain,
            domain_counts=selected_domain_counts,
            max_same_domain=max_same_domain,
            profile_kind=profile_kind,
        )
        layer_cap_penalty = _layer_soft_cap_penalty(
            layer=candidate_layer,
            layer_counts=selected_layer_counts,
            max_same_layer=max_same_layer,
            profile_kind=profile_kind,
        )
        shadow_penalty = _v8_shadow_penalty(node=node, profile_kind=profile_kind)
        if shadow_penalty > 0.0:
            shadow_penalty *= _POLICY_V8_SHADOW_PENALTY_SCALE
            shadow_penalty = _apply_shadow_penalty_share_guardrail(
                shadow_penalty=shadow_penalty,
                layer_cap_penalty=layer_cap_penalty,
                selected_layer_penalty_totals=selected_layer_penalty_totals,
                share_cap=_POLICY_V8_SHADOW_PENALTY_SHARE_CAP,
            )
        layer_penalty = layer_cap_penalty + shadow_penalty
        repetition_penalty = _repetition_penalty(
            features=features,
            selected_features=selected_summary_features,
            selected_openings=selected_openings,
        )
        if domain_penalty > 0.0:
            _inc_debug_metric(selection_debug_branch, "domain_cap_hits")
        if layer_cap_penalty > 0.0:
            _inc_debug_metric(selection_debug_branch, "layer_cap_hits")

        final_score = max(
            0.0,
            base_score
            - similarity_penalty
            - domain_penalty
            - layer_penalty
            - repetition_penalty,
        )
        if selection_debug_branch is not None:
            decomposition = selection_debug_branch.get("candidate_score_decomposition")
            if not isinstance(decomposition, list):
                decomposition = []
                selection_debug_branch["candidate_score_decomposition"] = decomposition
            decomposition.append(
                {
                    "stage_index": stage_index,
                    "node_id": node_id,
                    "base_score": round(base_score, 6),
                    "similarity_penalty": round(similarity_penalty, 6),
                    "domain_penalty": round(domain_penalty, 6),
                    "layer_penalty": round(layer_penalty, 6),
                    "repetition_penalty": round(repetition_penalty, 6),
                    "final_score": round(final_score, 6),
                }
            )
        _inc_reason_counter(selection_debug_branch, "scored_candidate")

        sort_key = (
            1 if is_soft_duplicate else 0,
            -final_score,
            -_node_priority(node),
            -_top_layer_weight(node),
            -_node_evidence_count(node),
            node_id,
        )
        node["__selection_penalties"] = {
            "layer_penalty": layer_penalty,
            "shadow_penalty": shadow_penalty,
        }
        candidates.append((sort_key, node, is_soft_duplicate))

    if not candidates:
        return None, False, None
    candidates.sort(key=lambda item: item[0])
    _, chosen, chosen_soft_duplicate = candidates[0]
    penalties = chosen.get("__selection_penalties") if isinstance(chosen.get("__selection_penalties"), Mapping) else {}
    chosen.pop("__selection_penalties", None)
    return chosen, chosen_soft_duplicate, {
        "layer_penalty": float(penalties.get("layer_penalty") or 0.0),
        "shadow_penalty": float(penalties.get("shadow_penalty") or 0.0),
    }


def _policy_score_node(node: Mapping[str, Any], *, seen_domains: set[str]) -> float:
    importance = _node_priority(node)
    emotional_weight = _top_layer_weight(node)
    domain_bonus = _domain_diversity_bonus(str(node.get("domain") or "").strip(), seen_domains=seen_domains)
    layer_bonus = _policy_layer_bonus(str(node.get("primary_layer") or "").strip())
    return round(
        (0.52 * importance)
        + (0.28 * emotional_weight)
        + (0.12 * domain_bonus)
        + (0.08 * layer_bonus),
        6,
    )


def _domain_diversity_bonus(domain: str, *, seen_domains: set[str]) -> float:
    normalized = str(domain or "").strip()
    if not normalized:
        return 0.5
    return 1.0 if normalized not in seen_domains else 0.35


def _policy_layer_bonus(primary_layer: str) -> float:
    return _POLICY_LAYER_BONUS.get(str(primary_layer or "").strip().lower(), 0.3)


def _node_dedupe_fingerprint(node: Mapping[str, Any]) -> str:
    return str(node.get("dedupe_fingerprint") or "").strip()


def _node_id(node: Mapping[str, Any]) -> str:
    return str(node.get("node_id") or "").strip()


def _node_cluster_id(node: Mapping[str, Any]) -> str:
    """Return the cluster id this projection node was sourced from, if any.

    Projection nodes built via :func:`_packet_projection_nodes` embed their
    upstream packet under ``natal_promise_packet``. ``_cluster_main_packet_copy``
    (and the support/detail copies) annotate that packet's
    ``cluster_context.cluster_id`` whenever the packet was pulled out of a
    cluster. Nodes that never went through the cluster path simply return
    an empty string.
    """

    packet = node.get("natal_promise_packet")
    if isinstance(packet, Mapping):
        context = packet.get("cluster_context")
        if isinstance(context, Mapping):
            cluster_id = str(context.get("cluster_id") or "").strip()
            if cluster_id:
                return cluster_id
    return ""


def _node_cluster_domain_family(node: Mapping[str, Any]) -> str:
    """Derive the domain family (identity / mind / career / relationship / …) for a node.

    Prefers the cluster-level ``domain_family`` annotation when present and
    falls back to the cluster id prefix (``identity_*`` / ``mind_*`` / …) so
    that detail-tier nodes whose cluster_context is missing the explicit
    family still get classified correctly. Final fallback is the packet's
    own ``domain`` field, then the projection node ``domain``.
    """

    packet = node.get("natal_promise_packet")
    if isinstance(packet, Mapping):
        context = packet.get("cluster_context")
        if isinstance(context, Mapping):
            family = str(context.get("domain_family") or "").strip().lower()
            if family:
                return family
            cluster_id = str(context.get("cluster_id") or "").strip().lower()
            if cluster_id:
                prefix = cluster_id.split("_", 1)[0]
                if prefix:
                    return prefix
        packet_domain = str(packet.get("domain") or "").strip().lower()
        if packet_domain:
            return packet_domain
    return str(node.get("domain") or "").strip().lower()


def _is_identity_family_node(node: Mapping[str, Any]) -> bool:
    family = _node_cluster_domain_family(node)
    if family == "identity":
        return True
    cluster_id = _node_cluster_id(node).lower()
    return cluster_id.startswith("identity_") if cluster_id else False


def _identity_axis_subtype_rank(node: Mapping[str, Any]) -> int:
    """Rank identity-family nodes by subtype preference for the identity_axis slot.

    Lower is better.

    * ``identity_identity_like_*`` — pure identity subtype, highest preference.
    * ``identity_gift_like_*`` — gift subtype.
    * ``identity_wound_like_*`` — wound subtype (already serves hero / contradiction-core
      use cases, so it sits last among identity-family).
    * Any other identity-family cluster id.
    """

    cluster_id = _node_cluster_id(node).lower()
    if cluster_id.startswith("identity_identity_like_"):
        return 0
    if cluster_id.startswith("identity_gift_like_"):
        return 1
    if cluster_id.startswith("identity_wound_like_"):
        return 3
    if cluster_id.startswith("identity_"):
        return 2
    return 4


def _pick_identity_axis_node(
    *,
    pool: Sequence[Mapping[str, Any]],
    hero_cluster_id: str,
) -> Dict[str, Any]:
    """Choose the v8 identity_axis node, preferring identity-family clusters.

    Preference order:

    1. ``identity_identity_like_*`` clusters (pure identity subtype) — including
       detail tier. Excludes the cluster already consumed by ``hero``.
    2. Other identity-family clusters (gift / wound / generic ``identity_*``),
       again excluding the hero cluster.
    3. ``None`` — caller must fall back to the legacy non-identity selector.

    Within identity-family, candidates are ordered by (subtype rank,
    projection priority desc, recognition/mechanism layer preference).
    Detail-tier clusters are deliberately kept eligible because the bug
    being fixed is that Adana's only identity-family cluster lives in detail
    and was being skipped.
    """

    if not pool:
        return {}

    hero_cluster = hero_cluster_id.strip().lower()
    candidates: list[tuple[int, int, float, int, Dict[str, Any]]] = []
    layer_pref = {"recognition": 0, "mechanism": 1}
    for index, raw in enumerate(pool):
        if not _is_identity_family_node(raw):
            continue
        node_cluster = _node_cluster_id(raw).lower()
        if hero_cluster and node_cluster and node_cluster == hero_cluster:
            continue
        subtype_rank = _identity_axis_subtype_rank(raw)
        primary = str(raw.get("primary_layer") or "").strip().lower()
        layer_rank = layer_pref.get(primary, 2)
        priority = _safe_float(
            (raw.get("projection_hints") or {}).get("priority"),
            _safe_float(raw.get("strength"), 0.0),
        )
        candidates.append((subtype_rank, layer_rank, -priority, index, dict(raw)))

    if not candidates:
        return {}

    candidates.sort(key=lambda item: (item[0], item[1], item[2], item[3]))
    return candidates[0][4]


def _node_evidence_count(node: Mapping[str, Any]) -> int:
    raw_ids = node.get("evidence_ids")
    evidence_ids = (
        raw_ids
        if isinstance(raw_ids, Sequence) and not isinstance(raw_ids, (str, bytes))
        else []
    )
    out: set[str] = set()
    for evidence_id in evidence_ids:
        value = str(evidence_id).strip()
        if value:
            out.add(value)
    return len(out)


def _summary_token_set(text: str) -> set[str]:
    return set(_summary_tokens(text))


def _summary_tokens(text: str) -> list[str]:
    normalized = _normalize_similarity_text(text)
    return [token for token in normalized.split(" ") if token and token not in _SIMILARITY_STOPWORDS]


def _summary_opening(tokens: Sequence[str]) -> str:
    return " ".join([token for token in tokens[:3] if token]).strip()


def _summary_ngrams(tokens: Sequence[str], n: int = 2) -> set[str]:
    if n <= 1:
        return set(tokens)
    out: set[str] = set()
    for idx in range(0, max(0, len(tokens) - n + 1)):
        gram = " ".join(tokens[idx : idx + n]).strip()
        if gram:
            out.add(gram)
    return out


def _summary_features(*, node: Mapping[str, Any]) -> dict[str, Any]:
    summary = str(node.get("summary") or "").strip()
    tokens = _summary_tokens(summary)
    token_set = set(tokens)
    bigrams = _summary_ngrams(tokens, n=2)
    domain = str(node.get("domain") or "").strip().lower()
    layers = {
        str(layer.get("layer") or "").strip().lower()
        for layer in (node.get("layers") if isinstance(node.get("layers"), Sequence) else [])
        if isinstance(layer, Mapping) and str(layer.get("layer") or "").strip()
    }
    primary = _primary_layer(node)
    if primary:
        layers.add(primary)
    return {
        "tokens": token_set,
        "bigrams": bigrams,
        "opening": _summary_opening(tokens),
        "domain": domain,
        "layers": layers,
    }


def _normalize_similarity_text(value: str) -> str:
    clean = str(value or "").lower().strip()
    clean = clean.replace("ı", "i").replace("İ", "i")
    clean = clean.replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    clean = clean.replace("&", " ve ")
    clean = re.sub(r"[^a-z0-9\s]", " ", clean)
    clean = re.sub(r"\b(\d+)\s*ev\b", r"\1 ev", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _max_summary_similarity(
    features: Mapping[str, Any],
    selected_features: Sequence[Mapping[str, Any]],
) -> float:
    candidate_tokens = features.get("tokens") if isinstance(features.get("tokens"), set) else set()
    candidate_bigrams = features.get("bigrams") if isinstance(features.get("bigrams"), set) else set()
    candidate_domain = str(features.get("domain") or "").strip()
    candidate_layers = features.get("layers") if isinstance(features.get("layers"), set) else set()
    if not candidate_tokens or not selected_features:
        return 0.0
    return max(
        (
            _combined_similarity(
                candidate_tokens=candidate_tokens,
                candidate_bigrams=candidate_bigrams,
                candidate_domain=candidate_domain,
                candidate_layers=candidate_layers,
                other=other,
            )
            for other in selected_features
            if isinstance(other, Mapping)
        ),
        default=0.0,
    )


def _combined_similarity(
    *,
    candidate_tokens: set[str],
    candidate_bigrams: set[str],
    candidate_domain: str,
    candidate_layers: set[str],
    other: Mapping[str, Any],
) -> float:
    other_tokens = other.get("tokens") if isinstance(other.get("tokens"), set) else set()
    if not other_tokens:
        return 0.0
    lexical = _jaccard_similarity(candidate_tokens, other_tokens)
    other_bigrams = other.get("bigrams") if isinstance(other.get("bigrams"), set) else set()
    bigram_sim = _jaccard_similarity(candidate_bigrams, other_bigrams) if candidate_bigrams and other_bigrams else 0.0
    base = (0.74 * lexical) + (0.2 * bigram_sim)
    other_domain = str(other.get("domain") or "").strip()
    if candidate_domain and other_domain and candidate_domain == other_domain:
        base += 0.04
    other_layers = other.get("layers") if isinstance(other.get("layers"), set) else set()
    if candidate_layers and other_layers and candidate_layers.intersection(other_layers):
        base += 0.04
    return min(1.0, base)


def _similarity_penalty(
    *,
    similarity: float,
    allow_soft_duplicates: bool,
    can_use_soft_duplicate: bool,
) -> float:
    if similarity <= 0.0:
        return 0.0
    base_penalty = similarity * _POLICY_SIMILARITY_PENALTY_WEIGHT
    if similarity <= _POLICY_SOFT_DUPLICATE_THRESHOLD:
        return base_penalty
    if allow_soft_duplicates and can_use_soft_duplicate:
        return base_penalty + _POLICY_SOFT_DUPLICATE_PENALTY
    return base_penalty + _POLICY_STRICT_DUPLICATE_PENALTY


def _domain_soft_cap_penalty(
    *,
    domain: str,
    domain_counts: Mapping[str, int],
    max_same_domain: int | None,
    profile_kind: str,
) -> float:
    if not domain or max_same_domain is None or max_same_domain <= 0:
        return 0.0
    current_count = int(domain_counts.get(domain, 0))
    if current_count < max_same_domain:
        return 0.0
    overflow = (current_count - max_same_domain) + 1
    penalty = _POLICY_DOMAIN_SOFT_CAP_PENALTY * overflow
    if str(profile_kind or "").strip().lower() == "v8":
        penalty += 0.04
    return penalty


def _layer_soft_cap_penalty(
    *,
    layer: str,
    layer_counts: Mapping[str, int],
    max_same_layer: int | None,
    profile_kind: str,
) -> float:
    normalized = str(layer or "").strip().lower()
    if not normalized or max_same_layer is None or max_same_layer <= 0:
        return 0.0
    current_count = int(layer_counts.get(normalized, 0))
    if current_count < max_same_layer:
        return 0.0
    overflow = (current_count - max_same_layer) + 1
    penalty = _POLICY_LAYER_SOFT_CAP_PENALTY * overflow
    if str(profile_kind or "").strip().lower() == "v8" and normalized == "shadow":
        penalty += 0.03
    return penalty


def _repetition_penalty(
    *,
    features: Mapping[str, Any],
    selected_features: Sequence[Mapping[str, Any]],
    selected_openings: Mapping[str, int],
) -> float:
    penalty = 0.0
    opening = str(features.get("opening") or "").strip()
    opening_count = int(selected_openings.get(opening, 0)) if opening else 0
    if opening_count > 0:
        penalty += _POLICY_OPENING_REPEAT_PENALTY * opening_count

    candidate_bigrams = features.get("bigrams") if isinstance(features.get("bigrams"), set) else set()
    if candidate_bigrams:
        max_overlap = max(
            (
                _phrase_overlap_ratio(
                    candidate_bigrams=candidate_bigrams,
                    other_bigrams=other.get("bigrams") if isinstance(other.get("bigrams"), set) else set(),
                )
                for other in selected_features
                if isinstance(other, Mapping)
            ),
            default=0.0,
        )
        if max_overlap > _POLICY_PHRASE_REPEAT_THRESHOLD:
            penalty += _POLICY_PHRASE_REPEAT_PENALTY * max_overlap
    return penalty


def _apply_shadow_penalty_share_guardrail(
    *,
    shadow_penalty: float,
    layer_cap_penalty: float,
    selected_layer_penalty_totals: Mapping[str, float],
    share_cap: float,
) -> float:
    shadow_value = max(0.0, float(shadow_penalty or 0.0))
    layer_value = max(0.0, float(layer_cap_penalty or 0.0))
    cap = max(0.0, min(0.95, float(share_cap or 0.0)))
    min_retained_shadow = shadow_value * _POLICY_V8_SHADOW_PENALTY_MIN_RETENTION
    if shadow_value <= 0.0:
        return 0.0
    if cap <= 0.0:
        return min_retained_shadow
    if cap >= 0.95:
        return shadow_value

    existing_shadow = max(0.0, float(selected_layer_penalty_totals.get("shadow_penalty_sum") or 0.0))
    existing_layer = max(0.0, float(selected_layer_penalty_totals.get("layer_penalty_sum") or 0.0))
    projected_layer_without_shadow = existing_layer + layer_value
    numerator = (cap * projected_layer_without_shadow) - existing_shadow
    denominator = max(1e-9, (1.0 - cap))
    allowed_shadow = max(0.0, numerator / denominator)
    guarded_shadow = min(shadow_value, allowed_shadow)
    return min(shadow_value, max(min_retained_shadow, guarded_shadow))


def _phrase_overlap_ratio(*, candidate_bigrams: set[str], other_bigrams: set[str]) -> float:
    if not candidate_bigrams or not other_bigrams:
        return 0.0
    return len(candidate_bigrams.intersection(other_bigrams)) / float(len(candidate_bigrams))


def _v8_shadow_penalty(*, node: Mapping[str, Any], profile_kind: str) -> float:
    if str(profile_kind or "").strip().lower() != "v8":
        return 0.0
    if _primary_layer(node) != "shadow":
        return 0.0
    return _POLICY_V8_SHADOW_PENALTY * _top_layer_weight(node)


def _selection_pool_for_v8(
    *,
    all_nodes: Sequence[Mapping[str, Any]],
    used_slot_ids: set[str],
    allow_cross_slot_duplicates: bool,
) -> list[dict[str, Any]]:
    unique_pool = [
        dict(node)
        for node in all_nodes
        if _node_id(node) and _node_id(node) not in used_slot_ids
    ]
    if unique_pool or not allow_cross_slot_duplicates:
        return unique_pool
    return [dict(node) for node in all_nodes if _node_id(node)]


def _hero_tuned_v8_pool(nodes: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    tuned: list[dict[str, Any]] = []
    for raw_node in nodes:
        node = dict(raw_node)
        projection_hints = (
            dict(node.get("projection_hints"))
            if isinstance(node.get("projection_hints"), Mapping)
            else {}
        )
        projection_hints["priority"] = _node_priority(node) + _v8_hero_bonus(node)
        node["projection_hints"] = projection_hints
        tuned.append(node)
    return tuned


def _v8_hero_bonus(node: Mapping[str, Any]) -> float:
    packet = _packet_from_node(node)
    if not packet:
        domain = str(node.get("domain") or "").strip().lower()
        if domain in {"identity", "mind"}:
            return 0.08
        if domain in {"relationships", "relationship"}:
            return -0.06
        return 0.0
    promise_type = str(packet.get("promise_type") or "").strip()
    domain = str(packet.get("domain") or "").strip()
    anchors = " ".join(str(item).strip() for item in (packet.get("technical_anchors") or []) if str(item).strip())
    bonus = 0.0
    if promise_type in {"mind_identity", "mind_style", "behavior_reflex"}:
        bonus += 0.22
    elif promise_type == "career_signature":
        bonus += 0.12
    elif promise_type in {"love_style", "need"}:
        bonus -= 0.16
    if domain in {"mind", "identity", "behavior_reflex"}:
        bonus += 0.18
    elif domain in {"career", "visibility", "creativity"}:
        bonus += 0.08
    elif domain in {"relationship", "love", "emotional_depth"}:
        bonus -= 0.12
    if any(token in anchors for token in ("Yükselen", "Asc", "1. ev", "MC", "Satürn", "Uranüs")):
        bonus += 0.1
    if "Uranüs" in anchors:
        bonus += 0.06
    return bonus


def _top_up_v8_slots(
    *,
    selected_nodes: list[dict[str, Any]],
    all_nodes: Sequence[Mapping[str, Any]],
    used_slot_ids: set[str],
    target: int,
    allow_cross_slot_duplicates: bool,
    blocked_fingerprints: set[str] | None = None,
) -> None:
    if len(selected_nodes) >= target:
        return
    local_ids = {_node_id(node) for node in selected_nodes if _node_id(node)}
    blocked_fps = {
        fingerprint
        for fingerprint in (blocked_fingerprints or set())
        if fingerprint
    }
    selected_fps = {
        _node_dedupe_fingerprint(node)
        for node in selected_nodes
        if _node_dedupe_fingerprint(node)
    }
    selected_fps.update(blocked_fps)

    def append_from_pool(*, allow_reused_ids: bool, enforce_fingerprint_guard: bool) -> None:
        for node in all_nodes:
            if len(selected_nodes) >= target:
                return
            node_id = _node_id(node)
            if not node_id or node_id in local_ids:
                continue
            if not allow_reused_ids and node_id in used_slot_ids:
                continue
            fingerprint = _node_dedupe_fingerprint(node)
            if enforce_fingerprint_guard and fingerprint and fingerprint in selected_fps:
                continue
            selected_nodes.append(dict(node))
            local_ids.add(node_id)
            if fingerprint:
                selected_fps.add(fingerprint)

    append_from_pool(allow_reused_ids=False, enforce_fingerprint_guard=True)
    if len(selected_nodes) < target and allow_cross_slot_duplicates:
        append_from_pool(allow_reused_ids=True, enforce_fingerprint_guard=True)
    if len(selected_nodes) < target:
        append_from_pool(
            allow_reused_ids=allow_cross_slot_duplicates,
            enforce_fingerprint_guard=False,
        )


def _enforce_v8_shadow_floor_and_cap(
    *,
    insight_nodes: list[dict[str, Any]],
    differentiator_nodes: list[dict[str, Any]],
    all_nodes: Sequence[Mapping[str, Any]],
    reserved_slot_ids: set[str],
    allow_cross_slot_duplicates: bool,
    min_shadow_nodes: int,
    max_shadow_nodes: int,
) -> None:
    if max_shadow_nodes < 0:
        return
    min_shadow_nodes = max(0, min_shadow_nodes)
    if min_shadow_nodes > max_shadow_nodes:
        min_shadow_nodes = max_shadow_nodes

    selected_nodes = [*insight_nodes, *differentiator_nodes]
    if not selected_nodes:
        return

    def selected_ids(*, exclude: tuple[str, int] | None = None) -> set[str]:
        ids = {node_id for node_id in reserved_slot_ids if node_id}
        for slot_name, slot_nodes in (("insight", insight_nodes), ("differentiator", differentiator_nodes)):
            for idx, node in enumerate(slot_nodes):
                if exclude is not None and exclude == (slot_name, idx):
                    continue
                node_id = _node_id(node)
                if node_id:
                    ids.add(node_id)
        return ids

    def selected_fingerprints(*, exclude: tuple[str, int] | None = None) -> set[str]:
        out: set[str] = set()
        for slot_name, slot_nodes in (("insight", insight_nodes), ("differentiator", differentiator_nodes)):
            for idx, node in enumerate(slot_nodes):
                if exclude is not None and exclude == (slot_name, idx):
                    continue
                fingerprint = _node_dedupe_fingerprint(node)
                if fingerprint:
                    out.add(fingerprint)
        return out

    def shadow_count() -> int:
        return sum(
            1
            for node in [*insight_nodes, *differentiator_nodes]
            if isinstance(node, Mapping) and _primary_layer(node) == "shadow"
        )

    def slot_candidates(
        *,
        require_shadow: bool | None,
        prefer_differentiator: bool,
    ) -> list[tuple[tuple[Any, ...], str, int, dict[str, Any]]]:
        candidates: list[tuple[tuple[Any, ...], str, int, dict[str, Any]]] = []
        for slot_name, slot_nodes in (("differentiator", differentiator_nodes), ("insight", insight_nodes)):
            slot_bias = 0 if (prefer_differentiator and slot_name == "differentiator") else 1
            for idx, raw_node in enumerate(slot_nodes):
                node = dict(raw_node)
                primary_layer = _primary_layer(node)
                if require_shadow is True and primary_layer != "shadow":
                    continue
                if require_shadow is False and primary_layer == "shadow":
                    continue
                key = (
                    slot_bias,
                    _policy_score_node(node, seen_domains=set()),
                    _node_priority(node),
                    _top_layer_weight(node),
                    _node_evidence_count(node),
                    _node_id(node),
                )
                candidates.append((key, slot_name, idx, node))
        candidates.sort(key=lambda item: item[0])
        return candidates

    def best_candidate(
        *,
        primary_layer: str | None,
        exclude_primary_layer: str | None,
        blocked_ids: set[str],
        blocked_fingerprints: set[str],
        allow_reused_ids: bool,
        allow_duplicate_fingerprints: bool,
    ) -> dict[str, Any] | None:
        scored: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        for raw_node in all_nodes:
            node = dict(raw_node)
            node_id = _node_id(node)
            if not node_id:
                continue
            if primary_layer is not None and _primary_layer(node) != primary_layer:
                continue
            if exclude_primary_layer is not None and _primary_layer(node) == exclude_primary_layer:
                continue
            if not allow_reused_ids and node_id in blocked_ids:
                continue
            fingerprint = _node_dedupe_fingerprint(node)
            if not allow_duplicate_fingerprints and fingerprint and fingerprint in blocked_fingerprints:
                continue
            sort_key = (
                -_policy_score_node(node, seen_domains=set()),
                -_node_priority(node),
                -_top_layer_weight(node),
                -_node_evidence_count(node),
                node_id,
            )
            scored.append((sort_key, node))
        if not scored:
            return None
        scored.sort(key=lambda item: item[0])
        return scored[0][1]

    available_shadow_nodes = [
        node for node in all_nodes if isinstance(node, Mapping) and _primary_layer(node) == "shadow" and _node_id(node)
    ]

    if available_shadow_nodes and shadow_count() < min_shadow_nodes:
        replace_candidates = slot_candidates(require_shadow=False, prefer_differentiator=True)
        if replace_candidates:
            _, target_slot, target_idx, _ = replace_candidates[0]
            exclude = (target_slot, target_idx)
            shadow_candidate = (
                best_candidate(
                    primary_layer="shadow",
                    exclude_primary_layer=None,
                    blocked_ids=selected_ids(exclude=exclude),
                    blocked_fingerprints=selected_fingerprints(exclude=exclude),
                    allow_reused_ids=False,
                    allow_duplicate_fingerprints=False,
                )
                or best_candidate(
                    primary_layer="shadow",
                    exclude_primary_layer=None,
                    blocked_ids=selected_ids(exclude=exclude),
                    blocked_fingerprints=selected_fingerprints(exclude=exclude),
                    allow_reused_ids=allow_cross_slot_duplicates,
                    allow_duplicate_fingerprints=False,
                )
                or best_candidate(
                    primary_layer="shadow",
                    exclude_primary_layer=None,
                    blocked_ids=selected_ids(exclude=exclude),
                    blocked_fingerprints=selected_fingerprints(exclude=exclude),
                    allow_reused_ids=allow_cross_slot_duplicates,
                    allow_duplicate_fingerprints=True,
                )
            )
            if shadow_candidate is not None:
                if target_slot == "differentiator":
                    differentiator_nodes[target_idx] = shadow_candidate
                else:
                    insight_nodes[target_idx] = shadow_candidate

    while shadow_count() > max_shadow_nodes:
        replace_candidates = slot_candidates(require_shadow=True, prefer_differentiator=True)
        if not replace_candidates:
            return
        shadow_fingerprint_counts: dict[str, int] = {}
        for node in [*insight_nodes, *differentiator_nodes]:
            if not isinstance(node, Mapping) or _primary_layer(node) != "shadow":
                continue
            fingerprint = _node_dedupe_fingerprint(node)
            if not fingerprint:
                continue
            shadow_fingerprint_counts[fingerprint] = shadow_fingerprint_counts.get(fingerprint, 0) + 1
        replace_candidates.sort(
            key=lambda item: (
                0
                if shadow_fingerprint_counts.get(_node_dedupe_fingerprint(item[3]), 0) > 1
                else 1,
                *item[0],
            )
        )
        _, target_slot, target_idx, _ = replace_candidates[0]
        exclude = (target_slot, target_idx)
        replacement = (
            best_candidate(
                primary_layer=None,
                exclude_primary_layer="shadow",
                blocked_ids=selected_ids(exclude=exclude),
                blocked_fingerprints=selected_fingerprints(exclude=exclude),
                allow_reused_ids=False,
                allow_duplicate_fingerprints=False,
            )
            or best_candidate(
                primary_layer=None,
                exclude_primary_layer="shadow",
                blocked_ids=selected_ids(exclude=exclude),
                blocked_fingerprints=selected_fingerprints(exclude=exclude),
                allow_reused_ids=allow_cross_slot_duplicates,
                allow_duplicate_fingerprints=False,
            )
            or best_candidate(
                primary_layer=None,
                exclude_primary_layer="shadow",
                blocked_ids=selected_ids(exclude=exclude),
                blocked_fingerprints=selected_fingerprints(exclude=exclude),
                allow_reused_ids=allow_cross_slot_duplicates,
                allow_duplicate_fingerprints=True,
            )
        )
        if replacement is None:
            return
        if target_slot == "differentiator":
            differentiator_nodes[target_idx] = replacement
        else:
            insight_nodes[target_idx] = replacement


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _pick_first(nodes: Sequence[Mapping[str, Any]], *, preferred_layers: Sequence[str]) -> Dict[str, Any]:
    preferred_set = {str(layer).strip() for layer in preferred_layers if str(layer).strip()}
    for node in nodes:
        primary = str(node.get("primary_layer") or "").strip()
        if primary in preferred_set:
            return dict(node)
    return {}


def _profile_block_from_node(
    *,
    node: Mapping[str, Any],
    emphasis: str,
    used_block_ids: set[str],
    used_openings: list[str],
    used_bodies: list[str],
) -> Dict[str, Any]:
    node_id = str(node.get("node_id") or "").strip()
    packet = _packet_from_node(node)
    raw_title = str(node.get("headline") or node.get("title") or "").strip() or "Meaning"
    summary = str(node.get("summary") or "").strip()
    family = _family_key(node)
    evidence_entries = node.get("evidence") if isinstance(node.get("evidence"), Sequence) else []
    detail_items = _detail_items(evidence_entries=evidence_entries)
    # Bug 2: guard the headline slot against body-shape long-form paragraphs.
    # When the incoming `node.headline` is a multi-sentence or >120 char
    # string (e.g. a bespoke override accidentally fed body copy into the
    # headline slot), demote it to body content and pull the actual headline
    # from short packet fields (teaser/voice_seeds/lived_scene_short).
    long_form_headline: str | None = None
    if _is_long_form_headline(raw_title):
        long_form_headline = raw_title
    clipped_title = _clip_to_headline(raw_title)
    if clipped_title is None:
        title = _fallback_short_headline(packet=packet, node=node, family=family) or "Meaning"
    elif long_form_headline:
        # Multi-sentence input — prefer a short alternative from packet
        # fields; if none available, fall back to the first-sentence slice
        # so we never emit an empty headline.
        title = (
            _fallback_short_headline(packet=packet, node=node, family=family)
            or clipped_title
        )
    else:
        title = clipped_title
    teaser_seed = _split_sentences(_packet_teaser_seed(packet) if packet else summary, max_sentences=1)
    teaser = editorialize_teaser((teaser_seed[0] if teaser_seed else summary) or title, family)
    teaser = _smart_clip(teaser or _smart_clip(summary or title, 180), 180)
    # If the teaser collapsed onto the headline (e.g. packets where
    # direct_meaning equals the chosen voice_seed), pull an alternate
    # seed so the card surfaces two different sentences.
    if packet and teaser and title and _strings_equal_ish(teaser, title):
        alt = _alternate_teaser_seed(packet=packet, avoid=title)
        if alt:
            teaser = _smart_clip(editorialize_teaser(alt, family) or alt, 180)
    if packet:
        micro_seed = _packet_micro(packet)
        micro = _short_text(micro_seed or _micro_text(summary or title), 120)
    else:
        micro = editorialize_micro(_micro_text(summary or title), family)
        micro = _short_text(micro or _micro_text(summary or title), 120)
    narrative_pattern = _pick_narrative_pattern(node=node, salt=f"block:{emphasis}")
    body = _select_projection_body(
        node=node,
        summary=summary,
        teaser=teaser,
        micro=micro,
        evidence_entries=evidence_entries,
        narrative_pattern=narrative_pattern,
        used_openings=used_openings,
        used_bodies=used_bodies,
    )
    # Bug 2 (continued): when we demoted a long-form headline string, prefer
    # it as the body if the body slot would otherwise be empty/very short.
    if long_form_headline:
        existing_body = (body or "").strip()
        if not existing_body or len(existing_body) < 80:
            body = _smart_clip(long_form_headline, 520)
    evidence_ids = [str(item.get("evidence_id") or "").strip() for item in detail_items if str(item.get("evidence_id") or "").strip()]
    block_id = _stable_block_id(
        node_id=node_id,
        domain=str(node.get("domain") or "").strip(),
        primary_layer=str(node.get("primary_layer") or "").strip(),
        used_ids=used_block_ids,
    )
    # Final-pass Turkish localization: catch any raw English aspect names
    # or contradiction labels that survived the packet/template pipeline.
    title = _localize_public_copy_tr(title)
    teaser = _localize_public_copy_tr(teaser)
    body = _localize_public_copy_tr(body)
    micro = _localize_public_copy_tr(micro)
    # Adana §8 polish backstop: strip chip-format `·` and translate English
    # internal labels that survived the bespoke-override + localization
    # layers. Idempotent / no-op on already-natural strings.
    teaser = _naturalize_chip_prose(teaser)
    body = _naturalize_chip_prose(body)
    micro = _naturalize_chip_prose(micro)
    return {
        "id": block_id,
        "headline": title,
        "teaser": teaser,
        "body": body,
        "micro": micro,
        "family": family,
        "emphasis": emphasis,
        "origin": "meaning_graph_v1_1_projection",
        "chips": _chips(node),
        "detail_items": detail_items,
        "node_id": node_id,
        "evidence_ids": evidence_ids,
        "trace": {
            "node_id": node_id,
            "evidence_ids": evidence_ids,
        },
    }


def _select_projection_body(
    *,
    node: Mapping[str, Any],
    summary: str,
    teaser: str,
    micro: str,
    evidence_entries: Sequence[Mapping[str, Any]],
    narrative_pattern: str,
    used_openings: list[str],
    used_bodies: list[str],
) -> str:
    packet = _packet_from_node(node)
    if packet:
        best_body = _packet_body_text(packet=packet, max_sentences=_BODY_MAX_SENTENCES)
        opening = opening_key(best_body)
        if opening:
            used_openings.append(opening)
        used_bodies.append(best_body)
        if len(used_openings) > 24:
            del used_openings[: len(used_openings) - 24]
        if len(used_bodies) > 24:
            del used_bodies[: len(used_bodies) - 24]
        return best_body
    family = _family_key(node)
    candidates = _projection_body_candidates(
        node=node,
        summary=summary,
        evidence_entries=evidence_entries,
        narrative_pattern=narrative_pattern,
    )
    best_body = ""
    best_issue_count = 99
    for candidate in candidates:
        issues = quality_issues(
            teaser=teaser,
            body=candidate,
            micro=micro,
            used_openings=used_openings,
            used_bodies=used_bodies,
        )
        issue_count = len(issues)
        if issue_count < best_issue_count:
            best_body = candidate
            best_issue_count = issue_count
        if issue_count == 0:
            break
    if not best_body:
        fallback_lines = [
            _core_sentence(node=node, summary=summary),
            _context_sentence(node=node, narrative_pattern=narrative_pattern),
            _implication_sentence(node=node, narrative_pattern=narrative_pattern),
        ]
        best_body = _compose_sentences(
            fallback_lines,
            min_sentences=_BODY_MIN_SENTENCES,
            max_sentences=_BODY_MAX_SENTENCES,
        )
    best_body = _smart_clip(best_body, 520)
    opening = opening_key(best_body)
    if opening:
        used_openings.append(opening)
    used_bodies.append(best_body)
    if len(used_openings) > 24:
        del used_openings[: len(used_openings) - 24]
    if len(used_bodies) > 24:
        del used_bodies[: len(used_bodies) - 24]
    if not best_body.strip():
        return _ensure_sentence(editorialize_teaser(summary or "Bu tema sende belirginleşiyor.", family))
    return best_body


def _projection_body_candidates(
    *,
    node: Mapping[str, Any],
    summary: str,
    evidence_entries: Sequence[Mapping[str, Any]],
    narrative_pattern: str,
) -> list[str]:
    core = _core_sentence(node=node, summary=summary)
    context = _context_sentence(node=node, narrative_pattern=narrative_pattern)
    implication = _implication_sentence(node=node, narrative_pattern=narrative_pattern)
    pattern = _pattern_sentence(
        node=node,
        narrative_pattern=narrative_pattern,
        summary=summary,
        evidence_entries=evidence_entries,
    )
    evidence_hint = _evidence_hint_sentence(evidence_entries=evidence_entries, node=node)
    candidates: list[str] = []
    layouts: list[list[str]] = [
        [core, pattern, context, implication],
        [pattern, core, context, implication],
        [core, context, pattern, implication],
        [core, pattern, evidence_hint, implication],
    ]
    for layout in layouts:
        body = _compose_sentences(layout, min_sentences=_BODY_MIN_SENTENCES, max_sentences=_BODY_MAX_SENTENCES)
        if body and body not in candidates:
            candidates.append(body)
    if not candidates:
        headline = _ensure_sentence(str(node.get("headline") or node.get("title") or "").strip()) or "Bu çizgi sende belirgin."
        fallback = _compose_sentences(
            [core or headline, context, implication],
            min_sentences=_BODY_MIN_SENTENCES,
            max_sentences=_BODY_MAX_SENTENCES,
        )
        if fallback:
            candidates.append(fallback)
    return candidates


def _context_sentence(*, node: Mapping[str, Any], narrative_pattern: str) -> str:
    domain_key = str(node.get("domain") or "").strip()
    domain_loc = _domain_locative(domain_key)
    raw_layers = node.get("layers") if isinstance(node.get("layers"), Sequence) else []
    layer_labels = [
        _layer_label(str(layer.get("layer") or "").strip())
        for layer in raw_layers
        if isinstance(layer, Mapping) and str(layer.get("layer") or "").strip()
    ][:2]
    if not layer_labels:
        layer_labels = [_layer_label(str(node.get("primary_layer") or "").strip())]
    layer_labels = [label for label in layer_labels if label]

    if domain_loc and layer_labels:
        layers_text = " ve ".join(layer_labels)
        templates = [
            f"Bu etki en çok {domain_loc} görünür ve {layers_text} birlikte çalışır",
            f"{domain_loc.capitalize()} bu {layers_text} çizgisi daha hızlı devreye girer",
            f"Günlük akışta {domain_loc} {layers_text} tonu belirginleşir",
        ]
        return _pick_sentence_variant(node=node, templates=templates, salt=f"context:{narrative_pattern}")
    if domain_loc:
        templates = [
            f"Bu tema en çok {domain_loc} görünür olur",
            f"{domain_loc.capitalize()} etkisini daha doğrudan fark edersin",
            f"Gündelik akışta bu çizgi özellikle {domain_loc} devreye girer",
        ]
        return _pick_sentence_variant(node=node, templates=templates, salt=f"context:{narrative_pattern}:domain")
    if layer_labels:
        templates = [
            f"Bu çizgide {layer_labels[0]} katmanı daha baskın çalışır",
            f"İç ritimde {layer_labels[0]} tonu yönü belirler",
            f"Genel akışta {layer_labels[0]} hattı kararlarını etkiler",
        ]
        return _pick_sentence_variant(node=node, templates=templates, salt=f"context:{narrative_pattern}:layer")
    return "Bu tema sende tekrar eden bir ritim kuruyor."


def _core_sentence(*, node: Mapping[str, Any], summary: str) -> str:
    summary_lines = _split_sentences(summary, max_sentences=2)
    base = summary_lines[0] if summary_lines else ""
    if not base:
        base = _ensure_sentence(str(node.get("headline") or node.get("title") or "").strip())
    stem = re.sub(r"[.!?]+$", "", base).strip()
    if not stem:
        stem = "Sende belirgin bir dinamik var"
    templates = [
        stem,
        f"{stem}, bu çizgi senden kolay kolay kaybolmaz",
        f"{stem}, kararlarının arka planında bu tema güçlü kalır",
        f"{stem}, gündelik ritmini en çok burası şekillendirir",
    ]
    return _pick_sentence_variant(node=node, templates=templates, salt="core")


def _pattern_sentence(
    *,
    node: Mapping[str, Any],
    narrative_pattern: str,
    summary: str,
    evidence_entries: Sequence[Mapping[str, Any]],
) -> str:
    domain_key = str(node.get("domain") or "").strip()
    domain_loc = _domain_locative(domain_key)
    primary_layer = _layer_label(_primary_layer(node))
    summary_stem = re.sub(r"[.!?]+$", "", (summary or "").strip())
    detail_hint = _evidence_hint_text(evidence_entries=evidence_entries)

    if narrative_pattern == "contrast":
        outer = _pick_variant_text(
            node=node,
            templates=[
                "kontrollü ve net",
                "sakin ama belirleyici",
                "mesafeli ama güven veren",
            ],
            salt="pattern:contrast:outer",
        )
        inner = _pick_variant_text(
            node=node,
            templates=[
                "yoğun bir iç değerlendirme",
                "ince ayarlı bir tartı mekanizması",
                "sessiz ama güçlü bir baskı",
            ],
            salt="pattern:contrast:inner",
        )
        return _ensure_sentence(f"Dışarıdan {outer} gibi görünürsün ama içeride {inner} çalışır")
    if narrative_pattern == "tension":
        strain = _pick_variant_text(
            node=node,
            templates=[
                "hız ile kontrol arasında sıkışman",
                "aşırı sorumluluk alıp ritmi zorlaman",
                "kendinden beklentiyi fazla yükseltmen",
            ],
            salt="pattern:tension:strain",
        )
        gain = _pick_variant_text(
            node=node,
            templates=[
                "dayanıklılık ve strateji",
                "net öncelik koyma becerisi",
                "krizde sakin kalma gücü",
            ],
            salt="pattern:tension:gain",
        )
        return _ensure_sentence(f"Zorlandığında {strain} öne çıkar, bu hat zamanla sana {gain} kazandırır")
    if narrative_pattern == "relational":
        relation_line = _pick_variant_text(
            node=node,
            templates=[
                "önce sınır çizerek sonra derinleşerek",
                "güven oluşunca hızla açılarak",
                "netlik arayıp belirsizlikten uzak durarak",
            ],
            salt="pattern:relational:line",
        )
        if domain_loc:
            return _ensure_sentence(f"İlişkilerde bu tema çoğunlukla {relation_line} görünür, özellikle {domain_loc} daha net hissedilir")
        return _ensure_sentence(f"İlişkilerde bu tema çoğunlukla {relation_line} görünür")
    if narrative_pattern == "growth":
        growth = _pick_variant_text(
            node=node,
            templates=[
                "gücün dağılmak yerine tek bir hatta toplanır",
                "hem etki hem denge aynı anda büyür",
                "daha az eforla daha net sonuç alırsın",
            ],
            salt="pattern:growth:gain",
        )
        return _ensure_sentence(f"Bunu doğru kullandığında {growth}")

    # inner_state default
    inner_state = _pick_variant_text(
        node=node,
        templates=[
            "önce iç tartı çalışır, sonra hareket gelir",
            "güvenlik kontrolü devreye girer, ardından karar netleşir",
            "önce anlamlandırma, sonra aksiyon sırası oluşur",
        ],
        salt="pattern:inner_state:line",
    )
    if primary_layer:
        return _ensure_sentence(f"İçeride genelde {inner_state}, bu da {primary_layer} katmanını daha görünür kılar")
    if detail_hint:
        return _ensure_sentence(f"İçeride genelde {inner_state}; ipuçları da bunu destekler: {detail_hint}")
    if summary_stem:
        return _ensure_sentence(f"İçeride genelde {inner_state}; bu yüzden {summary_stem.lower()}")
    return _ensure_sentence(f"İçeride genelde {inner_state}")


def _implication_sentence(*, node: Mapping[str, Any], narrative_pattern: str) -> str:
    primary_layer = _primary_layer(node)
    layer_label = _layer_label(primary_layer)
    domain_loc = _domain_locative(str(node.get("domain") or "").strip())

    if primary_layer == "shadow":
        templates = [
            "Fark edilmediğinde ilişki ve karar tarafında gereksiz sertleşme üretebilir; fark edildiğinde ise güçlü bir sınır zekasına dönüşür",
            "Yönetilmediğinde iç baskıyı artırabilir; bilinçli kullanıldığında netlik ve dayanıklılık sağlar",
            "Üstü örtülürse geri çekilme yaratabilir; işlendiğinde olgun bir öz-disipline evrilir",
        ]
    elif primary_layer == "potential":
        templates = [
            "Doğru yönde beslendiğinde hızla somut sonuca döner ve etki alanını büyütür",
            "Bilinçli kullanıldığında uzun vadede kalıcı bir uzmanlığa dönüşür",
            "Ritmi korunduğunda hem özgüveni hem üretkenliği aynı anda yükseltir",
        ]
    elif primary_layer == "mechanism":
        templates = [
            "Karar anlarında bu mekanizma devreye girer ve dağınıklığı toparlayıp önceliği netleştirir",
            "Günlük akışta bunu yönettiğinde zihinsel enerji daha verimli ve odaklı çalışır",
            "Bu işleyiş doğru kurulduğunda hem tempo hem karar kalitesi artar",
        ]
    elif primary_layer == "effect":
        templates = [
            "Dış dünyadaki yansıması güven ve ciddiyet üretir; bu da ilk izlenimi belirgin biçimde etkiler",
            "İnsanların senden aldığı sinyal daha kararlı olur; bu da etkileşimde net bir çerçeve kurar",
            "Görünür etkisi güçlü olduğu için sosyal ve iş bağlamında hızlı pozisyon aldırır",
        ]
    elif primary_layer == "recognition":
        templates = [
            "İlk temaslarda bu ton hızla okunur; doğru dozda kaldığında güçlü bir imza etkisi yaratır",
            "Fark edilirlik artar ve insanlar seni daha net bir çerçevede konumlandırır",
            "Bu çizgi görünürlüğü artırır; dengede kaldığında güven veren bir profil oluşturur",
        ]
    elif primary_layer == "cause":
        templates = [
            "Kökteki bu neden çözüldükçe hem davranış hem ilişki ritmi daha tutarlı hale gelir",
            "Temel tetikleyici netleştiğinde tepkiler daha bilinçli ve dengeli akmaya başlar",
            "Bu kök dinamiği tanımak tekrar eden döngüleri kırmada kritik rol oynar",
        ]
    else:
        templates = [
            "Bu çizgi düzenli işlendiğinde karar ve ilişki tarafında daha tutarlı sonuçlar üretir",
            "Farkındalıkla kullanıldığında ritmi sakinleştirir ve etkiyi netleştirir",
            "İyi yönetildiğinde gündelik akışta daha dengeli bir tempo kurar",
        ]
    if domain_loc and layer_label:
        templates.append(f"Özellikle {domain_loc} bu {layer_label} hattı sonucu belirleyen ana kaldıraç olur")
    return _pick_sentence_variant(node=node, templates=templates, salt=f"implication:{narrative_pattern}:{primary_layer}")


def _evidence_hint_sentence(
    *,
    evidence_entries: Sequence[Mapping[str, Any]],
    node: Mapping[str, Any],
) -> str:
    hint = _evidence_hint_text(evidence_entries=evidence_entries)
    if not hint:
        return ""
    templates = [
        f"Bunu destekleyen işaretler de açık: {hint}",
        f"Sahadaki ipuçları aynı çizgiyi doğruluyor: {hint}",
        f"Destekleyici sinyaller bu hattı güçlendiriyor: {hint}",
    ]
    return _pick_sentence_variant(node=node, templates=templates, salt="evidence_hint")


def _evidence_hint_text(*, evidence_entries: Sequence[Mapping[str, Any]]) -> str:
    for entry in evidence_entries:
        if not isinstance(entry, Mapping):
            continue
        text = str(entry.get("text") or "").strip()
        if not text:
            continue
        stem = re.sub(r"[.!?]+$", "", text).strip()
        if stem:
            return _short_text(stem, 110)
    return ""


def _pick_narrative_pattern(*, node: Mapping[str, Any], salt: str = "") -> str:
    base_salt = "narrative_pattern"
    if salt:
        base_salt = f"{base_salt}:{salt}"
    idx = _variant_index(node=node, salt=base_salt, modulo=len(_NARRATIVE_PATTERNS))
    return _NARRATIVE_PATTERNS[idx]


def _projection_passage_for_node(
    *,
    node: Mapping[str, Any],
    summary: str,
    evidence_entries: Sequence[Mapping[str, Any]],
    pattern_salt: str,
    max_chars: int,
) -> str:
    packet = _packet_from_node(node)
    if packet:
        return _short_text(_packet_body_text(packet=packet, max_sentences=4), max_chars)
    narrative_pattern = _pick_narrative_pattern(node=node, salt=pattern_salt)
    candidates = _projection_body_candidates(
        node=node,
        summary=summary,
        evidence_entries=evidence_entries,
        narrative_pattern=narrative_pattern,
    )
    headline_sentence = _ensure_sentence(str(node.get("headline") or node.get("title") or "").strip())
    if headline_sentence:
        preferred_candidates = [
            candidate
            for candidate in candidates
            if not candidate.startswith(headline_sentence)
        ]
        if preferred_candidates:
            candidates = preferred_candidates
    if not candidates:
        fallback = _compose_sentences(
            [
                _core_sentence(node=node, summary=summary),
                _context_sentence(node=node, narrative_pattern=narrative_pattern),
                _implication_sentence(node=node, narrative_pattern=narrative_pattern),
            ],
            min_sentences=2,
            max_sentences=4,
        )
        return _short_text(fallback or str(summary or "").strip(), max_chars)
    candidate_index = _variant_index(
        node=node,
        salt=f"passage_choice:{pattern_salt}",
        modulo=len(candidates),
    )
    return _short_text(candidates[candidate_index], max_chars)


def _pick_sentence_variant(
    *,
    node: Mapping[str, Any],
    templates: Sequence[str],
    salt: str,
) -> str:
    options = [_ensure_sentence(item) for item in templates if str(item).strip()]
    if not options:
        return ""
    idx = _variant_index(node=node, salt=salt, modulo=len(options))
    return options[idx]


def _pick_variant_text(
    *,
    node: Mapping[str, Any],
    templates: Sequence[str],
    salt: str,
) -> str:
    options = [" ".join(str(item).split()).strip() for item in templates if str(item).strip()]
    if not options:
        return ""
    idx = _variant_index(node=node, salt=salt, modulo=len(options))
    return options[idx]


def _variant_index(*, node: Mapping[str, Any], salt: str, modulo: int) -> int:
    if modulo <= 0:
        return 0
    seed = "|".join(
        [
            str(node.get("node_id") or "").strip(),
            str(node.get("domain") or "").strip(),
            str(node.get("primary_layer") or "").strip(),
            str(node.get("headline") or node.get("title") or "").strip(),
            salt,
        ]
    )
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % modulo


def _primary_layer(node: Mapping[str, Any]) -> str:
    primary = str(node.get("primary_layer") or "").strip().lower()
    if primary:
        return primary
    layers = node.get("layers") if isinstance(node.get("layers"), Sequence) else []
    for layer in layers:
        if not isinstance(layer, Mapping):
            continue
        label = str(layer.get("layer") or "").strip().lower()
        if label:
            return label
    return ""


def _domain_label(value: str) -> str:
    key = str(value or "").strip().lower()
    return _DOMAIN_LABELS.get(key, key)


def _domain_locative(value: str) -> str:
    key = str(value or "").strip().lower()
    if key in _DOMAIN_LOCATIVE_LABELS:
        return _DOMAIN_LOCATIVE_LABELS[key]
    label = _DOMAIN_LABELS.get(key, key)
    if not label:
        return ""
    if label.endswith("alan"):
        return f"{label}da"
    if label.endswith(("ler", "lar")):
        return f"{label}da"
    return f"{label}da"


def _layer_label(value: str) -> str:
    key = str(value or "").strip().lower()
    return _LAYER_LABELS.get(key, key)


def _clean_projection_title(text: str) -> str:
    clean = _clean_projection_text(text)
    normalized = clean.strip().lower()
    if normalized in {"identity.", "identity"}:
        return "Kimlik hattın"
    if normalized in {"mind.", "mind"}:
        return "Zihinsel ritmin"
    return clean


def _clean_projection_text(text: str) -> str:
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return ""
    clean = re.sub(r"(?i)^identity\.?$", "Kimlik hattın", clean)
    clean = re.sub(r"(?i)^mind\.?$", "Zihinsel ritmin", clean)
    clean = re.sub(r"\balan alanında\b", "alanda", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\balan alanı\b", "alan", clean, flags=re.IGNORECASE)
    clean = re.sub(r"(?i)\bPotential\b", "Potansiyel", clean)
    clean = re.sub(r"(?i)\bShadow\b", "Gölge", clean)
    clean = re.sub(r"(?i)\bMechanism\b", "İşleyiş", clean)
    clean = re.sub(r"(?i)\bRecognition\b", "Tanınma", clean)
    clean = _normalize_house_tokens(clean)
    return clean


def _normalize_house_tokens(text: str) -> str:
    clean = str(text or "")
    clean = re.sub(
        r"(?i)\b(\d+)\.\s*ev\b",
        lambda m: f"{m.group(1)}. ev",
        clean,
    )
    clean = re.sub(
        r"(?i)\b(\d+)\.\s*house\b",
        lambda m: f"{m.group(1)}. house",
        clean,
    )
    return clean


def _detail_card_from_block(block: Mapping[str, Any]) -> Dict[str, Any]:
    detail_items = block.get("detail_items") if isinstance(block.get("detail_items"), Sequence) else []
    supporting_blocks = [
        str(item.get("text") or "").strip()
        for item in detail_items
        if isinstance(item, Mapping) and str(item.get("text") or "").strip()
    ]
    detail_blocks = build_editorial_detail_blocks_for_profile_block(
        block,
        supporting_blocks=supporting_blocks,
    )
    if not detail_blocks:
        body = str(block.get("body") or "").strip()
        if body:
            detail_blocks = [body]
    evidence_ids = [
        str(item.get("evidence_id") or "").strip()
        for item in detail_items
        if isinstance(item, Mapping) and str(item.get("evidence_id") or "").strip()
    ]
    node_id = str(block.get("node_id") or "").strip()
    block_id = str(block.get("id") or "").strip() or "projection"
    title = str(block.get("headline") or "").strip()
    summary = str(block.get("teaser") or "").strip()
    return {
        "card_key": f"{block_id}_detail",
        "id": block_id,
        "family": str(block.get("family") or "").strip(),
        "origin": str(block.get("origin") or "").strip(),
        "title": title,
        "summary": summary,
        "detail_blocks": detail_blocks[:7],
        "node_id": node_id,
        "evidence_ids": evidence_ids,
        "trace": {
            "node_id": node_id,
            "evidence_ids": evidence_ids,
        },
    }


def _hero_from_node(*, node: Mapping[str, Any]) -> Dict[str, Any]:
    node_id = str(node.get("node_id") or "").strip()
    evidence_ids = _node_evidence_ids(node, {})
    raw_title = str(node.get("headline") or node.get("title") or "").strip() or "Profil Özü"
    # Bug 2 (v8 hero): protect the headline slot from long-form body copy.
    if _is_long_form_headline(raw_title):
        title = (
            _fallback_short_headline(
                packet=_packet_from_node(node), node=node, family=_family_key(node)
            )
            or _clip_to_headline(raw_title)
            or "Profil Özü"
        )
    else:
        title = _clip_to_headline(raw_title) or "Profil Özü"
    summary = _projection_passage_for_node(
        node=node,
        summary=str(node.get("summary") or "").strip(),
        evidence_entries=node.get("evidence") if isinstance(node.get("evidence"), Sequence) else [],
        pattern_salt="hero",
        max_chars=420,
    )
    return {
        "headline": title,
        "summary": summary,
        "node_id": node_id,
        "evidence_ids": evidence_ids,
        "trace": {
            "node_id": node_id,
            "evidence_ids": evidence_ids,
        },
    }


def _section_from_node(
    *,
    node: Mapping[str, Any],
    eyebrow: str,
) -> Dict[str, Any]:
    node_id = str(node.get("node_id") or "").strip()
    evidence_ids = _node_evidence_ids(node, {})
    raw_title = str(node.get("headline") or node.get("title") or "").strip() or "Kimlik Çizgisi"
    # Bug 2 (v8 identity axis / section): protect the headline slot.
    if _is_long_form_headline(raw_title):
        title = (
            _fallback_short_headline(
                packet=_packet_from_node(node), node=node, family=_family_key(node)
            )
            or _clip_to_headline(raw_title)
            or "Kimlik Çizgisi"
        )
    else:
        title = _clip_to_headline(raw_title) or "Kimlik Çizgisi"
    summary = _projection_passage_for_node(
        node=node,
        summary=str(node.get("summary") or "").strip(),
        evidence_entries=node.get("evidence") if isinstance(node.get("evidence"), Sequence) else [],
        pattern_salt="identity_axis",
        max_chars=520,
    )
    return {
        "eyebrow": eyebrow,
        "headline": title,
        "body": summary,
        "chips": _chips(node),
        "node_id": node_id,
        "evidence_ids": evidence_ids,
        "trace": {
            "node_id": node_id,
            "evidence_ids": evidence_ids,
        },
    }


def _insight_cell_from_node(
    *,
    node: Mapping[str, Any],
) -> Dict[str, Any]:
    node_id = str(node.get("node_id") or "").strip()
    evidence_ids = _node_evidence_ids(node, {})
    packet = _packet_from_node(node)
    title = str(node.get("headline") or node.get("title") or "").strip() or "İçgörü"
    summary = _projection_passage_for_node(
        node=node,
        summary=str(node.get("summary") or "").strip(),
        evidence_entries=node.get("evidence") if isinstance(node.get("evidence"), Sequence) else [],
        pattern_salt="insight",
        max_chars=240,
    )
    summary_line = _split_sentences(summary, max_sentences=1)
    layer = str(node.get("primary_layer") or "").strip()
    domain = str(node.get("domain") or "").strip()
    return {
        "label": _packet_label(packet) if packet else (layer.title() if layer else "Layer"),
        "title": _smart_clip(title, 84),
        "subtitle": _smart_clip(summary_line[0] if summary_line else summary, 140),
        "meta": {
            "domain": domain,
            "primary_layer": layer,
        },
        "node_id": node_id,
        "evidence_ids": evidence_ids,
        "trace": {
            "node_id": node_id,
            "evidence_ids": evidence_ids,
        },
    }


def _differentiator_from_node(
    *,
    node: Mapping[str, Any],
) -> Dict[str, Any]:
    node_id = str(node.get("node_id") or "").strip()
    evidence_ids = _node_evidence_ids(node, {})
    packet = _packet_from_node(node)
    summary = _projection_passage_for_node(
        node=node,
        summary=str(node.get("summary") or "").strip(),
        evidence_entries=node.get("evidence") if isinstance(node.get("evidence"), Sequence) else [],
        pattern_salt="differentiator",
        max_chars=520,
    )
    layer = str(node.get("primary_layer") or "").strip()
    domain = str(node.get("domain") or "").strip()
    raw_diff_title = str(node.get("headline") or node.get("title") or "").strip() or "Fark Yaratan Çizgi"
    # Bug 2 (v8 differentiators): protect the headline slot.
    if _is_long_form_headline(raw_diff_title):
        diff_title = (
            _fallback_short_headline(packet=packet, node=node, family=_family_key(node))
            or _clip_to_headline(raw_diff_title)
            or "Fark Yaratan Çizgi"
        )
    else:
        diff_title = _clip_to_headline(raw_diff_title) or "Fark Yaratan Çizgi"
    if packet:
        override = _packet_copy_override(packet)
        diff_override = str(override.get("differentiator_headline") or "").strip()
        if diff_override:
            diff_title = _clip_to_headline(diff_override) or diff_title
    return {
        "headline": diff_title,
        "body": _smart_clip(summary, 320),
        "stat": domain or "general",
        "stat_label": _packet_stat_label(packet) if packet else (layer or "layer"),
        "node_id": node_id,
        "evidence_ids": evidence_ids,
        "trace": {
            "node_id": node_id,
            "evidence_ids": evidence_ids,
        },
    }


def _node_evidence_ids(
    node: Mapping[str, Any],
    evidence_map: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    raw_ids = node.get("evidence_ids") if isinstance(node.get("evidence_ids"), Sequence) else []
    out: list[str] = []
    for evidence_id in raw_ids:
        value = str(evidence_id).strip()
        if not value or value in out:
            continue
        if not evidence_map or value in evidence_map:
            out.append(value)
    return out


def _detail_items(
    *,
    evidence_entries: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for entry in evidence_entries:
        if not isinstance(entry, Mapping):
            continue
        evidence_id = str(entry.get("evidence_id") or "").strip()
        if not evidence_id:
            continue
        text = str(entry.get("text") or "").strip()
        if not text:
            continue
        out.append(
            {
                "evidence_id": evidence_id,
                "text": _short_text(text, 180),
            }
        )
        if len(out) >= 4:
            break
    return out


def _evidence_text(entry: Mapping[str, Any]) -> str:
    text_payload = entry.get("text_payload")
    if isinstance(text_payload, str) and text_payload.strip():
        return _short_text(text_payload.strip(), 180)
    structured = entry.get("structured_payload") if isinstance(entry.get("structured_payload"), Mapping) else {}
    for key in ("proof_raw", "text", "snippet"):
        value = structured.get(key)
        if isinstance(value, str) and value.strip():
            return _short_text(value.strip(), 180)
    for key in ("chips", "tags", "support_keys"):
        value = structured.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            parts = [str(item).strip() for item in value if str(item).strip()]
            if parts:
                return _short_text(", ".join(parts), 180)
    if structured:
        key = sorted(structured.keys())[0]
        value = structured.get(key)
        if isinstance(value, str) and value.strip():
            return _short_text(value.strip(), 180)
    return ""


def _family_key(node: Mapping[str, Any]) -> str:
    packet = _packet_from_node(node)
    if packet:
        promise_type = str(packet.get("promise_type") or "").strip()
        if promise_type in {"shadow_or_friction", "wound_to_gift"}:
            return "contradiction_core"
        if promise_type in {"mind_style", "mind_identity", "behavior_reflex"}:
            return "mind_mechanics"
        if promise_type in {"love_style", "need"}:
            return "intimacy_guard"
        if promise_type == "career_signature":
            return "visible_power"
        if promise_type == "gift":
            domain = str(packet.get("domain") or "").strip()
            if domain in {"mind", "communication"}:
                return "mind_mechanics"
            if domain in {"relationship", "love", "emotional_depth"}:
                return "intimacy_guard"
            if domain in {"career", "visibility"}:
                return "visible_power"
            return "self_definition"
    domain = str(node.get("domain") or "").strip().lower()
    layer = str(node.get("primary_layer") or "").strip().lower()
    if layer == "shadow":
        return "contradiction_core"
    if domain in {"identity", "self"}:
        return "self_definition"
    if domain in {"mind", "mental"}:
        return "mind_mechanics"
    if domain in {"relationships", "relationship", "love"}:
        return "intimacy_guard"
    if domain in {"career", "work"}:
        return "visible_power"
    if layer == "effect":
        return "outer_inner_split"
    if layer == "potential":
        return "placement_signature"
    return "placement_signature"


def _chips(node: Mapping[str, Any]) -> list[str]:
    packet = _packet_from_node(node)
    if packet:
        out: list[str] = []
        domain = _packet_label(packet)
        if domain:
            out.append(domain)
        for anchor in packet.get("technical_anchors") or []:
            clean = _public_anchor_chip(str(anchor).strip())
            if clean and clean not in out:
                out.append(clean)
            if len(out) >= 3:
                break
        return out[:3]
    out: list[str] = []
    domain = str(node.get("domain") or "").strip()
    if domain:
        out.append(domain)
    primary_layer = str(node.get("primary_layer") or "").strip()
    if primary_layer and primary_layer not in out:
        out.append(primary_layer)
    raw_layers = node.get("layers") if isinstance(node.get("layers"), Sequence) else []
    for layer in raw_layers:
        if not isinstance(layer, Mapping):
            continue
        label = str(layer.get("layer") or "").strip()
        if label and label not in out:
            out.append(label)
        if len(out) >= 3:
            break
    node_type = str(node.get("node_type") or "").strip()
    if node_type and node_type not in out and len(out) < 3:
        out.append(node_type)
    return out[:3]


def _packet_from_node(node: Mapping[str, Any]) -> dict[str, Any] | None:
    payload = node.get("natal_promise_packet") if isinstance(node.get("natal_promise_packet"), Mapping) else None
    return dict(payload) if isinstance(payload, Mapping) else None


def _packet_teaser_seed(packet: Mapping[str, Any]) -> str:
    override = _packet_copy_override(packet)
    if override.get("teaser"):
        return str(override.get("teaser") or "").strip()
    return str(packet.get("direct_meaning") or packet.get("lived_scene") or packet.get("gift") or "").strip()


def _strings_equal_ish(a: str, b: str) -> bool:
    norm_a = re.sub(r"[.!?\s]+", " ", (a or "").lower()).strip()
    norm_b = re.sub(r"[.!?\s]+", " ", (b or "").lower()).strip()
    return bool(norm_a) and norm_a == norm_b


def _alternate_teaser_seed(*, packet: Mapping[str, Any], avoid: str) -> str:
    """Pick a teaser seed that does not collide with the headline. Walks
    direct_meaning -> lived_scene -> gift -> voice_seeds, returning the
    first candidate that is non-empty and not effectively equal to avoid."""
    candidates: list[str] = []
    for key in ("lived_scene", "gift", "direct_meaning", "growth_direction"):
        value = str(packet.get(key) or "").strip()
        if value:
            candidates.append(value)
    seeds = packet.get("voice_seeds") if isinstance(packet.get("voice_seeds"), Sequence) else []
    for seed in seeds:
        text = str(seed or "").strip()
        if text:
            candidates.append(text)
    for candidate in candidates:
        if not _strings_equal_ish(candidate, avoid):
            return candidate
    return ""


def _packet_micro(packet: Mapping[str, Any]) -> str:
    override = _packet_copy_override(packet)
    if override.get("micro"):
        return str(override.get("micro") or "").strip()
    for key in ("lived_scene", "gift", "direct_meaning"):
        value = str(packet.get(key) or "").strip()
        if value:
            return value
    return ""


def _packet_label(packet: Mapping[str, Any] | None) -> str:
    if not packet:
        return ""
    domain = str(packet.get("domain") or "").strip()
    mapping = {
        "mind": "Zihin",
        "communication": "Zihin",
        "identity": "Kimlik",
        "relationship": "İlişki",
        "love": "İlişki",
        "emotional_depth": "Duygu",
        "career": "Kariyer",
        "visibility": "Kariyer",
        "behavior_reflex": "Refleks",
        "creativity": "Yaratım",
        # Adana audit polish: ``community`` is used as a forced_domain for the
        # mars_leo_11h community variant. Without this entry the chip slot
        # used to fall through to the ``"İçgörü"`` default, which read as a
        # mind/insight label on a topluluk-leadership packet.
        "community": "Topluluk",
        "social": "Sosyal",
        "group": "Topluluk",
        "teaching": "Öğretmenlik",
        "spirituality": "İç dünya",
    }
    return mapping.get(domain, "İçgörü")


def _packet_stat_label(packet: Mapping[str, Any] | None) -> str:
    if not packet:
        return "layer"
    promise_type = str(packet.get("promise_type") or "").strip()
    mapping = {
        "gift": "hediye",
        "shadow_or_friction": "gerilim",
        "wound_to_gift": "dönüşüm",
        "need": "ihtiyaç",
        "drive": "itki",
        "mind_style": "zihin",
        "mind_identity": "zihin",
        "love_style": "yakınlık",
        "career_signature": "iz",
        "behavior_reflex": "refleks",
    }
    return mapping.get(promise_type, "iz")


def _packet_body_text(*, packet: Mapping[str, Any], max_sentences: int) -> str:
    override = _packet_copy_override(packet)
    if override.get("body"):
        return _smart_clip(_ensure_sentence(str(override.get("body") or "").strip()), 520)
    promise_type = str(packet.get("promise_type") or "").strip()
    domain = _packet_role_domain(packet)
    direct = _ensure_sentence(_packet_public_direct_meaning(packet))
    scene_sentences = _packet_scene_sentences(packet, max_sentences=1)
    gift = _packet_gift_sentence(
        text=str(packet.get("gift") or "").strip(),
        promise_type=promise_type,
        domain=domain,
        packet=packet,
    )
    shadow = _packet_shadow_sentence(
        text=str(packet.get("shadow_or_friction") or "").strip(),
        promise_type=promise_type,
        packet=packet,
    )
    tension = _packet_tension_sentence(
        text=str(packet.get("inner_tension") or "").strip(),
        promise_type=promise_type,
        packet=packet,
    )
    growth = _packet_growth_sentence(
        text=str(packet.get("growth_direction") or "").strip(),
        promise_type=promise_type,
        domain=domain,
        packet=packet,
    )
    anchor = _packet_anchor_sentence(packet)
    if promise_type == "gift":
        ordered = [
            anchor,
            direct,
            gift,
            *scene_sentences,
            shadow or tension,
            growth,
        ]
    elif promise_type in {"mind_style", "mind_identity", "behavior_reflex"}:
        ordered = [
            anchor,
            direct,
            *scene_sentences,
            gift,
            shadow or tension,
            growth,
        ]
    elif promise_type == "wound_to_gift":
        ordered = [
            anchor,
            tension or shadow or direct,
            *scene_sentences,
            gift,
            growth,
            direct if direct and direct != gift else "",
        ]
    elif promise_type == "shadow_or_friction":
        ordered = [
            anchor,
            shadow or direct,
            *scene_sentences,
            tension or gift,
            growth,
        ]
    elif promise_type in {"love_style", "need"}:
        ordered = [
            anchor,
            direct or (scene_sentences[0] if scene_sentences else ""),
            *scene_sentences,
            gift,
            tension or shadow,
            growth,
        ]
    elif promise_type == "career_signature":
        ordered = [
            anchor,
            direct or gift,
            *scene_sentences,
            gift,
            shadow or tension,
            growth,
        ]
    else:
        ordered = [
            anchor,
            direct,
            *scene_sentences,
            gift or tension,
            shadow,
            growth,
        ]
    body = _compose_sentences(ordered, min_sentences=3, max_sentences=max(max_sentences, 5))
    return _smart_clip(body, 520)


def _packet_anchor_sentence(packet: Mapping[str, Any]) -> str:
    anchors = packet.get("technical_anchors") if isinstance(packet.get("technical_anchors"), Sequence) else []
    cleaned = [
        str(item).strip()
        for item in anchors
        if str(item).strip() and "route" not in str(item).strip().lower()
    ]
    if not cleaned:
        return ""
    # De-duplicate anchors that point at the same underlying placement /
    # aspect under different surface labels before building the sentence.
    # Skip bare sign names ("Koç", "Yengeç", ...) — they read awkwardly as
    # standalone anchors when joined into prose.
    filtered = [item for item in cleaned if not _is_bare_sign_label(item)]
    deduped = _dedup_anchors_by_signature(filtered or cleaned, limit=4)
    top: list[str] = []
    seen_clauses: set[str] = set()
    for item in deduped:
        clause = _anchor_clause(item)
        if not clause:
            continue
        key = re.sub(r"[.!?\s]+", " ", clause.lower()).strip()
        if not key or key in seen_clauses:
            continue
        # Suppress narrower clauses that are wholly contained within an
        # earlier broader clause (e.g. "Güneş'inin 1. evde olması" when the
        # first clause was "Yükseleninin Oğlak'ta ve Güneş'inin 1. evde
        # olması").
        if any(key in earlier or earlier in key for earlier in seen_clauses):
            continue
        seen_clauses.add(key)
        top.append(clause)
        if len(top) >= 2:
            break
    if not top:
        return ""
    domain = _packet_role_domain(packet)
    promise_type = str(packet.get("promise_type") or "").strip()
    tail = _packet_anchor_tail(domain=domain, promise_type=promise_type)
    if len(top) == 1:
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="anchor_sentence_single",
            templates=[
                f"{top[0]} {tail}",
                f"{top[0]} bu hattın tonunu belirginleştiriyor",
            ],
        ))
    return _ensure_sentence(_pick_packet_variant(
        packet=packet,
        salt="anchor_sentence_double",
        templates=[
            f"{top[0]} ile {top[1]} birlikte {tail}",
            f"{top[0]} ve {top[1]} aynı çizgiyi güçlendiriyor",
            f"{top[0]} kadar {top[1]} de bu hattın karakterini belirliyor",
        ],
    ))


def _packet_scene_sentences(packet: Mapping[str, Any], *, max_sentences: int) -> list[str]:
    scene = str(packet.get("lived_scene") or "").strip()
    if not scene:
        return []
    pieces = _split_sentences(scene, max_sentences=max_sentences + 2)
    if not pieces:
        return [_ensure_sentence(_short_text(scene, 180))]
    out: list[str] = []
    for piece in pieces:
        clean = _ensure_sentence(_short_text(piece, 200))
        if clean and clean not in out:
            out.append(clean)
        if len(out) >= max_sentences:
            break
    return out


def _packet_field_sentence(*, text: str, prefix: str) -> str:
    clean = " ".join(str(text or "").split()).strip().rstrip(".")
    if not clean:
        return ""
    return _ensure_sentence(f"{prefix} {clean}")


def _packet_gift_sentence(*, text: str, promise_type: str, domain: str, packet: Mapping[str, Any]) -> str:
    clean = " ".join(str(text or "").split()).strip().rstrip(".")
    if not clean:
        return ""
    if promise_type in {"love_style", "need"}:
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="gift_sentence_love",
            templates=[
                f"{clean} sende sevginin daha yumuşak tarafını açıyor",
                f"{clean} bu bağın sıcak tarafını kuruyor",
                f"{clean} ilişkide iyi gelen yerini güçlendiriyor",
                f"İlişkide kendini en doğal hissettiğin yerlerden biri de {clean.lower()}",
                f"Bu hat sana yakınlıkta sıcak ve sağlam bir omurga veriyor: {clean.lower()}",
            ],
        ))
    if promise_type in {"mind_style", "mind_identity", "behavior_reflex", "gift"}:
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="gift_sentence_core",
            templates=[
                f"En rahat çalıştığın yerlerden biri de {clean.lower()}",
                f"{clean} bu çizginin sağlam yanını oluşturuyor",
                f"{clean} bu hattın imzasını netleştiriyor",
                f"Bu çizgide en güvendiğin taraf şu olabilir: {clean.lower()}",
                f"{clean} senin doğal işleyişine yakın bir yerde duruyor",
            ],
        ))
    if promise_type == "career_signature" or domain in {"career", "visibility", "creativity"}:
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="gift_sentence_career",
            templates=[
                f"{clean} bu görünürlük hattının güçlü tarafını kuruyor",
                f"{clean} işin rafine tarafını besliyor",
                f"{clean} üretim çizgine kalite ekliyor",
                f"Üretiminde sana özgün bir imza veren yer de burada: {clean.lower()}",
            ],
        ))
    return _ensure_sentence(_pick_packet_variant(
        packet=packet,
        salt="gift_sentence_generic",
        templates=[
            f"{clean} burada öne çıkan güçlü taraflardan biri",
            f"{clean} bu temanın besleyici tarafını kuruyor",
            f"Bu hattın sağlam yanını {clean.lower()} oluşturuyor",
        ],
    ))


def _packet_growth_sentence(*, text: str, promise_type: str, domain: str, packet: Mapping[str, Any]) -> str:
    clean = " ".join(str(text or "").split()).strip().rstrip(".")
    if not clean:
        return ""
    if promise_type in {"love_style", "need"}:
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="growth_sentence_love",
            templates=[
                f"Buradaki gelişim daha çok şu yönde çalışıyor: {clean.lower()}",
                f"Bu çizgi en çok {clean.lower()} tarafında olgunlaşıyor",
                f"İlişkide büyüyen yer de burada: {clean.lower()}",
            ],
        ))
    if promise_type in {"mind_style", "mind_identity", "behavior_reflex", "gift"}:
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="growth_sentence_core",
            templates=[
                f"Bunu kurabildiğinde {clean.lower()} daha kolay hale geliyor",
                f"Gelişim tarafı daha çok {clean.lower()} yönünde açılıyor",
                f"Bu hattın olgunlaşması için kritik yer de {clean.lower()}",
            ],
        ))
    if promise_type == "career_signature" or domain in {"career", "visibility", "creativity"}:
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="growth_sentence_career",
            templates=[
                f"Buradaki gelişim daha çok {clean.lower()} tarafında çalışıyor",
                f"Bunu dengelediğinde görünürlük hattı {clean.lower()} biçimde açılıyor",
                f"İşin olgunlaşan tarafı da burada: {clean.lower()}",
            ],
        ))
    if promise_type == "wound_to_gift":
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="growth_sentence_wound",
            templates=[
                f"Bu hassasiyet en çok {clean.lower()} yönünde ustalaşıyor",
                f"İyileşen taraf da burada beliriyor: {clean.lower()}",
            ],
        ))
    if promise_type == "shadow_or_friction":
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="growth_sentence_shadow",
            templates=[
                f"{clean} bu hattın daha dengeli işlemesine yardım ediyor",
                f"{clean} gerilimi daha kullanılabilir hale getiriyor",
            ],
        ))
    return _ensure_sentence(_pick_packet_variant(
        packet=packet,
        salt="growth_sentence_generic",
        templates=[
            f"{clean} burada büyüyen yönü gösteriyor",
            f"Gelişen taraf daha çok {clean.lower()} yönünde beliriyor",
        ],
    ))


def _packet_shadow_sentence(*, text: str, promise_type: str, packet: Mapping[str, Any]) -> str:
    clean = " ".join(str(text or "").split()).strip().rstrip(".")
    if not clean:
        return ""
    normalized_clean = clean.lower()
    if promise_type in {"love_style", "need"}:
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="shadow_sentence_love",
            templates=[
                f"Zorlayıcı tarafta ise {normalized_clean}",
                f"Gerilimli anlarda {normalized_clean} daha görünür olur",
            ],
        ))
    if promise_type in {"mind_style", "mind_identity", "behavior_reflex", "gift"}:
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="shadow_sentence_core",
            templates=[
                f"Zorlayan tarafta ise {normalized_clean}",
                f"Denge kaçtığında {normalized_clean} daha belirgin hale gelir",
            ],
        ))
    return _ensure_sentence(_pick_packet_variant(
        packet=packet,
        salt="shadow_sentence_generic",
        templates=[
            f"Zorlayan tarafıysa {normalized_clean}",
            f"Gerilim yaratan yerde çoğu zaman {normalized_clean} belirir",
        ],
    ))


def _packet_tension_sentence(*, text: str, promise_type: str, packet: Mapping[str, Any]) -> str:
    clean = " ".join(str(text or "").split()).strip().rstrip(".")
    if not clean:
        return ""
    if promise_type in {"love_style", "need"}:
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="tension_sentence_love",
            templates=[
                f"İçeride çoğu zaman şu ikilik çalışıyor: {clean.lower()}",
                f"Duygusal tarafta seni zorlayan şey de bu olabilir: {clean.lower()}",
            ],
        ))
    if promise_type in {"mind_style", "mind_identity", "behavior_reflex", "gift"}:
        return _ensure_sentence(_pick_packet_variant(
            packet=packet,
            salt="tension_sentence_core",
            templates=[
                f"İçerideki gerilim çoğu zaman burada toplanıyor: {clean.lower()}",
                f"Bu hattın iç basıncı da şurada birikiyor: {clean.lower()}",
            ],
        ))
    return _ensure_sentence(_pick_packet_variant(
        packet=packet,
        salt="tension_sentence_generic",
        templates=[
            f"İçerideki gerilim de şu olabilir: {clean.lower()}",
            f"İçeriden zorlayan taraf ise {clean.lower()}",
        ],
    ))


def _packet_copy_override(packet: Mapping[str, Any]) -> dict[str, str]:
    match_id = _packet_match_id(packet)
    role_domain = _packet_role_domain(packet)
    cluster_id = _packet_cluster_id(packet)
    packet_id = str(packet.get("id") or "").strip()

    if match_id == "venus_sagittarius_12h_hidden_expansive_love" and role_domain == "relationship":
        return {
            "headline": "Bazı duygular sende önce içeride büyüyor olabilir.",
            "teaser": "Sevgi bazen önce iç dünyanda anlam kazanıyor olabilir.",
            "micro": "Sevginin önce kendi içinde büyümesi ve kolay açılmaması.",
            "body": (
                "Venüs'ünün 12. evde Yay'da olması sevgiyi bazen önce içeride büyüten bir taraf verebilir. "
                "Birine yalnızca kişi olarak değil, sende açtığı anlama da bağlanabilirsin. "
                "Bu yüzden bazı duygular dışarıdan çok görünmese bile içeride uzun süre yer kaplayabilir. "
                "Buradaki gelişim, idealize ettiğin şeyi gerçek temasla da sınayabilmek."
            ),
        }
    if match_id == "venus_sagittarius_12h_hidden_expansive_love" and role_domain == "career":
        return {
            "headline": "Bir şeyi hemen göstermektense, önce içine sinmesini bekleyebilirsin.",
            "teaser": "Üretimin sende çoğu zaman görünmeden önce içeride olgunlaşıyor olabilir.",
            "micro": "Bir işi paylaşmadan önce içeride rafine etmek istemek.",
            "body": (
                "Venüs'ünün 12. evde Yay'da, kariyer hattının da Terazi'de olması üretiminde iç hazırlığı büyütüyor. "
                "Bir şeyi hemen göstermektense, önce içine sinmesini ve doğru formu bulmasını isteyebilirsin. "
                "Bu sana rafine bir sunum gücü verir; ama fazla beklersen görünür olma zamanı kaçabilir. "
                "Buradaki olgunlaşma, içerde büyüttüğün şeyi doğru anda dışarı çıkarabilmekte."
            ),
        }
    if match_id == "saturn_sextile_uranus_structured_originality" and role_domain == "identity":
        return {
            "headline": "Ciddi görünsen de içeride daha farklı bir çizgi taşıyorsun.",
            "teaser": "Kontrollü duruşunun içinde daha özgün ve beklenmedik bir taraf var.",
            "micro": "Dışarıda kontrollü kalırken içeride daha özgün bir çizgiyi taşımak.",
            "body": (
                "Yükselen Oğlak dışarıda daha kontrollü bir duruş verebilir. "
                "Ama Uranüs'ün 1. evde çalışması, kimliğinin içinde daha özgür ve kalıba sığmayan bir damar olduğunu gösteriyor. "
                "Bu tarafı bastırmak yerine ona yapı verdiğinde, farklılığın dağınık değil güçlü bir imzaya dönüşür. "
                "Buradaki gelişim, ciddiyetle özgünlüğü aynı bedende rahatça taşıyabilmek."
            ),
        }
    if match_id == "saturn_sextile_uranus_structured_originality" and role_domain == "mind":
        return {
            "headline": "Yeni fikri yalnızca bulmak değil, çalışır hale getirmek sende güçlü olabilir.",
            "teaser": "Zihninde yenilikle yapı aynı anda çalışabiliyor.",
            "micro": "Yeni bir fikri hızla çalışır bir sisteme çevirebilmek.",
        }
    if match_id == "chiron_conjunct_mc_visibility_wound_to_voice" and role_domain == "career":
        return {
            "body": (
                "Chiron'un kariyer hattıyla kavuşumda olması, görünürlüğüne hassas bir damar katıyor. "
                "Görünür olurken hassaslaşman boşuna değil. "
                "Bazen insanlara en çok dokunan tarafın, saklamaya çalıştığın kırılganlığın içinden çıkıyor olabilir. "
                "Bunu utanç gibi taşımak yerine, başkasına alan açan daha ince bir sezgiye çevirdiğinde sesin güçleniyor."
            ),
        }
    if match_id == "moon_trine_venus_emotional_warmth" and role_domain == "relationship":
        return {
            "headline": "Birini sevdiğinde yalnızca yaklaşmak değil, ona iyi gelmek de istersin.",
            "teaser": "Sevginin içinde yumuşatma, güzelleştirme ve bakım verme tarafı var.",
        }
    if match_id == "venus_trine_saturn_trust_bond" and role_domain == "relationship":
        return {
            "headline": "Sevgi verdiğinde bunun içinde tutarlılık ve söz taşıyan bir taraf var.",
            "teaser": "Sevgi sende hafiflik kadar güven, tutarlılık ve zamanla kurulan sadakati de ister.",
            "micro": "Bir bağın sadece heyecanlı değil, güvenilir de olmasına önem vermek.",
            "body": (
                "Venüs'ünün Satürn'le uyumlu çalışması, ilişkide hafifliğin yanında güven ve tutarlılık da aradığını gösteriyor. "
                "Bir bağın sadece heyecanlı değil, zamanla sağlamlaşan bir yerde durması senin için önemli olabilir. "
                "Sevgi sende sözün davranışla desteklendiği yerde daha rahat açılır. "
                "Gerilimli anlarda ise fazla kontrollü açılmak, duyguyu güven gelene kadar uzun süre tutmak ya da yakınlığı fazla test etmek öne çıkabilir."
            ),
        }
    if match_id in {"aquarius_mc_mars_conjunct_mc_visible_freedom_drive", "aquarius_mc_mars_conjunct_mc_visible_freedom_drive_aux"} and role_domain == "career":
        override = {
            "headline": "Görünür işte cesur başlatıcılık, bağımsız hareket ve canlı yön duygusu.",
            "teaser": "Görünürlük hattın, hız, inisiyatif ve kendi yönünü kendin belirleme isteğiyle çalışabilir.",
            "micro": "Sen görünür olmaya sadece dikkat çekmek gibi bakmıyorsun.",
            "body": (
                "Mars'ının kariyer hattına çok yakın olması, dış dünyada pasif kalmak istemeyen bir enerji verdiğini gösteriyor. "
                "Bir şeyi başlatmak, kendi yönünü göstermek ve gerektiğinde yolu açmak isteyebilirsin. "
                "Kova vurgusu bunu daha bağımsız, yenilikçi ve klasik kalıplara kolay sığmayan bir çizgiye taşıyor. "
                "Zorlandığında özgürlük ihtiyacını ani kopuşlara ya da yön değişimlerine çevirmemeye dikkat etmen gerekir."
            ),
        }
        if packet_id.endswith("_aux"):
            override["differentiator_headline"] = "Kendi yolunu açma cesareti"
        return override
    if match_id == "mind_mind_system" and role_domain == "mind":
        return {
            "headline": "Ne yapacağını bildiğin an tempo kendiliğinden yükselir.",
            "teaser": "Sen dışarıdan meraklı ve hareketli görünebilirsin. Yükselenin İkizler olduğu için bir ortama girer girmez zihnin çalışmaya, bağlantılar kurmaya başlıyor.",
            "micro": "Bir ortama girdiğinde bağlantıları hızlı kurmak.",
            "body": (
                "Yükseleninin İkizler, yöneticisi Merkür'ünün de 11. evde Balık'ta olması zihnini hem hızlı hem de sezgisel çalıştırıyor. "
                "Bir ortama girdiğinde bağlantıları çabuk kurabilir, insanların ne söylediği kadar ortamın duygusunu da sezebilirsin. "
                "Net bağlam geldiğinde tempon yükselir. "
                "Ama sınırlar belirsizleştiğinde zihnin dağılabilir."
            ),
        }
    if match_id == "gemini_asc_venus_1h_social_relational_presence" and role_domain == "identity":
        return {
            "headline": "Duruşun hafif görünse de kimle ne kadar açılacağını hızlı sezebiliyor olabilirsin.",
            "teaser": "İnsanların seni ilk anda sosyal, canlı ve ilişki kurmaya açık hissetmesi kolay olabilir.",
            "micro": "Bir ortama girdiğinde hızlıca temas kuracak bir ton bulmak.",
            "body": (
                "Yükseleninin İkizler, Venüs'ünün de 1. evde olması dışarıdan sosyal, canlı ve kolay temas kuran bir izlenim verir. "
                "İnsanların seni ilk anda ulaşılabilir ve meraklı hissetmesi kolay olabilir. "
                "Ama bu hafif görünüm, herkese aynı açıklıkta olduğun anlamına gelmez. "
                "Kime ne kadar açılacağını hızlı sezebilen bir tarafın var."
            ),
        }
    if match_id == "moon_scorpio_6h_emotional_routine_sensitivity" and role_domain == "relationship":
        return {
            "headline": "Duygun günlük akışta bile kolay yüzeyde kalmayabilir, küçük şeyler içeride daha derine işleyebilir.",
            "teaser": "Rutinindeki küçük bir değişiklik bile içeride sandığından daha fazla yer kaplayabilir.",
            "micro": "Günlük akıştaki küçük bir değişimin bile içeride uzun süre kalması.",
            "body": (
                "Ay'ının Akrep'te ve 6. evde olması, günlük akışın sende duygusal olarak daha derin çalıştığını gösteriyor. "
                "Rutinindeki küçük bir değişiklik bile içeride sandığından daha fazla yer kaplayabilir. "
                "Bu sana güçlü bir sezgi ve krizleri erken fark etme becerisi verir. "
                "Ama kontrol ihtiyacı arttığında bedenin ve ritmin de gerilebilir."
            ),
        }
    if match_id == "mercury_sextile_9h_capricorn_aquarius_intellectual_authority" and role_domain == "mind":
        return {
            "headline": "Bir fikri sadece bulmak değil, ona sağlam bir çerçeve vermek sende güçlü olabilir.",
            "teaser": "Bir fikri sadece sezmek değil, onu çerçeveleyip sağlam bir görüşe dönüştürmek sende güçlü olabilir.",
            "micro": "Öğrendiğin şeyi daha büyük bir görüşe yerleştirmek.",
            "body": (
                "Merkür'ünün Jüpiter, Satürn ve Plüton'la destekleyici bağları, zihninin bir fikri sadece sezmekle kalmayıp ona sağlam bir çerçeve vermek istediğini gösteriyor. "
                "Öğrendiğin şeyi daha büyük bir görüşe yerleştirmek sende güçlü olabilir. "
                "Bir düşünceyi daha geniş bir bağlama oturtmadan rahatlamamak da bu zihinsel omurganın parçası olabilir."
            ),
        }
    if match_id == "sun_aries_12h_hidden_private_fire" and role_domain == "identity":
        return {
            "headline": "Sende dışarıdan hemen görünmeyen ama içeride hızla alevlenen bir taraf olabilir.",
            "teaser": "Dışarıdan hemen görünmese de içeride hızlı, bağımsız ve kolay sönmeyen bir ateş çalışabilir.",
            "micro": "Bir şeye gerçekten yönelmeden önce bunu uzun süre kendi içinde taşımak.",
            "body": (
                "Güneş'inin 12. evde Koç'ta olması, dışarıdan hemen görünmeyen ama içeride hızlı alevlenen bir taraf verdiğini gösteriyor. "
                "Bir şeye gerçekten yönelmeden önce bunu uzun süre kendi içinde taşıyabilirsin. "
                "Cesaretin bazen sessiz başlar. "
                "Doğru anı bulduğunda görünür olur."
            ),
        }
    if match_id == "venus_trine_mars_relational_attraction_signal" and role_domain == "relationship":
        return {
            "headline": "Birine yaklaşırken bunu yalnızca sözle değil tonunla ve enerjinle de hissettirmek.",
            "teaser": "İlgini belli ettiğinde sıcaklık, çekim ve hareket aynı anda çalışabilir.",
            "micro": "Yakınlıkta canlılık ve karşılıklı çekimin hızlı yükselmesi.",
            "body": (
                "Venüs'ünün Mars'la uyumlu çalışması, ilgini sadece sözle değil tonunla, enerjinle ve hareketinle gösterebildiğini anlatır. "
                "Yakınlıkta canlılık ve karşılıklı çekim hızlı yükselebilir. "
                "Bu enerjiyi aceleye değil, ritme dönüştürdüğünde bağ daha doğal akar."
            ),
        }
    if match_id == "relationship_relationships" and role_domain == "relationship":
        return {
            "headline": "Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun.",
            "teaser": "Yakınlık burada çoğu zaman hafif ilerlemez, daha derin bir yere çekilebilir.",
            "micro": "İlişkide sadece yakınlık değil, içinin genişlediği bir güven aramak.",
            "body": (
                "Jüpiter'inin 9. evde Oğlak'ta olması ve 7. evinin Yay'da açılması, ilişkide hem alan hem de güven aradığını gösteriyor. "
                "Yakınlık sende çoğu zaman hafif bir hoşlanmadan çok, zamanla içeri oturan bir bağa dönüşmek ister. "
                "Bu yüzden ilişkide yalnızca sıcaklık değil, birlikte büyüyebileceğin ve içinin genişlediği bir güven de arayabilirsin."
            ),
        }
    if match_id == "moon_leo_8h_deep_proud_heart" and role_domain == "relationship" and cluster_id == "relationship_attachment_architecture":
        return {
            "headline": "Kalbin güven olmadan tam açılmıyor olabilir.",
            "teaser": "Yakınlık sende yüzeyde değil; güven oluşunca derinleşiyor.",
        }
    # Adana audit polish (#1, refined in §8): the auto-built anchor sentence
    # for the mc_cancer_moon_gemini_9h_teaching_voice career packet collided
    # with the chip-fragment form of proof_raw and substituted "Kariyer
    # hattının Yengeç" twice on the same line. The bespoke body below uses
    # the §8 user-supplied opener that drops the engine-mechanical
    # "çalıştırıyor" closing in favour of "istediğini gösteriyor".
    if match_id == "mc_cancer_moon_gemini_9h_teaching_voice" and role_domain == "career":
        return {
            "body": (
                "Kariyer hattının Yengeç'te, yöneticisi Ay'ın da 9. evde İkizler'de olması; "
                "dışarıda daha duyarlı, anlatan ve karşı tarafın anlayabileceği bir dil kurmak "
                "istediğini gösteriyor. "
                "Görünür olduğunda insanlara sadece bilgi değil, güven hissi de vermek isteyebilirsin. "
                "Senin public sesin sert bir otoriteden çok, anlayan ve perspektif açan bir yerden güçlenir."
            ),
        }
    # Adana audit polish (#2, refined in §8): the auto-built anchor sentence
    # joined "Venüs kare Plüton" with "Yoğun çekim" through the generic tail.
    # The §7 override fixed the opener; §8 replaces the rest of the body with
    # the user-supplied lived continuation so the card reads less like report
    # prose and more like recognised experience.
    if match_id == "venus_square_pluto_intense_love" and role_domain == "relationship":
        return {
            "body": (
                "Venüs'ün Plüton'la kare çalışması, ilişkilerde çekimi daha yoğun ve kolay geçmeyen bir yere taşıyabilir. "
                "Birine çekildiğinde bu sende kolay kolay hafif bir hoşlanma gibi kalmayabilir. "
                "O kişinin sende neyi uyandırdığını, ilişkide gücün kimin elinde olduğunu ya da neden bu kadar etkilendiğini hızlı fark edebilirsin. "
                "Bu yoğunluk kontrol etmeye çalıştığında yorabilir; ama dürüst kaldığında seni daha gerçek bir yakınlığa götürür."
            ),
        }
    # Adana audit polish §8 (B): libra_asc_venus_chart_ruler identity body
    # opened with the chip-format string
    # "Yükseleninin · Terazi · Venüs yönetici olması ile Sosyal sezgi
    # birlikte..." — the `·` separator belongs in chip arrays, not body
    # prose, and "Sosyal sezgi" is a motif label rather than a sentence
    # subject. Replace with the user-supplied lived opener that names the
    # Libra-rising + Venus-ruler dynamic in natural Turkish.
    if match_id == "libra_asc_venus_chart_ruler" and role_domain == "identity":
        return {
            "body": (
                "Dışarıdan uyumlu ve dengeli görünebilirsin; ama bu uyumun altında "
                "kiminle ne kadar yakınlaşacağını dikkatle seçen bir taraf var. "
                "Bir ortama girdiğinde önce tonu okuyup içeride seçici davranmak senin doğal işleyişine yakın. "
                "İnsan ilişkilerinde denge, zarafet ve üslup kurma becerisi buradaki güçlü tarafını netleştiriyor. "
                "Denge kaçtığında fazla uyum sağlamak, kendi tercihini geciktirmek ya da dışarıdaki dengeyi korumak için içeride gerilmek belirginleşebilir."
            ),
        }
    # Adana audit polish §8 (C): saturn_taurus_8h_steady_public_maturity
    # career body opened with the English internal label "Public maturity"
    # joined via the auto-built "X kadar Y de bu hattın karakterini
    # belirliyor" template. Replace with the user-supplied lived opener and
    # drop the English label entirely.
    if match_id == "saturn_taurus_8h_steady_public_maturity" and role_domain == "career":
        return {
            "body": (
                "Satürn'ünün 8. evde Boğa'da olması, görünür olmadan önce sağlam bir temel arayan tarafını güçlendiriyor. "
                "Derin güven, kaynak, kriz ve kontrol temaları zamanla daha olgun bir kariyer çizgisine dönüşebilir. "
                "Görünür olmadan önce temelin sağlam olduğundan emin olmak isteyebilirsin. "
                "Üretiminde sana özgün bir imza veren yer de burada: Sabır, olgunluk, krizden yapı çıkarma, güven veren profesyonel duruş."
            ),
        }
    # Adana audit polish §8 (E, community): mars_leo_11h_warm_visible_drive
    # community variant previously shared its mid-body sentence
    # ("topluluklar veya ortak idealler içinde görünür olma...")
    # byte-for-byte with the relationship variant, because both ran through
    # the same template path. Separate the two with bespoke bodies so the
    # community card actually speaks to grup/topluluk dynamics. The two
    # variants share the same match_id but differ in packet.id suffix
    # (`_community_chart_exact` vs `_chart_exact`), so we route on packet
    # id rather than role_domain — the cluster plan assigns the community
    # variant to an `action_pressure` cluster, not a literal `community`
    # role_domain.
    if match_id == "mars_leo_11h_warm_visible_drive":
        forced_domain = str(packet.get("domain") or "").strip().lower()
        if packet_id.endswith("_community_chart_exact") or forced_domain == "community":
            return {
                "body": (
                    "Bir grubun içinde sadece uyum sağlamak değil, kendi rengini göstermek isteyebilirsin. "
                    "Mars'ın 11. evde Aslan'da olması, sosyal alanda sıcak, görünür ve harekete geçiren bir enerji verir. "
                    "Bu iyi çalıştığında insanları canlandırırsın; zorlandığında ise onay görme ihtiyacı fazla büyüyebilir."
                ),
            }
        if role_domain == "relationship" or forced_domain == "relationship":
            # Adana audit polish §8 (E, relationship): relationship variant —
            # bespoke body so the relationship card talks about
            # yakınlık/heyecan rather than topluluk/grup dynamics.
            return {
                "body": (
                    "Yakınlıkta sıcaklık ve heyecan hızlı yükselebilir; ama kendi alanını ve kişisel ritmini kaybetmek istemezsin. "
                    "Birine yaklaşırken bile kendin gibi kalabilmek, bu ilişkilerde en önemli ihtiyaçlarından biri olabilir."
                ),
            }
    return {}


def _packet_match_id(packet: Mapping[str, Any]) -> str:
    meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
    match_id = str(meta.get("match_id") or "").strip()
    if match_id:
        return match_id
    packet_id = str(packet.get("id") or "").strip()
    for suffix in ("_relationship_chart_exact", "_identity_chart_exact", "_chart_exact"):
        if packet_id.endswith(suffix):
            return packet_id[: -len(suffix)]
    return packet_id


def _packet_cluster_context(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    context = packet.get("cluster_context")
    return context if isinstance(context, Mapping) else {}


def _packet_cluster_id(packet: Mapping[str, Any]) -> str:
    return str(_packet_cluster_context(packet).get("cluster_id") or "").strip()


def _packet_role_domain(packet: Mapping[str, Any]) -> str:
    return str(_packet_cluster_context(packet).get("domain_family") or packet.get("domain") or "").strip()


def _pick_packet_variant(
    *,
    packet: Mapping[str, Any],
    salt: str,
    templates: Sequence[str],
) -> str:
    options = [_ensure_sentence(item) for item in templates if str(item).strip()]
    if not options:
        return ""
    idx = _packet_variant_index(packet=packet, salt=salt, modulo=len(options))
    return options[idx]


def _packet_variant_index(*, packet: Mapping[str, Any], salt: str, modulo: int) -> int:
    if modulo <= 0:
        return 0
    seed = "|".join(
        [
            str(packet.get("id") or "").strip(),
            _packet_role_domain(packet),
            str(_packet_cluster_id(packet) or "").strip(),
            salt,
        ]
    )
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % modulo


def _anchor_clause(anchor: str) -> str:
    clean = str(anchor or "").strip()
    if not clean:
        return ""
    if clean == "Yükselen · Oğlak · Güneş 1. ev":
        return "Yükseleninin Oğlak'ta ve Güneş'inin 1. evde olması"
    localized = _public_anchor_chip(clean)
    aspect_clause = _aspect_anchor_clause(localized)
    if aspect_clause:
        return aspect_clause
    placement_match = re.match(r"^([A-Za-zÇĞİÖŞÜçğıöşü]+)\s*·\s*(\d+)\.\s*ev\s*·\s*([A-Za-zÇĞİÖŞÜçğıöşü]+)$", clean)
    if placement_match:
        planet, house, sign = placement_match.groups()
        return f"{_planet_possessive(planet)} {house}. evde {_sign_locative(sign)} olması"
    planet_house_match = re.match(r"^([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+(\d+)\.\s*ev$", clean)
    if planet_house_match:
        planet, house = planet_house_match.groups()
        return f"{_planet_possessive(planet)} {house}. evde olması"
    house_sign_match = re.match(r"^(\d+)\.\s*ev\s*([A-Za-zÇĞİÖŞÜçğıöşü]+)$", clean)
    if house_sign_match:
        house, sign = house_sign_match.groups()
        return f"{house}. evinin {sign} olması"
    rising_match = re.match(r"^Yükselen\s+(.+)$", clean)
    if rising_match:
        return f"Yükseleninin {rising_match.group(1).strip()} olması"
    mc_match = re.match(r"^(?:MC|Kariyer hattı)\s+(.+)$", localized)
    if mc_match:
        return f"Kariyer hattının {_sign_locative(mc_match.group(1).strip())} olması"
    if localized != clean:
        return localized
    return clean


def _planet_possessive(planet: str) -> str:
    mapping = {
        "Ay": "Ay'ının",
        "Güneş": "Güneş'inin",
        "Merkür": "Merkür'ünün",
        "Venüs": "Venüs'ünün",
        "Mars": "Mars'ının",
        "Jüpiter": "Jüpiter'inin",
        "Satürn": "Satürn'ünün",
        "Uranüs": "Uranüs'ünün",
        "Neptün": "Neptün'ünün",
        "Plüton": "Plüton'unun",
        "Chiron": "Chiron'unun",
    }
    return mapping.get(planet, f"{planet}'ünün")


def _sign_locative(sign: str) -> str:
    mapping = {
        "Koç": "Koç'ta",
        "Boğa": "Boğa'da",
        "İkizler": "İkizler'de",
        "Yengeç": "Yengeç'te",
        "Aslan": "Aslan'da",
        "Başak": "Başak'ta",
        "Terazi": "Terazi'de",
        "Akrep": "Akrep'te",
        "Yay": "Yay'da",
        "Oğlak": "Oğlak'ta",
        "Kova": "Kova'da",
        "Balık": "Balık'ta",
    }
    return mapping.get(sign, sign)


def _packet_anchor_tail(*, domain: str, promise_type: str) -> str:
    if domain in {"relationship", "love", "emotional_depth"} or promise_type in {"love_style", "need"}:
        return "ilişkideki bu hattı daha net hissettiriyor"
    if domain in {"career", "visibility", "creativity"} or promise_type == "career_signature":
        return "kariyer çizgine ayrı bir ton veriyor"
    if domain in {"mind", "communication"} or promise_type in {"mind_style", "mind_identity"}:
        return "zihninin çalışma biçimini daha net gösteriyor"
    return "bu temayı daha görünür hale getiriyor"


def _public_anchor_chip(anchor: str) -> str:
    clean = " ".join(str(anchor or "").split()).strip()
    if not clean:
        return ""
    exact_map = {
        "Saturn sextile Uranus": "Satürn–Uranüs desteği",
        "Moon trine Venus": "Ay–Venüs uyumu",
        "Mercury conjunction Jupiter": "Merkür–Jüpiter kavuşumu",
        "Mercury conjunct Jupiter": "Merkür–Jüpiter kavuşumu",
        "Sun square Saturn": "Güneş–Satürn karesi",
        "Mars opposite Saturn": "Mars–Satürn karşıtlığı",
        "Mars opposition Saturn": "Mars–Satürn karşıtlığı",
        "Saturn trine Pluto": "Satürn–Plüton desteği",
        "Chiron conjunct MC": "Chiron–kariyer hattı kavuşumu",
        "Chiron conjunct Midheaven": "Chiron–kariyer hattı kavuşumu",
        "Jupiter square Midheaven": "Jüpiter–kariyer hattı gerilimi",
        "Neptune square Midheaven": "Neptün–kariyer hattı gerilimi",
        "Sun conjunction Ascendant": "Güneş–Yükselen kavuşumu",
        "Ascendant Capricorn": "Yükselen Oğlak",
        "Venus in house 12": "Venüs 12. ev",
        "Saturn in house 3 Aries": "Satürn 3. ev Koç",
        "MC Terazi": "Kariyer hattı Terazi",
        # Moon-Mercury / Moon-Venus aspect labels used by the aux-anchor
        # domain-compatibility filter (Adana audit §5). Without these, an aux
        # whose technical_anchors got rewritten to the registry's English
        # label would surface raw English in the chip / body anchor sentence.
        "Moon square Mercury": "Ay–Merkür gerilimi",
        "Moon square Venus": "Ay–Venüs gerilimi",
        "Mercury conjunction Venus": "Merkür–Venüs kavuşumu",
        "Mercury conjunct Venus": "Merkür–Venüs kavuşumu",
        "Venus square Pluto": "Venüs–Plüton karesi",
        "Mars opposite Uranus": "Mars–Uranüs karşıtlığı",
        "Mars opposition Uranus": "Mars–Uranüs karşıtlığı",
        "Mercury square Pluto": "Merkür–Plüton karesi",
        "Moon opposition Pluto": "Ay–Plüton karşıtlığı",
        "Moon opposite Pluto": "Ay–Plüton karşıtlığı",
    }
    if clean in exact_map:
        return exact_map[clean]
    return clean


def _aspect_anchor_clause(anchor: str) -> str:
    mapping = {
        "Satürn–Uranüs desteği": "Satürn–Uranüs desteğinin çalışması",
        "Ay–Venüs uyumu": "Ay–Venüs uyumunun çalışması",
        "Merkür–Jüpiter kavuşumu": "Merkür–Jüpiter kavuşumunun çalışması",
        "Güneş–Satürn karesi": "Güneş–Satürn geriliminin çalışması",
        "Mars–Satürn karşıtlığı": "Mars–Satürn karşıtlığının çalışması",
        "Satürn–Plüton desteği": "Satürn–Plüton desteğinin çalışması",
        "Chiron–kariyer hattı kavuşumu": "Chiron'un kariyer hattıyla kavuşumda olması",
        "Jüpiter–kariyer hattı gerilimi": "Jüpiter'in kariyer hattına baskı kurması",
        "Neptün–kariyer hattı gerilimi": "Neptün'ün kariyer hattını sisli hale getirmesi",
        "Güneş–Yükselen kavuşumu": "Güneş ile yükselenin kavuşumda olması",
        "Ay–Merkür gerilimi": "Ay–Merkür geriliminin çalışması",
        "Ay–Venüs gerilimi": "Ay–Venüs geriliminin çalışması",
        "Merkür–Venüs kavuşumu": "Merkür–Venüs kavuşumunun çalışması",
        "Venüs–Plüton karesi": "Venüs–Plüton geriliminin çalışması",
        "Mars–Uranüs karşıtlığı": "Mars–Uranüs karşıtlığının çalışması",
        "Merkür–Plüton karesi": "Merkür–Plüton geriliminin çalışması",
        "Ay–Plüton karşıtlığı": "Ay–Plüton karşıtlığının çalışması",
    }
    return mapping.get(anchor, "")


# Public-copy sanitizer: translates raw English astrology fragments and
# canonical-but-untranslated contradiction labels that occasionally leak from
# upstream packet builders into Turkish renderer output.
_PUBLIC_COPY_TR_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    # contradiction labels left in English by upstream packet builder
    ("pressure vs resilience", "baskı ile dayanıklılık arasındaki çekişme"),
    ("structure vs originality", "yapı ile özgünlük arasındaki çekişme"),
    ("structured originality", "yapılı özgünlük çizgisi"),
    ("composure vs internal pressure", "dışsal sükunet ile içsel baskı"),
    ("speed vs control", "hız ile kontrol arasındaki çekişme"),
    ("closeness vs threshold", "yakınlık ile eşik arasındaki çekişme"),
    # planet/point name normalizations (English → Turkish)
    ("Sun conjunction Ascendant", "Güneş–Yükselen kavuşumu"),
    ("Sun square Saturn", "Güneş–Satürn karesi"),
    ("Saturn sextile Uranus", "Satürn–Uranüs desteği"),
    ("Saturn trine Pluto", "Satürn–Plüton desteği"),
    ("Moon trine Venus", "Ay–Venüs uyumu"),
    ("Mercury conjunction Jupiter", "Merkür–Jüpiter kavuşumu"),
    ("Mercury conjunct Jupiter", "Merkür–Jüpiter kavuşumu"),
    ("Mars opposition Saturn", "Mars–Satürn karşıtlığı"),
    ("Mars opposite Saturn", "Mars–Satürn karşıtlığı"),
    ("Chiron conjunct MC", "Chiron–Tepe Noktası kavuşumu"),
    ("Chiron conjunct Midheaven", "Chiron–Tepe Noktası kavuşumu"),
    ("Jupiter square Midheaven", "Jüpiter–Tepe Noktası karesi"),
    ("Neptune square Midheaven", "Neptün–Tepe Noktası karesi"),
)


def _naturalize_chip_prose(text: str) -> str:
    """Final-pass defensive cleanup for body / teaser strings.

    Two failure modes from upstream template composition that survive the
    bespoke-override layer:

    1. Chip-format `·` separators leaking into body sentences. Anchor
       fragments like ``"Yükselen · Terazi · Venüs yönetici"`` belong in
       chip arrays only; when they end up inside a prose sentence, they
       read as engine-internal label syntax rather than natural Turkish.
    2. Untranslated English internal labels (most commonly
       ``"Public maturity"``) that an upstream packet builder dropped into
       a Turkish body. These should never reach the user — translate the
       known ones to lived Turkish and let the rest flow through
       ``_localize_public_copy_tr``.

    Idempotent and safe to call on already-natural strings. Only fires when
    the suspicious tokens are present, so byte-identical output for any
    string that does not match.
    """

    clean = str(text or "")
    if not clean:
        return clean
    # English internal label that an upstream builder dropped into a body.
    # Translate to a descriptive Turkish phrase. Both casings.
    if "Public maturity" in clean:
        clean = clean.replace("Public maturity", "olgun bir kariyer çizgisi")
    if "public maturity" in clean:
        clean = clean.replace("public maturity", "olgun bir kariyer çizgisi")
    # Strip chip-format `·` separators that leaked into body / teaser prose.
    # The `·` belongs in chip arrays only; when it appears in a body the
    # surrounding tokens are anchor fragments that should be joined with a
    # natural Turkish space. Replacing with a single space and then
    # collapsing duplicate spaces gives ``"Yükselen Terazi Venüs yönetici"``
    # from ``"Yükselen · Terazi · Venüs yönetici"`` — still imperfect, but
    # no longer a chip-format leak. The bespoke override layer above should
    # always run first; this is a defensive backstop.
    if "·" in clean:
        clean = clean.replace(" · ", " ").replace("·", " ")
        clean = re.sub(r"\s{2,}", " ", clean).strip()
    return clean


def _localize_public_copy_tr(text: str) -> str:
    """Replace any raw English astrology phrasing left behind by upstream
    packet builders. Idempotent and safe to call on already-Turkish strings."""
    clean = str(text or "")
    if not clean:
        return clean
    for src, dst in _PUBLIC_COPY_TR_REPLACEMENTS:
        if src and src in clean:
            clean = clean.replace(src, dst)
    # Capitalize a lowercase letter that follows a sentence boundary like
    # ". bazen" -> ". Bazen". Skip cases where the period is part of a
    # numbered abbreviation such as "1. ev" / "12. ev". Also fires after
    # colon/semicolon (Bug 4) — Turkish post-colon concatenations like
    # "burada: i̇nsanlar..." need an İ (U+0130), not "i".
    # Map: lowercase Turkish letter -> correct uppercase form. The default
    # path uses str.upper(); the "i" → "İ" mapping is explicit so that the
    # post-colon "i" lands as U+0130 instead of "I" + combining dot.
    _TR_UPPER = {"i": "İ"}

    def _sentence_cap(m: "re.Match[str]") -> str:
        prefix = m.group(1)
        before = m.string[: m.start(1)]
        # If the period belongs to a numbered abbreviation (e.g. "1. ev"),
        # leave the following letter as-is. (Colon/semicolon never need this
        # guard.)
        if prefix == "." and before and before[-1].isdigit():
            return m.group(0)
        letter = m.group(2)
        upper = _TR_UPPER.get(letter, letter.upper())
        return f"{prefix} {upper}"

    clean = re.sub(
        r"([.!?:;])\s+([a-zçğıöşü])",
        _sentence_cap,
        clean,
    )
    # Defensive: undo accidental decomposed "i̇" (i + combining dot above,
    # U+0307) at sentence starts. The combining-dot sequence after a
    # sentence boundary is always a botched İ capitalization; outside that
    # context we leave it alone to avoid touching unrelated text.
    clean = re.sub(r"([.!?:;]\s+)i̇", r"\1İ", clean)
    # Also strip stray combining-dot characters that landed after an
    # already-capital İ ("İ̇" -> "İ").
    clean = clean.replace("İ̇", "İ")
    # Defensive: undo any accidental "1. Ev" capitalization left behind by
    # earlier passes in the pipeline.
    clean = re.sub(r"(\d+\.\s+)Ev\b", r"\1ev", clean)
    return clean


# Stable canonical signature used to de-duplicate anchors that describe the
# same astrological placement under different surface labels (e.g.
# "Satürn · 3. ev · Koç" and "Satürn 3. ev" both reduce to "satürn:3").
_PLANET_TOKENS: tuple[str, ...] = (
    "güneş",
    "ay",
    "merkür",
    "venüs",
    "mars",
    "jüpiter",
    "satürn",
    "uranüs",
    "neptün",
    "plüton",
    "chiron",
    "yükselen",
    "tepe noktası",
    "kariyer hattı",
)


def _anchor_signature(anchor: str) -> str:
    raw = " ".join(str(anchor or "").split()).strip().lower()
    if not raw:
        return ""
    # Aspect anchors are unique per pair; reduce to "planet1:planet2".
    for connector in ("–", "—", "-"):
        if connector in raw and any(
            kw in raw for kw in ("kavuşum", "kares", "üçgen", "destek", "karşıt", "uyum", "gerilim")
        ):
            head = raw.split(" ", 1)[0]
            return f"aspect:{head}"
    # House placements: extract planet + first numeric house number.
    house_match = re.search(r"(\d+)\.\s*ev", raw)
    house_part = house_match.group(1) if house_match else ""
    # Prefer the LEADING planet/point token in the surface label — e.g.
    # "Yükselen · Oğlak · Güneş 1. ev" describes the Ascendant primarily.
    planet = ""
    leading_token = raw.split("·")[0].split(" ")[0].strip()
    for token in _PLANET_TOKENS:
        if leading_token.startswith(token) or leading_token == token:
            planet = token
            break
    if not planet:
        for token in _PLANET_TOKENS:
            if token in raw:
                planet = token
                break
    if planet and house_part:
        return f"{planet}:h{house_part}"
    if planet:
        return f"planet:{planet}"
    if house_part:
        return f"house:{house_part}"
    return raw


_TR_SIGN_NAMES: frozenset[str] = frozenset(
    {"koç", "boğa", "ikizler", "yengeç", "aslan", "başak", "terazi", "akrep", "yay", "oğlak", "kova", "balık"}
)


def _is_bare_sign_label(anchor: str) -> bool:
    raw = " ".join(str(anchor or "").split()).strip().lower()
    return raw in _TR_SIGN_NAMES


def _dedup_anchors_by_signature(anchors: Sequence[str], *, limit: int = 2) -> list[str]:
    seen_sigs: set[str] = set()
    seen_planets: set[str] = set()
    out: list[str] = []
    for raw in anchors:
        clean = str(raw or "").strip()
        if not clean:
            continue
        sig = _anchor_signature(clean)
        # Collapse multiple labels that describe the same primary planet/point
        # (e.g. "Yükselen · Oğlak · Güneş 1. ev" and "Yükselen Oğlak" both
        # foreground Yükselen). Aspects have signatures starting with "aspect:"
        # and are not collapsed by primary planet.
        planet_key = ""
        if sig and not sig.startswith("aspect:"):
            if sig.startswith("planet:"):
                planet_key = sig.split(":", 1)[1]
            elif sig.startswith("house:"):
                planet_key = ""
            else:
                planet_key = sig.split(":", 1)[0]
        if sig and sig in seen_sigs:
            continue
        if planet_key and planet_key in seen_planets:
            continue
        if sig:
            seen_sigs.add(sig)
        if planet_key:
            seen_planets.add(planet_key)
        out.append(clean)
        if len(out) >= max(1, limit):
            break
    return out


def _micro_text(text: str) -> str:
    lines = _split_sentences(text, max_sentences=1)
    if lines:
        return _short_text(lines[0], 110)
    return _short_text(text, 110)


def _short_text(text: str, limit: int) -> str:
    clean = str(text or "").strip()
    if len(clean) <= limit:
        return clean
    if limit <= 3:
        return clean[:limit]
    return clean[: limit - 1].rstrip() + "…"


# Sentence-boundary chars used by the smart-clip helper. Includes the ellipsis
# character because it already terminates a "soft" sentence in our copy.
_SENTENCE_TERMINATORS: tuple[str, ...] = (".", "!", "?", "…")


def _smart_clip(text: str, max_chars: int) -> str:
    """Word- and sentence-aware truncation.

    Replaces hard ``text[:budget]``-style slicing for fields like teaser/body
    that previously produced mid-word ellipses (e.g. ``"... deği…"`` for
    ``"değil"``).

    Rules:
    1. If ``len(text) <= max_chars`` return it unchanged.
    2. Otherwise prefer the last full sentence (terminated by ``.!?…``) that
       fits inside the budget and return up to and including that terminator.
    3. If no sentence terminator fits, cut at the last whitespace before
       ``max_chars - 1`` and append ``…`` so the cut never lands inside a
       word.

    Numbered-house abbreviations (``7. ev``, ``12. evde``, ``1. evin``...)
    are protected: the period inside them is NOT treated as a sentence
    terminator, so the splitter never leaves a dangling ``"7."`` fragment at
    the tail of a clipped teaser/body. Mirrors the guard used by
    :func:`_split_sentences`.
    """

    clean = str(text or "").strip()
    if not clean:
        return ""
    if max_chars <= 0:
        return ""
    if len(clean) <= max_chars:
        return clean
    window = clean[:max_chars]
    # Prefer last sentence boundary inside the window. A terminator only
    # counts if it is at the very end of the window OR followed by
    # whitespace — this excludes the period inside numbered-house
    # abbreviations like ``7. ev`` / ``12. evde`` which used to leave a
    # dangling ``"7."`` at the tail of a clipped teaser/body (Adana audit
    # polish #4). The previous version used a plain ``rfind`` which treated
    # the period in ``"7. ev"`` as a sentence terminator.
    last_term = -1
    for i in range(len(window) - 1, -1, -1):
        ch = window[i]
        if ch not in _SENTENCE_TERMINATORS:
            continue
        # Reject if this is part of a numbered-house abbreviation ``\d+\. ev``.
        if ch == "." and _is_numbered_house_period(clean, i):
            continue
        # Require whitespace after the terminator OR end-of-window so we
        # don't cut mid-token (e.g. inside ``"3.14"``).
        if i == len(window) - 1 or window[i + 1].isspace():
            last_term = i
            break
    if last_term >= 0:
        candidate = window[: last_term + 1].rstrip()
        if candidate:
            return candidate
    # No sentence boundary — cut at last whitespace before budget-1 so the
    # appended ellipsis never lands inside a word.
    cut_window = clean[: max_chars - 1]
    space_idx = cut_window.rfind(" ")
    if space_idx <= 0:
        # Single long token / no whitespace — fall back to hard slice.
        return cut_window.rstrip() + "…"
    return cut_window[:space_idx].rstrip() + "…"


def _is_numbered_house_period(text: str, idx: int) -> bool:
    """True if ``text[idx]`` is the period inside a ``\\d+\\. ev`` label.

    Used by :func:`_smart_clip` to keep numbered-house abbreviations
    (``7. ev``, ``12. evde``, ``1. evin``...) from triggering a false
    sentence-boundary cut. Looks both ways from ``idx``: the character must
    be ``"."``, must be preceded by one or two digits (with no intervening
    letter), and the next non-period token must be ``ev`` plus an optional
    Turkish house suffix (``de``, ``in``, ``deki``, ``den``, ``ine``,
    ``inin``, ``i``).
    """
    if idx < 0 or idx >= len(text) or text[idx] != ".":
        return False
    # Walk back: must hit 1-2 digits, optionally preceded by non-letter.
    j = idx - 1
    if j < 0 or not text[j].isdigit():
        return False
    while j > 0 and text[j - 1].isdigit():
        j -= 1
    digit_start = j
    if digit_start > 0 and text[digit_start - 1].isalpha():
        return False
    # Walk forward: skip optional whitespace, then expect ``ev`` + optional
    # suffix (case-insensitive).
    k = idx + 1
    while k < len(text) and text[k].isspace():
        k += 1
    if k >= len(text):
        return False
    tail = text[k : k + 8].lower()
    return tail.startswith("ev")


def _is_long_form_headline(text: str, *, max_chars: int = 120) -> bool:
    """True when ``text`` should NOT be used as a headline in its full form.

    Used by the projection block builder to detect body-shape paragraphs
    that were accidentally routed to the headline slot. Returns True if the
    text exceeds ``max_chars`` OR contains more than one sentence
    terminator followed by additional content.
    """
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return False
    if len(clean) > max_chars:
        return True
    sentences = [piece for piece in re.split(r"(?<=[.!?…])\s+", clean) if piece.strip()]
    return len(sentences) > 1


def _clip_to_headline(text: str, *, max_chars: int = 120) -> str | None:
    """Return ``text`` if it fits the headline slot, else ``None``.

    A headline must be a single sentence under ``max_chars`` characters. If
    the incoming string is longer than the budget OR contains more than one
    sentence terminator, it is treated as body content and the caller must
    fall back to a shorter source.

    Returning ``None`` makes the bug-2 routing explicit: callers see "this is
    not a headline" rather than receiving a silently sliced paragraph.
    """

    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return None
    # Count sentence-terminating boundaries that are followed by more content.
    sentences = re.split(r"(?<=[.!?…])\s+", clean)
    sentences = [piece for piece in sentences if piece.strip()]
    if len(sentences) > 1:
        first = sentences[0].strip()
        if first and len(first) <= max_chars:
            return first
        return None
    if len(clean) > max_chars:
        return None
    return clean


def _is_aux_packet_id(packet_id: str) -> bool:
    """True when the packet id is the ``_aux`` mirror of another packet."""
    return bool(packet_id) and packet_id.endswith("_aux")


def _aux_base_packet_id(packet_id: str) -> str:
    """Strip the trailing ``_aux`` suffix from a packet id."""
    if packet_id.endswith("_aux"):
        return packet_id[: -len("_aux")]
    return packet_id


def _node_packet_id(node: Mapping[str, Any]) -> str:
    """Extract the packet id from a projection node.

    Projection node ids have the form ``promise::<packet_id>`` so we can
    recover the underlying packet id without re-reading the cluster plan.
    """
    raw = str(node.get("node_id") or "").strip()
    if raw.startswith("promise::"):
        return raw[len("promise::") :]
    return raw


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _ensure_sentence(text: str) -> str:
    clean = " ".join(str(text or "").split()).strip()
    clean = _clean_projection_text(clean)
    if not clean:
        return ""
    return clean if clean.endswith((".", "!", "?")) else f"{clean}."


_HOUSE_TOKEN_GUARD = "\x00HOUSE\x00"
_HOUSE_TOKEN_PATTERN = re.compile(
    r"(\b\d{1,2}\.)\s+(ev(?:de|in|deki|den|ine|inin|i)?\b)",
    flags=re.IGNORECASE,
)


def _split_sentences(text: str, *, max_sentences: int) -> list[str]:
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return []
    # Protect numbered-house labels ("8. ev", "12. evde", "1. evin") so the
    # period inside them is not treated as a sentence terminator.
    guarded = _HOUSE_TOKEN_PATTERN.sub(rf"\1{_HOUSE_TOKEN_GUARD}\2", clean)
    pieces = [
        part.replace(_HOUSE_TOKEN_GUARD, " ").strip()
        for part in re.split(r"(?<=[.!?])\s+", guarded)
        if part.strip()
    ]
    out = [_ensure_sentence(piece) for piece in pieces[: max(0, max_sentences)]]
    return [item for item in out if item]


def _compose_sentences(
    sentences: Sequence[str],
    *,
    min_sentences: int,
    max_sentences: int,
) -> str:
    normalized: list[str] = []
    seen: set[str] = set()
    for sentence in sentences:
        clean = _ensure_sentence(sentence)
        if not clean:
            continue
        key = re.sub(r"[.!?]+$", "", clean).strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        normalized.append(clean)
        if len(normalized) >= max(1, max_sentences):
            break
    if len(normalized) < max(1, min_sentences):
        return " ".join(normalized).strip()
    return " ".join(normalized[: max(1, max_sentences)]).strip()


def _stable_block_id(
    *,
    node_id: str,
    domain: str,
    primary_layer: str,
    used_ids: set[str],
) -> str:
    seed = node_id or f"{domain}|{primary_layer}"
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:10]
    base = f"mg_{digest}"
    candidate = base
    suffix = 2
    while candidate in used_ids:
        candidate = f"{base}_{suffix}"
        suffix += 1
    used_ids.add(candidate)
    return candidate
