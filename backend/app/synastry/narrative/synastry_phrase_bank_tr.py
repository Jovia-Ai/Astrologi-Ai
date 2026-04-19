from __future__ import annotations

import re
from typing import Any, Dict, Sequence

from app.synastry.narrative.synastry_library_tr import body_label_tr


PAIR_SIGNATURE_TEMPLATES = [
    {
        "id": "pair_deep_warm_pull",
        "category": "romantic_pull",
        "primary_categories": ("obsessive_depth",),
        "support_categories": ("romantic_pull", "sweetness", "visible_chemistry"),
        "label": "Sıcak ama derin bağ",
        "share_line": "Bu bağ yüzeyde durmayı bilmiyor.",
        "one_liner": "Bu bağ kolay yüzeyde kalmıyor; sıcaklık oluştuğunda hızla derinleşebiliyor.",
        "tone_family": "direct_trait",
    },
    {
        "id": "pair_steady_devotion",
        "category": "devotional_bond",
        "primary_categories": ("devotional_bond", "commitment_weight"),
        "support_categories": ("emotional_safety", "sweetness"),
        "label": "Bağ ciddiyet topluyor",
        "share_line": "Aranızda acele yok — çünkü gitmiyor.",
        "one_liner": "Aranızda yalnız çekim değil, birlikte durma ve bağı ciddiye alma isteği de birikiyor.",
        "tone_family": "outside_observation",
    },
    {
        "id": "pair_friendship_to_depth",
        "category": "friendship_to_love",
        "primary_categories": ("friendship_to_love", "playful_flirt"),
        "support_categories": ("visible_chemistry", "obsessive_depth", "romantic_pull"),
        "label": "Hafif başlayıp derinleşen bağ",
        "share_line": "Gülerek başladınız. Siz farkına varmadan derinleşti.",
        "one_liner": "Bu bağ hafif bir kapıdan girse bile içeride daha yoğun bir yere kayma eğilimi taşıyor.",
        "tone_family": "mini_scene",
    },
    {
        "id": "pair_visible_heat",
        "category": "visible_chemistry",
        "primary_categories": ("visible_chemistry", "romantic_pull"),
        "support_categories": ("sweetness", "playful_flirt"),
        "label": "Kimya saklanmıyor",
        "share_line": "Kimyanız siz fark etmeden önce odaya fark ettiriyor.",
        "one_liner": "Aranızdaki çekim kendini tutmuyor; temas olduğunda enerji hızla görünür hale geliyor.",
        "tone_family": "imagistic_short_line",
    },
    {
        "id": "pair_soft_hidden_bond",
        "category": "healing_bond",
        "primary_categories": ("healing_bond",),
        "support_categories": ("emotional_safety", "sweetness", "devotional_bond"),
        "label": "Sessiz ama etkili yakınlık",
        "share_line": "Söylemeseniz de birbirinizi iyileştiriyorsunuz.",
        "one_liner": "Bu bağ açık gösteriden çok içeride çalışan bir yumuşama ve şefkat alanı kuruyor.",
        "tone_family": "emotional_state",
    },
    {
        "id": "pair_electric_pull",
        "category": "freedom_tension",
        "primary_categories": ("freedom_tension",),
        "support_categories": ("romantic_pull", "visible_chemistry"),
        "label": "Elektrikli çekim",
        "share_line": "Birlikte sakin olamıyorsunuz. Belki de olmamalısınız.",
        "one_liner": "Yakınlık canlı ama ritim her zaman sabit değil; bağ bir anda hızlanıp alan isteyebiliyor.",
        "tone_family": "imagistic_short_line",
    },
    {
        "id": "pair_charge_and_pressure",
        "category": "growth_pressure",
        "primary_categories": ("growth_pressure",),
        "support_categories": ("commitment_weight", "obsessive_depth", "freedom_tension"),
        "label": "Çeken ama zorlayan hat",
        "share_line": "Birbirinizi büyütüyorsunuz — ama aynı zamanda yıpratıyorsunuz.",
        "one_liner": "Aranızdaki çekim kadar birbirini değiştirme ve zorlama etkisi de güçlü çalışıyor.",
        "tone_family": "outside_observation",
    },
    {
        "id": "pair_mind_flirt",
        "category": "mental_spark",
        "primary_categories": ("mental_spark",),
        "support_categories": ("playful_flirt", "romantic_pull"),
        "label": "Zihinle ısınan bağ",
        "share_line": "Önce konuşuyorsunuz. Sonra hissettiğinizi fark ediyorsunuz.",
        "one_liner": "Aranızda yalnız duygu değil, zihinsel kıvılcım da çekimi hızlıca büyütebiliyor.",
        "tone_family": "mini_scene",
    },
    {
        "id": "pair_partner_recognition",
        "category": "spouse_archetype",
        "primary_categories": ("spouse_archetype", "partner_recognition"),
        "support_categories": ("shared_future_pull", "commitment_pull", "marriage_potential"),
        "label": "Birbirinde partner figuru goren bag",
        "share_line": "Birbirinizde 'yan yana yürünebilir' birini tanıyorsunuz.",
        "one_liner": "Bu bag yalnizca cekim yaratmiyor; birlikte yurunebilecek bir eslesme hissi de kuruyor.",
        "tone_family": "imagistic_short_line",
    },
    {
        "id": "pair_future_weight",
        "category": "shared_future_pull",
        "primary_categories": ("shared_future_pull", "marriage_potential"),
        "support_categories": ("relationship_weight", "commitment_pull", "devotional_bond"),
        "label": "Gelecege toplanan bag",
        "share_line": "Bugünü değil, yarını konuşmak istiyor bu bağ.",
        "one_liner": "Aranizdaki bag bugunde kalmiyor; birlikte gelecek, sadakat ve yol duygusu da toplamaya basliyor.",
        "tone_family": "outside_observation",
    },
]

