"""Transit ranking benchmark — before/after aspect configurations.

Produces a reproducible comparison between two orb/aspect configurations on the
same natal chart across a fixed set of transit dates. Used to validate scoring
PRs (PR1, PR6, etc.) with concrete numbers: volume delta, top-N retention,
per-type breakdown, and a per-date top-10 diff.

Usage:
    PYTHONPATH=backend python backend/scripts/bench_transit_ranking.py
    PYTHONPATH=backend python backend/scripts/bench_transit_ranking.py --json > out.json

Configurations are intentionally kept inline: this is a PR gate, not a
general-purpose tool. Change CONFIG_A / CONFIG_B at the top of the file to
match whichever two states you want to compare, then run before and after your
change to capture the delta.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
EPHE_DIR = BACKEND_ROOT / "ephe"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("SUPABASE_URL", "https://bench.local")
os.environ.setdefault("SUPABASE_KEY", "bench")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "bench")

import swisseph  # noqa: E402

swisseph.set_ephe_path(str(EPHE_DIR))

from app.engine.transit_engine import build_transit_report  # noqa: E402


BIRTH = dict(
    birth_date="1996-12-28",
    birth_time="07:10",
    birth_place="Istanbul",
    birth_latitude=41.0082,
    birth_longitude=28.9784,
    birth_timezone="Europe/Istanbul",
)

TRANSIT_DATES = [
    "2026-02-01",
    "2026-03-04",
    "2026-05-15",
    "2026-08-21",
    "2026-11-10",
]

CONFIG_A = {
    "label": "OLD (pre-PR1, no OOS filter)",
    "orbs": {"conjunction": 6.0, "opposition": 6.0, "square": 6.0, "trine": 6.0, "sextile": 4.0},
    "aspect_types": ["conjunction", "opposition", "square", "trine", "sextile"],
    "apply_out_of_sign_filter": False,
}

CONFIG_B = {
    "label": "NEW (post-PR1+PR3)",
    "orbs": {
        "conjunction": 4.0, "opposition": 4.0, "square": 3.5, "trine": 3.0,
        "sextile": 2.5, "quincunx": 2.0, "semisextile": 1.5,
    },
    "aspect_types": [
        "conjunction", "opposition", "square", "trine", "sextile",
        "quincunx", "semisextile",
    ],
    "apply_out_of_sign_filter": True,
}


def _run(config: Dict[str, Any], transit_date: str) -> Dict[str, Any]:
    return build_transit_report(
        transit_date=transit_date,
        transit_time="12:00",
        transit_place="Istanbul",
        transit_latitude=41.0082,
        transit_longitude=28.9784,
        transit_timezone="Europe/Istanbul",
        options={
            "orbs": config["orbs"],
            "aspect_types": config["aspect_types"],
            "include_angles": True,
            "max_aspects_per_transit_body": 99,
            "apply_out_of_sign_filter": config.get("apply_out_of_sign_filter", True),
        },
        assumptions=[],
        **BIRTH,
    )


def _all_aspects(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    asp = report.get("aspects", {}) or {}
    return list(asp.get("transit_to_natal", []) or []) + list(asp.get("transit_to_angles", []) or [])


def _sig(aspect: Dict[str, Any]) -> str:
    tbody = (aspect.get("transit") or {}).get("body") or "?"
    natal = aspect.get("natal") or {}
    target = natal.get("body") or natal.get("angle") or natal.get("point") or "?"
    return f"{tbody}-{aspect.get('type')}-{target}"


def _sort_by_strength(aspects: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(aspects, key=lambda a: -float(a.get("strength") or 0.0))


def _per_type_counts(aspects: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for a in aspects:
        t = str(a.get("type") or "")
        out[t] = out.get(t, 0) + 1
    return out


def run(as_json: bool = False) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    per_type_a: Dict[str, int] = {}
    per_type_b: Dict[str, int] = {}
    top10_details: Dict[str, Any] = {}

    for td in TRANSIT_DATES:
        a_aspects = _sort_by_strength(_all_aspects(_run(CONFIG_A, td)))
        b_aspects = _sort_by_strength(_all_aspects(_run(CONFIG_B, td)))

        for a in a_aspects:
            per_type_a[a["type"]] = per_type_a.get(a["type"], 0) + 1
        for b in b_aspects:
            per_type_b[b["type"]] = per_type_b.get(b["type"], 0) + 1

        top5_a = {_sig(x) for x in a_aspects[:5]}
        top5_b = {_sig(x) for x in b_aspects[:5]}
        top10_a = {_sig(x) for x in a_aspects[:10]}
        top10_b = {_sig(x) for x in b_aspects[:10]}

        rows.append({
            "date": td,
            "count_a": len(a_aspects),
            "count_b": len(b_aspects),
            "delta_pct": 100.0 * (len(b_aspects) - len(a_aspects)) / max(len(a_aspects), 1),
            "top5_kept": len(top5_a & top5_b),
            "top10_kept": len(top10_a & top10_b),
            "oos_b": sum(1 for x in b_aspects if x.get("out_of_sign")),
        })

        top10_details[td] = {
            "a_top10": [{"sig": _sig(x), "strength": x.get("strength"), "orb": x.get("orb")} for x in a_aspects[:10]],
            "b_top10": [{"sig": _sig(x), "strength": x.get("strength"), "orb": x.get("orb")} for x in b_aspects[:10]],
        }

    summary = {
        "label_a": CONFIG_A["label"],
        "label_b": CONFIG_B["label"],
        "dates": TRANSIT_DATES,
        "rows": rows,
        "mean_count_a": statistics.mean(r["count_a"] for r in rows),
        "mean_count_b": statistics.mean(r["count_b"] for r in rows),
        "mean_delta_pct": statistics.mean(r["delta_pct"] for r in rows),
        "mean_top5_kept": statistics.mean(r["top5_kept"] for r in rows),
        "mean_top10_kept": statistics.mean(r["top10_kept"] for r in rows),
        "per_type_a": per_type_a,
        "per_type_b": per_type_b,
        "top10_details": top10_details,
    }

    if as_json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return summary

    print(f"\n=== Transit ranking benchmark: {CONFIG_A['label']} vs {CONFIG_B['label']} ===")
    print(f"Natal: {BIRTH['birth_date']} {BIRTH['birth_time']} {BIRTH['birth_place']}")
    print(f"Dates: {', '.join(TRANSIT_DATES)}\n")

    print(f"{'date':<12} {'count_a':>8} {'count_b':>8} {'delta%':>8} {'top5':>6} {'top10':>6} {'oos_b':>6}")
    print("-" * 66)
    for r in rows:
        print(f"{r['date']:<12} {r['count_a']:>8} {r['count_b']:>8} {r['delta_pct']:>+7.1f}% "
              f"{r['top5_kept']:>3}/5  {r['top10_kept']:>3}/10 {r['oos_b']:>6}")
    print("-" * 66)
    print(f"{'MEAN':<12} {summary['mean_count_a']:>8.1f} {summary['mean_count_b']:>8.1f} "
          f"{summary['mean_delta_pct']:>+7.1f}% "
          f"{summary['mean_top5_kept']:>3.1f}/5  {summary['mean_top10_kept']:>3.1f}/10")

    print(f"\n=== Per-aspect-type breakdown (sum across {len(TRANSIT_DATES)} dates) ===")
    print(f"{'type':<14} {'count_a':>8} {'count_b':>8}")
    for t in sorted(set(per_type_a) | set(per_type_b)):
        print(f"{t:<14} {per_type_a.get(t, 0):>8} {per_type_b.get(t, 0):>8}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()
    run(as_json=args.json)


if __name__ == "__main__":
    main()
