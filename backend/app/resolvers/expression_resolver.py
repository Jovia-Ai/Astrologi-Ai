"""Expression resolver that governs narrative tone without generating prose."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from app.natal.narrative.voice_profile_resolver import resolve_voice_profile_v2

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
        *,
        master_selector: Mapping[str, Any] | None = None,
        contradiction_signatures: Mapping[str, Any] | None = None,
        natal_feature_graph: Mapping[str, Any] | None = None,
        primitive_scores: Mapping[str, Any] | None = None,
        seed_key: str | None = None,
        include_debug: bool = False,
    ) -> Mapping[str, Any]:
        """Return the deterministic expression profile shape."""

        tone, softening_level = cls._derive_tone(pressure_index, support_index)
        sentence_length = cls._derive_sentence_length(pressure_index, support_index, axis_balance)
        fallback_mode = "silent" if len(composite_output or []) < 2 else "regulator_neutral"
        voice_profile = resolve_voice_profile_v2(
            master_selector=master_selector,
            contradiction_signatures=contradiction_signatures,
            natal_feature_graph=natal_feature_graph,
            primitive_scores=primitive_scores,
            seed_key=seed_key,
            include_debug=include_debug,
        )

        profile = {
            "tone": tone,
            "sentence_length": sentence_length,
            "softening_level": round(softening_level, 4),
            "forbidden_phrases": list(FORBIDDEN_PHRASES),
            "fallback_mode": fallback_mode,
            "tone_source": "legacy_expression_resolver",
            "voice_profile_v2": voice_profile,
        }

        if str(voice_profile.get("mode") or "") == "active":
            derived = voice_profile.get("derived_expression") if isinstance(voice_profile.get("derived_expression"), Mapping) else {}
            tone_profile = derived.get("tone_profile") if isinstance(derived.get("tone_profile"), Mapping) else {}
            profile.update(
                {
                    "tone": str(derived.get("tone") or tone),
                    "sentence_length": str(derived.get("sentence_length") or sentence_length),
                    "softening_level": round(float(derived.get("softening_level") or softening_level), 4),
                    "tone_source": "voice_profile_v2",
                    "voice_axes": voice_profile.get("axes") if isinstance(voice_profile.get("axes"), Mapping) else {},
                }
            )
            if tone_profile:
                profile.update(
                    {
                        "directness": round(float(tone_profile.get("directness") or 0.5), 4),
                        "warmth": round(float(tone_profile.get("warmth") or 0.55), 4),
                        "intensity": round(float(tone_profile.get("intensity") or 0.5), 4),
                        "certainty": round(float(tone_profile.get("certainty") or 0.55), 4),
                        "tempo": round(float(tone_profile.get("tempo") or 0.5), 4),
                        "distance": round(float(tone_profile.get("distance") or 0.5), 4),
                    }
                )
        elif str(voice_profile.get("mode") or "") == "shadow":
            profile["voice_profile_v2_preview"] = voice_profile

        return profile

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
