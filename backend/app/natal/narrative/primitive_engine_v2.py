from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from app.natal.narrative.primitive_engine import build_primitives
from app.natal.narrative.signature_engine import normalize_facts

from .natal_feature_graph import build_natal_feature_graph
from .natal_selection_config import get_natal_selection_v3_config


_PRIMITIVE_CATEGORY = {
    "self_definition": "identity",
    "visible_presence": "identity",
    "inner_structure": "regulation",
    "originality_drive": "identity",
    "big_picture_vision": "identity",
    "tone_sensitivity": "regulation",
    "systems_thinking": "regulation",
    "inner_critic": "shadow",
    "push_pull_drive": "shadow",
    "methodical_drive": "regulation",
    "mental_structuring": "regulation",
    "intimacy_depth": "relational",
    "relational_security": "relational",
    "graceful_affection": "relational",
    "transformative_bonding": "relational",
    "emotional_threshold": "shadow",
    "public_refinement": "visibility",
    "visibility_sensitivity": "visibility",
    "backstage_creation": "visibility",
    "recharge_through_home": "compensation",
    "family_self_reliance": "compensation",
    "creation_luck": "visibility",
    "network_luck": "visibility",
    "meaningful_expansion": "identity",
}

_PRIMITIVE_POLARITY = {
    "self_definition": "stabilizing",
    "visible_presence": "expressive",
    "inner_structure": "stabilizing",
    "originality_drive": "expansive",
    "big_picture_vision": "expansive",
    "tone_sensitivity": "protective",
    "systems_thinking": "stabilizing",
    "inner_critic": "contractive",
    "push_pull_drive": "tensional",
    "methodical_drive": "stabilizing",
    "mental_structuring": "stabilizing",
    "intimacy_depth": "receptive",
    "relational_security": "protective",
    "graceful_affection": "receptive",
    "transformative_bonding": "tensional",
    "emotional_threshold": "protective",
    "public_refinement": "expressive",
    "visibility_sensitivity": "protective",
    "backstage_creation": "protective",
    "recharge_through_home": "restorative",
    "family_self_reliance": "restorative",
    "creation_luck": "expressive",
    "network_luck": "expansive",
    "meaningful_expansion": "expansive",
}

_PRIMITIVE_PLANETS = {
    "self_definition": ["Sun", "Ascendant", "Saturn"],
    "visible_presence": ["Sun", "Midheaven"],
    "inner_structure": ["Saturn", "Mercury"],
    "originality_drive": ["Uranus", "Sun"],
    "big_picture_vision": ["Jupiter", "Neptune"],
    "tone_sensitivity": ["Mercury", "Saturn"],
    "systems_thinking": ["Mercury", "Saturn"],
    "inner_critic": ["Saturn", "Sun"],
    "push_pull_drive": ["Mars", "Saturn"],
    "methodical_drive": ["Mars", "Saturn", "Mercury"],
    "mental_structuring": ["Mercury", "Saturn"],
    "intimacy_depth": ["Moon", "Venus", "Pluto"],
    "relational_security": ["Moon", "Venus", "Saturn"],
    "graceful_affection": ["Moon", "Venus"],
    "transformative_bonding": ["Moon", "Pluto"],
    "emotional_threshold": ["Moon", "Saturn"],
    "public_refinement": ["Midheaven", "Sun", "Saturn"],
    "visibility_sensitivity": ["Midheaven", "Neptune", "Chiron"],
    "backstage_creation": ["Venus", "Neptune", "Moon"],
    "recharge_through_home": ["Moon", "Saturn"],
    "family_self_reliance": ["Mars", "Moon"],
    "creation_luck": ["Jupiter", "Fortune", "Sun"],
    "network_luck": ["Jupiter", "Mercury", "Venus"],
    "meaningful_expansion": ["Jupiter", "Neptune", "Mars"],
}

_PRIMITIVE_COUNTERWEIGHTS = {
    "inner_structure": ["originality_drive"],
    "originality_drive": ["inner_structure"],
    "intimacy_depth": ["emotional_threshold"],
    "emotional_threshold": ["intimacy_depth"],
    "visible_presence": ["backstage_creation"],
    "backstage_creation": ["visible_presence"],
    "push_pull_drive": ["methodical_drive"],
    "methodical_drive": ["push_pull_drive"],
}

