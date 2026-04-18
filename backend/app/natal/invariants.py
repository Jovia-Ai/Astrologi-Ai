"""Faz 1 scoring invariants — ucuz runtime guardrail'lar.

Her fonksiyon ihlaller listesi döner (boş = temiz). Caller karar verir:
- Test ortamı → ihlaller varsa fail
- Prod → warn-log + telemetri, request'i düşürme

Wiring ikinci fazda yapılacak; bu modül PR 1'de sadece **mevcut** ve
birim test'lerle doğrulanmış halde. Scoring refactor PR'larından biri
motif/vector/confidence pipeline'ına assertion ekleyebilir.

Design notları:
- Stateless pure function'lar — thread safety için başka katman gerekmez
- Float tolerance verilir (1e-9) — normalizer roundtrip'lerde tam eşitlik
  garanti değil
- Error message'lar kısa ve path'lı — log grep'i kolaylaştırır
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence


_FLOAT_TOLERANCE = 1e-9


def _is_in_unit_range(value: float) -> bool:
    return -_FLOAT_TOLERANCE <= value <= 1.0 + _FLOAT_TOLERANCE


def assert_motif_in_range(motifs: Mapping[str, Any]) -> list[str]:
    """Tüm motif skorları [0, 1] aralığında olmalı.

    `motifs` şekli: {motif_id: score} ya da {motif_id: {"score": float, ...}}.
    """
    violations: list[str] = []
    for motif_id, payload in motifs.items():
        score = payload.get("score") if isinstance(payload, Mapping) else payload
        try:
            score_f = float(score)
        except (TypeError, ValueError):
            violations.append(f"motif[{motif_id}]: non-numeric score {score!r}")
            continue
        if not _is_in_unit_range(score_f):
            violations.append(f"motif[{motif_id}]: score {score_f} out of [0,1]")
    return violations


def assert_confidence_monotonic(
    chart_confidence: float,
    test_confidence: float,
    global_confidence: float,
    *,
    has_test_scores: bool,
) -> list[str]:
    """Confidence değerleri için yapısal invariant'lar.

    1. Tüm alanlar [0,1]
    2. Test yoksa global == chart (bypass formülü)
    3. Test varsa global fusion formülünün iki bileşeni arasında kalır:
       min(chart, test) ≤ global ≤ max(chart, test)
    """
    violations: list[str] = []
    for name, value in [
        ("chart", chart_confidence),
        ("test", test_confidence),
        ("global", global_confidence),
    ]:
        if not _is_in_unit_range(float(value)):
            violations.append(f"confidence[{name}]: {value} out of [0,1]")

    if not has_test_scores:
        if abs(global_confidence - chart_confidence) > _FLOAT_TOLERANCE:
            violations.append(
                f"confidence[global]: test yoksa chart'a eşit olmalı "
                f"(chart={chart_confidence}, global={global_confidence})"
            )
    else:
        lo = min(chart_confidence, test_confidence)
        hi = max(chart_confidence, test_confidence)
        if not (lo - _FLOAT_TOLERANCE <= global_confidence <= hi + _FLOAT_TOLERANCE):
            violations.append(
                f"confidence[global]: {global_confidence} weighted-average "
                f"aralığı [{lo}, {hi}] dışında"
            )
    return violations


def assert_theme_weight_ceiling(
    themes: Iterable[Mapping[str, Any]],
    *,
    ceiling: float = 1.0,
    weight_key: str = "weight",
) -> list[str]:
    """Tema ağırlıklarının toplamı ceiling'i aşmamalı.

    Not: Bazı ontology'lerde overlap guard'lar birden fazla tema üretebilir —
    ceiling 1.0 olmak zorunda değil. `ceiling=2.0` vb. override edilebilir.
    """
    violations: list[str] = []
    total = 0.0
    for theme in themes:
        weight = theme.get(weight_key, 0.0)
        try:
            total += float(weight)
        except (TypeError, ValueError):
            violations.append(
                f"theme[{theme.get('id') or '?'}]: non-numeric weight {weight!r}"
            )
    if total > ceiling + _FLOAT_TOLERANCE:
        violations.append(
            f"theme_weight_sum: {total} > ceiling {ceiling}"
        )
    return violations


def assert_top_n_count(
    items: Sequence[Any],
    *,
    expected: int,
    label: str,
) -> list[str]:
    """Top-N seçim sonucu beklenen sayıda item'a sahip olmalı.

    Config-driven N ile kod selection'ı arasındaki drift'i yakalar (ör.
    `result_rules.top_archetypes=3` ama selection 2 döndürüyor)."""
    if len(items) != expected:
        return [f"{label}: expected {expected} items, got {len(items)}"]
    return []


def assert_all_in_unit_range(
    values: Mapping[str, Any],
    *,
    label: str,
) -> list[str]:
    """Herhangi bir {name: float} haritasının tüm değerleri [0,1]."""
    violations: list[str] = []
    for name, value in values.items():
        try:
            value_f = float(value)
        except (TypeError, ValueError):
            violations.append(f"{label}[{name}]: non-numeric {value!r}")
            continue
        if not _is_in_unit_range(value_f):
            violations.append(f"{label}[{name}]: {value_f} out of [0,1]")
    return violations
