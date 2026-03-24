from __future__ import annotations

from typing import Any, Dict, Mapping

from app.natal.dispositor_engine import (
    build_angle_ruler_map,
    build_dispositor_chain,
    build_house_ruler_map,
    extract_aspects,
    extract_planet_positions,
)
from app.natal.promise_vector_engine import (
    build_domain_vectors,
    build_familiarity_vectors,
    build_promise_vectors,
    build_sensitivity_vectors,
)


def _safe_house(value: Any) -> int | None:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return None
    return ivalue if 1 <= ivalue <= 12 else None


def _find_aspects(
    aspects: list[Dict[str, Any]],
    a: str,
    b: str,
    allowed: set[str] | None = None,
) -> list[Dict[str, Any]]:
    out: list[Dict[str, Any]] = []
    for aspect in aspects:
        pair = {str(aspect.get("planet1") or ""), str(aspect.get("planet2") or "")}
        if pair != {a, b}:
            continue
        if allowed and str(aspect.get("aspect") or "") not in allowed:
            continue
        out.append(aspect)
    return out


def _house_label(house: Any) -> str:
    value = _safe_house(house)
    if value is None:
        return ""
    if value == 1:
        return "1st"
    if value == 2:
        return "2nd"
    if value == 3:
        return "3rd"
    return f"{value}th"


def _add_motif(
    motifs: list[Dict[str, Any]],
    motif_id: str,
    raw_sum: float,
    evidence: list[str],
    normalizer: float = 0.70,
    dispositive_support: list[str] | None = None,
) -> None:
    unique_evidence = list(dict.fromkeys([item for item in evidence if item]))
    if not unique_evidence:
        return
    if len(unique_evidence) >= 3:
        raw_sum += 0.10
    score = min(1.0, raw_sum / normalizer)
    if score <= 0.0:
        return
    payload: Dict[str, Any] = {"id": motif_id, "score": round(score, 4), "evidence": unique_evidence}
    support = list(dict.fromkeys([item for item in (dispositive_support or []) if item]))
    if support:
        payload["dispositor_support"] = support
    motifs.append(payload)


def _chain_payload(chains: Mapping[str, Any], body: str) -> Mapping[str, Any]:
    payload = chains.get(body)
    return payload if isinstance(payload, Mapping) else {}


def _chain_list(chains: Mapping[str, Any], body: str) -> list[str]:
    payload = _chain_payload(chains, body)
    raw = payload.get("primary_chain")
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if item]


def _chain_contains(chains: Mapping[str, Any], body: str, target: str) -> bool:
    return target in _chain_list(chains, body)


def _chain_ends_with(chains: Mapping[str, Any], body: str, target: str) -> bool:
    chain = _chain_list(chains, body)
    return bool(chain) and chain[-1] == target


def _house_ruler_name(house_rulers: Mapping[str, Any], house_key: str) -> str:
    payload = house_rulers.get(house_key)
    if not isinstance(payload, Mapping):
        return ""
    return str(payload.get("primary") or "")


def _house_ruler_placement_house(house_rulers: Mapping[str, Any], house_key: str) -> int | None:
    payload = house_rulers.get(house_key)
    if not isinstance(payload, Mapping):
        return None
    placement = payload.get("placement")
    if not isinstance(placement, Mapping):
        return None
    return _safe_house(placement.get("house"))


def _house_ruler_chain_contains(
    house_rulers: Mapping[str, Any],
    chains: Mapping[str, Any],
    house_key: str,
    target: str,
) -> bool:
    ruler = _house_ruler_name(house_rulers, house_key)
    return bool(ruler) and _chain_contains(chains, ruler, target)


def _house_ruler_chain_ends_with(
    house_rulers: Mapping[str, Any],
    chains: Mapping[str, Any],
    house_key: str,
    target: str,
) -> bool:
    ruler = _house_ruler_name(house_rulers, house_key)
    return bool(ruler) and _chain_ends_with(chains, ruler, target)


def _mercury_support(planets: Mapping[str, Any], house_rulers: Mapping[str, Any], chains: Mapping[str, Any]) -> tuple[bool, list[str]]:
    support: list[str] = []
    mercury = planets.get("Mercury") or {}
    if str(mercury.get("sign") or "") in {"Virgo", "Gemini"}:
        support.append("mercury_domicile")
    if _safe_house(mercury.get("house")) in {1, 3, 12}:
        support.append("mercury_emphasized_house")
    if _house_ruler_name(house_rulers, "1") == "Mercury":
        support.append("asc_ruler_mercury")
    for body in ("Sun", "Mercury", "Venus", "Moon"):
        if _chain_ends_with(chains, body, "Mercury"):
            support.append(f"{body.lower()}_chain_mercury_terminal")
    return len(support) >= 2, list(dict.fromkeys(support))


