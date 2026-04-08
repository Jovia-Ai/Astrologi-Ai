"""Additive home endpoints backed by a performance orchestrator."""
from __future__ import annotations

from datetime import date as date_type

from fastapi import APIRouter, Query

from app.services.performance.home_orchestrator import (
    HomeRequestContext,
    home_orchestrator,
)

router = APIRouter(tags=["home"])


@router.get("/home/fast")
def home_fast(
    birth_date: str = Query(...),
    birth_time: str = Query(...),
    birth_place: str = Query(...),
    birth_latitude: float | None = Query(None),
    birth_longitude: float | None = Query(None),
    birth_timezone: str | None = Query(None),
    date: date_type | None = Query(None),
    tz: str = Query("Europe/Istanbul"),
    locale: str = Query("tr"),
    lens: str = Query("general"),
    user_id: str | None = Query(None),
    transit_place: str | None = Query(None),
    transit_latitude: float | None = Query(None),
    transit_longitude: float | None = Query(None),
    transit_timezone: str | None = Query(None),
) -> dict:
    context = HomeRequestContext(
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
        birth_latitude=birth_latitude,
        birth_longitude=birth_longitude,
        birth_timezone=birth_timezone,
        target_date=date or date_type.today(),
        tz=tz,
        locale=locale,
        lens=lens,
        user_id=user_id,
        transit_place=transit_place,
        transit_latitude=transit_latitude,
        transit_longitude=transit_longitude,
        transit_timezone=transit_timezone,
    )
    return home_orchestrator.get_fast(context)


@router.get("/home/deep")
def home_deep(
    birth_date: str = Query(...),
    birth_time: str = Query(...),
    birth_place: str = Query(...),
    birth_latitude: float | None = Query(None),
    birth_longitude: float | None = Query(None),
    birth_timezone: str | None = Query(None),
    date: date_type | None = Query(None),
    tz: str = Query("Europe/Istanbul"),
    locale: str = Query("tr"),
    lens: str = Query("general"),
    user_id: str | None = Query(None),
    transit_place: str | None = Query(None),
    transit_latitude: float | None = Query(None),
    transit_longitude: float | None = Query(None),
    transit_timezone: str | None = Query(None),
) -> dict:
    context = HomeRequestContext(
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
        birth_latitude=birth_latitude,
        birth_longitude=birth_longitude,
        birth_timezone=birth_timezone,
        target_date=date or date_type.today(),
        tz=tz,
        locale=locale,
        lens=lens,
        user_id=user_id,
        transit_place=transit_place,
        transit_latitude=transit_latitude,
        transit_longitude=transit_longitude,
        transit_timezone=transit_timezone,
    )
    return home_orchestrator.get_deep(context)
