"""Expression resolver that governs narrative tone without generating prose."""
from __future__ import annotations

from typing import Any, Iterable, List, Mapping, Sequence

CONTEXT_STATE_RULES: list[tuple[str, str]] = [
    ("yük arttığında", "pressure_high_support_low"),
    ("insanlarla temas ederken", "relationships_focus"),
    ("ifade alanı daraldığında", "axis_tight"),
    ("derinlik oluştuğunda", "support_high"),
]

TONE_TEMPLATE_MAP: Mapping[str, list[str]] = {
    "firm": ["identity", "career", "karma"],
    "soft": ["psychology", "relationships"],
    "neutral": ["identity", "psychology", "career", "karma"],
}

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
        dominant_domain: str,
        dominant_axis: str,
        themes: Sequence[str],
    ) -> Mapping[str, Any]:
        """Return the deterministic expression profile shape."""

        tone, softening_level = cls._derive_tone(pressure_index, support_index)
        sentence_length = cls._derive_sentence_length(pressure_index, support_index, axis_balance)
        context_states = cls._resolve_context_states(pressure_index, support_index, axis_balance, dominant_domain)
        allowed_templates = cls._derive_allowed_templates(tone, dominant_domain, themes)
        flags = cls._derive_flags(
            pressure_index=pressure_index,
            support_index=support_index,
            dominant_domain=dominant_domain,
            axis_balance=axis_balance,
        )
        fallback_mode = "silent" if len(composite_output or []) < 2 else "regulator_neutral"

        return {
            "tone": tone,
            "sentence_length": sentence_length,
            "softening_level": softening_level,
            "context_states": context_states,
            "allowed_templates": allowed_templates,
            "forbidden_phrases": list(FORBIDDEN_PHRASES),
            "fallback_mode": fallback_mode,
            "flags": flags,
            "dominant_axis": dominant_axis,
            "themes": list(themes),
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

    @classmethod
    def _resolve_context_states(
        cls,
        pressure_index: float,
        support_index: float,
        axis_balance: bool,
        dominant_domain: str,
    ) -> list[str]:
        states: list[str] = []
        scores = {
            "pressure_high_support_low": pressure_index > 0.6 and support_index < 0.45,
            "relationships_focus": dominant_domain in {"relationships", "psychology"} and support_index > 0.4,
            "axis_tight": not axis_balance,
            "support_high": support_index > 0.6,
        }
        for phrase, key in CONTEXT_STATE_RULES:
            if len(states) >= 2:
                break
            if scores.get(key):
                states.append(phrase)
        return states

    @classmethod
    def _derive_allowed_templates(
        cls,
        tone: str,
        dominant_domain: str,
        themes: Iterable[str],
    ) -> list[str]:
        templates = list(TONE_TEMPLATE_MAP.get(tone, TONE_TEMPLATE_MAP["neutral"]))
        if dominant_domain and dominant_domain not in templates:
            templates.append(dominant_domain)
        for theme in themes:
            if "_" in theme:
                domain = theme.split("_", 1)[0]
                if domain and domain not in templates:
                    templates.append(domain)
        return templates

    @classmethod
    def _derive_flags(
        cls,
        *,
        pressure_index: float,
        support_index: float,
        dominant_domain: str,
        axis_balance: bool,
    ) -> Mapping[str, bool]:
        high_load = pressure_index > 0.6 and support_index > 0.6
        oscillation = abs(pressure_index - support_index) > 0.4
        sublimation = dominant_domain in {"psychology", "relationships", "mind"} and support_index > 0.5
        return {
            "high_load_high_capacity": high_load,
            "oscillation_bias": oscillation,
            "sublimation_bias": sublimation,
            "axis_balance": axis_balance,
        }
