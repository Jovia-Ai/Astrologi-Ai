from __future__ import annotations

import re
from typing import Any, Mapping

from app.narrative.gold_natal_tone import NATAL_FORBIDDEN_LEXICON
from app.narrative.humanize_tr import (
    cleanup_duplicate_sentences,
    cleanup_tr_punctuation,
    humanize_tr_text,
    sentence_safe_clamp,
    split_tr_sentences,
)
from app.synastry.narrative.signature_catalog_tr_synastry import (
    BUNDLE_MECHANISM_COPY_TR,
    DOMAIN_CHIP_TR,
    DOMAIN_LABEL_TR,
    DOMAIN_ROOM_TR,
    MODE_COPY_TR,
    SHARED_THEME_COPY_TR,
    SUPPORT_COPY_TR,
    TENSION_COPY_TR,
)


def _safe_key(value: Any) -> str:
    return str(value or "")


def domain_label(domain: Any) -> str:
    return DOMAIN_LABEL_TR.get(_safe_key(domain), _safe_key(domain).replace("_", " "))


def domain_room(domain: Any) -> str:
    return DOMAIN_ROOM_TR.get(_safe_key(domain), f"{domain_label(domain)} odası")


def domain_chip(domain: Any) -> str:
    return DOMAIN_CHIP_TR.get(_safe_key(domain), domain_label(domain))


def mode_label(mode: Any) -> str:
    return MODE_COPY_TR.get(_safe_key(mode), MODE_COPY_TR["mixed_activation"])["label"]


def mode_line(mode: Any) -> str:
    return MODE_COPY_TR.get(_safe_key(mode), MODE_COPY_TR["mixed_activation"])["line"]


def mode_chip(mode: Any) -> str:
    return MODE_COPY_TR.get(_safe_key(mode), MODE_COPY_TR["mixed_activation"])["chip"]


def shared_theme_line(theme: Any) -> str:
    return SHARED_THEME_COPY_TR.get(_safe_key(theme), SHARED_THEME_COPY_TR["mixed_activation_field"])["line"]


def shared_theme_chip(theme: Any) -> str:
    return SHARED_THEME_COPY_TR.get(_safe_key(theme), SHARED_THEME_COPY_TR["mixed_activation_field"])["chip"]


def support_line(signature: Any) -> str:
    return SUPPORT_COPY_TR.get(
        _safe_key(signature),
        SUPPORT_COPY_TR["activation_without_clear_soft_buffer"],
    )["line"]


def support_chip(signature: Any) -> str:
    return SUPPORT_COPY_TR.get(
        _safe_key(signature),
        SUPPORT_COPY_TR["activation_without_clear_soft_buffer"],
    )["chip"]


def tension_line(signature: Any) -> str:
    return TENSION_COPY_TR.get(_safe_key(signature), TENSION_COPY_TR["manageable_tension"])["line"]


def tension_chip(signature: Any) -> str:
    return TENSION_COPY_TR.get(_safe_key(signature), TENSION_COPY_TR["manageable_tension"])["chip"]


def bundle_mechanism(kind: Any) -> str:
    return BUNDLE_MECHANISM_COPY_TR.get(_safe_key(kind), "")


def sustainability_band(value: Any) -> str:
    score = float(value or 0.0)
    if score >= 0.68:
        return "yüksek"
    if score >= 0.48:
        return "orta"
    return "kırılgan"


def asymmetry_phrase(value: Any) -> str:
    score = float(value or 0.0)
    if score >= 0.45:
        return "belirgin yön farkı taşıyor"
    if score >= 0.24:
        return "hafif değil, görünür bir yön farkı taşıyor"
    return "büyük ölçüde karşılıklı akıyor"


def mutuality_phrase(value: Any) -> str:
    score = float(value or 0.0)
    if score >= 0.72:
        return "karşılıklılık güçlü"
    if score >= 0.52:
        return "karşılıklılık orta seviyede"
    return "karşılıklılık dalgalı"


def comfort_trigger_snapshot(comfort: Any, trigger: Any) -> str:
    comfort_value = float(comfort or 0.0)
    trigger_value = float(trigger or 0.0)
    if comfort_value >= 0.62 and trigger_value >= 0.55:
        return "hem tanıdık hem de yorucu"
    if comfort_value >= 0.62:
        return "daha tanıdık ve daha yerleşik"
    if trigger_value >= 0.60:
        return "daha yüklü ve daha regülasyon isteyen"
    if comfort_value >= 0.52 and trigger_value < 0.48:
        return "daha dengeli ve daha yönetilebilir"
    return "bir yandan açık, bir yandan temkinli"


_SYN_FIELD_LIMITS = {
    "headline": (72, 1),
    "teaser": (190, 2),
    "body": (520, 4),
    "micro": (170, 1),
}

