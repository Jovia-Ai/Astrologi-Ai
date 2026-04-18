from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from app.astro.aspect_direction import direction_multiplier
from app.astro.orb_policy import MAX_ORB_BY_ASPECT, tightness as _orb_policy_tightness
from app.natal.dispositor_engine import extract_aspects, extract_planet_positions


# Geriye dönük re-export — natal'daki major aspect tablosu. Tek canlı kaynak
# `app.astro.orb_policy.MAX_ORB_BY_ASPECT`. Eski isim dışarıdan import
# edilebilir olsun diye alias tutuluyor.
MAJOR_ORBS = MAX_ORB_BY_ASPECT

DOMAIN_NORMALIZER = 0.80
FAMILIARITY_NORMALIZER = 0.70
SENSITIVITY_NORMALIZER = 0.65
PROMISE_NORMALIZER = 0.75


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _safe_house(value: Any) -> int | None:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return None
    return ivalue if 1 <= ivalue <= 12 else None


def _context(chart: Mapping[str, Any], natal_graph_v2_partial: Mapping[str, Any]) -> Dict[str, Any]:
    planets = extract_planet_positions(chart, natal_graph_v2_partial.get("source_natal_graph"))
    aspects = extract_aspects(chart, natal_graph_v2_partial.get("source_natal_graph"))
    chart_rulers = natal_graph_v2_partial.get("chart_rulers") if isinstance(natal_graph_v2_partial.get("chart_rulers"), Mapping) else {}
    motifs = natal_graph_v2_partial.get("signature_motifs") if isinstance(natal_graph_v2_partial.get("signature_motifs"), Sequence) else []
    motif_scores = {
        str(item.get("id") or ""): float(item.get("score") or 0.0)
        for item in motifs
        if isinstance(item, Mapping)
    }
    return {
        "planets": planets,
        "aspects": aspects,
        "house_rulers": chart_rulers.get("house_rulers") if isinstance(chart_rulers.get("house_rulers"), Mapping) else {},
        "angle_rulers": chart_rulers,
        "motif_scores": motif_scores,
    }


def _aspect_tightness(aspect: Mapping[str, Any]) -> float:
    """Natal aspect tightness — default konvansiyon (orb=0 → 1.0).

    Base tightness `app.astro.orb_policy.tightness`'ten alınır. PR 5'te
    direction multiplier (applying/exact → %10 bonus, separating → 1.0)
    wrapper seviyesinde uygulanır — `orb_policy` imzası değişmez, synastry
    tarafına sızmaz.

    Direction None ise (eksik speed / bilinmeyen aspect / stasyoner)
    multiplier 1.0 → zero-diff fallback. Sonuç max 1.0'a clamp'lenir.
    """
    aspect_name = str(aspect.get("aspect") or "").lower()
    orb_value = aspect.get("orb")
    if orb_value is None:
        return 0.0
    base = _orb_policy_tightness(aspect_name, orb_value)
    mult = direction_multiplier(aspect.get("direction"))
    return min(1.0, base * mult)


def _find_aspects(
    aspects: Sequence[Mapping[str, Any]],
    a: str,
    b: str,
    allowed: set[str] | None = None,
) -> list[Mapping[str, Any]]:
    out: list[Mapping[str, Any]] = []
    for aspect in aspects:
        pair = {str(aspect.get("planet1") or ""), str(aspect.get("planet2") or "")}
        if pair != {a, b}:
            continue
        if allowed and str(aspect.get("aspect") or "").lower() not in allowed:
            continue
        out.append(aspect)
    return out


def _planet_in_house(planets: Mapping[str, Mapping[str, Any]], planet: str, house: int) -> bool:
    return _safe_house((planets.get(planet) or {}).get("house")) == house


def _strong_placement(planets: Mapping[str, Mapping[str, Any]], planet: str) -> bool:
    return _safe_house((planets.get(planet) or {}).get("house")) in {1, 4, 7, 10}


def _ruler_house(rulers: Mapping[str, Any], house_key: str) -> int | None:
    payload = rulers.get(house_key)
    if not isinstance(payload, Mapping):
        return None
    placement = payload.get("placement")
    if not isinstance(placement, Mapping):
        return None
    return _safe_house(placement.get("house"))


