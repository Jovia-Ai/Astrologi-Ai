from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

_ROOT = Path(__file__).resolve().parents[3]
_ITEM_BANK_PATH = _ROOT / "config" / "classifiers" / "archetype_item_bank_v1.yaml"


def _clamp01(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _read_jsonish(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8").strip()
    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1].replace('\\"', '"')
    return json.loads(raw)


@lru_cache(maxsize=1)
def _item_bank() -> Dict[str, Any]:
    return _read_jsonish(_ITEM_BANK_PATH)


def current_question_bank_version() -> str:
    return _safe_text(_item_bank().get("version")) or "archetype_item_bank_v1"


def _normalize_answer_value(value: Any) -> float:
    number = _safe_float(value)
    if 0.0 <= number <= 1.0:
        return _clamp01(number)
    if 1.0 <= number <= 5.0:
        return _clamp01((number - 1.0) / 4.0)
    if 0.0 <= number <= 4.0:
        return _clamp01(number / 4.0)
    if 0.0 <= number <= 100.0:
        return _clamp01(number / 100.0)
    return _clamp01(number)


def _to_mapping(value: Any) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "model_dump"):
        payload = value.model_dump(exclude_none=True)
        if isinstance(payload, Mapping):
            return dict(payload)
    if hasattr(value, "dict"):
        payload = value.dict(exclude_none=True)
        if isinstance(payload, Mapping):
            return dict(payload)
    return {}


def build_public_question_bank(locale: str = "tr") -> Dict[str, Any]:
    bank = _item_bank()
    questions: list[dict[str, Any]] = []
    for entry in bank.get("questions") or []:
        if not isinstance(entry, Mapping):
            continue
        prompt = _safe_text(entry.get(f"prompt_{locale}")) or _safe_text(entry.get("prompt_tr"))
        if not prompt:
            continue
        questions.append(
            {
                "id": _safe_text(entry.get("id")),
                "prompt": prompt,
                "family": _safe_text(entry.get("family")),
                "stage": _safe_text(entry.get("stage")) or "core",
                "axis_hint": _safe_text(entry.get("axis_hint")),
                "order": int(_safe_float(entry.get("order"))),
            }
        )
    questions.sort(key=lambda item: (item["order"], item["id"]))
    core_count = sum(1 for item in questions if item["stage"] == "core")
    adaptive_count = sum(1 for item in questions if item["stage"] == "adaptive")
    return {
        "version": current_question_bank_version(),
        "locale": locale or "tr",
        "scale": dict(bank.get("scale") or {}),
        "summary": {
            "total_questions": len(questions),
            "core_questions": core_count,
            "adaptive_questions": adaptive_count,
        },
        "questions": questions,
    }


def score_archetype_answers(answers: Sequence[Any] | None) -> Dict[str, Any]:
    bank = _item_bank()
    item_lookup = {
        _safe_text(item.get("id")): dict(item)
        for item in bank.get("questions") or []
        if isinstance(item, Mapping) and _safe_text(item.get("id"))
    }

    available_weights: Dict[str, float] = {}
    for item in item_lookup.values():
        for archetype_id, archetype_weight in (item.get("weights") or {}).items():
            archetype_key = _safe_text(archetype_id)
            if not archetype_key:
                continue
            available_weights[archetype_key] = available_weights.get(archetype_key, 0.0) + max(
                _safe_float(archetype_weight),
                0.0,
            )

    totals: Dict[str, float] = {}
    weights: Dict[str, float] = {}
    matched_values: Dict[str, float] = {}
    matched_items: list[str] = []

    for raw_answer in answers or []:
        answer = _to_mapping(raw_answer)
        item_id = _safe_text(answer.get("item_id"))
        item = item_lookup.get(item_id)
        if item is None:
            continue
        value = _normalize_answer_value(answer.get("value"))
        if bool(item.get("reverse_scored")):
            value = 1.0 - value
        matched_values[item_id] = round(value, 4)
        matched_items.append(item_id)

        response_weight = max(
            _safe_float(answer.get("weight"), _safe_float(item.get("weight"), 1.0)),
            0.0,
        ) or 1.0
        for archetype_id, archetype_weight in (item.get("weights") or {}).items():
            archetype_key = _safe_text(archetype_id)
            if not archetype_key:
                continue
            contribution_weight = response_weight * max(_safe_float(archetype_weight), 0.0)
            if contribution_weight <= 0:
                continue
            totals[archetype_key] = totals.get(archetype_key, 0.0) + (value * contribution_weight)
            weights[archetype_key] = weights.get(archetype_key, 0.0) + contribution_weight

    scores: Dict[str, float] = {}
    coverage: Dict[str, float] = {}
    for archetype_id, total in totals.items():
        answered_weight = weights.get(archetype_id, 0.0)
        available_weight = max(available_weights.get(archetype_id, 0.0), 1e-6)
        if answered_weight <= 0:
            continue
        normalized_mean = total / max(answered_weight, 1e-6)
        coverage_ratio = _clamp01(answered_weight / available_weight)
        coverage[archetype_id] = round(coverage_ratio, 4)
        scores[archetype_id] = round(_clamp01(normalized_mean * coverage_ratio), 4)

    pair_scores: list[float] = []
    for pair in bank.get("consistency_pairs") or []:
        if not isinstance(pair, Sequence) or len(pair) != 2:
            continue
        first = matched_values.get(_safe_text(pair[0]))
        second = matched_values.get(_safe_text(pair[1]))
        if first is None or second is None:
            continue
        pair_scores.append(round(_clamp01(1.0 - abs(first - second)), 4))

    return {
        "scores": scores,
        "answer_consistency": round(sum(pair_scores) / len(pair_scores), 4) if pair_scores else None,
        "answered_count": len(set(matched_items)),
        "question_bank_version": current_question_bank_version(),
        "debug": {
            "coverage_by_archetype": coverage,
            "matched_item_ids": sorted(set(matched_items)),
            "consistency_pair_count": len(pair_scores),
        },
    }
