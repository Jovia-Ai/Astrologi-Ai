from __future__ import annotations

import re
from typing import Any, Dict, Mapping

from app.narrative.editorial_render_policy import apply_phrase_policy, select_rhythm_family
from app.narrative.humanize_en import clean_public_block_en
from app.narrative.humanize_tr import clean_public_block_tr
from app.natal.narrative.micro_example_engine_tr import choose_micro_example
from app.natal.narrative.primitive_engine import build_primitives
from app.natal.narrative.phrase_lib_en_profile import (
    humanize_public_chips as humanize_public_chips_en,
)
from app.natal.narrative.phrase_lib_en_profile import (
    render_block_template as render_block_template_en,
)
from app.natal.narrative.phrase_lib_en_profile import (
    soft_public_astro_hint as soft_public_astro_hint_en,
)
from app.natal.narrative.phrase_lib_tr_profile import (
    humanize_public_chips,
    render_block_template,
    soft_public_astro_hint,
)
from app.natal.narrative.signature_catalog_tr import SIGNATURE_CATALOG_TR
from app.natal.narrative.signature_engine import BLOCK_ORDER, extract_candidates, normalize_facts, select_by_block
from app.natal.narrative.signature_taxonomy_tr import BLOCK_ALIAS_TO_TAXONOMY
from app.natal.supporting_threads_builder import (
    HOUSE_ARENA_TR,
    SIGN_VIBE_TR,
    _CAREER_MC_BALANCE_TR,
    _CAREER_RULER_SIGN_BALANCE_TR,
    _RELATIONSHIP_RULER_SIGN_BALANCE_TR,
    _RELATIONSHIP_SIGN_BALANCE_TR,
    _RELATIONSHIP_SIGN_OPENING_TR,
)

ENGINE_VERSION = "profile_narrative_v2"
SEED_VERSION = "profile_signature_seed_v2_s1"

ASPECT_LABELS_TR = {
    "conjunction": "kavuşumu",
    "opposition": "karşıtlığı",
    "square": "karesi",
    "trine": "üçgeni",
    "sextile": "sekstili",
}

ANGLE_LABELS_TR = {
    "ASC": "Yükselen",
    "MC": "Tepe Noktası",
    "DSC": "Alçalan",
    "IC": "Dip Noktası",
}

PLANET_LABELS_TR = {
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
    "Ascendant": "Yükselen",
    "Midheaven": "Tepe Noktası",
    "Descendant": "Alçalan",
    "Imum Coeli": "Dip Noktası",
    "Fortune": "Fortuna",
    "Chiron": "Kiron",
    "Vertex": "Vertex",
    "Lilith": "Lilith",
}

ASPECT_LABELS_EN = {
    "conjunction": "conjunct",
    "opposition": "opposite",
    "square": "square",
    "trine": "trine",
    "sextile": "sextile",
}

ANGLE_LABELS_EN = {
    "ASC": "Ascendant",
    "MC": "Midheaven",
    "DSC": "Descendant",
    "IC": "IC",
}

PLANET_LABELS_EN = {
    "Sun": "Sun",
    "Moon": "Moon",
    "Mercury": "Mercury",
    "Venus": "Venus",
    "Mars": "Mars",
    "Jupiter": "Jupiter",
    "Saturn": "Saturn",
    "Uranus": "Uranus",
    "Neptune": "Neptune",
    "Pluto": "Pluto",
    "Ascendant": "Ascendant",
    "Midheaven": "Midheaven",
    "Descendant": "Descendant",
    "Imum Coeli": "IC",
    "Fortune": "Fortune",
    "Chiron": "Chiron",
    "Vertex": "Vertex",
    "Lilith": "Lilith",
}

SIGN_VIBE_EN = {
    "Aries": "direct and fast-moving",
    "Taurus": "steady and grounded",
    "Gemini": "quick, curious, and mentally alert",
    "Cancer": "soft, protective, and emotionally aware",
    "Leo": "warm, visible, and self-possessed",
    "Virgo": "measured, precise, and composed",
    "Libra": "diplomatic and balanced",
    "Scorpio": "private, intense, and controlled",
    "Sagittarius": "open, candid, and future-facing",
    "Capricorn": "serious, contained, and goal-oriented",
    "Aquarius": "independent and unmistakably individual",
    "Pisces": "intuitive, porous, and fluid",
}

HOUSE_ARENA_EN = {
    1: "identity and the way you carry yourself",
    2: "self-worth, security, and resources",
    3: "language, tone, and everyday communication",
    4: "home, emotional grounding, and private life",
    5: "expression, creativity, and what brings you alive",
    6: "routine, work habits, and daily systems",
    7: "close relationships and the way you meet another person",
    8: "trust, vulnerability, and emotional depth",
    9: "meaning, perspective, and the direction of your mind",
    10: "career, visibility, and public direction",
    11: "networks, communities, and future plans",
    12: "your inner world, retreat, and what happens offstage",
}

_RULER_SIGN_BALANCE_EN = {
    "Aries": {"gift": "more direct, brave, and willing to go first", "shadow": "too quick on the draw or overly reactive"},
    "Taurus": {"gift": "steady, reliable, and hard to knock off course", "shadow": "too fixed or slow to loosen your grip"},
    "Gemini": {"gift": "adaptable, articulate, and mentally agile", "shadow": "scattered or split between too many options"},
    "Cancer": {"gift": "emotionally intelligent, protective, and responsive", "shadow": "overly guarded, moody, or quick to withdraw"},
    "Leo": {"gift": "warm, expressive, and easy to feel", "shadow": "too proud to soften once hurt"},
    "Virgo": {"gift": "clear, thoughtful, and exacting in a useful way", "shadow": "over-editing, overthinking, or delaying too long"},
    "Libra": {"gift": "graceful, relational, and skilled at reading a room", "shadow": "stalling inside indecision or over-accommodation"},
    "Scorpio": {"gift": "deeply focused, loyal, and emotionally exact", "shadow": "too suspicious, controlling, or braced"},
    "Sagittarius": {"gift": "bold, expansive, and naturally future-facing", "shadow": "too blunt, too fast, or too willing to leap"},
    "Capricorn": {"gift": "solid, self-respecting, and quietly authoritative", "shadow": "too defended, burdened, or hard on yourself"},
    "Aquarius": {"gift": "independent, original, and hard to flatten into a type", "shadow": "too detached, distant, or hard to read"},
    "Pisces": {"gift": "imaginative, receptive, and intuitively tuned in", "shadow": "too uncontained, avoidant, or hard to ground"},
}

_RELATIONSHIP_SIGN_OPENING_EN = {
    "Aries": "clarity, honesty, and emotional momentum",
    "Taurus": "stability, consistency, and room to settle into the bond",
    "Gemini": "conversation, curiosity, and mental ease",
    "Cancer": "warmth, emotional safety, and a feeling of home",
    "Leo": "open affection, warmth, and a visible sense of being chosen",
    "Virgo": "care, reliability, and attention to the small things",
    "Libra": "mutuality, fairness, and emotional reciprocity",
    "Scorpio": "honesty, depth, and emotional nakedness",
    "Sagittarius": "space, truth, and a shared horizon",
    "Capricorn": "trust, seriousness, and emotional backbone",
    "Aquarius": "closeness without losing your own shape",
    "Pisces": "softness, intuition, and emotional permeability",
}

_RULER_SIGN_BALANCE_TR = {
    "Aries": {"gift": "cesaret ve direktlik", "shadow": "sabırsızlık ya da ani tepki"},
    "Taurus": {"gift": "sağlamlık ve istikrar", "shadow": "fazla tutunma ya da değişimi geciktirme"},
    "Gemini": {"gift": "çeviklik ve ifade gücü", "shadow": "dağılma ya da kararı fazla çoğaltma"},
    "Cancer": {"gift": "sezgi ve koruyucu bir hassasiyet", "shadow": "fazla alınma ya da geri çekilme"},
    "Leo": {"gift": "sıcaklık ve görünür bir ifade", "shadow": "gurur kırıldığında sert kapanma"},
    "Virgo": {"gift": "berraklık ve edit gücü", "shadow": "fazla inceleme ya da gecikme"},
    "Libra": {"gift": "denge ve ilişki zekası", "shadow": "kararı fazla tartıp geciktirme"},
    "Scorpio": {"gift": "odak ve derinlik", "shadow": "kuşku ya da fazla kontrol"},
    "Sagittarius": {"gift": "vizyon ve cesaret", "shadow": "fazla açılma ya da abartılı hız"},
    "Capricorn": {"gift": "omurga ve dayanıklılık", "shadow": "yükü gereğinden fazla içerde toplama"},
    "Aquarius": {"gift": "özgünlük ve bağımsızlık", "shadow": "mesafe ya da kopukluk"},
    "Pisces": {"gift": "sezgisel akış ve hayal gücü", "shadow": "dağılma ya da sınır kaybı"},
}

PRIMITIVE_SENTENCE_HINTS = {
    "inner_structure": "İçeride önce yapı ve çerçeve kuran bir omurga çalışıyor.",
    "self_definition": "Kimliğini netleştirme ihtiyacın güçlü olduğu için duruşun kolay silinmiyor.",
    "originality_drive": "Aynı anda kendi yolunu açmak isteyen özgün bir dürtü de var.",
    "big_picture_vision": "Sadece anı değil, büyük resmi de aynı anda duyma eğilimin belirgin.",
    "tone_sensitivity": "Sözün tonu ve yükü sende sadece ifade değil, güven meselesi de oluyor.",
    "inner_critic": "Standart yükseldiğinde içerdeki eleştirmen kolayca sesi büyütebiliyor.",
    "push_pull_drive": "Bir yanın hızlanmak isterken diğer yanın durup ölçmek istiyor.",
    "systems_thinking": "Parçaları bir sisteme bağlayınca zihnin ve üretimin güçleniyor.",
    "methodical_drive": "Hevesin en iyi sonuçlarını yöntem kurduğunda alıyorsun.",
    "intimacy_depth": "Yakınlık sende yüzeyden çok derinlik ve güven üzerinden kuruluyor.",
    "relational_security": "Bağ kurarken tutarlılık ve güven zemini senin için belirleyici.",
    "emotional_threshold": "Kalbin açılırken aynı anda korunma eşiği de devreye giriyor.",
    "transformative_bonding": "Gerçek bağlar sende sadece yakınlık değil, dönüşüm de yaratıyor.",
    "public_refinement": "Görünür olduğunda kaliteyi ve ince ayarı birlikte taşımak istiyorsun.",
    "visibility_sensitivity": "Dışarıdaki göz arttığında içerideki hassasiyet de yükseliyor.",
    "backstage_creation": "Bir şeyi önce görünmeden olgunlaştırma eğilimin güçlü.",
    "family_self_reliance": "Güveni çoğu zaman önce kendi içinde kurup sonra paylaşıyorsun.",
    "recharge_through_home": "Ev ve iç alan senin için gerçek bir toparlanma hattı gibi çalışıyor.",
    "creation_luck": "Şansın çoğu zaman üretim ve görünür deneme üzerinden açılıyor.",
    "meaningful_expansion": "Ufuk büyüdükçe enerjin de daha anlamlı bir akış buluyor.",
}

