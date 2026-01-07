from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Mapping


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic narrative pilot output.")
    parser.add_argument("--sample", choices=["identity", "full"], default="identity")
    parser.add_argument("--out-json", dest="out_json", default=None)
    parser.add_argument("--domain", dest="domain", default=None)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    try:
        chart_data = _load_chart_sample(args.sample)
        response = _build_response(chart_data)
        _self_check(response, args.domain, expect_phase2=args.debug)
        if os.getenv("NARRATIVE_PILOT_DEBUG") == "1":
            print("RESPONSE KEYS:", sorted(response.keys()))
            print("core_story len:", len(response.get("core_story") or ""))
            print("core_story_plan present:", isinstance(response.get("core_story_plan"), dict))
            legacy = (
                response.get("narrative")
                or response.get("narrative_text")
                or response.get("narrative_interpretation")
                or ""
            )
            print("legacy narrative len:", len(legacy or ""))
            plan = response.get("core_story_plan") or {}
            sections = plan.get("sections") or []
            print("DEBUG sections ids:", [section.get("section_id") for section in sections])
            if sections:
                first = sections[0]
                print("DEBUG first section:", first.get("section_id"), first.get("domain"))
                print("DEBUG first section slots:", first.get("slots"))
            snap = response.get("phase2_snapshot") or {}
            print("DEBUG phase2_snapshot top keys:", list(snap.keys())[:20])
            print(
                "DEBUG phase2_snapshot.slots keys:",
                list((snap.get("slots") or {}).keys())[:30],
            )
            accepted = ((snap.get("slots") or {}).get("accepted") or [])
            rejected = ((snap.get("slots") or {}).get("rejected") or [])
            print("DEBUG accepted count:", len(accepted))
            print("DEBUG rejected count:", len(rejected))
            if accepted:
                first = accepted[0]
                print(
                    "DEBUG accepted[0] keys:",
                    list(first.keys())[:30] if isinstance(first, dict) else type(first),
                )
                frag = first.get("best") if isinstance(first, dict) and "best" in first else first
                print(
                    "DEBUG frag keys:",
                    list(frag.keys())[:40] if isinstance(frag, dict) else type(frag),
                )
                if isinstance(frag, dict):
                    print(
                        "DEBUG frag domain/slot:",
                        frag.get("domain"),
                        frag.get("slot"),
                        frag.get("type"),
                        frag.get("category"),
                    )
                    print("DEBUG frag fragment_id:", frag.get("fragment_id"))

        if args.out_json:
            Path(args.out_json).write_text(
                json.dumps(response, ensure_ascii=True, indent=2), encoding="utf-8"
            )

        _print_meta_summary(response)
        _print_focus_composites(response)
        _print_upper_meaning(response)
        _print_narrative_preview(response, args.domain)
        if args.debug:
            _print_debug(response, args.domain)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 1


def _build_response(chart_data: Mapping[str, Any]) -> Dict[str, Any]:
    from app.api.routes.natal_interpretation import build_natal_interpretation_response_from_chart

    return build_natal_interpretation_response_from_chart(chart_data, output_profile="user_compact")


def _load_chart_sample(sample_key: str) -> Dict[str, Any]:
    try:
        from tests.approval import test_narrative_snapshots as snapshots

        chart_samples = getattr(snapshots, "_chart_samples", None)
        build_payload = getattr(snapshots, "_build_payload", None)
        if callable(chart_samples):
            samples = chart_samples()
            key = _select_sample_key(samples, sample_key)
            chart_data = samples[key]
            if callable(build_payload):
                _ = build_payload(chart_data)
            return chart_data
    except Exception:
        pass

    fallback = {
        "planets": {
            "sun": {"sign": "Taurus", "house": 1, "longitude": 30.0},
            "moon": {"sign": "Cancer", "house": 4, "longitude": 95.0},
            "mercury": {"sign": "Gemini", "house": 2, "longitude": 62.0},
        },
        "aspects": [],
        "location": {"name": "Fallback"},
    }
    return fallback


