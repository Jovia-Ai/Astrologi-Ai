"""RevenueCat webhook endpoints."""
from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

from app.core.config import settings
from app.services.revenuecat import revenuecat_webhook_service

router = APIRouter(tags=["billing"])
logger = logging.getLogger(__name__)


def _verify_webhook_authorization(authorization: str | None) -> None:
    expected = (settings.revenuecat_webhook_authorization or "").strip()
    if not expected:
        return
    if (authorization or "").strip() != expected:
        raise HTTPException(status_code=401, detail="Invalid RevenueCat webhook authorization.")


@router.post("/v1/billing/revenuecat/webhook")
async def handle_revenuecat_webhook(
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    _verify_webhook_authorization(authorization)

    raw_body = (await request.body()).decode("utf-8")
    try:
        payload = json.loads(raw_body or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.") from exc

    try:
        result = revenuecat_webhook_service.process(payload, raw_body=raw_body)
        return {"ok": True, "duplicate": result.duplicate, "action": result.action}
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to process RevenueCat webhook")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
