from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

_ROOT = Path(__file__).resolve().parents[3]
_ITEM_BANK_PATH = _ROOT / "config" / "classifiers" / "archetype_item_bank_v2.yaml"

_DEFAULT_ADAPTIVE_RULES = {
    "core_gap_trigger": 0.10,
    "subprofile_gap_trigger": 0.08,
    "max_families": 3,
    "max_questions": 4,
}


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
    return _safe_text(_item_bank().get("version")) or "archetype_item_bank_v2"


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


def _question_payload(entry: Mapping[str, Any], *, locale: str = "tr") -> Dict[str, Any]:
    prompt = _safe_text(entry.get(f"prompt_{locale}")) or _safe_text(entry.get("prompt_tr"))
    return {
        "id": _safe_text(entry.get("id")),
        "prompt": prompt,
        "family": _safe_text(entry.get("family")),
        "stage": _safe_text(entry.get("stage")) or "core",
        "axis_hint": _safe_text(entry.get("axis_hint")),
        "order": int(_safe_float(entry.get("order"))),
    }


def _questions_by_stage(locale: str = "tr") -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    core: list[dict[str, Any]] = []
    adaptive: list[dict[str, Any]] = []
    for entry in _item_bank().get("questions") or []:
        if not isinstance(entry, Mapping):
            continue
        payload = _question_payload(entry, locale=locale)
        if not payload["id"] or not payload["prompt"]:
            continue
        if payload["stage"] == "adaptive":
            adaptive.append(payload)
        else:
            core.append(payload)
    core.sort(key=lambda item: (item["order"], item["id"]))
    adaptive.sort(key=lambda item: (item["order"], item["id"]))
    return core, adaptive


def build_public_question_bank(locale: str = "tr") -> Dict[str, Any]:
    bank = _item_bank()
    core, adaptive = _questions_by_stage(locale=locale or "tr")
    adaptive_family_map: Dict[str, list[dict[str, Any]]] = {}
    for question in adaptive:
        family = _safe_text(question.get("family"))
        if not family:
            continue
        adaptive_family_map.setdefault(family, []).append(dict(question))
    return {
        "version": current_question_bank_version(),
        "locale": locale or "tr",
        "scale": dict(bank.get("scale") or {}),
        "summary": {
            "total_questions": len(core) + len(adaptive),
            "default_questions": len(core),
            "core_questions": len(core),
            "adaptive_questions": len(adaptive),
        },
        "questions": core,
        "adaptive_questions": adaptive,
        "all_questions": [*core, *adaptive],
        "adaptive_rules": dict(_DEFAULT_ADAPTIVE_RULES),
        "adaptive_family_map": adaptive_family_map,
    }


def select_adaptive_questions(
    *,
    families: Sequence[str] | None,
    locale: str = "tr",
    limit: int | None = None,
    exclude_ids: Iterable[str] = (),
) -> list[dict[str, Any]]:
    _, adaptive = _questions_by_stage(locale=locale or "tr")
    excluded = {_safe_text(item) for item in exclude_ids if _safe_text(item)}
    wanted_families = [_safe_text(item) for item in families or [] if _safe_text(item)]
    selected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    effective_limit = max(limit or _DEFAULT_ADAPTIVE_RULES["max_questions"], 1)

    def add_question(question: Mapping[str, Any]) -> None:
        question_id = _safe_text(question.get("id"))
        if not question_id or question_id in excluded or question_id in seen_ids:
            return
        selected.append(dict(question))
        seen_ids.add(question_id)

    for family in wanted_families:
        for question in adaptive:
            if _safe_text(question.get("family")) != family:
                continue
            add_question(question)
            if len(selected) >= effective_limit:
                return selected

    for question in adaptive:
        add_question(question)
        if len(selected) >= effective_limit:
            break
    return selected


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
    family_totals: Dict[str, float] = {}
    family_weights: Dict[str, float] = {}
    stage_counts = {"core": 0, "adaptive": 0}
    answered_families: set[str] = set()

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

        stage = _safe_text(item.get("stage")) or "core"
        if stage == "adaptive":
            stage_counts["adaptive"] += 1
        else:
            stage_counts["core"] += 1

        family = _safe_text(item.get("family"))
        if family:
            answered_families.add(family)

        response_weight = max(
            _safe_float(answer.get("weight"), _safe_float(item.get("weight"), 1.0)),
            0.0,
        ) or 1.0
        if family:
            family_totals[family] = family_totals.get(family, 0.0) + (value * response_weight)
            family_weights[family] = family_weights.get(family, 0.0) + response_weight

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

    family_scores = {
        family: round(_clamp01(total / max(family_weights.get(family, 1.0), 1e-6)), 4)
        for family, total in family_totals.items()
        if family_weights.get(family, 0.0) > 0
    }

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
        "family_scores": family_scores,
        "answer_consistency": round(sum(pair_scores) / len(pair_scores), 4) if pair_scores else None,
        "answered_count": len(set(matched_items)),
        "adaptive_answered_count": stage_counts["adaptive"],
        "question_bank_version": current_question_bank_version(),
        "debug": {
            "coverage_by_archetype": coverage,
            "matched_item_ids": sorted(set(matched_items)),
            "consistency_pair_count": len(pair_scores),
            "family_scores": family_scores,
            "stage_counts": stage_counts,
            "answered_families": sorted(answered_families),
        },
    }