TOGETHER_FIELD_TEMPLATES = [
    {
        "id": "field_friendship_to_depth",
        "category": "pair_field",
        "primary_categories": ("friendship_to_love", "playful_flirt"),
        "support_categories": ("obsessive_depth", "romantic_pull"),
        "label": "Arkadaşlıktan derinliğe kayan alan",
        "share_line": "Arkadaş olarak tanıştınız. O şekilde kalmadınız.",
        "one_liner": "Siz bir araya gelince bağ hafif bir tondan başlayıp içeride daha yoğun bir yere kayabiliyor.",
    },
    {
        "id": "field_safe_to_serious",
        "category": "pair_field",
        "primary_categories": ("emotional_safety", "devotional_bond"),
        "support_categories": ("commitment_weight", "sweetness"),
        "label": "Yumuşak başlayıp ciddileşen alan",
        "share_line": "Yavaş başladı. Kendi kendini ciddiye aldı.",
        "one_liner": "Siz bir araya gelince yakınlık kolay kuruluyor; sonra bağ kendiliğinden daha ciddi bir tona toplanabiliyor.",
    },
    {
        "id": "field_chemistry_and_awareness",
        "category": "pair_field",
        "primary_categories": ("visible_chemistry", "romantic_pull"),
        "support_categories": ("growth_pressure", "mental_spark"),
        "label": "Çekimle farkındalığın aynı anda arttığı alan",
        "share_line": "Birbirinizi hem çekiyor hem uyandırıyorsunuz.",
        "one_liner": "Siz bir araya gelince yalnız kimya değil, birbirini tetikleyen bir farkındalık da hızla yükseliyor.",
    },
    {
        "id": "field_depth_vs_space",
        "category": "pair_field",
        "primary_categories": ("obsessive_depth",),
        "support_categories": ("freedom_tension", "growth_pressure"),
        "label": "Derinlik ve alan ihtiyacının yer değiştirdiği alan",
        "share_line": "Biri yaklaşıyor, biri nefes istiyor. Dans bu.",
        "one_liner": "Siz bir araya gelince bir taraf derinleşirken diğer taraf zaman zaman nefes aramaya kayabiliyor.",
    },
    {
        "id": "field_inside_softening",
        "category": "pair_field",
        "primary_categories": ("healing_bond",),
        "support_categories": ("emotional_safety", "sweetness"),
        "label": "İçeriden yumuşayan alan",
        "share_line": "Söylemeseniz bile bu bağ sizi yumuşatıyor.",
        "one_liner": "Siz bir araya gelince duygu en çok içeride çözülüyor; söylenmeyen şeyler bile yumuşamaya başlayabiliyor.",
    },
    {
        "id": "field_shared_future_weight",
        "category": "pair_field",
        "primary_categories": ("shared_future_pull", "marriage_potential"),
        "support_categories": ("spouse_archetype", "relationship_weight"),
        "label": "Gelecege ve bagliliga toplanan alan",
        "share_line": "Birlikteyken 'yarın' sorusu kendiliğinden soruluyor.",
        "one_liner": "Siz bir araya gelince bag yalnizca bugunu degil, birlikte nereye varabileceginizi de dusundurtmeye basliyor.",
    },
]

