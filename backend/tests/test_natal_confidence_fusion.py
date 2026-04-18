"""Faz 1 behavior-lock: confidence fusion + dead-config tripwire.

Audit C3 revize edildi: `minimum_primary_score=0.52` ve
`minimum_gap_for_single_headline=0.08` `config/scoring/archetype_fusion_v2.yaml`
içinde tanımlı ama kodda HİÇ okunmuyor. Bu dosya iki şeyi dondurur:

1. Confidence fusion formülünün mevcut davranışı:
   - chart-only path (test yoksa) → global = chart
   - test varsa → global = 0.45 * chart + 0.55 * test
   - birth_time_confidence=unknown → chart = 0.45 (floor)
   - birth_time_confidence=exact → chart = 0.85 (ceiling)

2. Dead-config tripwire: `minimum_primary_score` ve
   `minimum_gap_for_single_headline` halen read edilmiyor. Biri bunları
   sessizce wire ederse bu test fail edecek ve "wire etmeden önce policy
   kararı ver" sinyali verecek — Faz 1 PR 4'ün konusu.
"""
from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from app.natal import archetype_profile
from app.natal.archetype_profile import (
    _chart_confidence,
    _test_confidence,
    build_archetype_profile,
)


# --------------------------------------------------------------------------
# Confidence fusion — formula lock
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "birth_time_confidence,expected_chart",
    [
        ("exact", 0.85),
        ("verified", 0.85),
        ("rounded", 0.75),
        ("estimated", 0.75),
        ("unknown", 0.45),
        ("missing", 0.45),
        ("approx", 0.45),
        ("low", 0.45),
        ("", 0.7),      # normalize edilmemiş string → baseline
        ("weird", 0.7),  # eşleşmeyen → baseline
    ],
)
def test_chart_confidence_mapping(birth_time_confidence: str, expected_chart: float) -> None:
    """_chart_confidence() birth_time_confidence kategorilerine göre sabit
    değerler üretir. Bu harita Faz 1 PR 4'te (unknown-birthtime policy)
    kasıtlı olarak değişebilir; o PR içinde bu test güncellenecek.
    """
    assert _chart_confidence(birth_time_confidence) == expected_chart


def test_test_confidence_defaults_when_absent() -> None:
    """Test skoru yoksa test_confidence = 0.0."""
    assert _test_confidence(None, has_test_scores=False) == 0.0
    assert _test_confidence(0.9, has_test_scores=False) == 0.0


def test_test_confidence_uses_answer_consistency_when_present() -> None:
    assert _test_confidence(0.83, has_test_scores=True) == 0.83
    assert _test_confidence(None, has_test_scores=True) == 0.7   # default when consistency None


def _inputs(**overrides):
    """Minimal valid input set for build_archetype_profile."""
    primitive_scores = {
        "primitive_scores": [
            {"primitive_id": "self_definition", "score": 0.82},
            {"primitive_id": "inner_structure", "score": 0.80},
            {"primitive_id": "methodical_drive", "score": 0.74},
            {"primitive_id": "public_refinement", "score": 0.68},
            {"primitive_id": "mental_structuring", "score": 0.78},
            {"primitive_id": "intimacy_depth", "score": 0.65},
            {"primitive_id": "emotional_threshold", "score": 0.61},
        ]
    }
    master_selector = {
        "identity_spine": {
            "primary_identity_spine": {
                "source_primitives": ["self_definition", "inner_structure"],
                "confidence": 0.84,
            },
            "secondary_balancing_line": {
                "source_primitives": ["originality_drive", "big_picture_vision"],
                "confidence": 0.76,
            },
            "relational_line": {
                "source_primitives": ["intimacy_depth"],
                "confidence": 0.67,
            },
            "work_visibility_line": {
                "source_primitives": ["public_refinement"],
                "confidence": 0.74,
            },
            "shadow_protection_line": {
                "source_primitives": ["emotional_threshold"],
                "confidence": 0.63,
            },
        }
    }
    defaults = dict(
        primitive_scores=primitive_scores,
        master_selector=master_selector,
        contradiction_signatures={"top_signatures": [{"id": "structure_vs_originality", "score": 0.7}]},
        natal_feature_graph={"public_private_split": {"public_score": 0.6, "private_score": 0.5}},
        test_scores=None,
        question_family_scores={"structure_preference": 0.9, "mental_precision": 0.82},
        birth_time_confidence="exact",
        answer_consistency=None,
    )
    defaults.update(overrides)
    return defaults


