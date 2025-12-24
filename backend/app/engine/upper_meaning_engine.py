from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence


class UpperMeaningEngine:
    MAX_MEANINGS = 2

    def __init__(self, upper_meaning_root: str | None = None) -> None:
        root = (
            Path(upper_meaning_root)
            if upper_meaning_root
            else Path(__file__).resolve().parents[2] / "data" / "astro_rules" / "upper_meaning"
        )
        self.rules = self._load_rules(root)

    def _load_rules(self, root: Path) -> List[Dict[str, Any]]:
        rules: List[Dict[str, Any]] = []
        if not root.exists():
            return rules
        for path in sorted(root.glob("*.json")):
            try:
                with path.open("r", encoding="utf-8") as handle:
                    payload = json.load(handle)
            except (json.JSONDecodeError, OSError):
                continue
            if payload.get("id") and payload.get("output"):
                rules.append(payload)
        return rules

    def build(
        self,
        focus_composites: Sequence[Dict[str, Any]],
        emphasis: Dict[str, Dict[str, Any]],
        *,
        core_aspects: Iterable[str],
        aspect_mechanics: Mapping[str, Dict[str, Any]] | None = None,
    ) -> List[Dict[str, Any]]:
        meanings: List[Dict[str, Any]] = []
        core_set = {aspect.lower() for aspect in core_aspects if isinstance(aspect, str)}
        mechanics = aspect_mechanics or {}
        for focus in focus_composites:
            comp_id = focus.get("composite_id")
            if not comp_id or len(meanings) >= self.MAX_MEANINGS:
                continue
            meta = emphasis.get(comp_id, {})
            rule = self._match_rule(meta, core_set, mechanics)
            if rule:
                meanings.append(
                    {
                        "composite_id": comp_id,
                        "upper_meaning": list(rule["output"].get("upper_meaning", [])),
                    }
                )
        return meanings

    def _match_rule(
        self,
        meta: Dict[str, Any],
        core_aspects: set[str],
        aspect_mechanics: Mapping[str, Dict[str, Any]],
    ) -> Dict[str, Any] | None:
        for rule in self.rules:
            triggers = rule.get("triggers", {})
            if self._matches_triggers(triggers, meta, core_aspects, aspect_mechanics):
                return rule
        return None

    @staticmethod
    def _matches_triggers(
        triggers: Dict[str, Any],
        meta: Dict[str, Any],
        core_aspects: set[str],
        aspect_mechanics: Mapping[str, Dict[str, Any]],
    ) -> bool:
        planet_trigger = triggers.get("planet_load")
        if planet_trigger:
            planet = str(planet_trigger.get("planet", "")).lower()
            minimum = int(planet_trigger.get("minimum", 0))
            if not planet or meta.get("planet_load", {}).get(planet, 0) < minimum:
                return False
        required_aspects = triggers.get("core_aspects", [])
        if required_aspects:
            if not all(aspect.lower() in core_aspects for aspect in required_aspects if isinstance(aspect, str)):
                return False
        dominance = triggers.get("dominance")
        if dominance and meta.get("dominance") != dominance:
            return False
        ruler_flow = triggers.get("ruler_flow")
        if ruler_flow and meta.get("ruler_flow") != ruler_flow:
            return False
        aspect_requirements = triggers.get("aspect_mechanics")
        if aspect_requirements:
            if not UpperMeaningEngine._aspect_requirement_met(aspect_requirements, aspect_mechanics):
                return False
        return True

    @staticmethod
    def _aspect_requirement_met(requirement: Dict[str, Any], aspect_mechanics: Mapping[str, Dict[str, Any]]) -> bool:
        if not requirement:
            return True
        entries = list(aspect_mechanics.values())
        if not entries:
            return False
        energy_modes = requirement.get("energy_mode")
        if energy_modes:
            if not any(entry.get("energy_mode") in energy_modes for entry in entries):
                return False
        regulation_required = requirement.get("regulation_required")
        if regulation_required is True:
            if not any(entry.get("regulation_required") for entry in entries):
                return False
        return True