def _chain_routes_to_12th_filter(
    planets: Mapping[str, Any],
    house_rulers: Mapping[str, Any],
    chains: Mapping[str, Any],
    body: str,
) -> bool:
    twelfth_ruler = _house_ruler_name(house_rulers, "12")
    if not twelfth_ruler:
        return False
    if _safe_house((planets.get(body) or {}).get("house")) == 12:
        return True
    return _chain_contains(chains, body, twelfth_ruler) or _chain_ends_with(chains, body, twelfth_ruler)


def build_signature_motifs(
    chart: Mapping[str, Any],
    house_rulers: Mapping[str, Any],
    angle_rulers: Mapping[str, Any],
    chains: Mapping[str, Any],
    natal_graph: Mapping[str, Any] | None = None,
) -> list[dict]:
    planets = extract_planet_positions(chart, natal_graph)
    aspects = extract_aspects(chart, natal_graph)
    motifs: list[Dict[str, Any]] = []

    asc_sign = str(angle_rulers.get("asc_sign") or "")
    venus_sign = str((planets.get("Venus") or {}).get("sign") or "")
    moon_sign = str((planets.get("Moon") or {}).get("sign") or "")
    sun_house = _safe_house((planets.get("Sun") or {}).get("house"))
    mercury_house = _safe_house((planets.get("Mercury") or {}).get("house"))
    venus_house = _safe_house((planets.get("Venus") or {}).get("house"))
    mars_house = _safe_house((planets.get("Mars") or {}).get("house"))
    moon_house = _safe_house((planets.get("Moon") or {}).get("house"))
    saturn_house = _safe_house((planets.get("Saturn") or {}).get("house"))
    mercury_strong, mercury_support = _mercury_support(planets, house_rulers, chains)
    venus_mercury_support = bool(_find_aspects(aspects, "Venus", "Mercury", None)) or _chain_ends_with(chains, "Venus", "Mercury")
    moon_mercury_support = bool(_find_aspects(aspects, "Moon", "Mercury", None)) or _chain_ends_with(chains, "Moon", "Mercury")
    control_loop = any(
        {"Saturn", "Mars", "Mercury"}.issubset(set(_chain_list(chains, body)))
        and str(_chain_payload(chains, body).get("termination_reason") or "") == "loop_detected"
        for body in ("Sun", "Mercury", "Venus", "Mars", "Moon")
    )

    identity_structure_evidence: list[str] = []
    identity_structure_raw = 0.0
    if asc_sign == "Capricorn":
        identity_structure_evidence.append("asc_capricorn")
        identity_structure_raw += 0.28
    if sun_house == 1:
        identity_structure_evidence.append("sun_1st")
        identity_structure_raw += 0.26
    if _house_ruler_name(house_rulers, "1") == "Saturn":
        placement_house = _house_ruler_placement_house(house_rulers, "1")
        if placement_house:
            identity_structure_evidence.append(f"asc_ruler_saturn_{_house_label(placement_house)}")
        identity_structure_raw += 0.22
    _add_motif(motifs, "identity_structure", identity_structure_raw, identity_structure_evidence)

    visionary_originality_evidence: list[str] = []
    visionary_originality_raw = 0.0
    visionary_support: list[str] = []
    if _safe_house((planets.get("Uranus") or {}).get("house")) == 1:
        visionary_originality_evidence.append("uranus_1st")
        visionary_originality_raw += 0.30
    if _safe_house((planets.get("Jupiter") or {}).get("house")) == 1 and _safe_house((planets.get("Neptune") or {}).get("house")) == 1:
        visionary_originality_evidence.append("jupiter_neptune_1st")
        visionary_originality_raw += 0.30
    if _chain_contains(chains, "Uranus", "Saturn") or _chain_contains(chains, "Uranus", "Mercury"):
        visionary_support.append("uranus_filtered_by_saturn_mercury")
    _add_motif(
        motifs,
        "visionary_originality",
        visionary_originality_raw,
        visionary_originality_evidence,
        dispositive_support=visionary_support,
    )

    depth_intimacy_evidence: list[str] = []
    depth_intimacy_raw = 0.0
    depth_support: list[str] = []
    if moon_house == 8:
        depth_intimacy_evidence.append("moon_8th")
        depth_intimacy_raw += 0.32
    if _safe_house((planets.get("Lilith") or {}).get("house")) == 8:
        depth_intimacy_evidence.append("lilith_8th")
        depth_intimacy_raw += 0.22
    if _house_ruler_placement_house(house_rulers, "7") == 8:
        depth_intimacy_evidence.append("7r_in_8th")
        depth_intimacy_raw += 0.28
    if _house_ruler_chain_contains(house_rulers, chains, "7", "Saturn") or _house_ruler_chain_contains(house_rulers, chains, "8", "Saturn"):
        depth_support.append("relationship_chain_routes_saturn")
    _add_motif(
        motifs,
        "depth_intimacy",
        depth_intimacy_raw,
        depth_intimacy_evidence,
        dispositive_support=depth_support,
    )

    language_boundary_evidence: list[str] = []
    language_boundary_raw = 0.0
    language_support: list[str] = list(mercury_support if mercury_strong else [])
    if saturn_house == 3:
        language_boundary_evidence.append("saturn_3rd")
        language_boundary_raw += 0.30
    if _find_aspects(aspects, "Mercury", "Saturn", None):
        language_boundary_evidence.append("mercury_saturn")
        language_boundary_raw += 0.24
    if _house_ruler_placement_house(house_rulers, "1") == 3:
        language_boundary_evidence.append("asc_ruler_in_3rd")
        language_boundary_raw += 0.22
    if control_loop:
        language_support.append("saturn_mars_mercury_loop")
    _add_motif(
        motifs,
        "language_boundary",
        language_boundary_raw,
        language_boundary_evidence,
        dispositive_support=language_support,
    )

    push_pull_evidence: list[str] = []
    push_pull_raw = 0.0
    if _find_aspects(aspects, "Mars", "Saturn", {"square", "opposition", "conjunction"}):
        push_pull_evidence.append("mars_saturn_hard")
        push_pull_raw += 0.30
    if mars_house == 9:
        push_pull_evidence.append("mars_9th")
        push_pull_raw += 0.18
    _add_motif(motifs, "push_pull_drive", push_pull_raw, push_pull_evidence)

    visibility_evidence: list[str] = []
    visibility_raw = 0.0
    if _safe_house((planets.get("Chiron") or {}).get("house")) == 10:
        visibility_evidence.append("chiron_10th")
        visibility_raw += 0.28
    if _find_aspects(aspects, "Neptune", "Midheaven", {"square", "opposition", "conjunction"}) or _find_aspects(aspects, "Jupiter", "Midheaven", {"square", "opposition", "conjunction"}):
        visibility_evidence.append("mc_sensitivity_aspects")
        visibility_raw += 0.22
    if _house_ruler_placement_house(house_rulers, "10") == 12:
        visibility_evidence.append("mc_ruler_12th")
        visibility_raw += 0.20
    _add_motif(motifs, "visibility_sensitivity", visibility_raw, visibility_evidence)

    hidden_creation_evidence: list[str] = []
    hidden_creation_raw = 0.0
    if venus_house == 12:
        hidden_creation_evidence.append("venus_12th")
        hidden_creation_raw += 0.28
    if _house_ruler_placement_house(house_rulers, "10") == 12:
        hidden_creation_evidence.append("10r_12th")
        hidden_creation_raw += 0.22
    _add_motif(motifs, "hidden_creation", hidden_creation_raw, hidden_creation_evidence)

    system_builder_evidence: list[str] = []
    system_builder_raw = 0.0
    system_support: list[str] = []
    if saturn_house == 3:
        system_builder_evidence.append("saturn_3rd")
        system_builder_raw += 0.24
    if _find_aspects(aspects, "Mercury", "Saturn", None):
        system_builder_evidence.append("mercury_saturn")
        system_builder_raw += 0.22
    if _chain_contains(chains, "Sun", "Saturn") and _chain_contains(chains, "Sun", "Mercury"):
        system_builder_evidence.append("saturn_mercury_chain")
        system_builder_raw += 0.22
    if control_loop:
        system_support.append("saturn_mars_mercury_loop")
    _add_motif(
        motifs,
        "system_builder",
        system_builder_raw,
        system_builder_evidence,
        dispositive_support=system_support,
    )

    soft_bonding_evidence: list[str] = []
    soft_bonding_raw = 0.0
    if _find_aspects(aspects, "Moon", "Venus", {"trine", "sextile", "conjunction"}):
        soft_bonding_evidence.append("moon_venus_soft")
        soft_bonding_raw += 0.30
    if _house_ruler_name(house_rulers, "7") == "Moon":
        soft_bonding_evidence.append("7r_moon")
        soft_bonding_raw += 0.18
    _add_motif(motifs, "soft_bonding", soft_bonding_raw, soft_bonding_evidence)

    independent_roots_evidence: list[str] = []
    independent_roots_raw = 0.0
    if str((house_rulers.get("4") or {}).get("sign") or "") == "Aries":
        independent_roots_evidence.append("ic_aries")
        independent_roots_raw += 0.28
    if _house_ruler_placement_house(house_rulers, "4") == 1:
        independent_roots_evidence.append("4r_in_1st")
        independent_roots_raw += 0.24
    _add_motif(motifs, "independent_roots", independent_roots_raw, independent_roots_evidence)

    creative_flow_evidence: list[str] = []
    creative_flow_raw = 0.0
    if _safe_house((planets.get("Fortune") or {}).get("house")) == 5:
        creative_flow_evidence.append("fortune_5th")
        creative_flow_raw += 0.28
    if _find_aspects(aspects, "Moon", "Venus", {"trine", "sextile", "conjunction"}):
        creative_flow_evidence.append("moon_venus_soft")
        creative_flow_raw += 0.18
    if _find_aspects(aspects, "Mars", "Neptune", {"trine", "sextile"}):
        creative_flow_evidence.append("mars_neptune_flow")
        creative_flow_raw += 0.22
    _add_motif(motifs, "creative_flow", creative_flow_raw, creative_flow_evidence)

    transformational_evidence: list[str] = []
    transformational_raw = 0.0
    transformational_support: list[str] = []
    if _safe_house((planets.get("Pluto") or {}).get("house")) == 8:
        transformational_evidence.append("pluto_8th")
        transformational_raw += 0.26
    if moon_house == 8:
        transformational_evidence.append("moon_8th")
        transformational_raw += 0.22
    if _safe_house((planets.get("Lilith") or {}).get("house")) == 8:
        transformational_evidence.append("lilith_8th")
        transformational_raw += 0.20
    if _find_aspects(aspects, "Pluto", "Moon", {"square", "opposition", "conjunction"}) or _find_aspects(aspects, "Pluto", "Venus", {"square", "opposition", "conjunction"}):
        transformational_evidence.append("pluto_personal_contact")
        transformational_raw += 0.20
    if _house_ruler_chain_contains(house_rulers, chains, "8", "Saturn") or _house_ruler_chain_contains(house_rulers, chains, "8", "Mercury"):
        transformational_support.append("8r_filtered_depth_chain")
    _add_motif(
        motifs,
        "transformational_intensity",
        transformational_raw,
        transformational_evidence,
        dispositive_support=transformational_support,
    )

    private_intellect_evidence: list[str] = []
    private_intellect_support: list[str] = []
    private_intellect_raw = 0.0
    if sun_house == 12:
        private_intellect_evidence.append("sun_12th")
        private_intellect_raw += 0.22
    if mercury_house == 12:
        private_intellect_evidence.append("mercury_12th")
        private_intellect_raw += 0.28
    if mercury_strong:
        private_intellect_evidence.append("mercury_strong")
        private_intellect_raw += 0.22
        private_intellect_support.extend(mercury_support)
    if venus_sign == "Virgo":
        private_intellect_evidence.append("virgo_filter")
        private_intellect_raw += 0.10
    _add_motif(
        motifs,
        "private_intellect",
        private_intellect_raw,
        private_intellect_evidence,
        normalizer=0.72,
        dispositive_support=private_intellect_support,
    )

    selective_bonding_evidence: list[str] = []
    selective_bonding_support: list[str] = []
    selective_bonding_raw = 0.0
    if venus_sign == "Virgo":
        selective_bonding_evidence.append("venus_virgo")
        selective_bonding_raw += 0.22
    if saturn_house == 8:
        selective_bonding_evidence.append("saturn_8th")
        selective_bonding_raw += 0.24
    if _house_ruler_chain_contains(house_rulers, chains, "8", "Saturn") or _house_ruler_chain_contains(house_rulers, chains, "8", "Mercury"):
        selective_bonding_evidence.append("8r_filtered")
        selective_bonding_raw += 0.18
    if _house_ruler_chain_contains(house_rulers, chains, "7", "Saturn") or _house_ruler_chain_contains(house_rulers, chains, "7", "Mercury"):
        selective_bonding_evidence.append("7r_filtered")
        selective_bonding_raw += 0.14
    if _house_ruler_chain_contains(house_rulers, chains, "8", "Saturn"):
        selective_bonding_support.append("8r_chain_routes_saturn")
    if _house_ruler_chain_contains(house_rulers, chains, "8", "Mercury"):
        selective_bonding_support.append("8r_chain_routes_mercury")
    if _house_ruler_chain_contains(house_rulers, chains, "7", "Mercury"):
        selective_bonding_support.append("7r_chain_routes_mercury")
    _add_motif(
        motifs,
        "selective_bonding",
        selective_bonding_raw,
        selective_bonding_evidence,
        normalizer=0.72,
        dispositive_support=selective_bonding_support,
    )

    service_love_evidence: list[str] = []
    service_love_support: list[str] = []
    service_love_raw = 0.0
    if venus_sign == "Virgo":
        service_love_evidence.append("venus_virgo")
        service_love_raw += 0.24
    if venus_mercury_support:
        service_love_evidence.append("venus_mercury_service_axis")
        service_love_raw += 0.18
    if _house_ruler_placement_house(house_rulers, "6") in {6, 12} or str((house_rulers.get("6") or {}).get("sign") or "") == "Pisces":
        service_love_evidence.append("care_axis_active")
        service_love_raw += 0.12
    if _chain_ends_with(chains, "Venus", "Mercury"):
        service_love_support.append("venus_chain_mercury_terminal")
    _add_motif(
        motifs,
        "service_love",
        service_love_raw,
        service_love_evidence,
        normalizer=0.68,
        dispositive_support=service_love_support,
    )

    relational_perfectionism_evidence: list[str] = []
    relational_perfectionism_support: list[str] = []
    relational_perfectionism_raw = 0.0
    if asc_sign == "Libra" and venus_sign == "Virgo":
        relational_perfectionism_evidence.append("libra_asc_venus_virgo")
        relational_perfectionism_raw += 0.34
    if venus_mercury_support:
        relational_perfectionism_evidence.append("venus_mercury_filter")
        relational_perfectionism_raw += 0.16
    if _house_ruler_chain_contains(house_rulers, chains, "7", "Mercury") or _house_ruler_chain_contains(house_rulers, chains, "8", "Mercury"):
        relational_perfectionism_evidence.append("relationship_axis_mercury_filtered")
        relational_perfectionism_raw += 0.16
    if _chain_ends_with(chains, "Venus", "Mercury"):
        relational_perfectionism_support.append("venus_chain_mercury_terminal")
    _add_motif(
        motifs,
        "relational_perfectionism",
        relational_perfectionism_raw,
        relational_perfectionism_evidence,
        normalizer=0.72,
        dispositive_support=relational_perfectionism_support,
    )

    depth_guardedness_evidence: list[str] = []
    depth_guardedness_support: list[str] = []
    depth_guardedness_raw = 0.0
    if saturn_house == 8:
        depth_guardedness_evidence.append("saturn_8th")
        depth_guardedness_raw += 0.30
    if _house_ruler_chain_contains(house_rulers, chains, "8", "Saturn"):
        depth_guardedness_evidence.append("8r_saturn_filtered")
        depth_guardedness_raw += 0.18
        depth_guardedness_support.append("8r_chain_routes_saturn")
    if str((planets.get("Saturn") or {}).get("sign") or "") == "Taurus" and (_house_ruler_placement_house(house_rulers, "8") == 11 or saturn_house == 8):
        depth_guardedness_evidence.append("fixed_earth_8th")
        depth_guardedness_raw += 0.12
    _add_motif(
        motifs,
        "depth_guardedness",
        depth_guardedness_raw,
        depth_guardedness_evidence,
        normalizer=0.68,
        dispositive_support=depth_guardedness_support,
    )

    social_fire_evidence: list[str] = []
    social_fire_support: list[str] = []
    social_fire_raw = 0.0
    if mars_house == 11 or venus_house == 11:
        social_fire_evidence.append("social_fire_11th")
        social_fire_raw += 0.18
    if sun_house == 12 or mercury_house == 12:
        social_fire_evidence.append("private_core_12th")
        social_fire_raw += 0.18
    if (mars_house == 11 or venus_house == 11) and (sun_house == 12 or mercury_house == 12):
        social_fire_raw += 0.10
    if _chain_routes_to_12th_filter(planets, house_rulers, chains, "Venus") or _chain_routes_to_12th_filter(planets, house_rulers, chains, "Mars"):
        social_fire_support.append("relational_chain_routes_12th_filter")
    _add_motif(
        motifs,
        "social_fire_private_core",
        social_fire_raw,
        social_fire_evidence,
        normalizer=0.64,
        dispositive_support=social_fire_support,
    )

    mentalized_emotion_evidence: list[str] = []
    mentalized_emotion_support: list[str] = []
    mentalized_emotion_raw = 0.0
    if moon_sign in {"Gemini", "Virgo"}:
        mentalized_emotion_evidence.append("moon_mercurial_sign")
        mentalized_emotion_raw += 0.20
    if moon_house in {3, 9, 12}:
        mentalized_emotion_evidence.append(f"moon_{_house_label(moon_house)}")
        mentalized_emotion_raw += 0.14
    if moon_mercury_support:
        mentalized_emotion_evidence.append("moon_mercury_tie")
        mentalized_emotion_raw += 0.18
    if _chain_ends_with(chains, "Moon", "Mercury"):
        mentalized_emotion_support.append("moon_chain_mercury_terminal")
    _add_motif(
        motifs,
        "mentalized_emotion",
        mentalized_emotion_raw,
        mentalized_emotion_evidence,
        normalizer=0.68,
        dispositive_support=mentalized_emotion_support,
    )

    quiet_loyalty_evidence: list[str] = []
    quiet_loyalty_support: list[str] = []
    quiet_loyalty_raw = 0.0
    if saturn_house in {4, 8} or str((planets.get("Saturn") or {}).get("sign") or "") in {"Taurus", "Capricorn", "Aquarius"}:
        quiet_loyalty_evidence.append("stable_saturn")
        quiet_loyalty_raw += 0.18
    if venus_house == 11 or mars_house == 11:
        quiet_loyalty_evidence.append("commitment_11th")
        quiet_loyalty_raw += 0.14
    if _house_ruler_placement_house(house_rulers, "7") in {8, 11} or _house_ruler_placement_house(house_rulers, "8") in {8, 11}:
        quiet_loyalty_evidence.append("relationship_commitment_axis")
        quiet_loyalty_raw += 0.16
    if _chain_contains(chains, "Venus", "Mercury") or _chain_contains(chains, "Mars", "Mercury"):
        quiet_loyalty_support.append("relational_chain_mercury_filtered")
    _add_motif(
        motifs,
        "quiet_loyalty",
        quiet_loyalty_raw,
        quiet_loyalty_evidence,
        normalizer=0.68,
        dispositive_support=quiet_loyalty_support,
    )

    hidden_devotion_evidence: list[str] = []
    hidden_devotion_support: list[str] = []
    hidden_devotion_raw = 0.0
    if venus_house == 12:
        hidden_devotion_evidence.append("venus_12th")
        hidden_devotion_raw += 0.26
    if _house_ruler_placement_house(house_rulers, "7") == 12:
        hidden_devotion_evidence.append("7r_12th")
        hidden_devotion_raw += 0.18
    if _house_ruler_placement_house(house_rulers, "10") == 12:
        hidden_devotion_evidence.append("10r_12th")
        hidden_devotion_raw += 0.16
    if _chain_routes_to_12th_filter(planets, house_rulers, chains, "Venus") or _house_ruler_chain_ends_with(house_rulers, chains, "7", _house_ruler_name(house_rulers, "12")):
        hidden_devotion_evidence.append("relational_chain_to_12th")
        hidden_devotion_raw += 0.16
    if _chain_routes_to_12th_filter(planets, house_rulers, chains, "Venus"):
        hidden_devotion_support.append("venus_routes_to_12th_filter")
    if _house_ruler_chain_ends_with(house_rulers, chains, "7", _house_ruler_name(house_rulers, "12")):
        hidden_devotion_support.append("7r_chain_routes_12th_ruler")
    _add_motif(
        motifs,
        "hidden_devotion",
        hidden_devotion_raw,
        hidden_devotion_evidence,
        normalizer=0.68,
        dispositive_support=hidden_devotion_support,
    )

    thresholded_intimacy_evidence: list[str] = []
    thresholded_intimacy_support: list[str] = []
    thresholded_intimacy_raw = 0.0
    if _house_ruler_chain_contains(house_rulers, chains, "8", "Saturn"):
        thresholded_intimacy_evidence.append("8r_saturn_filter")
        thresholded_intimacy_raw += 0.18
        thresholded_intimacy_support.append("8r_chain_routes_saturn")
    if _house_ruler_chain_contains(house_rulers, chains, "8", "Mercury"):
        thresholded_intimacy_evidence.append("8r_mercury_filter")
        thresholded_intimacy_raw += 0.18
        thresholded_intimacy_support.append("8r_chain_routes_mercury")
    if _house_ruler_chain_contains(house_rulers, chains, "8", "Pluto"):
        thresholded_intimacy_evidence.append("8r_pluto_filter")
        thresholded_intimacy_raw += 0.12
        thresholded_intimacy_support.append("8r_chain_routes_pluto")
    if saturn_house == 8:
        thresholded_intimacy_evidence.append("saturn_8th")
        thresholded_intimacy_raw += 0.16
    _add_motif(
        motifs,
        "thresholded_intimacy",
        thresholded_intimacy_raw,
        thresholded_intimacy_evidence,
        normalizer=0.68,
        dispositive_support=thresholded_intimacy_support,
    )

    return sorted(motifs, key=lambda item: (-float(item.get("score") or 0.0), str(item.get("id") or "")))


