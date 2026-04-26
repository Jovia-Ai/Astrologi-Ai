from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Mapping, Sequence

from app.narrative.editorial_render_policy import (
    editorialize_micro,
    editorialize_teaser,
    opening_key,
    quality_issues,
)
from app.narrative.humanize_tr import cleanup_duplicate_sentences, humanize_tr_text


RENDER_MODES = ("A", "B", "C", "D")

MODE_LABELS_TR = {
    "A": "direct",
    "B": "observational",
    "C": "cinematic",
    "D": "intimate",
}


TITLE_FAMILIES_TR: Dict[str, List[str]] = {
    "identity_aura": [
        "Kendi çizgin",
        "Sende ilk hissedilen şey",
        "Dışarıdan ve içeriden",
        "Varlığının omurgası",
    ],
    "mind_voice": [
        "İç ritmin",
        "Karar verirken içinde ne oluyor",
        "Zihnin nasıl çalışıyor",
        "Cümlelerinin arkası",
    ],
    "drive_rhythm": [
        "Gücün en çok nerede belirginleşiyor",
        "Sende doğal çalışan şey",
        "Yetenek çizgin",
        "Kurucu tarafın",
    ],
    "love_depth": [
        "Yakınlık sende nasıl açılıyor",
        "Bağ kurma tarzın",
        "Sevginin derinleşme biçimi",
        "Kalbinin eşiği",
    ],
    "career_visibility": [
        "İşinin parlayan tarafı",
        "Toplumda nasıl iz bırakıyorsun",
        "Görünür olmadan önce",
        "Dışarıya verdiğin iz",
    ],
    "home_roots": [
        "Evde nasıl toparlanıyorsun",
        "Köklerinde çalışan şey",
        "İç güvenin en çok nerede kuruluyor",
        "İç alanının dili",
    ],
    "luck_creation": [
        "Şansın nasıl açılıyor",
        "Fırsatın aktığı yer",
        "Şansın en kolay nerede açılıyor",
        "Kapıların açıldığı yer",
    ],
}


_BODY_TEMPLATE_BY_MODE: Dict[str, str] = {
    "A": (
        "{copy.core} "
        "{copy.mechanism} "
        "Baskı yükseldiğinde {copy.shadow_lower}. "
        "Yerini bulduğunda {copy.gift_lower}."
    ),
    "B": (
        "İnsanlar sende önce şu çizgiyi okur: {copy.core_lower}. "
        "Gündelik hayatta bunun karşılığı şu: {copy.mechanism_lower}. "
        "Zorlandığında {copy.shadow_lower}. "
        "Güçlü halinde {copy.gift_lower}."
    ),
    "C": (
        "Bir ortama girdiğinde {copy.core_lower}. "
        "Perde arkasında ise {copy.mechanism_lower}. "
        "Gerilim yükseldiğinde {copy.shadow_lower}. "
        "Denge geldiğinde {copy.gift_lower}."
    ),
    "D": (
        "{copy.core} "
        "İç hattında {copy.mechanism_lower}. "
        "Kırılgan yerde {copy.shadow_lower}. "
        "Güven oluştuğunda {copy.gift_lower}."
    ),
}

BODY_TEMPLATES_TR: Dict[str, Dict[str, str]] = {
    block_id: dict(_BODY_TEMPLATE_BY_MODE) for block_id in TITLE_FAMILIES_TR
}


SOFT_ASTRO_HINTS_TR: Dict[str, List[str]] = {
    "identity_aura": [
        "Sende sağlam bir omurga ile özgünlük aynı anda hissediliyor.",
        "Sağlam duruşun ile farklı kalan tarafın aynı çizgide ilerliyor.",
        "Yön duygun ile büyük resmi birlikte taşıyan bir yanın var.",
    ],
    "mind_voice": [
        "Zihin tarafında netlik ile iç denge birlikte çalışıyor.",
        "Düşünürken cümle disiplinin ile sezgin aynı anda devreye giriyor.",
        "İfade ederken iç düzenin ile ton hassasiyetin birlikte hissediliyor.",
    ],
    "drive_rhythm": [
        "Sende yetenek, anlamı bir yapıya dönüştürebildiğin yerde parlıyor.",
        "Dağınık olanı toparlayıp sezgisel olanı anlaşılır hale getiren bir tarafın var.",
        "Bir şeyi yalnız hissetmekle kalmayıp ona biçim verme isteğin güçlü.",
    ],
    "love_depth": [
        "İlişkide güven ile derinlik aynı anda önem kazanıyor.",
        "Bağ kurarken yakınlık isteğinle korunma eşiğin birlikte çalışıyor.",
        "Yakınlıkta sıcaklık kadar güven zemini de belirleyici oluyor.",
    ],
    "career_visibility": [
        "Kariyerde görünürlük kadar kalite standardın da güçlü.",
        "Toplum önünde hem etkili hem de incelikli bir iz bırakıyorsun.",
        "İş tarafında görünür olma isteğinle hazırlık duygun birlikte çalışıyor.",
    ],
    "home_roots": [
        "İç güvenin en çok düzen ve toparlanma duygusuyla kuruluyor.",
        "Ev tarafında korunma duygunla ritim kurma ihtiyacın birlikte çalışıyor.",
        "Köklerinde güven duygusu ile iç toparlanma birlikte öne çıkıyor.",
    ],
    "luck_creation": [
        "Fırsatların en çok üretim ile anlam duygusu birleştiğinde açılıyor.",
        "Akışın, cesaretinle sezgin aynı anda devrede olduğunda hızlanıyor.",
        "Şansın görünür bir denemeyle büyüme arzusunu buluşturduğunda açılıyor.",
    ],
}


