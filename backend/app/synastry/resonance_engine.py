from __future__ import annotations

import math
import re
from typing import Any, Dict, Iterable, Mapping, Sequence

from app.synastry.activation_engine import clamp01
from app.synastry.narrative.phrase_lib_tr_synastry import (
    asymmetry_phrase,
    domain_label,
    mode_label,
    mutuality_phrase,
    shared_theme_line,
    support_line,
    sustainability_band,
    tension_line,
)


DOMAIN_TO_FAMILIARITY: Dict[str, Dict[str, float]] = {
    "identity": {"structure_control": 0.55, "novelty_freedom": 0.35, "visibility_sensitivity": 0.20},
    "mind_communication": {"mental_precision": 0.70, "structure_control": 0.25},
    "relationships": {"soft_affection": 0.55, "intensity_depth": 0.35},
    "intimacy_depth": {"intensity_depth": 0.80, "soft_affection": 0.20},
    "private_inner_world": {"soft_affection": 0.35, "mental_precision": 0.25, "structure_control": 0.20, "intensity_depth": 0.15},
    "career_visibility": {"visibility_sensitivity": 0.75, "structure_control": 0.25},
    "home_roots": {"soft_affection": 0.45, "structure_control": 0.35},
    "creativity_talent": {"soft_affection": 0.40, "novelty_freedom": 0.35},
    "social_future": {"soft_affection": 0.35, "novelty_freedom": 0.25, "visibility_sensitivity": 0.15},
    "meaning_learning": {"mental_precision": 0.35, "novelty_freedom": 0.35, "intensity_depth": 0.15},
}

DOMAIN_TO_PROMISE: Dict[str, Dict[str, float]] = {
    "identity": {"embody_originality": 0.55, "integrate_vision_with_structure": 0.35},
    "mind_communication": {"learn_clear_expression": 0.80, "integrate_vision_with_structure": 0.20},
    "relationships": {"build_safe_intimacy": 0.70, "mature_visibility": 0.15},
    "intimacy_depth": {"build_safe_intimacy": 0.80, "turn_depth_into_wisdom": 0.30},
    "private_inner_world": {"build_safe_intimacy": 0.35, "turn_depth_into_wisdom": 0.30, "learn_clear_expression": 0.20},
    "career_visibility": {"mature_visibility": 0.80, "integrate_vision_with_structure": 0.20},
    "home_roots": {"build_safe_intimacy": 0.45, "turn_depth_into_wisdom": 0.20},
    "creativity_talent": {"embody_originality": 0.45, "mature_visibility": 0.25},
    "social_future": {"embody_originality": 0.25, "mature_visibility": 0.20, "build_safe_intimacy": 0.20},
    "meaning_learning": {"turn_depth_into_wisdom": 0.55, "integrate_vision_with_structure": 0.45},
}

DOMAIN_TO_SENSITIVITY: Dict[str, Dict[str, float]] = {
    "identity": {"criticism_pressure": 0.35, "visibility_exposure": 0.35, "instability_overload": 0.20},
    "mind_communication": {"criticism_pressure": 0.55, "fear_of_misalignment": 0.25},
    "relationships": {"fear_of_misalignment": 0.45, "rejection_or_distance": 0.35},
    "intimacy_depth": {"overwhelm_by_intensity": 0.75, "rejection_or_distance": 0.25},
    "private_inner_world": {"fear_of_misalignment": 0.35, "rejection_or_distance": 0.30, "instability_overload": 0.20},
    "career_visibility": {"visibility_exposure": 0.75, "criticism_pressure": 0.25},
    "home_roots": {"rejection_or_distance": 0.45, "fear_of_misalignment": 0.20},
    "creativity_talent": {"visibility_exposure": 0.35, "fear_of_misalignment": 0.20},
    "social_future": {"rejection_or_distance": 0.25, "visibility_exposure": 0.20, "fear_of_misalignment": 0.20},
    "meaning_learning": {"instability_overload": 0.25, "fear_of_misalignment": 0.15},
}

PROMISE_TO_DOMAIN_WEIGHTS: Dict[str, Dict[str, float]] = {
    "learn_clear_expression": {"mind_communication": 0.70, "meaning_learning": 0.20, "private_inner_world": 0.10},
    "build_safe_intimacy": {"intimacy_depth": 0.50, "relationships": 0.25, "home_roots": 0.15, "private_inner_world": 0.10},
    "integrate_vision_with_structure": {
        "identity": 0.35,
        "meaning_learning": 0.30,
        "mind_communication": 0.20,
        "career_visibility": 0.15,
    },
    "mature_visibility": {"career_visibility": 0.60, "identity": 0.20, "relationships": 0.10, "social_future": 0.10},
    "embody_originality": {"identity": 0.55, "creativity_talent": 0.20, "meaning_learning": 0.15, "social_future": 0.10},
    "turn_depth_into_wisdom": {"intimacy_depth": 0.35, "meaning_learning": 0.30, "home_roots": 0.20, "private_inner_world": 0.15},
}

MOTIF_ACTIVATION_HINTS: Dict[str, Dict[str, Any]] = {
    "identity_structure": {"domains": ("identity",), "houses": (1,), "bodies": ("sun", "asc", "saturn")},
    "visionary_originality": {"domains": ("identity", "meaning_learning"), "houses": (1, 9), "bodies": ("uranus", "jupiter", "neptune")},
    "depth_intimacy": {"domains": ("intimacy_depth", "private_inner_world"), "houses": (8, 12), "bodies": ("moon", "venus", "mars", "pluto")},
    "language_boundary": {"domains": ("mind_communication",), "houses": (3, 9, 12), "bodies": ("mercury", "saturn")},
    "push_pull_drive": {"domains": ("identity", "intimacy_depth"), "houses": (8, 9), "bodies": ("mars", "saturn")},
    "visibility_sensitivity": {"domains": ("career_visibility",), "houses": (10, 12), "bodies": ("mc", "moon", "chiron", "venus")},
    "hidden_creation": {"domains": ("creativity_talent", "private_inner_world"), "houses": (12,), "bodies": ("venus", "neptune")},
    "system_builder": {"domains": ("mind_communication", "meaning_learning"), "houses": (3, 9), "bodies": ("saturn", "mercury")},
    "soft_bonding": {"domains": ("relationships", "home_roots"), "houses": (4, 7), "bodies": ("moon", "venus")},
    "independent_roots": {"domains": ("home_roots", "identity"), "houses": (4,), "bodies": ("mars", "moon")},
    "creative_flow": {"domains": ("creativity_talent", "social_future"), "houses": (5, 11), "bodies": ("venus", "moon", "neptune", "mars")},
    "transformational_intensity": {"domains": ("intimacy_depth",), "houses": (8, 12), "bodies": ("pluto", "moon", "venus")},
    "private_intellect": {"domains": ("mind_communication", "private_inner_world"), "houses": (12, 3, 9), "bodies": ("sun", "mercury")},
    "selective_bonding": {"domains": ("relationships", "intimacy_depth"), "houses": (7, 8, 12), "bodies": ("venus", "saturn")},
    "service_love": {"domains": ("relationships", "social_future"), "houses": (6, 7, 11), "bodies": ("venus", "mercury")},
    "relational_perfectionism": {"domains": ("relationships", "mind_communication"), "houses": (1, 7, 12), "bodies": ("asc", "venus", "mercury")},
    "depth_guardedness": {"domains": ("intimacy_depth", "private_inner_world"), "houses": (8, 12), "bodies": ("saturn", "venus", "pluto")},
    "social_fire_private_core": {"domains": ("identity", "social_future", "private_inner_world"), "houses": (11, 12, 1), "bodies": ("mars", "venus", "sun", "mercury")},
    "mentalized_emotion": {"domains": ("mind_communication", "meaning_learning"), "houses": (3, 9, 12), "bodies": ("moon", "mercury")},
    "quiet_loyalty": {"domains": ("relationships", "home_roots", "social_future"), "houses": (4, 7, 8, 11), "bodies": ("saturn", "venus", "mars")},
    "hidden_devotion": {"domains": ("relationships", "private_inner_world"), "houses": (12, 7, 10), "bodies": ("venus", "moon", "node")},
    "thresholded_intimacy": {"domains": ("intimacy_depth", "private_inner_world"), "houses": (8, 12), "bodies": ("saturn", "pluto", "mercury", "venus")},
}

DOMAIN_HOUSE_BODY_FIT: Dict[str, Dict[str, Any]] = {
    "identity": {"houses": (1,), "bodies": ("sun", "asc", "uranus")},
    "mind_communication": {"houses": (3, 9, 12), "bodies": ("mercury",)},
    "relationships": {"houses": (7, 8), "bodies": ("venus", "moon", "node")},
    "intimacy_depth": {"houses": (8, 12), "bodies": ("pluto", "mars", "venus", "moon")},
    "private_inner_world": {"houses": (12,), "bodies": ("sun", "moon", "mercury", "venus", "neptune", "node")},
    "career_visibility": {"houses": (10,), "bodies": ("mc", "moon", "chiron")},
    "home_roots": {"houses": (4,), "bodies": ("moon", "saturn")},
    "creativity_talent": {"houses": (5, 11), "bodies": ("venus", "mars", "neptune")},
    "social_future": {"houses": (11,), "bodies": ("sun", "moon", "venus", "mars", "jupiter", "node")},
    "meaning_learning": {"houses": (9, 3, 12), "bodies": ("mercury", "jupiter", "node")},
}

HARDNESS_BY_ASPECT = {
    "conjunction": 0.55,
    "square": 1.00,
    "opposition": 0.90,
    "trine": 0.25,
    "sextile": 0.15,
}

SOFT_ASPECTS = {"conjunction", "trine", "sextile"}
HARD_ASPECTS = {"conjunction", "square", "opposition"}
PLUTO_RISK_TARGETS = {"sun", "moon", "mercury", "venus", "mars", "node", "vertex"}
SATURN_RISK_TARGETS = {"asc", "mc", "sun", "moon", "venus"}
PERSONAL_CLUSTER_BODIES = {"sun", "moon", "mercury", "venus", "mars", "node", "vertex"}
TWELFTH_PRESSURE_BODIES = {"sun", "venus", "mars", "node"}
FOURTH_ROOT_BODIES = {"sun", "moon", "mercury", "venus", "jupiter", "neptune", "uranus"}
ELEVENTH_SOCIAL_BODIES = {"moon", "venus", "jupiter", "sun", "mars"}

BUNDLE_TO_DOMAIN: Dict[str, str] = {
    "8th_personal_cluster": "intimacy_depth",
    "pluto_personal_bundle": "intimacy_depth",
    "saturn_angular_bundle": "relationships",
    "soft_attraction_bundle": "relationships",
    "roots_home_bundle": "home_roots",
    "social_future_bundle": "social_future",
    "identity_activation_bundle": "identity",
    "12th_pressure_bundle": "private_inner_world",
    "nodal_fated_bundle": "meaning_learning",
    "communication_bridge_bundle": "mind_communication",
}

SOFT_ATTRACTION_BODIES = {"sun", "moon", "venus", "mars", "mercury"}
IDENTITY_BODIES = {"sun", "asc", "uranus", "neptune", "chiron", "mars", "venus"}
COMMUNICATION_BODIES = {"mercury", "sun", "asc", "node", "jupiter", "saturn"}
NODAL_BODIES = {"node", "asc", "mc", "pluto"}
ROOTS_BODIES = {"moon", "saturn", "uranus", "sun", "jupiter", "neptune"}
ANGULAR_BODIES = {"asc", "mc"}

SOURCE_ACTIVATION_SCALE: Dict[str, float] = {
    "overlay": 0.42,
    "touchpoint": 0.72,
    "aspect": 0.58,
}

BUNDLE_KIND_PRIORITY: Dict[str, int] = {
    "8th_personal_cluster": 0,
    "roots_home_bundle": 1,
    "12th_pressure_bundle": 2,
    "social_future_bundle": 3,
    "pluto_personal_bundle": 4,
    "saturn_angular_bundle": 5,
    "soft_attraction_bundle": 6,
    "communication_bridge_bundle": 7,
    "nodal_fated_bundle": 8,
    "identity_activation_bundle": 9,
}

BUNDLE_KIND_SCORE_SCALE: Dict[str, float] = {
    "8th_personal_cluster": 1.12,
    "roots_home_bundle": 1.10,
    "12th_pressure_bundle": 1.04,
    "social_future_bundle": 0.96,
    "pluto_personal_bundle": 0.92,
    "saturn_angular_bundle": 0.78,
    "soft_attraction_bundle": 0.74,
    "communication_bridge_bundle": 0.72,
    "nodal_fated_bundle": 0.68,
    "identity_activation_bundle": 0.76,
}


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _vector_match(vector_map: Mapping[str, Any], weights: Mapping[str, float]) -> float:
    total = 0.0
    for key, weight in weights.items():
        total += _safe_float(vector_map.get(key)) * float(weight)
    return clamp01(total)


def _top_average(values: Iterable[Any], count: int = 3) -> float:
    nums = sorted((_safe_float(value) for value in values), reverse=True)
    if not nums:
        return 0.0
    top = nums[:count]
    return clamp01(sum(top) / len(top))


def _orb_value(hit: Mapping[str, Any]) -> float:
    value = hit.get("orb_deg")
    return _safe_float(value) if value is not None else 999.0


def _activation_peak(hits: Sequence[Mapping[str, Any]]) -> float:
    if not hits:
        return 0.0
    return clamp01(max(_safe_float(hit.get("activation_score")) for hit in hits) / 0.30)


def _orb_tight_bonus(hits: Sequence[Mapping[str, Any]]) -> float:
    if any(_orb_value(hit) <= 1.5 for hit in hits):
        return 0.12
    if any(_orb_value(hit) <= 3.0 for hit in hits):
        return 0.06
    return 0.0


def _body_match(hit: Mapping[str, Any], targets: set[str]) -> bool:
    incoming = str(hit.get("incoming_body") or "").lower()
    native = str(hit.get("native_body") or "").lower()
    return incoming in targets or native in targets


