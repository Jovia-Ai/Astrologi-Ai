"""API route for natal chart interpretation using the rule engine."""
from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
from time import perf_counter
from types import SimpleNamespace
from typing import Any, Dict, List, Mapping, Sequence


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.ai.narrative.formatter import (
    build_formatted_aspects,
    build_formatted_house_positions,
    build_formatted_planet_positions,
)
from app.builders.composite_builder import build_composite_layer, split_composites
from app.builders.composite_fragments import CompositeFragmentsBuilder
from app.builders.composite_guidance import build_guidance
from app.builders.composite_interpreter import CompositeInterpretationBuilder
from app.builders.composite_regulator import build_composite_regulation
from app.builders.meta_binding import build_meta_summary
from app.builders.narrative_binding import build_core_story_plan, build_narrative
from app.builders.narrative_renderer_v26 import render_core_story
from app.builders.narrative_builder import JoviaSemanticNarrativeBuilder, SLOT_NAMES
from app.builders.output_compactor import build_user_compact
from app.builders.phase2_selector import select_phase2_fragments
from app.builders.semantic_normalizer import contains_verb_phrase, normalize_slot_text
from app.builders.upper_meaning_gate import build_upper_meaning_output
from app.engine.aspect_mechanics import AspectMechanicsEngine
from app.engine.astro_dynamics_engine import AstroDynamicsEngine
from app.engine.pattern_context_engine import PatternContextEngine
from app.engine.composite_meaning_engine import CompositeMeaningEngineV1
from app.engine.composite_engine import CompositeEngine
from app.engine.pattern_engine import PatternEmphasisEngine
from app.engine.router import build_combined_insights
from app.engine.rule_engine import CATEGORIES, RuleEngine, TYPE_NAMES
from app.engine.upper_meaning_engine import UpperMeaningEngine
from app.engine.meaning_weighting import build_meaning_weighting
from app.engine.narrative_anchor import build_narrative_anchor
from app.engine.inquiry_engine import InquiryEngine
from app.engine.dispositor_flow import DispositorFlowEngine
from app.engine.activation_sensitivity import ActivationSensitivityEngine
from app.engine.axis_activation import AxisActivationEngine
from app.engine.latent_potential import LatentPotentialEngine
from app.helpers.pressure_support import calculate_pressure_support
from app.helpers.strain_resilience import build_strain_resilience
from app.resolvers.expression_resolver import ExpressionResolver
from app.services.chart_service import (
    compute_natal_chart,
    serialize_aspects,
    serialize_planets,
)
from app.helpers.narrative_context import derive_core_aspects, derive_placements
from app.helpers.domain_normalizer import canon_domain
from app.helpers.normalize import normalize_node_alias, normalize_planet_key, normalize_aspect_type
from app.engine.astro_normalize import aspect_strength, clamp01
from app.natal.public_builder import build_public_natal_view
from app.natal.natal_graph import build_natal_graph
from app.natal.natal_graph_v2 import build_natal_graph_v2
from app.natal.narrative.core_story_tr_natal import build_core_story_ui
from app.natal.personality_imprint import build_personality_imprint
from app.natal.narrative.profile_narrative_engine import build_profile_narrative
from app.natal.supporting_threads_builder import build_sections_v2, build_supporting_threads
from app.services.performance.cache_store import default_cache_store, utc_now

logger = logging.getLogger(__name__)


def _json_safe(value: Any) -> Any:
    if isinstance(value, set):
        return sorted(value)
    return str(value)


def _payload_size_bytes(payload: Any) -> int:
    return len(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            default=_json_safe,
        ).encode("utf-8")
    )

router = APIRouter(tags=["natal"])
rule_engine = RuleEngine()


class NatalInterpretationRequest(BaseModel):
    """Request body containing the birth data required for natal calculations."""

    model_config = ConfigDict(str_strip_whitespace=True)

    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format.")
    birth_time: str = Field(..., description="Birth time in HH:MM format.")
    birth_place: str = Field(..., description="City + country or recognizable location label.")
    locale: str | None = None


