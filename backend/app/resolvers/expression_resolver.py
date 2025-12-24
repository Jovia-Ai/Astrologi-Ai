"""Expression resolver that governs narrative tone without generating prose."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

FORBIDDEN_PHRASES: tuple[str, ...] = (
    "aktif eksen",
    "açı profili",
    "aktif akış",
    "zaman dilimi",
    "bu dönem",
    "zamanla",
)


class ExpressionResolver:
    """Determines expression metadata for the narrative builder."""

    @classmethod
    def resolve(
        cls,
        composite_output: Sequence[Mapping[str, Any]],
        pressure_index: float,
        support_index: float,
        axis_balance: bool,
    ) -> Mapping[str, Any]:
        """Return the deterministic expression profile shape."""

        tone, _softening_level = cls._derive_tone(pressure_index, support_index)
        sentence_length = cls._derive_sentence_length(pressure_index, support_index, axis_balance)
        fallback_mode = "silent" if len(composite_output or []) < 2 else "regulator_neutral"

        return {
            "tone": tone,
            "sentence_length": sentence_length,
            "forbidden_phrases": list(FORBIDDEN_PHRASES),
            "fallback_mode": fallback_mode,
        }

    @classmethod
    def _derive_tone(cls, pressure_index: float, support_index: float) -> tuple[str, float]:
        if pressure_index > 0.6 and support_index < 0.4:
            return "firm", 0.2
        if pressure_index < 0.4 and support_index > 0.6:
            return "soft", 0.8
        return "neutral", 0.5

    @classmethod
    def _derive_sentence_length(cls, pressure_index: float, support_index: float, axis_balance: bool) -> str:
        if not axis_balance or pressure_index > 0.65:
            return "short"
        if support_index > 0.65:
            return "long"
        return "medium"
