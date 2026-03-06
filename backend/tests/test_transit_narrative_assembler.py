from app.transit.narrative.assembler import assemble_blocks
from app.transit.narrative.screen_builders import build_calendar_day, build_personal_transit, build_space_hub


def _calendar_payload() -> dict:
    return {
        "range": {"start": "2026-03-01", "end": "2026-03-31", "tz": "Europe/Istanbul"},
        "year_summary": {
            "core_story": "Bu donemde iliski ve ritim temasi one cikiyor.",
            "dominant_domains": ["relationships", "mind"],
            "indices": {"pressure": 0.62, "support": 0.58},
        },
        "days": [
            {
                "date": "2026-03-05",
                "rating": 2,
                "note": "Gun icinde denge korunursa akistan yarar alinabilir.",
                "labels": ["destek", "iliski"],
                "event_count": 0,
                "top_events": [{"id": "evt_1"}],
                "is_critical": False,
            }
        ],
    }


def test_assembler_produces_core_theme_block_when_year_summary_exists() -> None:
    blocks = assemble_blocks(calendar_public=_calendar_payload(), selected_date="2026-03-05")
    block_types = {block.type for block in blocks}
    assert "core_theme" in block_types


def test_calendar_day_payload_has_no_zero_event_string() -> None:
    blocks = assemble_blocks(calendar_public=_calendar_payload(), selected_date="2026-03-05")
    payload = build_calendar_day(blocks, "2026-03-05")

    assert "0 event" not in str(payload).lower()
    assert payload["events_count"] == 0
    assert payload["signals_count"] >= 1


def test_best_time_primary_exists_when_candidates_exist() -> None:
    best_times = {
        "intent": "beauty_care_nourish",
        "candidates": [
            {"date": "2026-03-08", "score": 0.91, "reason": "Bakim ve besleme icin uyumlu."}
        ],
        "windows": [],
    }
    blocks = assemble_blocks(
        calendar_public=_calendar_payload(),
        best_times=best_times,
        selected_date="2026-03-05",
    )
    block_types = {block.type for block in blocks}
    assert "best_time_primary" in block_types


def test_space_hub_never_empty_when_blocks_exist() -> None:
    blocks = assemble_blocks(calendar_public=_calendar_payload(), selected_date="2026-03-05")
    screen = build_space_hub(blocks)
    assert screen["count"] >= 1
    assert len(screen["blocks"]) >= 1


def test_core_theme_fallback_generated_when_core_story_missing() -> None:
    payload = _calendar_payload()
    payload["year_summary"] = {
        "core_story": "",
        "dominant_domains": ["relationships"],
        "indices": {"pressure": 0.51, "support": 0.47},
    }
    blocks = assemble_blocks(calendar_public=payload, selected_date="2026-03-05")
    personal = build_personal_transit(blocks)
    serialized = str(personal).lower()
    assert "core_theme" in serialized or "gun enerjisi" in serialized
