from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import hashlib


ASPECT_POLARITY_DEFAULT = {
    "conjunction": "neutral",
    "opposition": "hard",
    "square": "hard",
    "trine": "soft",
    "sextile": "soft",
}

# Basit domain/tag seti (V1)
TAG_DOMAIN_TEXT_TR = {
    "self": "benlik",
    "relationships": "ilişkiler",
    "career": "kariyer",
    "home": "ev/aile",
    "inner": "iç dünya",
    "mind": "zihin/iletişim",
}

PHASE_TR = {
    "applying": "yaklaşıyor",
    "exactish": "en yoğun",
    "separating": "çözülüyor",
}


@dataclass(frozen=True)
class InterpretConfig:
    lang: str = "tr"
    content_version: str = "tr.v1"
    voice: str = "you"  # "you" => sen dili, "neutral" => bu dönem dili
    # deterministik varyasyon için
    variation_mod: int = 3


def stable_hash_to_int(s: str) -> int:
    h = hashlib.sha1(s.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def event_id_default(event: Dict[str, Any]) -> str:
    # input event_id yoksa deterministik üret
    basis = "|".join(
        [
            str(event.get("transit_body", "")),
            str(event.get("aspect", "")),
            str(event.get("natal_point", "")),
            str(event.get("scope", "")),
        ]
    )
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()


def resolve_content_key(event: Dict[str, Any]) -> List[str]:
    """
    En spesifikten en genel fallback’e:
      1) Transit.Aspect.Natal
      2) Transit.Aspect.ANY
      3) ANY.Aspect.Natal
      4) ANY.Aspect.ANY
      5) aspect_polarity.(hard|soft|neutral).ANY
      6) generic
    """
    t = str(event.get("transit_body") or "ANY")
    a = str(event.get("aspect") or "ANY")
    n = str(event.get("natal_point") or "ANY")
    p = str(event.get("polarity") or ASPECT_POLARITY_DEFAULT.get(a, "neutral"))

    keys = [
        f"{t}.{a}.{n}",
        f"{t}.{a}.ANY",
        f"ANY.{a}.{n}",
        f"ANY.{a}.ANY",
        f"polarity.{p}.ANY",
        "generic",
    ]
    return keys


def choose_variant(event: Dict[str, Any], cfg: InterpretConfig, max_len: int) -> int:
    # deterministik: event_id hash % max_len
    eid = str(event.get("event_id") or event_id_default(event))
    v = stable_hash_to_int(eid) % max_len
    # İstersen mod ile sınırla (örn 3 varyasyon)
    if cfg.variation_mod > 0:
        v = v % min(cfg.variation_mod, max_len)
    return v


def voice_wrap(text: str, cfg: InterpretConfig) -> str:
    if cfg.voice == "neutral":
        # Basit dönüşüm: "sen" dilini yumuşat
        # Not: V1 için minimal. İstersen daha kapsamlı NLP sonra.
        text = text.replace("hissedebilirsin", "hissedilebilir")
        text = text.replace("isteyebilirsin", "isteyebilirsin")  # aynı kalsın
        text = text.replace("sen", "")
        return " ".join(text.split())
    return text


def time_status_tr(event: Dict[str, Any]) -> str:
    phase = str(event.get("phase") or "")
    return PHASE_TR.get(phase, "devam ediyor")


def themes_from_tags(tags: List[str]) -> List[str]:
    # V1: tags -> themes birebir
    # UI yokken bile raporda kullanılır.
    themes = []
    for t in tags or []:
        if t in TAG_DOMAIN_TEXT_TR:
            themes.append(t)
    return themes


def compute_interp_confidence(event: Dict[str, Any], used_key: str) -> float:
    """
    Basit güven:
      - strength yüksekse artar
      - orb küçükse artar
      - spesifik key kullanıldıysa artar
    """
    strength = float(event.get("strength") or 0.0)
    orb = float(event.get("orb_deg") or event.get("orb") or 99.0)

    base = 0.35 + 0.55 * clamp01(strength)
    if orb <= 0.5:
        base += 0.10
    elif orb <= 1.5:
        base += 0.05

    if used_key not in ("generic", "polarity.hard.ANY", "polarity.soft.ANY", "polarity.neutral.ANY"):
        base += 0.05

    return clamp01(base)


def interpret_item(
    event: Dict[str, Any],
    content_store: Dict[str, Any],
    cfg: InterpretConfig,
) -> Dict[str, Any]:
    """
    event: display.items benzeri normalized event
    content_store: { "version": "...", "entries": { key: { ... } } }
    """
    entries = (content_store or {}).get("entries") or {}
    keys = resolve_content_key(event)

    used_key = "generic"
    entry = entries.get("generic") or {}

    for k in keys:
        if k in entries:
            used_key = k
            entry = entries[k]
            break

    # Varyasyon seçimi
    # headline/summary/do/watch alanları list veya string olabilir
    headline_pool = entry.get("headline") or ""
    summary_pool = entry.get("summary") or ""
    do_pool = entry.get("do") or []
    watch_pool = entry.get("watch") or []

    def pick(pool: Any) -> Any:
        if isinstance(pool, list):
            if not pool:
                return ""
            idx = choose_variant(event, cfg, len(pool))
            return pool[idx]
        return pool

    headline = pick(headline_pool) or fallback_headline(event)
    summary = pick(summary_pool) or fallback_summary(event)
    do_item = pick(do_pool)
    watch_item = pick(watch_pool)

    do_list: List[str] = []
    if isinstance(do_item, list):
        do_list = do_item
    elif isinstance(do_item, str) and do_item.strip():
        do_list = [do_item.strip()]

    watch_list: List[str] = []
    if isinstance(watch_item, list):
        watch_list = watch_item
    elif isinstance(watch_item, str) and watch_item.strip():
        watch_list = [watch_item.strip()]

    # Zenginleştirme: phase, themes, vb.
    tags = event.get("tags") or []
    themes = themes_from_tags(tags)

    # Voice
    headline = voice_wrap(headline, cfg)
    summary = voice_wrap(summary, cfg)
    do_list = [voice_wrap(x, cfg) for x in do_list]
    watch_list = [voice_wrap(x, cfg) for x in watch_list]

    return {
        "headline": headline,
        "summary": summary,
        "do": do_list,
        "watch": watch_list,
        "time_status": time_status_tr(event),
        "themes": themes,
        "confidence": compute_interp_confidence(event, used_key),
        "content_ref": {
            "version": cfg.content_version,
            "key": used_key,
        },
    }


def fallback_headline(event: Dict[str, Any]) -> str:
    t = str(event.get("transit_body") or "")
    a = str(event.get("aspect") or "")
    n = str(event.get("natal_point") or "")
    p = str(event.get("polarity") or "")
    if p == "hard":
        return f"{t} → {n}: zorlayıcı temas"
    if p == "soft":
        return f"{t} → {n}: destekleyici temas"
    return f"{t} → {n}: belirgin bir vurgu"


def fallback_summary(event: Dict[str, Any]) -> str:
    p = str(event.get("polarity") or "")
    phase = time_status_tr(event)
    if p == "hard":
        return f"Bu etki {phase}; sınır, baskı veya yön değiştirme ihtiyacı doğurabilir."
    if p == "soft":
        return f"Bu etki {phase}; akışı kolaylaştıran destek ve fırsat hissi verebilir."
    return f"Bu etki {phase}; dikkatin belirli bir temada toplanmasına neden olabilir."


def interpret_items(
    items: List[Dict[str, Any]],
    content_store: Dict[str, Any],
    cfg: Optional[InterpretConfig] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    cfg = cfg or InterpretConfig()

    out: List[Dict[str, Any]] = []
    theme_counts: Dict[str, float] = {}
    top_drivers: List[str] = []

    # İlk 5 item’i sürücü gibi say (V1). İstersen featured’den de beslersin.
    for i, it in enumerate(items):
        if not it.get("event_id"):
            it["event_id"] = event_id_default(it)

        interp = interpret_item(it, content_store, cfg)
        it2 = dict(it)
        it2["interpretation"] = interp
        out.append(it2)

        # Tema skor: strength ile ağırlıkla
        strength = float(it.get("strength") or 0.0)
        for th in interp.get("themes") or []:
            theme_counts[th] = theme_counts.get(th, 0.0) + strength

        if i < 5:
            top_drivers.append(str(it2["event_id"]))

    main_theme = None
    if theme_counts:
        main_theme = sorted(theme_counts.items(), key=lambda kv: kv[1], reverse=True)[0][0]

    # One-liner
    if main_theme:
        one_liner = f"Bu dönemde {TAG_DOMAIN_TEXT_TR.get(main_theme, main_theme)} teması daha görünür."
    else:
        one_liner = "Bu dönemde birkaç tema aynı anda hareketli görünüyor."

    summary = {
        "main_theme": main_theme,
        "one_liner": one_liner,
        "top_drivers": top_drivers,
        "theme_scores": theme_counts,
    }
    return out, summary
