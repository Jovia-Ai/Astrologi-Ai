"""Synastry endpoints for saving partner pairs."""
from __future__ import annotations

from fastapi import APIRouter

from app.models.synastry import SynastryPairSchema
from app.services.synastry import create_synastry_pair, get_synastry_pairs
from app.services.synastry_analysis import analyze_synastry

router = APIRouter(prefix="/api", tags=["synastry"])


@router.post("/synastry")
def add_synastry_pair(payload: SynastryPairSchema):
    result = create_synastry_pair(payload.user_id, payload.partner_id)
    return {"saved": result}


@router.get("/synastry/{user_id}")
def list_synastry_for_user(user_id: str):
    return get_synastry_pairs(user_id)


@router.post("/v1/relationship/synastry/analyze")
def synastry_analyze(payload: dict):
    return analyze_synastry(payload)


@router.post("/synastry/analyze")
def synastry_analyze_alias(payload: dict):
    return analyze_synastry(payload)