def _select_sample_key(samples: Mapping[str, Any], sample_key: str) -> str:
    if not samples:
        return ""
    if sample_key == "identity" and "taurus_cancer" in samples:
        return "taurus_cancer"
    if sample_key == "full" and "capricorn_aries" in samples:
        return "capricorn_aries"
    return next(iter(samples.keys()))


def _print_meta_summary(response: Mapping[str, Any]) -> None:
    meta = response.get("meta") or {}
    dominant_domains = meta.get("dominant_domains") or []
    dominant_domain = dominant_domains[0].get("domain") if dominant_domains else None
    dominant_axis = (meta.get("dominant_axis") or {}).get("axis")
    print("META SUMMARY")
    print(f"dominant_domain: {dominant_domain}")
    print(f"dominant_axis: {dominant_axis}")
    print(f"pressure_index: {meta.get('pressure_index')}, support_index: {meta.get('support_index')}")
    print(f"summary: {meta.get('meta_summary_text')}")
    print()


def _print_focus_composites(response: Mapping[str, Any]) -> None:
    composites = response.get("composites") or {}
    focus = composites.get("focus") or []
    supporting = composites.get("supporting") or []
    print("FOCUS COMPOSITES")
    for entry in focus:
        print(f"label: {entry.get('label')}")
        print(f"focus_score: {entry.get('focus_score')}")
        print(f"domain_hint: {entry.get('domain_hint')}, axis_hint: {entry.get('axis_hint')}")
        print("-")
    print(f"supporting_count: {len(supporting)}")
    print()


def _print_upper_meaning(response: Mapping[str, Any]) -> None:
    upper = response.get("upper_meaning_selected") or {}
    print("UPPER MEANING GATE")
    print(f"enabled: {upper.get('enabled')}")
    print(f"reasons: {upper.get('reasons')}")
    content = upper.get("content")
    if content:
        print(f"content: {content}")
    else:
        print("content: (none)")
    print()


def _print_narrative_preview(response: Mapping[str, Any], domain_filter: str | None) -> None:
    preview = response.get("core_story") or ""
    print("\nNARRATIVE PREVIEW")
    print(repr(preview))
    print(preview.strip() if preview.strip() else "(empty)")
    print()


def _print_debug(response: Mapping[str, Any], domain_filter: str | None) -> None:
    narrative = response.get("narrative") or {}
    domains = narrative.get("domains") or {}
    ordered = _domain_keys(domains, domain_filter)
    print("DEBUG")
    for domain in ordered:
        entry = domains.get(domain) or {}
        debug = entry.get("debug") or {}
        selected = debug.get("selected") or []
        suppressed = debug.get("suppressed") or []
        reasons = [item.get("reason") for item in suppressed if item.get("reason")]
        print(f"domain: {domain}")
        print(f"selected_items: {len(selected)}")
        print(f"suppressed_items: {len(suppressed)}")
        if reasons:
            print(f"suppressed_reasons: {reasons[:5]}")
        print(f"slot_ratios: {debug.get('ratios')}")
        print(f"tone_profile: {debug.get('tone_profile')}")
        print()


def _domain_keys(domains: Mapping[str, Any], domain_filter: str | None) -> list[str]:
    if domain_filter:
        return [domain_filter] if domain_filter in domains else []
    return list(domains.keys())


def _self_check(
    response: Mapping[str, Any],
    domain_filter: str | None,
    *,
    expect_phase2: bool = False,
) -> None:
    core_story = response.get("core_story")
    print("DEBUG core_story repr:", repr(core_story))
    print("DEBUG core_story len:", len(core_story or ""))
    plan = response.get("core_story_plan") or {}
    print("DEBUG core_story_plan keys:", list(plan.keys()))
    sections = plan.get("sections") or []
    print("DEBUG core_story_plan sections:", len(sections))
    assert response.get("core_story_plan"), "core_story_plan missing"
    if expect_phase2:
        assert response.get("phase2_snapshot"), "phase2_snapshot missing"


if __name__ == "__main__":
    raise SystemExit(main())