_COPY_STOPWORDS = {
    "ve",
    "ile",
    "bu",
    "bir",
    "da",
    "de",
    "gibi",
    "için",
    "daha",
    "çok",
    "ama",
    "hem",
    "sen",
    "sende",
    "senin",
    "olduğunda",
    "geldiğinde",
    "arttığında",
    "yükseldiğinde",
    "olgunlaştığında",
    "dengeye",
    "tarafın",
    "tarafı",
    "yapı",
}

_BLOCK_COPY_FALLBACKS = {
    "identity_aura": {
        "mechanism": "içeride hem sağlam kalmak hem kendi yolunu korumak istiyorsun",
        "shadow": "yük arttığında yönünü içerde yeniden toplamak isteyebilirsin",
        "gift": "bu yapı sana net, özgün ve güven veren bir duruş kazandırır",
    },
    "mind_voice": {
        "mechanism": "zihninde tartıp ayıklayarak en doğru formu bulmak istersin",
        "shadow": "iç standart yükselince akış gecikebilir",
        "gift": "bu yapı sana dayanıklılık ve berrak bir ifade kazandırır",
    },
    "drive_rhythm": {
        "mechanism": "bir şeyi sadece hissetmez, ona biçim de vermek istersin",
        "shadow": "ayrıntıda fazla oyalanıp akışı geciktirebilirsin",
        "gift": "bu yapı seni hem derin düşünen hem de kurabilen biri yapar",
    },
    "love_depth": {
        "mechanism": "yakınlık sende güvenle, açıklıkla ve korunma eşiğiyle birlikte çalışıyor",
        "shadow": "belirsiz bağlarda geri çekilme ya da fazla hassasiyet artabilir",
        "gift": "sahici bağlarda çok sıcak ve iyileştirici bir yakınlık kurarsın",
    },
    "career_visibility": {
        "mechanism": "görünürlük kadar içerde hazırlık ve kalite duygun da güçlü",
        "shadow": "hazır hissetmediğinde bekleme uzayabilir",
        "gift": "kalite ile etkiyi aynı yerde birleştirebilirsin",
    },
    "home_roots": {
        "mechanism": "kendi alanına dönmek sende sadece dinlenmek değil, ritmi geri kurmak anlamına geliyor",
        "shadow": "yükü tek başına üstlenmeye meyledebilirsin",
        "gift": "kendi alanında toplandığında dış dünyaya da daha rahat açılırsın",
    },
    "luck_creation": {
        "mechanism": "akış en çok içinden gelen şeyi somutlaştırdığında hızlanıyor",
        "shadow": "bekledikçe durgunluk artabilir",
        "gift": "yaratıcılığın görünür oldukça fırsatlar da çoğalıyor",
    },
}


FALLBACK_ARENA_BY_BLOCK = {
    "identity_aura": 1,
    "mind_voice": 3,
    "drive_rhythm": 9,
    "love_depth": 8,
    "career_visibility": 10,
    "home_roots": 4,
    "luck_creation": 5,
}

FALLBACK_SIGNATURES_BY_BLOCK = {
    "identity_aura": {
        "signature_id": "fallback_identity_chart_ruler",
        "spark": False,
        "chips": ["Duruş", "Yön", "Çerçeve"],
        "copy_tr": {
            "headline": "Dışarıdan ve içeriden",
            "teaser": "Dışarıda sağlam, içeride kendi yönünü korumak isteyen bir tarafın var.",
            "spark": "Kendini ortaya koyma biçimin, kararlarını ve duruşunu doğrudan etkiliyor.",
            "gift": "Bu yapı olgunlaştığında sana netlik ve istikrar kazandırır.",
            "watch": "Zorlandığında yönünü içerde yeniden toplamak isteyebilirsin.",
        },
    },
    "mind_voice": {
        "signature_id": "fallback_mind_voice",
        "spark": False,
        "chips": ["İç Ritim", "İnce Ayar", "Dayanıklılık"],
        "copy_tr": {
            "headline": "Karar verirken içinde ne oluyor",
            "teaser": "Başlatınca hızlanırsın; ama iç standardın bazen frene de basar.",
            "spark": "Sen karar verirken sadece seçmezsin; içinden tartar ve en doğru formu bulmak istersin.",
            "gift": "Bu yapı olgunlaştığında sana dayanıklılık ve güven veren bir netlik kazandırır.",
            "watch": "Denge bozulduğunda iç standart yükselir ve akış gecikebilir.",
        },
    },
    "drive_rhythm": {
        "signature_id": "fallback_drive_rhythm",
        "spark": False,
        "chips": ["Anlam", "Yapı", "Kurucu Zihin"],
        "copy_tr": {
            "headline": "Gücün en çok nerede belirginleşiyor",
            "teaser": "Sende yetenek, anlamı bir yapıya dönüştürebildiğin yerde parlıyor.",
            "spark": "Dağınık olanı toparlama ve sezgisel olanı anlaşılır hale getirme becerin güçlü.",
            "gift": "Bu yapı olgunlaştığında seni hem derin düşünen hem de kurabilen biri yapar.",
            "watch": "Yük arttığında ayrıntıda fazla oyalanabilir ya da iç standardın yüzünden akışı geciktirebilirsin.",
        },
    },
    "love_depth": {
        "signature_id": "fallback_love_depth",
        "spark": False,
        "chips": ["Güven", "Sadakat", "Derin Temas"],
        "copy_tr": {
            "headline": "Yakınlık sende nasıl açılıyor",
            "teaser": "Sende yakınlık yüzeyde kalmaz; güven kurdukça derinleşir.",
            "spark": "Sen bağ kurarken yalnızca sıcaklık değil, güven ve gerçek temas da istersin.",
            "gift": "Yakınlık sahici geldiğinde çok sadık, sıcak ve iyileştirici bir bağ kurarsın.",
            "watch": "Belirsiz ya da yarım duran bağlar seni çabuk yorabilir.",
        },
    },
    "career_visibility": {
        "signature_id": "fallback_career_visibility",
        "spark": False,
        "chips": ["Kalite", "Etki", "Görünürlük"],
        "copy_tr": {
            "headline": "Görünür olmadan önce",
            "teaser": "İşin güçlü; ama sen görünürlüğü önce içerde kurup sonra taşırsın.",
            "spark": "İş tarafında ilk dikkat çeken şey, yaptığın şeyin gerçekten güçlü olması.",
            "gift": "Olgun tarafında kalite ile etki aynı yerde birleşir.",
            "watch": "Baskı arttığında bekleme uzayabilir.",
        },
    },
    "home_roots": {
        "signature_id": "fallback_home_roots",
        "spark": False,
        "chips": ["Bağımsızlık", "Şarj", "Zemin"],
        "copy_tr": {
            "headline": "İç güvenin en çok nerede kuruluyor",
            "teaser": "Köklerde 'ben hallederim' refleksi güçlü; kendi alanın seni hızlı toplar.",
            "spark": "Ortama dağılıp sarsıldığında kendi alanına dönme ihtiyacın artıyor.",
            "gift": "Kendi alanında toparlandığında dış dünyaya da daha rahat açılıyorsun.",
            "watch": "Bazen yükü tek başına üstlenmeye meyledebilirsin.",
        },
    },
    "luck_creation": {
        "signature_id": "fallback_luck_creation",
        "spark": False,
        "chips": ["Yaratım", "Akış", "Canlılık"],
        "copy_tr": {
            "headline": "Şansın en kolay nerede açılıyor",
            "teaser": "Sende fırsat çoğu zaman tesadüf gibi değil; emek verdiğin yerde açılıyor.",
            "spark": "Bir şeyi sahiplenip ona emek verdiğinde hayat da orada karşılık vermeye başlıyor.",
            "gift": "İçinden gelen şeyi görünür kıldığında akış daha kolay hızlanıyor.",
            "watch": "Beklediğinde durgunlaşabilirsin.",
        },
    },
}


def _bridge(color_signature: Mapping[str, Any] | None) -> str:
    if not isinstance(color_signature, Mapping):
        return ""
    spark = str(((color_signature.get("copy_tr") or {}) if isinstance(color_signature.get("copy_tr"), Mapping) else {}).get("spark") or "").strip()
    if not spark:
        return ""
    return f"Buna eşlik eden ikinci ton da açık: {spark} "


def _planet_label(value: Any) -> str:
    return PLANET_LABELS_TR.get(str(value or "").strip(), str(value or "").strip())


def _planet_label_en(value: Any) -> str:
    return PLANET_LABELS_EN.get(str(value or "").strip(), str(value or "").strip())


def _sign_vibe(value: Any) -> str:
    return SIGN_VIBE_TR.get(str(value or "").strip(), "")


def _sign_vibe_en(value: Any) -> str:
    return SIGN_VIBE_EN.get(str(value or "").strip(), "")


def _sign_balance(sign: str) -> Dict[str, str]:
    payload = _RULER_SIGN_BALANCE_TR.get(str(sign or "").strip())
    return dict(payload) if isinstance(payload, dict) else {}


def _sign_balance_en(sign: str) -> Dict[str, str]:
    payload = _RULER_SIGN_BALANCE_EN.get(str(sign or "").strip())
    return dict(payload) if isinstance(payload, dict) else {}


def _house_arena(value: Any) -> str:
    resolved = _safe_house(value)
    return HOUSE_ARENA_TR.get(resolved, "") if resolved is not None else ""


def _house_arena_en(value: Any) -> str:
    resolved = _safe_house(value)
    return HOUSE_ARENA_EN.get(resolved, "") if resolved is not None else ""


