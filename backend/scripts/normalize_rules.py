#!/usr/bin/env python3
"""Normalize and validate all astrology rule JSON files for the engine."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

RULES_DIR = Path(__file__).resolve().parents[1] / "app" / "data" / "rules"
CATEGORY_KEYS = ("identity", "psychology", "relationships", "mind", "career", "karma")
FRAGMENT_KEYS = ("cause", "mechanism", "effect", "shadow", "potential")
VALID_EXT = ".json"

SAMPLE_PLANET = {"planet": "Sun", "sign": "Capricorn", "house": 1}

logging.basicConfig(level=logging.INFO, format="%(message)s")


def normalize_planet_key(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "_")


def normalize_node_alias(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"north_node", "true_node", "mean_node", "node"}:
        return "node"
    if normalized in {"lilith", "black_moon_lilith"}:
        return "lilith"
    return normalized


def title_case(value: Any) -> str:
    if not value:
        return ""
    return str(value).strip().title()


def require_list(value: Any) -> List[Dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def normalize_rule(rule: Dict[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}
    rule_id = str(rule.get("id") or "").strip()
    conditions = require_list(rule.get("conditions"))
    normalized_conditions: List[Dict[str, Any]] = []
    for condition in conditions:
        planet_raw = condition.get("planet")
        planet = title_case(planet_raw)
        planet_key = normalize_node_alias(normalize_planet_key(planet))
        sign_raw = condition.get("sign")
        sign = title_case(sign_raw)
        condition_entry: Dict[str, Any] = {"planet": planet, "sign": sign}
        if "house" in condition:
            try:
                condition_entry["house"] = int(condition["house"])
            except (TypeError, ValueError):
                condition_entry["house"] = None
        normalized_conditions.append(condition_entry)
        if not rule_id and planet_key:
            if sign:
                rule_id = f"{planet_key}_in_{sign.lower()}"
            elif "house" in condition_entry and condition_entry["house"] is not None:
                rule_id = f"{planet_key}_in_house_{condition_entry['house']}"
    normalized["id"] = rule_id or "unnamed_rule"
    normalized["conditions"] = normalized_conditions or [{"planet": "", "sign": ""}]

    output = rule.get("output") or {}
    normalized_output: Dict[str, Dict[str, List[str]]] = {}
    for category in CATEGORY_KEYS:
        category_data = output.get(category) or {}
        normalized_category: Dict[str, List[str]] = {}
        for fragment in FRAGMENT_KEYS:
            entries = category_data.get(fragment)
            if isinstance(entries, str):
                fragment_list = [entries.strip()]
            elif isinstance(entries, Sequence) and not isinstance(entries, dict):
                fragment_list = [str(item).strip() for item in entries if str(item).strip()]
            else:
                fragment_list = []
            normalized_category[fragment] = fragment_list
        normalized_output[category] = normalized_category
    normalized["output"] = normalized_output
    return normalized


def extract_rules(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, dict):
        flat: List[Dict[str, Any]] = []
        for key in ("planet_sign_rules", "planet_house_rules", "aspect_rules", "meta_rules"):
            flat.extend(require_list(payload.get(key, [])))
        if flat:
            return flat
        return [payload]
    if isinstance(payload, list):
        return require_list(payload)
    return []


def rewrite_file(path: Path) -> Tuple[Path, List[str], List[Dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = extract_rules(data)
    normalized_rules = [normalize_rule(rule) for rule in rules]
    normalized_name = f"{re.sub(r'[^a-z0-9_]', '_', path.stem.lower())}{VALID_EXT}"
    normalized_path = path.with_name(normalized_name)
    target_path = normalized_path if normalized_path != path else path
    if normalized_path != path:
        path.rename(normalized_path)
    target_path.write_text(json.dumps(normalized_rules, ensure_ascii=False, indent=2), encoding="utf-8")
    rule_ids = [rule["id"] for rule in normalized_rules]
    return target_path, rule_ids, normalized_rules


def sample_matches(rule: Dict[str, Any], sample: Dict[str, Any]) -> bool:
    for condition in rule.get("conditions", []):
        if not condition.get("planet") or not condition.get("sign"):
            return False
        if condition["planet"].lower() != title_case(sample["planet"]).lower():
            return False
        if condition["sign"].lower() != title_case(sample["sign"]).lower():
            return False
        if "house" in condition and condition["house"] is not None:
            if int(condition["house"]) != sample["house"]:
                return False
    return True


def main() -> None:
    if not RULES_DIR.exists():
        raise SystemExit(f"Rules directory not found: {RULES_DIR}")
    processed: List[str] = []
    rewritten: List[str] = []
    matched_rules: List[str] = []
    for json_file in sorted(RULES_DIR.glob("*.json")):
        processed.append(str(json_file))
        try:
            target, rule_ids, normalized = rewrite_file(json_file)
            rewritten.append(str(target))
            for rule in normalized:
                if sample_matches(rule, SAMPLE_PLANET):
                    matched_rules.append(rule["id"])
        except Exception as exc:
            logging.error("Failed to normalize %s: %s", json_file, exc)
    logging.info("=== Validation Report ===")
    logging.info("Processed files: %s", processed)
    logging.info("Rewritten files: %s", rewritten)
    logging.info("Sample matches for Sun/Capricorn/house 1: %s", matched_rules)


if __name__ == "__main__":
    main()
