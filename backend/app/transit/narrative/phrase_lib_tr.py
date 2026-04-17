from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Mapping, Sequence

from app.transit.narrative.point_policy import is_public_point, normalize_point_token

BLOCKED_TOKENS: set[str] = set()

# ----------------------------
# P0 LANGUAGE: strip tech tokens (BUT never remove ASC/DSC/MC/IC or planet names)
# ----------------------------
_TECH_TOKENS_RE = re.compile(
    r"(?ix)"
    r"\b("
    r"orb|orb_deg|degree|deg|exactish|exact|applying|separating|retrograde|rx|station"
    r"|percentile|marker|tier|bucket|phase|window_days|step_hours|raw|period"
    r")\b"
    r"|[°º]"
)

_TECH_VALUE_RE = re.compile(
    r"(?ix)"
    r"\b(?:orb|orb_deg)\s*[:=]?\s*\d+(?:[.,]\d+)?\b"
    r"|\b(?:t:\d+\s*->\s*n:\d+|n:\d+|t:\d+)\b"
)

HOUSE_LABEL_TR = {
    1: "kimlik/benlik",
    2: "değer/gelir",
    # 3.ev sadece “mesaj” değil: yakın çevre + öğrenme + iletişim tarzı + kısa yol trafiği
    3: "iletişim tarzı/öğrenme ritmi/yakın çevre",
    4: "ev/kök",
    5: "yaratıcılık/ifade",
    6: "rutin/sağlık",
    7: "ilişki/ortaklık",
    8: "derin bağ/dönüşüm",
    9: "anlam/ufuk/genişleme",
    10: "kariyer/görünürlük",
    11: "topluluk/hedef",
    12: "bilinçaltı/çözülme",
}

HOUSE_LIFE_SCENE_TR = {
    1: "kendini dışarıda nasıl taşıdığın",
    2: "para ve özdeğer dengesi",
    3: "mesajların, konuşmaların ve yakın çevre trafiğin",
    4: "ev düzenin ve iç güvenlik hissin",
    5: "yaratıcılık, keyif ve görünür üretim alanın",
    6: "iş düzenin, alışkanlıkların ve günlük akışın",
    7: "yakın ilişkilerde kurduğun denge",
    8: "yakınlık, güven ve paylaşım biçimin",
    9: "öğrenme, uzmanlaşma ve yön duygun",
    10: "kariyer yönün ve görünürlüğün",
    11: "arkadaş çevren, ekipler ve gelecek planların",
    12: "iç dünyan ve geri çekilme ihtiyacın",
}

PLANET_TR: Dict[str, str] = {
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
    "chiron": "Kiron",
    "lilith": "Lilith",
    "north_node": "Kuzey Ay Düğümü",
    "south_node": "Güney Ay Düğümü",
    "fortune": "Şans Noktası",
    "vertex": "Vertex",
}

