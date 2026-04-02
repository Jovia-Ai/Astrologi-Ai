from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Mapping, Sequence

POINT_AFFINITY_PATH = Path(__file__).resolve().parents[1] / "content" / "tr" / "point_affinity.v1.json"

HOUSE_TO_DOMAIN = {
    1: "identity",
    2: "money",
    3: "mind",
    4: "home",
    5: "identity",
    6: "body",
    7: "relationships",
    8: "inner",
    9: "mind",
    10: "career",
    11: "career",
    12: "inner",
}

TARGET_HOUSE_WEIGHTS: Dict[int, Dict[str, float]] = {
    1: {"identity": 0.28},
    2: {"money": 0.28},
    3: {"mind": 0.26},
    4: {"home": 0.24, "inner": 0.08},
    5: {"identity": 0.16, "relationships": 0.18},
    6: {"body": 0.26},
    7: {"relationships": 0.34},
    8: {"inner": 0.22, "relationships": 0.18},
    9: {"mind": 0.18, "identity": 0.06},
    10: {"career": 0.30},
    11: {"career": 0.14, "relationships": 0.08},
    12: {"inner": 0.24, "relationships": 0.12},
}

SOURCE_HOUSE_WEIGHTS: Dict[int, Dict[str, float]] = {
    1: {"identity": 0.12},
    2: {"money": 0.12},
    3: {"mind": 0.16},
    4: {"home": 0.12, "inner": 0.04},
    5: {"relationships": 0.10, "identity": 0.06},
    6: {"body": 0.12},
    7: {"relationships": 0.18},
    8: {"relationships": 0.12, "inner": 0.10},
    9: {"mind": 0.12},
    10: {"career": 0.14},
    11: {"relationships": 0.06, "career": 0.08},
    12: {"inner": 0.10, "relationships": 0.06},
}

SOURCE_FORCE_BY_BODY = {
    "sun": "self_visibility",
    "moon": "emotional_bonding",
    "mercury": "dialogue",
    "venus": "attraction",
    "mars": "desire_boundary",
    "jupiter": "expansion_pressure",
    "saturn": "commitment_boundary",
    "uranus": "disruption",
    "neptune": "blur",
    "pluto": "intensity",
}

SOURCE_BODY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "sun": {"identity": 0.12, "relationships": 0.04},
    "moon": {"inner": 0.16, "relationships": 0.10},
    "mercury": {"mind": 0.18, "relationships": 0.04},
    "venus": {"relationships": 0.22, "inner": 0.06},
    "mars": {"identity": 0.14, "relationships": 0.10},
    "jupiter": {"identity": 0.10, "relationships": 0.08, "career": 0.04},
    "saturn": {"career": 0.10, "relationships": 0.08, "identity": 0.04},
    "uranus": {"inner": 0.10, "identity": 0.06},
    "neptune": {"inner": 0.18},
    "pluto": {"inner": 0.16, "relationships": 0.06},
}

TARGET_POINT_WEIGHTS: Dict[str, Dict[str, float]] = {
    "asc": {"identity": 0.22},
    "dsc": {"relationships": 0.30},
    "mc": {"career": 0.24},
    "ic": {"home": 0.24, "inner": 0.08},
    "sun": {"identity": 0.20},
    "moon": {"inner": 0.16, "relationships": 0.08},
    "mercury": {"mind": 0.18, "relationships": 0.04},
    "venus": {"relationships": 0.30, "inner": 0.06},
    "mars": {"identity": 0.12, "relationships": 0.14},
    "jupiter": {"identity": 0.10, "career": 0.08, "relationships": 0.05},
    "saturn": {"career": 0.12, "identity": 0.08, "relationships": 0.05},
    "uranus": {"inner": 0.10, "identity": 0.08},
    "neptune": {"inner": 0.18},
    "pluto": {"inner": 0.18, "relationships": 0.06},
    "north node": {"identity": 0.12},
    "chiron": {"inner": 0.14, "relationships": 0.05},
}

