from __future__ import annotations

from typing import Any, Dict, Mapping, Optional


def derive_load_state(pressure: float, support: float) -> str:
    if pressure > 0.6 and support < 0.45:
        return "pressure_high_support_low"
    if pressure > 0.6 and support >= 0.45:
        return "pressure_high_support_mid"
    if pressure <= 0.6 and support > 0.6:
        return "support_high"
    return "balanced"


def select_primary_theme(
    *,
    theme_shares: Mapping[str, float] | None,
    patterns: Mapping[str, Mapping[str, Any]],
    theme_mapper_result: Mapping[str, Any] | None,
    pressure_index: float,
    support_index: float,
) -> tuple[Optional[str], Optional[str], float]:
    primary: Optional[str] = None
    secondary: Optional[str] = None
    confidence = _confidence_from_gap(0.0, pressure_index, support_index, base=0.4)

    if theme_shares:
        sorted_items = _sorted_theme_shares(theme_shares)
        primary = sorted_items[0][0]
        if len(sorted_items) > 1:
            secondary = sorted_items[1][0]
            gap = sorted_items[0][1] - sorted_items[1][1]
            confidence = _confidence_from_gap(gap, pressure_index, support_index, base=0.4)
        else:
            confidence = _confidence_from_gap(sorted_items[0][1], pressure_index, support_index, base=0.5)

    if not primary and patterns:
        theme = _select_pattern_theme(patterns)
        if theme:
            primary = theme
            confidence = _confidence_from_gap(0.0, pressure_index, support_index, base=0.45)

    if not primary and theme_mapper_result:
        theme = theme_mapper_result.get("theme")
        if isinstance(theme, str) and theme.strip():
            primary = theme.strip()
            confidence = _confidence_from_gap(0.0, pressure_index, support_index, base=0.55)

    return primary, secondary, confidence


def upper_meaning_allowed(pressure: float, support: float) -> bool:
    return pressure >= 0.6 and support >= 0.6


def build_meaning_weighting(
    *,
    pressure_index: float,
    support_index: float,
    dominant_domain: str,
    theme_shares: Mapping[str, float] | None,
    patterns: Mapping[str, Mapping[str, Any]],
    theme_mapper_result: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    load_state = derive_load_state(pressure_index, support_index)
    primary, secondary, confidence = select_primary_theme(
        theme_shares=theme_shares,
        patterns=patterns,
        theme_mapper_result=theme_mapper_result,
        pressure_index=pressure_index,
        support_index=support_index,
    )
    return {
        "pressure_index": pressure_index,
        "support_index": support_index,
        "load_state": load_state,
        "primary_theme": primary,
        "secondary_theme": secondary,
        "theme_confidence": round(confidence, 3),
        "dominant_domain": dominant_domain,
        "upper_meaning_allowed": upper_meaning_allowed(pressure_index, support_index),
    }


def _sorted_theme_shares(theme_shares: Mapping[str, float]) -> list[tuple[str, float]]:
    items: list[tuple[str, float]] = []
    for theme, share in theme_shares.items():
        try:
            value = float(share)
        except (TypeError, ValueError):
            continue
        items.append((str(theme), value))
    items.sort(key=lambda item: item[1], reverse=True)
    return items


def _select_pattern_theme(patterns: Mapping[str, Mapping[str, Any]]) -> Optional[str]:
    if not patterns:
        return None

    def _priority(item: tuple[str, Mapping[str, Any]]) -> float:
        try:
            return float(item[1].get("priority_score") or 0.0)
        except (TypeError, ValueError):
            return 0.0

    ordered = sorted(patterns.items(), key=lambda item: (-_priority(item), str(item[0])))
    for composite_id, meta in ordered:
        theme = _extract_theme(meta)
        if theme:
            return theme
        if isinstance(composite_id, str) and composite_id.strip():
            alias = meta.get("theme_alias") if isinstance(meta, Mapping) else None
            if isinstance(alias, str) and alias.strip():
                return alias.strip()
    return None


def _extract_theme(meta: Mapping[str, Any]) -> Optional[str]:
    for key in ("theme", "theme_id", "primary_theme", "resolved_theme"):
        value = meta.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _confidence_from_gap(gap: float, pressure: float, support: float, *, base: float) -> float:
    netness = abs(pressure - support)
    return _clamp(base + gap + (netness * 0.35))


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))