def _domain_activation_map(aggregate: Mapping[str, Mapping[str, Any]]) -> Dict[str, float]:
    return {
        str(domain): clamp01(_safe_float(payload.get("activation")))
        for domain, payload in aggregate.items()
        if _safe_float(payload.get("activation")) > 0.0
    }


def _promise_domain_map(promise_vectors: Mapping[str, Any]) -> Dict[str, float]:
    totals: Dict[str, float] = {}
    for promise_key, promise_score in promise_vectors.items():
        weights = PROMISE_TO_DOMAIN_WEIGHTS.get(str(promise_key), {})
        value = _safe_float(promise_score)
        if value <= 0.0 or not weights:
            continue
        for domain, weight in weights.items():
            totals[domain] = totals.get(domain, 0.0) + value * float(weight)
    total = sum(totals.values())
    if total <= 0.0:
        return {}
    return {domain: clamp01(value / total) for domain, value in totals.items()}


def _non_fallback_ratio(natal_graph_v2: Mapping[str, Any]) -> float:
    debug = natal_graph_v2.get("debug") if isinstance(natal_graph_v2, Mapping) else {}
    if isinstance(debug, Mapping) and debug.get("non_fallback_ratio") is not None:
        return clamp01(_safe_float(debug.get("non_fallback_ratio")))
    fallback_vectors = debug.get("fallback_vectors") if isinstance(debug, Mapping) else []
    vector_evidence = debug.get("vector_evidence") if isinstance(debug, Mapping) else {}
    if not isinstance(fallback_vectors, Sequence) or not isinstance(vector_evidence, Mapping):
        return 0.0
    total = len(vector_evidence)
    if total <= 0:
        return 0.0
    return clamp01(1.0 - (len(fallback_vectors) / total))


def _motif_richness_norm(signature_motifs: Sequence[Mapping[str, Any]]) -> float:
    if not signature_motifs:
        return 0.0
    weighted = 0.0
    count = 0
    for motif in signature_motifs:
        score = _safe_float(motif.get("score"))
        if score < 0.16:
            continue
        weighted += min(1.0, score / 0.35)
        count += 1
    if count <= 0:
        return 0.0
    return clamp01(weighted / 6.0)


def _relevant_motif_hits(
    partner_hits: Sequence[Mapping[str, Any]],
    domains: Sequence[str],
    houses: Sequence[int],
    bodies: Sequence[str],
) -> list[Mapping[str, Any]]:
    body_targets = {str(body).lower() for body in bodies}
    domain_targets = {str(domain) for domain in domains}
    house_targets = {int(house) for house in houses}
    out: list[Mapping[str, Any]] = []
    for hit in partner_hits:
        if str(hit.get("domain") or "") in domain_targets:
            out.append(hit)
            continue
        if int(hit.get("activated_house") or 0) in house_targets:
            out.append(hit)
            continue
        if body_targets and _body_match(hit, body_targets):
            out.append(hit)
    return out


def _compute_motif_activation_fit(
    partner_hits: Sequence[Mapping[str, Any]],
    aggregate: Mapping[str, Mapping[str, Any]],
    natal_graph_v2: Mapping[str, Any],
) -> float:
    motifs = natal_graph_v2.get("signature_motifs")
    if not isinstance(motifs, Sequence):
        return 0.0
    relevant = [motif for motif in motifs if _safe_float(motif.get("score")) >= 0.18]
    if not relevant:
        relevant = list(motifs[:3])
    if not relevant:
        return 0.0

    weighted_total = 0.0
    weight_sum = 0.0
    for motif in relevant:
        motif_id = str(motif.get("id") or "")
        hints = MOTIF_ACTIVATION_HINTS.get(motif_id, {})
        motif_hits = _relevant_motif_hits(
            partner_hits,
            domains=tuple(hints.get("domains") or ()),
            houses=tuple(hints.get("houses") or ()),
            bodies=tuple(hints.get("bodies") or ()),
        )
        domain_peak = 0.0
        for domain in hints.get("domains") or ():
            payload = aggregate.get(str(domain), {})
            domain_peak = max(domain_peak, _safe_float(payload.get("activation")))
        fit = clamp01((0.60 * domain_peak) + (0.30 * _activation_peak(motif_hits)) + _orb_tight_bonus(motif_hits))
        weight = max(0.20, _safe_float(motif.get("score")))
        weighted_total += fit * weight
        weight_sum += weight
    if weight_sum <= 0.0:
        return 0.0
    return clamp01(weighted_total / weight_sum)


def _compute_house_ruler_fit(
    partner_hits: Sequence[Mapping[str, Any]],
    aggregate: Mapping[str, Mapping[str, Any]],
    natal_graph_v2: Mapping[str, Any],
) -> float:
    chart_rulers = natal_graph_v2.get("chart_rulers") if isinstance(natal_graph_v2, Mapping) else {}
    house_rulers = chart_rulers.get("house_rulers") if isinstance(chart_rulers, Mapping) else {}
    domain_vectors = natal_graph_v2.get("domain_vectors") if isinstance(natal_graph_v2, Mapping) else {}
    promise_domain_map = _promise_domain_map(natal_graph_v2.get("promise_vectors") if isinstance(natal_graph_v2, Mapping) else {})

    priorities: Dict[str, float] = {}
    for domain, spec in DOMAIN_HOUSE_BODY_FIT.items():
        priorities[domain] = (0.55 * _safe_float(domain_vectors.get(domain))) + (0.45 * _safe_float(promise_domain_map.get(domain)))
    top_domains = sorted(priorities.items(), key=lambda item: item[1], reverse=True)[:3]
    if not top_domains:
        return 0.0

    weighted_total = 0.0
    weight_sum = 0.0
    for domain, domain_weight in top_domains:
        if domain_weight <= 0.0:
            continue
        spec = DOMAIN_HOUSE_BODY_FIT.get(domain, {})
        house_targets = {int(house) for house in spec.get("houses") or ()}
        body_targets = {str(body).lower() for body in spec.get("bodies") or ()}
        for house in house_targets:
            ruler_info = house_rulers.get(str(house)) if isinstance(house_rulers, Mapping) else {}
            primary = str(ruler_info.get("primary") or "").lower()
            secondary = str(ruler_info.get("secondary") or "").lower()
            if primary:
                body_targets.add(primary)
            if secondary:
                body_targets.add(secondary)

        relevant_hits = _relevant_motif_hits(partner_hits, domains=(domain,), houses=tuple(house_targets), bodies=tuple(body_targets))
        domain_activation = _safe_float(aggregate.get(domain, {}).get("activation"))
        fit = clamp01((0.65 * domain_activation) + (0.25 * _activation_peak(relevant_hits)) + (0.10 * _orb_tight_bonus(relevant_hits) / 0.12 if relevant_hits else 0.0))
        weighted_total += fit * domain_weight
        weight_sum += domain_weight
    if weight_sum <= 0.0:
        return 0.0
    return clamp01(weighted_total / weight_sum)


def expand_activation_records(
    records: Sequence[Mapping[str, Any]],
    natal_graph_v2: Mapping[str, Any],
    for_partner: str,
) -> list[dict]:
    familiarity = natal_graph_v2.get("familiarity_vectors") if isinstance(natal_graph_v2, Mapping) else {}
    promise = natal_graph_v2.get("promise_vectors") if isinstance(natal_graph_v2, Mapping) else {}
    sensitivity = natal_graph_v2.get("sensitivity_vectors") if isinstance(natal_graph_v2, Mapping) else {}
    familiarity = familiarity if isinstance(familiarity, Mapping) else {}
    promise = promise if isinstance(promise, Mapping) else {}
    sensitivity = sensitivity if isinstance(sensitivity, Mapping) else {}

    out: list[dict] = []
    for record_index, record in enumerate(records):
        domains = record.get("domains")
        if not isinstance(domains, Mapping):
            continue
        house = record.get("activated_house")
        aspect = str(record.get("aspect") or "").lower() or None
        hardness = HARDNESS_BY_ASPECT.get(aspect or "", 0.0)
        source = str(record.get("source") or "overlay").lower()
        source_scale = SOURCE_ACTIVATION_SCALE.get(source, 0.60)
        for domain, activation_score in domains.items():
            act = _safe_float(activation_score) * source_scale
            if act <= 0.0:
                continue
            familiarity_boost = _vector_match(familiarity, DOMAIN_TO_FAMILIARITY.get(str(domain), {}))
            promise_boost = _vector_match(promise, DOMAIN_TO_PROMISE.get(str(domain), {}))
            trigger_risk = _vector_match(sensitivity, DOMAIN_TO_SENSITIVITY.get(str(domain), {}))
            if house in {1, 4, 7, 8, 12}:
                trigger_risk += 0.05
            if house == 8 and str(domain) == "intimacy_depth":
                trigger_risk += 0.08
            if house == 12 and str(domain) in {"intimacy_depth", "private_inner_world"}:
                trigger_risk += 0.08
            if hardness:
                trigger_risk += 0.12 * hardness
            trigger_risk = clamp01(trigger_risk)
            out.append(
                {
                    "for_partner": for_partner,
                    "source": source,
                    "source_record_id": f"{for_partner}:{record_index}",
                    "hit_id": f"{for_partner}:{record_index}:{str(domain)}",
                    "incoming_body": record.get("incoming_body"),
                    "native_body": record.get("native_body"),
                    "activated_house": house,
                    "aspect": aspect,
                    "orb_deg": record.get("orb_deg"),
                    "domain": str(domain),
                    "activation_score": round(act, 4),
                    "familiarity_boost": round(familiarity_boost, 4),
                    "promise_boost": round(promise_boost, 4),
                    "trigger_risk": round(trigger_risk, 4),
                    "hardness": round(hardness, 4),
                    "because": list(record.get("because") or []),
                }
            )
    return sorted(
        out,
        key=lambda item: (
            -_safe_float(item.get("activation_score")),
            -_safe_float(item.get("promise_boost")),
            str(item.get("domain") or ""),
        ),
    )


def _aggregate_partner_hits(partner_hits: Sequence[Mapping[str, Any]]) -> Dict[str, dict]:
    aggregate: Dict[str, dict] = {}
    for hit in partner_hits:
        domain = str(hit.get("domain") or "")
        if not domain:
            continue
        bucket = aggregate.setdefault(
            domain,
            {
                "activation_raw": 0.0,
                "familiarity_sum": 0.0,
                "promise_sum": 0.0,
                "trigger_sum": 0.0,
                "hardness_sum": 0.0,
                "weight": 0.0,
                "because": [],
            },
        )
        act = _safe_float(hit.get("activation_score"))
        bucket["activation_raw"] = _safe_float(bucket["activation_raw"]) + act
        bucket["familiarity_sum"] = _safe_float(bucket["familiarity_sum"]) + act * _safe_float(hit.get("familiarity_boost"))
        bucket["promise_sum"] = _safe_float(bucket["promise_sum"]) + act * _safe_float(hit.get("promise_boost"))
        bucket["trigger_sum"] = _safe_float(bucket["trigger_sum"]) + act * _safe_float(hit.get("trigger_risk"))
        bucket["hardness_sum"] = _safe_float(bucket["hardness_sum"]) + act * _safe_float(hit.get("hardness"))
        bucket["weight"] = _safe_float(bucket["weight"]) + act
        reasons = bucket["because"]
        for item in hit.get("because") or []:
            if item not in reasons:
                reasons.append(item)

    for bucket in aggregate.values():
        weight = _safe_float(bucket.get("weight"))
        if weight <= 0.0:
            bucket["activation"] = 0.0
            bucket["familiarity"] = 0.0
            bucket["promise"] = 0.0
            bucket["trigger"] = 0.0
            bucket["hardness"] = 0.0
        else:
            bucket["activation"] = clamp01(_safe_float(bucket.get("activation_raw")) / 2.0)
            bucket["familiarity"] = clamp01(_safe_float(bucket.get("familiarity_sum")) / weight)
            bucket["promise"] = clamp01(_safe_float(bucket.get("promise_sum")) / weight)
            bucket["trigger"] = clamp01(_safe_float(bucket.get("trigger_sum")) / weight)
            bucket["hardness"] = clamp01(_safe_float(bucket.get("hardness_sum")) / weight)
    return aggregate


def build_domain_context(partner_hits: Sequence[Mapping[str, Any]], top_n: int = 3) -> list[dict]:
    aggregate = _aggregate_partner_hits(partner_hits)
    rows = [
        {
            "domain": domain,
            "score": round(_safe_float(payload.get("activation")), 4),
            "because": list(payload.get("because") or [])[:5],
        }
        for domain, payload in aggregate.items()
        if _safe_float(payload.get("activation")) > 0.0
    ]
    return sorted(rows, key=lambda item: (-_safe_float(item.get("score")), str(item.get("domain") or "")))[:top_n]


def compute_familiarity_resonance(partner_hits: Sequence[Mapping[str, Any]], natal_graph_v2: Mapping[str, Any]) -> float:
    aggregate = _aggregate_partner_hits(partner_hits)
    activation = sum(_safe_float(item.get("activation")) for item in aggregate.values())
    if activation <= 0.0:
        return 0.0
    match = sum(_safe_float(item.get("activation")) * _safe_float(item.get("familiarity")) for item in aggregate.values()) / activation
    activation_strength = clamp01(activation / 1.8)
    return round(clamp01(0.72 * match + 0.28 * activation_strength), 4)