def _add(
    raw_scores: Dict[str, float],
    evidence: Dict[str, list[str]],
    channels: Dict[str, set[str]],
    vector: str,
    amount: float,
    evidence_text: str,
    channel: str,
) -> None:
    raw_scores[vector] = raw_scores.get(vector, 0.0) + amount
    evidence.setdefault(vector, [])
    if evidence_text not in evidence[vector]:
        evidence[vector].append(evidence_text)
    channels.setdefault(vector, set()).add(channel)


def _finalize(
    raw_scores: Dict[str, float],
    evidence: Dict[str, list[str]],
    channels: Dict[str, set[str]],
    vectors: Sequence[str],
    normalizer: float,
) -> tuple[Dict[str, float], Dict[str, list[str]]]:
    scores: Dict[str, float] = {}
    final_evidence: Dict[str, list[str]] = {}
    for vector in vectors:
        raw = float(raw_scores.get(vector, 0.0))
        items = list(evidence.get(vector) or [])
        count = len(items)
        if count >= 3:
            raw += 0.08
        if count >= 5:
            raw += 0.06
        if not items:
            items = [f"{vector}_fallback"]
        scores[vector] = round(clamp01(raw / normalizer), 4)
        final_evidence[vector] = items
    return scores, final_evidence


def build_domain_vectors(
    chart: Mapping[str, Any],
    natal_graph_v2_partial: Mapping[str, Any],
) -> tuple[Dict[str, float], Dict[str, list[str]]]:
    ctx = _context(chart, natal_graph_v2_partial)
    planets = ctx["planets"]
    aspects = ctx["aspects"]
    rulers = ctx["house_rulers"]
    motifs = ctx["motif_scores"]
    raw: Dict[str, float] = {}
    evidence: Dict[str, list[str]] = {}
    channels: Dict[str, set[str]] = {}
    vectors = [
        "identity",
        "mind_communication",
        "relationships",
        "intimacy_depth",
        "career_visibility",
        "home_roots",
        "creativity_talent",
        "meaning_learning",
    ]

    for planet, weight in [("Sun", 0.22), ("Uranus", 0.14), ("Jupiter", 0.14), ("Neptune", 0.14)]:
        if _planet_in_house(planets, planet, 1):
            _add(raw, evidence, channels, "identity", weight, f"{planet} in 1st", "placement")
    if rulers.get("1", {}).get("sign"):
        _add(raw, evidence, channels, "identity", 0.16, f"ASC {rulers['1']['sign']}", "angle")
    if rulers.get("1", {}).get("primary") == "Saturn":
        _add(raw, evidence, channels, "identity", 0.12, "Saturn chart ruler", "ruler")
    if motifs.get("identity_structure"):
        _add(raw, evidence, channels, "identity", 0.14 * motifs["identity_structure"], "identity_structure motif", "motif")

    for planet, weight in [("Mercury", 0.22), ("Saturn", 0.14)]:
        if _planet_in_house(planets, planet, 3):
            _add(raw, evidence, channels, "mind_communication", weight, f"{planet} in 3rd", "placement")
    if rulers.get("3", {}).get("primary"):
        placement = rulers.get("3", {}).get("placement") or {}
        if placement.get("house") == 3:
            _add(raw, evidence, channels, "mind_communication", 0.18, "3rd ruler in 3rd", "ruler")
    if _ruler_house(rulers, "1") == 3:
        _add(raw, evidence, channels, "mind_communication", 0.18, "ASC ruler in 3rd", "ruler")
    for aspect in _find_aspects(aspects, "Mercury", "Saturn", None) + _find_aspects(aspects, "Sun", "Saturn", {"square", "opposition", "conjunction"}):
        _add(raw, evidence, channels, "mind_communication", 0.18 * _aspect_tightness(aspect), f"{aspect['planet1']}-{aspect['planet2']} {aspect['aspect']}", "aspect")
    if motifs.get("language_boundary"):
        _add(raw, evidence, channels, "mind_communication", 0.14 * motifs["language_boundary"], "language_boundary motif", "motif")
    if motifs.get("private_intellect"):
        _add(raw, evidence, channels, "mind_communication", 0.20 * motifs["private_intellect"], "private_intellect motif", "motif")
    if motifs.get("mentalized_emotion"):
        _add(raw, evidence, channels, "mind_communication", 0.16 * motifs["mentalized_emotion"], "mentalized_emotion motif", "motif")

    for planet, weight in [("Venus", 0.18), ("Moon", 0.12)]:
        if _planet_in_house(planets, planet, 7):
            _add(raw, evidence, channels, "relationships", weight, f"{planet} in 7th", "placement")
    if rulers.get("7", {}).get("primary"):
        _add(raw, evidence, channels, "relationships", 0.20, f"7th ruler {rulers['7']['primary']}", "ruler")
    if _ruler_house(rulers, "7") == 8:
        _add(raw, evidence, channels, "relationships", 0.18, "7th ruler in 8th", "ruler")
    if motifs.get("soft_bonding"):
        _add(raw, evidence, channels, "relationships", 0.14 * motifs["soft_bonding"], "soft_bonding motif", "motif")
    if motifs.get("selective_bonding"):
        _add(raw, evidence, channels, "relationships", 0.14 * motifs["selective_bonding"], "selective_bonding motif", "motif")
    if motifs.get("service_love"):
        _add(raw, evidence, channels, "relationships", 0.12 * motifs["service_love"], "service_love motif", "motif")
    if motifs.get("social_fire_private_core"):
        _add(raw, evidence, channels, "relationships", 0.10 * motifs["social_fire_private_core"], "social_fire_private_core motif", "motif")
    if motifs.get("quiet_loyalty"):
        _add(raw, evidence, channels, "relationships", 0.10 * motifs["quiet_loyalty"], "quiet_loyalty motif", "motif")
    if motifs.get("hidden_devotion"):
        _add(raw, evidence, channels, "relationships", 0.12 * motifs["hidden_devotion"], "hidden_devotion motif", "motif")

    for planet, weight in [("Moon", 0.24), ("Lilith", 0.16), ("Pluto", 0.16)]:
        if _planet_in_house(planets, planet, 8):
            _add(raw, evidence, channels, "intimacy_depth", weight, f"{planet} in 8th", "placement")
    if _ruler_house(rulers, "7") == 8:
        _add(raw, evidence, channels, "intimacy_depth", 0.22, "7th ruler in 8th", "ruler")
    if motifs.get("depth_intimacy"):
        _add(raw, evidence, channels, "intimacy_depth", 0.16 * motifs["depth_intimacy"], "depth_intimacy motif", "motif")
    if motifs.get("depth_guardedness"):
        _add(raw, evidence, channels, "intimacy_depth", 0.16 * motifs["depth_guardedness"], "depth_guardedness motif", "motif")
    if motifs.get("thresholded_intimacy"):
        _add(raw, evidence, channels, "intimacy_depth", 0.14 * motifs["thresholded_intimacy"], "thresholded_intimacy motif", "motif")

    if rulers.get("10", {}).get("sign"):
        _add(raw, evidence, channels, "career_visibility", 0.18, f"MC {rulers['10']['sign']}", "angle")
    for planet, weight in [("Saturn", 0.16), ("Chiron", 0.16)]:
        if _planet_in_house(planets, planet, 10):
            _add(raw, evidence, channels, "career_visibility", weight, f"{planet} in 10th", "placement")
    if _ruler_house(rulers, "10") in {1, 10, 12}:
        _add(raw, evidence, channels, "career_visibility", 0.18, "MC ruler emphasized", "ruler")
    if motifs.get("visibility_sensitivity"):
        _add(raw, evidence, channels, "career_visibility", 0.14 * motifs["visibility_sensitivity"], "visibility_sensitivity motif", "motif")

    if rulers.get("4", {}).get("sign"):
        _add(raw, evidence, channels, "home_roots", 0.18, f"IC {rulers['4']['sign']}", "angle")
    for planet, weight in [("Moon", 0.18), ("Saturn", 0.12)]:
        if _planet_in_house(planets, planet, 4):
            _add(raw, evidence, channels, "home_roots", weight, f"{planet} in 4th", "placement")
    if motifs.get("independent_roots"):
        _add(raw, evidence, channels, "home_roots", 0.16 * motifs["independent_roots"], "independent_roots motif", "motif")

    for planet, weight in [("Venus", 0.16), ("Fortune", 0.18), ("Sun", 0.12)]:
        if _planet_in_house(planets, planet, 5):
            _add(raw, evidence, channels, "creativity_talent", weight, f"{planet} in 5th", "placement")
    for aspect in _find_aspects(aspects, "Moon", "Venus", {"trine", "sextile", "conjunction"}) + _find_aspects(aspects, "Mars", "Neptune", {"trine", "sextile"}):
        _add(raw, evidence, channels, "creativity_talent", 0.16 * _aspect_tightness(aspect), f"{aspect['planet1']}-{aspect['planet2']} {aspect['aspect']}", "aspect")
    if motifs.get("creative_flow"):
        _add(raw, evidence, channels, "creativity_talent", 0.16 * motifs["creative_flow"], "creative_flow motif", "motif")

    for planet, weight in [("Jupiter", 0.18), ("Mars", 0.16), ("Node", 0.14)]:
        if _planet_in_house(planets, planet, 9):
            _add(raw, evidence, channels, "meaning_learning", weight, f"{planet} in 9th", "placement")
    if rulers.get("9", {}).get("primary"):
        _add(raw, evidence, channels, "meaning_learning", 0.18, f"9th ruler {rulers['9']['primary']}", "ruler")
    if motifs.get("visionary_originality"):
        _add(raw, evidence, channels, "meaning_learning", 0.12 * motifs["visionary_originality"], "visionary_originality motif", "motif")
    if motifs.get("mentalized_emotion"):
        _add(raw, evidence, channels, "meaning_learning", 0.12 * motifs["mentalized_emotion"], "mentalized_emotion motif", "motif")

    if motifs.get("social_fire_private_core"):
        _add(raw, evidence, channels, "identity", 0.08 * motifs["social_fire_private_core"], "social_fire_private_core motif", "motif")

    return _finalize(raw, evidence, channels, vectors, DOMAIN_NORMALIZER)


