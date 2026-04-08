from __future__ import annotations

import copy
import re
from typing import Any, Dict, Iterable, List, Mapping, Sequence

SUPPORT_VERSION = "natal_category_support_v1"

CATEGORY_FAMILY_BY_ID: Dict[str, str] = {
    "identity_aura": "identity",
    "identity_mechanics": "identity",
    "mind_voice": "mind",
    "mind_system": "mind",
    "drive_rhythm": "drive",
    "love_depth": "intimacy",
    "relationships": "intimacy",
    "relationships_depth": "intimacy",
    "career_visibility": "visibility",
    "home_roots": "home",
    "luck_creation": "opportunity",
}

_CANONICAL_ID_BY_FAMILY = {
    "identity": "identity_aura",
    "mind": "mind_voice",
    "drive": "drive_rhythm",
    "intimacy": "love_depth",
    "visibility": "career_visibility",
    "home": "home_roots",
    "opportunity": "luck_creation",
}

_FAMILY_SPECS: Dict[str, Dict[str, Any]] = {
    "identity": {
        "angle": "ASC",
        "anchor_houses": {1},
        "route_houses": {1},
        "route_preferred_houses": {1, 10},
        "anchor_planets": {"Sun", "Ascendant", "Saturn", "Uranus", "Jupiter", "Neptune"},
        "support_planets": {"Sun", "Ascendant", "Saturn", "Uranus", "Jupiter", "Neptune", "Mercury"},
        "contradictions": {"structure_vs_originality", "composure_vs_internal_pressure"},
        "motifs": {"identity_structure", "visionary_originality", "visibility_sensitivity"},
        "slot_biases": {"primary_identity_spine"},
    },
    "mind": {
        "anchor_houses": {3},
        "route_houses": {3},
        "route_preferred_houses": {1, 3, 6, 9},
        "anchor_planets": {"Mercury", "Saturn", "Mars", "Uranus"},
        "support_planets": {"Mercury", "Saturn", "Mars", "Uranus", "Jupiter", "Moon"},
        "contradictions": {"speed_vs_control", "composure_vs_internal_pressure"},
        "motifs": {"language_boundary", "private_intellect", "mentalized_emotion", "system_builder"},
        "slot_biases": {"secondary_balancing_line"},
    },
    "drive": {
        "anchor_houses": {6, 9, 10},
        "route_houses": {6, 9, 10},
        "route_preferred_houses": {1, 6, 9, 10},
        "anchor_planets": {"Mars", "Saturn", "Uranus", "Jupiter", "Neptune"},
        "support_planets": {"Mars", "Saturn", "Uranus", "Jupiter", "Neptune", "Mercury"},
        "contradictions": {"speed_vs_control", "structure_vs_originality"},
        "motifs": {"push_pull_drive", "system_builder", "creative_flow", "visionary_originality"},
        "slot_biases": {"secondary_balancing_line"},
    },
    "intimacy": {
        "anchor_houses": {7, 8, 12},
        "route_houses": {7, 8},
        "route_preferred_houses": {7, 8, 12},
        "anchor_planets": {"Moon", "Venus", "Pluto", "Saturn"},
        "support_planets": {"Moon", "Venus", "Pluto", "Saturn", "Lilith", "Neptune"},
        "contradictions": {"closeness_vs_threshold"},
        "motifs": {
            "depth_intimacy",
            "thresholded_intimacy",
            "selective_bonding",
            "depth_guardedness",
            "hidden_devotion",
            "soft_bonding",
        },
        "slot_biases": {"relational_line", "shadow_protection_line"},
    },
    "visibility": {
        "angle": "MC",
        "anchor_houses": {10, 11},
        "route_houses": {10},
        "route_preferred_houses": {1, 10, 11},
        "anchor_planets": {"Sun", "Jupiter", "Neptune", "Midheaven", "Chiron", "Saturn"},
        "support_planets": {"Sun", "Jupiter", "Neptune", "Midheaven", "Chiron", "Saturn", "Uranus"},
        "contradictions": {"visibility_vs_private_preparation", "composure_vs_internal_pressure"},
        "motifs": {"visibility_sensitivity", "identity_structure", "social_fire_private_core"},
        "slot_biases": {"work_visibility_line", "shadow_protection_line"},
    },
    "home": {
        "angle": "IC",
        "anchor_houses": {4, 12},
        "route_houses": {4},
        "route_preferred_houses": {4, 12},
        "anchor_planets": {"Moon", "Saturn", "IC"},
        "support_planets": {"Moon", "Saturn", "Venus", "Neptune", "IC"},
        "contradictions": {"visibility_vs_private_preparation"},
        "motifs": {"independent_roots", "hidden_creation"},
        "slot_biases": {"shadow_protection_line"},
    },
    "opportunity": {
        "anchor_houses": {2, 5, 10},
        "route_houses": {5, 2, 10},
        "route_preferred_houses": {1, 2, 5, 10},
        "anchor_planets": {"Fortune", "Jupiter", "Venus", "Sun"},
        "support_planets": {"Fortune", "Jupiter", "Venus", "Sun", "Neptune", "Mars"},
        "contradictions": {"visibility_vs_private_preparation"},
        "motifs": {"creative_flow", "hidden_creation", "visionary_originality"},
        "slot_biases": {"work_visibility_line"},
    },
}

