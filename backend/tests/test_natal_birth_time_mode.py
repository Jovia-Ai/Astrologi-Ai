"""Faz 1 PR 4: `birth_time_mode` single-source derivation lock.

`birth_time_confidence` string → `{exact, rounded, unknown}` mode map'i
TEK YERDE (`archetype_profile._BIRTH_TIME_MODE_BY_CONFIDENCE` +
`birth_time_mode()` helper) tanımlı. Başka yerlerde dağınık türetim
olmamalı.

`unknown_birthtime` fixture özellikle bu mapping'i exercise eder.
"""
from __future__ import annotations

import pytest

from app.natal.archetype_profile import (
    _BIRTH_TIME_MODE_BY_CONFIDENCE,
    birth_time_mode,
)


@pytest.mark.parametrize(
    "confidence,expected_mode",
    [
        ("exact", "exact"),
        ("verified", "exact"),
        ("Exact", "exact"),   # case-insensitive
        ("EXACT", "exact"),
        ("rounded", "rounded"),
        ("estimated", "rounded"),
        ("unknown", "unknown"),
        ("missing", "unknown"),
        ("approx", "unknown"),
        ("low", "unknown"),
    ],
)
def test_birth_time_mode_known_inputs(confidence: str, expected_mode: str) -> None:
    assert birth_time_mode(confidence) == expected_mode


@pytest.mark.parametrize(
    "confidence",
    ["", "   ", "weird_value", "unspecified"],
)
def test_birth_time_mode_unknown_inputs_default_to_exact(confidence: str) -> None:
    """Bilinmeyen/eşleşmeyen string → `exact` (muhafazakar default).

    Gerekçe: `_chart_confidence` de aynı bilinmeyen input'lar için
    baseline 0.7 döner — yani 'exact' mode'un confidence penceresine düşer.
    Tutarlılık için default 'exact'.
    """
    assert birth_time_mode(confidence) == "exact"


def test_birth_time_mode_mapping_table_is_complete() -> None:
    """Mapping tablosu expected tüm key'leri kapsar.

    Yeni bir confidence kategorisi eklenirse (örn. "projected")
    mapping'e de eklenmeli — bu test unutulmayı engeller."""
    expected_keys = {"exact", "verified", "rounded", "estimated",
                     "unknown", "missing", "approx", "low"}
    assert set(_BIRTH_TIME_MODE_BY_CONFIDENCE.keys()) == expected_keys


def test_birth_time_mode_values_are_three_valued() -> None:
    """Kanonik mode kümesi {exact, rounded, unknown}. Yeni mode eklenirse
    downstream consumer'lar (tone/narrative) güncellenmeli — bu test
    sinyal verir."""
    assert set(_BIRTH_TIME_MODE_BY_CONFIDENCE.values()) == {"exact", "rounded", "unknown"}
