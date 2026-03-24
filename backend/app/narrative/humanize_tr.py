from __future__ import annotations

import re
from typing import Any, Mapping

from app.narrative.gold_natal_tone import NATAL_FORBIDDEN_LEXICON

_TECH_REPLACEMENTS = (
    (r"\borb\b", "etki payı"),
    (r"\bapplying\b", "yaklaşan"),
    (r"\bseparating\b", "geri çekilen"),
    (r"\bconjunction\b", "kavuşum"),
    (r"\bopposition\b", "karşıtlık"),
    (r"\bsquare\b", "zorlayan açı"),
    (r"\btrine\b", "uyumlu etki"),
    (r"\bsextile\b", "destekleyici etki"),
    (r"\bphase\b", "evre"),
    (r"\btransit\b", "geçiş etkisi"),
    (r"\bnatal\b", "doğum haritası"),
    (r"\bmarker\b", "işaret"),
    (r"\bscore\b", "etkinin gücü"),
    (r"\bexactish\b", "en yoğun noktaya yakın"),
)

_TONE_SOFTENERS = (
    (r"\bkesinlikle\b", "çoğu durumda"),
    (r"\bkesin\b", "daha net"),
    (r"\bmutlaka\b", "mümkünse"),
    (r"\bkritik\b", "önemli"),
)


def cleanup_tr_punctuation(text: str) -> str:
    out = str(text or "").strip()
    if not out:
        return ""
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    out = re.sub(r"([,.;:!?])([^\s])", r"\1 \2", out)
    out = re.sub(r"\s+", " ", out).strip()
    out = re.sub(r"([.!?])[.!?]+", r"\1", out)
    return out


def split_tr_sentences(text: str) -> list[str]:
    raw = str(text or "").strip()
    if not raw:
        return []
    protected = re.sub(r"(\b\d{1,2})\.\s*(ev\w*)\b", r"\1__EV_DOT__ \2", raw, flags=re.IGNORECASE)
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", protected) if part.strip()]
    return [part.replace("__EV_DOT__", ".").strip() for part in parts]


def cleanup_duplicate_sentences(text: str) -> str:
    parts = split_tr_sentences(text)
    deduped: list[str] = []
    seen: set[str] = set()
    for part in parts:
        key = re.sub(r"[^a-z0-9çğıöşü]+", " ", part.lower())
        key = re.sub(r"\s+", " ", key).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(part)
    return " ".join(deduped).strip() if deduped else str(text or "").strip()


def sentence_safe_clamp(text: str, *, max_chars: int, max_sentences: int | None = None) -> str:
    out = cleanup_tr_punctuation(text)
    if not out:
        return ""

    parts = split_tr_sentences(out)
    if max_sentences and max_sentences > 0:
        parts = parts[:max_sentences]
    candidate = " ".join(parts).strip()
    if len(candidate) <= max_chars:
        return candidate

    best = ""
    current: list[str] = []
    for part in parts:
        tentative = " ".join(current + [part]).strip()
        if len(tentative) > max_chars:
            break
        current.append(part)
        best = tentative

    if best:
        return best
    return parts[0] if parts else out


def humanize_tr_text(text: str, *, max_sentences: int | None = None) -> str:
    out = str(text or "").strip()
    if not out:
        return ""

    paragraph_token = " __PARA_BREAK__ "
    out = out.replace("\n\n", paragraph_token)
    out = out.replace("\n", " ")
    out = re.sub(r"\s+", " ", out)
    for pattern, replacement in _TECH_REPLACEMENTS:
        out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)
    for pattern, replacement in _TONE_SOFTENERS:
        out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)
    out = re.sub(r"\b(Genel iklim|Dönemin havası):\s*\1:\s*", r"\1: ", out, flags=re.IGNORECASE)

    # Reduce dry parenthetical metadata in user-facing copy.
    out = re.sub(r"\((?:\s*[a-z_]+:\s*[^()]+)\)", "", out, flags=re.IGNORECASE)
    out = cleanup_tr_punctuation(out)
    out = cleanup_duplicate_sentences(out)

    if max_sentences and max_sentences > 0:
        limited = split_tr_sentences(out)
        if len(limited) > max_sentences:
            out = " ".join(limited[:max_sentences]).strip()

    if out and out[-1] not in ".!?":
        out += "."
    out = out.replace(paragraph_token, "\n\n").strip()
    return out


_PROFILE_FIELD_MAX_SENTENCES = {
    "headline": 1,
    "teaser": 2,
    "body": 4,
    "micro": 1,
    "astro_hint": 1,
}

_PROFILE_FIELD_MAX_CHARS = {
    "headline": 64,
    "teaser": 180,
    "body": 520,
    "micro": 170,
    "astro_hint": 96,
}

_PROFILE_WORD_REPLACEMENTS = (
    (r"\bupgrade\b", "yenilik"),
    (r"\bkalibrasyon\b", "iç denge"),
    (r"\biç ayar\b", "iç denge"),
    (r"\bsistem\s*\+\s*yenilik\b", "yapı ve yenilik"),
    (r"\bnetwork\b", "bağlantı"),
    (r"\biterasyon\b", "küçük yenileme"),
    (r"\btiming\b", "zamanlama"),
    (r"\bvitrin\b", "görünürlük"),
    (r"\bçıktı\b", "ortaya koyduğun şey"),
    (r"\bcikti\b", "ortaya koyduğun şey"),
    (r"\bworkflow\b", "akış"),
    (r"\boptimize\b", "netleştir"),
    (r"\bpaket\b", "biçim"),
)