ASPECT_TO_MODE = {
    "square": "friction",
    "quincunx": "friction",
    "opposition": "polarity",
    "conjunction": "concentration",
    "trine": "flow",
    "sextile": "opening",
}

RELATIONSHIP_LENS_MULTIPLIERS = {
    "relationships": 1.35,
    "inner": 1.05,
    "identity": 0.95,
    "mind": 0.90,
    "home": 0.92,
    "career": 0.72,
    "money": 0.72,
    "body": 0.80,
}


def _safe_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_point(value: Any) -> str:
    return str(value or "").strip().lower().replace("_", " ")


def normalize_domain(value: Any) -> str:
    token = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    alias_map = {
        "relationship": "relationships",
        "relationships": "relationships",
        "marriage": "relationships",
        "emotion": "inner",
        "emotions": "inner",
        "healing": "inner",
        "intensity": "inner",
        "change": "inner",
        "growth": "identity",
        "direction": "identity",
        "drive": "identity",
        "discipline": "career",
        "security": "home",
        "communication": "mind",
        "self": "identity",
    }
    return alias_map.get(token, token)


def normalize_lens(value: Any) -> str:
    token = normalize_domain(value)
    if token in {"general", ""}:
        return "general"
    return token


@lru_cache(maxsize=1)
def _point_affinity_map() -> Dict[str, str]:
    raw = json.loads(POINT_AFFINITY_PATH.read_text(encoding="utf-8"))
    return {_normalize_point(key): normalize_domain(value) for key, value in dict(raw).items()}


def _point_affinity(point: Any) -> str:
    return _point_affinity_map().get(_normalize_point(point), "")


def _house_domain(house: Any) -> str:
    house_int = _safe_int(house)
    if house_int is None:
        return "general"
    return HOUSE_TO_DOMAIN.get(house_int, "general")


def _target_house(event: Mapping[str, Any]) -> int | None:
    derived = event.get("derived_context") if isinstance(event.get("derived_context"), Mapping) else {}
    natal_target = derived.get("natal_target") if isinstance(derived.get("natal_target"), Mapping) else {}
    scene = event.get("scene") if isinstance(event.get("scene"), Mapping) else {}
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    for candidate in (
        natal_target.get("house"),
        scene.get("outcome_house"),
        houses.get("natal_point_house"),
    ):
        house = _safe_int(candidate)
        if house is not None and 1 <= house <= 12:
            return house
    return None


def _source_house(event: Mapping[str, Any]) -> int | None:
    scene = event.get("scene") if isinstance(event.get("scene"), Mapping) else {}
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    for candidate in (
        scene.get("start_house"),
        houses.get("transit_in_natal_house"),
    ):
        house = _safe_int(candidate)
        if house is not None and 1 <= house <= 12:
            return house
    return None


def _rulership_houses(event: Mapping[str, Any]) -> List[int]:
    derived = event.get("derived_context") if isinstance(event.get("derived_context"), Mapping) else {}
    natal_target = derived.get("natal_target") if isinstance(derived.get("natal_target"), Mapping) else {}
    out: List[int] = []
    for raw in natal_target.get("rulership_houses") or []:
        house = _safe_int(raw)
        if house is not None and 1 <= house <= 12 and house not in out:
            out.append(house)
    return out


def _aspect_mode(event: Mapping[str, Any]) -> str:
    return ASPECT_TO_MODE.get(str(event.get("aspect") or "").strip().lower(), "mixed")


def _timing_state(event: Mapping[str, Any]) -> str:
    phase = str(event.get("phase") or "").strip().lower()
    if phase in {"exact", "exactish"}:
        return "peaking_today"
    if phase == "applying":
        return "building"
    if phase == "separating":
        return "releasing"
    return "active"


def _structurality(event: Mapping[str, Any]) -> str:
    bucket = str(event.get("bucket") or "").strip().lower()
    if bucket == "long":
        return "structural"
    if bucket == "medium":
        return "developing"
    if bucket == "short":
        return "passing"
    return "mixed"


