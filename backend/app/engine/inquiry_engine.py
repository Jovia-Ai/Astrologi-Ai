from __future__ import annotations

from typing import Any, Dict, List, Sequence


class InquiryEngine:
    def __init__(self, priority_threshold: float = 0.5) -> None:
        self.priority_threshold = priority_threshold

    def select_focus(
        self,
        composites: Sequence[Dict[str, Any]],
        emphasis: Dict[str, Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, str]]]:
        focus: List[Dict[str, str]] = []
        for composite in composites:
            comp_id = composite.get("composite_id")
            meta = emphasis.get(comp_id, {})
            score = float(meta.get("priority_score", 0))
            if score >= self.priority_threshold:
                focus.append(
                    {
                        "composite_id": comp_id,
                        "reason": self._describe_reason(meta),
                    }
                )
        return {"focus_composites": focus}

    @staticmethod
    def _describe_reason(meta: Dict[str, Any]) -> str:
        if meta.get("planet_load_level") == "high":
            return "high_load"
        if meta.get("stellium"):
            return "stellium_load"
        if meta.get("dominance"):
            return str(meta["dominance"])
        if meta.get("ruler_flow"):
            return "ruler_flow_active"
        return "priority_score"
