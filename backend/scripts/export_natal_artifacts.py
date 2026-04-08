from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable

EXPECTED_BIRTH_DATETIME = "1996-12-28T07:10:00+02:00"
EXPECTED_TIMEZONE = "Europe/Istanbul"
EXPECTED_LOCATION = {
    "city": "Istanbul, TR",
    "latitude": 41.0082,
    "longitude": 28.9784,
    "timezone": EXPECTED_TIMEZONE,
}

ARTIFACT_FILES = {
    "raw": "natal_full_1996-12-28_07-10_istanbul.json",
    "full": "natal_interpret_full_1996-12-28_07-10_istanbul_debug.json",
    "user_compact": "natal_interpret_full_1996-12-28_07-10_istanbul_user_compact_debug.json",
}

RAW_REQUIRED_KEYS = {"location", "birth_datetime", "timezone", "planets", "houses", "house_positions"}
INTERPRETATION_REQUIRED_KEYS = {"metadata", "planets", "aspects"}


def artifact_root() -> Path:
    return Path(__file__).resolve().parents[1] / "tests" / "_artifacts"


def resolve_artifact_paths() -> dict[str, Path]:
    root = artifact_root()
    return {variant: root / filename for variant, filename in ARTIFACT_FILES.items()}


def load_artifact(variant: str) -> dict[str, Any]:
    path = resolve_artifact_paths()[variant]
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_variants(selected: Iterable[str] | None) -> tuple[str, ...]:
    items = tuple(selected or ())
    if not items or "all" in items:
        return tuple(ARTIFACT_FILES)
    return tuple(dict.fromkeys(items))


def validate_artifacts(variants: Iterable[str]) -> None:
    for variant in normalize_variants(variants):
        payload = load_artifact(variant)
        if variant == "raw":
            _validate_raw(payload)
        else:
            _validate_interpretation(payload, variant=variant)


def export_artifacts(output_dir: str | Path, variants: Iterable[str]) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []
    for variant in normalize_variants(variants):
        source = resolve_artifact_paths()[variant]
        target = destination / source.name
        shutil.copy2(source, target)
        copied.append(target)
    return copied


def _validate_location(location: Any) -> None:
    if not isinstance(location, dict):
        raise ValueError("location must be an object.")
    for key, expected in EXPECTED_LOCATION.items():
        actual = location.get(key)
        if actual != expected:
            raise ValueError(f"location.{key} mismatch: expected {expected!r}, got {actual!r}")


def _validate_raw(payload: dict[str, Any]) -> None:
    missing = RAW_REQUIRED_KEYS - payload.keys()
    if missing:
        raise ValueError(f"raw artifact is missing keys: {sorted(missing)}")
    if payload.get("birth_datetime") != EXPECTED_BIRTH_DATETIME:
        raise ValueError("raw artifact birth_datetime mismatch.")
    if payload.get("timezone") != EXPECTED_TIMEZONE:
        raise ValueError("raw artifact timezone mismatch.")
    _validate_location(payload.get("location"))


def _validate_interpretation(payload: dict[str, Any], *, variant: str) -> None:
    missing = INTERPRETATION_REQUIRED_KEYS - payload.keys()
    if missing:
        raise ValueError(f"{variant} artifact is missing keys: {sorted(missing)}")
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"{variant} artifact metadata must be an object.")
    if metadata.get("birth_datetime") != EXPECTED_BIRTH_DATETIME:
        raise ValueError(f"{variant} artifact birth_datetime mismatch.")
    if metadata.get("timezone") != EXPECTED_TIMEZONE:
        raise ValueError(f"{variant} artifact timezone mismatch.")
    _validate_location(metadata.get("location"))

    commentary_keys = set(payload) - INTERPRETATION_REQUIRED_KEYS
    if not commentary_keys:
        raise ValueError(f"{variant} artifact should include interpretation payload beyond metadata/planets/aspects.")


def build_manifest(variants: Iterable[str]) -> dict[str, Any]:
    return {
        "birth_data": {
            "birth_date": "1996-12-28",
            "birth_time": "07:10",
            "birth_place": "Istanbul, TR",
            "timezone": EXPECTED_TIMEZONE,
            "birth_datetime": EXPECTED_BIRTH_DATETIME,
        },
        "artifacts": {variant: str(resolve_artifact_paths()[variant]) for variant in normalize_variants(variants)},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and export the existing 1996-12-28 07:10 Istanbul natal artifact set."
    )
    parser.add_argument(
        "--variant",
        action="append",
        choices=("all", *ARTIFACT_FILES),
        help="Artifact variant to work with. Repeat for multiple variants. Defaults to all.",
    )
    parser.add_argument(
        "--output-dir",
        help="Copy the selected exact JSON artifacts into this directory without modifying their contents.",
    )
    parser.add_argument(
        "--print-paths",
        action="store_true",
        help="Print a JSON manifest of the selected artifact paths instead of emitting file contents.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the selected artifact set and print a short success message.",
    )
    args = parser.parse_args(argv)

    variants = normalize_variants(args.variant)
    validate_artifacts(variants)

    if args.output_dir:
        copied = export_artifacts(args.output_dir, variants)
        for path in copied:
            print(path)
        return 0

    if args.check:
        print(f"Validated {len(variants)} natal artifact(s) for {EXPECTED_BIRTH_DATETIME}.")
        return 0

    if args.print_paths or len(variants) > 1:
        json.dump(build_manifest(variants), sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    variant = variants[0]
    sys.stdout.write(resolve_artifact_paths()[variant].read_text(encoding="utf-8"))
    if not sys.stdout.isatty():
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
