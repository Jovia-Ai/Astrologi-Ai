"""Faz 1 öncesi natal payload baseline snapshot suite.

10 referans natal için `/interpret/ui` çıktısı (public payload + _debug_timing
hariç) JSON snapshot olarak kaydedilir. Faz 1 refactor'ları sonrası çıktı
değişirse diff burada yakalanır.

İlk çalıştırmada (snapshot yoksa) baseline'lar üretilir. Sonraki
çalıştırmalarda mevcut snapshot ile karşılaştırma yapılır.

Snapshot'ları kasten yenilemek için: `REGENERATE_NATAL_V8_SNAPSHOTS=1` env
var'ı ile çalıştır.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest

from app.api.routes import natal_interpretation


_FIXTURES_PATH = Path(__file__).parent / "_fixtures" / "natal_v8_baseline.json"
_SNAPSHOT_DIR = Path(__file__).parent / "_artifacts" / "natal_v8_baseline"
_VOLATILE_KEYS = {"_debug_timing", "cache_status", "cache_write"}


def _load_fixtures() -> list[Dict[str, Any]]:
    payload = json.loads(_FIXTURES_PATH.read_text(encoding="utf-8"))
    return list(payload.get("fixtures") or [])


def _strip_volatile(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {
            key: _strip_volatile(value)
            for key, value in payload.items()
            if key not in _VOLATILE_KEYS
        }
    if isinstance(payload, list):
        return [_strip_volatile(item) for item in payload]
    return payload


def _build_request(fixture: Dict[str, Any]) -> natal_interpretation.NatalInterpretationRequest:
    return natal_interpretation.NatalInterpretationRequest(
        birth_date=fixture["birth_date"],
        birth_time=fixture["birth_time"],
        birth_place=fixture["birth_place"],
        birth_latitude=fixture.get("birth_latitude"),
        birth_longitude=fixture.get("birth_longitude"),
        birth_timezone=fixture.get("birth_timezone"),
        locale="tr",
        summary_only=False,
    )


def _snapshot_path(fixture_id: str) -> Path:
    return _SNAPSHOT_DIR / f"{fixture_id}.json"


def _serialize(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


@pytest.mark.parametrize(
    "fixture",
    _load_fixtures(),
    ids=lambda fx: fx["id"],
)
def test_natal_v8_baseline_snapshot(fixture: Dict[str, Any]) -> None:
    """Her referans natal için public payload baseline ile eşleşmeli."""
    request = _build_request(fixture)
    response = natal_interpretation.interpret_natal_chart_ui(
        request,
        debug=False,
        include_debug=False,
        profile_engine=None,
    )
    cleaned = _strip_volatile(copy.deepcopy(response))
    snapshot_path = _snapshot_path(fixture["id"])
    regenerate = os.getenv("REGENERATE_NATAL_V8_SNAPSHOTS") == "1"

    if not snapshot_path.exists() or regenerate:
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(_serialize(cleaned), encoding="utf-8")
        if not regenerate:
            pytest.skip(
                f"baseline snapshot generated: {snapshot_path.name} "
                "(re-run to enforce)"
            )
        return

    expected = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if cleaned != expected:
        diff_summary = _diff_summary(expected, cleaned)
        pytest.fail(
            f"natal v8 baseline drifted for {fixture['id']}:\n{diff_summary}\n"
            f"Snapshot: {snapshot_path}\n"
            "Set REGENERATE_NATAL_V8_SNAPSHOTS=1 to accept."
        )


def _diff_summary(expected: Any, actual: Any, path: str = "$", max_items: int = 12) -> str:
    diffs: list[str] = []

    def _walk(exp: Any, act: Any, p: str) -> None:
        if len(diffs) >= max_items:
            return
        if type(exp) is not type(act):
            diffs.append(f"{p}: type {type(exp).__name__} -> {type(act).__name__}")
            return
        if isinstance(exp, dict):
            keys = set(exp.keys()) | set(act.keys())
            for key in sorted(keys):
                if key not in exp:
                    diffs.append(f"{p}.{key}: ADDED")
                elif key not in act:
                    diffs.append(f"{p}.{key}: REMOVED")
                else:
                    _walk(exp[key], act[key], f"{p}.{key}")
        elif isinstance(exp, list):
            if len(exp) != len(act):
                diffs.append(f"{p}: list len {len(exp)} -> {len(act)}")
            for idx, (a, b) in enumerate(zip(exp, act)):
                _walk(a, b, f"{p}[{idx}]")
        elif exp != act:
            diffs.append(
                f"{p}: {repr(exp)[:60]} -> {repr(act)[:60]}"
            )

    _walk(expected, actual, path)
    if not diffs:
        return "(no symbolic diff)"
    if len(diffs) >= max_items:
        diffs.append(f"... ({max_items}+ differences truncated)")
    return "\n".join(diffs)
