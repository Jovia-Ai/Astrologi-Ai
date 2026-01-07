from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence

from app.helpers.normalize import normalize_node_alias, normalize_planet_key


PATTERN_CONTEXT_MAP: dict[str, dict[str, Any]] = {
    "grand_trine": {
        "flow_type": "closed_loop",
        "pressure_modifier": -0.1,
        "integration_style": "self-contained",
        "tone_bias": "soft",
        "narrative_hint": "Bu yapi sende dogal calisir; cogu zaman zorlamadan ilerler.",
    },
    "t_square": {
        "flow_type": "pressure_driven",
        "pressure_modifier": 0.25,
        "integration_style": "reactive",
        "tone_bias": "intense",
        "narrative_hint": "Bu tema sende rahat birakmaz; seni surekli harekete zorlar.",
    },
    "stellium": {
        "flow_type": "concentrated",
        "pressure_modifier": 0.15,
        "integration_style": "focused",
        "narrative_hint": "Bu alanda enerji fazlasiyla yogunlasmis durumda.",
    },
    "kite": {
        "flow_type": "channeled",
        "pressure_modifier": 0.0,
        "integration_style": "directed",
        "narrative_hint": "Bu yapi dogal akisi belirli bir yone kanalize eder.",
    },
}


class PatternContextEngine:
    def build(
        self,
        patterns: Sequence[Mapping[str, Any]],
        spines: Sequence[Mapping[str, Any]],
        theme_scores: Mapping[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        return apply_pattern_context(patterns, spines)


def apply_pattern_context(
    patterns: Sequence[Mapping[str, Any]],
    spines: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    if not patterns or not spines:
        return [dict(spine) for spine in spines]

    normalized_patterns = _normalize_patterns(patterns)
    updated: List[Dict[str, Any]] = []
    for spine in spines:
        if not isinstance(spine, Mapping):
            continue
        spine_copy = dict(spine)
        bodies = _spine_bodies(spine_copy)
        if not bodies:
            updated.append(spine_copy)
            continue
        selected = _select_pattern_context(normalized_patterns, bodies)
        if selected:
            spine_copy["pattern_context"] = selected
        updated.append(spine_copy)
    return updated


def _normalize_patterns(
    patterns: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for pattern in patterns:
        if not isinstance(pattern, Mapping):
            continue
        pattern_type = str(pattern.get("pattern") or pattern.get("pattern_type") or "").strip().lower()
        if not pattern_type:
            continue
        if pattern_type not in PATTERN_CONTEXT_MAP:
            continue
        raw_bodies = pattern.get("planets") or pattern.get("bodies") or []
        bodies = [_normalize_body(body) for body in raw_bodies if _normalize_body(body)]
        score = pattern.get("score")
        score_value = float(score) if isinstance(score, (int, float)) else 1.0
        normalized.append(
            {
                "pattern_type": pattern_type,
                "bodies": bodies,
                "score": score_value,
            }
        )
    normalized.sort(
        key=lambda entry: (-float(entry.get("score") or 0.0), str(entry.get("pattern_type") or "")),
    )
    return normalized


def _select_pattern_context(
    patterns: Sequence[Mapping[str, Any]],
    spine_bodies: set[str],
) -> Dict[str, Any] | None:
    best: Dict[str, Any] | None = None
    for pattern in patterns:
        bodies = set(pattern.get("bodies") or [])
        if not bodies:
            continue
        overlap = bodies.intersection(spine_bodies)
        if len(overlap) < 2:
            continue
        if best is None:
            best = dict(pattern)
        else:
            if float(pattern.get("score") or 0.0) > float(best.get("score") or 0.0):
                best = dict(pattern)
            elif float(pattern.get("score") or 0.0) == float(best.get("score") or 0.0):
                if str(pattern.get("pattern_type") or "") < str(best.get("pattern_type") or ""):
                    best = dict(pattern)
    if not best:
        return None
    meta = PATTERN_CONTEXT_MAP.get(best.get("pattern_type") or "")
    if not meta:
        return None
    return {
        "pattern_type": best.get("pattern_type"),
        "flow_type": meta.get("flow_type"),
        "pressure_modifier": meta.get("pressure_modifier"),
        "integration_style": meta.get("integration_style"),
        "tone_bias": meta.get("tone_bias"),
        "narrative_hint": meta.get("narrative_hint"),
    }


def _spine_bodies(spine: Mapping[str, Any]) -> set[str]:
    bodies: set[str] = set()
    for entry in spine.get("evidence") or []:
        if not isinstance(entry, Mapping):
            continue
        if entry.get("type") == "placement":
            body = _normalize_body(entry.get("body"))
            if body:
                bodies.add(body)
        elif entry.get("type") == "aspect":
            body_a = _normalize_body(entry.get("a"))
            body_b = _normalize_body(entry.get("b"))
            if body_a:
                bodies.add(body_a)
            if body_b:
                bodies.add(body_b)
        elif entry.get("type") == "rulership":
            body = _normalize_body(entry.get("body"))
            if body:
                bodies.add(body)
        elif entry.get("type") == "house_emphasis":
            for body in entry.get("bodies") or []:
                normalized = _normalize_body(body)
                if normalized:
                    bodies.add(normalized)
        else:
            body = _normalize_body(entry.get("body"))
            if body:
                bodies.add(body)
    return bodies


def _normalize_body(value: Any) -> str:
    normalized = normalize_node_alias(normalize_planet_key(value))
    return normalized or ""
