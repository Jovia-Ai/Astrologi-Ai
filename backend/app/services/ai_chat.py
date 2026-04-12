"""Quota-aware AI chat services backed by Supabase and OpenAI."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

import requests

from app.core.config import settings
from app.services.supabase import supabase_admin

logger = logging.getLogger(__name__)

_CHAT_SOURCE = "mobile_chat"
_FREE_QUESTION_LIMIT = 3
_CHAT_SYSTEM_PROMPT = (
    "Sen Astrologi-AI icindeki Aila'sin. Turkce yanit ver. "
    "Kisa, net, empatik ve yonlendirici ol. Uydurma bilgi verme."
)


class OpenAIRequestError(Exception):
    """Raised when the OpenAI request fails or returns invalid output."""


@dataclass(frozen=True)
class QuotaState:
    """Resolved chat quota for a user."""

    remaining_free: int
    credits_remaining: int
    is_pro: bool
    consumed: bool = False
    consumption_type: str = "none"

    @property
    def can_chat(self) -> bool:
        return self.is_pro or self.remaining_free > 0 or self.credits_remaining > 0

    def projected_after_success(self) -> QuotaState:
        if self.is_pro:
            return QuotaState(
                remaining_free=self.remaining_free,
                credits_remaining=self.credits_remaining,
                is_pro=True,
                consumed=True,
                consumption_type="pro",
            )
        if self.remaining_free > 0:
            return QuotaState(
                remaining_free=max(0, self.remaining_free - 1),
                credits_remaining=self.credits_remaining,
                is_pro=False,
                consumed=True,
                consumption_type="free",
            )
        if self.credits_remaining > 0:
            return QuotaState(
                remaining_free=0,
                credits_remaining=max(0, self.credits_remaining - 1),
                is_pro=False,
                consumed=True,
                consumption_type="credit",
            )
        return self


@dataclass(frozen=True)
class OpenAIChatResult:
    """Successful OpenAI response payload."""

    text: str
    model: str
    conversation_id: str | None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None
        try:
            return datetime.fromisoformat(normalized.replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError:
            return None
    return None


def _as_int(value: Any, *, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class CostEstimator:
    """Estimate OpenAI usage cost from token counts."""

    def estimate_cost_usd(self, *, prompt_tokens: int, completion_tokens: int) -> float:
        prompt_cost = (prompt_tokens * settings.openai_input_cost_per_million_usd) / 1_000_000
        completion_cost = (completion_tokens * settings.openai_output_cost_per_million_usd) / 1_000_000
        return round(prompt_cost + completion_cost, 6)


class QuotaService:
    """Resolve and consume per-user AI quota."""

    def ensure_user_rows(self, *, user_id: str, email: str | None, full_name: str | None) -> None:
        profile_payload = {
            "id": user_id,
            "email": email,
            "full_name": full_name or (email or "User").split("@", 1)[0],
        }
        (
            supabase_admin.table("profiles")
            .upsert(profile_payload, on_conflict="id")
            .execute()
        )
        (
            supabase_admin.table("ai_entitlements")
            .upsert({"user_id": user_id}, on_conflict="user_id")
            .execute()
        )

    def resolve_quota_state(self, user_id: str) -> QuotaState:
        profile_response = (
            supabase_admin.table("profiles")
            .select("free_questions_used")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        profile_row = (profile_response.data or [{}])[0]
        free_questions_used = max(0, _as_int(profile_row.get("free_questions_used")))

        entitlement_response = (
            supabase_admin.table("ai_entitlements")
            .select("credits_remaining, is_pro, pro_until")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        entitlement_row = (entitlement_response.data or [{}])[0]
        credits_remaining = max(0, _as_int(entitlement_row.get("credits_remaining")))
        pro_until = _parse_datetime(entitlement_row.get("pro_until"))
        is_pro = bool(entitlement_row.get("is_pro")) and (
            pro_until is None or pro_until > datetime.now(timezone.utc)
        )

        remaining_free = max(0, _FREE_QUESTION_LIMIT - free_questions_used)
        return QuotaState(
            remaining_free=remaining_free,
            credits_remaining=credits_remaining,
            is_pro=is_pro,
        )

    def consume_after_success(self, user_id: str) -> QuotaState:
        response = supabase_admin.rpc("consume_ai_quota", {"p_user_id": user_id}).execute()
        row = (response.data or [{}])[0]
        return QuotaState(
            remaining_free=max(0, _as_int(row.get("remaining_free"))),
            credits_remaining=max(0, _as_int(row.get("credits_remaining"))),
            is_pro=bool(row.get("is_pro")),
            consumed=bool(row.get("consumed")),
            consumption_type=str(row.get("consumption_type") or "none"),
        )

    def log_usage_event(
        self,
        *,
        user_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        estimated_cost_usd: float,
        source: str = _CHAT_SOURCE,
    ) -> None:
        (
            supabase_admin.table("ai_usage_events")
            .insert(
                {
                    "user_id": user_id,
                    "model": model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "estimated_cost_usd": estimated_cost_usd,
                    "source": source,
                }
            )
            .execute()
        )


class OpenAIResponsesService:
    """Thin OpenAI Responses API wrapper."""

    def create_chat_response(self, *, message: str, conversation_id: str | None) -> OpenAIChatResult:
        if not settings.openai_api_key:
            raise OpenAIRequestError("OPENAI_API_KEY is not configured.")

        payload: dict[str, Any] = {
            "model": settings.openai_chat_model,
            "instructions": _CHAT_SYSTEM_PROMPT,
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": message}],
                }
            ],
            "max_output_tokens": settings.openai_max_output_tokens,
        }
        if conversation_id:
            payload["conversation"] = conversation_id

        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                settings.openai_api_url,
                json=payload,
                headers=headers,
                timeout=settings.openai_request_timeout_seconds,
            )
        except requests.RequestException as exc:  # pragma: no cover - upstream network failure
            raise OpenAIRequestError("OpenAI request failed.") from exc

        if response.status_code >= 500:
            raise OpenAIRequestError("OpenAI request failed.")
        if response.status_code >= 400:
            raise OpenAIRequestError("OpenAI request was rejected.")

        try:
            data = response.json()
        except ValueError as exc:
            raise OpenAIRequestError("OpenAI returned invalid JSON.") from exc

        text = self._extract_output_text(data)
        usage = data.get("usage") or {}
        resolved_conversation_id = self._extract_conversation_id(data) or conversation_id
        return OpenAIChatResult(
            text=text,
            model=str(data.get("model") or settings.openai_chat_model),
            conversation_id=resolved_conversation_id,
            prompt_tokens=max(0, _as_int(usage.get("input_tokens"))),
            completion_tokens=max(0, _as_int(usage.get("output_tokens"))),
            total_tokens=max(0, _as_int(usage.get("total_tokens"))),
        )

    def _extract_output_text(self, payload: Mapping[str, Any]) -> str:
        direct_text = str(payload.get("output_text") or "").strip()
        if direct_text:
            return direct_text

        chunks: list[str] = []
        for item in payload.get("output") or []:
            if not isinstance(item, Mapping):
                continue
            if item.get("type") != "message":
                continue
            for content in item.get("content") or []:
                if not isinstance(content, Mapping):
                    continue
                content_type = str(content.get("type") or "")
                if content_type not in {"output_text", "text"}:
                    continue
                text = str(content.get("text") or "").strip()
                if text:
                    chunks.append(text)

        combined = "\n".join(chunks).strip()
        if not combined:
            raise OpenAIRequestError("OpenAI returned an empty response.")
        return combined

    def _extract_conversation_id(self, payload: Mapping[str, Any]) -> str | None:
        conversation = payload.get("conversation")
        if isinstance(conversation, str) and conversation.strip():
            return conversation.strip()
        if isinstance(conversation, Mapping):
            conversation_id = str(conversation.get("id") or "").strip()
            if conversation_id:
                return conversation_id
        conversation_id = str(payload.get("conversation_id") or "").strip()
        return conversation_id or None


quota_service = QuotaService()
cost_estimator = CostEstimator()
openai_responses_service = OpenAIResponsesService()
