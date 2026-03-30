from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, Mapping

from app.natal.dispositor_engine import extract_aspects, extract_planet_positions


MAX_PRIMARY_BUNDLES = 3

MAJOR_ORBS = {
    "conjunction": 8.0,
    "opposition": 8.0,
    "square": 7.0,
    "trine": 7.0,
    "sextile": 5.0,
}

PLANET_WEIGHTS = {
    "Sun": 1.0,
    "Moon": 1.0,
    "Mercury": 0.9,
    "Venus": 0.9,
    "Mars": 0.9,
    "Jupiter": 0.75,
    "Saturn": 0.8,
    "Uranus": 0.7,
    "Neptune": 0.7,
    "Pluto": 0.7,
    "Ascendant": 1.0,
    "Descendant": 0.95,
    "Midheaven": 0.9,
    "IC": 0.85,
}

PERSONAL = {"Sun", "Moon", "Mercury", "Venus", "Mars"}
ANGLES = {"Ascendant", "Descendant", "Midheaven", "IC"}
LUMINARIES = {"Sun", "Moon"}
HARD = {"square", "opposition"}
SOFT = {"trine", "sextile"}

PLANET_LABELS_TR = {
    "Sun": "Güneş",
    "Moon": "Ay",
    "Mercury": "Merkür",
    "Venus": "Venüs",
    "Mars": "Mars",
    "Jupiter": "Jüpiter",
    "Saturn": "Satürn",
    "Uranus": "Uranüs",
    "Neptune": "Neptün",
    "Pluto": "Plüton",
    "Ascendant": "Yükselen",
    "Descendant": "Alçalan",
    "Midheaven": "Tepe Noktası",
    "IC": "Dip Noktası",
}

ASPECT_LABELS_TR = {
    "conjunction": "kavuşumu",
    "opposition": "karşıtlığı",
    "square": "karesi",
    "trine": "üçgeni",
    "sextile": "sekstili",
}

BUNDLE_DOMAINS = {
    "personal_core_bundle": ["identity"],
    "angle_identity_bundle": ["identity", "career_visibility"],
    "emotional_regulation_bundle": ["relationships", "intimacy_depth"],
    "mental_style_bundle": ["mind_communication", "meaning_learning"],
    "relational_pattern_bundle": ["relationships", "intimacy_depth"],
    "pressure_growth_bundle": ["identity", "career_visibility"],
    "soft_capacity_bundle": ["creativity_talent", "relationships"],
    "contradiction_bundle": ["identity", "mind_communication"],
}

BUNDLE_TAGS = {
    "personal_core_bundle": {
        "recognition": ["kendini ciddiye alma", "ic cizgiyi koruma"],
        "gift": ["tutarlilik", "daha net benlik"],
        "reflex": ["fazla kontrol", "erken kapanma"],
    },
    "angle_identity_bundle": {
        "recognition": ["disariya yansiyan guc", "gorunurluk hassasiyeti"],
        "gift": ["etki", "yon duygusu"],
        "reflex": ["fazla savunma", "fazla ayar yapma"],
    },
    "emotional_regulation_bundle": {
        "recognition": ["duyguyu filtreleme", "guvenlik arayisi"],
        "gift": ["duygusal dayaniklilik", "derin bag kurma"],
        "reflex": ["geri cekilme", "erken sertlesme"],
    },
    "mental_style_bundle": {
        "recognition": ["fazla dusunme", "cumleyi icte kurma"],
        "gift": ["dikkatli zihin", "dogru ifade"],
        "reflex": ["fazla ayiklama", "kararsiz kalma"],
    },
    "relational_pattern_bundle": {
        "recognition": ["yakinda hassasiyet", "denge arayisi"],
        "gift": ["uyum kurma", "gercek temas"],
        "reflex": ["fazla uyumlanma", "beklentiyi icte tutma"],
    },
    "pressure_growth_bundle": {
        "recognition": ["ic baski", "buyume gerilimi"],
        "gift": ["ustalik", "dayaniklilik"],
        "reflex": ["kendini fazla sikma", "kontrolu abartma"],
    },
    "soft_capacity_bundle": {
        "recognition": ["dogal akis", "kolay baglanti"],
        "gift": ["yaratici akis", "akiskan beceri"],
        "reflex": ["kolaya fazla yaslanma", "daginlasma"],
    },
    "contradiction_bundle": {
        "recognition": ["icte iki yone cekilme", "karisik tepki"],
        "gift": ["esneklik", "katmanli bakis"],
        "reflex": ["bolunme hissi", "ani gidip gelme"],
    },
}


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _aspect_tightness(aspect: Mapping[str, Any]) -> float:
    aspect_name = str(aspect.get("aspect") or "").lower()
    orb = _safe_float(aspect.get("orb"))
    max_orb = MAJOR_ORBS.get(aspect_name, 6.0)
    if orb is None:
        return 0.0
    return _clamp01(1.0 - (orb / max_orb))


