from __future__ import annotations

import hashlib
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from app.engine.astro_normalize import (
    AXIS_POINTS,
    PERSONAL_BODIES,
    RULER_TRAD,
    aspect_strength,
    canonical_body,
    normalize_chart,
    orb_strength,
    safe_float,
)


class AstroDynamicsEngine:
    def build(
        self,
        chart_data: Mapping[str, Any],
        meta_info: Mapping[str, Any],
        phase2_snapshot: Mapping[str, Any],
        composites: Mapping[str, Any] | List[Mapping[str, Any]],
        *,
        debug: bool = False,
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        return build_astro_dynamics(
            chart_data,
            phase2_snapshot,
            meta_info,
            debug=debug,
        )


def build_astro_dynamics(
    chart_data: Dict[str, Any],
    phase2_snapshot: Dict[str, Any] | None,
    meta_info: Dict[str, Any] | None,
    *,
    debug: bool = False,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    meta_info = meta_info or {}
    phase2_snapshot = phase2_snapshot or {}

    placements_by_body, aspects, house_cusps, asc_sign = normalize_chart(chart_data, meta_info)
    placements = list(placements_by_body.values())
    accepted = ((phase2_snapshot.get("slots") or {}).get("accepted") or [])

    selected, rejected = _build_dynamic_spines(placements, aspects, house_cusps, meta_info, accepted)
    theme_scores = _build_theme_scores(
        placements,
        aspects,
        house_cusps,
        selected,
        meta_info,
    )

    dynamic_insights: Dict[str, Any] = {
        "schema_version": "dyn.v1",
        "engine_version": "astro-dyn.v1",
        "theme_scores": theme_scores,
        "selected": selected,
        "rejected": rejected,
        "bindings": _bind_spines_selected(selected),
        "links": link_spines(selected),
        "spines": selected,
    }
    if debug:
        dynamic_insights["debug"] = {
            "selected_count": len(selected),
            "rejected_count": len(rejected),
            "normalize_summary": {
                "placements_by_body": sorted(placements_by_body.keys()),
                "aspect_count": len(aspects),
                "asc_sign": asc_sign,
            },
        }
    return theme_scores, dynamic_insights


def _canonical_body(name: Any) -> str:
    return canonical_body(name) or ""


def _build_dynamic_spines(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    rules = [
        (_spine_chart_ruler_mechanism, "dyn.chart_ruler.mechanism.v1"),
        (_spine_sun_saturn_authority, "dyn.sun_saturn.authority.v1"),
        (_spine_moon_saturn_containment, "dyn.moon_saturn.containment.v1"),
        (_spine_sun_moon_bridge, "dyn.sun_moon.bridge.v1"),
        (_spine_house8_depth, "dyn.house8.depth.v1"),
        (_spine_house12_hidden_layer, "dyn.house12.hidden_layer.v1"),
        (_spine_moon_venus_soft_channel, "dyn.moon_venus.soft_channel.v1"),
        (_spine_mars_saturn_drive_brake, "dyn.mars_saturn.drive_brake.v1"),
        (_spine_mercury_revision_identity, "dyn.mercury.revision_identity.v1"),
        (_spine_jupiter_neptune_meaning, "dyn.jupiter_neptune.meaning.v1"),
        (_spine_node_growth_vector, "dyn.node.growth_vector.v1"),
        (_spine_axis_stress_visibility, "dyn.axis.stress_visibility.v1"),
    ]
    selected: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    for rule, insight_id in rules:
        spine = rule(placements, aspects, house_cusps, meta_info, accepted)
        if spine:
            selected.append(spine)
        else:
            rejected.append({"insight_id": insight_id, "reason": "gate_failed"})

    selected.sort(
        key=lambda item: (
            -_safe_float(item.get("strength")),
            str(item.get("insight_id") or ""),
            str(item.get("instance_id") or ""),
        )
    )
    return selected, rejected


def _spine_chart_ruler_mechanism(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    asc_sign = _asc_sign(placements, house_cusps, meta_info)
    if not asc_sign:
        return None
    ruler = _asc_ruler(asc_sign)
    placement = _placement_by_body(placements, ruler)
    if not placement:
        return None
    score = 0.55
    breakdown = {"base": 0.55}
    if placement.get("house") in {1, 3, 10}:
        score += 0.15
        breakdown["house_bonus"] = 0.15
    hard_aspect = _major_aspect_between(aspects, ruler, "Sun", hard_only=True) or _major_aspect_between(
        aspects, ruler, "Moon", hard_only=True
    )
    if hard_aspect:
        score += 0.10
        breakdown["hard_aspect_bonus"] = 0.10
    score = _clamp(score, 0.0, 1.0)

    house_theme = _house_theme(placement.get("house"))
    evidence = [
        {"type": "rulership", "role": "asc_ruler", "body": ruler, "cusp_sign": asc_sign},
        {
            "type": "placement",
            "body": ruler,
            "sign": placement.get("sign"),
            "house": placement.get("house"),
        },
    ]
    if hard_aspect:
        evidence.append(_aspect_evidence(ruler, hard_aspect))

    return _make_selected_spine(
        insight_id="dyn.chart_ruler.mechanism.v1",
        kind="mechanism",
        title="Chart Ruler Mechanism",
        entities=[ruler],
        themes=["identity", "mind"],
        strength=score,
        polarity=_polarity_from_aspect(hard_aspect),
        evidence=evidence,
        claim_fragments=_claim_fragments(accepted, {"identity", "mind"}, limit=2),
        story_spine={
            "p1": f"Kimligini en cok {ruler} uzerinden kuruyorsun; bu da seni {house_theme} hattinda yapi kurmaya iter.",
            "p2": "Bu mekanizma bazen 'once saglam olayim' refleksi yaratabilir; guc paylasilinca rahatlar.",
        },
        score_breakdown=breakdown,
    )


def _spine_sun_saturn_authority(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    aspect = _major_aspect_between(aspects, "Sun", "Saturn")
    if not aspect:
        return None
    strength = _clamp(0.55 + 0.45 * _aspect_strength(aspect), 0.0, 1.0)
    evidence = [
        _aspect_evidence("Sun", aspect),
        _placement_evidence(placements, "Sun"),
        _placement_evidence(placements, "Saturn"),
    ]
    return _make_selected_spine(
        insight_id="dyn.sun_saturn.authority.v1",
        kind="tension_to_mastery",
        title="Sun–Saturn Authority",
        entities=["Sun", "Saturn"],
        themes=["identity", "mind"],
        strength=strength,
        polarity=_polarity_from_aspect(aspect),
        evidence=[e for e in evidence if e],
        claim_fragments=_claim_fragments(accepted, {"identity", "mind"}, limit=2),
        story_spine={
            "p1": "Kimliginde guclu bir sorumluluk ve 'dogru yapma' ihtiyaci var; bu seni saglamlastiriyor.",
            "p2": "Ama bazen icte 'yetmedi' hissi tetiklenebilir; bu aslinda ustalik kapisi.",
            "shadow": "Golge tarafinda bu, kendine baski kurma egilimini artirabilir.",
            "buffer": "Paylastikca yumusar ve daha rahat ilerlersin.",
        },
        score_breakdown={"base": 0.55, "aspect_strength": round(_aspect_strength(aspect), 3)},
    )


def _spine_moon_saturn_containment(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    aspect = _major_aspect_between(aspects, "Moon", "Saturn")
    if not aspect:
        return None
    strength = _clamp(0.5 + 0.5 * _aspect_strength(aspect), 0.0, 1.0)
    return _make_selected_spine(
        insight_id="dyn.moon_saturn.containment.v1",
        kind="containment",
        title="Moon–Saturn Containment",
        entities=["Moon", "Saturn"],
        themes=["psychology", "relationships"],
        strength=strength,
        polarity=_polarity_from_aspect(aspect),
        evidence=[_aspect_evidence("Moon", aspect)],
        claim_fragments=_claim_fragments(accepted, {"psychology", "relationships"}, limit=2),
        story_spine={
            "p2": "Duygularin kolay acilmiyor; once guven ve zaman istiyor.",
            "shadow": "Bu bazen 'tek basima tasirim' modunu artirabilir.",
            "buffer": "Guven olusunca ise cok sadik ve tutarli bir alan acarsin.",
        },
        score_breakdown={"base": 0.5, "aspect_strength": round(_aspect_strength(aspect), 3)},
    )


def _spine_sun_moon_bridge(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    aspect = _major_aspect_between(aspects, "Sun", "Moon")
    sun_house = _house_of(placements, "Sun")
    moon_house = _house_of(placements, "Moon")
    counterweight = sun_house in {1, 10} and moon_house in {4, 8, 12}
    if not aspect and not counterweight:
        return None
    if aspect:
        strength = _clamp(0.45 + 0.55 * _aspect_strength(aspect), 0.0, 1.0)
    else:
        strength = 0.55
    sun_style = _sun_style(placements)
    moon_style = _moon_style(placements)
    evidence: List[Dict[str, Any]] = []
    if aspect:
        evidence.append(_aspect_evidence("Sun", aspect))
    else:
        evidence.append({"type": "counterweight", "sun_house": sun_house, "moon_house": moon_house})
    return _make_selected_spine(
        insight_id="dyn.sun_moon.bridge.v1",
        kind="bridge",
        title="Sun–Moon Bridge",
        entities=["Sun", "Moon"],
        themes=["identity", "psychology"],
        strength=strength,
        polarity=_polarity_from_aspect(aspect),
        evidence=evidence,
        claim_fragments=_claim_fragments(accepted, {"identity", "psychology"}, limit=2),
        story_spine={
            "p1": f"Disariya {sun_style} bir kimlik yansirken, iceride {moon_style} calisan bir duygusal dunya var.",
            "p2": "Bu iki taraf ayni ritme geldiginde hem guclu hem canli kalabiliyorsun.",
        },
        score_breakdown={"base": 0.45 if aspect else 0.55, "aspect_strength": round(_aspect_strength(aspect), 3) if aspect else 0.0},
    )


def _spine_house8_depth(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    personal_in_8 = [p for p in placements if p.get("house") == 8 and _is_personal(p.get("body"))]
    moon_in_8 = _house_of(placements, "Moon") == 8
    lilith_in_8 = _house_of(placements, "Lilith") == 8
    pluto_in_8 = _house_of(placements, "Pluto") == 8
    if not (personal_in_8 or moon_in_8 or lilith_in_8 or pluto_in_8):
        return None
    score = 0.55
    score += min(0.25, 0.10 * len(personal_in_8))
    if moon_in_8:
        score += 0.10
    score = _clamp(score, 0.0, 1.0)
    evidence = [
        {"type": "placement", "body": p.get("body"), "sign": p.get("sign"), "house": 8}
        for p in personal_in_8
    ]
    if moon_in_8:
        evidence.append({"type": "placement", "body": "Moon", "sign": _sign_of(placements, "Moon"), "house": 8})
    if lilith_in_8:
        evidence.append({"type": "placement", "body": "Lilith", "house": 8})
    if pluto_in_8:
        evidence.append({"type": "placement", "body": "Pluto", "house": 8})
    return _make_selected_spine(
        insight_id="dyn.house8.depth.v1",
        kind="depth",
        title="8th House Depth",
        entities=_bodies(personal_in_8) or ["Moon"],
        themes=["psychology", "relationships"],
        strength=score,
        polarity={"tension": 0.4, "support": 0.5},
        evidence=evidence,
        claim_fragments=_claim_fragments(accepted, {"psychology", "relationships"}, limit=2),
        story_spine={
            "p3": "Yakinlik alaninda duygular yuzeyde degil, derinde calisiyor; bag kurunca yogunlasiyorsun.",
            "shadow": "Bazen kontrol etme ya da yogunlugu tek basina tasima egilimi tetiklenebilir.",
        },
        score_breakdown={"base": 0.55, "personal_8": round(min(0.25, 0.10 * len(personal_in_8)), 3), "moon_8": 0.1 if moon_in_8 else 0.0},
    )


def _spine_house12_hidden_layer(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    personal_12 = [p for p in placements if p.get("house") == 12 and _is_personal(p.get("body"))]
    venus_12 = _house_of(placements, "Venus") == 12
    vertex_12 = _house_of(placements, "Vertex") == 12
    if not (personal_12 or venus_12 or vertex_12):
        return None
    score = 0.5
    if venus_12:
        score += 0.10
    if vertex_12:
        score += 0.10
    if len(personal_12) >= 2:
        score += 0.10
    score = _clamp(score, 0.0, 1.0)
    evidence = [
        {"type": "placement", "body": p.get("body"), "sign": p.get("sign"), "house": 12}
        for p in personal_12
    ]
    if venus_12:
        evidence.append({"type": "placement", "body": "Venus", "sign": _sign_of(placements, "Venus"), "house": 12})
    if vertex_12:
        evidence.append({"type": "placement", "body": "Vertex", "house": 12})
    return _make_selected_spine(
        insight_id="dyn.house12.hidden_layer.v1",
        kind="hidden_layer",
        title="12th House Hidden Layer",
        entities=_bodies(personal_12) or ["Venus"],
        themes=["psychology", "relationships"],
        strength=score,
        polarity={"tension": 0.3, "support": 0.5},
        evidence=evidence,
        claim_fragments=_claim_fragments(accepted, {"psychology", "relationships"}, limit=2),
        story_spine={
            "p2": "Bazi duygularini disaridan gorunur kilmak yerine icte yasama egilimin var.",
            "p3": "Dogru bagda bu, derin bir sefkat ve sezgisel yakinlik yaratir.",
        },
        score_breakdown={"base": 0.5, "venus_12": 0.1 if venus_12 else 0.0, "vertex_12": 0.1 if vertex_12 else 0.0, "multi_12": 0.1 if len(personal_12) >= 2 else 0.0},
    )


def _spine_moon_venus_soft_channel(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    aspect = _aspect_between_with_types(aspects, "Moon", "Venus", {"trine", "sextile", "conjunction"})
    if not aspect:
        return None
    strength = _clamp(0.55 + 0.45 * _aspect_strength(aspect), 0.0, 1.0)
    return _make_selected_spine(
        insight_id="dyn.moon_venus.soft_channel.v1",
        kind="soft_channel",
        title="Moon–Venus Soft Channel",
        entities=["Moon", "Venus"],
        themes=["psychology", "relationships"],
        strength=strength,
        polarity=_polarity_from_aspect(aspect),
        evidence=[_aspect_evidence("Moon", aspect)],
        claim_fragments=_claim_fragments(accepted, {"psychology", "relationships"}, limit=2),
        story_spine={
            "p2": "Duygun sevgiyle bulustugunda hizli yumusarsin; sefkat kanali guclu.",
            "buffer": "Bu yuzden dogru iliskide hem derin hissedip hem guvenli kalabilirsin.",
        },
        score_breakdown={"base": 0.55, "aspect_strength": round(_aspect_strength(aspect), 3)},
    )


def _spine_mars_saturn_drive_brake(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    aspect = _major_aspect_between(aspects, "Mars", "Saturn")
    if not aspect:
        return None
    strength = _clamp(0.5 + 0.5 * _aspect_strength(aspect), 0.0, 1.0)
    return _make_selected_spine(
        insight_id="dyn.mars_saturn.drive_brake.v1",
        kind="drive_brake",
        title="Mars–Saturn Drive vs Brake",
        entities=["Mars", "Saturn"],
        themes=["mind", "career", "identity"],
        strength=strength,
        polarity=_polarity_from_aspect(aspect),
        evidence=[_aspect_evidence("Mars", aspect)],
        claim_fragments=_claim_fragments(accepted, {"mind", "career", "identity"}, limit=2),
        story_spine={
            "p2": "Ilerleme enerjin guclu ama 'dogru zaman/dogru yapi' ihtiyaciyle dur-kalk yasayabilirsin.",
            "p1": "Bu, sabirla calisinca buyuk ustaliga doner.",
        },
        score_breakdown={"base": 0.5, "aspect_strength": round(_aspect_strength(aspect), 3)},
    )


def _spine_mercury_revision_identity(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    mercury = _placement_by_body(placements, "Mercury")
    if not mercury:
        return None
    mercury_house = mercury.get("house")
    mercury_rx = bool(mercury.get("retrograde"))
    mercury_jupiter = _major_aspect_between(aspects, "Mercury", "Jupiter")
    mercury_saturn = _major_aspect_between(aspects, "Mercury", "Saturn")
    if not (mercury_rx or mercury_house in {1, 3} or mercury_jupiter or mercury_saturn):
        return None
    score = 0.55
    if mercury_rx:
        score += 0.15
    if mercury_house == 1:
        score += 0.10
    if mercury_jupiter:
        score += 0.10
    score = _clamp(score, 0.0, 1.0)
    evidence = [{"type": "placement", "body": "Mercury", "sign": mercury.get("sign"), "house": mercury_house}]
    if mercury_jupiter:
        evidence.append(_aspect_evidence("Mercury", mercury_jupiter))
    if mercury_saturn:
        evidence.append(_aspect_evidence("Mercury", mercury_saturn))
    return _make_selected_spine(
        insight_id="dyn.mercury.revision_identity.v1",
        kind="revision",
        title="Mercury Revision Identity",
        entities=["Mercury"],
        themes=["mind", "identity"],
        strength=score,
        polarity=_polarity_from_aspect(mercury_jupiter or mercury_saturn),
        evidence=evidence,
        claim_fragments=_claim_fragments(accepted, {"mind", "identity"}, limit=2),
        story_spine={
            "p2": "Zihnin once iceride dolasir, sonra netlesir; bu yuzden kararlarin revizyondan gecerek guclenir.",
            "p1": "Kendini ifade etme bicimin zamanla oturur; acele etmezsin.",
        },
        score_breakdown={
            "base": 0.55,
            "retrograde": 0.15 if mercury_rx else 0.0,
            "house_1": 0.1 if mercury_house == 1 else 0.0,
            "jupiter_aspect": 0.1 if mercury_jupiter else 0.0,
        },
    )


def _spine_jupiter_neptune_meaning(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    aspect = _major_aspect_between(aspects, "Jupiter", "Neptune")
    if not aspect:
        return None
    strength = _clamp(0.45 + 0.55 * _aspect_strength(aspect), 0.0, 1.0)
    return _make_selected_spine(
        insight_id="dyn.jupiter_neptune.meaning.v1",
        kind="meaning",
        title="Jupiter–Neptune Meaning Expansion",
        entities=["Jupiter", "Neptune"],
        themes=["psychology", "karma"],
        strength=strength,
        polarity=_polarity_from_aspect(aspect),
        evidence=[_aspect_evidence("Jupiter", aspect)],
        claim_fragments=_claim_fragments(accepted, {"psychology", "karma"}, limit=2),
        story_spine={
            "p2": "Anlam arayisin guclu; bir seyi sadece 'ise yariyor' diye degil, 'ne anlatiyor' diye de tartarsin.",
            "buffer": "Bu hat acildiginda icsel rehberlik kuvvetlenir.",
        },
        score_breakdown={"base": 0.45, "aspect_strength": round(_aspect_strength(aspect), 3)},
    )


def _spine_node_growth_vector(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    node = _placement_by_body(placements, "North Node")
    if not node:
        return None
    node_house = node.get("house")
    personal_aspects = _node_personal_aspects(aspects, "North Node")
    if not (node_house in {9, 10, 12} or personal_aspects):
        return None
    max_strength = max([_aspect_strength(a) for a in personal_aspects], default=0.0)
    score = 0.55 + 0.35 * max_strength
    if node_house in {9, 10, 12}:
        score += 0.10
    score = _clamp(score, 0.0, 1.0)
    evidence = [{"type": "placement", "body": "North Node", "house": node_house}]
    for aspect in personal_aspects:
        evidence.append(_aspect_evidence("North Node", aspect))
    node_theme = _house_theme(node_house)
    return _make_selected_spine(
        insight_id="dyn.node.growth_vector.v1",
        kind="growth_vector",
        title="Node Growth Vector",
        entities=["North Node"],
        themes=["karma", "mind", "career"],
        strength=score,
        polarity={"tension": 0.4, "support": 0.3},
        evidence=evidence,
        claim_fragments=_claim_fragments(accepted, {"karma", "mind", "career"}, limit=2),
        story_spine={
            "p2": f"Hayat seni {node_theme} uzerinden buyutuyor; bazi secimler daha buyuk bir hat gibi hissedilebilir.",
        },
        score_breakdown={
            "base": 0.55,
            "aspect_strength": round(max_strength, 3),
            "house_bonus": 0.1 if node_house in {9, 10, 12} else 0.0,
        },
    )


def _spine_axis_stress_visibility(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
    accepted: Iterable[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    axis_aspects = _axis_aspects(aspects)
    if not axis_aspects:
        return None
    max_strength = max(_aspect_strength(a) for a in axis_aspects)
    score = _clamp(0.55 + 0.45 * max_strength, 0.0, 1.0)
    evidence = []
    for aspect in axis_aspects:
        evidence.append(_aspect_evidence(None, aspect))
        body = aspect.get("a")
        placement = _placement_evidence(placements, body)
        if placement:
            evidence.append(placement)
    quality = _identity_quality(axis_aspects[0].get("a"))
    return _make_selected_spine(
        insight_id="dyn.axis.stress_visibility.v1",
        kind="axis_stress",
        title="Axis Stress / Visibility",
        entities=[axis_aspects[0].get("a"), axis_aspects[0].get("b")],
        themes=["identity", "relationships", "career"],
        strength=score,
        polarity={"tension": 0.6, "support": 0.2},
        evidence=evidence,
        claim_fragments=_claim_fragments(accepted, {"identity", "relationships", "career"}, limit=2),
        story_spine={
            "p1": f"Durusun gorunur; insanlar sende {quality} hisseder.",
            "p3": "Otekiyle temas (1-7 ekseni) seni buyuten bir alan.",
        },
        score_breakdown={"base": 0.55, "aspect_strength": round(max_strength, 3)},
    )


def _build_theme_scores(
    placements: List[Dict[str, Any]],
    aspects: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    selected: Sequence[Mapping[str, Any]],
    meta_info: Mapping[str, Any],
) -> Dict[str, Any]:
    triggers = {entry.get("insight_id") for entry in selected if isinstance(entry, Mapping)}
    theme_scores: Dict[str, Any] = {}

    def add_contrib(contribs: list, entry: Dict[str, Any]) -> None:
        if entry not in contribs:
            contribs.append(entry)

    # Identity
    identity = 0.0
    identity_contribs: List[Dict[str, Any]] = []
    house1_bodies = [p for p in placements if p.get("house") == 1]
    if len(house1_bodies) >= 3:
        identity += 0.20
        add_contrib(identity_contribs, {"type": "house_emphasis", "house": 1, "bodies": _bodies(house1_bodies)})
    if _house_of(placements, "Sun") == 1:
        identity += 0.10
        add_contrib(identity_contribs, {"type": "placement", "body": "Sun", "house": 1})
    if _asc_sign(placements, house_cusps, meta_info):
        identity += 0.10
        add_contrib(identity_contribs, {"type": "rulership", "role": "asc_ruler"})
    if "dyn.axis.stress_visibility.v1" in triggers:
        identity += 0.10
        add_contrib(identity_contribs, {"type": "spine", "insight_id": "dyn.axis.stress_visibility.v1"})
    identity = _clamp(identity, 0.0, 1.0)
    theme_scores["identity"] = {"score": round(identity, 3), "top_contributors": identity_contribs[:4]}

    # Mind
    mind = 0.0
    mind_contribs: List[Dict[str, Any]] = []
    mercury_house = _house_of(placements, "Mercury")
    if mercury_house in {1, 3}:
        mind += 0.15
        add_contrib(mind_contribs, {"type": "placement", "body": "Mercury", "house": mercury_house})
    if _house_of(placements, "Saturn") == 3:
        mind += 0.15
        add_contrib(mind_contribs, {"type": "placement", "body": "Saturn", "house": 3})
    if _house_of(placements, "Mars") == 9:
        mind += 0.10
        add_contrib(mind_contribs, {"type": "placement", "body": "Mars", "house": 9})
    if _major_aspect_between(aspects, "Mars", "Saturn"):
        mind += 0.10
        add_contrib(mind_contribs, {"type": "aspect", "a": "Mars", "b": "Saturn"})
    if _major_aspect_between(aspects, "Mercury", "Jupiter"):
        mind += 0.10
        add_contrib(mind_contribs, {"type": "aspect", "a": "Mercury", "b": "Jupiter"})
    mind = _clamp(mind, 0.0, 1.0)
    theme_scores["mind"] = {"score": round(mind, 3), "top_contributors": mind_contribs[:4]}

    # Psychology
    psychology = 0.0
    psychology_contribs: List[Dict[str, Any]] = []
    if _house_of(placements, "Moon") in {4, 8, 12}:
        psychology += 0.20
        add_contrib(psychology_contribs, {"type": "placement", "body": "Moon", "house": _house_of(placements, "Moon")})
    if "dyn.house8.depth.v1" in triggers:
        psychology += 0.15
        add_contrib(psychology_contribs, {"type": "spine", "insight_id": "dyn.house8.depth.v1"})
    if "dyn.jupiter_neptune.meaning.v1" in triggers:
        psychology += 0.10
        add_contrib(psychology_contribs, {"type": "spine", "insight_id": "dyn.jupiter_neptune.meaning.v1"})
    psychology = _clamp(psychology, 0.0, 1.0)
    theme_scores["psychology"] = {"score": round(psychology, 3), "top_contributors": psychology_contribs[:4]}

    # Relationships
    relationships = 0.0
    relationships_contribs: List[Dict[str, Any]] = []
    if _house_of(placements, "Venus") in {7, 8, 12}:
        relationships += 0.20
        add_contrib(relationships_contribs, {"type": "placement", "body": "Venus", "house": _house_of(placements, "Venus")})
    if "dyn.moon_venus.soft_channel.v1" in triggers:
        relationships += 0.15
        add_contrib(relationships_contribs, {"type": "spine", "insight_id": "dyn.moon_venus.soft_channel.v1"})
    if "dyn.house8.depth.v1" in triggers:
        relationships += 0.10
        add_contrib(relationships_contribs, {"type": "spine", "insight_id": "dyn.house8.depth.v1"})
    relationships = _clamp(relationships, 0.0, 1.0)
    theme_scores["relationships"] = {"score": round(relationships, 3), "top_contributors": relationships_contribs[:4]}

    # Career
    career = 0.0
    career_contribs: List[Dict[str, Any]] = []
    if _house_of(placements, "Saturn") == 10 or _axis_contact(aspects, "Midheaven"):
        career += 0.20
        add_contrib(career_contribs, {"type": "placement", "body": "Saturn", "house": _house_of(placements, "Saturn")})
    if _house_of(placements, "North Node") == 10:
        career += 0.10
        add_contrib(career_contribs, {"type": "placement", "body": "North Node", "house": 10})
    career = _clamp(career, 0.0, 1.0)
    theme_scores["career"] = {"score": round(career, 3), "top_contributors": career_contribs[:4]}

    # Karma
    karma = 0.0
    karma_contribs: List[Dict[str, Any]] = []
    if _house_of(placements, "North Node") in {9, 12}:
        karma += 0.25
        add_contrib(karma_contribs, {"type": "placement", "body": "North Node", "house": _house_of(placements, "North Node")})
    if _node_personal_aspects(aspects, "North Node"):
        karma += 0.10
        add_contrib(karma_contribs, {"type": "aspect", "a": "North Node", "b": "personal"})
    karma = _clamp(karma, 0.0, 1.0)
    theme_scores["karma"] = {"score": round(karma, 3), "top_contributors": karma_contribs[:4]}

    return theme_scores


def _make_selected_spine(
    *,
    insight_id: str,
    kind: str,
    title: str,
    entities: Sequence[str],
    themes: Sequence[str],
    strength: float,
    polarity: Mapping[str, float],
    evidence: Sequence[Mapping[str, Any]],
    claim_fragments: Sequence[str],
    story_spine: Mapping[str, Any],
    score_breakdown: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    evidence_keys = _evidence_keys(evidence)
    instance_id = _instance_id(insight_id, evidence_keys)
    strength_value = round(_clamp(strength, 0.0, 1.0), 3)
    return {
        "insight_id": insight_id,
        "instance_id": instance_id,
        "kind": kind,
        "title": title,
        "entities": list(entities),
        "evidence_refs": evidence_keys,
        "claim_fragments": list(claim_fragments),
        "connector_template": dict(story_spine),
        "themes": list(themes),
        "strength": strength_value,
        "score": strength_value,
        "polarity": {
            "tension": round(_clamp(_safe_float(polarity.get("tension")), 0.0, 1.0), 3),
            "support": round(_clamp(_safe_float(polarity.get("support")), 0.0, 1.0), 3),
        },
        "evidence": [dict(item) for item in evidence if item],
        "story_spine": dict(story_spine),
        "debug": {
            "gate_hits": [insight_id],
            "score_breakdown": dict(score_breakdown or {}),
        },
    }


def _instance_id(insight_id: str, evidence_keys: Sequence[str]) -> str:
    payload = insight_id + "|" + "|".join(sorted(evidence_keys))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _evidence_keys(evidence: Sequence[Mapping[str, Any]]) -> List[str]:
    keys: List[str] = []
    for entry in evidence:
        if entry.get("type") == "aspect":
            orb = entry.get("orb")
            orb_key = f"{orb:.2f}" if isinstance(orb, (int, float)) else ""
            keys.append(f"asp:{entry.get('a')}|{entry.get('b')}|{entry.get('aspect')}|{orb_key}")
        elif entry.get("type") == "placement":
            keys.append(f"pl:{entry.get('body')}|{entry.get('sign')}|{entry.get('house')}")
        elif entry.get("type") == "rulership":
            keys.append(f"rl:{entry.get('role')}|{entry.get('body')}|{entry.get('cusp_sign')}")
        elif entry.get("type") == "house_emphasis":
            keys.append(f"hc:{entry.get('house')}|{','.join(entry.get('bodies') or [])}")
        else:
            keys.append(str(entry))
    return keys


def _bind_spines_selected(selected: Sequence[Mapping[str, Any]]) -> Dict[str, List[str]]:
    bindings: Dict[str, List[str]] = {}
    for spine in selected:
        insight_id = spine.get("insight_id")
        themes = spine.get("themes") or []
        if not insight_id:
            continue
        section = _map_spine_section(themes)
        if section:
            bindings.setdefault(section, []).append(str(insight_id))
    return bindings


def link_spines(spines: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    links: List[Dict[str, Any]] = []

    def themes_of(item: Mapping[str, Any]) -> set[str]:
        return {str(t) for t in item.get("themes") or []}

    def strength_of(item: Mapping[str, Any]) -> float:
        return _safe_float(item.get("strength"))

    def kind_of(item: Mapping[str, Any]) -> str:
        return str(item.get("kind") or "")

    growth_kinds = {"growth_vector", "meaning"}
    stabilizer_kinds = {"soft_channel", "bridge", "containment", "hidden_layer"}

    for from_spine in spines:
        if not isinstance(from_spine, Mapping):
            continue
        from_id = from_spine.get("insight_id")
        if not from_id:
            continue
        from_themes = themes_of(from_spine)
        from_strength = strength_of(from_spine)
        from_kind = kind_of(from_spine)

        for to_spine in spines:
            if not isinstance(to_spine, Mapping):
                continue
            to_id = to_spine.get("insight_id")
            if not to_id or to_id == from_id:
                continue
            to_themes = themes_of(to_spine)
            to_strength = strength_of(to_spine)
            to_kind = kind_of(to_spine)

            if from_themes.intersection({"identity", "mind"}) and "psychology" in to_themes:
                if from_strength >= 0.6 and to_strength >= 0.55:
                    links.append(
                        {
                            "from": str(from_id),
                            "to": str(to_id),
                            "link_type": "identity_to_psychology",
                            "connector_text": (
                                "Bu nedenle, disarida kurdugun yapi ic dunyanda daha yogun ve derin bir sekilde yasanir."
                            ),
                            "strength": round(min(from_strength, to_strength), 3),
                        }
                    )
            if "identity" in from_themes and "relationships" in to_themes:
                links.append(
                    {
                        "from": str(from_id),
                        "to": str(to_id),
                        "link_type": "identity_to_relationships",
                        "connector_text": "Bu yapi, iliskilerde nasil bag kurdugunu da dogrudan etkiler.",
                        "strength": round(min(from_strength, to_strength), 3),
                    }
                )
            if "psychology" in from_themes and "relationships" in to_themes:
                links.append(
                    {
                        "from": str(from_id),
                        "to": str(to_id),
                        "link_type": "psychology_to_relationships",
                        "connector_text": "Ic dunyandaki bu dinamik, yakin iliskilerde daha gorunur hale gelir.",
                        "strength": round(min(from_strength, to_strength), 3),
                    }
                )
            if from_kind == "tension_to_mastery" and (to_kind in growth_kinds or to_kind in stabilizer_kinds):
                links.append(
                    {
                        "from": str(from_id),
                        "to": str(to_id),
                        "link_type": "tension_to_mastery",
                        "connector_text": "Zorlayici gorunen bu tema, zamanla ustalastigin bir guce donusur.",
                        "strength": round(min(from_strength, to_strength), 3),
                    }
                )

    links.sort(
        key=lambda item: (
            -_safe_float(item.get("strength")),
            str(item.get("from") or ""),
            str(item.get("to") or ""),
        )
    )
    return links[:2]


def _map_spine_section(themes: Sequence[str]) -> str | None:
    theme_set = {str(theme) for theme in themes if theme}
    if theme_set.intersection({"identity", "mind"}):
        return "inner_core"
    if theme_set.intersection({"psychology"}):
        return "emotions"
    if theme_set.intersection({"relationships"}):
        return "relationships"
    if theme_set.intersection({"mind"}):
        return "mind"
    return None


def _aspect_strength(aspect: Mapping[str, Any]) -> float:
    return aspect_strength(aspect)


def _orb_strength(orb: float, orb_max: float = 6.0) -> float:
    return orb_strength(orb, orb_max=orb_max)


def _polarity_from_aspect(aspect: Optional[Mapping[str, Any]]) -> Dict[str, float]:
    if not aspect:
        return {"tension": 0.0, "support": 0.0}
    aspect_type = aspect.get("type")
    if aspect_type in {"square", "opposition"}:
        return {"tension": 0.7, "support": 0.1}
    if aspect_type == "conjunction":
        return {"tension": 0.45, "support": 0.45}
    if aspect_type in {"trine", "sextile"}:
        return {"tension": 0.1, "support": 0.7}
    return {"tension": 0.3, "support": 0.3}


def _major_aspect_between(
    aspects: Iterable[Mapping[str, Any]],
    a: str,
    b: str,
    *,
    hard_only: bool = False,
) -> Optional[Dict[str, Any]]:
    aspect = _aspect_between_with_types(
        aspects,
        a,
        b,
        {"conjunction", "opposition", "square", "trine", "sextile"},
    )
    if hard_only and aspect and aspect.get("type") not in {"square", "opposition"}:
        return None
    return aspect


def _aspect_between_with_types(
    aspects: Iterable[Mapping[str, Any]],
    a: str,
    b: str,
    allowed: set[str],
) -> Optional[Dict[str, Any]]:
    best: Optional[Dict[str, Any]] = None
    best_strength = -1.0
    a_key = _canonical_body(a)
    b_key = _canonical_body(b)
    for aspect in aspects:
        if {aspect.get("a"), aspect.get("b")} != {a_key, b_key}:
            continue
        if aspect.get("type") not in allowed:
            continue
        strength = _aspect_strength(aspect)
        if strength > best_strength:
            best = aspect
            best_strength = strength
    return best


def _aspect_evidence(body: Optional[str], aspect: Mapping[str, Any]) -> Dict[str, Any]:
    a = aspect.get("a")
    b = aspect.get("b")
    if body:
        a = body
        b = aspect.get("b") if aspect.get("a") == body else aspect.get("a")
    return {
        "type": "aspect",
        "a": a,
        "b": b,
        "aspect": aspect.get("type"),
        "orb": aspect.get("orb"),
    }


def _placement_evidence(placements: List[Dict[str, Any]], body: str) -> Optional[Dict[str, Any]]:
    placement = _placement_by_body(placements, body)
    if not placement:
        return None
    return {
        "type": "placement",
        "body": body,
        "sign": placement.get("sign"),
        "house": placement.get("house"),
    }


def _axis_aspects(aspects: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for aspect in aspects:
        a = str(aspect.get("a") or "")
        b = str(aspect.get("b") or "")
        if a.lower() in AXIS_POINTS and b.lower() in PERSONAL_BODIES:
            entry = dict(aspect)
            entry["a"] = b
            entry["b"] = a
            matches.append(entry)
        elif b.lower() in AXIS_POINTS and a.lower() in PERSONAL_BODIES:
            entry = dict(aspect)
            entry["a"] = a
            entry["b"] = b
            matches.append(entry)
    return matches


def _axis_contact(aspects: Iterable[Mapping[str, Any]], point: str) -> bool:
    point_name = _canonical_body(point)
    for aspect in aspects:
        if point_name in {aspect.get("a"), aspect.get("b")}:
            return True
    return False


def _node_personal_aspects(aspects: Iterable[Mapping[str, Any]], node_name: str) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for aspect in aspects:
        if node_name not in {aspect.get("a"), aspect.get("b")}:
            continue
        other = aspect.get("b") if aspect.get("a") == node_name else aspect.get("a")
        if str(other).lower() not in PERSONAL_BODIES:
            continue
        matches.append(aspect)
    return matches


def _placement_by_body(placements: List[Dict[str, Any]], body: str) -> Optional[Dict[str, Any]]:
    key = _canonical_body(body)
    for placement in placements:
        if placement.get("body") == key:
            return placement
    return None


def _house_of(placements: List[Dict[str, Any]], body: str) -> Optional[int]:
    placement = _placement_by_body(placements, body)
    return placement.get("house") if placement else None


def _sign_of(placements: List[Dict[str, Any]], body: str) -> Optional[str]:
    placement = _placement_by_body(placements, body)
    return placement.get("sign") if placement else None


def _asc_sign(
    placements: List[Dict[str, Any]],
    house_cusps: List[Dict[str, Any]],
    meta_info: Mapping[str, Any],
) -> Optional[str]:
    if meta_info.get("ascendant_sign"):
        return str(meta_info.get("ascendant_sign"))
    for cusp in house_cusps:
        if cusp.get("house") == 1:
            return cusp.get("sign")
    return None


def _asc_ruler(sign: Optional[str]) -> Optional[str]:
    if not sign:
        return None
    return RULER_TRAD.get(sign)


def _house_theme(house: Optional[int]) -> str:
    themes = {
        1: "kendini ortaya koyma",
        3: "zihin/ifade/ogrenme",
        10: "yon/meslek/otonomi",
    }
    if house in themes:
        return themes[house]
    if house:
        return f"hayatinin {house}. alani"
    return "yon"


def _sun_style(placements: List[Dict[str, Any]]) -> str:
    sign = _sign_of(placements, "Sun") or ""
    styles = {
        "Aries": "net",
        "Taurus": "sakin",
        "Gemini": "merakli",
        "Cancer": "koruyucu",
        "Leo": "gorunur",
        "Virgo": "duzenli",
        "Libra": "uyumlu",
        "Scorpio": "derin",
        "Sagittarius": "genis",
        "Capricorn": "ciddi",
        "Aquarius": "bagimsiz",
        "Pisces": "sezgisel",
    }
    return styles.get(sign, "guclu")


def _moon_style(placements: List[Dict[str, Any]]) -> str:
    sign = _sign_of(placements, "Moon") or ""
    styles = {
        "Aries": "atak",
        "Taurus": "sakin",
        "Gemini": "degisken",
        "Cancer": "koruyucu",
        "Leo": "gururlu",
        "Virgo": "titiz",
        "Libra": "uyumlu",
        "Scorpio": "derin",
        "Sagittarius": "genis",
        "Capricorn": "olgun",
        "Aquarius": "mesafeli",
        "Pisces": "sezgisel",
    }
    return styles.get(sign, "hassas")


def _identity_quality(body: Any) -> str:
    mapping = {
        "Sun": "kararli",
        "Moon": "duygusal",
        "Mercury": "zihinsel",
        "Venus": "sakin",
        "Mars": "atak",
    }
    return mapping.get(str(body), "netlik")


def _is_personal(body: Any) -> bool:
    return str(body or "").lower() in PERSONAL_BODIES


def _bodies(placements: List[Dict[str, Any]]) -> List[str]:
    return [p.get("body") for p in placements if p.get("body")]


def _claim_fragments(
    accepted: Iterable[Mapping[str, Any]],
    domains: set[str],
    *,
    limit: int = 2,
) -> List[str]:
    results: List[str] = []
    for item in accepted:
        if not isinstance(item, Mapping):
            continue
        domain = str(item.get("domain") or "")
        if domain not in domains:
            continue
        fragment_id = item.get("fragment_id")
        if fragment_id:
            results.append(str(fragment_id))
        if len(results) >= limit:
            break
    return results


def _safe_float(value: Any) -> float:
    return safe_float(value)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
