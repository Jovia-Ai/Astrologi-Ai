# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import random
from typing import List, Optional

RISK_WORDS = (
    "zorlayıcı",
    "hassas",
    "hassasiyet",
    "yaralanma",
    "gerilim",
    "sert",
    "kaza",
    "yanlış anlama",
    "belirsizlik",
    "dağınık",
    "toksik",
    "kopuş",
)

FLOW_WORDS = (
    "akış",
    "destek",
    "uyum",
    "kolay",
    "verimli",
    "fırsat",
    "netleş",
    "şans",
    "genişleme",
    "büyüme",
)

HOME_WORDS = ("ev/aile", "yuva", "aile", "ev", "hane")
WORK_WORDS = ("iş/kariyer", "iş", "kariyer", "hedef", "sözleşme", "toplantı", "plan")

BODY_TR = {
    "Sun": "Güneş",
    "Moon": "Ay",
    "Mercury": "Merkür",
    "Venus": "Venüs",
    "Mars": "Mars",
    "Jupiter": "Jüpiter",
    "Saturn": "Satürn",
    "Uranus": "Uranüs",
    "Neptune": "Neptün",
    "Pluto": "Plüton",
    "Node": "Ay Düğümleri",
    "Fortune": "Fortuna",
    "Vertex": "Vertex",
    "Chiron": "Chiron",
}

NOTE_R0_RISK = [
    "Tempo düşür; bedeni ve sinir sistemini yormadan ilerle. Büyük hamleleri ertele.",
    "Bugün daha az eforla git; önemli kararları yarına bırak, yükü hafiflet.",
]
NOTE_R0_SOFT = [
    "Yüksek efor gerektiren işleri azalt; hazırlık, düzenleme ve plan için iyi.",
    "Büyük hamle yerine düzenleme yap; taslak çıkar, planı toparla.",
]

NOTE_R1 = [
    "Nötr; rutin işler için uygun.",
    "Nötr; küçük düzenlemeler ve bitirilmesi gerekenler için iyi.",
    "Nötr; akışa göre ilerle, gereksiz yük alma.",
]
NOTE_R2 = [
    "İyi; küçük risklerle ilerleyebilirsin.",
    "İyi; görüşme, yazışma ve somut ilerleme için destek var.",
    "İyi; doğru öncelik seçersen hız kazanırsın.",
]
NOTE_R3 = [
    "Çok ideal; tek hedef seçip odağı korursan çok verimli.",
    "Çok ideal; net bir planla ilerlersen sonuç alırsın.",
]

NOTE_R3_CRITICAL_BASE = (
    "Eşik + fırsat: tek hedef seç, planı sadeleştir, acele karar verme."
)


def _contains_any(text: str, words: tuple[str, ...]) -> bool:
    t = (text or "").lower()
    return any(w in t for w in words)


def _pick(seq: List[str], seed: Optional[str] = None) -> str:
    if not seq:
        return ""
    if seed:
        idx = sum(ord(c) for c in seed) % len(seq)
        return seq[idx]
    return random.choice(seq)


def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def normalize_dashes(s: str) -> str:
    s = (s or "").replace("— —", "—")
    s = s.replace("(— —", "(—")
    s = re.sub(r"\(\s*—\s*—\s*", "(— ", s)
    return s


SIGN_DATIVE = {
    "Koç": "Koç’a",
    "Boğa": "Boğa’ya",
    "İkizler": "İkizler’e",
    "Yengeç": "Yengeç’e",
    "Aslan": "Aslan’a",
    "Başak": "Başak’a",
    "Terazi": "Terazi’ye",
    "Akrep": "Akrep’e",
    "Yay": "Yay’a",
    "Oğlak": "Oğlak’a",
    "Kova": "Kova’ya",
    "Balık": "Balık’a",
}


def turkish_a_dative(sign: str) -> str:
    sign = (sign or "").strip()
    return SIGN_DATIVE.get(sign, f"{sign}’a")


def fix_ingress_label(label: str, lens_suffix: Optional[str] = None) -> str:
    if not label:
        return label
    m = re.match(
        r"^\s*([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+([A-Za-zÇĞİÖŞÜçğıöşü]+)\s+girişi\s*$",
        label,
    )
    if not m:
        return normalize_dashes(normalize_spaces(label))

    body_raw, sign = m.group(1), m.group(2)
    body = body_raw
    out = f"{body} {turkish_a_dative(sign)} giriş"

    if lens_suffix:
        out = f"{out} • {lens_suffix}"

    return normalize_dashes(normalize_spaces(out))


