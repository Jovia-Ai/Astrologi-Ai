from types import SimpleNamespace
from typing import Any, Dict, Mapping, Sequence

from app.builders.narrative_builder import JoviaLightNarrativeBuilder, SLOT_NAMES


class NarrativeBuilderRouter:
    """
    Routes interpretation to narrative builders.
    Currently only the deterministic JoviaLight builder is active.
    """

    def __init__(self, premium: bool = False) -> None:
        self.premium = premium

    def build(
        self,
        interpretation: Mapping[str, Mapping[str, Any]],
        *,
        meta_info: Mapping[str, Any] | None = None,
        planets: Sequence[Mapping[str, Any]] | None = None,
        aspects: Sequence[Mapping[str, Any]] | None = None,
    ) -> Dict[str, str]:
        engine_result = SimpleNamespace(
            interpretation=_slot_interpretation(interpretation),
            meta_info=meta_info or {},
            planets=planets or [],
            aspects=aspects or [],
        )
        builder = JoviaLightNarrativeBuilder(engine_result)
        return builder.build()


def _slot_interpretation(
    interpretation: Mapping[str, Mapping[str, Any]] | None,
) -> Dict[str, Dict[str, str]]:
    if not interpretation:
        return {}
    normalized: Dict[str, Dict[str, str]] = {}
    for domain, slots in interpretation.items():
        if not isinstance(domain, str):
            continue
        domain_key = domain.strip().lower()
        if not domain_key or not isinstance(slots, Mapping):
            continue
        slot_texts: Dict[str, str] = {}
        for slot in SLOT_NAMES:
            if slot_value := slots.get(slot):
                if text := _slot_text(slot_value):
                    slot_texts[slot] = text
        if slot_texts:
            normalized[domain_key] = slot_texts
    return normalized


def _slot_text(value: Any) -> str | None:
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None
    if isinstance(value, Mapping):
        for key in ("text", "sentence"):
            candidate = value.get(key)
            if isinstance(candidate, str):
                cleaned = candidate.strip()
                if cleaned:
                    return cleaned
        return None
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            if text := _slot_text(item):
                return text
    return None