def build_natal_graph_v2(
    chart: dict,
    natal_graph: dict | None = None,
) -> dict:
    chart = dict(chart or {})
    natal_graph = dict(natal_graph or {})
    chart_rulers = build_angle_ruler_map(chart, natal_graph)
    house_rulers = chart_rulers.get("house_rulers") if isinstance(chart_rulers.get("house_rulers"), Mapping) else build_house_ruler_map(chart, natal_graph)
    planets = extract_planet_positions(chart, natal_graph)
    chains = {
        planet: build_dispositor_chain(planet, chart, max_hops=6, natal_graph=natal_graph)
        for planet in planets
    }
    motifs = build_signature_motifs(chart, house_rulers, chart_rulers, chains, natal_graph=natal_graph)
    partial = {
        "chart_rulers": chart_rulers,
        "dispositor_chains": chains,
        "signature_motifs": motifs,
        "source_natal_graph": natal_graph,
    }
    domain_scores, domain_evidence = build_domain_vectors(chart, partial)
    familiarity_scores, familiarity_evidence = build_familiarity_vectors(chart, partial)
    sensitivity_scores, sensitivity_evidence = build_sensitivity_vectors(chart, partial)
    promise_scores, promise_evidence = build_promise_vectors(chart, partial)

    vector_evidence: Dict[str, list[str]] = {}
    vector_evidence.update(domain_evidence)
    vector_evidence.update(familiarity_evidence)
    vector_evidence.update(sensitivity_evidence)
    vector_evidence.update(promise_evidence)
    vector_keys = list(vector_evidence.keys())
    fallback_vectors = [
        key
        for key, items in vector_evidence.items()
        if isinstance(items, list) and len(items) == 1 and str(items[0]).endswith("_fallback")
    ]
    motif_dispositor_support = {
        str(item.get("id") or ""): list(item.get("dispositor_support") or [])
        for item in motifs
        if list(item.get("dispositor_support") or [])
    }

    chart_rulers["house_rulers"] = house_rulers
    return {
        "engine_version": "natal_graph_v2",
        "chart_rulers": chart_rulers,
        "dispositor_chains": chains,
        "signature_motifs": motifs,
        "domain_vectors": domain_scores,
        "familiarity_vectors": familiarity_scores,
        "sensitivity_vectors": sensitivity_scores,
        "promise_vectors": promise_scores,
        "debug": {
            "vector_evidence": vector_evidence,
            "fallback_vectors": fallback_vectors,
            "non_fallback_ratio": round(1.0 - (len(fallback_vectors) / len(vector_keys)), 4) if vector_keys else 0.0,
            "motif_dispositor_support": motif_dispositor_support,
        },
    }
