from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Mapping

BLACKLIST = {
    "orb",
    "aspect",
    "applying",
    "separating",
    "percentile",
    "marker",
    "tier",
}
YOU_STYLE_HINTS = (
    "hissedebilirsin",
    "fark edebilirsin",
    "bazen",
    "olabilir",
    "tetikleyebilir",
)

SIGN_ALIASES = {
    "aries": "Aries",
    "taurus": "Taurus",
    "gemini": "Gemini",
    "cancer": "Cancer",
    "libra": "Libra",
    "capricorn": "Capricorn",
}


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _normalize_sentence(value: str) -> str:
    text = _normalize_text(value)
    if not text:
        return ""
    text = re.sub(r"[.!?]+$", "", text)
    return f"{text}."


def _contains_blacklist(value: str) -> bool:
    low = value.lower()
    return any(word in low for word in BLACKLIST)


def _safe_sentence(value: str) -> str:
    text = _normalize_sentence(value)
    if not text:
        return "Bugunu sade ve net adimlarla tasimak daha iyi hissettirebilir."
    if _contains_blacklist(text):
        return "Bugunu sade ve net adimlarla tasimak daha iyi hissettirebilir."
    return text


def _clamp_chars(value: str, limit: int = 280) -> str:
    text = _safe_sentence(value)
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rstrip()
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return f"{cut}."


def _apply_voice_style(text: str, *, voice_style: str, seed: int, salt: str) -> str:
    normalized = _safe_sentence(text)
    if voice_style != "you":
        return normalized
    low = normalized.lower()
    if any(token in low for token in YOU_STYLE_HINTS):
        return normalized
    variants = [
        "Bunu gun icinde daha net hissedebilirsin.",
        "Ozellikle bu temayi daha kolay fark edebilirsin.",
        "Bazen bu etki dusundugunden daha belirgin olabilir.",
        "Bu ritim tepkilerini farkli sekilde tetikleyebilir.",
    ]
    idx_seed = int(hashlib.sha1(f"{seed}|voice|{salt}".encode("utf-8")).hexdigest()[:8], 16)
    return f"{normalized.rstrip('.')} {variants[idx_seed % len(variants)]}"


def _pick(options: list[str], seed: int, salt: str, fallback: str) -> str:
    cleaned = [str(opt).strip() for opt in options if str(opt).strip()]
    if not cleaned:
        return fallback
    idx_seed = int(hashlib.sha1(f"{seed}|{salt}".encode("utf-8")).hexdigest()[:8], 16)
    return cleaned[idx_seed % len(cleaned)]


def _seed_from_item(item: Mapping[str, Any]) -> int:
    signs = item.get("signs") if isinstance(item.get("signs"), Mapping) else {}
    houses = item.get("houses") if isinstance(item.get("houses"), Mapping) else {}
    sign = str(signs.get("transit_body_sign") or "generic")
    house = str(houses.get("transit_in_natal_house") or "generic")
    raw = "|".join(
        [
            str(item.get("event_id") or ""),
            str(item.get("transit_body") or ""),
            sign,
            house,
            str(item.get("aspect") or ""),
            str(item.get("phase") or ""),
            str(item.get("bucket") or ""),
        ]
    )
    return int(hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8], 16)