def build_familiarity_vectors(
    chart: Mapping[str, Any],
    natal_graph_v2_partial: Mapping[str, Any],
) -> tuple[Dict[str, float], Dict[str, list[str]]]:
    ctx = _context(chart, natal_graph_v2_partial)
    planets = ctx["planets"]
    aspects = ctx["aspects"]
    rulers = ctx["angle_rulers"]
    motifs = ctx["motif_scores"]
    raw: Dict[str, float] = {}
    evidence: Dict[str, list[str]] = {}
    channels: Dict[str, set[str]] = {}
    vectors = [
        "structure_control",
        "intensity_depth",
        "novelty_freedom",
        "soft_affection",
        "mental_precision",
        "visibility_sensitivity",
    ]

    if rulers.get("asc_sign") == "Capricorn":
        _add(raw, evidence, channels, "structure_control", 0.18, "ASC Capricorn", "angle")
    if rulers.get("asc_ruler_primary") == "Saturn":
        _add(raw, evidence, channels, "structure_control", 0.18, "Saturn chart ruler", "ruler")
    if _planet_in_house(planets, "Saturn", 3):
        _add(raw, evidence, channels, "structure_control", 0.16, "Saturn in 3rd", "placement")
    for aspect in _find_aspects(aspects, "Sun", "Saturn", {"square", "opposition", "conjunction"}):
        _add(raw, evidence, channels, "structure_control", 0.18 * _aspect_tightness(aspect), "Sun-Saturn hard", "aspect")

    for planet, weight in [("Moon", 0.22), ("Lilith", 0.16), ("Pluto", 0.16)]:
        if _planet_in_house(planets, planet, 8):
            _add(raw, evidence, channels, "intensity_depth", weight, f"{planet} in 8th", "placement")
    if motifs.get("transformational_intensity"):
        _add(raw, evidence, channels, "intensity_depth", 0.16 * motifs["transformational_intensity"], "transformational_intensity motif", "motif")

    if _strong_placement(planets, "Uranus") or _planet_in_house(planets, "Uranus", 1):
        _add(raw, evidence, channels, "novelty_freedom", 0.20, "Uranus angular/1st", "placement")
    if rulers.get("asc_sign") == "Aquarius" or rulers.get("house_rulers", {}).get("11", {}).get("sign") == "Aquarius":
        _add(raw, evidence, channels, "novelty_freedom", 0.16, "Aquarius emphasis", "sign")
    if motifs.get("visionary_originality"):
        _add(raw, evidence, channels, "novelty_freedom", 0.14 * motifs["visionary_originality"], "visionary_originality motif", "motif")

    for aspect in _find_aspects(aspects, "Moon", "Venus", {"trine", "sextile", "conjunction"}):
        _add(raw, evidence, channels, "soft_affection", 0.20 * _aspect_tightness(aspect), "Moon-Venus soft", "aspect")
    if _strong_placement(planets, "Venus"):
        _add(raw, evidence, channels, "soft_affection", 0.16, "Venus strong", "placement")
    if motifs.get("soft_bonding"):
        _add(raw, evidence, channels, "soft_affection", 0.14 * motifs["soft_bonding"], "soft_bonding motif", "motif")

    if _strong_placement(planets, "Mercury") or _planet_in_house(planets, "Mercury", 3):
        _add(raw, evidence, channels, "mental_precision", 0.20, "Mercury strong/3rd", "placement")
    if _planet_in_house(planets, "Mars", 9) and (planets.get("Mars") or {}).get("sign") == "Virgo":
        _add(raw, evidence, channels, "mental_precision", 0.12, "Mars in Virgo", "placement")
    for aspect in _find_aspects(aspects, "Mercury", "Saturn", None):
        _add(raw, evidence, channels, "mental_precision", 0.18 * _aspect_tightness(aspect), "Mercury-Saturn aspect", "aspect")
    if motifs.get("private_intellect"):
        _add(raw, evidence, channels, "mental_precision", 0.14 * motifs["private_intellect"], "private_intellect motif", "motif")
    if motifs.get("relational_perfectionism"):
        _add(raw, evidence, channels, "mental_precision", 0.10 * motifs["relational_perfectionism"], "relational_perfectionism motif", "motif")
    if motifs.get("mentalized_emotion"):
        _add(raw, evidence, channels, "mental_precision", 0.08 * motifs["mentalized_emotion"], "mentalized_emotion motif", "motif")

    if motifs.get("thresholded_intimacy"):
        _add(raw, evidence, channels, "structure_control", 0.10 * motifs["thresholded_intimacy"], "thresholded_intimacy motif", "motif")
    if motifs.get("depth_guardedness"):
        _add(raw, evidence, channels, "intensity_depth", 0.10 * motifs["depth_guardedness"], "depth_guardedness motif", "motif")
    if motifs.get("service_love"):
        _add(raw, evidence, channels, "soft_affection", 0.10 * motifs["service_love"], "service_love motif", "motif")
    if motifs.get("quiet_loyalty"):
        _add(raw, evidence, channels, "soft_affection", 0.08 * motifs["quiet_loyalty"], "quiet_loyalty motif", "motif")

    if rulers.get("mc_sign"):
        _add(raw, evidence, channels, "visibility_sensitivity", 0.14, f"MC {rulers['mc_sign']}", "angle")
    if _planet_in_house(planets, "Chiron", 10):
        _add(raw, evidence, channels, "visibility_sensitivity", 0.20, "Chiron in 10th", "placement")
    if _planet_in_house(planets, "Venus", 12):
        _add(raw, evidence, channels, "visibility_sensitivity", 0.14, "Venus in 12th", "placement")
    if motifs.get("visibility_sensitivity"):
        _add(raw, evidence, channels, "visibility_sensitivity", 0.16 * motifs["visibility_sensitivity"], "visibility_sensitivity motif", "motif")

    return _finalize(raw, evidence, channels, vectors, FAMILIARITY_NORMALIZER)