def _house_ruler_payload(facts: Mapping[str, Any], house: int) -> tuple[str, str, int | None]:
    house_rulers = facts.get("house_rulers") if isinstance(facts.get("house_rulers"), Mapping) else {}
    payload = house_rulers.get(str(house)) if isinstance(house_rulers.get(str(house)), Mapping) else {}
    ruler = str(payload.get("primary_ruler") or "").strip()
    pos = payload.get("primary_ruler_pos") if isinstance(payload.get("primary_ruler_pos"), Mapping) else {}
    sign = str(pos.get("sign") or "").strip()
    return ruler, sign, _safe_house(pos.get("house"))


def _house_label(value: Any) -> str:
    resolved = _safe_house(value)
    return f"{resolved}. ev" if resolved is not None else ""


def _house_label_en(value: Any) -> str:
    resolved = _safe_house(value)
    if resolved is None:
        return ""
    suffix = "th"
    if resolved % 10 == 1 and resolved % 100 != 11:
        suffix = "st"
    elif resolved % 10 == 2 and resolved % 100 != 12:
        suffix = "nd"
    elif resolved % 10 == 3 and resolved % 100 != 13:
        suffix = "rd"
    return f"{resolved}{suffix} house"


def _planet_payload(facts: Mapping[str, Any], planet: str) -> tuple[str, int | None]:
    planets = facts.get("planets") if isinstance(facts.get("planets"), Mapping) else {}
    payload = planets.get(planet) if isinstance(planets.get(planet), Mapping) else {}
    return str(payload.get("sign") or "").strip(), _safe_house(payload.get("house"))


def _selection_signature_ids(selection: Mapping[str, Any]) -> set[str]:
    out: set[str] = set()
    for key in ("primary", "spine_signature", "spark_signature", "area_signature", "tone_modifier"):
        candidate = selection.get(key) if isinstance(selection.get(key), Mapping) else {}
        value = str(candidate.get("signature_id") or candidate.get("id") or "").strip()
        if value:
            out.add(value)
    return out


