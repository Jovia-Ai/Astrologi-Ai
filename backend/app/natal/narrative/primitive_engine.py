from __future__ import annotations

from typing import Any, Dict, List, Mapping

from app.natal.narrative.primitive_taxonomy_tr import PRIMITIVE_REGISTRY_V1_TR


def _safe_house(value: Any) -> int | None:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return None
    return ivalue if 1 <= ivalue <= 12 else None


def _norm_aspect(value: Any) -> str:
    return str(value or "").strip().lower()


def _placement(planets: Mapping[str, Any], planet: str) -> Mapping[str, Any]:
    payload = planets.get(planet) if isinstance(planets.get(planet), Mapping) else {}
    return payload if isinstance(payload, Mapping) else {}


def _has_house(planets: Mapping[str, Any], planet: str, house: int) -> bool:
    return _safe_house(_placement(planets, planet).get("house")) == house


def _aspect_matches(facts: Mapping[str, Any], a: str, b: str, allowed: set[str]) -> list[Mapping[str, Any]]:
    out: list[Mapping[str, Any]] = []
    for aspect in facts.get("aspects") or []:
        if not isinstance(aspect, Mapping):
            continue
        pair = {str(aspect.get("planet1") or ""), str(aspect.get("planet2") or "")}
        if pair != {a, b}:
            continue
        if _norm_aspect(aspect.get("type")) in allowed:
            out.append(aspect)
    return out


def _strong_planet(facts: Mapping[str, Any], planet: str) -> bool:
    house = _safe_house(_placement(facts.get("planets") or {}, planet).get("house"))
    if house in {1, 4, 7, 10}:
        return True
    for aspect in facts.get("aspects") or []:
        if not isinstance(aspect, Mapping):
            continue
        pair = {str(aspect.get("planet1") or ""), str(aspect.get("planet2") or "")}
        if planet in pair and pair.intersection({"Ascendant", "Midheaven", "Descendant", "Imum Coeli", "ASC", "MC", "DSC", "IC"}):
            if _norm_aspect(aspect.get("type")) == "conjunction":
                return True
    return False


def _add_hit(
    hits: list[dict[str, Any]],
    *,
    primitive_id: str,
    score: float,
    evidence: list[dict[str, Any]],
    sources: list[str],
    tone_tags: list[str],
    spark: bool,
    category_hint: str,
) -> None:
    meta = PRIMITIVE_REGISTRY_V1_TR.get(primitive_id, {})
    hits.append(
        {
            "primitive_id": primitive_id,
            "score": round(max(0.0, min(score, 1.0)), 4),
            "evidence": evidence[:4],
            "sources": sources[:4],
            "tone_tags": list(dict.fromkeys([*tone_tags, *(meta.get("tone_tags") or [])])),
            "spark": spark,
            "category_hint": category_hint,
            "theme_bias": meta.get("theme_bias"),
            "possible_chips": list(meta.get("possible_chips") or []),
            "description_debug": meta.get("description_debug"),
        }
    )


