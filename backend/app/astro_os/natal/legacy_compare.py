from __future__ import annotations

import re
from typing import Any, Mapping

from .contracts import CanonicalNatalStateV1


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _collect_texts(value: Any, *, source: str, out: list[dict[str, Any]]) -> None:
    if isinstance(value, str):
        text = _normalize_text(value)
        if text:
            out.append({"source": source, "text": text})
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            _collect_texts(item, source=f"{source}.{key}", out=out)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _collect_texts(item, source=f"{source}[{index}]", out=out)


def _legacy_surface_texts(base_payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    texts: list[dict[str, Any]] = []
    for surface_key in (
        "personality_imprint",
        "profile_narrative",
        "sections_v2",
        "supporting_threads",
        "profile_v8",
    ):
        _collect_texts(base_payload.get(surface_key), source=surface_key, out=texts)
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in texts:
        key = (item["source"], item["text"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _surface_counts(base_payload: Mapping[str, Any]) -> dict[str, int]:
    return {
        "personality_imprint_entries": len(_as_list(_as_dict(base_payload.get("personality_imprint")).get("entries"))),
        "personality_imprint_extra_entries": len(_as_list(_as_dict(base_payload.get("personality_imprint")).get("extra_entries"))),
        "profile_narrative_blocks": len(
            _as_list(_as_dict(_as_dict(base_payload.get("profile_narrative")).get("profile_public")).get("blocks"))
        ),
        "sections_v2": len(_as_list(base_payload.get("sections_v2"))),
        "supporting_threads": len(_as_list(base_payload.get("supporting_threads"))),
        "profile_v8_differentiators": len(_as_list(_as_dict(base_payload.get("profile_v8")).get("differentiators"))),
    }


def _canonical_texts(state: CanonicalNatalStateV1) -> list[str]:
    texts: list[str] = []
    for promise in state.core_promises:
        texts.extend(
            [
                _normalize_text(promise.theme),
                _normalize_text(promise.psychological_pattern),
                _normalize_text(promise.growth_path),
            ]
        )
    for contradiction in state.contradictions:
        texts.extend(
            [
                _normalize_text(contradiction.title),
                _normalize_text(contradiction.integration_path),
            ]
        )
    for line in (
        state.chart_spine.primary_identity_line,
        state.chart_spine.emotional_regulation_line,
        state.chart_spine.relational_line,
        state.chart_spine.work_visibility_line,
        state.chart_spine.shadow_protection_line,
        state.chart_spine.growth_integration_line,
    ):
        texts.extend([_normalize_text(line.title), _normalize_text(line.summary)])
    return [text for text in texts if text]


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]{4,}", text.lower()) if token}


def _coverage_score(text: str, canonical_texts: list[str]) -> float:
    text_tokens = _tokenize(text)
    if not text_tokens:
        return 0.0
    best = 0.0
    for candidate in canonical_texts:
        candidate_tokens = _tokenize(candidate)
        if not candidate_tokens:
            continue
        overlap = len(text_tokens & candidate_tokens) / len(text_tokens | candidate_tokens)
        best = max(best, overlap)
    return round(best, 4)


def compare_legacy_branches_to_canonical_state(
    *,
    base_payload: Mapping[str, Any],
    canonical_state: CanonicalNatalStateV1,
) -> dict[str, Any]:
    legacy_texts = _legacy_surface_texts(base_payload)
    canonical_texts = _canonical_texts(canonical_state)
    coverage_rows = [
        {
            "source": item["source"],
            "text": item["text"],
            "coverage_score": _coverage_score(item["text"], canonical_texts),
        }
        for item in legacy_texts
    ]
    phrase_rescue_candidates = [
        row
        for row in coverage_rows
        if row["coverage_score"] < 0.18 and 24 <= len(row["text"]) <= 180
    ][:12]
    semantic_loss_risks = [
        row
        for row in coverage_rows
        if row["coverage_score"] < 0.08
    ][:12]
    return {
        "legacy_surface_counts": _surface_counts(base_payload),
        "canonical_counts": {
            "core_promises": len(canonical_state.core_promises),
            "contradictions": len(canonical_state.contradictions),
            "spine_lines": len(
                [
                    line
                    for line in (
                        canonical_state.chart_spine.primary_identity_line,
                        canonical_state.chart_spine.emotional_regulation_line,
                        canonical_state.chart_spine.relational_line,
                        canonical_state.chart_spine.work_visibility_line,
                        canonical_state.chart_spine.shadow_protection_line,
                        canonical_state.chart_spine.growth_integration_line,
                    )
                    if line.node_id
                ]
            ),
        },
        "coverage_rows": coverage_rows[:40],
        "phrase_rescue_candidates": phrase_rescue_candidates,
        "semantic_loss_risks": semantic_loss_risks,
    }