def build_sensitivity_vectors(
    chart: Mapping[str, Any],
    natal_graph_v2_partial: Mapping[str, Any],
) -> tuple[Dict[str, float], Dict[str, list[str]]]:
    ctx = _context(chart, natal_graph_v2_partial)
    planets = ctx["planets"]
    aspects = ctx["aspects"]
    motifs = ctx["motif_scores"]
    raw: Dict[str, float] = {}
    evidence: Dict[str, list[str]] = {}
    channels: Dict[str, set[str]] = {}
    vectors = [
        "criticism_pressure",
        "overwhelm_by_intensity",
        "fear_of_misalignment",
        "instability_overload",
        "visibility_exposure",
        "rejection_or_distance",
    ]

    for aspect in _find_aspects(aspects, "Sun", "Saturn", {"square", "opposition", "conjunction"}) + _find_aspects(aspects, "Mercury", "Saturn", {"square", "opposition", "conjunction"}):
        _add(raw, evidence, channels, "criticism_pressure", 0.22 * _aspect_tightness(aspect), f"{aspect['planet1']}-{aspect['planet2']} hard", "aspect")
    if _planet_in_house(planets, "Saturn", 3) or _planet_in_house(planets, "Saturn", 10):
        _add(raw, evidence, channels, "criticism_pressure", 0.16, "Saturn on 3rd/10th axis", "placement")

    if motifs.get("depth_intimacy"):
        _add(raw, evidence, channels, "overwhelm_by_intensity", 0.18 * motifs["depth_intimacy"], "depth_intimacy motif", "motif")
    if _planet_in_house(planets, "Moon", 8) or _planet_in_house(planets, "Lilith", 8):
        _add(raw, evidence, channels, "overwhelm_by_intensity", 0.18, "8th house depth emphasis", "placement")
    for aspect in _find_aspects(aspects, "Pluto", "Moon", {"square", "opposition", "conjunction"}) + _find_aspects(aspects, "Pluto", "Venus", {"square", "opposition", "conjunction"}):
        _add(raw, evidence, channels, "overwhelm_by_intensity", 0.18 * _aspect_tightness(aspect), f"{aspect['planet1']}-{aspect['planet2']} deep contact", "aspect")

    for aspect in _find_aspects(aspects, "Venus", "Saturn", {"square", "opposition", "conjunction"}) + _find_aspects(aspects, "Mercury", "Neptune", {"square", "opposition", "conjunction"}):
        _add(raw, evidence, channels, "fear_of_misalignment", 0.18 * _aspect_tightness(aspect), f"{aspect['planet1']}-{aspect['planet2']} hard", "aspect")
    if (planets.get("Venus") or {}).get("sign") in {"Virgo", "Libra"}:
        _add(raw, evidence, channels, "fear_of_misalignment", 0.12, "relational perfectionism emphasis", "sign")
    if motifs.get("relational_perfectionism"):
        _add(raw, evidence, channels, "fear_of_misalignment", 0.18 * motifs["relational_perfectionism"], "relational_perfectionism motif", "motif")

    for aspect in _find_aspects(aspects, "Uranus", "Saturn", {"square", "opposition", "conjunction"}) + _find_aspects(aspects, "Uranus", "Moon", {"square", "opposition", "conjunction"}):
        _add(raw, evidence, channels, "instability_overload", 0.20 * _aspect_tightness(aspect), f"{aspect['planet1']}-{aspect['planet2']} instability", "aspect")
    if _strong_placement(planets, "Uranus"):
        _add(raw, evidence, channels, "instability_overload", 0.12, "Uranus strong", "placement")

    if _planet_in_house(planets, "Chiron", 10):
        _add(raw, evidence, channels, "visibility_exposure", 0.20, "Chiron in 10th", "placement")
    for aspect in _find_aspects(aspects, "Neptune", "Midheaven", {"square", "opposition", "conjunction"}) + _find_aspects(aspects, "Jupiter", "Midheaven", {"square", "opposition", "conjunction"}):
        _add(raw, evidence, channels, "visibility_exposure", 0.18 * _aspect_tightness(aspect), f"{aspect['planet1']}-MC sensitivity", "aspect")
    if motifs.get("visibility_sensitivity"):
        _add(raw, evidence, channels, "visibility_exposure", 0.14 * motifs["visibility_sensitivity"], "visibility_sensitivity motif", "motif")

    for aspect in _find_aspects(aspects, "Saturn", "Moon", {"square", "opposition", "conjunction"}) + _find_aspects(aspects, "Saturn", "Venus", {"square", "opposition", "conjunction"}):
        _add(raw, evidence, channels, "rejection_or_distance", 0.18 * _aspect_tightness(aspect), f"{aspect['planet1']}-{aspect['planet2']} hard", "aspect")
    if _planet_in_house(planets, "Venus", 12):
        _add(raw, evidence, channels, "rejection_or_distance", 0.14, "Venus in 12th", "placement")
    if motifs.get("depth_guardedness"):
        _add(raw, evidence, channels, "overwhelm_by_intensity", 0.14 * motifs["depth_guardedness"], "depth_guardedness motif", "motif")
    if motifs.get("thresholded_intimacy"):
        _add(raw, evidence, channels, "overwhelm_by_intensity", 0.12 * motifs["thresholded_intimacy"], "thresholded_intimacy motif", "motif")
    if motifs.get("selective_bonding"):
        _add(raw, evidence, channels, "rejection_or_distance", 0.12 * motifs["selective_bonding"], "selective_bonding motif", "motif")
    if motifs.get("hidden_devotion"):
        _add(raw, evidence, channels, "rejection_or_distance", 0.14 * motifs["hidden_devotion"], "hidden_devotion motif", "motif")

    return _finalize(raw, evidence, channels, vectors, SENSITIVITY_NORMALIZER)


