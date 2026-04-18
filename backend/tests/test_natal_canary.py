"""Unit tests for backend/app/natal/canary.py.

PR 1 scope: interface doğruluğu + NoopCanary exception-free davranış.
Gerçek wiring ve LoggingCanary Faz 1 refactor PR'larında eklenecek.
"""
from __future__ import annotations

from typing import Any, Mapping

from app.natal.canary import NoopCanary, ScoringCanary, get_canary, reset_canary, set_canary


class _RecordingCanary:
    """Test yardımcısı — kaydedilen çağrıları tutar."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def record(
        self,
        *,
        legacy_payload: Mapping[str, Any],
        candidate_payload: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self.calls.append(
            {
                "legacy": dict(legacy_payload),
                "candidate": dict(candidate_payload),
                "context": dict(context) if context else None,
            }
        )


def test_default_canary_is_noop() -> None:
    reset_canary()
    canary = get_canary()
    assert isinstance(canary, NoopCanary)


def test_noop_record_accepts_without_error() -> None:
    noop = NoopCanary()
    # Hiçbir input kombinasyonu exception atmamalı
    noop.record(legacy_payload={}, candidate_payload={})
    noop.record(legacy_payload={"a": 1}, candidate_payload={"a": 2}, context={"id": "x"})
    noop.record(legacy_payload={"deep": {"nested": [1, 2]}}, candidate_payload={"deep": {"nested": [3]}})


def test_noop_record_returns_none() -> None:
    assert NoopCanary().record(legacy_payload={}, candidate_payload={}) is None


def test_set_canary_replaces_active_instance() -> None:
    reset_canary()
    recording = _RecordingCanary()
    set_canary(recording)
    try:
        active = get_canary()
        assert active is recording
        active.record(
            legacy_payload={"id": "a"},
            candidate_payload={"id": "b"},
            context={"fixture": "simple"},
        )
        assert len(recording.calls) == 1
        assert recording.calls[0]["legacy"] == {"id": "a"}
        assert recording.calls[0]["candidate"] == {"id": "b"}
        assert recording.calls[0]["context"] == {"fixture": "simple"}
    finally:
        reset_canary()


def test_reset_canary_restores_noop() -> None:
    set_canary(_RecordingCanary())
    reset_canary()
    assert isinstance(get_canary(), NoopCanary)


def test_scoring_canary_protocol_accepts_noop() -> None:
    """Structural typing — NoopCanary ScoringCanary contract'ını sağlar."""
    # Not: isinstance(x, Protocol) runtime'da çalışmaz (runtime_checkable yok).
    # Structural check: record() signature'ı uyumlu mu?
    canary: ScoringCanary = NoopCanary()
    canary.record(legacy_payload={}, candidate_payload={})
