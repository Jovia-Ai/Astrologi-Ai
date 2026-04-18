"""Lunar phase detection — Faz 2 PR 7.

Sun ve Moon ekliptik longitude'larından doğum anındaki ay fazını hesaplar.
8 kanonik faz × 45° equal bucket convention.

### Role — narrative-only

PR 7 scope'u: phase'i payload'a **top-level metadata** olarak surface
etmek. Ranking'e, shadow seçimine, confidence formülüne, subprofile
kararına hiç dokunulmaz. Narrative engine'in Phase 3'te tüketmesi için
hazır sinyal üretir.

### Input contract

`compute_lunar_phase(sun_longitude, moon_longitude)` — iki parametre de
**numeric (float) veya None** kabul eder. Bu tek contract.

Non-numeric tip gelirse (string, vb.) fonksiyon None döner — bu legacy
fail-safe davranıştır, production caller'larının numeric geçmesi
beklenir. Test'te bu path doğrulanır ama call-site'larda sessiz veri
bozulmasını gizlememek için normal akışta kullanılmaz.

### Boundaries

`[lower_inclusive, upper_exclusive)` convention. New phase wrap-around'u
açıkça ele alınır (337.5°'den 360°'ye ve 0°'dan 22.5°'ye kadar).
"""
from __future__ import annotations

from typing import Literal, Optional, Sequence, Tuple


LunarPhase = Literal[
    "new",
    "waxing_crescent",
    "first_quarter",
    "waxing_gibbous",
    "full",
    "waning_gibbous",
    "last_quarter",
    "balsamic",
]


# Her entry: (phase_name, lower_inclusive, upper_exclusive).
# "new" faz'ı wrap-around — lower > upper; compute_lunar_phase bunu açıkça
# handle eder. Bu tablo behavior-lock'lu (constants, config değil).
PHASE_BOUNDARIES: Sequence[Tuple[str, float, float]] = (
    ("new", 337.5, 22.5),              # wraps 0°
    ("waxing_crescent", 22.5, 67.5),
    ("first_quarter", 67.5, 112.5),
    ("waxing_gibbous", 112.5, 157.5),
    ("full", 157.5, 202.5),
    ("waning_gibbous", 202.5, 247.5),
    ("last_quarter", 247.5, 292.5),
    ("balsamic", 292.5, 337.5),
)


def compute_lunar_phase(
    sun_longitude: float | None,
    moon_longitude: float | None,
) -> Optional[LunarPhase]:
    """Sun + Moon longitude → kanonik 8 fazdan biri veya None.

    Args:
        sun_longitude: Sun ekliptik longitude'u (derece, 0..360).
        moon_longitude: Moon ekliptik longitude'u (derece, 0..360).

    Returns:
        8 phase string'inden biri veya None (eksik/bozuk input).

    Fail-safe:
        Sun veya Moon None ise None. Non-numeric (string vb.) ise None.
        Bu "legacy" path'tir — caller'ların numeric göndermesi beklenir.
    """
    try:
        sun = float(sun_longitude) if sun_longitude is not None else None
        moon = float(moon_longitude) if moon_longitude is not None else None
    except (TypeError, ValueError):
        return None
    if sun is None or moon is None:
        return None

    elongation = (moon - sun) % 360.0

    # 'new' phase wrap-around: [337.5, 360) ∪ [0, 22.5)
    if elongation < 22.5 or elongation >= 337.5:
        return "new"
    if elongation < 67.5:
        return "waxing_crescent"
    if elongation < 112.5:
        return "first_quarter"
    if elongation < 157.5:
        return "waxing_gibbous"
    if elongation < 202.5:
        return "full"
    if elongation < 247.5:
        return "waning_gibbous"
    if elongation < 292.5:
        return "last_quarter"
    return "balsamic"