def test_fusion_uses_chart_only_when_test_scores_absent() -> None:
    """Test yoksa: global = chart. 0.45 * chart + 0.55 * test formülü
    ATLANIR — chart raw değeri döner."""
    payload = build_archetype_profile(**_inputs(birth_time_confidence="exact"))
    assert payload["confidence"]["chart"] == 0.85
    assert payload["confidence"]["test"] == 0.0
    assert payload["confidence"]["global"] == 0.85  # chart == global, formül bypass
    assert payload["chart_prior"]["weight_profile"] == "chart_only"


def test_fusion_applies_weighted_formula_when_test_present() -> None:
    """Test varsa: global = 0.45 * chart + 0.55 * test."""
    payload = build_archetype_profile(**_inputs(
        test_scores={"builder": 0.9, "visionary": 0.5},
        answer_consistency=0.8,
        birth_time_confidence="exact",
    ))
    chart, test = payload["confidence"]["chart"], payload["confidence"]["test"]
    expected_global = round(chart * 0.45 + test * 0.55, 4)
    assert payload["confidence"]["global"] == expected_global
    assert payload["chart_prior"]["weight_profile"] == "default"


def test_unknown_birthtime_still_selects_primary_archetype() -> None:
    """C3 revised: unknown birthtime silent failure yaratmıyor.

    Chart=0.45 (floor), global=0.45 (chart-only path) olmasına rağmen
    top_archetypes[0] mevcut. minimum_primary_score=0.52 declared ama
    enforce edilmiyor.

    Faz 1 PR 4 bu davranışı açık policy'e bağlayacak."""
    payload = build_archetype_profile(**_inputs(birth_time_confidence="unknown"))
    assert payload["confidence"]["chart"] == 0.45
    assert payload["confidence"]["global"] == 0.45
    assert len(payload["top_archetypes"]) >= 1, (
        "Unknown birthtime silent failure üretmemeli — archetype seçilmeli"
    )
    # Softening path çalışmalı
    assert payload["top_archetypes"][0]["subprofile_is_softened"] is True


# --------------------------------------------------------------------------
# Dead-config tripwire
# --------------------------------------------------------------------------
# Biri bu alanları wire ederse aşağıdaki test'ler fail edecek. O noktada
# testler güncellenebilir — ama güncelleme aynı PR'da unknown-birthtime
# policy (PR 4) kararıyla birlikte alınmalı.

_ARCHETYPE_SOURCE = Path(inspect.getfile(archetype_profile)).read_text(encoding="utf-8")


def test_minimum_primary_score_is_dead_config() -> None:
    """`minimum_primary_score` config'de declared ama kodda okunmuyor.

    Eğer birisi `result_rules.get("minimum_primary_score")` şeklinde okursa
    bu test fail olacak. Sessiz wire engellendi.
    """
    assert "minimum_primary_score" not in _ARCHETYPE_SOURCE, (
        "minimum_primary_score artık kodda — wire policy'si Faz 1 PR 4 ile "
        "birlikte alınmadan merge edilmemeli. Test snapshot'larındaki unknown-"
        "birthtime path'i için sonuçları ayrıca doğrula."
    )


def test_minimum_gap_for_single_headline_is_dead_config() -> None:
    """`minimum_gap_for_single_headline` de dead — tie-break sinyali olarak
    Faz 1 PR 3 (meaningful tie-break) ile anlamlı hale getirilecek."""
    assert "minimum_gap_for_single_headline" not in _ARCHETYPE_SOURCE, (
        "minimum_gap_for_single_headline kodda okunuyor — tie-break semantiği "
        "Faz 1 PR 3'te açıkça tanımlanmalı. Mevcut deterministic_hash fallback "
        "davranışı da aynı PR'da değiştirilmeli."
    )
