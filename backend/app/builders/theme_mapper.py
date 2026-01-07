"""Deterministic theme mapper that follows the V2.2 resolution flow."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

DEFAULT_MAPPING_PATH = (
    Path(__file__).resolve().parents[3] / "config" / "ontology" / "mapping.yaml"
)

logger = logging.getLogger(__name__)
_RESOLUTION_FAILURE_THRESHOLD = 0.2


class ThemeResolutionError(Exception):
    """Raised when the theme mapper fails to resolve a deterministic theme."""


class ThemeMapper:
    """Implements the multi-stage theme resolution flow described in V2.2."""

    _resolution_attempts = 0
    _resolution_failures = 0

    def __init__(self, mapping_path: Path | None = None):
        self.mapping = self._load_mapping(mapping_path or DEFAULT_MAPPING_PATH)
        self.fallback_runs = 0

    def map_signals(
        self,
        chart_hash: str,
        signals: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        signal_list = list(signals)
        signal_count = len(signal_list)
        try:
            candidates = self._stage1_candidate_generation(signal_list)
            if not candidates:
                raise ThemeResolutionError("No theme candidates could be generated.")
            candidates = self._stage2_contextual_modifiers(candidates)
            resolved = self._stage3_resolve(candidates, chart_hash)
            if resolved and self._should_force_weak_fallback(resolved):
                resolved = None
            if not resolved:
                resolved = self._stage4_weak_fallback(chart_hash, candidates)
            if not resolved:
                raise ThemeResolutionError("Unable to resolve a theme after fallback.")
        except ThemeResolutionError:
            self._log_resolution_event(False, chart_hash, signal_count)
            raise
        else:
            self._log_resolution_event(True, chart_hash, signal_count, resolved)
            return resolved

    def _load_mapping(self, mapping_path: Path) -> Mapping[str, Any]:
        if not mapping_path.exists():
            raise FileNotFoundError(f"Theme mapping file not found at {mapping_path}")
        text = mapping_path.read_text(encoding="utf-8")
        parsed = None
        try:
            parsed = yaml.safe_load(text)
        except yaml.YAMLError:
            parsed = None
        if isinstance(parsed, Mapping):
            if "candidates" in parsed and "rules" not in parsed:
                return self._normalize_mapping(parsed)
            if self._looks_like_mapping(parsed):
                return parsed
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = self._decode_embedded_json(text)
        if isinstance(parsed, str):
            parsed = self._decode_embedded_json(parsed)
        if isinstance(parsed, str):
            parsed = self._decode_embedded_json(parsed)
        if isinstance(parsed, Mapping):
            if "candidates" in parsed and "rules" not in parsed:
                return self._normalize_mapping(parsed)
            if self._looks_like_mapping(parsed):
                return parsed
        raise ValueError("Theme mapping payload could not be parsed.")

    @staticmethod
    def _looks_like_mapping(parsed: Mapping[str, Any]) -> bool:
        if "rules" in parsed:
            return True
        return any(
            key in parsed
            for key in ("candidate_generation", "tie_breaker", "weak_fallback", "settings")
        )

    @staticmethod
    def _decode_embedded_json(text: str) -> str | Mapping[str, Any] | None:
        cleaned = text.strip()
        if cleaned.startswith('"'):
            cleaned = cleaned[1:]
        if cleaned.endswith('"'):
            cleaned = cleaned[:-1]
        cleaned = cleaned.replace('\\"', '"')
        cleaned = cleaned.replace("\\n", "\n")
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _normalize_mapping(parsed: Mapping[str, Any]) -> Mapping[str, Any]:
        settings = parsed.get("settings") or {}
        max_candidates = int(settings.get("max_candidates", 3))
        weak_threshold = float(settings.get("weak_mapping_threshold", 0.25))
        weak_candidates = (parsed.get("weak_mapping") or {}).get("candidates") or []
        fallback_theme = ""
        if weak_candidates:
            fallback_theme = str(weak_candidates[0].get("theme") or "")
        rules: list[Mapping[str, Any]] = []
        for entry in parsed.get("candidates") or []:
            condition = entry.get("if") or {}
            normalized_condition: dict[str, Any] = {}
            aspect_cluster = condition.get("aspect_cluster")
            if isinstance(aspect_cluster, Mapping):
                if aspect_cluster.get("type"):
                    normalized_condition["aspect_type"] = aspect_cluster.get("type")
                if aspect_cluster.get("involves"):
                    normalized_condition["involves"] = aspect_cluster.get("involves")
            for key in ("axis", "house_group", "house", "dispositor_loop"):
                if key in condition:
                    normalized_condition[key] = condition.get(key)
            if not normalized_condition:
                continue
            candidates = (entry.get("then") or {}).get("candidates") or []
            for candidate in candidates:
                theme = candidate.get("theme")
                priority = float(candidate.get("base", 0.0))
                if not theme:
                    continue
                rules.append(
                    {"if": normalized_condition, "then": {"theme": theme, "priority": priority}}
                )
        return {
            "candidate_generation": {"max_candidates": max_candidates},
            "rules": rules,
            "contextual_modifiers": {},
            "tie_breaker": {"fallback": "signal_score"},
            "weak_fallback": {
                "base_threshold": weak_threshold,
                "fallback_theme": fallback_theme,
                "max_runs": int((parsed.get("weak_mapping") or {}).get("max_usage_per_chart", 1)),
            },
        }

    def _stage1_candidate_generation(
        self,
        signals: Sequence[Mapping[str, Any]],
    ) -> list[Mapping[str, Any]]:
        limit = self.mapping.get("candidate_generation", {}).get("max_candidates", 3)
        rules = self.mapping.get("rules", [])
        candidates: list[Mapping[str, Any]] = []
        for signal in sorted(signals, key=lambda item: float(item.get("signal_score", 0)), reverse=True):
            rule_match = self._match_rule(signal, rules)
            if not rule_match:
                continue
            theme, priority = rule_match
            candidates.append(
                {
                    "theme": theme,
                    "base_score": float(signal.get("signal_score", 0)),
                    "rule_priority": float(priority),
                    "axis": signal.get("axis_candidates", []),
                    "focus_object": signal.get("focus_object"),
                    "signal": signal,
                }
            )
            if len(candidates) >= limit:
                break
        return candidates

    def _match_rule(
        self,
        signal: Mapping[str, Any],
        rules: Sequence[Mapping[str, Any]],
    ) -> tuple[str, float] | None:
        best: tuple[str, float] | None = None
        for rule in rules:
            condition = rule.get("if", {})
            if self._matches_condition(signal, condition):
                outcome = rule.get("then", {})
                theme = outcome.get("theme")
                priority = float(outcome.get("priority", 0))
                if theme and (best is None or priority > best[1]):
                    best = (theme, priority)
        return best

    def _matches_condition(self, signal: Mapping[str, Any], condition: Mapping[str, Any]) -> bool:
        for key, expected in condition.items():
            if key == "aspect_type":
                if str(signal.get("aspect_type", "")).lower() != str(expected).lower():
                    return False
            elif key == "involves":
                involved = [
                    str(item).lower()
                    for item in signal.get("involves", signal.get("planets_involved", []) or [])
                ]
                if not any(str(val).lower() in involved for val in expected):
                    return False
            elif key == "house_group":
                if str(signal.get("house_group", "")).lower() != str(expected).lower():
                    return False
            elif key == "house":
                if int(signal.get("house", -1)) != int(expected):
                    return False
            elif key == "axis":
                axes = signal.get("axis_candidates") or []
                if not any(ax in expected for ax in axes):
                    return False
            elif key == "dispositor_loop":
                if bool(signal.get("dispositor_loop")) != bool(expected):
                    return False
        return True

    def _stage2_contextual_modifiers(
        self,
        candidates: Sequence[Mapping[str, Any]],
    ) -> list[Mapping[str, Any]]:
        modifiers = self.mapping.get("contextual_modifiers", {})
        axis_cfg = modifiers.get("axis", {})
        object_cfg = modifiers.get("object_importance", {})
        life_cfg = modifiers.get("life_stage", {})

        def _calc_bonus(candidate: Mapping[str, Any]) -> float:
            axis_bonus = axis_cfg.get("primary_axis_bonus", 0) if candidate.get("axis") else axis_cfg.get("secondary_axis_bonus", 0)
            focus_bonus = object_cfg.get("focus_object_bonus", 0) if candidate["signal"].get("focus_object") else 0
            tags = candidate["signal"].get("trigger_tags", [])
            importance = object_cfg.get("trigger_tag_bonus", 0) if tags else 0
            stage = candidate["signal"].get("life_stage")
            life_bonus = life_cfg.get(stage, 0)
            return axis_bonus + focus_bonus + importance + life_bonus

        enriched = []
        for candidate in candidates:
            bonus = _calc_bonus(candidate)
            candidate_score = candidate["base_score"] + bonus + candidate["rule_priority"]
            enriched.append({**candidate, "score": candidate_score})
        return enriched

    def _stage3_resolve(
        self,
        candidates: Sequence[Mapping[str, Any]],
        chart_hash: str,
    ) -> Mapping[str, Any] | None:
        if not candidates:
            return None
        best_score = max(candidate["score"] for candidate in candidates)
        tied = [c for c in candidates if c["score"] == best_score]
        if len(tied) == 1:
            return tied[0]
        tie_config = self.mapping.get("tie_breaker", {})
        priority_candidates = tied
        if tie_config.get("rule") == "highest_priority":
            highest = max(entry["rule_priority"] for entry in priority_candidates)
            priority_candidates = [entry for entry in priority_candidates if entry["rule_priority"] == highest]
        fallback = tie_config.get("fallback")
        if fallback == "signal_score" and priority_candidates:
            priority_candidates = sorted(priority_candidates, key=lambda entry: entry["base_score"], reverse=True)
        if priority_candidates:
            return priority_candidates[0]
        sorted_tied = sorted(
            tied,
            key=lambda entry: hashlib.sha256(f"{chart_hash}-{entry['theme']}".encode("utf-8")).hexdigest(),
        )
        return sorted_tied[0]

    def _stage4_weak_fallback(
        self,
        chart_hash: str,
        candidates: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, Any] | None:
        fallback_cfg = self.mapping.get("weak_fallback", {})
        if self.fallback_runs >= fallback_cfg.get("max_runs", 1):
            return None
        threshold = fallback_cfg.get("base_threshold", 0.25)
        fallback_theme = fallback_cfg.get("fallback_theme")
        best_candidate = max(candidates, key=lambda entry: entry["score"], default=None)
        if not best_candidate or not fallback_theme:
            return None
        if best_candidate["base_score"] <= threshold:
            self.fallback_runs += 1
            return {
                "theme": fallback_theme,
                "base_score": best_candidate["base_score"],
                "score": threshold,
                "resolved_from": "weak_fallback",
            }
        return None

    def _should_force_weak_fallback(self, resolved: Mapping[str, Any]) -> bool:
        weak_cfg = self.mapping.get("weak_fallback") or {}
        threshold = weak_cfg.get("base_threshold")
        if threshold is None:
            return False
        try:
            base_score = float(resolved.get("base_score", 0.0))
            return base_score <= float(threshold)
        except (TypeError, ValueError):
            return False

    def _log_resolution_event(
        self,
        resolved: bool,
        chart_hash: str,
        signal_count: int,
        resolved_metadata: Mapping[str, Any] | None = None,
    ) -> None:
        attempts, failures, ratio = type(self)._update_resolution_stats(resolved)
        resolved_source = (
            resolved_metadata.get("resolved_from") if resolved_metadata else "none"
        )
        payload = {
            "chart_hash": chart_hash,
            "resolved_theme": resolved,
            "signal_count": signal_count,
            "resolved_source": resolved_source,
            "resolution_failure_ratio": ratio,
            "resolution_attempts": attempts,
            "resolution_failures": failures,
        }
        logger.info("Theme mapping resolution event", extra=payload)
        if ratio >= _RESOLUTION_FAILURE_THRESHOLD:
            logger.warning(
                "Theme mapping failure ratio crossed threshold; rules may not match runtime inputs",
                extra=payload,
            )

    @classmethod
    def _update_resolution_stats(cls, resolved: bool) -> tuple[int, int, float]:
        cls._resolution_attempts += 1
        if not resolved:
            cls._resolution_failures += 1
        ratio = cls._resolution_failures / cls._resolution_attempts
        return cls._resolution_attempts, cls._resolution_failures, ratio