def _log_natal_timing(
    *,
    endpoint: str,
    request: NatalInterpretationRequest,
    response: Mapping[str, Any],
    duration_ms: float,
) -> None:
    if not os.getenv("ENABLE_TIMING_LOGS", "true").strip().lower() in {"1", "true", "yes", "on"}:
        return
    logger.info(
        "natal_timing %s",
        json.dumps(
            {
                "endpoint": endpoint,
                "cache_status": "not_cached",
                "birth_place": request.birth_place,
                "locale": request.locale or "tr",
                "duration_ms": round(duration_ms, 3),
                "payload_bytes": _payload_size_bytes(response),
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
    )


def _profile_fast_cache_key(request: NatalInterpretationRequest) -> str:
    digest = hashlib.sha1(
        "|".join(
            [
                request.birth_date.strip(),
                request.birth_time.strip(),
                request.birth_place.strip().lower(),
                (request.locale or "tr").strip().lower(),
            ]
        ).encode("utf-8")
    ).hexdigest()
    return f"profile_fast:v1:{digest}"


def _extract_fast_sign(planets: Sequence[Mapping[str, Any]], body: str) -> str:
    target = body.strip().lower()
    for item in planets:
        name = str(item.get("planet") or item.get("name") or "").strip().lower()
        if name != target:
            continue
        sign = str(item.get("sign") or item.get("zodiac_sign") or "").strip()
        if sign:
            return sign
    return ""


def _profile_fast_ruler_for_sign(sign: str) -> str:
    normalized = sign.strip().lower()
    if normalized in {"aries"}:
        return "Mars"
    if normalized in {"taurus"}:
        return "Venus"
    if normalized in {"gemini", "virgo"}:
        return "Mercury"
    if normalized in {"cancer"}:
        return "Moon"
    if normalized in {"leo"}:
        return "Sun"
    if normalized in {"libra"}:
        return "Venus"
    if normalized in {"scorpio"}:
        return "Mars"
    if normalized in {"sagittarius", "pisces"}:
        return "Jupiter"
    if normalized in {"capricorn", "aquarius"}:
        return "Saturn"
    return ""


def _build_profile_fast_payload(
    request: NatalInterpretationRequest,
) -> tuple[dict[str, Any], dict[str, float]]:
    chart_started = perf_counter()
    chart_data = compute_natal_chart(
        request.birth_date,
        request.birth_time,
        request.birth_place,
    )
    chart_compute_ms = (perf_counter() - chart_started) * 1000.0

    serialize_started = perf_counter()
    planets = serialize_planets(chart_data.get("planets", {}))
    angles = chart_data.get("angles") if isinstance(chart_data, Mapping) else None
    asc_sign = ""
    asc_degree = None
    if isinstance(angles, Mapping):
        asc_sign = str(angles.get("ascendant_sign") or "").strip()
        asc_degree = angles.get("ascendant")
        if asc_sign and not any(
            str(entry.get("planet") or "").strip().lower() == "ascendant"
            for entry in planets
            if isinstance(entry, Mapping)
        ):
            planets.append(
                {
                    "planet": "Ascendant",
                    "sign": asc_sign,
                    "house": 1,
                    "degree": asc_degree,
                    "is_point": True,
                }
            )

    sun_sign = _extract_fast_sign(planets, "Sun")
    moon_sign = _extract_fast_sign(planets, "Moon")
    rising_sign = _extract_fast_sign(planets, "Ascendant") or asc_sign
    chart_ruler = _profile_fast_ruler_for_sign(rising_sign)
    chart_ruler_house = None
    placements: list[dict[str, Any]] = []
    for item in planets:
        label = str(item.get("planet") or item.get("name") or "").strip()
        sign = str(item.get("sign") or item.get("zodiac_sign") or "").strip()
        house = item.get("house")
        if not label or not sign or house in (None, ""):
            continue
        if chart_ruler and label.lower() == chart_ruler.lower() and chart_ruler_house is None:
            try:
                chart_ruler_house = int(house)
            except (TypeError, ValueError):
                chart_ruler_house = None
        placements.append(
            {
                "label": label,
                "sign": sign,
                "house": house,
            }
        )

    payload = {
        "profile_fast": {
            "sun_sign": sun_sign,
            "moon_sign": moon_sign,
            "rising_sign": rising_sign,
            "chart_ruler": chart_ruler,
            "chart_ruler_house": chart_ruler_house,
            "placements": placements,
        }
    }
    serialization_ms = (perf_counter() - serialize_started) * 1000.0
    return payload, {
        "chart_compute_ms": round(chart_compute_ms, 3),
        "serialization_ms": round(serialization_ms, 3),
    }


def _log_profile_fast_timing(
    *,
    request: NatalInterpretationRequest,
    response: Mapping[str, Any],
    duration_ms: float,
    cache_status: str,
    cache_key: str,
    chart_compute_ms: float,
    serialization_ms: float,
) -> None:
    if not os.getenv("ENABLE_TIMING_LOGS", "true").strip().lower() in {"1", "true", "yes", "on"}:
        return
    logger.info(
        "profile_fast_timing %s",
        json.dumps(
            {
                "endpoint": "/profile/fast",
                "cache_status": cache_status,
                "cache_key": cache_key,
                "birth_place": request.birth_place,
                "locale": request.locale or "tr",
                "duration_ms": round(duration_ms, 3),
                "chart_compute_ms": round(chart_compute_ms, 3),
                "serialization_ms": round(serialization_ms, 3),
                "payload_bytes": _payload_size_bytes(response),
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
    )


@router.post("/profile/fast")
def profile_fast(
    request: NatalInterpretationRequest,
) -> Dict[str, Any]:
    started = perf_counter()
    cache_key = _profile_fast_cache_key(request)
    lookup = default_cache_store.get(cache_key, now=utc_now())
    if lookup.status == "hit" and lookup.entry is not None:
        payload = dict(lookup.entry.value)
        payload["cache_status"] = "hit"
        _log_profile_fast_timing(
            request=request,
            response=payload,
            duration_ms=(perf_counter() - started) * 1000.0,
            cache_status="hit",
            cache_key=cache_key,
            chart_compute_ms=0.0,
            serialization_ms=0.0,
        )
        return payload

    payload, timing = _build_profile_fast_payload(request)
    response = {
        **payload,
        "cache_status": "miss",
    }
    default_cache_store.set(
        cache_key,
        {key: value for key, value in response.items() if key != "cache_status"},
        ttl_seconds=60 * 60,
        stale_ttl_seconds=5 * 60,
        now=utc_now(),
    )
    _log_profile_fast_timing(
        request=request,
        response=response,
        duration_ms=(perf_counter() - started) * 1000.0,
        cache_status="miss",
        cache_key=cache_key,
        chart_compute_ms=timing["chart_compute_ms"],
        serialization_ms=timing["serialization_ms"],
    )
    return response


@router.post("/interpret")
def interpret_natal_chart(
    request: NatalInterpretationRequest,
    debug: bool = False,
    output_profile: str = "user_compact",
    profile_engine: str | None = None,
) -> Dict[str, Any]:
    """Free deterministic interpretation endpoint (JoviaWeighted narratives)."""
    started = perf_counter()
    base_payload = _prepare_payload(
        request,
        premium_mode=False,
        debug_mode=debug,
        profile_engine=profile_engine,
    )
    response = _finalize_response(
        base_payload,
        premium_mode=False,
        debug_mode=debug,
        output_profile=output_profile,
    )
    _log_natal_timing(
        endpoint="/interpret",
        request=request,
        response=response,
        duration_ms=(perf_counter() - started) * 1000.0,
    )
    return response


@router.post("/interpret/ui")
def interpret_natal_chart_ui(
    request: NatalInterpretationRequest,
    debug: bool = False,
    include_debug: bool = False,
    profile_engine: str | None = None,
) -> Dict[str, Any]:
    started = perf_counter()
    base_payload = _prepare_payload(
        request,
        premium_mode=False,
        debug_mode=debug,
        profile_engine=profile_engine,
    )
    response = _finalize_response(
        base_payload,
        premium_mode=False,
        debug_mode=debug,
        output_profile="user_compact",
    )
    public = build_public_natal_view(response, locale=request.locale or "tr", include_debug=include_debug)
    payload = {"public": public}
    _log_natal_timing(
        endpoint="/interpret/ui",
        request=request,
        response=payload,
        duration_ms=(perf_counter() - started) * 1000.0,
    )
    return payload


@router.post("/interpret/debug")
def interpret_natal_chart_debug(
    request: NatalInterpretationRequest,
    debug: bool = False,
    profile_engine: str | None = None,
) -> Dict[str, Any]:
    if os.getenv("ENABLE_NATAL_DEBUG_ENDPOINTS", "false").strip().lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }:
        raise HTTPException(status_code=403, detail="Debug endpoint disabled")
    base_payload = _prepare_payload(
        request,
        premium_mode=False,
        debug_mode=True,
        profile_engine=profile_engine,
    )
    response = _finalize_response(
        base_payload,
        premium_mode=False,
        debug_mode=True,
        output_profile="user_compact",
    )
    public = build_public_natal_view(response, locale=request.locale or "tr", include_debug=True)
    return {"public": public, "debug": response}


@router.post("/interpret/premium")
def interpret_natal_chart_premium(
    request: NatalInterpretationRequest,
    debug: bool = False,
    output_profile: str = "user_compact",
    profile_engine: str | None = None,
) -> Dict[str, Any]:
    """Premium endpoint (PRO Jovia narratives)."""

    base_payload = _prepare_payload(
        request,
        premium_mode=True,
        debug_mode=debug,
        profile_engine=profile_engine,
    )
    return _finalize_response(
        base_payload,
        premium_mode=True,
        debug_mode=debug,
        output_profile=output_profile,
    )


@router.post("/interpret/premium/ui")
def interpret_natal_chart_premium_ui(
    request: NatalInterpretationRequest,
    debug: bool = False,
    include_debug: bool = False,
    profile_engine: str | None = None,
) -> Dict[str, Any]:
    base_payload = _prepare_payload(
        request,
        premium_mode=True,
        debug_mode=debug,
        profile_engine=profile_engine,
    )
    response = _finalize_response(
        base_payload,
        premium_mode=True,
        debug_mode=debug,
        output_profile="user_compact",
    )
    public = build_public_natal_view(response, locale=request.locale or "tr", include_debug=include_debug)
    return {"public": public}


@router.post("/interpret/premium/debug")
def interpret_natal_chart_premium_debug(
    request: NatalInterpretationRequest,
    debug: bool = False,
    profile_engine: str | None = None,
) -> Dict[str, Any]:
    if os.getenv("ENABLE_NATAL_DEBUG_ENDPOINTS", "false").strip().lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }:
        raise HTTPException(status_code=403, detail="Debug endpoint disabled")
    base_payload = _prepare_payload(
        request,
        premium_mode=True,
        debug_mode=True,
        profile_engine=profile_engine,
    )
    response = _finalize_response(
        base_payload,
        premium_mode=True,
        debug_mode=True,
        output_profile="user_compact",
    )
    public = build_public_natal_view(response, locale=request.locale or "tr", include_debug=True)
    return {"public": public, "debug": response}


def _build_metadata(request: NatalInterpretationRequest, chart_data: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "birth_date": request.birth_date,
        "birth_time": request.birth_time,
        "birth_place": request.birth_place,
        "location": chart_data.get("location"),
        "birth_datetime": chart_data.get("birth_datetime"),
        "timezone": chart_data.get("timezone"),
    }


def _prepare_payload(
    request: NatalInterpretationRequest,
    *,
    premium_mode: bool,
    debug_mode: bool = False,
    tone_enabled: bool = True,
    profile_engine: str | None = None,
) -> Dict[str, Any]:
    try:
        chart_data = compute_natal_chart(request.birth_date, request.birth_time, request.birth_place)
    except Exception as exc:  # pragma: no cover - network/env specific
        logger.exception("Failed to calculate natal chart from inputs")
        raise HTTPException(status_code=500, detail=f"Chart calculation failed: {exc}") from exc
    return _prepare_payload_from_chart(
        chart_data,
        premium_mode=premium_mode,
        debug_mode=debug_mode,
        tone_enabled=tone_enabled,
        request=request,
        profile_engine=profile_engine,
    )


def _prepare_payload_from_chart(
    chart_data: Mapping[str, Any],
    *,
    premium_mode: bool,
    debug_mode: bool = False,
    tone_enabled: bool = True,
    request: NatalInterpretationRequest | None = None,
    profile_engine: str | None = None,
) -> Dict[str, Any]:
    snapshots: Dict[str, Any] | None = {} if debug_mode else None

    planets = serialize_planets(chart_data.get("planets", {}))
    angles = chart_data.get("angles") if isinstance(chart_data, Mapping) else None
    if isinstance(angles, Mapping):
        asc_sign = angles.get("ascendant_sign")
        if asc_sign and not any(
            str(entry.get("planet") or "").strip().lower() == "ascendant"
            for entry in planets
            if isinstance(entry, Mapping)
        ):
            planets.append(
                {
                    "planet": "Ascendant",
                    "sign": asc_sign,
                    "house": 1,
                    "degree": angles.get("ascendant"),
                    "is_point": True,
                }
            )
    aspects = serialize_aspects(chart_data.get("aspects", []))
    natal_graph = build_natal_graph(chart_data=chart_data, planets=planets, aspects=aspects)
    interpretation, meta_info = rule_engine.interpret(planets=planets, aspects=aspects, return_meta=True)
    if snapshots is not None:
        snapshots["rule_engine_output_summary"] = _summarize_rule_engine(interpretation, meta_info)

    placements = derive_placements(planets)
    core_aspects = derive_core_aspects(aspects)
    composite_engine = CompositeEngine()
    composites = composite_engine.build_composites(chart_data)
    dispositor_engine = DispositorFlowEngine()
    dispositor_flow = dispositor_engine.build(placements)
    axis_engine = AxisActivationEngine()
    axis_activation = axis_engine.build(placements, core_aspects=aspects)
    aspect_engine = AspectMechanicsEngine()
    aspect_mechanics = aspect_engine.build(aspects)
    sensitivity_engine = ActivationSensitivityEngine()
    activation_sensitivity = sensitivity_engine.build(composites, aspect_mechanics)
    pattern_engine = PatternEmphasisEngine()
    patterns = pattern_engine.build(
        composites,
        placements=placements,
        core_aspects=core_aspects,
        meta_info=meta_info,
    )
    regulations = build_composite_regulation(composites, patterns, axis_activation)
    domain_regulators = _primary_domain_regulations(composites, patterns, regulations)
    phase2_fragments = select_phase2_fragments(
        interpretation,
        composites,
        meta_info,
        domain_regulators,
        axis_activation,
    )
    compressed_domains = phase2_fragments.pop("__compressed_domains__", None)
    latent_engine = LatentPotentialEngine()
    latent_potential = latent_engine.build(composites, patterns, aspect_mechanics)
    upper_engine = UpperMeaningEngine()
    upper_meanings = upper_engine.build(
        composites,
        patterns,
        core_aspects=core_aspects,
        aspect_mechanics=aspect_mechanics,
    )

    composite_guidance = build_guidance(
        composites,
        patterns,
        meta_info,
        dispositor_flow,
        axis_activation,
        activation_sensitivity,
    )
    guidance_probe: Dict[str, Any] = {
        "active_domains": list(composite_guidance.get("active_domains") or []),
    }
    if composite_guidance.get("domain_priority"):
        guidance_probe["domain_priority"] = composite_guidance.get("domain_priority")
    if snapshots is not None:
        snapshots["composite_guidance"] = _snapshot_composite_guidance(composite_guidance)

    narrative: Dict[str, str] = {}
    used_composites: List[str] = []
    narrative_meta: Dict[str, Any] = {}
    inquiry_engine = InquiryEngine()
    focus_result = inquiry_engine.select_focus(composites, patterns)
    domain_builder = CompositeInterpretationBuilder(
        composites,
        patterns,
        focus_composites=focus_result.get("focus_composites", []),
    )
    composite_interpretation = domain_builder.build()
    pressure_support = calculate_pressure_support(composites, patterns, axis_activation)
    meaning_weighting = build_meaning_weighting(
        pressure_index=pressure_support["pressure_index"],
        support_index=pressure_support["support_index"],
        dominant_domain=pressure_support["dominant_domain"],
        theme_shares=None,
        patterns=patterns,
        theme_mapper_result=None,
    )
    meta_info["strain_resilience"] = build_strain_resilience(
        pressure_support=pressure_support,
        meaning_weighting=meaning_weighting,
        aspect_mechanics=aspect_mechanics,
    )
    meta_summary = build_meta_summary(
        composites=composites,
        patterns=patterns,
        axis_activation=axis_activation,
        pressure_support=pressure_support,
        dispositor_flow=dispositor_flow,
        meta_info=meta_info,
        placements=placements,
        core_aspects=core_aspects,
    )
    composite_layer = build_composite_layer(
        composites,
        patterns=patterns,
        axis_activation=axis_activation,
        activation_sensitivity=activation_sensitivity,
        meta_summary=meta_summary,
        dispositor_flow=dispositor_flow,
        meta_info=meta_info,
    )
    composite_split = split_composites(composite_layer)
    expression_profile = ExpressionResolver.resolve(
        composite_output=composites,
        pressure_index=pressure_support["pressure_index"],
        support_index=pressure_support["support_index"],
        axis_balance=pressure_support["axis_balance"],
    )
    narrative_fragments, phase2_snapshot = _build_phase2_fragment_payload(phase2_fragments)
    potential_count = 0
    for entry in phase2_fragments.values():
        slots = entry.get("slots") or {}
        if slots.get("potential"):
            potential_count += 1
    local_pressure = compute_local_pressure(
        meta_info,
        phase2_snapshot,
        dynamic_insights=None,
        composite_meanings=None,
    )
    resilience_score = _safe_float(
        ((meta_info.get("strain_resilience") or {}).get("resilience") or {}).get("score")
    )
    uncertainty_score = _safe_float((meta_summary or {}).get("uncertainty"), 0.35)
    capacity_score = compute_capacity_score(
        support_index=pressure_support["support_index"],
        resilience=resilience_score,
        uncertainty=uncertainty_score,
    )
    integration_score, integration_components = compute_integration_score(
        aspects,
        meta_info,
        meta_summary,
    )
    upper_meaning_selected = build_upper_meaning_output(
        upper_meanings,
        pressure_index=pressure_support["pressure_index"],
        support_index=pressure_support["support_index"],
        capacity_score=capacity_score,
        integration_score=integration_score,
        integration_components=integration_components,
        dispositor_flow=dispositor_flow,
        latent_potential=latent_potential,
        potential_count=potential_count,
        axis_activation=axis_activation,
        dynamic_insights=None,
        premium_mode=premium_mode,
    )
    narrative_anchor = build_narrative_anchor(
        fragments_by_domain=narrative_fragments,
        dominant_domain=meaning_weighting["dominant_domain"],
        meaning_weighting=meaning_weighting,
    )
    if snapshots is not None:
        snapshots["semantic_normalizer_output_summary"] = phase2_snapshot["summary"]
        snapshots["phase2_slots"] = phase2_snapshot["slots"]
    phase2_fragment_probe: Dict[str, Any] = {
        "domains": list(phase2_fragments.keys()),
        "slot_counts": {},
    }
    total_slots = len(SLOT_NAMES)
    for domain, entry in phase2_fragments.items():
        slots = entry.get("slots") or {}
        filled = sum(1 for slot_name in SLOT_NAMES if slots.get(slot_name))
        ratio = filled / total_slots if total_slots else 0.0
        phase2_fragment_probe["slot_counts"][domain] = ratio
    expression_profile_probe: Dict[str, Any] = {
        "tone": expression_profile.get("tone"),
        "sentence_length": expression_profile.get("sentence_length"),
        "fallback_mode": expression_profile.get("fallback_mode"),
    }
    builder = JoviaSemanticNarrativeBuilder(
        SimpleNamespace(
            composites=composites,
            patterns=patterns,
            upper_meanings=upper_meanings,
            meta_info=meta_info,
            aspect_mechanics=aspect_mechanics,
            dispositor_flow=dispositor_flow,
            axis_activation=axis_activation,
            activation_sensitivity=activation_sensitivity,
            fragments=narrative_fragments,
            narrative_anchor=narrative_anchor,
            guidance=composite_guidance,
            regulations=domain_regulators,
            expression_profile=expression_profile,
            quality_gates=phase2_snapshot["quality_gates_applied"],
            meaning_weighting=meaning_weighting,
            tone_enabled=tone_enabled,
            compressed_domains=compressed_domains,
        )
    )
    narrative = builder.build()
    if builder.fallback_used:
        narrative_meta["fallback_used"] = True
    narrative_meta["expression_profile"] = expression_profile
    used_composites = list(builder.used_composite_ids)
    if snapshots is not None:
        snapshots["narrative_plan"] = builder.narrative_plan
    combined_insights = build_combined_insights(meta_info, interpretation)

    warnings = _collect_debug_warnings(
        phase2_snapshot,
        composite_guidance,
        builder,
        debug_mode,
    )

    runtime_info = {
        "engine": rule_engine.__class__.__name__,
        "narrative_builder": builder.__class__.__name__,
        "pipeline_version": "v2.4",
    }
    routing_info = {
        "active_domains_source": builder.narrative_debug_active_domains_source,
    }

    debug_info = {
        "used_domain_composites": domain_builder.used_composite_ids,
        "used_narrative_composites": used_composites,
        "triggered_patterns": sorted(patterns.keys()),
        "triggered_upper_meaning": [
            entry.get("composite_id")
            for entry in upper_meanings
            if entry.get("composite_id")
        ],
        "stellium_composites": sorted(
            comp_id for comp_id, meta in patterns.items() if meta.get("stellium")
        ),
        "dispositor_flow": dispositor_flow,
        "axis_activation": axis_activation,
        "activation_sensitivity": activation_sensitivity,
        "latent_potential": latent_potential,
        "composite_guidance": composite_guidance,
        "quality_actions_applied": builder.quality_actions_applied,
        "pressure_support": pressure_support,
        "local_pressure": local_pressure,
        "meaning_weighting": meaning_weighting,
        "expression_profile": expression_profile,
        "narrative_anchor": narrative_anchor,
        "guidance_probe": guidance_probe,
        "expression_profile_probe": expression_profile_probe,
        "phase2_fragments_probe": phase2_fragment_probe,
        "runtime": runtime_info,
        "narrative_debug_selected_domains": builder.narrative_debug_selected_domains,
        "narrative_debug_selected_slots": builder.narrative_debug_selected_slots,
        "narrative_debug_source_fragment_ids": builder.narrative_debug_source_fragment_ids,
        "narrative_debug_active_domains_source": builder.narrative_debug_active_domains_source,
        "tone_profile": builder.tone_profiles,
        "routing": routing_info,
        "natal_graph_compact": natal_graph.get("compact"),
    }
    if debug_mode:
        debug_info["warnings"] = warnings
        if snapshots:
            debug_info["snapshots"] = snapshots
    sections_v2 = build_sections_v2(
        chart_data=chart_data,
        planets=planets,
        natal_graph=natal_graph,
    )
    supporting_threads = build_supporting_threads(
        chart_data=chart_data,
        planets=planets,
        natal_graph=natal_graph,
        max_threads=4,
    )
    profile_narrative = build_profile_narrative(
        chart_data,
        natal_graph,
        locale=(request.locale if request else "tr") or "tr",
        include_debug=debug_mode,
        engine_override=(profile_engine or "").strip().lower() or None,
    )
    personality_imprint = build_personality_imprint(
        planets=planets,
        aspects=aspects,
        natal_graph=natal_graph,
        locale=(request.locale if request else "tr") or "tr",
        include_debug=debug_mode,
    )
    return {
        "chart_data": chart_data,
        "metadata": _build_metadata(request, chart_data) if request else _build_metadata_from_chart(chart_data),
        "planets": planets,
        "aspects": aspects,
        "formatted_positions": build_formatted_planet_positions(chart_data),
        "formatted_houses": build_formatted_house_positions(chart_data),
        "formatted_aspects": build_formatted_aspects(chart_data),
        "interpretation": interpretation,
        "meta_info": meta_info,
        "combined_insights": combined_insights,
        "meta_summary": meta_summary,
        "composites": composites,
        "composite_layer": composite_layer,
        "composite_split": composite_split,
        "patterns": patterns,
        "upper_meaning": upper_meanings,
        "upper_meaning_selected": upper_meaning_selected,
        "aspect_mechanics": aspect_mechanics,
        "composite_interpretation": composite_interpretation,
        "dispositor_flow": dispositor_flow,
        "axis_activation": axis_activation,
        "activation_sensitivity": activation_sensitivity,
        "latent_potential": latent_potential,
        "composite_guidance": composite_guidance,
        "meaning_weighting": meaning_weighting,
        "narrative_anchor": narrative_anchor,
        "natal_graph": natal_graph,
        "natal_graph_compact": natal_graph.get("compact"),
        "personality_imprint": personality_imprint,
        "profile_narrative": profile_narrative,
        "sections_v2": sections_v2,
        "supporting_threads": supporting_threads,
        "debug": debug_info,
        "local_pressure": local_pressure,
        "__narrative_fragments": narrative_fragments,
        "_phase2_snapshot": phase2_snapshot,
        "narrative_interpretation": narrative,
        "narrative_meta": narrative_meta,
        "expression_profile": expression_profile,
    }


def _build_metadata_from_chart(chart_data: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "birth_date": chart_data.get("birth_date"),
        "birth_time": chart_data.get("birth_time"),
        "birth_place": chart_data.get("birth_place"),
        "location": chart_data.get("location"),
        "birth_datetime": chart_data.get("birth_datetime"),
        "timezone": chart_data.get("timezone"),
    }


def build_natal_interpretation_response_from_chart(
    chart_data: Mapping[str, Any],
    *,
    output_profile: str = "user_compact",
    debug_mode: bool = False,
    tone_enabled: bool = True,
    premium_mode: bool = False,
) -> Dict[str, Any]:
    base_payload = _prepare_payload_from_chart(
        chart_data,
        premium_mode=premium_mode,
        debug_mode=debug_mode,
        tone_enabled=tone_enabled,
    )
    return _finalize_response(
        base_payload,
        premium_mode=premium_mode,
        debug_mode=debug_mode,
        output_profile=output_profile,
    )
def _finalize_response(
    base_payload: Mapping[str, Any],
    *,
    premium_mode: bool,
    debug_mode: bool = False,
    output_profile: str = "user_compact",
) -> Dict[str, Any]:
    legacy_enabled = os.getenv("ENABLE_LEGACY_NARRATIVE", "false").strip().lower() == "true"
    dynamic_enabled = os.getenv("ENABLE_DYNAMIC_INSIGHTS", "false").strip().lower() == "true"
    phase2_snapshot = base_payload.get("_phase2_snapshot") or {}
    response = {
        "metadata": base_payload["metadata"],
        "planets": base_payload["planets"],
        "aspects": base_payload["aspects"],
        "interpretation": base_payload["interpretation"],
        "meta_info": base_payload["meta_info"],
        "formatted_positions": base_payload["formatted_positions"],
        "formatted_houses": base_payload["formatted_houses"],
        "formatted_aspects": base_payload["formatted_aspects"],
        "combined_insights": base_payload["combined_insights"],
        "meta": base_payload.get("meta_summary") or {},
        "composites": base_payload.get("composite_split") or {"focus": [], "supporting": []},
        "patterns": base_payload["patterns"],
        "upper_meaning": base_payload["upper_meaning"],
        "upper_meaning_selected": base_payload.get("upper_meaning_selected"),
        "aspect_mechanics": base_payload["aspect_mechanics"],
        "composite_interpretation": base_payload.get("composite_interpretation", {}),
        "dispositor_flow": base_payload["dispositor_flow"],
        "axis_activation": base_payload["axis_activation"],
        "activation_sensitivity": base_payload["activation_sensitivity"],
        "latent_potential": base_payload["latent_potential"],
        "composite_guidance": base_payload["composite_guidance"],
        "meaning_weighting": base_payload["meaning_weighting"],
        "narrative_anchor": base_payload["narrative_anchor"],
        "natal_graph_compact": base_payload.get("natal_graph_compact"),
        "personality_imprint": base_payload.get("personality_imprint") or {},
        "profile_narrative": base_payload.get("profile_narrative") or {},
        "sections_v2": base_payload.get("sections_v2") or [],
        "supporting_threads": base_payload.get("supporting_threads") or [],
        "debug": base_payload["debug"],
        "phase2_snapshot": phase2_snapshot,
        "narrative_interpretation": base_payload["narrative_interpretation"] if legacy_enabled else "",
        "narrative_text": (
            base_payload.get("narrative_text") or base_payload.get("narrative_interpretation")
        )
        if legacy_enabled
        else "",
        "premium_mode": premium_mode,
        "expression_profile": base_payload.get("expression_profile"),
    }
    dynamic_insights = None
    enable_pattern_context = os.getenv("ENABLE_PATTERN_CONTEXT", "true").strip().lower() in {"1", "true", "yes", "on"}
    render_pattern_context = os.getenv("RENDER_PATTERN_CONTEXT", "false").strip().lower() in {"1", "true", "yes", "on"}
    composite_meanings = None
    if dynamic_enabled:
        chart_payload = {
            "planets": base_payload.get("planets") or [],
            "aspects": base_payload.get("aspects") or [],
            "formatted_positions": base_payload.get("formatted_positions") or [],
            "formatted_aspects": base_payload.get("formatted_aspects") or [],
            "formatted_houses": base_payload.get("formatted_houses") or [],
        }
        engine = AstroDynamicsEngine()
        theme_scores, dynamic_insights_payload = engine.build(
            chart_payload,
            base_payload.get("meta_info") or {},
            phase2_snapshot,
            base_payload.get("composite_split") or {},
            debug=debug_mode,
        )
        response["theme_scores"] = theme_scores
        response["dynamic_insights"] = dynamic_insights_payload
        dynamic_insights = response.get("dynamic_insights")
    if dynamic_insights and enable_pattern_context:
        patterns = (base_payload.get("meta_info") or {}).get("aspect_patterns") or []
        pattern_engine = PatternContextEngine()
        updated_spines = pattern_engine.build(
            patterns=patterns,
            spines=dynamic_insights.get("selected") or [],
            theme_scores=dynamic_insights.get("theme_scores") or {},
        )
        dynamic_insights["selected"] = updated_spines
        if render_pattern_context:
            dynamic_insights["render_pattern_context"] = True
    chart_payload = {
        "planets": base_payload.get("planets") or [],
        "aspects": base_payload.get("aspects") or [],
        "formatted_positions": base_payload.get("formatted_positions") or [],
        "formatted_aspects": base_payload.get("formatted_aspects") or [],
        "formatted_houses": base_payload.get("formatted_houses") or [],
    }
    composite_engine = CompositeMeaningEngineV1()
    composite_meanings = composite_engine.build_composite_meanings_v1(
        composites=base_payload.get("composites") or [],
        theme_scores=response.get("theme_scores"),
        dynamic_insights=dynamic_insights,
        debug=debug_mode,
    )
    response["composite_meanings"] = composite_meanings
    local_pressure = compute_local_pressure(
        base_payload.get("meta_info") or {},
        phase2_snapshot,
        dynamic_insights=dynamic_insights,
        composite_meanings=composite_meanings,
    )
    potential_count = 0
    for entry in (base_payload.get("__narrative_fragments") or {}).values():
        slots = entry.get("slots") or {}
        if slots.get("potential"):
            potential_count += 1
    pressure_support = (base_payload.get("debug") or {}).get("pressure_support") or {}
    resilience_score = _safe_float(
        ((base_payload.get("meta_info") or {}).get("strain_resilience") or {}).get("resilience", {}).get("score")
    )
    uncertainty_score = _safe_float((base_payload.get("meta_summary") or {}).get("uncertainty"), 0.35)
    capacity_score = compute_capacity_score(
        support_index=pressure_support.get("support_index", 0.0),
        resilience=resilience_score,
        uncertainty=uncertainty_score,
    )
    integration_score, integration_components = compute_integration_score(
        base_payload.get("aspects") or [],
        base_payload.get("meta_info") or {},
        base_payload.get("meta_summary") or {},
    )
    updated_upper_meaning = build_upper_meaning_output(
        base_payload.get("upper_meaning") or [],
        pressure_index=pressure_support.get("pressure_index", 0.0),
        support_index=pressure_support.get("support_index", 0.0),
        capacity_score=capacity_score,
        integration_score=integration_score,
        integration_components=integration_components,
        dispositor_flow=base_payload.get("dispositor_flow") or {},
        latent_potential=base_payload.get("latent_potential") or {},
        potential_count=potential_count,
        axis_activation=base_payload.get("axis_activation") or {},
        dynamic_insights=dynamic_insights,
        premium_mode=bool(base_payload.get("premium_mode")),
    )
    response["upper_meaning_selected"] = updated_upper_meaning
    response["local_pressure"] = local_pressure
    if isinstance(base_payload, dict):
        base_payload["upper_meaning_selected"] = updated_upper_meaning
        base_payload["local_pressure"] = local_pressure
        debug_entry = base_payload.get("debug")
        if isinstance(debug_entry, dict):
            debug_entry["upper_meaning_mode"] = updated_upper_meaning.get("mode")
            debug_entry["local_pressure"] = local_pressure
            debug_entry["upper_meaning_gate"] = _build_upper_meaning_gate_debug(
                updated_upper_meaning,
                meta_summary=base_payload.get("meta_summary") or {},
                pressure_support=pressure_support,
            )
    debug_entry = response.get("debug")
    if isinstance(debug_entry, dict):
        debug_entry["upper_meaning_mode"] = updated_upper_meaning.get("mode")
        debug_entry["local_pressure"] = local_pressure
        debug_entry["upper_meaning_gate"] = _build_upper_meaning_gate_debug(
            updated_upper_meaning,
            meta_summary=base_payload.get("meta_summary") or {},
            pressure_support=pressure_support,
        )
    if legacy_enabled:
        _ensure_narrative_presence(base_payload, response)
    else:
        debug_entry = response.get("debug")
        if isinstance(debug_entry, dict):
            debug_entry["narrative_deprecation"] = (
                "legacy narrative_interpretation is disabled; use core_story."
            )
    narrative_fragments = base_payload.get("__narrative_fragments") or {}
    response["core_story_plan"] = build_core_story_plan(
        phase2_snapshot,
        base_payload.get("meta_info") or {},
        base_payload.get("expression_profile"),
        base_payload.get("upper_meaning_selected"),
        dynamic_insights=dynamic_insights,
        composite_meanings=composite_meanings,
    )
    response["core_story"] = render_core_story(
        phase2_snapshot,
        response.get("core_story_plan") or {},
        base_payload.get("expression_profile"),
        dynamic_insights=response.get("dynamic_insights"),
        composite_meanings=composite_meanings,
        upper_meaning_selected=base_payload.get("upper_meaning_selected"),
        debug=debug_mode,
        debug_payload=response.get("debug") if debug_mode else None,
    )
    response["core_story_ui"] = build_core_story_ui(
        chart_data=base_payload.get("chart_data") or {},
        planets=base_payload.get("planets") or [],
        natal_graph=base_payload.get("natal_graph") or {},
    )
    response["data_quality"] = _build_data_quality_payload(
        response.get("core_story_plan") or {},
        base_payload.get("meta_summary") or {},
        base_payload.get("upper_meaning_selected") or {},
        debug_mode=debug_mode,
    )
    if debug_mode:
        debug_entry = response.get("debug")
        if isinstance(debug_entry, dict):
            chart_for_v2 = {
                **dict(base_payload.get("chart_data") or {}),
                "planets": list(base_payload.get("planets") or []),
                "aspects": list(base_payload.get("aspects") or []),
            }
            debug_entry["natal_graph_v2"] = build_natal_graph_v2(
                chart_for_v2,
                natal_graph=base_payload.get("natal_graph") or {},
            )
    meta_entry = response.get("meta")
    if isinstance(meta_entry, dict):
        meta_entry["deprecated_fields"] = ["narrative_interpretation", "narrative_text"]
    if output_profile != "debug":
        fragments = base_payload.get("__narrative_fragments") or {}
        response["user_compact"] = build_user_compact(
            fragments,
            phase2_snapshot=base_payload.get("_phase2_snapshot") or {},
            tone_profile=base_payload.get("expression_profile"),
        )
    if debug_mode:
        _record_final_response_snapshot(response, base_payload.get("debug") or {})
    return response


def _build_data_quality_payload(
    core_story_plan: Mapping[str, Any],
    meta_summary: Mapping[str, Any],
    upper_meaning: Mapping[str, Any],
    *,
    debug_mode: bool,
) -> Dict[str, Any]:
    data_quality = core_story_plan.get("data_quality") if isinstance(core_story_plan, Mapping) else {}
    summary = {
        "blocked_sections": data_quality.get("blocked_sections", []),
        "fallback_used_slots": data_quality.get("fallback_used", []),
        "missing_signals": data_quality.get("missing_slots", []),
        "confidence": meta_summary.get("support_index"),
        "uncertainty": meta_summary.get("pressure_index"),
    }
    if not debug_mode:
        return {"summary": summary}

    debug_detail = {
        "slot_empty_reasons": (core_story_plan.get("debug") or {}).get("slot_empty_reasons", {}),
        "fallback_sources": (core_story_plan.get("debug") or {}).get("fallback_sources", {}),
        "upper_meaning_reasons": (core_story_plan.get("debug") or {}).get(
            "upper_meaning_reasons", []
        ),
        "phase2_domains": (core_story_plan.get("debug") or {}).get("phase2_domains", []),
        "max_domains": (core_story_plan.get("debug") or {}).get("max_domains", 3),
        "upper_meaning_gate": _build_upper_meaning_gate_debug(
            upper_meaning,
            meta_summary=meta_summary,
            pressure_support={},
        ),
    }
    return {"summary": summary, "detail": debug_detail}


def _build_upper_meaning_gate_debug(
    upper_meaning: Mapping[str, Any],
    *,
    meta_summary: Mapping[str, Any],
    pressure_support: Mapping[str, Any],
) -> Dict[str, Any]:
    thresholds = upper_meaning.get("thresholds") or {
        "pressure_min": 0.45,
        "support_min": 0.45,
        "capacity_min": 0.55,
        "integration_min": 0.55,
    }
    pressure_index = _safe_float(meta_summary.get("pressure_index") or pressure_support.get("pressure_index"))
    support_index = _safe_float(meta_summary.get("support_index") or pressure_support.get("support_index"))
    debug_scores = upper_meaning.get("debug_scores") or {}
    return {
        "enabled": bool(upper_meaning.get("enabled")),
        "reasons": upper_meaning.get("reasons") or [],
        "pressure_index": round(pressure_index, 3),
        "support_index": round(support_index, 3),
        "capacity": debug_scores.get("capacity"),
        "integration": debug_scores.get("integration"),
        "thresholds": thresholds,
        "source": "meta_summary",
    }


def compute_local_pressure(
    meta_info: Mapping[str, Any],
    phase2_snapshot: Mapping[str, Any],
    dynamic_insights: Mapping[str, Any] | None,
    composite_meanings: Mapping[str, Any] | None,
) -> Dict[str, float]:
    _ = (meta_info, composite_meanings)
    local_pressure: Dict[str, float] = {}
    accepted = ((phase2_snapshot.get("slots") or {}).get("accepted") or [])
    has_slot_roles = any(isinstance(entry, Mapping) and entry.get("slot") for entry in accepted)

    if has_slot_roles:
        for entry in accepted:
            if not isinstance(entry, Mapping):
                continue
            domain = canon_domain(entry.get("domain"))
            if not domain:
                continue
            local_pressure.setdefault(domain, 0.0)
            if entry.get("slot") == "shadow":
                local_pressure[domain] += 0.25

        selected = (dynamic_insights or {}).get("selected")
        if isinstance(selected, list):
            for entry in selected:
                if not isinstance(entry, Mapping):
                    continue
                themes = [
                    canon_domain(theme)
                    for theme in (entry.get("themes") or [])
                    if isinstance(theme, str)
                ]
                themes = [theme for theme in themes if theme]
                if not themes:
                    continue
                evidence = entry.get("evidence") or []
                has_hard_aspect = any(
                    isinstance(e, Mapping)
                    and e.get("type") == "aspect"
                    and str(e.get("aspect") or "").lower() in {"square", "opposition"}
                    for e in evidence
                )
                if has_hard_aspect:
                    for domain in themes:
                        local_pressure[domain] = local_pressure.get(domain, 0.0) + 0.25

                insight_id = str(entry.get("insight_id") or "")
                if insight_id in {
                    "dyn.mars_saturn.drive_brake.v1",
                    "dyn.sun_saturn.authority.v1",
                    "dyn.moon_saturn.containment.v1",
                }:
                    for domain in themes:
                        local_pressure[domain] = local_pressure.get(domain, 0.0) + 0.30
                if insight_id in {"dyn.house8.depth.v1", "dyn.house12.hidden_layer.v1"}:
                    for domain in themes:
                        local_pressure[domain] = local_pressure.get(domain, 0.0) + 0.20
    else:
        selected = (dynamic_insights or {}).get("selected")
        if isinstance(selected, list):
            for entry in selected:
                if not isinstance(entry, Mapping):
                    continue
                themes = [
                    canon_domain(theme)
                    for theme in (entry.get("themes") or [])
                    if isinstance(theme, str)
                ]
                themes = [theme for theme in themes if theme]
                if not themes:
                    continue
                strength = _safe_float(entry.get("strength") or entry.get("score"))
                tension = _safe_float((entry.get("polarity") or {}).get("tension"))
                contribution = (0.6 * strength + 0.4 * tension) * 0.5
                for domain in themes:
                    local_pressure[domain] = local_pressure.get(domain, 0.0) + contribution

    for domain, score in list(local_pressure.items()):
        local_pressure[domain] = max(0.0, min(1.0, score))
    return local_pressure


def compute_capacity_score(
    *,
    support_index: float,
    resilience: float,
    uncertainty: float,
) -> float:
    return clamp01(0.55 * support_index + 0.25 * resilience + 0.20 * (1.0 - uncertainty))


def compute_integration_score(
    aspects: Sequence[Mapping[str, Any]],
    meta_info: Mapping[str, Any],
    meta_summary: Mapping[str, Any],
) -> tuple[float, Dict[str, float]]:
    planet_houses = meta_info.get("planet_houses") or {}
    sun_house = planet_houses.get("sun")
    moon_house = planet_houses.get("moon")
    node_house = planet_houses.get("node")
    chiron_house = planet_houses.get("chiron")

    major_aspects = {"conjunction", "opposition", "square", "trine", "sextile"}
    hard_aspects = {"square", "opposition"}

    sun_moon = _best_aspect(aspects, "sun", "moon", major_aspects)
    if sun_moon:
        bridge = aspect_strength(sun_moon)
    elif sun_house in {1, 10} and moon_house in {4, 8, 12}:
        bridge = 0.55
    else:
        bridge = 0.0

    hard_counts: Dict[str, int] = {}
    for entry in aspects:
        aspect_type = normalize_aspect_type(entry.get("type") or entry.get("aspect"))
        if aspect_type not in hard_aspects:
            continue
        a = _normalize_body(entry.get("planet1") or entry.get("a") or entry.get("planet"))
        b = _normalize_body(entry.get("planet2") or entry.get("b") or entry.get("target"))
        if not (a and b):
            continue
        hard_counts[a] = hard_counts.get(a, 0) + 1
        hard_counts[b] = hard_counts.get(b, 0) + 1
    recurrence = 0.0
    if any(count >= 2 for count in hard_counts.values()):
        recurrence += 0.25

    if _best_aspect(aspects, "mars", "saturn", hard_aspects) or _best_aspect(
        aspects, "sun", "saturn", hard_aspects
    ) or _best_aspect(aspects, "moon", "saturn", hard_aspects):
        recurrence += 0.35

    personal = {"sun", "moon", "mercury", "venus", "mars"}
    if _best_aspect(aspects, "node", tuple(personal), hard_aspects):
        recurrence += 0.20

    pattern_bonus = 0.0
    if recurrence > 0.35:
        patterns = meta_summary.get("aspect_patterns") or meta_info.get("aspect_patterns") or []
        pattern_bonus += _pattern_bonus(patterns)
    recurrence = clamp01(recurrence + pattern_bonus)

    directionality = 0.0
    if node_house in {9, 10, 12}:
        directionality += 0.25
    node_personal = _best_aspect(aspects, "node", tuple(personal), major_aspects)
    if node_personal:
        directionality += 0.35 * aspect_strength(node_personal)
    if chiron_house == 10:
        directionality += 0.15
    if _best_aspect(aspects, "jupiter", "neptune", major_aspects):
        directionality += 0.15
    directionality = clamp01(directionality)

    integration = clamp01(0.35 * bridge + 0.35 * recurrence + 0.30 * directionality)
    return integration, {
        "bridge": round(bridge, 3),
        "recurrence": round(recurrence, 3),
        "directionality": round(directionality, 3),
    }


def _best_aspect(
    aspects: Sequence[Mapping[str, Any]],
    a: str,
    b: str | tuple[str, ...],
    allowed: set[str],
) -> Mapping[str, Any] | None:
    targets = {b} if isinstance(b, str) else set(b)
    best: Mapping[str, Any] | None = None
    best_strength = -1.0
    for entry in aspects:
        aspect_type = normalize_aspect_type(entry.get("type") or entry.get("aspect"))
        if aspect_type not in allowed:
            continue
        p1 = _normalize_body(entry.get("planet1") or entry.get("a") or entry.get("planet"))
        p2 = _normalize_body(entry.get("planet2") or entry.get("b") or entry.get("target"))
        if not (p1 and p2):
            continue
        if not ({p1, p2} & {a}):
            continue
        if not ({p1, p2} & targets):
            continue
        strength = aspect_strength(entry)
        if strength > best_strength:
            best_strength = strength
            best = entry
    return best


def _pattern_bonus(patterns: Sequence[Mapping[str, Any]]) -> float:
    bonus_map = {
        "t_square": 0.30,
        "stellium": 0.20,
        "kite": 0.20,
        "grand_trine": 0.10,
    }
    bonus = 0.0
    for entry in patterns:
        if not isinstance(entry, Mapping):
            continue
        pattern_type = str(entry.get("pattern") or entry.get("pattern_type") or "").strip().lower()
        bonus += bonus_map.get(pattern_type, 0.0)
    return bonus


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_body(value: Any) -> str:
    normalized = normalize_node_alias(normalize_planet_key(value))
    return normalized or ""


def _ensure_narrative_presence(base_payload: Mapping[str, Any], response: Dict[str, Any]) -> None:
    if response.get("narrative_interpretation"):
        return
    phase2_snapshot = base_payload.get("_phase2_snapshot") or {}
    accepted_domains = {
        str(entry.get("domain")).strip().lower()
        for entry in phase2_snapshot.get("slots", {}).get("accepted", [])
        if isinstance(entry.get("domain"), str) and entry.get("domain").strip()
    }
    if not accepted_domains:
        return
    fragments = base_payload.get("__narrative_fragments") or {}
    fallback = _build_fragment_paragraphs(fragments, sorted(accepted_domains))
    if not fallback:
        return
    response["narrative_interpretation"] = fallback
    debug_entry = response.get("debug")
    if isinstance(debug_entry, dict):
        debug_entry["narrative_fallback_domains"] = sorted(fallback.keys())
    logger.warning(
        "Narrative builder cleared paragraphs for %s despite fragments being selected; injecting fallback text.",
        sorted(accepted_domains),
    )


def _record_final_response_snapshot(response: Dict[str, Any], debug_entry: Mapping[str, Any]) -> None:
    snapshots = debug_entry.get("snapshots")
    if not isinstance(snapshots, dict):
        return
    final_snapshot = copy.deepcopy(response)
    final_snapshot.pop("user", None)
    final_snapshot.pop("user_compact", None)
    debug_payload = final_snapshot.get("debug")
    if isinstance(debug_payload, dict):
        debug_payload = dict(debug_payload)
        debug_payload.pop("snapshots", None)
        final_snapshot["debug"] = debug_payload
    snapshots["final_response_payload"] = final_snapshot


def _summarize_rule_engine(
    interpretation: Mapping[str, Mapping[str, Sequence[Any]]],
    meta_info: Mapping[str, Any],
) -> Dict[str, Any]:
    domain_summary: Dict[str, Dict[str, int]] = {}
    total_sentences = 0
    for domain, tile in interpretation.items():
        if not isinstance(tile, Mapping):
            continue
        counts: Dict[str, int] = {}
        for type_name in TYPE_NAMES:
            bucket = tile.get(type_name) or []
            counts[type_name] = len(bucket)
            total_sentences += len(bucket)
        domain_summary[domain] = {"counts": counts, "total": sum(counts.values())}
    meta_snapshot = {
        "planet_count": len(meta_info.get("planet_signs", {}) or {}),
        "stellium_planets": meta_info.get("stellium_planets") or [],
        "aspect_pairs": len(meta_info.get("aspect_pairs") or []),
    }
    return {
        "domain_summary": domain_summary,
        "total_sentences": total_sentences,
        "meta": meta_snapshot,
    }


def _snapshot_composite_guidance(guidance: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "active_domains": list(guidance.get("active_domains") or []),
        "domain_priority": guidance.get("domain_priority") or {},
        "tone_modifiers": guidance.get("tone_modifiers") or {},
    }


def _collect_debug_warnings(
    phase2_snapshot: Mapping[str, Any],
    guidance: Mapping[str, Any],
    builder: JoviaSemanticNarrativeBuilder,
    debug_mode: bool,
) -> List[str]:
    if not debug_mode:
        return []
    warnings: List[str] = []
    accepted_slots = phase2_snapshot.get("slots", {}).get("accepted", [])
    if not accepted_slots:
        warnings.append("Phase2 slot map normalized to zero entries.")
    accepted_domains = {
        canon_domain(entry.get("domain"))
        for entry in accepted_slots
        if isinstance(entry.get("domain"), str)
    }
    accepted_domains = {domain for domain in accepted_domains if domain}
    active_domains = {
        canon_domain(domain)
        for domain in guidance.get("active_domains") or []
        if isinstance(domain, str)
    }
    active_domains = {domain for domain in active_domains if domain}
    if active_domains and not accepted_domains.intersection(active_domains):
        warnings.append(
            "Composite guidance active domains do not align with any selected phase2 slot domains."
        )
    drop_clause_count = phase2_snapshot.get("quality_gates_applied", {}).get("drop_clause", 0)
    if drop_clause_count > 2:
        warnings.append(f"Quality gate drop_clause triggered {drop_clause_count} times.")
    for domain, plan in getattr(builder, "narrative_plan", {}).items():
        canonical_domain = canon_domain(domain)
        compiler_input = str(plan.get("compiler_input") or "").strip()
        final_text = str(plan.get("final_text") or "").strip()
        if compiler_input and not final_text:
            domain_label = canonical_domain or domain
            warnings.append(
                f"Domain '{domain_label}' had compiler input ({len(compiler_input)} chars) but produced empty paragraph text."
            )
    return warnings


def _build_fragment_paragraphs(
    fragments: Mapping[str, Dict[str, Any]],
    domains: Sequence[str],
) -> Dict[str, str]:
    paragraphs: Dict[str, str] = {}
    seen: set[str] = set()
    for domain in domains:
        canonical_domain = canon_domain(domain)
        if not canonical_domain or canonical_domain in seen:
            continue
        seen.add(canonical_domain)
        entry = fragments.get(canonical_domain)
        if not isinstance(entry, Mapping):
            continue
        paragraph = _paragraph_from_fragment_slots(entry.get("slots") or {})
        if paragraph:
            paragraphs[canonical_domain] = paragraph
    return paragraphs


def _paragraph_from_fragment_slots(slots: Mapping[str, Any]) -> str | None:
    sentences: List[str] = []
    for slot in SLOT_NAMES:
        fragment = slots.get(slot)
        if not isinstance(fragment, Mapping):
            continue
        text = fragment.get("text") or fragment.get("_semantic_text")
        normalized = _normalize_fragment_sentence(text)
        if not normalized:
            continue
        if normalized[-1] not in ".!?":
            normalized = f"{normalized}."
        sentences.append(normalized)
    if sentences:
        return " ".join(sentences)
    return None


def _normalize_fragment_sentence(text: Any) -> str:
    if text is None:
        return ""
    cleaned = " ".join(str(text).strip().split())
    return cleaned


def _build_phase2_fragment_payload(
    phase2_fragments: Mapping[str, Mapping[str, Any]]
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    payload: Dict[str, Dict[str, Any]] = {}
    for domain, entry in phase2_fragments.items():
        canonical_domain = canon_domain(domain)
        if not canonical_domain or canonical_domain in payload:
            continue
        if not isinstance(entry, Mapping):
            continue
        slots = entry.get("slots")
        anchor = entry.get("anchor")
        if not isinstance(slots, Mapping):
            continue
        valid_slots: Dict[str, Dict[str, Any]] = {}
        for slot_name in SLOT_NAMES:
            value = slots.get(slot_name)
            if isinstance(value, Mapping):
                valid_slots[slot_name] = dict(value)
        if not valid_slots:
            continue
        payload[canonical_domain] = {
            "slots": valid_slots,
            "anchor": anchor if isinstance(anchor, Mapping) else valid_slots.get("cause"),
        }
    normalized_payload, normalization_trace = _apply_semantic_normalization(payload)
    normalized_payload = _normalize_phase2_texts(normalized_payload)
    return normalized_payload, normalization_trace


def _apply_semantic_normalization(payload: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    normalized_payload: Dict[str, Dict[str, Any]] = {}
    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    summary = {
        "total_slots": 0,
        "accepted_slots": 0,
        "rejected_slots": 0,
        "rejection_reasons": {
            "no_text": 0,
            "empty_normalized": 0,
            "contains_verb_phrase": 0,
        },
        "domains_with_accepted": set(),
    }
    for domain, entry in payload.items():
        canonical_domain = canon_domain(domain)
        if not canonical_domain or not isinstance(entry, Mapping):
            continue
        slots = entry.get("slots") or {}
        normalized_slots: Dict[str, Dict[str, Any]] = {}
        for slot_name, fragment in slots.items():
            if not isinstance(fragment, Mapping):
                continue
            text = fragment.get("text")
            summary["total_slots"] += 1
            original_text = str(text).strip() if text else ""
            if not original_text:
                summary["rejection_reasons"]["no_text"] += 1
                summary["rejected_slots"] += 1
                rejected.append(
                    {
                        "domain": canonical_domain,
                        "slot": slot_name,
                        "reason": "no_text",
                        "original_text": original_text,
                        "fragment_id": fragment.get("fragment_ref") or fragment.get("id"),
                    }
                )
                continue
            semantic_text = normalize_slot_text(text, slot_name)
            if not semantic_text:
                summary["rejection_reasons"]["empty_normalized"] += 1
                summary["rejected_slots"] += 1
                rejected.append(
                    {
                        "domain": canonical_domain,
                        "slot": slot_name,
                        "reason": "empty_after_normalize",
                        "original_text": original_text,
                        "fragment_id": fragment.get("fragment_ref") or fragment.get("id"),
                    }
                )
                continue
            if contains_verb_phrase(semantic_text):
                summary["rejection_reasons"]["contains_verb_phrase"] += 1
                summary["rejected_slots"] += 1
                rejected.append(
                    {
                        "domain": canonical_domain,
                        "slot": slot_name,
                        "reason": "contains_verb_phrase",
                        "original_text": original_text,
                        "fragment_id": fragment.get("fragment_ref") or fragment.get("id"),
                    }
                )
                continue
            fragment_id = _ensure_fragment_id(
                fragment,
                domain=canonical_domain,
                slot=slot_name,
                normalized_text=semantic_text,
            )
            normalized_fragment = dict(fragment)
            normalized_fragment["_semantic_text"] = semantic_text
            normalized_fragment["text"] = semantic_text
            if fragment_id:
                normalized_fragment["fragment_id"] = fragment_id
            normalized_slots[slot_name] = normalized_fragment
            summary["accepted_slots"] += 1
            summary["domains_with_accepted"].add(canonical_domain)
            accepted.append(
                {
                    "domain": canonical_domain,
                    "slot": slot_name,
                    "normalized_text": semantic_text,
                    "original_text": original_text,
                    "fragment_id": fragment_id,
                    "source_composite_ids": fragment.get("source_composite_ids") or [],
                }
            )
        anchor = entry.get("anchor")
        normalized_payload[canonical_domain] = {
            "slots": normalized_slots,
            "anchor": anchor if isinstance(anchor, Mapping) else normalized_slots.get("cause"),
        }
    domains_with_accepted = sorted(summary["domains_with_accepted"])
    summary["domains_with_accepted"] = domains_with_accepted
    trace = {
        "slots": {
            "accepted": accepted,
            "rejected": rejected,
        },
        "summary": summary,
        "quality_gates_applied": {"drop_clause": summary["rejected_slots"]},
    }
    return normalized_payload, trace


def _normalize_phase2_texts(payload: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    normalized: Dict[str, Dict[str, Any]] = {}
    for domain, entry in payload.items():
        canonical_domain = canon_domain(domain)
        if not canonical_domain or not isinstance(entry, Mapping):
            continue
        if canonical_domain == "identity":
            normalized[canonical_domain] = entry
            continue
        slots = entry.get("slots") or {}
        normalized_slots: Dict[str, Dict[str, Any]] = {}
        for slot_name, fragment in slots.items():
            if not isinstance(fragment, Mapping):
                continue
            text = fragment.get("text")
            normalized_text = normalize_slot_text(text, slot_name)
            normalized_fragment = dict(fragment)
            if normalized_text:
                normalized_fragment["text"] = normalized_text
            else:
                fallback = fragment.get("_semantic_text")
                if fallback:
                    normalized_fragment["text"] = fallback
            normalized_slots[slot_name] = normalized_fragment
        anchor = entry.get("anchor")
        normalized[canonical_domain] = {
            "slots": normalized_slots,
            "anchor": anchor if isinstance(anchor, Mapping) else normalized_slots.get("cause"),
        }
    return normalized


def _ensure_fragment_id(
    fragment: Mapping[str, Any],
    *,
    domain: str,
    slot: str,
    normalized_text: str,
) -> str | None:
    fragment_id = fragment.get("fragment_id") or fragment.get("fragment_ref") or fragment.get("id")
    if fragment_id:
        return str(fragment_id)
    rule_id = fragment.get("rule_id")
    if not rule_id:
        rule_ids = fragment.get("rule_ids") or fragment.get("source_rule_ids") or []
        if isinstance(rule_ids, list) and rule_ids:
            rule_id = rule_ids[0]
    trigger = fragment.get("trigger") if isinstance(fragment.get("trigger"), Mapping) else None
    if not trigger:
        trigger = {
            "planet": fragment.get("planet"),
            "sign": fragment.get("sign"),
            "house": fragment.get("house"),
            "aspect": fragment.get("aspect"),
        }
        trigger = {k: v for k, v in trigger.items() if v is not None}
    payload = {
        "domain": domain,
        "slot": slot,
        "normalized_text": normalized_text,
        "rule_id": rule_id,
        "trigger": trigger,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _primary_domain_regulations(
    composites: Sequence[Mapping[str, Any]],
    patterns: Mapping[str, Mapping[str, Any]],
    regulations: Mapping[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    primary: Dict[str, Dict[str, Any]] = {}
    for composite in sorted(
        composites,
        key=lambda comp: _extract_composite_priority(patterns, comp),
        reverse=True,
    ):
        domain = canon_domain(composite.get("domain"))
        comp_id = composite.get("composite_id")
        if not domain or not comp_id:
            continue
        if domain in primary:
            continue
        regulation = regulations.get(comp_id)
        if regulation:
            primary[domain] = regulation
    return primary


def _extract_composite_priority(
    patterns: Mapping[str, Mapping[str, Any]],
    composite: Mapping[str, Any],
) -> float:
    comp_id = composite.get("composite_id")
    meta = patterns.get(comp_id or "", {})
    try:
        return float(meta.get("priority_score") or 0.0)
    except (TypeError, ValueError):
        return 0.0
