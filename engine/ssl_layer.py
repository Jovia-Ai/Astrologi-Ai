"""Signal Support Logic layer (SSL) that monitors quality without mutating scores."""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence


class SSLLayer:
    """SSL tracks repetition, life-stage alignment, and identity axis overlap."""

    def apply(
        self,
        signals: Sequence[Mapping[str, object]],
        chart_stage: str = "mid",
    ) -> list[Mapping[str, object]]:
        reports: list[Mapping[str, object]] = []
        seen_domains: set[str] = set()
        seen_axes: set[str] = set()
        for signal in signals:
            domain = signal.get("domain", "general")
            axis = signal.get("axis", "none")
            repetition_penalty = self._repetition_across_domains(domain, seen_domains)
            axis_overlap = self._identity_axis_overlap(axis, seen_axes)
            stage_alignment = self._life_stage_alignment(signal, chart_stage)
            seen_domains.add(domain)
            if axis != "none":
                seen_axes.add(axis)
            reports.append(
                {
                    "signal_id": signal.get("signal_id"),
                    "repetition_penalty": repetition_penalty,
                    "axis_overlap": axis_overlap,
                    "life_stage_alignment": stage_alignment,
                    "note": "SSL monitors but does not mutate experienced_weight",
                }
            )
        return reports

    def _repetition_across_domains(self, domain: str, seen: set[str]) -> float:
        if domain in seen:
            return 0.1
        return 0.0

    def _life_stage_alignment(self, signal: Mapping[str, object], stage: str) -> float:
        if signal.get("life_stage") == stage:
            return 0.0
        return 0.05

    def _identity_axis_overlap(self, axis: str, seen: set[str]) -> float:
        if axis in seen:
            return 0.08
        return 0.0
