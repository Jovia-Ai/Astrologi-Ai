from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Mapping, Sequence

from app.natal.dispositor_engine import extract_aspects, extract_planet_positions
from app.natal.natal_graph_v2 import build_natal_graph_v2

from .natal_selection_config import get_natal_selection_v3_config


_ASPECT_WEIGHTS = {
    "conjunction": 1.0,
    "opposition": 0.92,
    "square": 0.88,
    "trine": 0.78,
    "sextile": 0.68,
}

_IDENTITY_PLANETS = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Saturn", "Uranus"}


def _clamp01(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def _safe_house(value: Any) -> int | None:
    try:
        house = int(value)
    except (TypeError, ValueError):
        return None
    return house if 1 <= house <= 12 else None


def _aspect_exactness(orb: Any, max_orb: float) -> float:
    try:
        orb_value = float(orb)
    except (TypeError, ValueError):
        return 0.0
    if orb_value < 0:
        return 0.0
    return _clamp01(1.0 - (min(orb_value, max_orb) / max_orb))


def _chart_payload(
    chart_data: Mapping[str, Any],
    planets: Sequence[Mapping[str, Any]] | Mapping[str, Any],
    aspects: Sequence[Mapping[str, Any]] | Mapping[str, Any],
) -> Dict[str, Any]:
    if isinstance(planets, Mapping):
        normalized_planets = [
            {**dict(payload), "planet": key}
            for key, payload in planets.items()
            if isinstance(payload, Mapping)
        ]
    else:
        normalized_planets = [dict(item) for item in planets if isinstance(item, Mapping)]
    if isinstance(aspects, Mapping):
        normalized_aspects = [dict(item) for item in aspects.values() if isinstance(item, Mapping)]
    else:
        normalized_aspects = [dict(item) for item in aspects if isinstance(item, Mapping)]
    return {
        **dict(chart_data or {}),
        "planets": normalized_planets,
        "aspects": normalized_aspects,
    }


def _planet_names(planets_map: Mapping[str, Mapping[str, Any]]) -> list[str]:
    return [str(name) for name in planets_map.keys() if str(name).strip()]


def _planet_role_score(house: int | None, houses: Sequence[int]) -> float:
    return 1.0 if house in set(houses) else 0.0


def _compute_chart_ruler_centrality(
    *,
    planet_names: Sequence[str],
    chart_rulers: Mapping[str, Any],
    house_rulers: Mapping[str, Any],
) -> Dict[str, float]:
    asc_primary = str(chart_rulers.get("asc_ruler_primary") or "")
    mc_primary = str(chart_rulers.get("mc_ruler_primary") or "")
    house_rule_counts: Counter[str] = Counter(
        str(payload.get("primary") or "")
        for payload in house_rulers.values()
        if isinstance(payload, Mapping) and str(payload.get("primary") or "").strip()
    )
    scores: Dict[str, float] = {}
    for planet in planet_names:
        score = 0.0
        if planet == asc_primary:
            score += 0.62
        if planet == mc_primary:
            score += 0.36
        score += min(0.22, house_rule_counts.get(planet, 0) * 0.05)
        scores[planet] = round(_clamp01(score), 4)
    return scores


def _compute_angular_dominance(
    *,
    planets_map: Mapping[str, Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, Any],
) -> Dict[str, Any]:
    max_orb = float(thresholds.get("aspect_max_orb") or 6.0)
    by_planet: Dict[str, float] = {}
    house_counter: Counter[int] = Counter()
    for planet, payload in planets_map.items():
        house = _safe_house(payload.get("house"))
        if house is not None:
            house_counter[house] += 1
        score = 0.8 if house in {1, 4, 7, 10} else 0.0
        by_planet[planet] = round(_clamp01(score), 4)

    for aspect in aspects:
        pair = {str(aspect.get("planet1") or ""), str(aspect.get("planet2") or "")}
        angle_points = {"Ascendant", "Midheaven", "Descendant", "Imum Coeli", "ASC", "MC", "DSC", "IC"}
        if not pair.intersection(angle_points):
            continue
        exactness = _aspect_exactness(aspect.get("orb"), max_orb)
        for planet in pair:
            if planet in angle_points:
                continue
            by_planet[planet] = round(_clamp01(float(by_planet.get(planet) or 0.0) + exactness * 0.25), 4)

    global_score = _clamp01(sum(by_planet.values()) / max(len(by_planet), 1))
    return {
        "by_planet": by_planet,
        "global": round(global_score, 4),
        "dominant_houses": [house for house, _count in house_counter.most_common(4)],
    }


def _compute_house_ruler_recursion(
    *,
    house_rulers: Mapping[str, Any],
    chart_rulers: Mapping[str, Any],
    planet_names: Sequence[str],
) -> Dict[str, Any]:
    counts: Counter[str] = Counter()
    for house_key, payload in house_rulers.items():
        if not isinstance(payload, Mapping):
            continue
        primary = str(payload.get("primary") or "")
        if not primary:
            continue
        counts[primary] += 1
        placement = payload.get("placement") if isinstance(payload.get("placement"), Mapping) else {}
        placement_house = _safe_house(placement.get("house"))
        if placement_house in {1, 4, 7, 10}:
            counts[primary] += 1
        if str(house_key) in {"1", "10"}:
            counts[primary] += 1

    by_planet = {
        planet: round(_clamp01((counts.get(planet, 0) / 4.0)), 4)
        for planet in planet_names
    }
    focus = [planet for planet, _count in counts.most_common(4)]
    return {
        "by_planet": by_planet,
        "summary": {
            "dominant_ruler_bodies": focus,
            "asc_ruler": chart_rulers.get("asc_ruler_primary"),
            "mc_ruler": chart_rulers.get("mc_ruler_primary"),
        },
    }


def _compute_dispositor_chain_pressure(
    *,
    chains: Mapping[str, Any],
    loops: Sequence[Mapping[str, Any]],
    planet_names: Sequence[str],
) -> Dict[str, Any]:
    by_planet: Dict[str, float] = {}
    loop_planets = {
        str(planet)
        for payload in loops
        if isinstance(payload, Mapping)
        for planet in (payload.get("planets") or [])
    }
    for planet in planet_names:
        payload = chains.get(planet) if isinstance(chains.get(planet), Mapping) else {}
        chain = payload.get("primary_chain") or payload.get("chain") or []
        termination = str(payload.get("termination_reason") or "")
        score = min(0.48, len(chain) * 0.08)
        if termination == "loop_detected":
            score += 0.32
        elif termination == "domicile":
            score += 0.12
        if planet in loop_planets:
            score += 0.16
        by_planet[planet] = round(_clamp01(score), 4)
    return {
        "by_planet": by_planet,
        "loops": [dict(item) for item in loops if isinstance(item, Mapping)],
        "summary": {
            "loop_count": len(list(loops or [])),
            "dominant_loop_signatures": [str(item.get("signature") or "") for item in loops[:3] if isinstance(item, Mapping)],
        },
    }


def _compute_exact_aspect_salience(
    *,
    aspects: Sequence[Mapping[str, Any]],
    planet_names: Sequence[str],
    thresholds: Mapping[str, Any],
) -> Dict[str, Any]:
    max_orb = float(thresholds.get("aspect_max_orb") or 6.0)
    by_planet: Dict[str, float] = {planet: 0.0 for planet in planet_names}
    density: Counter[str] = Counter()
    major_exact: list[dict[str, Any]] = []
    for aspect in aspects:
        p1 = str(aspect.get("planet1") or "")
        p2 = str(aspect.get("planet2") or "")
        aspect_name = str(aspect.get("aspect") or aspect.get("type") or "").strip().lower()
        if not p1 or not p2 or not aspect_name:
            continue
        exactness = _aspect_exactness(aspect.get("orb"), max_orb)
        weight = _ASPECT_WEIGHTS.get(aspect_name, 0.55)
        contribution = exactness * weight
        by_planet[p1] = round(_clamp01(float(by_planet.get(p1) or 0.0) + contribution), 4)
        by_planet[p2] = round(_clamp01(float(by_planet.get(p2) or 0.0) + contribution), 4)
        density[p1] += 1
        density[p2] += 1
        if contribution >= 0.42:
            major_exact.append(
                {
                    "planet1": p1,
                    "planet2": p2,
                    "aspect": aspect_name,
                    "orb": aspect.get("orb"),
                    "score": round(contribution, 4),
                }
            )
    density_scores = {
        planet: round(_clamp01((density.get(planet, 0) / 6.0)), 4)
        for planet in planet_names
    }
    return {
        "by_planet": by_planet,
        "density_by_planet": density_scores,
        "summary": {"major_exact_aspects": major_exact[:8]},
    }


def _compute_repeated_motif_count(
    *,
    motifs: Sequence[Mapping[str, Any]],
    planet_names: Sequence[str],
    thresholds: Mapping[str, Any],
) -> Dict[str, Any]:
    minimum = float(thresholds.get("motif_min_score") or 0.18)
    counts: Counter[str] = Counter()
    dominant_motifs: list[dict[str, Any]] = []
    lowered_names = {planet.lower(): planet for planet in planet_names}
    for motif in motifs:
        if not isinstance(motif, Mapping):
            continue
        score = float(motif.get("score") or 0.0)
        if score < minimum:
            continue
        dominant_motifs.append(
            {
                "id": str(motif.get("id") or ""),
                "score": round(score, 4),
                "evidence": list(motif.get("evidence") or []),
            }
        )
        evidence = [str(item).lower() for item in motif.get("evidence") or []]
        support = [str(item).lower() for item in motif.get("dispositor_support") or []]
        combined = " ".join([*evidence, *support])
        for lowered, planet in lowered_names.items():
            if lowered in combined:
                counts[planet] += 1
    by_planet = {
        planet: round(_clamp01(counts.get(planet, 0) / 3.0), 4)
        for planet in planet_names
    }
    return {
        "by_planet": by_planet,
        "motif_ids": [item["id"] for item in dominant_motifs],
        "dominant_motifs": dominant_motifs[:8],
    }


def _compute_public_private_split(
    *,
    planets_map: Mapping[str, Mapping[str, Any]],
    motif_ids: Sequence[str],
    thresholds: Mapping[str, Any],
) -> Dict[str, Any]:
    public_houses = [int(item) for item in thresholds.get("public_houses") or [1, 7, 10, 11]]
    private_houses = [int(item) for item in thresholds.get("private_houses") or [4, 8, 12]]
    public_score = 0.0
    private_score = 0.0
    by_planet: Dict[str, Dict[str, Any]] = {}
    for planet, payload in planets_map.items():
        house = _safe_house(payload.get("house"))
        public_component = _planet_role_score(house, public_houses)
        private_component = _planet_role_score(house, private_houses)
        if planet == "Sun":
            public_component += 0.2
        if planet == "Moon":
            private_component += 0.2
        if planet == "Saturn":
            private_component += 0.1
        if planet == "Midheaven":
            public_component += 0.2
        public_component = _clamp01(public_component)
        private_component = _clamp01(private_component)
        public_score += public_component
        private_score += private_component
        if public_component > private_component + 0.15:
            role = "public"
        elif private_component > public_component + 0.15:
            role = "private"
        else:
            role = "bridge"
        by_planet[planet] = {
            "public": round(public_component, 4),
            "private": round(private_component, 4),
            "role": role,
        }
    if any(motif_id in {"mature_visibility", "identity_structure", "public_refinement"} for motif_id in motif_ids):
        public_score += 0.45
    if any(motif_id in {"thresholded_intimacy", "depth_intimacy", "private_intellect"} for motif_id in motif_ids):
        private_score += 0.45
    public_score = round(_clamp01(public_score / max(len(planets_map), 1)), 4)
    private_score = round(_clamp01(private_score / max(len(planets_map), 1)), 4)
    if public_score > private_score + 0.1:
        dominant = "public"
    elif private_score > public_score + 0.1:
        dominant = "private"
    else:
        dominant = "balanced"
    return {
        "public_score": public_score,
        "private_score": private_score,
        "balance": round(abs(public_score - private_score), 4),
        "dominant": dominant,
        "by_planet": by_planet,
    }


def _compute_contradiction_polarity(
    *,
    public_private_split: Mapping[str, Any],
    motifs: Sequence[Mapping[str, Any]],
    planet_salience_inputs: Mapping[str, float],
) -> list[dict[str, Any]]:
    motif_scores = {
        str(item.get("id") or ""): float(item.get("score") or 0.0)
        for item in motifs
        if isinstance(item, Mapping)
    }
    contradictions: list[dict[str, Any]] = []
    visibility_private = min(
        float(public_private_split.get("public_score") or 0.0),
        float(public_private_split.get("private_score") or 0.0),
    )
    if visibility_private >= 0.42:
        contradictions.append(
            {
                "id": "visibility_vs_private_preparation",
                "score": round(visibility_private, 4),
                "left": "visibility",
                "right": "private_preparation",
                "evidence": ["public_private_split", "dual_surface_activation"],
            }
        )
    closeness_threshold = min(
        motif_scores.get("depth_intimacy", 0.0),
        max(motif_scores.get("thresholded_intimacy", 0.0), planet_salience_inputs.get("Moon", 0.0) * 0.6),
    )
    if closeness_threshold >= 0.26:
        contradictions.append(
            {
                "id": "closeness_vs_threshold",
                "score": round(closeness_threshold, 4),
                "left": "closeness",
                "right": "trust_threshold",
                "evidence": ["depth_intimacy", "thresholded_intimacy"],
            }
        )
    structure_originality = min(
        max(planet_salience_inputs.get("Saturn", 0.0), motif_scores.get("identity_structure", 0.0)),
        max(planet_salience_inputs.get("Uranus", 0.0), motif_scores.get("visionary_originality", 0.0)),
    )
    if structure_originality >= 0.26:
        contradictions.append(
            {
                "id": "structure_vs_originality",
                "score": round(structure_originality, 4),
                "left": "structure",
                "right": "originality",
                "evidence": ["identity_structure", "visionary_originality"],
            }
        )
    composed_pressure = min(
        max(planet_salience_inputs.get("Saturn", 0.0), planet_salience_inputs.get("Sun", 0.0)),
        float(public_private_split.get("private_score") or 0.0),
    )
    if composed_pressure >= 0.28:
        contradictions.append(
            {
                "id": "composure_vs_internal_pressure",
                "score": round(composed_pressure, 4),
                "left": "composure",
                "right": "internal_pressure",
                "evidence": ["saturn_salience", "private_score"],
            }
        )
    return sorted(contradictions, key=lambda item: (-float(item.get("score") or 0.0), str(item.get("id") or "")))


def _compute_compensation_patterns(
    *,
    contradictions: Sequence[Mapping[str, Any]],
    planet_salience_inputs: Mapping[str, float],
    public_private_split: Mapping[str, Any],
) -> list[dict[str, Any]]:
    contradiction_scores = {str(item.get("id") or ""): float(item.get("score") or 0.0) for item in contradictions}
    patterns: list[dict[str, Any]] = []
    structure_for_originality = min(
        contradiction_scores.get("structure_vs_originality", 0.0),
        max(planet_salience_inputs.get("Saturn", 0.0), planet_salience_inputs.get("Mercury", 0.0)),
    )
    if structure_for_originality >= 0.2:
        patterns.append(
            {
                "id": "structure_scaffolds_originality",
                "score": round(structure_for_originality, 4),
                "evidence": ["structure_vs_originality", "saturn_mercury_support"],
            }
        )
    preparation_for_visibility = min(
        contradiction_scores.get("visibility_vs_private_preparation", 0.0),
        float(public_private_split.get("private_score") or 0.0),
    )
    if preparation_for_visibility >= 0.2:
        patterns.append(
            {
                "id": "private_preparation_before_visibility",
                "score": round(preparation_for_visibility, 4),
                "evidence": ["visibility_vs_private_preparation", "private_score"],
            }
        )
    threshold_for_closeness = min(
        contradiction_scores.get("closeness_vs_threshold", 0.0),
        max(planet_salience_inputs.get("Moon", 0.0), planet_salience_inputs.get("Venus", 0.0)),
    )
    if threshold_for_closeness >= 0.2:
        patterns.append(
            {
                "id": "trust_threshold_regulates_closeness",
                "score": round(threshold_for_closeness, 4),
                "evidence": ["closeness_vs_threshold", "moon_venus_salience"],
            }
        )
    return patterns


def build_natal_feature_graph(
    *,
    chart_data: Mapping[str, Any],
    planets: Sequence[Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
    natal_graph_v2: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    config = get_natal_selection_v3_config()
    thresholds = config.get("thresholds") if isinstance(config.get("thresholds"), Mapping) else {}
    weights = (config.get("weights") or {}).get("planet_salience") if isinstance(config.get("weights"), Mapping) else {}
    chart = _chart_payload(chart_data, planets, aspects)
    graph_v2 = natal_graph_v2 if isinstance(natal_graph_v2, Mapping) and natal_graph_v2 else build_natal_graph_v2(chart, natal_graph=dict(natal_graph or {}))
    planets_map = extract_planet_positions(chart, natal_graph)
    aspects_list = extract_aspects(chart, natal_graph)
    planet_names = _planet_names(planets_map)
    importance = natal_graph.get("importance") if isinstance(natal_graph.get("importance"), Mapping) else {}
    chart_rulers = graph_v2.get("chart_rulers") if isinstance(graph_v2.get("chart_rulers"), Mapping) else {}
    house_rulers = chart_rulers.get("house_rulers") if isinstance(chart_rulers.get("house_rulers"), Mapping) else {}
    motifs = graph_v2.get("signature_motifs") if isinstance(graph_v2.get("signature_motifs"), Sequence) else []
    chains = graph_v2.get("dispositor_chains") if isinstance(graph_v2.get("dispositor_chains"), Mapping) else {}
    loops = natal_graph.get("dominant_loops") if isinstance(natal_graph.get("dominant_loops"), Sequence) else []

    chart_ruler_centrality = _compute_chart_ruler_centrality(
        planet_names=planet_names,
        chart_rulers=chart_rulers,
        house_rulers=house_rulers,
    )
    angular_dominance = _compute_angular_dominance(
        planets_map=planets_map,
        aspects=aspects_list,
        thresholds=thresholds,
    )
    house_ruler_recursion = _compute_house_ruler_recursion(
        house_rulers=house_rulers,
        chart_rulers=chart_rulers,
        planet_names=planet_names,
    )
    dispositor_chain_pressure = _compute_dispositor_chain_pressure(
        chains=chains,
        loops=loops,
        planet_names=planet_names,
    )
    exact_aspect_salience = _compute_exact_aspect_salience(
        aspects=aspects_list,
        planet_names=planet_names,
        thresholds=thresholds,
    )
    repeated_motif_count = _compute_repeated_motif_count(
        motifs=motifs,
        planet_names=planet_names,
        thresholds=thresholds,
    )
    public_private_split = _compute_public_private_split(
        planets_map=planets_map,
        motif_ids=repeated_motif_count.get("motif_ids") or [],
        thresholds=thresholds,
    )

    luminary_condition = {
        "Sun": round(
            _clamp01(
                (
                    float(importance.get("Sun") or 0.0)
                    + float(angular_dominance["by_planet"].get("Sun") or 0.0)
                    + float(exact_aspect_salience["by_planet"].get("Sun") or 0.0)
                )
                / 3.0
            ),
            4,
        ),
        "Moon": round(
            _clamp01(
                (
                    float(importance.get("Moon") or 0.0)
                    + float(angular_dominance["by_planet"].get("Moon") or 0.0)
                    + float(exact_aspect_salience["by_planet"].get("Moon") or 0.0)
                )
                / 3.0
            ),
            4,
        ),
    }

    contradiction_polarity = _compute_contradiction_polarity(
        public_private_split=public_private_split,
        motifs=motifs,
        planet_salience_inputs={
            planet: max(
                float(importance.get(planet) or 0.0),
                float(exact_aspect_salience["by_planet"].get(planet) or 0.0),
            )
            for planet in planet_names
        },
    )
    compensation_patterns = _compute_compensation_patterns(
        contradictions=contradiction_polarity,
        planet_salience_inputs={
            planet: max(
                float(importance.get(planet) or 0.0),
                float(angular_dominance["by_planet"].get(planet) or 0.0),
            )
            for planet in planet_names
        },
        public_private_split=public_private_split,
    )

    contradiction_bonus = min(
        1.0,
        sum(float(item.get("score") or 0.0) for item in contradiction_polarity[:2]) / 1.4,
    )

    planet_salience: Dict[str, Dict[str, Any]] = {}
    for planet in planet_names:
        house = _safe_house(planets_map.get(planet, {}).get("house"))
        role_payload = public_private_split.get("by_planet", {}).get(planet, {})
        components = {
            "angularity": float(angular_dominance["by_planet"].get(planet) or 0.0),
            "chart_ruler_centrality": float(chart_ruler_centrality.get(planet) or 0.0),
            "luminary_condition": float(luminary_condition.get(planet) or 0.0),
            "aspect_density": float(exact_aspect_salience["density_by_planet"].get(planet) or 0.0),
            "exact_aspect_salience": float(exact_aspect_salience["by_planet"].get(planet) or 0.0),
            "dispositor_chain_pressure": float(dispositor_chain_pressure["by_planet"].get(planet) or 0.0),
            "motif_density": float(repeated_motif_count["by_planet"].get(planet) or 0.0),
            "contradiction_polarity": contradiction_bonus,
            "public_private_split": max(
                float(role_payload.get("public") or 0.0),
                float(role_payload.get("private") or 0.0),
            ),
            "house_ruler_recursion": float(house_ruler_recursion["by_planet"].get(planet) or 0.0),
        }
        total = float(weights.get("base") or 0.22)
        for key, value in components.items():
            total += float(weights.get(key) or 0.0) * value
        planet_salience[planet] = {
            "score": round(_clamp01(total), 4),
            "house": house,
            "role": str(role_payload.get("role") or "bridge"),
            "components": {key: round(value, 4) for key, value in components.items()},
        }

    dominant_planets = sorted(
        (
            {"planet": planet, "score": payload["score"], "role": payload["role"]}
            for planet, payload in planet_salience.items()
            if planet in _IDENTITY_PLANETS
        ),
        key=lambda item: (-float(item.get("score") or 0.0), str(item.get("planet") or "")),
    )[:6]

    return {
        "engine_version": "natal_feature_graph_v2",
        "config_version": str(config.get("engine_version") or "natal_selection_v3_config_v1"),
        "planet_salience": planet_salience,
        "chart_ruler_centrality": chart_ruler_centrality,
        "luminary_condition": luminary_condition,
        "angular_dominance": angular_dominance,
        "house_ruler_recursion": house_ruler_recursion,
        "dispositor_chain_pressure": dispositor_chain_pressure,
        "exact_aspect_salience": exact_aspect_salience,
        "repeated_motif_count": repeated_motif_count,
        "contradiction_polarity": contradiction_polarity,
        "compensation_patterns": compensation_patterns,
        "public_private_split": public_private_split,
        "voice_inputs": {
            "public_private_split": {
                "dominant": public_private_split.get("dominant"),
                "balance": public_private_split.get("balance"),
            },
            "structurality": round(
                _clamp01(
                    max(
                        float(planet_salience.get("Saturn", {}).get("score") or 0.0),
                        float(house_ruler_recursion["by_planet"].get("Saturn") or 0.0),
                    )
                ),
                4,
            ),
            "emotional_threshold": round(
                _clamp01(
                    max(
                        next(
                            (
                                float(item.get("score") or 0.0)
                                for item in contradiction_polarity
                                if str(item.get("id") or "") == "closeness_vs_threshold"
                            ),
                            0.0,
                        ),
                        float(luminary_condition.get("Moon") or 0.0) * 0.65,
                    )
                ),
                4,
            ),
        },
        "debug": {
            "config_path": config.get("config_path"),
            "dominant_planets": dominant_planets,
            "source_motif_ids": repeated_motif_count.get("motif_ids") or [],
        },
    }