DEFAULT_PUBLIC_CHIPS_TR: Dict[str, List[str]] = {
    "identity_aura": ["Kendi Çizgin", "Özgün Yol", "Geniş Görüş"],
    "mind_voice": ["İç Ritim", "Net İfade", "İç Denge"],
    "drive_rhythm": ["Anlam Çizgisi", "Kurma Gücü", "Kurucu Zihin"],
    "love_depth": ["Derin Temas", "Güven Zemini", "Açılma Ritmi"],
    "career_visibility": ["Zarif Etki", "İz Bırak", "Ustalık"],
    "home_roots": ["İç Alan", "Toparlanma", "Güven Zemini"],
    "luck_creation": ["Yaratım", "Akış Hattı", "Açılma Eşiği"],
}


CHIP_REPLACEMENTS_TR = {
    "İtki–Fren": "İç Ritim",
    "Başlat–Rafine": "İnce Ayar",
    "Sistem": "Kurucu Akıl",
    "Sistem + Yenilik": "Yapı ve Yenilik",
    "Yapı Kur": "Kurma Gücü",
    "Netleştir": "Net Bakış",
    "Düzelt–Yenile": "İç Editör",
    "Kendin Hallet": "Kendi Dayanağın",
    "Uygula": "Hayata Geçirme",
    "Upgrade": "Yenilik",
    "Kalibrasyon": "İç Denge",
    "İç Ayar": "İç Denge",
    "Pattern": "Desen Görüsü",
    "Network": "Bağlantı Gücü",
    "Paylaş": "Görünür İz",
    "Başlat": "İlk Hamle",
    "Vitrin": "Görünür İz",
    "İnkübasyon": "İçte Olgunlaşma",
    "Pişirip Çık": "İçte Olgunlaşma",
}


TECH_ASTRO_PATTERN = re.compile(
    r"(\b(?:sun|moon|mercury|mars|venus|jupiter|saturn|uranus|neptune|pluto|"
    r"merkur|güneş|gunes|ay|satürn|jüpiter|uran[üu]s|nept[üu]n|pl[üu]ton)\b|"
    r"\b(?:asc|mc|ic|dsc|midheaven|ascendant|descendant)\b|"
    r"\b\d{1,2}\.\s*ev\b|"
    r"\b(?:kare|karşıt|kavuşum|üçgen|sekstil|stellium|yönetici|vurgu|vurgusu|yoğunluğu)\b)",
    re.IGNORECASE,
)

TECH_CHIP_PATTERN = re.compile(
    r"(\b\d{1,2}\.?\s*ev\b|"
    r"\b(?:satürn|saturn|merkur|merkür|mars|venus|venüs|jupiter|jüpiter|uran[üu]s|nept[üu]n|pl[üu]ton|asc|mc|ic|dsc)\b|"
    r"[+/])",
    re.IGNORECASE,
)


def _stable_int(seed: str) -> int:
    return int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16)


def _cleanup(text: str, *, max_sentences: int = 4) -> str:
    value = " ".join(str(text or "").split()).strip()
    if not value:
        return ""
    return humanize_tr_text(cleanup_duplicate_sentences(value), max_sentences=max_sentences)


