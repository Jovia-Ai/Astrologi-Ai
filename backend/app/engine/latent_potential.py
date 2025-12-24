from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Sequence


class LatentPotentialEngine:
    """Flags structural potential when strong composites lack regulation pathways."""

    PRIORITY_THRESHOLD = 0.75

    def build(
        self,
        composites: Sequence[Mapping[str, Any]],
        patterns: Mapping[str, Mapping[str, Any]],
        aspect_mechanics: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> Dict[str, bool]:
        mechanics = aspect_mechanics or {}
        latent_flags: Dict[str, bool] = {}
        for composite in composites:
            comp_id = composite.get("composite_id")
            if not comp_id:
                continue
            meta = patterns.get(comp_id, {})
            priority = float(meta.get("priority_score") or 0.0)
            if priority < self.PRIORITY_THRESHOLD:
                continue
            sources = composite.get("sources", []) or []
            regulation_paths = 0
            for source in sources:
                normalized = str(source).lower()
                entry = mechanics.get(normalized)
                if entry and entry.get("regulation_possible"):
                    regulation_paths += 1
            latent_flags[comp_id] = regulation_paths == 0
        return latent_flags
