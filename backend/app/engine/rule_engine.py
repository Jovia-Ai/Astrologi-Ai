"""Rule engine that evaluates natal chart rules from JSON definitions."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Set, Tuple

from app.engine.meta_detectors import (
    analyze_planets,
    normalize_node_alias,
    normalize_planet_key,
)

TYPE_NAMES = ("cause", "mechanism", "effect", "shadow", "potential")
CATEGORIES = ("identity", "psychology", "relationships", "mind", "career", "karma")

logger = logging.getLogger(__name__)

class RuleEngine:
    """Loads planet/sign/house, aspect, and meta rules and evaluates them."""

    def __init__(self, rules_path: str | None = None) -> None:
        rules_dir = (
            Path(rules_path)
            if rules_path
            else Path(__file__).resolve().parents[1] / "data" / "rules"
        )

        all_sign_rules: List[Dict[str, Any]] = []
        all_house_rules: List[Dict[str, Any]] = []
        all_aspect_rules: List[Dict[str, Any]] = []
        all_meta_rules: List[Dict[str, Any]] = []

        if rules_dir.exists():
            for file in sorted(rules_dir.glob("*.json")):
                with file.open("r", encoding="utf-8") as handle:
                    payload = json.load(handle)
                all_sign_rules.extend(payload.get("planet_sign_rules", []))
                all_house_rules.extend(payload.get("planet_house_rules", []))
                all_aspect_rules.extend(payload.get("aspect_rules", []))
                all_meta_rules.extend(payload.get("meta_rules", []))

        self.planet_sign_rules = self._normalize_rule_list(all_sign_rules)
        self.planet_house_rules = self._normalize_rule_list(all_house_rules)
        self.aspect_rules = self._normalize_rule_list(all_aspect_rules)
        self.meta_rules = self._normalize_rule_list(all_meta_rules)
        print("RuleEngine initialized with", len(self.planet_sign_rules), "planet sign rules")
        self.interpretation: Dict[str, List[Dict[str, str]]] = {category: [] for category in CATEGORIES}

    def interpret(
        self,
        planets: List[Dict[str, Any]],
        aspects: List[Dict[str, Any]],
        *,
        return_meta: bool = False,
    ) -> Tuple[Dict[str, List[str]], Dict[str, Any]] | Dict[str, List[str]]:
        """
        Evaluate all rule types and return interpretations grouped by category.

        Returns (interpretation, meta_info) when return_meta=True; otherwise just interpretation.
        """

        logger.info("PLANETS INPUT: %s", planets)
        meta_info = analyze_planets(planets)
        meta_info["aspect_pairs"] = self._build_aspect_pairs(aspects)

        results: Dict[str, Dict[str, List[str]]] = {
            category: {type_name: [] for type_name in TYPE_NAMES}
            for category in CATEGORIES
        }

        for rule in self.planet_sign_rules:
            logger.info("CHECKING RULE: %s → conditions: %s", rule.get("id"), rule.get("conditions"))
            if self._conditions_met(rule.get("conditions"), meta_info, rule_id=rule.get("id")):
                self._append_output(results, rule.get("output"))
        for rule in self.planet_house_rules:
            logger.info("CHECKING RULE: %s → conditions: %s", rule.get("id"), rule.get("conditions"))
            if self._conditions_met(rule.get("conditions"), meta_info, rule_id=rule.get("id")):
                self._append_output(results, rule.get("output"))
        for rule in self.aspect_rules:
            logger.info("CHECKING RULE: %s → conditions: %s", rule.get("id"), rule.get("conditions"))
            if self._conditions_met(rule.get("conditions"), meta_info, rule_id=rule.get("id")):
                self._append_output(results, rule.get("output"))
        for rule in self.meta_rules:
            logger.info("CHECKING RULE: %s → conditions: %s", rule.get("id"), rule.get("conditions"))
            if self._conditions_met(rule.get("conditions"), meta_info, rule_id=rule.get("id")):
                self._append_output(results, rule.get("output"))

        self.interpretation = results

        if return_meta:
            return results, meta_info
        return results

    def get_sentence(self, category: str, type_name: str) -> str | None:
        bucket = self.interpretation.get(category, {})
        if not isinstance(bucket, Mapping):
            return None
        sentences = bucket.get(type_name)
        if isinstance(sentences, Sequence):
            for entry in sentences:
                if isinstance(entry, str) and entry.strip():
                    return entry.strip()
                if isinstance(entry, Mapping) and entry.get("text"):
                    return str(entry["text"]).strip()
        return None

    @staticmethod
    def _normalize_rule_list(value: Any) -> List[Dict[str, Any]]:
        if isinstance(value, list):
            return [entry for entry in value if isinstance(entry, dict)]
        return []

    @staticmethod
    def _build_aspect_pairs(aspects: Iterable[Mapping[str, Any]]) -> Set[Tuple[str, str, str]]:
        aspect_pairs: Set[Tuple[str, str, str]] = set()
        for aspect in aspects:
            planet1 = aspect.get("planet1") or aspect.get("planet") or ""
            planet2 = aspect.get("planet2") or aspect.get("target") or ""
            aspect_type = aspect.get("type") or aspect.get("aspect") or ""
            if not (planet1 and planet2 and aspect_type):
                continue
            key = (str(planet1).lower(), str(aspect_type).lower(), str(planet2).lower())
            aspect_pairs.add(key)
            aspect_pairs.add((key[2], key[1], key[0]))
        return aspect_pairs

    def _conditions_met(
        self,
        conditions: Any,
        meta_info: Mapping[str, Any],
        *,
        rule_id: str | None = None,
    ) -> bool:
        if not conditions:
            return True
        if not isinstance(conditions, Sequence):
            return False
        for condition in conditions:
            if not isinstance(condition, Mapping):
                return False
            if "planet" in condition:
                if not self._match_planet_condition(condition, meta_info, rule_id=rule_id):
                    return False
            elif "aspect" in condition or ("planet1" in condition and "planet2" in condition):
                if not self._match_aspect_condition(condition, meta_info):
                    return False
            elif "stellium" in condition:
                if not self._match_stellium_condition(condition["stellium"], meta_info):
                    return False
            elif "element_dominance" in condition:
                if not self._match_element_condition(condition["element_dominance"], meta_info):
                    return False
            elif "modality_dominance" in condition:
                if not self._match_modality_condition(condition["modality_dominance"], meta_info):
                    return False
            elif "house_focus" in condition:
                if not self._match_house_focus(condition["house_focus"], meta_info):
                    return False
            else:
                # Unknown condition type; treat as failure to avoid false positives.
                return False
        return True

    def _match_planet_condition(
        self,
        condition: Mapping[str, Any],
        meta_info: Mapping[str, Any],
        *,
        rule_id: str | None = None,
    ) -> bool:
        expected_planet = normalize_node_alias(normalize_planet_key(condition.get("planet")))
        if not expected_planet:
            return False

        planet_signs: Mapping[str, str] = meta_info.get("planet_signs", {})
        planet_houses: Mapping[str, Any] = meta_info.get("planet_houses", {})
        actual_sign = planet_signs.get(expected_planet)
        actual_house = planet_houses.get(expected_planet)

        expected_sign_raw = condition.get("sign", "")
        expected_sign = str(expected_sign_raw).lower().strip() if expected_sign_raw else ""
        expected_house: int | None = None
        if "house" in condition:
            try:
                expected_house = int(condition["house"])
            except (TypeError, ValueError):
                return False

        logger.info(
            "MATCH CHECK: planet=%s, expected=%s, actual=%s/%s, expected_sign=%s, expected_house=%s",
            expected_planet,
            condition.get("planet"),
            actual_sign,
            actual_house,
            expected_sign,
            expected_house,
        )

        if expected_sign:
            if not isinstance(actual_sign, str) or actual_sign.strip().lower() != expected_sign:
                return False

        if expected_house is not None:
            if actual_house is None or actual_house != expected_house:
                return False

        if rule_id:
            logger.info("✔ MATCHED RULE: %s", rule_id)
        return True

    def _match_aspect_condition(self, condition: Mapping[str, Any], meta_info: Mapping[str, Any]) -> bool:
        if "aspect" in condition and isinstance(condition["aspect"], Mapping):
            aspect_condition = condition["aspect"]
        else:
            aspect_condition = condition
        planet1 = str(aspect_condition.get("planet1") or aspect_condition.get("planet") or "").lower()
        planet2 = str(aspect_condition.get("planet2") or aspect_condition.get("target") or "").lower()
        aspect_type = str(aspect_condition.get("type") or "").lower()
        if not (planet1 and planet2 and aspect_type):
            return False
        return (planet1, aspect_type, planet2) in meta_info.get("aspect_pairs", set())

    def _match_stellium_condition(self, payload: Mapping[str, Any], meta_info: Mapping[str, Any]) -> bool:
        if not isinstance(payload, Mapping):
            return False
        house = payload.get("house")
        min_planets = int(payload.get("min_planets", 3))
        stelliums: Mapping[int, int] = meta_info.get("stelliums", {})
        if house is None:
            return False
        return stelliums.get(int(house), 0) >= min_planets

    def _match_element_condition(self, payload: Mapping[str, Any], meta_info: Mapping[str, Any]) -> bool:
        if not isinstance(payload, Mapping):
            return False
        element = payload.get("element")
        if not element:
            return False
        min_planets = int(payload.get("min_planets", 4))
        counts = meta_info.get("element_counts", {})
        return counts.get(str(element), 0) >= min_planets

    def _match_modality_condition(self, payload: Mapping[str, Any], meta_info: Mapping[str, Any]) -> bool:
        if not isinstance(payload, Mapping):
            return False
        modality = payload.get("modality")
        if not modality:
            return False
        min_planets = int(payload.get("min_planets", 4))
        counts = meta_info.get("modality_counts", {})
        return counts.get(str(modality), 0) >= min_planets

    def _match_house_focus(self, payload: Mapping[str, Any], meta_info: Mapping[str, Any]) -> bool:
        if not isinstance(payload, Mapping):
            return False
        houses = payload.get("houses")
        if not isinstance(houses, Sequence):
            return False
        min_planets = int(payload.get("min_planets", 3))
        house_counts: Mapping[int, int] = meta_info.get("house_counts", {})
        count = sum(house_counts.get(int(house), 0) for house in houses)
        return count >= min_planets

    def _append_output(self, results: MutableMapping[str, Dict[str, List[str]]], output: Any) -> None:
        """
        Merge rule output (tagged) into the global results dictionary.
        output structure:

        {
           "identity": { "cause": [...], "mechanism": [...], ... },
           "psychology": { ... },
           ...
        }
        """
        if not output:
            return

        if not isinstance(output, Mapping):
            return

        for category, tagged in output.items():
            if category not in results or not isinstance(tagged, Mapping):
                continue

            for type_name, sentences in tagged.items():
                bucket = results[category].get(type_name)
                if bucket is None:
                    continue
                normalized = self._normalize_fragments(sentences)
                bucket.extend(normalized)

    @staticmethod
    def _normalize_fragments(value: Any) -> List[str]:
        if isinstance(value, Mapping):
            fragments: List[str] = []
            for sub_value in value.values():
                fragments.extend(RuleEngine._normalize_fragments(sub_value))
            return fragments
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        if isinstance(value, Sequence):
            return [str(item).strip() for item in value if str(item).strip()]
        return []
