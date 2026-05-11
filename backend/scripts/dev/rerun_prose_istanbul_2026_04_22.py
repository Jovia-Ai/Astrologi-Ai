"""Dev-only: re-run period prose stage against the existing live Istanbul
2026-04-22 period_core artifact, using the patched fallback code path.

We can't re-run the full /transit/narrative locally because extended ephemeris
files (`seas_18.se1`) are not on this machine. The previous live artifact
already captured a real `period_core` (featured_events + semantic_focus +
canonical_period_spine + active_life_chapter), so we replay only the prose
composer against that real input.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

ARTIFACT = (
    BACKEND_ROOT
    / "tests"
    / "_artifacts"
    / "transit_output_review_after_period_reading_v1"
    / "post_fix_raw_transit_narrative_istanbul_2026-04-22.json"
)
OUT_DIR = BACKEND_ROOT / "tests" / "_artifacts" / "reasoning_output_review"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    from app.transit.narrative.astrolog_narrative_engine import (
        PeriodStoryContext,
        build_period_story,
    )

    raw = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    public = raw.get("public") or {}
    period_core = public.get("period_core") or {}
    canonical_period_spine = period_core.get("canonical_period_spine")
    active_life_chapter = period_core.get("active_life_chapter")

    ctx = PeriodStoryContext(
        period_core=period_core,
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine=canonical_period_spine
        if isinstance(canonical_period_spine, dict)
        else None,
        active_life_chapter=active_life_chapter
        if isinstance(active_life_chapter, dict)
        else None,
        locale="tr",
        enable_fun=True,
    )
    narrative = build_period_story(ctx)

    period_reading_v1 = narrative.period_reading_v1
    debug = narrative.debug or {}

    payload = {
        "case": "Istanbul 1996-12-28 07:10 / window 2026-04-01..2026-04-30 / selected 2026-04-22",
        "period_reading_v1": period_reading_v1,
        "period_opening": narrative.period_opening,
        "big_picture": narrative.big_picture,
        "mechanism": narrative.mechanism,
        "growth_edge": narrative.growth_edge,
        "relational_or_life_expression": narrative.relational_or_life_expression,
        "what_it_builds": narrative.what_it_builds,
        "upper_meaning": narrative.upper_meaning,
        "debug": {
            "composer_mode": debug.get("composer_mode"),
            "composer_semantic_mode": debug.get("composer_semantic_mode"),
            "track_id": debug.get("track_id"),
            "active_life_chapter_present": active_life_chapter is not None,
            "semantic_focus_source": (period_core.get("semantic_focus") or {}).get("source"),
            "primary_domain": (period_core.get("semantic_focus") or {}).get("primary_domain"),
            "secondary_domains": (period_core.get("semantic_focus") or {}).get("secondary_domains"),
            "scene_translation_request": (period_core.get("semantic_focus") or {}).get(
                "scene_translation_request"
            ),
        },
        "featured_events_summary": [
            {
                "label": ev.get("label"),
                "transit_body": ev.get("transit_body"),
                "natal_point": ev.get("natal_point"),
                "aspect": ev.get("aspect"),
                "polarity": ev.get("polarity"),
                "phase": ev.get("phase"),
                "orb_deg": ev.get("orb_deg"),
                "houses": ev.get("houses"),
                "interpretation_where": (ev.get("interpretation") or {}).get("where"),
            }
            for ev in (period_core.get("featured_events") or [])
        ],
    }

    target = OUT_DIR / "period_istanbul_1996_2026_04_22_post_patch.json"
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {target.relative_to(REPO_ROOT)}")
    print()
    print("=== composer mode / semantic mode ===")
    print(debug.get("composer_mode"), "/", debug.get("composer_semantic_mode"))
    print()
    print("=== period_reading_v1.full_text (length:", len(period_reading_v1.get("full_text") or ""), ") ===")
    print(period_reading_v1.get("full_text") or "(none)")
    print()
    print("=== period_opening ===")
    print(narrative.period_opening)
    print()
    print("=== big_picture ===")
    print(narrative.big_picture)
    print()
    print("=== mechanism ===")
    print(narrative.mechanism)


if __name__ == "__main__":
    main()
