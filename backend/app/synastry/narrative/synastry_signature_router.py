from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from app.astro.orb_policy import tightness as _orb_policy_tightness
from app.synastry.activation_engine import clamp01
from app.synastry.narrative.synastry_library_tr import (
    SYNSTRY_CATEGORY_BUNDLE_SUPPORT,
    SYNSTRY_CATEGORY_DOMAINS,
    SYNSTRY_CATEGORY_SCORE_CHANNEL,
    SYNSTRY_POSITIVE_CATEGORIES,
    SYNSTRY_SIGNATURE_LIBRARY_INDEX_TR_V1,
    SYNSTRY_TENSION_CATEGORIES,
    aspect_signature_key,
    overlay_signature_key,
)
from app.synastry.narrative.synastry_phrase_bank_tr import (
    FRICTION_POINT_TEMPLATES,
    PAIR_SIGNATURE_TEMPLATES,
    SWEET_SPOT_TEMPLATES,
    TOGETHER_FIELD_TEMPLATES,
    soft_astro_hint_from_sources,
)


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _domain_peak(rows: Sequence[Mapping[str, Any]], category: str) -> float:
    domains = SYNSTRY_CATEGORY_DOMAINS.get(category, ())
    best = 0.0
    for row in rows:
        domain = str(row.get("domain") or "")
        if domain not in domains:
            continue
        best = max(best, _safe_float(row.get("score")))
    return clamp01(best)


def _bundle_peak(bundles: Sequence[Mapping[str, Any]], category: str) -> float:
    kinds = set(SYNSTRY_CATEGORY_BUNDLE_SUPPORT.get(category, ()))
    best = 0.0
    for bundle in bundles:
        if str(bundle.get("kind") or "") not in kinds:
            continue
        best = max(best, _safe_float(bundle.get("score")))
    return clamp01(best)


def _channel_support(category: str, corrected_scores: Mapping[str, Any]) -> float:
    key = SYNSTRY_CATEGORY_SCORE_CHANNEL.get(category, "bond")
    return clamp01(_safe_float(corrected_scores.get(key)))


def _orb_tightness(hit: Mapping[str, Any]) -> float:
    """Synastry aspect tightness — zero-orb 'missing data' sentinel.

    Tek kaynak `app.astro.orb_policy.tightness`. Synastry konvansiyonu
    korunur: orb<=0 → 0.0. Natal ile semantik farkı `zero_orb_as_missing`
    flag'iyle açık.

    TODO(faz1-pr4): orb=0 hit'leri gerçekten missing mi yoksa exact 0° aspect
    olarak sayılmalı mı — synastry data kaynağıyla birlikte gözden geçir.
    """
    aspect = str(hit.get("aspect") or "").lower()
    orb = _safe_float(hit.get("orb_deg"))
    return _orb_policy_tightness(aspect, orb, zero_orb_as_missing=True)


def _aspect_source_key(hit: Mapping[str, Any]) -> str:
    left = str(hit.get("a_body") or "").lower()
    right = str(hit.get("b_body") or "").lower()
    aspect = str(hit.get("aspect") or "").lower()
    ordered = ":".join(sorted([left, right]))
    return f"aspect:{ordered}:{aspect}"


def _aspect_debug_line(hit: Mapping[str, Any]) -> str:
    left = str(hit.get("a_body") or "").lower()
    right = str(hit.get("b_body") or "").lower()
    aspect = str(hit.get("aspect") or "").lower()
    orb = _safe_float(hit.get("orb_deg"))
    return f"{left}-{right} {aspect} {round(orb, 2)}°"


def _overlay_debug_line(direction: str, body: str, house: int) -> str:
    if direction == "a_to_b":
        return f"A {body} in B {house}th"
    return f"B {body} in A {house}th"


def _directionalize_copy(text: str, direction: str) -> str:
    value = str(text or "").strip()
    if not value or direction == "a_to_b":
        return value
    placeholders = {
        "A, B'de": "__LABEL__",
        "A'nın": "__A_POS__",
        "B'nin": "__B_GEN__",
        "B'ye": "__B_TO__",
        "B'de": "__B_IN__",
    }
    for source, placeholder in placeholders.items():
        value = value.replace(source, placeholder)
    replacements = {
        "__LABEL__": "B, A'da",
        "__A_POS__": "B'nin",
        "__B_GEN__": "A'nın",
        "__B_TO__": "A'ya",
        "__B_IN__": "A'da",
    }
    for placeholder, target in replacements.items():
        value = value.replace(placeholder, target)
    return value