def compute_promise_alignment_breakdown(
    partner_hits: Sequence[Mapping[str, Any]],
    natal_graph_v2: Mapping[str, Any],
) -> Dict[str, float]:
    aggregate = _aggregate_partner_hits(partner_hits)
    promise_vectors = natal_graph_v2.get("promise_vectors") if isinstance(natal_graph_v2, Mapping) else {}
    promise_vectors = promise_vectors if isinstance(promise_vectors, Mapping) else {}
    signature_motifs = natal_graph_v2.get("signature_motifs") if isinstance(natal_graph_v2, Mapping) else []
    signature_motifs = signature_motifs if isinstance(signature_motifs, Sequence) else []

    promise_domain_map = _promise_domain_map(promise_vectors)
    activated_domain_map = _domain_activation_map(aggregate)
    non_fallback_ratio = _non_fallback_ratio(natal_graph_v2)
    motif_richness_norm = _motif_richness_norm(signature_motifs)
    top3_promise_avg = _top_average(promise_vectors.values(), count=3)

    natal_promise_strength = clamp01(
        (0.45 * top3_promise_avg)
        + (0.30 * motif_richness_norm)
        + (0.25 * non_fallback_ratio)
    )

    activated_domain_fit = 0.0
    if promise_domain_map:
        weighted_overlap = sum(
            _safe_float(weight) * _safe_float(activated_domain_map.get(domain))
            for domain, weight in promise_domain_map.items()
        )
        top_promise_domain = max(promise_domain_map, key=promise_domain_map.get) if promise_domain_map else None
        top_activation_domain = max(activated_domain_map, key=activated_domain_map.get) if activated_domain_map else None
        if top_promise_domain and top_activation_domain and top_promise_domain == top_activation_domain:
            weighted_overlap += 0.08
        activated_domain_fit = clamp01(weighted_overlap)

    motif_activation_fit = _compute_motif_activation_fit(partner_hits, aggregate, natal_graph_v2)
    house_ruler_fit = _compute_house_ruler_fit(partner_hits, aggregate, natal_graph_v2)

    fallback_penalty = 0.0
    if non_fallback_ratio < 0.58:
        fallback_penalty = round(clamp01((0.58 - non_fallback_ratio) / 0.58) * 0.16, 4)

    score = clamp01(
        (0.35 * natal_promise_strength)
        + (0.30 * activated_domain_fit)
        + (0.20 * motif_activation_fit)
        + (0.15 * house_ruler_fit)
        - fallback_penalty
    )

    return {
        "score": round(score, 4),
        "natal_promise_strength": round(natal_promise_strength, 4),
        "activated_domain_fit": round(activated_domain_fit, 4),
        "motif_activation_fit": round(motif_activation_fit, 4),
        "house_ruler_fit": round(house_ruler_fit, 4),
        "fallback_penalty": round(fallback_penalty, 4),
    }


def compute_promise_alignment(partner_hits: Sequence[Mapping[str, Any]], natal_graph_v2: Mapping[str, Any]) -> float:
    return compute_promise_alignment_breakdown(partner_hits, natal_graph_v2)["score"]


def compute_growth_tension(partner_hits: Sequence[Mapping[str, Any]], natal_graph_v2: Mapping[str, Any]) -> float:
    aggregate = _aggregate_partner_hits(partner_hits)
    activation = sum(_safe_float(item.get("activation")) for item in aggregate.values())
    if activation <= 0.0:
        return 0.0
    tension = 0.0
    for item in aggregate.values():
        promise = _safe_float(item.get("promise"))
        familiarity = _safe_float(item.get("familiarity"))
        hardness = _safe_float(item.get("hardness"))
        activation_score = _safe_float(item.get("activation"))
        tension += activation_score * clamp01(promise * (1.0 - (familiarity * 0.85)) + (0.18 * hardness))
    tension /= activation
    activation_strength = clamp01(activation / 1.8)
    return round(clamp01(0.70 * tension + 0.30 * activation_strength), 4)


def compute_trigger_load(partner_hits: Sequence[Mapping[str, Any]], natal_graph_v2: Mapping[str, Any]) -> float:
    aggregate = _aggregate_partner_hits(partner_hits)
    activation = sum(_safe_float(item.get("activation")) for item in aggregate.values())
    if activation <= 0.0:
        return 0.0
    trigger = sum(_safe_float(item.get("activation")) * _safe_float(item.get("trigger")) for item in aggregate.values()) / activation
    activation_strength = clamp01(activation / 1.8)
    return round(clamp01(0.74 * trigger + 0.26 * activation_strength), 4)


def compute_mutuality(a_scores: Mapping[str, Any], b_scores: Mapping[str, Any]) -> float:
    keys = ("familiarity_resonance", "promise_alignment", "growth_tension", "trigger_load")
    diffs = [abs(_safe_float(a_scores.get(key)) - _safe_float(b_scores.get(key))) for key in keys]
    if not diffs:
        return 0.0
    return round(clamp01(1.0 - (sum(diffs) / len(diffs))), 4)


def compute_asymmetry(a_ctx: Sequence[Mapping[str, Any]], b_ctx: Sequence[Mapping[str, Any]]) -> float:
    a_map = {str(item.get("domain") or ""): _safe_float(item.get("score")) for item in a_ctx}
    b_map = {str(item.get("domain") or ""): _safe_float(item.get("score")) for item in b_ctx}
    domains = sorted(set(a_map) | set(b_map))
    if not domains:
        return 0.0
    diff = sum(abs(a_map.get(domain, 0.0) - b_map.get(domain, 0.0)) for domain in domains) / len(domains)
    if a_ctx and b_ctx and str(a_ctx[0].get("domain") or "") != str(b_ctx[0].get("domain") or ""):
        diff += 0.12
    return round(clamp01(diff), 4)


def compute_magnetic_intensity(
    base_scores: Mapping[str, Any],
    a_scores: Mapping[str, Any],
    b_scores: Mapping[str, Any],
) -> float:
    spark = _safe_float(base_scores.get("spark"))
    depth = _safe_float(base_scores.get("depth"))
    growth = (_safe_float(a_scores.get("growth_tension")) + _safe_float(b_scores.get("growth_tension"))) / 2.0
    trigger = (_safe_float(a_scores.get("trigger_load")) + _safe_float(b_scores.get("trigger_load"))) / 2.0
    familiarity = (_safe_float(a_scores.get("familiarity_resonance")) + _safe_float(b_scores.get("familiarity_resonance"))) / 2.0
    return round(
        clamp01((0.42 * spark) + (0.22 * depth) + (0.16 * growth) + (0.10 * trigger) + (0.10 * familiarity)),
        4,
    )


def compute_sustainable_bond(base_scores: Mapping[str, Any], resonance_scores: Mapping[str, Any]) -> float:
    bond = _safe_float(base_scores.get("bond"))
    confidence = _safe_float(base_scores.get("confidence"))
    avg_familiarity = (
        _safe_float(resonance_scores.get("partner_a", {}).get("familiarity_resonance"))
        + _safe_float(resonance_scores.get("partner_b", {}).get("familiarity_resonance"))
    ) / 2.0
    avg_promise = (
        _safe_float(resonance_scores.get("partner_a", {}).get("promise_alignment"))
        + _safe_float(resonance_scores.get("partner_b", {}).get("promise_alignment"))
    ) / 2.0
    avg_growth = (
        _safe_float(resonance_scores.get("partner_a", {}).get("growth_tension"))
        + _safe_float(resonance_scores.get("partner_b", {}).get("growth_tension"))
    ) / 2.0
    avg_trigger = (
        _safe_float(resonance_scores.get("partner_a", {}).get("trigger_load"))
        + _safe_float(resonance_scores.get("partner_b", {}).get("trigger_load"))
    ) / 2.0
    return round(
        clamp01(
            (0.30 * bond)
            + (0.26 * confidence)
            + (0.22 * avg_promise)
            + (0.12 * avg_familiarity)
            + (0.10 * avg_growth)
            - (0.22 * avg_trigger)
        ),
        4,
    )


def _bodies_in_house(overlay_table: Sequence[Mapping[str, Any]], house: int, bodies: set[str]) -> list[str]:
    found: list[str] = []
    for row in overlay_table:
        if int(row.get("in_house") or 0) != house:
            continue
        body = str(row.get("body") or "").lower()
        if body in bodies:
            found.append(body)
    return sorted(found)


def build_overlay_cluster_summary(overlays: Mapping[str, Any]) -> Dict[str, Any]:
    a_in_b_table = list((overlays.get("a_in_b") or {}).get("table") or [])
    b_in_a_table = list((overlays.get("b_in_a") or {}).get("table") or [])

    details = {
        "8th_personal_cluster_a": _bodies_in_house(b_in_a_table, 8, PERSONAL_CLUSTER_BODIES),
        "8th_personal_cluster_b": _bodies_in_house(a_in_b_table, 8, PERSONAL_CLUSTER_BODIES),
        "12th_pressure_a": _bodies_in_house(b_in_a_table, 12, TWELFTH_PRESSURE_BODIES),
        "12th_pressure_b": _bodies_in_house(a_in_b_table, 12, TWELFTH_PRESSURE_BODIES),
        "4th_root_cluster_a": _bodies_in_house(b_in_a_table, 4, FOURTH_ROOT_BODIES),
        "4th_root_cluster_b": _bodies_in_house(a_in_b_table, 4, FOURTH_ROOT_BODIES),
        "11th_social_cluster_a": _bodies_in_house(b_in_a_table, 11, ELEVENTH_SOCIAL_BODIES),
        "11th_social_cluster_b": _bodies_in_house(a_in_b_table, 11, ELEVENTH_SOCIAL_BODIES),
    }

    summary: Dict[str, Any] = {
        key: len(value)
        for key, value in details.items()
    }
    summary["details"] = details
    return summary


def _pair_hit(
    hit: Mapping[str, Any],
    left: str,
    right: str,
    aspects: Iterable[str] | None = None,
    orb_max: float | None = None,
) -> bool:
    pair = {str(hit.get("a_body") or "").lower(), str(hit.get("b_body") or "").lower()}
    if pair != {left, right}:
        return False
    aspect = str(hit.get("aspect") or "").lower()
    if aspects and aspect not in {str(item).lower() for item in aspects}:
        return False
    if orb_max is not None and _orb_value(hit) > orb_max:
        return False
    return True


