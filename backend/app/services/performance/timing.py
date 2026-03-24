"""Lightweight timing helper for structured stage logs."""
from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter


class TimingRecorder:
    def __init__(self) -> None:
        self._started_at = perf_counter()
        self.stage_breakdown_ms: dict[str, float] = {}

    @contextmanager
    def stage(self, name: str):
        started = perf_counter()
        try:
            yield
        finally:
            self.stage_breakdown_ms[name] = round((perf_counter() - started) * 1000.0, 3)

    def total_ms(self) -> float:
        return round((perf_counter() - self._started_at) * 1000.0, 3)
