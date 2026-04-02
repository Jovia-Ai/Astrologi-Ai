from pathlib import Path

from app.transit.narrative.selection_benchmark import (
    load_benchmark_cases,
    render_selection_benchmark_csv,
    render_selection_benchmark_markdown,
    run_selection_benchmark,
)


FIXTURE = Path(__file__).resolve().parent / "_fixtures" / "selection_benchmark_cases.json"
GOLDEN_FIXTURE = Path(__file__).resolve().parent / "_fixtures" / "golden_days.json"


def test_selection_benchmark_fixture_runs_clean() -> None:
    cases = load_benchmark_cases(FIXTURE)
    report = run_selection_benchmark(cases)

    assert report["summary"]["total"] == len(cases)
    assert report["summary"]["failed"] == 0
    assert all(case["ok"] for case in report["cases"])
    assert report["summary"]["grouped_failure_counts"]["by_surface"] == {}


def test_golden_fixture_loads_real_cases_and_runs_clean() -> None:
    cases = load_benchmark_cases(GOLDEN_FIXTURE)
    report = run_selection_benchmark(cases)

    assert len(cases) >= 20
    assert all(case["fixture_source"] == "golden_days.json" for case in cases)
    assert all(case["watchlist_related"] for case in cases)
    assert any(case["type"] == "combined" for case in cases)
    assert report["summary"]["failed"] == 0
    assert all(case["ok"] for case in report["cases"])
    assert report["summary"]["total"] == len(cases)


def test_selection_benchmark_renderers_include_summary_and_cases() -> None:
    cases = load_benchmark_cases(FIXTURE)
    report = run_selection_benchmark(cases)

    markdown = render_selection_benchmark_markdown(report)
    csv_text = render_selection_benchmark_csv(report)

    assert "# Selection Benchmark" in markdown
    assert "## Failure Groups" in markdown
    assert "## Top Regressions" in markdown
    assert "daily_personalized_career" in markdown
    assert "Eval Summary" in markdown
    assert "row_type,summary_group,summary_key,summary_value,id,type,surface,severity,ok,tags,primary_result,evaluation_summary,fallback_used,clustering_used,personalization_present,watchlist_related,fixture_source,notes" in csv_text
    assert "summary,headline,total" in csv_text
    assert "period_story_spine" in csv_text


def test_selection_benchmark_baseline_compare_reports_new_failures() -> None:
    cases = load_benchmark_cases(FIXTURE)
    cases[0]["expected"] = {"daily_event_id": "definitely_not_the_selected_event"}
    baseline = {
        "cases": [
            {"id": "daily_personalized_career", "ok": True},
            {"id": "daily_period_fallback_story", "ok": True},
        ]
    }
    report = run_selection_benchmark(cases, baseline_report=baseline)

    comparison = report["summary"]["comparison"]

    assert comparison["resolved_failures_since_baseline"] == []
    assert comparison["new_failures_since_baseline"] == ["daily_personalized_career"]


def test_golden_expectation_types_can_fail_cleanly() -> None:
    cases = load_benchmark_cases(GOLDEN_FIXTURE)
    target = next(case for case in cases if case["id"] == "golden_period_2026_03_04_spine")
    target["expected"]["minimum_distinct_roles"] = 99
    target["expected"]["support_contains"] = ["definitely_missing_support"]
    report = run_selection_benchmark([target])

    result = report["cases"][0]

    assert result["ok"] is False
    assert any("distinct roles below minimum" in reason for reason in result["reasons"])
    assert any("missing support ids" in reason for reason in result["reasons"])
