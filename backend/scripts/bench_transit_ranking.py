"""Transit ranking benchmark — frozen OLD baseline vs live NEW engine.

CONFIG_A is not computed: it is read from frozen JSON artifacts under
`tests/_artifacts/bench_baseline_sprint1/`. Each artifact was produced by
`scripts/freeze_baseline.py` with pre-PR1 engine config (wide orbs, major
aspects only, no OOS filter, linear decay) and carries a SHA256 hash of its
canonicalized payload. This script verifies the hash on load; if the stored
hash doesn't match the current file, the run aborts — preventing silent
baseline drift.

CONFIG_B is computed live using the current engine + post-PR1 config. As the
engine evolves, OLD stays byte-for-byte stable while NEW advances, so the
delta accumulates the cumulative impact of all shipped PRs.

The bench runs over 3 fixtures (simple / angular_heavy / stellium), all
using the same 5 transit dates, and reports per-fixture + aggregate numbers.

Usage:
    PYTHONPATH=backend python backend/scripts/bench_transit_ranking.py
    PYTHONPATH=backend python backend/scripts/bench_transit_ranking.py --json > out.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
EPHE_DIR = BACKEND_ROOT / "ephe"
ARTIFACT_DIR = BACKEND_ROOT / "tests" / "_artifacts" / "bench_baseline_sprint1"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("SUPABASE_URL", "https://bench.local")
os.environ.setdefault("SUPABASE_KEY", "bench")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "bench")

import swisseph  # noqa: E402

swisseph.set_ephe_path(str(EPHE_DIR))

from app.engine.transit_engine import build_transit_report  # noqa: E402


FIXTURE_NAMES = ["simple", "angular_heavy", "stellium"]

NEW_CONFIG = {
    "label": "NEW (current engine, post-PR1..PR11)",
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


def _canonical_payload_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _hash_payload(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_payload_bytes(payload)).hexdigest()


def _load_frozen_artifact(name: str) -> Dict[str, Any]:
    path = ARTIFACT_DIR / f"{name}.json"
    if not path.exists():
        raise SystemExit(f"frozen baseline missing: {path}. Run scripts/freeze_baseline.py first.")
    with path.open("r", encoding="utf-8") as f:
        artifact = json.load(f)
    stored = artifact["metadata"]["hash_of_canonical_payload"]
    recomputed = _hash_payload(artifact["payload"])
    if stored != recomputed:
        raise SystemExit(
            f"baseline hash mismatch for {name}: stored={stored[:12]}… recomputed={recomputed[:12]}…\n"
            "Do NOT ignore this. Either the file was edited, Python's JSON serialization drifted, "
            "or the freeze format changed. Investigate before proceeding."
        )
    return artifact


def _live_aspects(birth: Mapping[str, Any], transit_date: str) -> List[Dict[str, Any]]:
    report = build_transit_report(
        birth_date=birth["date"],
        birth_time=birth["time"],
        birth_place=birth["place"],
        birth_latitude=birth["latitude"],
        birth_longitude=birth["longitude"],
        birth_timezone=birth["timezone"],
        transit_date=transit_date,
        transit_time="12:00",
        transit_place=birth["place"],
        transit_latitude=birth["latitude"],
        transit_longitude=birth["longitude"],
        transit_timezone=birth["timezone"],
        options={
            "orbs": NEW_CONFIG["orbs"],
            "aspect_types": NEW_CONFIG["aspect_types"],
            "include_angles": True,
            "max_aspects_per_transit_body": 99,
            "apply_out_of_sign_filter": NEW_CONFIG["apply_out_of_sign_filter"],
        },
        assumptions=[],
    )
    asp = report.get("aspects", {}) or {}
    raw = list(asp.get("transit_to_natal", []) or []) + list(asp.get("transit_to_angles", []) or [])
    minimal = []
    for a in raw:
        natal = a.get("natal") or {}
        minimal.append({
            "type": a.get("type"),
            "orb": round(float(a.get("orb") or 0.0), 4),
            "strength": round(float(a.get("strength") or 0.0), 4),
            "transit_body": (a.get("transit") or {}).get("body"),
            "target": natal.get("body") or natal.get("angle") or natal.get("point") or "",
            "out_of_sign": bool(a.get("out_of_sign", False)),
        })
    minimal.sort(key=lambda x: (-(x["strength"] or 0.0), x["orb"] or 0.0, x["transit_body"] or "",
                                 x["target"] or "", x["type"] or ""))
    return minimal


def _sig(a: Mapping[str, Any]) -> str:
    return f"{a.get('transit_body')}-{a.get('type')}-{a.get('target')}"


def _fixture_row(name: str) -> Dict[str, Any]:
    art = _load_frozen_artifact(name)
    birth = art["metadata"]["birth_data"]
    dates: List[str] = art["metadata"]["benchmark_dates"]

    per_date: List[Dict[str, Any]] = []
    per_type_a: Dict[str, int] = {}
    per_type_b: Dict[str, int] = {}

    for td in dates:
        a_list = art["payload"].get(td, [])
        b_list = _live_aspects(birth, td)

        for a in a_list:
            per_type_a[a["type"]] = per_type_a.get(a["type"], 0) + 1
        for b in b_list:
            per_type_b[b["type"]] = per_type_b.get(b["type"], 0) + 1

        top5_a = {_sig(x) for x in a_list[:5]}
        top5_b = {_sig(x) for x in b_list[:5]}
        top10_a = {_sig(x) for x in a_list[:10]}
        top10_b = {_sig(x) for x in b_list[:10]}

        per_date.append({
            "date": td,
            "count_a": len(a_list),
            "count_b": len(b_list),
            "delta_pct": 100.0 * (len(b_list) - len(a_list)) / max(len(a_list), 1),
            "top5_kept": len(top5_a & top5_b),
            "top10_kept": len(top10_a & top10_b),
            "oos_b": sum(1 for x in b_list if x.get("out_of_sign")),
        })

    return {
        "fixture": name,
        "classification": art["metadata"]["classification"],
        "rows": per_date,
        "mean_count_a": statistics.mean(r["count_a"] for r in per_date),
        "mean_count_b": statistics.mean(r["count_b"] for r in per_date),
        "mean_delta_pct": statistics.mean(r["delta_pct"] for r in per_date),
        "mean_top5_kept": statistics.mean(r["top5_kept"] for r in per_date),
        "mean_top10_kept": statistics.mean(r["top10_kept"] for r in per_date),
        "total_oos_b": sum(r["oos_b"] for r in per_date),
        "per_type_a": per_type_a,
        "per_type_b": per_type_b,
        "baseline_hash": art["metadata"]["hash_of_canonical_payload"],
    }


def run(as_json: bool = False) -> Dict[str, Any]:
    summaries = [_fixture_row(name) for name in FIXTURE_NAMES]

    aggregate = {
        "label_a": "OLD (frozen pre-PR1 baseline)",
        "label_b": NEW_CONFIG["label"],
        "mean_count_a": statistics.mean(s["mean_count_a"] for s in summaries),
        "mean_count_b": statistics.mean(s["mean_count_b"] for s in summaries),
        "mean_delta_pct": statistics.mean(s["mean_delta_pct"] for s in summaries),
        "mean_top5_kept": statistics.mean(s["mean_top5_kept"] for s in summaries),
        "mean_top10_kept": statistics.mean(s["mean_top10_kept"] for s in summaries),
    }

    if as_json:
        print(json.dumps({"fixtures": summaries, "aggregate": aggregate}, indent=2, ensure_ascii=False))
        return {"fixtures": summaries, "aggregate": aggregate}

    print(f"\n=== Transit ranking benchmark: {aggregate['label_a']} vs {aggregate['label_b']} ===\n")

    for s in summaries:
        cls = s["classification"]
        traits = cls.get("primary_profile", "?")
        if cls.get("secondary_traits"):
            traits += f" (+{','.join(cls['secondary_traits'])})"
        print(f"--- fixture: {s['fixture']} [{traits}] · baseline hash {s['baseline_hash'][:12]}… ---")
        print(f"{'date':<12} {'count_a':>8} {'count_b':>8} {'delta%':>8} {'top5':>6} {'top10':>7} {'oos_b':>6}")
        print("-" * 60)
        for r in s["rows"]:
            print(f"{r['date']:<12} {r['count_a']:>8} {r['count_b']:>8} {r['delta_pct']:>+7.1f}% "
                  f"{r['top5_kept']:>3}/5  {r['top10_kept']:>3}/10 {r['oos_b']:>6}")
        print("-" * 60)
        print(f"{'MEAN':<12} {s['mean_count_a']:>8.1f} {s['mean_count_b']:>8.1f} "
              f"{s['mean_delta_pct']:>+7.1f}% "
              f"{s['mean_top5_kept']:>3.1f}/5  {s['mean_top10_kept']:>3.1f}/10 "
              f"{s['total_oos_b']:>6}")
        print()

    print(f"=== Aggregate across {len(summaries)} fixtures ===")
    print(f"  OLD mean aspects/day:  {aggregate['mean_count_a']:.1f}")
    print(f"  NEW mean aspects/day:  {aggregate['mean_count_b']:.1f}")
    print(f"  delta:                 {aggregate['mean_delta_pct']:+.1f}%")
    print(f"  top-5 retention:       {aggregate['mean_top5_kept']:.2f}/5")
    print(f"  top-10 retention:      {aggregate['mean_top10_kept']:.2f}/10")

    return {"fixtures": summaries, "aggregate": aggregate}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    run(as_json=args.json)


if __name__ == "__main__":
    main()
