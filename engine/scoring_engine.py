"""Scoring engine that calculates deterministic weights for chart signals."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

CONFIG_PATH = (
    Path(__file__).resolve().parents[1] / "config" / "scoring" / "weights.yaml"
)


class ScoringEngine:
    def __init__(self, variant: str = "simple", config_path: Path | None = None):
        path = config_path or CONFIG_PATH
        if not path.exists():
            raise FileNotFoundError(f"Scoring config not found at {path}")
        self.config = json.loads(path.read_text())
        self.variant = variant

    def base_score(self, signal: Mapping[str, object]) -> float:
        config = self.config["model_variants"][self.variant]
        planet_class = str(signal.get("planet_class", "personal"))
        aspect_type = str(signal.get("aspect_type", "hard"))
        orb = float(signal.get("orb", 6))
        planet_weight = config["planet_class_weights"].get(planet_class, 0.5)
        aspect_weight = config["aspect_weights"].get(aspect_type, 0.5)
        orb_weight = self._orb_curve_weight(config["orb_curve"], orb)
        base = float(signal.get("signal_score", 0.0))
        dominance_bonus = self._dominance_bonus(signal, config.get("dominance_bonus", {}))
        object_bonus = self._object_importance_bonus(signal, self.config.get("object_weights", {}))
        return (base * planet_weight * aspect_weight * orb_weight) + dominance_bonus + object_bonus

    def signal_score(self, signal: Mapping[str, object]) -> Mapping[str, object]:
        base = self.base_score(signal)
        multiplier = self._salience_multiplier(signal)
        experienced_weight = max(base * multiplier, 0.05)
        return {
            "signal_id": signal.get("signal_id"),
            "base_score": base,
            "experienced_weight": experienced_weight,
            "salience_multiplier": multiplier,
        }

    def _orb_curve_weight(self, curve: list[Mapping[str, float]], orb: float) -> float:
        for point in curve:
            if orb <= point["max_orb"]:
                return float(point["weight"])
        return float(curve[-1]["weight"])

    def _dominance_bonus(self, signal: Mapping[str, object], dominance_cfg: Mapping[str, float]) -> float:
        bonus = 0.0
        if signal.get("stellar_density"):
            bonus += dominance_cfg.get("stellium", 0)
        if signal.get("angular_density"):
            bonus += dominance_cfg.get("angular_density", 0)
        if signal.get("dispositor_loop"):
            bonus += dominance_cfg.get("dispositor_chain", 0)
        return bonus

    def _object_importance_bonus(
        self,
        signal: Mapping[str, object],
        object_cfg: Mapping[str, object],
    ) -> float:
        bonus = 0.0
        if signal.get("is_chart_ruler"):
            bonus += object_cfg.get("chart_ruler_bonus", 0)
        angle = str(signal.get("angle_contact", "")).lower()
        angle_cfg = object_cfg.get("angle_contact_bonus", {})
        if angle in angle_cfg:
            bonus += float(angle_cfg.get(angle, 0))
        if signal.get("stellium_core"):
            bonus += object_cfg.get("stellium_core_bonus", 0)
        if signal.get("axis_activation"):
            bonus += object_cfg.get("axis_activation_bonus", 0)
        return bonus

    def _salience_multiplier(self, signal: Mapping[str, object]) -> float:
        tags = signal.get("trigger_tags", [])
        multipliers = self.config.get("salience_multipliers", {})
        if "high" in tags:
            return multipliers.get("trigger_tag_high", 1.0)
        if "medium" in tags:
            return multipliers.get("trigger_tag_medium", 1.0)
        if "low" in tags:
            return multipliers.get("trigger_tag_low", 1.0)
        return 1.0
