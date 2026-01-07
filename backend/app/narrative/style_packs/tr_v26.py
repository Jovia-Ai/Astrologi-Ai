from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# -----------------------------
# v2.6 TR STYLE PACK — Identity
# -----------------------------

STYLE_PACK_TR_V26: Dict[str, dict] = {
    "identity": {
        "title": "Senin Dünyanın İç Çekirdeği",

        # Recognition: 1–2 paragraf (2.6 hissi)
        # Not: Bu blok “dış görünüm” + “ama içte başka bir dünya” kontrastını kurmalı.
        "recognition_templates": [
            [
                "Sen hayata {start_style} başlayan, her şeyi biraz daha {depth_style} alan birisin.",
                "Boş konuşmayı sevmiyorsun; “{core_motto1}” diye düşünen bir tarafın hep var.",
                "İnsanlar seni gördüğünde çoğu zaman {outer_adjs} biri gibi görür.",
            ],
            [
                "Ama bu sadece dışarıdan görünen tarafın.",
                "İçinde bundan çok daha {inner_adjs} bir dünya akıyor.",
            ],
        ],

        # Experienced: mekanizma merkezli (2–3 kısa paragraf)
        "experienced_templates": [
            [
                "İçinde aynı anda iki ihtiyaç çalışır: {tension_pair}.",
                "Bazen {tension_line}.",
            ],
            [
                "Kimi zaman kendi içinde {inner_questions} gibi sorular belirir.",
                "Bunu hemen dışarıya göstermeyebilirsin; bazen için için taşırsın.",
            ],
            [
                "Senin sistemin şöyle kurulur: {mechanism_anchor}.",
                "Bu yüzden bir yanın {side_a}, bir yanın {side_b}.",
            ],
        ],

        # Potential: 1 paragraf
        "potential_templates": [
            [
                "Bu yapı aslında seni {growth_dir} doğru iter.",
                "{resource_anchor} güçlendikçe {positive_outcome} daha doğal olur.",
            ]
        ],

        # Shadow: 1 kısa paragraf (korkutmadan)
        "shadow_templates": [
            [
                "Gölge tarafta en çok şu sapma görülebilir: {shadow_risk}.",
                "Bu bir suç değil; sadece yükün fazla bindiği bir yer.",
            ]
        ],

        # Upper Meaning: ayrı katman (enabled ise)
        "upper_meaning_templates": [
            [
                "Senin hayatında tekrarlayan tema çoğu zaman şu eksende çalışır: {growth_axis_line}.",
                "Bunu taşıyabildiğinde sende {mastery_line} oluşur.",
            ]
        ],

        # -----------------------------
        # OPTION BANKS (Deterministic)
        # -----------------------------

        # “hayata ciddiyetle başlayan” hissi için start_style
        "start_style_by_pressure": {
            "low": ["temkinli", "sakin", "ölçülü"],
            "mid": ["ciddiyetle", "dikkatle", "kontrollü"],
            "high": ["yük taşıyarak", "erken olgunlaşarak", "güçlü durmaya çalışarak"],
        },

        # “derin / ağırdan” hissi
        "depth_style_by_intensity": {
            "low": ["hafifçe", "pratikçe", "daha düz"],
            "mid": ["derin", "ağırdan", "özümseyerek"],
            "high": ["çok derin", "yoğun", "sindire sindire"],
        },

        # “core motto” bankası (identity tonunu kurar)
        "core_motto_bank": [
            "Hazır olayım",
            "sağlam olayım",
            "güçlü olayım",
            "kendimi toparlayayım",
            "kontrol bende olsun",
        ],

        # Dış algı sıfat bankası (outer_adjs)
        "outer_adj_bank": {
            "control": ["güçlü", "kontrollü", "sağlam"],
            "security": ["sakin", "kararlı", "dayanıklı"],
            "worth": ["ciddi", "saygın", "kendinden emin"],
            "visibility": ["dikkat çeken", "net", "kendini ortaya koyan"],
            "depth": ["ağırbaşlı", "derin", "kolay açılmayan"],
            "autonomy": ["bağımsız", "mesafeli", "kendi alanı olan"],
            "generic": ["güçlü", "kontrollü", "sağlam"],
        },

        # İç dünya sıfat bankası (inner_adjs)
        "inner_adj_bank": {
            "depth": ["canlı", "yoğun", "sahici"],
            "visibility": ["parlamak isteyen", "görünmek isteyen", "kendini ifade eden"],
            "autonomy": ["özgür", "yaratıcı", "kendi ritmi olan"],
            "security": ["hassas", "korumacı", "ince ayarlı"],
            "control": ["düzen kuran", "planlayan", "kendini tutan"],
            "worth": ["incelikli", "yüksek standartlı", "kendini kanıtlamak isteyen"],
            "generic": ["canlı", "yoğun", "sahici"],
        },

        # Tension pair line (etiketlerden)
        "tension_pair_phrases": {
            ("control", "authenticity"): "kontrol etme ihtiyacı ↔ gerçek olma ihtiyacı",
            ("control", "visibility"): "kontrol ihtiyacı ↔ görülme ihtiyacı",
            ("security", "visibility"): "güvende kalma ↔ görünür olma",
            ("security", "depth"): "güven ihtiyacı ↔ derin bağ ihtiyacı",
            ("worth", "visibility"): "değerini kanıtlama ↔ görülme",
            ("autonomy", "depth"): "özgürlük ↔ yakınlık",
        },

        # Tension line templates (tek cümle)
        "tension_line_bank": {
            "control": [
                "“sağlam durmalıyım” tarafın yükselir",
                "“kontrolü bırakmamam gerek” diye içten içe sıkılaşırsın",
            ],
            "visibility": [
                "“beni gerçekten görüyorlar mı?” hissi belirir",
                "“ben buradayım” demek istersin",
            ],
            "security": [
                "“zemin sağlam mı?” diye yoklarsın",
                "belirsizlik artınca içten içe kapanabilirsin",
            ],
            "depth": [
                "yakınlık ararsın ama kolay açılmazsın",
                "duygular derinleşince daha fazla sahiplenirsin",
            ],
            "worth": [
                "kendini kanıtlama ihtiyacı devreye girer",
                "standartların yükselir, hata payın azalır",
            ],
            "autonomy": [
                "alan ihtiyacın yükselir",
                "“kendi ritmimde kalayım” dersin",
            ],
            "generic": [
                "iki uç arasında gidip gelirsin",
                "bir yanın tutar, bir yanın açılmak ister",
            ],
        },

        # Inner questions (2.6 hissi için çok önemli)
        "inner_question_bank": {
            "visibility": [
                "“beni gerçekten gören var mı?”",
                "“ben bu kadar emek veriyorum ama bu fark ediliyor mu?”",
            ],
            "depth": [
                "“ben bu kadar hissediyorum ama bu anlaşılıyor mu?”",
                "“yakınlık güvenli mi?”",
            ],
            "worth": [
                "“yeterli miyim?”",
                "“bunu hak ediyor muyum?”",
            ],
            "control": [
                "“kontrolü bıraksam da dağılmaz mı?”",
                "“güçlü durmazsam çöker mi?”",
            ],
            "security": [
                "“bu bana iyi gelir mi?”",
                "“bu güvenli mi?”",
            ],
            "autonomy": [
                "“alanım kalacak mı?”",
                "“kendim olarak kalabilecek miyim?”",
            ],
            "generic": [
                "“ben kimim?”",
                "“bunu nasıl dengeleyebilirim?”",
            ],
        },

        # Mechanism anchor paraphrase (slot text basmak yerine)
        "mechanism_anchor_bank": {
            "control": "yapı üzerinden kimlik kurma; düzen ve sorumlulukla kendini sağlam tutma",
            "security": "istikrar ihtiyacıyla hareket etme; güveni önce içeride kurma",
            "visibility": "varlığını görünür kılma; değerinin fark edilmesini isteme",
            "depth": "derin his ve bağ ihtiyacı; sahici temas arama",
            "worth": "değerini kanıtlama; standart ve başarı üzerinden kendini konumlama",
            "autonomy": "kendi alanını koruma; özgür kalma ihtiyacı",
            "generic": "birkaç temel ihtiyacın aynı anda çalıştığı, dengeli ama hassas bir iç sistem",
        },

        # side A / side B (tension pair’den türetilecek)
        "side_phrases": {
            "control": "güçlü ve sağlam kalmak ister",
            "security": "zemini garantiye almak ister",
            "visibility": "kendini ortaya koymak ister",
            "depth": "gerçek temas ve derinlik ister",
            "worth": "saygı ve yeterlilik arar",
            "autonomy": "kendi alanını korumak ister",
            "authenticity": "daha sahici, daha çıplak olmayı ister",
        },

        # Growth direction
        "growth_dir_bank": {
            "control": ["kontrolü bilinçli güce dönüştürmeye", "yükü paylaşarak sağlam kalmaya"],
            "security": ["güveni dış koşullardan iç kaynaklara taşımaya", "kendi içinde emniyet kurmaya"],
            "visibility": ["görünürlüğü duygusal liderliğe taşımaya", "kendini ifade ederken yumuşamaya"],
            "depth": ["derinliği güven alanına çevirmeye", "yakınlıkta sağlam kalmaya"],
            "worth": ["değeri başarıdan kimliğe taşımaya", "kendini kanıtlamadan da değerli hissetmeye"],
            "autonomy": ["özgürlüğü bağ kurmanın içinde de korumaya", "alan ihtiyacını dürüstçe konuşmaya"],
            "generic": ["dengenin olgun formunu kurmaya", "iki ucu aynı anda taşıyabilmeye"],
        },

        # Resource anchor (yapı güçlenince…)
        "resource_anchor_bank": {
            "control": "esneklik ve güven",
            "security": "içsel kaynak ve sabır",
            "visibility": "kendini ifade etme cesareti",
            "depth": "şefkat ve duygusal kapasite",
            "worth": "öz saygı ve tutarlılık",
            "autonomy": "sınır koyma ve netlik",
            "generic": "farkındalık ve pratik",
        },

        # Positive outcome
        "positive_outcome_bank": {
            "control": "güçlü duruşun sertleşmeden akar",
            "security": "sağlamlık hissin dışarıya bağımlı olmaz",
            "visibility": "görünürlük ihtiyacın daha sakin bir ifadeye dönüşür",
            "depth": "yoğunluğun yıpratmaz; güç verir",
            "worth": "değer hissin kanıt istemez",
            "autonomy": "bağ kurarken de kendin kalırsın",
            "generic": "denge daha sürdürülebilir hale gelir",
        },

        # Shadow risk (korkutmadan)
        "shadow_risk_bank": {
            "control": "fazla kontrol etme ve gevşeyememe",
            "security": "aşırı temkin ve riskten kaçınma",
            "visibility": "onay arayışına takılma",
            "depth": "yoğunlukla yorulma, içe çekilme",
            "worth": "kendine sertlik ve yetersizlik hissi",
            "autonomy": "mesafeyi fazla açma",
            "generic": "aşırı yüklenme ve içsel sıkışma",
        },

        # Upper meaning lines
        "growth_axis_line_bank": {
            "1-7": "Ben / Biz",
            "4-10": "İç dünya / Yön",
            "2-8": "Güvenlik / Paylaşım",
            "3-9": "Zihin / Anlam",
            "generic": "iki kutup",
        },
        "mastery_line_bank": [
            "temiz güç ve şefkatli bir duruş",
            "krizde bile ayakta kalabilen bir bilinç",
            "derin ama sağlam bir kalp",
        ],
    }
}


