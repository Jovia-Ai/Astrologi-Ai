from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping


REGISTRY_VERSION = "natal_promise_archetype_registry_sprint1"


NATAL_PROMISE_ARCHETYPE_LIBRARY_V0_1: Dict[str, Dict[str, Any]] = {
    "moon_trine_venus_emotional_warmth": {
        "id": "moon_trine_venus_emotional_warmth",
        "match": {
            "labels": ["Moon trine Venus"],
            "source_refs": ["Moon:Venus:trine"],
        },
        "promise_type": "gift",
        "domains": ["love", "emotional_depth", "relationship", "creativity"],
        "themes": [
            "duygusal sıcaklık",
            "şefkat",
            "sevdiğini güzelleştirme",
            "ortamı yumuşatma",
            "sevgiyle koruma",
        ],
        "direct_meaning": "Sevdiği şeyi yumuşatan, güzelleştiren ve korumak isteyen bir kalp.",
        "lived_scenes": [
            "Birine kızsan bile onun kırılgan tarafını hissedebilmek.",
            "Sevdiğin kişinin iyi halini içten istemek.",
            "Gergin bir ortamı sıcaklıkla yumuşatmak.",
            "Sevdiğin şeyi daha güzel, daha anlamlı, daha yaşanır hale getirmek.",
        ],
        "gift": "Duyguya sıcaklık ve zarafet katmak; sevgiyle iyileştirmek.",
        "shadow_or_friction": "Fazla vermek, sevdiğini idealize etmek, kendi ihtiyacını ikinci plana atmak.",
        "growth_direction": "Sevgi verirken kendini de görünür tutmak.",
        "voice_seeds": [
            "Ay’ın Venüs’le uyumu, sende sevdiğini güzelleştiren bir kalp açıyor.",
            "Birine kızsan bile onun kırılgan tarafını hissedebilen bir yanın olabilir.",
            "Sevgi sende sadece hissetmek değil; iyi gelmek, yumuşatmak ve güzelleştirmek ister.",
        ],
        "context_modifiers": {
            "proof_raw_contains": {
                "Ay · 8. ev · Aslan": {
                    "direct_meaning": "Sevgi sende güven ve derinlik istiyor; bağlandığında kalbin kolay kolay yüzeyde kalmıyor.",
                }
            },
            "chip_contains": {
                "Ay 8. ev": {"domain_boosts": {"love_style": 0.12, "need": 0.08}},
                "Aslan": {"domain_boosts": {"love_style": 0.08}},
                "Venüs 12. ev": {"domain_boosts": {"need": 0.06}},
            },
        },
    },
    "saturn_sextile_uranus_structured_originality": {
        "id": "saturn_sextile_uranus_structured_originality",
        "match": {
            "labels": ["Saturn sextile Uranus"],
            "source_refs": ["Saturn:Uranus:sextile"],
        },
        "promise_type": "gift",
        "domains": ["mind", "identity", "career", "behavior_reflex"],
        "themes": [
            "structured originality",
            "özgün fikri yapılandırma",
            "yeniliğe omurga verme",
            "farklı olanı uygulanabilir hale getirme",
        ],
        "direct_meaning": "Farklı fikri sadece bulmak değil, ona çalışır bir form verebilmek.",
        "lived_scenes": [
            "Herkesin dağınık gördüğü yerde sistem kurmak.",
            "Yeni bir fikri gerçek hayatta uygulanabilir hale getirmek.",
            "Alışılmış yoldan sıkılsan bile tamamen zeminsiz kalmak istememek.",
            "Özgürlük ihtiyacını koparak değil, yapı kurarak yaşamak.",
        ],
        "gift": "Yenilikle disiplini aynı yerde tutabilmek.",
        "shadow_or_friction": "Fazla kontrol yeniliği boğabilir; fazla hız düzeni dağıtabilir.",
        "inner_tension": "Bir yanın sağlamlık isterken, başka bir yanın daha özgür ve farklı bir yol arar.",
        "growth_direction": "Özgün fikri sağlam bir yapıya çevirmek.",
        "voice_seeds": [
            "Senin gücün yeni fikri havada bırakmamakta; ona omurga verebilmekte.",
            "Ciddi görünen yerinin altında daha sıra dışı çalışan bir zihin var.",
            "Sende özgürlük tamamen kopmak değil; kendine ait bir sistem kurmak isteyebilir.",
        ],
        "context_modifiers": {
            "chip_contains": {
                "Yükselen Oğlak": {"domain_boosts": {"mind_style": 0.08, "mind_identity": 0.1}},
                "Satürn 3. ev": {"domain_boosts": {"mind_style": 0.12}},
                "Koç": {"domain_boosts": {"mind_style": 0.08}},
            }
        },
    },
    "saturn_trine_pluto_deep_resilience": {
        "id": "saturn_trine_pluto_deep_resilience",
        "match": {
            "labels": ["Saturn trine Pluto"],
            "source_refs": ["Saturn:Pluto:trine"],
        },
        "promise_type": "gift",
        "domains": ["identity", "career", "emotional_depth", "behavior_reflex"],
        "themes": [
            "derin dayanıklılık",
            "baskı altında dönüşüm gücü",
            "krizden yapı çıkarma",
        ],
        "direct_meaning": "Baskı geldiğinde bile yapıyı koruyup içerden dönüşebilmek.",
        "gift": "Zor zamanlarda bile çözülmek yerine omurgayı koruyabilmek.",
        "shadow_or_friction": "Her şeyi tek başına taşımaya çalışma ve duyguyu fazla sıkıştırma.",
        "growth_direction": "Gücü yalnızca dayanmakta değil, yumuşayabildiğin yerde de kurmak.",
        "voice_seeds": [
            "Zorlandığında bile dağılıp gitmeyen, içeride yapı kuran bir gücün var.",
            "Baskı arttığında sende panik değil, daha derin bir omurga devreye girebilir.",
        ],
    },
    "mercury_conjunct_jupiter_big_mind": {
        "id": "mercury_conjunct_jupiter_big_mind",
        "match": {
            "labels": ["Mercury conjunction Jupiter", "Mercury conjunct Jupiter"],
            "source_refs": ["Mercury:Jupiter:conjunction"],
        },
        "promise_type": "gift",
        "domains": ["mind", "communication", "career"],
        "themes": [
            "büyük resim kurma",
            "anlamı genişletme",
            "anlatıyı toplama",
        ],
        "direct_meaning": "Parçaları tek tek görmekten çok, aralarındaki anlamı kuran bir zihin.",
        "gift": "Bilgiyi bağlama yerleştirmek ve başkasına anlatılabilir hale getirmek.",
        "shadow_or_friction": "Fazla büyütmek ya da ayrıntı kaybı.",
        "growth_direction": "Geniş görüşü daha somut ve isabetli bir dile çevirmek.",
        "voice_seeds": [
            "Senin zihnin tek tek parçalardan çok, aralarındaki anlamı kurmak ister.",
            "Bir şeyi yalnızca bilmek değil, onu daha büyük bir çerçeveye oturtmak sana doğal gelebilir.",
        ],
    },
    "chiron_conjunct_mc_visibility_wound_to_voice": {
        "id": "chiron_conjunct_mc_visibility_wound_to_voice",
        "match": {
            "labels": ["Chiron conjunct Midheaven", "Chiron conjunct MC", "Chiron near MC"],
            "source_refs": ["Chiron:Midheaven:conjunction", "Chiron:MC:conjunction"],
        },
        "promise_type": "wound_to_gift",
        "domains": ["career", "visibility", "identity"],
        "themes": [
            "visibility wound",
            "healing voice",
            "public sensitivity",
        ],
        "direct_meaning": "Görünür olma hassasiyetini zamanla başkalarına dokunan bir sese çevirmek.",
        "lived_scenes": [
            "Ortaya çıkmadan önce çok hazır olmak istemek.",
            "Eleştiriyi gereğinden fazla içeri almak.",
            "Kendi kırılganlığından başkalarına alan açan bir dil kurmak.",
        ],
        "gift": "Kırılganlığı utanç değil, başkasına alan açan bir sezgiye çevirmek.",
        "shadow_or_friction": "Görünür olmadan önce kendini gereğinden fazla sınamak.",
        "growth_direction": "Yaranı saklamadan, ona teslim de olmadan görünür kalabilmek.",
        "voice_seeds": [
            "Görünür olmak sende bazen hassas bir yere dokunabilir; ama tam da oradan başkasına iyi gelen bir ses doğabilir.",
            "Ortaya çıkmadan önce çok hazır olmak istemen, bazen sesinin değerini olduğundan geç vermene neden olabilir.",
        ],
    },
    "moon_leo_8h_deep_proud_heart": {
        "id": "moon_leo_8h_deep_proud_heart",
        "match": {
            "proof_raw_contains": ["Ay · 8. ev · Aslan"],
            "chip_contains": ["Ay 8. ev", "Aslan"],
        },
        "promise_type": "love_style",
        "domains": ["love", "emotional_depth", "relationship"],
        "themes": [
            "deep proud heart",
            "need to be seen safely",
            "emotional intensity",
        ],
        "direct_meaning": "Derin, gururlu, kolay açılmayan ama açıldığında güçlü bağlanan kalp.",
        "gift": "Bağlandığında hem sıcak hem de sadık kalabilmek.",
        "shadow_or_friction": "Görülmek isteyip incinmekten çekinmek; kolay kolay bırakmamak.",
        "inner_tension": "Kalbin hem güven hem de özel hissetme ihtiyacı taşıyor olabilir.",
        "growth_direction": "Derinliği krizden değil, güven veren bağlardan kurmak.",
        "voice_seeds": [
            "Kalbin güven olmadan tam açılmıyor olabilir.",
            "Sevgi sende hafif yaşamıyor; bağ kurduğunda daha derin ve daha gururlu bir yere gidiyor.",
        ],
    },
    "venus_sagittarius_12h_hidden_expansive_love": {
        "id": "venus_sagittarius_12h_hidden_expansive_love",
        "match": {
            "proof_raw_contains": ["Venüs · 12. ev · Yay"],
            "chip_contains": ["Venüs 12. ev", "Yay"],
        },
        "promise_type": "career_signature",
        "domains": ["career", "creativity", "love"],
        "themes": [
            "internally maturing love",
            "hidden creation",
            "meaning-seeking affection",
        ],
        "direct_meaning": "Üretim ve görünürlük sende önce içeride olgunlaşmak isteyebilir.",
        "gift": "Görünmeyen hazırlıkta güç toplayıp ortaya daha rafine bir iş koyabilmek.",
        "shadow_or_friction": "İdealize etmek ya da görünür olmayı gereğinden fazla ertelemek.",
        "growth_direction": "İçeride büyüttüğün şeyi doğru zamanda hayata açabilmek.",
        "voice_seeds": [
            "Üretimin sende çoğu zaman önce içeride büyüyor olabilir.",
            "Bir şeyi hemen göstermekten çok, içine sindirip olgunlaştırmak senin ritmine daha yakın olabilir.",
        ],
    },
    "capricorn_asc_sun_1h_composed_self_construction": {
        "id": "capricorn_asc_sun_1h_composed_self_construction",
        "match": {
            "chip_contains": ["Yükselen Oğlak"],
        },
        "promise_type": "behavior_reflex",
        "domains": ["identity", "visibility", "behavior_reflex"],
        "themes": [
            "composed public self",
            "self-construction",
            "strong appearance",
        ],
        "direct_meaning": "Dışarıda toparlanmış ve kontrollü görünmek senin için önemli olabilir.",
        "gift": "Zor zamanda bile çizgini koruyabilmek.",
        "shadow_or_friction": "Gücü bazen sadece kontrol üzerinden taşımaya çalışma.",
        "growth_direction": "Omurganı sertlik olmadan da koruyabildiğini görmek.",
        "voice_seeds": [
            "Dışarıda güçlü ve toparlanmış görünmek senin için hafif bir konu olmayabilir.",
            "İlk tepkin çoğu zaman dağılmak değil, kendini toplamak olabilir.",
        ],
    },
    "saturn_3h_aries_speech_decision_language": {
        "id": "saturn_3h_aries_speech_decision_language",
        "match": {
            "proof_raw_contains": ["Satürn · 3. ev · Koç"],
            "chip_contains": ["Satürn 3. ev", "Koç"],
        },
        "promise_type": "mind_style",
        "domains": ["mind", "communication", "behavior_reflex"],
        "themes": [
            "speech tone decision language",
            "measured directness",
            "fast but weighted thought",
        ],
        "direct_meaning": "Söz, ton ve karar dili sende kimliğe yakın bir yerden çalışıyor olabilir.",
        "gift": "Cümleye hem ağırlık hem hız verebilmek.",
        "shadow_or_friction": "Kendini fazla tutup sonra sert çıkmak.",
        "growth_direction": "Sesi bastırmadan, sertliğe mahkûm etmeden kullanmak.",
        "voice_seeds": [
            "Bir şey sana çarptığında zihnin boşta kalmıyor; içeride hemen pozisyon alan bir taraf çalışıyor olabilir.",
            "Sözün sende hafif çalışmıyor; hem tartılıyor hem de bir anda çok net çıkabiliyor.",
        ],
    },
}