@lru_cache(maxsize=1)
def _load_pack() -> Dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "content" / "archetypes.v1.tr.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_insight_pack(
    item: Mapping[str, Any],
    seed: int | None = None,
    *,
    voice_style: str = "you",
    locale: str = "tr",
) -> Dict[str, str]:
    pack = _load_pack()
    if seed is None:
        seed = _seed_from_item(item)

    transit_body = str(item.get("transit_body") or "Saturn")
    signs = item.get("signs") if isinstance(item.get("signs"), Mapping) else {}
    sign_raw = str(signs.get("transit_body_sign") or "").strip()
    sign = SIGN_ALIASES.get(sign_raw.lower(), "generic")
    houses = item.get("houses") if isinstance(item.get("houses"), Mapping) else {}
    house = str(houses.get("transit_in_natal_house") or "generic")

    planets = pack.get("planets") if isinstance(pack.get("planets"), Mapping) else {}
    signs_pack = pack.get("signs") if isinstance(pack.get("signs"), Mapping) else {}
    houses_pack = pack.get("houses") if isinstance(pack.get("houses"), Mapping) else {}
    templates = pack.get("templates") if isinstance(pack.get("templates"), Mapping) else {}

    planet_data = planets.get(transit_body) if isinstance(planets.get(transit_body), Mapping) else {}
    if not planet_data:
        planet_data = planets.get("Saturn") if isinstance(planets.get("Saturn"), Mapping) else {}
    sign_data = signs_pack.get(sign) if isinstance(signs_pack.get(sign), Mapping) else {}
    if not sign_data:
        sign_data = signs_pack.get("generic") if isinstance(signs_pack.get("generic"), Mapping) else {}
    house_data = houses_pack.get(house) if isinstance(houses_pack.get(house), Mapping) else {}
    if not house_data:
        house_data = houses_pack.get("generic") if isinstance(houses_pack.get("generic"), Mapping) else {}

    arena = str(house_data.get("arena") or "gunluk yasam akisi icinde")
    conflict = _pick(
        list(planet_data.get("conflict") or []),
        seed,
        f"planet_conflict:{locale}",
        "icteki beklenti ile dis tempo arasinda zorlayici bir gerilim olusabilir",
    )
    shadow = _pick(
        list(planet_data.get("shadow") or []),
        seed,
        f"planet_shadow:{locale}",
        "savunma refleksi net iletisim yerine kapanmaya yonelebilir",
    )
    growth = _pick(
        list(planet_data.get("growth") or []),
        seed,
        f"planet_growth:{locale}",
        "kucuk ama istikrarli adimlar daha saglam bir denge kurdurur",
    )
    sign_drive = _pick(
        list(sign_data.get("drive") or []),
        seed,
        f"sign_drive:{locale}",
        "gundemin ritmi belirgin sekilde degisiyor",
    )
    sign_risk = _pick(
        list(sign_data.get("risk") or []),
        seed,
        f"sign_risk:{locale}",
        "dengeyi korumak icin tempo ayari gerekebilir",
    )
    sign_growth = _pick(
        list(sign_data.get("growth") or []),
        seed,
        f"sign_growth:{locale}",
        "olculu netlik daha guvenli bir akis yaratir",
    )
    house_shadow = str(house_data.get("shadow") or "fazla yuklenme ritmi zorlayabilir")
    house_upper = str(house_data.get("upper") or "olculu tempo dengeyi korur")

    conflict_sentence = _clamp_chars(f"{arena.capitalize()} {sign_drive}; {conflict}.")
    shadow_sentence = _clamp_chars(f"{shadow}; {sign_risk}. {house_shadow}.")
    upper_sentence = _clamp_chars(f"{growth}; {sign_growth}. {house_upper}.")

    conflict_sentence = _clamp_chars(
        _apply_voice_style(conflict_sentence, voice_style=voice_style, seed=seed, salt="conflict")
    )
    shadow_sentence = _clamp_chars(
        _apply_voice_style(shadow_sentence, voice_style=voice_style, seed=seed, salt="shadow")
    )
    upper_sentence = _clamp_chars(
        _apply_voice_style(upper_sentence, voice_style=voice_style, seed=seed, salt="upper")
    )

    short_templates = list(templates.get("conflict_short") or [])
    short_raw = _pick(
        short_templates,
        seed,
        f"conflict_short:{locale}",
        "{arena} once sakinlesip netlesmek ister.",
    )
    conflict_short = _clamp_chars(
        _apply_voice_style(
            short_raw.format(arena=arena),
            voice_style=voice_style,
            seed=seed,
            salt="conflict_short",
        )
    )

    return {
        "conflict": conflict_sentence,
        "shadow": shadow_sentence,
        "upper": upper_sentence,
        "conflict_short": conflict_short,
    }
