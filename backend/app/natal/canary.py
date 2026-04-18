"""Faz 1 scoring canary — dual-scoring diff recorder skeleton.

Amaç: Faz 1 scoring refactor PR'larında (orb policy, shadow, tie-break,
confidence) eski davranışı yeni implementasyonla paralel çalıştırıp
diverjans'ı kaydetmek. User'a her zaman legacy output gösterilir;
candidate output sadece log/metrics'e gider.

PR 1 scope: sadece interface + NoopCanary default. Refactor PR'ları:
1. LoggingCanary (JSON-lines telemetry)
2. Pipeline'a bağla (`get_canary().record(...)` call site'ları)
3. Karşılaştırma metriği: archetype order değişimi, confidence band kayması,
   top theme diff, shadow değişimi

Design notları:
- Protocol-based — tip sistemi gevşek bağlanma için
- Singleton getter + set_canary — test'te mock kolay
- Record çağrıları ASLA exception fırlatmamalı (canary user path'ini bozamaz)
"""
from __future__ import annotations

from typing import Any, Mapping, Protocol


class ScoringCanary(Protocol):
    """Dual-scoring diff recorder interface.

    `legacy_payload` → mevcut davranış (user'a giden)
    `candidate_payload` → yeni implementasyon (diff için)
    `context` → fixture_id, request_hash, scenario tag gibi metadata
    """

    def record(
        self,
        *,
        legacy_payload: Mapping[str, Any],
        candidate_payload: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> None: ...


class NoopCanary:
    """Default — no-op. Prod'da canary kapalıyken bu kullanılır.

    Bütün çağrıları sessizce yut. Asla exception atma — canary kodu
    user path'ini kıramaz."""

    def record(
        self,
        *,
        legacy_payload: Mapping[str, Any],
        candidate_payload: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> None:
        return None


# Modül-seviye singleton. set_canary() test/runtime'da değiştirebilir.
_active_canary: ScoringCanary = NoopCanary()


def get_canary() -> ScoringCanary:
    """Aktif canary instance'ını döner."""
    return _active_canary


def set_canary(canary: ScoringCanary) -> None:
    """Aktif canary'i değiştir (test ve future wiring için)."""
    global _active_canary
    _active_canary = canary


def reset_canary() -> None:
    """Default NoopCanary'e dön. Test teardown'ları için."""
    global _active_canary
    _active_canary = NoopCanary()
