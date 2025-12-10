"""API route for natal chart interpretation using the rule engine."""
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, Mapping

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.narrative.formatter import (
    build_formatted_aspects,
    build_formatted_house_positions,
    build_formatted_planet_positions,
)
from app.engine.jovia_narrative_builder import JoviaSemanticNarrativeBuilder
from app.engine.jovia_weighted_builder import JoviaWeightedNarrativeBuilder
from app.engine.jovia_flow_builder import JoviaNarrativeFlowEngine
from app.engine.router import build_combined_insights
from app.engine.rule_engine import RuleEngine
from app.services.chart_service import (
    compute_natal_chart,
    serialize_aspects,
    serialize_planets,
)

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
    if premium_mode:
        builder = JoviaSemanticNarrativeBuilder(SimpleNamespace(interpretation=interpretation))
        raw_narrative = builder.build()
    else:
        builder = JoviaWeightedNarrativeBuilder()
        raw_narrative = builder.build(interpretation)

    flow_engine = JoviaNarrativeFlowEngine()
    flowed_narrative: Dict[str, str] = {}
    for category, text in raw_narrative.items():
        flowed_narrative[category] = flow_engine.build_flow(
            category,
            rule_engine.get_sentence(category, "cause") or "",
            rule_engine.get_sentence(category, "mechanism") or "",
            rule_engine.get_sentence(category, "shadow") or "",
            rule_engine.get_sentence(category, "potential") or "",
        )

    narrative = flowed_narrative
    combined_insights = build_combined_insights(meta_info, interpretation)

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
        "narrative_interpretation": narrative,
    }


def _finalize_response(base_payload: Mapping[str, Any], *, premium_mode: bool) -> Dict[str, Any]:
    response = {
        "metadata": base_payload["metadata"],
        "planets": base_payload["planets"],
        "aspects": base_payload["aspects"],
        "formatted_positions": base_payload["formatted_positions"],
        "formatted_houses": base_payload["formatted_houses"],
        "formatted_aspects": base_payload["formatted_aspects"],
        "interpretation": base_payload["interpretation"],
        "combined_insights": base_payload["combined_insights"],
        "narrative_interpretation": base_payload["narrative_interpretation"],
        "premium_mode": premium_mode,
    }
    return response