def build_aspect_candidates(
    *,
    aspect_hits: Sequence[Mapping[str, Any]],
    partner_a_rows: Sequence[Mapping[str, Any]],
    partner_b_rows: Sequence[Mapping[str, Any]],
    corrected_scores: Mapping[str, Any],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for hit in aspect_hits:
        key = aspect_signature_key(hit.get("a_body"), hit.get("b_body"), hit.get("aspect"))
        entry = SYNSTRY_SIGNATURE_LIBRARY_INDEX_TR_V1.get(key)
        if not entry:
            continue
        category = str(entry.get("category") or "")
        domain_peak = max(_domain_peak(partner_a_rows, category), _domain_peak(partner_b_rows, category))
        orb_bonus = 0.18 * _orb_tightness(hit)
        channel_bonus = 0.10 * _channel_support(category, corrected_scores)
        score = clamp01((0.68 * _safe_float(entry.get("base_score"))) + (0.12 * domain_peak) + (0.12 * _orb_tightness(hit)) + (0.06 * _channel_support(category, corrected_scores)))
        source_debug = [_aspect_debug_line(hit)]
        candidates.append(
            {
                "id": str(entry.get("key") or ""),
                "category": category,
                "label": str(entry.get("label_tr") or "").strip(),
                "one_liner": str(entry.get("one_liner") or "").strip(),
                "shadow_line": str(entry.get("shadow_line") or "").strip(),
                "score": round(score, 4),
                "confidence": round(score, 4),
                "astro_hint_soft": str(entry.get("astro_hint_soft") or "").strip(),
                "source_keys": [_aspect_source_key(hit)],
                "source_debug": source_debug,
                "primary_signature_id": str(entry.get("key") or ""),
                "support_signature_ids": [],
                "tone_family": str(entry.get("tone_family") or ""),
                "source_family": "aspect",
                "direction": "pair",
                "polarity": str(entry.get("polarity") or "mixed"),
            }
        )
    return sorted(candidates, key=lambda item: (-_safe_float(item.get("score")), str(item.get("id") or "")))


def build_directional_candidates(
    *,
    direction: str,
    overlay_table: Sequence[Mapping[str, Any]],
    domain_rows: Sequence[Mapping[str, Any]],
    bundles: Sequence[Mapping[str, Any]],
    aspect_candidates: Sequence[Mapping[str, Any]],
    corrected_scores: Mapping[str, Any],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for row in overlay_table:
        body = str(row.get("body") or "").strip().lower()
        house = int(row.get("in_house") or 0)
        key = overlay_signature_key(body, house)
        entry = SYNSTRY_SIGNATURE_LIBRARY_INDEX_TR_V1.get(key)
        if not entry:
            continue
        category = str(entry.get("category") or "")
        matching_aspects = [
            aspect
            for aspect in aspect_candidates
            if str(aspect.get("category") or "") == category
            or body in " ".join(aspect.get("source_debug") or []).lower()
        ]
        aspect_support = max((_safe_float(item.get("score")) for item in matching_aspects), default=0.0)
        domain_peak = _domain_peak(domain_rows, category)
        bundle_bonus = 0.14 * _bundle_peak(bundles, category)
        channel_bonus = 0.08 * _channel_support(category, corrected_scores)
        aspect_bonus = 0.08 * aspect_support
        score = clamp01((0.72 * _safe_float(entry.get("base_score"))) + (0.12 * domain_peak) + (0.10 * _bundle_peak(bundles, category)) + (0.04 * _channel_support(category, corrected_scores)) + (0.06 * aspect_support))
        source_debug = [_overlay_debug_line(direction, body, house)]
        support_signature_ids = [str(item.get("id") or "") for item in matching_aspects[:2] if str(item.get("id") or "")]
        for aspect in matching_aspects[:2]:
            source_debug.extend(aspect.get("source_debug") or [])
        candidates.append(
            {
                "id": f"{direction}:{key}",
                "category": category,
                "label": _directionalize_copy(str(entry.get("label_tr") or "").strip(), direction),
                "one_liner": _directionalize_copy(str(entry.get("one_liner") or "").strip(), direction),
                "shadow_line": _directionalize_copy(str(entry.get("shadow_line") or "").strip(), direction),
                "score": round(score, 4),
                "confidence": round(score, 4),
                "astro_hint_soft": str(entry.get("astro_hint_soft") or "").strip(),
                "source_keys": [f"{direction}:overlay:{body}:{house}"],
                "source_debug": source_debug[:4],
                "primary_signature_id": key,
                "support_signature_ids": support_signature_ids[:3],
                "tone_family": str(entry.get("tone_family") or ""),
                "source_family": "overlay",
                "direction": direction,
                "polarity": str(entry.get("polarity") or "mixed"),
            }
        )
    return sorted(candidates, key=lambda item: (-_safe_float(item.get("score")), str(item.get("id") or "")))


def build_category_aggregates(
    *,
    directional_candidates: Mapping[str, Sequence[Mapping[str, Any]]],
    aspect_candidates: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    grouped: Dict[str, dict[str, Any]] = {}
    all_candidates = list(aspect_candidates)
    for direction in ("a_to_b", "b_to_a"):
        all_candidates.extend(directional_candidates.get(direction) or [])
    for item in all_candidates:
        category = str(item.get("category") or "")
        if not category:
            continue
        bucket = grouped.setdefault(
            category,
            {
                "items": [],
                "source_keys": [],
                "source_debug": [],
                "directions": set(),
                "signal_families": set(),
            },
        )
        bucket["items"].append(item)
        bucket["source_keys"].extend(item.get("source_keys") or [])
        bucket["source_debug"].extend(item.get("source_debug") or [])
        direction = str(item.get("direction") or "")
        if direction in {"a_to_b", "b_to_a"}:
            bucket["directions"].add(direction)
        bucket["signal_families"].add(str(item.get("source_family") or ""))

    out: dict[str, dict[str, Any]] = {}
    for category, bucket in grouped.items():
        items = sorted(bucket["items"], key=lambda item: -_safe_float(item.get("score")))
        top_score = _safe_float(items[0].get("score")) if items else 0.0
        avg_top = sum(_safe_float(item.get("score")) for item in items[:2]) / max(1, min(2, len(items)))
        direction_balance = len(bucket["directions"]) / 2.0
        signal_diversity = min(1.0, len(bucket["signal_families"]) / 2.0)
        aspect_presence = 1.0 if any(str(item.get("source_family") or "") == "aspect" for item in items) else 0.0
        score = clamp01(
            (0.48 * top_score)
            + (0.22 * avg_top)
            + (0.12 * direction_balance)
            + (0.10 * signal_diversity)
            + (0.08 * aspect_presence)
        )
        unique_keys: list[str] = []
        seen_keys: set[str] = set()
        for key in bucket["source_keys"]:
            value = str(key).strip()
            if not value or value in seen_keys:
                continue
            seen_keys.add(value)
            unique_keys.append(value)
        unique_debug: list[str] = []
        seen_debug: set[str] = set()
        for line in bucket["source_debug"]:
            value = str(line).strip()
            if not value or value in seen_debug:
                continue
            seen_debug.add(value)
            unique_debug.append(value)
        out[category] = {
            "category": category,
            "score": round(score, 4),
            "source_keys": unique_keys[:6],
            "source_debug": unique_debug[:6],
            "primary_signature_id": str(items[0].get("primary_signature_id") or items[0].get("id") or "") if items else "",
            "support_signature_ids": [
                str(item.get("primary_signature_id") or item.get("id") or "")
                for item in items[:4]
                if str(item.get("primary_signature_id") or item.get("id") or "")
            ],
        }
    return out


def _build_composite_candidate(
    *,
    template: Mapping[str, Any],
    aggregates: Mapping[str, Mapping[str, Any]],
    corrected_scores: Mapping[str, Any],
    role: str,
) -> dict[str, Any] | None:
    primary_categories = [str(item) for item in template.get("primary_categories") or []]
    support_categories = [str(item) for item in template.get("support_categories") or []]
    primary = max(
        (aggregates.get(category, {}) for category in primary_categories),
        key=lambda item: _safe_float(item.get("score")),
        default={},
    )
    support = max(
        (aggregates.get(category, {}) for category in support_categories),
        key=lambda item: _safe_float(item.get("score")),
        default={},
    )
    primary_score = _safe_float(primary.get("score"))
    support_score = _safe_float(support.get("score"))
    if primary_score < 0.44:
        return None
    if support_categories and support_score < 0.28:
        return None
    category = str(template.get("category") or "")
    channel_bonus = 0.10 * _channel_support(category if category != "pair_field" else "romantic_pull", corrected_scores)
    score = clamp01((0.62 * primary_score) + (0.28 * support_score) + channel_bonus)
    source_debug = [str(item).strip() for item in (primary.get("source_debug") or []) if str(item).strip()]
    for item in support.get("source_debug") or []:
        value = str(item).strip()
        if value and value not in source_debug:
            source_debug.append(value)
    source_keys = [str(item).strip() for item in (primary.get("source_keys") or []) if str(item).strip()]
    for item in support.get("source_keys") or []:
        value = str(item).strip()
        if value and value not in source_keys:
            source_keys.append(value)
    astro_hint_soft = soft_astro_hint_from_sources(source_debug) or ""
    return {
        "id": str(template.get("id") or ""),
        "category": category,
        "label": str(template.get("label") or "").strip(),
        "one_liner": str(template.get("one_liner") or "").strip(),
        "score": round(score, 4),
        "confidence": round(score, 4),
        "astro_hint_soft": astro_hint_soft,
        "source_keys": source_keys[:6],
        "source_debug": source_debug[:6],
        "primary_signature_id": str(primary.get("primary_signature_id") or primary.get("category") or ""),
        "support_signature_ids": [
            str(primary.get("category") or ""),
            str(support.get("category") or ""),
        ],
        "role": role,
    }


def build_pair_signature_candidates(
    *,
    aggregates: Mapping[str, Mapping[str, Any]],
    aspect_candidates: Sequence[Mapping[str, Any]],
    corrected_scores: Mapping[str, Any],
) -> list[dict[str, Any]]:
    candidates = [
        candidate
        for template in PAIR_SIGNATURE_TEMPLATES
        for candidate in [_build_composite_candidate(template=template, aggregates=aggregates, corrected_scores=corrected_scores, role="pair_signature")]
        if candidate
    ]
    if len(candidates) >= 3:
        return sorted(candidates, key=lambda item: (-_safe_float(item.get("score")), str(item.get("id") or "")))
    for aspect in aspect_candidates[:6]:
        if _safe_float(aspect.get("score")) < 0.62:
            continue
        candidates.append(
            {
                **dict(aspect),
                "id": str(aspect.get("id") or ""),
                "role": "pair_signature",
            }
        )
    return sorted(candidates, key=lambda item: (-_safe_float(item.get("score")), str(item.get("id") or "")))


def build_together_field_candidates(
    *,
    aggregates: Mapping[str, Mapping[str, Any]],
    corrected_scores: Mapping[str, Any],
) -> list[dict[str, Any]]:
    candidates = [
        candidate
        for template in TOGETHER_FIELD_TEMPLATES
        for candidate in [_build_composite_candidate(template=template, aggregates=aggregates, corrected_scores=corrected_scores, role="together_field")]
        if candidate
    ]
    return sorted(candidates, key=lambda item: (-_safe_float(item.get("score")), str(item.get("id") or "")))


def build_sweet_spot_candidates(
    *,
    aggregates: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for category in SYNSTRY_POSITIVE_CATEGORIES:
        aggregate = aggregates.get(category, {})
        score = _safe_float(aggregate.get("score"))
        text = SWEET_SPOT_TEMPLATES.get(category)
        if score < 0.42 or not text:
            continue
        out.append(
            {
                "id": f"sweet_{category}",
                "category": category,
                "text": text,
                "score": round(score, 4),
                "source_keys": list(aggregate.get("source_keys") or [])[:4],
            }
        )
    return sorted(out, key=lambda item: (-_safe_float(item.get("score")), str(item.get("id") or "")))


def build_friction_point_candidates(
    *,
    aggregates: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for category in SYNSTRY_TENSION_CATEGORIES:
        aggregate = aggregates.get(category, {})
        score = _safe_float(aggregate.get("score"))
        text = FRICTION_POINT_TEMPLATES.get(category)
        if score < 0.42 or not text:
            continue
        out.append(
            {
                "id": f"friction_{category}",
                "category": category,
                "text": text,
                "score": round(score, 4),
                "source_keys": list(aggregate.get("source_keys") or [])[:4],
            }
        )
    return sorted(out, key=lambda item: (-_safe_float(item.get("score")), str(item.get("id") or "")))