_PRIMITIVE_FEATURES = {
    "self_definition": ["chart_ruler_centrality", "angular_dominance", "public_private_split"],
    "visible_presence": ["angular_dominance", "public_private_split", "exact_aspect_salience"],
    "inner_structure": ["chart_ruler_centrality", "house_ruler_recursion", "dispositor_chain_pressure"],
    "originality_drive": ["angular_dominance", "contradiction_polarity", "compensation_patterns"],
    "big_picture_vision": ["repeated_motif_count", "exact_aspect_salience", "public_private_split"],
    "tone_sensitivity": ["dispositor_chain_pressure", "exact_aspect_salience", "public_private_split"],
    "systems_thinking": ["house_ruler_recursion", "dispositor_chain_pressure", "repeated_motif_count"],
    "inner_critic": ["dispositor_chain_pressure", "contradiction_polarity", "public_private_split"],
    "push_pull_drive": ["contradiction_polarity", "exact_aspect_salience", "dispositor_chain_pressure"],
    "methodical_drive": ["house_ruler_recursion", "compensation_patterns", "exact_aspect_salience"],
    "mental_structuring": ["house_ruler_recursion", "dispositor_chain_pressure", "public_private_split"],
    "intimacy_depth": ["repeated_motif_count", "public_private_split", "contradiction_polarity"],
    "relational_security": ["repeated_motif_count", "public_private_split", "compensation_patterns"],
    "graceful_affection": ["exact_aspect_salience", "public_private_split"],
    "transformative_bonding": ["repeated_motif_count", "contradiction_polarity"],
    "emotional_threshold": ["public_private_split", "contradiction_polarity", "dispositor_chain_pressure"],
    "public_refinement": ["chart_ruler_centrality", "angular_dominance", "public_private_split"],
    "visibility_sensitivity": ["public_private_split", "contradiction_polarity", "exact_aspect_salience"],
    "backstage_creation": ["public_private_split", "compensation_patterns", "repeated_motif_count"],
    "recharge_through_home": ["public_private_split", "compensation_patterns"],
    "family_self_reliance": ["compensation_patterns", "public_private_split"],
    "creation_luck": ["repeated_motif_count", "public_private_split", "angular_dominance"],
    "network_luck": ["public_private_split", "repeated_motif_count"],
    "meaningful_expansion": ["repeated_motif_count", "exact_aspect_salience", "public_private_split"],
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


def _feature_bucket_score(
    primitive_id: str,
    natal_feature_graph: Mapping[str, Any],
) -> tuple[float, list[str]]:
    source_features: list[str] = []
    values: list[float] = []
    for bucket in _PRIMITIVE_FEATURES.get(primitive_id, []):
        value = 0.0
        if bucket == "chart_ruler_centrality":
            related = [float((natal_feature_graph.get("chart_ruler_centrality") or {}).get(planet) or 0.0) for planet in _PRIMITIVE_PLANETS.get(primitive_id, [])]
            value = _safe_avg(related)
        elif bucket == "angular_dominance":
            related = [float(((natal_feature_graph.get("angular_dominance") or {}).get("by_planet") or {}).get(planet) or 0.0) for planet in _PRIMITIVE_PLANETS.get(primitive_id, [])]
            value = max(_safe_avg(related), float((natal_feature_graph.get("angular_dominance") or {}).get("global") or 0.0) * 0.6)
        elif bucket == "house_ruler_recursion":
            related = [float(((natal_feature_graph.get("house_ruler_recursion") or {}).get("by_planet") or {}).get(planet) or 0.0) for planet in _PRIMITIVE_PLANETS.get(primitive_id, [])]
            value = _safe_avg(related)
        elif bucket == "dispositor_chain_pressure":
            related = [float(((natal_feature_graph.get("dispositor_chain_pressure") or {}).get("by_planet") or {}).get(planet) or 0.0) for planet in _PRIMITIVE_PLANETS.get(primitive_id, [])]
            value = _safe_avg(related)
        elif bucket == "exact_aspect_salience":
            related = [float(((natal_feature_graph.get("exact_aspect_salience") or {}).get("by_planet") or {}).get(planet) or 0.0) for planet in _PRIMITIVE_PLANETS.get(primitive_id, [])]
            value = _safe_avg(related)
        elif bucket == "repeated_motif_count":
            related = [float(((natal_feature_graph.get("repeated_motif_count") or {}).get("by_planet") or {}).get(planet) or 0.0) for planet in _PRIMITIVE_PLANETS.get(primitive_id, [])]
            value = _safe_avg(related)
        elif bucket == "public_private_split":
            public_private = natal_feature_graph.get("public_private_split") or {}
            if primitive_id in {"backstage_creation", "recharge_through_home", "family_self_reliance", "emotional_threshold", "intimacy_depth", "relational_security"}:
                value = float(public_private.get("private_score") or 0.0)
            elif primitive_id in {"public_refinement", "visible_presence", "creation_luck", "network_luck"}:
                value = float(public_private.get("public_score") or 0.0)
            else:
                value = max(float(public_private.get("public_score") or 0.0), float(public_private.get("private_score") or 0.0))
        elif bucket == "contradiction_polarity":
            contradiction_scores = [
                float(item.get("score") or 0.0)
                for item in natal_feature_graph.get("contradiction_polarity") or []
                if isinstance(item, Mapping)
            ]
            value = max(contradiction_scores, default=0.0)
        elif bucket == "compensation_patterns":
            compensation_scores = [
                float(item.get("score") or 0.0)
                for item in natal_feature_graph.get("compensation_patterns") or []
                if isinstance(item, Mapping)
            ]
            value = max(compensation_scores, default=0.0)
        values.append(value)
        if value > 0.0:
            source_features.append(bucket)
    return round(_clamp01(_safe_avg(values)), 4), source_features


def _salience_score(
    primitive_id: str,
    natal_feature_graph: Mapping[str, Any],
) -> float:
    related_planets = _PRIMITIVE_PLANETS.get(primitive_id, [])
    scores = [
        float((natal_feature_graph.get("planet_salience") or {}).get(planet, {}).get("score") or 0.0)
        for planet in related_planets
    ]
    return round(_clamp01(_safe_avg(scores)), 4)


def _build_ranking_diff(
    legacy_hits: Sequence[Mapping[str, Any]],
    rescored_hits: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    legacy_positions = {
        str(item.get("primitive_id") or ""): index
        for index, item in enumerate(legacy_hits, start=1)
        if isinstance(item, Mapping)
    }
    new_positions = {
        str(item.get("primitive_id") or ""): index
        for index, item in enumerate(rescored_hits, start=1)
        if isinstance(item, Mapping)
    }
    shifts = []
    for primitive_id, new_position in new_positions.items():
        old_position = legacy_positions.get(primitive_id)
        if old_position is None:
            continue
        delta = old_position - new_position
        if delta == 0:
            continue
        shifts.append(
            {
                "primitive_id": primitive_id,
                "legacy_rank": old_position,
                "new_rank": new_position,
                "delta": delta,
            }
        )
    return {
        "rank_shifts": shifts[:10],
        "legacy_top_ids": [str(item.get("primitive_id") or "") for item in legacy_hits[:5] if isinstance(item, Mapping)],
        "v2_top_ids": [str(item.get("primitive_id") or "") for item in rescored_hits[:5] if isinstance(item, Mapping)],
    }


def build_primitives_v2(
    chart: Mapping[str, Any],
    *,
    natal_graph: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any] | None = None,
    natal_graph_v2: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    _ = natal_graph_v2
    config = get_natal_selection_v3_config()
    weights = (config.get("weights") or {}).get("primitive_v2") if isinstance(config.get("weights"), Mapping) else {}
    feature_graph = natal_feature_graph if isinstance(natal_feature_graph, Mapping) and natal_feature_graph else build_natal_feature_graph(
        chart_data=chart,
        planets=chart.get("planets") or [],
        aspects=chart.get("aspects") or [],
        natal_graph=natal_graph,
        natal_graph_v2=natal_graph_v2,
    )
    facts = normalize_facts(chart, natal_graph)
    legacy_hits = build_primitives(chart, natal_graph, facts=facts)
    rescored_hits: list[dict[str, Any]] = []

    for hit in legacy_hits:
        primitive_id = str(hit.get("primitive_id") or "")
        legacy_score = float(hit.get("score") or 0.0)
        feature_support, source_features = _feature_bucket_score(primitive_id, feature_graph)
        salience = _salience_score(primitive_id, feature_graph)
        score = (
            legacy_score * float(weights.get("legacy_score_weight") or 0.44)
            + feature_support * float(weights.get("feature_support_weight") or 0.36)
            + salience * float(weights.get("salience_weight") or 0.20)
        )
        confidence = _clamp01(0.42 + feature_support * 0.34 + salience * 0.24)
        rescored_hits.append(
            {
                **dict(hit),
                "category": _PRIMITIVE_CATEGORY.get(primitive_id, "identity"),
                "polarity": _PRIMITIVE_POLARITY.get(primitive_id, "stabilizing"),
                "related_planets": list(_PRIMITIVE_PLANETS.get(primitive_id, [])),
                "legacy_score": round(legacy_score, 4),
                "feature_support": round(feature_support, 4),
                "salience": round(salience, 4),
                "confidence": round(confidence, 4),
                "score": round(_clamp01(score), 4),
                "source_features": source_features,
                "counterweights": list(_PRIMITIVE_COUNTERWEIGHTS.get(primitive_id, [])),
            }
        )

    rescored_hits.sort(key=lambda item: (-float(item.get("score") or 0.0), str(item.get("primitive_id") or "")))
    grouped: Dict[str, list[dict[str, Any]]] = {
        "identity": [],
        "regulation": [],
        "relational": [],
        "visibility": [],
        "shadow": [],
        "compensation": [],
    }
    for hit in rescored_hits:
        grouped.setdefault(str(hit.get("category") or "identity"), []).append(hit)

    return {
        "engine_version": "primitive_engine_v2",
        "config_version": str(config.get("engine_version") or "natal_selection_v3_config_v1"),
        "primitive_scores": rescored_hits,
        "top_primitives": rescored_hits[:8],
        "shadow_primitives": grouped.get("shadow", [])[:4],
        "relational_primitives": grouped.get("relational", [])[:4],
        "visibility_primitives": grouped.get("visibility", [])[:4],
        "compensation_primitives": grouped.get("compensation", [])[:4],
        "grouped": grouped,
        "ranking_diff": _build_ranking_diff(legacy_hits, rescored_hits),
    }