SWEET_SPOT_TEMPLATES = {
    "sweetness": "Şefkat devreye girdiğinde bu bağın tonu hemen yumuşuyor.",
    "emotional_safety": "Gerçek temas kurduğunuzda bu bağ hızlıca güven ve yerleşme hissi üretebiliyor.",
    "friendship_to_love": "Rahat olduğunuzda aranızdaki sıcaklık doğal biçimde romantik bir yere akabiliyor.",
    "visible_chemistry": "Çekim kendini zorlamadan gösterdiğinde ilişkinin canlı tarafı hemen açılıyor.",
    "devotional_bond": "Birbirinize net davrandığınızda bu bağ kolayca daha sahici ve ciddi bir tona giriyor.",
    "playful_flirt": "Oyun, mizah ve hafiflik geldiğinde aranızdaki kapı çok hızlı açılıyor.",
    "healing_bond": "Açık konuşamasanız bile aranızdaki şefkat içeride gerçek bir yumuşama yaratabiliyor.",
    "romantic_pull": "Karşılıklı sıcaklık oluştuğunda çekimle yakınlık aynı anda büyüyebiliyor.",
    "commitment_pull": "Bag yalnizca histe kalmadiginda bu iliskinin daha sahici ve tasinabilir tarafi aciliyor.",
    "spouse_archetype": "Birbirinizi yalnizca cekici degil, birlikte yurunebilir hissettiginiz anlar bagi guclendiriyor.",
    "partner_recognition": "Tanidik bir partnerlik hissi geldigi an bu iliski hizla derin anlam kazaniyor.",
    "marriage_potential": "Sevgiyle niyet ayni hatta toplandiginda bagin ciddiyeti kendini belli ediyor.",
    "shared_future_pull": "Birlikte yarina bakabildiginiz an bu bag cok daha guclu akiyor.",
}

FRICTION_POINT_TEMPLATES = {
    "freedom_tension": "Yakınlık arttığında ritim sabit kalmak istemeyebiliyor; bir yakınlaşıp bir uzaklaşan dalga oluşabiliyor.",
    "growth_pressure": "Bağın zorlayan tarafı şu: çekim var ama ihtiyaç ritimleriniz aynı anda aynı şeye açılmayabiliyor.",
    "obsessive_depth": "Derinlik arttığında savunmalar, kıskançlık ya da duyguyu fazla sıkı tutma eğilimi yükselmeye başlayabiliyor.",
    "commitment_weight": "Bir taraf bağı ciddileştirirken diğer taraf zaman zaman bunun ağırlığını daha sert hissedebiliyor.",
    "friction": "İlişkiyi büyüten şey aynı zamanda onu zorlayan baskıyı da artırabiliyor.",
    "loyalty_pressure": "Bagi koruma istegi bazen nefes alanini daraltip iliskiyi fazla sikistirabiliyor.",
    "relationship_weight": "Yakinlik guclendikce bagin agirligi da buyuyor; bu da zaman zaman sicaklik yerine baski gibi hissedilebiliyor.",
}

