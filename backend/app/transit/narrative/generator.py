from __future__ import annotations

import hashlib
import random
import re
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from app.transit.narrative.composer import compose_daily_line2_from_top_event

BLACKLIST = {
    "orb",
    "aspect",
    "transit",
    "marker",
    "score",
    "event_count",
    "signals_count",
    "retrograde",
    "percentile",
    "heat",
}

CRITICAL_TONES = [
    "Bugun bazi seyler keskin yasanabilir.",
    "Bugun kucuk bir olay bile buyuyebilir.",
    "Bugun dikkatli ilerlemek daha iyi olur.",
]

RATING_TONES = {
    0: [
        "Bugun daha sakin bir gun.",
        "Bugun dengeli bir akista ilerleyebilirsin.",
        "Su an buyuk bir baski gorunmuyor.",
    ],
    1: [
        "Bugun hafif bir hareketlilik var.",
        "Bugun ufak degisimler dikkat cekebilir.",
        "Bugun tempo yumusak ama canli.",
    ],
    2: [
        "Bugun tempo biraz yukseliyor.",
        "Bugun konular daha gorunur olabilir.",
        "Bugun dikkatini toparlamak onemli.",
    ],
    3: [
        "Bugun oldukca yogun.",
        "Bugun tepkiler normalden daha guclu olabilir.",
        "Bugun akis hizli ve talepkar olabilir.",
    ],
}

GUIDANCE_POOL = [
    "Acele karar vermemek iyi olur.",
    "Kucuk bir mola iyi gelebilir.",
    "Net ama sakin kalmak onemli.",
    "Buyuk resmi kacirmamaya calis.",
    "Tepki vermeden once dusunmek faydali olur.",
    "Esnek kalirsan gun daha rahat ilerler.",
]

LABEL_FRAGMENTS: Dict[str, List[str]] = {
    "phase_shift": ["Bir seylerin yonu degisiyor.", "Ayni sekilde devam etmek zor gelebilir."],
    "ingress": ["Yeni bir donem basliyor.", "Farkli bir alan aciliyor."],
    "peak_energy": ["Bugun enerji yuksek.", "Hareket istegi artabilir."],
    "retro_station": ["Ritim ani sekilde degisebilir.", "Durup yonunu yeniden belirlemek iyi gelebilir."],
    "eclipse_window": ["Duygular daha hizli yukselebilir.", "Netlik icin biraz zaman tanimak iyi olur."],
    "relationships_axis": ["Iliskiler daha hassas olabilir.", "Karsilikli etkilenme daha hizli olabilir."],
    "career_axis": ["Is ve yon konulari one cikiyor.", "Sorumluluklar daha gorunur olabilir."],
    "money_axis": ["Para ve deger konulari dikkat cekebilir.", "Harcamalarda sakin kalmak fayda saglar."],
    "home_axis": ["Ev ve duzen ihtiyaci artabilir.", "Gun icinde alanini toparlamak iyi hissettirebilir."],
    "mind_axis": ["Zihin daha hareketli olabilir.", "Konu degisimi hizlanabilir."],
    "volatility": ["Beklenmedik gelismeler olabilir.", "Planlar aniden degisebilir."],
    "injury_risk": ["Hassasiyet artabilir.", "Bedensel sinirlari zorlamamak iyi olur."],
    "procedure_block": ["Bugun zorlayici adimlar uygun olmayabilir.", "Nazik ilerlemek daha guvenli olur."],
    "support_tone": ["Arka planda bir destek var.", "Isler dusundugunden daha kolay akabilir."],
    "pressure_tone": ["Ic baski artabilir.", "Kendini zaman zaman sikismis hissedebilirsin."],
}

PRIMARY_LABELS = {"phase_shift", "ingress", "peak_energy", "retro_station", "eclipse_window"}
RISK_LABELS = {"volatility", "injury_risk", "procedure_block"}
DOMAIN_LABELS = {"relationships_axis", "career_axis", "money_axis", "home_axis", "mind_axis"}

LABEL_ALIASES = {
    "event_peak": "peak_energy",
    "phase_shift": "phase_shift",
    "retro": "retro_station",
    "station": "retro_station",
    "ingress": "ingress",
    "eclipse_window": "eclipse_window",
    "risk_signal": "volatility",
    "hard_mars": "injury_risk",
    "hard_saturn": "pressure_tone",
    "procedure_block": "procedure_block",
    "injury_risk": "injury_risk",
    "relationship": "relationships_axis",
    "relationships": "relationships_axis",
    "career": "career_axis",
    "money": "money_axis",
    "home": "home_axis",
    "mind": "mind_axis",
    "support": "support_tone",
    "pressure": "pressure_tone",
    "peak_energy": "peak_energy",
    "volatility": "volatility",
}


