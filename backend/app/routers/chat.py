"""Chat routes powered by Groq."""
from __future__ import annotations

import logging
from typing import Any, Dict, Mapping

from fastapi import APIRouter, Body, HTTPException

from app.ai.narrative.groq_client import call_groq, chart_to_summary
from app.core.errors import AIError

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("/chat/message")
def chat_message(payload: Dict[str, Any] = Body(...)):
    try:
        message = str(payload.get("message", "")).strip()
        if not message:
            raise ValueError("message alanı gerekli.")

        history = []
        raw_history = payload.get("history")
        if isinstance(raw_history, list):
            for item in raw_history:
                if not isinstance(item, Mapping):
                    continue
                role = item.get("role")
                content = item.get("content")
                if role in {"user", "assistant"} and isinstance(content, str):
                    history.append({"role": role, "content": content})

        system_messages = [
            {
                "role": "system",
                "content": "Sen Astrologi-AI adlı kozmik rehbersin. Türkçe yanıt ver, kullanıcıya empatik ve açıklayıcı bir tavırla yaklaş.",
            }
        ]

        chart_context = payload.get("chart")
        if isinstance(chart_context, Mapping):
            system_messages.append(
                {
                    "role": "system",
                    "content": "Kullanıcı doğum haritası verileri:\n" + chart_to_summary(chart_context),
                }
            )

        messages = [*system_messages, *history, {"role": "user", "content": message}]
        temperature = float(payload.get("temperature", 0.6))
        max_tokens = int(payload.get("maxTokens", 600))
        reply = call_groq(messages, temperature=temperature, max_tokens=max_tokens)
        return {"reply": reply}
    except AIError as exc:
        logger.error("AI chat error: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to process chat message")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