_PROFILE_HEADLINE_REWRITES = {
    "karar alırken içinde olan şey": "Karar verirken içinde ne oluyor",
    "iç güvenini nerede kuruyorsun": "İç güvenin en çok nerede kuruluyor",
    "sende akış nerede hızlanıyor": "Şansın en kolay nerede açılıyor",
    "görünür olmadan önce": "Görünür olmadan önce sende olan şey",
}

_PROFILE_SENTENCE_REWRITES = {
    "yakınlık sende yüzey değil": "Yakınlık senin için yüzeyde kalan bir şey değil.",
    "yakınlık sende yüzey değil güven kurdukça büyür": "Yakınlık senin için yüzeyde kalmaz; güven kurdukça büyür.",
    "sende sevgi yüzey değil kök ister": "Sende sevgi yüzeyde kalmaz; kök ister.",
    "içeride söz senin kasın": "Sözü seçme ve yerli yerine koyma becerin güçlü.",
    "söz senin kasın": "Sözü seçme ve yerli yerine koyma becerin güçlü.",
    "sende kapı açan taraf şans sende tesadüf değil": "Şans sende çoğu zaman tesadüf gibi değil, hazırlığın açtığı bir kapı gibi çalışır.",
    "iş ve görünürlük hattında sende belirgin olan şey işin güçlü": "İş tarafında asıl dikkat çeken şey, yaptığın şeyin gerçekten güçlü olması.",
    "kimlik hattında yön duygusu ve büyük resim birlikte belirgin": "Sende yön duygusu ile büyük resmi birlikte taşıyan bir taraf var.",
    "kimlik hattında omurga ve özgünlük birlikte öne çıkıyor": "Sende sağlam bir omurga ile özgünlük aynı anda hissediliyor.",
    "kimlik tarafında sağlam duruş ile farklılık aynı çizgide çalışıyor": "Sağlam duran ama farklı kalabilen bir tarafın var.",
    "zihin hattında netlik ve iç ayar birlikte çalışıyor": "Zihin tarafında netlik ile iç denge birlikte çalışıyor.",
    "zihinsel tarafta cümle disiplini ile sezgi aynı anda devrede": "Düşünürken hem cümle disiplinin hem sezgin birlikte çalışıyor.",
    "ifade hattında iç düzen ve ton hassasiyeti öne çıkıyor": "İfade tarafında iç düzen ile ton hassasiyeti birlikte öne çıkıyor.",
    "hareket hattında ritim ve yön duygusu birlikte öne çıkıyor": "Harekete geçerken ritim ile yön duygun birlikte çalışıyor.",
    "eylem tarafında cesaret ile ölçü aynı anda çalışıyor": "Eylemde cesaret ile ölçü aynı anda devreye giriyor.",
    "ivme hattında ataklık ile ayar duygusu birlikte belirgin": "İvmende ataklık ile ince ayar duygusu birlikte hissediliyor.",
    "ilişki temasında güven ve derinlik öne çıkıyor": "İlişkide güven ile derinlik birlikte çalışıyor.",
    "bağ kurma tarafında yakınlık ile korunma eşiği birlikte çalışıyor": "Bağ kurarken yakınlık isteğinle korunma eşiğin aynı anda devreye giriyor.",
    "yakınlık hattında sıcaklık kadar güven zemini de belirleyici": "Yakınlıkta sıcaklık kadar güven zemini de belirleyici.",
    "kariyer hattında görünürlük ve kalite standardı birlikte çalışıyor": "Görünürlük söz konusu olduğunda kalite standardın da aynı anda yükseliyor.",
    "toplumsal tarafta etki ile incelik aynı anda öne çıkıyor": "Toplum önünde hem etkili hem de incelikli bir iz bırakıyorsun.",
    "iş hattında görünürlük isteği ile hazırlık duygusu birlikte belirgin": "İş tarafında görünür olma isteğinle hazırlık duygun birlikte çalışıyor.",
    "iç güven hattında düzen ve toparlanma ihtiyacı belirgin": "İç güvenin en çok düzen ve toparlanma duygusuyla kuruluyor.",
    "ev tarafında korunma duygusu ile ritim kurma ihtiyacı birlikte çalışıyor": "Ev tarafında korunma duygunla ritim kurma ihtiyacın birlikte çalışıyor.",
    "köklerinde güven zemini ve iç toparlanma birlikte öne çıkıyor": "Köklerinde güven duygusu ile iç toparlanma birlikte öne çıkıyor.",
    "fırsat hattında üretim ve anlam duygusu birlikte açılıyor": "Fırsatların en çok üretimle anlam duygusu birleştiğinde açılıyor.",
    "akış tarafında cesaret ile sezgi aynı kapıyı çalıştırıyor": "Akışın en çok, cesaretinle sezgin aynı anda devreye girdiğinde açılıyor.",
    "şans hattında görünür deneme ile büyüme arzusu birlikte öne çıkıyor": "Şansın, görünür bir denemeyle büyüme arzusunu birleştirdiğinde açılıyor.",
    "küçük plan + ilk adım en iyi ilacın": "Böyle anlarda küçük bir plan kurup ilk adımı atınca daha hızlı toparlanırsın.",
    "tek sprint yaklaşımı iyi gelir": "Tek bir hatta odaklandığında zihnin daha hızlı netleşir.",
    "tek sprint seçmek seni uçurur": "Tek bir hatta odaklandığında hızın da netliğin de artar.",
    "küçük iterasyon en iyi yol": "Sende değişim çoğu zaman küçük yenilemelerle daha sağlam kurulur.",
    "sen anında vitrin değil önce kur sonra net paket yaklaşımıyla büyürsün": "Sende görünürlük bir anda değil, önce içeride kurup sonra netleştirdiğinde büyür.",
    "iç dünyan güçlü sezgiyle çalışırsın ama bunu net paketleyince etkili olursun": "İç dünyan güçlü; sezgiyle çalışırsın ama bunu netleştirdiğinde etkili olursun.",
    "toplumdaki rolün hedef ve itibar çizgisinde belirgin çıktı görünür oldukça büyür": "Toplumdaki rolün hedef ve itibar çizgisinde belirgin; ortaya koyduğun şey görünür oldukça büyür.",
    "kariyerin görünürlük ve hedef hattında doğrudan büyür çıktın konuşur": "Kariyerin görünürlük ve hedef tarafında büyür; ortaya koyduğun iş konuşur.",
    "yaratım ve görünür çıktı fırsat doğurur": "Yaratıcılığın görünür oldukça fırsat doğar.",
}

