"""API route for natal chart interpretation using the rule engine."""
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, List, Mapping, Sequence

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.narrative.formatter import (
    build_formatted_aspects,
    build_formatted_house_positions,
    build_formatted_planet_positions,
)
from app.builders.composite_guidance import build_guidance
from app.builders.composite_interpreter import CompositeInterpretationBuilder
from app.builders.composite_regulator import build_composite_regulation
from app.builders.narrative_builder import JoviaSemanticNarrativeBuilder, SLOT_NAMES
from app.builders.phase2_selector import select_phase2_fragments
from app.builders.semantic_normalizer import contains_verb_phrase, normalize_slot_text
from app.engine.aspect_mechanics import AspectMechanicsEngine
from app.engine.composite_engine import CompositeEngine
from app.engine.pattern_engine import PatternEmphasisEngine
from app.engine.router import build_combined_insights
from app.engine.rule_engine import RuleEngine
from app.engine.upper_meaning_engine import UpperMeaningEngine
from app.engine.inquiry_engine import InquiryEngine
from app.engine.dispositor_flow import DispositorFlowEngine
from app.engine.activation_sensitivity import ActivationSensitivityEngine
from app.engine.axis_activation import AxisActivationEngine
from app.engine.latent_potential import LatentPotentialEngine
from app.helpers.pressure_support import calculate_pressure_support
from app.resolvers.expression_resolver import ExpressionResolver
from app.services.chart_service import (
    compute_natal_chart,
    serialize_aspects,
    serialize_planets,
)
from app.helpers.narrative_context import derive_core_aspects, derive_placements

logger = logging.getLogger(__name__)

router = APIRouter(tags=["natal"])
rule_engine = RuleEngine()


class NatalInterpretationRequest(BaseModel):
    """Request body containing the birth data required for natal calculations."""

    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format.")
    birth_time: str = Field(..., description="Birth time in HH:MM format.")
    birth_place: str = Field(..., description="City + country or recognizable location label.")

    class Config:
        anystr_strip_whitespace = True


@router.post("/interpret")
def interpret_natal_chart(request: NatalInterpretationRequest) -> Dict[str, Any]:
    """Free deterministic interpretation endpoint (JoviaWeighted narratives)."""

    base_payload = _prepare_payload(request, premium_mode=False)
    return _finalize_response(base_payload, premium_mode=False)


@router.post("/interpret/premium")
def interpret_natal_chart_premium(request: NatalInterpretationRequest) -> Dict[str, Any]:
    """Premium endpoint (PRO Jovia narratives)."""

    base_payload = _prepare_payload(request, premium_mode=True)
    return _finalize_response(base_payload, premium_mode=True)


def _build_metadata(request: NatalInterpretationRequest, chart_data: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "birth_date": request.birth_date,
        "birth_time": request.birth_time,
        "birth_place": request.birth_place,
        "location": chart_data.get("location"),
        "birth_datetime": chart_data.get("birth_datetime"),
        "timezone": chart_data.get("timezone"),
    }


def _prepare_payload(request: NatalInterpretationRequest, *, premium_mode: bool) -> Dict[str, Any]:
    try:
        chart_data = compute_natal_chart(request.birth_date, request.birth_time, request.birth_place)
    except Exception as exc:  # pragma: no cover - network/env specific
        logger.exception("Failed to calculate natal chart from inputs")
        raise HTTPException(status_code=500, detail=f"Chart calculation failed: {exc}") from exc

    planets = serialize_planets(chart_data.get("planets", {}))
    aspects = serialize_aspects(chart_data.get("aspects", []))
    interpretation, meta_info = rule_engine.interpret(planets=planets, aspects=aspects, return_meta=True)

    placements = derive_placements(planets)
    core_aspects = derive_core_aspects(aspects)
    composite_engine = CompositeEngine()
    composites = composite_engine.build(placements, core_aspects)
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
    )
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
    expression_profile = ExpressionResolver.resolve(
        composite_output=composites,
        pressure_index=pressure_support["pressure_index"],
        support_index=pressure_support["support_index"],
        axis_balance=pressure_support["axis_balance"],
        dominant_domain=pressure_support["dominant_domain"],
        dominant_axis=pressure_support["dominant_axis"],
        themes=pressure_support["themes"],
    )
    narrative_fragments = _build_phase2_fragment_payload(phase2_fragments)
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
            guidance=composite_guidance,
            regulations=domain_regulators,
            expression_profile=expression_profile,
        )
    )
    narrative = builder.build()
    if builder.fallback_used:
        narrative_meta["fallback_used"] = True
    narrative_meta["expression_profile"] = expression_profile
    used_composites = list(builder.used_composite_ids)
    combined_insights = build_combined_insights(meta_info, interpretation)

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
        "pressure_support": pressure_support,
        "expression_profile": expression_profile,
    }
    return {
        "metadata": _build_metadata(request, chart_data),
        "planets": planets,
        "aspects": aspects,
        "formatted_positions": build_formatted_planet_positions(chart_data),
        "formatted_houses": build_formatted_house_positions(chart_data),
        "formatted_aspects": build_formatted_aspects(chart_data),
        "interpretation": interpretation,
        "meta_info": meta_info,
        "combined_insights": combined_insights,
        "composites": composites,
        "patterns": patterns,
        "upper_meaning": upper_meanings,
        "aspect_mechanics": aspect_mechanics,
        "composite_interpretation": composite_interpretation,
        "dispositor_flow": dispositor_flow,
        "axis_activation": axis_activation,
        "activation_sensitivity": activation_sensitivity,
        "latent_potential": latent_potential,
        "composite_guidance": composite_guidance,
        "debug": debug_info,
        "narrative_interpretation": narrative,
        "narrative_meta": narrative_meta,
        "expression_profile": expression_profile,
    }


