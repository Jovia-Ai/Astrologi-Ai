from __future__ import annotations

from typing import Any, Mapping, Sequence, TypedDict

from app.transit.narrative.life_chapter_contract import (
    ActivatedNatalFactor,
    ChapterConfidence,
    ChapterPhase,
    ChapterPriority,
    ChapterType,
    LifeChapter,
    LifeChapterDomainOwnership,
    LifeChapterEvidence,
    LifeChapterRendererHandoff,
    LifeChapterSemanticFocus,
    LifeChapterTimeWindow,
    LifeChapterVoiceHints,
    SuppressedReading,
)
from app.transit.narrative.point_policy import normalize_point_token


class LifeChapterCandidate(TypedDict, total=False):
    source_signal_id: str
    chapter_type: str
    signal_type: str
    time_window: dict[str, str | None]
    candidate_reason: str
    confidence: str
    debug: dict[str, Any]


class LifeChapterDetectionResult(TypedDict):
    active_life_chapter: dict[str, Any] | None
    candidates: list[LifeChapterCandidate]
    debug: dict[str, Any]


class LifeChapterEnrichmentContext(TypedDict, total=False):
    candidate: LifeChapterCandidate
    event: Mapping[str, Any]
    natal_context: Mapping[str, Any]
    overlap: Mapping[str, Any]
    house: int | None
    sign: str
    direction: Mapping[str, Any]
    phase: ChapterPhase
    phase_source: str
    phase_reason: str
    confidence: ChapterConfidence


def detect_active_life_chapter(
    *,
    canonical_natal_state: Mapping[str, Any] | None,
    transit_events: Sequence[Mapping[str, Any]],
    solar_year_frame: Mapping[str, Any] | None = None,
    structural_chapter_rail: Mapping[str, Any] | None = None,
    debug: bool = False,
) -> LifeChapterDetectionResult:
    candidates: list[LifeChapterCandidate] = []
    for event in transit_events:
        candidates.extend(_extract_event_candidates(event))

    solar_candidate = _extract_solar_year_candidate(solar_year_frame)
    if solar_candidate is not None:
        candidates.append(solar_candidate)

    structural_candidate = _extract_structural_candidate(structural_chapter_rail)
    if structural_candidate is not None:
        candidates.append(structural_candidate)

    candidates = _sorted_candidates(candidates)
    active_life_chapter = _emit_active_life_chapter(
        candidates=candidates,
        transit_events=transit_events,
        canonical_natal_state=canonical_natal_state,
    )
    debug_payload: dict[str, Any] = {
        "candidate_count": len(candidates),
        "candidate_source_ids": [str(candidate.get("source_signal_id") or "") for candidate in candidates],
        "active_life_chapter_emitted": active_life_chapter is not None,
    }
    if active_life_chapter is not None:
        debug_payload["active_life_chapter_type"] = str(active_life_chapter.get("chapter_type") or "")
        debug_payload["active_life_chapter_id"] = str(active_life_chapter.get("chapter_id") or "")
    if debug:
        debug_payload["candidates"] = candidates

    return {
        "active_life_chapter": active_life_chapter,
        "candidates": candidates,
        "debug": debug_payload,
    }


def _extract_event_candidates(event: Mapping[str, Any]) -> list[LifeChapterCandidate]:
    subtype = _safe_str(event.get("event_subtype") or event.get("subtype")).lower()
    family = _safe_str(event.get("event_family") or event.get("family")).lower()
    candidates: list[LifeChapterCandidate] = []

    cycle_candidate = _extract_cycle_candidate(event, subtype=subtype, family=family)
    if cycle_candidate is not None:
        candidates.append(cycle_candidate)

    event_candidate = _extract_family_candidate(event, subtype=subtype, family=family)
    if event_candidate is not None:
        candidates.append(event_candidate)

    return candidates


def _extract_cycle_candidate(
    event: Mapping[str, Any],
    *,
    subtype: str,
    family: str,
) -> LifeChapterCandidate | None:
    if family != "cycle_event" and subtype not in {
        "saturn_return",
        "jupiter_return",
        "nodal_return",
        "nodal_opposition",
    }:
        return None

    if subtype == "saturn_return":
        chapter_type = ChapterType.SATURN_RETURN.value
        signal_type = "saturn_return"
        confidence = ChapterConfidence.HIGH.value
        reason = "Transit events içinde Satürn dönüşü subtype'ı bulundu."
    elif subtype == "jupiter_return":
        chapter_type = ChapterType.JUPITER_RETURN.value
        signal_type = "jupiter_return"
        confidence = ChapterConfidence.MEDIUM.value
        reason = "Transit events içinde Jüpiter dönüşü subtype'ı bulundu."
    elif subtype == "nodal_return":
        chapter_type = ChapterType.NODAL_RETURN.value
        signal_type = "nodal_return"
        confidence = ChapterConfidence.HIGH.value
        reason = "Transit events içinde nodal return subtype'ı bulundu."
    elif subtype == "nodal_opposition":
        chapter_type = ChapterType.NODAL_ACTIVATION.value
        signal_type = "nodal_opposition"
        confidence = ChapterConfidence.MEDIUM.value
        reason = "Transit events içinde nodal opposition subtype'ı bulundu; skeleton bunu nodal activation adayı olarak sınıflıyor."
    else:
        return None

    return _build_candidate(
        event,
        chapter_type=chapter_type,
        signal_type=signal_type,
        confidence=confidence,
        candidate_reason=reason,
    )


def _extract_family_candidate(
    event: Mapping[str, Any],
    *,
    subtype: str,
    family: str,
) -> LifeChapterCandidate | None:
    if family == "eclipse_trigger" or subtype in {"solar_eclipse", "lunar_eclipse"}:
        return _build_candidate(
            event,
            chapter_type=ChapterType.ECLIPSE_ACTIVATION.value,
            signal_type="eclipse",
            confidence=ChapterConfidence.MEDIUM.value,
            candidate_reason="Transit events içinde tutulma/eclipsed trigger bulundu.",
        )

    if family == "station_event" or subtype.startswith("station") or subtype in {"retro_shift", "direction_change"}:
        return _build_candidate(
            event,
            chapter_type=ChapterType.MAJOR_TRANSIT_CHAPTER.value,
            signal_type="station",
            confidence=ChapterConfidence.MEDIUM.value,
            candidate_reason="Transit events içinde station/retro yön değişimi sinyali bulundu.",
        )

    if family == "house_ingress_event" or ".house_" in subtype:
        return _build_candidate(
            event,
            chapter_type=ChapterType.MAJOR_TRANSIT_CHAPTER.value,
            signal_type="house_ingress",
            confidence=ChapterConfidence.MEDIUM.value,
            candidate_reason="Transit events içinde house ingress sinyali bulundu.",
        )

    return None


def _extract_solar_year_candidate(solar_year_frame: Mapping[str, Any] | None) -> LifeChapterCandidate | None:
    frame = _unwrap_solar_year_frame(solar_year_frame)
    if not frame:
        return None

    return {
        "source_signal_id": _safe_str(frame.get("event_id")) or "solar_year_frame",
        "chapter_type": ChapterType.SOLAR_RETURN_THEME.value,
        "signal_type": "solar_year_frame",
        "time_window": _extract_time_window(frame),
        "candidate_reason": "Solar year frame payload side-rail olarak mevcut; skeleton bunu annual chapter adayı olarak yüzeye çıkarıyor.",
        "confidence": ChapterConfidence.MEDIUM.value,
        "debug": {
            "source_family": _safe_str(frame.get("event_family")) or "solar_year_theme",
            "source_subtype": _safe_str(frame.get("event_subtype")) or "solar_return_frame",
            "year_ruler": _safe_str(frame.get("year_ruler")),
            "dominant_houses": list(frame.get("dominant_houses") or []) if isinstance(frame.get("dominant_houses"), list) else [],
        },
    }


def _extract_structural_candidate(structural_chapter_rail: Mapping[str, Any] | None) -> LifeChapterCandidate | None:
    if not isinstance(structural_chapter_rail, Mapping) or not structural_chapter_rail:
        return None

    return {
        "source_signal_id": _safe_str(structural_chapter_rail.get("event_id") or structural_chapter_rail.get("id")) or "structural_natal_pattern",
        "chapter_type": ChapterType.STRUCTURAL_NATAL_CHAPTER.value,
        "signal_type": "structural_natal_pattern",
        "time_window": _extract_time_window(structural_chapter_rail),
        "candidate_reason": "Natal structural rail bulundu; skeleton bunu gelecekte structural natal chapter üretebilecek derived source olarak tutuyor.",
        "confidence": ChapterConfidence.LOW.value,
        "debug": {
            "source_keys": sorted(str(key) for key in structural_chapter_rail.keys()),
            "semantic_focus": {
                "primary": "three_part_pressure_system",
                "secondary": ["apex_release_point", "dense_integration"],
                "not_this": ["two-needs-only simplification", "generic stress reading"],
            },
            "renderer_handoff": {
                "human_scene": "basıncın en çok yüzeye çıktığı kişisel alan",
                "core_contrast": "sürtünmeyi alarm okumak ile onun kurduğu kası görmek",
                "chapter_weight": "structural natal pattern, not transient mood",
                "chart_specific_anchor": "üç parçalı basınç sistemi ve release noktası",
                "voice_register": "integration / dense",
                "avoid_readings": ["two-needs-only simplification", "generic stress reading"],
            },
        },
    }