_PROFILE_DEBUGISH_PREFIXES = (
    "kimlik hattında",
    "kariyer hattında",
    "akış tarafında",
    "zihinsel tarafta",
)

_PROFILE_ASTRO_EVIDENCE_PATTERN = re.compile(
    r"(\b\d{1,2}\.\s*ev\b|"
    r"\b(?:merkür|merkur|güneş|gunes|ay|venüs|venus|mars|jüpiter|jupiter|satürn|saturn|uran[üu]s|nept[üu]n|pl[üu]ton)\b|"
    r"\b(?:kavuşum|kare|karşıt|karsit|üçgen|ucgen|sekstil|asc|mc|ic|dsc)\b)",
    re.IGNORECASE,
)

_PROFILE_RAW_ASTRO_HINT_PATTERN = re.compile(
    r"(\b(?:yükselen|tepe noktası|dip noktası|alçalan|ascendant|midheaven|descendant|imum coeli)\b|"
    r"\b(?:aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces)\b|"
    r"\b(?:koç|boğa|ikizler|yengeç|aslan|başak|terazi|akrep|yay|oğlak|kova|balık)\b)",
    re.IGNORECASE,
)

_PROFILE_MICRO_FALLBACKS = {
    "identity_aura": "Bir ortama girdiğinde önce kendi çizgini sessizce kurarsın.",
    "mind_voice": "Bir cümle çıkmadan önce onu içeride bir kez daha tartarsın.",
    "drive_rhythm": "Büyük resmi sade bir yapıya çevirdiğinde rahatlayıp hızlanırsın.",
    "love_depth": "Karşı taraf gerçek geldiğinde yakınlık hızla derinleşir.",
    "career_visibility": "İçine sinmeyen işi görünür kılmak istemezsin.",
    "home_roots": "Kendi alanına geçtiğinde ritmin kısa sürede toparlanır.",
    "luck_creation": "Bir şeyi keyif ve yaratıma çevirdiğinde enerjin hemen açılır.",
}

_PROFILE_ASTRO_HINT_FALLBACKS = {
    "identity_aura": "Sende sağlam bir omurga ile özgünlük aynı anda hissediliyor.",
    "mind_voice": "Zihin tarafında netlik ile iç denge birlikte çalışıyor.",
    "drive_rhythm": "Sende yetenek, anlamı bir yapıya dönüştürebildiğin yerde parlıyor.",
    "love_depth": "İlişkide güven ile derinlik aynı anda önem kazanıyor.",
    "career_visibility": "Kariyerde görünürlük kadar kalite standardın da güçlü.",
    "home_roots": "İç güvenin en çok düzen ve toparlanma duygusuyla kuruluyor.",
    "luck_creation": "Sende fırsat çoğu zaman tesadüf gibi değil; emek verdiğin yerde açılıyor.",
}