def _cleanup_fragment(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    value = re.sub(r"[.!?]+$", "", value).strip()
    value = value.replace(";", ",").replace(":", ",")
    value = re.sub(r"\s+", " ", value).strip(" ,")
    return value


class _SafeDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return ""


def _normalize_copy_fragment(text: str) -> str:
    value = _cleanup_fragment(text)
    if not value:
        return ""
    first = value[:1]
    lowered_first = {"I": "ı", "İ": "i"}.get(first, first.lower())
    value = lowered_first + value[1:]
    value = re.sub(r"^(?:şu:|şu)\s+", "", value, flags=re.IGNORECASE)
    return value


def _render_text(template: str, slots: Mapping[str, Any], *, max_sentences: int) -> str:
    local = dict(slots)
    copy_payload = {k: str(v or "") for k, v in dict(local.get("copy") or {}).items()}
    defaults = {
        "core": "Sende belirgin bir iç hat var.",
        "mechanism": "İçeride birden fazla hat aynı anda çalışıyor.",
        "shadow": "Yük arttığında ritmin zorlanabiliyor.",
        "gift": "Olgun tarafında daha net ve güven veren bir akış kuruluyor.",
    }
    for field, default in defaults.items():
        if not str(copy_payload.get(field) or "").strip():
            copy_payload[field] = default
    for field in ("headline", "teaser", "core", "mechanism", "shadow", "gift", "spark", "watch"):
        copy_payload.setdefault(field, "")
        copy_payload[f"{field}_lower"] = _normalize_copy_fragment(copy_payload.get(field, ""))

    rendered = str(template or "")
    for field, value in copy_payload.items():
        rendered = rendered.replace(f"{{copy.{field}}}", value)
    rendered = rendered.format_map(_SafeDict({key: value for key, value in local.items() if key != "copy"}))
    return _cleanup(rendered, max_sentences=max_sentences)


def _select_mode(seed: str, block_id: str, signature_id: str) -> tuple[int, str]:
    mode_index = _stable_int(f"{seed}|{block_id}|{signature_id}|mode") % len(RENDER_MODES)
    return mode_index, RENDER_MODES[mode_index]


def _candidate_modes(seed: str, block_id: str, signature_id: str, preferred_family: str = "") -> List[str]:
    start_index, stable_mode = _select_mode(seed, block_id, signature_id)
    ordered = list(RENDER_MODES[start_index:]) + list(RENDER_MODES[:start_index])
    preferred_mode = next((mode for mode, label in MODE_LABELS_TR.items() if label == preferred_family), "")
    if preferred_mode and preferred_mode in ordered:
        ordered.remove(preferred_mode)
        ordered.insert(0, preferred_mode)
    if stable_mode in ordered:
        return ordered
    ordered.insert(0, stable_mode)
    return ordered


def _select_title(block_id: str, seed: str, mode: str, signature_id: str) -> tuple[int, str]:
    titles = TITLE_FAMILIES_TR.get(block_id) or [""]
    index = _stable_int(f"{seed}|{block_id}|{signature_id}|{mode}|headline") % len(titles)
    return index, str(titles[index])


def _is_technical_hint(text: str) -> bool:
    value = str(text or "").strip()
    return bool(value and TECH_ASTRO_PATTERN.search(value))


def soft_public_astro_hint(
    block_id: str,
    raw_hint: str | None,
    *,
    seed: str = "",
    signature_id: str = "",
) -> str:
    value = str(raw_hint or "").strip()
    if value and not _is_technical_hint(value) and len(value) <= 84:
        return _cleanup(value, max_sentences=1)

    hints = SOFT_ASTRO_HINTS_TR.get(block_id) or [""]
    index = _stable_int(f"{seed}|{block_id}|{signature_id}|{value}|astro_hint") % len(hints)
    return _cleanup(str(hints[index]), max_sentences=1)


def humanize_public_chips(block_id: str, chips: Sequence[Any] | None) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()

    for chip in chips or []:
        value = str(chip or "").strip()
        if not value:
            continue
        value = CHIP_REPLACEMENTS_TR.get(value, value)
        if TECH_CHIP_PATTERN.search(value):
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
        if len(out) >= 3:
            return out

    for fallback in DEFAULT_PUBLIC_CHIPS_TR.get(block_id, []):
        key = fallback.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(fallback)
        if len(out) >= 3:
            break

    return out


def render_block_template(
    *,
    block_id: str,
    seed: str,
    slots: Mapping[str, Any],
    signature_id: str = "",
    preferred_family: str = "",
    used_openings: Sequence[str] | None = None,
    used_bodies: Sequence[str] | None = None,
) -> Dict[str, Any]:
    copy_payload = (slots.get("copy") or {}) if isinstance(slots.get("copy"), Mapping) else {}
    teaser_seed = str(copy_payload.get("teaser") or copy_payload.get("core") or "").strip()
    best_payload: Dict[str, Any] | None = None

    for mode in _candidate_modes(seed, block_id, signature_id, preferred_family):
        title_index, headline = _select_title(block_id, seed, mode, signature_id)
        family = MODE_LABELS_TR.get(mode, "direct")
        body_template = ((BODY_TEMPLATES_TR.get(block_id) or {}).get(mode)) or "{copy.core}. {copy.mechanism}. {copy.shadow}. {copy.gift}."
        teaser = editorialize_teaser(teaser_seed, family)
        teaser = _cleanup(teaser, max_sentences=2) if teaser else ""
        micro = _cleanup(editorialize_micro(str(slots.get("micro") or ""), family), max_sentences=2)
        body = _render_text(body_template, slots, max_sentences=4)
        issues = quality_issues(
            teaser=teaser,
            body=body,
            micro=micro,
            used_openings=used_openings,
            used_bodies=used_bodies,
        )
        candidate = {
            "headline": _cleanup(headline, max_sentences=1),
            "teaser": teaser,
            "body": body,
            "micro": micro,
            "mode": mode,
            "mode_label": family,
            "template_index": RENDER_MODES.index(mode),
            "title_index": title_index,
            "quality_issues": issues,
            "opening_key": opening_key(body),
        }
        if best_payload is None or len(issues) < len(best_payload.get("quality_issues") or []):
            best_payload = candidate
        if not issues:
            best_payload = candidate
            break
    return best_payload or {
        "headline": "",
        "teaser": "",
        "body": "",
        "micro": "",
        "mode": "A",
        "mode_label": "direct",
        "template_index": 0,
        "title_index": 0,
        "quality_issues": [],
        "opening_key": "",
    }