def build_primitives(chart: Mapping[str, Any], natal_graph: Mapping[str, Any], facts: Mapping[str, Any] | None = None) -> List[Dict[str, Any]]:
    _ = chart
    facts = dict(facts or {})
    planets = facts.get("planets") if isinstance(facts.get("planets"), Mapping) else {}
    house_rulers = facts.get("house_rulers") if isinstance(facts.get("house_rulers"), Mapping) else {}
    angle_signs = facts.get("angle_signs") if isinstance(facts.get("angle_signs"), Mapping) else {}
    house_counts = facts.get("house_counts") if isinstance(facts.get("house_counts"), Mapping) else {}
    dominant_loops = facts.get("dominant_loops") if isinstance(facts.get("dominant_loops"), list) else []
    importance = facts.get("importance") if isinstance(facts.get("importance"), Mapping) else {}
    hits: list[dict[str, Any]] = []

    first_count = int(house_counts.get(1, 0))
    third_count = int(house_counts.get(3, 0))
    tenth_count = int(house_counts.get(10, 0))
    eleventh_count = int(house_counts.get(11, 0))

    if angle_signs.get("ASC") or first_count >= 2:
        evidence = []
        if angle_signs.get("ASC"):
            evidence.append({"type": "angle", "ref": f"ASC {angle_signs.get('ASC')}"})
        if first_count >= 2:
            evidence.append({"type": "house_emphasis", "ref": f"1.ev yoğunluğu {first_count}"})
        _add_hit(hits, primitive_id="self_definition", score=0.55 + min(first_count * 0.05, 0.2), evidence=evidence, sources=["asc_sign", "first_house_emphasis"], tone_tags=["identity"], spark=False, category_hint="spine")

    if _strong_planet(facts, "Saturn") or _has_house(planets, "Saturn", 3):
        evidence = []
        if _strong_planet(facts, "Saturn"):
            evidence.append({"type": "placement", "ref": "Satürn güçlü/angüler"})
        if _has_house(planets, "Saturn", 3):
            evidence.append({"type": "placement", "ref": "Satürn 3.ev"})
        _add_hit(hits, primitive_id="inner_structure", score=0.62, evidence=evidence, sources=["saturn", "angular_weight"], tone_tags=["saturnian"], spark=False, category_hint="spine")

    if _strong_planet(facts, "Uranus") or _has_house(planets, "Uranus", 1):
        evidence = [{"type": "placement", "ref": "Uranüs 1.ev/angüler"}]
        _add_hit(hits, primitive_id="originality_drive", score=0.68, evidence=evidence, sources=["angular_uranus"], tone_tags=["uranian"], spark=True, category_hint="spark")

    if _aspect_matches(facts, "Jupiter", "Neptune", {"conjunction", "trine", "sextile"}) or _has_house(planets, "Jupiter", 1) or _has_house(planets, "Neptune", 1):
        evidence = [{"type": "aspect", "ref": "Jüpiter-Neptün teması"}]
        if _has_house(planets, "Jupiter", 1) or _has_house(planets, "Neptune", 1):
            evidence.append({"type": "placement", "ref": "1.ev Jüpiter/Neptün"})
        _add_hit(hits, primitive_id="big_picture_vision", score=0.66, evidence=evidence, sources=["jupiter_neptune_first"], tone_tags=["neptunian", "jupiterian"], spark=True, category_hint="spark")

    if _strong_planet(facts, "Sun") or _has_house(planets, "Sun", 1):
        _add_hit(hits, primitive_id="visible_presence", score=0.56, evidence=[{"type": "placement", "ref": "Güneş görünür/angüler"}], sources=["sun_angular"], tone_tags=["solar"], spark=False, category_hint="tone")

    if _has_house(planets, "Saturn", 3) or _has_house(planets, "Mercury", 3) or _aspect_matches(facts, "Mercury", "Saturn", {"square", "opposition", "conjunction", "trine", "sextile"}):
        evidence = []
        if _has_house(planets, "Saturn", 3):
            evidence.append({"type": "placement", "ref": "Satürn 3.ev"})
        if _has_house(planets, "Mercury", 3):
            evidence.append({"type": "placement", "ref": "Merkür 3.ev"})
        if _aspect_matches(facts, "Mercury", "Saturn", {"square", "opposition", "conjunction", "trine", "sextile"}):
            evidence.append({"type": "aspect", "ref": "Merkür-Satürn açısı"})
        _add_hit(hits, primitive_id="tone_sensitivity", score=0.63, evidence=evidence, sources=["mercury", "third_house", "saturn"], tone_tags=["mercurial", "saturnian"], spark=False, category_hint="spine")
        _add_hit(hits, primitive_id="systems_thinking", score=0.58, evidence=evidence, sources=["mercury", "saturn"], tone_tags=["mercurial"], spark=False, category_hint="area")

    if _aspect_matches(facts, "Sun", "Saturn", {"square", "opposition", "conjunction"}) or _has_house(planets, "Saturn", 3):
        evidence = [{"type": "aspect", "ref": "Güneş-Satürn baskısı"}] if _aspect_matches(facts, "Sun", "Saturn", {"square", "opposition", "conjunction"}) else []
        if _has_house(planets, "Saturn", 3):
            evidence.append({"type": "placement", "ref": "Satürn 3.ev"})
        _add_hit(hits, primitive_id="inner_critic", score=0.67, evidence=evidence, sources=["sun_saturn", "saturn"], tone_tags=["saturnian"], spark=True, category_hint="spark")

    if _aspect_matches(facts, "Mars", "Saturn", {"square", "opposition", "conjunction"}) or _has_house(planets, "Mars", 9):
        evidence = []
        if _aspect_matches(facts, "Mars", "Saturn", {"square", "opposition", "conjunction"}):
            evidence.append({"type": "aspect", "ref": "Mars-Satürn gerilimi"})
        if _has_house(planets, "Mars", 9):
            evidence.append({"type": "placement", "ref": "Mars 9.ev"})
        _add_hit(hits, primitive_id="push_pull_drive", score=0.7, evidence=evidence, sources=["mars_saturn", "mars_ninth"], tone_tags=["mars", "saturnian"], spark=True, category_hint="spark")
        _add_hit(hits, primitive_id="methodical_drive", score=0.6, evidence=evidence, sources=["mars", "ninth_house"], tone_tags=["earth"], spark=False, category_hint="area")

    if third_count >= 2 or _placement(planets, "Mercury").get("retrograde"):
        evidence = []
        if third_count >= 2:
            evidence.append({"type": "house_emphasis", "ref": f"3.ev yoğunluğu {third_count}"})
        if _placement(planets, "Mercury").get("retrograde"):
            evidence.append({"type": "retrograde", "ref": "Merkür retro"})
        _add_hit(hits, primitive_id="mental_structuring", score=0.57, evidence=evidence, sources=["third_house", "mercury_retro"], tone_tags=["mercurial"], spark=False, category_hint="spine")

    if _has_house(planets, "Moon", 8) or _has_house(planets, "Moon", 7) or any(_safe_house((house_rulers.get("7") or {}).get("primary_ruler_pos", {}).get("house")) == 8 for _ in [0]):
        evidence = []
        if _has_house(planets, "Moon", 8):
            evidence.append({"type": "placement", "ref": "Ay 8.ev"})
        if _safe_house((house_rulers.get("7") or {}).get("primary_ruler_pos", {}).get("house")) == 8:
            evidence.append({"type": "ruler_chain", "ref": "7.ev yöneticisi 8.ev"})
        _add_hit(hits, primitive_id="intimacy_depth", score=0.67, evidence=evidence, sources=["moon", "eighth_house", "seventh_ruler"], tone_tags=["water"], spark=True, category_hint="spine")
        _add_hit(hits, primitive_id="relational_security", score=0.61, evidence=evidence, sources=["seventh_ruler", "moon"], tone_tags=["venusian", "saturnian"], spark=False, category_hint="spine")

    if _aspect_matches(facts, "Moon", "Venus", {"trine", "sextile", "conjunction"}):
        _add_hit(hits, primitive_id="graceful_affection", score=0.55, evidence=[{"type": "aspect", "ref": "Ay-Venüs uyumu"}], sources=["moon_venus"], tone_tags=["venusian"], spark=False, category_hint="tone")

    if _has_house(planets, "Moon", 8) or _aspect_matches(facts, "Moon", "Pluto", {"square", "opposition", "conjunction", "trine", "sextile"}):
        _add_hit(hits, primitive_id="transformative_bonding", score=0.62, evidence=[{"type": "aspect", "ref": "Ay-Plüton/8.ev yoğunluğu"}], sources=["moon_pluto", "eighth_house"], tone_tags=["plutonian"], spark=True, category_hint="spark")
        _add_hit(hits, primitive_id="emotional_threshold", score=0.58, evidence=[{"type": "placement", "ref": "Ay duygusal eşiği yükseltiyor"}], sources=["moon"], tone_tags=["moon"], spark=False, category_hint="tone")

    if angle_signs.get("MC") or tenth_count >= 1:
        evidence = []
        if angle_signs.get("MC"):
            evidence.append({"type": "angle", "ref": f"MC {angle_signs.get('MC')}"})
        if tenth_count >= 1:
            evidence.append({"type": "house_emphasis", "ref": f"10.ev görünür {tenth_count} vurgu"})
        _add_hit(hits, primitive_id="public_refinement", score=0.58 + min(tenth_count * 0.04, 0.12), evidence=evidence, sources=["mc", "tenth_house"], tone_tags=["career"], spark=False, category_hint="spine")

    if _has_house(planets, "Chiron", 10) or _aspect_matches(facts, "Jupiter", "Midheaven", {"square", "opposition", "conjunction"}) or _aspect_matches(facts, "Neptune", "Midheaven", {"square", "opposition", "conjunction"}):
        evidence = []
        if _has_house(planets, "Chiron", 10):
            evidence.append({"type": "placement", "ref": "Kiron 10.ev"})
        if _aspect_matches(facts, "Jupiter", "Midheaven", {"square", "opposition", "conjunction"}):
            evidence.append({"type": "aspect", "ref": "Jüpiter-MC teması"})
        if _aspect_matches(facts, "Neptune", "Midheaven", {"square", "opposition", "conjunction"}):
            evidence.append({"type": "aspect", "ref": "Neptün-MC teması"})
        _add_hit(hits, primitive_id="visibility_sensitivity", score=0.64, evidence=evidence, sources=["mc", "chiron_tenth", "neptune_mc"], tone_tags=["neptunian"], spark=True, category_hint="spark")

    if _placement(planets, "Venus").get("house") == 12:
        _add_hit(hits, primitive_id="backstage_creation", score=0.56, evidence=[{"type": "placement", "ref": "Venüs 12.ev"}], sources=["venus_twelve"], tone_tags=["venusian"], spark=False, category_hint="tone")

    if angle_signs.get("IC") or _has_house(planets, "Moon", 4):
        evidence = []
        if angle_signs.get("IC"):
            evidence.append({"type": "angle", "ref": f"IC {angle_signs.get('IC')}"})
        if _has_house(planets, "Moon", 4):
            evidence.append({"type": "placement", "ref": "Ay 4.ev"})
        _add_hit(hits, primitive_id="recharge_through_home", score=0.6, evidence=evidence, sources=["ic", "moon"], tone_tags=["moon"], spark=False, category_hint="spine")

    if str(angle_signs.get("IC") or "").lower() == "aries" or _safe_house((house_rulers.get("4") or {}).get("primary_ruler_pos", {}).get("house")) == 1:
        _add_hit(hits, primitive_id="family_self_reliance", score=0.59, evidence=[{"type": "angle", "ref": "IC Koç / kökte bağımsızlık"}], sources=["ic_mars"], tone_tags=["mars"], spark=True, category_hint="spark")

    if _strong_planet(facts, "Moon") or _has_house(planets, "Moon", 4) or _has_house(planets, "Saturn", 4):
        _add_hit(hits, primitive_id="recharge_through_home", score=0.58, evidence=[{"type": "placement", "ref": "Ay/Satürn ev hattı"}], sources=["moon", "saturn"], tone_tags=["home"], spark=False, category_hint="spine")

    if _has_house(planets, "Fortune", 5) or _has_house(planets, "Jupiter", 5) or _aspect_matches(facts, "Fortune", "Jupiter", {"trine", "sextile", "conjunction"}):
        _add_hit(hits, primitive_id="creation_luck", score=0.64, evidence=[{"type": "placement", "ref": "Fortuna/Jüpiter yaratım alanında"}], sources=["fortune", "fifth_house"], tone_tags=["jupiterian"], spark=True, category_hint="spine")

    if eleventh_count >= 2 or _has_house(planets, "Fortune", 11):
        _add_hit(hits, primitive_id="network_luck", score=0.56, evidence=[{"type": "house_emphasis", "ref": "11.ev sosyal akış"}], sources=["eleventh_house"], tone_tags=["air"], spark=False, category_hint="spark")

    if _has_house(planets, "Jupiter", 9) or _has_house(planets, "Jupiter", 3) or _aspect_matches(facts, "Jupiter", "Neptune", {"conjunction", "trine", "sextile"}):
        _add_hit(hits, primitive_id="meaningful_expansion", score=0.62, evidence=[{"type": "placement", "ref": "Jüpiter anlam hattını büyütüyor"}], sources=["jupiter", "ninth_house"], tone_tags=["jupiterian"], spark=False, category_hint="spine")

    if dominant_loops or importance:
        top_loop = str(dominant_loops[0].get("signature") or "") if dominant_loops and isinstance(dominant_loops[0], Mapping) else ""
        if top_loop:
            _add_hit(hits, primitive_id="systems_thinking", score=0.54, evidence=[{"type": "configuration", "ref": f"Dominant loop {top_loop}"}], sources=["dispositor_loop"], tone_tags=["pattern"], spark=False, category_hint="area")

    deduped: dict[str, dict[str, Any]] = {}
    for hit in hits:
        existing = deduped.get(hit["primitive_id"])
        if not existing or float(hit["score"]) > float(existing["score"]):
            deduped[hit["primitive_id"]] = hit
    return sorted(deduped.values(), key=lambda item: (-float(item.get("score") or 0.0), str(item.get("primitive_id") or "")))
