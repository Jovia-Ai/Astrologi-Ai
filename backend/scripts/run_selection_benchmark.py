from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.transit.narrative.selection_benchmark import (
    load_benchmark_cases,
    render_selection_benchmark_csv,
    render_selection_benchmark_json,
    render_selection_benchmark_markdown,
    run_selection_benchmark,
)


DEFAULT_FIXTURE = Path(__file__).resolve().parents[1] / "tests" / "_fixtures" / "selection_benchmark_cases.json"
DEFAULT_GOLDEN_FIXTURE = Path(__file__).resolve().parents[1] / "tests" / "_fixtures" / "golden_days.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run offline selection benchmark and export report.")
    parser.add_argument("--fixture", default="")
    parser.add_argument("--fixture-set", choices=["benchmark", "golden", "combined"], default="benchmark")
    parser.add_argument("--baseline-report", default="")
    parser.add_argument("--output", default="")
    parser.add_argument("--format", choices=["json", "md", "csv"], default="")
    args = parser.parse_args()

    fixture_paths = []
    if args.fixture:
        fixture_paths = [Path(args.fixture)]
    elif args.fixture_set == "golden":
        fixture_paths = [DEFAULT_GOLDEN_FIXTURE]
    elif args.fixture_set == "combined":
        fixture_paths = [DEFAULT_FIXTURE, DEFAULT_GOLDEN_FIXTURE]
    else:
        fixture_paths = [DEFAULT_FIXTURE]

    cases = []
    for fixture_path in fixture_paths:
        cases.extend(load_benchmark_cases(fixture_path))

    baseline_report = None
    if args.baseline_report:
        baseline_report = json.loads(Path(args.baseline_report).read_text(encoding="utf-8"))
    report = run_selection_benchmark(cases, baseline_report=baseline_report)
    report_format = args.format.strip().lower()
    if not report_format and args.output:
        suffix = Path(args.output).suffix.lower()
        report_format = {"json": "json", ".json": "json", ".md": "md", ".markdown": "md", ".csv": "csv"}.get(suffix, "json")
    if not report_format:
        report_format = "json"

    if report_format == "md":
        rendered = render_selection_benchmark_markdown(report)
    elif report_format == "csv":
        rendered = render_selection_benchmark_csv(report)
    else:
        rendered = render_selection_benchmark_json(report)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(rendered, encoding="utf-8")
        print(str(output_path))
        return

    print(rendered)


if __name__ == "__main__":
    main()