def _build_candidate(
    event: Mapping[str, Any],
    *,
    chapter_type: str,
    signal_type: str,
    confidence: str,
    candidate_reason: str,
) -> LifeChapterCandidate:
    return {
        "source_signal_id": _safe_str(event.get("event_id")) or f"{signal_type}:{_safe_str(event.get('title_tr')) or 'unknown'}",
        "chapter_type": chapter_type,
        "signal_type": signal_type,
        "time_window": _extract_time_window(event),
        "candidate_reason": candidate_reason,
        "confidence": confidence,
        "debug": {
            "source_family": _safe_str(event.get("event_family") or event.get("family")),
            "source_subtype": _safe_str(event.get("event_subtype") or event.get("subtype")),
            "chapter_opening": bool(event.get("chapter_opening")),
            "structural_significance": _safe_float(event.get("structural_significance")),
            "precision_signal": _safe_float(event.get("precision_signal")),
        },
    }


def _unwrap_solar_year_frame(solar_year_frame: Mapping[str, Any] | None) -> Mapping[str, Any] | None:
    if not isinstance(solar_year_frame, Mapping) or not solar_year_frame:
        return None
    nested = solar_year_frame.get("solar_year_frame")
    if isinstance(nested, Mapping) and nested:
        return nested
    return solar_year_frame


def _extract_time_window(item: Mapping[str, Any]) -> dict[str, str | None]:
    timebox = item.get("timebox")
    if isinstance(timebox, Mapping):
        peaks = timebox.get("peaks")
        peak = None
        if isinstance(peaks, list):
            for entry in peaks:
                if isinstance(entry, Mapping):
                    peak = _safe_str(entry.get("t"))
                    if peak:
                        break
        return {
            "start": _safe_str(timebox.get("enter")) or _safe_str(item.get("start_at")),
            "peak": peak or _first_exact(item),
            "end": _safe_str(timebox.get("exit")) or _safe_str(item.get("end_at")),
        }

    return {
        "start": _safe_str(item.get("start_at") or item.get("year_start") or item.get("date")),
        "peak": _safe_str(item.get("solar_return_at")) or _first_exact(item) or _safe_str(item.get("peak")),
        "end": _safe_str(item.get("end_at") or item.get("year_end")),
    }


def _first_exact(item: Mapping[str, Any]) -> str:
    exact_at = item.get("exact_at")
    if isinstance(exact_at, list):
        for entry in exact_at:
            token = _safe_str(entry)
            if token:
                return token
    return _safe_str(exact_at)


def _sorted_candidates(candidates: list[LifeChapterCandidate]) -> list[LifeChapterCandidate]:
    return sorted(
        candidates,
        key=lambda candidate: (
            _safe_str((candidate.get("time_window") or {}).get("start")),
            _safe_str(candidate.get("chapter_type")),
            _safe_str(candidate.get("source_signal_id")),
        ),
    )