# The raw v0.2 manual delta is not present as a standalone file in the workspace.
# Sprint 1 still freezes an explicit overlay here so registry authority is
# `v0.1 + manual sprint delta`, not raw v0.1.
NATAL_PROMISE_MANUAL_DELTA_V0_2: Dict[str, Dict[str, Any]] = {
    "moon_trine_venus_emotional_warmth": {
        "preferred_types": ["love_style", "gift"],
        "gift": "Sevdiğini güzelleştirmek, ona iyi gelmek ve duyguyu yumuşatmak.",
        "voice_seeds": [
            "Kalbin birini sevdiğinde onu yalnızca sevmek değil, ona iyi gelmek de isteyebilir.",
            "Sevgi sende çoğu zaman yumuşatmak, güzelleştirmek ve korumak ister.",
        ],
    },
    "saturn_sextile_uranus_structured_originality": {
        "preferred_types": ["mind_style", "mind_identity", "gift"],
        "voice_seeds": [
            "Ciddi duran yerinin altında çok daha özgün çalışan bir zihin olabilir.",
            "Yeni fikri yalnızca bulmak değil, ona çalışır bir omurga vermek senin güçlü tarafın olabilir.",
        ],
    },
    "chiron_conjunct_mc_visibility_wound_to_voice": {
        "preferred_types": ["wound_to_gift", "career_signature"],
    },
    "moon_leo_8h_deep_proud_heart": {
        "preferred_types": ["love_style", "need"],
    },
    "venus_sagittarius_12h_hidden_expansive_love": {
        "preferred_types": ["career_signature", "love_style"],
        "direct_meaning": "Üretim ve görünürlük sende önce içeride olgunlaşmak isteyebilir.",
        "gift": "Görünmeyen hazırlıkta güç toplayıp işi daha rafine bir biçimde sunabilmek.",
        "voice_seeds": [
            "Bir şeyi hemen göstermekten çok, içine sindirip olgunlaştırmak senin ritmine daha yakın olabilir.",
            "Görünürlük sende çoğu zaman önce içeride kurduğun dengeyle güçleniyor olabilir.",
        ],
    },
}


