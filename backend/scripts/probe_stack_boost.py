"""Probe stack boost behavior across the 3 bench fixtures.

Runs the full transit pipeline end-to-end for each fixture × a multi-day
window, then measures the stack-detection surface:

  * total days observed
  * stack days (≥2 events ≥ 0.42 on the same natal-local day)
  * boosted event count
  * cap-hit day count
  * bucket crossings (meaningful → high, etc.)
  * per-stack-day significance shift summary

Bench-adjacent, not engine. Uses live engine (current code), not frozen
artifacts. Intended to be rerun whenever stack_boost params are retuned.

Usage:
    PYTHONPATH=backend python backend/scripts/probe_stack_boost.py
    PYTHONPATH=backend python backend/scripts/probe_stack_boost.py --days 30
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
EPHE_DIR = BACKEND_ROOT / "ephe"
ARTIFACT_DIR = BACKEND_ROOT / "tests" / "_artifacts" / "bench_baseline_sprint1"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("SUPABASE_URL", "https://probe.local")
os.environ.setdefault("SUPABASE_KEY", "probe")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "probe")

import swisseph  # noqa: E402

swisseph.set_ephe_path(str(EPHE_DIR))

from app.engine.transit_engine import build_transit_report  # noqa: E402
from app.transit.astro_event_v2 import (  # noqa: E402
    build_personal_multi_event_payload,
    STACK_MEANINGFUL_THRESHOLD,
)


FIXTURES = ["simple", "angular_heavy", "stellium"]

# Windowed dates — sample the first N days from the bench transit dates
# to get a broader view of stack incidence than 5 sparse snapshots.
DEFAULT_WINDOW_DAYS = 15


def _load_fixture_meta(name: str) -> Dict[str, Any]:
    with (ARTIFACT_DIR / f"{name}.json").open() as f:
        return json.load(f)["metadata"]


def _build_event_payload(
    birth: Mapping[str, Any],
    transit_date: str,
    *,
    apply_stack: bool,
) -> Dict[str, Any]:
    # First build the raw transit report (aspect layer)
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
        options={},
        assumptions=[],
    )
    # Then run event-layer aggregation with/without stack boost
    # Pass a minimal non-empty solar_year stub so build_personal_multi_event_payload
    # doesn't try to re-resolve the birth location via OpenCage (the probe runs
    # offline). Stack boost logic is independent of solar year contents.
    solar_stub = {"dominant_houses": [], "year_ruler": "", "solar_natal_overlays": []}
    return build_personal_multi_event_payload(
        report=report,
        transit_date=transit_date,
        transit_place=birth["place"],
        transit_latitude=birth["latitude"],
        transit_longitude=birth["longitude"],
        transit_timezone=birth["timezone"],
        solar_year=solar_stub,
        birth_timezone=birth["timezone"],
        apply_stack_boost=apply_stack,
    )


def _all_events(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rail = list(payload.get("personal_transit_rail") or [])
    rail += list(payload.get("structural_chapter_rail") or [])
    return rail


def _bucket(sig: float) -> str:
    if sig >= 0.58:
        return "high"
    if sig >= 0.42:
        return "meaningful"
    if sig >= 0.35:
        return "humanizer"
    if sig >= 0.18:
        return "eligible"
    if sig >= 0.12:
        return "narrative"
    return "below"


def probe_fixture(name: str, window_days: int) -> Dict[str, Any]:
    meta = _load_fixture_meta(name)
    birth = meta["birth_data"]
    base_dates = meta["benchmark_dates"]

    # Expand each bench date into a small window to see stack formation
    window_dates = []
    for d in base_dates:
        y, m, dd = [int(x) for x in d.split("-")]
        anchor = date(y, m, dd)
        for delta in range(window_days):
            window_dates.append((anchor + timedelta(days=delta)).isoformat())

    stats = {
        "fixture": name,
        "window_days_per_anchor": window_days,
        "total_transit_dates": len(window_dates),
        "boosted_events": 0,
        "stack_days_seen": set(),
        "capped_days_seen": set(),
        "bucket_crossings": 0,
        "churn_non_stack_top5": 0,
        "examples": [],  # collect a few before/after samples
        "size2_no_mod_days": set(),
        "size_ge_3_days": set(),
        # PR7b: narrative fire-rate measurement.
        # "narrative_fired_days_intersect" counts dates where the probed date
        # itself (not ±window events) is a natal-local day with a fired clause.
        # That's the UX-realistic metric: on the day the user opens the app,
        # does ANY top-rail event carry the stack clause?
        "narrative_fired_probed_dates": set(),
    }

    for td in window_dates:
        with_stack = _build_event_payload(birth, td, apply_stack=True)
        without_stack = _build_event_payload(birth, td, apply_stack=False)

        sm = with_stack.get("stack_meta") or {}
        for d_iso in sm.get("stack_days", []):
            stats["stack_days_seen"].add(d_iso)
        # PR7b: narrative fire-rate — is the probed date itself a day where
        # any top-rail event carries the stack clause?
        fired_days = set(sm.get("narrative_fired_days") or [])
        if td in fired_days:
            stats["narrative_fired_probed_dates"].add(td)
        stats["boosted_events"] += int(sm.get("boosted_event_count") or 0)
        # capped_day_count is per-call, but same stack day may recur across window slides
        # We track unique stack-days that had a cap
        pt_rail_stack = _all_events(with_stack)
        pt_rail_plain = _all_events(without_stack)
        for ev in pt_rail_stack:
            prov = ev.get("provenance") or {}
            st = prov.get("stack_meta")
            if not st:
                continue
            if st.get("capped"):
                stats["capped_days_seen"].add(st.get("day"))
            # Distribution metrics: marginal (size=2, no modifier) vs real (size>=3)
            if st.get("size", 0) >= 3:
                stats["size_ge_3_days"].add(st.get("day"))
            elif st.get("size") == 2 and not st.get("flags"):
                stats["size2_no_mod_days"].add(st.get("day"))

        # Bucket crossings: for each matched event_id, compare bucket(plain) vs bucket(stack)
        by_id_plain = {e["event_id"]: e for e in pt_rail_plain}
        by_id_stack = {e["event_id"]: e for e in pt_rail_stack}
        for eid, e_stk in by_id_stack.items():
            e_pln = by_id_plain.get(eid)
            if not e_pln:
                continue
            if _bucket(e_stk["significance_score"]) != _bucket(e_pln["significance_score"]):
                stats["bucket_crossings"] += 1

        # Churn on non-stack days: if no boosted events, top-5 ranking by id
        # should be identical between the two variants
        if not sm.get("stack_days"):
            top5_stack = [e["event_id"] for e in pt_rail_stack[:5]]
            top5_plain = [e["event_id"] for e in pt_rail_plain[:5]]
            if top5_stack != top5_plain:
                stats["churn_non_stack_top5"] += 1

        # Capture up to 3 concrete before/after examples across the whole probe
        if len(stats["examples"]) < 3 and sm.get("stack_days"):
            stats["examples"].append({
                "transit_date": td,
                "stack_days": sm.get("stack_days"),
                "sample_event": _sample_example(by_id_plain, by_id_stack),
            })

    stats["stack_days_seen"] = sorted(stats["stack_days_seen"])
    stats["capped_days_seen"] = sorted(stats["capped_days_seen"])
    stats["size2_no_mod_days"] = sorted(stats["size2_no_mod_days"])
    stats["size_ge_3_days"] = sorted(stats["size_ge_3_days"])
    stats["narrative_fired_probed_dates"] = sorted(stats["narrative_fired_probed_dates"])
    return stats


def _sample_example(plain: Mapping[str, Dict], stack: Mapping[str, Dict]) -> Dict[str, Any]:
    """Pick the first event that is in a stack and show its before/after."""
    for eid, e_stk in stack.items():
        prov = e_stk.get("provenance") or {}
        meta = prov.get("stack_meta")
        if not meta:
            continue
        e_pln = plain.get(eid)
        if not e_pln:
            continue
        return {
            "event_id": eid,
            "subtype": e_stk.get("event_subtype"),
            "plain_significance": round(float(e_pln["significance_score"]), 4),
            "boosted_significance": round(float(e_stk["significance_score"]), 4),
            "plain_bucket": _bucket(e_pln["significance_score"]),
            "boosted_bucket": _bucket(e_stk["significance_score"]),
            "stack_meta": meta,
        }
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=DEFAULT_WINDOW_DAYS,
                        help=f"Window length per bench anchor date (default {DEFAULT_WINDOW_DAYS})")
    args = parser.parse_args()

    print(f"\n=== PR7 stack-boost probe · {args.days}-day window per anchor ===")
    print(f"meaningful_threshold={STACK_MEANINGFUL_THRESHOLD}  "
          f"cap=1.20  (see engine_toggles.md for full spec)\n")

    overall = {
        "total_transit_dates": 0,
        "stack_days_unique": set(),
        "capped_days_unique": set(),
        "boosted_events": 0,
        "bucket_crossings": 0,
        "churn_non_stack": 0,
        "narrative_fired_probe_date_count": 0,
    }

    for name in FIXTURES:
        s = probe_fixture(name, args.days)
        print(f"--- {name} ---")
        print(f"  transit dates probed:       {s['total_transit_dates']}")
        print(f"  stack days (unique, local): {len(s['stack_days_seen'])}")
        print(f"  cap-hit days (unique):      {len(s['capped_days_seen'])}")
        print(f"  boosted event-applications: {s['boosted_events']}")
        print(f"  bucket crossings:           {s['bucket_crossings']}")
        print(f"  non-stack-day top-5 churn:  {s['churn_non_stack_top5']}  (should be 0)")
        total_days = len(s["stack_days_seen"])
        sz2 = len(s["size2_no_mod_days"])
        sz3 = len(s["size_ge_3_days"])
        sz2_pct = 100.0 * sz2 / max(total_days, 1)
        sz3_pct = 100.0 * sz3 / max(total_days, 1)
        print(f"  size=2 no-mod days:         {sz2} ({sz2_pct:.1f}% of stack days)")
        print(f"  size>=3 days:               {sz3} ({sz3_pct:.1f}% of stack days)")
        fire_days = len(s["narrative_fired_probed_dates"])
        fire_rate = 100.0 * fire_days / max(s["total_transit_dates"], 1)
        print(f"  narrative fire-rate:        {fire_days}/{s['total_transit_dates']} probed "
              f"dates = {fire_rate:.1f}%  (target <=15%)")
        if s["examples"]:
            ex = s["examples"][0].get("sample_event") or {}
            if ex:
                print(f"  first example: {ex.get('subtype'):>12} · "
                      f"{ex.get('plain_significance')} [{ex.get('plain_bucket')}] → "
                      f"{ex.get('boosted_significance')} [{ex.get('boosted_bucket')}]  "
                      f"boost={ex['stack_meta']['boost']} size={ex['stack_meta']['size']} "
                      f"flags={ex['stack_meta']['flags']}")
        print()

        overall["total_transit_dates"] += s["total_transit_dates"]
        overall["stack_days_unique"].update(s["stack_days_seen"])
        overall["capped_days_unique"].update(s["capped_days_seen"])
        overall["boosted_events"] += s["boosted_events"]
        overall["bucket_crossings"] += s["bucket_crossings"]
        overall["churn_non_stack"] += s["churn_non_stack_top5"]
        overall["narrative_fired_probe_date_count"] += len(s["narrative_fired_probed_dates"])

    print(f"=== Aggregate across {len(FIXTURES)} fixtures ===")
    print(f"  total dates probed:        {overall['total_transit_dates']}")
    print(f"  stack days (unique):       {len(overall['stack_days_unique'])}")
    print(f"  cap-hit days (unique):     {len(overall['capped_days_unique'])}")
    print(f"  boosted event-applications {overall['boosted_events']}")
    print(f"  bucket crossings:          {overall['bucket_crossings']}")
    print(f"  non-stack-day churn:       {overall['churn_non_stack']}  (MUST be 0)")
    agg_fire_rate = 100.0 * overall["narrative_fired_probe_date_count"] / max(overall["total_transit_dates"], 1)
    print(f"  narrative fire-rate (agg): {overall['narrative_fired_probe_date_count']}/"
          f"{overall['total_transit_dates']} = {agg_fire_rate:.1f}%  (target <=15%)")


if __name__ == "__main__":
    main()
