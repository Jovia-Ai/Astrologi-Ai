from __future__ import annotations

from typing import Dict, Optional

from app.transit.astro.moon_phase import moon_phase_score


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def base_marker_score(severity: float, confidence: float, is_peak: bool, orb_deg: Optional[float]) -> float:
    """
    severity/confidence: 0..1 varsayımı
    orb_deg: küçükse daha güçlü
    """
    sev = clamp(float(severity))
    conf = clamp(float(confidence))
    peak_boost = 1.15 if is_peak else 1.0

    if orb_deg is None:
        orb_factor = 1.0
    else:
        orb = max(0.0, float(orb_deg))
        orb_factor = clamp(1.0 - (orb / 6.0), 0.35, 1.0)

    return clamp(sev * 0.55 + conf * 0.45) * peak_boost * orb_factor


def score_for_lens(base: float, lens: str, weight_sum: float, priority: int) -> float:
    """
    base: marker'ın astro gücü
    weight_sum: rulebook'tan gelen lens uyumu ağırlığı
    priority: intent/lens için ekstra öne çıkarma
    """
    compat = clamp(0.35 + weight_sum, 0.0, 1.25)
    pr_boost = 1.0 + (min(max(priority, 0), 5) * 0.05)

    if lens == "general":
        compat = 1.0

    return clamp(base * compat * pr_boost, 0.0, 1.0)


def score_for_intent(base: float, intent_weight: float, priority: int) -> float:
    pr_boost = 1.0 + (min(max(priority, 0), 5) * 0.06)
    return clamp(base * clamp(0.25 + intent_weight, 0.0, 1.35) * pr_boost, 0.0, 1.0)


def score_marker_for_intent(marker: Dict, intent_policy: Dict, moon_phase: str) -> float:
    score = 0.0

    score += float(marker.get("score", 0.0))
    score += moon_phase_score(moon_phase)

    for dom in marker.get("domains", []):
        if dom in intent_policy.get("support", []):
            score += 0.15

    for dom in marker.get("domains", []):
        if dom in intent_policy.get("avoid", []):
            score -= 0.2

    penalties = intent_policy.get("penalties", {})
    for rule, penalty in penalties.items():
        if rule in marker.get("tags", []):
            score += penalty

    return round(score, 3)