def _relationship_bonus(
    *,
    lens: str,
    target_point: str,
    target_house: int | None,
    source_house: int | None,
    source_body: str,
    aspect_mode: str,
    rulership_houses: Sequence[int],
) -> float:
    if lens != "relationships":
        return 0.0

    bonus = 0.0
    if target_point in {"venus", "dsc"}:
        bonus += 0.30
    if target_point in {"moon", "mars"}:
        bonus += 0.18
    if target_house in {5, 7, 8}:
        bonus += 0.22
    if source_house in {5, 7, 8}:
        bonus += 0.12
    if any(house in {5, 7, 8} for house in rulership_houses):
        bonus += 0.15
    if source_body in {"venus", "moon", "mars"}:
        bonus += 0.08
    if source_body in {"jupiter", "saturn"}:
        bonus += 0.05
    if aspect_mode in {"flow", "opening", "friction", "polarity"}:
        bonus += 0.08
    if target_house == 12 and target_point in {"venus", "dsc", "moon"}:
        bonus += 0.10
    return bonus


def _apply_weight(
    scores: DefaultDict[str, float],
    reasons: DefaultDict[str, List[str]],
    *,
    domain: str,
    weight: float,
    reason: str,
) -> None:
    normalized = normalize_domain(domain)
    if normalized in {"", "general"} or weight == 0.0:
        return
    scores[normalized] += weight
    if reason not in reasons[normalized]:
        reasons[normalized].append(reason)


def _build_domain_scores(
    event: Mapping[str, Any],
    *,
    target_point: str,
    target_affinity: str,
    target_house: int | None,
    source_house: int | None,
    source_body: str,
    aspect_mode: str,
    rulership_houses: Sequence[int],
) -> tuple[Dict[str, float], Dict[str, List[str]]]:
    scores: DefaultDict[str, float] = defaultdict(float)
    reasons: DefaultDict[str, List[str]] = defaultdict(list)

    if target_affinity:
        _apply_weight(
            scores,
            reasons,
            domain=target_affinity,
            weight=0.42,
            reason=f"target_affinity:{target_affinity}",
        )

    for domain, weight in TARGET_POINT_WEIGHTS.get(target_point, {}).items():
        _apply_weight(
            scores,
            reasons,
            domain=domain,
            weight=weight,
            reason=f"target_point:{target_point}",
        )

    if target_house is not None:
        for domain, weight in TARGET_HOUSE_WEIGHTS.get(target_house, {}).items():
            _apply_weight(
                scores,
                reasons,
                domain=domain,
                weight=weight,
                reason=f"target_house:{target_house}",
            )

    if source_house is not None:
        for domain, weight in SOURCE_HOUSE_WEIGHTS.get(source_house, {}).items():
            _apply_weight(
                scores,
                reasons,
                domain=domain,
                weight=weight,
                reason=f"source_house:{source_house}",
            )

    for domain, weight in SOURCE_BODY_WEIGHTS.get(source_body, {}).items():
        _apply_weight(
            scores,
            reasons,
            domain=domain,
            weight=weight,
            reason=f"source_body:{source_body}",
        )

    for house in rulership_houses:
        for domain, weight in TARGET_HOUSE_WEIGHTS.get(house, {}).items():
            _apply_weight(
                scores,
                reasons,
                domain=domain,
                weight=min(0.12, weight * 0.45),
                reason=f"rulership_house:{house}",
            )

    if aspect_mode in {"flow", "opening"} and scores.get("relationships", 0.0) > 0.0:
        _apply_weight(
            scores,
            reasons,
            domain="relationships",
            weight=0.06,
            reason=f"aspect_mode:{aspect_mode}",
        )
    if aspect_mode in {"friction", "polarity"} and scores.get("relationships", 0.0) > 0.0:
        _apply_weight(
            scores,
            reasons,
            domain="relationships",
            weight=0.06,
            reason=f"aspect_mode:{aspect_mode}",
        )
        _apply_weight(
            scores,
            reasons,
            domain="identity",
            weight=0.04,
            reason=f"aspect_mode:{aspect_mode}",
        )

    natal_promise = event.get("natal_promise") if isinstance(event.get("natal_promise"), Mapping) else {}
    natal_promise_score = _safe_float(natal_promise.get("score"), 0.0)
    if natal_promise_score > 0.0:
        anchor_domain = target_affinity or _house_domain(target_house)
        _apply_weight(
            scores,
            reasons,
            domain=anchor_domain,
            weight=min(0.08, natal_promise_score * 0.08),
            reason="natal_promise",
        )

    return dict(scores), dict(reasons)


