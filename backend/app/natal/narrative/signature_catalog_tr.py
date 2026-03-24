from __future__ import annotations

from typing import Any, Dict, List

from app.natal.narrative.signature_catalog_tr_extra import SIGNATURES_V1_TR_EXTRA

# Signature format:
# {
#   id: str
#   spark: bool
#   block_affinity: list[str]
#   chips: list[str]
#   rules: list[{"fn": str, "args": dict}]
#   scoring: {"base": float, "boosts": list[...], "cap": float}
#   copy_tr: {"headline": str, "teaser": str, "spark": str, "gift": str, "watch": str}
#   astro_tokens: list[{"type": "...", ...}]
# }

SIGNATURES_V0_TR: List[Dict[str, Any]] = [
    {
        "id": "identity_1st_stellium",
        "spark": True,
        "block_affinity": ["identity_aura"],
        "chips": ["Güçlü Benlik", "Net Duruş", "Kendi Çizgin"],
        "rules": [
            {"fn": "stellium_in_house", "args": {"house": 1, "min_count": 3}},
        ],
        "scoring": {
            "base": 0.55,
            "boosts": [
                {"fn": "sun_in_house", "args": {"house": 1}, "add": 0.10},
                {"fn": "planet_near_angle", "args": {"planet": "Sun", "angle": "ASC", "max_orb": 6.0}, "add": 0.10},
            ],
            "cap": 0.95,
        },
        "copy_tr": {
            "headline": "Güçlü benlik alanı",
            "teaser": "Kendini ortaya koyma ihtiyacın yüksek; duruşun genelde net ve etkili.",
            "spark": "Kimliğin ‘ben buradayım’ diye konuşuyor; varlığın, bulunduğun yere ağırlık ve yön veriyor.",
            "gift": "En iyi hâlinde bu, insanlara güven veren bir liderlik ve sakin bir otoriteye dönüşür.",
            "watch": "Zorlandığında, her şeyi tek başına taşıma ya da fazla kontrol etme refleksi artabilir.",
        },
        "astro_tokens": [{"type": "house_emphasis", "house": 1}],
    },
    {
        "id": "identity_uranus_angular",
        "spark": True,
        "block_affinity": ["identity_aura", "drive_rhythm"],
        "chips": ["Özgün Yol", "Elektrik", "Kendi Ritmin"],
        "rules": [
            {"fn": "planet_near_angle", "args": {"planet": "Uranus", "angle": "ASC", "max_orb": 4.5}},
        ],
        "scoring": {
            "base": 0.50,
            "boosts": [
                {"fn": "tight_orb_bonus", "args": {"planet": "Uranus", "angle": "ASC", "max_orb": 2.0}, "add": 0.20},
                {
                    "fn": "aspect_between",
                    "args": {"a": "Uranus", "b": "Sun", "types": ["Conjunction", "Square", "Opposition"], "max_orb": 5.0},
                    "add": 0.10,
                },
            ],
            "cap": 0.95,
        },
        "copy_tr": {
            "headline": "Özgün çizgi",
            "teaser": "Dışarıdan kontrollü görünsen bile içeride ‘benim yolum başka’ diyen bir kıvılcım var.",
            "spark": "Seni canlı tutan şey özgünlük; aynı yolu yürümekten çok kendi yolunu icat etmek istiyorsun.",
            "gift": "Doğru çalıştığında bu, hızlı uyanan bir yaratıcılık ve cesur bir yenilik kası verir.",
            "watch": "Zorlandığında ‘ani kopuş’ ya da sabırsız yön değiştirme görülebilir; ritmi korumak işleri büyütür.",
        },
        "astro_tokens": [{"type": "angle_hit", "angle": "ASC"}, {"type": "placement", "planet": "Uranus"}],
    },
    {
        "id": "identity_jupiter_neptune_vision",
        "spark": True,
        "block_affinity": ["identity_aura", "luck_creation"],
        "chips": ["Büyük Resim", "Vizyon", "Sezgi"],
        "rules": [
            {"fn": "aspect_between", "args": {"a": "Jupiter", "b": "Neptune", "types": ["Conjunction"], "max_orb": 3.5}},
        ],
        "scoring": {
            "base": 0.48,
            "boosts": [
                {"fn": "either_in_house", "args": {"planets": ["Jupiter", "Neptune"], "house": 1}, "add": 0.15},
                {"fn": "either_near_angle", "args": {"planets": ["Jupiter", "Neptune"], "angle": "ASC", "max_orb": 6.0}, "add": 0.10},
            ],
            "cap": 0.93,
        },
        "copy_tr": {
            "headline": "Vizyon damarları",
            "teaser": "Netlik istersin ama aynı anda büyük resmi de duyarsın; önce anlam oturur, sonra karar keskinleşir.",
            "spark": "İçeride bir olasılık alanı hep açık; bu seni hem sezgisel hem de yön kuran biri yapar.",
            "gift": "En iyi hâlinde vizyonu yapıya dönüştürürsün; insanlara sadece ilham değil yön duygusu da verirsin.",
            "watch": "Zorlandığında sis artabilir; tek bir küçük adımı seçmek vizyonu gerçek hayata indirir.",
        },
        "astro_tokens": [{"type": "aspect", "a": "Jupiter", "b": "Neptune", "aspect": "Conjunction"}],
    },
    {
        "id": "identity_sun_angular",
        "spark": False,
        "block_affinity": ["identity_aura"],
        "chips": ["Görünürlük", "Duruş", "Öz Güven"],
        "rules": [
            {"fn": "planet_near_angle", "args": {"planet": "Sun", "angle": "ASC", "max_orb": 6.0}},
        ],
        "scoring": {
            "base": 0.42,
            "boosts": [
                {"fn": "tight_orb_bonus", "args": {"planet": "Sun", "angle": "ASC", "max_orb": 3.0}, "add": 0.12},
            ],
            "cap": 0.85,
        },
        "copy_tr": {
            "headline": "Duruşun konuşur",
            "teaser": "İnsanlar seni hızlı fark eder; sahneye çıktığında yön verme tarafın belirir.",
            "spark": "Varlığın çekim yaratır; bazen tek bir cümleyle bile atmosferi değiştirirsin.",
            "gift": "İyi çalıştığında bu, ‘net ama sıcak’ bir etkiye dönüşür.",
            "watch": "Zorlandığında kendini fazla tartma ya da ‘hazır mıyım’ eşiğinde bekleme görülebilir.",
        },
        "astro_tokens": [{"type": "placement", "planet": "Sun"}, {"type": "angle_hit", "angle": "ASC"}],
    },
    {
        "id": "mind_saturn_3rd_boundary",
        "spark": True,
        "block_affinity": ["mind_voice"],
        "chips": ["Kısa Net", "Sınır", "Ton"],
        "rules": [{"fn": "planet_in_house", "args": {"planet": "Saturn", "house": 3}}],
        "scoring": {
            "base": 0.55,
            "boosts": [
                {
                    "fn": "planet_aspect_angle",
                    "args": {"planet": "Saturn", "angle": "ASC", "types": ["Square", "Opposition", "Conjunction"], "max_orb": 3.0},
                    "add": 0.18,
                },
                {
                    "fn": "aspect_between",
                    "args": {"a": "Sun", "b": "Saturn", "types": ["Square", "Opposition", "Conjunction"], "max_orb": 6.0},
                    "add": 0.12,
                },
            ],
            "cap": 0.95,
        },
        "copy_tr": {
            "headline": "Cümle kası",
            "teaser": "Niyeti kısa cümleyle netleştirmek sende gerçek bir güç.",
            "spark": "Yanlış anlaşılma ihtimali doğunca içeride tonu yeniden tartan bir refleks çalışıyor.",
            "gift": "En iyi hâlinde az kelimeyle güven kurarsın; hem kendine hem karşı tarafa alan açarsın.",
            "watch": "Zorlandığında fazla açıklama ya da gereğinden sert sınır riski var; niyeti kısa ve temiz söylemek dengeyi kurar.",
        },
        "astro_tokens": [{"type": "placement", "planet": "Saturn", "house": 3}],
    },
    {
        "id": "mind_mercury_1st",
        "spark": False,
        "block_affinity": ["mind_voice", "identity_aura"],
        "chips": ["Zihin Gücü", "Analiz", "Netleştir"],
        "rules": [{"fn": "planet_in_house", "args": {"planet": "Mercury", "house": 1}}],
        "scoring": {"base": 0.42, "boosts": [{"fn": "mercury_angular", "args": {"max_orb": 6.0}, "add": 0.10}], "cap": 0.80},
        "copy_tr": {
            "headline": "Zihin sahnede",
            "teaser": "Kendini en çok düşünme biçimin ve ifade tarzın üzerinden kuruyorsun.",
            "spark": "Zihnin hızlı çalışır; meseleleri kısa sürede ‘anlama–adlandırma–çerçeveleme’ eğilimin var.",
            "gift": "İyi çalıştığında bu, stratejik bir açıklık ve güçlü bir anlatı kurma becerisi verir.",
            "watch": "Zorlandığında fazla düşünmek karar geciktirebilir; tek bir hatta toplanmak iyi gelir.",
        },
        "astro_tokens": [{"type": "placement", "planet": "Mercury", "house": 1}],
    },
    {
        "id": "mind_mercury_rx_refine",
        "spark": False,
        "block_affinity": ["mind_voice"],
        "chips": ["Rafine Et", "İç Düzen", "Düzelt–Yenile"],
        "rules": [{"fn": "planet_retrograde", "args": {"planet": "Mercury"}}],
        "scoring": {"base": 0.35, "boosts": [{"fn": "planet_in_house", "args": {"planet": "Mercury", "house": 1}, "add": 0.08}], "cap": 0.70},
        "copy_tr": {
            "headline": "İç editör",
            "teaser": "Zihninde bir ‘editör’ var; cümleyi ve kararı rafine etmek istersin.",
            "spark": "Bir fikri dışarı almadan önce içeride olgunlaştırman doğal; bu seni daha ‘temiz’ anlatır.",
            "gift": "İyi çalıştığında düşünceyi sadeleştirip sağlam bir biçime kavuşturma becerisi verir.",
            "watch": "Zorlandığında ‘hazır değil’ hissi uzayabilir; ilk taslağı çıkarmak sistemi açar.",
        },
        "astro_tokens": [{"type": "retrograde", "planet": "Mercury"}],
    },
    {
        "id": "mind_sun_square_saturn_standard",
        "spark": True,
        "block_affinity": ["mind_voice", "career_visibility"],
        "chips": ["Yüksek Standart", "Sorumluluk", "İnşa Et"],
        "rules": [{"fn": "aspect_between", "args": {"a": "Sun", "b": "Saturn", "types": ["Square"], "max_orb": 6.5}}],
        "scoring": {"base": 0.52, "boosts": [{"fn": "saturn_hard_to_angle", "args": {"angle": "ASC", "max_orb": 2.0}, "add": 0.15}], "cap": 0.92},
        "copy_tr": {
            "headline": "İç eleştirmen",
            "teaser": "Başarı kasın ‘kolay’ değil; inşa ederek büyüyor ve bu seni çok güçlendiriyor.",
            "spark": "Kendine karşı bazen fazla ciddi davranabilirsin; standart yükselince ağırlık da artar.",
            "gift": "İyi çalıştığında dayanıklılık, ustalık ve gerçek bir profesyonellik verir.",
            "watch": "Zorlandığında kendini sert tartma artar; standardı ‘destek’ gibi kullanmak akışı açar.",
        },
        "astro_tokens": [{"type": "aspect", "a": "Sun", "b": "Saturn", "aspect": "Square"}],
    },
    {
        "id": "drive_mars_9th_method",
        "spark": True,
        "block_affinity": ["drive_rhythm", "talent_gifts"],
        "chips": ["Yöntem", "Rota", "Öğrenerek Büyü"],
        "rules": [{"fn": "planet_in_house", "args": {"planet": "Mars", "house": 9}}],
        "scoring": {"base": 0.48, "boosts": [{"fn": "mars_strong_aspects", "args": {"types": ["Trine", "Conjunction"], "max_orb": 4.5}, "add": 0.12}], "cap": 0.90},
        "copy_tr": {
            "headline": "Yöntemle hız",
            "teaser": "Heves değil yöntem; yön netleşince hızlanırsın.",
            "spark": "Bir anda ‘tamam buradan gidiyorum’ hissi açılabilir ama sende bu kıvılcım en iyi plana dönünce büyür.",
            "gift": "İyi çalıştığında öğrenme, üretim ve öğretilebilir sistem kurma becerisi verir.",
            "watch": "Zorlandığında aynı anda çok fazla yön açılabilir; tek bir hatta kalmak seni güçlendirir.",
        },
        "astro_tokens": [{"type": "placement", "planet": "Mars", "house": 9}],
    },
    {
        "id": "drive_mars_opp_saturn_push_pull",
        "spark": True,
        "block_affinity": ["drive_rhythm", "mind_voice"],
        "chips": ["İtki–Fren", "Başlat–Rafine", "Süreklilik"],
        "rules": [{"fn": "aspect_between", "args": {"a": "Mars", "b": "Saturn", "types": ["Opposition"], "max_orb": 5.5}}],
        "scoring": {
            "base": 0.55,
            "boosts": [
                {"fn": "mars_in_house", "args": {"house": 9}, "add": 0.08},
                {"fn": "saturn_in_house", "args": {"house": 3}, "add": 0.08},
            ],
            "cap": 0.95,
        },
        "copy_tr": {
            "headline": "İtki–fren ritmi",
            "teaser": "Başlatınca hızlanırsın; ‘doğru mu?’ gecikirse frene basman kolay.",
            "spark": "İçeride aynı anda iki ses çalışır: biri ‘hadi’ der, diğeri ‘dur, düzelt’ der.",
            "gift": "İyi çalıştığında seni hem cesur hem de kaliteli kılar; sonuç alırsın.",
            "watch": "Zorlandığında erteleme ya da yeniden başlatma döngüsü artar; küçük ve net bir başlangıç ritmi geri toplar.",
        },
        "astro_tokens": [{"type": "aspect", "a": "Mars", "b": "Saturn", "aspect": "Opposition"}],
    },
    {
        "id": "drive_mars_trine_neptune_inspired_action",
        "spark": True,
        "block_affinity": ["drive_rhythm", "luck_creation", "talent_gifts"],
        "chips": ["İlham", "Akış", "Yaratıcı Hamle"],
        "rules": [{"fn": "aspect_between", "args": {"a": "Mars", "b": "Neptune", "types": ["Trine"], "max_orb": 3.0}}],
        "scoring": {"base": 0.44, "boosts": [{"fn": "neptune_or_mars_angular", "args": {"max_orb": 6.0}, "add": 0.10}], "cap": 0.85},
        "copy_tr": {
            "headline": "İlhamı işe çevirme",
            "teaser": "Sezgi sende havada kalmaz; doğru anda hamleye dönüşür.",
            "spark": "Bazen bir fikir bir anda ‘tamam’ diye yerine oturur ve o an hareket edince akış açılır.",
            "gift": "İyi çalıştığında yaratıcı üretim ve güçlü timing verir.",
            "watch": "Zorlandığında sis artabilir; odağı tek bir somut hatta indirmek ilhamı toplar.",
        },
        "astro_tokens": [{"type": "aspect", "a": "Mars", "b": "Neptune", "aspect": "Trine"}],
    },
    {
        "id": "drive_saturn_sextile_uranus_structured_change",
        "spark": True,
        "block_affinity": ["drive_rhythm", "career_visibility"],
        "chips": ["Yapı ve Yenilik", "Yenilik", "İç Denge"],
        "rules": [{"fn": "aspect_between", "args": {"a": "Saturn", "b": "Uranus", "types": ["Sextile", "Trine"], "max_orb": 3.0}}],
        "scoring": {"base": 0.46, "boosts": [{"fn": "either_angular", "args": {"planets": ["Saturn", "Uranus"], "max_orb": 6.0}, "add": 0.10}], "cap": 0.88},
        "copy_tr": {
            "headline": "Yeniliği yapılandırma",
            "teaser": "Senin yeniliğin kaos değil; sistem kurarak gelir.",
            "spark": "Bir şeyi yıkıp savurmaktan çok, iyileştirip sağlamlaştırmayı seçersin.",
            "gift": "İyi çalıştığında düzen kurduğun alanlarda kalıcı dönüşüm sağlar.",
            "watch": "Zorlandığında fazla mükemmellik yüklenebilir; küçük yenilemeler daha iyi çalışır.",
        },
        "astro_tokens": [{"type": "aspect", "a": "Saturn", "b": "Uranus"}],
    },
    {
        "id": "love_7th_ruler_in_8th",
        "spark": True,
        "block_affinity": ["love_depth", "partner_style"],
        "chips": ["Güven", "Sadakat", "Gerçek Temas"],
        "rules": [{"fn": "house_ruler_in_house", "args": {"house": 7, "target_house": 8}}],
        "scoring": {"base": 0.52, "boosts": [{"fn": "moon_in_house", "args": {"house": 8}, "add": 0.10}], "cap": 0.92},
        "copy_tr": {
            "headline": "Sevgi derinlik ister",
            "teaser": "Yakınlık sende yüzey değil; güven kurdukça büyür.",
            "spark": "Bağ kurunca ‘yarım’ sevmezsin; temas gerçekse yaşar, belirsizse yorar.",
            "gift": "İyi çalıştığında çok sadık ve iyileştirici bir bağ kurarsın.",
            "watch": "Zorlandığında ya tamamen açılmak ya tamamen kapanmak görülebilir; ilişki ritmi bir anda sertleşebilir.",
        },
        "astro_tokens": [{"type": "ruler_chain", "house": 7, "target_house": 8}],
    },
    {
        "id": "love_7th_ruler_in_11th_friends_to_love",
        "spark": True,
        "block_affinity": ["love_depth", "partner_style"],
        "chips": ["Arkadaşlıktan Bağ", "Birlikte Üret", "Aynı Ekip"],
        "rules": [{"fn": "house_ruler_in_house", "args": {"house": 7, "target_house": 11}}],
        "scoring": {"base": 0.48, "boosts": [{"fn": "dominance_house", "args": {"house": 11, "min_count": 2}, "add": 0.10}], "cap": 0.88},
        "copy_tr": {
            "headline": "Arkadaşlıktan ilişkiye",
            "teaser": "Bağların çoğu sosyal bağlamda büyür; birlikte üretmek güveni hızlandırır.",
            "spark": "İlişki sende çoğu zaman tek kişilik hikâye değil; bir bağlamın içinde derinleşir.",
            "gift": "İyi çalıştığında partnerin aynı zamanda yol arkadaşı olur.",
            "watch": "Zorlandığında ‘rol belirsizliği’ yorar; küçük bir netlik cümlesi zemini kurar.",
        },
        "astro_tokens": [{"type": "ruler_chain", "house": 7, "target_house": 11}],
    },
    {
        "id": "love_moon_in_8_intimacy_threshold",
        "spark": True,
        "block_affinity": ["love_depth"],
        "chips": ["Yakınlık", "Eşik", "Duygusal Güç"],
        "rules": [{"fn": "planet_in_house", "args": {"planet": "Moon", "house": 8}}],
        "scoring": {"base": 0.46, "boosts": [{"fn": "moon_aspects_personal", "args": {"max_orb": 3.5}, "add": 0.10}], "cap": 0.86},
        "copy_tr": {
            "headline": "Güven eşiği",
            "teaser": "Yakınlık artınca içerde ‘güvende miyim?’ testi çalışır.",
            "spark": "Sevgi sende duygusal bir cesaret ister; temas gerçek olunca çok açılırsın.",
            "gift": "İyi çalıştığında sezgisel, şefkatli ve derin bir bağ kurarsın.",
            "watch": "Zorlandığında geri çekilme artabilir; sinyal vermek bağı koparmadan ilerletir.",
        },
        "astro_tokens": [{"type": "placement", "planet": "Moon", "house": 8}],
    },
    {
        "id": "love_moon_trine_venus_soft_bond",
        "spark": False,
        "block_affinity": ["love_depth", "talent_gifts"],
        "chips": ["Şefkat", "Zarafet", "İyileştirici Dil"],
        "rules": [{"fn": "aspect_between", "args": {"a": "Moon", "b": "Venus", "types": ["Trine", "Sextile"], "max_orb": 2.0}}],
        "scoring": {"base": 0.40, "boosts": [{"fn": "tight_orb_aspect_bonus", "args": {"a": "Moon", "b": "Venus", "max_orb": 1.0}, "add": 0.12}], "cap": 0.80},
        "copy_tr": {
            "headline": "Sevgi dili",
            "teaser": "Duygunun dili sende yumuşak; şefkatle bağ kurma yeteneğin var.",
            "spark": "Bazen tek bir sakin cümleyle ortamı yumuşatabilirsin.",
            "gift": "İyi çalıştığında ilişkilerde iyileştirici, güven veren bir enerji olursun.",
            "watch": "Zorlandığında kırılganlığı saklamak yerine küçük ve temiz söylemek daha iyi gelir.",
        },
        "astro_tokens": [{"type": "aspect", "a": "Moon", "b": "Venus"}],
    },
    {
        "id": "love_venus_in_12_private_affection",
        "spark": True,
        "block_affinity": ["love_depth", "career_visibility"],
        "chips": ["Gizli Hassasiyet", "İçte Olgunlaşma", "Derin Sevgi"],
        "rules": [{"fn": "planet_in_house", "args": {"planet": "Venus", "house": 12}}],
        "scoring": {"base": 0.45, "boosts": [{"fn": "venus_aspects_neptune_or_moon", "args": {"max_orb": 4.0}, "add": 0.10}], "cap": 0.85},
        "copy_tr": {
            "headline": "Perde arkası sevgi",
            "teaser": "Sevgi sende biraz içeride olgunlaşır; acele değil derinlik ister.",
            "spark": "Birini hemen ‘göstererek’ değil, içeride hissettirerek seversin.",
            "gift": "İyi çalıştığında romantik ve çok şefkatli bir bağ verir.",
            "watch": "Zorlandığında kapanma artabilir; küçük bir sinyal ilişkiyi taşır.",
        },
        "astro_tokens": [{"type": "placement", "planet": "Venus", "house": 12}],
    },
    {
        "id": "career_mc_ruler_12_backstage",
        "spark": True,
        "block_affinity": ["career_visibility"],
        "chips": ["Perde Arkası Güç", "Rafine Et", "Sessiz Üretim"],
        "rules": [{"fn": "angle_ruler_in_house", "args": {"angle": "MC", "target_house": 12}}],
        "scoring": {"base": 0.50, "boosts": [{"fn": "mc_sign_known", "args": {}, "add": 0.08}], "cap": 0.90},
        "copy_tr": {
            "headline": "Pişirip çıkma ritmi",
            "teaser": "En iyi işin içeride olgunlaşınca dışarıda daha güçlü görünür.",
            "spark": "Sende görünürlük bir anda değil; önce içeride kurup sonra netleştirdiğinde büyür.",
            "gift": "İyi çalıştığında kalite, estetik ve strateji aynı yerde birleşir.",
            "watch": "Zorlandığında görünürlük ertelenebilir; küçük ama düzenli görünürlük adımları dengeyi kurar.",
        },
        "astro_tokens": [{"type": "ruler_chain", "angle": "MC", "target_house": 12}],
    },
    {
        "id": "career_mc_square_neptune_or_jupiter_visibility_sensitivity",
        "spark": True,
        "block_affinity": ["career_visibility"],
        "chips": ["Düzenli Görünürlük", "Hassas Görünürlük", "İz Bırak"],
        "rules": [
            {"fn": "angle_aspected_by", "args": {"angle": "MC", "planet": "Neptune", "types": ["Square", "Opposition", "Conjunction"], "max_orb": 3.5}},
        ],
        "scoring": {"base": 0.50, "boosts": [{"fn": "both_hits", "args": {"a": "MC", "b": ["Neptune", "Jupiter"]}, "add": 0.12}], "cap": 0.92},
        "copy_tr": {
            "headline": "Görünürlükte hassasiyet",
            "teaser": "İşin güçlü; ama görünür olduğun anlar daha hassas çalışabilir.",
            "spark": "Büyük hedefi duyarsın ama ‘tam oldu mu?’ eşiği görünürlükte yükselir.",
            "gift": "İyi çalıştığında çok rafine ve etkileyici bir sunum gücü verir.",
            "watch": "Zorlandığında bekleme uzar; düzenli küçük iz bırakmak özgüveni büyütür.",
        },
        "astro_tokens": [{"type": "angle_hit", "angle": "MC"}, {"type": "aspect_family", "topic": "MC_hard_benefic_outer"}],
    },
    {
        "id": "career_chiron_10_heal_visibility",
        "spark": True,
        "block_affinity": ["career_visibility"],
        "chips": ["Ustalık", "Şifa", "Kendi Sesin"],
        "rules": [{"fn": "planet_in_house", "args": {"planet": "Chiron", "house": 10}}],
        "scoring": {"base": 0.44, "boosts": [{"fn": "planet_near_angle", "args": {"planet": "Chiron", "angle": "MC", "max_orb": 6.0}, "add": 0.10}], "cap": 0.84},
        "copy_tr": {
            "headline": "Kendi sesini görünür kılmak",
            "teaser": "Kariyerde ‘nasıl algılanıyorum?’ hassasiyeti ustalığa dönüşebilir.",
            "spark": "Görünürlük bazen yara gibi çalışsa da, tam orası senin uzmanlık alanın olur.",
            "gift": "İyi çalıştığında öğretme, rehberlik ve ‘iyileştirici etki’ getirir.",
            "watch": "Zorlandığında saklanma artabilir; küçük görünürlük adımları şifayı başlatır.",
        },
        "astro_tokens": [{"type": "placement", "planet": "Chiron", "house": 10}],
    },
    {
        "id": "home_ic_aries_independence",
        "spark": True,
        "block_affinity": ["home_roots"],
        "chips": ["Bağımsızlık", "Şarj", "Ritim"],
        "rules": [{"fn": "ic_sign_is", "args": {"sign": "Aries"}}],
        "scoring": {"base": 0.42, "boosts": [{"fn": "ic_ruler_is_mars", "args": {}, "add": 0.10}], "cap": 0.80},
        "copy_tr": {
            "headline": "Evde inisiyatif",
            "teaser": "Köklerde ‘ben hallederim’ refleksi güçlü; ev ritmi seni hızlı toparlar.",
            "spark": "Ev içinde küçük bir düzen kurmak, iç güvenini anında yükseltir.",
            "gift": "İyi çalıştığında ev, senin şarj istasyonun olur; dış hedeflere daha rahat açılırsın.",
            "watch": "Zorlandığında her şeyi tek başına taşıma artabilir; rol paylaşımı iyi gelir.",
        },
        "astro_tokens": [{"type": "angle", "angle": "IC"}],
    },
    {
        "id": "home_moon_recharge_deep",
        "spark": True,
        "block_affinity": ["home_roots"],
        "chips": ["Duygusal Şarj", "Güven", "İç Alan"],
        "rules": [{"fn": "planet_in_house", "args": {"planet": "Moon", "house": 4}}],
        "scoring": {"base": 0.45, "boosts": [{"fn": "moon_aspect_ic", "args": {"max_orb": 5.0}, "add": 0.10}], "cap": 0.85},
        "copy_tr": {
            "headline": "Ev = şarj alanı",
            "teaser": "Ev, senin için sadece dinlenme değil; duygusal şarj alanı.",
            "spark": "İçeride güvende hissettiğinde dışarıdaki hedefler çok daha kolay akar.",
            "gift": "İyi çalıştığında ev ritmi performansını büyütür.",
            "watch": "Zorlandığında içe kapanma artabilir ve ritim daha içerde kurulmak isteyebilir.",
        },
        "astro_tokens": [{"type": "placement", "planet": "Moon", "house": 4}],
    },
    {
        "id": "luck_fortune_5_creation",
        "spark": True,
        "block_affinity": ["luck_creation", "talent_gifts"],
        "chips": ["Yaratım", "Somutlaştır", "Keyif"],
        "rules": [{"fn": "planet_in_house", "args": {"planet": "Fortune", "house": 5}}],
        "scoring": {"base": 0.50, "boosts": [{"fn": "fortune_aspected_by_benefic", "args": {"max_orb": 3.5}, "add": 0.12}], "cap": 0.90},
        "copy_tr": {
            "headline": "Şans: üretince açılır",
            "teaser": "Şans sende tesadüf değil; üretim sahnesinde açılan kapı gibi çalışır.",
            "spark": "Bir şeyi somutlaştırdığında akış hızlanır; başlatınca büyür.",
            "gift": "İyi çalıştığında yaratımın görünür oldukça fırsat üretir.",
            "watch": "Zorlandığında bekleme uzar; küçük bir başlangıç şansı hareketlendirir.",
        },
        "astro_tokens": [{"type": "placement", "planet": "Fortune", "house": 5}],
    },
    {
        "id": "fallback_identity_chart_ruler",
        "spark": False,
        "block_affinity": ["identity_aura"],
        "chips": ["Duruş", "Yön", "Çerçeve"],
        "rules": [{"fn": "always", "args": {}}],
        "scoring": {"base": 0.20, "boosts": [], "cap": 0.40},
        "copy_tr": {
            "headline": "Duruşun",
            "teaser": "Haritanın yönü, senin duruş ve karar tarzın üzerinden güçleniyor.",
            "spark": "Kendini ortaya koyma biçimin, hayatın ritmini de belirler.",
            "gift": "İyi çalıştığında netlik ve istikrar verir.",
            "watch": "Zorlandığında dağılma artabilir; küçük çerçeve iyi gelir.",
        },
        "astro_tokens": [{"type": "fallback"}],
    },
]

# Backward-compatible alias used by the current integration.
def _merge_catalogs(*catalogs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for catalog in catalogs:
        for signature in catalog:
            signature_id = str(signature.get("id") or "").strip()
            if not signature_id:
                continue
            if signature_id not in merged:
                order.append(signature_id)
            merged[signature_id] = dict(signature)
    return [merged[signature_id] for signature_id in order]


SIGNATURE_CATALOG_TR = _merge_catalogs(SIGNATURES_V0_TR, SIGNATURES_V1_TR_EXTRA)
