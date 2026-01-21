"""Run transit engine with a sample payload."""
from __future__ import annotations

import argparse
import json

from app.engine.transit_engine import build_transit_report


SAMPLES = {
    "my_chart": {
        "birth_date": "1991-03-12",
        "birth_time": "09:30",
        "birth_place": "Istanbul, TR",
    }
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", default="my_chart")
    parser.add_argument("--date", required=True)
    parser.add_argument("--time", default="12:00")
    parser.add_argument("--place", required=True)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    sample = SAMPLES.get(args.sample)
    if not sample:
        raise SystemExit(f"Unknown sample: {args.sample}")

    payload = build_transit_report(
        birth_date=sample["birth_date"],
        birth_time=sample["birth_time"],
        birth_place=sample["birth_place"],
        transit_date=args.date,
        transit_time=args.time,
        transit_place=args.place,
        options={"debug": args.debug},
        assumptions=[],
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
