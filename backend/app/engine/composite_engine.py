from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import re
from typing import Any, Dict, List, Sequence

from app.engine.context_maps import DEFAULT_CONTEXT, HOUSE_CONTEXT
from app.engine.style_maps import (
    ELEMENT_FALLBACK,
    DEFAULT_STYLE,
    SIGN_STYLE,
    apply_style_modifiers,
)
from app.helpers.meta_detectors import get_element_for_sign, normalize_sign


class CompositeEngine:
    """
    CompositeEngine builds lived-experience composites.
    It has TWO layers:
    1) Base composites (always generated, programmatic)
    2) Rule composites (JSON-triggered, optional, high-precision)
    """

    def __init__(self, astro_rules_root: str | None = None) -> None:
        rules_root = (
            Path(astro_rules_root)
            if astro_rules_root
            else Path(__file__).resolve().parents[2] / "data" / "astro_rules"
        )

        self.composite_rules = self._load_composite_rules(rules_root / "composite")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(
        self,
        placements: Sequence[str],
        core_aspects: Sequence[str],
    ) -> List[Dict[str, Any]]:
        """
        Build composites for a chart.

        Order:
        1) Base composites (always)
        2) Rule composites (conditional JSON matches)
        """

        base = self._build_base_composites(placements, core_aspects)
        rule_based = self._build_rule_composites(placements, core_aspects)

        return base + rule_based

    # ------------------------------------------------------------------
    # Base composites (ALWAYS GENERATED)
    # ------------------------------------------------------------------

    def _build_base_composites(
        self,
        placements: Sequence[str],
        core_aspects: Sequence[str],
    ) -> List[Dict[str, Any]]:
        """
        Programmatic composites.
        These describe WHAT IS HAPPENING, not why.
        No destiny, no evolution, no interpretation tone.
        """

        composites: List[Dict[str, Any]] = []

        context = set(placements) | set(core_aspects)

        # --- IDENTITY (Sun-based) ---
        sun_sources = [p for p in placements if p.startswith("sun_in_")]
        sun_aspects = [a for a in core_aspects if a.startswith("sun_")]

        if sun_sources:
            composites.append(
                {
                    "composite_id": "identity_sun_base",
                    "domain": "identity",
                    "sources": sun_sources + sun_aspects,
                    "derived_signals": self._derive_structural_signals(sun_sources + sun_aspects, placements),
                }
            )

        # --- EMOTIONAL / PSYCHOLOGY (Moon-based) ---
        moon_sources = [p for p in placements if p.startswith("moon_in_")]
        moon_aspects = [a for a in core_aspects if a.startswith("moon_")]

        if moon_sources:
            composites.append(
                {
                    "composite_id": "psychology_moon_base",
                    "domain": "psychology",
                    "sources": moon_sources + moon_aspects,
                    "derived_signals": self._derive_structural_signals(moon_sources + moon_aspects, placements),
                }
            )

        return composites

    # ------------------------------------------------------------------
    # Rule-based composites (JSON-triggered)
    # ------------------------------------------------------------------

    def _build_rule_composites(
        self,
        placements: Sequence[str],
        core_aspects: Sequence[str],
    ) -> List[Dict[str, Any]]:
        context = set(placements) | set(core_aspects)
        matched: List[Dict[str, Any]] = []

        for rule in self.composite_rules:
            conditions = rule["conditions"]
            if not conditions:
                continue

            if set(conditions).issubset(context):
                interpretation = self._normalize_output(rule["output"])
                matched.append(
                    {
                        "composite_id": rule["id"],
                        "domain": rule["domain"],
                        "sources": list(conditions),
                        "derived_signals": self._derive_structural_signals(list(conditions), placements),
                    }
                )

        return matched

    # ------------------------------------------------------------------
    # Rule loading helpers
    # ------------------------------------------------------------------

    def _load_composite_rules(self, directory: Path) -> List[Dict[str, Any]]:
        rules: List[Dict[str, Any]] = []
        if not directory.exists():
            return rules

        for file_path in sorted(directory.glob("*.json")):
            payload = self._read_json(file_path)
            if not payload:
                continue
            conditions = payload.get("conditions", [])
            rule = {
                "id": payload.get("id"),
                "domain": self._derive_domain(file_path),
                "conditions": conditions,
                "output": payload.get("output", {}),
            }
            if rule["id"] and conditions:
                rules.append(rule)
        return rules

    @staticmethod
    def _read_json(path: Path) -> Dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError):
            return {}

    @staticmethod
    def _derive_domain(path: Path) -> str:
        stem = path.stem.lower()
        if stem.startswith("identity"):
            return "identity"
        if stem.startswith("psychology"):
            return "psychology"
        if stem.startswith("relationships"):
            return "relationships"
        if stem.startswith("career"):
            return "career"
        if stem.startswith("karma"):
            return "karma"
        return "composite"

    @staticmethod
    def _normalize_output(output: Any) -> List[str]:
        if isinstance(output, dict):
            return list(output.get("composite_interpretation", []))
        if isinstance(output, list):
            return [str(entry) for entry in output]
        return []

    # ------------------------------------------------------------------
    # Structural signal derivation helpers
    # ------------------------------------------------------------------

    def _derive_structural_signals(
        self,
        sources: Sequence[str],
        placements: Sequence[str],
    ) -> Dict[str, Any]:
        houses = [self._extract_house(token) for token in sources]
        house_counts = Counter(self._extract_house(token) for token in placements if self._extract_house(token))
        main_house = next((house for house in houses if house is not None), None)
        if main_house is None and houses:
            main_house = houses[0]
        sign = next((self._extract_sign(token) for token in sources if self._extract_sign(token)), None)
        house_context = self._house_context(main_house)
        sign_style = self._sign_style(sign)
        cluster_intensity = self._cluster_intensity(main_house, house_counts)
        ruler_loop = self._ruler_loop(main_house, houses)
        contrast = self._inner_outer_contrast(houses)
        return {
            "house_context": house_context,
            "sign_style": sign_style,
            "cluster_intensity": cluster_intensity,
            "ruler_loop": ruler_loop,
            "inner_outer_contrast": contrast,
        }

    @staticmethod
    def _house_context(house: int | None) -> Dict[str, str]:
        if house is None:
            return DEFAULT_CONTEXT
        return HOUSE_CONTEXT.get(int(house), DEFAULT_CONTEXT)

    @staticmethod
    def _sign_style(sign: str | None) -> Dict[str, str]:
        normalized = normalize_sign(sign)
        base_style = SIGN_STYLE.get(normalized)
        if base_style:
            return apply_style_modifiers(base_style, {})
        element = get_element_for_sign(sign)
        fallback_style = ELEMENT_FALLBACK.get(element or "", DEFAULT_STYLE)
        return apply_style_modifiers(fallback_style, {})

    def _cluster_intensity(self, house: int | None, counts: Counter[int]) -> Dict[str, Any]:
        if house is None:
            return {"house": None, "level": "low", "continuous": False}
        count = counts.get(house, 0)
        level = "low"
        if count >= 4:
            level = "very_high"
        elif count >= 2:
            level = "high"
        return {"house": house, "level": level, "continuous": count >= 2}

    @staticmethod
    def _ruler_loop(house: int | None, houses: Sequence[int | None]) -> Dict[str, Any]:
        if house is None:
            return {"house": None, "active": False}
        occurrences = sum(1 for h in houses if h == house)
        return {"house": house, "active": occurrences > 1}

    @staticmethod
    def _inner_outer_contrast(houses: Sequence[int | None]) -> Dict[str, str | None]:
        inner = {4, 8, 12}
        outer = {1, 7, 10}
        inner_hit = next((h for h in houses if h in inner), None)
        outer_hit = next((h for h in houses if h in outer), None)
        mapping = {
            4: "internal_foundational",
            8: "shared_intense",
            12: "private_reflective",
            1: "direct_present",
            7: "relational_mirrored",
            10: "visible_performative",
        }
        return {
            "inner": mapping.get(inner_hit, "neutral_inner"),
            "outer": mapping.get(outer_hit, "neutral_outer"),
        }

    @staticmethod
    def _extract_house(token: str) -> int | None:
        match = re.search(r"_in_(\d+)(?:st|nd|rd|th)_house", token)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None

    @staticmethod
    def _extract_sign(token: str) -> str | None:
        if "_in_" in token:
            parts = token.split("_in_", 1)[1]
            if "_house" in parts:
                parts = parts.split("_house", 1)[0]
            return parts.strip().lower()
        return None