def build_promise_vectors(
    chart: Mapping[str, Any],
    natal_graph_v2_partial: Mapping[str, Any],
) -> tuple[Dict[str, float], Dict[str, list[str]]]:
    ctx = _context(chart, natal_graph_v2_partial)
    planets = ctx["planets"]
    aspects = ctx["aspects"]
    rulers = ctx["house_rulers"]
    motifs = ctx["motif_scores"]
    raw: Dict[str, float] = {}
    evidence: Dict[str, list[str]] = {}
    channels: Dict[str, set[str]] = {}
    vectors = [
        "learn_clear_expression",
        "build_safe_intimacy",
        "integrate_vision_with_structure",
        "mature_visibility",
        "embody_originality",
        "turn_depth_into_wisdom",
    ]

    if _ruler_house(rulers, "1") == 3:
        _add(raw, evidence, channels, "learn_clear_expression", 0.22, "ASC ruler in 3rd", "ruler")
    if _planet_in_house(planets, "Mercury", 3) or _planet_in_house(planets, "Saturn", 3):
        _add(raw, evidence, channels, "learn_clear_expression", 0.18, "3rd house refinement emphasis", "placement")
    if motifs.get("language_boundary"):
        _add(raw, evidence, channels, "learn_clear_expression", 0.16 * motifs["language_boundary"], "language_boundary motif", "motif")
    if motifs.get("private_intellect"):
        _add(raw, evidence, channels, "learn_clear_expression", 0.14 * motifs["private_intellect"], "private_intellect motif", "motif")
    if motifs.get("mentalized_emotion"):
        _add(raw, evidence, channels, "learn_clear_expression", 0.10 * motifs["mentalized_emotion"], "mentalized_emotion motif", "motif")

    if _ruler_house(rulers, "7") == 8:
        _add(raw, evidence, channels, "build_safe_intimacy", 0.22, "7th ruler in 8th", "ruler")
    if _planet_in_house(planets, "Moon", 8):
        _add(raw, evidence, channels, "build_safe_intimacy", 0.20, "Moon in 8th", "placement")
    if motifs.get("depth_intimacy"):
        _add(raw, evidence, channels, "build_safe_intimacy", 0.16 * motifs["depth_intimacy"], "depth_intimacy motif", "motif")
    if motifs.get("selective_bonding"):
        _add(raw, evidence, channels, "build_safe_intimacy", 0.16 * motifs["selective_bonding"], "selective_bonding motif", "motif")
    if motifs.get("service_love"):
        _add(raw, evidence, channels, "build_safe_intimacy", 0.10 * motifs["service_love"], "service_love motif", "motif")
    if motifs.get("relational_perfectionism"):
        _add(raw, evidence, channels, "build_safe_intimacy", 0.10 * motifs["relational_perfectionism"], "relational_perfectionism motif", "motif")
    if motifs.get("depth_guardedness"):
        _add(raw, evidence, channels, "build_safe_intimacy", 0.14 * motifs["depth_guardedness"], "depth_guardedness motif", "motif")
    if motifs.get("quiet_loyalty"):
        _add(raw, evidence, channels, "build_safe_intimacy", 0.10 * motifs["quiet_loyalty"], "quiet_loyalty motif", "motif")
    if motifs.get("hidden_devotion"):
        _add(raw, evidence, channels, "build_safe_intimacy", 0.12 * motifs["hidden_devotion"], "hidden_devotion motif", "motif")
    if motifs.get("thresholded_intimacy"):
        _add(raw, evidence, channels, "build_safe_intimacy", 0.14 * motifs["thresholded_intimacy"], "thresholded_intimacy motif", "motif")

    for aspect in _find_aspects(aspects, "Jupiter", "Neptune", {"conjunction", "trine", "sextile"}) + _find_aspects(aspects, "Saturn", "Uranus", {"conjunction", "trine", "sextile", "square", "opposition"}):
        _add(raw, evidence, channels, "integrate_vision_with_structure", 0.18 * _aspect_tightness(aspect), f"{aspect['planet1']}-{aspect['planet2']} bridge", "aspect")
    if _planet_in_house(planets, "Jupiter", 1) or _planet_in_house(planets, "Neptune", 1):
        _add(raw, evidence, channels, "integrate_vision_with_structure", 0.16, "vision emphasis in 1st", "placement")
    if motifs.get("system_builder"):
        _add(raw, evidence, channels, "integrate_vision_with_structure", 0.16 * motifs["system_builder"], "system_builder motif", "motif")

    if _planet_in_house(planets, "Chiron", 10):
        _add(raw, evidence, channels, "mature_visibility", 0.20, "Chiron in 10th", "placement")
    if _ruler_house(rulers, "10") in {1, 10, 12}:
        _add(raw, evidence, channels, "mature_visibility", 0.18, "MC ruler carries visibility lesson", "ruler")
    if motifs.get("visibility_sensitivity"):
        _add(raw, evidence, channels, "mature_visibility", 0.14 * motifs["visibility_sensitivity"], "visibility_sensitivity motif", "motif")
    if motifs.get("social_fire_private_core"):
        _add(raw, evidence, channels, "mature_visibility", 0.08 * motifs["social_fire_private_core"], "social_fire_private_core motif", "motif")

    if _strong_placement(planets, "Uranus") or _planet_in_house(planets, "Uranus", 1):
        _add(raw, evidence, channels, "embody_originality", 0.22, "Uranus angular/1st", "placement")
    if motifs.get("visionary_originality"):
        _add(raw, evidence, channels, "embody_originality", 0.18 * motifs["visionary_originality"], "visionary_originality motif", "motif")

    if _planet_in_house(planets, "Moon", 8) and _planet_in_house(planets, "Mars", 9):
        _add(raw, evidence, channels, "turn_depth_into_wisdom", 0.20, "8th/9th bridge", "placement")
    if _planet_in_house(planets, "Node", 9):
        _add(raw, evidence, channels, "turn_depth_into_wisdom", 0.16, "Node in 9th", "placement")
    if motifs.get("transformational_intensity"):
        _add(raw, evidence, channels, "turn_depth_into_wisdom", 0.16 * motifs["transformational_intensity"], "transformational_intensity motif", "motif")
    if motifs.get("depth_guardedness"):
        _add(raw, evidence, channels, "turn_depth_into_wisdom", 0.08 * motifs["depth_guardedness"], "depth_guardedness motif", "motif")

    return _finalize(raw, evidence, channels, vectors, PROMISE_NORMALIZER)