def _pluto_hard_personal_hits(aspect_hits: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    out: list[Mapping[str, Any]] = []
    for hit in aspect_hits:
        a_body = str(hit.get("a_body") or "").lower()
        b_body = str(hit.get("b_body") or "").lower()
        aspect = str(hit.get("aspect") or "").lower()
        if aspect not in HARD_ASPECTS:
            continue
        if _orb_value(hit) > 3.0:
            continue
        if a_body == "pluto" and b_body in PLUTO_RISK_TARGETS:
            out.append(hit)
        elif b_body == "pluto" and a_body in PLUTO_RISK_TARGETS:
            out.append(hit)
    return out


def _saturn_angular_hard_hits(aspect_hits: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    out: list[Mapping[str, Any]] = []
    for hit in aspect_hits:
        a_body = str(hit.get("a_body") or "").lower()
        b_body = str(hit.get("b_body") or "").lower()
        aspect = str(hit.get("aspect") or "").lower()
        if aspect not in HARD_ASPECTS:
            continue
        if _orb_value(hit) > 4.0:
            continue
        if a_body == "saturn" and b_body in SATURN_RISK_TARGETS:
            out.append(hit)
        elif b_body == "saturn" and a_body in SATURN_RISK_TARGETS:
            out.append(hit)
    return out


def _uranus_saturn_hard_exact(aspect_hits: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [
        hit
        for hit in aspect_hits
        if _pair_hit(hit, "uranus", "saturn", aspects=HARD_ASPECTS, orb_max=1.0)
    ]


def _relationship_activation(partner_hits: Mapping[str, Sequence[Mapping[str, Any]]], domain: str) -> float:
    activations: list[float] = []
    for hits in partner_hits.values():
        aggregate = _aggregate_partner_hits(hits)
        activations.append(_safe_float(aggregate.get(domain, {}).get("activation")))
    return max(activations) if activations else 0.0


def _make_unscored_entry(reason: str, hit: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "reason": reason,
        "a_body": hit.get("a_body"),
        "b_body": hit.get("b_body"),
        "aspect": hit.get("aspect"),
        "orb_deg": round(_orb_value(hit), 4),
    }


def diminishing_weight(rank: int) -> float:
    table = [1.0, 0.72, 0.55, 0.42, 0.33]
    return table[min(rank, len(table) - 1)]


def _normalize_partner_key(key: str) -> str:
    value = str(key or "").lower()
    if value in {"a", "partner_a"}:
        return "partner_a"
    return "partner_b"


def _partner_suffix(key: str) -> str:
    return "a" if _normalize_partner_key(key) == "partner_a" else "b"


def _partner_direction(key: str) -> str:
    return "b_to_a" if _normalize_partner_key(key) == "partner_a" else "a_to_b"


def _target_partner_label(key: str) -> str:
    return _normalize_partner_key(key)


def _source_partner_label(key: str) -> str:
    return "partner_b" if _normalize_partner_key(key) == "partner_a" else "partner_a"


def _unique_preserve(items: Sequence[Any]) -> list[Any]:
    out: list[Any] = []
    seen: set[Any] = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _incoming_body(hit: Mapping[str, Any]) -> str:
    return str(hit.get("incoming_body") or "").lower()


def _native_body(hit: Mapping[str, Any]) -> str:
    return str(hit.get("native_body") or "").lower()


def _pair_contains_one_of_each(hit: Mapping[str, Any], left: set[str], right: set[str]) -> bool:
    incoming = _incoming_body(hit)
    native = _native_body(hit)
    return (incoming in left and native in right) or (incoming in right and native in left)


def _bundle_hits(
    partner_hits: Sequence[Mapping[str, Any]],
    *,
    domains: Sequence[str] | None = None,
    houses: Sequence[int] | None = None,
    bodies: Sequence[str] | None = None,
    aspects: Sequence[str] | None = None,
    hardness_min: float | None = None,
    sources: Sequence[str] | None = None,
) -> list[Mapping[str, Any]]:
    domain_targets = {str(item) for item in (domains or ())}
    house_targets = {int(item) for item in (houses or ())}
    body_targets = {str(item).lower() for item in (bodies or ())}
    aspect_targets = {str(item).lower() for item in (aspects or ())}
    source_targets = {str(item).lower() for item in (sources or ())}
    out: list[Mapping[str, Any]] = []
    for hit in partner_hits:
        if domain_targets and str(hit.get("domain") or "") not in domain_targets:
            continue
        if house_targets and int(hit.get("activated_house") or 0) not in house_targets:
            continue
        if body_targets and not _body_match(hit, body_targets):
            continue
        if aspect_targets and str(hit.get("aspect") or "").lower() not in aspect_targets:
            continue
        if source_targets and str(hit.get("source") or "").lower() not in source_targets:
            continue
        if hardness_min is not None and _safe_float(hit.get("hardness")) < hardness_min:
            continue
        out.append(hit)
    return out


def _bundle_summary_key(kind: str, partner_key: str) -> str:
    target = _target_partner_label(partner_key)
    source = _source_partner_label(partner_key)
    if kind == "8th_personal_cluster":
        return f"{source}_personals_in_{target}_8th"
    if kind == "12th_pressure_bundle":
        return f"{source}_pressure_in_{target}_12th"
    if kind == "roots_home_bundle":
        return f"{source}_roots_in_{target}_4th"
    if kind == "social_future_bundle":
        return f"{source}_social_future_in_{target}_11th"
    if kind == "pluto_personal_bundle":
        return f"{source}_pluto_personal_into_{target}"
    if kind == "saturn_angular_bundle":
        return f"{source}_saturn_angular_to_{target}"
    if kind == "soft_attraction_bundle":
        return f"{source}_soft_attraction_to_{target}"
    if kind == "identity_activation_bundle":
        return f"{source}_identity_activation_for_{target}"
    if kind == "nodal_fated_bundle":
        return f"{source}_nodal_axis_to_{target}"
    if kind == "communication_bridge_bundle":
        return f"{source}_communication_bridge_to_{target}"
    return f"{source}_{kind}_to_{target}"


def _bundle_payload_from_hits(
    *,
    kind: str,
    partner_key: str,
    partner_hits: Sequence[Mapping[str, Any]],
    natal_graph_v2: Mapping[str, Any],
    extra_evidence: Sequence[str] | None = None,
    count_override: int | None = None,
) -> dict | None:
    if not partner_hits and not count_override:
        return None

    bundle_scale = BUNDLE_KIND_SCORE_SCALE.get(kind, 0.82)
    hits_sorted = sorted(
        partner_hits,
        key=lambda item: (
            -_safe_float(item.get("activation_score")),
            _orb_value(item),
            str(item.get("domain") or ""),
            str(item.get("incoming_body") or ""),
        ),
    )
    scored_hits = hits_sorted[:6]
    domain = BUNDLE_TO_DOMAIN.get(kind, str(hits_sorted[0].get("domain") or "") if hits_sorted else "")
    if not domain:
        return None

    weighted_activation = 0.0
    familiarity_sum = 0.0
    promise_sum = 0.0
    trigger_sum = 0.0
    hardness_sum = 0.0
    weight_sum = 0.0
    evidence: list[str] = list(extra_evidence or [])
    unique_units: list[str] = []
    source_record_ids = _unique_preserve(
        [str(hit.get("source_record_id") or "") for hit in hits_sorted if str(hit.get("source_record_id") or "")]
    )
    expanded_hit_ids = _unique_preserve(
        [str(hit.get("hit_id") or "") for hit in hits_sorted if str(hit.get("hit_id") or "")]
    )

    unique_hit_signatures: list[tuple[Any, ...]] = []
    for idx, hit in enumerate(scored_hits):
        weight = diminishing_weight(idx)
        activation = _safe_float(hit.get("activation_score"))
        weighted_activation += activation * weight
        familiarity_sum += _safe_float(hit.get("familiarity_boost")) * weight
        promise_sum += _safe_float(hit.get("promise_boost")) * weight
        trigger_sum += _safe_float(hit.get("trigger_risk")) * weight
        hardness_sum += _safe_float(hit.get("hardness")) * weight
        weight_sum += weight
        incoming = _incoming_body(hit)
        native = _native_body(hit)
        if incoming:
            unique_units.append(incoming)
        elif native:
            unique_units.append(native)
        unique_hit_signatures.append(
            (
                incoming,
                native,
                str(hit.get("aspect") or ""),
                int(hit.get("activated_house") or 0),
                str(hit.get("domain") or ""),
            )
        )
        for because in hit.get("because") or []:
            if isinstance(because, str):
                evidence.append(because)

    unique_hit_count = len(source_record_ids)
    structural_count = max(
        count_override or 0,
        len(source_record_ids),
        len(_unique_preserve(unique_hit_signatures)),
        len(_unique_preserve(unique_units)),
    )
    display_count = min(5, len(_unique_preserve(evidence)))
    familiarity = clamp01(familiarity_sum / weight_sum) if weight_sum > 0.0 else 0.0
    promise_fit = clamp01(promise_sum / weight_sum) if weight_sum > 0.0 else 0.0
    trigger_cost = clamp01(trigger_sum / weight_sum) if weight_sum > 0.0 else 0.0
    hardness_mix = clamp01(hardness_sum / weight_sum) if weight_sum > 0.0 else 0.0
    domain_fit = _safe_float((natal_graph_v2.get("domain_vectors") or {}).get(domain))
    base_sum = weighted_activation + min(0.24, 0.04 * structural_count)
    score = clamp01(
        (1.0 - math.exp(-base_sum * 1.25))
        * (0.80 + (0.12 * promise_fit) + (0.08 * domain_fit))
        * bundle_scale
    )

    return {
        "bundle_id": f"{_partner_direction(partner_key)}_{kind}",
        "domain": domain,
        "direction": _partner_direction(partner_key),
        "kind": kind,
        "score": round(score, 4),
        "familiarity": round(familiarity, 4),
        "promise_fit": round(promise_fit, 4),
        "trigger_cost": round(trigger_cost, 4),
        "hardness_mix": round(hardness_mix, 4),
        "count": int(unique_hit_count),
        "unique_hit_count": int(unique_hit_count),
        "structural_count": int(structural_count),
        "displayed_evidence_count": int(display_count),
        "source_hit_ids": source_record_ids,
        "expanded_hit_ids": expanded_hit_ids,
        "summary_key": _bundle_summary_key(kind, partner_key),
        "evidence": _unique_preserve(evidence)[:5],
    }


def _build_partner_activation_bundles(
    partner_key: str,
    partner_hits: Sequence[Mapping[str, Any]],
    overlay_cluster_summary: Mapping[str, Any],
    natal_graph_v2: Mapping[str, Any],
) -> list[dict]:
    suffix = _partner_suffix(partner_key)
    details = overlay_cluster_summary.get("details") if isinstance(overlay_cluster_summary, Mapping) else {}
    details = details if isinstance(details, Mapping) else {}
    bundle_candidates: list[dict] = []

    def add_bundle(
        kind: str,
        hits: Sequence[Mapping[str, Any]],
        *,
        extra_evidence: Sequence[str] | None = None,
        count_override: int | None = None,
        min_score: float = 0.16,
    ) -> None:
        bundle = _bundle_payload_from_hits(
            kind=kind,
            partner_key=partner_key,
            partner_hits=hits,
            natal_graph_v2=natal_graph_v2,
            extra_evidence=extra_evidence,
            count_override=count_override,
        )
        if not bundle:
            return
        if _safe_float(bundle.get("score")) < min_score:
            return
        bundle["min_score"] = round(min_score, 4)
        bundle["candidate_hit_ids"] = list(bundle.get("source_hit_ids") or [])
        bundle_candidates.append(bundle)

    cluster_8th = list(details.get(f"8th_personal_cluster_{suffix}") or [])
    if len(cluster_8th) >= 3:
        hits = [
            hit
            for hit in partner_hits
            if int(hit.get("activated_house") or 0) == 8
            and _incoming_body(hit) in {str(body).lower() for body in cluster_8th}
        ]
        add_bundle(
            "8th_personal_cluster",
            hits,
            extra_evidence=[f"{body} in 8th" for body in cluster_8th],
            count_override=len(cluster_8th),
            min_score=0.20,
        )

    cluster_12th = list(details.get(f"12th_pressure_{suffix}") or [])
    if len(cluster_12th) >= 2:
        hits = [
            hit
            for hit in partner_hits
            if int(hit.get("activated_house") or 0) == 12
            and _incoming_body(hit) in {str(body).lower() for body in cluster_12th}
        ]
        add_bundle(
            "12th_pressure_bundle",
            hits,
            extra_evidence=[f"{body} in 12th" for body in cluster_12th],
            count_override=len(cluster_12th),
            min_score=0.18,
        )

    cluster_4th = list(details.get(f"4th_root_cluster_{suffix}") or [])
    cluster_11th = list(details.get(f"11th_social_cluster_{suffix}") or [])
    home_hits = [
        hit
        for hit in partner_hits
        if str(hit.get("domain") or "") == "home_roots"
        or int(hit.get("activated_house") or 0) == 4
        or (_body_match(hit, ROOTS_BODIES) and int(hit.get("activated_house") or 0) in {4, 5})
    ]
    if len(cluster_4th) >= 3 or _activation_peak(home_hits) >= 0.18:
        add_bundle(
            "roots_home_bundle",
            home_hits,
            extra_evidence=[f"{body} in 4th" for body in cluster_4th],
            count_override=max(len(cluster_4th), min(6, len(home_hits))),
            min_score=0.17,
        )

    social_hits = [
        hit
        for hit in partner_hits
        if str(hit.get("domain") or "") == "social_future"
        or int(hit.get("activated_house") or 0) == 11
        or (_body_match(hit, ELEVENTH_SOCIAL_BODIES) and int(hit.get("activated_house") or 0) in {5, 11})
    ]
    if len(cluster_11th) >= 2 or _activation_peak(social_hits) >= 0.16:
        add_bundle(
            "social_future_bundle",
            social_hits,
            extra_evidence=[f"{body} in 11th" for body in cluster_11th],
            count_override=max(len(cluster_11th), min(6, len(social_hits))),
            min_score=0.15,
        )

    identity_hits = [
        hit
        for hit in partner_hits
        if str(hit.get("domain") or "") == "identity"
        or int(hit.get("activated_house") or 0) == 1
        or (_body_match(hit, IDENTITY_BODIES) and int(hit.get("activated_house") or 0) in {1, 7, 9, 10})
    ]
    if len(identity_hits) >= 2 or _activation_peak(identity_hits) >= 0.18:
        add_bundle("identity_activation_bundle", identity_hits, min_score=0.16)

    communication_hits = [
        hit
        for hit in partner_hits
        if str(hit.get("domain") or "") in {"mind_communication", "meaning_learning"}
        or int(hit.get("activated_house") or 0) in {3, 9}
        or (_body_match(hit, COMMUNICATION_BODIES) and int(hit.get("activated_house") or 0) in {3, 9, 12})
    ]
    if len(communication_hits) >= 2 or _activation_peak(communication_hits) >= 0.16:
        add_bundle("communication_bridge_bundle", communication_hits, min_score=0.15)

    nodal_hits = [
        hit
        for hit in partner_hits
        if _body_match(hit, NODAL_BODIES)
        and str(hit.get("domain") or "") in {"meaning_learning", "relationships", "intimacy_depth", "identity"}
    ]
    if len(nodal_hits) >= 2:
        add_bundle("nodal_fated_bundle", nodal_hits, min_score=0.16)

    soft_hits = [
        hit
        for hit in partner_hits
        if str(hit.get("aspect") or "").lower() in SOFT_ASPECTS
        and _orb_value(hit) <= 2.6
        and _body_match(hit, SOFT_ATTRACTION_BODIES)
        and str(hit.get("domain") or "") in {"relationships", "intimacy_depth", "identity", "home_roots", "creativity_talent"}
    ]
    if len(soft_hits) >= 2:
        add_bundle("soft_attraction_bundle", soft_hits, min_score=0.18)

    pluto_hits = [
        hit
        for hit in partner_hits
        if _pair_contains_one_of_each(hit, {"pluto"}, PERSONAL_CLUSTER_BODIES)
        and _safe_float(hit.get("hardness")) >= 0.55
        and _orb_value(hit) <= 3.2
    ]
    if len(pluto_hits) >= 2 or _activation_peak(pluto_hits) >= 0.16:
        add_bundle("pluto_personal_bundle", pluto_hits, min_score=0.18)

    saturn_hits = [
        hit
        for hit in partner_hits
        if (
            _pair_contains_one_of_each(hit, {"saturn"}, ANGULAR_BODIES | SATURN_RISK_TARGETS)
            or (_incoming_body(hit) == "mc" and _native_body(hit) == "saturn")
            or (_incoming_body(hit) == "asc" and _native_body(hit) == "saturn")
            or (_incoming_body(hit) == "saturn" and _native_body(hit) in ANGULAR_BODIES)
        )
        and (
            (_safe_float(hit.get("hardness")) >= 0.85 and _orb_value(hit) <= 4.0)
            or (str(hit.get("aspect") or "").lower() in {"trine", "sextile"} and _orb_value(hit) <= 2.6)
        )
    ]
    if saturn_hits:
        add_bundle("saturn_angular_bundle", saturn_hits, min_score=0.16)

    if not bundle_candidates:
        return []

    source_hits: Dict[str, list[Mapping[str, Any]]] = {}
    for hit in partner_hits:
        source_record_id = str(hit.get("source_record_id") or "")
        if not source_record_id:
            continue
        source_hits.setdefault(source_record_id, []).append(hit)
    owned_source_ids: set[str] = set()
    bundles: list[dict] = []
    candidates_sorted = sorted(
        bundle_candidates,
        key=lambda item: (
            BUNDLE_KIND_PRIORITY.get(str(item.get("kind") or ""), 99),
            -_safe_float(item.get("score")),
            str(item.get("kind") or ""),
        ),
    )

    for candidate in candidates_sorted:
        candidate_source_ids = [
            source_id
            for source_id in candidate.get("candidate_hit_ids") or []
            if source_id in source_hits
        ]
        owned_for_bundle = [
            hit
            for source_id in candidate_source_ids
            if source_id not in owned_source_ids
            for hit in source_hits[source_id]
        ]
        secondary_source_ids = [source_id for source_id in candidate_source_ids if source_id in owned_source_ids]
        overlap_ratio = (len(secondary_source_ids) / len(candidate_source_ids)) if candidate_source_ids else 0.0

        if not owned_for_bundle:
            continue

        rebuilt = _bundle_payload_from_hits(
            kind=str(candidate.get("kind") or ""),
            partner_key=partner_key,
            partner_hits=owned_for_bundle,
            natal_graph_v2=natal_graph_v2,
            extra_evidence=list(candidate.get("evidence") or []),
            count_override=None,
        )
        if not rebuilt:
            continue
        if overlap_ratio >= 0.45:
            decayed_score = _safe_float(rebuilt.get("score")) * max(0.55, 1.0 - (0.50 * overlap_ratio))
            rebuilt["score"] = round(decayed_score, 4)
        if _safe_float(rebuilt.get("score")) < _safe_float(candidate.get("min_score")):
            continue

        rebuilt["secondary_hit_ids"] = secondary_source_ids
        rebuilt["overlap_ratio"] = round(overlap_ratio, 4)
        rebuilt["candidate_hit_ids"] = candidate_source_ids
        bundles.append(rebuilt)
        owned_source_ids.update(rebuilt.get("source_hit_ids") or [])

    bundles = sorted(
        bundles,
        key=lambda item: (
            -_safe_float(item.get("score")),
            -int(item.get("unique_hit_count") or item.get("count") or 0),
            str(item.get("kind") or ""),
        ),
    )
    return bundles[:12]


def build_activation_bundles(
    resonance_hits: Mapping[str, Sequence[Mapping[str, Any]]],
    overlay_cluster_summary: Mapping[str, Any],
    natal_graph_v2: Mapping[str, Mapping[str, Any]],
) -> dict:
    bundles_by_partner: Dict[str, list[dict]] = {}
    for partner_key in ("partner_a", "partner_b"):
        hits = list(resonance_hits.get(partner_key) or resonance_hits.get("a" if partner_key == "partner_a" else "b") or [])
        graph = natal_graph_v2.get(partner_key) if isinstance(natal_graph_v2, Mapping) else {}
        graph = graph if isinstance(graph, Mapping) else {}
        bundles_by_partner[partner_key] = _build_partner_activation_bundles(
            partner_key=partner_key,
            partner_hits=hits,
            overlay_cluster_summary=overlay_cluster_summary,
            natal_graph_v2=graph,
        )
    return bundles_by_partner


def rank_partner_domains(bundles_by_partner: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict:
    rankings: Dict[str, list[dict]] = {}
    for partner_key in ("partner_a", "partner_b"):
        bundles = list(bundles_by_partner.get(partner_key) or [])
        grouped: Dict[str, list[Mapping[str, Any]]] = {}
        for bundle in bundles:
            domain = str(bundle.get("domain") or "")
            if not domain:
                continue
            grouped.setdefault(domain, []).append(bundle)

        rows: list[dict] = []
        for domain, domain_bundles in grouped.items():
            sorted_bundles = sorted(
                domain_bundles,
                key=lambda item: (-_safe_float(item.get("score")), str(item.get("kind") or "")),
            )
            weighted_sum = 0.0
            familiarity = 0.0
            promise = 0.0
            trigger = 0.0
            weight_sum = 0.0
            evidence: list[str] = []
            bundle_ids: list[str] = []
            for idx, bundle in enumerate(sorted_bundles):
                weight = diminishing_weight(idx)
                kind_scale = BUNDLE_KIND_SCORE_SCALE.get(str(bundle.get("kind") or ""), 0.82)
                bundle_score = _safe_float(bundle.get("score")) * kind_scale
                weighted_sum += bundle_score * weight
                familiarity += _safe_float(bundle.get("familiarity")) * weight
                promise += _safe_float(bundle.get("promise_fit")) * weight
                trigger += _safe_float(bundle.get("trigger_cost")) * weight
                weight_sum += weight
                bundle_ids.append(str(bundle.get("bundle_id") or ""))
                evidence.extend(bundle.get("evidence") or [])
            structural_bonus = 0.0
            bundle_kinds = {str(bundle.get("kind") or "") for bundle in sorted_bundles}
            if bundle_kinds & {"8th_personal_cluster", "roots_home_bundle", "12th_pressure_bundle"}:
                structural_bonus += 0.14
            if "pluto_personal_bundle" in bundle_kinds:
                structural_bonus += 0.05
            if domain == "relationships" and bundle_kinds <= {"soft_attraction_bundle", "saturn_angular_bundle"}:
                structural_bonus -= 0.08
            if domain == "home_roots" and "roots_home_bundle" in bundle_kinds:
                structural_bonus += 0.08
            if domain == "private_inner_world" and "12th_pressure_bundle" in bundle_kinds:
                structural_bonus += 0.06
            domain_score = clamp01(1.0 - math.exp(-(weighted_sum + structural_bonus) * 1.05))
            rows.append(
                {
                    "domain": domain,
                    "score": round(domain_score, 4),
                    "familiarity": round(clamp01(familiarity / weight_sum) if weight_sum > 0.0 else 0.0, 4),
                    "promise_fit": round(clamp01(promise / weight_sum) if weight_sum > 0.0 else 0.0, 4),
                    "trigger_cost": round(clamp01(trigger / weight_sum) if weight_sum > 0.0 else 0.0, 4),
                    "bundle_count": len(sorted_bundles),
                    "bundle_ids": bundle_ids[:4],
                    "because": _unique_preserve(evidence)[:6],
                }
            )

        rows = sorted(rows, key=lambda item: (-_safe_float(item.get("score")), str(item.get("domain") or "")))
        for idx, row in enumerate(rows):
            if idx == 0:
                row["tier"] = "primary"
            elif idx < 3 and _safe_float(row.get("score")) >= 0.20:
                row["tier"] = "secondary"
            else:
                row["tier"] = "background"
        rankings[partner_key] = rows
    return rankings


def _ranking_score_map(rows: Sequence[Mapping[str, Any]]) -> Dict[str, float]:
    return {
        str(row.get("domain") or ""): _safe_float(row.get("score"))
        for row in rows
        if str(row.get("domain") or "")
    }


def compute_directional_asymmetry(
    resonance_scores: Mapping[str, Any],
    overlay_cluster_summary: Mapping[str, Any],
    domain_rankings: Mapping[str, Sequence[Mapping[str, Any]]],
) -> float:
    a_rows = list(domain_rankings.get("partner_a") or [])
    b_rows = list(domain_rankings.get("partner_b") or [])
    a_map = _ranking_score_map(a_rows)
    b_map = _ranking_score_map(b_rows)

    a_top_activation = _top_average([row.get("score") for row in a_rows], count=2)
    b_top_activation = _top_average([row.get("score") for row in b_rows], count=2)
    activation_gap = abs(a_top_activation - b_top_activation)

    familiarity_gap = abs(
        _safe_float(resonance_scores.get("partner_a", {}).get("familiarity_resonance"))
        - _safe_float(resonance_scores.get("partner_b", {}).get("familiarity_resonance"))
    )
    trigger_gap = abs(
        _safe_float(resonance_scores.get("partner_a", {}).get("trigger_load"))
        - _safe_float(resonance_scores.get("partner_b", {}).get("trigger_load"))
    )
    promise_gap = abs(
        _safe_float(resonance_scores.get("partner_a", {}).get("promise_alignment"))
        - _safe_float(resonance_scores.get("partner_b", {}).get("promise_alignment"))
    )

    directional_cluster_gap = (
        abs(int(overlay_cluster_summary.get("8th_personal_cluster_a") or 0) - int(overlay_cluster_summary.get("8th_personal_cluster_b") or 0)) / 5.0
        + abs(int(overlay_cluster_summary.get("4th_root_cluster_a") or 0) - int(overlay_cluster_summary.get("4th_root_cluster_b") or 0)) / 5.0
        + abs(int(overlay_cluster_summary.get("12th_pressure_a") or 0) - int(overlay_cluster_summary.get("12th_pressure_b") or 0)) / 3.0
    ) / 3.0
    directional_cluster_gap = clamp01(directional_cluster_gap)

    domains = sorted(set(a_map) | set(b_map))
    domain_shape_gap = 0.0
    if domains:
        domain_shape_gap = clamp01(
            sum(abs(a_map.get(domain, 0.0) - b_map.get(domain, 0.0)) for domain in domains) / len(domains)
        )

    top_domain_bonus = 0.08 if a_rows and b_rows and str(a_rows[0].get("domain") or "") != str(b_rows[0].get("domain") or "") else 0.0
    asymmetry_raw = (
        (0.28 * activation_gap)
        + (0.22 * familiarity_gap)
        + (0.22 * trigger_gap)
        + (0.14 * promise_gap)
        + (0.14 * directional_cluster_gap)
        + (0.10 * domain_shape_gap)
        + top_domain_bonus
    )
    return round(clamp01(asymmetry_raw), 4)


def build_relational_modes(
    resonance_scores: Mapping[str, Any],
    promise_alignment_breakdown: Mapping[str, Mapping[str, Any]],
) -> dict:
    modes: Dict[str, dict] = {}
    for partner_key in ("partner_a", "partner_b"):
        resonance = resonance_scores.get(partner_key, {}) if isinstance(resonance_scores, Mapping) else {}
        breakdown = promise_alignment_breakdown.get(partner_key, {}) if isinstance(promise_alignment_breakdown, Mapping) else {}
        comfort_pull = clamp01(
            (0.72 * _safe_float(resonance.get("familiarity_resonance")))
            + (0.14 * (1.0 - _safe_float(resonance.get("trigger_load"))))
            + (0.14 * _safe_float(breakdown.get("activated_domain_fit")))
        )
        growth_pull = clamp01(
            (0.48 * _safe_float(resonance.get("growth_tension")))
            + (0.30 * _safe_float(resonance.get("promise_alignment")))
            + (0.22 * _safe_float(breakdown.get("motif_activation_fit")))
        )
        modes[partner_key] = {
            "comfort_pull": round(comfort_pull, 4),
            "growth_pull": round(growth_pull, 4),
            "trigger_load": round(_safe_float(resonance.get("trigger_load")), 4),
        }
    return modes


def build_relationship_calibration(
    corrected_scores: Mapping[str, Any],
    resonance_scores: Mapping[str, Any],
    relational_modes: Mapping[str, Mapping[str, Any]],
    asymmetry: float,
) -> dict:
    avg_comfort = (
        _safe_float(relational_modes.get("partner_a", {}).get("comfort_pull"))
        + _safe_float(relational_modes.get("partner_b", {}).get("comfort_pull"))
    ) / 2.0
    avg_growth = (
        _safe_float(relational_modes.get("partner_a", {}).get("growth_pull"))
        + _safe_float(relational_modes.get("partner_b", {}).get("growth_pull"))
    ) / 2.0
    avg_trigger = (
        _safe_float(relational_modes.get("partner_a", {}).get("trigger_load"))
        + _safe_float(relational_modes.get("partner_b", {}).get("trigger_load"))
    ) / 2.0
    mutuality = _safe_float(resonance_scores.get("relationship", {}).get("mutuality"))
    sustainable = _safe_float(resonance_scores.get("relationship", {}).get("sustainable_bond"))
    magnetic = _safe_float(resonance_scores.get("relationship", {}).get("magnetic_intensity"))
    promise_avg = (
        _safe_float(resonance_scores.get("partner_a", {}).get("promise_alignment"))
        + _safe_float(resonance_scores.get("partner_b", {}).get("promise_alignment"))
    ) / 2.0

    return {
        "shared_pull": round(
            clamp01((0.36 * _safe_float(corrected_scores.get("bond"))) + (0.34 * _safe_float(corrected_scores.get("spark"))) + (0.30 * avg_comfort)),
            4,
        ),
        "shared_depth": round(
            clamp01((0.46 * _safe_float(corrected_scores.get("depth"))) + (0.24 * avg_growth) + (0.18 * promise_avg) + (0.12 * magnetic)),
            4,
        ),
        "shared_stability": round(
            clamp01((0.34 * sustainable) + (0.26 * mutuality) + (0.20 * avg_comfort) + (0.20 * (1.0 - _safe_float(corrected_scores.get("risk_index"))))),
            4,
        ),
        "shared_tension": round(
            clamp01((0.34 * _safe_float(corrected_scores.get("risk_index"))) + (0.26 * avg_trigger) + (0.22 * magnetic) + (0.18 * avg_growth)),
            4,
        ),
        "directional_asymmetry": round(clamp01(asymmetry), 4),
        "narrative_confidence": round(
            clamp01((0.54 * _safe_float(corrected_scores.get("confidence"))) + (0.18 * mutuality) + (0.16 * promise_avg) + (0.12 * (1.0 - asymmetry))),
            4,
        ),
    }


def _bundle_kind_exists(bundles_by_partner: Mapping[str, Sequence[Mapping[str, Any]]], kind: str) -> bool:
    for bundles in bundles_by_partner.values():
        if any(str(bundle.get("kind") or "") == kind for bundle in bundles):
            return True
    return False


def _narrative_mode_label(mode_row: Mapping[str, Any]) -> str:
    comfort = _safe_float(mode_row.get("comfort_pull"))
    growth = _safe_float(mode_row.get("growth_pull"))
    trigger = _safe_float(mode_row.get("trigger_load"))
    if comfort >= 0.62 and trigger >= 0.55:
        return "deep_familiar_but_triggering"
    if growth >= 0.62 and comfort < 0.55:
        return "growth_oriented_less_familiar"
    if comfort >= 0.62 and growth >= 0.55:
        return "familiar_growth_mix"
    if trigger >= 0.62 and comfort < 0.50:
        return "high_charge_low_comfort"
    if comfort >= 0.58:
        return "comfort_forward"
    if growth >= 0.58:
        return "growth_forward"
    return "mixed_activation"


_HOUSE_ROUTE_RE = re.compile(r"(\d+)(?:st|nd|rd|th) ruler [^ ]+ in (\d+)(?:st|nd|rd|th)")


def _bundle_by_kind(bundles: Sequence[Mapping[str, Any]], kind: str) -> Mapping[str, Any]:
    for bundle in bundles:
        if str(bundle.get("kind") or "") == kind:
            return bundle
    return {}


def _bundle_domain_peak(bundles: Sequence[Mapping[str, Any]], domain: str) -> float:
    best = 0.0
    for bundle in bundles:
        if str(bundle.get("domain") or "") != domain:
            continue
        best = max(best, _safe_float(bundle.get("score")))
    return best


def _bundle_routes_to(bundle: Mapping[str, Any], source_house: int, targets: set[int]) -> bool:
    for item in bundle.get("evidence") or []:
        match = _HOUSE_ROUTE_RE.search(str(item))
        if not match:
            continue
        from_house = int(match.group(1))
        to_house = int(match.group(2))
        if from_house == source_house and to_house in targets:
            return True
    return False


def _candidate_story_score(
    *,
    row: Mapping[str, Any],
    domain_bundle_peak: float,
    routed_bonus: float = 0.0,
    structural_bonus: float = 0.0,
) -> float:
    return round(
        clamp01(
            (0.50 * _safe_float(row.get("score")))
            + (0.25 * domain_bundle_peak)
            + (0.15 * _safe_float(row.get("promise_fit")))
            + routed_bonus
            + structural_bonus
        ),
        4,
    )


def _story_summary_line(primary_domain: str, secondary_domain: str, mode: str) -> str:
    primary = domain_label(primary_domain)
    secondary = domain_label(secondary_domain)
    if primary_domain == "home_roots" and secondary_domain:
        return f"Bu bağ bu tarafta önce {primary} tarafını açıyor; ardından {secondary} duygusu da ilişkiye karışıyor."
    if primary_domain == "intimacy_depth" and secondary_domain:
        return f"Bu bağ bu tarafta kısa sürede {primary} alanına iniyor; {secondary} de hemen arkasından devreye giriyor."
    if primary_domain == "private_inner_world":
        return f"Bu bağ bu tarafta açık bir gösteriden çok, içerde büyüyen bir yakınlık gibi yaşanıyor."
    if primary_domain == "social_future":
        return f"Bu bağ bu tarafta önce ortak alan, akış ve birlikte olma hissi üzerinden çalışıyor."
    if primary_domain:
        if secondary_domain:
            return f"Bu bağ bu tarafta en çok {primary} alanında hissediliyor; {secondary} da bu deneyimin ikinci damarını oluşturuyor."
        return f"Bu bağ bu tarafta en çok {primary} alanında hissediliyor."
    return f"Bu bağ bu tarafta {mode_label(mode)} bir tonda çalışıyor."


def _relationship_shape_summary(mutuality: float, asymmetry: float, sustainability: float) -> str:
    return (
        f"{mutuality_phrase(mutuality).capitalize()}; ama ilişki {asymmetry_phrase(asymmetry)} "
        f"ve bu yüzden uzun vadede {sustainability_band(sustainability)} bir taşıma kapasitesi gösteriyor."
    )


def _resolve_partner_story(
    *,
    partner_key: str,
    bundles_by_partner: Mapping[str, Sequence[Mapping[str, Any]]],
    domain_rankings: Mapping[str, Sequence[Mapping[str, Any]]],
    relational_modes: Mapping[str, Mapping[str, Any]],
    overlay_cluster_summary: Mapping[str, Any],
) -> dict:
    rows = list(domain_rankings.get(partner_key) or [])
    mode_row = relational_modes.get(partner_key, {}) if isinstance(relational_modes, Mapping) else {}
    bundles = list(bundles_by_partner.get(partner_key) or [])
    suffix = _partner_suffix(partner_key)
    top_row = rows[0] if rows else {}
    top_bundle = bundles[0] if bundles else {}
    surface_domain = str(top_row.get("domain") or "")

    if not rows:
        return {
            "primary_domain": "",
            "secondary_domain": "",
            "surface_domain": "",
            "background_domain": "",
            "mode": _narrative_mode_label(mode_row),
            "modifier": "",
            "lived_as": "",
            "routed_through": "",
            "top_bundle_kind": str(top_bundle.get("kind") or ""),
        }

    home_bundle = _bundle_by_kind(bundles, "roots_home_bundle")
    private_bundle = _bundle_by_kind(bundles, "12th_pressure_bundle")
    social_bundle = _bundle_by_kind(bundles, "social_future_bundle")
    intimacy_bundle = _bundle_by_kind(bundles, "8th_personal_cluster")
    pluto_bundle = _bundle_by_kind(bundles, "pluto_personal_bundle")

    cluster_8th = int(overlay_cluster_summary.get(f"8th_personal_cluster_{suffix}") or 0)
    cluster_4th = int(overlay_cluster_summary.get(f"4th_root_cluster_{suffix}") or 0)
    cluster_11th = int(overlay_cluster_summary.get(f"11th_social_cluster_{suffix}") or 0)
    cluster_12th = int(overlay_cluster_summary.get(f"12th_pressure_{suffix}") or 0)

    home_routed_deeper = bool(home_bundle) and _bundle_routes_to(home_bundle, 4, {8, 12})
    private_self_routed = bool(private_bundle) and _bundle_routes_to(private_bundle, 12, {8, 12})

    primary_domain = surface_domain
    second_row = rows[1] if len(rows) > 1 else {}
    secondary_domain = str(second_row.get("domain") or "")
    if primary_domain == "home_roots" and private_bundle:
        secondary_domain = "private_inner_world"
    elif primary_domain == "private_inner_world" and home_bundle:
        secondary_domain = "home_roots"

    background_domain = ""
    if social_bundle and "social_future" not in {primary_domain, secondary_domain}:
        background_domain = "social_future"
    else:
        for row in rows[2:5]:
            candidate_domain = str(row.get("domain") or "")
            if candidate_domain and candidate_domain not in {primary_domain, secondary_domain}:
                background_domain = candidate_domain
                break

    modifier = ""
    lived_as = ""
    routed_through = ""
    selection_reason = ""
    if primary_domain == "home_roots" and home_routed_deeper:
        modifier = "private_or_deepened"
        lived_as = "Güven duygusu burada hemen yüzeye çıkmıyor; daha içte ve daha derinden kuruluyor."
        routed_through = "4th_to_8th_or_12th"
    elif primary_domain == "private_inner_world":
        modifier = "inner_processing"
        lived_as = "Bağ burada daha çok içe alınan, sessizce büyüyen bir hatta yaşanıyor."
        routed_through = "12th_emphasis"
    elif primary_domain == "intimacy_depth":
        modifier = "direct_depth"
        lived_as = "Bağ burada doğrudan mahremiyet, yoğunluk ve dönüşüm alanına iniyor."
        routed_through = "8th_cluster"
    elif primary_domain == "social_future":
        modifier = "social_opening"
        lived_as = "Bağ burada önce ortak alan, sosyal akış ve birlikte olma hissinde görünür oluyor."
        routed_through = "11th_cluster"

    summary_line = _story_summary_line(primary_domain, secondary_domain, _narrative_mode_label(mode_row))

    return {
        "primary_domain": primary_domain,
        "primary_label": domain_label(primary_domain),
        "secondary_domain": secondary_domain,
        "secondary_label": domain_label(secondary_domain) if secondary_domain else "",
        "surface_domain": surface_domain,
        "background_domain": background_domain,
        "background_label": domain_label(background_domain) if background_domain else "",
        "mode": _narrative_mode_label(mode_row),
        "mode_label": mode_label(_narrative_mode_label(mode_row)),
        "modifier": modifier,
        "lived_as": lived_as,
        "summary_line": summary_line,
        "routed_through": routed_through,
        "top_bundle_kind": str(top_bundle.get("kind") or ""),
        "top_bundle_score": round(_safe_float(top_bundle.get("score")), 4),
        "selection_reason": selection_reason or summary_line,
        "story_candidates": [
            {
                "domain": str(row.get("domain") or ""),
                "score": round(_safe_float(row.get("score")), 4),
                "promise_fit": round(_safe_float(row.get("promise_fit")), 4),
            }
            for row in rows[:4]
            if str(row.get("domain") or "")
        ],
    }


def build_narrative_ready_summary(
    bundles_by_partner: Mapping[str, Sequence[Mapping[str, Any]]],
    domain_rankings: Mapping[str, Sequence[Mapping[str, Any]]],
    relational_modes: Mapping[str, Mapping[str, Any]],
    corrected_scores: Mapping[str, Any],
    asymmetry: float,
    overlay_cluster_summary: Mapping[str, Any] | None = None,
) -> dict:
    a_rows = list(domain_rankings.get("partner_a") or [])
    b_rows = list(domain_rankings.get("partner_b") or [])
    overlay_cluster_summary = overlay_cluster_summary if isinstance(overlay_cluster_summary, Mapping) else {}
    a_top_domain = str(a_rows[0].get("domain") or "") if a_rows else ""
    b_top_domain = str(b_rows[0].get("domain") or "") if b_rows else ""

    shared_theme = "mixed_activation_field"
    if (
        a_top_domain == "intimacy_depth"
        and b_top_domain == "intimacy_depth"
        and _safe_float(corrected_scores.get("depth")) >= 0.62
        and _safe_float(corrected_scores.get("spark")) >= 0.55
    ):
        shared_theme = "intense_magnetic_depth"
    elif (
        _safe_float(corrected_scores.get("bond")) >= 0.58
        and (
            _bundle_kind_exists(bundles_by_partner, "roots_home_bundle")
            or {a_top_domain, b_top_domain} & {"home_roots", "private_inner_world"}
        )
    ):
        shared_theme = "rooted_binding_pull"
    elif _safe_float(corrected_scores.get("spark")) >= 0.60:
        shared_theme = "chemistry_forward_contact"

    shared_support = "activation_without_clear_soft_buffer"
    if _bundle_kind_exists(bundles_by_partner, "soft_attraction_bundle") and _bundle_kind_exists(bundles_by_partner, "communication_bridge_bundle"):
        shared_support = "soft_attraction_plus_mental_flow"
    elif _bundle_kind_exists(bundles_by_partner, "soft_attraction_bundle"):
        shared_support = "soft_attraction_buffer"
    elif _bundle_kind_exists(bundles_by_partner, "roots_home_bundle"):
        shared_support = "roots_and_home_support"
    elif _bundle_kind_exists(bundles_by_partner, "communication_bridge_bundle"):
        shared_support = "mental_flow_support"

    shared_tension = "manageable_tension"
    if _bundle_kind_exists(bundles_by_partner, "saturn_angular_bundle") and _bundle_kind_exists(bundles_by_partner, "pluto_personal_bundle"):
        shared_tension = "saturn_angular_pressure_plus_pluto_intensity"
    elif _bundle_kind_exists(bundles_by_partner, "pluto_personal_bundle") and _bundle_kind_exists(bundles_by_partner, "12th_pressure_bundle"):
        shared_tension = "pluto_intensity_plus_12th_pressure"
    elif _bundle_kind_exists(bundles_by_partner, "saturn_angular_bundle"):
        shared_tension = "saturn_angular_pressure"
    elif _bundle_kind_exists(bundles_by_partner, "12th_pressure_bundle"):
        shared_tension = "12th_house_pressure"

    return {
        "relationship_core": {
            "shared_theme": shared_theme,
            "shared_support": shared_support,
            "shared_tension": shared_tension,
            "shared_theme_line": shared_theme_line(shared_theme).capitalize(),
            "shared_support_line": support_line(shared_support).capitalize(),
            "shared_tension_line": tension_line(shared_tension).capitalize(),
            "summary_line": (
                f"{shared_theme_line(shared_theme).capitalize()}. "
                f"{support_line(shared_support).capitalize()}. "
                f"{tension_line(shared_tension).capitalize()}."
            ),
        },
        "partner_a_story": _resolve_partner_story(
            partner_key="partner_a",
            bundles_by_partner=bundles_by_partner,
            domain_rankings=domain_rankings,
            relational_modes=relational_modes,
            overlay_cluster_summary=overlay_cluster_summary,
        ),
        "partner_b_story": _resolve_partner_story(
            partner_key="partner_b",
            bundles_by_partner=bundles_by_partner,
            domain_rankings=domain_rankings,
            relational_modes=relational_modes,
            overlay_cluster_summary=overlay_cluster_summary,
        ),
        "relationship_shape": {
            "mutuality": round(_safe_float(corrected_scores.get("mutuality")), 4),
            "asymmetry": round(clamp01(asymmetry), 4),
            "sustainability": round(_safe_float(corrected_scores.get("sustainable_bond")), 4),
            "summary_line": _relationship_shape_summary(
                _safe_float(corrected_scores.get("mutuality")),
                clamp01(asymmetry),
                _safe_float(corrected_scores.get("sustainable_bond")),
            ),
        },
    }


def _best_bundle_score(bundles_by_partner: Mapping[str, Sequence[Mapping[str, Any]]], kind: str) -> float:
    best = 0.0
    for bundles in bundles_by_partner.values():
        for bundle in bundles:
            if str(bundle.get("kind") or "") != kind:
                continue
            best = max(best, _safe_float(bundle.get("score")))
    return best


def _sum_bridge_contributors(contributors: Sequence[Mapping[str, Any]]) -> float:
    return sum(_safe_float(item.get("value")) for item in contributors)


def build_bridge_contributors(
    base_scores: Mapping[str, Any],
    bundles_by_partner: Mapping[str, Sequence[Mapping[str, Any]]],
    overlay_cluster_summary: Mapping[str, Any],
    relevant_hits: Sequence[Mapping[str, Any]],
    resonance_scores: Mapping[str, Any] | None = None,
) -> dict:
    contributors = {
        "depth": [],
        "risk_index": [],
        "bond": [],
    }

    def add(metric: str, contributor_id: str, value: float) -> None:
        clipped = round(clamp01(value), 4)
        if clipped <= 0.0:
            return
        contributors[metric].append({"id": contributor_id, "value": clipped})

    max_8th_cluster = max(
        int(overlay_cluster_summary.get("8th_personal_cluster_a") or 0),
        int(overlay_cluster_summary.get("8th_personal_cluster_b") or 0),
    )
    total_12th_pressure = int(overlay_cluster_summary.get("12th_pressure_a") or 0) + int(overlay_cluster_summary.get("12th_pressure_b") or 0)
    max_4th_cluster = max(
        int(overlay_cluster_summary.get("4th_root_cluster_a") or 0),
        int(overlay_cluster_summary.get("4th_root_cluster_b") or 0),
    )

    pluto_bundle = _best_bundle_score(bundles_by_partner, "pluto_personal_bundle")
    saturn_bundle = _best_bundle_score(bundles_by_partner, "saturn_angular_bundle")
    soft_bundle = _best_bundle_score(bundles_by_partner, "soft_attraction_bundle")
    roots_bundle = _best_bundle_score(bundles_by_partner, "roots_home_bundle")
    communication_bundle = _best_bundle_score(bundles_by_partner, "communication_bridge_bundle")
    nodal_bundle = _best_bundle_score(bundles_by_partner, "nodal_fated_bundle")
    twelfth_bundle = _best_bundle_score(bundles_by_partner, "12th_pressure_bundle")

    moon_mars_soft = [hit for hit in relevant_hits if _pair_hit(hit, "moon", "mars", aspects=("conjunction", "trine"), orb_max=3.0)]
    moon_mars_exact = any(_orb_value(hit) <= 1.0 for hit in moon_mars_soft)
    venus_mars_soft = [hit for hit in relevant_hits if _pair_hit(hit, "venus", "mars", aspects=("conjunction", "trine"), orb_max=3.0)]
    venus_mars_exact = any(_orb_value(hit) <= 1.0 for hit in venus_mars_soft)
    sun_venus_soft = [hit for hit in relevant_hits if _pair_hit(hit, "sun", "venus", aspects=SOFT_ASPECTS, orb_max=2.0)]
    sun_mercury_soft = [hit for hit in relevant_hits if _pair_hit(hit, "sun", "mercury", aspects=SOFT_ASPECTS, orb_max=2.0)]
    asc_node_soft = [hit for hit in relevant_hits if _pair_hit(hit, "asc", "node", aspects=SOFT_ASPECTS, orb_max=2.0)]
    uranus_saturn_hits = _uranus_saturn_hard_exact(relevant_hits)

    if max_8th_cluster >= 5:
        add("depth", "8th_personal_cluster_bonus", 0.18)
    elif max_8th_cluster == 4:
        add("depth", "8th_personal_cluster_bonus", 0.14)
    elif max_8th_cluster == 3:
        add("depth", "8th_personal_cluster_bonus", 0.10)

    if pluto_bundle > 0.0:
        add("depth", "pluto_personal_depth_bonus", min(0.12, 0.05 + (0.08 * pluto_bundle)))
        add("risk_index", "pluto_personal_risk_bonus", min(0.11, 0.05 + (0.07 * pluto_bundle)))

    if total_12th_pressure > 0 and twelfth_bundle > 0.0:
        add("depth", "12th_pressure_depth_bonus", min(0.10, 0.03 + (0.02 * total_12th_pressure)))
        add("risk_index", "12th_pressure_risk_bonus", min(0.06, 0.02 + (0.015 * total_12th_pressure)))

    if moon_mars_soft:
        add("depth", "moon_mars_depth_bonus", 0.09 if moon_mars_exact else 0.06)
        add("bond", "moon_mars_soft_bonus", 0.07 if moon_mars_exact else 0.04)

    if venus_mars_soft:
        add("depth", "venus_mars_depth_bonus", 0.07 if venus_mars_exact else 0.05)

    if saturn_bundle > 0.0:
        add("risk_index", "saturn_angular_risk_bonus", min(0.09, 0.04 + (0.06 * saturn_bundle)))

    if uranus_saturn_hits:
        add("risk_index", "uranus_saturn_instability_bonus", 0.05)

    if soft_bundle > 0.0:
        add("bond", "soft_attraction_bundle_bonus", min(0.10, 0.05 + (0.06 * soft_bundle)))

    if sun_venus_soft:
        exact = min(_orb_value(hit) for hit in sun_venus_soft) <= 1.0
        add("bond", "sun_venus_soft_bonus", 0.09 if exact else 0.06)

    if sun_mercury_soft or communication_bundle > 0.0:
        add("bond", "sun_mercury_soft_bonus", 0.06 if sun_mercury_soft else min(0.04, 0.03 + (0.02 * communication_bundle)))

    if asc_node_soft or nodal_bundle > 0.0:
        add("bond", "asc_node_soft_bonus", 0.04 if asc_node_soft else min(0.03, 0.02 + (0.02 * nodal_bundle)))

    if max_4th_cluster >= 4 or roots_bundle > 0.0:
        add("bond", "roots_home_bonus", 0.06 if max_4th_cluster >= 4 else min(0.05, 0.03 + (0.03 * roots_bundle)))

    if resonance_scores:
        mutuality = _safe_float(resonance_scores.get("relationship", {}).get("mutuality"))
        sustainable = _safe_float(resonance_scores.get("relationship", {}).get("sustainable_bond"))
        avg_trigger = (
            _safe_float(resonance_scores.get("partner_a", {}).get("trigger_load"))
            + _safe_float(resonance_scores.get("partner_b", {}).get("trigger_load"))
        ) / 2.0
        add("bond", "mutuality_support_bonus", min(0.06, (0.04 * mutuality) + (0.02 * sustainable)))
        add("risk_index", "trigger_load_risk_bonus", min(0.06, 0.10 * avg_trigger))

    return contributors


def _best_bundle_payload(bundles_by_partner: Mapping[str, Sequence[Mapping[str, Any]]], kind: str) -> Mapping[str, Any]:
    best: Mapping[str, Any] = {}
    best_score = 0.0
    for bundles in bundles_by_partner.values():
        for bundle in bundles:
            if str(bundle.get("kind") or "") != kind:
                continue
            score = _safe_float(bundle.get("score"))
            if score > best_score:
                best_score = score
                best = bundle
    return best


def _canonical_metric_driver(
    *,
    source_type: str,
    metric: str,
    text: str,
    score: float,
    bundle: Mapping[str, Any] | None = None,
) -> dict:
    payload = {
        "type": source_type,
        "metric": metric,
        "text": text,
        "score": round(score, 4),
    }
    if bundle:
        payload["bundle_id"] = bundle.get("bundle_id")
        payload["kind"] = bundle.get("kind")
        payload["domain"] = bundle.get("domain")
    return payload


def build_canonical_public_metrics(
    *,
    base_scores: Mapping[str, Any],
    bundles_by_partner: Mapping[str, Sequence[Mapping[str, Any]]],
    overlay_cluster_summary: Mapping[str, Any],
    resonance_scores: Mapping[str, Any],
    aspect_hits: Sequence[Mapping[str, Any]],
) -> dict:
    base = {
        key: clamp01(_safe_float(base_scores.get(key)))
        for key in ("bond", "depth", "spark", "freedom", "risk_index", "confidence")
    }
    max_8th_cluster = max(
        int(overlay_cluster_summary.get("8th_personal_cluster_a") or 0),
        int(overlay_cluster_summary.get("8th_personal_cluster_b") or 0),
    )
    total_12th_pressure = int(overlay_cluster_summary.get("12th_pressure_a") or 0) + int(overlay_cluster_summary.get("12th_pressure_b") or 0)
    max_4th_cluster = max(
        int(overlay_cluster_summary.get("4th_root_cluster_a") or 0),
        int(overlay_cluster_summary.get("4th_root_cluster_b") or 0),
    )
    max_11th_cluster = max(
        int(overlay_cluster_summary.get("11th_social_cluster_a") or 0),
        int(overlay_cluster_summary.get("11th_social_cluster_b") or 0),
    )

    bundle_8th = _best_bundle_payload(bundles_by_partner, "8th_personal_cluster")
    bundle_pluto = _best_bundle_payload(bundles_by_partner, "pluto_personal_bundle")
    bundle_soft = _best_bundle_payload(bundles_by_partner, "soft_attraction_bundle")
    bundle_roots = _best_bundle_payload(bundles_by_partner, "roots_home_bundle")
    bundle_private = _best_bundle_payload(bundles_by_partner, "12th_pressure_bundle")
    bundle_social = _best_bundle_payload(bundles_by_partner, "social_future_bundle")
    bundle_saturn = _best_bundle_payload(bundles_by_partner, "saturn_angular_bundle")
    bundle_comm = _best_bundle_payload(bundles_by_partner, "communication_bridge_bundle")
    bundle_nodal = _best_bundle_payload(bundles_by_partner, "nodal_fated_bundle")

    score_8th = _safe_float(bundle_8th.get("score"))
    score_pluto = _safe_float(bundle_pluto.get("score"))
    score_soft = _safe_float(bundle_soft.get("score"))
    score_roots = _safe_float(bundle_roots.get("score"))
    score_private = _safe_float(bundle_private.get("score"))
    score_social = _safe_float(bundle_social.get("score"))
    score_saturn = _safe_float(bundle_saturn.get("score"))
    score_comm = _safe_float(bundle_comm.get("score"))
    score_nodal = _safe_float(bundle_nodal.get("score"))

    mutuality = _safe_float(resonance_scores.get("relationship", {}).get("mutuality"))
    sustainable_bond = _safe_float(resonance_scores.get("relationship", {}).get("sustainable_bond"))
    magnetic_intensity = _safe_float(resonance_scores.get("relationship", {}).get("magnetic_intensity"))
    asymmetry = _safe_float(resonance_scores.get("relationship", {}).get("asymmetry"))
    avg_trigger = (
        _safe_float(resonance_scores.get("partner_a", {}).get("trigger_load"))
        + _safe_float(resonance_scores.get("partner_b", {}).get("trigger_load"))
    ) / 2.0
    avg_growth = (
        _safe_float(resonance_scores.get("partner_a", {}).get("growth_tension"))
        + _safe_float(resonance_scores.get("partner_b", {}).get("growth_tension"))
    ) / 2.0
    avg_familiarity = (
        _safe_float(resonance_scores.get("partner_a", {}).get("familiarity_resonance"))
        + _safe_float(resonance_scores.get("partner_b", {}).get("familiarity_resonance"))
    ) / 2.0
    avg_promise = (
        _safe_float(resonance_scores.get("partner_a", {}).get("promise_alignment"))
        + _safe_float(resonance_scores.get("partner_b", {}).get("promise_alignment"))
    ) / 2.0

    moon_mars_soft = [hit for hit in aspect_hits if _pair_hit(hit, "moon", "mars", aspects=("conjunction", "trine"), orb_max=3.0)]
    venus_mars_soft = [hit for hit in aspect_hits if _pair_hit(hit, "venus", "mars", aspects=("conjunction", "trine"), orb_max=3.0)]
    sun_venus_soft = [hit for hit in aspect_hits if _pair_hit(hit, "sun", "venus", aspects=SOFT_ASPECTS, orb_max=2.0)]
    uranus_saturn_hits = _uranus_saturn_hard_exact(aspect_hits)

    depth_bundle = clamp01(
        (0.44 * score_8th)
        + (0.20 * score_pluto)
        + (0.16 * score_private)
        + (0.10 * clamp01(max_8th_cluster / 5.0))
        + (0.10 * (0.10 if moon_mars_soft else 0.0))
    )
    depth_calibration = clamp01((0.42 * magnetic_intensity) + (0.32 * avg_growth) + (0.26 * avg_promise))

    bond_bundle = clamp01(
        (0.32 * score_soft)
        + (0.28 * score_roots)
        + (0.12 * score_private)
        + (0.10 * score_social)
        + (0.08 * score_comm)
        + (0.05 * score_nodal)
        + (0.05 * clamp01(max_4th_cluster / 5.0))
    )
    bond_calibration = clamp01((0.40 * mutuality) + (0.32 * sustainable_bond) + (0.28 * avg_familiarity))

    risk_bundle = clamp01(
        (0.36 * score_pluto)
        + (0.26 * score_saturn)
        + (0.16 * score_private)
        + (0.08 * clamp01(total_12th_pressure / 4.0))
        + (0.08 * (0.10 if uranus_saturn_hits else 0.0))
        + (0.06 * avg_trigger)
    )
    risk_calibration = clamp01((0.56 * avg_trigger) + (0.24 * asymmetry) + (0.20 * avg_growth))

    spark_support = clamp01(
        (0.55 * base["spark"])
        + (0.18 * score_soft)
        + (0.10 * score_social)
        + (0.09 * (0.12 if venus_mars_soft else 0.0))
        + (0.08 * magnetic_intensity)
    )
    freedom_support = clamp01((0.80 * base["freedom"]) + (0.12 * (1.0 - avg_trigger)) + (0.08 * (1.0 - score_saturn)))

    scores = {
        "depth": round(clamp01((0.18 * base["depth"]) + (0.52 * depth_bundle) + (0.30 * depth_calibration)), 4),
        "bond": round(clamp01((0.18 * base["bond"]) + (0.52 * bond_bundle) + (0.30 * bond_calibration)), 4),
        "risk_index": round(clamp01((0.18 * base["risk_index"]) + (0.50 * risk_bundle) + (0.32 * risk_calibration)), 4),
        "spark": round(spark_support, 4),
        "freedom": round(freedom_support, 4),
        "confidence": round(base["confidence"], 4),
    }

    drivers = {
        "depth": [],
        "bond": [],
        "risk_index": [],
    }
    if score_8th > 0.0:
        drivers["depth"].append(
            _canonical_metric_driver(
                source_type="bundle",
                metric="depth",
                text="8. ev kişisel kümelenmesi derinlik merkezini taşıyor.",
                score=score_8th,
                bundle=bundle_8th,
            )
        )
    if score_pluto > 0.0:
        drivers["depth"].append(
            _canonical_metric_driver(
                source_type="bundle",
                metric="depth",
                text="Plüton kişisel teması yoğunluğu sertleştiriyor.",
                score=score_pluto,
                bundle=bundle_pluto,
            )
        )
    if score_private > 0.0:
        drivers["depth"].append(
            _canonical_metric_driver(
                source_type="bundle",
                metric="depth",
                text="12. ev baskısı bağı içe alan bir derinlik ekliyor.",
                score=score_private,
                bundle=bundle_private,
            )
        )
    if score_roots > 0.0:
        drivers["bond"].append(
            _canonical_metric_driver(
                source_type="bundle",
                metric="bond",
                text="4. ev / kök hattı yerleşme ve güven hissini büyütüyor.",
                score=score_roots,
                bundle=bundle_roots,
            )
        )
    if score_soft > 0.0:
        drivers["bond"].append(
            _canonical_metric_driver(
                source_type="bundle",
                metric="bond",
                text="Yumuşak çekim hattı bağı taşımayı kolaylaştırıyor.",
                score=score_soft,
                bundle=bundle_soft,
            )
        )
    if score_comm > 0.0:
        drivers["bond"].append(
            _canonical_metric_driver(
                source_type="bundle",
                metric="bond",
                text="Konuşma ve zihinsel akış bağ kurmayı destekliyor.",
                score=score_comm,
                bundle=bundle_comm,
            )
        )
    if score_pluto > 0.0:
        drivers["risk_index"].append(
            _canonical_metric_driver(
                source_type="bundle",
                metric="risk_index",
                text="Plüton kişisel teması güç ve yoğunluk baskısını artırıyor.",
                score=score_pluto,
                bundle=bundle_pluto,
            )
        )
    if score_saturn > 0.0:
        drivers["risk_index"].append(
            _canonical_metric_driver(
                source_type="bundle",
                metric="risk_index",
                text="Satürn açısı ilişkinin yük ve baskı tarafını büyütüyor.",
                score=score_saturn,
                bundle=bundle_saturn,
            )
        )
    if score_private > 0.0:
        drivers["risk_index"].append(
            _canonical_metric_driver(
                source_type="bundle",
                metric="risk_index",
                text="12. ev teması geri çekilme ve belirsizlik riskini artırıyor.",
                score=score_private,
                bundle=bundle_private,
            )
        )

    return {
        "scores": scores,
        "drivers": {metric: rows[:3] for metric, rows in drivers.items()},
        "canonical_components": {
            "depth_bundle": round(depth_bundle, 4),
            "depth_calibration": round(depth_calibration, 4),
            "bond_bundle": round(bond_bundle, 4),
            "bond_calibration": round(bond_calibration, 4),
            "risk_bundle": round(risk_bundle, 4),
            "risk_calibration": round(risk_calibration, 4),
            "max_8th_cluster": max_8th_cluster,
            "total_12th_pressure": total_12th_pressure,
            "max_4th_cluster": max_4th_cluster,
            "max_11th_cluster": max_11th_cluster,
        },
    }


def bridge_bonus_for_public_scores(
    base_scores: Mapping[str, Any],
    resonance_scores: Mapping[str, Any],
    partner_hits: Mapping[str, Sequence[Mapping[str, Any]]],
    overlays: Mapping[str, Any],
    aspect_hits: Sequence[Mapping[str, Any]],
    bundles_by_partner: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> Dict[str, Any]:
    raw_scores = {
        key: clamp01(_safe_float(base_scores.get(key)))
        for key in ("bond", "depth", "spark", "freedom", "risk_index", "confidence")
    }
    overlay_cluster_summary = build_overlay_cluster_summary(overlays)
    bundle_map = bundles_by_partner if isinstance(bundles_by_partner, Mapping) else {}
    canonical = build_canonical_public_metrics(
        base_scores=base_scores,
        bundles_by_partner=bundle_map,
        overlay_cluster_summary=overlay_cluster_summary,
        resonance_scores=resonance_scores,
        aspect_hits=aspect_hits,
    )
    scores = {
        key: clamp01(_safe_float(canonical.get("scores", {}).get(key)))
        for key in ("bond", "depth", "spark", "freedom", "risk_index", "confidence")
    }

    max_8th_cluster = max(
        int(overlay_cluster_summary.get("8th_personal_cluster_a") or 0),
        int(overlay_cluster_summary.get("8th_personal_cluster_b") or 0),
    )
    total_12th_pressure = int(overlay_cluster_summary.get("12th_pressure_a") or 0) + int(overlay_cluster_summary.get("12th_pressure_b") or 0)
    max_4th_cluster = max(
        int(overlay_cluster_summary.get("4th_root_cluster_a") or 0),
        int(overlay_cluster_summary.get("4th_root_cluster_b") or 0),
    )
    max_11th_cluster = max(
        int(overlay_cluster_summary.get("11th_social_cluster_a") or 0),
        int(overlay_cluster_summary.get("11th_social_cluster_b") or 0),
    )

    pluto_hard_hits = _pluto_hard_personal_hits(aspect_hits)
    saturn_angular_hits = _saturn_angular_hard_hits(aspect_hits)
    uranus_saturn_hits = _uranus_saturn_hard_exact(aspect_hits)

    intimacy_depth_aggregate = _relationship_activation(partner_hits, "intimacy_depth")
    relationship_activation = _relationship_activation(partner_hits, "relationships")
    avg_trigger = (
        _safe_float(resonance_scores.get("partner_a", {}).get("trigger_load"))
        + _safe_float(resonance_scores.get("partner_b", {}).get("trigger_load"))
    ) / 2.0
    avg_promise = (
        _safe_float(resonance_scores.get("partner_a", {}).get("promise_alignment"))
        + _safe_float(resonance_scores.get("partner_b", {}).get("promise_alignment"))
    ) / 2.0
    mutuality = _safe_float(resonance_scores.get("relationship", {}).get("mutuality"))
    asymmetry = _safe_float(resonance_scores.get("relationship", {}).get("asymmetry"))
    magnetic_intensity = _safe_float(resonance_scores.get("relationship", {}).get("magnetic_intensity"))
    sustainable_bond = _safe_float(resonance_scores.get("relationship", {}).get("sustainable_bond"))

    moon_mars_soft = [hit for hit in aspect_hits if _pair_hit(hit, "moon", "mars", aspects=("conjunction", "trine"), orb_max=3.0)]
    moon_mars_exact = any(_orb_value(hit) <= 1.0 for hit in moon_mars_soft)
    venus_mars_soft = [hit for hit in aspect_hits if _pair_hit(hit, "venus", "mars", aspects=("conjunction", "trine"), orb_max=3.0)]
    venus_mars_exact = any(_orb_value(hit) <= 1.0 for hit in venus_mars_soft)
    sun_venus_soft = [hit for hit in aspect_hits if _pair_hit(hit, "sun", "venus", aspects=SOFT_ASPECTS, orb_max=2.0)]
    sun_mercury_soft = [hit for hit in aspect_hits if _pair_hit(hit, "sun", "mercury", aspects=SOFT_ASPECTS, orb_max=2.0)]
    deep_context_present = max_8th_cluster >= 4 or total_12th_pressure > 0 or bool(pluto_hard_hits)

    bridge_contributors = build_bridge_contributors(
        base_scores=base_scores,
        bundles_by_partner=bundle_map,
        overlay_cluster_summary=overlay_cluster_summary,
        relevant_hits=aspect_hits,
        resonance_scores=resonance_scores,
    )
    if intimacy_depth_aggregate > 0.0:
        bridge_contributors["depth"].append(
            {
                "id": "intimacy_activation_bridge_bonus",
                "value": round(min(0.04, (0.02 * intimacy_depth_aggregate) + (0.01 * magnetic_intensity)), 4),
            }
        )
    if relationship_activation >= 0.55:
        bridge_contributors["bond"].append({"id": "relationship_activation_bonus", "value": 0.02})
    if max_11th_cluster >= 2:
        social_bonus = 0.03 if any("moon" in bodies for bodies in (overlay_cluster_summary.get("details") or {}).values()) else 0.02
        bridge_contributors["bond"].append({"id": "11th_social_cluster_bonus", "value": round(social_bonus, 4)})

    def _bounded_bridge(metric: str, max_total: float) -> float:
        raw_total = _sum_bridge_contributors(bridge_contributors[metric])
        return round(min(max_total, raw_total * 0.30), 4)

    depth_bridge = _bounded_bridge("depth", 0.08)
    bond_bridge = _bounded_bridge("bond", 0.08)
    risk_bridge = _bounded_bridge("risk_index", 0.06)

    scores["depth"] = clamp01(scores["depth"] + depth_bridge)
    scores["bond"] = clamp01(scores["bond"] + bond_bridge)
    scores["risk_index"] = clamp01(scores["risk_index"] + risk_bridge)

    target_scores = dict(scores)

    def _shape_context_lift(metric: str, target: float) -> float:
        raw = raw_scores.get(metric, 0.0)
        if metric == "depth":
            anchor = clamp01(
                (0.46 * target)
                + (0.18 * mutuality)
                + (0.16 * magnetic_intensity)
                + (0.10 * avg_promise)
                + (0.10 * min(1.0, intimacy_depth_aggregate))
            )
            lift_cap = 0.46
        elif metric == "bond":
            anchor = clamp01(
                (0.48 * target)
                + (0.18 * mutuality)
                + (0.14 * sustainable_bond)
                + (0.12 * min(1.0, relationship_activation))
                + (0.08 * min(1.0, max_4th_cluster / 4.0))
            )
            lift_cap = 0.34
        else:
            anchor = clamp01(
                (0.54 * target)
                + (0.18 * avg_trigger)
                + (0.12 * asymmetry)
                + (0.08 * min(1.0, len(pluto_hard_hits) / 2.0))
                + (0.08 * min(1.0, total_12th_pressure / 3.0))
            )
            lift_cap = 0.34

        if target <= raw:
            return round(max(target, raw * 0.84), 4)
        anchor = min(anchor, raw + lift_cap)
        shaped_lift = raw + min(lift_cap, 0.74 * (target - raw))
        return round(min(target, max(raw, anchor, shaped_lift)), 4)

    scores["depth"] = _shape_context_lift("depth", scores["depth"])
    scores["bond"] = _shape_context_lift("bond", scores["bond"])
    scores["risk_index"] = _shape_context_lift("risk_index", scores["risk_index"])
    spark_floor = clamp01(
        (0.62 * raw_scores.get("spark", 0.0))
        + (0.18 * magnetic_intensity)
        + (0.12 * min(1.0, relationship_activation))
        - (0.08 * avg_trigger)
    )
    scores["spark"] = round(max(scores["spark"], spark_floor), 4)

    depth_floor_applied = 0.0
    risk_floor_applied = 0.0
    bond_floor_applied = 0.0

    bridge_sources = _unique_preserve(
        [
            contributor["id"]
            for metric in ("depth", "risk_index", "bond")
            for contributor in bridge_contributors[metric]
        ]
    )

    bridge_debug = {
        "base_scores": {key: round(value, 4) for key, value in raw_scores.items()},
        "canonical_scores": {key: round(_safe_float(canonical.get("scores", {}).get(key)), 4) for key in scores},
        "corrected_scores": {key: round(value, 4) for key, value in scores.items()},
        "depth_floor_applied": depth_floor_applied,
        "risk_floor_applied": risk_floor_applied,
        "bond_floor_applied": bond_floor_applied,
        "bridge_sources": bridge_sources,
        "bridge_contributors": bridge_contributors,
        "bounded_bridge_applied": {
            "depth": depth_bridge,
            "bond": bond_bridge,
            "risk_index": risk_bridge,
        },
        "target_scores_before_shaping": {key: round(value, 4) for key, value in target_scores.items()},
        "spark_floor_applied": round(max(0.0, scores["spark"] - target_scores.get("spark", 0.0)), 4),
        "canonical_components": canonical.get("canonical_components", {}),
        "intimacy_depth_aggregate": round(intimacy_depth_aggregate, 4),
        "trigger_load_average": round(avg_trigger, 4),
        "pluto_hard_personal_count": len(pluto_hard_hits),
        "saturn_angular_hard_count": len(saturn_angular_hits),
        "uranus_saturn_exact_hard_count": len(uranus_saturn_hits),
        "unscored_but_relevant_hits": [],
    }

    return {
        "scores": {key: round(value, 4) for key, value in scores.items()},
        "drivers": canonical.get("drivers", {}),
        "overlay_cluster_summary": overlay_cluster_summary,
        "public_score_bridge_debug": bridge_debug,
    }


def build_asymmetry_notes(
    partner_a_ctx: Sequence[Mapping[str, Any]],
    partner_b_ctx: Sequence[Mapping[str, Any]],
    partner_a_name: str,
    partner_b_name: str,
    asymmetry: float | None = None,
) -> list[str]:
    notes: list[str] = []
    asymmetry_value = clamp01(_safe_float(asymmetry))
    a_top = partner_a_ctx[0] if partner_a_ctx else None
    b_top = partner_b_ctx[0] if partner_b_ctx else None
    if a_top and b_top:
        a_domain = str(a_top.get("domain") or "")
        b_domain = str(b_top.get("domain") or "")
        a_label = domain_label(a_domain)
        b_label = domain_label(b_domain)
        if a_domain == b_domain:
            if asymmetry_value >= 0.18:
                notes.append(f"Bağ ikinizde de en çok {a_label} alanını açıyor; ama yoğunluğu aynı dağılmıyor.")
            else:
                notes.append(f"Bağ ikinizde de en çok {a_label} alanında çalışıyor.")
        else:
            notes.append(f"{partner_a_name} bu bağı daha çok {a_label} üzerinden yaşıyor.")
            notes.append(f"{partner_b_name} tarafında ise ilk vurgu {b_label} oluyor.")
            notes.append("Bu yüzden ilişki iki tarafta aynı merkezden değil, farklı odalardan deneyimleniyor.")
    elif a_top:
        notes.append(f"{partner_a_name} tarafında en güçlü vurgu {domain_label(a_top.get('domain'))} alanında toplanıyor.")
    elif b_top:
        notes.append(f"{partner_b_name} tarafında en güçlü vurgu {domain_label(b_top.get('domain'))} alanında toplanıyor.")
    if asymmetry_value >= 0.28 and len(notes) < 3:
        notes.append("Bağın yükü iki kişide de eşit birikmiyor; deneyim daha yönlü akıyor.")
    return notes[:3]
