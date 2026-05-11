from __future__ import annotations

from typing import Any

from .contracts import (
    AspectPatternNode,
    CanonicalNatalStateV1,
    ContradictionNode,
    DispositorRouteNode,
    HouseRulerRouteNode,
    NatalPromiseNode,
    PlanetConditionNode,
)


def _promise_node(node: NatalPromiseNode) -> dict[str, Any]:
    return {
        "node_id": node.id,
        "node_type": "natal_promise",
        "domain": node.domain,
        "title": node.theme,
        "summary": node.growth_path,
        "centrality": node.centrality,
        "status": node.status,
        "evidence_ids": [item.id for item in node.evidence],
    }


def _contradiction_node(node: ContradictionNode) -> dict[str, Any]:
    return {
        "node_id": node.id,
        "node_type": "contradiction",
        "domain": "growth_shadow",
        "title": node.title,
        "summary": node.integration_path,
        "centrality": node.centrality,
        "status": node.status,
        "evidence_ids": [item.id for item in node.evidence],
    }


def _planet_condition_node(node: PlanetConditionNode) -> dict[str, Any]:
    return {
        "node_id": node.id,
        "node_type": "planet_condition",
        "domain": "general",
        "title": f"{node.planet} condition",
        "summary": node.summary,
        "condition_type": node.condition_type,
        "status": node.status,
        "evidence_ids": [item.id for item in node.evidence],
    }


def _dispositor_route_node(node: DispositorRouteNode) -> dict[str, Any]:
    return {
        "node_id": node.id,
        "node_type": "dispositor_route",
        "domain": "general",
        "title": f"{node.origin} to {node.terminal}",
        "summary": node.summary,
        "strength": node.strength,
        "route": list(node.route),
        "status": node.status,
        "evidence_ids": [item.id for item in node.evidence],
    }


def _house_ruler_route_node(node: HouseRulerRouteNode) -> dict[str, Any]:
    return {
        "node_id": node.id,
        "node_type": "house_ruler_route",
        "domain": "general",
        "title": f"{node.house_key} ruler route",
        "summary": node.summary,
        "house_key": node.house_key,
        "ruler": node.ruler,
        "target_house": node.target_house,
        "status": node.status,
        "evidence_ids": [item.id for item in node.evidence],
    }


def _aspect_pattern_node(node: AspectPatternNode) -> dict[str, Any]:
    return {
        "node_id": node.id,
        "node_type": "aspect_pattern",
        "domain": "general",
        "title": node.pattern_type.replace("_", " "),
        "summary": node.summary,
        "pattern_type": node.pattern_type,
        "participating_bodies": list(node.participating_bodies),
        "status": node.status,
        "evidence_ids": [item.id for item in node.evidence],
    }


def _spine_line_node(line_key: str, line: Any) -> dict[str, Any]:
    return {
        "node_id": f"spine:{line_key}",
        "node_type": "chart_spine_line",
        "domain": "general",
        "title": line.title or line_key.replace("_", " "),
        "summary": line.summary or "",
        "spine_key": line_key,
        "target_node_id": line.node_id,
        "source_candidates": list(line.source_candidates),
        "evidence_ids": [item.id for item in line.evidence],
    }


