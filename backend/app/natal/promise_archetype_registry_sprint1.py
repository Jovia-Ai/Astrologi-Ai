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


# v0.4 addendum — Gemini / Aries / Aquarius / Scorpio coverage.
# Additive only. Designed to recover the 2020-04-10 Istanbul chart's identity,
# career-action, relationship-trust, emotional-routine, and belief-authority
# signatures without changing the existing overlay architecture.
NATAL_PROMISE_LIBRARY_V0_4: Dict[str, Dict[str, Any]] = {
    "gemini_asc_venus_1h_social_relational_presence": {
        "id": "gemini_asc_venus_1h_social_relational_presence",
        "match": {
            "labels": [],
            "source_refs": ["asc:gemini", "planet:Venus:sign:Gemini:house:1"],
        },
        "promise_type": "behavior_reflex",
        "preferred_types": ["behavior_reflex", "gift", "love_style"],
        "domains": ["identity", "relationship", "visibility"],
        "themes": [
            "sosyal canlılık",
            "ilişki kuran ilk izlenim",
            "oyunlu çekim",
            "hafif ama uyanık duruş",
        ],
        "direct_meaning": "İnsanların seni ilk anda sosyal, canlı ve ilişki kurmaya açık hissetmesi kolay olabilir.",
        "lived_scenes": [
            "Bir ortama girdiğinde hızlıca bağ kuracak bir ton bulmak.",
            "İlgiyi ağırlıkla değil, hafiflik ve hareketle çekmek.",
            "Sohbetin içinde hem meraklı hem de oyunlu bir tarafın görünmesi.",
        ],
        "gift": "İnsanla hızlı temas kurmak, sosyal havayı canlandırmak ve ilgiyi doğal taşımak.",
        "shadow_or_friction": "Dağılmak, her şeye aynı anda açılmak, hafif görünürken derin ihtiyacı geciktirmek.",
        "growth_direction": "Sosyal parlaklığı yalnızca hızda değil, gerçek seçimlerinde de taşımak.",
        "voice_seeds": [
            "İlk izlenimde sende hızlıca temas kuran, canlı bir sosyal ton hissedilebilir.",
            "İnsanlara yaklaşırken sende merakla oyunu aynı anda taşıyan bir taraf olabilir.",
            "Duruşun hafif görünse de kimle ne kadar açılacağını hızlı sezebiliyor olabilirsin.",
        ],
    },
    "sun_aries_12h_hidden_private_fire": {
        "id": "sun_aries_12h_hidden_private_fire",
        "match": {
            "labels": [],
            "source_refs": ["planet:Sun:sign:Aries:house:12"],
        },
        "promise_type": "behavior_reflex",
        "preferred_types": ["behavior_reflex", "wound_to_gift", "gift"],
        "domains": ["identity", "behavior_reflex", "emotional_depth"],
        "themes": [
            "gizli ateş",
            "özel alanda irade",
            "geri planda hızlanan benlik",
            "içeride bağımsızlık",
        ],
        "direct_meaning": "Dışarıdan hemen görünmese de içeride hızlı, bağımsız ve kolay sönmeyen bir ateş çalışabilir.",
        "lived_scenes": [
            "Bir şeye gerçekten yönelmeden önce bunu uzun süre kendi içinde taşımak.",
            "Hızlı tepkiyi dışarıda göstermeyip içeride büyütmek.",
            "Kendi alanında yalnızken daha netleşen güçlü bir irade hissetmek.",
        ],
        "gift": "Sessiz ama güçlü irade, içeride hızla toparlanan benlik, görünmeden de yön tutabilmek.",
        "shadow_or_friction": "Öfkeyi içeri atmak, yalnız savaşmak, yardım istemeden kendi başına halletmeye çalışma.",
        "growth_direction": "İçerideki ateşi saklanmak için değil, daha bilinçli görünmek için kullanmak.",
        "voice_seeds": [
            "Sende dışarıdan hemen görünmeyen ama içeride hızla alevlenen bir taraf olabilir.",
            "Kendi alanında kaldığında iraden daha net ve daha keskin çalışıyor olabilir.",
            "İçerideki ateşini bastırmak yerine onu daha bilinçli yönlendirdiğinde kimliğin güçlenir.",
        ],
    },
    "aquarius_mc_mars_conjunct_mc_visible_freedom_drive": {
        "id": "aquarius_mc_mars_conjunct_mc_visible_freedom_drive",
        "match": {
            "labels": [],
            "source_refs": ["Mars:Midheaven:conjunction", "Uranus:Midheaven:square"],
        },
        "promise_type": "career_signature",
        "preferred_types": ["career_signature", "drive", "wound_to_gift"],
        "domains": ["career", "visibility", "identity"],
        "themes": [
            "görünür eylem",
            "kariyerde hız",
            "özgürlük ihtiyacı",
            "kendi yönünü belirleme",
            "bağımsız duruş",
        ],
        "direct_meaning": "Görünürlük hattın, hız, inisiyatif ve kendi yönünü kendin belirleme isteğiyle çalışabilir.",
        "lived_scenes": [
            "Bir işte beklemekten çok harekete geçerek yol açmak istemek.",
            "Kariyerde kendi yöntemini kurmadan tam rahatlayamamak.",
            "Sana uymayan görünürlük biçimlerine hızla itiraz etmek.",
        ],
        "gift": "Görünür işte cesur başlatıcılık, bağımsız hareket ve canlı yön duygusu.",
        "shadow_or_friction": "Sabırsız kopuş, yön değişimlerini sert yapmak, özgürlük ihtiyacını çatışmaya çevirmek.",
        "growth_direction": "Hızı sadece kaçışta değil, daha bilinçli bir yön kurmakta kullanmak.",
        "voice_seeds": [
            "Kariyerde sende beklemekten çok hareket ederek yol açan bir enerji olabilir.",
            "Görünür olduğunda kendi yönünü kendin belirleme ihtiyacın güçleniyor olabilir.",
            "Özgürlük ihtiyacını rastgele kopuşa değil, daha net bir kariyer çizgisine çevirdiğinde etki büyür.",
        ],
    },
    "venus_trine_mars_relational_attraction_signal": {
        "id": "venus_trine_mars_relational_attraction_signal",
        "match": {
            "labels": ["Venus trine Mars"],
            "source_refs": ["Venus:Mars:trine"],
        },
        "promise_type": "love_style",
        "preferred_types": ["love_style", "gift"],
        "domains": ["relationship", "love", "identity"],
        "themes": [
            "doğal çekim",
            "sıcak yaklaşım",
            "oyunlu yakınlık",
            "beden ve duygu akışı",
        ],
        "direct_meaning": "İlgini belli ettiğinde sıcaklık, çekim ve hareket aynı anda çalışabilir.",
        "lived_scenes": [
            "Birine yaklaşırken bunu sadece sözle değil tonunla ve enerjinle de hissettirmek.",
            "Yakınlıkta oyun, hareket ve canlılığın hızlı yükselmesi.",
            "Sevgiyle istek arasında doğal bir akış hissetmek.",
        ],
        "gift": "Yakınlıkta canlılık, sıcak çekim ve doğal hareket.",
        "shadow_or_friction": "Hızlı yükselip tempoyu fazla aceleye çekmek, çekimi ritim yerine dürtüyle taşımak.",
        "growth_direction": "Çekimi yalnızca hızla değil, karşılıklılık ve ritimle büyütmek.",
        "voice_seeds": [
            "Birine ilgi duyduğunda bunu yalnızca düşünmez, enerjinle de belli edebilirsin.",
            "Yakınlıkta sende oyunla çekimin aynı anda açılması kolay olabilir.",
            "Çekim sende doğal çalışıyor olabilir; ritimle birleştiğinde daha kalıcı bir bağ kurar.",
        ],
    },
    "venus_trine_saturn_trust_bond": {
        "id": "venus_trine_saturn_trust_bond",
        "match": {
            "labels": ["Venus trine Saturn"],
            "source_refs": ["Venus:Saturn:trine"],
        },
        "promise_type": "love_style",
        "preferred_types": ["love_style", "gift", "need"],
        "domains": ["relationship", "love", "emotional_depth"],
        "themes": [
            "güven veren sevgi",
            "tutarlılık",
            "zamana yayılan bağ",
            "sadakat",
            "ölçülü yakınlık",
        ],
        "direct_meaning": "Sevgi sende hafiflik kadar güven, tutarlılık ve zamanla kurulan sadakati de ister.",
        "lived_scenes": [
            "Bir bağın sadece heyecanlı değil, güvenilir de olmasına önem vermek.",
            "Yakınlıkta acele değil, ritim ve tutarlılık aramak.",
            "Sevdiğin kişiye sözle değil, sürdürülebilir duruşla güven vermek.",
        ],
        "gift": "Sevgiyi güven, sadakat ve uzun vadeli emekle taşıyabilmek.",
        "shadow_or_friction": "Fazla kontrollü açılmak, duyguyu güven gelene kadar uzun süre tutmak, yakınlığı fazla test etmek.",
        "growth_direction": "Güveni duyguyu geciktirmenin değil, daha rahat açılmanın zemini haline getirmek.",
        "voice_seeds": [
            "Yakınlıkta sende sadece heyecan değil, güvenilirlik de çok şey belirliyor olabilir.",
            "Sevgi verdiğinde bunun içinde tutarlılık ve söz taşıyan bir taraf var.",
            "Bir bağı kalıcı yapan şeyin yalnızca his değil, güven olduğunu erken sezebilirsin.",
        ],
    },
    "moon_scorpio_6h_emotional_routine_sensitivity": {
        "id": "moon_scorpio_6h_emotional_routine_sensitivity",
        "match": {
            "labels": [],
            "source_refs": ["planet:Moon:sign:Scorpio:house:6"],
        },
        "promise_type": "need",
        "preferred_types": ["need", "wound_to_gift", "love_style"],
        "domains": ["emotional_depth", "relationship", "behavior_reflex"],
        "themes": [
            "günlük duygusal hassasiyet",
            "rutin içinde yoğun his",
            "bedensel sezgi",
            "kolay derine işleme",
        ],
        "direct_meaning": "Duygun, günlük akışta bile kolay yüzeyde kalmayabilir; küçük şeyler içeride daha derine işleyebilir.",
        "lived_scenes": [
            "Günlük ritimdeki küçük bir değişimin içeride sandığından daha çok yer kaplaması.",
            "Birinin tonu veya tavrı küçük görünse de bedeninde hemen bir karşılık yaratması.",
            "Rutin bozulduğunda duygunun daha yoğun uyanması.",
        ],
        "gift": "İnce sezgi, duygusal alt akımı erken fark etme ve gündelik olanda bile derin bağ kurma.",
        "shadow_or_friction": "Küçük gerilimleri bedeninde biriktirmek, gündelik baskıyı yoğun hissetmek, duyguyu bırakmakta zorlanmak.",
        "growth_direction": "Yoğun hissi yalnızca yük gibi değil, ritmini korumaya yardım eden bir sinyal gibi okumak.",
        "voice_seeds": [
            "Gündelik şeyler sende bazen göründüğünden daha derin bir duygu uyandırabilir.",
            "Rutinindeki küçük bir değişim bile içeride büyük bir hassasiyeti açabilir.",
            "Bedenin ve duygun sana çoğu zaman küçük sinyallerle konuşuyor olabilir.",
        ],
    },
    "mercury_sextile_9h_capricorn_aquarius_intellectual_authority": {
        "id": "mercury_sextile_9h_capricorn_aquarius_intellectual_authority",
        "match": {
            "labels": [],
            "source_refs": [
                "Mercury:Jupiter:sextile",
                "Mercury:Saturn:sextile",
                "Mercury:Pluto:sextile",
            ],
        },
        "promise_type": "mind_style",
        "preferred_types": ["mind_style", "gift", "career_signature"],
        "domains": ["mind", "communication", "career", "identity"],
        "themes": [
            "entelektüel omurga",
            "inanç ve fikir kurma",
            "sağlam düşünce",
            "otoriteli anlatım",
            "büyük resmi yapılandırma",
        ],
        "direct_meaning": "Bir fikri sadece sezmek değil, onu çerçeveleyip sağlam bir görüşe dönüştürmek sende güçlü olabilir.",
        "lived_scenes": [
            "Bir düşünceyi daha büyük bir çerçeveye oturtmadan rahatlayamamak.",
            "Fikri hem açık hem de ağırlığı olan bir dille kurmak istemek.",
            "Bilgiyi kanaate, kanaati de duruşa çevirmek.",
        ],
        "gift": "Düşünceye omurga vermek, inancı zihinsel çerçeveye dönüştürmek, sözde güven yaratmak.",
        "shadow_or_friction": "Kendi fikrini fazla yüklenmek, zihni sürekli ispat modunda tutmak, düşünceyi fazla kontrol etmek.",
        "growth_direction": "Ağırlığı katılığa değil, açık ama sağlam bir zihinsel otoriteye çevirmek.",
        "voice_seeds": [
            "Bir fikri sadece bulmak değil, ona sağlam bir çerçeve vermek sende güçlü olabilir.",
            "Zihnin sezgiyle açılan şeyi kolayca görüşe ve yapıya çevirebiliyor olabilir.",
            "Sözünün ağırlığı, bildiğini daha büyük bir çerçeveye yerleştirebildiğinde artar.",
        ],
    },
}