_SYN_MICRO_FALLBACKS = {
    "what_you_open_in_them": "Senden giden etkinin onda önce güven ihtiyacına dokunması burada belirgin.",
    "what_they_open_in_you": "Bu temasın sende kısa sürede daha derin bir yere inmesi çok tipik.",
    "main_rooms_of_relationship": "Aynı bağın ikinizde de farklı merkezlerden yaşanması burada çok belirgin.",
    "growth_axis": "Yakınlaştıran şeyle zorlayan şey burada aynı çizgide duruyor.",
    "comfort_vs_trigger": "Rahatlatan tarafla yoran taraf iki kişide aynı yerde toplanmıyor.",
    "long_term_shape": "Karşılık var; ama ilişkinin ağırlığı iki tarafta aynı hızda birikmiyor.",
}

_SYN_TEASER_FALLBACKS = {
    "what_you_open_in_them": "Senden giden etki onda önce güven ve yerleşme ihtiyacını uyandırıyor.",
    "what_they_open_in_you": "Ondan gelen etki sende yüzeyde kalmayıp daha derin bir yere iniyor.",
    "main_rooms_of_relationship": "Bu ilişki ikinizde de aynı kapıyı açmıyor.",
    "growth_axis": "Bu bağın yakınlaştıran tarafı kadar zorlayan tarafı da güçlü.",
    "comfort_vs_trigger": "Tanıdıklık ve yük iki tarafta aynı şekilde dağılmıyor.",
    "long_term_shape": "Uzun vadede bu bağı yalnız çekim değil, taşıma kapasitesi belirliyor.",
}

_SYN_CHIP_REWRITES = {
    "tanıdık yoğunluk": "tanıdık yoğunluk",
    "gelişim baskısı": "gelişim",
    "ham etki": "yoğun etki",
    "baskı ve yoğunluk": "baskı ve yoğunluk",
}

_SYN_STOPWORDS = {
    "ve",
    "ile",
    "bir",
    "bu",
    "da",
    "de",
    "çok",
    "daha",
    "gibi",
    "ama",
    "ise",
    "için",
    "aynı",
    "olan",
    "oluyor",
    "olduğunu",
    "burada",
    "tarafta",
    "ilişki",
    "bağ",
}


def _text_key(text: str) -> str:
    key = re.sub(r"[^a-z0-9çğıöşü]+", " ", str(text or "").lower())
    return re.sub(r"\s+", " ", key).strip()


