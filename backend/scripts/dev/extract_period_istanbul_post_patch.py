"""Dev-only: hit /transit/narrative for Istanbul 1996-12-28 07:10 against
the current month and dump period_reading_v1 prose for analysis.

Writes to backend/tests/_artifacts/reasoning_output_review/.
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

OUTPUT_DIR = BACKEND_ROOT / "tests" / "_artifacts" / "reasoning_output_review"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    from app.api.routes import transits as transits_route

    # Use a fixed analysis window so the artifact is reproducible. Pick
    # 2026-04-01 .. 2026-04-30 to exercise the documented non-LifeChapter
    # fallback path on this chart.
    start = date(2026, 4, 1)
    end = date(2026, 4, 30)
    selected_date = date(2026, 4, 22)

    request = transits_route.TransitNarrativeRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        birth_latitude=41.0082,
        birth_longitude=28.9784,
        birth_timezone="Europe/Istanbul",
        start=start.isoformat(),
        end=end.isoformat(),
        tz="Europe/Istanbul",
        transit_place="Istanbul, TR",
        transit_latitude=41.0082,
        transit_longitude=28.9784,
        transit_timezone="Europe/Istanbul",
        lens="general",
        intent=None,
        selected_date=selected_date.isoformat(),
        include_best_times=False,
        top=10,
        window=3,
        debug=True,
        response_mode="full",
        payload_profile="full",
        subscription_tier="free",
        locale="tr",
    )

    try:
        response = transits_route.build_transit_narrative(request)
    except Exception as exc:  # noqa: BLE001
        out = {"status": "error", "error": str(exc)}
        target = OUTPUT_DIR / "period_istanbul_1996_post_patch.json"
        target.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"FAILED: {exc}", file=sys.stderr)
        raise

    public = response.get("public") or {}
    period_core = public.get("period_core") or {}
    period_reading_v1 = period_core.get("period_reading_v1") or {}

    payload = {
        "request": {
            "birth_date": request.birth_date,
            "birth_time": request.birth_time,
            "birth_place": request.birth_place,
            "start": request.start,
            "end": request.end,
            "selected_date": request.selected_date,
        },
        "period_reading_v1": period_reading_v1,
        "period_core_summary": {
            "title": period_core.get("title"),
            "core_story": period_core.get("core_story"),
            "narrative_version": period_core.get("narrative_version"),
            "tags": period_core.get("tags"),
            "semantic_focus": period_core.get("semantic_focus"),
            "active_life_chapter": period_core.get("active_life_chapter"),
            "_period_story_debug": period_core.get("_period_story_debug"),
            "canonical_period_spine": period_core.get("canonical_period_spine"),
        },
        "featured_events": [
            {
                "event_id": ev.get("event_id"),
                "label": ev.get("label"),
                "transit_body": ev.get("transit_body"),
                "natal_point": ev.get("natal_point"),
                "aspect": ev.get("aspect"),
                "polarity": ev.get("polarity"),
                "phase": ev.get("phase"),
                "orb_deg": ev.get("orb_deg"),
                "houses": ev.get("houses"),
                "interpretation": ev.get("interpretation"),
            }
            for ev in (period_core.get("featured_events") or [])
        ],
    }
    target = OUTPUT_DIR / "period_istanbul_1996_post_patch.json"
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {target.relative_to(REPO_ROOT)}")
    print()
    print("=== period_reading_v1.full_text ===")
    print(period_reading_v1.get("full_text") or "(none)")
    print()
    print("=== period_core.title ===")
    print(period_core.get("title"))
    print()
    print(
        "=== semantic_focus.source ===",
        (period_core.get("semantic_focus") or {}).get("source"),
    )
    print(
        "=== composer_mode / semantic_mode ===",
        period_core.get("_period_story_debug", {}).get("composer_mode"),
        "/",
        period_core.get("_period_story_debug", {}).get("composer_semantic_mode"),
    )


if __name__ == "__main__":
    main()