# v0.5 addendum — Taurus / Scorpio / Pisces-12H coverage.
# Additive only. Designed to recover charts whose main promise sits in hidden
# value, invisible preparation, trust-threshold relationship, and 12H
# saturation signatures before they become visible in public life.
NATAL_PROMISE_LIBRARY_V0_5: Dict[str, Dict[str, Any]] = {
    "taurus_asc_venus_12h_hidden_value_identity": {
        "id": "taurus_asc_venus_12h_hidden_value_identity",
        "match": {
            "labels": [],
            "source_refs": ["asc:taurus", "planet:Venus:sign:Taurus:house:12"],
        },
        "promise_type": "behavior_reflex",
        "preferred_types": ["behavior_reflex", "gift", "love_style"],
        "domains": ["identity", "love", "money_self_worth", "inner_world"],
        "themes": [
            "sakin dış izlenim",
            "görünmeyen değer",
            "içte olgunlaşan sevgi",
            "yavaş güven",
            "sessiz çekim",
            "bedensel ve duyusal güven",
        ],
        "direct_meaning": "Dışarıdan sakin, yumuşak ve güven veren bir izlenim olabilir; ama değer, sevgi, çekim ve özdeğer hemen dışarı dökülmeden önce içeride olgunlaşır.",
        "lived_scenes": [
            "İnsanların sende önce sakin, güvenli veya yumuşak bir duruş görmesi.",
            "Bir şeyi sevsen bile bunu hemen açıkça göstermemek.",
            "Değer verdiğin şeyi içeride uzun süre taşıyıp dışarıya daha yavaş açmak.",
            "Güvenmediğin yerde kendini daha sessiz, kapalı veya ulaşılması zor tutmak.",
            "Güzelliği, zevki veya bağlılığı gösteriden çok içte saklamak.",
        ],
        "gift": "Sessiz çekim, sadelik, güven veren varlık, içte büyüyen değer ve derin bağlılık.",
        "shadow_or_friction": "Kendini fazla saklamak, değerini görünmez kılmak, güven gelmeden açılmamak, sevdiğini söylemeden sadece içeride taşımak.",
        "inner_tension": "Dışarıdan sakin ve ulaşılabilir görünürken, içeride kimin gerçekten yaklaşabileceğini yavaş ve dikkatli seçen bir taraf olabilir.",
        "growth_direction": "İçte taşıdığın değeri ve sevgiyi tamamen saklamadan, güvenli biçimde görünür kılmak.",
        "voice_seeds": [
            "Dışarıdan sakin ve güven veren görünebilirsin; ama içindeki değer hemen görünmeyebilir.",
            "Sevdiğin şeyi hızlıca göstermeyebilir, önce kendi içinde olgunlaştırabilirsin.",
            "Sende çekim çoğu zaman yüksek sesle değil, sessiz ve derin bir yerden çalışır.",
        ],
    },
    "venus_taurus_12h_private_love_inner_beauty": {
        "id": "venus_taurus_12h_private_love_inner_beauty",
        "match": {
            "labels": [],
            "source_refs": ["planet:Venus:sign:Taurus:house:12"],
        },
        "promise_type": "love_style",
        "preferred_types": ["love_style", "gift", "need"],
        "domains": ["relationship", "love", "identity", "spirituality"],
        "themes": [
            "gizli sevgi",
            "içte büyüyen bağlılık",
            "yavaş açılan kalp",
            "duyusal ve bedensel güven",
            "görünmeyen estetik",
            "idealize edilen bağlılık",
        ],
        "direct_meaning": "Sevgi, hızlıca gösterilen bir duygu olmaktan çok, içeride büyüyen, güven arayan ve bedensel olarak yerleşmek isteyen bir bağlılık olabilir.",
        "lived_scenes": [
            "Birine olan duyguyu hemen söylemek yerine uzun süre içinde taşımak.",
            "Sevdiğin kişiye sessizce sadık kalmak.",
            "Dokunma, sakinlik, huzur ve güven hissiyle sevgi göstermek.",
            "Ulaşılması zor veya tam açılamayan bağlara içten anlam yüklemek.",
            "Sevdiğin şeyin güzelliğini başkalarına göstermeden önce kendi içinde korumak.",
        ],
        "gift": "Derin sadakat, sakin sevgi, içsel estetik, güvenli ve duyusal bağlılık.",
        "shadow_or_friction": "Duyguyu fazla saklamak, ulaşılmaz olana bağlanmak, sevdiğini söylemekte gecikmek, kendi değerini görünmez kılmak.",
        "inner_tension": "Kalp bağlanmak isterken, bunu gösterdiğinde kırılmaktan veya kontrolü kaybetmekten çekinebilir.",
        "growth_direction": "İçeride büyüyen sevgiyi gerçek temasla, açık sözle ve güvenli görünürlükle buluşturmak.",
        "voice_seeds": [
            "Sevgi sende bazen önce içeride büyür, sonra yavaş yavaş görünür olur.",
            "Birine bağlandığında bunu hemen söylemeyebilir, önce kendi içinde taşıyabilirsin.",
            "Kalbin güven duyduğunda çok sadık ve derin çalışır.",
        ],
    },
    "venus_12h_conjunct_asc_soft_hidden_magnetism": {
        "id": "venus_12h_conjunct_asc_soft_hidden_magnetism",
        "match": {
            "labels": ["Venus conjunct Ascendant"],
            "source_refs": ["Venus:Ascendant:conjunction", "planet:Venus:house:12"],
        },
        "promise_type": "behavior_reflex",
        "preferred_types": ["behavior_reflex", "gift", "love_style"],
        "domains": ["identity", "visibility", "love", "self_worth"],
        "themes": [
            "sessiz çekim",
            "görünmeyen venüs etkisi",
            "yumuşak dış izlenim",
            "saklı güzellik",
            "içte taşınan değer",
        ],
        "direct_meaning": "Dışarıdan hissedilen bir yumuşaklığın, çekiciliğin veya estetik etkin olabilir; ama bu etki tam gösterdiğinden çok içeride taşıdığın sessiz değer duygusundan gelir.",
        "lived_scenes": [
            "İnsanların sende açıklaması zor bir yumuşaklık veya çekim hissetmesi.",
            "Çok şey göstermeden de dikkat çekmek.",
            "Sessiz kaldığında bile ortamda bir varlık bırakmak.",
            "Güzelliği veya çekimi gösterişli değil, daha sakin ve içten taşımak.",
        ],
        "gift": "Sessiz magnetizma, sakin ilişki kurma, yumuşak görünürlük ve zarif varlık.",
        "shadow_or_friction": "Kendini görünmez kılmak, değeri saklamak, sevilmeyi beklerken kendini açmamak.",
        "growth_direction": "Çekimi ve değeri saklanacak bir şey değil, güvenli biçimde taşınacak bir varlık hali olarak görmek.",
        "voice_seeds": [
            "Çok şey göstermeden de insanlarda iz bırakan bir tarafın olabilir.",
            "Sende çekim gösterişten çok sessiz bir varlık gibi çalışır.",
            "Dışarıdan sakin görünen duruşunun altında güçlü bir değer duygusu var.",
        ],
    },
    "mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation": {
        "id": "mc_capricorn_ruler_saturn_pisces_12h_invisible_preparation",
        "match": {
            "labels": [],
            "source_refs": ["mc:capricorn", "planet:Saturn:sign:Pisces:house:12"],
        },
        "promise_type": "career_signature",
        "preferred_types": ["career_signature", "wound_to_gift", "gift"],
        "domains": ["career", "visibility", "inner_world", "responsibility"],
        "themes": [
            "görünmeden önce hazırlık",
            "perde arkası emek",
            "sessiz sorumluluk",
            "olgunlaşmadan görünmeme",
            "içsel disiplin",
            "görünmeyen yük",
        ],
        "direct_meaning": "Dış dünyada sağlam, güvenilir ve olgun bir iz bırakmak isteyebilirsin; ama bu görünürlüğün arkasında uzun bir iç hazırlık, sessiz sorumluluk ve perde arkası emek bulunabilir.",
        "lived_scenes": [
            "Bir şeyi dışarı göstermeden önce uzun süre kendi içinde hazırlamak.",
            "Görünür olmadan önce yeterince olgun, yeterince doğru veya yeterince sağlam olduğundan emin olmak.",
            "Başkalarının görmediği bir yükü sessizce taşımak.",
            "Dışarıda güçlü görünmeden önce içeride prova yapmak.",
            "Başarıyı hızlı çıkıştan çok uzun süreli dayanıklılıkla kurmak.",
        ],
        "gift": "Sabır, iç disiplin, perde arkası ustalık, sessiz olgunluk ve güvenilir kamu duruşu.",
        "shadow_or_friction": "Fazla beklemek, kendini görünür kılmakta gecikmek, görünmeyen sorumlulukları tek başına taşımak, kusursuz hazırlık ihtiyacı.",
        "inner_tension": "Dışarıda sağlam görünmek isteyen tarafla, içeride hâlâ hazır olmadığını düşünen taraf aynı anda çalışabilir.",
        "growth_direction": "Görünür olmayı mükemmel hazır olduğunda değil, içsel emeğin yeterince olgunlaştığında seçmek.",
        "voice_seeds": [
            "Dışarıda sağlam görünmeden önce içeride uzun bir hazırlık yapman gerekebilir.",
            "Kariyerinde hızlı çıkıştan çok, görünmeyen emek ve sessiz olgunlaşma çalışıyor olabilir.",
            "Perde açılmadan önce içeride uzun bir prova yaparsın.",
        ],
    },
    "saturn_pisces_12h_private_maturity_boundary_sensitivity": {
        "id": "saturn_pisces_12h_private_maturity_boundary_sensitivity",
        "match": {
            "labels": [],
            "source_refs": ["planet:Saturn:sign:Pisces:house:12"],
        },
        "promise_type": "wound_to_gift",
        "preferred_types": ["wound_to_gift", "need", "gift"],
        "domains": ["inner_world", "identity", "career", "spirituality"],
        "themes": [
            "sessiz yük",
            "sınır hassasiyeti",
            "içsel sorumluluk",
            "görünmeyen korku",
            "ruhsal olgunlaşma",
            "yalnız taşınan disiplin",
        ],
        "direct_meaning": "Sorumluluk, sınır, korku ve olgunlaşma temalarını çoğu zaman dışarıdan görünmeyen, içsel ve hassas bir alanda yaşayabilirsin.",
        "lived_scenes": [
            "Bir yükü kimse anlamadan içeride taşımak.",
            "Başkalarının duygusunu, ihtiyacını veya belirsizliğini üstlenmek.",
            "Sınır koymakta zorlanıp sonra kendi içinde katılaşmak.",
            "Görünmeyen bir alanda sürekli olgun olmak zorundaymış gibi hissetmek.",
            "Yalnız kaldığında sorumlulukların daha ağır duyulması.",
        ],
        "gift": "Derin olgunluk, hassasiyete sınır verme, içsel dayanıklılık ve ruhsal sorumluluk bilinci.",
        "shadow_or_friction": "Kendini izole etmek, sınırları bulanıklaştırmak, görünmeyen yükleri tek başına taşımak, suçluluk veya yetersizlik hissi.",
        "inner_tension": "Şefkat ve açıklık isterken, dağılmamak için sınır ve yapı arayan bir taraf aynı anda çalışır.",
        "growth_direction": "Hassasiyeti yüklenmek yerine, ona sınır ve yapı vererek içsel olgunluğa çevirmek.",
        "voice_seeds": [
            "Bazı sorumlulukları dışarıdan görünmeden içeride taşıyor olabilirsin.",
            "Sınır koymak sende hassas bir yerden geçebilir.",
            "İçsel yüklerini tek başına taşımak zorunda olmadığını öğrendikçe daha sağlam bir olgunluk kurarsın.",
        ],
    },
    "dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire": {
        "id": "dsc_scorpio_ruler_mars_pisces_12h_trust_threshold_silent_desire",
        "match": {
            "labels": [],
            "source_refs": ["dsc:scorpio", "planet:Mars:sign:Pisces:house:12"],
        },
        "promise_type": "need",
        "preferred_types": ["need", "love_style", "gift"],
        "domains": ["relationship", "love", "emotional_depth", "inner_world"],
        "themes": [
            "güven eşiği",
            "sessiz arzu",
            "sezgisel yakınlık",
            "derin ve gizli bağ",
            "koruyucu çekilme",
            "yoğunluğu hemen göstermeme",
        ],
        "direct_meaning": "İlişkide yüzeysel sıcaklık yetmeyebilir; derinlik, güven ve duygusal dürüstlük arayabilirsin, ama arzu ve kırılganlık her zaman doğrudan gösterilmeyebilir.",
        "lived_scenes": [
            "Birine yaklaşmak isteyip aynı anda kendini korumaya almak.",
            "Bir bağın gerçekten güvenli olup olmadığını sezgisel olarak tartmak.",
            "Duyguyu açıkça söylemeden önce içeride büyütmek.",
            "Yoğun çekimi sessizce taşımak.",
            "Güven yoksa geri çekilmek veya kendini belirsizleştirmek.",
        ],
        "gift": "Derin sezgi, güçlü bağ kurma, ilişkide görünmeyeni hissetme ve sadık yakınlık.",
        "shadow_or_friction": "Açılmamak, pasif beklemek, duyguyu saklamak, güvensizlikte geri çekilmek, ne istediğini dolaylı göstermek.",
        "inner_tension": "Kalp derin bağ isterken, aynı anda kendini tamamen açmaktan çekinebilir.",
        "growth_direction": "Derinliği sadece sessizce taşımak yerine, güvenli olduğunda daha açık ve dürüst temas kurmak.",
        "voice_seeds": [
            "İlişkide yüzeysel sıcaklık sana yetmeyebilir; güven ve derinlik ararsın.",
            "Birine yaklaşmak istediğinde bile, önce içeride güvenli olup olmadığını tartabilirsin.",
            "En yoğun arzuların bile bazen önce sessizleşir, içeride büyür.",
        ],
    },
    "pluto_7h_relationship_power_depth": {
        "id": "pluto_7h_relationship_power_depth",
        "match": {
            "labels": [],
            "source_refs": ["planet:Pluto:house:7"],
        },
        "promise_type": "wound_to_gift",
        "preferred_types": ["wound_to_gift", "gift", "need"],
        "domains": ["relationship", "emotional_depth", "shadow_or_friction"],
        "themes": [
            "ilişkide güç dinamiği",
            "yoğun karşılaşmalar",
            "dönüşen bağlar",
            "kontrol ve teslimiyet",
            "kolay geçmeyen ilişki izi",
        ],
        "direct_meaning": "İlişkiler sende yüzeysel kalmayabilir; karşılaşmalar güç, teslimiyet, kontrol, derin çekim ve dönüşüm temalarını açabilir.",
        "lived_scenes": [
            "Bir ilişkiyi kapatmış gibi görünsen bile içeride hâlâ taşımak.",
            "Karşı tarafın niyetini, gücünü veya etkisini çok derinden hissetmek.",
            "Yakınlıkta kimin neyi kontrol ettiği sorusunu sezmek.",
            "Bazı ilişkilerin seni tamamen değiştirmesi.",
        ],
        "gift": "İlişki dinamiklerini derinden okumak ve bağların dönüştürücü gücünü görmek.",
        "shadow_or_friction": "Kontrol savaşı, takılı kalma, kıskançlık, güven kırıldığında eskiye dönememek.",
        "inner_tension": "Derinleşmek isteyen tarafla kontrolü kaybetmekten çekinen taraf aynı anda çalışabilir.",
        "growth_direction": "İlişkideki yoğunluğu güç savaşına değil, daha dürüst ve dönüştürücü yakınlığa çevirmek.",
        "voice_seeds": [
            "İlişkiler sende kolay kolay yüzeyde kalmayabilir.",
            "Bazı karşılaşmalar seni sadece etkilemez; dönüştürür.",
            "Yakınlıkta güç ve teslimiyet temalarını hızlı hissedebilirsin.",
        ],
    },
    "mars_pisces_12h_hidden_action_soft_drive": {
        "id": "mars_pisces_12h_hidden_action_soft_drive",
        "match": {
            "labels": [],
            "source_refs": ["planet:Mars:sign:Pisces:house:12"],
        },
        "promise_type": "drive",
        "preferred_types": ["drive", "need", "gift"],
        "domains": ["inner_world", "action", "relationship", "career"],
        "themes": [
            "dolaylı hareket",
            "sessiz arzu",
            "içte biriken eylem",
            "yumuşak mücadele",
            "sezgisel aksiyon",
            "görünmeden çaba",
        ],
        "direct_meaning": "Hareket ve arzu doğrudan, sert veya hemen görünür çalışmak yerine; içeride biriken, sezgisel, yumuşak ve bazen dolaylı bir yoldan akabilir.",
        "lived_scenes": [
            "Bir şeyi istemek ama hemen açıkça harekete geçmemek.",
            "Önce sezmek, sonra davranmak.",
            "Mücadeleyi açık çatışma yerine sessiz çaba ile yürütmek.",
            "Arzuyu veya öfkeyi içeride biriktirmek.",
            "Birine yaklaşmak istediğinde bunu dolaylı göstermek.",
        ],
        "gift": "Sezgisel hareket, yumuşak güç, görünmeden emek ve başkasının ihtiyacını hissederek aksiyon alma.",
        "shadow_or_friction": "Pasif kalmak, öfkeyi saklamak, arzuyu belirsizleştirmek, dolaylı davranmak, kendi isteğini kaybetmek.",
        "inner_tension": "Bir yanın harekete geçmek isterken, başka bir yanın çatışmadan kaçmak veya görünmemek isteyebilir.",
        "growth_direction": "Sezgisel hareketi belirsizliğe bırakmadan, ne istediğini daha net ve yumuşak şekilde göstermek.",
        "voice_seeds": [
            "Harekete geçmeden önce içeride uzun süre sezebilir ve tartabilirsin.",
            "Mücadelen çoğu zaman yüksek sesle değil, sessiz bir çabayla başlar.",
            "Ne istediğini dolaylı değil, daha net ama yumuşak bir yerden göstermeyi öğreniyorsun.",
        ],
    },
    "sun_mars_pisces_12h_private_will_and_hidden_drive": {
        "id": "sun_mars_pisces_12h_private_will_and_hidden_drive",
        "match": {
            "labels": ["Sun conjunct Mars"],
            "source_refs": ["Sun:Mars:conjunction", "planet:Sun:sign:Pisces:house:12", "planet:Mars:sign:Pisces:house:12"],
        },
        "promise_type": "behavior_reflex",
        "preferred_types": ["behavior_reflex", "drive", "gift"],
        "domains": ["inner_world", "identity", "action"],
        "themes": [
            "içte yanan hareket",
            "özel irade",
            "sessiz mücadele",
            "görünmeyen cesaret",
            "bastırılmış öfke veya arzu",
            "içsel yön",
        ],
        "direct_meaning": "Kimlik ve hareket enerjin birbirine bağlı olabilir; ama bu enerji çoğu zaman dışarıdan görünmeden önce içeride, yalnızlıkta veya sezgisel bir alanda çalışır.",
        "lived_scenes": [
            "İçinde çok güçlü bir istek varken dışarıdan sakin görünmek.",
            "Bir şeyi başlatmadan önce kendi içinde uzun süre mücadele etmek.",
            "Öfkeyi veya arzuyu hemen göstermemek.",
            "Yalnız kaldığında ne istediğini daha net hissetmek.",
            "Başkaları fark etmeden çoktan içsel bir karar almış olmak.",
        ],
        "gift": "Sessiz cesaret, içten gelen yön duygusu, sezgisel aksiyon ve görünmeyen mücadele gücü.",
        "shadow_or_friction": "Kendi isteğini saklamak, öfkeyi içeride büyütmek, eylemi ertelemek, kendini yalnız mücadeleye mahkûm etmek.",
        "inner_tension": "İçte hareket çok güçlü olabilir, ama görünür olana kadar uzun süre sessiz kalabilir.",
        "growth_direction": "İçte yanan isteği belirsizliğe veya yalnızlığa hapsetmeden, doğru zamanda açık ve yumuşak bir harekete çevirmek.",
        "voice_seeds": [
            "İçinde çok güçlü bir istek çalışabilir; ama bunu her zaman hemen göstermeyebilirsin.",
            "Mücadelen bazen dışarıda değil, kimsenin görmediği bir iç alanda başlar.",
            "Ne istediğini içeride netleştirdiğinde, dışarıdaki adımın daha sakin ama güçlü olur.",
        ],
    },
    "pisces_12h_stellium_inner_world_saturation": {
        "id": "pisces_12h_stellium_inner_world_saturation",
        "match": {
            "labels": [],
            "source_refs": ["house:12:stellium", "planet:Sun:house:12", "planet:Mars:house:12", "planet:Saturn:house:12", "planet:Venus:house:12"],
        },
        "promise_type": "need",
        "preferred_types": ["need", "gift", "wound_to_gift"],
        "domains": ["inner_world", "identity", "spirituality", "emotional_depth"],
        "themes": [
            "yoğun iç dünya",
            "görünmeyen süreçler",
            "sezgisel doygunluk",
            "yalnızlıkta işleme",
            "perde arkası benlik",
            "duygusal geçirgenlik",
        ],
        "direct_meaning": "Haritada birçok temel gösterge 12. eve bağlandığında, yaşamın önemli kararları, arzuları, sorumlulukları ve ilişkisel temaları önce görünmeyen iç alanda işlenebilir.",
        "lived_scenes": [
            "Bir şeyi dışarıya göstermeden önce içeride uzun süre yaşamak.",
            "Karar, arzu, sorumluluk veya sevginin önce sessiz bir odada şekillenmesi gibi hissetmek.",
            "Dışarıdan sakin görünürken içeride çok yoğun bir çözülme veya toparlanma yaşamak.",
            "Yalnızlıkta dolmak, boşalmak, anlamak ve yeniden yön bulmak.",
            "Başkalarının fark etmediği duygusal veya ruhsal yükleri hissetmek.",
        ],
        "gift": "Derin sezgi, içsel işleme gücü, görünmeyeni anlama ve sessiz dönüşüm.",
        "shadow_or_friction": "İzolasyon, belirsizlik, kendi isteğini saklamak, başkasının duygusunu taşımak, görünmeden yorulmak.",
        "inner_tension": "Dışarıda hayat devam ederken, içeride çok daha yoğun bir alan çalışıyor olabilir.",
        "growth_direction": "İç dünyayı kaçış veya saklanma alanı değil, bilinçli hazırlık ve sezgisel güç alanı haline getirmek.",
        "voice_seeds": [
            "Birçok şey sende dışarıda olmadan önce içeride olur.",
            "Dışarıdan sakin görünürken içeride çok yoğun bir dünya çalışıyor olabilir.",
            "Görünmeyen alanda işlediğin şeyler, zamanla dışarıdaki yönünü belirler.",
        ],
    },
    "mercury_pisces_11h_social_intuition_mind": {
        "id": "mercury_pisces_11h_social_intuition_mind",
        "match": {
            "labels": [],
            "source_refs": ["planet:Mercury:sign:Pisces:house:11"],
        },
        "promise_type": "mind_style",
        "preferred_types": ["mind_style", "gift", "need"],
        "domains": ["mind", "community", "communication", "spirituality"],
        "themes": [
            "sezgisel sosyal zihin",
            "toplulukların duygusunu okuma",
            "belirsiz sinyalleri yakalama",
            "arkadaşlıkta empati",
            "kolektif hayal",
        ],
        "direct_meaning": "Zihnin sosyal çevreler, arkadaşlıklar ve ortak idealler içinde sezgisel, geçirgen ve atmosfer okuyabilen bir şekilde çalışabilir.",
        "lived_scenes": [
            "Bir grubun içinde herkesin söylemediği şeyi hissetmek.",
            "Arkadaş çevresindeki duygusal tonu hızlıca almak.",
            "Sözden çok atmosferden anlam çıkarmak.",
            "Ortak hayallere, idealist fikirlere veya sezgisel bağlara çekilmek.",
            "İnsanların niyetini veya ruh halini konuşmadan anlamaya çalışmak.",
        ],
        "gift": "Sosyal sezgi, empatik zihin, kolektif atmosfer okuma ve yaratıcı iletişim.",
        "shadow_or_friction": "Sınırların bulanıklaşması, herkesin duygusunu taşımak, belirsiz sözlerden fazla anlam çıkarmak.",
        "inner_tension": "Bir gruba ait olmak isterken, o grubun duygusal yükünü de üstlenebilirsin.",
        "growth_direction": "Sosyal sezgiyi net söz, sınır ve ayıklama becerisiyle dengelemek.",
        "voice_seeds": [
            "Bir grubun içinde söylenmeyen şeyi bile hızlıca hissedebilirsin.",
            "Zihnin sadece kelimeleri değil, ortamın duygusunu da okur.",
            "Sosyal sezgin, sınırla birleştiğinde çok güçlü bir iletişim becerisine dönüşür.",
        ],
    },
    "uranus_square_asc_venus_unsettled_outer_signal": {
        "id": "uranus_square_asc_venus_unsettled_outer_signal",
        "match": {
            "labels": ["Uranus square Ascendant", "Venus square Uranus"],
            "source_refs": ["Uranus:Ascendant:square", "Venus:Uranus:square"],
        },
        "promise_type": "wound_to_gift",
        "preferred_types": ["wound_to_gift", "gift", "behavior_reflex"],
        "domains": ["identity", "relationship", "visibility"],
        "themes": [
            "sakin dış tonun altında elektrik",
            "ani uzaklaşma",
            "özgürlük ihtiyacı",
            "alışılmadık çekim",
            "ilişki ve görünürlükte düzensiz ritim",
        ],
        "direct_meaning": "Dışarıdan sakin veya yumuşak görünen varlığın, içeride özgürlük, farklılık ve ani yön değiştirme ihtiyacıyla gerilim yaşayabilir.",
        "lived_scenes": [
            "İnsanlar seni sakin görürken, içeride bir anda uzaklaşmak istemek.",
            "Çok yakınlaşan veya sabitleyen ilişkilerde elektriklenmek.",
            "Kendi ritmini kaybettiğinde beklenmedik tepkiler vermek.",
            "Sakin dış görüntünün altında daha özgür, farklı veya alışılmadık bir çizgi taşımak.",
        ],
        "gift": "Özgün çekim, kalıba sığmayan varlık, ilişkide canlılık ve farklılık.",
        "shadow_or_friction": "Ani kopuş, huzursuzluk, sabit kalmakta zorlanma, yakınlıkta özgürlük krizleri.",
        "inner_tension": "Güven ve sakinlik isterken, bir yanın da tamamen özgür ve kalıpsız kalmak isteyebilir.",
        "growth_direction": "Özgürlüğü kopuşla değil, ilişki ve kimlik içinde alan açarak yaşamak.",
        "voice_seeds": [
            "Dışarıdan sakin görünsen de içeride daha elektrikli bir taraf çalışabilir.",
            "Yakınlık fazla sabitlendiğinde bir anda alan ihtiyacın yükselebilir.",
            "Özgürlüğünü kopuşla değil, kendi ritmini açıkça kurarak yaşadığında daha rahat edersin.",
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
    # v0.4 addendum — additive overlay, never replaces v0.1/v0.2/v0.3 archetypes.
    for key, entry in NATAL_PROMISE_LIBRARY_V0_4.items():
        if key not in entries:
            entries[key] = deepcopy(dict(entry))
    # v0.5 addendum — additive overlay, never replaces earlier archetypes.
    for key, entry in NATAL_PROMISE_LIBRARY_V0_5.items():
        if key not in entries:
            entries[key] = deepcopy(dict(entry))
    return {
        "version": REGISTRY_VERSION,
        "authority": "v0.1_plus_manual_delta_v0_2_plus_v0_3_plus_v0_4_plus_v0_5",
        "entries": entries,
    }
