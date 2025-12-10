"""Chart-related HTTP routes."""
from __future__ import annotations

import logging
from typing import Any, Dict, Mapping

from fastapi import APIRouter, Body, HTTPException

from app.ai.narrative.formatter import (
    build_formatted_aspects,
    build_formatted_house_positions,
    build_formatted_planet_positions,
)
from app.ai.narrative.groq_client import (
    chart_to_summary,
    generate_ai_interpretation,
    generate_synastry_interpretation,
)
from app.astro.chart_engine.builder import build_natal_chart
from app.astro.synastry.cross_aspects import calculate_synastry_aspects
from app.core.config import settings
from app.core.errors import AIError, ApiError
from app.models.user import BirthDataSchema
from app.services.profiles import save_birth_data

router = APIRouter(prefix="/api", tags=["charts"])
logger = logging.getLogger(__name__)


def _calculate_chart(payload: Mapping[str, Any]) -> Dict[str, Any]:
    chart = build_natal_chart(payload)
    summary = chart_to_summary(chart)
    chart["interpretation"] = generate_ai_interpretation(summary)
    chart["formatted_positions"] = build_formatted_planet_positions(chart)
    chart["formatted_houses"] = build_formatted_house_positions(chart)
    chart["formatted_aspects"] = build_formatted_aspects(chart)
    return chart


@router.post("/calculate-natal-chart")
@router.post("/natal-chart")
def calculate_natal_chart(payload: Dict[str, Any] = Body(...)):
    try:
        return _calculate_chart(payload)
    except ApiError as exc:
        logger.error("External API error: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to calculate natal chart")
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/calculate-synastry")
@router.post("/calculate_synastry_chart")
def calculate_synastry(payload: Dict[str, Any] = Body(...)):
    try:
        person1 = payload.get("person1")
        person2 = payload.get("person2")
        if not isinstance(person1, Mapping) or not isinstance(person2, Mapping):
            raise ValueError("person1 and person2 must be objects containing birth date and city information.")
        chart1 = build_natal_chart(person1)
        chart2 = build_natal_chart(person2)
        aspects = calculate_synastry_aspects(chart1["planets"], chart2["planets"])
        response: Dict[str, Any] = {
            "person1": chart1,
            "person2": chart2,
            "aspects": aspects,
        }
        if settings.groq_api_key:
            try:
                response["interpretation"] = generate_synastry_interpretation(chart1, chart2, aspects)
            except AIError as exc:
                logger.warning("Synastry interpretation failed: %s", exc)
                response["interpretation_error"] = str(exc)
        return response
    except ApiError as exc:
        logger.error("External API error: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to calculate synastry")
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/save-birth-data")
def save_birth_data_route(payload: BirthDataSchema):
    result = save_birth_data(
        user_id=payload.user_id,
        birth_date=payload.birth_date,
        birth_time=payload.birth_time,
        timezone=payload.timezone,
        place=payload.place,
        lat=payload.latitude,
        lon=payload.longitude,
    )
    return {"status": "ok", "saved": result}