def _emit_active_life_chapter(
    *,
    candidates: Sequence[LifeChapterCandidate],
    transit_events: Sequence[Mapping[str, Any]],
    canonical_natal_state: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    event_index = {
        _safe_str(event.get("event_id")): event
        for event in transit_events
        if _safe_str(event.get("event_id"))
    }
    natal_context = _build_natal_context(canonical_natal_state)

    tier1_candidates = sorted(
        (
            candidate
            for candidate in candidates
            if _safe_str(candidate.get("chapter_type"))
            in {
                ChapterType.SATURN_RETURN.value,
                ChapterType.NODAL_RETURN.value,
                ChapterType.NODAL_ACTIVATION.value,
            }
        ),
        key=lambda candidate: (
            _tier1_priority(_safe_str(candidate.get("chapter_type"))),
            -_confidence_rank(_safe_str(candidate.get("confidence"))),
            _safe_str(candidate.get("source_signal_id")),
        ),
    )

    built: list[tuple[LifeChapterCandidate, LifeChapter, LifeChapterEnrichmentContext]] = []
    for candidate in tier1_candidates:
        event = event_index.get(_safe_str(candidate.get("source_signal_id")))
        if not isinstance(event, Mapping):
            continue
        built_chapter = _build_active_life_chapter(candidate=candidate, event=event, natal_context=natal_context)
        if built_chapter is not None:
            built.append(built_chapter)

    if not built:
        return None

    merged = _maybe_merge_overlapping_tier1_chapters(built)
    if merged is not None:
        return merged.model_dump()

    chosen_candidate, chosen_chapter, chosen_ctx = built[0]
    suppressed = [
        {
            "source_signal_id": _safe_str(candidate.get("source_signal_id")),
            "chapter_type": _safe_str(candidate.get("chapter_type")),
            "reason": "lower Tier-1 hierarchy",
        }
        for candidate, _chapter, _ctx in built[1:]
    ]
    selection_reason = f"highest-confidence Tier-1 candidate selected: {_safe_str(chosen_candidate.get('chapter_type'))}"
    if suppressed:
        selection_reason = (
            f"{_safe_str(chosen_candidate.get('chapter_type'))} chosen over "
            f"{', '.join(_safe_str(candidate.get('chapter_type')) for candidate, _chapter, _ctx in built[1:])} per Tier-1 hierarchy"
        )
    return _apply_debug_updates(
        chosen_chapter,
        {
            "selection_reason": selection_reason,
            "suppressed_candidates": suppressed,
            "confidence_rationale": _confidence_rationale(chosen_ctx),
        },
    ).model_dump()


def _build_active_life_chapter(
    *,
    candidate: LifeChapterCandidate,
    event: Mapping[str, Any],
    natal_context: Mapping[str, Any],
) -> tuple[LifeChapterCandidate, LifeChapter, LifeChapterEnrichmentContext] | None:
    chapter_type = _safe_str(candidate.get("chapter_type"))
    if not _is_high_confidence_tier1_candidate(candidate, event, natal_context):
        return None

    overlap = _node_overlap_info(event=event, natal_context=natal_context)
    house = _primary_house(event=event, natal_context=natal_context, chapter_type=chapter_type, overlap=overlap)
    sign = _primary_sign(event=event, natal_context=natal_context, chapter_type=chapter_type, overlap=overlap)
    phase, phase_source, phase_reason = _phase_details(event)
    confidence = _effective_confidence(candidate, overlap)
    signal_type = _safe_str(candidate.get("signal_type"))
    source_signal_types = [signal_type] if signal_type else []
    if overlap["has_overlap"]:
        source_signal_types.append("node_overlap")
    direction = _node_direction_info(natal_context)
    voice_hints = _default_voice_hints(chapter_type=chapter_type, house=house)

    chapter = LifeChapter(
        chapter_id=f"lc:{chapter_type}:{_safe_str(candidate.get('source_signal_id'))}",
        chapter_type=chapter_type,
        domain=_domain_for_house(house),
        spine_line=_safe_str(event.get("spine_line") or event.get("primary_spine_line")) or None,
        time_window=LifeChapterTimeWindow(**(candidate.get("time_window") or {"start": "", "peak": None, "end": ""})),
        phase=phase,
        activated_natal_factors=_activated_natal_factors(
            chapter_type=chapter_type,
            house=house,
            overlap=overlap,
        ),
        core_question=_core_question(chapter_type=chapter_type, sign=sign, house=house, overlap=overlap),
        selected_meaning=_selected_meaning(chapter_type=chapter_type, sign=sign, house=house, overlap=overlap),
        selected_meaning_family=_default_meaning_family(chapter_type=chapter_type, house=house),
        semantic_focus=LifeChapterSemanticFocus(
            primary=_default_semantic_focus_primary(chapter_type=chapter_type, house=house),
            secondary=[],
            not_this=["generic fallback reading"],
        ),
        domain_ownership=LifeChapterDomainOwnership(
            primary_domain=_domain_for_house(house),
            secondary_domains=[],
            rationale="initial detector ownership placeholder",
        ),
        renderer_handoff=LifeChapterRendererHandoff(
            human_scene=_default_human_scene(house),
            core_contrast="generic chapter contrast placeholder",
            chapter_weight="major life chapter",
            chart_specific_anchor=_zone_text(sign=sign, house=house),
            voice_register=f"{voice_hints.valence_mode} / {voice_hints.intensity_mode}",
            avoid_readings=["generic fallback reading"],
        ),
        evidence=_evidence(chapter_type=chapter_type, event=event, overlap=overlap),
        suppressed_readings=_suppressed_readings(chapter_type=chapter_type, overlap=overlap),
        suppressed_surface_readings=_suppressed_surface_readings(chapter_type=chapter_type, house=house, overlap=overlap),
        voice_hints=voice_hints,
        priority=ChapterPriority.LIFE_CHAPTER,
        confidence=confidence,
        debug={
            "source_event_ids": [_safe_str(candidate.get("source_signal_id"))],
            "source_signal_types": source_signal_types,
            "node_overlap": overlap,
            "phase_source": phase_source,
            "phase_reason": phase_reason,
        },
    )
    ctx: LifeChapterEnrichmentContext = {
        "candidate": candidate,
        "event": event,
        "natal_context": natal_context,
        "overlap": overlap,
        "house": house,
        "sign": sign,
        "direction": direction,
        "phase": phase,
        "phase_source": phase_source,
        "phase_reason": phase_reason,
        "confidence": confidence,
    }
    chapter = _enrich_chapter_meaning(chapter, ctx)
    chapter = _apply_debug_updates(
        chapter,
        {
            "selection_reason": "pending Tier-1 selection",
            "confidence_rationale": _confidence_rationale(ctx),
            "overlap_reason": (
                "natal South Node in same sign/house as Saturn return — axis activation"
                if overlap.get("has_overlap")
                else ""
            ),
        },
    )
    return candidate, chapter, ctx


def _is_high_confidence_tier1_candidate(
    candidate: LifeChapterCandidate,
    event: Mapping[str, Any],
    natal_context: Mapping[str, Any],
) -> bool:
    chapter_type = _safe_str(candidate.get("chapter_type"))
    precision = _safe_float((candidate.get("debug") or {}).get("precision_signal")) or _safe_float(event.get("precision_signal")) or 0.0
    structural = _safe_float((candidate.get("debug") or {}).get("structural_significance")) or _safe_float(event.get("structural_significance")) or 0.0
    chapter_opening = bool((candidate.get("debug") or {}).get("chapter_opening")) or bool(event.get("chapter_opening"))
    overlap = _node_overlap_info(event=event, natal_context=natal_context)

    if chapter_type == ChapterType.SATURN_RETURN.value:
        return chapter_opening or precision >= 0.7 or structural >= 0.9
    if chapter_type == ChapterType.NODAL_RETURN.value:
        return chapter_opening or precision >= 0.68 or structural >= 0.85
    if chapter_type == ChapterType.NODAL_ACTIVATION.value:
        return overlap["has_overlap"] or chapter_opening or precision >= 0.7 or structural >= 0.85
    return False


def _tier1_priority(chapter_type: str) -> int:
    priorities = {
        ChapterType.SATURN_RETURN.value: 0,
        ChapterType.NODAL_RETURN.value: 1,
        ChapterType.NODAL_ACTIVATION.value: 2,
    }
    return priorities.get(chapter_type, 99)


def _confidence_rank(value: str) -> int:
    ranks = {
        ChapterConfidence.HIGH.value: 3,
        ChapterConfidence.MEDIUM.value: 2,
        ChapterConfidence.LOW.value: 1,
    }
    return ranks.get(value, 0)


def _effective_confidence(candidate: LifeChapterCandidate, overlap: Mapping[str, Any]) -> ChapterConfidence:
    base = _safe_str(candidate.get("confidence"))
    if overlap.get("has_overlap"):
        return ChapterConfidence.HIGH
    if base == ChapterConfidence.HIGH.value:
        return ChapterConfidence.HIGH
    if base == ChapterConfidence.MEDIUM.value:
        return ChapterConfidence.MEDIUM
    return ChapterConfidence.LOW


def _confidence_rationale(ctx: Mapping[str, Any]) -> str:
    confidence = ctx.get("confidence")
    if isinstance(confidence, ChapterConfidence):
        confidence_label = confidence.value
    else:
        confidence_label = _safe_str(confidence) or "unknown"
    phase = ctx.get("phase")
    phase_label = phase.value if isinstance(phase, ChapterPhase) else _safe_str(phase)
    overlap = ctx.get("overlap") if isinstance(ctx.get("overlap"), Mapping) else {}
    sign = _safe_str(ctx.get("sign"))
    house = _safe_int(ctx.get("house"))
    overlap_note = "node overlap present" if overlap.get("has_overlap") else "no node overlap"
    zone = _zone_text(sign=sign, house=house)
    return f"{zone} known, phase {phase_label or 'unknown'}, {overlap_note} -> {confidence_label} confidence"


def _build_natal_context(canonical_natal_state: Mapping[str, Any] | None) -> dict[str, Any]:
    snapshot = canonical_natal_state if isinstance(canonical_natal_state, Mapping) else {}
    bodies_map: dict[str, dict[str, Any]] = {}
    house_cusps_map: dict[int, dict[str, Any]] = {}
    bodies = snapshot.get("bodies")
    if isinstance(bodies, Mapping):
        for key, value in bodies.items():
            if isinstance(value, Mapping):
                bodies_map[normalize_point_token(key)] = dict(value)
    elif isinstance(bodies, Sequence) and not isinstance(bodies, (str, bytes)):
        for item in bodies:
            if not isinstance(item, Mapping):
                continue
            name = normalize_point_token(item.get("name") or item.get("planet") or item.get("body"))
            if name:
                bodies_map[name] = dict(item)
    raw_cusps = snapshot.get("house_cusps") or snapshot.get("house_positions")
    if isinstance(raw_cusps, Mapping):
        for key, value in raw_cusps.items():
            house = _safe_int(key)
            if house is not None and isinstance(value, Mapping):
                house_cusps_map[house] = dict(value)
    elif isinstance(raw_cusps, Sequence) and not isinstance(raw_cusps, (str, bytes)):
        for item in raw_cusps:
            if not isinstance(item, Mapping):
                continue
            house = _safe_int(item.get("house"))
            if house is not None:
                house_cusps_map[house] = dict(item)

    return {
        "bodies_map": bodies_map,
        "house_cusps_map": house_cusps_map,
        "ruled_houses": _derive_ruled_houses(house_cusps_map),
    }


def _derive_ruled_houses(house_cusps_map: Mapping[int, Mapping[str, Any]]) -> dict[str, list[int]]:
    ruler_map = {
        "aries": {"mars"},
        "taurus": {"venus"},
        "gemini": {"mercury"},
        "cancer": {"moon"},
        "leo": {"sun"},
        "virgo": {"mercury"},
        "libra": {"venus"},
        "scorpio": {"mars", "pluto"},
        "sagittarius": {"jupiter"},
        "capricorn": {"saturn"},
        "aquarius": {"saturn", "uranus"},
        "pisces": {"jupiter", "neptune"},
    }
    out: dict[str, list[int]] = {}
    for house, cusp in house_cusps_map.items():
        sign = _safe_str(cusp.get("sign")).lower()
        for ruler in ruler_map.get(sign, set()):
            out.setdefault(ruler, []).append(int(house))
    return out


def _node_direction_info(natal_context: Mapping[str, Any]) -> dict[str, Any]:
    bodies_map = natal_context.get("bodies_map") if isinstance(natal_context.get("bodies_map"), Mapping) else {}
    north = bodies_map.get("north_node") if isinstance(bodies_map.get("north_node"), Mapping) else {}
    south = bodies_map.get("south_node") if isinstance(bodies_map.get("south_node"), Mapping) else {}
    north_sign = _safe_str(north.get("sign"))
    south_sign = _safe_str(south.get("sign"))
    north_house = _safe_int(north.get("house"))
    south_house = _safe_int(south.get("house"))
    known = bool(north_sign and south_sign)
    return {
        "known": known,
        "north_sign": north_sign,
        "south_sign": south_sign,
        "north_house": north_house,
        "south_house": south_house,
    }


def _enrich_chapter_meaning(chapter: LifeChapter, ctx: Mapping[str, Any]) -> LifeChapter:
    chapter_type = str(chapter.chapter_type.value if hasattr(chapter.chapter_type, "value") else chapter.chapter_type)
    if chapter_type == ChapterType.SATURN_RETURN.value:
        return _enrich_saturn_return_meaning(chapter, ctx)
    if chapter_type == ChapterType.NODAL_RETURN.value:
        return _enrich_nodal_return_meaning(chapter, ctx)
    if chapter_type == ChapterType.NODAL_ACTIVATION.value:
        return _enrich_nodal_activation_meaning(chapter, ctx)
    return chapter


def _enrich_saturn_return_meaning(chapter: LifeChapter, ctx: Mapping[str, Any]) -> LifeChapter:
    sign = _safe_str(ctx.get("sign"))
    house = _safe_int(ctx.get("house"))
    overlap = ctx.get("overlap") if isinstance(ctx.get("overlap"), Mapping) else {}
    natal_context = ctx.get("natal_context") if isinstance(ctx.get("natal_context"), Mapping) else {}
    ruled_houses = list((natal_context.get("ruled_houses") or {}).get("saturn") or [])

    selected_meaning = _saturn_selected_meaning(sign=sign, house=house, overlap=overlap)
    core_question = _saturn_core_question(sign=sign, house=house, overlap=overlap)
    evidence = [
        LifeChapterEvidence(
            factor="Transit Saturn conjunct natal Saturn",
            role="return",
            explanation="Saturn return ana olgunlaşma döngüsünü doğrudan açıyor.",
        ),
        LifeChapterEvidence(
            factor=_saturn_placement_factor(sign=sign, house=house),
            role="natal_context",
            explanation=_saturn_placement_explanation(sign=sign, house=house, ruled_houses=ruled_houses),
        ),
    ]
    if overlap.get("has_overlap"):
        matched = ", ".join(str(node) for node in overlap.get("matched_nodes") or [])
        evidence.append(
            LifeChapterEvidence(
                factor="South/North Node same sign/house overlap",
                role="axis_overlap",
                explanation=f"Satürn dönüşü {matched} ile aynı sign/house alanına düştüğü için chapter eksensel ve karmik bir ağırlık kazanıyor.",
            )
        )

    suppressed = [
        SuppressedReading(
            reading="generic communication difficulty",
            reason="Saturn return sadece iletişim zorluğu değil; natal Saturn temasının olgunlaşmasıdır.",
        ),
        SuppressedReading(
            reading="generic burden / heaviness",
            reason="Bu chapter olgunlaşma; yük cliché'sine indirgenmemeli.",
        ),
    ]
    semantic_focus, meaning_family, domain_ownership, renderer_handoff, suppressed_surface_readings, voice_hints = _saturn_handoff_bundle(
        sign=sign,
        house=house,
        overlap=overlap,
        chapter=chapter,
    )
    return _validated_chapter_update(
        chapter,
        {
            "core_question": core_question,
            "selected_meaning": selected_meaning,
            "selected_meaning_family": meaning_family,
            "semantic_focus": semantic_focus,
            "domain_ownership": domain_ownership,
            "renderer_handoff": renderer_handoff,
            "evidence": evidence,
            "suppressed_readings": suppressed,
            "suppressed_surface_readings": suppressed_surface_readings,
            "voice_hints": voice_hints,
        },
    )


def _enrich_nodal_return_meaning(chapter: LifeChapter, ctx: Mapping[str, Any]) -> LifeChapter:
    return _enrich_directional_node_chapter(chapter, ctx, activation=False)


def _enrich_nodal_activation_meaning(chapter: LifeChapter, ctx: Mapping[str, Any]) -> LifeChapter:
    return _enrich_directional_node_chapter(chapter, ctx, activation=True)


def _enrich_directional_node_chapter(chapter: LifeChapter, ctx: Mapping[str, Any], *, activation: bool) -> LifeChapter:
    direction = ctx.get("direction") if isinstance(ctx.get("direction"), Mapping) else {}
    sign = _safe_str(ctx.get("sign"))
    house = _safe_int(ctx.get("house"))
    overlap = ctx.get("overlap") if isinstance(ctx.get("overlap"), Mapping) else {}
    confidence = ctx.get("confidence")
    if not isinstance(confidence, ChapterConfidence):
        confidence = ChapterConfidence.MEDIUM

    north_sign = _safe_str(direction.get("north_sign"))
    south_sign = _safe_str(direction.get("south_sign"))
    north_house = _safe_int(direction.get("north_house"))
    south_house = _safe_int(direction.get("south_house"))
    direction_known = bool(direction.get("known"))
    directional_selected, directional_question = _directional_node_language(
        north_sign=north_sign,
        south_sign=south_sign,
        north_house=north_house,
        south_house=south_house,
        activation=activation,
        sign=sign,
        house=house,
    )

    evidence = [
        LifeChapterEvidence(
            factor="Transit node chapter signal",
            role="return" if not activation else "activation",
            explanation="Node ekseni tekrar eden yön ve ilişki kalıplarını chapter düzeyinde görünür kılıyor.",
        )
    ]
    suppressed = []
    if direction_known:
        evidence.append(
            LifeChapterEvidence(
                factor=f"North Node {north_sign} / South Node {south_sign}",
                role="natal_context",
                explanation="Node direction bilindiği için chapter meaning generic denge söylemine düşmeden yön seçebiliyor.",
            )
        )
        if activation and overlap.get("has_overlap"):
            evidence.append(
                LifeChapterEvidence(
                    factor="South/North Node same sign/house overlap",
                    role="axis_overlap",
                    explanation="Node ekseni aynı sign/house overlap ile tetiklendiği için activation chapter daha merkezî hale geliyor.",
                )
            )
    else:
        suppressed.append(
            SuppressedReading(
                reading="generic self/other balance",
                reason="Node direction must be known before selecting directional meaning.",
            )
        )
        evidence.append(
            LifeChapterEvidence(
                factor="Node direction incomplete",
                role="natal_context",
                explanation="North/South node yönü eksik olduğu için chapter meaning daha temkinli tutuldu.",
            )
        )
        if confidence == ChapterConfidence.HIGH:
            confidence = ChapterConfidence.MEDIUM

    if activation:
        suppressed.append(
            SuppressedReading(
                reading="generic relationship or direction drama",
                reason="Nodal activation eksensel bir tekrar temasını işaret eder; bunu olay tahminine çevirmiyoruz.",
            )
        )
    else:
        suppressed.append(
            SuppressedReading(
                reading="fated event prediction",
                reason="Nodal return burada kader cümlesi üretmek için değil, tekrar eden yön kalıplarını görünür kılmak için tutuluyor.",
            )
        )

    semantic_focus, meaning_family, domain_ownership, renderer_handoff, suppressed_surface_readings, voice_hints = _nodal_handoff_bundle(
        sign=sign,
        house=house,
        direction=direction,
        activation=activation,
        overlap=overlap,
        chapter=chapter,
    )

    return _validated_chapter_update(
        chapter,
        {
            "core_question": directional_question,
            "selected_meaning": directional_selected,
            "selected_meaning_family": meaning_family,
            "semantic_focus": semantic_focus,
            "domain_ownership": domain_ownership,
            "renderer_handoff": renderer_handoff,
            "evidence": evidence,
            "suppressed_readings": suppressed,
            "suppressed_surface_readings": suppressed_surface_readings,
            "confidence": confidence,
            "voice_hints": voice_hints,
        },
    )


def _directional_node_language(
    *,
    north_sign: str,
    south_sign: str,
    north_house: int | None,
    south_house: int | None,
    activation: bool,
    sign: str,
    house: int | None,
) -> tuple[str, str]:
    zone = _zone_text(sign=sign or north_sign, house=house or north_house)
    if north_sign == "Aries" and south_sign == "Libra":
        return (
            f"{zone} başkalarına göre ayar verme refleksinden çıkıp daha doğrudan yön seçmeye alan açılması",
            f"{zone} başkalarına göre ayar verme alışkanlığından çıkıp kendi yönünü nasıl daha açık seçiyorsun?",
        )
    if north_sign == "Libra" and south_sign == "Aries":
        return (
            f"{zone} tek başına hız alma refleksinin yanına ilişki ve eşgüdüm kurmayı daha bilinçli yerleştirmek",
            f"{zone} tek başına hız alma refleksinin yanına ilişkiyi nasıl daha bilinçli yerleştiriyorsun?",
        )
    if north_sign and south_sign:
        north_label = _sign_label_tr(north_sign)
        south_label = _sign_label_tr(south_sign)
        verb = "görünür olup daha bilinçli bir yön seçmeye zorlanması" if activation else "daha bilinçli bir yöne yerleşmesi"
        return (
            f"{zone} {south_label} tarafının eski reflekslerinden çıkıp {north_label} tarafının daha seçilmiş yönüne {verb}",
            f"{zone} {south_label} refleksinden çıkıp {north_label} yönünü nasıl daha bilinçli seçiyorsun?",
        )
    return (
        f"{zone} node eksenindeki tekrar eden yön reflekslerinin daha bilinçli bir seçim istemesi",
        f"{zone} tekrar eden yön reflekslerini nasıl daha bilinçli bir seçime dönüştürüyorsun?",
    )


def _saturn_handoff_bundle(
    *,
    sign: str,
    house: int | None,
    overlap: Mapping[str, Any],
    chapter: LifeChapter,
) -> tuple[
    LifeChapterSemanticFocus,
    str,
    LifeChapterDomainOwnership,
    LifeChapterRendererHandoff,
    list[SuppressedReading],
    LifeChapterVoiceHints,
]:
    if house == 3:
        primary = "speech_authority"
        secondary = ["self_definition", "mental_reflex_maturation"]
        not_this = ["generic communication difficulty", "sibling conflict prediction"]
        family = "speech_authority_maturation"
        rationale = "Saturn return 3. evde sözü, zihinsel refleksi ve yakın çevre içindeki duruşu daha seçilmiş bir otoriteye topluyor."
        human_scene = "kısa mesajlar, yarım kalmış konuşmalar, hızlı cevap verme anları"
        core_contrast = "hızlı cevap vermek ile gerçekten nerede durduğunu söylemek"
        anchor = "eski refleksif konuşma biçiminin daha seçilmiş bir omurgaya yerleşmesi"
        avoid = ["generic communication difficulty", "sibling conflict prediction", "ordinary transit framing"]
        surface = [
            SuppressedReading(reading="generic communication difficulty", reason="3. ev burada yalnız iletişim zorluğu değil; sözün taşıdığı otoritenin olgunlaşması."),
            SuppressedReading(reading="sibling conflict prediction", reason="Yakın çevre alanı tetiklenebilir ama chapter'ın sahibi kardeş çatışması değil, ifade refleksinin olgunlaşması."),
        ]
        if overlap.get("has_overlap"):
            rationale += " South Node overlap eski refleksif söz kalıbını chapter'ın merkezine taşıyor."
            anchor = "eski refleksif konuşma kalıbının daha seçilmiş bir söz formuna yerleşmesi"
        return (
            LifeChapterSemanticFocus(primary=primary, secondary=secondary, not_this=not_this),
            family,
            LifeChapterDomainOwnership(
                primary_domain="communication_learning",
                secondary_domains=["identity_presence", "mental_patterning"],
                rationale=rationale,
            ),
            LifeChapterRendererHandoff(
                human_scene=human_scene,
                core_contrast=core_contrast,
                chapter_weight="not ordinary transit; long-cycle maturation",
                chart_specific_anchor=anchor,
                voice_register="maturation / medium",
                avoid_readings=avoid,
            ),
            surface,
            LifeChapterVoiceHints(valence_mode="maturation", intensity_mode="medium", rhetorical_frame="construction", tone="friend-warm"),
        )
    if house == 8:
        return (
            LifeChapterSemanticFocus(
                primary="shared_emotional_territory",
                secondary=["trust_under_pressure", "intimacy_boundary_maturation", "shared_resource_weight"],
                not_this=["generic emotional regulation", "body-rhythm reading without body backing"],
            ),
            "shared_trust_maturation",
            LifeChapterDomainOwnership(
                primary_domain="trust_transformation",
                secondary_domains=["shared_resources", "intimacy_psychology"],
                rationale="Cancer 8. ev Saturn return derin bağ, ortak yük, güven ve paylaşılan duygusal alanın nasıl taşındığını olgunlaştırır.",
            ),
            LifeChapterRendererHandoff(
                human_scene="mahrem konuşmalar, birlikte taşınan yükler, güven verirken ve alırken sıkışan anlar",
                core_contrast="duygusal güvenlik aramak ile her şeyi tek başına içte taşımak",
                chapter_weight="not ordinary transit; deep shared-space maturation",
                chart_specific_anchor="ortak duygusal alanın ve güvenin daha dayanıklı bir forma yerleşmesi",
                voice_register="maturation / dense",
                avoid_readings=["generic emotional regulation", "body-rhythm reading", "surface mood language"],
            ),
            [
                SuppressedReading(reading="generic emotional regulation", reason="8. ev sahibi duygu düzenleme değil; ortak yük, güven, mahremiyet ve paylaşılmış alan."),
                SuppressedReading(reading="body-rhythm reading", reason="1./6. ev ya da belirgin beden bağlamı yoksa bu chapter beden rutini diye okunmamalı."),
            ],
            LifeChapterVoiceHints(valence_mode="maturation", intensity_mode="dense", rhetorical_frame="deepening", tone="friend-warm"),
        )
    if house == 10:
        return (
            LifeChapterSemanticFocus(
                primary="public_authority_settling",
                secondary=["role_maturity", "visible_responsibility", "identity_stage"],
                not_this=["generic career success", "simple recognition"],
            ),
            "public_authority_maturation",
            LifeChapterDomainOwnership(
                primary_domain="public_role",
                secondary_domains=["career_visibility", "identity_presence"],
                rationale="Saturn return 10. evde kamusal rolü sadece görünürlük olarak değil, kimliğin dış dünyada nasıl taşındığı olarak olgunlaştırır.",
            ),
            LifeChapterRendererHandoff(
                human_scene="beklentinin netleştiği iş konuşmaları, kamusal sorumluluk, görünür rol anları",
                core_contrast="kendini kanıtlamak ile zaten taşıdığın rolün içine yerleşmek",
                chapter_weight="not ordinary transit; public-role maturation",
                chart_specific_anchor="kamusal rolün daha sakin ama daha kalıcı bir otoriteye yerleşmesi",
                voice_register="maturation / medium",
                avoid_readings=["generic career success", "cheerleading recognition"],
            ),
            [
                SuppressedReading(reading="generic career success", reason="10. ev burada başarı vaadi değil; rol ve otorite taşıma biçiminin olgunlaşması."),
                SuppressedReading(reading="simple recognition", reason="Saturn return tanınmaktan çok, görünür rolün içine yerleşme ağırlığı taşır."),
            ],
            LifeChapterVoiceHints(valence_mode="maturation", intensity_mode="medium", rhetorical_frame="settling", tone="friend-warm"),
        )

    return (
        LifeChapterSemanticFocus(
            primary=_default_semantic_focus_primary(chapter_type=chapter.chapter_type.value, house=house),
            secondary=["structure_maturation"],
            not_this=["generic burden"],
        ),
        _default_meaning_family(chapter_type=chapter.chapter_type.value, house=house),
        LifeChapterDomainOwnership(
            primary_domain=chapter.domain,
            secondary_domains=[],
            rationale=f"{_zone_text(sign=sign, house=house)} Satürn dönüşü bu yaşam alanındaki yapıyı olgunlaştırıyor.",
        ),
        LifeChapterRendererHandoff(
            human_scene=_default_human_scene(house),
            core_contrast="eski refleks ile daha seçilmiş biçim",
            chapter_weight="major life chapter",
            chart_specific_anchor=chapter.selected_meaning,
            voice_register="maturation / medium",
            avoid_readings=["generic burden"],
        ),
        [SuppressedReading(reading="generic burden", reason="Saturn return yük cümlesine indirgenmeden, yapı ve otorite olgunlaşması olarak tutulmalı.")],
        LifeChapterVoiceHints(valence_mode="maturation", intensity_mode="medium", rhetorical_frame="settling", tone="friend-warm"),
    )


def _nodal_handoff_bundle(
    *,
    sign: str,
    house: int | None,
    direction: Mapping[str, Any],
    activation: bool,
    overlap: Mapping[str, Any],
    chapter: LifeChapter,
) -> tuple[
    LifeChapterSemanticFocus,
    str,
    LifeChapterDomainOwnership,
    LifeChapterRendererHandoff,
    list[SuppressedReading],
    LifeChapterVoiceHints,
]:
    north_sign = _safe_str(direction.get("north_sign"))
    south_sign = _safe_str(direction.get("south_sign"))
    if north_sign == "Aries" and south_sign == "Libra":
        return (
            LifeChapterSemanticFocus(
                primary="directional_self_definition",
                secondary=["self_assertion_without_self_erasure", "relational_deconditioning"],
                not_this=["generic self/other balance"],
            ),
            "nodal_direction_self_definition",
            LifeChapterDomainOwnership(
                primary_domain="identity_presence" if house in {1, 3} else chapter.domain,
                secondary_domains=["relationships_agreements", "belief_direction"],
                rationale="NN Koç / SN Terazi aksı başkalarına göre ayar verme kalıbından çıkıp daha doğrudan yön seçmeyi büyüme hattı yapar.",
            ),
            LifeChapterRendererHandoff(
                human_scene="yan yana dururken kendi sözünü ayarladığın anlar, yön seçimi, görünür pozisyon alma",
                core_contrast="ilişkiyi korumak ile kendi yönünü silmeden söylemek",
                chapter_weight="major axis chapter",
                chart_specific_anchor="başkalarına göre ayar verme refleksinden daha doğrudan bir yöne geçiş",
                voice_register="momentum / medium",
                avoid_readings=["generic self/other balance", "fated relationship drama"],
            ),
            [
                SuppressedReading(reading="generic self/other balance", reason="Node direction biliniyorsa bu chapter denge klişesine düşmeden yön taşır."),
                SuppressedReading(reading="fated relationship drama", reason="Node chapter ilişki kaderi değil, yön ve seçim alışkanlığının eksensel tekrarıdır."),
            ],
            LifeChapterVoiceHints(valence_mode="momentum", intensity_mode="medium", rhetorical_frame="directional", tone="friend-warm"),
        )
    if north_sign == "Libra" and south_sign == "Aries":
        return (
            LifeChapterSemanticFocus(
                primary="cooperative_direction",
                secondary=["decelerating_self_reliance", "relational_coordination"],
                not_this=["generic self/other balance"],
            ),
            "nodal_direction_cooperation",
            LifeChapterDomainOwnership(
                primary_domain="relationships_agreements",
                secondary_domains=["identity_presence", "belief_direction"],
                rationale="NN Terazi / SN Koç aksı tek başına hız alma refleksinden çıkıp eşgüdüm ve ortak ritim kurmayı büyüme hattı yapar.",
            ),
            LifeChapterRendererHandoff(
                human_scene="tek başına yüklenmek yerine yan yana adım kurduğun anlar, ortak karar, tempo ayarı",
                core_contrast="hızı tek başına almak ile ilişkiyi de denkleme katmak",
                chapter_weight="major axis chapter",
                chart_specific_anchor="tek başına hız alma refleksinin yanına ilişki ve eşgüdüm yerleştirmek",
                voice_register="integration / medium",
                avoid_readings=["generic self/other balance", "fated relationship drama"],
            ),
            [
                SuppressedReading(reading="generic self/other balance", reason="Direction known iken bu chapter yalnız denge diliyle anlatılamaz."),
                SuppressedReading(reading="fated relationship drama", reason="Node ekseni yön ve işbirliği kalıbını açar; olay tahmini yapmaz."),
            ],
            LifeChapterVoiceHints(valence_mode="integration", intensity_mode="medium", rhetorical_frame="directional", tone="friend-warm"),
        )
    if activation and overlap.get("has_overlap"):
        return (
            LifeChapterSemanticFocus(
                primary="axis_activation_of_old_pattern",
                secondary=["old_pattern_relevance", "directional_reselection"],
                not_this=["generic self/other balance"],
            ),
            "nodal_axis_activation",
            LifeChapterDomainOwnership(
                primary_domain=chapter.domain,
                secondary_domains=["identity_presence"],
                rationale="Node activation aynı sign/house overlap ile eski yön kalıbını chapter merkezine taşıyor.",
            ),
            LifeChapterRendererHandoff(
                human_scene=_default_human_scene(house),
                core_contrast="eski yön refleksine geri düşmek ile daha seçilmiş yeni yönü almak",
                chapter_weight="major axis activation inside larger chapter",
                chart_specific_anchor="aynı sign/house overlap ile eski eksensel kalıbın yeniden görünür olması",
                voice_register="integration / medium",
                avoid_readings=["generic self/other balance", "surface transit drama"],
            ),
            [
                SuppressedReading(reading="generic self/other balance", reason="Overlap varsa bu chapter daha eksensel ve kalıp-odaklıdır."),
                SuppressedReading(reading="surface transit drama", reason="Node activation burada olay değil, eski yön refleksinin geri çağrılmasıdır."),
            ],
            LifeChapterVoiceHints(valence_mode="integration", intensity_mode="medium", rhetorical_frame="axis_activation", tone="friend-warm"),
        )

    return (
        LifeChapterSemanticFocus(
            primary=_default_semantic_focus_primary(chapter_type=chapter.chapter_type.value, house=house),
            secondary=["direction_repatterning"],
            not_this=["generic self/other balance"],
        ),
        _default_meaning_family(chapter_type=chapter.chapter_type.value, house=house),
        LifeChapterDomainOwnership(
            primary_domain=chapter.domain,
            secondary_domains=[],
            rationale="Node chapter tekrar eden yön kalıbını generic denge söyleminden daha spesifik bir seçime taşımalıdır.",
        ),
        LifeChapterRendererHandoff(
            human_scene=_default_human_scene(house),
            core_contrast="eski yön alışkanlığı ile daha bilinçli seçim",
            chapter_weight="major axis chapter",
            chart_specific_anchor=chapter.selected_meaning,
            voice_register="integration / medium",
            avoid_readings=["generic self/other balance"],
        ),
        [SuppressedReading(reading="generic self/other balance", reason="Direction ekseni bilinmeden balance klişesi güvenli değildir.")],
        LifeChapterVoiceHints(valence_mode="integration", intensity_mode="medium", rhetorical_frame="directional", tone="friend-warm"),
    )


def _maybe_merge_overlapping_tier1_chapters(
    built: Sequence[tuple[LifeChapterCandidate, LifeChapter, LifeChapterEnrichmentContext]],
) -> LifeChapter | None:
    saturn_bundle = next(
        (
            bundle
            for bundle in built
            if _safe_str(bundle[0].get("chapter_type")) == ChapterType.SATURN_RETURN.value
            and isinstance(bundle[2].get("overlap"), Mapping)
            and bool((bundle[2].get("overlap") or {}).get("has_overlap"))
        ),
        None,
    )
    if saturn_bundle is None:
        return None

    secondary = next(
        (
            bundle
            for bundle in built
            if bundle is not saturn_bundle
            and _safe_str(bundle[0].get("chapter_type")) in {ChapterType.NODAL_RETURN.value, ChapterType.NODAL_ACTIVATION.value}
        ),
        None,
    )
    if secondary is None:
        return None

    primary_candidate, primary_chapter, primary_ctx = saturn_bundle
    secondary_candidate, secondary_chapter, _secondary_ctx = secondary
    evidence = list(primary_chapter.evidence)
    evidence.append(
        LifeChapterEvidence(
            factor=f"{_safe_str(secondary_candidate.get('chapter_type'))} overlap",
            role="axis_overlap",
            explanation="Saturn return ile node activation aynı sign/house ekseninde çakıştığı için bu chapter birleşik okunuyor.",
        )
    )
    suppressed = [
        {
            "source_signal_id": _safe_str(candidate.get("source_signal_id")),
            "chapter_type": _safe_str(candidate.get("chapter_type")),
            "reason": "merged into primary saturn_return via axis overlap",
        }
        for candidate, _chapter, _ctx in built
        if candidate is not primary_candidate and candidate is not secondary_candidate
    ]
    merged = _validated_chapter_update(
        primary_chapter,
        {
            "evidence": evidence,
        },
    )
    return _apply_debug_updates(
        merged,
        {
            "merge_reason": f"saturn_return + {_safe_str(secondary_candidate.get('chapter_type'))} merged via same-sign-house axis overlap",
            "selection_reason": "highest-confidence Tier-1 merge via axis overlap",
            "suppressed_candidates": suppressed,
            "confidence_rationale": _confidence_rationale(primary_ctx),
            "overlap_reason": "natal South Node in same sign/house as Saturn return — axis activation",
            "merged_secondary_chapter_type": _safe_str(secondary_candidate.get("chapter_type")),
        },
    )


def _apply_debug_updates(chapter: LifeChapter, updates: Mapping[str, Any]) -> LifeChapter:
    debug = dict(chapter.debug or {})
    debug.update(dict(updates))
    return _validated_chapter_update(chapter, {"debug": debug})


def _validated_chapter_update(chapter: LifeChapter, updates: Mapping[str, Any]) -> LifeChapter:
    payload = chapter.model_dump()
    payload.update(dict(updates))
    return LifeChapter(**payload)


def _node_overlap_info(*, event: Mapping[str, Any], natal_context: Mapping[str, Any]) -> dict[str, Any]:
    bodies_map = natal_context.get("bodies_map") if isinstance(natal_context.get("bodies_map"), Mapping) else {}
    saturn = bodies_map.get("saturn") if isinstance(bodies_map, Mapping) else None
    nodes = {
        key: bodies_map.get(key)
        for key in ("north_node", "south_node")
        if isinstance(bodies_map.get(key), Mapping)
    }
    if not isinstance(saturn, Mapping) or not nodes:
        return {
            "has_overlap": False,
            "matched_nodes": [],
            "same_sign": False,
            "same_house": False,
        }

    saturn_sign = _safe_str(saturn.get("sign"))
    saturn_house = _safe_int(saturn.get("house"))
    source_bodies = {normalize_point_token(value) for value in (event.get("source_bodies") or []) if _safe_str(value)}
    target_points = {normalize_point_token(value) for value in (event.get("target_points") or []) if _safe_str(value)}
    if "saturn" not in source_bodies and "saturn" not in target_points and normalize_point_token(event.get("event_subtype")) != "saturn_return":
        return {
            "has_overlap": False,
            "matched_nodes": [],
            "same_sign": False,
            "same_house": False,
        }

    matched_nodes: list[str] = []
    same_sign = False
    same_house = False
    for node_id, node in nodes.items():
        node_sign = _safe_str(node.get("sign"))
        node_house = _safe_int(node.get("house"))
        sign_match = bool(saturn_sign and node_sign and saturn_sign == node_sign)
        house_match = saturn_house is not None and node_house is not None and saturn_house == node_house
        if sign_match or house_match:
            matched_nodes.append(node_id)
        same_sign = same_sign or sign_match
        same_house = same_house or house_match

    return {
        "has_overlap": bool(matched_nodes),
        "matched_nodes": matched_nodes,
        "same_sign": same_sign,
        "same_house": same_house,
        "saturn_sign": saturn_sign,
        "saturn_house": saturn_house,
    }


def _primary_house(
    *,
    event: Mapping[str, Any],
    natal_context: Mapping[str, Any],
    chapter_type: str,
    overlap: Mapping[str, Any],
) -> int | None:
    if chapter_type == ChapterType.SATURN_RETURN.value and overlap.get("same_house"):
        return _safe_int(overlap.get("saturn_house"))
    bodies_map = natal_context.get("bodies_map") if isinstance(natal_context.get("bodies_map"), Mapping) else {}
    if chapter_type == ChapterType.SATURN_RETURN.value:
        return _safe_int((bodies_map.get("saturn") or {}).get("house")) or _first_house_from_event(event)
    if chapter_type == ChapterType.NODAL_RETURN.value:
        return _safe_int((bodies_map.get("north_node") or {}).get("house")) or _first_house_from_event(event)
    if chapter_type == ChapterType.NODAL_ACTIVATION.value:
        if overlap.get("same_house"):
            return _safe_int(overlap.get("saturn_house"))
        return _safe_int((bodies_map.get("north_node") or {}).get("house")) or _first_house_from_event(event)
    return _first_house_from_event(event)


def _primary_sign(
    *,
    event: Mapping[str, Any],
    natal_context: Mapping[str, Any],
    chapter_type: str,
    overlap: Mapping[str, Any],
) -> str:
    bodies_map = natal_context.get("bodies_map") if isinstance(natal_context.get("bodies_map"), Mapping) else {}
    if chapter_type == ChapterType.SATURN_RETURN.value and _safe_str(overlap.get("saturn_sign")):
        return _safe_str(overlap.get("saturn_sign"))
    if chapter_type == ChapterType.SATURN_RETURN.value:
        return _safe_str((bodies_map.get("saturn") or {}).get("sign"))
    if chapter_type == ChapterType.NODAL_RETURN.value:
        return _safe_str((bodies_map.get("north_node") or {}).get("sign"))
    if chapter_type == ChapterType.NODAL_ACTIVATION.value:
        return _safe_str((bodies_map.get("north_node") or {}).get("sign")) or _safe_str(overlap.get("saturn_sign"))
    return ""


def _first_house_from_event(event: Mapping[str, Any]) -> int | None:
    houses = event.get("target_houses")
    if isinstance(houses, list):
        for value in houses:
            house = _safe_int(value)
            if house is not None:
                return house
    return None


def _core_question(*, chapter_type: str, sign: str, house: int | None, overlap: Mapping[str, Any]) -> str:
    zone = _zone_text(sign=sign, house=house)
    if chapter_type == ChapterType.SATURN_RETURN.value:
        if overlap.get("has_overlap"):
            return f"{zone} eski reflekslerini daha seçilmiş bir otoriteye nasıl dönüştürüyorsun?"
        return f"{zone} daha sorumlu ve daha kalıcı bir omurgaya nasıl yerleşiyor?"
    if chapter_type == ChapterType.NODAL_RETURN.value:
        return f"{zone} tekrar eden yön kalıpları daha bilinçli bir hatta nasıl toplanıyor?"
    return f"{zone} ekseninde eski yön refleksi ile yeni seçim arasındaki fark nasıl belirginleşiyor?"


def _selected_meaning(*, chapter_type: str, sign: str, house: int | None, overlap: Mapping[str, Any]) -> str:
    zone = _zone_text(sign=sign, house=house)
    if chapter_type == ChapterType.SATURN_RETURN.value:
        if overlap.get("has_overlap"):
            return f"{zone} eski refleksif çıkışların, düğüm temasıyla birlikte daha sorumlu ve daha seçilmiş bir forma yerleşmesi"
        return f"{zone} daha hızlı çıkan reflekslerin daha sorumlu ve daha seçilmiş bir omurgaya yerleşmesi"
    if chapter_type == ChapterType.NODAL_RETURN.value:
        return f"{zone} tekrar eden yön ve ilişki kalıplarının daha bilinçli bir eksene oturması"
    return f"{zone} eksenindeki eski yön reflekslerinin görünür olup daha bilinçli bir ayar istemesi"


def _evidence(*, chapter_type: str, event: Mapping[str, Any], overlap: Mapping[str, Any]) -> list[LifeChapterEvidence]:
    subtype = _safe_str(event.get("event_subtype"))
    title = _safe_str(event.get("title_tr"))
    evidence = [
        LifeChapterEvidence(
            factor=title or subtype or _safe_str(event.get("event_id")) or "chapter_signal",
            role="chapter_trigger",
            explanation=_chapter_trigger_explanation(chapter_type, subtype),
        )
    ]
    if overlap.get("has_overlap"):
        matched_nodes = ", ".join(str(node) for node in overlap.get("matched_nodes") or [])
        evidence.append(
            LifeChapterEvidence(
                factor="node_overlap",
                role="supporting_signal",
                explanation=f"Satürn hattı natal {matched_nodes} ile aynı sign/house alanında çalışıyor; bu chapter daha eksensel bir ağırlık kazanıyor.",
            )
        )
    return evidence


def _suppressed_readings(*, chapter_type: str, overlap: Mapping[str, Any]) -> list[SuppressedReading]:
    if chapter_type == ChapterType.SATURN_RETURN.value:
        reason = "Bu chapter sadece iletişim zorluğu değil; natal Satürn temasının daha kalıcı bir omurgaya yerleşmesi."
        if overlap.get("has_overlap"):
            reason = "Satürn dönüşü node overlap ile birlikte çalıştığı için mesele sırf iletişim stresi değil, eski yön reflekslerinin olgunlaşması."
        return [
            SuppressedReading(
                reading="generic communication difficulty",
                reason=reason,
            )
        ]
    if chapter_type == ChapterType.NODAL_RETURN.value:
        return [
            SuppressedReading(
                reading="fated event prediction",
                reason="Nodal return burada kader cümlesi üretmek için değil, tekrar eden yön kalıplarını görünür kılmak için tutuluyor.",
            )
        ]
    return [
        SuppressedReading(
            reading="generic relationship or direction drama",
            reason="Nodal activation eksensel bir tekrar temasını işaret eder; bunu tek başına olay tahminine çevirmiyoruz.",
        )
    ]


def _suppressed_surface_readings(*, chapter_type: str, house: int | None, overlap: Mapping[str, Any]) -> list[SuppressedReading]:
    if chapter_type == ChapterType.SATURN_RETURN.value and house == 3:
        return [
            SuppressedReading(reading="generic communication difficulty", reason="3. ev sahnesi var diye chapter iletişim problemi diye daraltılmıyor."),
            SuppressedReading(reading="sibling conflict prediction", reason="Yakın çevre alanı tetiklenebilir ama seçilen meaning söz ve refleks otoritesinin olgunlaşmasıdır."),
        ]
    if chapter_type == ChapterType.SATURN_RETURN.value and house == 8:
        return [
            SuppressedReading(reading="generic emotional regulation", reason="8. ev bağlamı varsa meaning ortak yük, güven ve mahrem paylaşım ekseninde tutulur."),
            SuppressedReading(reading="body-rhythm reading", reason="1./6. ev ya da beden backing'i olmadan chapter beden rutmine indirgenmez."),
        ]
    if chapter_type == ChapterType.STRUCTURAL_NATAL_CHAPTER.value:
        return [
            SuppressedReading(reading="two-needs-only simplification", reason="T-square varsa üç parçalı basınç sistemi iki ihtiyaç cümlesine indirgenmemeli."),
        ]
    return [
        SuppressedReading(reading="generic fallback reading", reason="Seçilen chapter meaning'i yüzey bir astroloji kısayoluna indirgenmiyor."),
    ]


def _default_meaning_family(*, chapter_type: str, house: int | None) -> str:
    if chapter_type == ChapterType.SATURN_RETURN.value and house == 3:
        return "speech_authority_maturation"
    if chapter_type == ChapterType.SATURN_RETURN.value and house == 8:
        return "shared_trust_maturation"
    if chapter_type == ChapterType.SATURN_RETURN.value and house == 10:
        return "public_authority_maturation"
    if chapter_type == ChapterType.NODAL_RETURN.value:
        return "directional_axis_return"
    if chapter_type == ChapterType.NODAL_ACTIVATION.value:
        return "directional_axis_activation"
    return f"{chapter_type}_meaning"


def _default_semantic_focus_primary(*, chapter_type: str, house: int | None) -> str:
    if chapter_type == ChapterType.SATURN_RETURN.value and house == 3:
        return "speech_authority"
    if chapter_type == ChapterType.SATURN_RETURN.value and house == 8:
        return "shared_emotional_territory"
    if chapter_type == ChapterType.SATURN_RETURN.value and house == 10:
        return "public_authority_settling"
    if chapter_type == ChapterType.NODAL_RETURN.value:
        return "directional_axis"
    if chapter_type == ChapterType.NODAL_ACTIVATION.value:
        return "axis_activation"
    if chapter_type == ChapterType.STRUCTURAL_NATAL_CHAPTER.value:
        return "three_part_pressure_system"
    return "chapter_focus"


def _default_human_scene(house: int | None) -> str:
    scenes = {
        3: "kısa mesajlar, gündelik konuşmalar, yarım kalmış cümleler",
        4: "ev, iç düzen, kendine ait hissettiğin alan",
        8: "mahrem konuşmalar, ortak yükler, güven verirken zorlanan anlar",
        10: "görünür rol, beklenti konuşmaları, kamusal duruş",
    }
    return scenes.get(house, "gündelik sahnede tekrar eden küçük karar anları")


def _default_voice_hints(*, chapter_type: str, house: int | None) -> LifeChapterVoiceHints:
    if chapter_type == ChapterType.SATURN_RETURN.value and house == 3:
        return LifeChapterVoiceHints(valence_mode="maturation", intensity_mode="medium", rhetorical_frame="construction", tone="friend-warm")
    if chapter_type == ChapterType.SATURN_RETURN.value and house == 8:
        return LifeChapterVoiceHints(valence_mode="maturation", intensity_mode="dense", rhetorical_frame="deepening", tone="friend-warm")
    if chapter_type == ChapterType.SATURN_RETURN.value and house == 10:
        return LifeChapterVoiceHints(valence_mode="maturation", intensity_mode="medium", rhetorical_frame="settling", tone="friend-warm")
    if chapter_type == ChapterType.NODAL_RETURN.value:
        return LifeChapterVoiceHints(valence_mode="momentum", intensity_mode="medium", rhetorical_frame="directional", tone="friend-warm")
    if chapter_type == ChapterType.NODAL_ACTIVATION.value:
        return LifeChapterVoiceHints(valence_mode="integration", intensity_mode="medium", rhetorical_frame="axis_activation", tone="friend-warm")
    return LifeChapterVoiceHints(valence_mode="maturation", intensity_mode="medium", rhetorical_frame="reflective", tone="friend-warm")


def _activated_natal_factors(*, chapter_type: str, house: int | None, overlap: Mapping[str, Any]) -> list[ActivatedNatalFactor]:
    factors: list[ActivatedNatalFactor] = []
    if chapter_type == ChapterType.SATURN_RETURN.value:
        factors.append(ActivatedNatalFactor(type="planet", id="natal_saturn"))
    elif chapter_type == ChapterType.NODAL_RETURN.value:
        factors.append(ActivatedNatalFactor(type="node", id="north_node"))
    else:
        factors.append(ActivatedNatalFactor(type="node", id="node_axis"))

    if house is not None:
        factors.append(ActivatedNatalFactor(type="house", id=f"house_{house}"))

    for node_id in overlap.get("matched_nodes") or []:
        factors.append(ActivatedNatalFactor(type="node", id=str(node_id)))
    return factors


def _infer_phase(event: Mapping[str, Any]) -> ChapterPhase:
    current_phase = _safe_str(event.get("current_phase") or event.get("phase")).lower()
    subtype = _safe_str(event.get("event_subtype")).lower()
    if current_phase in {"approaching", "applying", "building"}:
        return ChapterPhase.APPROACHING
    if current_phase in {"exact", "exactish", "active"}:
        return ChapterPhase.FIRST_PASS
    if current_phase in {"retrograde_review", "retro_review"} or "retro" in current_phase or "retro" in subtype:
        return ChapterPhase.RETROGRADE_REVIEW
    if current_phase in {"final", "final_pass", "final_settlement"}:
        return ChapterPhase.FINAL_PASS
    if current_phase in {"integrating", "separating", "waning"}:
        return ChapterPhase.INTEGRATING
    if not bool(event.get("chapter_opening")) and (_safe_float(event.get("precision_signal")) or 0.0) < 0.4:
        return ChapterPhase.BACKGROUND
    return ChapterPhase.FIRST_PASS


def _phase_details(event: Mapping[str, Any]) -> tuple[ChapterPhase, str, str]:
    phase = _infer_phase(event)
    current_phase = _safe_str(event.get("current_phase") or event.get("phase")).lower()
    if current_phase:
        source = "event_payload_phase_field"
        reason_map = {
            ChapterPhase.APPROACHING: "event metadata indicates first pass is still forming",
            ChapterPhase.FIRST_PASS: "event metadata indicates exact or active pass",
            ChapterPhase.RETROGRADE_REVIEW: "event metadata indicates retrograde or review pass",
            ChapterPhase.FINAL_PASS: "event metadata indicates settlement or final pass",
            ChapterPhase.INTEGRATING: "event metadata indicates integration or separating phase",
            ChapterPhase.BACKGROUND: "event metadata indicates background or low-intensity pass",
        }
        return phase, source, reason_map.get(phase, "event metadata supplied the chapter phase")

    precision = _safe_float(event.get("precision_signal")) or 0.0
    if precision >= 0.75:
        return phase, "orb_proximity", "high precision signal suggests an exact or near-exact active pass"
    return phase, "fallback_active", "no explicit phase metadata; detector used safe fallback rules"


def _domain_for_house(house: int | None) -> str:
    domain_map = {
        1: "identity_presence",
        2: "resources_selfworth",
        3: "communication_learning",
        4: "home_foundation",
        5: "creativity_expression",
        6: "work_rhythm",
        7: "relationships_agreements",
        8: "trust_transformation",
        9: "belief_direction",
        10: "public_role",
        11: "network_future",
        12: "inner_release",
    }
    return domain_map.get(house, "general_life_direction")


def _chapter_trigger_explanation(chapter_type: str, subtype: str) -> str:
    if chapter_type == ChapterType.SATURN_RETURN.value:
        return "Saturn return ana olgunlaşma döngüsünü doğrudan açıyor."
    if chapter_type == ChapterType.NODAL_RETURN.value:
        return "Nodal return tekrar eden yön ve ilişki kalıplarını chapter seviyesinde görünür kılıyor."
    if subtype == "nodal_opposition":
        return "Nodal opposition eksensel gerilimi artırdığı için bunu nodal activation chapter adayı olarak ele alıyoruz."
    return "Node teması chapter düzeyinde yeniden ağırlık kazanıyor."


def _saturn_selected_meaning(*, sign: str, house: int | None, overlap: Mapping[str, Any]) -> str:
    zone = _zone_text(sign=sign, house=house)
    house_meanings = {
        3: "söz ve zihinsel reflekslerin",
        8: "duygusal güvenlik ve derin bağ kurma biçiminin",
        10: "görünürlük ve kamusal rol taşıma biçiminin",
    }
    subject = house_meanings.get(house, "eski reflekslerinin ve yapı kurma biçiminin")
    if overlap.get("has_overlap"):
        return f"{zone} {subject}, düğüm ekseniyle birlikte, daha seçilmiş ve daha sorumlu bir forma yerleşmesi"
    if house == 8:
        return f"{zone} {subject} daha dayanıklı, daha ölçülü ve daha seçilmiş bir forma yerleşmesi"
    if house == 10:
        return f"{zone} {subject} daha sakin ama daha kalıcı bir otoriteye yerleşmesi"
    return f"{zone} {subject} daha seçilmiş, daha sorumlu bir forma yerleşmesi"


def _saturn_core_question(*, sign: str, house: int | None, overlap: Mapping[str, Any]) -> str:
    zone = _zone_text(sign=sign, house=house)
    house_questions = {
        3: "sözünü ve zihinsel reflekslerini",
        8: "duygusal güvenlik ve derin bağ kurma biçimini",
        10: "görünürlük ve kamusal rol taşıma biçimini",
    }
    subject = house_questions.get(house, "yapı kurma biçimini")
    if overlap.get("has_overlap"):
        return f"{zone} {subject} düğüm ekseniyle birlikte nasıl daha seçilmiş bir otoriteye dönüştürüyorsun?"
    return f"{zone} {subject} nasıl daha seçilmiş ve daha kalıcı bir forma dönüştürüyorsun?"


def _saturn_placement_factor(*, sign: str, house: int | None) -> str:
    sign_label = _sign_label_tr(sign)
    if sign_label and house is not None:
        return f"Natal Saturn in {sign_label} {house}"
    if sign_label:
        return f"Natal Saturn in {sign_label}"
    if house is not None:
        return f"Natal Saturn in house {house}"
    return "Natal Saturn placement"


def _saturn_placement_explanation(*, sign: str, house: int | None, ruled_houses: Sequence[int]) -> str:
    zone = _zone_text(sign=sign, house=house)
    if ruled_houses:
        ruled = ", ".join(str(house_id) for house_id in ruled_houses[:3])
        return f"{zone} Satürn bu chapter'da yalnız yerleşimini değil, yönettiği {ruled}. ev başlıklarını da olgunlaştırıyor."
    return f"{zone} Satürn'ün natal yerleşimi bu chapter'ın hangi yaşam sahnesinde olgunlaşacağını belirliyor."


def _zone_text(*, sign: str, house: int | None) -> str:
    sign_label = _sign_label_tr(sign)
    if sign_label and house is not None:
        return f"{sign_label} {house}. ev hattında"
    if sign_label:
        return f"{sign_label} hattında"
    if house is not None:
        return f"{house}. ev hattında"
    return "bu hatta"


def _sign_label_tr(sign: str) -> str:
    mapping = {
        "Aries": "Koç",
        "Taurus": "Boğa",
        "Gemini": "İkizler",
        "Cancer": "Yengeç",
        "Leo": "Aslan",
        "Virgo": "Başak",
        "Libra": "Terazi",
        "Scorpio": "Akrep",
        "Sagittarius": "Yay",
        "Capricorn": "Oğlak",
        "Aquarius": "Kova",
        "Pisces": "Balık",
        "Koç": "Koç",
        "Boğa": "Boğa",
        "İkizler": "İkizler",
        "Yengeç": "Yengeç",
        "Aslan": "Aslan",
        "Başak": "Başak",
        "Terazi": "Terazi",
        "Akrep": "Akrep",
        "Yay": "Yay",
        "Oğlak": "Oğlak",
        "Kova": "Kova",
        "Balık": "Balık",
    }
    return mapping.get(sign, sign)


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_float(value: Any) -> float | None:
    try:
        return round(float(value), 3)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