_CONTRADICTION_LABELS = {
    "visibility_vs_private_preparation": "visibility vs private preparation",
    "closeness_vs_threshold": "closeness vs threshold",
    "structure_vs_originality": "structure vs originality",
    "composure_vs_internal_pressure": "composure vs internal pressure",
    "speed_vs_control": "speed vs control",
}

_ANGLE_ALIAS_TO_PLANET = {
    "ASC": "Ascendant",
    "MC": "Midheaven",
    "DSC": "Descendant",
    "IC": "Imum Coeli",
}

_ASPECT_ALIASES = {
    "conjunction": "conjunction",
    "conj": "conjunction",
    "opposition": "opposition",
    "opp": "opposition",
    "opposite": "opposition",
    "square": "square",
    "trine": "trine",
    "sextile": "sextile",
}

_ANGLE_BASE_SCORE = 0.46
_ROUTE_BASE_SCORE = 0.38
_PLACEMENT_BASE_SCORE = 0.24
_ASPECT_BASE_SCORE = 0.22
_HOUSE_EMPHASIS_BASE_SCORE = 0.24
_PRIMARY_THRESHOLD = 0.54
_SUPPORT_THRESHOLD = 0.46
_HIDDEN_THRESHOLD = 0.38
_CONTRADICTION_THRESHOLD = 0.58
_MOTIF_THRESHOLD = 0.20