def make_birth_fingerprint(*, birth_date: str, birth_time: str, birth_place: str, tz: str) -> str:
    raw = f"{birth_date}|{birth_time}|{birth_place}|{tz}".strip().lower()
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def make_seed(
    *,
    birth_fingerprint: str,
    date: str,
    intent: str,
    lens: str,
    rating: int,
    is_critical: bool,
    labels: Sequence[str],
) -> int:
    labels_sorted = sorted(str(label).strip().lower() for label in labels if str(label).strip())
    seed_key = (
        f"{birth_fingerprint}|{date}|{intent}|{lens}|{rating}|{int(is_critical)}|"
        f"{','.join(labels_sorted[:5])}"
    )
    return int(hashlib.sha1(seed_key.encode("utf-8")).hexdigest()[:8], 16)


def _canonical_label(label: str) -> str | None:
    norm = str(label or "").strip().lower().replace(" ", "_")
    if not norm:
        return None
    if norm in LABEL_ALIASES:
        return LABEL_ALIASES[norm]
    for key, value in LABEL_ALIASES.items():
        if key in norm:
            return value
    return norm if norm in LABEL_FRAGMENTS else None


def pick_label_fragments(labels: Sequence[str], seed: int) -> Tuple[List[str], List[str]]:
    rng = random.Random(seed)
    normalized = []
    for raw in labels:
        label = _canonical_label(str(raw))
        if label and label not in normalized:
            normalized.append(label)

    primary = [label for label in normalized if label in PRIMARY_LABELS]
    risk = [label for label in normalized if label in RISK_LABELS]
    domain = [label for label in normalized if label in DOMAIN_LABELS]
    other = [label for label in normalized if label not in PRIMARY_LABELS | RISK_LABELS | DOMAIN_LABELS]

    picked: List[str] = []
    for bucket in (primary, risk, domain, other):
        if not bucket:
            continue
        label = rng.choice(bucket)
        if label not in picked:
            picked.append(label)
        if len(picked) >= 2:
            break

    fragments: List[str] = []
    for label in picked:
        options = LABEL_FRAGMENTS.get(label) or []
        if not options:
            continue
        fragments.append(rng.choice(options))
    return picked, fragments[:2]


def _sanitize_sentence(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return ""
    if cleaned[-1] not in ".!?":
        cleaned = f"{cleaned}."
    return cleaned


def _strip_terminal_punct(text: str) -> str:
    return re.sub(r"[.!?]+$", "", text.strip())


def _has_blacklist(sentence: str) -> bool:
    low = sentence.lower()
    return any(word in low for word in BLACKLIST)


def generate_daily_narrative(
    *,
    rating: int,
    is_critical: bool,
    labels: Sequence[str],
    seed: int,
    top_event: Mapping[str, Any] | None = None,
    locale: str = "tr",
) -> str:
    if locale != "tr":
        locale = "tr"

    tone_pool = CRITICAL_TONES if is_critical else RATING_TONES.get(max(0, min(3, int(rating))), RATING_TONES[1])
    line1 = _sanitize_sentence(tone_pool[seed % len(tone_pool)])

    line2 = _sanitize_sentence(
        compose_daily_line2_from_top_event(
            top_event=top_event,
            labels=[str(label) for label in labels],
            seed=seed,
            voice_style="you",
        )
    )
    if not line2:
        _, fragments = pick_label_fragments(labels, seed)
        if fragments:
            fragments_compact = [_strip_terminal_punct(part) for part in fragments[:2] if part.strip()]
            line2 = _sanitize_sentence(" ve ".join(fragments_compact))
        else:
            fallback = [
                "Bugun buyuk bir zorlanma gorunmuyor.",
                "Bugunun ritmi gun icinde daha netlesebilir.",
                "Kucuk degisimler gunun akisini belirleyebilir.",
            ]
            line2 = _sanitize_sentence(fallback[(seed // 3) % len(fallback)])

    line3 = _sanitize_sentence(GUIDANCE_POOL[(seed // 7) % len(GUIDANCE_POOL)])

    lines = [line1, line2, line3]
    normalized: List[str] = []
    for line in lines:
        if not line:
            continue
        if _has_blacklist(line):
            line = "Bugunu sade tutmak ve sakin kalmak daha iyi hissettirebilir."
        normalized.append(_sanitize_sentence(line))

    while len(normalized) < 3:
        normalized.append("Bugunu sade tutmak ve sakin kalmak daha iyi hissettirebilir.")

    return " ".join(normalized[:3])
