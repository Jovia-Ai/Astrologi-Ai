"""Freeze OLD-config transit output into canonical JSON artifacts.

The frozen artifact is the pristine pre-PR1 baseline: wide orbs (6/6/6/6/4),
major aspects only (conj/opp/sq/tri/sex), no out-of-sign filter, linear orb
decay. As the engine evolves, the baseline stays byte-for-byte stable so
benchmark comparisons don't drift.

Each artifact is a JSON file under tests/_artifacts/bench_baseline_sprint1/
containing:

  metadata:  fixture descriptor (birth data, classification, body set,
             engine config, creation timestamp, SHA256 hash of the
             canonicalized payload)
  payload:   { "<transit_date>": [ aspect, ... ], ... }

The hash covers the canonicalized `payload` only (not metadata) — computed
over `json.dumps(payload, sort_keys=True, separators=(",", ":"))`. Floats
in the payload are rounded to 4 decimals before serialization for
cross-platform stability.

Usage:
    PYTHONPATH=backend python backend/scripts/freeze_baseline.py
    PYTHONPATH=backend python backend/scripts/freeze_baseline.py --verify

--verify: reads existing artifacts and recomputes the hash to detect drift.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
EPHE_DIR = BACKEND_ROOT / "ephe"
ARTIFACT_DIR = BACKEND_ROOT / "tests" / "_artifacts" / "bench_baseline_sprint1"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("SUPABASE_URL", "https://bench.local")
os.environ.setdefault("SUPABASE_KEY", "bench")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "bench")

import swisseph  # noqa: E402

swisseph.set_ephe_path(str(EPHE_DIR))

from app.engine.transit_engine import build_transit_report  # noqa: E402


CLASSIFICATION_CRITERIA_VERSION = "v1"

BODY_SET_LABEL = "traditional_10"
BODY_SET = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

BENCH_DATES = ["2026-02-01", "2026-03-04", "2026-05-15", "2026-08-21", "2026-11-10"]

OLD_ENGINE_CONFIG = {
    "label": "OLD (pre-PR1: wide orbs, no minor aspects, no OOS filter, linear decay)",
    "orbs": {"conjunction": 6.0, "opposition": 6.0, "square": 6.0, "trine": 6.0, "sextile": 4.0},
    "aspect_types": ["conjunction", "opposition", "square", "trine", "sextile"],
    "apply_out_of_sign_filter": False,
    # orb_decay_mode: linear (implicit default in this codebase; PR6 will add
    # the flag. Frozen baseline always reflects linear, regardless of what
    # the live engine defaults to in the future.)
    "orb_decay_mode": "linear",
}


FIXTURES: List[Dict[str, Any]] = [
    {
        "name": "simple",
        "birth": {
            "date": "1996-12-28",
            "time": "07:10",
            "place": "Istanbul",
            "latitude": 41.0082,
            "longitude": 28.9784,
            "timezone": "Europe/Istanbul",
        },
        "classification": {
            "primary_profile": "SIMPLE",
            "secondary_traits": [],
            "notes": (
                "No tight stellium (traditional 10 bodies). No body within 5° of ASC/MC/DSC/IC. "
                "Chart ruler Saturn at 1.16° Aries in cadent H3. Real birth data."
            ),
        },
    },
    {
        "name": "angular_heavy",
        "birth": {
            "date": "1995-12-24",
            "time": "13:44",
            "place": "Lucerne",
            "latitude": 47.0502,
            "longitude": 8.3093,
            "timezone": "Europe/Zurich",
        },
        "classification": {
            "primary_profile": "ANGULAR_HEAVY",
            "secondary_traits": [],
            "notes": (
                "Three traditional bodies within 5° of MC: Mercury 1.2°, Mars 1.9°, Neptune 4.2°. "
                "No tight stellium. Real birth data."
            ),
        },
    },
    {
        "name": "stellium",
        "birth": {
            "date": "2015-09-10",
            "time": "12:00",
            "place": "Istanbul",
            "latitude": 41.0082,
            "longitude": 28.9784,
            "timezone": "Europe/Istanbul",
        },
        "classification": {
            "primary_profile": "STELLIUM",
            "secondary_traits": [],
            "notes": (
                "SYNTHETIC FIXTURE — not a real person's chart. Birth time 12:00 is a NOON PLACEHOLDER. "
                "Moon is time-sensitive (~13°/day), so real-time charts on this date will differ. "
                "At noon Istanbul: Leo stellium — Moon + Venus + Mars, span 6.0°. Primary trait = STELLIUM. "
                "Intended as a controlled synthetic test case for stellium sensitivity logic."
            ),
        },
    },
]


def _round_floats(obj: Any, decimals: int = 4) -> Any:
    if isinstance(obj, float):
        return round(obj, decimals)
    if isinstance(obj, dict):
        return {k: _round_floats(v, decimals) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(v, decimals) for v in obj]
    return obj


def _canonical_payload_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _hash_payload(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_payload_bytes(payload)).hexdigest()


def _aspects_for(report: Mapping[str, Any]) -> List[Dict[str, Any]]:
    asp = report.get("aspects", {}) or {}
    return list(asp.get("transit_to_natal", []) or []) + list(asp.get("transit_to_angles", []) or [])


def _minimal_aspect(a: Mapping[str, Any]) -> Dict[str, Any]:
    """Strip the full aspect payload down to fields that drive ranking + narrative.

    Keeping only these fields makes the frozen baseline resilient to cosmetic
    engine changes (e.g. adding a new metadata field on aspects). Ranking and
    retention checks never read the extra fields anyway.
    """
    natal = a.get("natal") or {}
    target = natal.get("body") or natal.get("angle") or natal.get("point") or ""
    return {
        "type": a.get("type"),
        "orb": a.get("orb"),
        "strength": a.get("strength"),
        "polarity": a.get("polarity"),
        "phase": a.get("phase"),
        "out_of_sign": bool(a.get("out_of_sign", False)),
        "transit_body": (a.get("transit") or {}).get("body"),
        "target": target,
    }


def _build_payload(birth: Mapping[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    payload: Dict[str, List[Dict[str, Any]]] = {}
    for td in BENCH_DATES:
        report = build_transit_report(
            birth_date=birth["date"],
            birth_time=birth["time"],
            birth_place=birth["place"],
            birth_latitude=birth["latitude"],
            birth_longitude=birth["longitude"],
            birth_timezone=birth["timezone"],
            transit_date=td,
            transit_time="12:00",
            transit_place=birth["place"],
            transit_latitude=birth["latitude"],
            transit_longitude=birth["longitude"],
            transit_timezone=birth["timezone"],
            options={
                "orbs": OLD_ENGINE_CONFIG["orbs"],
                "aspect_types": OLD_ENGINE_CONFIG["aspect_types"],
                "include_angles": True,
                "max_aspects_per_transit_body": 99,
                "apply_out_of_sign_filter": OLD_ENGINE_CONFIG["apply_out_of_sign_filter"],
            },
            assumptions=[],
        )
        aspects = [_minimal_aspect(a) for a in _aspects_for(report)]
        aspects.sort(key=lambda a: (
            -(a.get("strength") or 0.0),
            a.get("orb") or 0.0,
            a.get("transit_body") or "",
            a.get("target") or "",
            a.get("type") or "",
        ))
        payload[td] = aspects
    return _round_floats(payload)


def _build_artifact(fixture: Mapping[str, Any]) -> Dict[str, Any]:
    payload = _build_payload(fixture["birth"])
    hash_hex = _hash_payload(payload)
    metadata = {
        "fixture_name": fixture["name"],
        "birth_data": fixture["birth"],
        "classification": fixture["classification"],
        "classification_criteria_version": CLASSIFICATION_CRITERIA_VERSION,
        "body_set_label": BODY_SET_LABEL,
        "body_set": BODY_SET,
        "benchmark_dates": BENCH_DATES,
        "engine_config": OLD_ENGINE_CONFIG,
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hash_algorithm": "sha256",
        "hash_scope": "payload_only",
        "hash_canonical_form": "json.dumps(payload, sort_keys=True, separators=(',',':'), ensure_ascii=False) UTF-8 bytes; floats rounded to 4 decimals",
        "hash_of_canonical_payload": hash_hex,
    }
    return {"metadata": metadata, "payload": payload}


def _write_artifact(path: Path, artifact: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, sort_keys=True, indent=2, ensure_ascii=False)
        f.write("\n")


def freeze() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    for fixture in FIXTURES:
        artifact = _build_artifact(fixture)
        path = ARTIFACT_DIR / f"{fixture['name']}.json"
        _write_artifact(path, artifact)
        n = sum(len(v) for v in artifact["payload"].values())
        print(f"froze {fixture['name']}: {n} aspects across {len(artifact['payload'])} dates "
              f"→ {path.relative_to(REPO_ROOT)} [hash={artifact['metadata']['hash_of_canonical_payload'][:12]}…]")


def verify() -> int:
    """Recompute hash of each artifact's payload and compare to stored metadata hash."""
    failures = 0
    for fixture in FIXTURES:
        path = ARTIFACT_DIR / f"{fixture['name']}.json"
        if not path.exists():
            print(f"MISSING: {path}")
            failures += 1
            continue
        with path.open("r", encoding="utf-8") as f:
            artifact = json.load(f)
        stored = artifact["metadata"]["hash_of_canonical_payload"]
        recomputed = _hash_payload(artifact["payload"])
        ok = stored == recomputed
        status = "OK" if ok else "MISMATCH"
        print(f"{status}: {fixture['name']} stored={stored[:12]}… recomputed={recomputed[:12]}…")
        if not ok:
            failures += 1
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Verify stored hashes without regenerating")
    args = parser.parse_args()
    if args.verify:
        rc = verify()
        sys.exit(1 if rc else 0)
    freeze()


if __name__ == "__main__":
    main()