def _planet_weight(name: str) -> float:
    return PLANET_WEIGHTS.get(name, 0.55)


def _planet_label_tr(name: str) -> str:
    return PLANET_LABELS_TR.get(name, name)


def _aspect_label_tr(name: str) -> str:
    return ASPECT_LABELS_TR.get(name, name)


def _astro_sources_tr(
    aspect: Mapping[str, Any],
    planets: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    p1 = str(aspect.get("planet1") or "")
    p2 = str(aspect.get("planet2") or "")
    aspect_name = str(aspect.get("aspect") or "").lower()

    sources: list[str] = []
    if p1 and p2 and aspect_name:
        sources.append(f"{_planet_label_tr(p1)}-{_planet_label_tr(p2)} {_aspect_label_tr(aspect_name)}")

    for planet in (p1, p2):
        placement = planets.get(planet) or {}
        house = placement.get("house")
        try:
            house_num = int(house)
        except (TypeError, ValueError):
            house_num = 0
        if planet and house_num > 0:
            sources.append(f"{_planet_label_tr(planet)} {house_num}. ev")

    deduped: list[str] = []
    seen: set[str] = set()
    for item in sources:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item.strip())
        if len(deduped) >= 3:
            break
    return deduped


def _bundle_type_for(aspect: Mapping[str, Any]) -> str:
    p1 = str(aspect.get("planet1") or "")
    p2 = str(aspect.get("planet2") or "")
    aspect_name = str(aspect.get("aspect") or "").lower()
    pair = {p1, p2}

    if pair & ANGLES:
        return "angle_identity_bundle"
    if "Mercury" in pair:
        return "mental_style_bundle"
    if "Moon" in pair and pair & {"Saturn", "Neptune", "Pluto"}:
        return "emotional_regulation_bundle"
    if pair & {"Venus", "Mars", "Descendant"}:
        return "relational_pattern_bundle"
    if aspect_name in HARD and pair & {"Saturn", "Uranus", "Neptune", "Pluto"}:
        return "pressure_growth_bundle"
    if aspect_name in SOFT and pair & PERSONAL:
        return "soft_capacity_bundle"
    if aspect_name in HARD and pair & PERSONAL:
        return "contradiction_bundle"
    return "personal_core_bundle"


def _domain_vector_score(response: Mapping[str, Any], domains: Iterable[str]) -> float:
    expression = response.get("expression_profile")
    if isinstance(expression, Mapping):
        vectors = expression.get("domain_vectors")
        if isinstance(vectors, Mapping):
            scores = []
            for domain in domains:
                raw = _safe_float(vectors.get(domain))
                if raw is not None:
                    scores.append(raw)
            if scores:
                return sum(scores) / len(scores)
    theme_scores = response.get("theme_scores")
    if isinstance(theme_scores, Mapping):
        scores = []
        for domain in domains:
            raw = _safe_float(theme_scores.get(domain))
            if raw is not None:
                scores.append(raw)
        if scores:
            return sum(scores) / len(scores)
    return 0.45


def _motif_resonance(response: Mapping[str, Any], bundle_type: str) -> float:
    patterns = response.get("patterns")
    if isinstance(patterns, Mapping):
        keys = {str(key).lower() for key in patterns.keys()}
        if bundle_type == "mental_style_bundle" and any("mind" in key or "mercur" in key for key in keys):
            return 0.85
        if bundle_type == "emotional_regulation_bundle" and any("emotion" in key or "moon" in key for key in keys):
            return 0.85
        if bundle_type == "relational_pattern_bundle" and any("relationship" in key or "bond" in key for key in keys):
            return 0.85
    return 0.45


def _psychological_recognition(aspect: Mapping[str, Any], bundle_type: str) -> float:
    aspect_name = str(aspect.get("aspect") or "").lower()
    p1 = str(aspect.get("planet1") or "")
    p2 = str(aspect.get("planet2") or "")
    pair = {p1, p2}
    score = 0.4
    if bundle_type in {"emotional_regulation_bundle", "mental_style_bundle", "relational_pattern_bundle"}:
        score += 0.25
    if pair & {"Moon", "Mercury", "Venus", "Mars"}:
        score += 0.15
    if aspect_name in HARD:
        score += 0.15
    elif aspect_name in SOFT:
        score += 0.10
    else:
        score += 0.05
    return _clamp01(score)


def _repetition_support(aspect: Mapping[str, Any], counts: Counter[str]) -> float:
    p1 = str(aspect.get("planet1") or "")
    p2 = str(aspect.get("planet2") or "")
    score = 0.0
    if counts[p1] > 1:
        score += 0.5
    if counts[p2] > 1:
        score += 0.5
    return _clamp01(score)


