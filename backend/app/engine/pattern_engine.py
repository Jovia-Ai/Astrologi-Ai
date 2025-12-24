from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, Mapping, Sequence

import re

from app.helpers.meta_detectors import normalize_node_alias, normalize_planet_key


class PatternEmphasisEngine:
    """
    Scores composite rules based on emphasis signals.
    This engine only attaches metadata; it never rewrites any text.
    """

    def build(
        self,
        composites: Sequence[Dict[str, Any]],
        *,
        placements: Sequence[str],
        core_aspects: Sequence[str],
        meta_info: Mapping[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        emphasis: Dict[str, Dict[str, Any]] = {}
        dominance = self._derive_dominance(meta_info)
        ruler_flow = "active" if meta_info.get("house_clusters") else "calm"
        base_planet_load = self._build_base_planet_load(placements, core_aspects)
        house_clusters = meta_info.get("house_clusters", {})

        for composite in composites:
            comp_id = composite.get("composite_id")
            if not comp_id:
                continue
            sources = composite.get("sources", [])
            planet_counts = self._count_planet_contexts(sources)
            aspect_weight = sum(1 for source in sources if source in core_aspects)
            stellium_flag = self._has_stellium(sources, house_clusters)
            bonus = 0.06 if stellium_flag else 0.0
            priority = self._calculate_priority(len(sources), len(planet_counts), aspect_weight) + bonus
            emphasis[comp_id] = {
                "planet_load": planet_counts or base_planet_load,
                "dominance": dominance,
                "ruler_flow": ruler_flow,
                "aspect_weight": aspect_weight,
                "priority_score": round(priority, 3),
                "stellium": stellium_flag,
            }
        return emphasis

    @staticmethod
    def _derive_dominance(meta_info: Mapping[str, Any]) -> str | None:
        dominant_elements = meta_info.get("dominant_elements") or {}
        dominant_modalities = meta_info.get("dominant_modalities") or {}
        if dominant_elements:
            element = next(iter(dominant_elements))
            return f"element:{element}"
        if dominant_modalities:
            modality = next(iter(dominant_modalities))
            return f"modality:{modality}"
        return None

    @staticmethod
    def _calculate_priority(source_count: int, planet_count: int, aspect_weight: int) -> float:
        base = min(0.95, 0.3 + (source_count * 0.12) + (aspect_weight * 0.08))
        modifier = min(1.0, 0.1 * planet_count)
        return min(1.0, base + modifier)

    @staticmethod
    def _build_base_planet_load(
        placements: Sequence[str],
        core_aspects: Sequence[str],
    ) -> Dict[str, int]:
        counts: Counter[str] = Counter()
        for placement in placements:
            planet = placement.split("_in_", 1)[0]
            if planet:
                counts[planet] += 1
        for aspect in core_aspects:
            parts = aspect.split("_")
            if len(parts) >= 3:
                counts[parts[0]] += 1
                counts[parts[2]] += 1
        return dict(counts)

    @staticmethod
    def _count_planet_contexts(contexts: Iterable[str]) -> Dict[str, int]:
        counts: Counter[str] = Counter()
        for context in contexts:
            planets = PatternEmphasisEngine._extract_planets(context)
            for planet in planets:
                normalized = normalize_node_alias(normalize_planet_key(planet))
                if normalized:
                    counts[normalized] += 1
        return dict(counts)

    @staticmethod
    def _extract_planets(context: str) -> Sequence[str]:
        if "_in_" in context:
            return [context.split("_in_", 1)[0]]
        parts = context.split("_")
        if len(parts) >= 3:
            return [parts[0], parts[-1]]
        if parts:
            return [parts[0]]
        return []

    @staticmethod
    def _has_stellium(sources: Iterable[str], house_clusters: Mapping[int, int]) -> bool:
        if not house_clusters:
            return False
        for source in sources:
            house = PatternEmphasisEngine._extract_house(source)
            if house and house_clusters.get(house, 0) >= 3:
                return True
        return False

    @staticmethod
    def _extract_house(token: str) -> int | None:
        if not token:
            return None
        match = re.search(r"_in_(?P<num>\d+)(?:st|nd|rd|th)_house", token)
        if match:
            try:
                return int(match.group("num"))
            except ValueError:
                return None
        return None
