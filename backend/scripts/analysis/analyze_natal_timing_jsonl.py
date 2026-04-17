"""Analyze natal timing JSONL logs and print stage-level latency summary."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(0, min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1))
    return ordered[rank]


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log-path",
        default="/tmp/natal_timings.jsonl",
        help="Path to natal timing JSONL log file.",
    )
    args = parser.parse_args()

    log_path = Path(args.log_path)
    if not log_path.exists():
        raise SystemExit(f"Log file not found: {log_path}")

    stage_durations: dict[str, list[float]] = defaultdict(list)
    total_lines = 0
    invalid_lines = 0

    with log_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            total_lines += 1
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                invalid_lines += 1
                continue
            if payload.get("type") != "natal_stage_timing":
                continue
            stage = str(payload.get("stage") or "").strip()
            duration = payload.get("duration_ms")
            if not stage or not isinstance(duration, (int, float)):
                continue
            stage_durations[stage].append(float(duration))

    if not stage_durations:
        print("No natal_stage_timing records found.")
        print(f"total_lines={total_lines} invalid_lines={invalid_lines}")
        return

    rows = []
    for stage, values in stage_durations.items():
        avg_ms = mean(values)
        p95_ms = _p95(values)
        max_ms = max(values)
        count = len(values)
        ratio = (p95_ms / avg_ms) if avg_ms > 0 else float("inf")
        stability = "stable" if ratio <= 1.5 else "spiky"
        rows.append((stage, avg_ms, p95_ms, max_ms, count, stability))

    rows.sort(key=lambda item: (-item[1], -item[2], item[0]))

    print("| stage | avg_ms | p95 | max | count |")
    print("|---|---:|---:|---:|---:|")
    for stage, avg_ms, p95_ms, max_ms, count, _ in rows:
        print(f"| {stage} | {_fmt(avg_ms)} | {_fmt(p95_ms)} | {_fmt(max_ms)} | {count} |")

    stable = [stage for stage, *_rest, stability in rows if stability == "stable"]
    spiky = [stage for stage, *_rest, stability in rows if stability == "spiky"]
    top3 = [stage for stage, *_ in rows[:3]]

    print("")
    print(f"stable_stages: {', '.join(stable) if stable else '-'}")
    print(f"spiky_stages: {', '.join(spiky) if spiky else '-'}")
    print(f"top3_by_avg: {', '.join(top3) if top3 else '-'}")
    print(f"total_lines={total_lines} invalid_lines={invalid_lines}")


if __name__ == "__main__":
    main()
