"""Faz 1 PR 2 behavior-lock: synastry _orb_tightness boundaries.

Synastry'nin `_orb_tightness` fonksiyonu natal'dan semantik olarak **farklı**
davranır: `orb <= 0.0` durumu synastry'de "missing data" olarak 0.0 döner,
natal'da ise 0° "tightest possible" olarak 1.0 döner.

PR 2'de shared `app.astro.orb_policy` modülüne geçerken bu divergence
`zero_orb_as_missing=True` flag'i ile korunur. Bu test dosyası refactor'dan
ÖNCE mevcut davranışı dondurur; refactor sonrası zero-diff beklenir.

Not: Synastry'nin zero-orb konvansiyonunun aslında doğru mu (sentinel olarak
bilinçli mi) yoksa bug mu olduğu ayrı bir soru. PR 2 bu kararı vermez —
mevcut davranışı korur ve TODO olarak işaretler.
"""
from __future__ import annotations

import pytest

from app.synastry.narrative.synastry_signature_router import _orb_tightness


def _hit(aspect: str, orb: float) -> dict:
    return {"aspect": aspect, "orb_deg": orb}


_BOUNDARY_CASES = [
    # Synastry semantik: orb <= 0 → 0.0 (missing data sentinel)
    ("conjunction", 0.0, 0.0),
    ("conjunction", -1.0, 0.0),
    # Positive orb → linear decay, natal ile aynı tablo
    ("conjunction", 4.0, 0.5),     # 8.0 max → 4/8 = 0.5
    ("conjunction", 7.99, pytest.approx(1.0 - 7.99 / 8.0, abs=1e-6)),
    ("conjunction", 8.0, 0.0),      # tam sınır — tightness 0
    ("conjunction", 10.0, 0.0),     # clamp edilir
    ("opposition", 0.0, 0.0),
    ("opposition", 4.0, 0.5),
    ("opposition", 8.0, 0.0),
    ("square", 0.0, 0.0),
    ("square", 3.5, 0.5),            # 7.0 max
    ("square", 7.0, 0.0),
    ("trine", 0.0, 0.0),
    ("trine", 3.5, 0.5),
    ("trine", 7.0, 0.0),
    ("sextile", 0.0, 0.0),
    ("sextile", 2.5, 0.5),           # 5.0 max
    ("sextile", 5.0, 0.0),
    # Unknown aspect → 6.0 fallback
    ("quincunx", 3.0, 0.5),
    ("quincunx", 6.0, 0.0),
    ("quincunx", 0.0, 0.0),          # fallback path'inde de zero sentinel
]


@pytest.mark.parametrize("aspect,orb,expected", _BOUNDARY_CASES)
def test_synastry_orb_tightness_boundary_behavior(
    aspect: str, orb: float, expected: float
) -> None:
    assert _orb_tightness(_hit(aspect, orb)) == expected


def test_synastry_zero_orb_treated_as_missing() -> None:
    """Kilit semantik fark: synastry'de orb=0 → 0.0, natal'da → 1.0.

    PR 2 sonrası bu davranış `zero_orb_as_missing=True` flag'i ile korunur.
    Eğer birisi synastry'de flag'i unutursa, bu test fail edecek ve
    davranış kayması yakalanacak.
    """
    assert _orb_tightness(_hit("conjunction", 0.0)) == 0.0
    assert _orb_tightness(_hit("trine", 0.0)) == 0.0


def test_synastry_orb_tightness_handles_missing_fields() -> None:
    """orb_deg yok veya parse edilemez → 0.0 (zero_orb_as_missing path)."""
    assert _orb_tightness({"aspect": "conjunction"}) == 0.0
    assert _orb_tightness({"aspect": "conjunction", "orb_deg": None}) == 0.0
    assert _orb_tightness({"aspect": "conjunction", "orb_deg": "bad"}) == 0.0


def test_synastry_unknown_aspect_uses_6_degree_fallback() -> None:
    """Bilinmeyen aspect'e 6.0° max_orb uygulanır, natal ile aynı fallback."""
    assert _orb_tightness(_hit("semisextile", 3.0)) == 0.5
    assert _orb_tightness(_hit("semisextile", 6.0)) == 0.0
