from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from app.transit.narrative.daily_selection import select_daily_and_period_event_cards
from app.transit.narrative.selection import select_event_ids

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _normalize_severity(value: Any) -> str:
    token = str(value or "").strip().lower()
    return token if token in {"high", "medium", "low"} else "medium"


def _normalize_tags(value: Any) -> List[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    tags: List[str] = []
    for raw in value:
        token = str(raw or "").strip().lower()
        if token and token not in tags:
            tags.append(token)
    return tags


def _load_json(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, Mapping) else {}


def _extract_artifact_payload(artifact: Mapping[str, Any]) -> Dict[str, Any]:
    public = artifact.get("public") if isinstance(artifact.get("public"), Mapping) else {}
    display = artifact.get("display") if isinstance(artifact.get("display"), Mapping) else {}
    request_echo = artifact.get("request_echo") if isinstance(artifact.get("request_echo"), Mapping) else {}
    raw_events = []
    if isinstance(display.get("items"), list):
        raw_events = display.get("items") or []
    elif isinstance(artifact.get("items_raw_unscored"), list):
        raw_events = artifact.get("items_raw_unscored") or []
    elif isinstance(artifact.get("items"), list):
        raw_events = artifact.get("items") or []
    event_cards = []
    if isinstance(public.get("event_cards"), list):
        event_cards = public.get("event_cards") or []
    elif isinstance(artifact.get("event_cards"), list):
        event_cards = artifact.get("event_cards") or []
    return {
        "natal": artifact.get("natal") if isinstance(artifact.get("natal"), Mapping) else {},
        "raw_events": raw_events,
        "event_cards": event_cards,
        "selected_date": str(
            request_echo.get("transit_date")
            or artifact.get("transit_date")
            or ""
        ).strip(),
    }


def _artifact_case_payload(case: Mapping[str, Any], *, base_dir: Path) -> Dict[str, Any]:
    out = dict(case)
    artifact_path = str(case.get("artifact_path") or "").strip()
    raw_artifact_path = str(case.get("raw_artifact_path") or "").strip()
    event_cards_artifact_path = str(case.get("event_cards_artifact_path") or "").strip()
    natal_artifact_path = str(case.get("natal_artifact_path") or "").strip()

    if artifact_path:
        artifact = _load_json((base_dir / artifact_path).resolve())
        extracted = _extract_artifact_payload(artifact)
        out.setdefault("natal", extracted["natal"])
        out.setdefault("raw_events", extracted["raw_events"])
        out.setdefault("event_cards", extracted["event_cards"])
        out.setdefault("selected_date", extracted["selected_date"])

    if raw_artifact_path:
        raw_artifact = _load_json((base_dir / raw_artifact_path).resolve())
        extracted = _extract_artifact_payload(raw_artifact)
        out.setdefault("raw_events", extracted["raw_events"])
        out.setdefault("selected_date", extracted["selected_date"])

    if event_cards_artifact_path:
        cards_artifact = _load_json((base_dir / event_cards_artifact_path).resolve())
        extracted = _extract_artifact_payload(cards_artifact)
        out.setdefault("event_cards", extracted["event_cards"])
        if not out.get("selected_date"):
            out["selected_date"] = extracted["selected_date"]

    if natal_artifact_path:
        natal_artifact = _load_json((base_dir / natal_artifact_path).resolve())
        extracted = _extract_artifact_payload(natal_artifact)
        out.setdefault("natal", extracted["natal"])

    return out


def _normalize_case(case: Mapping[str, Any], *, base_dir: Path, fixture_name: str) -> Dict[str, Any]:
    normalized = _artifact_case_payload(case, base_dir=base_dir)
    normalized["id"] = str(normalized.get("id") or f"{fixture_name}_{len(str(normalized))}")
    normalized["type"] = str(normalized.get("type") or "daily").strip().lower()
    normalized["severity"] = _normalize_severity(normalized.get("severity"))
    normalized["tags"] = _normalize_tags(normalized.get("tags"))
    normalized["notes"] = str(normalized.get("notes") or "").strip()
    normalized["surface"] = str(normalized.get("surface") or normalized["type"]).strip().lower()
    normalized["fixture_source"] = fixture_name
    normalized["watchlist_related"] = bool(normalized.get("watchlist_related")) or bool(normalized["tags"])
    return normalized


def load_benchmark_cases(path: str | Path) -> List[Dict[str, Any]]:
    file_path = Path(path)
    payload = _load_json(file_path)
    cases = payload.get("cases") if isinstance(payload, Mapping) else None
    return [
        _normalize_case(case, base_dir=file_path.parent, fixture_name=file_path.name)
        for case in (cases or [])
        if isinstance(case, Mapping)
    ]


def _surfaces_for_case(case: Mapping[str, Any]) -> List[str]:
    tags = set(_normalize_tags(case.get("tags")))
    surfaces = {str(case.get("surface") or case.get("type") or "daily").strip().lower() or "daily"}
    if "clustering" in tags:
        surfaces.add("clustering")
    if "fallback" in tags:
        surfaces.add("fallback")
    if "personalization" in tags:
        surfaces.add("personalization")
    if "narrative-quality" in tags or "narrative_quality" in tags:
        surfaces.add("narrative_quality")
    return sorted(surfaces)


def _group_failure_counts(cases: Sequence[Mapping[str, Any]]) -> Dict[str, Dict[str, int]]:
    by_severity: Dict[str, int] = {}
    by_category: Dict[str, int] = {}
    by_surface: Dict[str, int] = {}
    for case in cases:
        if bool(case.get("ok")):
            continue
        severity = _normalize_severity(case.get("severity"))
        by_severity[severity] = by_severity.get(severity, 0) + 1
        for tag in _normalize_tags(case.get("tags")):
            by_category[tag] = by_category.get(tag, 0) + 1
        for surface in _surfaces_for_case(case):
            by_surface[surface] = by_surface.get(surface, 0) + 1
    return {
        "by_severity": dict(sorted(by_severity.items(), key=lambda item: SEVERITY_ORDER.get(item[0], 9))),
        "by_category": dict(sorted(by_category.items())),
        "by_surface": dict(sorted(by_surface.items())),
    }


def _augment_report_with_baseline(report: Dict[str, Any], baseline_report: Mapping[str, Any] | None) -> None:
    if not isinstance(baseline_report, Mapping):
        return
    baseline_cases = baseline_report.get("cases") if isinstance(baseline_report, Mapping) else []
    current_cases = report.get("cases") if isinstance(report.get("cases"), list) else []
    baseline_failed = {
        str(case.get("id") or "")
        for case in baseline_cases
        if isinstance(case, Mapping) and not bool(case.get("ok"))
    }
    current_failed = {
        str(case.get("id") or "")
        for case in current_cases
        if isinstance(case, Mapping) and not bool(case.get("ok"))
    }
    report.setdefault("summary", {})
    report["summary"]["comparison"] = {
        "new_failures_since_baseline": sorted(current_failed - baseline_failed),
        "resolved_failures_since_baseline": sorted(baseline_failed - current_failed),
    }


def _bool_token(value: Any) -> str:
    return "yes" if bool(value) else "no"


def _daily_primary_result(daily_ids: Sequence[str]) -> str:
    return ", ".join(str(token) for token in daily_ids if token) or "-"


def _period_primary_result(selected_ids: Sequence[str]) -> str:
    return ", ".join(str(token) for token in selected_ids if token) or "-"


def _daily_evaluation_summary(selection_meta: Mapping[str, Any]) -> str:
    evaluation = {}
    selection_v3 = selection_meta.get("selection_v3") if isinstance(selection_meta.get("selection_v3"), Mapping) else {}
    if isinstance(selection_v3.get("evaluation"), Mapping):
        evaluation = selection_v3.get("evaluation") or {}
    return (
        f"candidates={int(evaluation.get('candidate_count') or 0)}, "
        f"avg_narrative={round(float(evaluation.get('avg_narrative_score') or 0.0), 3)}, "
        f"avg_delta={round(float(evaluation.get('avg_delta_salience_score') or 0.0), 3)}"
    )


def _period_evaluation_summary(evaluation: Mapping[str, Any]) -> str:
    return (
        f"spine={str(evaluation.get('spine_event_id') or '-')}, "
        f"role={str(evaluation.get('spine_role') or '-')}, "
        f"avg_story={round(float(evaluation.get('avg_story_score') or 0.0), 3)}"
    )


def _daily_case_result(case: Mapping[str, Any]) -> Dict[str, Any]:
    raw_events = [dict(item) for item in (case.get("raw_events") or []) if isinstance(item, Mapping)]
    event_cards = [dict(item) for item in (case.get("event_cards") or []) if isinstance(item, Mapping)]
    result = select_daily_and_period_event_cards(
        raw_events=raw_events,
        event_cards=event_cards,
        selected_date=str(case.get("selected_date") or ""),
        selected_day_context=dict(case.get("selected_day_context") or {}),
        natal=case.get("natal") if isinstance(case.get("natal"), Mapping) else {},
        event_v2_by_id=dict(case.get("event_v2_by_id") or {}),
    )
    daily_ids = [str(card.get("event_id") or "") for card in (result.get("daily_event_cards") or []) if isinstance(card, Mapping)]
    period_ids = [str(card.get("event_id") or "") for card in (result.get("period_event_cards") or []) if isinstance(card, Mapping)]
    expected = case.get("expected") if isinstance(case.get("expected"), Mapping) else {}
    expected_daily = str(expected.get("daily_event_id") or "")
    expected_fallback = expected.get("used_period_fallback")
    if expected_fallback is None and "fallback_expected" in expected:
        expected_fallback = expected.get("fallback_expected")
    expected_clustering = expected.get("clustering_expected")
    expected_personalization = expected.get("personalization_expected")
    expected_daily_contains = {str(token).strip() for token in (expected.get("daily_contains") or []) if str(token).strip()}
    expected_daily_not_contains = {str(token).strip() for token in (expected.get("daily_not_contains") or []) if str(token).strip()}

    ok = True
    reasons: List[str] = []
    if expected_daily and (not daily_ids or daily_ids[0] != expected_daily):
        ok = False
        reasons.append(f"expected daily {expected_daily}, got {daily_ids[0] if daily_ids else ''}")
    missing_daily = [token for token in expected_daily_contains if token not in daily_ids]
    if missing_daily:
        ok = False
        reasons.append(f"missing daily ids: {missing_daily}")
    unexpected_daily = [token for token in expected_daily_not_contains if token in daily_ids]
    if unexpected_daily:
        ok = False
        reasons.append(f"unexpected daily ids: {unexpected_daily}")
    if expected_fallback is not None and bool((result.get("daily_selection") or {}).get("used_period_fallback")) != bool(expected_fallback):
        ok = False
        reasons.append("fallback flag mismatch")

    selection_meta = dict(result.get("daily_selection") or {})
    selection_v3 = selection_meta.get("selection_v3") if isinstance(selection_meta.get("selection_v3"), Mapping) else {}
    clusters = selection_v3.get("experience_clusters") if isinstance(selection_v3.get("experience_clusters"), Sequence) else []
    clustering_used = any(int(cluster.get("cluster_size") or 0) > 1 for cluster in clusters if isinstance(cluster, Mapping))
    score_breakdown = selection_meta.get("score_breakdown") if isinstance(selection_meta.get("score_breakdown"), Mapping) else {}
    personalization_present = any(
        float((score_breakdown.get(event_id) or {}).get("personalization_score") or 0.0) > 0.0
        for event_id in score_breakdown
    )
    if expected_clustering is not None and clustering_used != bool(expected_clustering):
        ok = False
        reasons.append("clustering flag mismatch")
    if expected_personalization is not None and personalization_present != bool(expected_personalization):
        ok = False
        reasons.append("personalization flag mismatch")
    return {
        "id": str(case.get("id") or ""),
        "type": "daily",
        "surface": str(case.get("surface") or "daily"),
        "severity": _normalize_severity(case.get("severity")),
        "tags": _normalize_tags(case.get("tags")),
        "notes": str(case.get("notes") or ""),
        "watchlist_related": bool(case.get("watchlist_related")) or bool(_normalize_tags(case.get("tags"))),
        "fixture_source": str(case.get("fixture_source") or ""),
        "ok": ok,
        "reasons": reasons,
        "daily_event_ids": daily_ids,
        "period_event_ids": period_ids,
        "selection_meta": selection_meta,
        "fallback_used": bool(selection_meta.get("used_period_fallback")),
        "clustering_used": clustering_used,
        "personalization_present": personalization_present,
        "primary_result": _daily_primary_result(daily_ids),
        "evaluation_summary": _daily_evaluation_summary(selection_meta),
    }


def _period_case_result(case: Mapping[str, Any]) -> Dict[str, Any]:
    events = [dict(item) for item in (case.get("raw_events") or case.get("events") or []) if isinstance(item, Mapping)]
    max_cards = int(case.get("max_cards") or 5)
    selected, meta = select_event_ids(
        events,
        max_cards=max_cards,
        natal=case.get("natal") if isinstance(case.get("natal"), Mapping) else {},
        focus_date=str(case.get("selected_date") or case.get("focus_date") or "") or None,
    )
    selected_ids = [str(item.get("event_id") or "") for item in selected]
    expected = case.get("expected") if isinstance(case.get("expected"), Mapping) else {}
    expected_spine = str(expected.get("spine_event_id") or "")
    expected_spine_any_of = {str(token).strip() for token in (expected.get("spine_any_of") or []) if str(token).strip()}
    expected_selected_any_of = {str(token).strip() for token in (expected.get("selected_any_of") or []) if str(token).strip()}
    expected_contains = {str(token).strip() for token in (expected.get("selected_contains") or []) if str(token).strip()}
    expected_not_contains = {str(token).strip() for token in (expected.get("selected_not_contains") or []) if str(token).strip()}
    expected_support_contains = {str(token).strip() for token in (expected.get("support_contains") or []) if str(token).strip()}
    expected_support_not_contains = {str(token).strip() for token in (expected.get("support_not_contains") or []) if str(token).strip()}
    expected_personalization = expected.get("personalization_expected")
    min_roles = expected.get("minimum_distinct_roles")
    min_domains = expected.get("minimum_distinct_domains")

    ok = True
    reasons: List[str] = []
    if expected_spine and (not selected_ids or selected_ids[0] != expected_spine):
        ok = False
        reasons.append(f"expected spine {expected_spine}, got {selected_ids[0] if selected_ids else ''}")
    if expected_spine_any_of and (not selected_ids or selected_ids[0] not in expected_spine_any_of):
        ok = False
        reasons.append(f"spine not in acceptable set: {sorted(expected_spine_any_of)}")
    if expected_selected_any_of and not expected_selected_any_of.intersection(selected_ids):
        ok = False
        reasons.append(f"selected set missing any-of ids: {sorted(expected_selected_any_of)}")
    missing = [token for token in expected_contains if token not in selected_ids]
    if missing:
        ok = False
        reasons.append(f"missing selected ids: {missing}")
    unexpected = [token for token in expected_not_contains if token in selected_ids]
    if unexpected:
        ok = False
        reasons.append(f"unexpected selected ids: {unexpected}")

    evaluation = dict(meta.get("evaluation") or {})
    support_ids = selected_ids[1:]
    missing_support = [token for token in expected_support_contains if token not in support_ids]
    if missing_support:
        ok = False
        reasons.append(f"missing support ids: {missing_support}")
    unexpected_support = [token for token in expected_support_not_contains if token in support_ids]
    if unexpected_support:
        ok = False
        reasons.append(f"unexpected support ids: {unexpected_support}")
    personalization_present = float(evaluation.get("avg_personalization_bonus") or 0.0) > 0.0
    if expected_personalization is not None and personalization_present != bool(expected_personalization):
        ok = False
        reasons.append("personalization flag mismatch")
    if min_roles is not None and int(evaluation.get("distinct_roles") or 0) < int(min_roles):
        ok = False
        reasons.append(f"distinct roles below minimum: {int(evaluation.get('distinct_roles') or 0)} < {int(min_roles)}")
    if min_domains is not None and int(evaluation.get("distinct_domains") or 0) < int(min_domains):
        ok = False
        reasons.append(f"distinct domains below minimum: {int(evaluation.get('distinct_domains') or 0)} < {int(min_domains)}")
    return {
        "id": str(case.get("id") or ""),
        "type": "period",
        "surface": str(case.get("surface") or "period"),
        "severity": _normalize_severity(case.get("severity")),
        "tags": _normalize_tags(case.get("tags")),
        "notes": str(case.get("notes") or ""),
        "watchlist_related": bool(case.get("watchlist_related")) or bool(_normalize_tags(case.get("tags"))),
        "fixture_source": str(case.get("fixture_source") or ""),
        "ok": ok,
        "reasons": reasons,
        "selected_ids": selected_ids,
        "selection_mode": meta.get("selection_mode"),
        "evaluation": evaluation,
        "fallback_used": False,
        "clustering_used": False,
        "personalization_present": personalization_present,
        "primary_result": _period_primary_result(selected_ids),
        "evaluation_summary": _period_evaluation_summary(evaluation),
    }


def _combined_case_result(case: Mapping[str, Any]) -> Dict[str, Any]:
    daily_result = _daily_case_result(case)
    period_result = _period_case_result(case)
    ok = bool(daily_result.get("ok")) and bool(period_result.get("ok"))
    reasons = list(daily_result.get("reasons") or []) + list(period_result.get("reasons") or [])
    return {
        "id": str(case.get("id") or ""),
        "type": "combined",
        "surface": str(case.get("surface") or "combined"),
        "severity": _normalize_severity(case.get("severity")),
        "tags": _normalize_tags(case.get("tags")),
        "notes": str(case.get("notes") or ""),
        "watchlist_related": bool(case.get("watchlist_related")) or bool(_normalize_tags(case.get("tags"))),
        "fixture_source": str(case.get("fixture_source") or ""),
        "ok": ok,
        "reasons": reasons,
        "daily_event_ids": daily_result.get("daily_event_ids") or [],
        "period_event_ids": daily_result.get("period_event_ids") or [],
        "selected_ids": period_result.get("selected_ids") or [],
        "selection_mode": period_result.get("selection_mode"),
        "selection_meta": daily_result.get("selection_meta") or {},
        "evaluation": period_result.get("evaluation") or {},
        "fallback_used": bool(daily_result.get("fallback_used")),
        "clustering_used": bool(daily_result.get("clustering_used")),
        "personalization_present": bool(daily_result.get("personalization_present")) or bool(period_result.get("personalization_present")),
        "primary_result": (
            f"daily={daily_result.get('primary_result') or '-'} | "
            f"period={period_result.get('primary_result') or '-'}"
        ),
        "evaluation_summary": (
            f"{daily_result.get('evaluation_summary') or '-'} | "
            f"{period_result.get('evaluation_summary') or '-'}"
        ),
    }


def _summary_block(summary: Mapping[str, Any]) -> List[Dict[str, Any]]:
    grouped = summary.get("grouped_failure_counts") if isinstance(summary.get("grouped_failure_counts"), Mapping) else {}
    return [
        {"label": "total", "value": int(summary.get("total") or 0)},
        {"label": "passed", "value": int(summary.get("passed") or 0)},
        {"label": "failed", "value": int(summary.get("failed") or 0)},
        {"label": "high_severity_failures", "value": len(summary.get("high_severity_failures") or [])},
        {"label": "watchlist_related_failures", "value": len(summary.get("watchlist_related_failures") or [])},
        {"label": "failure_groups_by_surface", "value": dict(grouped.get("by_surface") or {})},
        {"label": "failure_groups_by_category", "value": dict(grouped.get("by_category") or {})},
    ]


def run_selection_benchmark(
    cases: Sequence[Mapping[str, Any]],
    *,
    baseline_report: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    passed = 0

    for raw_case in cases:
        case = dict(raw_case)
        case_type = str(case.get("type") or "daily").strip().lower()
        if case_type == "period":
            result = _period_case_result(case)
        elif case_type == "combined":
            result = _combined_case_result(case)
        else:
            result = _daily_case_result(case)
        results.append(result)
        if result["ok"]:
            passed += 1

    failed_cases = [case for case in results if not bool(case.get("ok"))]
    failed_cases_sorted = sorted(
        failed_cases,
        key=lambda case: (
            SEVERITY_ORDER.get(_normalize_severity(case.get("severity")), 9),
            str(case.get("id") or ""),
        ),
    )
    summary = {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "grouped_failure_counts": _group_failure_counts(results),
        "high_severity_failures": [
            str(case.get("id") or "")
            for case in failed_cases_sorted
            if _normalize_severity(case.get("severity")) == "high"
        ],
        "watchlist_related_failures": [
            str(case.get("id") or "")
            for case in failed_cases_sorted
            if bool(case.get("watchlist_related"))
        ],
    }
    summary["summary_block"] = _summary_block(summary)
    report = {
        "summary": summary,
        "cases": results,
        "top_regressions": failed_cases_sorted[:5],
    }
    _augment_report_with_baseline(report, baseline_report)
    return report


def render_selection_benchmark_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False)


def render_selection_benchmark_markdown(report: Mapping[str, Any]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), Mapping) else {}
    grouped = summary.get("grouped_failure_counts") if isinstance(summary.get("grouped_failure_counts"), Mapping) else {}
    comparison = summary.get("comparison") if isinstance(summary.get("comparison"), Mapping) else {}
    cases = report.get("cases") if isinstance(report.get("cases"), Sequence) else []
    top_regressions = report.get("top_regressions") if isinstance(report.get("top_regressions"), Sequence) else []

    lines = [
        "# Selection Benchmark",
        "",
        "## Summary",
        "",
        f"- Total: {int(summary.get('total') or 0)}",
        f"- Passed: {int(summary.get('passed') or 0)}",
        f"- Failed: {int(summary.get('failed') or 0)}",
        f"- High severity failures: {len(summary.get('high_severity_failures') or [])}",
        f"- Watchlist-related failures: {len(summary.get('watchlist_related_failures') or [])}",
        "",
        "## Failure Groups",
        "",
        f"- By severity: {dict(grouped.get('by_severity') or {})}",
        f"- By surface: {dict(grouped.get('by_surface') or {})}",
        f"- By category: {dict(grouped.get('by_category') or {})}",
        "",
    ]

    if comparison:
        lines.extend(
            [
                "## Baseline Compare",
                "",
                f"- New failures since baseline: {list(comparison.get('new_failures_since_baseline') or [])}",
                f"- Resolved failures since baseline: {list(comparison.get('resolved_failures_since_baseline') or [])}",
                "",
            ]
        )

    lines.extend(["## Top Regressions", ""])
    if top_regressions:
        for case in top_regressions:
            lines.append(
                f"- `{case.get('id')}` [{_normalize_severity(case.get('severity'))}] "
                f"{str(case.get('surface') or case.get('type') or '')}: {'; '.join(case.get('reasons') or []) or '-'}"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| Case | Type | Surface | Severity | Status | Primary Result | Eval Summary | Fallback | Cluster | Personalization | Fixture | Notes |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for case in cases:
        if not isinstance(case, Mapping):
            continue
        status = "PASS" if bool(case.get("ok")) else "FAIL"
        notes = "; ".join(str(token) for token in (case.get("reasons") or [])) or str(case.get("notes") or "-")
        lines.append(
            f"| {str(case.get('id') or '')} | {str(case.get('type') or '')} | {str(case.get('surface') or '')} | "
            f"{_normalize_severity(case.get('severity'))} | {status} | {str(case.get('primary_result') or '-')} | "
            f"{str(case.get('evaluation_summary') or '-')} | {_bool_token(case.get('fallback_used'))} | "
            f"{_bool_token(case.get('clustering_used'))} | {_bool_token(case.get('personalization_present'))} | "
            f"{str(case.get('fixture_source') or '-')} | {notes} |"
        )
    return "\n".join(lines).strip() + "\n"


def render_selection_benchmark_csv(report: Mapping[str, Any]) -> str:
    output = io.StringIO()
    fieldnames = [
        "row_type",
        "summary_group",
        "summary_key",
        "summary_value",
        "id",
        "type",
        "surface",
        "severity",
        "ok",
        "tags",
        "primary_result",
        "evaluation_summary",
        "fallback_used",
        "clustering_used",
        "personalization_present",
        "watchlist_related",
        "fixture_source",
        "notes",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    summary = report.get("summary") if isinstance(report.get("summary"), Mapping) else {}
    grouped = summary.get("grouped_failure_counts") if isinstance(summary.get("grouped_failure_counts"), Mapping) else {}
    for key in ["total", "passed", "failed"]:
        writer.writerow(
            {
                "row_type": "summary",
                "summary_group": "headline",
                "summary_key": key,
                "summary_value": summary.get(key),
            }
        )
    writer.writerow(
        {
            "row_type": "summary",
            "summary_group": "headline",
            "summary_key": "high_severity_failures",
            "summary_value": len(summary.get("high_severity_failures") or []),
        }
    )
    writer.writerow(
        {
            "row_type": "summary",
            "summary_group": "headline",
            "summary_key": "watchlist_related_failures",
            "summary_value": len(summary.get("watchlist_related_failures") or []),
        }
    )
    for group_name in ["by_severity", "by_surface", "by_category"]:
        for key, value in dict(grouped.get(group_name) or {}).items():
            writer.writerow(
                {
                    "row_type": "summary",
                    "summary_group": group_name,
                    "summary_key": key,
                    "summary_value": value,
                }
            )
    comparison = summary.get("comparison") if isinstance(summary.get("comparison"), Mapping) else {}
    for key in ["new_failures_since_baseline", "resolved_failures_since_baseline"]:
        if key in comparison:
            writer.writerow(
                {
                    "row_type": "summary",
                    "summary_group": "comparison",
                    "summary_key": key,
                    "summary_value": ",".join(str(token) for token in (comparison.get(key) or [])),
                }
            )

    cases = report.get("cases") if isinstance(report.get("cases"), Sequence) else []
    for case in cases:
        if not isinstance(case, Mapping):
            continue
        writer.writerow(
            {
                "row_type": "case",
                "id": str(case.get("id") or ""),
                "type": str(case.get("type") or ""),
                "surface": str(case.get("surface") or ""),
                "severity": _normalize_severity(case.get("severity")),
                "ok": bool(case.get("ok")),
                "tags": ",".join(_normalize_tags(case.get("tags"))),
                "primary_result": str(case.get("primary_result") or ""),
                "evaluation_summary": str(case.get("evaluation_summary") or ""),
                "fallback_used": bool(case.get("fallback_used")),
                "clustering_used": bool(case.get("clustering_used")),
                "personalization_present": bool(case.get("personalization_present")),
                "watchlist_related": bool(case.get("watchlist_related")),
                "fixture_source": str(case.get("fixture_source") or ""),
                "notes": "; ".join(str(token) for token in (case.get("reasons") or [])) or str(case.get("notes") or ""),
            }
        )
    return output.getvalue()