def build_natal_category_support_bundle(
    *,
    chart_data: Mapping[str, Any],
    planets: Sequence[Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any] | None = None,
    contradiction_signatures: Mapping[str, Any] | None = None,
    master_selector: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    by_family: Dict[str, Dict[str, Any]] = {}
    for family in _CANONICAL_ID_BY_FAMILY:
        support = _build_family_support(
            family=family,
            chart_data=chart_data,
            planets=planets,
            aspects=aspects,
            natal_graph=natal_graph,
            natal_feature_graph=natal_feature_graph,
            contradiction_signatures=contradiction_signatures,
            master_selector=master_selector,
        )
        if support:
            by_family[family] = support

    by_id: Dict[str, Dict[str, Any]] = {}
    for category_id, family in CATEGORY_FAMILY_BY_ID.items():
        family_support = by_family.get(family)
        if not family_support:
            continue
        by_id[category_id] = _materialize_support(family_support, category_id=category_id)

    return {
        "support_version": SUPPORT_VERSION,
        "inventory": dict(CATEGORY_FAMILY_BY_ID),
        "by_family": by_family,
        "by_id": by_id,
    }


def apply_category_support_to_profile_narrative(
    payload: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> Dict[str, Any]:
    out = copy.deepcopy(payload if isinstance(payload, Mapping) else {})
    public = out.get("profile_public")
    by_id = bundle.get("by_id") if isinstance(bundle.get("by_id"), Mapping) else {}
    if isinstance(public, dict) and isinstance(public.get("blocks"), list):
        for block in public.get("blocks") or []:
            if not isinstance(block, dict):
                continue
            category_id = str(block.get("id") or "").strip()
            support = by_id.get(category_id)
            if isinstance(support, Mapping):
                block["category_support"] = copy.deepcopy(support)
    internal = out.get("profile_internal")
    if isinstance(internal, dict) and isinstance(internal.get("blocks_debug"), list):
        for block in internal.get("blocks_debug") or []:
            if not isinstance(block, dict):
                continue
            category_id = str(block.get("id") or "").strip()
            support = by_id.get(category_id)
            if isinstance(support, Mapping):
                block["category_support"] = copy.deepcopy(support)
    return out


def apply_category_support_to_sections(
    sections: Sequence[Mapping[str, Any]],
    bundle: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    by_id = bundle.get("by_id") if isinstance(bundle.get("by_id"), Mapping) else {}
    out: List[Dict[str, Any]] = []
    for raw in sections:
        if not isinstance(raw, Mapping):
            continue
        entry = dict(raw)
        category_id = str(entry.get("id") or "").strip()
        support = by_id.get(category_id)
        if isinstance(support, Mapping):
            entry["category_support"] = copy.deepcopy(support)
            entry["evidence"] = build_surface_evidence_from_support(support)
        out.append(entry)
    return out


def apply_category_support_to_threads(
    threads: Sequence[Mapping[str, Any]],
    bundle: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    by_id = bundle.get("by_id") if isinstance(bundle.get("by_id"), Mapping) else {}
    out: List[Dict[str, Any]] = []
    for raw in threads:
        if not isinstance(raw, Mapping):
            continue
        entry = dict(raw)
        category_id = str(entry.get("id") or "").strip()
        support = by_id.get(category_id)
        if isinstance(support, Mapping):
            entry["category_support"] = copy.deepcopy(support)
            entry["evidence"] = build_surface_evidence_from_support(support)
        out.append(entry)
    return out


def apply_category_support_to_personality_imprint(
    payload: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> Dict[str, Any]:
    out = copy.deepcopy(payload if isinstance(payload, Mapping) else {})
    by_family = bundle.get("by_family") if isinstance(bundle.get("by_family"), Mapping) else {}
    for field in ("entries", "extra_entries"):
        items = out.get(field)
        if not isinstance(items, list):
            continue
        for entry in items:
            if not isinstance(entry, dict):
                continue
            family = infer_imprint_family(entry)
            if not family:
                continue
            support = by_family.get(family)
            if not isinstance(support, Mapping):
                continue
            entry["category_support"] = _materialize_support(
                support,
                category_id=_CANONICAL_ID_BY_FAMILY.get(family, family),
            )
    return out


def build_surface_evidence_from_support(support: Mapping[str, Any]) -> List[Dict[str, Any]]:
    evidence: List[Dict[str, Any]] = []
    primary = support.get("primary_anchor")
    if isinstance(primary, Mapping):
        evidence.append(dict(primary))
    supporting = support.get("supporting_combo") if isinstance(support.get("supporting_combo"), Sequence) else []
    for item in supporting[:2]:
        if isinstance(item, Mapping):
            evidence.append(dict(item))
    contradiction = support.get("contradiction_signature")
    if isinstance(contradiction, Mapping):
        evidence.append(dict(contradiction))
    return evidence


def infer_imprint_family(entry: Mapping[str, Any]) -> str | None:
    kind = str(entry.get("kind") or "").strip()
    key = str(entry.get("key") or "").strip().lower()
    house_match = re.search(r"_house_(\d+)$", key)
    if house_match:
        house = int(house_match.group(1))
        if house == 1:
            return "identity"
        if house == 3:
            return "mind"
        if house in {6, 9}:
            return "drive"
        if house in {7, 8, 12}:
            return "intimacy"
        if house in {10, 11}:
            return "visibility"
        if house == 4:
            return "home"
        if house in {2, 5}:
            return "opportunity"
    planets = _parse_key_planets(key)
    if kind == "aspect":
        if {"moon", "venus", "pluto", "lilith"} & planets:
            return "intimacy"
        if "mercury" in planets:
            return "mind"
        if {"midheaven", "chiron"} & planets:
            return "visibility"
        if {"fortune", "jupiter"} & planets:
            return "opportunity"
        if {"mars", "saturn", "uranus"} & planets:
            return "drive"
        if {"sun", "ascendant"} & planets:
            return "identity"
    if kind == "house_placement":
        if "mercury" in key:
            return "mind"
        if "mars" in key:
            return "drive"
        if "venus" in key or "moon" in key:
            return "intimacy"
        if "fortune" in key or "jupiter" in key:
            return "opportunity"
        if "sun" in key:
            return "identity"
    return None


def _build_family_support(
    *,
    family: str,
    chart_data: Mapping[str, Any],
    planets: Sequence[Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any] | None = None,
    contradiction_signatures: Mapping[str, Any] | None = None,
    master_selector: Mapping[str, Any] | None = None,
) -> Dict[str, Any] | None:
    spec = _FAMILY_SPECS[family]
    planets_map = _planet_map(planets)
    house_rulers = natal_graph.get("house_rulers") if isinstance(natal_graph.get("house_rulers"), Mapping) else {}
    house_counts = _house_counts(planets)
    feature_graph = natal_feature_graph if isinstance(natal_feature_graph, Mapping) else {}
    anchor_candidates = _anchor_candidates(
        family=family,
        spec=spec,
        chart_data=chart_data,
        planets=planets_map,
        house_rulers=house_rulers,
        house_counts=house_counts,
        natal_graph=natal_graph,
        natal_feature_graph=feature_graph,
    )
    primary_anchor = _pick_best(anchor_candidates, minimum_score=_PRIMARY_THRESHOLD)
    if primary_anchor is None:
        return None

    contradiction = _contradiction_candidate(
        family=family,
        spec=spec,
        contradiction_signatures=contradiction_signatures,
        master_selector=master_selector,
    )
    if contradiction and float(contradiction.get("score") or 0.0) < _CONTRADICTION_THRESHOLD:
        contradiction = None

    support_candidates = _support_candidates(
        family=family,
        spec=spec,
        planets=planets_map,
        aspects=aspects,
        house_rulers=house_rulers,
        house_counts=house_counts,
        natal_graph=natal_graph,
        natal_feature_graph=feature_graph,
    )
    support_candidates = [
        candidate
        for candidate in support_candidates
        if str(candidate.get("source_ref") or "") != str(primary_anchor.get("source_ref") or "")
    ]
    supporting_combo = _pick_ranked(
        support_candidates,
        minimum_score=_SUPPORT_THRESHOLD,
        limit=3,
    )
    supporting_refs = {str(item.get("source_ref") or "") for item in supporting_combo}
    hidden_support = _pick_ranked(
        [
            candidate
            for candidate in support_candidates
            if str(candidate.get("source_ref") or "") not in supporting_refs
        ],
        minimum_score=_HIDDEN_THRESHOLD,
        limit=2,
    )

    repeated_motifs = _motif_candidates(
        family=family,
        spec=spec,
        natal_feature_graph=feature_graph,
    )
    repeated_motifs = _pick_ranked(repeated_motifs, minimum_score=_MOTIF_THRESHOLD, limit=3)
    confidence = _clamp01(
        0.28
        + (float(primary_anchor.get("score") or 0.0) * 0.34)
        + (len(supporting_combo) * 0.08)
        + (len(repeated_motifs) * 0.05)
        + (float((contradiction or {}).get("score") or 0.0) * 0.10)
    )
    salience = _clamp01(
        0.22
        + (float(primary_anchor.get("score") or 0.0) * 0.42)
        + (sum(float(item.get("score") or 0.0) for item in supporting_combo[:2]) * 0.12)
        + (sum(float(item.get("score") or 0.0) for item in repeated_motifs[:2]) * 0.08)
    )

    return {
        "support_version": SUPPORT_VERSION,
        "family": family,
        "primary_anchor": primary_anchor,
        "supporting_combo": supporting_combo,
        "contradiction_signature": contradiction,
        "hidden_support": hidden_support,
        "repeated_motifs": repeated_motifs,
        "salience": round(salience, 4),
        "confidence": round(confidence, 4),
    }


def _anchor_candidates(
    *,
    family: str,
    spec: Mapping[str, Any],
    chart_data: Mapping[str, Any],
    planets: Mapping[str, Mapping[str, Any]],
    house_rulers: Mapping[str, Any],
    house_counts: Mapping[int, int],
    natal_graph: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    angle = str(spec.get("angle") or "").strip()
    if angle:
        angle_payload = _angle_candidate(
            angle=angle,
            family=family,
            planets=planets,
            chart_data=chart_data,
            natal_graph=natal_graph,
            natal_feature_graph=natal_feature_graph,
        )
        if angle_payload:
            out.append(angle_payload)
    for house in spec.get("route_houses") or []:
        route_payload = _route_candidate(
            house=house,
            family=family,
            spec=spec,
            planets=planets,
            house_rulers=house_rulers,
            natal_graph=natal_graph,
            natal_feature_graph=natal_feature_graph,
        )
        if route_payload:
            out.append(route_payload)
    for house in spec.get("anchor_houses") or []:
        if house_counts.get(int(house), 0) >= 2:
            out.append(
                _house_emphasis_candidate(
                    family=family,
                    house=int(house),
                    count=house_counts.get(int(house), 0),
                    natal_feature_graph=natal_feature_graph,
                    natal_graph=natal_graph,
                )
            )
    for planet_name, payload in planets.items():
        candidate = _placement_candidate(
            family=family,
            spec=spec,
            planet=planet_name,
            payload=payload,
            natal_graph=natal_graph,
            natal_feature_graph=natal_feature_graph,
            anchor_mode=True,
        )
        if candidate:
            out.append(candidate)
    return out


def _support_candidates(
    *,
    family: str,
    spec: Mapping[str, Any],
    planets: Mapping[str, Mapping[str, Any]],
    aspects: Sequence[Mapping[str, Any]],
    house_rulers: Mapping[str, Any],
    house_counts: Mapping[int, int],
    natal_graph: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for planet_name, payload in planets.items():
        candidate = _placement_candidate(
            family=family,
            spec=spec,
            planet=planet_name,
            payload=payload,
            natal_graph=natal_graph,
            natal_feature_graph=natal_feature_graph,
            anchor_mode=False,
        )
        if candidate:
            out.append(candidate)
    for house in spec.get("route_houses") or []:
        route_payload = _route_candidate(
            house=house,
            family=family,
            spec=spec,
            planets=planets,
            house_rulers=house_rulers,
            natal_graph=natal_graph,
            natal_feature_graph=natal_feature_graph,
        )
        if route_payload:
            out.append(route_payload)
    for house in spec.get("anchor_houses") or []:
        if house_counts.get(int(house), 0) >= 1:
            out.append(
                _house_emphasis_candidate(
                    family=family,
                    house=int(house),
                    count=house_counts.get(int(house), 0),
                    natal_feature_graph=natal_feature_graph,
                    natal_graph=natal_graph,
                )
            )
    for aspect in aspects:
        candidate = _aspect_candidate(
            family=family,
            spec=spec,
            payload=aspect,
            natal_graph=natal_graph,
            natal_feature_graph=natal_feature_graph,
        )
        if candidate:
            out.append(candidate)
    return out


def _angle_candidate(
    *,
    angle: str,
    family: str,
    planets: Mapping[str, Mapping[str, Any]],
    chart_data: Mapping[str, Any],
    natal_graph: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any],
) -> Dict[str, Any] | None:
    angle_name = _ANGLE_ALIAS_TO_PLANET.get(angle, angle)
    angle_payload = planets.get(angle_name) or _chart_angle_payload(chart_data, angle)
    if not angle_payload:
        return None
    sign = str(angle_payload.get("sign") or "").strip()
    score = _ANGLE_BASE_SCORE + _planet_salience(angle_name, natal_graph, natal_feature_graph) * 0.18
    if family in {"identity", "visibility"}:
        score += 0.06
    return _candidate_item(
        kind="anchor",
        label=f"{angle} angle",
        source_type="angle",
        source_ref=f"angle:{angle}:{sign or 'unknown'}",
        score=score,
        ruler_route_strength=0.0,
        exactness=0.0,
        planet_salience=_planet_salience(angle_name, natal_graph, natal_feature_graph),
    )


def _route_candidate(
    *,
    house: int,
    family: str,
    spec: Mapping[str, Any],
    planets: Mapping[str, Mapping[str, Any]],
    house_rulers: Mapping[str, Any],
    natal_graph: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any],
) -> Dict[str, Any] | None:
    payload = house_rulers.get(str(house)) if isinstance(house_rulers.get(str(house)), Mapping) else {}
    ruler = str(payload.get("primary_ruler") or "").strip()
    pos = payload.get("primary_ruler_pos") if isinstance(payload.get("primary_ruler_pos"), Mapping) else {}
    ruler_house = _safe_house(pos.get("house"))
    if not ruler:
        return None
    salience = _planet_salience(ruler, natal_graph, natal_feature_graph)
    route_strength = 0.72 if ruler_house in (spec.get("route_preferred_houses") or set()) else 0.56
    score = _ROUTE_BASE_SCORE
    if ruler in (spec.get("anchor_planets") or set()):
        score += 0.12
    if ruler_house in (spec.get("anchor_houses") or set()):
        score += 0.10
    if ruler_house in {1, 4, 7, 10}:
        score += 0.08
    score += route_strength * 0.10
    score += salience * 0.12
    if family in {"mind", "intimacy", "visibility"}:
        score += 0.02
    label = f"{house}th house ruler route"
    source_ref = f"house:{house}->ruler:{ruler}->house:{ruler_house or 'unknown'}"
    return _candidate_item(
        kind="anchor",
        label=label,
        source_type="ruler_route",
        source_ref=source_ref,
        score=score,
        ruler_route_strength=route_strength,
        exactness=0.0,
        planet_salience=salience,
    )


def _placement_candidate(
    *,
    family: str,
    spec: Mapping[str, Any],
    planet: str,
    payload: Mapping[str, Any],
    natal_graph: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any],
    anchor_mode: bool,
) -> Dict[str, Any] | None:
    house = _safe_house(payload.get("house"))
    if house is None:
        return None
    relevant_planets = spec.get("anchor_planets") if anchor_mode else spec.get("support_planets")
    if planet not in relevant_planets and house not in (spec.get("anchor_houses") or set()):
        return None
    salience = _planet_salience(planet, natal_graph, natal_feature_graph)
    score = _PLACEMENT_BASE_SCORE
    if planet in relevant_planets:
        score += 0.10
    if house in (spec.get("anchor_houses") or set()):
        score += 0.12
    if house in {1, 4, 7, 10}:
        score += 0.04
    score += salience * 0.14
    if anchor_mode and house not in (spec.get("anchor_houses") or set()):
        score -= 0.04
    return _candidate_item(
        kind="anchor" if anchor_mode else "supporting_combo",
        label=f"{planet} in house {house}",
        source_type="placement",
        source_ref=f"planet:{planet}:house:{house}",
        score=score,
        ruler_route_strength=0.0,
        exactness=0.0,
        planet_salience=salience,
    )


def _aspect_candidate(
    *,
    family: str,
    spec: Mapping[str, Any],
    payload: Mapping[str, Any],
    natal_graph: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any],
) -> Dict[str, Any] | None:
    planet1 = str(payload.get("planet1") or payload.get("a") or "").strip()
    planet2 = str(payload.get("planet2") or payload.get("b") or "").strip()
    raw_aspect = str(payload.get("type") or payload.get("aspect") or "").strip().lower()
    aspect_type = _ASPECT_ALIASES.get(raw_aspect, raw_aspect)
    if not planet1 or not planet2 or not aspect_type:
        return None
    planets = {planet1, planet2}
    if not planets & set(spec.get("support_planets") or set()):
        return None
    exactness = _aspect_exactness(payload.get("orb"))
    average_salience = (
        _planet_salience(planet1, natal_graph, natal_feature_graph)
        + _planet_salience(planet2, natal_graph, natal_feature_graph)
    ) / 2.0
    score = _ASPECT_BASE_SCORE + exactness * 0.20 + average_salience * 0.18
    if planets & set(spec.get("anchor_planets") or set()):
        score += 0.06
    if family == "mind" and planets & {"Mercury", "Saturn", "Mars", "Uranus"}:
        score += 0.06
    if family == "intimacy" and planets & {"Moon", "Venus", "Pluto", "Saturn"}:
        score += 0.06
    if family == "visibility" and planets & {"Jupiter", "Neptune", "Midheaven", "Chiron", "Sun"}:
        score += 0.05
    if family == "drive" and planets & {"Mars", "Saturn", "Uranus", "Jupiter", "Neptune"}:
        score += 0.05
    if family == "opportunity" and planets & {"Fortune", "Jupiter", "Venus", "Sun", "Mars"}:
        score += 0.04
    return _candidate_item(
        kind="supporting_combo",
        label=f"{planet1} {aspect_type} {planet2}",
        source_type="aspect",
        source_ref=f"{planet1}:{planet2}:{aspect_type}",
        score=score,
        ruler_route_strength=0.0,
        exactness=exactness,
        planet_salience=average_salience,
    )


def _house_emphasis_candidate(
    *,
    family: str,
    house: int,
    count: int,
    natal_feature_graph: Mapping[str, Any],
    natal_graph: Mapping[str, Any],
) -> Dict[str, Any]:
    score = _HOUSE_EMPHASIS_BASE_SCORE + min(max(count - 1, 0), 3) * 0.08
    if house in {1, 4, 7, 10}:
        score += 0.04
    score += _dominant_house_salience(house, natal_graph, natal_feature_graph) * 0.08
    return _candidate_item(
        kind="supporting_combo",
        label=f"house {house} emphasis",
        source_type="house_emphasis",
        source_ref=f"house_emphasis:{house}:{count}",
        score=score,
        ruler_route_strength=0.0,
        exactness=0.0,
        planet_salience=_dominant_house_salience(house, natal_graph, natal_feature_graph),
    )


def _motif_candidates(
    *,
    family: str,
    spec: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    repeated = (
        (natal_feature_graph.get("repeated_motif_count") or {}).get("dominant_motifs")
        if isinstance((natal_feature_graph.get("repeated_motif_count") or {}), Mapping)
        else []
    )
    out: List[Dict[str, Any]] = []
    for item in repeated or []:
        if not isinstance(item, Mapping):
            continue
        motif_id = str(item.get("id") or "").strip()
        if motif_id not in (spec.get("motifs") or set()):
            continue
        score = float(item.get("score") or 0.0)
        out.append(
            _candidate_item(
                kind="motif",
                label=motif_id.replace("_", " "),
                source_type="motif",
                source_ref=motif_id,
                score=score,
                ruler_route_strength=0.0,
                exactness=0.0,
                planet_salience=0.0,
            )
        )
    return out


def _contradiction_candidate(
    *,
    family: str,
    spec: Mapping[str, Any],
    contradiction_signatures: Mapping[str, Any] | None,
    master_selector: Mapping[str, Any] | None,
) -> Dict[str, Any] | None:
    payload = contradiction_signatures if isinstance(contradiction_signatures, Mapping) else {}
    items = payload.get("signatures") if isinstance(payload.get("signatures"), Sequence) else []
    slot_lookup = _slot_confidence(master_selector)
    candidates: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            continue
        contradiction_id = str(item.get("id") or "").strip()
        if contradiction_id not in (spec.get("contradictions") or set()):
            continue
        score = float(item.get("score") or 0.0)
        slot_biases = [str(value) for value in item.get("slot_biases") or [] if str(value).strip()]
        slot_bonus = max((slot_lookup.get(slot) or 0.0) for slot in slot_biases) if slot_biases else 0.0
        candidates.append(
            _candidate_item(
                kind="contradiction",
                label=_CONTRADICTION_LABELS.get(contradiction_id, contradiction_id.replace("_", " ")),
                source_type="contradiction_signature",
                source_ref=contradiction_id,
                score=score + slot_bonus * 0.04,
                ruler_route_strength=0.0,
                exactness=0.0,
                planet_salience=slot_bonus,
            )
        )
    return _pick_best(candidates, minimum_score=_CONTRADICTION_THRESHOLD)


def _materialize_support(support: Mapping[str, Any], *, category_id: str) -> Dict[str, Any]:
    out = copy.deepcopy(dict(support))
    out["category_id"] = category_id
    return out


def _pick_best(candidates: Iterable[Mapping[str, Any]], *, minimum_score: float) -> Dict[str, Any] | None:
    ranked = _pick_ranked(candidates, minimum_score=minimum_score, limit=1)
    return ranked[0] if ranked else None


def _pick_ranked(
    candidates: Iterable[Mapping[str, Any]],
    *,
    minimum_score: float,
    limit: int,
) -> List[Dict[str, Any]]:
    filtered = [
        dict(candidate)
        for candidate in candidates
        if isinstance(candidate, Mapping) and float(candidate.get("score") or 0.0) >= minimum_score
    ]
    filtered.sort(key=_candidate_sort_key, reverse=True)
    selected: List[Dict[str, Any]] = []
    seen_refs: set[str] = set()
    for item in filtered:
        source_ref = str(item.get("source_ref") or "")
        if source_ref in seen_refs:
            continue
        seen_refs.add(source_ref)
        selected.append(_public_item_shape(item))
        if len(selected) >= limit:
            break
    return selected


def _candidate_item(
    *,
    kind: str,
    label: str,
    source_type: str,
    source_ref: str,
    score: float,
    ruler_route_strength: float,
    exactness: float,
    planet_salience: float,
) -> Dict[str, Any]:
    return {
        "kind": kind,
        "label": label,
        "source_type": source_type,
        "source_ref": source_ref,
        "score": round(_clamp01(score), 4),
        "ruler_route_strength": round(_clamp01(ruler_route_strength), 4),
        "exactness": round(_clamp01(exactness), 4),
        "planet_salience": round(_clamp01(planet_salience), 4),
    }


def _public_item_shape(item: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "kind": str(item.get("kind") or "").strip(),
        "label": str(item.get("label") or "").strip(),
        "source_type": str(item.get("source_type") or "").strip(),
        "source_ref": str(item.get("source_ref") or "").strip(),
        "score": round(float(item.get("score") or 0.0), 4),
    }


def _candidate_sort_key(item: Mapping[str, Any]) -> tuple[float, float, float, float, str]:
    return (
        float(item.get("score") or 0.0),
        float(item.get("ruler_route_strength") or 0.0),
        float(item.get("exactness") or 0.0),
        float(item.get("planet_salience") or 0.0),
        str(item.get("source_ref") or ""),
    )


def _planet_map(planets: Sequence[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for item in planets:
        if not isinstance(item, Mapping):
            continue
        name = str(item.get("planet") or item.get("name") or "").strip()
        if name:
            out[name] = dict(item)
    return out


def _house_counts(planets: Sequence[Mapping[str, Any]]) -> Dict[int, int]:
    out: Dict[int, int] = {}
    for item in planets:
        if not isinstance(item, Mapping):
            continue
        house = _safe_house(item.get("house"))
        if house is None:
            continue
        out[house] = out.get(house, 0) + 1
    return out


def _chart_angle_payload(chart_data: Mapping[str, Any], angle: str) -> Dict[str, Any]:
    angles = chart_data.get("angles") if isinstance(chart_data.get("angles"), Mapping) else {}
    key = {
        "ASC": ("ascendant_sign", "asc_sign"),
        "MC": ("midheaven_sign", "mc_sign"),
        "DSC": ("descendant_sign", "dsc_sign"),
        "IC": ("imum_coeli_sign", "ic_sign"),
    }.get(angle, ())
    for field in key:
        value = str(angles.get(field) or "").strip()
        if value:
            return {"sign": value}
    return {}


def _planet_salience(
    planet: str,
    natal_graph: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any],
) -> float:
    feature_planets = (
        natal_feature_graph.get("planet_salience")
        if isinstance(natal_feature_graph.get("planet_salience"), Mapping)
        else {}
    )
    if isinstance(feature_planets.get(planet), Mapping):
        return _clamp01(feature_planets.get(planet, {}).get("score"))
    importance = natal_graph.get("importance") if isinstance(natal_graph.get("importance"), Mapping) else {}
    return _clamp01(importance.get(planet))


def _dominant_house_salience(
    house: int,
    natal_graph: Mapping[str, Any],
    natal_feature_graph: Mapping[str, Any],
) -> float:
    planets = natal_feature_graph.get("planet_salience") if isinstance(natal_feature_graph.get("planet_salience"), Mapping) else {}
    values = [
        float(payload.get("score") or 0.0)
        for payload in planets.values()
        if isinstance(payload, Mapping) and _safe_house(payload.get("house")) == house
    ]
    if values:
        return _clamp01(max(values))
    importance = natal_graph.get("importance") if isinstance(natal_graph.get("importance"), Mapping) else {}
    return _clamp01(max((float(value or 0.0) for value in importance.values()), default=0.0) * 0.5)


def _aspect_exactness(orb: Any) -> float:
    try:
        value = float(orb)
    except (TypeError, ValueError):
        return 0.0
    if value <= 0:
        return 1.0
    return _clamp01((6.0 - min(value, 6.0)) / 6.0)


def _slot_confidence(master_selector: Mapping[str, Any] | None) -> Dict[str, float]:
    payload = master_selector if isinstance(master_selector, Mapping) else {}
    identity_spine = payload.get("identity_spine") if isinstance(payload.get("identity_spine"), Mapping) else {}
    return {
        str(slot): float((value or {}).get("confidence") or 0.0)
        for slot, value in identity_spine.items()
        if isinstance(value, Mapping)
    }


def _parse_key_planets(key: str) -> set[str]:
    tokens = [piece for piece in re.split(r"[^a-z]+", key.lower()) if piece]
    known = {
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
        "fortune",
        "midheaven",
        "ascendant",
        "chiron",
        "lilith",
    }
    return {token for token in tokens if token in known}


def _safe_house(value: Any) -> int | None:
    try:
        house = int(value)
    except (TypeError, ValueError):
        return None
    return house if 1 <= house <= 12 else None


def _clamp01(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))
