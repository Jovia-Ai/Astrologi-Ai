from types import SimpleNamespace
from typing import Any, Dict, Mapping, Sequence

from app.engine.jovia_narrative_builder import JoviaLightNarrativeBuilder


class NarrativeBuilderRouter:
    """
    Routes interpretation to narrative builders.
    Currently only the deterministic JoviaLight builder is active.
    """

    def __init__(self, premium: bool = False) -> None:
        self.premium = premium

    def build(
        self,
        interpretation: Mapping[str, Sequence[str]],
        meta_info: Mapping[str, Any] | None = None,
    ) -> Dict[str, str]:
        engine_result = SimpleNamespace(interpretation=interpretation)
        builder = JoviaLightNarrativeBuilder(engine_result)
        return builder.build()
