from __future__ import annotations

from typing import Any, Mapping, Sequence

from app.synastry.activation_engine import clamp01
from app.synastry.narrative.synastry_internal_builder import build_synastry_imprint_internal
from app.synastry.narrative.synastry_public_builder import build_synastry_imprint_public
from app.synastry.narrative.synastry_signature_router import (
    build_aspect_candidates,
    build_category_aggregates,
    build_directional_candidates,
    build_friction_point_candidates,
    build_pair_signature_candidates,
    build_sweet_spot_candidates,
    build_together_field_candidates,
)


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _source_overlap_ratio(source_keys: Sequence[str], used_source_keys: set[str]) -> float:
    keys = {str(item).strip() for item in source_keys if str(item).strip()}
    if not keys:
        return 0.0
    return len(keys & used_source_keys) / len(keys)


def _select_signature_block(
    candidates: Sequence[Mapping[str, Any]],
    *,
    limit: int,
    used_source_keys: set[str],
    banned_labels: set[str] | None = None,
    max_per_category: int = 1,
    max_overlap_ratio: float = 0.49,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    category_counts: dict[str, int] = {}
    banned_labels = banned_labels or set()
    selected_ids: set[str] = set()

    def _try_select(candidate: Mapping[str, Any], *, relaxed: bool) -> bool:
        label = str(candidate.get("label") or "").strip()
        category = str(candidate.get("category") or "").strip()
        overlap_ratio = _source_overlap_ratio(candidate.get("source_keys") or [], used_source_keys)
        candidate_id = str(candidate.get("id") or "").strip()
        if candidate_id and candidate_id in selected_ids:
            return False
        if not relaxed:
            if label and label in banned_labels and len(selected) + 1 < limit:
                return False
            if category and category_counts.get(category, 0) >= max_per_category and len(selected) + 1 < limit:
                return False
            if overlap_ratio > max_overlap_ratio and _safe_float(candidate.get("score")) < 0.76:
                return False
        selected.append(dict(candidate))
        if candidate_id:
            selected_ids.add(candidate_id)
        category_counts[category] = category_counts.get(category, 0) + 1
        used_source_keys.update(str(item).strip() for item in (candidate.get("source_keys") or []) if str(item).strip())
        return True

    for candidate in candidates:
        _try_select(candidate, relaxed=False)
        if len(selected) >= limit:
            break
    if len(selected) < limit:
        for candidate in candidates:
            _try_select(candidate, relaxed=True)
            if len(selected) >= limit:
                break
    return selected


def _select_text_block(
    candidates: Sequence[Mapping[str, Any]],
    *,
    limit: int,
    used_source_keys: set[str],
    max_overlap_ratio: float = 1.0,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for candidate in candidates:
        overlap_ratio = _source_overlap_ratio(candidate.get("source_keys") or [], used_source_keys)
        if overlap_ratio > max_overlap_ratio and _safe_float(candidate.get("score")) < 0.72:
            continue
        selected.append(dict(candidate))
        used_source_keys.update(str(item).strip() for item in (candidate.get("source_keys") or []) if str(item).strip())
        if len(selected) >= limit:
            break
    return selected


def _quality_gate(
    *,
    selection: Mapping[str, Sequence[Mapping[str, Any]]],
    corrected_scores: Mapping[str, Any],
    relationship_calibration: Mapping[str, Any],
) -> bool:
    pair_signature = list(selection.get("pair_signature") or [])
    a_to_b = list(selection.get("a_to_b") or [])
    b_to_a = list(selection.get("b_to_a") or [])
    together_field = list(selection.get("together_field") or [])
    sweet_spots = list(selection.get("sweet_spots") or [])
    friction_points = list(selection.get("friction_points") or [])
    if not pair_signature or not a_to_b or not b_to_a or not together_field or not sweet_spots or not friction_points:
        return False
    narrative_confidence = _safe_float(relationship_calibration.get("narrative_confidence"))
    base_confidence = _safe_float(corrected_scores.get("confidence"))
    avg_top = clamp01(
        (
            _safe_float(pair_signature[0].get("score"))
            + _safe_float(a_to_b[0].get("score"))
            + _safe_float(b_to_a[0].get("score"))
        ) / 3.0
    )
    if narrative_confidence < 0.4 and base_confidence < 0.42 and avg_top < 0.62:
        return False
    unique_sources = {
        str(source).strip()
        for block_name in ("pair_signature", "a_to_b", "b_to_a", "together_field")
        for item in selection.get(block_name) or []
        for source in item.get("source_keys") or []
        if str(source).strip()
    }
    return len(unique_sources) >= 5


def build_synastry_imprint(
    *,
    partner_a_name: str,
    partner_b_name: str,
    aspect_hits: Sequence[Mapping[str, Any]],
    overlays: Mapping[str, Any],
    domain_rankings: Mapping[str, Sequence[Mapping[str, Any]]],
    activation_bundles: Mapping[str, Sequence[Mapping[str, Any]]],
    corrected_scores: Mapping[str, Any],
    relationship_calibration: Mapping[str, Any],
) -> dict[str, Any]:
    partner_a_rows = list(domain_rankings.get("partner_a") or [])
    partner_b_rows = list(domain_rankings.get("partner_b") or [])
    partner_a_bundles = list(activation_bundles.get("partner_a") or [])
    partner_b_bundles = list(activation_bundles.get("partner_b") or [])

    aspect_candidates = build_aspect_candidates(
        aspect_hits=aspect_hits,
        partner_a_rows=partner_a_rows,
        partner_b_rows=partner_b_rows,
        corrected_scores=corrected_scores,
    )
    directional_candidates = {
        "a_to_b": build_directional_candidates(
            direction="a_to_b",
            overlay_table=list((overlays.get("a_in_b") or {}).get("table") or []),
            domain_rows=partner_b_rows,
            bundles=partner_b_bundles,
            aspect_candidates=aspect_candidates,
            corrected_scores=corrected_scores,
        ),
        "b_to_a": build_directional_candidates(
            direction="b_to_a",
            overlay_table=list((overlays.get("b_in_a") or {}).get("table") or []),
            domain_rows=partner_a_rows,
            bundles=partner_a_bundles,
            aspect_candidates=aspect_candidates,
            corrected_scores=corrected_scores,
        ),
    }
    aggregates = build_category_aggregates(
        directional_candidates=directional_candidates,
        aspect_candidates=aspect_candidates,
    )
    pair_candidates = build_pair_signature_candidates(
        aggregates=aggregates,
        aspect_candidates=aspect_candidates,
        corrected_scores=corrected_scores,
    )
    together_candidates = build_together_field_candidates(
        aggregates=aggregates,
        corrected_scores=corrected_scores,
    )
    sweet_candidates = build_sweet_spot_candidates(aggregates=aggregates)
    friction_candidates = build_friction_point_candidates(aggregates=aggregates)

    used_source_keys: set[str] = set()
    a_to_b = _select_signature_block(
        directional_candidates["a_to_b"],
        limit=3,
        used_source_keys=used_source_keys,
        max_overlap_ratio=0.7,
    )
    banned_labels = {str(item.get("label") or "").strip() for item in a_to_b}
    b_to_a = _select_signature_block(
        directional_candidates["b_to_a"],
        limit=3,
        used_source_keys=used_source_keys,
        banned_labels=banned_labels,
        max_overlap_ratio=0.7,
    )
    pair_signature = _select_signature_block(
        pair_candidates,
        limit=3,
        used_source_keys=used_source_keys,
        max_overlap_ratio=0.8,
    )
    together_field = _select_signature_block(
        together_candidates,
        limit=2,
        used_source_keys=used_source_keys,
        max_overlap_ratio=1.0,
    )
    sweet_spots = _select_text_block(sweet_candidates, limit=1, used_source_keys=used_source_keys)
    friction_points = _select_text_block(friction_candidates, limit=1, used_source_keys=used_source_keys)

    selection = {
        "pair_signature": pair_signature,
        "a_to_b": a_to_b,
        "b_to_a": b_to_a,
        "together_field": together_field,
        "sweet_spots": sweet_spots,
        "friction_points": friction_points,
    }
    if not _quality_gate(
        selection=selection,
        corrected_scores=corrected_scores,
        relationship_calibration=relationship_calibration,
    ):
        return {"public": None, "internal": None}
    return {
        "public": build_synastry_imprint_public(
            selection,
            partner_a_name=partner_a_name,
            partner_b_name=partner_b_name,
        ),
        "internal": build_synastry_imprint_internal(selection),
    }
