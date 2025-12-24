"""Builds composite-level system interpretations.

BOOT SHIM: This module exists to satisfy imports from natal_interpretation route.
It intentionally produces deterministic, minimal output (no narrative writing).
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

# If CATEGORIES import is available, use it. Otherwise fallback to a safe default list.
try:
    from app.engine.rule_engine import CATEGORIES  # type: ignore
except Exception:
    CATEGORIES = ("identity", "psychology", "relationships", "mind", "career", "karma")


class CompositeInterpretationBuilder:
    """Minimal, deterministic composite interpretation builder (compat shim)."""

    def __init__(
        self,
        composites: Sequence[Dict[str, Any]],
        patterns: Mapping[str, Dict[str, Any]] | None = None,
        *,
        focus_composites: Sequence[Dict[str, Any]] | None = None,
    ) -> None:
        self.composites = list(composites or [])
        self.patterns = patterns or {}
        self.focus_composites = list(focus_composites or [])
        self.used_composite_ids: List[str] = []

    def build(self) -> Dict[str, str]:
        """
        Returns a per-domain short system interpretation if base_interpretation exists.
        If upstream composites don't carry base_interpretation (common), returns {}.
        """
        grouped: Dict[str, List[Dict[str, Any]]] = {d: [] for d in CATEGORIES}
        for comp in self.composites:
            domain = comp.get("domain")
            if isinstance(domain, str) and domain in grouped:
                grouped[domain].append(comp)

        out: Dict[str, str] = {}
        for domain, comps in grouped.items():
            if not comps:
                continue
            sentences: List[str] = []
            seen: set[str] = set()

            for comp in sorted(comps, key=self._priority, reverse=True):
                comp_id = comp.get("composite_id")
                if isinstance(comp_id, str) and comp_id and comp_id not in self.used_composite_ids:
                    self.used_composite_ids.append(comp_id)

                for s in comp.get("base_interpretation", []) or []:
                    norm = self._normalize(s)
                    if norm and norm not in seen:
                        seen.add(norm)
                        sentences.append(norm)

            if sentences:
                out[domain] = " ".join(sentences)

        return out

    def _priority(self, comp: Dict[str, Any]) -> float:
        comp_id = comp.get("composite_id")
        meta = self.patterns.get(comp_id or "", {})
        try:
            return float(meta.get("priority_score") or 0.0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _normalize(text: Any) -> str:
        if not isinstance(text, str):
            return ""
        return " ".join(text.strip().split())