def build_natal_meaning_graph(state: CanonicalNatalStateV1) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []

    def add_evidence(node_id: str, items: list[Any], *, source: str) -> None:
        for item in items:
            evidence.append(
                {
                    "evidence_id": item.id,
                    "node_id": node_id,
                    "technical": item.technical,
                    "humanized": item.humanized,
                    "layer": item.layer,
                    "role": item.role,
                    "source": item.source or source,
                    "source_ref": item.source_ref,
                }
            )

    for promise in state.core_promises:
        nodes.append(_promise_node(promise))
        add_evidence(promise.id, promise.evidence, source="canonical_state.core_promises")
        for contradiction_id in promise.linked_contradictions:
            if contradiction_id:
                edges.append(
                    {
                        "from": promise.id,
                        "to": contradiction_id,
                        "type": "contradicts",
                    }
                )
        for pattern_id in promise.linked_character_patterns:
            if pattern_id:
                edges.append(
                    {
                        "from": promise.id,
                        "to": pattern_id,
                        "type": "supports",
                    }
                )

    for contradiction in state.contradictions:
        nodes.append(_contradiction_node(contradiction))
        add_evidence(
            contradiction.id,
            contradiction.evidence,
            source="canonical_state.contradictions",
        )
        for promise_id in contradiction.linked_promises:
            if promise_id:
                edges.append(
                    {
                        "from": contradiction.id,
                        "to": promise_id,
                        "type": "integrates_through",
                    }
                )

    for node in state.structural_state.planet_conditions:
        nodes.append(_planet_condition_node(node))
        add_evidence(node.id, node.evidence, source="canonical_state.structural_state.planet_conditions")
        for promise_id in node.linked_promises:
            edges.append({"from": node.id, "to": promise_id, "type": "activates_sensitivity"})

    for node in state.structural_state.dispositor_routes:
        nodes.append(_dispositor_route_node(node))
        add_evidence(node.id, node.evidence, source="canonical_state.structural_state.dispositor_routes")
        for promise_id in node.linked_promises:
            edges.append({"from": node.id, "to": promise_id, "type": "routes_through"})

    for node in state.structural_state.house_ruler_routes:
        nodes.append(_house_ruler_route_node(node))
        add_evidence(node.id, node.evidence, source="canonical_state.structural_state.house_ruler_routes")
        for promise_id in node.linked_promises:
            edges.append({"from": node.id, "to": promise_id, "type": "manifests_in"})

    for node in state.structural_state.aspect_patterns:
        nodes.append(_aspect_pattern_node(node))
        add_evidence(node.id, node.evidence, source="canonical_state.structural_state.aspect_patterns")
        for promise_id in node.linked_promises:
            edges.append({"from": node.id, "to": promise_id, "type": "supports"})
        for contradiction_id in node.linked_contradictions:
            edges.append({"from": node.id, "to": contradiction_id, "type": "supports"})

    for line_key in (
        "primary_identity_line",
        "emotional_regulation_line",
        "relational_line",
        "work_visibility_line",
        "shadow_protection_line",
        "growth_integration_line",
    ):
        line = getattr(state.chart_spine, line_key)
        if not line.node_id:
            continue
        nodes.append(_spine_line_node(line_key, line))
        add_evidence(f"spine:{line_key}", list(line.evidence), source=f"canonical_state.chart_spine.{line_key}")
        edges.append(
            {
                "from": line.node_id,
                "to": f"spine:{line_key}",
                "type": "integrates_through",
            }
        )

    activation_hooks = [
        {
            "hook_id": f"hook:{promise.id}",
            "type": "promise_activation",
            "target_node_id": promise.id,
            "domains": [promise.domain],
            "spine_lines": [
                line_key
                for line_key in (
                    "primary_identity_line",
                    "emotional_regulation_line",
                    "relational_line",
                    "work_visibility_line",
                    "shadow_protection_line",
                    "growth_integration_line",
                )
                if getattr(state.chart_spine, line_key).node_id == promise.id
            ],
        }
        for promise in state.core_promises
        if promise.evidence
    ]
    activation_hooks.extend(
        {
            "hook_id": f"hook:{contradiction.id}",
            "type": "contradiction_activation",
            "target_node_id": contradiction.id,
            "domains": ["growth_shadow"],
            "spine_lines": [
                line_key
                for line_key in (
                    "primary_identity_line",
                    "emotional_regulation_line",
                    "relational_line",
                    "work_visibility_line",
                    "shadow_protection_line",
                    "growth_integration_line",
                )
                if getattr(state.chart_spine, line_key).node_id == contradiction.id
            ],
        }
        for contradiction in state.contradictions
        if contradiction.evidence
    )

    return {
        "version": "natal_meaning_graph_v1",
        "canonical_intent": True,
        "nodes": nodes,
        "edges": edges,
        "evidence": evidence,
        "activation_hooks": activation_hooks,
        "meta": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "evidence_count": len(evidence),
            "activation_hook_count": len(activation_hooks),
        },
    }