A_TO_B_OPENERS = [
    "{a_name}, {b_name}'de daha gorunur bir kalp aciyor.",
    "{a_name}'in enerjisi, {b_name}'de guvenince derinlesen bir bag uyandiriyor.",
    "{a_name}, {b_name}'ye hem cekim hem de karsilik verme istegi hissettiriyor.",
    "{a_name}'in varligi, {b_name}'nin iliski alanini daha canli hale getiriyor.",
    "{a_name}, {b_name}'de hem sicaklik hem de dikkatli olma ihtiyaci acabiliyor.",
]

B_TO_A_OPENERS = [
    "{b_name}, {a_name}'da gorulme ve secilme hissini buyutebiliyor.",
    "{b_name}'in enerjisi, {a_name}'da kalbi acarken savunmalari da yukseltebiliyor.",
    "{b_name}, {a_name}'ya yalnizca cekim degil, ciddiyet de hissettirebiliyor.",
    "{b_name}, {a_name}'da daha sahici ama daha yogun bir bag alani aciyor.",
    "{b_name}'in varligi, {a_name}'nin kolay gostermedigi duygulari disari cekebiliyor.",
]

TOGETHER_FIELD_OPENERS = [
    "Siz bir araya gelince bag kolay yuzeyde kalmiyor.",
    "Bu iliskide cekim kadar farkindalik da artiyor.",
    "Aranizda arkadaslik tonunda baslayip icte derinlesen bir akim var.",
    "Birlikteyken hem yakinlik hem de hareket buyuyor.",
    "Bu bag rahat hissettirse bile altinda guclu bir yogunluk tasiyor.",
]

SWEET_SPOT_BANK = [
    "Gercek temas kurdugunuzda bu bag cok hizli canlaniyor.",
    "Birbirinizi yormadan isitabileceginiz anlar bu iliskinin en guzel tarafi oluyor.",
    "Aranizdaki yakinlik zorlamadan aktiginda iliski cok dogal hissediliyor.",
]

FRICTION_POINT_BANK = [
    "Bir taraf derinlesmek isterken diger taraf zaman zaman alan istemeye kayabiliyor.",
    "Cekim yukselirken savunmalar da ayni hizla acilabiliyor.",
    "Yakinlikla birlikte tempo buyudugunde iliski kolayca gerilebiliyor.",
]

_OVERLAY_HINT_RE = re.compile(r"([AB]) ([a-z_]+) in ([AB]) (\d+)(?:st|nd|rd|th)", re.IGNORECASE)
_ASPECT_HINT_RE = re.compile(r"([a-z_]+)-([a-z_]+) ([a-z_]+)(?: ([0-9.]+)°)?", re.IGNORECASE)

_ASPECT_LABELS_TR = {
    "conjunction": "kavuşumu",
    "trine": "akışı",
    "square": "sert teması",
    "opposition": "karşıtlığı",
    "sextile": "uyumu",
}


def soft_astro_hint_from_sources(source_debug: Sequence[str]) -> str:
    hints: list[str] = []
    for raw in source_debug:
        text = str(raw or "").strip()
        if not text:
            continue
        overlay_match = _OVERLAY_HINT_RE.search(text)
        if overlay_match:
            body = body_label_tr(overlay_match.group(2))
            house = overlay_match.group(4)
            hints.append(f"{body} + {house}.ev aktivasyonu")
            continue
        aspect_match = _ASPECT_HINT_RE.search(text)
        if aspect_match:
            left = body_label_tr(aspect_match.group(1))
            right = body_label_tr(aspect_match.group(2))
            aspect = _ASPECT_LABELS_TR.get(aspect_match.group(3).lower(), "teması")
            hints.append(f"{left}/{right} {aspect}")
    unique = []
    seen = set()
    for hint in hints:
        if hint in seen:
            continue
        seen.add(hint)
        unique.append(hint)
    return " + ".join(unique[:2])


def pair_template_index() -> Dict[str, Dict[str, Any]]:
    return {str(item["id"]): dict(item) for item in PAIR_SIGNATURE_TEMPLATES}
