from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


def _collect_items(payload: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if "salience_breakdown" in value:
                items.append(value)
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for entry in value:
                walk(entry)

    walk(payload)
    return items


def _rank(values: list[float]) -> list[float]:
    sorted_pairs = sorted((val, idx) for idx, val in enumerate(values))
    ranks = [0.0] * len(values)
    i = 0
    while i < len(sorted_pairs):
        j = i
        while j < len(sorted_pairs) and sorted_pairs[j][0] == sorted_pairs[i][0]:
            j += 1
        avg_rank = (i + j - 1) / 2.0 + 1.0
        for _, idx in sorted_pairs[i:j]:
            ranks[idx] = avg_rank
        i = j
    return ranks


def _pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 2:
        return None
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    num = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    den_x = sum((a - mean_x) ** 2 for a in x)
    den_y = sum((b - mean_y) ** 2 for b in y)
    if den_x <= 0 or den_y <= 0:
        return None
    return num / (den_x**0.5 * den_y**0.5)


def _spearman(x: list[float], y: list[float]) -> float | None:
    if len(x) < 2:
        return None
    rx = _rank(x)
    ry = _rank(y)
    return _pearson(rx, ry)


def _group_metrics(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, float | None]]:
    x = [float(rec.get("dominance", 0.0)) for rec in records]
    y = [float(rec.get("axis_weight_raw", rec.get("axis_weight", 0.0))) for rec in records]
    return {
        "spearman": _spearman(x, y),
        "pearson": _pearson(x, y),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to JSON payload containing salience_breakdown.")
    parser.add_argument("--output", help="Optional output JSON path.")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    items = _collect_items(payload)

    records: list[dict[str, Any]] = []
    for item in items:
        breakdown = item.get("salience_breakdown") or {}
        records.append(
            {
                "domain": item.get("domain"),
                "slot": item.get("slot"),
                "dominance": breakdown.get("dominance", 0.0),
                "axis_weight_raw": breakdown.get("axis_weight_raw", breakdown.get("axis_weight", 0.0)),
            }
        )

    report: dict[str, Any] = {"global": _group_metrics(records), "by_domain": {}, "by_slot": {}}

    domains = sorted({rec.get("domain") for rec in records if rec.get("domain")})
    for domain in domains:
        subset = [rec for rec in records if rec.get("domain") == domain]
        report["by_domain"][domain] = _group_metrics(subset)

    slots = sorted({rec.get("slot") for rec in records if rec.get("slot")})
    for slot in slots:
        subset = [rec for rec in records if rec.get("slot") == slot]
        report["by_slot"][slot] = _group_metrics(subset)

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
