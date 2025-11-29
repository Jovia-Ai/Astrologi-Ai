"""Groq integration helpers for AI narratives."""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Mapping, Sequence

import requests

from app.ai.archetypes.analyzer import extract_archetype_data
from app.ai.prompts import AI_PROMPT, INTERPRETATION_PROMPT
from app.core.config import settings
from app.core.errors import AIError

logger = logging.getLogger(__name__)


def call_groq(
    messages: Sequence[Dict[str, str]],
    *,
    temperature: float = 0.6,
    max_tokens: int = 600,
    top_p: float | None = None,
    presence_penalty: float | None = None,
    frequency_penalty: float | None = None,
) -> str:
    """Send a chat completion request to Groq and return the model response."""

    if not settings.groq_api_key:
        raise AIError("GROQ_API_KEY yapılandırılmadı.")

    payload = {
        "model": settings.groq_model,
        "messages": list(messages),
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if top_p is not None:
        payload["top_p"] = top_p
    if presence_penalty is not None:
        payload["presence_penalty"] = presence_penalty
    if frequency_penalty is not None:
        payload["frequency_penalty"] = frequency_penalty

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(settings.groq_api_url, json=payload, headers=headers, timeout=20)
    except requests.RequestException as exc:  # pragma: no cover - network error
        raise AIError("Groq API isteği başarısız oldu.") from exc

    if response.status_code >= 400:
        raise AIError(f"Groq API hatası: {response.status_code} - {response.text}")

    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        raise AIError("Groq API beklenen yanıtı döndürmedi.")

    message = choices[0].get("message") or {}
    content = message.get("content", "").strip()
    if not content:
        raise AIError("Groq yanıtı boş döndü.")
    return content


def call_groq_ai(
    prompt: str,
    *,
    temperature: float = 0.4,
    top_p: float = 0.85,
    presence_penalty: float = 0.1,
    frequency_penalty: float = 0.3,
    max_tokens: int = 400,
) -> str:
    """Helper dedicated to life narrative generations with strict settings."""

    messages = [
        {"role": "user", "content": prompt},
    ]
    return call_groq(
        messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
    )


def generate_ai_interpretation(chart_data: dict[str, Any] | str) -> str:
    """Call Groq Chat Completions to produce an interpretation."""

    if not settings.groq_api_key:
        return "AI interpretation unavailable."

    if isinstance(chart_data, str):
        chart_text = chart_data
    else:
        try:
            chart_text = json.dumps(chart_data, ensure_ascii=False)
        except (TypeError, ValueError):
            chart_text = str(chart_data)

    prompt = f"You are an expert astrologer. Analyze this chart: {chart_text}"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.groq_model,
        "messages": [
            {
                "role": "system",
                "content": "You are an AI astrologer providing deep and empathetic insights.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    try:
        response = requests.post(settings.groq_api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "AI interpretation unavailable.")
    except requests.RequestException as exc:
        logger.warning("Groq request failed: %s", exc)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Groq response parsing failed: %s", exc)
    return "AI interpretation unavailable."


def chart_to_summary(chart: Mapping[str, Any]) -> str:
    """Convert chart data into a textual summary for the AI assistant."""

    location = chart.get("location", {})
    lines = [
        f"Konum: {location.get('city', 'Bilinmeyen')} | Zaman Dilimi: {chart.get('timezone', 'N/A')} | Doğum: {chart.get('birth_datetime', 'N/A')}",
        "Gezegenler:",
    ]

    planets = chart.get("planets", {})
    for planet, details in planets.items():
        lines.append(
            f"- {planet}: {details.get('sign', 'N/A')} burcunda, {details.get('house', '?')} evde (uzunluk {details.get('longitude')}°)"
        )

    houses = chart.get("houses")
    if isinstance(houses, list) and houses:
        lines.append("Ev Başlangıçları:")
        lines.append(", ".join(f"Ev {idx + 1}: {angle}°" for idx, angle in enumerate(houses)))

    angles = chart.get("angles", {})
    if angles:
        lines.append(
            "Özel Açılar: "
            + ", ".join(f"{name.title()}: {value}°" for name, value in angles.items())
        )

    return "\n".join(lines)


def generate_chart_interpretation(chart: Mapping[str, Any], *, name: str | None = None) -> str:
    """Use Groq to interpret the natal chart data."""

    summary = chart_to_summary(chart)
    user_prompt = "\n".join(
        filter(
            None,
            [
                "Aşağıda kullanıcının doğum haritası verileri bulunuyor.",
                f"Kullanıcı adı: {name}" if name else None,
                summary,
                "Lütfen Türkçe olarak, burçların anlamlarını, gezegenlerin evlerdeki etkilerini ve dikkat edilmesi gereken noktaları içeren detaylı fakat anlaşılır bir yorum yaz.",
            ],
        )
    )

    messages: Sequence[Dict[str, str]] = (
        {"role": "system", "content": "Sen deneyimli bir astroloji yorumcususun. Açıklayıcı, empatik ve eğitici bir ton kullan."},
        {"role": "user", "content": user_prompt},
    )

    return call_groq(messages, temperature=0.7, max_tokens=700)


def generate_synastry_interpretation(chart1: Mapping[str, Any], chart2: Mapping[str, Any], aspects: Sequence[Mapping[str, Any]]) -> str:
    """Produce a relational interpretation for two charts using Groq."""

    summary = "\n".join(
        [
            "Kişi 1 Haritası:",
            chart_to_summary(chart1),
            "",
            "Kişi 2 Haritası:",
            chart_to_summary(chart2),
            "",
            "Önemli Açılar:",
            "\n".join(
                f"- {item.get('planet1')} & {item.get('planet2')}: {item.get('aspect')} (orb {item.get('orb')}°)"
                for item in aspects
            )
            if aspects
            else "- Paylaşılan önemli açı bulunamadı.",
        ]
    )

    messages: Sequence[Dict[str, str]] = (
        {"role": "system", "content": "Sen uzman bir sinastri yorumcususun. Dengeleyici ve sezgisel içgörüler sun."},
        {
            "role": "user",
            "content": summary + "\nLütfen ilişki dinamiklerini, güçlü ve zorlayıcı temaları Türkçe olarak açıkla.",
        },
    )

    return call_groq(messages, temperature=0.65, max_tokens=600)


def get_ai_interpretation(chart_data: Mapping[str, Any]) -> Dict[str, Any]:
    """Generate a rich interpretation by blending archetype themes with Groq output."""

    try:
        archetype = extract_archetype_data(chart_data)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Archetype extraction failed: %s", exc)
        fallback_ai = {
            "headline": "Interpretation unavailable",
            "summary": "We could not generate a full interpretation at this time.",
            "advice": "Stay grounded and patient; your insight is unfolding.",
        }
        return {
            "ai_interpretation": fallback_ai,
            "themes": [],
            "tone": "balanced growth",
        }

    groq_api_key = settings.groq_api_key
    groq_model = settings.groq_model
    if not groq_api_key:
        logger.warning("⚠️ GROQ_API_KEY not found; cannot call Groq.")
        fallback_ai = {
            "headline": "Interpretation unavailable",
            "summary": "We could not generate a full interpretation at this time.",
            "advice": "Stay grounded and patient; your insight is unfolding.",
        }
        return {
            "ai_interpretation": fallback_ai,
            "themes": archetype.get("core_themes", []),
            "tone": archetype.get("story_tone", "balanced growth"),
        }

    core_themes = archetype.get("core_themes", [])
    tone_value = archetype.get("story_tone", "balanced growth")
    themes = ", ".join(core_themes) or "inner exploration"
    aspects = ", ".join(archetype.get("notable_aspects", [])) or "No notable aspects recorded."

    fallback_ai = {
        "headline": "Interpretation unavailable",
        "summary": "We could not generate a full interpretation at this time.",
        "advice": "Stay grounded and patient; your insight is unfolding.",
    }

    def build_result(ai_output: Dict[str, str]) -> Dict[str, Any]:
        return {
            "ai_interpretation": ai_output,
            "themes": core_themes,
            "tone": tone_value,
        }

    correlations = archetype.get("correlations") or {}
    prompt = (
        f"{INTERPRETATION_PROMPT}\n\n"
        "Verilen astrolojik veriyi aşağıdaki bağlamla yorumla ve belirtilen şemaya uygun JSON üret:\n"
        f"- Temalar: {themes}\n"
        f"- Ton: {tone_value}\n"
        f"- Ana eksen: {archetype.get('dominant_axis') or 'belirtilmedi'}\n"
        f"- Dikkate değer açılar: {aspects}\n"
        f"- Davranış kalıpları: {archetype.get('behavior_patterns')}\n"
        f"- Element dengesi: {correlations.get('element_balance')}\n"
        f"- Modalite dengesi: {correlations.get('modality_balance')}\n"
        f"- Baskın gezegen: {correlations.get('dominant_planet')}\n"
        f"- Polar eksen: {correlations.get('polar_axis')}\n"
        f"- Enerji deseni: {correlations.get('dominant_cluster')}\n"
        "Her alanı Türkçe doldur; temaları doğal dile çevir.\n"
    )

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": groq_model,
        "messages": [
            {"role": "system", "content": "Sen bir psikolojik astrologsun."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.55,
        "max_tokens": 650,
    }

    try:
        response = requests.post(settings.groq_api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if content:
            ai_output = json.loads(content)
            return build_result(ai_output)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Groq archetype generation failed: %s", exc)
    return {
        "ai_interpretation": fallback_ai,
        "themes": core_themes,
        "tone": tone_value,
    }


def request_refined_interpretation(archetype: Mapping[str, Any], chart_data: Mapping[str, Any]) -> Dict[str, Any]:
    """Call Groq to craft a poetic interpretation informed by extracted themes."""

    groq_api_key = settings.groq_api_key
    if not groq_api_key:
        logger.warning("⚠️ GROQ_API_KEY not found in environment.")
        raise AIError("GROQ_API_KEY yapılandırılmadı.")

    system_prompt = "You are an experienced psychological astrologer and storyteller."
    context_payload = {
        "core_themes": archetype.get("core_themes", []),
        "story_tone": archetype.get("story_tone"),
        "dominant_axis": archetype.get("dominant_axis"),
        "notable_aspects": archetype.get("notable_aspects", []),
        "behavior_patterns": archetype.get("behavior_patterns", []),
        "correlations": archetype.get("correlations", {}),
        "chart_data": chart_data,
    }
    user_prompt = (
        f"{INTERPRETATION_PROMPT}\n\n"
        "Verilen bağlamı kullanarak şemaya sadık kal:\n"
        f"{json.dumps(context_payload, ensure_ascii=False)}"
    )

    try:
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            settings.groq_api_url,
            headers=headers,
            json={
                "model": settings.groq_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": 400,
                "temperature": 0.8,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        ai_message = data["choices"][0]["message"]["content"]
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Groq request failed: %s", exc)
        raise AIError("Groq isteği başarısız oldu.") from exc

    parsed = None
    if ai_message:
        try:
            parsed = json.loads(ai_message)
        except json.JSONDecodeError:
            headline_match = re.search(r"(?i)(headline|title)[:\-]\s*(.*)", ai_message)
            summary_match = re.search(r"(?i)(summary|interpretation)[:\-]\s*(.*)", ai_message)
            advice_match = re.search(r"(?i)(advice|guidance)[:\-]\s*(.*)", ai_message)

            headline = headline_match.group(2).strip() if headline_match else "Interpretation unavailable"
            summary = summary_match.group(2).strip() if summary_match else ai_message[:400].strip()
            advice = advice_match.group(2).strip() if advice_match else "Trust your own timing."

            parsed = {
                "headline": headline,
                "summary": summary,
                "advice": advice,
            }
    if not parsed:
        parsed = {
            "headline": "Interpretation unavailable",
            "summary": "We could not generate a full interpretation at this time.",
            "advice": "Stay grounded and patient; your insight is unfolding.",
        }

    headline = str(parsed.get("headline", "")).strip() or "Interpretation unavailable"
    summary = str(parsed.get("summary", "")).strip() or "We could not generate a full interpretation at this time."
    advice = str(parsed.get("advice", "")).strip() or "Stay grounded and patient; your insight is unfolding."

    ai_output = {
        "headline": headline,
        "summary": summary,
        "advice": advice,
    }

    return {
        "ai_interpretation": ai_output,
        "themes": archetype.get("core_themes", []),
        "tone": archetype.get("story_tone", "balanced growth"),
    }