_PROFILE_MICRO_SCENE_REWRITES = {
    "bir ortama girdiginde tonu sessizce toplaman senden": "Bir ortama girdiğinde tonu sessizce toplaman senden.",
    "kalabalik arttiginda once kendi eksenini yoklaman cok tipik": "Kalabalık arttığında önce kendi eksenini yoklaman çok tipik.",
    "bir cumleyi zihninde tartip sonra daha sade kurman senden": "Bir cümleyi zihninde tartıp sonra daha sade kurman senden.",
    "daginik bir fikri icinde toparlayip tek bir cizgiye indirmen senden": "Dağınık bir fikri içinde toparlayıp tek bir çizgiye indirmen senden.",
    "yanlis anlasilma ihtimali hissedince kelimeleri icerde tekrar cevirmen senden": "Yanlış anlaşılma ihtimali hissedince kelimeleri içerde tekrar çevirmen senden.",
    "kendi alanina gecince ritmini hizla toparlaman senden": "Kendi alanına geçince ritmini hızla toparlaman senden.",
    "disarisi yorunca once icine cekilip guvenini evde kurman senden": "Dışarısı yorunca önce içine çekilip güvenini evde kurman senden.",
    "bir seyi oyun keyif ya da yaratim alanina cevirdiginde acilman senden": "Bir şeyi oyun, keyif ya da yaratım alanına çevirdiğinde açılman senden.",
    "kafandaki buyuk seyi sonunda sade bir yapiya indirmen senden": "Kafandaki büyük şeyi sonunda sade bir yapıya indirdiğinde rahatlaman senden.",
    "hevesin dagildiginda once icindeki keyif damarini araman senden": "Hevesin dağıldığında önce içindeki keyif damarını araman senden.",
    "yakinlik gercek geldigi anda hizla derinlesmen senden": "Yakınlık gerçek geldiği anda hızla derinleşmen senden.",
    "yakinlik artinca once icinden yoklayip sonra acilman cok tipik": "Yakınlık artınca önce içinden yoklayıp sonra açılman çok tipik.",
    "bir seyi anlamli bir ifadeye cevirdiginde enerjinin buyumesi senden": "Bir şeyi anlamlı bir ifadeye çevirdiğinde enerjinin büyümesi senden.",
    "yonu buldugunda gerisini yolda kurman senden": "Doğru damarı bulduğunda gerisini içeride netleştirmen senden.",
    "cok rota acildiginda once icerde yonunu yeniden toplaman senden": "Aynı anda çok fazla ihtimal açıldığında önce kendi yönünü içerden toplaman senden.",
    "is ciddilestiginde sesi yukseltmek yerine durusunla agirlik koyman senden": "İş ciddileştiğinde sesi yükseltmek yerine duruşunla ağırlık koyman senden.",
    "dogru anda one cikmadan once icten olcup sonra yerini alman senden": "Doğru anda öne çıkmadan önce içten ölçüp sonra yerini alman senden.",
    "gorunur olma ani yaklasinca once icerden olcup tartman senden": "Bir şeyi içine sindirmeden ortaya koymak istememen senden.",
    "bir grubun icinde kendi yerini sessizce netlestirmen senden": "Bir grubun içinde kendi yerini sessizce netleştirmen senden.",
    "insanlari birbirine dogru yerden baglaman senden": "İnsanları birbirine doğru yerden bağlaman senden.",
    "kalabalikta once havayi yoklayip sonra rengini koyman senden": "Kalabalıkta önce havayı yoklayıp sonra rengini koyman senden.",
    "bir seyi once icerde pisirip sonra paylasman senden": "Bir şeyi önce içerde olgunlaştırıp sonra paylaşman senden.",
    "icinde olgunlasan bir seyi tam zamani gelince disari cikarman senden": "İçinde olgunlaşan bir şeyi tam zamanı gelince dışarı çıkarman senden.",
    "hazir hissetmediginde biraz daha icerde tutup olgunlastirman senden": "Hazır hissetmediğinde biraz daha içerde tutup olgunlaştırman senden.",
}

_PROFILE_TEASER_FALLBACKS = {
    "identity_aura": "Dışarıda sağlam, içeride kendi yönünü kurmak isteyen bir tarafın var.",
    "mind_voice": "Başlatınca hızlanırsın; ama iç standardın bazen frene de basar.",
    "drive_rhythm": "Sende yetenek, anlamı bir yapıya dönüştürebildiğin yerde parlıyor.",
    "love_depth": "Sende yakınlık yüzeyde kalmaz; güven kurdukça derinleşir.",
    "career_visibility": "İşin güçlü; ama görünürlüğü önce içerde kurup sonra taşırsın.",
    "home_roots": "Köklerde ben hallederim refleksi güçlü; kendi alanın seni hızlı toplar.",
    "luck_creation": "Sende fırsat çoğu zaman tesadüf gibi değil; emek verdiğin yerde açılıyor.",
}

_PROFILE_MATURE_OPENERS = {
    "identity_aura": "Olgun tarafında",
    "mind_voice": "Yerine oturduğunda",
    "drive_rhythm": "Bu yapı olgunlaştığında",
    "love_depth": "Güvende hissettiğinde",
    "career_visibility": "En güçlü halinde",
    "home_roots": "Toparlandığında",
    "luck_creation": "Açıldığında",
}

_PROFILE_SHADOW_OPENERS = {
    "identity_aura": "Yorulduğunda",
    "mind_voice": "Denge bozulduğunda",
    "drive_rhythm": "Yük arttığında",
    "love_depth": "Kırıldığında",
    "career_visibility": "Baskı arttığında",
    "home_roots": "Sarsıldığında",
    "luck_creation": "Dağıldığında",
}

_PROFILE_STOPWORDS = {
    "ve",
    "ile",
    "bu",
    "bir",
    "da",
    "de",
    "için",
    "gibi",
    "daha",
    "çok",
    "ama",
    "hem",
    "sen",
    "sende",
    "senin",
    "olan",
    "olur",
    "oluyor",
    "olduğunda",
    "olgunlaştığında",
    "geldiğinde",
    "arttığında",
    "yükseldiğinde",
    "bozulduğunda",
    "birlikte",
    "taraf",
    "tarafın",
    "şey",
    "böylece",
    "bu yüzden",
}

_PROFILE_CHIP_REPLACEMENTS = {
    "Upgrade": "Yenilik",
    "Kalibrasyon": "İç Denge",
    "İç Ayar": "İç Denge",
    "İç ayar": "İç Denge",
    "Sistem + Yenilik": "Yapı ve Yenilik",
    "Network": "Bağlantı",
    "İnkübasyon": "İçte Olgunlaşma",
    "Pişirip Çık": "İçte Olgunlaşma",
}


def _profile_text_key(text: str) -> str:
    key = re.sub(r"[^a-z0-9çğıöşü]+", " ", str(text or "").lower())
    return re.sub(r"\s+", " ", key).strip()


