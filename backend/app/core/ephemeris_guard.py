"""Swiss Ephemeris startup guard.

The natal/transit pipeline silently degrades when ephemeris files are
missing — Chiron / Juno / extended bodies fail to compute and downstream
charts go subtly wrong. This module makes the failure mode loud and
explicit: if the minimum required set is not on disk under the resolved
ephemeris path, raise immediately.

Required minimum set must match `REQUIRED_FILES` in
`backend/scripts/setup_ephemeris.sh`. Update both together.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

# Minimum required ephemeris files for natal + transit math up to ~year 2100
# (Sun/Moon/Planets in the 1800-2399 epoch chunk — covers all current users).
# Keep in sync with backend/scripts/setup_ephemeris.sh REQUIRED_FILES.
REQUIRED_EPHE_FILES: tuple[str, ...] = (
    "seas_18.se1",  # asteroid (Chiron etc.) — 1800-2399
    "sepl_18.se1",  # planets — 1800-2399
    "semo_18.se1",  # moon — 1800-2399
)


class EphemerisMissingError(RuntimeError):
    """Raised when the Swiss Ephemeris setup is incomplete."""


def missing_files(ephe_path: str | Path, required: Sequence[str] = REQUIRED_EPHE_FILES) -> list[str]:
    """Return the names of required files that are absent or empty."""
    base = Path(ephe_path)
    missing: list[str] = []
    for name in required:
        target = base / name
        if not target.is_file() or target.stat().st_size == 0:
            missing.append(name)
    return missing


def assert_ephemeris_ready(
    ephe_path: str | Path,
    *,
    required: Sequence[str] = REQUIRED_EPHE_FILES,
) -> None:
    """Raise `EphemerisMissingError` if any required file is missing/empty.

    No silent fallback: by the time the route handlers run, this must have
    succeeded — otherwise PySwissEph degrades quietly to default-noon
    placeholders for the affected bodies.
    """
    base = Path(ephe_path)
    if not base.exists():
        raise EphemerisMissingError(
            f"Swiss Ephemeris directory does not exist: {base}. "
            f"Run `bash backend/scripts/setup_ephemeris.sh` "
            f"or set SE_EPHE_PATH to a directory containing: "
            f"{', '.join(required)}."
        )
    if not base.is_dir():
        raise EphemerisMissingError(
            f"Swiss Ephemeris path is not a directory: {base}."
        )
    absent = missing_files(base, required=required)
    if absent:
        raise EphemerisMissingError(
            "Swiss Ephemeris missing required files in "
            f"{base}: {', '.join(absent)}. "
            "Run `bash backend/scripts/setup_ephemeris.sh` to install."
        )


def _format_required(required: Iterable[str]) -> str:
    return ", ".join(required)