def _finalize_response(base_payload: Mapping[str, Any], *, premium_mode: bool) -> Dict[str, Any]:
    response = {
        "metadata": base_payload["metadata"],
        "planets": base_payload["planets"],
        "aspects": base_payload["aspects"],
        "formatted_positions": base_payload["formatted_positions"],
        "formatted_houses": base_payload["formatted_houses"],
        "formatted_aspects": base_payload["formatted_aspects"],
        "combined_insights": base_payload["combined_insights"],
        "composites": base_payload["composites"],
        "patterns": base_payload["patterns"],
        "upper_meaning": base_payload["upper_meaning"],
        "aspect_mechanics": base_payload["aspect_mechanics"],
        "composite_interpretation": {},
        "dispositor_flow": base_payload["dispositor_flow"],
        "axis_activation": base_payload["axis_activation"],
        "activation_sensitivity": base_payload["activation_sensitivity"],
        "latent_potential": base_payload["latent_potential"],
        "composite_guidance": base_payload["composite_guidance"],
        "debug": base_payload["debug"],
        "narrative_interpretation": base_payload["narrative_interpretation"],
        "premium_mode": premium_mode,
        "expression_profile": base_payload.get("expression_profile"),
    }
    return response


def _build_phase2_fragment_payload(
    phase2_fragments: Mapping[str, Mapping[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    payload: Dict[str, Dict[str, Any]] = {}
    for domain, entry in phase2_fragments.items():
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
                valid_slots[slot_name] = value
        if not valid_slots:
            continue
        payload[domain] = {
            "slots": valid_slots,
            "anchor": anchor if isinstance(anchor, Mapping) else valid_slots.get("cause"),
        }
    payload = _apply_semantic_normalization(payload)
    return _normalize_phase2_texts(payload)


def _apply_semantic_normalization(payload: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    normalized_payload: Dict[str, Dict[str, Any]] = {}
    for domain, entry in payload.items():
        if not isinstance(entry, Mapping):
            continue
        slots = entry.get("slots") or {}
        normalized_slots: Dict[str, Dict[str, Any]] = {}
        for slot_name, fragment in slots.items():
            if not isinstance(fragment, Mapping):
                continue
            text = fragment.get("text")
            semantic_text = normalize_slot_text(text)
            if not semantic_text:
                continue
            if contains_verb_phrase(semantic_text):
                continue
            normalized_fragment = dict(fragment)
            normalized_fragment["_semantic_text"] = semantic_text
            normalized_fragment["text"] = semantic_text
            normalized_slots[slot_name] = normalized_fragment
        anchor = entry.get("anchor")
        normalized_payload[domain] = {
            "slots": normalized_slots,
            "anchor": anchor if isinstance(anchor, Mapping) else normalized_slots.get("cause"),
        }
    return normalized_payload


def _normalize_phase2_texts(payload: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    normalized: Dict[str, Dict[str, Any]] = {}
    for domain, entry in payload.items():
        if not isinstance(entry, Mapping):
            continue
        if domain == "identity":
            normalized[domain] = entry
            continue
        slots = entry.get("slots") or {}
        normalized_slots: Dict[str, Dict[str, Any]] = {}
        for slot_name, fragment in slots.items():
            if not isinstance(fragment, Mapping):
                continue
            text = fragment.get("text")
            normalized_text = normalize_slot_text(text)
            normalized_fragment = dict(fragment)
            if normalized_text:
                normalized_fragment["text"] = normalized_text
            else:
                fallback = fragment.get("_semantic_text")
                if fallback:
                    normalized_fragment["text"] = fallback
            normalized_slots[slot_name] = normalized_fragment
        anchor = entry.get("anchor")
        normalized[domain] = {
            "slots": normalized_slots,
            "anchor": anchor if isinstance(anchor, Mapping) else normalized_slots.get("cause"),
        }
    return normalized


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
        domain = str(composite.get("domain") or "").lower()
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