def _gift_clause_en(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    if value.lower().startswith(("you ", "your ", "there is ", "it becomes ")):
        return value
    return f"you come through as {value}"


def _shadow_clause_en(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    if value.lower().startswith(("you ", "your ", "there is ", "it can ")):
        return value
    return f"you can become {value}"


def _compact_join(parts: list[str]) -> str:
    return " ".join(part for part in parts if part).strip()


def _astro_item_label(item: Mapping[str, Any]) -> str:
    item_type = str(item.get("type") or "").strip().lower()

    if item_type == "placement":
        return _compact_join([_planet_label(item.get("planet")), _house_label(item.get("house"))])

    if item_type == "stellium":
        return _compact_join([_house_label(item.get("house")), "yoğunluğu"])

    if item_type == "house_emphasis":
        return _compact_join([_house_label(item.get("house")), "vurgusu"])

    if item_type == "house_ruler":
        return _compact_join(
            [
                _house_label(item.get("house")),
                "yöneticisi",
                _planet_label(item.get("ruler")),
                _house_label(item.get("ruler_house")),
            ]
        )

    if item_type == "angle":
        return _compact_join(
            [
                ANGLE_LABELS_TR.get(str(item.get("angle") or "").strip(), str(item.get("angle") or "").strip()),
                str(item.get("sign") or "").strip(),
            ]
        )

    if item_type == "aspect":
        return _compact_join(
            [
                _planet_label(item.get("planet1") or item.get("a")),
                ASPECT_LABELS_TR.get(str(item.get("aspect") or item.get("type_name") or "").strip().lower(), ""),
                _planet_label(item.get("planet2") or item.get("b")),
            ]
        )

    if item_type == "ruler_chain":
        return _compact_join([_house_label(item.get("house")), "yöneticisi", _house_label(item.get("target_house"))])

    if item_type == "retrograde":
        return _compact_join([_planet_label(item.get("planet")), "retro"])

    planet = _planet_label(item.get("planet"))
    house = _house_label(item.get("house") or item.get("target_house"))
    sign = str(item.get("sign") or "").strip()
    if planet and house:
        return _compact_join([planet, house])
    if planet and sign:
        return _compact_join([planet, sign])
    return ""


def _astro_item_label_en(item: Mapping[str, Any]) -> str:
    item_type = str(item.get("type") or "").strip().lower()

    if item_type == "placement":
        return _compact_join([_planet_label_en(item.get("planet")), _house_label_en(item.get("house"))])

    if item_type == "stellium":
        return _compact_join([_house_label_en(item.get("house")), "stellium"])

    if item_type == "house_emphasis":
        return _compact_join([_house_label_en(item.get("house")), "emphasis"])

    if item_type == "house_ruler":
        return _compact_join(
            [
                _house_label_en(item.get("house")),
                "ruler",
                _planet_label_en(item.get("ruler")),
                _house_label_en(item.get("ruler_house")),
            ]
        )

    if item_type == "angle":
        return _compact_join(
            [
                ANGLE_LABELS_EN.get(str(item.get("angle") or "").strip(), str(item.get("angle") or "").strip()),
                str(item.get("sign") or "").strip(),
            ]
        )

    if item_type == "aspect":
        return _compact_join(
            [
                _planet_label_en(item.get("planet1") or item.get("a")),
                ASPECT_LABELS_EN.get(str(item.get("aspect") or item.get("type_name") or "").strip().lower(), ""),
                _planet_label_en(item.get("planet2") or item.get("b")),
            ]
        )

    if item_type == "ruler_chain":
        return _compact_join([_house_label_en(item.get("house")), "ruler in", _house_label_en(item.get("target_house"))])

    if item_type == "retrograde":
        return _compact_join([_planet_label_en(item.get("planet")), "retrograde"])

    planet = _planet_label_en(item.get("planet"))
    house = _house_label_en(item.get("house") or item.get("target_house"))
    sign = str(item.get("sign") or "").strip()
    if planet and house:
        return _compact_join([planet, house])
    if planet and sign:
        return _compact_join([planet, sign])
    return ""


def _astro_hint(block_id: str, selection: Mapping[str, Any], facts: Mapping[str, Any]) -> str:
    labels: list[str] = []
    seen: set[str] = set()

    def add_label(value: str) -> None:
        clean = str(value or "").strip()
        if not clean:
            return
        key = clean.lower()
        if key in seen:
            return
        seen.add(key)
        labels.append(clean)

    for candidate in (selection.get("primary"), selection.get("color")):
        if not isinstance(candidate, Mapping):
            continue
        for item in candidate.get("astro_tokens") or []:
            if isinstance(item, Mapping):
                add_label(_astro_item_label(item))
            if len(labels) >= 2:
                break
        for item in candidate.get("evidence") or []:
            if isinstance(item, Mapping):
                add_label(_astro_item_label(item))
            if len(labels) >= 2:
                break
        if len(labels) >= 2:
            break

    for item in _fallback_evidence(block_id, facts):
        if isinstance(item, Mapping):
            add_label(_astro_item_label(item))
        if len(labels) >= 2:
            break

    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    raw_hint = ", ".join(labels[:2])
    return soft_public_astro_hint(
        block_id,
        raw_hint,
        seed=str(facts.get("seed") or ""),
        signature_id=str(primary.get("signature_id") or ""),
    )


def _astro_hint_en(block_id: str, selection: Mapping[str, Any], facts: Mapping[str, Any]) -> str:
    labels: list[str] = []
    seen: set[str] = set()

    def add_label(value: str) -> None:
        clean = str(value or "").strip()
        if not clean:
            return
        key = clean.lower()
        if key in seen:
            return
        seen.add(key)
        labels.append(clean)

    for candidate in (selection.get("primary"), selection.get("color")):
        if not isinstance(candidate, Mapping):
            continue
        for item in candidate.get("astro_tokens") or []:
            if isinstance(item, Mapping):
                add_label(_astro_item_label_en(item))
            if len(labels) >= 2:
                break
        for item in candidate.get("evidence") or []:
            if isinstance(item, Mapping):
                add_label(_astro_item_label_en(item))
            if len(labels) >= 2:
                break
        if len(labels) >= 2:
            break

    for item in _fallback_evidence(block_id, facts):
        if isinstance(item, Mapping):
            add_label(_astro_item_label_en(item))
        if len(labels) >= 2:
            break

    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    raw_hint = ", ".join(labels[:2])
    return soft_public_astro_hint_en(
        block_id,
        raw_hint,
        seed=str(facts.get("seed") or ""),
        signature_id=str(primary.get("signature_id") or ""),
    )


def _infer_arena_house(block_id: str, selection: Mapping[str, Any]) -> int:
    for candidate in (selection.get("primary"), selection.get("color")):
        if not isinstance(candidate, Mapping):
            continue
        for token in candidate.get("astro_tokens") or []:
            if not isinstance(token, Mapping):
                continue
            house = token.get("house") or token.get("target_house")
            resolved = _safe_house(house)
            if resolved is not None:
                return resolved
        for evidence in candidate.get("evidence") or []:
            if not isinstance(evidence, Mapping):
                continue
            house = evidence.get("house") or evidence.get("ruler_house")
            resolved = _safe_house(house)
            if resolved is not None:
                return resolved
    return FALLBACK_ARENA_BY_BLOCK.get(block_id, 1)


def _safe_house(value: Any) -> int | None:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return None
    return ivalue if 1 <= ivalue <= 12 else None


def _micro_mode(selection: Mapping[str, Any]) -> str:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    for evidence in primary.get("evidence") or []:
        if not isinstance(evidence, Mapping):
            continue
        aspect = str(evidence.get("aspect") or "").lower()
        if aspect in {"square", "opposition"}:
            return "hard"
        if aspect in {"trine", "sextile"}:
            return "soft"
        if aspect == "conjunction":
            return "conj"
    return "neutral"


def _micro_valence(selection: Mapping[str, Any]) -> str:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    if primary.get("spark"):
        return "growth"
    for evidence in primary.get("evidence") or []:
        if isinstance(evidence, Mapping) and str(evidence.get("aspect") or "").lower() in {"square", "opposition"}:
            return "repair"
    return "growth"


def _tone_planets(selection: Mapping[str, Any]) -> list[str]:
    planets: list[str] = []
    for candidate in (selection.get("primary"), selection.get("color")):
        if not isinstance(candidate, Mapping):
            continue
        for token in candidate.get("astro_tokens") or []:
            if not isinstance(token, Mapping):
                continue
            for key in ("planet", "a", "b"):
                value = str(token.get(key) or "").strip()
                if value and value not in {"ASC", "MC", "DSC", "IC"} and value not in planets:
                    planets.append(value)
        for evidence in candidate.get("evidence") or []:
            if not isinstance(evidence, Mapping):
                continue
            for key in ("planet", "planet1", "planet2", "ruler"):
                value = str(evidence.get(key) or "").strip()
                if value and value not in {"Ascendant", "Midheaven", "Descendant", "Imum Coeli"} and value not in planets:
                    planets.append(value)
    return planets


def _fallback_evidence(block_id: str, facts: Mapping[str, Any]) -> list[Dict[str, Any]]:
    planets = facts.get("planets") if isinstance(facts.get("planets"), Mapping) else {}
    house_rulers = facts.get("house_rulers") if isinstance(facts.get("house_rulers"), Mapping) else {}
    angle_signs = facts.get("angle_signs") if isinstance(facts.get("angle_signs"), Mapping) else {}

    def placement(planet: str) -> Dict[str, Any]:
        payload = planets.get(planet) if isinstance(planets.get(planet), Mapping) else {}
        return {"type": "placement", "planet": planet, "sign": payload.get("sign"), "house": payload.get("house")}

    def ruler(house: int) -> Dict[str, Any]:
        payload = house_rulers.get(str(house)) if isinstance(house_rulers.get(str(house)), Mapping) else {}
        pos = payload.get("primary_ruler_pos") if isinstance(payload.get("primary_ruler_pos"), Mapping) else {}
        return {
            "type": "house_ruler",
            "house": house,
            "cusp_sign": payload.get("cusp_sign"),
            "ruler": payload.get("primary_ruler"),
            "ruler_house": pos.get("house"),
        }

    mapping = {
        "identity_aura": [{"type": "angle", "angle": "ASC", "sign": angle_signs.get("ASC")}, ruler(1)],
        "mind_voice": [placement("Mercury"), ruler(3)],
        "drive_rhythm": [placement("Mars"), ruler(9)],
        "love_depth": [placement("Moon"), ruler(7)],
        "career_visibility": [{"type": "angle", "angle": "MC", "sign": angle_signs.get("MC")}, ruler(10)],
        "home_roots": [{"type": "angle", "angle": "IC", "sign": angle_signs.get("IC")}, ruler(4)],
        "luck_creation": [placement("Fortune"), placement("Jupiter")],
    }
    return mapping.get(block_id, [])


def _editorialize_copy_payload(block_id: str, copy_payload: Mapping[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    background_mode = "background" if block_id == "home_roots" else "core"
    for field in ("headline", "teaser", "core", "mechanism", "shadow", "gift", "spark", "watch"):
        value = str(copy_payload.get(field) or "").strip()
        mode = background_mode if field in {"shadow", "watch"} else "core"
        out[field] = apply_phrase_policy(value, mode=mode)
    return out


def _render_block(
    block_id: str,
    selection: Mapping[str, Any],
    seed: str,
    *,
    family: str,
    used_openings: list[str],
    used_bodies: list[str],
) -> Dict[str, Any]:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    arena_house = _infer_arena_house(block_id, selection)
    micro = choose_micro_example(
        seed=f"{seed}|{block_id}|{primary.get('signature_id')}",
        arena_house=arena_house,
        mode=_micro_mode(selection),
        tone_planets=_tone_planets(selection),
        valence=_micro_valence(selection),
    )
    copy_payload = _editorialize_copy_payload(block_id, dict(primary.get("copy_tr") or {}))
    slots = {
        "copy": copy_payload,
        "micro": str(micro or "").strip(),
        "bridge": _bridge(selection.get("color")),
    }
    return render_block_template(
        block_id=block_id,
        seed=seed,
        slots=slots,
        signature_id=str(primary.get("signature_id") or ""),
        preferred_family=family,
        used_openings=used_openings,
        used_bodies=used_bodies,
    )


def _fallback_selection(block_id: str, facts: Mapping[str, Any]) -> Dict[str, Any]:
    base = FALLBACK_SIGNATURES_BY_BLOCK[block_id]
    primary = {
        **base,
        "id": base["signature_id"],
        "score": 0.2,
        "evidence": _fallback_evidence(block_id, facts),
        "astro_tokens": [{"type": "fallback", "house": FALLBACK_ARENA_BY_BLOCK.get(block_id)}],
    }
    return {
        "primary": primary,
        "color": None,
        "spine_signature": primary,
        "spark_signature": None,
        "area_signature": None,
        "tone_modifier": None,
        "taxonomy_block_id": BLOCK_ALIAS_TO_TAXONOMY.get(block_id, block_id),
    }


def _ensure_sentence(text: str, fallback: str = "") -> str:
    value = str(text or fallback or "").strip()
    if not value:
        return ""
    return value if value[-1] in ".!?" else f"{value}."


def _first_clause(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    value = value.replace(";", ", ")
    return re.split(r"(?<=[.!?])\s+", value, maxsplit=1)[0].strip()


def _clean_copy_sentence(text: str, fallback: str = "") -> str:
    value = _first_clause(text or fallback)
    if not value:
        return _ensure_sentence(fallback)
    for prefix in (
        "iyi çalıştığında ",
        "en iyi hâlinde ",
        "en iyi halinde ",
        "doğru çalıştığında ",
        "olgun ifadesinde ",
        "olgun halinde ",
        "dengeye geldiğinde ",
        "zorlandığında ",
        "baskı yükseldiğinde ",
        "baskı arttığında ",
        "yerine oturduğunda ",
        "güvende hissettiğinde ",
        "bu yapı olgunlaştığında ",
        "yük arttığında ",
        "denge bozulduğunda ",
        "yorulduğunda ",
        "kırıldığında ",
    ):
        if value.lower().startswith(prefix):
            value = value[len(prefix) :].strip()
            break
    value = value.lstrip(",:; ")
    value = value.replace("’", "'")
    return _ensure_sentence(value, fallback)


_BALANCE_GIFT_LEADS = (
    "Bu yapı olgunlaştığında",
    "Olgun tarafında",
    "Dengeye geldiğinde",
    "Dengede olduğunda",
    "Yakınlık sahici geldiğinde",
    "Kendi alanında toparlandığında",
    "İçinden gelen şeyi görünür kıldığında",
)

_BALANCE_SHADOW_LEADS = (
    "Zorlandığında",
    "Denge bozulduğunda",
    "Yük arttığında",
    "Baskı arttığında",
    "Baskı yükseldiğinde",
    "Beklediğinde",
    "Yorulduğunda",
    "Kırıldığında",
)


def _strip_balance_lead(text: str, *, leads: tuple[str, ...]) -> str:
    value = _first_clause(text).strip().rstrip(".!?")
    if not value:
        return ""
    for lead in leads:
        if value.lower().startswith(lead.lower()):
            value = value[len(lead) :].strip(" ,;:")
            break
    if value:
        value = value[0].lower() + value[1:]
    return value


def _balance_sentence(gift: str, shadow: str) -> str:
    gift_clause = _strip_balance_lead(gift, leads=_BALANCE_GIFT_LEADS)
    shadow_clause = _strip_balance_lead(shadow, leads=_BALANCE_SHADOW_LEADS)
    if gift_clause and shadow_clause:
        return _ensure_sentence(f"İyi çalıştığında {gift_clause}; gölgesinde {shadow_clause}")
    if gift_clause:
        return _ensure_sentence(f"İyi çalıştığında {gift_clause}")
    if shadow_clause:
        return _ensure_sentence(f"Gölgesinde {shadow_clause}")
    return ""


def _split_public_sentences(text: str) -> list[str]:
    return [piece.strip() for piece in re.split(r"(?<=[.!?])\s+", str(text or "").strip()) if piece.strip()]


def _copy_tokens(text: str) -> set[str]:
    import re

    tokens = re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", str(text or "").lower())
    return {token for token in tokens if len(token) >= 3 and token not in _COPY_STOPWORDS}


def _copy_overlap(a: str, b: str) -> float:
    left = _copy_tokens(a)
    right = _copy_tokens(b)
    if not left or not right:
        return 0.0
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _choose_distinct_copy(candidates: list[Any], fallback: str, used: list[str]) -> str:
    fallback_clean = _clean_copy_sentence(fallback, fallback)
    for candidate in candidates:
        text = str(candidate or "").strip()
        if not text:
            continue
        cleaned = _clean_copy_sentence(text, fallback_clean)
        if not cleaned:
            continue
        if all(_copy_overlap(cleaned, prior) < 0.58 for prior in used if prior):
            return cleaned
    return fallback_clean


def _append_balance_to_body(body: str, gift: str, shadow: str, *, max_sentences: int = 4) -> str:
    balance = _balance_sentence(gift, shadow)
    if not balance:
        return str(body or "").strip()
    sentences = _split_public_sentences(body)
    if not sentences:
        return balance
    if any(_copy_overlap(balance, sentence) >= 0.72 for sentence in sentences):
        return " ".join(sentences)
    if len(sentences) >= max_sentences:
        merged = sentences[-1].rstrip(".!?")
        balance_clause = _strip_balance_lead(balance, leads=())
        sentences[-1] = _ensure_sentence(f"{merged}; {balance_clause}")
        return " ".join(sentences)
    sentences.append(balance)
    return " ".join(sentences)


def _personalize_identity_copy(copy_payload: Mapping[str, Any], facts: Mapping[str, Any]) -> Dict[str, str] | None:
    asc_sign = str(((facts.get("angle_signs") or {}) if isinstance(facts.get("angle_signs"), Mapping) else {}).get("ASC") or "").strip()
    _, ruler_sign, ruler_house = _house_ruler_payload(facts, 1)
    vibe = _sign_vibe(asc_sign)
    balance = _sign_balance(ruler_sign)
    arena = _house_arena(ruler_house)
    if not any((vibe, balance, arena)):
        return None

    teaser = str(copy_payload.get("teaser") or "").strip() or (
        f"İlk hissedilen şey çoğu zaman daha {vibe} bir duruşun olması." if vibe else ""
    )
    core = (
        f"İlk hissedilen şey çoğu zaman daha {vibe} bir duruşun olması; ama bunun altında kendi yönünü koruyan bir taraf da var."
        if vibe
        else str(copy_payload.get("core") or "").strip()
    )
    mechanism = str(copy_payload.get("mechanism") or "").strip()
    if arena:
        mechanism = (
            f"Kimliğin en çok {arena} tarafında sınanıyor; orada hem kendi çizgini korumak hem de yönünü kaybetmemek istiyorsun."
        )
    shadow = str(copy_payload.get("shadow") or "").strip()
    gift = str(copy_payload.get("gift") or "").strip()
    if balance.get("shadow"):
        shadow = f"{balance['shadow']} daha hızlı öne çıkabiliyor."
    if balance.get("gift"):
        gift = f"bu yapı sana {balance['gift']} kazandırıyor."
    return {
        "teaser": teaser,
        "core": _ensure_sentence(core),
        "mechanism": _ensure_sentence(mechanism),
        "shadow": _ensure_sentence(shadow),
        "gift": _ensure_sentence(gift),
    }


def _personalize_mind_copy(copy_payload: Mapping[str, Any], facts: Mapping[str, Any]) -> Dict[str, str] | None:
    angle_signs = facts.get("angle_signs") if isinstance(facts.get("angle_signs"), Mapping) else {}
    asc_sign = str(angle_signs.get("ASC") or "").strip()
    _, ruler_sign, ruler_house = _house_ruler_payload(facts, 1)
    outer_vibe = _sign_vibe(asc_sign)
    inner_vibe = _sign_vibe(ruler_sign)
    balance = _sign_balance(ruler_sign)
    arena = _house_arena(ruler_house)
    if not any((outer_vibe, inner_vibe, balance, arena)):
        return None

    teaser = (
        f"Dışarıda daha {outer_vibe} görünsen de zihnin içeride daha {inner_vibe} bir ritim taşıyabiliyor."
        if outer_vibe and inner_vibe
        else str(copy_payload.get("teaser") or "").strip()
    )
    core = "Bir şey sana çarptığında zihnin boşta kalmıyor; içeride hemen pozisyon alan bir tarafın çalışıyor."
    mechanism = str(copy_payload.get("mechanism") or "").strip()
    if arena:
        mechanism = (
            f"Bu hat en çok {arena} tarafında belirginleşiyor; bazen söylemeden önce uzun uzun tartman, bazen de bir anda çok netleşmen biraz bundan."
        )
    shadow = str(copy_payload.get("shadow") or "").strip()
    gift = str(copy_payload.get("gift") or "").strip()
    if balance.get("shadow"):
        shadow = f"{balance['shadow']} daha hızlı öne çıkabiliyor."
    if balance.get("gift"):
        gift = f"bu yapı sana {balance['gift']} kazandırıyor."
    return {
        "teaser": teaser,
        "core": core,
        "mechanism": mechanism,
        "shadow": shadow,
        "gift": gift,
    }


def _personalize_love_copy(copy_payload: Mapping[str, Any], facts: Mapping[str, Any]) -> Dict[str, str] | None:
    dsc_sign = str(((facts.get("angle_signs") or {}) if isinstance(facts.get("angle_signs"), Mapping) else {}).get("DSC") or "").strip()
    _, ruler_sign, ruler_house = _house_ruler_payload(facts, 7)
    opening = _RELATIONSHIP_SIGN_OPENING_TR.get(dsc_sign) if isinstance(_RELATIONSHIP_SIGN_OPENING_TR.get(dsc_sign), Mapping) else {}
    sign_balance = _RELATIONSHIP_SIGN_BALANCE_TR.get(dsc_sign) if isinstance(_RELATIONSHIP_SIGN_BALANCE_TR.get(dsc_sign), Mapping) else {}
    ruler_balance = (
        _RELATIONSHIP_RULER_SIGN_BALANCE_TR.get(ruler_sign)
        if isinstance(_RELATIONSHIP_RULER_SIGN_BALANCE_TR.get(ruler_sign), Mapping)
        else {}
    )
    arena = _house_arena(ruler_house)
    if not any((opening, sign_balance, ruler_balance, arena)):
        return None

    need = str(opening.get("need") or "").strip()
    teaser = (
        f"İlişkide önce {need} arıyorsun."
        if need
        else str(copy_payload.get("teaser") or "").strip()
    )
    core = str(copy_payload.get("core") or "").strip()
    if str(sign_balance.get("gift") or "").strip():
        core = "Kalbin yakınlığı hafif yaşamıyor; güven gördüğünde hızla derinleşiyor."
    mechanism = str(copy_payload.get("mechanism") or "").strip()
    if arena:
        mechanism = f"Bağ sende en çok {arena} tarafında açılıyor; bu yüzden gerçek açıklık arıyor ve sevildiğini hissedilir biçimde duymak istiyorsun."
    ruler_gift = str(ruler_balance.get("gift") or "").strip()
    if ruler_gift:
        mechanism = f"{mechanism.rstrip('.')}. Açıldığında {ruler_gift} tarafın da belirginleşiyor."
    shadow_parts = [str(sign_balance.get("shadow") or "").strip()]
    shadow = str(copy_payload.get("shadow") or "").strip()
    shadow_parts = [part for part in shadow_parts if part]
    if shadow_parts:
        shadow = f"{shadow_parts[0]} daha kolay tetiklenebiliyor."
    gift = str(copy_payload.get("gift") or "").strip()
    gift_parts = [str(sign_balance.get("gift") or "").strip()]
    gift_parts = [part for part in gift_parts if part]
    if gift_parts:
        gift = f"sende {gift_parts[0]} belirginleşiyor."
    return {
        "teaser": teaser,
        "core": _ensure_sentence(core),
        "mechanism": _ensure_sentence(mechanism),
        "shadow": _ensure_sentence(shadow),
        "gift": _ensure_sentence(gift),
    }


def _personalize_career_copy(copy_payload: Mapping[str, Any], facts: Mapping[str, Any]) -> Dict[str, str] | None:
    mc_sign = str(((facts.get("angle_signs") or {}) if isinstance(facts.get("angle_signs"), Mapping) else {}).get("MC") or "").strip()
    _, ruler_sign, ruler_house = _house_ruler_payload(facts, 10)
    mc_balance = _CAREER_MC_BALANCE_TR.get(mc_sign) if isinstance(_CAREER_MC_BALANCE_TR.get(mc_sign), Mapping) else {}
    ruler_balance = (
        _CAREER_RULER_SIGN_BALANCE_TR.get(ruler_sign)
        if isinstance(_CAREER_RULER_SIGN_BALANCE_TR.get(ruler_sign), Mapping)
        else {}
    )
    arena = _house_arena(ruler_house)
    if not any((mc_balance, ruler_balance, arena)):
        return None

    teaser = str(copy_payload.get("teaser") or "").strip()
    if str(mc_balance.get("gift") or "").strip():
        teaser = f"İş tarafında ilk okunan şey çoğu zaman sende {mc_balance['gift']} olması."
    core = "Görünür olmak sende yalnız çıkmak değil; işin içerden oturması da önemli."
    mechanism = str(copy_payload.get("mechanism") or "").strip()
    if arena:
        mechanism = f"Asıl motor en çok {arena} tarafında çalışıyor; bu yüzden görünmeden önce işi sağlamlaştırmak istiyorsun."
    ruler_gift = str(ruler_balance.get("gift") or "").strip()
    if ruler_gift:
        mechanism = f"{mechanism.rstrip('.')}. İçi dolduğunda {ruler_gift} tarafın da açılıyor."
    shadow = str(copy_payload.get("shadow") or "").strip()
    shadow_parts = [str(mc_balance.get("shadow") or "").strip()]
    shadow_parts = [part for part in shadow_parts if part]
    if shadow_parts:
        shadow = f"{shadow_parts[0]} daha kolay çalışabiliyor."
    gift = str(copy_payload.get("gift") or "").strip()
    gift_parts = [str(mc_balance.get("gift") or "").strip()]
    gift_parts = [part for part in gift_parts if part]
    if gift_parts:
        gift = f"sende {gift_parts[0]} belirginleşiyor."
    return {
        "teaser": teaser,
        "core": _ensure_sentence(core),
        "mechanism": _ensure_sentence(mechanism),
        "shadow": _ensure_sentence(shadow),
        "gift": _ensure_sentence(gift),
    }


def _personalize_block_copy(block_id: str, copy_payload: Mapping[str, Any], facts: Mapping[str, Any]) -> Dict[str, str] | None:
    if block_id == "identity_aura":
        return _personalize_identity_copy(copy_payload, facts)
    if block_id == "mind_voice":
        return _personalize_mind_copy(copy_payload, facts)
    if block_id == "love_depth":
        return _personalize_love_copy(copy_payload, facts)
    if block_id == "career_visibility":
        return _personalize_career_copy(copy_payload, facts)
    return None


def _identity_priority_copy(
    selection: Mapping[str, Any],
    primitive_ids: list[str],
    primary_copy: Mapping[str, Any],
) -> Dict[str, str] | None:
    signature_ids = {
        str(((selection.get(key) or {}) if isinstance(selection.get(key), Mapping) else {}).get("signature_id") or "")
        for key in ("primary", "spine_signature", "spark_signature", "area_signature", "tone_modifier")
    }
    primitive_set = {str(item) for item in primitive_ids}

    structure = bool(signature_ids & {"identity_1st_stellium", "identity_sun_angular", "fallback_identity_chart_ruler"}) or bool(
        primitive_set & {"inner_structure", "self_definition"}
    )
    originality = "identity_uranus_angular" in signature_ids or "originality_drive" in primitive_set
    vision = "identity_jupiter_neptune_vision" in signature_ids or "big_picture_vision" in primitive_set

    if not (structure and (originality or vision)):
        return None

    teaser = "Dışarıda sağlam, içeride farklı ve kendi yönünü kurmak isteyen bir tarafın var."
    core = "dışarıda sağlam duran ama içeride aynı çizgide kalıba sığmayan bir yapın var"
    mechanism = "çerçeve kurmak istersin ama o çerçevenin içinde kendi yolunu ve büyük resmi de duyman gerekir"
    shadow = "yükü fazla tek başına sırtlanabilir ya da aynı anda çok fazla olasılığı hissedip yönünü geciktirebilirsin"
    gift = "bu yapı sonunda yalnızca güçlü değil, özgün ve ufuk açan bir etkiye dönüşür"

    if structure and originality and not vision:
        teaser = "Dışarıda toplu, içeride kendi yolunu açan bir çizgin var."
        mechanism = "önce omurga kurup sonra o omurganın içinde farklı olanı ayırmak istersin"
        gift = "bu yapı sonunda sana hem güven veren hem de taklit edilemeyen bir duruş kazandırır"
    elif structure and vision and not originality:
        teaser = "Sağlam dururken aynı anda büyük resmi duyan bir tarafın var."
        core = "duruşunda omurga var ama o omurga sadece kontrol için değil, yön duygusu için de çalışıyor"
        mechanism = "ayrıntıyı tutarken içeride anlamı ve uzun resmi de kaybetmek istemezsin"
        gift = "bu yapı sonunda sana yön veren, toparlayıcı ve ufku geniş bir etki kazandırır"

    raw_teaser = str(primary_copy.get("teaser") or "").strip()
    if raw_teaser and "büyük resmi" in raw_teaser.lower() and "özgün" in raw_teaser.lower():
        teaser = raw_teaser

    return {
        "headline": "Kendi çizgin",
        "teaser": teaser,
        "core": _ensure_sentence(core),
        "mechanism": _ensure_sentence(mechanism),
        "shadow": _ensure_sentence(shadow),
        "gift": _ensure_sentence(gift),
        "spark": _clean_copy_sentence(primary_copy.get("spark") or "", core),
        "watch": _clean_copy_sentence(primary_copy.get("watch") or "", shadow),
    }


def _talent_priority_copy(
    selection: Mapping[str, Any],
    primitive_ids: list[str],
    primary_copy: Mapping[str, Any],
) -> Dict[str, str] | None:
    primitive_set = {str(item) for item in primitive_ids}
    signature_ids = {
        str(((selection.get(key) or {}) if isinstance(selection.get(key), Mapping) else {}).get("signature_id") or "")
        for key in ("primary", "spine_signature", "spark_signature", "area_signature", "tone_modifier")
    }
    if not (
        primitive_set
        & {
            "systems_thinking",
            "meaning_making",
            "creative_synthesis",
            "vision_to_structure",
            "pattern_recognition",
            "translational_intelligence",
            "implementation_power",
        }
        or signature_ids
        & {
            "drive_mars_trine_neptune_inspired_action",
            "drive_saturn_sextile_uranus_structured_change",
            "drive_mars_9th_method",
        }
    ):
        return None

    teaser = "Sende yetenek, anlamı bir yapıya dönüştürebildiğin yerde parlıyor."
    core = "dağınık olanı toparlayıp sezgisel olanı anlaşılır hale getirebilen bir tarafın var"
    mechanism = "bir şeyi sadece hissetmekle kalmaz, ona biçim verip başkalarının da tutabileceği bir düzene oturtmak istersin"
    shadow = "yük arttığında ayrıntıda fazla oyalanabilir ya da iç standardın yüzünden akışı geciktirebilirsin"
    gift = "bu yapı olgunlaştığında seni hem derin düşünen hem de kurabilen biri yapar"

    raw_teaser = str(primary_copy.get("teaser") or "").strip().lower()
    if "anlam" in raw_teaser and ("yapı" in raw_teaser or "biçim" in raw_teaser):
        teaser = str(primary_copy.get("teaser") or teaser).strip()

    return {
        "headline": "Gücün en çok nerede belirginleşiyor",
        "teaser": teaser,
        "core": _ensure_sentence(core),
        "mechanism": _ensure_sentence(mechanism),
        "shadow": _ensure_sentence(shadow),
        "gift": _ensure_sentence(gift),
        "spark": _clean_copy_sentence(primary_copy.get("spark") or "", core),
        "watch": _clean_copy_sentence(primary_copy.get("watch") or "", shadow),
    }


def _top_primitive_ids_for_block(block_id: str, primitive_hits: list[Mapping[str, Any]]) -> list[str]:
    taxonomy_block_id = BLOCK_ALIAS_TO_TAXONOMY.get(block_id, block_id)
    out: list[str] = []
    for hit in primitive_hits:
        if not isinstance(hit, Mapping):
            continue
        primitive_id = str(hit.get("primitive_id") or "")
        if not primitive_id:
            continue
        theme_bias = hit.get("theme_bias")
        if isinstance(theme_bias, list) and taxonomy_block_id not in [str(item) for item in theme_bias]:
            continue
        out.append(primitive_id)
        if len(out) >= 4:
            break
    return out


def _compose_copy(
    block_id: str,
    selection: Mapping[str, Any],
    primitive_hits: list[Mapping[str, Any]],
    facts: Mapping[str, Any],
) -> Dict[str, str]:
    primary = selection.get("spine_signature") if isinstance(selection.get("spine_signature"), Mapping) else selection.get("primary")
    spark = selection.get("spark_signature") if isinstance(selection.get("spark_signature"), Mapping) else {}
    area = selection.get("area_signature") if isinstance(selection.get("area_signature"), Mapping) else {}
    tone = selection.get("tone_modifier") if isinstance(selection.get("tone_modifier"), Mapping) else {}
    primary_copy = dict(primary.get("copy_tr") or {}) if isinstance(primary, Mapping) else {}
    spark_copy = dict(spark.get("copy_tr") or {}) if isinstance(spark, Mapping) else {}
    area_copy = dict(area.get("copy_tr") or {}) if isinstance(area, Mapping) else {}
    tone_copy = dict(tone.get("copy_tr") or {}) if isinstance(tone, Mapping) else {}

    primitive_ids = _top_primitive_ids_for_block(block_id, primitive_hits)
    primitive_lines = [PRIMITIVE_SENTENCE_HINTS.get(pid, "") for pid in primitive_ids]
    block_fallbacks = _BLOCK_COPY_FALLBACKS.get(block_id, {})

    core_fallback = primitive_lines[0] if primitive_lines else ""

    primitive_mechanism = primitive_lines[1] if len(primitive_lines) > 1 else ""
    if not primitive_mechanism or "birden fazla" in primitive_mechanism.lower():
        primitive_mechanism = str(block_fallbacks.get("mechanism") or "")
    mechanism_fallback = primitive_mechanism or "Bunun altında birden fazla iç dürtü aynı anda çalışıyor."

    primitive_shadow = primitive_lines[2] if len(primitive_lines) > 2 else ""
    if not primitive_shadow or "aynı güç" in primitive_shadow.lower():
        primitive_shadow = str(block_fallbacks.get("shadow") or "")
    shadow_fallback = primitive_shadow or "Zorlandığında aynı güç kendi içinde baskı veya duraksama yaratabiliyor."

    primitive_gift = primitive_lines[3] if len(primitive_lines) > 3 else ""
    if not primitive_gift or "dengeye geldiğinde" in primitive_gift.lower() or "iyi çalıştığında" in primitive_gift.lower():
        primitive_gift = str(block_fallbacks.get("gift") or "")
    gift_fallback = primitive_gift or "Dengeye geldiğinde bu yapı sende olgun ve güven veren bir etkiye dönüşüyor."

    if block_id == "identity_aura":
        identity_override = _identity_priority_copy(selection, primitive_ids, primary_copy)
        if identity_override:
            personalized = _personalize_block_copy(block_id, identity_override, facts)
            if personalized:
                identity_override.update({key: value for key, value in personalized.items() if str(value or "").strip()})
            return identity_override
    if block_id == "drive_rhythm":
        talent_override = _talent_priority_copy(selection, primitive_ids, primary_copy)
        if talent_override:
            return talent_override

    core = _choose_distinct_copy(
        [
            primary_copy.get("core"),
            primary_copy.get("spark"),
            spark_copy.get("spark"),
            primary_copy.get("teaser"),
        ],
        core_fallback,
        [],
    )
    mechanism = _choose_distinct_copy(
        [
            spark_copy.get("mechanism"),
            spark_copy.get("spark"),
            primary_copy.get("spark"),
            primitive_lines[1] if len(primitive_lines) > 1 else "",
        ],
        mechanism_fallback,
        [core],
    )
    shadow = _choose_distinct_copy(
        [
            spark_copy.get("shadow"),
            primary_copy.get("shadow"),
            primary_copy.get("watch"),
            tone_copy.get("watch"),
            primitive_lines[2] if len(primitive_lines) > 2 else "",
        ],
        shadow_fallback,
        [core, mechanism],
    )
    gift = _choose_distinct_copy(
        [
            area_copy.get("gift"),
            primary_copy.get("gift"),
            tone_copy.get("gift"),
            primitive_lines[3] if len(primitive_lines) > 3 else "",
        ],
        gift_fallback,
        [core, mechanism, shadow],
    )

    copy_payload = {
        "headline": str(primary_copy.get("headline") or area_copy.get("headline") or ""),
        "teaser": str(primary_copy.get("teaser") or area_copy.get("teaser") or ""),
        "core": core,
        "mechanism": mechanism,
        "shadow": shadow,
        "gift": gift,
        "spark": str(primary_copy.get("spark") or spark_copy.get("spark") or ""),
        "watch": str(primary_copy.get("watch") or spark_copy.get("watch") or ""),
    }
    personalized = _personalize_block_copy(block_id, copy_payload, facts)
    if personalized:
        copy_payload.update({key: value for key, value in personalized.items() if str(value or "").strip()})
    return copy_payload


def _micro_line_en(block_id: str, facts: Mapping[str, Any]) -> str:
    if block_id == "identity_aura":
        return "You usually read the room before you decide how fully to step in."
    if block_id == "mind_voice":
        return "A sentence often gets one more pass in your head before it leaves your mouth."
    if block_id == "drive_rhythm":
        return "Once the direction feels true, your momentum picks up fast."
    if block_id == "love_depth":
        return "You rarely open all at once; trust usually comes first."
    if block_id == "career_visibility":
        return "You want the work to feel solid before you make it public."
    if block_id == "home_roots":
        return "Your own space is where your system settles back into rhythm."
    if block_id == "luck_creation":
        return "Things tend to move once you stop hovering and actually put something out there."
    return ""


def _compose_copy_en(
    block_id: str,
    selection: Mapping[str, Any],
    primitive_hits: list[Mapping[str, Any]],
    facts: Mapping[str, Any],
) -> Dict[str, str]:
    _ = primitive_hits
    ids = _selection_signature_ids(selection)
    angle_signs = facts.get("angle_signs") if isinstance(facts.get("angle_signs"), Mapping) else {}
    asc_sign = str(angle_signs.get("ASC") or "").strip()
    dsc_sign = str(angle_signs.get("DSC") or "").strip()
    mc_sign = str(angle_signs.get("MC") or "").strip()
    ic_sign = str(angle_signs.get("IC") or "").strip()
    chart_ruler, chart_ruler_sign, chart_ruler_house = _house_ruler_payload(facts, 1)
    rel_ruler, rel_ruler_sign, rel_ruler_house = _house_ruler_payload(facts, 7)
    career_ruler, career_ruler_sign, career_ruler_house = _house_ruler_payload(facts, 10)
    home_ruler, home_ruler_sign, home_ruler_house = _house_ruler_payload(facts, 4)
    mercury_sign, mercury_house = _planet_payload(facts, "Mercury")
    mars_sign, mars_house = _planet_payload(facts, "Mars")
    fortune_sign, fortune_house = _planet_payload(facts, "Fortune")
    jupiter_sign, jupiter_house = _planet_payload(facts, "Jupiter")

    if block_id == "identity_aura":
        outer_vibe = _sign_vibe_en(asc_sign) or "measured and self-possessed"
        arena = _house_arena_en(chart_ruler_house) or "the way you move through life"
        balance = _sign_balance_en(chart_ruler_sign or asc_sign)
        teaser = f"People usually meet the more {outer_vibe} version of you first."
        core = "You rarely throw your whole self into a room immediately; you tend to take stock first and then decide how fully to step in."
        mechanism = f"Your chart ruler works through {arena}, so keeping your own line intact matters more to you than people first realise."
        if "identity_uranus_angular" in ids:
            mechanism = f"Your chart ruler works through {arena}, but there is also a strong refusal to become generic or predictable."
        elif "identity_jupiter_neptune_vision" in ids:
            mechanism = f"Your chart ruler works through {arena}, and there is usually a bigger picture running quietly behind your decisions."
        shadow = _shadow_clause_en(balance.get("shadow") or "you can over-manage yourself while trying to make the right move")
        gift = _gift_clause_en(balance.get("gift") or "steady, self-defined, and quietly compelling")
        return {
            "teaser": teaser,
            "core": _ensure_sentence(core),
            "mechanism": _ensure_sentence(mechanism),
            "shadow": _ensure_sentence(shadow),
            "gift": _ensure_sentence(gift),
        }

    if block_id == "mind_voice":
        inner_sign = mercury_sign or chart_ruler_sign
        inner_house = mercury_house or chart_ruler_house
        inner_vibe = _sign_vibe_en(inner_sign) or "fast, alert, and self-monitoring"
        arena = _house_arena_en(inner_house or 3) or "the way you think and speak"
        balance = _sign_balance_en(inner_sign)
        teaser = f"Your mind does not really idle; even when you look calm, there is usually another internal pass happening in the background."
        core = f"On the surface you can seem more contained, but underneath there is a much more {inner_vibe} mental pace."
        mechanism = f"This becomes especially visible around {arena}; you may hold a sentence back for a while and then suddenly say it with real force."
        if "mind_saturn_3rd_boundary" in ids:
            core = "You usually think before you speak, and once a sentence matters to you, you feel the weight of it."
        if "mind_mercury_rx_refine" in ids:
            shadow = "you can keep editing past the point where the thought is already ready"
            gift = "you are able to refine language until it becomes clear, exact, and trustworthy"
        else:
            shadow = _shadow_clause_en(balance.get("shadow") or "you can tighten around the wording and lose the timing")
            gift = _gift_clause_en(balance.get("gift") or "clear, precise, and trustworthy")
        return {
            "teaser": teaser,
            "core": _ensure_sentence(core),
            "mechanism": _ensure_sentence(mechanism),
            "shadow": _ensure_sentence(shadow),
            "gift": _ensure_sentence(gift),
        }

    if block_id == "drive_rhythm":
        drive_sign = mars_sign or chart_ruler_sign
        drive_house = mars_house or 9
        arena = _house_arena_en(drive_house) or "the way you build momentum"
        balance = _sign_balance_en(drive_sign)
        teaser = "Your momentum tends to grow when instinct has a direction, not just energy."
        core = "You usually work best when movement and meaning are linked; random effort drains you much faster than purposeful effort."
        mechanism = f"That shows up most clearly around {arena}; once the line of travel feels right, you can suddenly become much more decisive."
        if "drive_mars_opp_saturn_push_pull" in ids:
            shadow = "you can get stuck between the part of you that wants to move now and the part that wants to get it exactly right first"
            gift = "you end up with both courage and staying power"
        elif "drive_mars_trine_neptune_inspired_action" in ids:
            shadow = "inspiration can diffuse if it is not given a shape quickly enough"
            gift = "you know how to turn instinct and imagination into movement"
        else:
            shadow = _shadow_clause_en(balance.get("shadow") or "you can either scatter your force or hesitate too long at the edge of action")
            gift = _gift_clause_en(balance.get("gift") or "clearer, more focused, and easier to trust")
        return {
            "teaser": teaser,
            "core": _ensure_sentence(core),
            "mechanism": _ensure_sentence(mechanism),
            "shadow": _ensure_sentence(shadow),
            "gift": _ensure_sentence(gift),
        }

    if block_id == "love_depth":
        need = _RELATIONSHIP_SIGN_OPENING_EN.get(dsc_sign, "emotional safety and a real sense of being met")
        arena = _house_arena_en(rel_ruler_house) or "the way closeness actually unfolds"
        balance = _sign_balance_en(rel_ruler_sign or dsc_sign)
        teaser = f"You are not looking for chemistry without substance; in love you need {need}."
        core = "When you let someone in, it usually is not a light or half-hearted thing. The bond tends to matter to you in a real way."
        mechanism = f"This gets especially visible around {arena}; if the bond does not feel emotionally real, your system does not fully relax into it."
        if rel_ruler and rel_ruler_house:
            mechanism = f"{mechanism.rstrip('.')}. Part of that story runs through your {rel_ruler} placement, so closeness is rarely just about attraction for you."
        shadow = _shadow_clause_en(balance.get("shadow") or "ambiguity can keep you braced for too long")
        gift = _gift_clause_en(balance.get("gift") or "steady, warm, and deep in the way you love")
        return {
            "teaser": teaser,
            "core": _ensure_sentence(core),
            "mechanism": _ensure_sentence(mechanism),
            "shadow": _ensure_sentence(shadow),
            "gift": _ensure_sentence(gift),
        }

    if block_id == "career_visibility":
        arena = _house_arena_en(career_ruler_house) or "the way your public life actually gets built"
        balance = _sign_balance_en(career_ruler_sign or mc_sign)
        public_tone = _sign_balance_en(mc_sign)
        teaser = f"People often notice the {public_tone.get('gift', 'clarity and presence')} side of you first when it comes to work."
        core = "For you, visibility is rarely just about being seen. It also has to feel earned, coherent, and internally solid."
        mechanism = f"The real engine sits in {arena}; you usually want the work to hold together before you push it outward."
        if career_ruler and career_ruler_house:
            mechanism = f"{mechanism.rstrip('.')}. That is why public growth is usually tied to what your {career_ruler} is doing in the chart."
        shadow = _shadow_clause_en(public_tone.get("shadow") or balance.get("shadow") or "you can wait too long for the perfect moment to show the work")
        gift = _gift_clause_en(public_tone.get("gift") or balance.get("gift") or "able to make work feel both polished and substantial")
        return {
            "teaser": teaser,
            "core": _ensure_sentence(core),
            "mechanism": _ensure_sentence(mechanism),
            "shadow": _ensure_sentence(shadow),
            "gift": _ensure_sentence(gift),
        }

    if block_id == "home_roots":
        arena = _house_arena_en(home_ruler_house) or "your private rhythms"
        balance = _sign_balance_en(home_ruler_sign or ic_sign)
        teaser = "Home is not just where you rest. It is where you regulate."
        core = "Your private world usually does more than give you comfort; it gives your system a way to return to itself."
        mechanism = f"A lot of that runs through {arena}, so when your inner base feels off, the rest of life can start to feel louder and less workable."
        shadow = _shadow_clause_en(balance.get("shadow") or "you can end up carrying too much on your own before you let yourself reset")
        gift = _gift_clause_en(balance.get("gift") or "steadier and more resourced once you return to yourself")
        return {
            "teaser": teaser,
            "core": _ensure_sentence(core),
            "mechanism": _ensure_sentence(mechanism),
            "shadow": _ensure_sentence(shadow),
            "gift": _ensure_sentence(gift),
        }

    if block_id == "luck_creation":
        luck_sign = fortune_sign or jupiter_sign
        luck_house = fortune_house or jupiter_house
        arena = _house_arena_en(luck_house or 5) or "the part of life that opens when you express something real"
        balance = _sign_balance_en(luck_sign)
        teaser = "Your luck usually does not feel random. It tends to open when you actually move something from inside to outside."
        core = "Opportunity tends to build around expression, visibility, and the moments when you stop hovering and let something become real."
        mechanism = f"That becomes most obvious around {arena}; life tends to answer you once you stop keeping everything in draft."
        shadow = _shadow_clause_en(balance.get("shadow") or "hesitation can keep a door half-open for longer than necessary")
        gift = _gift_clause_en(balance.get("gift") or "faster to notice and use openings once something is real")
        return {
            "teaser": teaser,
            "core": _ensure_sentence(core),
            "mechanism": _ensure_sentence(mechanism),
            "shadow": _ensure_sentence(shadow),
            "gift": _ensure_sentence(gift),
        }

    return {
        "teaser": "There is a distinct inner pattern running through this part of your chart.",
        "core": "A clear internal pattern shapes this area of life.",
        "mechanism": "It tends to become visible once the pressure is real, not while everything is still hypothetical.",
        "shadow": "you can over-manage this part of yourself under pressure",
        "gift": "with maturity, it becomes steadier and easier to trust",
    }


def _render_block_en(
    block_id: str,
    selection: Mapping[str, Any],
    seed: str,
    *,
    family: str,
    facts: Mapping[str, Any],
    used_openings: list[str],
    used_bodies: list[str],
) -> Dict[str, Any]:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    copy_payload = dict(primary.get("copy_en") or {})
    slots = {
        "copy": copy_payload,
        "micro": _micro_line_en(block_id, facts),
        "bridge": "",
    }
    return render_block_template_en(
        block_id=block_id,
        seed=seed,
        slots=slots,
        signature_id=str(primary.get("signature_id") or ""),
        preferred_family=family,
        used_openings=used_openings,
        used_bodies=used_bodies,
    )


def _public_block_en(block_id: str, rendered: Mapping[str, Any], selection: Mapping[str, Any]) -> Dict[str, Any]:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    color = selection.get("color") if isinstance(selection.get("color"), Mapping) else {}
    raw_chips: list[str] = []
    for source in (primary.get("chips") or [], color.get("chips") or []):
        for chip in source:
            value = str(chip).strip()
            if value and value not in raw_chips and len(raw_chips) < 6:
                raw_chips.append(value)
    return clean_public_block_en(
        {
            "id": block_id,
            "headline": rendered.get("headline"),
            "teaser": rendered.get("teaser"),
            "subtitle": rendered.get("teaser"),
            "body": rendered.get("body") or "",
            "micro": rendered.get("micro") or "",
            "astro_hint": rendered.get("astro_hint"),
            "astro_sources": [],
            "chips": humanize_public_chips_en(block_id, raw_chips),
        }
    )


def _public_astro_sources(selection: Mapping[str, Any], facts: Mapping[str, Any]) -> list[str]:
    labels: list[str] = []
    seen: set[str] = set()

    def add_item(item: Mapping[str, Any] | None) -> None:
        if not isinstance(item, Mapping):
            return
        label = _astro_item_label(item)
        if not label:
            return
        key = label.lower()
        if key in seen:
            return
        seen.add(key)
        labels.append(label)

    for candidate in (selection.get("primary"), selection.get("color")):
        if not isinstance(candidate, Mapping):
            continue
        for item in candidate.get("evidence") or []:
            add_item(item if isinstance(item, Mapping) else None)
            if len(labels) >= 3:
                return labels
        for item in candidate.get("astro_tokens") or []:
            add_item(item if isinstance(item, Mapping) else None)
            if len(labels) >= 3:
                return labels

    block_id = str(selection.get("block_id") or "")
    for item in _fallback_evidence(block_id, facts):
        add_item(item if isinstance(item, Mapping) else None)
        if len(labels) >= 3:
            break
    return labels


def _public_block(block_id: str, rendered: Mapping[str, Any], selection: Mapping[str, Any], facts: Mapping[str, Any]) -> Dict[str, Any]:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    color = selection.get("color") if isinstance(selection.get("color"), Mapping) else {}
    raw_chips: list[str] = []
    for source in (primary.get("chips") or [], color.get("chips") or []):
        for chip in source:
            value = str(chip).strip()
            if value and value not in raw_chips and len(raw_chips) < 6:
                raw_chips.append(value)
    return clean_public_block_tr(
        {
        "id": block_id,
        "headline": rendered.get("headline"),
        "teaser": rendered.get("teaser"),
        "subtitle": rendered.get("teaser"),
        "body": _append_balance_to_body(
            str(rendered.get("body") or "").strip(),
            str(rendered.get("gift") or "").strip(),
            str(rendered.get("shadow") or rendered.get("watch") or "").strip(),
        ),
        "micro": rendered.get("micro") or "",
        "astro_hint": rendered.get("astro_hint"),
        "astro_sources": _public_astro_sources(selection, facts),
        "chips": humanize_public_chips(block_id, raw_chips),
        }
    )


def _debug_block(block_id: str, selection: Mapping[str, Any], rendered: Mapping[str, Any], facts: Mapping[str, Any]) -> Dict[str, Any]:
    primary = selection.get("primary") if isinstance(selection.get("primary"), Mapping) else {}
    color = selection.get("color") if isinstance(selection.get("color"), Mapping) else {}
    fallback_reason = None
    if str(primary.get("signature_id") or "").startswith("fallback_"):
        fallback_reason = "no_matching_signature"
    evidence = list(primary.get("evidence") or [])
    for item in color.get("evidence") or []:
        if item not in evidence:
            evidence.append(item)
    if len(evidence) < 2:
        for item in _fallback_evidence(block_id, facts):
            if item not in evidence:
                evidence.append(item)
    primitive_hits = selection.get("primitive_hits") if isinstance(selection.get("primitive_hits"), list) else []
    spine = selection.get("spine_signature") if isinstance(selection.get("spine_signature"), Mapping) else {}
    spine_contract = selection.get("spine_contract") if isinstance(selection.get("spine_contract"), Mapping) else {}
    spark = selection.get("spark_signature") if isinstance(selection.get("spark_signature"), Mapping) else {}
    area = selection.get("area_signature") if isinstance(selection.get("area_signature"), Mapping) else {}
    tone = selection.get("tone_modifier") if isinstance(selection.get("tone_modifier"), Mapping) else {}
    block_primitive_ids = set(_top_primitive_ids_for_block(block_id, primitive_hits))
    return {
        "id": block_id,
        "engine": "signature",
        "block_id": block_id,
        "seed": facts.get("seed"),
        "seed_material": facts.get("seed"),
        "seed_version": SEED_VERSION,
        "selected_template_index": rendered.get("template_index"),
        "render_mode": rendered.get("mode"),
        "render_mode_label": rendered.get("mode_label"),
        "template_id": f"{block_id}:body_4step",
        "selected_template_id": f"{block_id}:body_4step:{rendered.get('template_index')}",
        "template_variant_id": f"{block_id}:body_4step:{rendered.get('template_index')}",
        "primary_signature_id": primary.get("signature_id"),
        "spark_signature_id": spark.get("signature_id"),
        "area_signature_id": area.get("signature_id"),
        "tone_modifier_id": tone.get("signature_id"),
        "score_primary": primary.get("score"),
        "primary_score": primary.get("score"),
        "spark_score": spark.get("score"),
        "area_score": area.get("score"),
        "color_signature_id": color.get("signature_id"),
        "score_color": color.get("score"),
        "color_score": color.get("score"),
        "evidence": evidence,
        "astro_evidence": [{"type": item.get("type"), "ref": _astro_item_label(item)} for item in evidence if isinstance(item, Mapping)],
        "primitive_hits": [{"primitive_id": item.get("primitive_id"), "score": item.get("score")} for item in primitive_hits],
        "selected_spine_primitive_ids": [item.get("primitive_id") for item in primitive_hits if item.get("category_hint") == "spine" and item.get("primitive_id") in block_primitive_ids][:3],
        "selected_spark_primitive_ids": [item.get("primitive_id") for item in primitive_hits if item.get("spark") and item.get("primitive_id") in block_primitive_ids][:3],
        "selected_tone_primitive_ids": [item.get("primitive_id") for item in primitive_hits if item.get("category_hint") == "tone" and item.get("primitive_id") in block_primitive_ids][:3],
        "taxonomy_block_id": selection.get("taxonomy_block_id"),
        "spine_target_slot": spine_contract.get("slot"),
        "spine_target_line_id": spine_contract.get("line_id"),
        "spine_target_label": spine_contract.get("label"),
        "spine_alignment_bonus": selection.get("spine_alignment_bonus"),
        "fallback_reason": fallback_reason,
    }


def build_profile_narrative_signature(
    chart: Mapping[str, Any],
    natal_graph: Mapping[str, Any],
    locale: str = "tr",
    include_debug: bool = False,
    seed_key: str | None = None,
    block_spine_contract: Mapping[str, Mapping[str, Any]] | None = None,
) -> Dict[str, Any]:
    locale = (locale or "tr").lower()
    use_en = locale.startswith("en")
    facts = normalize_facts(chart, natal_graph)
    if seed_key:
        facts = dict(facts)
        facts["seed"] = seed_key
    primitive_hits = build_primitives(chart, natal_graph, facts=facts)
    candidates = extract_candidates(facts, SIGNATURE_CATALOG_TR)
    selected = select_by_block(
        candidates,
        facts,
        primitive_hits=primitive_hits,
        block_spine_contract=block_spine_contract,
    )

    public_blocks = []
    debug_blocks = []
    used_families: list[str] = []
    used_openings: list[str] = []
    used_bodies: list[str] = []
    for block_id in BLOCK_ORDER:
        selection = selected.get(block_id) or _fallback_selection(block_id, facts)
        selection = dict(selection)
        selection["block_id"] = block_id
        selection["primitive_hits"] = primitive_hits
        selection["spine_contract"] = (
            block_spine_contract.get(block_id)
            if isinstance(block_spine_contract, Mapping) and isinstance(block_spine_contract.get(block_id), Mapping)
            else {}
        )
        selection.setdefault("spine_alignment_bonus", 0.0)
        primary = selection.get("primary")
        if isinstance(primary, dict):
            if use_en:
                primary["copy_en"] = _compose_copy_en(block_id, selection, primitive_hits, facts)
            else:
                primary["copy_tr"] = _compose_copy(block_id, selection, primitive_hits, facts)
        family = select_rhythm_family(str(facts.get("seed") or ""), "profile_narrative", block_id, used_families)
        if use_en:
            rendered = _render_block_en(
                block_id,
                selection,
                str(facts.get("seed") or ""),
                family=family,
                facts=facts,
                used_openings=used_openings,
                used_bodies=used_bodies,
            )
            rendered["astro_hint"] = _astro_hint_en(block_id, selection, facts) or None
        else:
            rendered = _render_block(
                block_id,
                selection,
                str(facts.get("seed") or ""),
                family=family,
                used_openings=used_openings,
                used_bodies=used_bodies,
            )
            rendered["astro_hint"] = _astro_hint(block_id, selection, facts) or None
        used_families.append(str(rendered.get("mode_label") or family))
        if rendered.get("opening_key"):
            used_openings.append(str(rendered.get("opening_key") or ""))
        if rendered.get("body"):
            used_bodies.append(str(rendered.get("body") or ""))
        public_blocks.append(
            _public_block_en(block_id, rendered, selection)
            if use_en
            else _public_block(block_id, rendered, selection, facts)
        )
        if include_debug:
            debug_blocks.append(_debug_block(block_id, selection, rendered, facts))

    payload: Dict[str, Any] = {
        "profile_public": {
            "engine_version": ENGINE_VERSION,
            "blocks": public_blocks,
        }
    }
    if include_debug:
        payload["profile_internal"] = {"blocks_debug": debug_blocks}
    return payload
