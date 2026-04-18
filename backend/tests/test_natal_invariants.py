"""Unit tests for backend/app/natal/invariants.py.

Scoring pipeline'ının hiçbir kullanıcısı değil — fonksiyonlar stateless,
PR 1'de yalnızca modül olarak var. Wiring sonraki PR'larda.
"""
from __future__ import annotations

import pytest

from app.natal.invariants import (
    assert_all_in_unit_range,
    assert_confidence_monotonic,
    assert_motif_in_range,
    assert_theme_weight_ceiling,
    assert_top_n_count,
)


# --------------------------------------------------------------------------
# motif
# --------------------------------------------------------------------------

def test_motif_flat_scores_clean() -> None:
    assert assert_motif_in_range({"a": 0.4, "b": 0.9, "c": 0.0}) == []


def test_motif_nested_scores_clean() -> None:
    assert assert_motif_in_range({"a": {"score": 0.3}, "b": {"score": 1.0}}) == []


def test_motif_out_of_range_flagged() -> None:
    violations = assert_motif_in_range({"a": 1.2, "b": -0.01, "c": 0.5})
    assert len(violations) == 2
    assert any("a" in v for v in violations)
    assert any("b" in v for v in violations)


def test_motif_non_numeric_flagged() -> None:
    violations = assert_motif_in_range({"a": "bad"})
    assert len(violations) == 1
    assert "non-numeric" in violations[0]


def test_motif_float_tolerance_allows_tiny_overshoot() -> None:
    """Normalizer roundtrip'lerde 1e-12 gibi artıklara tolerans."""
    assert assert_motif_in_range({"a": 1.0 + 1e-12}) == []


# --------------------------------------------------------------------------
# confidence
# --------------------------------------------------------------------------

def test_confidence_chart_only_path_clean() -> None:
    violations = assert_confidence_monotonic(
        chart_confidence=0.85,
        test_confidence=0.0,
        global_confidence=0.85,
        has_test_scores=False,
    )
    assert violations == []


def test_confidence_chart_only_mismatch_flagged() -> None:
    violations = assert_confidence_monotonic(
        chart_confidence=0.85,
        test_confidence=0.0,
        global_confidence=0.70,
        has_test_scores=False,
    )
    assert len(violations) == 1
    assert "chart'a eşit olmalı" in violations[0]


def test_confidence_fusion_path_clean() -> None:
    # chart=0.85, test=0.6 → global should be between [0.6, 0.85]
    violations = assert_confidence_monotonic(
        chart_confidence=0.85,
        test_confidence=0.6,
        global_confidence=0.713,
        has_test_scores=True,
    )
    assert violations == []


def test_confidence_fusion_out_of_interval_flagged() -> None:
    violations = assert_confidence_monotonic(
        chart_confidence=0.85,
        test_confidence=0.6,
        global_confidence=0.95,   # > max(chart, test) — invalid
        has_test_scores=True,
    )
    assert len(violations) == 1
    assert "aralığı" in violations[0]


def test_confidence_out_of_unit_range_flagged() -> None:
    violations = assert_confidence_monotonic(
        chart_confidence=1.2,
        test_confidence=0.5,
        global_confidence=0.8,
        has_test_scores=True,
    )
    assert any("chart" in v and "out of" in v for v in violations)


# --------------------------------------------------------------------------
# theme weight
# --------------------------------------------------------------------------

def test_theme_weight_sum_within_ceiling() -> None:
    themes = [{"id": "t1", "weight": 0.3}, {"id": "t2", "weight": 0.4}]
    assert assert_theme_weight_ceiling(themes) == []


def test_theme_weight_sum_exceeds_ceiling_flagged() -> None:
    themes = [{"id": "t1", "weight": 0.6}, {"id": "t2", "weight": 0.5}]
    violations = assert_theme_weight_ceiling(themes)
    assert len(violations) == 1
    assert "theme_weight_sum" in violations[0]


def test_theme_weight_respects_custom_ceiling() -> None:
    themes = [{"id": "t1", "weight": 0.9}, {"id": "t2", "weight": 0.9}]
    assert assert_theme_weight_ceiling(themes, ceiling=2.0) == []


def test_theme_non_numeric_weight_flagged() -> None:
    themes = [{"id": "t1", "weight": "nope"}, {"id": "t2", "weight": 0.3}]
    violations = assert_theme_weight_ceiling(themes)
    assert any("non-numeric" in v for v in violations)


# --------------------------------------------------------------------------
# top_n
# --------------------------------------------------------------------------

def test_top_n_exact_match() -> None:
    assert assert_top_n_count([1, 2, 3], expected=3, label="top_archetypes") == []


@pytest.mark.parametrize("count", [0, 1, 2, 4, 5])
def test_top_n_mismatch_flagged(count: int) -> None:
    items = list(range(count))
    violations = assert_top_n_count(items, expected=3, label="top_archetypes")
    assert len(violations) == 1
    assert "top_archetypes" in violations[0]


# --------------------------------------------------------------------------
# unit-range helper
# --------------------------------------------------------------------------

def test_unit_range_helper_clean() -> None:
    assert assert_all_in_unit_range({"a": 0.0, "b": 1.0, "c": 0.5}, label="v") == []


def test_unit_range_helper_flags_both_out_and_nonnumeric() -> None:
    violations = assert_all_in_unit_range(
        {"a": 1.5, "b": "x", "c": 0.3}, label="v"
    )
    assert len(violations) == 2