SIGN_TR: Dict[str, str] = {
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

POINT_TR: Dict[str, str] = {
    "ASC": "Yükselen",
    "DSC": "Alçalan",
    "MC": "Tepe Noktası",
    "IC": "Dip Noktası",
}

ASPECT_TR: Dict[str, str] = {
    "square": "kare",
    "trine": "üçgen",
    "sextile": "altmışlık",
    "conjunction": "kavuşum",
    "opposition": "karşıt",
}

HOUSE_MOTIFS_TR: Dict[int, Sequence[str]] = {
    1: (
        "benlik ve duruş tarafında daha net bir çizgi kurman isteniyor.",
        "duruşun, ilk izlenimin ve başlangıç enerjin bu dönemde yeniden ayarlanıyor.",
        "kendini ortaya koyma biçimin sadeleştikçe yön hissin de güçleniyor.",
        "imajın ile iç niyetin arasındaki fark kapanmak istiyor.",
        "beden dili ve öz güven hattın daha bilinçli çalışmak istiyor.",
        "başlangıç enerjini dağıtmadan kullanman önemli hale geliyor.",
    ),
    3: (
        "iletişim tarzın, yakın çevre ilişkilerin ve düşünme ritmin bu dönemde yeniden ayarlanıyor.",
        "kardeşler, kısa eğitimler ve günlük trafik gibi 3. Ev başlıklarında netlik ihtiyacı artıyor.",
        "mesajların kadar konuşma tonun ve zihinsel hızın da bu dönemin konusu.",
        "yakın çevreyle kurduğun dil sadeleştikçe düşünce akışın da toparlanıyor.",
        "kısa yolculuklar, yazışmalar ve öğrenme ritmin tek bir hatta toplanmak istiyor.",
        "düşünceyi ifade etme biçiminle günlük koordinasyonun aynı anda ince ayar istiyor.",
    ),
    4: (
        "ev, kökler ve iç güven alanında daha sakin bir düzen kurman bekleniyor.",
        "dinlenme biçiminle duygusal temelini aynı anda güçlendiren bir dönemdesin.",
        "özel alanındaki düzen dış dünyadaki ritmini doğrudan etkiliyor.",
        "ev içi ritim sadeleştikçe iç güvenin daha kolay toparlanıyor.",
        "kök duygun ve aitlik hissin yeniden yerleşmek istiyor.",
        "iç dünyanı taşıyan temel düzen şimdi daha görünür çalışıyor.",
    ),
    7: (
        "ilişkiler ve ortaklıklar tarafında sınır ile karşılıklılık yeniden tanımlanıyor.",
        "karşındaki insanla kurduğun denge bu dönemde daha bilinçli bir ayar istiyor.",
        "beklenti, anlaşma ve açık ilişki dili daha net kurulmak istiyor.",
        "ilişki aynası sana hem ihtiyacını hem sınırını daha görünür kılıyor.",
        "ortaklık kurma biçimin ve pazarlık tonun yeniden kalibre ediliyor.",
        "yakın ilişkilerde ne verdiğin ve ne beklediğin daha açık hale gelmek istiyor.",
    ),
    9: (
        "ufuk, uzmanlaşma ve eğitim hattında yeni bir yön duygusu kuruluyor.",
        "yayın, yabancılar, inançlar ve yol haritası tarafında büyüyen bir tema var.",
        "öğrenme biçimin ile büyük resim kurma yeteneğin aynı anda güncelleniyor.",
        "uzmanlaşma, uzak bağlantılar ve anlam arayışın tek bir eksende toparlanıyor.",
        "eğitim ve yayın başlıklarında daha olgun bir yöntem geliştirme zamanı.",
        "vizyonunu taşıyan inanç ve öğrenme düzeni bu dönemde değişiyor.",
    ),
    10: (
        "kariyer, itibar ve yön duygun daha görünür bir çizgiye taşınıyor.",
        "sorumluluk alma biçimin ile görünürlük hattın aynı anda yeniden ayarlanıyor.",
        "hedeflerinle dış dünyadaki imzan arasında daha net bir bağ kuruluyor.",
        "iş ve itibar alanında kalıcı sonuç verecek bir düzen arıyorsun.",
        "otoriteyle ilişkin ve kendi yön duygun şimdi daha açık hale geliyor.",
        "dış dünyada nasıl göründüğünle neyi temsil ettiğin aynı hatta toplanıyor.",
    ),
    11: (
        "topluluk, network ve ortak hedefler alanında yeni bir ritim kuruluyor.",
        "ekip ilişkileri ve gelecek planları bu dönemde daha seçici hale geliyor.",
        "arkadaş çevresi, proje ağı ve hedef paylaşımı tek bir eksende toparlanıyor.",
        "ait olduğun topluluklarla kurduğun bağlar daha bilinçli bir ayar istiyor.",
        "network içindeki yerin ve gelecek hedeflerin yeniden hizalanıyor.",
        "ortak üretim, ekip koordinasyonu ve uzun vadeli hedefler daha görünür çalışıyor.",
    ),
}

PLANET_ARCHETYPES_TR: Dict[str, Dict[str, Sequence[str]]] = {
    "uranus": {
        "verbs": ("sarsar", "uyandırır", "yeni yol açar"),
        "shadow": ("sabırsız kopuş", "ani karar", "kanal dağılması"),
        "gift": ("yaratıcı sıçrama", "elektrik netlik", "yenilik cesareti"),
    },
    "neptune": {
        "verbs": ("bulanıklaştırır", "yumuşatır", "sezdirir"),
        "shadow": ("sınır erimesi", "projeksiyon", "yanlış okuma"),
        "gift": ("sezgiyi ayıklama", "nazik sınır", "ilhamlı netlik"),
    },
    "mars": {
        "verbs": ("başlatır", "iter", "hamleyi açar"),
        "shadow": ("acele", "sertleşme", "tepkisellik"),
        "gift": ("doğru hamle", "cesur netlik", "odak"),
    },
    "saturn": {
        "verbs": ("test eder", "sıkılaştırır", "olgunlaştırır"),
        "shadow": ("katılık", "aşırı yük", "yavaş kilitlenme"),
        "gift": ("ustalık", "kalıcı sistem", "iç otorite"),
    },
}

ASPECT_VOICES_TR: Dict[str, Dict[str, Sequence[str]]] = {
    "trine": {
        "conflict": (
            "Akış açık; doğal ilerleyen bir hat var.",
            "Yetenek devrede; kapı açılıyor ve sen girersen büyür.",
        ),
        "shadow": (
            "Fazla kanal açmak hızı dağıtır.",
            "Konfor alanı ölçümü gevşetebilir.",
        ),
        "upper": (
            "Ritim kurarsan bu açı kalıcı ivme üretir.",
            "Doğal akışı plana bağlamak hızlı sıçrama getirir.",
        ),
    },
    "sextile": {
        "conflict": (
            "Fırsat var; küçük hamleyle açılır.",
            "Mikro adım atarsan destek büyür.",
        ),
        "shadow": (
            "Pasif kalmak bu açının hızını söndürür.",
            "Erteleme küçük fırsatları kaçırabilir.",
        ),
        "upper": (
            "Küçük adım + düzenli tekrar büyük kazanca döner.",
            "Mikro hamleleri zincirlediğinde sonuç büyür.",
        ),
    },
    "square": {
        "conflict": (
            "Sürtünme davranışı test eder; tonu yanlış ayarlama riski artar.",
            "Baskı anında hızlanmak yerine çerçeve kurmak gerekir.",
        ),
        "shadow": (
            "Savunma refleksi veriyi kişisel saldırı gibi okutabilir.",
            "Acele yanıt kısa rahatlık verir, uzun maliyet çıkarır.",
        ),
        "upper": (
            "Gerilimi metoda çevirdiğinde net güç açılır.",
            "Sınır netliği bu açıda oyunu lehine çevirir.",
        ),
    },
    "opposition": {
        "conflict": (
            "Ayna etkisi kutupları büyütür; denge hızla bozulabilir.",
            "Karşı taraf ritmi değiştirirken iç merkez test edilir.",
        ),
        "shadow": (
            "Projeksiyon arttığında ihtiyaç görünmez kalır.",
            "Onay arayışı yön kaymasına yol açabilir.",
        ),
        "upper": (
            "Net soru ve net sınır kutupları ortak dile taşır.",
            "Karşıtlık doğru yönetilirse ilişki zekâsı büyür.",
        ),
    },
    "conjunction": {
        "conflict": (
            "Enerji tek hatta toplanınca yük hissi artar.",
            "Aynı anda çok hedef açmak odağı kırar.",
        ),
        "shadow": (
            "Yoğunlaşma kontrol takıntısına kayabilir.",
            "Hızlı sonuç isteği yöntemi daraltabilir.",
        ),
        "upper": (
            "Tek hedefte kalırsan bu açı ustalık üretir.",
            "Baskıyı sıraya koyduğunda netlik hızdan öne geçer.",
        ),
    },
}

ASPECT_SECTION_TR: Dict[str, Dict[str, str]] = {
    "square": {"label": "Sürtünme", "tone": "pressure"},
    "opposition": {"label": "Ayna", "tone": "mirror"},
    "trine": {"label": "Akış", "tone": "flow"},
    "sextile": {"label": "Fırsat", "tone": "opportunity"},
    "conjunction": {"label": "Yoğunlaşma", "tone": "focus"},
}

ASPECT_TONE_TR: Dict[str, str] = {
    "trine": "flow",
    "sextile": "chance",
    "square": "friction",
    "opposition": "mirror",
    "conjunction": "focus",
}

SECTION_LABELS_BY_TONE_TR: Dict[str, Dict[str, str]] = {
    "flow": {"conflict": "Akış", "shadow": "Abartırsan", "upper": "Potansiyel"},
    "chance": {"conflict": "Fırsat", "shadow": "Kaçırma riski", "upper": "Kazanca çevir"},
    "friction": {"conflict": "Sürtünme", "shadow": "Refleks", "upper": "Ustalık"},
    "mirror": {"conflict": "Ayna", "shadow": "Projeksiyon", "upper": "Denge"},
    "focus": {"conflict": "Yoğunluk", "shadow": "Taşma", "upper": "Tek hedef"},
}

HOUSE_SCENES_TR: Dict[int, Dict[str, Sequence[str]]] = {
    3: {
        "scene": ("mesaj", "konuşma", "yazı-not", "yakın çevre", "kanal yönetimi"),
        "examples": ("yanlış anlaşılma", "kısa metin", "toplantı notu"),
    },
    5: {
        "scene": ("üretim", "yaratıcılık", "sahne", "oyun", "prototip"),
        "examples": ("taslak", "mini demo", "üretim ritmi"),
    },
    7: {
        "scene": ("anlaşma dili", "ilişki ritmi", "ayna", "pazarlık", "sınır"),
        "examples": ("beklenti netliği", "karşılıklı söz"),
    },
    9: {
        "scene": ("eğitim", "sertifika", "yayın", "yabancı dil", "uzak temas"),
        "examples": ("öğrenme sprinti", "mentorluk", "uzmanlaşma"),
    },
    11: {
        "scene": ("topluluk", "network", "ortak hedef", "yayılım", "ürün ağı"),
        "examples": ("paylaşım planı", "takım koordinasyonu"),
    },
}

SIGN_STYLES_TR: Dict[str, Dict[str, str]] = {
    "aries": {"style": "ilk hamle", "pitfall": "acele patlama", "superpower": "cesur başlatma"},
    "taurus": {"style": "sabır ve değer", "pitfall": "değişime direnç", "superpower": "kalıcı inşa"},
    "gemini": {"style": "merak ve bağ", "pitfall": "dağılma", "superpower": "hızlı öğrenme"},
    "cancer": {"style": "bakım ve kök", "pitfall": "içe çekilme", "superpower": "güvenli alan kurma"},
    "leo": {"style": "kendini ortaya koyma", "pitfall": "onay ihtiyacı", "superpower": "otantik görünürlük"},
    "virgo": {"style": "metod ve iyileştirme", "pitfall": "mükemmellik ertelemesi", "superpower": "ölçülü ustalık"},
    "libra": {"style": "denge ve ilişki", "pitfall": "karar erteleme", "superpower": "adil köprü kurma"},
    "scorpio": {"style": "derinlik ve dönüşüm", "pitfall": "kontrol şüphesi", "superpower": "gerçeğe inme"},
    "sagittarius": {"style": "ufuk ve inanç", "pitfall": "aşırı genelleme", "superpower": "büyük resim görme"},
    "capricorn": {"style": "yapı ve sorumluluk", "pitfall": "aşırı kontrol", "superpower": "sürdürülebilir sonuç"},
    "aquarius": {"style": "yenilik", "pitfall": "ani kopuş", "superpower": "yaratıcı sıçrama"},
    "pisces": {"style": "sezgi", "pitfall": "sınır erimesi", "superpower": "ince duyarlık"},
}

DISPOSITOR_HINTS_TR: Dict[str, Dict[str, Sequence[str]]] = {
    "Mercury": {
        "mechanism": ("mekanizma Merkür: not al, sırala, gönder", "Merkür hattı: kısa yaz, net sor"),
    },
    "Saturn": {
        "mechanism": ("mekanizma Satürn: sınır koy, takvimle", "Satürn hattı: yavaşla, sabitle, tamamla"),
    },
    "Mars": {
        "mechanism": ("mekanizma Mars: tek hamle, tek hedef", "Mars hattı: başlat, ölç, düzelt"),
    },
}

PLANET_NATURE_TR: Dict[str, Dict[str, Sequence[str]]] = {
    "Neptune": {
        "nouns": ("sis", "buğu", "çözülme", "sezgi"),
        "verbs": ("bulanıklaştırır", "yumuşatır", "hassaslaştırır"),
    },
    "Uranus": {
        "nouns": ("kıvılcım", "sıçrama", "yeni yöntem", "özgürleşme"),
        "verbs": ("uyandırır", "hızlandırır", "alışkanlığı kırar"),
    },
    "Pluto": {
        "nouns": ("derin dönüşüm", "arınma", "güç", "konum değişimi"),
        "verbs": ("derinleştirir", "dönüştürür", "eleyip seçtirir"),
    },
    "Mars": {
        "nouns": ("hamle", "cesaret", "somut adım", "netlik"),
        "verbs": ("hız verir", "somutlaştırır", "harekete geçirir"),
    },
    "Saturn": {
        "nouns": ("çerçeve", "sorumluluk", "yapı", "dayanıklılık"),
        "verbs": ("test eder", "yavaşlatır", "olgunlaştırır"),
    },
}

ASPECT_FLAVOR_TR: Dict[str, Dict[str, Sequence[str]]] = {
    "square": {"verbs": ("sınar", "gerer", "test eder")},
    "opposition": {"verbs": ("ayna tutar", "dengeye zorlar", "müzakereye iter")},
    "conjunction": {"verbs": ("yoğunlaştırır", "tek hatta toplar", "odaklar")},
    "trine": {"verbs": ("kolaylaştırır", "akıtıp büyütür", "destekler")},
    "sextile": {"verbs": ("kapı aralar", "fırsat üretir", "alan açar")},
}

TARGET_TONE_TR: Dict[str, Sequence[str]] = {
    "ASC": ("duruş", "kimlik", "ilk izlenim"),
    "DSC": ("ilişki aynası", "bağ", "ortaklık"),
    "MC": ("kariyer yönü", "itibar", "hedef"),
    "IC": ("kökler", "ev", "iç güven"),
}

PERIOD_TRACK_COPY_TR: Dict[str, Dict[str, Any]] = {
    "identity_spine": {
        "version": "v2",
        "period_opening": (
            "Bu dönem önce kendini nasıl anlattığın değişiyor, sonra bunun etkisi dışarıda nasıl göründüğüne yansıyor.",
            "Şu sıralar mesele daha çok görünmek değil; daha anlaşılır, daha tutarlı görünmek.",
        ),
        "big_picture": (
            "Kimlik hattında gereksiz fazlalıklar ayıklanıyor. İçeride hissettiğinle dışarıda bıraktığın iz arasındaki mesafe kapanmak istiyor.",
            "Buradaki kazanım imaj üretmek değil, daha güvenilir ve daha okunur bir ifade biçimi kurmak.",
        ),
        "mechanism": (
            "Hikâye önce iletişim, konuşma ve yakın çevre tarafında başlıyor; sonra bunun karşılığı kimlik ve duruş alanında görülüyor.",
            "Önce dil sadeleşiyor, ardından dışarıda nasıl algılandığın değişiyor.",
        ),
        "growth_edge": (
            "En kritik eşik, yanlış anlaşılmayı yalnızca ton sorunu sanmak. İçeriği netleştirmediğinde aynı konuşmayı tekrar tekrar yapmak yorabilir.",
            "Muğlaklık uzadıkça gereksiz açıklama döngüsü başlar; o yüzden sınırı baştan kurmak önemli.",
        ),
        "relational_or_life_expression": (
            "Günlük hayatta bu; önemli konuşmalarda daha çok açıklık ihtiyacı, daha seçilmiş kelimeler ve net sınırlar olarak görünür.",
            "İnsanlar seni yanlış değil, eksik okumaya daha yatkın olabilir; bu yüzden eksik yeri sen tamamlıyorsun.",
        ),
        "what_it_builds": (
            "Bu dönem sende kendini daha net ifade etme kasını geliştiriyor.",
            "Bu dönem sende yanlış anlaşılma payını azaltan daha temiz bir ifade kası kuruyor.",
        ),
    },
    "method_shift_9_virgo": {
        "version": "v2",
        "period_opening": (
            "Bu dönem hevesin kendisi kadar, onu nasıl sürdüreceğin de değişiyor.",
            "Yeni bir şey denemek kolay; asıl hikâye bunu tekrar edilebilir bir yönteme çevirmende.",
        ),
        "big_picture": (
            "Buradaki açılım sadece yaratıcı bir kıvılcım değil; yön duygunu değiştirebilecek bir çalışma biçimi.",
            "Küçük bir yöntem değişikliği, uzun vadede öğrenme, uzmanlaşma ve üretim hattını yeniden kurabilir.",
        ),
        "mechanism": (
            "Etki önce deneme, üretim ve cesaret tarafında açılıyor; sonra bunun sonucu öğrenme, uzmanlaşma ve yön duygusunda görülüyor.",
            "İlk kıvılcım keyif alanından geliyor, asıl dönüşüm ise bunu çalışır bir düzene bağladığında oluyor.",
        ),
        "growth_edge": (
            "Risk, aynı anda fazla fikir açıp hiçbirini yeterince derinleştirmemek.",
            "Hızın cazibesi ölçüyü dağıttığında gerçek kazanım yerine kısa süreli heyecan kalabilir.",
        ),
        "relational_or_life_expression": (
            "Günlük hayatta bunu yeni bir kurs, yeni bir yayın fikri, yeni bir üretim biçimi ya da farklı bir yol haritası ihtiyacı olarak hissedebilirsin.",
            "Kendini geliştirme isteğin artar; ama bu kez sadece bilgi toplamak değil, onu sonuç verecek bir düzene koymak önem kazanır.",
        ),
        "what_it_builds": (
            "Bu dönem sende ilhamı çalışır bir sisteme çevirme kasını geliştiriyor.",
            "Bu dönem sende hevesi yön duygusuna bağlama kasını güçlendiriyor.",
        ),
    },
    "network_transform_11": {
        "version": "v2",
        "period_opening": (
            "Bu dönem çevren, hedeflerin ve kiminle yürümek istediğin daha seçici hale geliyor.",
            "Mesele çok insan değil; doğru çevre, doğru hedef ve doğru ortaklık.",
        ),
        "big_picture": (
            "İçeride değişen güç algın, dışarıda hangi çevrede yer almak istediğini de yeniden tanımlıyor.",
            "Eski hedefler ve yeni yön aynı anda masada; bu dönem neyi temsil etmek istediğini netleştiriyor.",
        ),
        "mechanism": (
            "Dönüşüm önce içeride hangi rolde durmak istediğin konusunda başlıyor; sonra bunun yankısı topluluklar, ekipler ve gelecek planlarında görülüyor.",
            "Önce içeride eleme oluyor, sonra dışarıda çevre ve hedef kendini yeniden sıralıyor.",
        ),
        "growth_edge": (
            "Risk, seçiciliği soğukluk ya da kontrol etme ihtiyacına çevirmek.",
            "Her ilişkiyi yalnızca işlevine göre okumak bağı kurutabilir.",
        ),
        "relational_or_life_expression": (
            "Günlük hayatta bu; bazı ekiplerden uzaklaşma, bazı hedefleri yeniden adlandırma ve seni büyüten çevreye daha bilinçli yaklaşma ihtiyacı olarak çalışır.",
            "Kiminle görünür olacağına ve neyin parçası olacağına daha bilinçli karar vermek istersin.",
        ),
        "what_it_builds": (
            "Bu dönem sende gücünü doğru çevrelerle birleştirme kasını geliştiriyor.",
            "Bu dönem sende uzun vadeli hedefleri daha seçici kurma kasını güçlendiriyor.",
        ),
    },
    "mirror_axis_1_7": {
        "version": "v2",
        "period_opening": (
            "Bu dönem ilişkilerde yakınlık kadar tanım ve çerçeve ihtiyacı da büyüyor.",
            "Karşı tarafı anlamak kadar, kendi beklentini açık söylemek de önemli hale geliyor.",
        ),
        "big_picture": (
            "İlişki tarafında mesele sadece bağ kurmak değil; bağı taşıyacak dili ve sınırı kurmak.",
            "Ayna etkisi büyüdüğünde ne hissettiğin kadar neyi açık söylediğin de belirleyici olur.",
        ),
        "mechanism": (
            "Süreç önce iletişim tonunda, mesajlarda ve beklenti konuşmalarında başlar; sonra doğrudan ilişki dengesine taşınır.",
            "Önce konuşma biçimi değişir, ardından ilişkinin ritmi ve güven duygusu buna cevap verir.",
        ),
        "growth_edge": (
            "Risk, ima ile anlaşılmayı beklemek ya da karşı tarafın tepkisini bütün niyetin yerine koymak.",
            "Belirsizlik uzadıkça hem kırgınlık hem yanlış okuma artabilir.",
        ),
        "relational_or_life_expression": (
            "Günlük hayatta bu; ilişkilerde beklenti konuşmalarının artması, ortak planların daha net kurulması ve sınır cümlelerinin daha önemli hale gelmesi olarak yaşanabilir.",
            "Yakın bağlarda yumuşak ama açık bir dil bu dönemin ana taşıyıcısı olur.",
        ),
        "what_it_builds": (
            "Bu dönem sende yakınlık içinde kendini kaybetmeden kalabilme kasını geliştiriyor.",
            "Bu dönem sende ilişkide beklentiyi açık kurma kasını güçlendiriyor.",
        ),
    },
    "default": {
        "version": "v2",
        "period_opening": ("Bu dönem hayatının bir alanı daha görünür hale geliyor ve senden daha bilinçli seçimler istiyor.",),
        "big_picture": ("Mesele sadece bir konunun açılması değil; ona nasıl yaklaştığının değişmesi.",),
        "mechanism": ("Etki önce gündelik hayatta görünür oluyor, sonra bunun sonucu daha kalıcı bir davranış değişimine dönüşüyor.",),
        "growth_edge": ("Risk, ilk hissi sonuç sanıp süreci aceleye getirmek.",),
        "relational_or_life_expression": ("Günlük hayatta bu, daha seçici kararlar ve daha net sınırlar olarak hissedilebilir.",),
        "what_it_builds": ("Bu dönem sende daha net seçim yapma kasını geliştiriyor.",),
    },
}

ROLE_VOICES_TR: Dict[str, Dict[str, str]] = {
    "north_node": {
        "conflict": "Yön hattı açılırken eski ivmeyle yeni rota arasında sürtünme olabilir.",
        "upper": "Büyüme rotası küçük ama sürekli ileri adımla netleşir.",
    },
    "south_node": {
        "conflict": "Otomatik pilot ve eski kalıp tekrar devreye girebilir.",
        "upper": "Alışkanlığı fark edip güncel seçim yaptığında enerji serbest kalır.",
    },
    "lilith": {
        "conflict": "Ham sınır ve dürtü dili sertleşirse temas kopabilir.",
        "upper": "Bastırılmış isteği net bir sınır cümlesiyle ifade etmek güç kazandırır.",
    },
}


_ALLOWED_PUBLIC_POINTS = {
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
}


def _safe_text(s: Any) -> str:
    return str(s or "").strip()


def _canonical_key(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def _planet_tr(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    upper = raw.upper()
    if upper in POINT_TR:
        return POINT_TR[upper]
    key = _canonical_key(raw)
    return PLANET_TR.get(key, raw.title())


def _sign_tr(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    return SIGN_TR.get(_canonical_key(raw), raw.title())


def _point_tr(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    upper = raw.upper()
    if upper in POINT_TR:
        return POINT_TR[upper]
    return _planet_tr(raw)


def _aspect_tr(value: Any) -> str:
    raw = str(value or "").strip().lower()
    return ASPECT_TR.get(raw, raw)


def _phase_hint_tr(value: Any) -> str:
    phase = str(value or "").strip().lower()
    return {
        "applying": "yaklaşıyor",
        "exact": "tam üstünde",
        "exactish": "tam üstünde",
        "separating": "geri çekiliyor",
    }.get(phase, "")


def strip_tech_tokens(text: str) -> str:
    out = _safe_text(text)
    out = _TECH_VALUE_RE.sub("", out)
    out = _TECH_TOKENS_RE.sub("", out)
    out = re.sub(r"\s{2,}", " ", out).strip()
    out = re.sub(r"\s+([.,;:!?])", r"\1", out)
    out = re.sub(r"\(\s*\)", "", out)
    return out


def render_signature_tr(event: Mapping[str, Any]) -> str:
    transit_body = _planet_tr(event.get("transit_body") or "Transit")
    natal_point = _point_tr(event.get("natal_point") or "Nokta")
    aspect = _aspect_tr(event.get("aspect"))
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    transit_house = _safe_int(houses.get("transit_in_natal_house"))
    house_part = f" ({transit_house}. Ev)" if transit_house else ""
    phase = _phase_hint_tr(event.get("phase"))
    tail = phase or "şu an güçlü"
    return f"{transit_body} {natal_point} ile {aspect}{house_part} — {tail}"


def house_motif_line(house: int | None, seed: str | None = None) -> str:
    if not house:
        return ""
    variants = list(HOUSE_MOTIFS_TR.get(int(house), ()))
    if not variants:
        return ""
    raw_seed = seed or f"house:{int(house)}"
    idx = int(hashlib.sha1(raw_seed.encode("utf-8")).hexdigest()[:8], 16) % len(variants)
    return str(variants[idx]).strip()


def compose_phrase_pack(
    *,
    transit_body: str,
    aspect: str,
    natal_point: str,
    context_pack: Mapping[str, Any],
    event: Mapping[str, Any],
    max_len: Mapping[str, int],
) -> Dict[str, Any]:
    transit_l = str(transit_body or "").strip().lower()
    aspect_l = str(aspect or "").strip().lower()
    natal_point_safe = _safe_point(natal_point)
    pack = context_pack if isinstance(context_pack, Mapping) else {}
    target = pack.get("target") if isinstance(pack.get("target"), Mapping) else {}
    target_planet = _safe_point(target.get("planet") or natal_point_safe)
    target_house = _safe_int(target.get("house"))
    target_sign = str(target.get("sign") or "").strip().lower()
    target_sign_tr = str(target.get("sign_tr") or target.get("sign") or "").strip()
    dispositor = pack.get("dispositor") if isinstance(pack.get("dispositor"), Mapping) else {}
    rulership = pack.get("rulership_houses") if isinstance(pack.get("rulership_houses"), list) else []

    transit_house = _safe_int((event.get("houses") or {}).get("transit_in_natal_house"))
    seed = _seed(event, "phrase_pack")

    base = ASPECT_VOICES_TR.get(aspect_l, ASPECT_VOICES_TR["square"])
    style = SIGN_STYLES_TR.get(target_sign, {})

    scene_line = _build_scene_line(transit_house, target_house)
    title = _build_title(transit_l, aspect_l, target_planet, target_house, transit_house, seed)

    conflict_add = " ".join(base["conflict"][:2])
    shadow_add = " ".join(base["shadow"][:2])
    upper_add = " ".join(base["upper"][:2])

    guidance_add: List[str] = []
    watch_add: List[str] = []

    is_uranus_mars = transit_l == "uranus" and aspect_l in {"trine", "sextile"} and str(target_planet).lower() == "mars"
    if is_uranus_mars:
        conflict_add = (
            "Bir anda yöntem değiştirip hız kazanırsın; yaratıcı sıçrama burada kolay. "
            "Başak tarafında metod kurdukça akış büyür."
        )
        shadow_add = "Aşırı overclock odak kaydırır; aynı anda üç plan açmak kısa devre yaratır."
        upper_add = (
            "Yeni yöntem + yapılandırılmış sprint sıçraması burada çalışır; öğrenme ve yayın hattı hızlanır. "
            "Ölç, not al, sprint ritmi kur; sonra yayına al."
        )
        guidance_add = [
            "Seç tek bir hedef; 14 gün sprint aç.",
            "Yayınla mini bir prototip ve sonucu test et.",
        ]
        watch_add = ["Durdur aşırı optimizasyonu; başlamayı geciktirme."]

    if transit_l == "neptune" and aspect_l == "square" and natal_point_safe == "ASC":
        conflict_add = (
            "Neptün, ASC ile kare açı kuruyor; kimlik hattında sis artar. "
            "Dış imaj ile iç niyet kolay ayrışır, sınırı baştan yazmak gerekir."
        )
        shadow_add = "Belirsiz sözler yanlış anlaşılmayı büyütebilir."
        upper_add = "Nazik ama net sınır koyduğunda sezgi netliğe döner."
        guidance_add = ["Sözünü kısa tut; niyeti bir cümlede sabitle."]
        watch_add = ["Belirsiz vaat verme."]

    if transit_l == "neptune" and aspect_l == "square" and natal_point_safe == "DSC":
        conflict_add = (
            "Neptün, DSC ile kare açı kuruyor; ilişki aynasında projeksiyon artar. "
            "Karşı tarafı idealize etme riski bu hatta yükselir."
        )
        shadow_add = "Sınır erimesi beklenti karmaşası yaratabilir."
        upper_add = "İlişki dilini netleştirince sis yerine temas kalır."
        guidance_add = ["Beklentiyi iki maddede yaz ve karşılıklı teyit al."]
        watch_add = ["İma ile anlaşılmayı bekleme."]

    if transit_l == "neptune" and aspect_l == "conjunction" and natal_point_safe == "Saturn":
        conflict_add = "Eski yapı çözülürken kontrol refleksi sertleşebilir."
        shadow_add = "Katı planı bırakmadan yeni akış kurulmaz."
        upper_add = "Çerçeveyi sadeleştirip sınırı güncellediğinde sağlam bir yeniden kurulum gelir."
        guidance_add = ["Tek kural seç ve bu hafta onu uygula."]
        watch_add = ["Hepsini aynı anda düzeltmeye çalışma."]

    if style:
        conflict_add = f"{conflict_add} {target_sign_tr} stilinde tema: {style['style']}; risk: {style['pitfall']}."
        upper_add = f"{upper_add} Güç tarafı: {style['superpower']}."

    role_key = normalize_point_token(target_planet or natal_point_safe)
    role_voice = ROLE_VOICES_TR.get(role_key) or ROLE_VOICES_TR.get(normalize_point_token(natal_point_safe))
    if role_voice:
        conflict_add = _append_unique_sentence(conflict_add, role_voice.get("conflict") or "")
        upper_add = _append_unique_sentence(upper_add, role_voice.get("upper") or "")

    disp_planet = _safe_point(dispositor.get("planet") or "")
    if disp_planet and disp_planet in DISPOSITOR_HINTS_TR:
        mech = _pick(DISPOSITOR_HINTS_TR[disp_planet]["mechanism"], seed)
        upper_add = f"{upper_add} {mech}."

    rulership_line = _rulership_line(rulership)

    if transit_house == 5 and is_uranus_mars:
        conflict_add = f"{conflict_add} 5. Evde üretim ve sahne tarafında elektrikli bir itki var."
    if target_house == 9 and is_uranus_mars:
        upper_add = f"{upper_add} 9. Evde öğrenme, yayın ve uzmanlaşma burada sonuç verir."

    if not guidance_add:
        guidance_add = [
            "Tek bir hamle seç ve gün içinde tamamla.",
            "Kısa not al; akşam tek ölçümle sonucu kontrol et.",
        ]
    if not watch_add:
        watch_add = ["Aynı anda iki odak açıp ritmi dağıtma."]

    section = ASPECT_SECTION_TR.get(aspect_l, {"label": "Dinamik", "tone": "calibration"})

    out = {
        "title": _limit_sentences(_sanitize(title), 1),
        "conflict_label": section["label"],
        "conflict_tone": section["tone"],
        "tone": ASPECT_TONE_TR.get(aspect_l, "focus"),
        "section_labels": SECTION_LABELS_BY_TONE_TR.get(
            ASPECT_TONE_TR.get(aspect_l, "focus"),
            SECTION_LABELS_BY_TONE_TR["focus"],
        ),
        "why_now": _build_why_now(event),
        "conflict_add": _limit_sentences(_sanitize(conflict_add), int(max_len.get("conflict", 2))),
        "shadow_add": _limit_sentences(_sanitize(shadow_add), int(max_len.get("shadow", 2))),
        "upper_add": _limit_sentences(_sanitize(upper_add), int(max_len.get("upper", 2))),
        "guidance_add": _sanitize_bullets(guidance_add, exact_max=2),
        "watch_out_add": _sanitize_bullets(watch_add, exact_max=1),
        "scene_line": _limit_sentences(_sanitize(scene_line), 1),
        "technical_note": _limit_sentences(_sanitize(rulership_line), 1),
    }
    return out


def _build_scene_line(transit_house: int | None, target_house: int | None) -> str:
    if transit_house and target_house and transit_house != target_house:
        return (
            f"Etki önce {HOUSE_LIFE_SCENE_TR.get(transit_house, f'{transit_house}. ev alanı')} tarafında açılır; "
            f"sonra {HOUSE_LIFE_SCENE_TR.get(target_house, f'{target_house}. ev alanı')} alanında sonuç verir."
        )
    if target_house:
        return f"Etki en çok {HOUSE_LIFE_SCENE_TR.get(target_house, f'{target_house}. ev alanı')} tarafında görünür olur."
    if transit_house:
        return f"Etki en çok {HOUSE_LIFE_SCENE_TR.get(transit_house, f'{transit_house}. ev alanı')} tarafında çalışır."
    return ""


def _build_title(
    transit_body: str,
    aspect: str,
    target_planet: str,
    target_house: int | None,
    transit_house: int | None,
    seed: int,
) -> str:
    if transit_body == "uranus" and aspect in {"trine", "sextile"} and str(target_planet).lower() == "mars":
        pool = ["Kıvılcım Planı", "Yöntem Sıçraması", "Elektrik Prototip"]
        return pool[(seed + (target_house or 0) + (transit_house or 0)) % len(pool)]
    if transit_body == "neptune" and aspect == "square" and target_planet in {"ASC", "DSC"}:
        return "Sınır Kalibrasyonu" if target_planet == "ASC" else "Ayna Sisi"
    pool = {
        "square": ["Netlik Pazarlığı", "Sınır Testi"],
        "trine": ["Akış Hattı", "Hızlı İvme"],
        "sextile": ["Fırsat Penceresi", "Küçük Hamle"],
        "opposition": ["Ayna Dengesi", "Kutupları Birleştir"],
        "conjunction": ["Tek Kanal", "Yoğun Odak"],
    }.get(aspect, ["Tema Güncellemesi"])
    return pool[seed % len(pool)]


def _rulership_line(rulership_houses: Sequence[Mapping[str, Any]]) -> str:
    houses: List[int] = []
    for entry in rulership_houses:
        house = _safe_int(entry.get("house")) if isinstance(entry, Mapping) else None
        if house and house not in houses:
            houses.append(house)
    if not houses:
        return ""
    if len(houses) == 1:
        h = houses[0]
        return f"Teknik yankı: {h}. Ev ({HOUSE_LABEL_TR.get(h, 'genel')}) hattına uzanır."
    a, b = houses[0], houses[1]
    return (
        f"Teknik yankı: {a}. Ev ({HOUSE_LABEL_TR.get(a, 'genel')}) ve "
        f"{b}. Ev ({HOUSE_LABEL_TR.get(b, 'genel')}) arasında çalışır."
    )


def _safe_point(value: Any) -> str:
    token = str(value or "").strip()
    if not token:
        return ""
    low = normalize_point_token(token)
    if is_public_point(low):
        if low in {"asc", "dsc", "mc", "ic"}:
            return low.upper()
        label_map = {
            "north_node": "North Node",
            "south_node": "South Node",
            "lilith": "Lilith",
            "chiron": "Chiron",
            "vertex": "Vertex",
            "fortune": "Fortune",
        }
        if low in label_map:
            return label_map[low]
        return low.replace("_", " ").title()
    return token


def _sanitize(text: str) -> str:
    out = strip_tech_tokens(str(text or ""))
    out = re.sub(r"\s+", " ", out).strip()
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    return out


def _sanitize_bullets(values: Sequence[str], *, exact_max: int) -> List[str]:
    out: List[str] = []
    for value in values:
        text = _sanitize(value)
        if not text:
            continue
        words = text.split()
        if len(words) > 14:
            text = " ".join(words[:14])
        if text[-1] not in ".!?":
            text += "."
        out.append(text)
        if len(out) >= exact_max:
            break
    return out


def _build_why_now(event: Mapping[str, Any]) -> str:
    orb = _safe_float(event.get("orb_deg"), default=9.9)
    if orb <= 0.3:
        orb_phrase = "Etki şu an çok belirgin."
    elif orb <= 1.0:
        orb_phrase = "Etki şu sıralar güçlü biçimde hissediliyor."
    else:
        orb_phrase = "Tema şimdiden çalışıyor."

    bucket = str(event.get("bucket") or "").strip().lower()
    duration_phrase = {
        "long": "Bu dalga birkaç ay boyunca etkisini sürdürebilir.",
        "medium": "Bu tema birkaç hafta gündemde kalabilir.",
        "short": "Bu etki kısa ama dikkat çekici bir pencere açar.",
    }.get(bucket, "Bu etki bir süre daha çalışır.")

    natal_point = str(event.get("natal_point") or "").strip().upper()
    angle_phrase = {
        "ASC": "Kimlik hattı aktif.",
        "DSC": "İlişki hattı aktif.",
        "MC": "Yön ve kariyer hattı aktif.",
        "IC": "Ev ve iç güven hattı aktif.",
    }.get(natal_point, "")

    phase = str(event.get("phase") or "").strip().lower()
    phase_phrase = {
        "exact": "Ana vurgu tam odakta.",
        "exactish": "Ana vurgu tam odakta.",
        "applying": "Etki büyüyor.",
        "separating": "Ana vurgu geçti ama yankısı sürüyor.",
    }.get(phase, "")
    parts = [orb_phrase, duration_phrase]
    if angle_phrase:
        parts.append(angle_phrase)
    if phase_phrase:
        parts.append(phase_phrase)
    text = " ".join(parts[:3])
    text = _sanitize(text)
    return text


def _limit_sentences(text: str, max_sentences: int) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    parts = [p.strip() for p in re.split(r"(?<!\d[.!?])(?<=[.!?])\s+", raw) if p.strip()]
    if not parts:
        return raw
    limited = " ".join(parts[: max(1, max_sentences)]).strip()
    if limited and limited[-1] not in ".!?":
        limited += "."
    return limited


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _seed(event: Mapping[str, Any], key: str) -> int:
    raw = "|".join(
        [
            str(event.get("event_id") or ""),
            str(event.get("transit_body") or ""),
            str(event.get("aspect") or ""),
            str(event.get("natal_point") or ""),
            key,
        ]
    )
    return int(hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8], 16)


def _pick(values: Sequence[str], seed: int) -> str:
    if not values:
        return ""
    return str(values[seed % len(values)])


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


def period_big_picture(domain: str, seed: int, enable_fun: bool = True) -> str:
    pool = [
        f"Bu dönem {domain} alanında ne yaptığın kadar bunu nasıl taşıdığın da değişiyor. İlk bakışta karışık gelen şey, aslında daha temiz bir yön kurma ihtiyacından geliyor.",
        f"Bu süreç {domain} tarafında fazlalıkları ayıklıyor. Dışarıdan baskı gibi görünen şey, içeride daha net ve daha tutarlı bir çizgi istemesinden kaynaklanıyor.",
        f"Buradaki tema büyük sözler vermek değil; {domain} alanında daha anlaşılır, daha seçici ve daha çalışır bir düzen kurmak.",
    ]
    return _pick(pool, seed)


def period_mechanism_chain(
    *,
    transit_body: str,
    aspect: str,
    natal_point: str,
    angle_chain: Mapping[str, Any] | None,
    target_chain: Mapping[str, Any] | None,
    start_theme: str,
    end_theme: str,
    seed: int,
    enable_fun: bool = True,
) -> str:
    if isinstance(angle_chain, Mapping):
        angle_name = str(angle_chain.get("angle") or natal_point or "").upper()
        angle_tr = {
            "ASC": "Yükselen",
            "DSC": "Alçalan",
            "MC": "Tepe Noktası",
            "IC": "Dip Noktası",
        }.get(angle_name, natal_point)
        sign = str(angle_chain.get("sign") or "").strip()
        ruler = str(angle_chain.get("ruler") or "").strip()
        ruler_house = _safe_int(angle_chain.get("ruler_house"))
        ruler_house_txt = f"{ruler_house}. evde" if ruler_house else "ilgili evde"

        pool = [
            f"Bu dönemde hikâye önce {start_theme} tarafında başlıyor. Sonra bunun etkisi {angle_tr} üzerinden {end_theme} alanına yerleşiyor. {sign} tonunun yöneticisi {ruler} {ruler_house_txt} çalıştığı için mesele yüzeyde kalmıyor; daha kalıcı bir ayara dönüşmek istiyor.",
            f"{angle_tr} hattı bu süreçte daha hassas. Etki önce {start_theme} tarafında beliriyor, sonra seni {end_theme} alanında daha bilinçli davranmaya zorluyor. {ruler} {ruler_house_txt} olduğu için öğrendiğin şey kısa süreli olmuyor.",
        ]
        return _pick(pool, seed)

    if isinstance(target_chain, Mapping):
        planet = str(target_chain.get("planet") or natal_point or "").strip()
        sign = str(target_chain.get("sign") or "").strip()
        house = _safe_int(target_chain.get("house"))
        house_txt = f"{house}. evde" if house else "kendi alanında"
        dispositor = str(target_chain.get("dispositor") or "").strip()

        pool = [
            f"Bu dönem etki önce {start_theme} tarafında açılıyor, ama asıl gelişim {planet} yüzünden {end_theme} alanına bağlanıyor. {sign} tonu meseleyi yöntem ve detay tarafına çekiyor; bu yüzden yaşanan şey geçici bir duygu değil, kalıcı bir öğrenme haline geliyor.",
        ]
        return _pick(pool, seed)

    return _pick(
        [
            f"Bu dönem hikâye önce {start_theme} tarafında başlıyor, sonra yavaş yavaş {end_theme} alanına yayılıyor. Yani küçük görünen bir hareket daha büyük bir yön değişimini tetikleyebilir."
        ],
        seed,
    )


def period_upper_meaning(
    *,
    promise_theme: str,
    skill_gain: str,
    seed: int,
    enable_fun: bool = True,
) -> str:
    pool = [
        f"Bu dönemin asıl hediyesi {skill_gain} kasını büyütmesi. Bu, sende {promise_theme} temasıyla birleştiğinde hem kararlarını hem ilişkilerini daha az yorarak taşımanı sağlar.",
        f"Buradaki gelişim gösterişli değil, kalıcı. Süreç bittiğinde sende kalan şey daha net seçim, daha sakin güç ve {skill_gain} becerisi olur.",
    ]
    return _pick(pool, seed)