def build_semantic_projection(
    event: Mapping[str, Any],
    *,
    lens: str = "general",
) -> Dict[str, Any]:
    target_point = _normalize_point(event.get("natal_point"))
    source_body = _normalize_point(event.get("transit_body"))
    target_house = _target_house(event)
    source_house = _source_house(event)
    target_affinity = _point_affinity(event.get("natal_point"))
    aspect_mode = _aspect_mode(event)
    requested_lens = normalize_lens(lens)
    projection_lens = "relationships" if requested_lens == "marriage" else requested_lens
    rulership_houses = _rulership_houses(event)

    raw_scores, reasons = _build_domain_scores(
        event,
        target_point=target_point,
        target_affinity=target_affinity,
        target_house=target_house,
        source_house=source_house,
        source_body=source_body,
        aspect_mode=aspect_mode,
        rulership_houses=rulership_houses,
    )

    projected_scores = dict(raw_scores)
    if projection_lens == "relationships":
        for domain, value in list(projected_scores.items()):
            projected_scores[domain] = value * RELATIONSHIP_LENS_MULTIPLIERS.get(domain, 1.0)
        projected_scores["relationships"] = projected_scores.get("relationships", 0.0) + _relationship_bonus(
            lens=projection_lens,
            target_point=target_point,
            target_house=target_house,
            source_house=source_house,
            source_body=source_body,
            aspect_mode=aspect_mode,
            rulership_houses=rulership_houses,
        )

    sorted_domains = sorted(projected_scores.items(), key=lambda item: (-item[1], item[0]))
    primary_domain = sorted_domains[0][0] if sorted_domains else (_house_domain(target_house) or "general")
    secondary_domain = sorted_domains[1][0] if len(sorted_domains) > 1 else ""
    mixed_mode = False
    if len(sorted_domains) > 1:
        mixed_mode = abs(sorted_domains[0][1] - sorted_domains[1][1]) < 0.12

    semantic_core = {
        "source_body": str(event.get("transit_body") or "").strip(),
        "source_force": SOURCE_FORCE_BY_BODY.get(source_body, "mixed"),
        "source_house": source_house,
        "source_house_domain": _house_domain(source_house),
        "target_point": str(event.get("natal_point") or "").strip(),
        "target_affinity": target_affinity or _house_domain(target_house),
        "target_house": target_house,
        "target_house_domain": _house_domain(target_house),
        "aspect_mode": aspect_mode,
        "timing_state": _timing_state(event),
        "structurality": _structurality(event),
        "rulership_houses": list(rulership_houses),
    }

    return {
        "semantic_core": semantic_core,
        "domain_scores": {
            domain: round(score, 3)
            for domain, score in raw_scores.items()
            if score > 0.0
        },
        "lens_projection": {
            "lens": projection_lens or "general",
            "primary_domain": primary_domain,
            "secondary_domain": secondary_domain,
            "mixed_mode": mixed_mode,
            "framing_reason": reasons.get(primary_domain, [])[:4],
            "projected_scores": {
                domain: round(score, 3)
                for domain, score in projected_scores.items()
                if score > 0.0
            },
        },
    }
