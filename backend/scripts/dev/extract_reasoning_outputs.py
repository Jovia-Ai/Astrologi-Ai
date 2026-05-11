"""Dev-only extraction script for SHOU reasoning/voice review.

Generates representative real backend outputs for:
  - natal public output (Istanbul 1996-12-28 sample)
  - period output cases (Aries 3rd Saturn return + South Node overlap, Cancer 8th
    Saturn return, structural T-square, nodal activation)
  - daily synthesis sample (uses the same transit narrative artifact's event cards
    if available, otherwise synthetic cards exercising the live builder)

NOT FOR PRODUCTION USE. Place under backend/scripts/dev/. The script never writes
outside backend/tests/_artifacts/reasoning_output_review/ and never mutates
product code.

Usage:
    PYTHONPATH=backend python backend/scripts/dev/extract_reasoning_outputs.py
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

OUTPUT_DIR = BACKEND_ROOT / "tests" / "_artifacts" / "reasoning_output_review"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FIXTURE_ROOT = BACKEND_ROOT / "tests" / "fixtures" / "life_chapter"
TRANSIT_ARTIFACT = (
    BACKEND_ROOT
    / "tests"
    / "_artifacts"
    / "transit_narrative_1996-12-28_07-10_istanbul_2026-03-04.json"
)


def _dump_json(name: str, payload: Dict[str, Any]) -> Path:
    target = OUTPUT_DIR / name
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    return target


def _load_fixture(group: str, name: str) -> Dict[str, Any]:
    return json.loads((FIXTURE_ROOT / group / f"{name}.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Case 1: Natal public output (Istanbul)
# ---------------------------------------------------------------------------
def extract_natal_public() -> Dict[str, Any]:
    from app.api.routes import natal_interpretation

    request = natal_interpretation.NatalInterpretationRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul, TR",
        birth_latitude=41.0082,
        birth_longitude=28.9784,
        birth_timezone="Europe/Istanbul",
        locale="tr",
        summary_only=False,
        include_full_profile=True,
    )
    response = natal_interpretation.interpret_natal_chart_ui(
        request,
        debug=True,
        include_debug=True,
        profile_engine=None,
    )
    return response


# ---------------------------------------------------------------------------
# Period output helper
# ---------------------------------------------------------------------------
def _build_period_payload(
    case_label: str,
    *,
    canonical_natal_state: Dict[str, Any],
    transit_events: list[Dict[str, Any]],
    structural_chapter_rail: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    from app.transit.narrative.astrolog_narrative_engine import (
        PeriodStoryContext,
        build_period_story,
    )
    from app.transit.narrative.life_chapter_detector import detect_active_life_chapter
    from app.transit.narrative.life_chapter_contract import LifeChapter

    detector = detect_active_life_chapter(
        canonical_natal_state=canonical_natal_state,
        transit_events=transit_events,
        structural_chapter_rail=structural_chapter_rail,
        debug=True,
    )

    active = detector.get("active_life_chapter")

    # Build a representative period_core from the fixture event(s) so that the
    # period story engine has something to express. We translate the input
    # transit_events into a featured_events shape consistent with the live
    # period_core contract (used by build_period_story).
    featured_events = []
    for idx, evt in enumerate(transit_events):
        featured = {
            "event_id": evt.get("event_id"),
            "scope": evt.get("scope") or "transit_to_natal",
            "label": evt.get("event_id"),
            "transit_body": evt.get("source_bodies", ["Saturn"])[0]
            if isinstance(evt.get("source_bodies"), list)
            else "Saturn",
            "natal_point": (evt.get("target_points") or ["Saturn"])[0],
            "aspect": "conjunction"
            if evt.get("event_subtype") in {"saturn_return", "nodal_return"}
            else "square",
            "polarity": "hard",
            "strength": float(evt.get("structural_significance") or 0.9),
            "orb_deg": 0.2,
            "phase": evt.get("current_phase") or "exactish",
            "bucket": "long",
            "tags": ["self", "structural"],
            "houses": {
                "transit_in_natal_house": (evt.get("target_houses") or [1])[0],
                "natal_point_house": (evt.get("target_houses") or [1])[0],
            },
            "story_score": 0.95 - idx * 0.05,
            "selection_index": idx,
        }
        featured_events.append(featured)

    period_core = {
        "title": f"Period story for {case_label}",
        "core_story": "",
        "featured_events": featured_events,
        "tags": [],
    }

    period_story_ctx = PeriodStoryContext(
        period_core=period_core,
        chart_snapshot={},
        natal_promise={},
        canonical_period_spine=None,
        active_life_chapter=active,
        locale="tr",
        enable_fun=True,
    )
    narrative = build_period_story(period_story_ctx)

    payload: Dict[str, Any] = {
        "case_label": case_label,
        "inputs": {
            "canonical_natal_state": canonical_natal_state,
            "transit_events": transit_events,
            "structural_chapter_rail": structural_chapter_rail,
        },
        "detector_result": detector,
        "active_life_chapter": active,
        "candidates": detector.get("candidates"),
        "structural_chapter_rail_input": structural_chapter_rail,
        "period_core": period_core,
        "renderer_handoff": (
            (active or {}).get("renderer_handoff")
            if isinstance(active, dict)
            else None
        ),
        "semantic_focus": (
            (active or {}).get("semantic_focus") if isinstance(active, dict) else None
        ),
        "suppressed_readings": (
            (active or {}).get("suppressed_readings")
            if isinstance(active, dict)
            else None
        ),
        "selected_meaning": (
            (active or {}).get("selected_meaning")
            if isinstance(active, dict)
            else None
        ),
        "natal_architecture_anchor": (
            (active or {}).get("natal_architecture_anchor")
            if isinstance(active, dict)
            else None
        ),
        "period_voice_policy": None,  # Detector itself doesn't emit it; populated downstream
        "period_narrative_prose": {
            "period_reading_v1": narrative.period_reading_v1,
            "period_opening": narrative.period_opening,
            "big_picture": narrative.big_picture,
            "mechanism": narrative.mechanism,
            "growth_edge": narrative.growth_edge,
            "relational_or_life_expression": narrative.relational_or_life_expression,
            "what_it_builds": narrative.what_it_builds,
            "upper_meaning": narrative.upper_meaning,
            "debug": narrative.debug,
        },
    }
    return payload


# ---------------------------------------------------------------------------
# Cases 2-5: period outputs from fixtures
# ---------------------------------------------------------------------------
def extract_period_aries_3rd_saturn() -> Dict[str, Any]:
    fx = _load_fixture("saturn_return", "aries_3rd_with_south_node_overlap")
    return _build_period_payload(
        "Aries 3rd Saturn return + South Node overlap",
        canonical_natal_state=fx["canonical_natal_state"],
        transit_events=fx["transit_events"],
    )


def extract_period_cancer_8th_saturn() -> Dict[str, Any]:
    fx = _load_fixture("saturn_return", "cancer_8th_water_emotional")
    return _build_period_payload(
        "Cancer 8th Saturn return",
        canonical_natal_state=fx["canonical_natal_state"],
        transit_events=fx["transit_events"],
    )


def extract_period_t_square() -> Dict[str, Any]:
    """Structural T-square is *not* a transit event — it's a natal architectural
    rail. We pass a structural_chapter_rail into the detector to confirm it is
    only emitted as a low-confidence candidate (excluded from PR-D ownership).

    No fixture exists for this case in the repo, so we hand-craft a minimal
    structural rail input. The detector contract for T-square is what we want
    to inspect — not invent prose.
    """
    canonical_state = {
        "bodies": [
            {"body": "Sun", "sign": "Capricorn", "house": 1},
            {"body": "Mars", "sign": "Aries", "house": 4},
            {"body": "Pluto", "sign": "Cancer", "house": 7},
            {"body": "Saturn", "sign": "Libra", "house": 10},
        ],
        "house_cusps": [
            {"house": idx, "sign": s}
            for idx, s in enumerate(
                [
                    "Capricorn",
                    "Aquarius",
                    "Pisces",
                    "Aries",
                    "Taurus",
                    "Gemini",
                    "Cancer",
                    "Leo",
                    "Virgo",
                    "Libra",
                    "Scorpio",
                    "Sagittarius",
                ],
                start=1,
            )
        ],
    }
    structural_rail = {
        "id": "structural_t_square_cardinal",
        "pattern": "t_square",
        "modality": "cardinal",
        "apex_house": 4,
        "release_point": 10,
        "members": [
            {"body": "Mars", "house": 4},
            {"body": "Pluto", "house": 7},
            {"body": "Saturn", "house": 10},
        ],
    }
    # No transit events — this case is purely structural.
    return _build_period_payload(
        "Structural T-square (cardinal, apex 4th)",
        canonical_natal_state=canonical_state,
        transit_events=[],
        structural_chapter_rail=structural_rail,
    )


def extract_period_nodal_activation() -> Dict[str, Any]:
    fx = _load_fixture("nodal", "nn_aries_sn_libra")
    return _build_period_payload(
        "Nodal activation (NN Aries / SN Libra)",
        canonical_natal_state=fx["canonical_natal_state"],
        transit_events=fx["transit_events"],
    )


# ---------------------------------------------------------------------------
# Case 6: Daily synthesis output
# ---------------------------------------------------------------------------
def extract_daily_synthesis() -> Dict[str, Any]:
    """Use the live build_daily_synthesis with a card that exercises both the
    period-context bridge and a clear daily trigger.

    We intentionally reuse the period_core from the existing transit narrative
    artifact (Istanbul / 2026-03) so that the period spine is an actual current
    backend output (not synthetic). Daily card itself is constructed via the
    real generate_daily_from_event humanizer so phrasing comes from production
    voice packs, not handcrafted strings.
    """
    from app.transit.narrative.daily_humanizer_tr import generate_daily_from_event
    from app.transit.narrative.daily_synthesis import build_daily_synthesis

    period_core: Dict[str, Any] = {}
    period_event_cards: list[Dict[str, Any]] = []
    period_artifact: Dict[str, Any] | None = None
    if TRANSIT_ARTIFACT.exists():
        try:
            full = json.loads(TRANSIT_ARTIFACT.read_text(encoding="utf-8"))
            period_artifact = full
            period_core = (
                ((full.get("response") or {}).get("public") or {}).get("period_core")
                or {}
            )
            period_event_cards = list(
                ((full.get("response") or {}).get("public") or {}).get(
                    "event_cards", []
                )
            )
        except Exception:
            period_artifact = None

    # Build a realistic raw daily event using a Mercury–Sun square with a 3rd
    # house touchpoint (common, well-covered pack).
    raw_event = {
        "event_id": "daily_mercury_square_sun_2026-05-05",
        "transit_body": "Mercury",
        "natal_point": "Sun",
        "aspect": "square",
        "aspect_mode": "friction",
        "orb_deg": 0.4,
        "phase": "exactish",
        "polarity": "hard",
        "bucket": "short",
        "houses": {
            "transit_in_natal_house": 3,
            "natal_point_house": 3,
        },
        "timing": {"peak_date_utc": "2026-05-05T12:00:00+00:00"},
        "time": {
            "is_peaking_today": True,
            "is_rising_today": False,
            "is_releasing_today": False,
        },
        "natal_promise": {"score": 0.71},
        "ranking": {"tier": "main", "weight": 1.05, "exact_in_days": 0},
        "tags": ["self", "communication", "pressure"],
    }
    daily_card = generate_daily_from_event(raw_event, score=0.82, is_period_derived=False)

    natal_snapshot = {
        "asc_sign": "Capricorn",
        "sun_sign": "Capricorn",
        "moon_sign": "Aquarius",
    }

    synthesis = build_daily_synthesis(
        daily_event_cards=[daily_card],
        period_core=period_core,
        natal_snapshot=natal_snapshot,
        period_event_cards=period_event_cards or None,
    )

    return {
        "inputs": {
            "raw_event": raw_event,
            "natal_snapshot": natal_snapshot,
            "period_core_source": "tests/_artifacts/transit_narrative_1996-12-28_07-10_istanbul_2026-03-04.json"
            if period_artifact
            else None,
        },
        "daily_event_cards": [daily_card],
        "period_core_consumed": period_core,
        "period_event_cards_consumed_sample": period_event_cards[:2]
        if period_event_cards
        else [],
        "daily_synthesis": synthesis,
        "final_body": (synthesis or {}).get("body"),
        "final_headline": (synthesis or {}).get("headline"),
        "final_guidance": (synthesis or {}).get("guidance"),
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
EXTRACTORS = [
    ("natal_public_istanbul_1996_12_28.json", extract_natal_public),
    ("period_aries_3rd_saturn_return.json", extract_period_aries_3rd_saturn),
    ("period_cancer_8th_saturn_return.json", extract_period_cancer_8th_saturn),
    ("period_structural_t_square.json", extract_period_t_square),
    ("period_nodal_activation.json", extract_period_nodal_activation),
    ("daily_synthesis_sample.json", extract_daily_synthesis),
]


def main() -> None:
    summary: Dict[str, Any] = {}
    for filename, fn in EXTRACTORS:
        print(f"--- extracting: {filename}")
        try:
            payload = fn()
            target = _dump_json(filename, payload)
            summary[filename] = {"status": "ok", "path": str(target.relative_to(REPO_ROOT))}
            print(f"    wrote {target.relative_to(REPO_ROOT)}")
        except Exception as exc:
            tb = traceback.format_exc()
            err_payload = {
                "status": "error",
                "error": str(exc),
                "traceback": tb,
            }
            target = _dump_json(filename, err_payload)
            summary[filename] = {
                "status": "error",
                "path": str(target.relative_to(REPO_ROOT)),
                "error": str(exc),
            }
            print(f"    FAILED: {exc}", file=sys.stderr)
            print(tb, file=sys.stderr)

    _dump_json("_extraction_summary.json", summary)
    print("\nDone. Output:", OUTPUT_DIR.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