def _bundle_score(aspect: Mapping[str, Any], response: Mapping[str, Any], counts: Counter[str]) -> float:
    p1 = str(aspect.get("planet1") or "")
    p2 = str(aspect.get("planet2") or "")
    bundle_type = _bundle_type_for(aspect)
    exactness = _aspect_tightness(aspect)
    planet_importance = (_planet_weight(p1) + _planet_weight(p2)) / 2.0
    angle_or_luminary = 0.3
    if {p1, p2} & ANGLES:
        angle_or_luminary += 0.4
    if {p1, p2} & LUMINARIES:
        angle_or_luminary += 0.3
    domains = BUNDLE_DOMAINS.get(bundle_type, ["identity"])
    domain_relevance = _domain_vector_score(response, domains)
    psychological = _psychological_recognition(aspect, bundle_type)
    motif = _motif_resonance(response, bundle_type)
    repetition = _repetition_support(aspect, counts)
    score = (
        exactness * 0.20
        + planet_importance * 0.20
        + angle_or_luminary * 0.15
        + domain_relevance * 0.15
        + psychological * 0.15
        + motif * 0.10
        + repetition * 0.05
    )
    if bundle_type == "personal_core_bundle" and exactness < 0.2:
        score -= 0.05
    return round(_clamp01(score), 4)


def _bundle_domains(bundle_type: str, planets: Mapping[str, Mapping[str, Any]], p1: str, p2: str) -> list[str]:
    domains = list(BUNDLE_DOMAINS.get(bundle_type, ["identity"]))
    houses = {int((planets.get(p1) or {}).get("house") or 0), int((planets.get(p2) or {}).get("house") or 0)}
    if 7 in houses and "relationships" not in domains:
        domains.append("relationships")
    if 8 in houses and "intimacy_depth" not in domains:
        domains.append("intimacy_depth")
    if 3 in houses and "mind_communication" not in domains:
        domains.append("mind_communication")
    if 9 in houses and "meaning_learning" not in domains:
        domains.append("meaning_learning")
    return domains


def _bundle_payload(aspect: Mapping[str, Any], response: Mapping[str, Any], planets: Mapping[str, Mapping[str, Any]], counts: Counter[str]) -> Dict[str, Any]:
    p1 = str(aspect.get("planet1") or "")
    p2 = str(aspect.get("planet2") or "")
    bundle_type = _bundle_type_for(aspect)
    tags = BUNDLE_TAGS.get(bundle_type, BUNDLE_TAGS["personal_core_bundle"])
    score = _bundle_score(aspect, response, counts)
    domains = _bundle_domains(bundle_type, planets, p1, p2)
    return {
        "bundle_id": f"{p1.lower()}_{p2.lower()}_{str(aspect.get('aspect') or '').lower()}",
        "bundle_type": bundle_type,
        "score": score,
        "lead_aspects": [f"{p1} {str(aspect.get('aspect') or '').lower()} {p2}".strip()],
        "support_aspects": [],
        "domains": domains,
        "recognition_tags": list(tags.get("recognition") or []),
        "gift_tags": list(tags.get("gift") or []),
        "reflex_tags": list(tags.get("reflex") or []),
        "source_planets": [p1, p2],
        "astro_sources": _astro_sources_tr(aspect, planets),
    }


def _select_diverse(candidates: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    selected: list[Dict[str, Any]] = []
    used_types: set[str] = set()
    used_pairs: set[tuple[str, ...]] = set()
    for candidate in candidates:
        bundle_type = str(candidate.get("bundle_type") or "")
        pair = tuple(sorted(str(item) for item in candidate.get("source_planets") or []))
        if pair in used_pairs:
            continue
        if bundle_type in used_types and float(candidate.get("score") or 0.0) < 0.78:
            continue
        selected.append(candidate)
        used_types.add(bundle_type)
        used_pairs.add(pair)
        if len(selected) >= MAX_PRIMARY_BUNDLES:
            break
    return selected


def select_aspect_bundles(response: Mapping[str, Any], *, max_bundles: int = MAX_PRIMARY_BUNDLES) -> Dict[str, Any]:
    planets = extract_planet_positions(response)
    aspects = extract_aspects(response)
    if not aspects:
        return {
            "selected_bundles": [],
            "candidate_count": 0,
            "max_primary_bundles": max_bundles,
            "selection_policy": "no_aspects_available",
        }

    counts: Counter[str] = Counter()
    for aspect in aspects:
        counts[str(aspect.get("planet1") or "")] += 1
        counts[str(aspect.get("planet2") or "")] += 1

    candidates = [_bundle_payload(aspect, response, planets, counts) for aspect in aspects]
    candidates.sort(key=lambda item: float(item.get("score") or 0.0), reverse=True)
    selected = _select_diverse(candidates)[:max_bundles]
    return {
        "selected_bundles": selected,
        "candidate_count": len(candidates),
        "max_primary_bundles": max_bundles,
        "selection_policy": "top_scored_diverse_bundles",
    }