def _semantic_tokens(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", str(text or "").lower())
    return {token for token in tokens if len(token) >= 3 and token not in _SYN_STOPWORDS}


def _semantic_overlap(a: str, b: str) -> float:
    left = _semantic_tokens(a)
    right = _semantic_tokens(b)
    if not left or not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def _is_near_duplicate(a: str, b: str) -> bool:
    left = _text_key(a)
    right = _text_key(b)
    if not left or not right:
        return False
    if left == right or left in right or right in left:
        return True
    return _semantic_overlap(a, b) >= 0.68


def _ensure_sentence(text: str) -> str:
    value = cleanup_tr_punctuation(text)
    if not value:
        return ""
    return value if value[-1] in ".!?" else f"{value}."


def _capitalize_initial(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    first = value[:1]
    return {"i": "İ", "ı": "I"}.get(first, first.upper()) + value[1:]


def _rewrite_synastry_sentence(sentence: str, *, field: str, block_id: str) -> str:
    value = cleanup_tr_punctuation(sentence)
    if not value:
        return ""

    replacements = (
        (r"\baktivasyon\b", "etki"),
        (r"\btampon\b", "dengeleyen alan"),
        (r"\btek kanallı\b", "tek bir hatta"),
        (r"\balt tonunu belirgin biçimde etkiliyor\b", "tonunu sessizce belirliyor"),
        (r"\byalnızca ilk çekimi değil\b", "ilk anda görünen çekimin ötesinde"),
        (r"\bArka planda\b", "İçerde"),
        (r"\bBu bağ ikinizde aynı yerde çalışmıyor\b", "Aynı temas ikinizde de aynı kapıyı açmıyor"),
        (
            r"\bBu ilişki sende hem tanıdık hem de yorucu bir iz bırakıyor\b",
            "Bu ilişki sende hem yakın hem de ağır bir iz bırakıyor",
        ),
        (
            r"\bKarşı tarafta ise deneyim\b",
            "Karşı tarafta bu deneyim",
        ),
        (
            r"\bÇekim tek başına değil, bağın iç mimarisi ile çalışıyor\b",
            "Bu ilişki yalnız çekimle değil, taşıdığı iç düzenle şekilleniyor",
        ),
        (
            r"\bArka planda ([^.]*) hissi de bu bağı daha görünür kılıyor\b",
            r"\1 duygusu da bu ilişkinin arka planında kendini hissettiriyor",
        ),
        (
            r"\b([A-Za-zçğıöşüÇĞİÖŞÜ ]+) da bu alanın alt tonunu belirgin biçimde etkiliyor\b",
            r"\1 da bu alanın tonunu sessizce belirliyor",
        ),
    )
    for pattern, replacement in replacements:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)

    if field == "micro":
        lowered = value.lower()
        if any(token in lowered for token in ("gerekir", "öneri", "en iyi", "ideal", "tampon", "aktivasyon")):
            return _SYN_MICRO_FALLBACKS.get(block_id, value)
        if any(token in lowered for token in NATAL_FORBIDDEN_LEXICON):
            return _SYN_MICRO_FALLBACKS.get(block_id, value)

    return _capitalize_initial(value)


def _vary_synastry_starters(sentences: list[str]) -> list[str]:
    out: list[str] = []
    counts: dict[str, int] = {}
    for sentence in sentences:
        value = sentence.strip()
        if not value:
            continue
        starter = " ".join(value.split()[:3]).lower()
        counts[starter] = counts.get(starter, 0) + 1
        if counts[starter] >= 2:
            value = re.sub(r"^Senden giden etki\b", "Bu temas", value)
            value = re.sub(r"^Ondan gelen etki\b", "Karşı taraftan gelen etki", value)
            value = re.sub(r"^Bu bağ\b", "Bu ilişki", value)
            value = re.sub(r"^İçerde\b", "Bunun altında", value)
        out.append(value.strip())
    return out


def naturalize_synastry_text(text: str, *, field: str, block_id: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""

    max_chars, max_sentences = _SYN_FIELD_LIMITS.get(field, (200, 2))
    out = humanize_tr_text(value, max_sentences=max_sentences)
    parts = split_tr_sentences(out)
    parts = [_rewrite_synastry_sentence(part, field=field, block_id=block_id) for part in parts]
    parts = _vary_synastry_starters([part for part in parts if part.strip()])
    out = cleanup_duplicate_sentences(" ".join(parts).strip())
    out = cleanup_tr_punctuation(out)

    if field == "headline":
        return re.sub(r"[.!?]+$", "", out).strip()
    if field == "micro":
        if not out or not any(marker in out.lower() for marker in (" tipik", " belirgin", " birikmiyor", " dokun", " iner", " yaşıyor")):
            out = _SYN_MICRO_FALLBACKS.get(block_id, out)
    out = sentence_safe_clamp(out, max_chars=max_chars, max_sentences=max_sentences)
    return _ensure_sentence(out) if out else ""


def clean_synastry_public_block(block: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(block)
    block_id = str(out.get("id") or "").strip()

    for field in ("headline", "teaser", "body", "micro"):
        raw = out.get(field)
        if isinstance(raw, str):
            out[field] = naturalize_synastry_text(raw, field=field, block_id=block_id)

    body = str(out.get("body") or "").strip()
    teaser = str(out.get("teaser") or "").strip()
    micro = str(out.get("micro") or "").strip()
    first_body = split_tr_sentences(body)[0] if body else ""

    if teaser and first_body and _is_near_duplicate(teaser, first_body):
        out["teaser"] = naturalize_synastry_text(_SYN_TEASER_FALLBACKS.get(block_id, teaser), field="teaser", block_id=block_id)
        teaser = str(out.get("teaser") or "").strip()

    if body:
        filtered: list[str] = []
        for sentence in split_tr_sentences(body):
            if any(_is_near_duplicate(sentence, prior) for prior in filtered):
                continue
            filtered.append(sentence)
        out["body"] = _ensure_sentence(
            sentence_safe_clamp(" ".join(filtered).strip(), max_chars=_SYN_FIELD_LIMITS["body"][0], max_sentences=_SYN_FIELD_LIMITS["body"][1])
        )
        body = str(out.get("body") or "").strip()
        first_body = split_tr_sentences(body)[0] if body else ""

    if micro and any(_is_near_duplicate(micro, candidate) for candidate in (teaser, body, first_body) if candidate):
        out["micro"] = naturalize_synastry_text(_SYN_MICRO_FALLBACKS.get(block_id, micro), field="micro", block_id=block_id)

    chips = out.get("chips")
    if isinstance(chips, list):
        normalized: list[str] = []
        seen: set[str] = set()
        for chip in chips:
            value = _SYN_CHIP_REWRITES.get(str(chip or "").strip(), str(chip or "").strip())
            value = cleanup_tr_punctuation(value).strip(" .")
            key = value.lower()
            if not value or key in seen:
                continue
            seen.add(key)
            normalized.append(value)
            if len(normalized) >= 3:
                break
        out["chips"] = normalized

    return out
