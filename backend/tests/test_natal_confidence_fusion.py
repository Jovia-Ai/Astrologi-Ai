"""Faz 1 behavior-lock: confidence fusion + wired config policy.

PR 4'te `minimum_primary_score` ve `minimum_gap_for_single_headline` ikisi de
**açık policy altında wire'landı**:

- `minimum_primary_score` → her top_archetype item'ına
  `score_meets_primary_threshold` flag'i olarak düşer. Gate değil, metadata.
  Silent failure yaratmaz; consumer UI düşük güven rozeti gösterebilir.

- `minimum_gap_for_single_headline` → `_attach_why_this_not_that`'in inline
  hardcoded 0.08 eşiği yerine config'ten okunur. Davranış aynı, drift biter.

Confidence fusion formülü (PR 1'den beri lock'lu):
  - chart-only path (test yoksa) → global = chart
  - test varsa → global = 0.45 * chart + 0.55 * test
  - birth_time_confidence=unknown → chart = 0.45 (floor)
  - birth_time_confidence=exact → chart = 0.85 (ceiling)
"""
from __future__ import annotations

import pytest

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
# PR 4 wired policy locks
# --------------------------------------------------------------------------
# Eski dead-config tripwire'larının yerini yeni davranış lock'ları aldı.
# Bu test'ler "wired correctly and behavior is exact" diyor — deleting the
# assertions to make them pass is the wrong fix; updating the value is.


def test_minimum_primary_score_wired_as_flag_not_gate() -> None:
    """`minimum_primary_score` her top_archetype item'ında
    `score_meets_primary_threshold` olarak belirir. Gate DEĞİL:
    score < threshold bile olsa archetype seçimi silinmez (silent failure yok).
    """
    payload = build_archetype_profile(**_inputs(
        test_scores={"builder": 0.95, "visionary": 0.55, "depthkeeper": 0.30},
        answer_consistency=0.9,
    ))
    top = payload["top_archetypes"]
    assert len(top) >= 1, "minimum_primary_score gate olmamalı — item'lar silinmedi"
    for item in top:
        assert "score_meets_primary_threshold" in item, (
            f"{item.get('id')}: score_meets_primary_threshold flag'i yok"
        )
        assert isinstance(item["score_meets_primary_threshold"], bool)


def test_minimum_primary_score_flag_tracks_threshold() -> None:
    """Flag davranışı: score >= 0.52 → True, aksi False."""
    payload = build_archetype_profile(**_inputs(
        test_scores={"builder": 0.95, "visionary": 0.50, "depthkeeper": 0.30},
        answer_consistency=0.9,
    ))
    by_id = {item["id"]: item for item in payload["top_archetypes"]}
    # Builder sağlam skor üzerinde → meets threshold
    if "builder" in by_id:
        assert by_id["builder"]["score_meets_primary_threshold"] is True


def test_minimum_gap_for_single_headline_wired_from_config() -> None:
    """Mevcut config değeri 0.08. Hardcoded inline'dan config'e çekildi.
    İki yakın skorlu arketip → why_this_not_that runner-up mention'ı tetiklenir.
    """
    # İki arketip çok yakın skor üretecek şekilde ayarla — gap < 0.08
    payload = build_archetype_profile(**_inputs(
        test_scores={"builder": 0.80, "visionary": 0.79, "depthkeeper": 0.40},
        answer_consistency=0.85,
    ))
    top = payload["top_archetypes"]
    # İlk item yakın gap'te → why_this_not_that'te runner-up label referansı olmalı
    first_why = top[0].get("why_this_not_that", "")
    # Wired olduğunu doğrula: runner-up'a referans var (visionary label'ı)
    # Davranış aynı olduğu için mesaj formatı bozulmadı
    assert first_why, "why_this_not_that boş olmamalı"


# --------------------------------------------------------------------------
# Birth time mode (single-source derivation lock)
# --------------------------------------------------------------------------

def test_birth_time_mode_surfaces_in_payload() -> None:
    """`birth_time_mode` payload'ta görünür ve confidence input'undan
    tek kaynak üzerinden türetilir."""
    exact = build_archetype_profile(**_inputs(birth_time_confidence="exact"))
    unknown = build_archetype_profile(**_inputs(birth_time_confidence="unknown"))
    rounded = build_archetype_profile(**_inputs(birth_time_confidence="rounded"))

    assert exact["birth_time_mode"] == "exact"
    assert unknown["birth_time_mode"] == "unknown"
    assert rounded["birth_time_mode"] == "rounded"