def humanize_label(label: str, lens_suffix: Optional[str] = None) -> str:
    if not label:
        return label

    s = normalize_spaces(label)
    s = normalize_dashes(s)

    if s.endswith("girişi"):
        s = fix_ingress_label(s, lens_suffix=lens_suffix)

    s = s.replace("değiş/kariyerim", "değişim")
    s = s.replace("giriş/kariyeri", "giriş")

    return normalize_dashes(normalize_spaces(s))


def spice_from_labels(labels: List[str]) -> str:
    joined = " | ".join(labels or [])
    j = joined.lower()

    if "merkür" in j:
        return "Yazışma/planlama yap; net bir mesaj taslağı çıkar."
    if "venüs" in j:
        return "İlişkilerde yumuşak bir adım fayda getirir."
    if "mars" in j:
        return "Enerjiyi dağıtma; tek aksiyon seç."
    if "ay" in j:
        return "Duygu iniş-çıkışına göre hız ayarla."

    if _contains_any(j, HOME_WORDS) and _contains_any(j, ("zorlayıcı", "gerilim", "hassas")):
        return "Ev/aile tarafında yük bindirmemeye dikkat."
    if _contains_any(j, WORK_WORDS) and _contains_any(j, ("zorlayıcı", "gerilim", "hassas")):
        return "İş tarafında scope’u şişirme; küçük ve net kal."
    if "netleş" in j or "yön" in j:
        return "Kararı basitleştir: tek kriter, tek öncelik."
    if "akış" in j or "destek" in j:
        return "İlerlemek için fırsat var; küçük ama net adım at."
    if "sezgi" in j or "belirsiz" in j:
        return "Belirsizse imza/taahhüt yerine taslakla ilerle."

    return ""


def generate_user_note(
    date: str,
    rating: int,
    is_critical: bool,
    labels: List[str],
    intent: str = "transit",
) -> str:
    joined = " | ".join(labels or [])
    has_risk = _contains_any(joined, RISK_WORDS)
    has_flow = _contains_any(joined, FLOW_WORDS)

    if intent == "beauty_care":
        if rating <= 0:
            return _pick(NOTE_R0_RISK if has_risk else NOTE_R0_SOFT, seed=date)
        if rating == 1:
            return "Hafif bakım ve düzenleme için uygun; aşırıya kaçma."
        if rating == 2:
            return "İyi; bakım rutini, temizlik ve küçük adımlar için destek var."
        if is_critical:
            spice = spice_from_labels(labels)
            return normalize_spaces(f"{NOTE_R3_CRITICAL_BASE} {spice}".strip())
        return "Çok ideal; tek işlem/tek hedef seçip sade ilerle."

    if rating >= 3 and is_critical:
        base = "Eşik gün: odağı sadeleştir, hızını iyi ayarla."
        spice = spice_from_labels(labels)
        return normalize_spaces(f"{base} {spice}".strip())

    if rating <= 0:
        if has_risk:
            return "Hassas bir gün; tempoyu düşür, bedeni ve zihni zorlamadan ilerle."
        return "Daha sakin bir gün; hazırlık, düzenleme ve planlama iyi çalışır."

    if rating == 1:
        base = _pick(
            [
                "Dengeli; rutin akışta ilerlemek için uygun.",
                "Dengeli; küçük düzenlemeler ve tamamlamalar iyi gider.",
            ],
            seed=date,
        )
        return normalize_spaces(f"{base} {spice_from_labels(labels)}".strip())

    if rating == 2:
        base = _pick(
            [
                "Destekleyici; iletişim ve somut ilerleme daha rahat akar.",
                "Destekleyici; doğru öncelikle verim artar.",
            ],
            seed=date,
        )
        return normalize_spaces(f"{base} {spice_from_labels(labels)}".strip())

    base = _pick(
        [
            "Güçlü; odağı korursan yüksek verim alırsın.",
            "Güçlü; net planla hızlı sonuç alabilirsin.",
        ],
        seed=date,
    )
    return normalize_spaces(f"{base} {spice_from_labels(labels)}".strip())