# -----------------------------
# Deterministic helpers
# -----------------------------

def _band(value: float, low: float = 0.4, high: float = 0.75) -> str:
    if value < low:
        return "low"
    if value >= high:
        return "high"
    return "mid"


def pick_identity_plan_tokens(
    *,
    pressure_index: float,
    support_index: float,
    primary_intent: str,
    secondary_intent: str,
    axis: Optional[str],
) -> dict:
    """
    Minimal deterministic token picker for identity placeholders.
    (Planner daha zengin olacak; şimdilik render'a hazır token seti döndürüyor.)
    """
    pack = STYLE_PACK_TR_V26["identity"]

    pressure_band = _band(pressure_index, low=0.45, high=0.78)
    intensity_band = _band(pressure_index, low=0.45, high=0.78)  # pressure ≈ intensity proxy v1

    start_style = pack["start_style_by_pressure"][pressure_band][0]
    depth_style = pack["depth_style_by_intensity"][intensity_band][1] if intensity_band != "low" else pack["depth_style_by_intensity"]["low"][0]

    core_motto1 = pack["core_motto_bank"][0] if primary_intent in ("control", "security") else pack["core_motto_bank"][2]

    outer_adjs = ", ".join(pack["outer_adj_bank"].get(primary_intent, pack["outer_adj_bank"]["generic"])[:3])
    inner_adjs = ", ".join(pack["inner_adj_bank"].get(secondary_intent, pack["inner_adj_bank"]["generic"])[:3])

    # tension pair
    # authenticity yoksa: control ↔ visibility/security/depth vb.
    key = (primary_intent, secondary_intent)
    tension_pair = pack["tension_pair_phrases"].get(key) or pack["tension_pair_phrases"].get((secondary_intent, primary_intent)) or f"{primary_intent} ↔ {secondary_intent}"

    tension_line = pack["tension_line_bank"].get(primary_intent, pack["tension_line_bank"]["generic"])[0]

    # inner questions choose 2
    q_bank = pack["inner_question_bank"].get(primary_intent, pack["inner_question_bank"]["generic"])
    q2_bank = pack["inner_question_bank"].get(secondary_intent, pack["inner_question_bank"]["generic"])
    inner_questions = f"{q_bank[0]} / {q2_bank[0]}"

    mechanism_anchor = pack["mechanism_anchor_bank"].get(primary_intent, pack["mechanism_anchor_bank"]["generic"])

    side_a = pack["side_phrases"].get(primary_intent, "bir tarafın tutar")
    side_b = pack["side_phrases"].get(secondary_intent, "bir tarafın açılmak ister")

    growth_dir = pack["growth_dir_bank"].get(primary_intent, pack["growth_dir_bank"]["generic"])[0]
    resource_anchor = pack["resource_anchor_bank"].get(primary_intent, pack["resource_anchor_bank"]["generic"])
    positive_outcome = pack["positive_outcome_bank"].get(primary_intent, pack["positive_outcome_bank"]["generic"])

    shadow_risk = pack["shadow_risk_bank"].get(primary_intent, pack["shadow_risk_bank"]["generic"])

    growth_axis_line = pack["growth_axis_line_bank"].get(axis or "generic", pack["growth_axis_line_bank"]["generic"])
    mastery_line = pack["mastery_line_bank"][0]

    # support_index -> soften/harden a little (still deterministic)
    # High support => slightly warmer phrasing tokens (future hook)
    if support_index >= 0.62:
        core_motto1 = "Hazır olayım"
        mastery_line = pack["mastery_line_bank"][2]

    return {
        "start_style": start_style,
        "depth_style": depth_style,
        "core_motto1": core_motto1,
        "outer_adjs": outer_adjs,
        "inner_adjs": inner_adjs,
        "tension_pair": tension_pair,
        "tension_line": tension_line,
        "inner_questions": inner_questions,
        "mechanism_anchor": mechanism_anchor,
        "side_a": side_a,
        "side_b": side_b,
        "growth_dir": growth_dir,
        "resource_anchor": resource_anchor,
        "positive_outcome": positive_outcome,
        "shadow_risk": shadow_risk,
        "growth_axis_line": growth_axis_line,
        "mastery_line": mastery_line,
    }
