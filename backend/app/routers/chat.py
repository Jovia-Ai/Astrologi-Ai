"""Quota-aware AI chat routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.auth.supabase_auth import (
    AuthenticatedSupabaseUser,
    get_required_supabase_user,
)
from app.services.ai_chat import (
    cost_estimator,
    openai_responses_service,
    quota_service,
    OpenAIRequestError,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request body."""

    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None)


class ChatSuccessResponse(BaseModel):
    """Successful chat response."""

    ok: bool = True
    text: str
    remaining_free: int
    credits_remaining: int
    is_pro: bool
    paywall: bool = False
    conversation_id: str | None = None


class ChatPaywallResponse(BaseModel):
    """Quota exhausted response."""

    ok: bool = False
    paywall: bool = True
    code: str = "QUOTA_EXCEEDED"
    message: str = "Free quota is exhausted"


@router.post("/v1/ai/chat", response_model=ChatSuccessResponse | ChatPaywallResponse)
def chat_message(
    payload: ChatRequest,
    current_user: AuthenticatedSupabaseUser = Depends(get_required_supabase_user),
):
    try:
        quota_service.ensure_user_rows(
            user_id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
        )
        quota_before = quota_service.resolve_quota_state(current_user.id)
        if not quota_before.can_chat:
            return ChatPaywallResponse()

        ai_result = openai_responses_service.create_chat_response(
            message=payload.message,
            conversation_id=payload.conversation_id,
        )

        quota_after = quota_before.projected_after_success()
        try:
            quota_after = quota_service.consume_after_success(current_user.id)
        except Exception:  # pragma: no cover - safeguard after upstream success
            logger.exception("Failed to persist AI quota consumption for user %s", current_user.id)

        estimated_cost = cost_estimator.estimate_cost_usd(
            prompt_tokens=ai_result.prompt_tokens,
            completion_tokens=ai_result.completion_tokens,
        )

        try:
            quota_service.log_usage_event(
                user_id=current_user.id,
                model=ai_result.model,
                prompt_tokens=ai_result.prompt_tokens,
                completion_tokens=ai_result.completion_tokens,
                total_tokens=ai_result.total_tokens,
                estimated_cost_usd=estimated_cost,
            )
        except Exception:  # pragma: no cover - logging should not break chat delivery
            logger.exception("Failed to log AI usage event for user %s", current_user.id)

        if not quota_after.consumed and not quota_after.is_pro:
            logger.warning("AI quota was not consumed after a successful response for user %s", current_user.id)

        return ChatSuccessResponse(
            text=ai_result.text,
            remaining_free=quota_after.remaining_free,
            credits_remaining=quota_after.credits_remaining,
            is_pro=quota_after.is_pro,
            conversation_id=ai_result.conversation_id,
        )
    except OpenAIRequestError as exc:
        logger.error("OpenAI chat request failed: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to process chat message")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
