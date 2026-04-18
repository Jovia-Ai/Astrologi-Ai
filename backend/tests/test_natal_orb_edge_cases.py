"""Faz 1 behavior-lock: promise_vector_engine orb/tightness boundaries.

Mevcut davranışı (MAJOR_ORBS binary cutoff + linear tightness eğrisi)
dondurur. Faz 1 PR 2 (orb policy unification) bu testleri kasıtlı olarak
kıracak — o PR içinde yeni `orb_policy.yaml` SSoT üzerinden beklenen
değerler güncellenir.

Bu test `promise_vector_engine._aspect_tightness` fonksiyonunu hedefler —
tüm promise vector hesaplamalarının geçtiği çekirdek eğri.

Audit bulguları korunur:
- C1 (orb duality): weights.yaml:orb_curve ile promise_vector MAJOR_ORBS
  arasındaki uyumsuzluk burada test edilmez; her iki yanı da PR 2 ele alır.
  Burada sadece MAJOR_ORBS tarafı dondurulur.
- C5 (double-penalty): tightness'ın downstream orb_curve ile çarpılmasına
  karşı birim test yoktur — integration'da snapshot yakalar.
"""
from __future__ import annotations

import math

import pytest

from app.natal.promise_vector_engine import MAJOR_ORBS, _aspect_tightness


def _aspect(aspect_name: str, orb: float) -> dict:
    return {"aspect": aspect_name, "orb": orb}


# --------------------------------------------------------------------------
# Exact-boundary table: mevcut lineer eğrinin tam kritik noktaları.
# aspect_name, orb, expected_tightness
# --------------------------------------------------------------------------
_BOUNDARY_CASES = [
    # Conjunction max_orb = 8.0
    ("conjunction", 0.00, 1.0),
    ("conjunction", 4.00, 0.5),
    ("conjunction", 7.99, pytest.approx(1.0 - 7.99 / 8.0, abs=1e-6)),
    ("conjunction", 8.00, 0.0),          # tam sınır — halen dahil (tightness 0)
    ("conjunction", 8.01, 0.0),          # sınır dışı — clamp
    ("conjunction", 15.0, 0.0),          # çok dışarıda — negatife düşmez
    # Opposition max_orb = 8.0 (conjunction ile aynı)
    ("opposition", 0.00, 1.0),
    ("opposition", 8.00, 0.0),
    # Square max_orb = 7.0
    ("square", 0.00, 1.0),
    ("square", 3.50, 0.5),
    ("square", 7.00, 0.0),
    # Trine max_orb = 7.0
    ("trine", 0.00, 1.0),
    ("trine", 7.00, 0.0),
    # Sextile max_orb = 5.0
    ("sextile", 0.00, 1.0),
    ("sextile", 2.50, 0.5),
    ("sextile", 5.00, 0.0),
    ("sextile", 5.01, 0.0),
]


@pytest.mark.parametrize("aspect_name,orb,expected", _BOUNDARY_CASES)
def test_aspect_tightness_boundary_behavior(
    aspect_name: str, orb: float, expected: float
) -> None:
    """MAJOR_ORBS tablosunun mevcut kesin davranışını dondur."""
    tightness = _aspect_tightness(_aspect(aspect_name, orb))
    assert tightness == expected, (
        f"{aspect_name}@{orb}°: tightness={tightness}, expected={expected}"
    )


def test_aspect_tightness_unknown_aspect_falls_back_to_6_degrees() -> None:
    """Bilinmeyen aspect adı 6.0° default max_orb kullanır.

    Bu behavior dokümante edilmemiş — Faz 1 PR 2'de açık policy'e bağlanmalı.
    Quincunx, semisextile vb. eklenirse bu fallback silent şekilde
    değişmesin diye lock'luyoruz.
    """
    tightness = _aspect_tightness(_aspect("quincunx", 3.0))
    assert tightness == 0.5


def test_aspect_tightness_negative_when_orb_exceeds_fallback() -> None:
    """Fallback 6.0°'nin üstündeki orb için clamp devreye girer (negatif
    tightness'a izin verilmez)."""
    tightness = _aspect_tightness(_aspect("quincunx", 10.0))
    assert tightness == 0.0


def test_aspect_tightness_handles_missing_orb() -> None:
    """orb None ya da parse edilemezse tightness 0.0 (evidence yok kabul)."""
    assert _aspect_tightness({"aspect": "conjunction"}) == 0.0
    assert _aspect_tightness({"aspect": "conjunction", "orb": None}) == 0.0
    assert _aspect_tightness({"aspect": "conjunction", "orb": "bad"}) == 0.0


def test_major_orbs_table_is_frozen() -> None:
    """MAJOR_ORBS değerleri behavior-lock altında.

    Audit C1: bu tablo ile `config/scoring/weights.yaml:orb_curve` arasında
    uyumsuzluk var. Faz 1 PR 2 tek kaynak `orb_policy.yaml`'a taşırken bu
    sabitler silinecek; silme aynı PR'da `test_aspect_tightness_boundary_behavior`'ı
    da güncellemeyi zorunlu kılar.
    """
    assert MAJOR_ORBS == {
        "conjunction": 8.0,
        "opposition": 8.0,
        "square": 7.0,
        "trine": 7.0,
        "sextile": 5.0,
    }


def test_tightness_linear_not_cosine() -> None:
    """Mevcut tightness formülü lineer (`1 - orb/max`) — cosine değil.

    Audit D2 cosine eğrisi öneriyor (astrolojik sezgiye daha yakın).
    Faz 1 PR 2 eğri değişimini yaparsa bu test fail eder ve diff gözden
    geçirilir. Lineer davranışın köşe taşı: orb=max_orb/2'de tightness=0.5.
    """
    half_orb_tightness = _aspect_tightness(_aspect("conjunction", 4.0))
    assert half_orb_tightness == 0.5

    # Cosine olsaydı `cos(π/2 * 0.5) ≈ 0.707` olurdu — lineer olduğunu doğrular.
    assert half_orb_tightness != pytest.approx(math.cos(math.pi / 4), abs=1e-3)
