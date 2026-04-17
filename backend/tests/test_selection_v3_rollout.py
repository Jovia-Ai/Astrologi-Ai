"""Selection V3 hash bazlı canary rollout testi (S1.5).

Doğrulanan davranışlar:
- Boolean phase flag set ise → her seed için aktif (config_flag override)
- Rollout pct 0 → her seed için pasif
- Rollout pct 100 → her seed için aktif
- Rollout pct 10 → SHA256 bucket içindeki seed'ler için aktif (deterministic)
- Aynı seed iki kez sorulduğunda aynı sonucu döner (per-user stable)
"""
from __future__ import annotations

import pytest

from app.natal.narrative.natal_selection_config import (
    _resolve_rollout_pct,
    _seed_in_rollout_bucket,
    is_selection_v3_active_for_seed,
)


def test_rollout_pct_default_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SELECTION_V3_ROLLOUT_PCT", raising=False)
    assert _resolve_rollout_pct() == 0


def test_rollout_pct_clamps_to_range(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SELECTION_V3_ROLLOUT_PCT", "150")
    assert _resolve_rollout_pct() == 100
    monkeypatch.setenv("SELECTION_V3_ROLLOUT_PCT", "-5")
    assert _resolve_rollout_pct() == 0
    monkeypatch.setenv("SELECTION_V3_ROLLOUT_PCT", "  not-a-number  ")
    assert _resolve_rollout_pct() == 0


def test_seed_bucket_zero_pct_always_false() -> None:
    assert _seed_in_rollout_bucket("any-seed-here", 0) is False


def test_seed_bucket_hundred_pct_always_true() -> None:
    assert _seed_in_rollout_bucket("any-seed-here", 100) is True


def test_seed_bucket_deterministic() -> None:
    seed = "1996-12-28T07:10|Istanbul|Capricorn|Libra"
    first = _seed_in_rollout_bucket(seed, 50)
    second = _seed_in_rollout_bucket(seed, 50)
    assert first == second


def test_seed_bucket_distribution_at_10pct() -> None:
    """Geniş örneklemde ~%10 kabul oranı bekliyoruz."""
    pct = 10
    samples = 1000
    accepted = sum(
        _seed_in_rollout_bucket(f"seed-{i}|test|asc|mc", pct)
        for i in range(samples)
    )
    assert 60 <= accepted <= 140  # ~%10 ± kabul edilebilir varyans


def test_config_flag_override_beats_canary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SELECTION_V3_ROLLOUT_PCT", "0")
    decision = is_selection_v3_active_for_seed(
        "any-seed",
        phase_flags={"master_selector_enabled": True},
    )
    assert decision["active"] is True
    assert decision["decision"] == "config_flag"


def test_canary_active_when_seed_in_bucket(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SELECTION_V3_ROLLOUT_PCT", "100")
    decision = is_selection_v3_active_for_seed("any-seed", phase_flags={})
    assert decision["active"] is True
    assert decision["decision"] == "canary"
    assert decision["rollout_pct"] == 100


def test_off_when_no_flag_no_rollout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SELECTION_V3_ROLLOUT_PCT", "0")
    decision = is_selection_v3_active_for_seed("any-seed", phase_flags={})
    assert decision["active"] is False
    assert decision["decision"] == "off"


def test_seed_hash_present_in_decision(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SELECTION_V3_ROLLOUT_PCT", "50")
    decision = is_selection_v3_active_for_seed("user-seed-key", phase_flags={})
    assert len(decision["seed_hash_short"]) == 12
    # hex characters only
    assert all(c in "0123456789abcdef" for c in decision["seed_hash_short"])