def _ensure_tr_sentence(text: str) -> str:
    value = cleanup_tr_punctuation(text)
    if not value:
        return ""
    return value if value[-1] in ".!?" else f"{value}."


def _capitalize_tr_initial(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    first = value[:1]
    upper_first = {"i": "İ", "ı": "I"}.get(first, first.upper())
    return upper_first + value[1:]


def _semantic_tokens(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", str(text or "").lower())
    return {
        token
        for token in tokens
        if len(token) >= 3 and token not in _PROFILE_STOPWORDS
    }


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
    left = _profile_text_key(a)
    right = _profile_text_key(b)
    if not left or not right:
        return False
    if left == right or left in right or right in left:
        return True
    return _semantic_overlap(a, b) >= 0.72


def _rewrite_profile_sentence(sentence: str, *, field: str, block_id: str, sentence_count: int) -> str:
    value = cleanup_tr_punctuation(sentence)
    if not value:
        return ""

    for pattern, replacement in _PROFILE_WORD_REPLACEMENTS:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)

    key = _profile_text_key(value)
    if field == "headline" and key in _PROFILE_HEADLINE_REWRITES:
        return _PROFILE_HEADLINE_REWRITES[key]
    if key in _PROFILE_SENTENCE_REWRITES:
        return _PROFILE_SENTENCE_REWRITES[key]
    if field == "micro" and key in _PROFILE_MICRO_SCENE_REWRITES:
        return _PROFILE_MICRO_SCENE_REWRITES[key]
    if field == "teaser" and "başlatınca hızlanırsın" in key and "doğru mu" in key:
        return "Başlatınca hızlanırsın; ama içindeki ölçü duygusu bazen frene de basar."
    if sentence_count > 1 and re.match(r"^[\"'‘’]\s*gecikirse\b", value, flags=re.IGNORECASE):
        return ""

    if field in {"body", "micro"} and _PROFILE_ASTRO_EVIDENCE_PATTERN.search(value):
        return "" if sentence_count > 1 else _PROFILE_MICRO_FALLBACKS.get(block_id, "")

    value = re.sub(
        r"\bpişir(?:ip|mek|irken|ince)?\b",
        "olgunlaştır",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bpisir(?:ip|mek|irken|ince)?\b",
        "olgunlaştır",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\brota\b",
        "yön",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bYakınlık sende yüzey değil\b",
        "Yakınlık senin için yüzeyde kalmaz",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bSevgi sende yüzey değil\b",
        "Sende sevgi yüzeyde kalmaz",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\b(?:İçeride\s+)?Söz senin kasın\b",
        "Sözü seçme ve yerli yerine koyma becerin güçlü",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bşans sende tesadüf değil\b",
        "şans sende çoğu zaman tesadüf gibi işlemez",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bçıktın konuşur\b",
        "ortaya koyduğun iş konuşur",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bnet paketleyince\b",
        "netleştirince",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bnet paket\b",
        "netleştirilmiş hâli",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"Sen [\"'‘’]?anında vitrin[\"'‘’]? değil [\"'‘’]?önce kur,\s*sonra [^\"'‘’]+[\"'‘’]? yaklaşımıyla büyürsün",
        "Sende görünürlük bir anda değil, önce içeride kurup sonra netleştirdiğinde büyür",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bYaratım ve görünür çıktı fırsat doğurur\b",
        "Yaratıcılığın görünür oldukça fırsat doğar",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"^Yakınlık sende en çok,\s*Yakınlık senin için\s+",
        "Sende yakınlık ",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"Bir yanın görünür olmak isterken,\s*başka bir yanın Sende görünürlük bir anda değil,\s*önce içeride kurup sonra netleştirdiğinde büyür",
        "Bir yanın görünür olmak isterken, başka bir yanın önce içeride kurup sonra netleştirerek büyümek ister",
        value,
        flags=re.IGNORECASE,
    )

    if field in {"body", "micro"} and any(key.startswith(prefix) for prefix in _PROFILE_DEBUGISH_PREFIXES):
        mapped = _PROFILE_SENTENCE_REWRITES.get(key, "")
        if mapped:
            return mapped
        return "" if sentence_count > 1 else _PROFILE_MICRO_FALLBACKS.get(block_id, "")

    value = re.sub(r"^Sende düşünürken\b", "Düşünürken", value)
    value = re.sub(r"^Sende ilk hissedilen şey\b", "İlk hissedilen şey", value)
    value = re.sub(r"^Sende kapı açan taraf\b", "Sende fırsatları açan şey", value)
    value = re.sub(r"^Senin çizginde\b", "Sende", value)
    value = re.sub(r"\bİyi tarafı şu:\s*", "", value)
    value = re.sub(r"\bOlgun halinde\b", _PROFILE_MATURE_OPENERS.get(block_id, "Dengeye geldiğinde"), value)
    value = re.sub(r"\bİç ayar\b", "iç denge", value, flags=re.IGNORECASE)
    value = re.sub(r"\biyi çalıştığında\b", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\bDenge bozulduğunda yük arttığında\b", "Yük arttığında", value, flags=re.IGNORECASE)
    value = re.sub(r"\bOlgun tarafında iyi çalıştığında\b", "Olgun tarafında", value, flags=re.IGNORECASE)
    value = re.sub(r"\bGüvende hissettiğinde iyi çalıştığında\b", "Güvende hissettiğinde", value, flags=re.IGNORECASE)
    value = re.sub(r"\bToparlandığında iyi çalıştığında\b", "Toparlandığında", value, flags=re.IGNORECASE)
    value = re.sub(r"\bAçıldığında iyi çalıştığında\b", "Açıldığında", value, flags=re.IGNORECASE)
    value = re.sub(r"\bYerine oturduğunda iyi çalıştığında\b", "Yerine oturduğunda", value, flags=re.IGNORECASE)
    value = re.sub(r"\bEn güçlü halinde iyi çalıştığında\b", "En güçlü halinde", value, flags=re.IGNORECASE)
    value = re.sub(r"\bBazı anlarda da\b", "Bazen", value, flags=re.IGNORECASE)
    value = re.sub(r"\biyi gelir\b", "dengeyi kurar", value, flags=re.IGNORECASE)
    value = re.sub(r"\bToparlandığında kendi alanında toparlandığında\b", "Toparlandığında", value, flags=re.IGNORECASE)
    value = re.sub(
        r"Başlatınca hızlanırsın;\s*[\"'‘’]?\s*doğru mu\?\s*[\"'‘’]?\s*gecikirse frene basman kolay",
        "Başlatınca hızlanırsın; ama içindeki ölçü duygusu bazen frene de basar",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"erteleme ya da yeniden başlatma döngüsü artar[,;]\s*küçük ve net bir başlangıç ritmi geri toplar",
        "erteleme ya da yeniden başlama döngüsü artabilir; böyle anlarda küçük bir başlangıca sığmak seni yeniden merkeze getirir",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"dayanıklılık,\s*ustalık ve gerçek bir profesyonellik verir",
        "sana dayanıklılık, ustalık ve güven veren bir netlik kazandırır",
        value,
        flags=re.IGNORECASE,
    )

    mature_opener = _PROFILE_MATURE_OPENERS.get(block_id)
    if mature_opener:
        value = re.sub(r"^Dengeye geldiğinde\b", mature_opener, value)
        value = re.sub(r"^Bu tarafın olgun halinde\b", mature_opener, value)
        value = re.sub(r"^Olgun tarafında\b", mature_opener, value)

    shadow_opener = _PROFILE_SHADOW_OPENERS.get(block_id)
    if shadow_opener:
        value = re.sub(r"^Zorlandığında\b", shadow_opener, value)
        value = re.sub(r"^Baskı yükseldiğinde\b", shadow_opener, value)
        value = re.sub(r"^Kalbin yorulduğunda\b", shadow_opener, value)
        value = re.sub(r"^Gerilim yükseldiğinde\b", shadow_opener, value)
        value = re.sub(r"^Gerilim arttığında\b", shadow_opener, value)

    value = re.sub(r"^([A-Za-zÇĞİÖŞÜçğıöşü\s]+?)\s+\1\b", r"\1", value, flags=re.IGNORECASE)

    if field == "micro":
        lowered = value.lower()
        if any(token in lowered for token in ("iyi gelir", "gerekir", "önemli", "en iyi", "strateji", "ideal")):
            return _PROFILE_MICRO_FALLBACKS.get(block_id, value)
        if any(token in lowered for token in NATAL_FORBIDDEN_LEXICON):
            return _PROFILE_MICRO_FALLBACKS.get(block_id, value)

    return _capitalize_tr_initial(value)


def _vary_repeated_profile_starters(sentences: list[str]) -> list[str]:
    out: list[str] = []
    starter_counts: dict[str, int] = {}
    for sentence in sentences:
        value = sentence.strip()
        if not value:
            continue
        starter = " ".join(value.split()[:2]).lower()
        starter_counts[starter] = starter_counts.get(starter, 0) + 1
        if re.match(r"^Sende\b", value) and starter_counts[starter] >= 2:
            value = re.sub(r"^Sende\s+", "", value).strip()
        elif re.match(r"^Bu yüzden\b", value) and starter_counts[starter] >= 2:
            value = re.sub(r"^Bu yüzden\b", "Bu nedenle", value).strip()
        elif re.match(r"^Bunun altında\b", value) and starter_counts[starter] >= 2:
            value = re.sub(r"^Bunun altında\b", "İçeride", value).strip()
        elif re.match(r"^Bu tarafın\b", value) and starter_counts[starter] >= 2:
            value = re.sub(r"^Bu tarafın\b", "Burada", value).strip()
        out.append(value)
    return out


def _looks_like_micro_scene(text: str) -> bool:
    lowered = str(text or "").lower()
    return any(marker in lowered for marker in (" senden", " çok tipik", "ince ", "ınca ", "dığında ", "duğunda "))


def _dedupe_body_sentences(body: str) -> str:
    sentences = split_tr_sentences(body)
    filtered: list[str] = []
    for sentence in sentences:
        if any(_is_near_duplicate(sentence, prior) for prior in filtered):
            continue
        filtered.append(sentence)
    return " ".join(filtered).strip()


def _normalize_profile_block_fields(out: dict[str, Any], block_id: str) -> dict[str, Any]:
    teaser = str(out.get("teaser") or "").strip()
    body = str(out.get("body") or "").strip()
    micro = str(out.get("micro") or "").strip()
    astro_hint = str(out.get("astro_hint") or "").strip()
    first_body = split_tr_sentences(body)[0] if body else ""

    if body:
        deduped_body = _dedupe_body_sentences(body)
        if deduped_body:
            out["body"] = _ensure_tr_sentence(
                sentence_safe_clamp(
                    deduped_body,
                    max_chars=_PROFILE_FIELD_MAX_CHARS["body"],
                    max_sentences=_PROFILE_FIELD_MAX_SENTENCES["body"],
                )
            )
            body = str(out.get("body") or "").strip()
            first_body = split_tr_sentences(body)[0] if body else ""

    if teaser and first_body and _is_near_duplicate(teaser, first_body):
        fallback = _PROFILE_TEASER_FALLBACKS.get(block_id, teaser)
        out["teaser"] = naturalize_profile_tr_text(fallback, field="teaser", block_id=block_id)
        teaser = str(out.get("teaser") or "").strip()

    if micro and any(_is_near_duplicate(micro, candidate) for candidate in (teaser, body, first_body) if candidate):
        fallback_micro = _PROFILE_MICRO_FALLBACKS.get(block_id, micro)
        out["micro"] = naturalize_profile_tr_text(fallback_micro, field="micro", block_id=block_id)
        micro = str(out.get("micro") or "").strip()

    if astro_hint and any(_is_near_duplicate(astro_hint, candidate) for candidate in (teaser, first_body) if candidate):
        fallback_hint = _PROFILE_ASTRO_HINT_FALLBACKS.get(block_id, astro_hint)
        out["astro_hint"] = naturalize_profile_tr_text(fallback_hint, field="astro_hint", block_id=block_id)

    return out


def naturalize_profile_tr_text(
    text: str,
    *,
    field: str = "body",
    block_id: str = "",
    max_sentences: int | None = None,
) -> str:
    value = str(text or "").strip()
    if not value:
        return ""

    sentence_limit = max_sentences if max_sentences is not None else _PROFILE_FIELD_MAX_SENTENCES.get(field, 2)
    out = humanize_tr_text(value, max_sentences=sentence_limit)
    sentences = split_tr_sentences(out)
    rewritten = [
        _rewrite_profile_sentence(sentence, field=field, block_id=block_id, sentence_count=len(sentences))
        for sentence in sentences
    ]
    rewritten = _vary_repeated_profile_starters([sentence for sentence in rewritten if sentence.strip()])
    out = " ".join(rewritten).strip()
    out = cleanup_duplicate_sentences(out)
    out = cleanup_tr_punctuation(out)

    if field == "micro":
        if not out or not _looks_like_micro_scene(out):
            out = _PROFILE_MICRO_FALLBACKS.get(block_id, out)
        out = sentence_safe_clamp(out, max_chars=_PROFILE_FIELD_MAX_CHARS["micro"], max_sentences=1)
        return _ensure_tr_sentence(out) if out else ""

    if field == "headline":
        out = re.sub(r"[.!?]+$", "", out).strip()
        return out

    if field == "astro_hint" and (
        _PROFILE_ASTRO_EVIDENCE_PATTERN.search(out) or _PROFILE_RAW_ASTRO_HINT_PATTERN.search(out)
    ):
        out = _PROFILE_ASTRO_HINT_FALLBACKS.get(block_id, out)

    if field == "body":
        out = sentence_safe_clamp(out, max_chars=_PROFILE_FIELD_MAX_CHARS["body"], max_sentences=sentence_limit)
    else:
        out = sentence_safe_clamp(
            out,
            max_chars=_PROFILE_FIELD_MAX_CHARS.get(field, 180),
            max_sentences=sentence_limit,
        )

    out = out.replace("? '", "?'").replace("? ’", "?’").replace("! '", "!'").replace("! ’", "!’")

    return _ensure_tr_sentence(out) if out else ""


def clean_public_block_tr(block: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(block)
    block_id = str(out.get("id") or "").strip()

    for field in ("headline", "teaser", "body", "micro", "astro_hint"):
        raw = out.get(field)
        if not isinstance(raw, str):
            continue
        out[field] = naturalize_profile_tr_text(raw, field=field, block_id=block_id)

    chips = out.get("chips")
    if isinstance(chips, list):
        normalized_chips: list[str] = []
        seen: set[str] = set()
        for chip in chips:
            value = str(chip or "").strip()
            if not value:
                continue
            value = _PROFILE_CHIP_REPLACEMENTS.get(value, value)
            value = cleanup_tr_punctuation(value).strip(" .")
            key = value.lower()
            if not value or key in seen:
                continue
            seen.add(key)
            normalized_chips.append(value)
            if len(normalized_chips) >= 3:
                break
        out["chips"] = normalized_chips

    out = _normalize_profile_block_fields(out, block_id)

    return out


_NATAL_LAYER_STOPWORDS = {
    "ve",
    "ile",
    "bu",
    "bir",
    "da",
    "de",
    "için",
    "gibi",
    "ama",
    "daha",
    "çok",
    "sen",
    "sende",
    "senin",
    "şey",
    "olan",
    "olur",
    "ise",
    "hem",
}

_NATAL_LAYER_REPLACEMENTS = (
    (r"\britim hızın çarpanı\b", "netleştikçe akışın da toparlanıyor"),
    (r"\bküçük ve net bir başlangıç ritmi geri toplar\b", "böyle anlarda küçük bir başlangıca sığmak seni yeniden merkeze getirir"),
    (r"\britim bozulduğunda sistem yoruluyor, ritim oturduğunda ise çok hızlı toparlanıyorsun\b", "iç ritmin dağıldığında yoruluyorsun; yerine geldiğinde ise hızın da berraklığın da geri dönüyor"),
    (r"\britim bozulduğunda sistem yoruluyor\b", "iç ritmin dağıldığında daha çabuk yoruluyorsun"),
    (r"\britim oturduğunda ise çok hızlı toparlanıyorsun\b", "yerine geldiğinde ise kendini daha çabuk topluyorsun"),
    (r"\bküçük ama düzenli görünürlük adımlarıyla ritim kurmak\b", "görünürlüğü bir anda değil, kendi hızında taşımak"),
    (r"\byayınlanabilir iyi seviyesini tutarlı biçimde çoğaltmaktan geliyor\b", "her şeyi kusursuzlaştırmayı beklemeden görünür kılabildiğinde açılıyor"),
    (r"\ben güçlü anahtarın\b", "en güçlü yollarından biri"),
    (r"\badım adım açılmakla daha sağlıklı ilerliyor\b", "yavaş yavaş güven kazandığında daha doğal akıyor"),
    (r"\bküçük ve temiz bir sinyal verdiğinde\b", "duygunu küçük ama dürüst bir işaretle açtığında"),
    (r"\bperformansını en hızlı yükselten ritim\b", "en doğal çalışma biçimlerinden biri"),
    (r"\bGörünürlüğü küçük ve düzenli dozlarla taşıman\b", "Görünürlüğü bir anda değil, kendi hızında taşıman"),
)

_CORE_STORY_REPLACEMENTS = (
    (r"^Bu ihtiyaç yükseldiğinde,\s*", "Yük arttığında "),
    (r"^Böylece\s+", ""),
    (r"\bPsikolojik temelinde\b", "İçeride"),
)


def _semantic_dedupe(sentences: list[str], *, threshold: float = 0.84) -> list[str]:
    filtered: list[str] = []
    for sentence in sentences:
        if any(_semantic_overlap(sentence, prior) >= threshold for prior in filtered):
            continue
        filtered.append(sentence)
    return filtered


def _cleanup_natal_sentence(sentence: str, *, layer: str) -> str:
    value = cleanup_tr_punctuation(str(sentence or "").replace("‘", "'").replace("’", "'")).strip()
    if not value:
        return ""

    for pattern, replacement in _NATAL_LAYER_REPLACEMENTS:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)

    if layer == "core_story":
        for pattern, replacement in _CORE_STORY_REPLACEMENTS:
            value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
        quote_match = re.match(r"^İçeride(?:\s+sık(?:\s+sık)?)?\s+'?([^.!?']{6,})\.?$", value)
        if quote_match:
            prompt = quote_match.group(1).strip(" '").rstrip(" .!?")
            value = f"İçeride sık sık '{prompt}?' sorusu çalışıyor"
        value = re.sub(
            r"^İçeride\s+sık(?:\s+sık)?\s+'([^']+?)\.\s*'\s+sorusu çalışıyor\.?$",
            lambda m: f"İçeride sık sık '{m.group(1).strip()}?' sorusu çalışıyor",
            value,
            flags=re.IGNORECASE,
        )
        value = re.sub(r"^İçeride\s+Böylece\s+", "İçeride ", value, flags=re.IGNORECASE)

    value = re.sub(r",\s*([A-ZÇĞİÖŞÜ])", lambda m: ", " + m.group(1).lower(), value, count=1)
    value = re.sub(r"^Yük arttığında\s+([A-ZÇĞİÖŞÜ])", lambda m: "Yük arttığında " + m.group(1).lower(), value)
    value = re.sub(r"\s+\?'", "?'", value)
    value = re.sub(r"([?!])\s+'", r"\1'", value)
    value = re.sub(r"'\s+sorusu", "' sorusu", value)
    value = value.replace("? '", "?'").replace("! '", "!'")
    value = re.sub(r"\bçok daha rahat açılıyorsun\b", "daha rahat açılıyorsun", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value).strip(" ,;")
    value = _capitalize_tr_initial(value)
    return _ensure_tr_sentence(value) if value else ""


def _naturalize_natal_longform(text: str, *, max_sentences: int, layer: str) -> str:
    value = humanize_tr_text(text, max_sentences=max_sentences)
    sentences = split_tr_sentences(value)
    cleaned = [_cleanup_natal_sentence(sentence, layer=layer) for sentence in sentences]
    cleaned = [sentence for sentence in cleaned if sentence]
    cleaned = _semantic_dedupe(cleaned, threshold=0.82 if layer == "core_story" else 0.84)
    cleaned = _vary_repeated_profile_starters(cleaned)
    out = " ".join(cleaned).strip()
    out = cleanup_duplicate_sentences(out)
    out = cleanup_tr_punctuation(out)
    out = out.replace("? '", "?'").replace("! '", "!'").replace("' sorusu", "' sorusu")
    return out


def humanize_natal_core_story_tr(text: str) -> str:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", str(text or "").strip()) if part.strip()]
    if not paragraphs:
        return ""
    cleaned: list[str] = []
    for paragraph in paragraphs[:3]:
        normalized = _naturalize_natal_longform(paragraph, max_sentences=4, layer="core_story")
        if normalized:
            cleaned.append(normalized)
    return "\n\n".join(cleaned).strip()


def humanize_natal_layer_tr(text: str, *, max_sentences: int, layer: str) -> str:
    return _naturalize_natal_longform(text, max_sentences=max_sentences, layer=layer)


def humanize_compact_item(item: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(item)
    for field in ("title", "summary", "text", "condition", "how_to_use", "message"):
        value = out.get(field)
        if isinstance(value, str) and value.strip():
            out[field] = humanize_tr_text(value)
    return out