def _deep_merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> Dict[str, Any]:
    out = deepcopy(dict(base))
    for key, value in overlay.items():
        if isinstance(value, Mapping) and isinstance(out.get(key), Mapping):
            out[key] = _deep_merge(out[key], value)
        elif isinstance(value, list) and isinstance(out.get(key), list):
            merged: list[Any] = []
            seen: set[str] = set()
            for item in [*out.get(key, []), *value]:
                marker = repr(item)
                if marker in seen:
                    continue
                seen.add(marker)
                merged.append(item)
            out[key] = merged
        else:
            out[key] = deepcopy(value)
    return out


# v0.3 addendum — Virgo / Libra / Mercury–Venus / Pluto / Mars–Uranus coverage.
# Additive only. These archetypes are placement / aspect specific; they only
# fire through the chart-signature pipeline (see ``natal_promise_packets._build_chart_signature_candidates``)
# so a label-based ``match`` block is intentionally absent on most entries.
NATAL_PROMISE_LIBRARY_V0_3: Dict[str, Dict[str, Any]] = {
    "libra_asc_venus_chart_ruler": {
        "id": "libra_asc_venus_chart_ruler",
        "match": {
            "labels": [],
            "source_refs": ["asc:libra", "chart_ruler:venus"],
        },
        "promise_type": "behavior_reflex",
        "preferred_types": ["behavior_reflex", "mind_identity", "gift"],
        "domains": ["identity", "relationship", "visibility", "social_field"],
        "themes": [
            "dışarıda uyum",
            "insanları okuma",
            "sosyal sezgi",
            "estetik üslup",
            "içeride seçicilik",
        ],
        "direct_meaning": "Dışarıdan uyumlu ve dengeli görünürken, içeride kiminle ne kadar yakınlaşacağını seçen dikkatli bir taraf.",
        "lived_scenes": [
            "Bir ortama girdiğinde önce havayı ve insanlar arasındaki tonu okumak.",
            "Dışarıdan sakin ve uyumlu görünürken içeride çok şey tartmak.",
            "Herkese aynı mesafede görünmek ama içeride seçici olmak.",
        ],
        "gift": "İnsan ilişkilerinde denge, zarafet ve üslup kurma becerisi.",
        "shadow_or_friction": "Fazla uyum sağlamak, kendi tercihini geciktirmek, dışarıdaki dengeyi korumak için içeride gerilmek.",
        "inner_tension": "Dışarıda uyumu korumak isteyen tarafla, içeride daha seçici olan taraf aynı anda çalışabilir.",
        "growth_direction": "Dengeyi sadece ortamı yatıştırmak için değil, kendi yerini de koruyarak kurmak.",
        "voice_seeds": [
            "Dışarıdan uyumlu görünsen de içeride oldukça seçici bir tarafın olabilir.",
            "Bir ortama girdiğinde önce havayı ve insanlar arasındaki tonu okuyabilirsin.",
            "Denge senin için herkesi memnun etmek değil; kendi yerini kaybetmeden ilişki kurabilmek.",
        ],
    },
    "venus_virgo_11h_selective_social_care": {
        "id": "venus_virgo_11h_selective_social_care",
        "match": {"labels": [], "source_refs": ["planet:Venus:sign:Virgo:house:11"]},
        "promise_type": "love_style",
        "preferred_types": ["love_style", "gift"],
        "domains": ["relationship", "community", "creativity", "identity"],
        "themes": [
            "seçici sevgi",
            "fayda göstererek değer verme",
            "arkadaşlık içinde ilişki",
            "kalite ve emek",
        ],
        "direct_meaning": "Sevgi ve değer verme, sende çoğu zaman faydalı olmak, düzenlemek ve bir çevre içinde işe yarayan bağ kurmak üzerinden çalışabilir.",
        "lived_scenes": [
            "Sevdiğin kişiye büyük sözler etmek yerine onun hayatını kolaylaştıran küçük şeyler yapmak.",
            "Yakınlıkta kalite, emek ve tutarlılık aramak.",
            "Arkadaşlıkla başlayan veya ortak bir çevrede olgunlaşan bağlara önem vermek.",
        ],
        "gift": "İnce bakım, detay görme, ilişkide fayda ve sadelikle sevgi gösterme.",
        "shadow_or_friction": "Fazla eleştirel olmak, sevgiyi düzeltilecek şeyler listesine çevirmek, kendini yeterince iyi hissetmeden açılmamak.",
        "inner_tension": "Sevgi vermek isteyen tarafla, her şey doğru olsun isteyen taraf arasında gerilim olabilir.",
        "growth_direction": "Sevgiyi mükemmelleştirmeye çalışmadan, emeğin içindeki sıcaklığı görünür kılmak.",
        "voice_seeds": [
            "Sevgi sende çoğu zaman büyük sözlerden çok küçük ama işe yarayan dikkatlerle görünür.",
            "Birini sevdiğinde onun hayatını biraz daha düzenli, hafif veya iyi hale getirmek isteyebilirsin.",
            "Yakınlıkta sadece his değil, emek ve tutarlılık da ararsın.",
        ],
    },
    "sun_virgo_12h_quiet_inner_self": {
        "id": "sun_virgo_12h_quiet_inner_self",
        "match": {"labels": [], "source_refs": ["planet:Sun:sign:Virgo:house:12"]},
        "promise_type": "behavior_reflex",
        "preferred_types": ["behavior_reflex", "mind_identity", "gift"],
        "domains": ["identity", "spirituality", "work", "inner_world"],
        "themes": [
            "görünmeden çalışma",
            "iç dünyada düzen",
            "faydalı olma arzusu",
            "kendini geri planda tutma",
            "içsel analiz",
        ],
        "direct_meaning": "Kimlik, görünür olmaktan çok içeride işleyen analiz, fayda sağlama ve perde arkasında iyileştirme ihtiyacıyla şekillenebilir.",
        "lived_scenes": [
            "Bir şeyi açıkça sahiplenmeden önce kendi içinde uzun süre düzeltmek.",
            "İnsanlara yardım ederken görünür olmaktan çok işin işe yaramasını önemsemek.",
            "İçeride çok çalışmasına rağmen dışarıdan bunu az göstermek.",
        ],
        "gift": "Perde arkasında güçlü emek, içgörü, fayda sağlama ve iyileştirme kapasitesi.",
        "shadow_or_friction": "Kendini fazla geri plana atmak, yeterince hazır hissetmeden görünmemek, kusura takılıp kendi ışığını küçültmek.",
        "inner_tension": "Görünür olmak isteyen tarafla, önce her şeyi içeride düzeltmek isteyen taraf aynı anda çalışabilir.",
        "growth_direction": "Faydalı olmayı kendini saklamanın değil, kendini daha doğru göstermenin yolu haline getirmek.",
        "voice_seeds": [
            "Kendini çoğu zaman sahnenin ortasında değil, arka planda işe yarayan şeyi kurarken bulabilirsin.",
            "Görünmeden önce içeride düzeltmek, temizlemek ve işe yarar hale getirmek isteyebilirsin.",
            "Senin ışığın bazen yüksek sesle değil, bir şeyi gerçekten iyileştirdiğinde görünür.",
        ],
    },
    "mercury_virgo_12h_private_analytical_mind": {
        "id": "mercury_virgo_12h_private_analytical_mind",
        "match": {"labels": [], "source_refs": ["planet:Mercury:sign:Virgo:house:12"]},
        "promise_type": "mind_style",
        "preferred_types": ["mind_style", "mind_identity", "gift"],
        "domains": ["mind", "communication", "inner_world", "work"],
        "themes": [
            "içerde çalışan zihin",
            "detay ve ayrıştırma",
            "sessiz analiz",
            "kusur fark etme",
        ],
        "direct_meaning": "Zihin, dışarıdan hemen görünmeyen ama içeride sürekli ayrıştıran, düzenleyen ve anlamaya çalışan bir hat gibi çalışabilir.",
        "lived_scenes": [
            "Bir konuşmadan sonra söylenenleri kendi içinde tekrar ayrıştırmak.",
            "Herkesin kaçırdığı küçük bir detayı fark etmek.",
            "Bir şeyi anlatmadan önce içeride doğru kelimeyi aramak.",
        ],
        "gift": "İnce analiz, görünmeyeni fark etme, karmaşık şeyi sadeleştirme.",
        "shadow_or_friction": "Fazla düşünmek, kusura takılmak, kendini ifade etmeden önce zihinde yorulmak.",
        "inner_tension": "Bir şeyi söylemek isteyen tarafla, önce tamamen doğru hale getirmek isteyen taraf arasında gerilim olabilir.",
        "growth_direction": "Zihnindeki analizi suskunluğa hapsetmeden, sade ve anlaşılır bir dile çevirmek.",
        "voice_seeds": [
            "Zihnin dışarıdan göründüğünden çok daha fazla şeyi içeride işliyor olabilir.",
            "Bir şeyi söylemeden önce kendi içinde defalarca ayıklamak isteyebilirsin.",
            "Senin aklın karmaşayı büyütmek için değil, doğru yerinden sadeleştirmek için çalışıyor.",
        ],
    },
    "moon_gemini_9h_curious_mind": {
        "id": "moon_gemini_9h_curious_mind",
        "match": {"labels": [], "source_refs": ["planet:Moon:sign:Gemini:house:9"]},
        "promise_type": "mind_style",
        "preferred_types": ["mind_style", "mind_identity"],
        "domains": ["mind", "emotional_world", "learning", "belief"],
        "themes": [
            "duyguyu düşünerek işleme",
            "anlam arayışı",
            "merak",
            "uzak perspektif",
            "fikirle rahatlama",
        ],
        "direct_meaning": "Duygular, sende çoğu zaman konuşarak, düşünerek, anlam arayarak ve büyük resmi görmeye çalışarak hareket eder.",
        "lived_scenes": [
            "Hissettiğin şeyi anlamlandırmadan tam rahatlayamamak.",
            "Duygu yükseldiğinde konuşmak, okumak veya bir fikre bağlanmak istemek.",
            "Bir olayın sadece ne olduğunu değil, ne anlama geldiğini de sormak.",
        ],
        "gift": "Duyguyu fikirle açmak, bağlantı kurmak, öğrenerek rahatlamak.",
        "shadow_or_friction": "Duyguyu fazla zihinselleştirmek, hissetmeden açıklamaya çalışmak.",
        "inner_tension": "Kalp bir şey hissederken zihin hemen anlam ve açıklama arayabilir.",
        "growth_direction": "Duyguyu sadece açıklamak yerine, önce bedeninde ve kalbinde yer açarak dinlemek.",
        "voice_seeds": [
            "Bir şeyi hissettiğinde onu anlamlandırmadan tam rahatlayamayabilirsin.",
            "Duygun çoğu zaman bir soruya, bir fikre ya da daha büyük bir anlama bağlanmak ister.",
            "Hislerini konuşarak açman kolay olabilir; ama bazen açıklamadan önce hissetmen gerekir.",
        ],
    },
    "moon_square_mercury_emotion_mind_friction": {
        "id": "moon_square_mercury_emotion_mind_friction",
        "match": {
            "labels": ["Moon square Mercury"],
            "source_refs": ["Moon:Mercury:square"],
        },
        "promise_type": "wound_to_gift",
        "preferred_types": ["wound_to_gift", "mind_style"],
        "domains": ["mind", "emotional_world", "communication"],
        "themes": [
            "duygu ve düşünce çatışması",
            "hızlı iç konuşma",
            "yanlış anlaşılma hassasiyeti",
            "zihinsel-duygusal gerilim",
        ],
        "direct_meaning": "Hissettiğin şeyle onu nasıl anlatacağın her zaman aynı anda rahat akmayabilir.",
        "lived_scenes": [
            "Bir şeyi hissederken hemen anlatmaya çalışmak ama kelimenin oturmaması.",
            "Duygu yükseldiğinde zihnin hızlanması.",
            "Konuştuktan sonra 'bunu böyle demek istemedim' diye içinden geçirmek.",
        ],
        "gift": "Duyguyu dile çevirme konusunda zamanla çok incelikli bir beceri geliştirmek.",
        "shadow_or_friction": "Fazla açıklamak, duyguyu zihinde döndürmek, yanlış anlaşılma kaygısı.",
        "inner_tension": "Kalp hızlanırken zihin de hızlanır; bazen ikisi birbirini sakinleştirmek yerine daha çok karıştırabilir.",
        "growth_direction": "Önce duyguyu tanımak, sonra cümleyi kurmak.",
        "voice_seeds": [
            "Hissettiğin şeyle onu nasıl anlatacağın bazen aynı anda rahat akmayabilir.",
            "Duygu yükseldiğinde zihnin de hızlanıyor olabilir.",
            "Bazı cümleler tam hissettiğin yere denk gelene kadar içeride birkaç kez değişebilir.",
        ],
    },
    "moon_square_venus_need_affection_friction": {
        "id": "moon_square_venus_need_affection_friction",
        "match": {
            "labels": ["Moon square Venus"],
            "source_refs": ["Moon:Venus:square"],
        },
        "promise_type": "wound_to_gift",
        "preferred_types": ["wound_to_gift", "love_style"],
        "domains": ["relationship", "love", "emotional_world"],
        "themes": [
            "ihtiyaç ve sevgi dili arasında gerilim",
            "sevilme isteği",
            "yakınlıkta huzursuzluk",
            "değer görme hassasiyeti",
        ],
        "direct_meaning": "Duygusal ihtiyacınla sevgi gösterme veya sevgi alma biçimin bazen aynı yerden akmayabilir.",
        "lived_scenes": [
            "Birinden ilgi isterken bunu nasıl isteyeceğini bilememek.",
            "Sevildiğin halde tam rahatlamamak.",
            "Küçük bir ilgisizlikte değerin sorgulanıyormuş gibi hissetmek.",
        ],
        "gift": "Sevgi dilini ve duygusal ihtiyacını zamanla daha dürüst bir yerde buluşturmak.",
        "shadow_or_friction": "Memnuniyetsizlik, fazla verme, karşılık beklerken bunu açık söyleyememek.",
        "inner_tension": "Kalbin yakınlık isterken, sevgi dilin bunu dolaylı veya kontrollü göstermeye çalışabilir.",
        "growth_direction": "Ne istediğini dolaylı yollardan değil, daha sade ve açık bir yerden göstermek.",
        "voice_seeds": [
            "Sevgi görmekle gerçekten anlaşılmış hissetmek sende aynı şey olmayabilir.",
            "Yakınlıkta küçük bir ilgisizlik bile içeride büyük bir soru açabilir.",
            "Duygusal ihtiyacını dolaylı yollardan değil, daha açık bir yerden göstermeyi öğreniyorsun.",
        ],
    },
    "moon_opposite_pluto_emotional_intensity_control": {
        "id": "moon_opposite_pluto_emotional_intensity_control",
        "match": {
            "labels": ["Moon opposite Pluto", "Moon opposition Pluto"],
            "source_refs": ["Moon:Pluto:opposition"],
        },
        "promise_type": "wound_to_gift",
        "preferred_types": ["wound_to_gift", "need"],
        "domains": ["relationship", "emotional_world", "mind"],
        "themes": [
            "yoğun duygu",
            "kontrol ve teslimiyet",
            "duygusal güç savaşı",
            "kolay bırakamama",
            "derin sezgi",
        ],
        "direct_meaning": "Duygular yüzeyde kalmayabilir; bir şey dokunduğunda içeride daha derin ve bazen daha kontrolcü bir hat açılabilir.",
        "lived_scenes": [
            "Bir konuyu kapattığını sanıp içeride hâlâ taşımak.",
            "Birinin niyetini anlamaya çalışırken fazla derine inmek.",
            "Güven kırıldığında kolay kolay eski haline dönememek.",
        ],
        "gift": "İnsanların altında çalışan duyguyu sezmek, krizi dönüştürmek, derin psikolojik okuma.",
        "shadow_or_friction": "Takılı kalmak, kontrol etmek, duyguyu bırakmakta zorlanmak, her şeyi güç meselesi gibi hissetmek.",
        "inner_tension": "Kalp yakınlık isterken, kontrolü kaybetmekten de çekinebilir.",
        "growth_direction": "Duygunun derinliğini kontrol etmek için değil, kendini daha doğru tanımak için kullanmak.",
        "voice_seeds": [
            "Duygular sende kolay kolay yüzeyde kalmayabilir.",
            "Bir şey gerçekten dokunduğunda, onu sadece hissedip geçmek zor olabilir.",
            "Derin sezgin, kontrol ihtiyacıyla değil açıklıkla birleştiğinde çok güçlü çalışır.",
        ],
    },
    "mercury_conjunct_venus_refined_relational_language": {
        "id": "mercury_conjunct_venus_refined_relational_language",
        "match": {
            "labels": ["Mercury conjunct Venus", "Mercury conjunction Venus"],
            "source_refs": ["Mercury:Venus:conjunction"],
        },
        "promise_type": "gift",
        "preferred_types": ["gift", "mind_style"],
        "domains": ["communication", "relationship", "creativity", "social_field"],
        "themes": [
            "zarif dil",
            "ilişki kuran zihin",
            "estetik ifade",
            "güzel anlatma",
        ],
        "direct_meaning": "Düşünce ve sevgi dili birbirine yakın çalışır; kelimelerle bağ kurmak, yumuşatmak ve güzelleştirmek güçlü bir yetenek olabilir.",
        "lived_scenes": [
            "Bir şeyi sert söylemek yerine daha güzel, daha kabul edilebilir bir dille anlatmaya çalışmak.",
            "Yazı, konuşma veya anlatıda estetik aramak.",
            "Birinin ne duymaya ihtiyacı olduğunu sezmek.",
        ],
        "gift": "Zarif ifade, estetik zihin, ilişki kuran dil.",
        "shadow_or_friction": "Fazla düzgün söylemeye çalışıp gerçek ihtiyacı geciktirmek, rahatsızlığı yumuşatarak saklamak.",
        "inner_tension": "Güzel söylemek isteyen tarafla, net söylemek isteyen taraf bazen farklı yönlere çekebilir.",
        "growth_direction": "Üslubu korurken gerçeği de eksiltmemek.",
        "voice_seeds": [
            "Kelimeler sende sadece anlatmak için değil, bağ kurmak için de çalışabilir.",
            "Bir şeyi nasıl söylediğin, ne söylediğin kadar önemli olabilir.",
            "Güzel anlatma yeteneğin, gerçeği saklamadığında daha güçlü olur.",
        ],
    },
    "mercury_square_pluto_deep_mind_pressure": {
        "id": "mercury_square_pluto_deep_mind_pressure",
        "match": {
            "labels": ["Mercury square Pluto"],
            "source_refs": ["Mercury:Pluto:square"],
        },
        "promise_type": "wound_to_gift",
        "preferred_types": ["wound_to_gift", "mind_style"],
        "domains": ["mind", "communication", "emotional_depth"],
        "themes": [
            "derin düşünce",
            "zihinsel takılma",
            "güç ve söz",
            "araştırma",
        ],
        "direct_meaning": "Zihin yüzeyde kalmak istemez; bir şeyi anlamak istediğinde köküne inene kadar bırakmak zor olabilir.",
        "lived_scenes": [
            "Bir konuşmadaki alt anlamı yakalamaya çalışmak.",
            "Bir fikre takılıp onu tamamen çözmek istemek.",
            "Sözün güç veya savunma alanına dönüşmesi.",
        ],
        "gift": "Derin araştırma, psikolojik sezgi, sözün altında çalışan şeyi fark etme.",
        "shadow_or_friction": "Takıntılı düşünmek, şüpheye düşmek, kelimeleri güç savaşına çevirmek.",
        "inner_tension": "Anlamak isteyen tarafla kontrol etmek isteyen taraf birbirine karışabilir.",
        "growth_direction": "Derin düşünceyi zihinsel baskıya değil, net ve dönüştürücü içgörüye çevirmek.",
        "voice_seeds": [
            "Zihnin bir konunun yüzeyinde kalmak istemeyebilir.",
            "Bir cümlenin altındaki niyeti sezmek sende güçlü olabilir.",
            "Derin düşüncen, kontrol ihtiyacıyla değil açıklıkla birleştiğinde gerçek içgörüye dönüşür.",
        ],
    },
    "venus_square_pluto_intense_love": {
        "id": "venus_square_pluto_intense_love",
        "match": {
            "labels": ["Venus square Pluto"],
            "source_refs": ["Venus:Pluto:square"],
        },
        "promise_type": "love_style",
        "preferred_types": ["love_style", "wound_to_gift"],
        "domains": ["relationship", "love", "emotional_depth"],
        "themes": [
            "yoğun çekim",
            "güç ve kontrol",
            "kolay bırakamama",
            "değer görme hassasiyeti",
            "dönüşen sevgi",
        ],
        "direct_meaning": "Sevgi ve çekim sende hafif kalmayabilir; bağ kurduğunda yoğunluk, değer görme ve kontrol temaları da çalışabilir.",
        "lived_scenes": [
            "Birine çekildiğinde bunu kolayca sıradan bir hoşlanma gibi yaşamamak.",
            "Yakınlıkta güç dengelerini çok hızlı hissetmek.",
            "Bir bağın sende uzun süre iz bırakması.",
        ],
        "gift": "Derin bağ kurma, sevginin dönüştürücü tarafını görme, ilişki dinamiklerini sezme.",
        "shadow_or_friction": "Kıskançlık, kontrol, takılı kalma, değerini karşı tarafın tavrına fazla bağlama.",
        "inner_tension": "Kalp teslim olmak isterken, bir tarafın güvende kalmak için kontrol etmek isteyebilir.",
        "growth_direction": "Yoğunluğu güç savaşına değil, dürüst ve dönüştürücü yakınlığa çevirmek.",
        "voice_seeds": [
            "Sevgi sende kolay kolay hafif bir yerde kalmayabilir.",
            "Birine çekildiğinde, o bağın altında çalışan güç dengesini de hızlı hissedebilirsin.",
            "Yoğunluğu kontrol etmeye çalışmadığında, ilişki seni daha dürüst bir yakınlığa taşıyabilir.",
        ],
    },
    "mars_leo_11h_warm_visible_drive": {
        "id": "mars_leo_11h_warm_visible_drive",
        "match": {"labels": [], "source_refs": ["planet:Mars:sign:Leo:house:11"]},
        "promise_type": "drive",
        "preferred_types": ["drive", "behavior_reflex"],
        "domains": ["community", "creativity", "identity", "relationship"],
        "themes": [
            "topluluk içinde görünme",
            "yaratıcı cesaret",
            "sosyal sahnede hareket",
            "arkadaş çevresinde liderlik",
        ],
        "direct_meaning": "Hareket enerjisi, topluluklar veya ortak idealler içinde görünür olma ve kendini yaratıcı biçimde gösterme isteğiyle çalışabilir.",
        "lived_scenes": [
            "Bir grubun içinde kendi rengini göstermek istemek.",
            "Arkadaş çevresinde veya sosyal alanda inisiyatif almak.",
            "Bir fikri sahneye koymak, görünür kılmak ya da insanları harekete geçirmek.",
        ],
        "gift": "Sosyal cesaret, yaratıcı hareket, topluluk içinde sıcak liderlik.",
        "shadow_or_friction": "Gurur, dramatik tepki, sosyal alanda onay bekleme, kendi rengini göstermek için fazla yüklenme.",
        "inner_tension": "Bir gruba ait olmak isterken, o grubun içinde özel ve görünür kalmak da isteyebilirsin.",
        "growth_direction": "Işığını başkalarını bastırmadan, ortak bir alana canlılık katmak için kullanmak.",
        "voice_seeds": [
            "Bir grubun içinde kaybolmak değil, kendi rengini göstermek isteyebilirsin.",
            "Sosyal alanda hareket ettiğinde sıcak, cesur ve dikkat çeken bir enerjin var.",
            "Ait olduğun yerde bile kendi ışığını korumak senin için önemli olabilir.",
        ],
    },
    "mars_opposite_uranus_freedom_in_action": {
        "id": "mars_opposite_uranus_freedom_in_action",
        "match": {
            "labels": ["Mars opposite Uranus", "Mars opposition Uranus"],
            "source_refs": ["Mars:Uranus:opposition"],
        },
        "promise_type": "wound_to_gift",
        "preferred_types": ["wound_to_gift", "drive"],
        "domains": ["relationship", "creativity", "community", "behavior_reflex"],
        "themes": [
            "özgürlük ihtiyacı",
            "ani hareket",
            "sıkışmaya tepki",
            "yaratıcı elektrik",
        ],
        "direct_meaning": "Hareket enerjisi hızlı, özgür ve beklenmedik çalışabilir; sıkıştığında bir anda yön değiştirme isteği doğabilir.",
        "lived_scenes": [
            "Bir şey seni fazla kontrol ettiğinde aniden uzaklaşmak istemek.",
            "Heyecan veren insanlara veya ortamlara hızlı çekilmek.",
            "Rutinleşen bir ilişkide veya projede içinin daralması.",
        ],
        "gift": "Cesur yenilik, hızlı çözüm, yaratıcı sıçrama, bağımsız hareket.",
        "shadow_or_friction": "Sabırsız kopuş, ani tepki, başladığın şeyi hızla bırakmak, yakınlıkta sıkışma hissi.",
        "inner_tension": "Yakınlık veya bağlılık isterken, bir tarafın da özgür ve kontrol edilmemiş kalmak ister.",
        "growth_direction": "Özgürlük ihtiyacını kopuşla değil, daha açık sınır ve canlı hareket alanıyla kurmak.",
        "voice_seeds": [
            "Sıkıştığını hissettiğinde bir anda uzaklaşma isteğin yükselebilir.",
            "Heyecan ve özgürlük sende aynı anda çalışır.",
            "Özgür kalma ihtiyacını koparak değil, kendi alanını açıkça kurarak yaşayabilirsin.",
        ],
    },
    "mars_square_chiron_tender_courage": {
        "id": "mars_square_chiron_tender_courage",
        "match": {
            "labels": ["Mars square Chiron"],
            "source_refs": ["Mars:Chiron:square"],
        },
        "promise_type": "wound_to_gift",
        "preferred_types": ["wound_to_gift", "behavior_reflex"],
        "domains": ["behavior_reflex", "relationship", "identity", "community"],
        "themes": [
            "kendini ortaya koyma yarası",
            "cesaret ve hassasiyet",
            "öfke ve savunma",
            "kırılgan cesaret",
        ],
        "direct_meaning": "Kendini ortaya koymak, harekete geçmek veya tepki vermek hassas bir yerden geçebilir; zamanla bu hassasiyet daha bilinçli bir cesarete dönüşebilir.",
        "lived_scenes": [
            "Bir şey istediğinde bunu doğrudan söylemekte zorlanmak.",
            "Kendini savunurken fazla sertleşmek ya da tam tersi geri çekilmek.",
            "Öfkenin altında aslında görülme veya incinme hassasiyeti olması.",
        ],
        "gift": "Kırılganlığı bastırmadan cesaret geliştirmek, başkalarının kendini ortaya koymasına alan açmak.",
        "shadow_or_friction": "Ani savunma, öfkeyi saklama, hareket etmekten çekinme, kendini gösterince yara alma korkusu.",
        "inner_tension": "Bir yanın hemen hareket etmek isterken, başka bir yanın incinmemek için durabilir.",
        "growth_direction": "Cesareti sertleşmeden, hassasiyeti de geri çekilmeden taşımak.",
        "voice_seeds": [
            "Kendini ortaya koymak sende bazen hassas bir yerden geçebilir.",
            "Öfkenin altında çoğu zaman görülme veya incinme ihtiyacı olabilir.",
            "Cesaretin, kırılganlığını saklamadan hareket edebildiğinde güçlenir.",
        ],
    },
    "mc_cancer_moon_gemini_9h_teaching_voice": {
        "id": "mc_cancer_moon_gemini_9h_teaching_voice",
        "match": {"labels": [], "source_refs": ["mc:cancer:ruler_route:moon:9"]},
        "promise_type": "career_signature",
        "preferred_types": ["career_signature", "mind_style"],
        "domains": ["career", "visibility", "teaching", "communication"],
        "themes": [
            "koruyucu görünürlük",
            "anlatma ve öğretme",
            "duygusal zeka ile bilgi",
            "duyarlı public voice",
        ],
        "direct_meaning": "Dış dünyada bıraktığın iz, insanlara güvenli ve duyarlı bir alan açarken aynı zamanda bilgi, anlatı veya perspektif verme üzerinden çalışabilir.",
        "lived_scenes": [
            "Bir konuyu anlatırken karşı tarafın kendini daha güvende hissetmesini istemek.",
            "Görünür olduğunda sert bir otoriteden çok, anlayan ve açıklayan bir ses taşımak.",
            "Kariyerde öğretmek, anlatmak, yazmak veya rehberlik etmek.",
        ],
        "gift": "Duyarlı anlatım, koruyucu öğretme, bilgiyi insani bir tonda aktarma.",
        "shadow_or_friction": "Fazla koruyucu olmak, görünmeden önce herkesi gözetmeye çalışmak, kendi yönünü geciktirmek.",
        "inner_tension": "İnsanlara güven vermek isterken, kendi görünürlüğünü erteleyebilirsin.",
        "growth_direction": "Duyarlılığı geri çekilmek için değil, daha insani bir görünürlük dili kurmak için kullanmak.",
        "voice_seeds": [
            "Görünür olduğunda insanlara sadece bilgi değil, güven hissi de vermek isteyebilirsin.",
            "Kariyer hattında anlatmak, açıklamak ve karşı tarafın duygusunu gözetmek birlikte çalışabilir.",
            "Senin public sesin sert bir otoriteden çok, anlayan ve perspektif açan bir yerden güçlenir.",
        ],
    },
    "saturn_taurus_8h_steady_public_maturity": {
        "id": "saturn_taurus_8h_steady_public_maturity",
        "match": {"labels": [], "source_refs": ["planet:Saturn:sign:Taurus:house:8"]},
        "promise_type": "career_signature",
        "preferred_types": ["career_signature", "wound_to_gift"],
        "domains": ["career", "emotional_depth", "money_self_worth", "identity"],
        "themes": [
            "derin dayanıklılık",
            "yavaş olgunlaşma",
            "güven ve kontrol",
            "krizden yapı çıkarma",
        ],
        "direct_meaning": "Derin güven, kaynak, kriz ve kontrol temaları zamanla daha sağlam bir public duruşa ve olgun kariyer çizgisine dönüşebilir.",
        "lived_scenes": [
            "Zor veya belirsiz bir alanda bile yavaş yavaş güven inşa etmek.",
            "Görünür olmadan önce temelin sağlam olduğundan emin olmak.",
            "Krizli ya da hassas konularda soğukkanlı kalmaya çalışmak.",
        ],
        "gift": "Sabır, olgunluk, krizden yapı çıkarma, güven veren profesyonel duruş.",
        "shadow_or_friction": "Fazla kontrol, güvenmeden açılmamak, kaynak/değer konularında katılaşmak, geç görünür olmak.",
        "inner_tension": "Güven istemekle, güven gelene kadar her şeyi kontrol etmeye çalışmak aynı anda çalışabilir.",
        "growth_direction": "Kontrolü tek güven kaynağı yapmadan, derin dayanıklılığını görünür bir olgunluğa çevirmek.",
        "voice_seeds": [
            "Zor alanlarda bile yavaş yavaş güven inşa eden bir tarafın var.",
            "Görünür olmadan önce temelin sağlam olduğundan emin olmak isteyebilirsin.",
            "Krizden kaçmak yerine, zamanla ondan daha sağlam bir yapı çıkarabilirsin.",
        ],
    },
    "sun_opposite_jupiter_service_expansion_tension": {
        "id": "sun_opposite_jupiter_service_expansion_tension",
        "match": {
            "labels": ["Sun opposite Jupiter", "Sun opposition Jupiter"],
            "source_refs": ["Sun:Jupiter:opposition"],
        },
        "promise_type": "wound_to_gift",
        "preferred_types": ["wound_to_gift", "drive"],
        "domains": ["identity", "work", "belief", "visibility"],
        "themes": [
            "fayda ve büyüme gerilimi",
            "fazla verme",
            "büyük ideal",
            "sınır ve genişleme",
        ],
        "direct_meaning": "Faydalı, düzenli ve doğru olanı yapmak isteyen tarafla, daha büyük bir anlam ve genişleme isteyen taraf birbirini çekebilir.",
        "lived_scenes": [
            "Bir işi küçük ve net tutman gerekirken onu büyütmek istemek.",
            "Yardım etmek isterken kendi sınırını kaçırmak.",
            "Günlük sorumlulukla büyük ideal arasında kalmak.",
        ],
        "gift": "Büyük resmi görürken faydalı ve işlevsel kalabilmek.",
        "shadow_or_friction": "Fazla söz vermek, fazla yük almak, dağılmak, ölçüyü kaçırmak.",
        "inner_tension": "Düzen kurmak isteyen tarafla, genişlemek isteyen taraf farklı yönlere çekebilir.",
        "growth_direction": "Büyümeyi sınırla, faydayı da kendini tüketmeden kurmak.",
        "voice_seeds": [
            "Faydalı olmak isteyen tarafınla daha büyük bir etki yaratmak isteyen tarafın aynı anda çalışabilir.",
            "Bazen bir işi hem kusursuz hem de büyük yapmak isterken yorulabilirsin.",
            "Gerçek büyüme, her şeyi büyütmekten değil, doğru ölçüyü bulmaktan gelir.",
        ],
    },
    "neptune_4h_soft_inner_presence": {
        "id": "neptune_4h_soft_inner_presence",
        "match": {"labels": [], "source_refs": ["planet:Neptune:house:4"]},
        "promise_type": "behavior_reflex",
        "preferred_types": ["behavior_reflex", "gift"],
        "domains": ["identity", "home_family", "spirituality", "emotional_world"],
        "themes": [
            "yumuşak iç dünya",
            "aile köklerde belirsizlik",
            "sezgisel varlık",
            "dışarıya yumuşak etki",
        ],
        "direct_meaning": "İç dünyada ve köklenme hissinde akışkanlık olabilir; dışarıdaki varlığın ise daha yumuşak, sezgisel veya kolay hisseden bir ton taşıyabilir.",
        "lived_scenes": [
            "Ev, aile veya köklerle ilgili duyguların net çizgilerle değil, sezgisel hislerle çalışması.",
            "Bir ortama girdiğinde insanların senin yumuşak veya sakinleştirici tarafını hissetmesi.",
            "İç güvenliği somut kurallar yerine atmosfer, huzur ve his üzerinden aramak.",
        ],
        "gift": "Sezgisel varlık, yumuşak etki, ruhsal duyarlılık, atmosfer okuma.",
        "shadow_or_friction": "Sınırların bulanıklaşması, aile/köklerde netlik eksikliği, başkasının duygusunu taşıma.",
        "inner_tension": "Yumuşak kalmak isteyen tarafla, net bir iç güven kurmak isteyen taraf aynı anda çalışabilir.",
        "growth_direction": "Yumuşaklığını kaybetmeden sınır kurmak; sezgini kendini dağıtmadan kullanmak.",
        "voice_seeds": [
            "İç dünyan net çizgilerden çok hisler, atmosferler ve sezgilerle çalışabilir.",
            "İnsanlar sende bazen yumuşak, sakinleştirici veya sezgisel bir etki hissedebilir.",
            "Yumuşaklığın güçlü bir hediye; sınırla birleştiğinde seni dağıtmak yerine derinleştirir.",
        ],
    },
}


def get_natal_promise_archetype_registry_sprint1() -> Dict[str, Any]:
    entries: Dict[str, Dict[str, Any]] = {}
    for key, entry in NATAL_PROMISE_ARCHETYPE_LIBRARY_V0_1.items():
        overlay = NATAL_PROMISE_MANUAL_DELTA_V0_2.get(key) or {}
        entries[key] = _deep_merge(entry, overlay)
    for key, overlay in NATAL_PROMISE_MANUAL_DELTA_V0_2.items():
        if key not in entries:
            entries[key] = deepcopy(dict(overlay))
    # v0.3 addendum — additive overlay, never replaces v0.1/v0.2 archetypes.
    for key, entry in NATAL_PROMISE_LIBRARY_V0_3.items():
        if key not in entries:
            entries[key] = deepcopy(dict(entry))
    return {
        "version": REGISTRY_VERSION,
        "authority": "v0.1_plus_manual_delta_v0_2_plus_v0_3",
        "entries": entries,
    }
