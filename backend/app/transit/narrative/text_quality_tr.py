from __future__ import annotations

import os
import re
from collections import Counter
from difflib import SequenceMatcher
from typing import Any, Dict, List, Mapping, Sequence

from app.narrative.humanize_tr import humanize_tr_text
from app.transit.narrative.phrase_lib_tr import (
    compose_phrase_pack,
    house_motif_line,
    strip_tech_tokens,
)

_COPY_QUALITY_ENABLED = str(os.getenv("COPY_QUALITY_LAYER", "1")).strip().lower() not in {
    "0",
    "false",
    "off",
    "no",
}
_ENABLE_MICRO_LLM_POLISH = str(os.getenv("ENABLE_MICRO_LLM_POLISH", "0")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
_MICRO_LLM_PROVIDER = str(os.getenv("MICRO_LLM_PROVIDER", "none")).strip().lower() or "none"

_TR_WORD_FIXES = {
    "iletisim": "iletişim",
    "iliski": "ilişki",
    "hiz": "hız",
    "dogrudan": "doğrudan",
    "kacinma": "kaçınma",
    "golge": "gölge",
    "duzen": "düzen",
    "donusum": "dönüşüm",
    "ic": "iç",
    "dis": "dış",
    "firsat": "fırsat",
    "netlik": "netlik",
    "yonsuz": "yönsüz",
    "stili": "stili",
    "yaklasim": "yaklaşım",
    "uygulama": "uygulama",
    "donemde": "dönemde",
    "donem": "dönem",
    "surec": "süreç",
    "sureci": "süreci",
    "ozet": "özet",
    "ozel": "özel",
    "ozgur": "özgür",
    "ozgurluk": "özgürlük",
    "goz": "göz",
    "gonder": "gönder",
    "cikar": "çıkar",
    "karsi": "karşı",
    "cozuluyor": "çözülüyor",
    "cozulme": "çözülme",
    "bilincalti": "bilinçaltı",
    "olcum": "ölçüm",
    "olc": "ölç",
    "tasma": "taşma",
    "saglik": "sağlık",
    "gorunurluk": "görünürlük",
    "iliski": "ilişki",
    "iliski": "ilişki",
    "yontem": "yöntem",
    "degisim": "değişim",
    "netlesme": "netleşme",
    "dengeleme": "dengeleme",
}

_SIGN_TR = {
    "aries": "Koç",
    "taurus": "Boğa",
    "gemini": "İkizler",
    "cancer": "Yengeç",
    "leo": "Aslan",
    "virgo": "Başak",
    "libra": "Terazi",
    "scorpio": "Akrep",
    "sagittarius": "Yay",
    "capricorn": "Oğlak",
    "aquarius": "Kova",
    "pisces": "Balık",
}

_PLANET_ALLOWLIST = {
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "asc",
    "dsc",
    "mc",
    "ic",
    "north_node",
    "south_node",
    "lilith",
    "chiron",
    "vertex",
    "fortune",
}

_PLANET_TR = {
    "sun": "Güneş",
    "moon": "Ay",
    "mercury": "Merkür",
    "venus": "Venüs",
    "mars": "Mars",
    "jupiter": "Jüpiter",
    "saturn": "Satürn",
    "uranus": "Uranüs",
    "neptune": "Neptün",
    "pluto": "Plüton",
    "asc": "ASC",
    "dsc": "DSC",
    "mc": "MC",
    "ic": "IC",
    "north_node": "Kuzey Ay Düğümü",
    "south_node": "Güney Ay Düğümü",
    "lilith": "Lilith",
    "chiron": "Chiron",
    "vertex": "Vertex",
    "fortune": "Fortune",
}

_VERB_STARTS = (
    "netleştir",
    "sadeleştir",
    "yaz",
    "çıkar",
    "cikar",
    "bağla",
    "bagla",
    "sabitle",
    "açma",
    "acma",
    "tamamla",
    "planla",
    "koru",
    "seç",
    "ölç",
    "sor",
    "bekle",
    "gözden",
    "durdur",
    "teyit",
    "odaklan",
    "yenile",
    "yavaşlat",
)

_THEME_BANK: Dict[str, Any] = {
    "modes": {
        "daily": {
            "length": {
                "conflict_sentences": (2, 3),
                "shadow_sentences": (1, 2),
                "upper_sentences": (2, 3),
                "extra_line_sentences": (1, 1),
                "guidance_bullets": 3,
                "watch_out_bullets": 2,
            }
        },
        "period": {
            "length": {
                "core_story_paragraphs": (2, 4),
                "core_story_sentences_per_paragraph": (3, 5),
                "upper_meaning_paragraphs": (1, 2),
                "upper_meaning_sentences": (3, 5),
            }
        },
    },
    "event_generation": {
        "path_scoring": {
            "max_hops": 3,
            "node_weights": {
                "transit_planet": 0.9,
                "aspect": 0.7,
                "natal_target_planet": 1.0,
                "natal_target_house": 0.9,
                "natal_target_sign": 0.7,
                "dispositor": 0.6,
                "rulership_house": 0.5,
                "angle_hit": 0.85,
            },
            "edge_weights": {
                "aspect_edge": 1.0,
                "house_edge": 0.6,
                "sign_edge": 0.6,
                "dispositor_edge": 0.8,
                "rulership_edge": 0.7,
                "angle_edge": 0.9,
            },
        },
        "motif_selection": {
            "top_motifs": 3,
            "must_include": ("house_scene",),
            "prefer_include": ("sign_style", "dispositor_hint"),
        },
    },
    "houses": {
        3: {
            "label": "zihin/iletisim",
            "scene": "mesajlar-konuşmalar ve yazma-not alma ritmi",
            "motif": "dil kalibrasyonu",
        },
        6: {
            "label": "rutin/saglik/servis",
            "scene": "takvim ve iş akışı ritmi",
            "motif": "mikro alışkanlık",
        },
        7: {
            "label": "iliskiler/ortaklik",
            "scene": "anlaşma dili ve beklenti dengesi",
            "motif": "uyum ve sınır",
        },
        9: {
            "label": "anlam/ufuk/genisleme",
            "scene": "öğrenme, yayın ve yabancı dil sahnesi",
            "motif": "anlam motoru",
        },
    },
    "promise_hooks": {
        "identity_line": "Dış geri bildirim içeride kalıcı bir kimlik ayarı kuruyor.",
        "mind_line": "Zihinsel otoriteyi kurdukça kararların kalıcılığı artıyor.",
    },
}


def tr_normalize(text: str) -> str:
    out = str(text or "")
    if not out.strip():
        return ""

    out = out.replace("\n", " ")
    out = re.sub(r"\s+", " ", out).strip()

    for raw, fixed in _TR_WORD_FIXES.items():
        out = re.sub(rf"\b{re.escape(raw)}\b", fixed, out, flags=re.IGNORECASE)

    out = re.sub(r"\b([1-9]|1[0-2])\s*ev\b", r"\1. Ev", out, flags=re.IGNORECASE)
    out = re.sub(r"\b([1-9]|1[0-2])\.\s*ev\b", r"\1. Ev", out, flags=re.IGNORECASE)

    for raw_sign, tr_sign in _SIGN_TR.items():
        out = re.sub(rf"\b{re.escape(raw_sign)}\b", tr_sign, out, flags=re.IGNORECASE)

    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    out = re.sub(r"([,;:!?])(?!\s|$)", r"\1 ", out)
    out = re.sub(r"\.{2,}", ".", out)
    out = re.sub(r"\s+", " ", out).strip()
    return out


def sanitize_connected_points(connected_points: Sequence[Mapping[str, Any]] | None) -> Dict[str, Any]:
    items = connected_points if isinstance(connected_points, Sequence) else []
    houses: List[str] = []
    house_values: List[int] = []
    signs: List[str] = []
    planets: List[str] = []
    chain = ""
    seen = set()

    def _append_unique(bucket: List[str], value: str) -> None:
        key = (id(bucket), value)
        if key in seen:
            return
        seen.add(key)
        bucket.append(value)

    for entry in items:
        if not isinstance(entry, Mapping):
            continue
        kind = str(entry.get("kind") or "").strip().lower()
        raw_value = entry.get("value")

        if kind == "house":
            number = None
            if isinstance(raw_value, int):
                number = raw_value
            else:
                match = re.search(r"\d+", str(raw_value or ""))
                if match:
                    number = int(match.group(0))
            if isinstance(number, int) and 1 <= number <= 12:
                _append_unique(houses, f"{number}. Ev")
                house_values.append(number)
            continue

        if kind == "sign":
            sign = str(raw_value or "").strip().lower()
            if sign in _SIGN_TR:
                _append_unique(signs, _SIGN_TR[sign])
            continue

        if kind == "planet":
            planet = str(raw_value or "").strip().lower()
            if planet in _PLANET_ALLOWLIST:
                _append_unique(planets, _PLANET_TR.get(planet, planet.title()))
            continue

        if kind == "dispositor_chain" and not chain:
            raw_parts = re.split(r"\s*->\s*", str(raw_value or ""))
            safe_parts = []
            for part in raw_parts:
                token = part.strip().lower()
                if token in _PLANET_ALLOWLIST:
                    safe_parts.append(_PLANET_TR.get(token, token.title()))
                if len(safe_parts) >= 4:
                    break
            if safe_parts:
                chain = " -> ".join(safe_parts)

    return {
        "houses": houses,
        "house_values": house_values,
        "signs": signs,
        "planets": planets,
        "dispositor_chain": chain,
        "house_3": 3 in house_values,
        "house_9": 9 in house_values,
    }


def polish_collocations(text: str) -> str:
    out = str(text or "")
    if not out.strip():
        return ""

    replacements = {
        r"\bneptune disiplini\b": "belirsizliği yönetme becerin",
        r"\bneptun disiplini\b": "belirsizliği yönetme becerin",
        r"\bneptün disiplini\b": "belirsizliği yönetme becerin",
        r"\bcapricorn stili\b": "kontrole çekilme hali",
        r"\boğlak stili\b": "kontrole çekilme hali",
    }
    for pattern, value in replacements.items():
        out = re.sub(pattern, value, out, flags=re.IGNORECASE)

    # Keep all allowed points visible; only normalize spacing/punctuation.
    out = re.sub(r"\s{2,}", " ", out).strip()
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    out = re.sub(r"\s+,", ",", out)
    out = re.sub(r",\s*,", ", ", out)
    return out


def cap_sentences(text: str, max_sentences: int = 3) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    if max_sentences < 1:
        return ""

    parts = [p.strip() for p in re.split(r"(?<!\d[.!?])(?<=[.!?])\s+", raw) if p.strip()]
    if len(parts) == 1 and "." not in raw and "!" not in raw and "?" not in raw:
        parts = [p.strip() for p in re.split(r"\s*;\s*", raw) if p.strip()]
    if not parts:
        return ""

    out = " ".join(parts[:max_sentences]).strip()
    if out and out[-1] not in ".!?":
        out += "."
    return out


def _s(x: Any) -> str:
    return str(x or "").strip()


def _first_sentence(text: str, max_len: int = 160) -> str:
    t = strip_tech_tokens(str(text or "")).strip()
    if not t:
        return ""
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", t) if p.strip()]
    s = parts[0] if parts else t
    if len(s) > max_len:
        s = s[:max_len].rstrip() + "…"
    return s


def _dedupe_sentences(text: str) -> str:
    t = strip_tech_tokens(str(text or "")).strip()
    if not t:
        return ""
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", t) if p.strip()]
    seen: set[str] = set()
    out: List[str] = []
    for p in parts:
        key = " ".join(p.lower().split())
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    merged = " ".join(out).strip()
    if merged and merged[-1] not in ".!?":
        merged += "."
    return merged


def _clamp_bullets(items: Any, max_n: int = 3) -> List[str]:
    if not isinstance(items, list):
        return []
    out: List[str] = []
    seen: set[str] = set()
    for it in items:
        s = strip_tech_tokens(str(it or "")).strip()
        if not s:
            continue
        key = " ".join(s.lower().split())
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
        if len(out) >= max_n:
            break
    return out


def rewrite_period_card_tr(
    card: Mapping[str, Any],
    event: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Final-pass rewrite for PERIOD cards: human tone, 'sana ne katıyor' framing,
    house motif expansion, tech token stripping, de-duplication.
    """
    out = dict(card)
    ev = dict(event or {})

    # House context (scene): prefer transit house, else target house
    houses = ev.get("houses") if isinstance(ev.get("houses"), Mapping) else {}
    transit_house = houses.get("transit_in_natal_house")
    target_house = houses.get("natal_point_house")
    scene_house = int(transit_house) if transit_house else (int(target_house) if target_house else None)
    scene = house_motif_line(scene_house)

    # Teaser (tap reason) — 1 clear line
    # Prefer existing teaser/why_now/conflict; but make it period-style
    raw_seed = out.get("teaser") or out.get("why_now") or out.get("conflict") or out.get("upper") or ""
    seed_1 = _first_sentence(str(raw_seed), max_len=170)
    if scene:
        # "Bu dönem ..." opener, very clear and non-technical
        out["teaser"] = (
            f"Bu dönem {scene} alanında ince ayar var: "
            f"{seed_1.lower() if seed_1 else 'daha net seçim, daha iyi ritim.'}"
        )
    else:
        out["teaser"] = seed_1

    # Reframe sections to period tone (gain / skill)
    # conflict -> "Ne oluyor?" already in UI, keep but humanize
    out["conflict"] = _dedupe_sentences(out.get("conflict") or out.get("why_now") or "")
    # shadow -> "Refleks" in UI
    out["shadow"] = _dedupe_sentences(out.get("shadow") or "")
    # upper -> "Ustalık": always answer "sana ne katıyor?"
    upper_seed = out.get("upper") or ""
    upper_1 = _first_sentence(upper_seed, max_len=220)
    if scene:
        out["upper"] = _dedupe_sentences(
            f"Bu tema sende {scene} kasını güçlendiriyor: daha net seçim, daha iyi ritim. {upper_1}"
        )
    else:
        out["upper"] = _dedupe_sentences(upper_1)

    # Bullets
    out["guidance"] = _clamp_bullets(out.get("guidance"), max_n=3)
    out["watch_out"] = _clamp_bullets(out.get("watch_out"), max_n=2)

    # Extra line: short, warm, period
    extra = out.get("extra_line") or ""
    extra_1 = _first_sentence(extra, max_len=120)
    out["extra_line"] = extra_1

    # Final tech strip for all visible fields
    for k in ["title", "teaser", "conflict", "shadow", "upper", "extra_line"]:
        if k in out:
            out[k] = strip_tech_tokens(str(out.get(k) or "")).strip()
    return out


def normalize_card_text_tr(card: Mapping[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = dict(card)

    for field in ("title", "conflict", "shadow", "upper", "extra_line", "time_hint"):
        value = str(normalized.get(field) or "")
        value = humanize_tr_text(value)
        value = tr_normalize(value)
        value = polish_collocations(value)
        cap = 2 if field in {"title", "time_hint"} else 3
        normalized[field] = cap_sentences(value, max_sentences=cap)

    guidance = normalized.get("guidance") if isinstance(normalized.get("guidance"), list) else []
    normalized["guidance"] = _normalize_bullet_list(
        guidance,
        fallback=["Yaz tek cümle niyet.", "Çıkar taslak, sonra gönder.", "Bağla ritmi mini-rutine."],
        minimum=3,
    )[:3]

    watch = normalized.get("watch_out") if isinstance(normalized.get("watch_out"), list) else []
    normalized["watch_out"] = _normalize_bullet_list(watch, fallback=["Açma aynı anda iki kanal.", "Sabitle önce niyeti, sonra hız ver."], minimum=2)[:2]
    return normalized


def apply_house_theme_hints(
    card: Mapping[str, Any],
    injection_bits: Mapping[str, Any],
    context: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = dict(card)
    ctx = context if isinstance(context, Mapping) else {}

    transit_house = _safe_int(ctx.get("transit_house"))
    is_house_3 = bool(injection_bits.get("house_3")) or transit_house == 3
    is_house_9 = bool(injection_bits.get("house_9")) or transit_house == 9

    if is_house_3:
        conflict = str(out.get("conflict") or "")
        if not _has_any(conflict, ("mesaj", "konuş", "yazı", "yanlış anlaşıl", "yakın çevre", "dijital")):
            conflict = f"{conflict} Mesaj ve konuşma trafiğinde yanlış anlaşılmayı azaltmak kritik."
            out["conflict"] = cap_sentences(tr_normalize(conflict), max_sentences=3)
        guidance = out.get("guidance") if isinstance(out.get("guidance"), list) else []
        if not _list_has_any(guidance, ("mesaj", "konuş", "yaz", "yakın çevre", "dijital")):
            guidance = list(guidance)
            clause = "Mesajını kısa ve net yaz; yakın çevre iletişiminde teyit al."
            if len(guidance) < 3:
                guidance.append(clause)
            elif guidance:
                guidance[-1] = clause
            out["guidance"] = [_normalize_bullet(x) for x in guidance][:3]

    if is_house_9:
        upper = str(out.get("upper") or "")
        if not _has_any(upper, ("öğren", "uzmanlaş", "yayın", "dünya görüş", "yabancı dil", "uzak")):
            upper = f"{upper} Öğrenme, uzmanlaşma ve dünya görüşünü güncelleme burada güçlenir."
            out["upper"] = cap_sentences(tr_normalize(upper), max_sentences=3)
        guidance = out.get("guidance") if isinstance(out.get("guidance"), list) else []
        if not _list_has_any(guidance, ("öğren", "uzman", "yayın", "yabancı dil", "uzak")):
            guidance = list(guidance)
            clause = "Öğrenme veya yabancı dil planını haftalık rutine bağla."
            if len(guidance) < 3:
                guidance.append(clause)
            elif guidance:
                guidance[-1] = clause
            out["guidance"] = [_normalize_bullet(x) for x in guidance][:3]

    return out


def apply_copy_quality_layer(
    card: Mapping[str, Any],
    connected_points: Sequence[Mapping[str, Any]] | None,
    context: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    if not _COPY_QUALITY_ENABLED:
        return dict(card)
    bits = sanitize_connected_points(connected_points)
    motifs = select_path_motifs(bits, context=context)
    out = normalize_card_text_tr(card)
    out = inject_selected_motifs(out, motifs, bits, context=context)
    out = apply_house_theme_hints(out, bits, context=context)
    out = _inject_phrase_pack(out, context=context)
    out = _dedupe_section_overlap(out)
    out = finalize_daily_lengths(out)
    if _ENABLE_MICRO_LLM_POLISH and _MICRO_LLM_PROVIDER != "none":
        out = polish_with_llm(out, {"connected_points": list(connected_points or []), "context": dict(context or {})})
    return out


def polish_with_llm(text_blocks: Mapping[str, Any], context: Mapping[str, Any]) -> Dict[str, Any]:
    _ = context
    # Placeholder hook only; provider integration intentionally disabled.
    return dict(text_blocks)


def _inject_phrase_pack(card: Mapping[str, Any], context: Mapping[str, Any] | None) -> Dict[str, Any]:
    out = dict(card)
    ctx = context if isinstance(context, Mapping) else {}
    pack = out.get("natal_context_pack") if isinstance(out.get("natal_context_pack"), Mapping) else {}

    event = {
        "event_id": str(out.get("event_id") or ""),
        "transit_body": str(ctx.get("transit_planet") or ""),
        "aspect": str(ctx.get("aspect") or ""),
        "natal_point": str(ctx.get("target") or ""),
        "orb_deg": _safe_float(ctx.get("orb_deg"), 9.9),
        "bucket": str(ctx.get("duration") or ""),
        "phase": str(ctx.get("phase") or ""),
        "houses": {"transit_in_natal_house": _safe_int(ctx.get("transit_house"))},
    }
    phrase = compose_phrase_pack(
        transit_body=str(event["transit_body"]),
        aspect=str(event["aspect"]),
        natal_point=str(event["natal_point"]),
        context_pack=pack,
        event=event,
        max_len={"conflict": 2, "shadow": 2, "upper": 2},
    )

    conflict_label = str(phrase.get("conflict_label") or "").strip()
    conflict_tone = str(phrase.get("conflict_tone") or "").strip()
    if conflict_label:
        out["conflict_label"] = conflict_label
    if conflict_tone:
        out["conflict_tone"] = conflict_tone
    tone = str(phrase.get("tone") or "").strip()
    if tone:
        out["tone"] = tone
    section_labels = phrase.get("section_labels") if isinstance(phrase.get("section_labels"), Mapping) else {}
    if section_labels:
        out["section_labels"] = dict(section_labels)
    why_now = str(phrase.get("why_now") or "").strip()
    if why_now:
        out["why_now"] = why_now

    title = str(phrase.get("title") or "").strip()
    if title:
        out["title"] = title

    scene_line = str(phrase.get("scene_line") or "").strip()
    conflict = str(out.get("conflict") or "").strip()
    conflict_add = str(phrase.get("conflict_add") or "").strip()
    if scene_line:
        conflict = _append_unique_sentence(scene_line, conflict)
    if conflict_add:
        conflict = _append_unique_sentence(conflict_add, conflict)
    out["conflict"] = conflict

    shadow = str(out.get("shadow") or "").strip()
    shadow_add = str(phrase.get("shadow_add") or "").strip()
    if shadow_add:
        shadow = _append_unique_sentence(shadow_add, shadow)
    out["shadow"] = shadow

    upper = str(out.get("upper") or "").strip()
    upper_add = str(phrase.get("upper_add") or "").strip()
    if upper_add:
        upper = _append_unique_sentence(upper_add, upper)
    out["upper"] = upper

    guidance = out.get("guidance") if isinstance(out.get("guidance"), list) else []
    guidance_add = phrase.get("guidance_add") if isinstance(phrase.get("guidance_add"), list) else []
    out["guidance"] = _merge_unique_list([str(x) for x in guidance_add], [str(x) for x in guidance], cap=3)

    watch = out.get("watch_out") if isinstance(out.get("watch_out"), list) else []
    watch_add = phrase.get("watch_out_add") if isinstance(phrase.get("watch_out_add"), list) else []
    out["watch_out"] = _merge_unique_list([str(x) for x in watch_add], [str(x) for x in watch], cap=2)
    return out


def select_path_motifs(injection_bits: Mapping[str, Any], context: Mapping[str, Any] | None) -> Dict[str, Any]:
    ctx = context if isinstance(context, Mapping) else {}
    node_weights = _THEME_BANK["event_generation"]["path_scoring"]["node_weights"]
    edge_weights = _THEME_BANK["event_generation"]["path_scoring"]["edge_weights"]
    top_k = int(_THEME_BANK["event_generation"]["motif_selection"]["top_motifs"])

    motifs: List[Dict[str, Any]] = []
    houses = injection_bits.get("house_values") if isinstance(injection_bits.get("house_values"), list) else []
    signs = injection_bits.get("signs") if isinstance(injection_bits.get("signs"), list) else []
    chain = str(injection_bits.get("dispositor_chain") or "").strip()

    if houses:
        h = int(houses[0])
        score = 1.0 * float(node_weights.get("natal_target_house", 0.9)) * float(edge_weights.get("house_edge", 0.6))
        motifs.append({"type": "house_scene", "value": h, "score": round(min(1.0, score), 3)})
    if signs:
        score = 1.0 * float(node_weights.get("natal_target_sign", 0.7)) * float(edge_weights.get("sign_edge", 0.6))
        motifs.append({"type": "sign_style", "value": signs[0], "score": round(min(1.0, score), 3)})
    if chain:
        score = 1.0 * float(node_weights.get("dispositor", 0.6)) * float(edge_weights.get("dispositor_edge", 0.8))
        motifs.append({"type": "dispositor_hint", "value": chain, "score": round(min(1.0, score), 3)})

    transit_house = _safe_int(ctx.get("transit_house"))
    if transit_house and all(m.get("type") != "house_scene" for m in motifs):
        score = 0.9 * float(node_weights.get("transit_planet", 0.9)) * float(edge_weights.get("house_edge", 0.6))
        motifs.append({"type": "house_scene", "value": transit_house, "score": round(min(1.0, score), 3)})

    motifs.sort(key=lambda item: _safe_float(item.get("score"), 0.0), reverse=True)
    selected = motifs[:top_k]

    must = _THEME_BANK["event_generation"]["motif_selection"]["must_include"]
    if "house_scene" in must and all(item.get("type") != "house_scene" for item in selected) and transit_house:
        selected.append({"type": "house_scene", "value": transit_house, "score": 0.3})

    selected = selected[:top_k]
    return {"selected": selected}


def inject_selected_motifs(
    card: Mapping[str, Any],
    motifs: Mapping[str, Any],
    injection_bits: Mapping[str, Any],
    context: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    out = dict(card)
    selected = motifs.get("selected") if isinstance(motifs.get("selected"), list) else []
    if not selected:
        return out

    motif_types = {str(item.get("type")): item for item in selected if isinstance(item, Mapping)}
    house_motif = motif_types.get("house_scene")
    sign_motif = motif_types.get("sign_style")
    disp_motif = motif_types.get("dispositor_hint")

    if house_motif:
        house = _safe_int(house_motif.get("value"))
        scene = (_THEME_BANK["houses"].get(house) or {}).get("scene")
        if scene:
            conflict = str(out.get("conflict") or "")
            if not _has_any(conflict, ("mesaj", "öğren", "yakın çevre", "yayın", "takvim", "anlaşma")):
                conflict = f"{conflict} Etki {house}. Evde {scene} üzerinden görünür olur."
                out["conflict"] = cap_sentences(tr_normalize(conflict), max_sentences=3)

    if sign_motif:
        sign = str(sign_motif.get("value") or "")
        upper = str(out.get("upper") or "")
        if sign and sign not in upper:
            upper = f"{upper} {sign} stili burada tempoyu belirliyor."
            out["upper"] = cap_sentences(tr_normalize(upper), max_sentences=3)

    if disp_motif:
        chain = str(disp_motif.get("value") or "")
        extra_line = str(out.get("extra_line") or "")
        if chain and chain not in extra_line:
            extra_line = f"{extra_line} Dispozitor akışı: {chain}."
            out["extra_line"] = cap_sentences(tr_normalize(extra_line), max_sentences=1)

    return out


def finalize_daily_lengths(card: Mapping[str, Any]) -> Dict[str, Any]:
    out = dict(card)
    daily = _THEME_BANK["modes"]["daily"]["length"]
    out["conflict"] = cap_sentences(str(out.get("conflict") or ""), max_sentences=int(daily["conflict_sentences"][1]))
    out["shadow"] = cap_sentences(str(out.get("shadow") or ""), max_sentences=int(daily["shadow_sentences"][1]))
    out["upper"] = cap_sentences(str(out.get("upper") or ""), max_sentences=int(daily["upper_sentences"][1]))
    out["extra_line"] = cap_sentences(str(out.get("extra_line") or ""), max_sentences=int(daily["extra_line_sentences"][1]))
    guidance = out.get("guidance") if isinstance(out.get("guidance"), list) else []
    watch = out.get("watch_out") if isinstance(out.get("watch_out"), list) else []
    out["guidance"] = _normalize_bullet_list(
        guidance,
        fallback=["Yaz tek cümle niyet.", "Çıkar taslak, sonra gönder.", "Bağla ritmi mini-rutine."],
        minimum=3,
    )[: int(daily["guidance_bullets"])]
    out["watch_out"] = _normalize_bullet_list(
        watch,
        fallback=["Açma aynı anda iki kanal.", "Sabitle önce niyeti, sonra hız ver."],
        minimum=2,
    )[: int(daily["watch_out_bullets"])]
    return out


def build_period_copy(
    *,
    selected_events: Sequence[Mapping[str, Any]],
    natal_snapshot: Mapping[str, Any] | None = None,
    dominant_house: int | None,
    dominant_planet: str,
    pressure: float,
    support: float,
    domains: Sequence[str],
) -> Dict[str, str]:
    houses = []
    for event in selected_events:
        houses_map = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
        house = _safe_int(houses_map.get("transit_in_natal_house"))
        if house:
            houses.append(house)
    house_counter = Counter(houses)
    main_house = dominant_house or (house_counter.most_common(1)[0][0] if house_counter else 3)
    house_pack = _THEME_BANK["houses"].get(main_house) or _THEME_BANK["houses"][3]
    scene = house_pack["scene"]
    motif = house_pack["motif"]
    domain_text = ", ".join(str(x) for x in domains[:2]) if domains else "zihin"

    if pressure >= support + 0.08:
        mode = "pressure"
    elif support >= pressure + 0.08:
        mode = "expansion"
    else:
        mode = "calibration"

    root_causes = build_root_causes(selected_events, natal_snapshot or {})
    primary = root_causes[0] if root_causes else {"key": "identity_spine", "evidence": []}
    secondary = root_causes[1] if len(root_causes) > 1 else {"key": "mind_axis_3_9", "evidence": []}

    p1 = _period_paragraph_for_root(primary, mode=mode, paragraph_idx=1, domain_text=domain_text)
    p2 = _period_paragraph_for_root(secondary, mode=mode, paragraph_idx=2, domain_text=domain_text)
    p3 = _period_transform_paragraph(
        root_causes=root_causes,
        mode=mode,
        main_house=main_house,
        scene=scene,
        motif=motif,
    )

    paragraphs = [p1, p2, p3]
    normalized_paragraphs: List[str] = []
    seen = set()
    for paragraph in paragraphs:
        cleaned = cap_sentences(tr_normalize(polish_collocations(paragraph)), max_sentences=4)
        key = " ".join(cleaned.lower().split())
        if not cleaned or key in seen:
            continue
        seen.add(key)
        normalized_paragraphs.append(cleaned)
    core_story = "\n\n".join(normalized_paragraphs[:3])
    core_story = _period_general_climate(core_story)
    core_story = humanize_tr_text(core_story, max_sentences=12)

    upper_lines = [
        "Bu dönemde nedeni fark ettiğinde adımlarını daha kolay netleştirirsin.",
        "Sürecini sadeleştirdikçe sonuçları daha az yorularak alırsın.",
        "Dönem sonunda sana iyi gelen ritmi daha kalıcı hale getirebilirsin.",
    ]
    if any(cause.get("key") == "mind_axis_3_9" for cause in root_causes):
        upper_lines.insert(1, "3/9 hattı hareketliyken öğrenme planını küçük adımlara bölmek işleri hızlandırır.")
    if any(cause.get("key") == "identity_spine" for cause in root_causes):
        upper_lines.insert(1, "Kimlik tarafı netleştikçe dış yorumlar seni daha az dağıtır.")
    upper = cap_sentences(" ".join(upper_lines[:5]), max_sentences=4)
    upper = humanize_tr_text(upper, max_sentences=4)
    return {"core_story": core_story, "upper_meaning": upper, "root_causes": root_causes}


def _period_general_climate(text: str) -> str:
    out = str(text or "").strip()
    if not out:
        return out
    replacements = (
        (r"\bana hat\b", "dönemin havası"),
        (r"\bkalibrasyon\b", "denge ayarı"),
        (r"\bgüncelleme\b", "değişim"),
        (r"\bnetlik ayarı\b", "netleşme"),
        (r"\byöntem güncellemesi\b", "ritim değişimi"),
    )
    paragraphs = [p.strip() for p in out.split("\n\n") if p.strip()]
    normalized: List[str] = []
    for paragraph in paragraphs:
        line = paragraph
        for pattern, dst in replacements:
            line = re.sub(pattern, dst, line, flags=re.IGNORECASE)
        normalized.append(line)
    if normalized and not normalized[0].lower().startswith("dönemin havası"):
        normalized[0] = f"Dönemin havası: {normalized[0]}"
    return "\n\n".join(normalized)


def build_root_causes(
    selected_events: Sequence[Mapping[str, Any]],
    natal_snapshot: Mapping[str, Any] | None,
) -> List[Dict[str, Any]]:
    events = [item for item in selected_events if isinstance(item, Mapping)]
    natal = natal_snapshot if isinstance(natal_snapshot, Mapping) else {}
    if not events:
        return []

    bodies = natal.get("bodies") if isinstance(natal.get("bodies"), list) else []
    first_house_natal = 0
    for body in bodies:
        if not isinstance(body, Mapping):
            continue
        if _safe_int(body.get("house")) == 1:
            first_house_natal += 1
    first_density = min(1.0, first_house_natal / 3.0)
    asc_present = 1.0 if isinstance(natal.get("angles"), Mapping) and natal.get("angles", {}).get("ASC") else 0.0

    angle_hits = 0
    outer_angle_hits = 0
    mind_hits = 0
    mirror_house_hits = 0
    mercury_chain_hits = 0
    uranus_mars_candidates: List[Mapping[str, Any]] = []
    evidence_map: Dict[str, List[str]] = {
        "identity_spine": [],
        "mind_axis_3_9": [],
        "mirror_axis_1_7": [],
        "method_shift_9_virgo": [],
    }
    evidence_id_map: Dict[str, List[str]] = {
        "identity_spine": [],
        "mind_axis_3_9": [],
        "mirror_axis_1_7": [],
        "method_shift_9_virgo": [],
    }

    natal_mars_house, natal_mars_sign = _natal_mars_signature(natal)
    for event in events:
        houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
        transit_house = _safe_int(houses.get("transit_in_natal_house"))
        target_house = _safe_int(houses.get("natal_point_house"))
        natal_point = str(event.get("natal_point") or "").upper()
        body = str(event.get("transit_body") or "").lower()
        aspect = str(event.get("aspect") or "").lower()

        is_angle = natal_point in {"ASC", "DSC", "MC", "IC"}
        event_id = str(event.get("event_id") or "").strip()
        if is_angle or transit_house in {1, 4, 7, 10}:
            angle_hits += 1
            evidence_map["identity_spine"].append(_event_evidence(event))
            if event_id:
                evidence_id_map["identity_spine"].append(event_id)
        if (is_angle or transit_house == 1) and body in {"neptune", "pluto", "saturn", "uranus"}:
            outer_angle_hits += 1
            evidence_map["identity_spine"].append(_event_evidence(event))
            if event_id:
                evidence_id_map["identity_spine"].append(event_id)

        if transit_house in {3, 9} or target_house in {3, 9}:
            mind_hits += 1
            evidence_map["mind_axis_3_9"].append(_event_evidence(event))
            if event_id:
                evidence_id_map["mind_axis_3_9"].append(event_id)

        if (natal_point in {"ASC", "DSC"}) or (transit_house in {1, 7} and target_house in {1, 7}):
            evidence_map["mirror_axis_1_7"].append(_event_evidence(event))
            if event_id:
                evidence_id_map["mirror_axis_1_7"].append(event_id)
        if transit_house in {1, 7} or target_house in {1, 7}:
            mirror_house_hits += 1

        if _has_mercury_dispositor(event):
            mercury_chain_hits += 1
            evidence_map["mind_axis_3_9"].append(_event_evidence(event))
            if event_id:
                evidence_id_map["mind_axis_3_9"].append(event_id)

        if body == "uranus" and aspect in {"trine", "sextile", "conjunction", "opposition", "square"}:
            target_planet = str(event.get("natal_point") or "").strip().lower()
            if target_planet == "mars":
                uranus_mars_candidates.append(event)

    total = max(1, len(events))
    identity_score = (
        0.20 * first_density
        + 0.30 * asc_present
        + 0.25 * min(1.0, angle_hits / total * 1.8)
        + 0.25 * min(1.0, outer_angle_hits / total * 2.4)
    )

    mind_score = (
        0.75 * min(1.0, mind_hits / total * 1.8)
        + 0.25 * min(1.0, mercury_chain_hits / max(1, total // 2 or 1))
    )

    mirror_score = (
        0.55 * min(1.0, len(evidence_map["mirror_axis_1_7"]) / total * 2.0)
        + 0.45 * min(1.0, mirror_house_hits / total * 1.8)
    )

    method_score = 0.0
    if uranus_mars_candidates:
        has_9th = False
        has_virgo = False
        for event in uranus_mars_candidates:
            houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
            event_target_house = _safe_int(houses.get("natal_point_house"))
            if event_target_house == 9 or natal_mars_house == 9:
                has_9th = True
            event_sign = _event_target_sign(event)
            if event_sign == "virgo" or natal_mars_sign == "virgo":
                has_virgo = True
            evidence_map["method_shift_9_virgo"].append(_event_evidence(event, suffix="(9th Virgo)"))
            event_id = str(event.get("event_id") or "").strip()
            if event_id:
                evidence_id_map["method_shift_9_virgo"].append(event_id)
        method_score = 0.40
        if has_9th:
            method_score += 0.30
        if has_virgo:
            method_score += 0.30
        method_score = min(1.0, method_score)

    candidates: List[Dict[str, Any]] = [
        {
            "key": "identity_spine",
            "score": round(identity_score, 3),
            "evidence": _dedupe_strings(evidence_map["identity_spine"])[:3],
            "evidence_ids": _dedupe_strings(evidence_id_map["identity_spine"])[:3],
        },
        {
            "key": "mind_axis_3_9",
            "score": round(mind_score, 3),
            "evidence": _dedupe_strings(evidence_map["mind_axis_3_9"])[:3],
            "evidence_ids": _dedupe_strings(evidence_id_map["mind_axis_3_9"])[:3],
        },
        {
            "key": "mirror_axis_1_7",
            "score": round(mirror_score, 3),
            "evidence": _dedupe_strings(evidence_map["mirror_axis_1_7"])[:3],
            "evidence_ids": _dedupe_strings(evidence_id_map["mirror_axis_1_7"])[:3],
        },
    ]
    if method_score > 0:
        candidates.append(
            {
                "key": "method_shift_9_virgo",
                "score": round(method_score, 3),
                "evidence": _dedupe_strings(evidence_map["method_shift_9_virgo"])[:3],
                "evidence_ids": _dedupe_strings(evidence_id_map["method_shift_9_virgo"])[:3],
            }
        )

    filtered = [item for item in candidates if float(item.get("score") or 0.0) >= 0.35]
    filtered.sort(key=lambda item: (-float(item.get("score") or 0.0), str(item.get("key") or "")))
    return filtered


def _period_paragraph_for_root(
    cause: Mapping[str, Any],
    *,
    mode: str,
    paragraph_idx: int,
    domain_text: str,
) -> str:
    key = str(cause.get("key") or "")
    evidence = ", ".join(_dedupe_strings(cause.get("evidence") or [])[:2]) or "seçili transitler"
    if paragraph_idx == 1:
        if key == "identity_spine":
            return f"Bu dönem kimlik omurgasına dokunuyor çünkü açıların ağırlığı ASC/1.ev eksenine biniyor: {evidence}."
        if key == "mind_axis_3_9":
            return f"Bu dönem zihinsel omurgayı zorluyor çünkü 3/9 hattı tekrar eden şekilde aktif: {evidence}."
        if key == "mirror_axis_1_7":
            return f"Bu dönem ilişki aynasını büyütüyor çünkü 1/7 ekseni aynı anda uyarılıyor: {evidence}."
        if key == "method_shift_9_virgo":
            return f"Bu dönem yöntemi değiştiriyor çünkü 9.ev Başak hattı Uranüs etkisiyle açılıyor: {evidence}."
    if key == "mind_axis_3_9":
        return f"Zihin ve ifade hattı bu yüzden devrede; {domain_text} tarafında karar kalitesi kullanılan metoda bağlı: {evidence}."
    if key == "mirror_axis_1_7":
        return f"İlişki aynası bu yüzden güçlü; sınır ve karşılıklılık dili güncellendikçe gerilim düşer: {evidence}."
    if key == "identity_spine":
        return f"Kimlik hattı ikinci dalga olarak çalışıyor; dış geri bildirim iç omurgayı kalibre ediyor: {evidence}."
    if key == "method_shift_9_virgo":
        return f"Yöntem tarafı bu yüzden kritik; dağınık hız yerine düzenli deneme ritmi kazandırır: {evidence}."
    if mode == "pressure":
        return "İkinci hat baskıyı davranış modeline çevirme testinde; netlik tepkiden önce gelince dönem yumuşar."
    if mode == "expansion":
        return "İkinci hat fırsatı kalıcı kas haline getirme testinde; seçici odak akışı büyütür."
    return "İkinci hat kalibrasyon testi; hız ve çerçeve birlikte güncellendiğinde sonuç temizleşir."


def _period_transform_paragraph(
    *,
    root_causes: Sequence[Mapping[str, Any]],
    mode: str,
    main_house: int,
    scene: str,
    motif: str,
) -> str:
    keys = {str(item.get("key") or "") for item in root_causes}
    if "method_shift_9_virgo" in keys:
        return (
            f"Bu dönem 'nasıl'ı değiştiriyor: {main_house}. Evde {scene} sahnesi yöntem ve ritim güncellemesi istiyor. "
            "Üst potansiyel, mikro sprintleri ölçümle birleştirip kalıcı öğrenme ivmesine çevirmek."
        )
    if "identity_spine" in keys and "mirror_axis_1_7" in keys:
        return (
            f"Bu dönem 'nasıl'ı sınır dili üzerinden değiştiriyor; tema {motif} olsa da ana kazanç rol netliğinde. "
            "Üst potansiyel, ilişki aynasını kullanıp iç referansı daha sakin ve tutarlı kurmak."
        )
    if mode == "pressure":
        return (
            f"Bu dönem 'nasıl'ı çerçeve disipliniyle değiştiriyor; {main_house}. Evde {scene} hattı tekrar isteyen bir laboratuvar. "
            "Üst potansiyel, baskıyı tek kanallı yönteme çevirerek güvenilir bir ritim üretmek."
        )
    if mode == "expansion":
        return (
            f"Bu dönem 'nasıl'ı fırsat seçimiyle değiştiriyor; {main_house}. Evde {scene} hattı dağılmadan büyümeyi çağırıyor. "
            "Üst potansiyel, küçük ama tekrarlı hamlelerle verimi görünür biçimde artırmak."
        )
    return (
        f"Bu dönem 'nasıl'ı kalibrasyonla değiştiriyor; {main_house}. Evde {scene} ve tema {motif} birlikte ince ayar istiyor. "
        "Üst potansiyel, tempoyu sadeleştirip daha net bir iç ritim kurmak."
    )


def _append_unique_sentence(base: str, addon: str) -> str:
    left = str(base or "").strip()
    right = str(addon or "").strip()
    if not right:
        return left
    if not left:
        return right
    left_norm = " ".join(left.lower().split())
    right_norm = " ".join(right.lower().split())
    if right_norm in left_norm:
        return left
    return f"{left} {right}".strip()


def _merge_unique_list(base: Sequence[str], addon: Sequence[str], *, cap: int) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in list(base) + list(addon):
        raw = str(item or "").strip()
        if not raw:
            continue
        key = " ".join(raw.lower().split())
        if key in seen:
            continue
        seen.add(key)
        out.append(raw)
        if len(out) >= cap:
            break
    return out


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _has_any(text: str, keywords: Sequence[str]) -> bool:
    haystack = str(text or "").lower()
    return any(keyword in haystack for keyword in keywords)


def _list_has_any(items: Sequence[Any], keywords: Sequence[str]) -> bool:
    for item in items:
        if _has_any(str(item or ""), keywords):
            return True
    return False


def _normalize_bullet(text: Any, max_words: int = 14) -> str:
    value = cap_sentences(polish_collocations(tr_normalize(str(text or ""))), max_sentences=1)
    if not value:
        return ""
    value = re.sub(r"^\s*\d+\.?\s*ev\b[^:;,.!?-]*[:\-]?\s*", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^\s*[^:]{1,24}:\s*", "", value).strip()
    words = value.split()
    if not words:
        return ""
    if len(words) > max_words:
        words = words[:max_words]
        value = " ".join(words).rstrip(".,;:!?") + "."
    first = words[0].lower().strip(".,;:!?") if words else ""
    compact = re.sub(r"[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ ]", "", value).strip().lower()
    if not compact or re.fullmatch(r"[\d. ]+", compact):
        return ""
    if len(words) <= 2:
        return ""

    if first not in _VERB_STARTS:
        lowered = value.lower()
        if "yaz" in lowered:
            value = f"Yaz {value[0].lower() + value[1:] if len(value) > 1 else value.lower()}"
        elif "gonder" in lowered or "gönder" in lowered:
            value = "Çıkar taslak, sonra gönder."
        elif "acma" in lowered or "açma" in lowered:
            value = "Açma aynı anda iki kanal."
        else:
            return ""
    value = " ".join(value.split()).strip()
    if value and value[-1] not in ".!?":
        value += "."
    return value


def _normalize_bullet_list(items: Sequence[Any], *, fallback: Sequence[str], minimum: int) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        normalized = _normalize_bullet(item)
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        out.append(normalized)
    for item in fallback:
        if len(out) >= minimum:
            break
        normalized = _normalize_bullet(item)
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        out.append(normalized)
    return out


def _event_evidence(event: Mapping[str, Any], *, suffix: str = "") -> str:
    body = str(event.get("transit_body") or "").strip().title()
    aspect = str(event.get("aspect") or "").strip().lower()
    point = str(event.get("natal_point") or "").strip().upper()
    if point and point not in {"ASC", "DSC", "MC", "IC"}:
        point = point.title()
    if not body:
        return ""
    chunk = f"{body} {aspect} {point}".strip()
    if suffix:
        chunk = f"{chunk} {suffix}".strip()
    return chunk


def _natal_mars_signature(natal_snapshot: Mapping[str, Any]) -> tuple[int | None, str]:
    bodies = natal_snapshot.get("bodies") if isinstance(natal_snapshot.get("bodies"), list) else []
    for body in bodies:
        if not isinstance(body, Mapping):
            continue
        if str(body.get("body") or "").strip().lower() != "mars":
            continue
        house = _safe_int(body.get("house"))
        sign = str(body.get("sign") or "").strip().lower()
        return house, sign
    return None, ""


def _event_target_sign(event: Mapping[str, Any]) -> str:
    ctx = event.get("natal_context_pack") if isinstance(event.get("natal_context_pack"), Mapping) else {}
    target = ctx.get("target") if isinstance(ctx.get("target"), Mapping) else {}
    sign = str(target.get("sign") or "").strip().lower()
    if sign:
        return sign
    return ""


def _has_mercury_dispositor(event: Mapping[str, Any]) -> bool:
    context = event.get("natal_context_pack") if isinstance(event.get("natal_context_pack"), Mapping) else {}
    disp = context.get("dispositor") if isinstance(context.get("dispositor"), Mapping) else {}
    planet = str(disp.get("planet") or "").strip().lower()
    if planet == "mercury":
        return True
    connected = event.get("connected_points") if isinstance(event.get("connected_points"), list) else []
    for item in connected:
        if not isinstance(item, Mapping):
            continue
        value = str(item.get("value") or "").strip().lower()
        kind = str(item.get("kind") or "").strip().lower()
        if kind == "dispositor_chain" and "mercury" in value:
            return True
    return False


def _dedupe_strings(values: Sequence[Any]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in values:
        text = str(item or "").strip()
        if not text:
            continue
        key = " ".join(text.lower().split())
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return out


def _dedupe_section_overlap(card: Mapping[str, Any]) -> Dict[str, Any]:
    out = dict(card)
    seen: set[str] = set()

    def _strip_sentences(text: str) -> str:
        parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", str(text or "").strip()) if p.strip()]
        cleaned: List[str] = []
        for part in parts:
            lowered = " ".join(part.lower().split())
            if re.match(r"^\s*Sahne\s", part, flags=re.IGNORECASE):
                continue
            if " sahne " in f" {lowered} ":
                continue
            if "vurduğu yer" in lowered or "vurdugu yer" in lowered:
                continue
            key = " ".join(part.lower().split())
            if not key or key in seen:
                continue
            seen.add(key)
            cleaned.append(part)
        merged = " ".join(cleaned).strip()
        if merged and merged[-1] not in ".!?":
            merged += "."
        return merged

    for field in (
        "teaser",
        "why_now",
        "conflict",
        "shadow",
        "upper",
        "headline",
        "big_picture",
        "mechanism",
        "upper_meaning",
    ):
        if field in out:
            out[field] = _strip_sentences(out.get(field) or "")

    def _norm(value: str) -> str:
        text = str(value or "").strip().lower()
        text = re.sub(r"\s+", " ", text)
        return text

    def _sim(a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, _norm(a), _norm(b)).ratio()

    def _drop_if_similar(primary: str, secondary: str, threshold: float = 0.8) -> None:
        left = str(out.get(primary) or "").strip()
        right = str(out.get(secondary) or "").strip()
        if _sim(left, right) >= threshold:
            out[secondary] = ""

    _drop_if_similar("headline", "big_picture", 0.8)
    _drop_if_similar("headline", "upper", 0.8)
    _drop_if_similar("big_picture", "mechanism", 0.8)
    _drop_if_similar("teaser", "why_now", 0.8)
    _drop_if_similar("teaser", "upper", 0.8)
    _drop_if_similar("why_now", "conflict", 0.8)
    return out
