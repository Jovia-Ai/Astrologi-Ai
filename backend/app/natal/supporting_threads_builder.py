from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Mapping, Sequence

from app.narrative.editorial_render_policy import editorialize_micro, select_rhythm_family
from app.natal.natal_graph import TRADITIONAL_RULERS

SIGN_VIBE_TR = {
    "Aries": "direkt ve atak",
    "Taurus": "sakin ve sağlam",
    "Gemini": "meraklı ve hareketli",
    "Cancer": "koruyucu ve duyarlı",
    "Leo": "sıcak ve görünür",
    "Virgo": "ölçülü ve düzenli",
    "Libra": "uyumlu ve dengeli",
    "Scorpio": "derin ve kontrollü",
    "Sagittarius": "açık ve vizyoner",
    "Capricorn": "ciddi ve hedef odaklı",
    "Aquarius": "bağımsız ve özgün",
    "Pisces": "sezgisel ve yumuşak",
}

SIGN_TONE_TR = {
    "Aries": "hızlı, ateşli ve direkt; gölgesinde dürtüsel",
    "Taurus": "sabit, dayanıklı ve inatçı",
    "Gemini": "hareketli, meraklı ve dağınık",
    "Cancer": "duygusal, korumacı ve çekingen",
    "Leo": "görünür, sıcak ve gururlu",
    "Virgo": "ölçülü, seçici ve eleştirel",
    "Libra": "uyum arayan, tartan ve kararsız",
    "Scorpio": "yoğun, kontrollü ve kuşkulu",
    "Sagittarius": "açık, cesur ve risk alan",
    "Capricorn": "kontrollü, ciddi ve dayanıklı",
    "Aquarius": "bağımsız, mesafeli ve sıra dışı",
    "Pisces": "sezgisel, geçirgen ve dalgalı",
}

SIGN_LABEL_TR = {
    "Aries": "Koç",
    "Taurus": "Boğa",
    "Gemini": "İkizler",
    "Cancer": "Yengeç",
    "Leo": "Aslan",
    "Virgo": "Başak",
    "Libra": "Terazi",
    "Scorpio": "Akrep",
    "Sagittarius": "Yay",
    "Capricorn": "Oğlak",
    "Aquarius": "Kova",
    "Pisces": "Balık",
}

SIGN_LOCATIVE_TR = {
    "Aries": "Koç'ta",
    "Taurus": "Boğa'da",
    "Gemini": "İkizler'de",
    "Cancer": "Yengeç'te",
    "Leo": "Aslan'da",
    "Virgo": "Başak'ta",
    "Libra": "Terazi'de",
    "Scorpio": "Akrep'te",
    "Sagittarius": "Yay'da",
    "Capricorn": "Oğlak'ta",
    "Aquarius": "Kova'da",
    "Pisces": "Balık'ta",
}

PLANET_LABEL_TR = {
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
}

HOUSE_ARENA_TR = {
    1: "benlik ve duruş",
    2: "özdeğer ve kaynaklar",
    3: "söz, ton ve karar dili",
    4: "ev ve iç güven",
    5: "yaratıcılık ve ifade",
    6: "günlük ritim ve düzen",
    7: "yakın ilişkiler",
    8: "güven, mahremiyet ve derinlik",
    9: "anlam, inanç ve ufuk",
    10: "kariyer ve görünürlük",
    11: "network, ekip ve sosyal bağlam",
    12: "perde arkası ve iç dünya",
}

_MIND_MICROS = [
    "Bir cümleyi göndermeden önce içinden bir kez daha tartarsın.",
    "Bir konuşmanın ardından tonu daha da sadeleştirmek istersin.",
    "Yanlış anlaşılma ihtimali doğduğunda kelimeleri içeride hemen yeniden dizersin.",
]

_REL_MICROS = [
    "Yakınlık ciddileştiğinde önce içini yoklar, sonra açılırsın.",
    "Güven geldiğinde sıcaklığın bir anda daha görünür olur.",
    "Belirsizlik uzadığında kalbin çabuk yorulur.",
]

_CAREER_MICROS = [
    "Bir şeyi tam sahiplenmeden ortaya koymak istemezsin.",
    "Görünür olmadan önce içerden bir kez daha ölçüp tartarsın.",
    "İçinde olgunlaşan şeyi doğru anda dışarı çıkarırsın.",
]

_RELATIONSHIP_SIGN_OPENING_TR = {
    "Aries": {
        "need": "yanında fazla dolanmadan açık olabildiğin bir bağ",
        "line": "7. evin Koç olduğu için ilişkide netlik, cesaret ve doğrudanlık senin için çok şey belirliyor.",
        "gate": "Duygu varsa bunun hareketi de olsun istiyorsun; sürekli beklemek ya da ölçmek seni çabuk yorabiliyor.",
    },
    "Taurus": {
        "need": "yanında gerçekten gevşeyebildiğin, yavaşlayabildiğin bir bağ",
        "line": "7. evin Boğa olduğu için ilişkide istikrar, güven ve bedensel rahatlık senin için çok belirleyici.",
        "gate": "Zemin oynamıyorsa açılıyorsun; zemin kayıyorsa hemen mesafe koyabiliyorsun.",
    },
    "Gemini": {
        "need": "yanında hem rahat konuşabildiğin hem de zihninin canlı kaldığı bir bağ",
        "line": "7. evin İkizler olduğu için ilişkide söz, merak ve zihinsel akış senin için duygunun kendisi kadar önemli.",
        "gate": "Cümle tıkanıyorsa ya da iletişim ağırlaşıyorsa bağın ritmi sende hemen düşebiliyor.",
    },
    "Cancer": {
        "need": "yanında gerçekten yumuşayabildiğin bir bağ",
        "line": "7. evin Yengeç olduğu için sen aşkı biraz ev gibi yaşıyorsun.",
        "gate": "Güven yoksa, duygusal sıcaklık yoksa ve ait hissetmiyorsan kolay kolay tam açılmıyorsun.",
    },
    "Leo": {
        "need": "yanında hem sevildiğini hem de içtenlikle seçildiğini hissedebildiğin bir bağ",
        "line": "7. evin Aslan olduğu için ilişkide sıcaklık, görünür sevgi ve açık ilgi senin için çok şey anlatıyor.",
        "gate": "Kalpten gelen bir ışık yoksa bağ sende kolay kolay tam canlanmıyor.",
    },
    "Virgo": {
        "need": "yanında hem huzur bulduğun hem de hayatın daha düzenli aktığı bir bağ",
        "line": "7. evin Başak olduğu için ilişkide özen, tutarlılık ve küçük şeylere dikkat edilmesi senin için önemli.",
        "gate": "Dağınıklık, belirsizlik ya da sürekli açıkta kalan detaylar sende bağı yorabiliyor.",
    },
    "Libra": {
        "need": "yanında hem yakınlık hem de karşılıklılık hissedebildiğin bir bağ",
        "line": "7. evin Terazi olduğu için ilişkide denge, zarafet ve karşılıklı istek senin için çok belirleyici.",
        "gate": "Tek taraflılık ya da kaba bir ton varsa içten içe hızla geri çekilebiliyorsun.",
    },
    "Scorpio": {
        "need": "yanında hem güvende hem de gerçekten derinde hissedebildiğin bir bağ",
        "line": "7. evin Akrep olduğu için ilişkide yoğunluk, dürüstlük ve duygusal çıplaklık senin için önemli.",
        "gate": "Yüzeyde kalan bağlar sende kolay kolay yer etmiyor.",
    },
    "Sagittarius": {
        "need": "yanında hem yakınlık hem de içinin genişlediğini hissedebildiğin bir bağ",
        "line": "7. evin Yay olduğu için ilişkide açıklık, dürüstlük ve ortak ufuk duygusu seni çok etkiliyor.",
        "gate": "Daraltan, boğan ya da sürekli hesap yapan ilişkiler sende çabuk yorulma yaratabiliyor.",
    },
    "Capricorn": {
        "need": "yanında hem güven hem de omurga hissedebildiğin bir bağ",
        "line": "7. evin Oğlak olduğu için ilişkide ciddiyet, güvenilirlik ve uzun vadeli duruş senin için önemli.",
        "gate": "Duygu varsa bunun ağırlığı da olsun istiyorsun; hafiflik bazen sende güvensizlik yaratabiliyor.",
    },
    "Aquarius": {
        "need": "yanında hem yakınlık hem de kendin kalabildiğin bir bağ",
        "line": "7. evin Kova olduğu için ilişkide özgürlük, zihinsel alan ve farklılık payı seni çok etkiliyor.",
        "gate": "Üzerine fazla gelinen ya da kalıba sokan bağlar sende hızla mesafe yaratabiliyor.",
    },
    "Pisces": {
        "need": "yanında hem duygusal akış hem de ruhsal bir yakınlık hissedebildiğin bir bağ",
        "line": "7. evin Balık olduğu için ilişkide sezgi, merhamet ve görünmeyen bağlar senin için önemli.",
        "gate": "Ruhsuz, kuru ya da fazla sert hissettiren ilişkiler sende kolay kolay derinleşmiyor.",
    },
}

_RELATIONSHIP_RULER_SIGN_NEED_TR = {
    "Aries": "Kalbinde yer açtığında sevginin biraz daha cesur, direkt ve beklemeye tahammülsüz akmasını istiyorsun.",
    "Taurus": "Kalbinde yer açtığında sevginin daha somut, sakin ve güven veren bir şekilde görünmesini istiyorsun.",
    "Gemini": "Kalbinde yer açtığında sevginin konuşulabilir, canlı ve hareketli kalmasını istiyorsun.",
    "Cancer": "Kalbinde yer açtığında sevginin koruyucu, yumuşak ve duygusal olarak güven veren bir hale gelmesini istiyorsun.",
    "Leo": "Sen sadece sevilmek istemiyorsun; özel hissetmek, seçildiğini görmek ve sevginin görünür olmasını da istiyorsun.",
    "Virgo": "Kalbinde yer açtığında sevginin özenli, dikkatli ve küçük jestlerle hissedilir olmasını istiyorsun.",
    "Libra": "Kalbinde yer açtığında sevginin dengeli, zarif ve karşılıklı akmasını istiyorsun.",
    "Scorpio": "Kalbinde yer açtığında sevginin yüzeyde kalmasını değil, gerçek ve dönüştürücü olmasını istiyorsun.",
    "Sagittarius": "Kalbinde yer açtığında sevginin açık, dürüst ve ferah hissettiren bir tonda akmasını istiyorsun.",
    "Capricorn": "Kalbinde yer açtığında sevginin ciddi, güvenilir ve omurgalı bir şekilde görünmesini istiyorsun.",
    "Aquarius": "Kalbinde yer açtığında sevginin alan bırakan, özgür ama yine de gerçek kalan bir tonda akmasını istiyorsun.",
    "Pisces": "Kalbinde yer açtığında sevginin sezgisel, içten ve yumuşatan bir şekilde hissedilmesini istiyorsun.",
}

_RELATIONSHIP_SIGN_BALANCE_TR = {
    "Aries": {
        "gift": "ilişkide canlılık, cesaret ve bekletmeyen bir dürüstlük",
        "shadow": "sabrın düştüğünde acele karar ya da ani tepki",
    },
    "Taurus": {
        "gift": "ilişkide güven, sadakat ve sakinleştirici bir istikrar",
        "shadow": "zemin sarsıldığında inatla kapanmak ya da değişime direnmek",
    },
    "Gemini": {
        "gift": "ilişkide canlı iletişim, merak ve zihinsel yakınlık",
        "shadow": "ritim düştüğünde dağılmak ya da duygudan çok zihinde kalmak",
    },
    "Cancer": {
        "gift": "ilişkide şefkat, aidiyet ve gerçek duygusal sıcaklık",
        "shadow": "güvensizlikte fazla alınmak ya da kabuğa çekilmek",
    },
    "Leo": {
        "gift": "ilişkide sıcaklık, görünür sevgi ve kalpten gelen cömertlik",
        "shadow": "özel hissetmediğinde kırılgan gurur ya da dramatik geri çekilme",
    },
    "Virgo": {
        "gift": "ilişkide özen, dikkat ve gerçekten emek veren bir sevgi",
        "shadow": "fazla kusur görme ya da rahat akışı gereğinden çok kontrol etme",
    },
    "Libra": {
        "gift": "ilişkide denge, zarafet ve karşılıklılığı büyüten bir ton",
        "shadow": "uyumu korumak için kendini erteleme ya da kararsız kalma",
    },
    "Scorpio": {
        "gift": "ilişkide derinlik, sadakat ve yüzeyde kalmayan bir bağ gücü",
        "shadow": "güven sarsıldığında kuşku, kontrol ya da fazla sert kapanma",
    },
    "Sagittarius": {
        "gift": "ilişkide ferahlık, dürüstlük ve birlikte büyüme hissi",
        "shadow": "daraldığında uzaklaşmak ya da yakınlığa rağmen alan için fazla sertleşmek",
    },
    "Capricorn": {
        "gift": "ilişkide omurga, ciddiyet ve uzun vadeli güven",
        "shadow": "duyguyu fazla tutmak ya da kırılganlığı göstermekte zorlanmak",
    },
    "Aquarius": {
        "gift": "ilişkide özgürlük, dürüstlük ve iki kişinin de kendisi kalabilmesi",
        "shadow": "fazla mesafe koymak ya da duyguyu zihinselleştirip geri çekmek",
    },
    "Pisces": {
        "gift": "ilişkide sezgi, merhamet ve ruhsal yakınlık",
        "shadow": "sınırların bulanıklaşması ya da hayal kırıklığında dağılmak",
    },
}

_RELATIONSHIP_RULER_SIGN_BALANCE_TR = {
    "Aries": {
        "gift": "sevgiyi direkt, cesur ve bekletmeden gösterebilme",
        "shadow": "acele tepki vermek ya da sabır düşünce hemen sertleşmek",
    },
    "Taurus": {
        "gift": "sevgiyi sakin, somut ve güven veren biçimde büyütebilme",
        "shadow": "alıştığı ritim bozulunca inatla kapanmak",
    },
    "Gemini": {
        "gift": "sevgiyi konuşarak, paylaşarak ve canlı tutabilme",
        "shadow": "duyguyu fazla düşünceye çekip dağılmak",
    },
    "Cancer": {
        "gift": "sevgiyi koruyucu, içten ve duygusal olarak besleyici yaşayabilme",
        "shadow": "incindiğinde hemen kabuğa çekilmek ya da fazla hassaslaşmak",
    },
    "Leo": {
        "gift": "sevgiyi sıcak, görünür ve cömert biçimde hissettirebilme",
        "shadow": "görülmediğinde kırılmak ya da gurur üzerinden geri çekilmek",
    },
    "Virgo": {
        "gift": "sevgiyi özen, emek ve küçük ayrıntılarla somutlaştırabilme",
        "shadow": "yetersizlik hissiyle fazla eleştirel ya da kontrollü olmak",
    },
    "Libra": {
        "gift": "sevgiyi zarif, dengeli ve karşılıklı bir tonda yaşatabilme",
        "shadow": "denge bozulmasın diye gerçek ihtiyacı geciktirmek",
    },
    "Scorpio": {
        "gift": "sevgiyi derin, sadık ve dönüştürücü bir yerden kurabilme",
        "shadow": "güvensizlikte kontrol, kuşku ya da hep ya hiç tepkisi vermek",
    },
    "Sagittarius": {
        "gift": "sevgiyi açık, dürüst ve ferah hissettiren bir tonda akıtabilme",
        "shadow": "yakınlık ağırlaştığında bir anda mesafe istemek",
    },
    "Capricorn": {
        "gift": "sevgiyi ciddi, güvenilir ve omurgalı bir şekilde taşıyabilme",
        "shadow": "duyguyu fazla tutmak ya da yumuşak tarafı göstermekte zorlanmak",
    },
    "Aquarius": {
        "gift": "sevgiyi özgürlük bırakarak ama yine de gerçek kalarak yaşayabilme",
        "shadow": "yakınlık arttığında aşırı mesafe koymak",
    },
    "Pisces": {
        "gift": "sevgiyi sezgisel, içten ve gerçekten yumuşatan bir akışa çevirebilme",
        "shadow": "fazla idealize etmek ya da sınırı kaybetmek",
    },
}

_CAREER_MC_BALANCE_TR = {
    "Aries": {
        "gift": "görünürlükte cesaret, inisiyatif ve hızla öne çıkabilme",
        "shadow": "acele çıkmak ya da sabır düştüğünde fazla sert görünmek",
    },
    "Taurus": {
        "gift": "görünürlükte güven, istikrar ve sağlam bir kalite hissi",
        "shadow": "fazla beklemek ya da güvenli alandan geç çıkmak",
    },
    "Gemini": {
        "gift": "görünürlükte iletişim, çeviklik ve çok yönlü ifade",
        "shadow": "fazla dağılmak ya da aynı anda çok şeye açılmak",
    },
    "Cancer": {
        "gift": "görünürlükte şefkat, bağ kurma ve koruyucu bir etki",
        "shadow": "algıya fazla alınmak ya da ruh haline göre geri çekilmek",
    },
    "Leo": {
        "gift": "görünürlükte sıcaklık, karizma ve doğal sahne gücü",
        "shadow": "görülmediğinde motivasyon düşmesi ya da gurur üzerinden kapanmak",
    },
    "Virgo": {
        "gift": "görünürlükte ustalık, düzen ve rafine bir işçilik",
        "shadow": "fazla düzeltmek ya da kusursuzlaşana kadar beklemek",
    },
    "Libra": {
        "gift": "görünürlükte denge, estetik ve ilişki zekası",
        "shadow": "herkesi gözetirken kendi yönünü geciktirmek",
    },
    "Scorpio": {
        "gift": "görünürlükte yoğunluk, strateji ve güçlü bir manyetizma",
        "shadow": "fazla kontrol etmek ya da kendini gereğinden çok saklamak",
    },
    "Sagittarius": {
        "gift": "görünürlükte vizyon, cesaret ve ferah bir genişleme hissi",
        "shadow": "fazla büyütmek ya da hazırlığı atlayıp ileri fırlamak",
    },
    "Capricorn": {
        "gift": "görünürlükte otorite, ciddiyet ve güven veren bir omurga",
        "shadow": "fazla yük almak ya da her şeyi tek başına taşımaya çalışmak",
    },
    "Aquarius": {
        "gift": "görünürlükte özgünlük, bağımsızlık ve geleceğe açık bir ton",
        "shadow": "mesafeli görünmek ya da fazla ters köşe kalmak",
    },
    "Pisces": {
        "gift": "görünürlükte sezgi, atmosfer ve ilham veren bir etki",
        "shadow": "yönün bulanıklaşması ya da sınırların gevşemesi",
    },
}

_CAREER_RULER_SIGN_BALANCE_TR = {
    "Aries": {
        "gift": "üretimde cesaret, hız ve ilk adımı atabilme",
        "shadow": "sabırsızlık ya da bir şeyi fazla erken dışarı koymak",
    },
    "Taurus": {
        "gift": "üretimde sağlamlık, kalite ve sürdürülebilir ritim",
        "shadow": "alıştığı tempodan çıkmakta zorlanmak",
    },
    "Gemini": {
        "gift": "üretimde çeviklik, fikir akışı ve iletişim gücü",
        "shadow": "fazla yayılmak ya da odağı çabuk değiştirmek",
    },
    "Cancer": {
        "gift": "üretimde hassasiyet, sahiplenme ve insan dokusu",
        "shadow": "geri bildirimi fazla kişisel almak",
    },
    "Leo": {
        "gift": "üretimde sıcaklık, görünür ifade ve yaratıcı cesaret",
        "shadow": "takdir eksikliğinde motivasyon kırılması",
    },
    "Virgo": {
        "gift": "üretimde detay gücü, edit becerisi ve temiz işçilik",
        "shadow": "fazla incelemek ya da bitirmeyi geciktirmek",
    },
    "Libra": {
        "gift": "üretimde estetik, ton ayarı ve ilişki yönetimi",
        "shadow": "fazla tartmak ya da net kararı geciktirmek",
    },
    "Scorpio": {
        "gift": "üretimde derinlik, odak ve stratejik güç",
        "shadow": "kontrolü bırakmakta zorlanmak ya da fazla kapanmak",
    },
    "Sagittarius": {
        "gift": "üretimde vizyon, cesaret ve büyük resmi taşıyabilme",
        "shadow": "fazla açılmak ya da her şeyi aynı anda büyütmek",
    },
    "Capricorn": {
        "gift": "üretimde disiplin, dayanıklılık ve yapı kurma gücü",
        "shadow": "kendine fazla sert davranmak ya da süreci ağırlaştırmak",
    },
    "Aquarius": {
        "gift": "üretimde özgünlük, bağımsız düşünce ve yenilik",
        "shadow": "kopuklaşmak ya da çok ters bir çizgide kalmak",
    },
    "Pisces": {
        "gift": "üretimde sezgi, atmosfer ve yaratıcı geçirgenlik",
        "shadow": "dağılmak ya da sınırları yeterince net kuramamak",
    },
}

_MIND_ASC_OPENING_TR = {
    "Aries": "Yükselenin Koç olduğu için hayata genelde hızlı, direkt ve fazla dolanmadan giriyorsun.",
    "Taurus": "Yükselenin Boğa olduğu için hayata önce zemini yoklayarak, rahatlayınca açılarak giriyorsun.",
    "Gemini": "Yükselenin İkizler olduğu için bir ortama girer girmez zihnin çalışmaya, bağlantılar kurmaya başlıyor.",
    "Cancer": "Yükselenin Yengeç olduğu için hayata önce hissi yoklayarak, güven gördüğün yerde açılarak giriyorsun.",
    "Leo": "Yükselenin Aslan olduğu için bir ortama girdiğinde görünür olsan bile, içeride yine de nasıl algılandığını takip ediyorsun.",
    "Virgo": "Yükselenin Başak olduğu için hayata önce detayları ve düzeni okuyarak giriyorsun.",
    "Libra": "Yükselenin Terazi olduğu için bir ortama girdiğinde önce havayı, tonu ve insanlar arasındaki dengeyi yokluyorsun.",
    "Scorpio": "Yükselenin Akrep olduğu için hayata hemen açılarak değil, önce sezerek ve güveni tartarak giriyorsun.",
    "Sagittarius": "Yükselenin Yay olduğu için hayata genelde açık, meraklı ve hareket etmeye hazır bir yerden giriyorsun.",
    "Capricorn": "Yükselenin Oğlak olduğu için hayata genelde temkinli giriyorsun. Önce bakıyor, tartıyor, kim nasıl biri anlamaya çalışıyorsun.",
    "Aquarius": "Yükselenin Kova olduğu için bir ortama girdiğinde önce sistemi, mesafeyi ve insanların nasıl çalıştığını okuyorsun.",
    "Pisces": "Yükselenin Balık olduğu için hayata önce hissi alarak, sonra şeklini bularak giriyorsun.",
}

_MIND_SIGN_DRIVE_TR = {
    "Aries": "Koç ise buna cesaret, hız ve direktlik ekliyor; gölgesinde sabırsızlık ya da ani tepki de taşıyabiliyor.",
    "Taurus": "Boğa ise buna sabitlik, dayanıklılık ve kolay vazgeçmeme hali ekliyor.",
    "Gemini": "İkizler ise buna hız, merak ve aynı anda birkaç ihtimali açma eğilimi ekliyor.",
    "Cancer": "Yengeç ise buna duygusal hassasiyet, içe çekilme ve korunma ihtiyacı ekliyor.",
    "Leo": "Aslan ise buna sıcaklık, görünürlük ve söylediğinin etkisini hissetme isteği ekliyor.",
    "Virgo": "Başak ise buna analiz, detay takibi ve hatayı ayıklama refleksi ekliyor.",
    "Libra": "Terazi ise buna ton ayarı, ilişki bilinci ve tartarak ilerleme hali ekliyor.",
    "Scorpio": "Akrep ise buna yoğunluk, kontrol ve kolay açılmayan bir iç radar ekliyor.",
    "Sagittarius": "Yay ise buna cesaret, geniş bakış ve direkt anlam arayışı ekliyor.",
    "Capricorn": "Oğlak ise buna kontrol, ciddiyet ve her şeyi sağlam bir zemine oturtma isteği ekliyor.",
    "Aquarius": "Kova ise buna mesafe, bağımsızlık ve kendi doğrusuna göre hareket etme hali ekliyor.",
    "Pisces": "Balık ise buna sezgisellik, geçirgenlik ve bazen dağılmaya açık bir akış ekliyor.",
}

_MIND_PLANET_ENGINE_TR = {
    "Saturn": "Sürekli bir şeyi fark eden, bir şeye karşı duran ya da bir şeyi düzeltmek isteyen bir tarafın olabilir.",
    "Mars": "Sürekli bir şeyi harekete geçirmek, hızlandırmak ya da tıkananı açmak isteyen bir tarafın olabilir.",
    "Mercury": "Sürekli bağlantı kuran, ayrıntı toplayan ve aynı anda birkaç ihtimali düşünen bir tarafın olabilir.",
    "Venus": "Sürekli ton ayarlayan, insanların arasındaki ince farkları ve ilişki ritmini yoklayan bir tarafın olabilir.",
    "Jupiter": "Sürekli anlam arayan, resmi büyüten ve bir yere yön vermek isteyen bir tarafın olabilir.",
    "Moon": "Sürekli duygusal tonu yoklayan, neyin güven verdiğini neyin yorduğunu hızla hisseden bir tarafın olabilir.",
    "Sun": "Sürekli kendi merkezini, duruşunu ve ne söylemek istediğini toparlayan bir tarafın olabilir.",
}

_MIND_PLANET_TENSION_TR = {
    "Saturn": (
        "Bir yanın 'dur, doğru söyle, dikkatli ol' diyor.",
        "Diğer yanın ise 'şimdi söyle, direkt söyle, açık ol' diyor.",
    ),
    "Mars": (
        "Bir yanın 'bekleme, şimdi hareket et' diyor.",
        "Diğer yanın ise 'bir saniye, bunun nereye çarpacağını da gör' diyor.",
    ),
    "Mercury": (
        "Bir yanın aynı anda birkaç ihtimali açıyor.",
        "Diğer yanın ise bunların içinden tek bir net cümle çıkarmaya çalışıyor.",
    ),
    "Venus": (
        "Bir yanın tonu korumak, kimseyi gereksiz yere sertleştirmemek istiyor.",
        "Diğer yanın ise içinden gelen şeyi fazla yumuşatmadan söylemek istiyor.",
    ),
    "Jupiter": (
        "Bir yanın resmi büyütmek ve açık konuşmak istiyor.",
        "Diğer yanın ise söylediğin şeyin gerçekten anlamlı ve yerli yerinde olmasını arıyor.",
    ),
    "Moon": (
        "Bir yanın kendini korumak ve geri çekilmek istiyor.",
        "Diğer yanın ise anlaşılmak için gerçek duygunu ortaya koymak istiyor.",
    ),
    "Sun": (
        "Bir yanın görünür olmak ve adını koymak istiyor.",
        "Diğer yanın ise bunu taşıyacak ağırlığı ve doğru anı kolluyor.",
    ),
}

_MIND_PLANET_STRENGTH_TR = {
    "Saturn": "Sözünde hem ağırlık hem kıvılcım var.",
    "Mars": "Sözünde hem hız hem cesaret var.",
    "Mercury": "Sözünde hem zeka hem çeviklik var.",
    "Venus": "Sözünde hem ton hem bağ kurma gücü var.",
    "Jupiter": "Sözünde hem ufuk hem inandırıcılık var.",
    "Moon": "Sözünde hem duygu hem sezgi var.",
    "Sun": "Sözünde hem netlik hem etki var.",
}

_MIND_PLANET_GROWTH_TR = {
    "Saturn": "Sesini kullanmak için sertleşmek zorunda değilsin.",
    "Mars": "Hızlı olmak güzel ama her an savaşta olmak zorunda değilsin.",
    "Mercury": "Her şeyi aynı anda söylemek zorunda değilsin; en doğru cümle bazen daha sade olan oluyor.",
    "Venus": "Her şeyi yumuşatmak zorunda değilsin; bazen en gerçek ton, en dürüst olandır.",
    "Jupiter": "Her şeyi büyük bir açıklamaya çevirmek zorunda değilsin; bazen netlik zaten yeterince güçlüdür.",
    "Moon": "Kendini korumak önemli ama her yakınlıkta geri çekilmek zorunda değilsin.",
    "Sun": "Görünür olmak için sürekli kendini kanıtlamak zorunda değilsin.",
}

_HARD_ASPECT_TYPES = {"square", "opposition"}
_SOFT_ASPECT_TYPES = {"trine", "sextile"}
_MAJOR_ASPECT_TYPES = _HARD_ASPECT_TYPES | _SOFT_ASPECT_TYPES | {"conjunction"}

_SECTION_SLOT = {
    "mind_system": "secondary_balancing_line",
    "relationships": "relational_line",
    "career_visibility": "work_visibility_line",
}

_PRIMITIVE_CHIP_TR = {
    "self_definition": "Kimlik",
    "visible_presence": "Görünürlük",
    "inner_structure": "İç Yapı",
    "originality_drive": "Özgünlük",
    "big_picture_vision": "Vizyon",
    "tone_sensitivity": "Ton Hassasiyeti",
    "systems_thinking": "Sistem Zihni",
    "inner_critic": "İç Standart",
    "push_pull_drive": "İtme-Çekme",
    "methodical_drive": "Yöntem",
    "mental_structuring": "Zihinsel Düzen",
    "intimacy_depth": "Derin Yakınlık",
    "relational_security": "İlişki Güveni",
    "graceful_affection": "Yumuşak Bağ",
    "transformative_bonding": "Dönüştürücü Bağ",
    "emotional_threshold": "Güven Eşiği",
    "public_refinement": "Rafine Etki",
    "visibility_sensitivity": "Görünürlük Eşiği",
    "backstage_creation": "Perde Arkası",
    "recharge_through_home": "İç Toparlanma",
    "family_self_reliance": "Kendi Zemini",
    "creation_luck": "Yaratım Akışı",
    "network_luck": "Çevre Akışı",
    "meaningful_expansion": "Anlamlı Büyüme",
}


def _house_ruler(graph: Mapping[str, Any], house: int) -> Mapping[str, Any]:
    house_rulers = graph.get("house_rulers")
    if not isinstance(house_rulers, Mapping):
        return {}
    raw = house_rulers.get(str(house))
    return raw if isinstance(raw, Mapping) else {}


def _planet_positions(planets: List[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for item in planets:
        if not isinstance(item, Mapping):
            continue
        name = str(item.get("planet") or "").strip()
        if not name:
            continue
        out[name] = dict(item)
    return out


def _planet_pos(planet: str, planets_map: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Any]:
    raw = planets_map.get(planet)
    return raw if isinstance(raw, Mapping) else {}


def _seed_base(chart_data: Mapping[str, Any], asc_sign: str, mc_sign: str) -> str:
    birth_dt = (
        str(chart_data.get("birth_datetime") or "").strip()
        or str(chart_data.get("birthDateTime") or "").strip()
        or str(chart_data.get("metadata", {}).get("birth_datetime") or "").strip()
    )
    raw = f"{birth_dt}|{asc_sign}|{mc_sign}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _to_house(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _pick_variant(options: List[str], seed: str) -> str:
    if not options:
        return ""
    index = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[index]


def _cleanup_text(text: str) -> str:
    value = str(text or "").replace("/", " ").replace("(", "").replace(")", "")
    value = re.sub(r"\s+", " ", value).strip()
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", value) if part.strip()]
    seen: set[str] = set()
    deduped: List[str] = []
    for part in parts:
        key = re.sub(r"[^a-z0-9çğıöşü]+", "", part.lower())
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(part)
    return " ".join(deduped).strip()


def _join_body_micro(body: str, micro: str) -> str:
    return _cleanup_text(f"{body} {micro}")


def _split_sentences(text: str) -> List[str]:
    raw = str(text or "").strip()
    if not raw:
        return []
    protected = re.sub(r"(\b\d{1,2})\.\s*(ev\w*)\b", r"\1__EV_DOT__ \2", raw, flags=re.IGNORECASE)
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", protected) if part.strip()]
    return [part.replace("__EV_DOT__", ".").strip() for part in parts]


def _semantic_tokens(text: str) -> set[str]:
    stopwords = {
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
    }
    return {
        token
        for token in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", str(text or "").lower())
        if len(token) >= 3 and token not in stopwords
    }


def _semantic_overlap(a: str, b: str) -> float:
    left = _semantic_tokens(a)
    right = _semantic_tokens(b)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _build_thread_paragraph(one_liner: str, body: str, micro: str) -> str:
    sentences: List[str] = []
    lead = str(one_liner or "").strip()
    body_sentences = _split_sentences(body)
    if lead and (not body_sentences or _semantic_overlap(lead, body_sentences[0]) < 0.7):
        sentences.append(lead)
    for sentence in body_sentences:
        if any(_semantic_overlap(sentence, prior) >= 0.78 for prior in sentences):
            continue
        sentences.append(sentence)
        if len(sentences) >= 4:
            break
    if len(sentences) < 4 and micro and all(_semantic_overlap(micro, prior) < 0.74 for prior in sentences):
        sentences.append(micro)
    return _cleanup_text(" ".join(sentences[:4]))


def _family_line(options: Mapping[str, str], family: str, fallback: str) -> str:
    return str(options.get(family) or fallback).strip()


def _spine_line(master_selector: Mapping[str, Any] | None, slot: str) -> Mapping[str, Any]:
    identity_spine = (
        master_selector.get("identity_spine")
        if isinstance(master_selector, Mapping) and isinstance(master_selector.get("identity_spine"), Mapping)
        else {}
    )
    payload = identity_spine.get(slot)
    return payload if isinstance(payload, Mapping) else {}


def _spine_chip_labels(line: Mapping[str, Any]) -> list[str]:
    labels: list[str] = []
    for primitive_id in line.get("source_primitives") or []:
        label = _PRIMITIVE_CHIP_TR.get(str(primitive_id))
        if label and label not in labels:
            labels.append(label)
        if len(labels) >= 2:
            break
    return labels


def _spine_sentence(slot: str, line: Mapping[str, Any]) -> str:
    labels = _spine_chip_labels(line)
    phrase = " ve ".join(labels[:2]) if labels else str(line.get("label") or "").strip()
    if not phrase:
        return ""
    if slot == "secondary_balancing_line":
        return f"Burada asıl çalışan çizgi, {phrase.lower()} tarafını düzen kurdukça daha net hissetmen."
    if slot == "relational_line":
        return f"Bu alanda merkezde duran şey, {phrase.lower()} çizgisinin güven geldikçe açılması."
    if slot == "work_visibility_line":
        return f"Görünür tarafta fark yaratan şey, {phrase.lower()} hattının hazırlıkla birlikte güçlenmesi."
    if slot == "shadow_protection_line":
        return f"Zorlandığında seni toparlayan çizgi, {phrase.lower()} tarafının içerde zemin kurması."
    return f"Bu başlıkta merkezde duran tema, {phrase.lower()} çizginin daha belirgin çalışması."


def _apply_spine_to_sections(
    sections: List[Dict[str, Any]],
    *,
    master_selector: Mapping[str, Any] | None,
) -> List[Dict[str, Any]]:
    aligned: List[Dict[str, Any]] = []
    for section in sections:
        if not isinstance(section, Mapping):
            continue
        item = dict(section)
        slot = _SECTION_SLOT.get(str(item.get("id") or ""))
        line = _spine_line(master_selector, slot or "")
        if not slot or not line:
            aligned.append(item)
            continue
        spine_sentence = _spine_sentence(slot, line)
        body = str(item.get("body") or "").strip()
        if spine_sentence and _semantic_overlap(body, spine_sentence) < 0.48:
            item["body"] = _cleanup_text(f"{body} {spine_sentence}")
        chips = list(item.get("chips") or [])
        for label in _spine_chip_labels(line):
            if label not in chips:
                chips.append(label)
            if len(chips) >= 4:
                break
        item["chips"] = chips[:4]
        aligned.append(item)
    return aligned


def _sign_label(sign: str) -> str:
    return SIGN_LABEL_TR.get(str(sign or "").strip(), str(sign or "").strip())


def _planet_label(planet: str) -> str:
    return PLANET_LABEL_TR.get(str(planet or "").strip(), str(planet or "").strip())


def _house_phrase(house: int) -> str:
    return f"{house}. ev"


def _house_locative(house: int) -> str:
    return f"{house}. evde"


def _sign_locative(sign: str) -> str:
    return SIGN_LOCATIVE_TR.get(str(sign or "").strip(), "")


def _sign_vibe(sign: str) -> str:
    return SIGN_VIBE_TR.get(str(sign or "").strip(), "kendine özgü")


def _sign_tone(sign: str) -> str:
    return SIGN_TONE_TR.get(str(sign or "").strip(), "kendine özgü")


def _planet_placement_phrase(*, planet_label: str, sign: str, house: int, sign_first: bool = False) -> str:
    sign_locative = _sign_locative(sign)
    house_locative = _house_locative(house)
    if sign_first and sign_locative:
        return f"{planet_label} {sign_locative} ve {house_locative}"
    if sign_locative:
        return f"{planet_label} {house_locative} ve {sign_locative}"
    return f"{planet_label} {house_locative}"


def _safe_float(value: Any, default: float = 99.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _aspect_type(entry: Mapping[str, Any]) -> str:
    return str(entry.get("aspect") or entry.get("type") or "").strip().lower()


def _aspect_partner(entry: Mapping[str, Any], planet: str) -> str:
    p1 = str(entry.get("planet1") or "").strip()
    p2 = str(entry.get("planet2") or "").strip()
    if p1 == planet:
        return p2
    if p2 == planet:
        return p1
    return ""


def _best_matching_aspect(
    *,
    planet: str,
    partners: List[str],
    aspect_index: Mapping[str, List[Mapping[str, Any]]],
    allowed_types: set[str] | None = None,
) -> Mapping[str, Any]:
    if not planet or not isinstance(aspect_index, Mapping):
        return {}
    partner_order = {name: idx for idx, name in enumerate(partners)}
    best_entry: Mapping[str, Any] = {}
    best_rank: tuple[int, int, float] | None = None
    for raw in aspect_index.get(planet) or []:
        if not isinstance(raw, Mapping):
            continue
        partner = _aspect_partner(raw, planet)
        if partner not in partner_order:
            continue
        aspect_type = _aspect_type(raw)
        if allowed_types and aspect_type not in allowed_types:
            continue
        quality_rank = 0 if aspect_type == "conjunction" else 1 if aspect_type in _HARD_ASPECT_TYPES else 2 if aspect_type in _SOFT_ASPECT_TYPES else 3
        rank = (partner_order[partner], quality_rank, _safe_float(raw.get("orb")))
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_entry = raw
    return dict(best_entry) if best_entry else {}


def _has_control_loop(loops: List[Mapping[str, Any]], planet: str) -> bool:
    for entry in loops:
        if not isinstance(entry, Mapping):
            continue
        planets = entry.get("planets") or []
        if not isinstance(planets, list):
            continue
        if planet in planets and {"Saturn", "Mars", "Mercury"}.issubset(set(str(item) for item in planets)):
            return True
    return False


def _merge_block_line(block: str, extra: str) -> str:
    if not extra:
        return block
    return _cleanup_text(f"{block} {extra}")


def _mind_personalization_profile(
    *,
    asc_ruler: str,
    planets_map: Mapping[str, Mapping[str, Any]],
    aspect_index: Mapping[str, List[Mapping[str, Any]]],
    loops: List[Mapping[str, Any]],
) -> Dict[str, str]:
    retrograde = bool(_planet_pos(asc_ruler, planets_map).get("retrograde"))
    reactive = _best_matching_aspect(
        planet=asc_ruler,
        partners=["Mars", "Uranus", "Pluto"],
        aspect_index=aspect_index,
        allowed_types=_HARD_ASPECT_TYPES | {"conjunction"},
    )
    filtered = _best_matching_aspect(
        planet=asc_ruler,
        partners=["Saturn", "Mercury"],
        aspect_index=aspect_index,
        allowed_types=_MAJOR_ASPECT_TYPES,
    )
    sensitive = _best_matching_aspect(
        planet=asc_ruler,
        partners=["Moon", "Venus", "Neptune"],
        aspect_index=aspect_index,
        allowed_types=_MAJOR_ASPECT_TYPES,
    )
    expressive = _best_matching_aspect(
        planet=asc_ruler,
        partners=["Jupiter", "Sun"],
        aspect_index=aspect_index,
        allowed_types=_SOFT_ASPECT_TYPES | {"conjunction"},
    )
    control_loop = _has_control_loop(loops, asc_ruler)

    if reactive:
        profile = {
            "opening": "Bu yüzden dışarıdaki sakinlik, içerideki başlatan ve cesur enerjiyi her zaman göstermiyor olabilir.",
            "engine": "Bir şey içerde çarptığında düşüncen çok hızlı biçimde pozisyona dönüşebiliyor; bu sana çok net ve direkt bir ifade verirken gölgesinde ani tepki ya da savunmaya geçme hali de yaratabiliyor.",
            "tension": "Bazen kendini fazla tutup sonra bir anda sert çıkman biraz da buradan geliyor olabilir.",
            "strength": "Kritik anlarda başkalarının dolandığı şeyi çok kısa bir cümleyle açığa çıkarabiliyor, gerektiğinde ilk hareketi sen başlatabiliyorsun.",
            "growth": "Burada mesele ateşi söndürmek değil; onu daha isabetli ve daha az savunmalı kullanmak.",
            "caption": "Hızınla omurgan aynı anda çalıştığında sözün gerçekten yön değiştiriyor; ayarı kaçtığında ise aynı güç keskinliğe dönebiliyor.",
            "body": "Bu yüzden zihnindeki hız sadece tempo değil; iyi çalıştığında cesaret ve netlik, zorlandığında ise savunma refleksi yaratabiliyor.",
        }
    elif retrograde or filtered:
        profile = {
            "opening": "Dışarıdaki sakinliğinin arkasında, cümleleri sürekli elden geçiren ikinci bir iç editör de çalışıyor olabilir.",
            "engine": "Mesele sende hız eksikliği değil; düşünceyi dışarı vermeden önce içerden filtrelemek.",
            "tension": "Ne söyleyeceğini bilmediğin için değil, yanlış ya da eksik söylemek istemediğin için duruyor olabilirsin.",
            "strength": "Bu filtre doğru çalıştığında sözün yükselmeden de çok etkili olabiliyor.",
            "growth": "Kendini her seferinde bu kadar sıkmadan da anlaşılabileceğini görmek burada önemli.",
            "caption": "O yüzden sesin güçlendikçe daha gürültülü değil, daha isabetli hale geliyor.",
            "body": "Bu iç filtre bazen seni gereğinden fazla düşündürse de, doğru çalıştığında çok güçlü bir zihin disiplini veriyor.",
        }
    elif sensitive:
        profile = {
            "opening": "Bu yüzden zihninde sadece mantık değil, ton ve his de aynı anda çalışıyor olabilir.",
            "engine": "Bir şeyi yalnızca ne olduğu üzerinden değil, sende nasıl yankılandığı üzerinden de okuyorsun.",
            "tension": "Bazen içinden gelen şeyi söylemekle ortamın tonunu korumak arasında kalabiliyorsun.",
            "strength": "İnsanların söylemediği duyguyu da sezdiğin için sözün yalnızca net değil, temas eden bir güç taşıyor.",
            "growth": "Herkesin yükünü hissetmeden de kendi sesini koruyabileceğini görmek burada önemli.",
            "caption": "Senin zihnin yalnızca hızlı değil; aynı zamanda ince ayar yapabilen bir zihin.",
            "body": "Bu yüzden kararların yalnızca mantıktan değil, sezdiğin ince tonlardan da etkileniyor olabilir.",
        }
    elif expressive:
        profile = {
            "opening": "Bu yüzden içeride yalnızca hız değil, kelimeyle anlam arasında güçlü bir bağ da çalışıyor olabilir.",
            "engine": "Bir şeyin adını koyabildiğinde yalnızca anlatmıyor, aynı zamanda yön de veriyorsun.",
            "tension": "Bazen zihnin fazla açıldığı için bir düşünceyi tam bitirmeden ötekine geçmek isteyebilirsin.",
            "strength": "Anlatabildiğinde çevrendeki insanları da hızla toparlayıp hareket ettirebiliyorsun.",
            "growth": "Her içgörüyü aynı anda yetiştirmek zorunda olmadığını görmek burada rahatlatıcı.",
            "caption": "Senin sesin yalnızca savunma değil, yön verme aracı da olabiliyor.",
            "body": "Bu yüzden doğru cümle geldiğinde yalnızca sen değil, etrafındaki akış da netleşmeye başlayabiliyor.",
        }
    else:
        profile = {
            "opening": "",
            "engine": "Bu yüzden zihninin ritmi yalnızca karakterinden değil, haritandaki asıl çalışma biçiminden geliyor.",
            "tension": "İçerdeki bu ritim bazen seni aynı anda hem temkinli hem de hızlı kılabiliyor.",
            "strength": "Doğru çalıştığında sözün abartısız ama güven veren bir etki bırakıyor.",
            "growth": "Burada asıl öğrenme, iç hızını dışarıya daha temiz taşımak.",
            "caption": "",
            "body": "",
        }

    if control_loop:
        profile["engine"] = _cleanup_text(
            f"{profile.get('engine') or ''} Karar, ifade ve hareketin birbirini tetiklemesi yüzünden bazen tek bir cümle içeride birkaç tur dönebiliyor."
        )
    if retrograde:
        profile["opening"] = _cleanup_text(
            f"{profile.get('opening') or ''} Dışarıdan net görünsen de kararın çoğu zaman içeride bir tur daha dönmek isteyebilir."
        )
        profile["growth"] = _cleanup_text(
            f"{profile.get('growth') or ''} Kendi içine bu kadar çok geri dönmeden de ilerleyebileceğini görmek burada ayrı bir rahatlama getirir."
        )
    return profile


def _relationship_personalization_profile(
    *,
    r7: str,
    planets_map: Mapping[str, Mapping[str, Any]],
    aspect_index: Mapping[str, List[Mapping[str, Any]]],
) -> Dict[str, str]:
    retrograde = bool(_planet_pos(r7, planets_map).get("retrograde"))
    intense = _best_matching_aspect(
        planet=r7,
        partners=["Pluto"],
        aspect_index=aspect_index,
        allowed_types=_HARD_ASPECT_TYPES | {"conjunction"},
    )
    guarded = _best_matching_aspect(
        planet=r7,
        partners=["Saturn"],
        aspect_index=aspect_index,
        allowed_types=_MAJOR_ASPECT_TYPES,
    )
    dreamy = _best_matching_aspect(
        planet=r7,
        partners=["Neptune"],
        aspect_index=aspect_index,
        allowed_types=_MAJOR_ASPECT_TYPES,
    )
    charged = _best_matching_aspect(
        planet=r7,
        partners=["Mars"],
        aspect_index=aspect_index,
        allowed_types=_HARD_ASPECT_TYPES | {"conjunction"},
    )
    warm = _best_matching_aspect(
        planet=r7,
        partners=["Moon", "Venus", "Jupiter"],
        aspect_index=aspect_index,
        allowed_types=_SOFT_ASPECT_TYPES | {"conjunction"},
    )

    if intense:
        profile = {
            "opening": "Bu yüzden birine açıldığında bağ sende kolay kolay hafif kalmıyor olabilir.",
            "house": "Yakınlık sende sevgiyle beraber kontrol, kaybetme korkusu ya da dönüşüm ihtiyacını da açabiliyor olabilir.",
            "sign": "Karşındaki insanın senden ne kadar içeri geçtiği, duygunun kendisi kadar belirleyici hale gelebiliyor.",
            "strength": "Sevdiğinde gerçekten derine inebildiğin için yüzeyde kalmayan bir sadakat taşıyorsun.",
            "shadow": "Ama aynı derinlik, karşı tarafın yarım kalışını sende daha sert bir yere dokundurabiliyor.",
            "growth": "Burada asıl öğrenme, derinlik ile kriz arasındaki farkı ayırabilmek.",
            "caption": "Senin sevme biçimin güçlü; bunun illa yorucu olması gerekmiyor.",
            "body": "Bu yüzden bir bağ başladığında yalnızca yakınlaşmıyor, aynı zamanda hayatında çok daha derin bir yer kaplayabiliyor.",
        }
    elif guarded:
        profile = {
            "opening": "Bu yüzden bağ kurmadan önce karşındaki insanın omurgasını ve yük taşıyıp taşıyamayacağını da ölçüyor olabilirsin.",
            "house": "Yakınlık sende ancak güvenlik hissi oluştuğunda gerçekten rahatlıyor olabilir.",
            "sign": "Kalbin yalnızca sıcaklık değil, ciddiyet ve tutarlılık da arıyor olabilir.",
            "strength": "Birini seçtiğinde kolay kolay bırakmayan, ciddi ve dayanıklı bir bağ kurabiliyorsun.",
            "shadow": "Ama bu temkin bazen seni fazla bekleten ya da gereğinden fazla yük taşıtan bir hale de dönebilir.",
            "growth": "Burada asıl rahatlama, güveni sadece kontrol ederek değil yaşayarak da kurabileceğini görmek.",
            "caption": "Senin sevgin yavaş açılabilir ama açıldığında çok sağlam çalışıyor.",
            "body": "Bu yüzden bir ilişkiye yalnızca kalbinle değil, sorumluluk duygunla da giriyor olabilirsin.",
        }
    elif dreamy:
        profile = {
            "opening": "Bu yüzden bazen karşındakine yalnızca olduğu gibi değil, ne hissettirdiği ve ne olabileceği üzerinden de bağlanabiliyorsun.",
            "house": "Yakınlıkta sezgi ve hayal gücü çok güçlü çalıştığı için bağın tonunu kolayca büyütebiliyorsun.",
            "sign": "Belirsiz ama büyülü gelen şeyler seni bazen beklediğinden daha çok içine çekebilir.",
            "strength": "İlişkide çok ince bir ruh halini, şefkati ve görünmeyen bağı hissedebiliyorsun.",
            "shadow": "Ama aynı açıklık, sınırların ve beklentilerin bazen bulanıklaşmasına da neden olabilir.",
            "growth": "Sezgini korurken sınırını da korumak burada çok belirleyici.",
            "caption": "Kalbinin sezgisi çok güçlü; mesele bunu kendini kaybetmeden kullanmak.",
            "body": "Bu yüzden bir bağın ihtimali bile sende bazen ilişkinin kendisi kadar yer tutabiliyor.",
        }
    elif charged:
        profile = {
            "opening": "Bu yüzden yakınlık sende kolayca canlı, direkt ve zaman zaman gerilimli bir ritim de taşıyabiliyor.",
            "house": "Birine bağlandığında duygu ile tepki birbirine karışabildiği için ilişki daha hareketli bir tonda yaşanabilir.",
            "sign": "Sevgi geldiğinde bunu hissettirmek istiyorsun; ama hayal kırıklığı da sende hızlı tepki doğurabiliyor.",
            "strength": "İlişkiye canlılık, dürüstlük ve gerçek bir hareket getirebiliyorsun.",
            "shadow": "Ama sevgiyle savunma refleksi birbirine karıştığında gereğinden sertleşmek de mümkün olabiliyor.",
            "growth": "Burada asıl öğrenme, dürüstlüğü gerilimle karıştırmadan koruyabilmek.",
            "caption": "Senin yakınlığın pasif değil; mesele bunu yormayan bir ritimde tutmak.",
            "body": "Bu yüzden bağ kurduğunda ilişki yalnızca his değil, aynı zamanda enerji de taşımaya başlıyor.",
        }
    elif warm:
        profile = {
            "opening": "Bu yüzden güven geldiğinde sıcaklığın ve yumuşaklığın çok daha hızlı görünür oluyor olabilir.",
            "house": "Yakınlık sadece derinlik değil, şefkat ve rahatlama hissi de getirebilir.",
            "sign": "Kalbin bağ kurduğunda hem yumuşuyor hem de daha cömert çalışıyor olabilir.",
            "strength": "Sevildiğinde yalnızca açılmıyor, karşındakine de ciddi bir duygusal alan verebiliyorsun.",
            "shadow": "Bu yüzden ilgisizlik ya da duygusal soğukluk sende normalden daha fazla hayal kırıklığı yaratabiliyor.",
            "growth": "Sevginin akışını korurken, karşı tarafın yükünü tek başına almamak burada önemli.",
            "caption": "Senin sevgin sıcak, gerçek ve besleyici; onu koruman gereken yer kendi sınırların.",
            "body": "Bu yüzden ilişkide karşılıklı sıcaklık hissettiğinde çok daha rahat ve içten açılabiliyorsun.",
        }
    else:
        profile = {
            "opening": "",
            "house": "Bu yüzden ilişkide ne hissettiğin kadar, bu bağın sende nereye dokunduğu da önemli hale geliyor.",
            "sign": "",
            "strength": "Sevdiğinde hafif değil, gerçek bir yatırım yapıyorsun.",
            "shadow": "Tam da bu yüzden yarım kalan şeyler sende daha uzun süre yankı bulabiliyor.",
            "growth": "Yakınlık ile yük taşımak arasındaki çizgiyi ayırmak burada ana öğrenme olabilir.",
            "caption": "",
            "body": "",
        }

    if retrograde:
        profile["opening"] = _cleanup_text(
            f"{profile.get('opening') or ''} Eski bağların ya da yarım kalmış hislerin sende kolay kapanmaması da bunun bir parçası olabilir."
        )
        profile["growth"] = _cleanup_text(
            f"{profile.get('growth') or ''} Geçmişten kalan duyguyu bugünkü bağa karıştırmadığını fark etmek burada çok şey değiştirir."
        )
    return profile


def _career_personalization_profile(
    *,
    mc_ruler: str,
    mc_house: int,
    planets_map: Mapping[str, Mapping[str, Any]],
    aspect_index: Mapping[str, List[Mapping[str, Any]]],
) -> Dict[str, str]:
    retrograde = bool(_planet_pos(mc_ruler, planets_map).get("retrograde"))
    misted = bool(
        _best_matching_aspect(
            planet=mc_ruler,
            partners=["Neptune"],
            aspect_index=aspect_index,
            allowed_types=_MAJOR_ASPECT_TYPES,
        )
    )
    reflective = mc_house == 12 or misted
    disciplined = _best_matching_aspect(
        planet=mc_ruler,
        partners=["Saturn"],
        aspect_index=aspect_index,
        allowed_types=_MAJOR_ASPECT_TYPES,
    )
    expansive = _best_matching_aspect(
        planet=mc_ruler,
        partners=["Jupiter", "Sun"],
        aspect_index=aspect_index,
        allowed_types=_SOFT_ASPECT_TYPES | {"conjunction"},
    )
    assertive = _best_matching_aspect(
        planet=mc_ruler,
        partners=["Mars"],
        aspect_index=aspect_index,
        allowed_types=_MAJOR_ASPECT_TYPES,
    )
    chiron_house = _to_house(_planet_pos("Chiron", planets_map).get("house"), 0)
    sensitive_visibility = chiron_house == 10 or bool(
        _best_matching_aspect(
            planet="Chiron",
            partners=["MC", "Midheaven", mc_ruler],
            aspect_index=aspect_index,
            allowed_types=_MAJOR_ASPECT_TYPES,
        )
    )

    if reflective:
        profile = {
            "opening": "Bu yüzden görünür olmadan önce içeride uzun bir hazırlık alanı kurmak istiyor olabilirsin; insanlar da sende çoğu zaman yalnızca ne yaptığını değil, nasıl bir enerji taşıdığını okuyor olabilir.",
            "engine": "Senin için hazırlık erteleme değil; işin ruhunu, yönünü ve dışarıya nasıl yansıyacağını yerli yerine koyma süreci olabilir.",
            "tension": "Bir yanın henüz hazır hissetmediği şeyi dışarı koymak istemezken, bir yanın da fazla beklediğinde etkinin bulanıklaştığını hissediyor olabilir; bu da görünürlükte hem çekici hem de yorucu bir sis yaratabiliyor.",
            "origin": "Erken yaşta görünür olmadan önce kendi kaliteni içeride kurmayı öğrenmiş olman ya da tam görünmeden önce kendini bir kez daha toplama ihtiyacı geliştirmen mümkün.",
            "strength": "Bu iç hazırlık doğru çalıştığında ortaya koyduğun şey yalnızca estetik değil; aynı zamanda sezgisel, karakterli ve kolay unutulmayan bir iz bırakıyor.",
            "growth": "Asıl öğrenme, yumuşaklığını kaybetmeden daha net görünmek ve başkalarının üzerine yüklediği anlamı taşımak zorunda olmadığını fark etmek.",
            "caption": "Senin görünürlüğün sadece sahne değil; perde arkasında kurduğun iç sağlamlık, sezgi ve nüans duygusuyla da çalışıyor.",
            "body": "Bu yüzden dışarıdaki tempo ile içerdeki hazırlık ritmin her zaman aynı hızda akmayabiliyor; bazen insanlar seni olduğun gibi değil, görmek istedikleri gibi de okuyabiliyor.",
        }
    elif disciplined:
        profile = {
            "opening": "Bu yüzden işte sadece görünmek değil, gerçekten sağlam durmak da istiyor olabilirsin.",
            "engine": "Standart çıtan yüksek olduğu için üretimin kolay kolay yarım çıkmıyor.",
            "tension": "Ama aynı standart bazen seni fazladan bekletebiliyor ya da kendine gereğinden sert davranmana yol açabiliyor.",
            "origin": "Erken yaşta sorumluluk almak ya da sonucu taşıman beklenmiş olabilir.",
            "strength": "Görünür olduğunda insanlar sende yalnızca yetenek değil, güvenilirlik de hissediyor.",
            "growth": "Burada mesele çıtayı düşürmek değil; kendini o çıtanın altında ezmemek.",
            "caption": "Senin görünürlüğün parlamaktan çok, sağlamlık ve süreklilik üzerinden güçleniyor.",
            "body": "Bu yüzden yaptığın şeylerde kalite duygusu çoğu zaman doğal eşiğin gibi çalışıyor.",
        }
    elif expansive:
        profile = {
            "opening": "Bu yüzden görünür olduğunda yalnızca dikkat çekmiyor, alan da açıyor olabilirsin.",
            "engine": "İşini dışarı taşıdığında insanlar sende yön, vizyon ya da büyüme hissi alabiliyor.",
            "tension": "Bazen büyük resmi o kadar hızlı görüyorsun ki detaylarla sahne anı arasında ritim farkı oluşabiliyor.",
            "origin": "Erken yaşta bir şeyleri büyütme, yön verme ya da temsil etme rolü üstlenmiş olman mümkün.",
            "strength": "Doğru çalıştığında görünürlüğün yalnızca başarılı değil, ilham verici de olabiliyor.",
            "growth": "Burada ana öğrenme, büyüklük hissini dağılmadan taşıyabilmek.",
            "caption": "Senin dışarıdaki etkin yalnızca sonuçtan değil, yarattığın ufuk duygusundan geliyor.",
            "body": "Bu yüzden ürettiğin şeyi dolaşıma soktuğunda etkisi sadece bir iş gibi değil, bir yön gibi hissedilebiliyor.",
        }
    elif assertive:
        profile = {
            "opening": "Bu yüzden işte fırsat beklemekten çok, hareket başlatmak isteyen bir tarafın olabilir.",
            "engine": "Görünürlük sende bazen cesaret, hız ve anında aksiyon alma isteğiyle çalışıyor.",
            "tension": "Ama hızlı çıkmak ile doğru anda çıkmak her zaman aynı şey değil; asıl ayar burada gerekiyor.",
            "origin": "Erken yaşta kendi alanını kendin açmak ya da kendi hızını kendin yaratmak zorunda kalmış olabilirsin.",
            "strength": "İş sahasında inisiyatif aldığında etkini hızlı biçimde görünür kılabiliyorsun.",
            "growth": "Burada asıl öğrenme, cesareti aceleyle karıştırmadan kullanmak.",
            "caption": "Senin görünürlüğünde ciddi bir hareket başlatma gücü var.",
            "body": "Bu yüzden işte karar aldığında uzun uzun beklemekten çok ilerlemek isteyebilirsin.",
        }
    else:
        profile = {
            "opening": "",
            "engine": "Bu yüzden görünürlük sende yalnızca sonuç değil, ritim ve zamanlama meselesi de oluyor.",
            "tension": "İç hazırlık ile dış sahne arasındaki ayarı bulmak burada temel konu.",
            "origin": "İş tarafında neyi temsil ettiğini zamanla daha çok kuruyor olabilirsin.",
            "strength": "Doğru çalıştığında etkini sakin ama kalıcı biçimde kuruyorsun.",
            "growth": "Burada asıl öğrenme, kendi ritmini dış dünyayla daha rahat buluşturmak.",
            "caption": "",
            "body": "",
        }

    if sensitive_visibility:
        profile["origin"] = _cleanup_text(
            f"{profile.get('origin') or ''} Görülmek, ciddiye alınmak ya da ortaya koyduğun şeyle değerlendirilmek sende normalden daha hassas bir yere de dokunuyor olabilir."
        )
        profile["growth"] = _cleanup_text(
            f"{profile.get('growth') or ''} Tam da bu yüzden görünürlükteki kırılganlığını saklamak yerine onunla daha bilinçli ilişki kurmak burada ayrı bir güç yaratır."
        )
        profile["caption"] = _cleanup_text(
            f"{profile.get('caption') or ''} En çok hassas olduğun yerde en çok iz bırakma potansiyelin de birikiyor olabilir."
        )

    if retrograde:
        profile["opening"] = _cleanup_text(
            f"{profile.get('opening') or ''} Dışarı koymadan önce kendi içinden ikinci kez geçirmek istemen de buradan gelebilir."
        )
        profile["growth"] = _cleanup_text(
            f"{profile.get('growth') or ''} Her şeyi içerde bir tur daha döndürmeden de paylaşabileceğini fark etmek burada rahatlatıcı olabilir."
        )
    return profile


def _relationship_opening_block(dsc_sign: str) -> str:
    sign_label = _sign_label(dsc_sign)
    payload = _RELATIONSHIP_SIGN_OPENING_TR.get(dsc_sign) or {}
    balance = _RELATIONSHIP_SIGN_BALANCE_TR.get(dsc_sign) or {}
    need = str(payload.get("need") or "yanında gerçekten rahatlayabildiğin bir bağ").strip()
    line = str(payload.get("line") or f"7. evin {sign_label} olduğu için yakınlığı kendine özgü bir tonda yaşıyorsun.").strip()
    gate = str(payload.get("gate") or "Güven oluşmadan tam açılman kolay olmuyor.").strip()
    gift = str(balance.get("gift") or "").strip()
    shadow = str(balance.get("shadow") or "").strip()
    balance_line = ""
    if gift and shadow:
        balance_line = f"Bu yapı sana {gift} verirken, zorlandığında {shadow} tarafı da açığa çıkabiliyor."
    return _cleanup_text(
        f"Sen ilişkide sadece biriyle olmak istemiyorsun. "
        f"Senin aradığın şey, {need}. "
        f"{line} "
        f"{gate} "
        f"{balance_line}"
    )


def _relationship_house_block(*, ruler_label: str, r7_house: int) -> str:
    if r7_house == 8:
        return _cleanup_text(
            f"Birine bağlandığında bunu hafif yaşamıyorsun. "
            "Karşındaki insan bir noktadan sonra yalnızca hoşlandığın biri olmaktan çıkıp iç dünyanda yer eden birine dönüşebiliyor. "
            f"{ruler_label} {_house_locative(r7_house)} olduğu için sen bağ kurarken yüzeyde kalmıyorsun. "
            "Ya gerçekten giriyorsun, ya da zaten hiç girmemiş oluyorsun."
        )
    if r7_house == 3:
        return _cleanup_text(
            "Birine bağlandığında bunu sadece kalbinle değil, zihninle de yaşıyorsun. "
            f"{ruler_label} {_house_locative(r7_house)} olduğu için bağın ritmi çoğu zaman sözle, tonla ve mesaj trafiğiyle kuruluyor. "
            "Yarım cümleler, açıkta kalan meseleler ve belirsiz konuşmalar sende gereğinden fazla yük yaratabiliyor. "
            "Senin için yakınlık biraz da konuşulabilir olmak demek."
        )
    if r7_house == 11:
        return _cleanup_text(
            "Birine bağlandığında mesele sadece aranızdaki duygu olmuyor; aynı tarafta olup olmadığınız da önem kazanıyor. "
            f"{ruler_label} {_house_locative(r7_house)} olduğu için güven sende çoğu zaman arkadaşlık, ekip ve ortak hedef üzerinden kuruluyor. "
            "Bir bağ sosyal zeminde rahatladığında kalbin de daha kolay açılıyor. "
            "Bu yüzden bir ilişkinin yalnızca özel değil, aynı zamanda yönü olan bir tarafı da olsun istiyorsun."
        )
    return _cleanup_text(
        f"Birine bağlandığında bunu hafif yaşamıyorsun. "
        f"{ruler_label} {_house_locative(r7_house)} olduğu için ilişki sende en çok {_house_phrase(r7_house)} temaları üzerinden derinleşiyor. "
        "Bu yüzden bir bağ ya gerçekten içeri giriyor ya da sende yüzeyde kalıyor. "
        "Senin için yakınlık, biraz da o ilişkinin hayatında nereye dokunduğuyla ilgili."
    )


def _relationship_ruler_sign_block(*, r7: str, r7_sign: str) -> str:
    ruler_label = _planet_label(r7)
    sign_label = _sign_label(r7_sign)
    locative = _sign_locative(r7_sign)
    need = _RELATIONSHIP_RULER_SIGN_NEED_TR.get(r7_sign) or (
        "Sen sadece sevilmek istemiyorsun; sevginin sende nasıl hissettirdiği de en az bunun kadar önemli."
    )
    balance = _RELATIONSHIP_RULER_SIGN_BALANCE_TR.get(r7_sign) or {}
    gift = str(balance.get("gift") or "").strip()
    shadow = str(balance.get("shadow") or "").strip()
    balance_line = ""
    if gift and shadow:
        balance_line = f"İyi çalıştığında bu ton sende {gift} tarafını büyütüyor; zorlandığında ise {shadow} tarafı da açığa çıkabiliyor."
    return _cleanup_text(
        f"{ruler_label} {locative if locative else sign_label} olduğu için ilişkide kalbinin aradığı ton daha görünür hale geliyor. "
        f"{need} "
        "Sessiz, belirsiz ya da ne hissettirdiği anlaşılmayan sevgiler sende kolay kolay tam karşılık bulmuyor. "
        f"{balance_line}"
    )


def _relationship_strength_block(*, dsc_sign: str, r7_house: int) -> str:
    if dsc_sign == "Cancer":
        return _cleanup_text(
            "Sen sevdiğinde cömert, koruyan ve duygusal olarak alan açan birine dönüşebiliyorsun. "
            "Karşındaki insanın ihtiyacını, tonunu ve geri çekildiği yeri çabuk fark edebiliyorsun. "
            "Tam da bu yüzden ilişkide karşı tarafın mesafesi seni normalden daha fazla yaralayabiliyor. "
            "Çünkü sen bağa yalnızca ilginle değil, kalbinden yatırım yaparak giriyorsun."
        )
    return _cleanup_text(
        "Sen sevdiğinde ilişkinin içine yalnızca ilgi değil, ciddi bir dikkat de koyuyorsun. "
        "Karşındaki insanın tonunu, mesafesini ve gerçekten orada olup olmadığını kolay fark edebiliyorsun. "
        "Bu sana ilişkide güçlü bir sezgi veriyor. "
        "Ama aynı hassasiyet, karşı tarafın yarım kalışını da sende daha büyük hissettirebiliyor."
    )


def _relationship_shadow_block(*, r7_house: int) -> str:
    if r7_house == 8:
        return _cleanup_text(
            "Buradaki hassas nokta şu: sen bazen bağ kurunca sadece sevmiyorsun, o bağın yükünü de taşımaya başlıyorsun. "
            "Karşındakini anlamaya, çözmeye ve aradaki bağı korumaya çok emek verebiliyorsun. "
            "Bu yüzden kaybetme korkusu, açıkta kalma korkusu ya da 'ben bu kadar açıldım ya karşılığı yoksa?' hissi kolay tetiklenebiliyor. "
            "Ve bunu her zaman dışarı göstermeyebilirsin; dışarıda güçlü dururken içeride çok daha derin etkileniyor olabiliyorsun."
        )
    return _cleanup_text(
        "Buradaki hassas nokta şu: sen bazen bağ kurunca sadece sevmiyor, o bağın düzenini de içinde taşımaya başlıyorsun. "
        "Karşı tarafın tonunu, mesafesini ya da kararsızlığını fazlasıyla üstlenebiliyorsun. "
        "Bu yüzden bir noktadan sonra yalnızca üzülmüyor, aynı zamanda aradaki yükü de tek başına taşımış gibi hissedebiliyorsun. "
        "Dışarıdan kontrollü görünsen bile içeride çok daha derin etkileniyor olabiliyorsun."
    )


def _relationship_growth_block() -> str:
    return _cleanup_text(
        "Senin ilişkide öğrenmeye geldiğin şey şu olabilir: derin bağ kurmak için kendini tüketmen gerekmiyor. "
        "Yoğun sevmen, çok önemsemen ve ciddi bağlanman güzel; ama gerçek bağın illa kriz, kaygı ya da duygusal savaşla kanıtlanması gerekmiyor. "
        "Seni gerçekten besleyen bağ, seni yoran değil; seni sakinleştiren, güven veren ve kalbini yumuşatan bağ."
    )


def _relationship_caption_block(*, dsc_sign: str, r7_house: int) -> str:
    sign_label = _sign_label(dsc_sign)
    return _cleanup_text(
        f"Sen ilişkide sadece aşk aramıyorsun. "
        f"7. evin {sign_label} ve yöneticinin {_house_locative(r7_house)} olması yüzünden, birinin yanında gerçekten içeri alınmayı arıyorsun. "
        "Sevilmekten fazlasını; seçilmek, önemsenmek ve gerçekten tutulmak istiyorsun. "
        "Bu seni hassas yapabiliyor olabilir ama aynı zamanda çok derin, çok sadık ve çok gerçek bir sevme biçimi veriyor."
    )


def _relationship_detail_blocks(
    *,
    dsc_sign: str,
    r7: str,
    r7_sign: str,
    r7_house: int,
    profile: Mapping[str, str] | None = None,
) -> List[str]:
    ruler_label = _planet_label(r7)
    blocks = [
        _relationship_opening_block(dsc_sign),
        _relationship_house_block(ruler_label=ruler_label, r7_house=r7_house),
        _relationship_ruler_sign_block(r7=r7, r7_sign=r7_sign),
        _relationship_strength_block(dsc_sign=dsc_sign, r7_house=r7_house),
        _relationship_shadow_block(r7_house=r7_house),
        _relationship_growth_block(),
        _relationship_caption_block(dsc_sign=dsc_sign, r7_house=r7_house),
    ]
    profile_map = profile or {}
    return [
        _merge_block_line(blocks[0], str(profile_map.get("opening") or "")),
        _merge_block_line(blocks[1], str(profile_map.get("house") or "")),
        _merge_block_line(blocks[2], str(profile_map.get("sign") or "")),
        _merge_block_line(blocks[3], str(profile_map.get("strength") or "")),
        _merge_block_line(blocks[4], str(profile_map.get("shadow") or "")),
        _merge_block_line(blocks[5], str(profile_map.get("growth") or "")),
        _merge_block_line(blocks[6], str(profile_map.get("caption") or "")),
    ]


def _mind_house_line(asc_house: int) -> str:
    if asc_house == 3:
        return "3. ev bunu iletişime, düşünceye, yakın çevreye ve günlük hayata taşıyor."
    if asc_house == 6:
        return "6. ev bunu gündelik ritme, iş yapma biçimine ve sürekli iyileştirmek istediğin yerlere taşıyor."
    if asc_house == 11:
        return "11. ev bunu ekip, arkadaş çevresi, sosyal bağlam ve ortak hedefler tarafına taşıyor."
    if asc_house == 12:
        return "12. ev bunu önce içeriye, perde arkasına ve kendi iç dünyanda çözmeye çalıştığın alanlara taşıyor."
    if asc_house == 1:
        return "1. ev bunu doğrudan duruşuna, beden diline ve hayata verdiğin ilk tepkiye taşıyor."
    return f"{_house_phrase(asc_house)} bunu en çok {HOUSE_ARENA_TR.get(asc_house, 'günlük akış')} tarafına taşıyor."


def _mind_opening_block(
    *,
    asc_sign: str,
    asc_ruler: str,
    asc_ruler_sign: str,
    asc_house: int,
) -> str:
    sign_label = _sign_label(asc_sign)
    ruler_label = _planet_label(asc_ruler)
    asc_line = _MIND_ASC_OPENING_TR.get(asc_sign) or f"Yükselenin {sign_label} olduğu için hayata kendine özgü bir ritimle giriyorsun."
    placement = _planet_placement_phrase(
        planet_label=ruler_label,
        sign=asc_ruler_sign,
        house=asc_house,
        sign_first=True,
    )
    return _cleanup_text(
        f"Sen dışarıdan {_sign_vibe(asc_sign)} görünebilirsin. "
        f"{asc_line} "
        f"Ama iş zihnine ve kendini ifade etme biçimine geldiğinde içeride çok daha {_sign_tone(asc_ruler_sign)} bir şey çalışıyor. "
        f"Çünkü senin yöneticin {placement}. "
        "Yani dışarıdan daha sakin görünsen de içeride hep çalışan, tetikte kalan ya da pozisyon alan bir tarafın var."
    )


def _mind_engine_block(*, asc_ruler: str, asc_ruler_sign: str, asc_house: int) -> str:
    ruler_label = _planet_label(asc_ruler)
    sign_label = _sign_label(asc_ruler_sign)
    engine = _MIND_PLANET_ENGINE_TR.get(
        asc_ruler,
        "Sürekli bir şeyi anlamaya, toparlamaya ve içinden doğru cümleyi çıkarmaya çalışan bir tarafın olabilir.",
    )
    sign_drive = _MIND_SIGN_DRIVE_TR.get(asc_ruler_sign) or f"{sign_label} ise buna kendine özgü bir hız ve ton ekliyor."
    return _cleanup_text(
        "Senin zihnin boşta duran bir zihin değil. "
        f"{engine} "
        f"{_mind_house_line(asc_house)} "
        f"{sign_drive} "
        "O yüzden bazı şeyler sana saçma, adaletsiz ya da gereksiz geldiğinde içeride hemen bir hareket başlıyor."
    )


def _mind_tension_block(*, asc_sign: str, asc_ruler: str) -> str:
    line1, line2 = _MIND_PLANET_TENSION_TR.get(
        asc_ruler,
        (
            "Bir yanın önce durup her şeyi anlamak istiyor.",
            "Diğer yanın ise artık doğrudan söyleyip rahatlamak istiyor.",
        ),
    )
    sign_label = _sign_label(asc_sign)
    return _cleanup_text(
        "Buradaki asıl hikâye şu: içinde aynı anda iki ayrı ritim çalışıyor. "
        f"{line1} "
        f"{line2} "
        "Bu yüzden bazen çok susup beklersin, bazen de bir anda çok net, çok direkt ya da beklenmedik kadar açık çıkarsın. "
        f"İnsanlar seni dışarıdan daha {_sign_vibe(asc_sign)} sanarken, içeride ne kadar hızlı çalıştığını sonradan fark edebilir."
    )


def _mind_origin_block(*, asc_house: int) -> str:
    if asc_house == 3:
        return _cleanup_text(
            "Bu yerleşim çoğu zaman çocukluktan beri bir kendini savunma hali getirebilir. "
            "Yakın çevrede, okulda, kardeşlerle ya da günlük iletişimde sesini duyurmak kolay gelmemiş olabilir. "
            "Sanki alan açmak bazen sana verilmemiş de senin alman gerekmiş gibi çalışabilir. "
            "Bu da seni erken yaşta zihinsel olarak dayanıklı yaparken, bir yandan da hep tetikte kalmana neden olabilir."
        )
    if asc_house == 6:
        return _cleanup_text(
            "Bu yerleşim seni erken yaşta toparlayan, yetiştiren ve eksik olanı fark eden tarafa çekmiş olabilir. "
            "Bir şey aksadığında içinden hemen düzeltmek istemen biraz da buradan geliyor. "
            "O yüzden sen sadece düşünen biri değil, aynı zamanda sistemi çalıştırmaya çalışan birisin. "
            "Ama bu da bazen zihninin hiç tam kapanmamasına neden olabiliyor."
        )
    if asc_house == 11:
        return _cleanup_text(
            "Bu yerleşim erken yaşta grupların içinde kendine yer açma, aynı fikirde olmadığında pozisyon alma ve sosyal bağlamı iyi okuma hali verebilir. "
            "Arkadaşlıklar, ekipler ya da sosyal çevre içinde bir şeyler kolay verilmemiş de senin kendin kurman gerekmiş gibi hissedebilirsin. "
            "Bu da seni hem gözlemci hem de gerektiğinde tavır alan birine dönüştürüyor. "
            "Ama bir yandan da kalabalığın içinde bile zihinsel olarak fazla açık kalmana neden olabiliyor."
        )
    if asc_house == 12:
        return _cleanup_text(
            "Bu yerleşim çoğu zaman duygunu ya da fikrini hemen dışarı vermeden önce içeride toplama alışkanlığı getiriyor. "
            "Bir şey yaşandığında önce kendi içinde anlamlandırıyor, sonra paylaşmak istiyorsun. "
            "Bu seni dışarıdan sakin gösterebilir ama içeride düşündüğünden çok daha fazla şey dönüyor olabilir. "
            "Yani sen sadece sessiz biri değil, önce içerde işleyen birisin."
        )
    return _cleanup_text(
        f"Bu yerleşim seni hayatın en çok {_house_phrase(asc_house)} tarafında uyanık tutuyor olabilir. "
        "Bir şey yaşandığında yalnızca tepki vermiyor, aynı zamanda onun ağırlığını ve sonucunu da düşünüyorsun. "
        "Bu seni erken yaşta daha dikkatli, daha hızlı fark eden ve gerektiğinde pozisyon alan birine çevirmiş olabilir. "
        "Ama bazen bunun bedeli, zihninin kolay kolay tam gevşeyememesi oluyor."
    )


def _mind_strength_block(*, asc_ruler: str) -> str:
    strength = _MIND_PLANET_STRENGTH_TR.get(asc_ruler, "Sözünde hem netlik hem etki var.")
    return _cleanup_text(
        "Senin en güçlü taraflarından biri şu: konuştuğunda sadece fikir söylemiyorsun, hareket başlatabiliyorsun. "
        f"{strength} "
        "Bu yüzden insanlar bazen senden çekinebilir ama aynı zamanda sana saygı da duyar. "
        "Çünkü sen bir şeyin adını koyduğunda, o artık havada kalmıyor."
    )


def _mind_growth_block(*, asc_ruler: str) -> str:
    growth = _MIND_PLANET_GROWTH_TR.get(
        asc_ruler,
        "Kendi sesini kullanmak için ya tamamen susman ya da sertleşmen gerekmiyor.",
    )
    return _cleanup_text(
        "Senin burada öğrenmeye geldiğin şey şu olabilir: "
        f"{growth} "
        "Hayat sana hem içindeki enerjiyi kaybetmeden, hem de kendini tüketmeden konuşmayı öğretiyor. "
        "Senin gücün sadece hızlı tepki vermende değil; ne zaman duracağını, ne zaman çıkacağını ve ne zaman netleşeceğini öğrenmende."
    )


def _mind_caption_block(
    *,
    asc_sign: str,
    asc_ruler: str,
    asc_ruler_sign: str,
    asc_house: int,
) -> str:
    ruler_label = _planet_label(asc_ruler)
    placement = _planet_placement_phrase(
        planet_label=ruler_label,
        sign=asc_ruler_sign,
        house=asc_house,
        sign_first=False,
    )
    return _cleanup_text(
        f"Sen dışarıdan {_sign_vibe(asc_sign)} görünüyorsun ama içinde çok daha {_sign_tone(asc_ruler_sign)} bir zihin taşıyorsun. "
        f"{placement} olduğu için, bir yanın her şeyi ölçmek isterken diğer yanın daha direkt çıkmak isteyebiliyor. "
        "Asıl gücün burada: kendi sesini bastırmadan, kendini sertliğe de mahkûm etmeden kullanmayı öğreniyorsun. "
        "Senin sözünün hem ağırlığı var hem de ateşi."
    )


def _mind_detail_blocks(
    *,
    asc_sign: str,
    asc_ruler: str,
    asc_ruler_sign: str,
    asc_house: int,
    profile: Mapping[str, str] | None = None,
) -> List[str]:
    blocks = [
        _mind_opening_block(
            asc_sign=asc_sign,
            asc_ruler=asc_ruler,
            asc_ruler_sign=asc_ruler_sign,
            asc_house=asc_house,
        ),
        _mind_engine_block(
            asc_ruler=asc_ruler,
            asc_ruler_sign=asc_ruler_sign,
            asc_house=asc_house,
        ),
        _mind_tension_block(asc_sign=asc_sign, asc_ruler=asc_ruler),
        _mind_origin_block(asc_house=asc_house),
        _mind_strength_block(asc_ruler=asc_ruler),
        _mind_growth_block(asc_ruler=asc_ruler),
        _mind_caption_block(
            asc_sign=asc_sign,
            asc_ruler=asc_ruler,
            asc_ruler_sign=asc_ruler_sign,
            asc_house=asc_house,
        ),
    ]
    profile_map = profile or {}
    return [
        _merge_block_line(blocks[0], str(profile_map.get("opening") or "")),
        _merge_block_line(blocks[1], str(profile_map.get("engine") or "")),
        _merge_block_line(blocks[2], str(profile_map.get("tension") or "")),
        _merge_block_line(blocks[3], str(profile_map.get("origin") or "")),
        _merge_block_line(blocks[4], str(profile_map.get("strength") or "")),
        _merge_block_line(blocks[5], str(profile_map.get("growth") or "")),
        _merge_block_line(blocks[6], str(profile_map.get("caption") or "")),
    ]


def _career_opening_block(*, mc_sign: str) -> str:
    sign_label = _sign_label(mc_sign)
    balance = _CAREER_MC_BALANCE_TR.get(mc_sign) or {}
    gift = str(balance.get("gift") or "").strip()
    shadow = str(balance.get("shadow") or "").strip()
    balance_line = ""
    if gift and shadow:
        balance_line = f"Bu eksen sana {gift} verirken, zorlandığında {shadow} tarafı da açığa çıkabiliyor."
    return _cleanup_text(
        "Sen görünür olmaya sadece dikkat çekmek gibi bakmıyorsun. "
        f"MC'nin {sign_label} olduğu için dış dünyada daha {_sign_vibe(mc_sign)} bir etki bırakıyorsun. "
        "İnsanlar sende yalnızca sonucu değil, o sonucun nasıl taşındığını da fark ediyor. "
        "Yani senin için görünürlük biraz da duruş, üslup ve ağırlık meselesi. "
        f"{balance_line}"
    )


def _career_house_line(mc_house: int) -> str:
    if mc_house == 12:
        return "12. ev bunu önce perde arkasına, hazırlığa ve görünmeden olgunlaşan üretime taşıyor."
    if mc_house == 11:
        return "11. ev bunu ekip, network, çevre ve birlikte büyüyen hedefler tarafına taşıyor."
    if mc_house == 10:
        return "10. ev bunu doğrudan sahneye, görünürlüğe ve dışarıdaki duruşuna taşıyor."
    if mc_house == 6:
        return "6. ev bunu ustalığa, gündelik emeğe ve işin nasıl yürüdüğüne taşıyor."
    return f"{_house_phrase(mc_house)} bunu en çok {HOUSE_ARENA_TR.get(mc_house, 'kariyer akışı')} tarafına taşıyor."


def _career_engine_block(*, mc_ruler: str, mc_ruler_sign: str, mc_house: int) -> str:
    ruler_label = _planet_label(mc_ruler)
    placement = _planet_placement_phrase(
        planet_label=ruler_label,
        sign=mc_ruler_sign,
        house=mc_house,
        sign_first=False,
    )
    balance = _CAREER_RULER_SIGN_BALANCE_TR.get(mc_ruler_sign) or {}
    gift = str(balance.get("gift") or "").strip()
    shadow = str(balance.get("shadow") or "").strip()
    balance_line = ""
    if gift and shadow:
        balance_line = f"İyi çalıştığında bu ton sende {gift} tarafını büyütüyor; zorlandığında ise {shadow} tarafı da açığa çıkabiliyor."
    return _cleanup_text(
        "Ama işin mutfağında seni çalıştıran şey biraz daha başka. "
        f"Yöneticin {placement} olduğu için üretimin önce kendi içinde şekil almak istiyor. "
        f"{_career_house_line(mc_house)} "
        f"{_MIND_SIGN_DRIVE_TR.get(mc_ruler_sign) or 'Bu da çalışma biçimine kendine özgü bir ton ekliyor.'} "
        "O yüzden sen çoğu zaman yalnızca ne yaptığınla değil, onu hangi ritimde kurduğunla fark yaratıyorsun. "
        f"{balance_line}"
    )


def _career_tension_block(*, mc_ruler: str, mc_house: int) -> str:
    if mc_house == 12:
        return _cleanup_text(
            "Buradaki asıl gerilim şu olabilir: bir yanın hazır olmadan görünmek istemiyor, diğer yanın ise içerde olgunlaşan şeyi artık dışarı taşımak istiyor. "
            "Bu yüzden bazen çok uzun hazırlık yapıyor, bazen de bir anda karar verip ortaya çıkıyorsun. "
            "İnsanlar senden sonucu gördüğünde her şey kolay olmuş gibi sanabilir ama içeride uzun bir toplama süreci yaşanmış oluyor. "
            "Senin görünürlüğün çoğu zaman sessiz ama yoğun bir hazırlığın içinden geliyor."
        )
    if mc_house == 11:
        return _cleanup_text(
            "Buradaki asıl hikâye şu: sen tek başına parlamaktan çok, doğru bağlamın içinde etkini büyütüyorsun. "
            "Bir yanın kendi işini kendi ritminde kurmak istiyor, diğer yanın ise doğru insanlarla birleştiğinde gücünün arttığını biliyor. "
            "Bu yüzden görünürlük sende biraz da kimlerle yan yana geldiğinle şekilleniyor. "
            "Doğru çevrede çok daha rahat açılıyor, yanlış çevrede ise hızla geri çekilebiliyorsun."
        )
    return _cleanup_text(
        "Buradaki asıl gerilim şu: bir yanın ürettiğin şeyi kusursuzlaştırmak istiyor, diğer yanın ise onun artık dolaşıma girmesi gerektiğini biliyor. "
        "Bu yüzden bazen fazla bekleyebilir, bazen de bir anda karar verip görünür olabilirsin. "
        "İnsanlar senin sonucunu gördüğünde bunun arkasındaki iç hazırlığı ya da standardı her zaman fark etmeyebilir. "
        "Ama senin için mesele sadece görünmek değil; doğru şeyle görünmek."
    )


def _career_origin_block(*, mc_house: int) -> str:
    if mc_house == 12:
        return _cleanup_text(
            "Bu yerleşim çoğu zaman seni perde arkasında güç toplamaya alıştırmış olabilir. "
            "Bir şeyi tam hazır hissetmeden ortaya koymak istememen biraz da buradan geliyor. "
            "Belki de erken yaşta görünür olmadan önce kendi kendine yetmeyi, kendi kaliteni kendi içinde kurmayı öğrendin. "
            "Bu güzel bir derinlik veriyor ama bazen seni gereğinden uzun süre içeride tutabiliyor."
        )
    if mc_house == 11:
        return _cleanup_text(
            "Bu yerleşim seni erken yaşta çevre, ekip, arkadaşlıklar ve ortak hedefler üzerinden güç toplamaya itmiş olabilir. "
            "Bir şeyi yalnızca iyi yapman değil, doğru insanlarla doğru yere bağlaman da önemli hale gelmiş olabilir. "
            "Bu seni network kuran, insanları bir araya getiren ve ortamın yönünü okuyan birine çevirebilir. "
            "Ama bir yandan da yanlış çevrelerde enerjini gereksiz yere harcama riski taşıyorsun."
        )
    if mc_house == 10:
        return _cleanup_text(
            "Bu yerleşim erken yaşta görünür olma, performans gösterme ya da bir şeyin sorumluluğunu üstlenme hissi verebilir. "
            "İnsanların seni sonuçla ölçmesi sana yabancı gelmeyebilir. "
            "Bu seni güçlü, odaklı ve sahne anında toparlanan biri yapar. "
            "Ama bir yandan da her şeyin senin omzunda olduğu hissi yorucu olabilir."
        )
    return _cleanup_text(
        f"Bu yerleşim seni kariyer ve görünürlük tarafında en çok {_house_phrase(mc_house)} alanında büyütüyor. "
        "Yani dışarıdaki hedeflerin, hayatının o bölümündeki deneyimlerle birlikte şekilleniyor. "
        "Sen yalnızca çalışmıyor; aynı zamanda neyi temsil ettiğini de kuruyorsun. "
        "Bu da görünürlüğünü daha kişisel ve daha anlamlı kılıyor."
    )


def _career_strength_block(*, mc_ruler: str, mc_ruler_sign: str) -> str:
    return _cleanup_text(
        "Senin en güçlü taraflarından biri şu: görünür olduğunda sadece dikkat çekmiyorsun, iz bırakıyorsun. "
        f"{_planet_label(mc_ruler)}'ün {_sign_locative(mc_ruler_sign) or _sign_label(mc_ruler_sign)} olması üretimine daha {_sign_tone(mc_ruler_sign)} bir ton veriyor. "
        "Bu yüzden insanlar sende yalnızca yetkinlik değil, aynı zamanda karakter de hissediyor. "
        "Doğru çalıştığında etkini hızlı değil, kalıcı kuruyorsun."
    )


def _career_growth_block() -> str:
    return _cleanup_text(
        "Senin burada öğrenmeye geldiğin şey şu olabilir: görünür olmak için her şeyi tamamen bitirmiş olman gerekmiyor. "
        "Kalite duygun çok değerli ama bazen seni gereğinden uzun hazırlıkta tutabiliyor. "
        "Hayat sana hem standardını koruyup hem de kendini dolaşıma sokmayı öğretiyor. "
        "İşte o zaman yalnızca iyi üreten değil, etkisini gerçekten yayabilen birine dönüşüyorsun."
    )


def _career_caption_block(*, mc_sign: str, mc_ruler: str, mc_ruler_sign: str, mc_house: int) -> str:
    placement = _planet_placement_phrase(
        planet_label=_planet_label(mc_ruler),
        sign=mc_ruler_sign,
        house=mc_house,
        sign_first=False,
    )
    return _cleanup_text(
        f"Sen dış dünyada daha {_sign_vibe(mc_sign)} bir etki bırakıyorsun ama işin gerçek ritmi içeride daha {_sign_tone(mc_ruler_sign)} çalışıyor. "
        f"{placement} olduğu için görünürlük sende yalnızca sahne değil, hazırlık ve doğru zaman meselesi de oluyor. "
        "Asıl gücün burada: hem kaliteni koruyup hem de kendini fazla geride tutmadan ortaya koymayı öğreniyorsun. "
        "O zaman görünürlüğün daha doğal, daha güven veren ve daha kalıcı hale geliyor."
    )


def _career_detail_blocks(
    *,
    mc_sign: str,
    mc_ruler: str,
    mc_ruler_sign: str,
    mc_house: int,
    profile: Mapping[str, str] | None = None,
) -> List[str]:
    blocks = [
        _career_opening_block(mc_sign=mc_sign),
        _career_engine_block(
            mc_ruler=mc_ruler,
            mc_ruler_sign=mc_ruler_sign,
            mc_house=mc_house,
        ),
        _career_tension_block(mc_ruler=mc_ruler, mc_house=mc_house),
        _career_origin_block(mc_house=mc_house),
        _career_strength_block(mc_ruler=mc_ruler, mc_ruler_sign=mc_ruler_sign),
        _career_growth_block(),
        _career_caption_block(
            mc_sign=mc_sign,
            mc_ruler=mc_ruler,
            mc_ruler_sign=mc_ruler_sign,
            mc_house=mc_house,
        ),
    ]
    profile_map = profile or {}
    return [
        _merge_block_line(blocks[0], str(profile_map.get("opening") or "")),
        _merge_block_line(blocks[1], str(profile_map.get("engine") or "")),
        _merge_block_line(blocks[2], str(profile_map.get("tension") or "")),
        _merge_block_line(blocks[3], str(profile_map.get("origin") or "")),
        _merge_block_line(blocks[4], str(profile_map.get("strength") or "")),
        _merge_block_line(blocks[5], str(profile_map.get("growth") or "")),
        _merge_block_line(blocks[6], str(profile_map.get("caption") or "")),
    ]


def _core_mind_body(
    *,
    asc_sign: str,
    asc_ruler: str,
    asc_house: int,
    loop_signature: str,
) -> str:
    sign_label = _sign_label(asc_sign)
    ruler_label = _planet_label(asc_ruler)
    arena = HOUSE_ARENA_TR.get(asc_house, "günlük akış")
    loop_line = ""
    if loop_signature:
        loop_line = (
            " Karar, ifade ve hareketin birbirini tetiklemesi yüzünden bazen zihnin bir cümleyi "
            "söylemeden önce birkaç kez tartabiliyor."
        )
    if asc_house in {3, 6}:
        return _cleanup_text(
            f"Netlik sende kontrol değil güven meselesi; Yükselen {sign_label} belirsizliği uzatmayı sevmez "
            f"ve yöneticin {ruler_label}'ün {_house_phrase(asc_house)} vurgusu bunu en çok söz, ton ve karar "
            f"anlarında görünür kılar, bu yüzden bazen bir cümleyi kurmadan önce içinden ölçüp biçmen ya da "
            f"konuşma bittikten sonra ne demek istediğini zihninde yeniden toplaman fazla düşünmekten çok "
            f"netlik aradığını gösterir.{loop_line}"
        )
    if asc_house == 12:
        return _cleanup_text(
            f"Netlik sende kontrol değil güven meselesi; Yükselen {sign_label} dışarıda ölçülü dururken "
            f"yöneticin {ruler_label}'ün {_house_phrase(asc_house)} vurgusu kararlarını önce içeride olgunlaştırmana "
            f"neden olur, bu yüzden hızlı cevap vermek yerine içinden toparlayıp sonra konuşmak senin için "
            f"kaçınma değil kalite filtresidir."
        )
    if asc_house == 11:
        return _cleanup_text(
            f"Netlik sende yalnız kalınca değil, bağlam netleşince geliyor; Yükselen {sign_label} belirsizliği "
            f"uzatmayı sevmez ve yöneticin {ruler_label}'ün {_house_phrase(asc_house)} vurgusu rolünü en çok "
            f"ekip, çevre ve ortak hedef içinde görünür kılıyor, bu yüzden kiminle ve ne için ilerlediğini "
            f"bildiğinde zihnin de çok daha hızlı toparlanıyor."
        )
    return _cleanup_text(
        f"Netlik sende kontrol değil güven meselesi; Yükselen {sign_label} belirsizliği uzatmayı sevmez ve "
        f"yöneticin {ruler_label}'ün {_house_phrase(asc_house)} vurgusu bunu en çok {arena} alanında görünür "
        f"kılar, bu yüzden kararlarını içinden tartıp sağlam bir cümleye dönüştürdüğünde hem ritmin hem "
        f"duruşun aynı anda güçlenir."
    )


def _mind_section(
    *,
    seed: str,
    asc_sign: str,
    asc_ruler: str,
    asc_ruler_sign: str,
    asc_house: int,
    loop_signature: str,
    profile: Mapping[str, str] | None,
    family: str,
) -> Dict[str, Any]:
    micro = editorialize_micro(_pick_variant(_MIND_MICROS, seed + ":mind_micro"), family)
    sign_label = _sign_label(asc_sign)
    ruler_label = _planet_label(asc_ruler)
    ruler_sign_label = _sign_label(asc_ruler_sign)
    ruler_sign_locative = _sign_locative(asc_ruler_sign)
    arena = HOUSE_ARENA_TR.get(asc_house, "günlük akış")
    detail_blocks = _mind_detail_blocks(
        asc_sign=asc_sign,
        asc_ruler=asc_ruler,
        asc_ruler_sign=asc_ruler_sign,
        asc_house=asc_house,
        profile=profile,
    )
    tone_line = (
        f"{ruler_label}'ün {ruler_sign_locative} olması da burayı daha {_sign_tone(asc_ruler_sign)} bir tona çekiyor."
        if ruler_sign_locative
        else ""
    )
    body = (
        f"Yükselen {sign_label} sana dışarıda daha {_sign_vibe(asc_sign)} bir duruş veriyor; insanlar çoğu zaman "
        "sende önce kontrollü tarafı görüyor. "
        "Ama zihnin çoğu zaman o kadar sakin çalışmıyor; içeride karar, tepki ve ifade aynı anda hızlanan bir hat gibi ilerliyor. "
        f"Yükselen {sign_label} olup yöneticin {ruler_label} {_house_locative(asc_house)}"
        f"{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, bu hat en çok "
        f"{arena} tarafında belirginleşiyor{'; ' + tone_line if tone_line else '.'} "
        "Bu yüzden bazen tek bir cümleyi söylemeden önce uzun uzun tartıyor, bazen de tam tersine bir anda çok net ve "
        "keskin çıkabiliyorsun; iyi gününde bu sana isabetli bir ifade gücü verirken zor gününde zihnin tek bir "
        "cümle üzerinde gereğinden fazla yük taşıyabiliyor."
    )
    if asc_house == 12:
        body = (
            f"Yükselen {sign_label} sana dışarıda daha {_sign_vibe(asc_sign)} bir duruş veriyor; ama içeride olan şey "
            "çoğu zaman bundan daha hareketli. "
            "Senin zihnin önce içeride toparlıyor, sonra dışarı açılıyor; bu yüzden hemen cevap vermemek sende kaçınma "
            "değil, cümleyi ve duyguyu yerli yerine koyma ihtiyacı. "
            f"Yükselen {sign_label} olup yöneticin {ruler_label} {_house_locative(asc_house)}"
            f"{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, belirsizlik en çok "
            f"içeride büyüyor{'; ' + tone_line if tone_line else '.'} Asıl rahatlama, ne hissettiğini kelimeye "
            "dökebildiğin anda geliyor."
        )
    elif asc_house == 11:
        body = (
            f"Yükselen {sign_label} dışarıda daha {_sign_vibe(asc_sign)} bir izlenim bırakıyor; ama zihnin özellikle "
            "bağlam netleşince hızlanıyor. "
            "Bir grubun içinde yerin, yönün ve neden orada olduğun belli olduğunda cümlen de kararın da daha rahat akıyor. "
            f"Yükselen {sign_label} olup yöneticin {ruler_label} {_house_locative(asc_house)}"
            f"{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, belirsizlik en çok ekip, "
            f"çevre ve ortak hedef tarafında yük yaratıyor{'; ' + tone_line if tone_line else '.'} Kiminle ve ne için ilerlediğini bildiğinde hem zihnin "
            "hem ritmin rahatlıyor."
        )
    return {
        "id": "mind_system",
        "title": "Zihin–eylem–kontrol",
        "subtitle": _family_line(
            {
                "direct": "Ne yapacağını bildiğin an tempo kendiliğinden yükselir.",
                "observational": "İnsanlar sende önce kontrollü zihni, sonra hızlanan tempoyu görür.",
                "cinematic": "Cümle yerine oturduğu anda iç ritmin de hızlanır.",
                "intimate": "İçeride netleştiğin an dışarıdaki tempo da rahatlar.",
            },
            family,
            "Ne yapacağını bildiğin an tempo kendiliğinden yükselir.",
        ),
        "body": _cleanup_text(f"{body} {str((profile or {}).get('body') or '').strip()}"),
        "detail_blocks": detail_blocks,
        "micro": micro,
        "chips": [
            f"Yükselen {sign_label}",
            f"{ruler_label} {_house_phrase(asc_house)}",
            *( [ruler_sign_label] if ruler_sign_label else [] ),
        ],
        "legacy_id": "identity_mechanics",
    }


def _relationship_section(
    *,
    seed: str,
    dsc_sign: str,
    r7: str,
    r7_sign: str,
    r7_house: int,
    moon_house: int,
    profile: Mapping[str, str] | None,
    family: str,
) -> Dict[str, Any]:
    micro = editorialize_micro(_pick_variant(_REL_MICROS, seed + ":rel_micro"), family)
    sign_label = _sign_label(dsc_sign)
    ruler_label = _planet_label(r7)
    ruler_sign_label = _sign_label(r7_sign)
    ruler_sign_locative = _sign_locative(r7_sign)
    tone_line = (
        f"{ruler_label}'ın {ruler_sign_locative} olması da bu hattı daha {_sign_tone(r7_sign)} bir tona çekiyor."
        if ruler_sign_locative
        else ""
    )
    detail_blocks = _relationship_detail_blocks(
        dsc_sign=dsc_sign,
        r7=r7,
        r7_sign=r7_sign,
        r7_house=r7_house,
        profile=profile,
    )
    moon_ref = "Ay"
    body = (
        "Sen ilişkide yüzeysel bir sıcaklıktan çok, içine oturan bir güven arıyorsun. "
        "Bu yüzden bir bağın gidişi sende yalnızca söylenen şeyden değil, söylenmeyenlerden de etkileniyor. "
        f"7. evin {sign_label} olduğu ve yöneticisi {moon_ref if r7 == 'Moon' else ruler_label} "
        f"{_house_locative(r7_house)}{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, "
        f"yakınlık sende kolayca daha derin ve daha belirleyici bir yere oturabiliyor{'; ' + tone_line if tone_line else '.'} "
        "İyi gününde bu sana çok güçlü bir bağ sezgisi veriyor; zor gününde ise ya içine çekiliyor ya da duyguyu bir anda "
        "hep ya hiç çizgisine taşıyabiliyorsun."
    )
    if r7_house == 11:
        body = (
            "Sen ilişkide yalnızca sıcaklık değil, aynı tarafta olma hissi arıyorsun. "
            "Bu yüzden bağın hangi çevrede ve hangi ritimde büyüdüğü, duygunun kendisi kadar belirleyici oluyor. "
            f"7. evin {sign_label} olduğu ve yöneticisi {ruler_label} {_house_locative(r7_house)}"
            f"{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, güven en çok arkadaşlık, "
            f"ekip ve ortak hedef tarafında kuruluyor; bağ çoğu zaman önce sosyal zeminde rahatlayıp sonra derinleşiyor{'; ' + tone_line if tone_line else '.'} "
            "Rol netleştiğinde hem kalbin hem zihnin rahatlıyor."
        )
    elif r7_house == 3:
        body = (
            "Sen ilişkide yalnızca yakınlık değil, o yakınlığın konuşulabilir olmasını da istiyorsun. "
            "Bu yüzden yarım cümleler, belirsiz tonlar ve açıkta kalan meseleler sende gereğinden fazla yük yaratabiliyor. "
            f"7. evin {sign_label} olduğu ve yöneticisi {ruler_label} {_house_locative(r7_house)}"
            f"{' ve ' + ruler_sign_locative if ruler_sign_locative else ''} olduğu için, güven en çok söz, ton ve "
            f"mesaj trafiği üzerinden kuruluyor; bir bağın ritmi çoğu zaman nasıl konuştuğunuzla şekilleniyor{'; ' + tone_line if tone_line else '.'} "
            "Burada belirleyici olan büyük açıklamalar değil, doğru anda gelen temiz bir netlik cümlesi."
        )
    return {
        "id": "relationships",
        "title": "Duygusal derinlik" if r7_house == 8 else "İlişkiler ve yakınlık",
        "subtitle": _family_line(
            {
                "direct": "Güven geldiğinde bağ hızla derinleşir.",
                "observational": "İnsanlar sende sıcaklıktan önce güven eşiğini hisseder.",
                "cinematic": "Yakınlık burada hafif ilerlemez; bir anda derine çekilir.",
                "intimate": "Kalbin, güven olmadan yarım açılmaz.",
            },
            family,
            "Güven geldiğinde bağ hızla derinleşir.",
        ),
        "body": _cleanup_text(f"{body} {str((profile or {}).get('body') or '').strip()}"),
        "detail_blocks": detail_blocks,
        "micro": micro,
        "chips": [
            f"7. ev {sign_label}",
            f"{ruler_label} {_house_phrase(r7_house)}",
            *( [ruler_sign_label] if ruler_sign_label else [] ),
        ],
        "legacy_id": "relationships_depth",
    }


def _career_section(
    *,
    seed: str,
    mc_sign: str,
    mc_ruler: str,
    mc_ruler_sign: str,
    mc_house: int,
    profile: Mapping[str, str] | None,
    family: str,
) -> Dict[str, Any]:
    micro = editorialize_micro(_pick_variant(_CAREER_MICROS, seed + ":career_micro"), family)
    mc_sign_label = _sign_label(mc_sign)
    mc_ruler_label = _planet_label(mc_ruler)
    mc_ruler_sign_label = _sign_label(mc_ruler_sign)
    mc_ruler_sign_locative = _sign_locative(mc_ruler_sign)
    detail_blocks = _career_detail_blocks(
        mc_sign=mc_sign,
        mc_ruler=mc_ruler,
        mc_ruler_sign=mc_ruler_sign,
        mc_house=mc_house,
        profile=profile,
    )
    tone_line = (
        f"{mc_ruler_label}'ün {mc_ruler_sign_locative} olması da görünürlük hattını daha {_sign_tone(mc_ruler_sign)} çalıştırıyor."
        if mc_ruler_sign_locative
        else ""
    )
    body = (
        "Sen işte yalnızca iyi yapmak istemiyorsun; yaptığın şeyin yerine oturmasını ve içe sinmesini de istiyorsun. "
        "Bu yüzden hazırlık süreci sende işin kendisi kadar önemli çalışıyor; acele görünür olmak çoğu zaman sana göre değil. "
        f"MC'nin {mc_sign_label} olması sana denge, ilişki yönetimi ve sunum tarafında avantaj veriyor; yöneticin "
        f"{mc_ruler_label} {_house_locative(mc_house)}{' ve ' + mc_ruler_sign_locative if mc_ruler_sign_locative else ''} "
        f"olduğu için üretiminin bir kısmı önce içeride olgunlaşmak istiyor{'; ' + tone_line if tone_line else '.'} "
        "İyi gününde bu sana rafine, güven veren ve etkisi kolay dağılmayan bir görünürlük veriyor."
    )
    if mc_house == 11:
        body = (
            "Sen işte yalnızca iyi yapmak istemiyorsun; doğru insanları ve doğru bağlamı birbirine bağlamak da senin gücün. "
            "Bu yüzden görünürlük burada tek başına parlamaktan çok doğru ağ içinde büyüyor. "
            f"MC'nin {mc_sign_label} olması sana denge ve ilişki yönetimi getirirken, yöneticin {mc_ruler_label} "
            f"{_house_locative(mc_house)}{' ve ' + mc_ruler_sign_locative if mc_ruler_sign_locative else ''} olduğu için "
            f"işin ekip, çevre ve ortak hedef üzerinden hızlanıyor{'; ' + tone_line if tone_line else '.'} "
            "Doğru çevre kurulduğunda performansın da görünürlüğün de daha rahat akıyor."
        )
    elif mc_house == 10:
        body = (
            "Sen işte yalnızca iyi yapmak istemiyorsun; doğru zamanda görünür olup ürettiğini dışarı taşıyabilmek de senin hikâyenin parçası. "
            "Bu yüzden hazırlık kadar sahne anı da belirleyici oluyor. "
            f"MC'nin {mc_sign_label} olması sana denge ve sunum becerisi verirken, yöneticin {mc_ruler_label} "
            f"{_house_locative(mc_house)}{' ve ' + mc_ruler_sign_locative if mc_ruler_sign_locative else ''} olduğu için "
            f"üretmek ve bunu dolaşıma sokmak aynı zincirin iki halkası gibi çalışıyor{'; ' + tone_line if tone_line else '.'} "
            "Burada asıl fark, her şeyi kusursuzlaştırmayı beklemeden görünür kılabildiğinde ortaya çıkıyor."
        )
    return {
        "id": "career_visibility",
        "title": "Görünür olma ritmin",
        "subtitle": _family_line(
            {
                "direct": "Hazır hissettiğin an görünürlüğün de ağırlık kazanır.",
                "observational": "İnsanlar önce kalite çıtasını, sonra etkini görür.",
                "cinematic": "Perde açılmadan önce içeride uzun bir son prova olur.",
                "intimate": "İçinde yerine oturmayan şeyi dışarı taşımak istemezsin.",
            },
            family,
            "Hazır hissettiğin an görünürlüğün de ağırlık kazanır.",
        ),
        "body": _cleanup_text(f"{body} {str((profile or {}).get('body') or '').strip()}"),
        "detail_blocks": detail_blocks,
        "micro": micro,
        "chips": [
            f"MC {mc_sign_label}",
            f"{mc_ruler_label} {_house_phrase(mc_house)}",
            *( [mc_ruler_sign_label] if mc_ruler_sign_label else [] ),
        ],
        "legacy_id": "career_visibility",
    }


def build_sections_v2(
    *,
    chart_data: Mapping[str, Any],
    planets: List[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
    master_selector: Mapping[str, Any] | None = None,
    migration_mode: str = "legacy",
) -> List[Dict[str, Any]]:
    planets_map = _planet_positions(planets)
    aspect_index = natal_graph.get("aspect_index") if isinstance(natal_graph.get("aspect_index"), Mapping) else {}
    angles = chart_data.get("angles")
    asc_sign = ""
    mc_sign = ""
    if isinstance(angles, Mapping):
        asc_sign = str(angles.get("ascendant_sign") or "").strip()
        mc_sign = str(angles.get("midheaven_sign") or "").strip()
    base_seed = _seed_base(chart_data, asc_sign, mc_sign)

    house1 = _house_ruler(natal_graph, 1)
    asc_ruler = str(house1.get("primary_ruler") or "").strip() or TRADITIONAL_RULERS.get(asc_sign.lower(), "")
    asc_ruler_pos = _planet_pos(asc_ruler, planets_map)
    asc_house = _to_house(asc_ruler_pos.get("house"), 1)
    asc_ruler_sign = str(asc_ruler_pos.get("sign") or "").strip()

    house7 = _house_ruler(natal_graph, 7)
    dsc_sign = str(house7.get("cusp_sign") or "").strip()
    r7 = str(house7.get("primary_ruler") or "").strip() or TRADITIONAL_RULERS.get(dsc_sign.lower(), "")
    r7_pos = _planet_pos(r7, planets_map)
    r7_house = _to_house(r7_pos.get("house"), 7)
    r7_sign = str(r7_pos.get("sign") or "").strip()
    moon_house = _to_house(_planet_pos("Moon", planets_map).get("house"), 8)

    house10 = _house_ruler(natal_graph, 10)
    mc_ruler = str(house10.get("primary_ruler") or "").strip() or TRADITIONAL_RULERS.get(mc_sign.lower(), "")
    mc_ruler_pos = _planet_pos(mc_ruler, planets_map)
    mc_house = _to_house(mc_ruler_pos.get("house"), 10)
    mc_ruler_sign = str(mc_ruler_pos.get("sign") or "").strip()

    loops = natal_graph.get("dominant_loops") if isinstance(natal_graph.get("dominant_loops"), list) else []
    loop_signature = str(((loops or [{}])[0] or {}).get("signature") or "").strip()
    mind_profile = _mind_personalization_profile(
        asc_ruler=asc_ruler,
        planets_map=planets_map,
        aspect_index=aspect_index,
        loops=loops,
    )
    relationship_profile = _relationship_personalization_profile(
        r7=r7,
        planets_map=planets_map,
        aspect_index=aspect_index,
    )
    career_profile = _career_personalization_profile(
        mc_ruler=mc_ruler,
        mc_house=mc_house,
        planets_map=planets_map,
        aspect_index=aspect_index,
    )
    used_families: list[str] = []
    mind_family = select_rhythm_family(base_seed, "sections_v2", "mind_system", used_families)
    used_families.append(mind_family)
    rel_family = select_rhythm_family(base_seed, "sections_v2", "relationships", used_families)
    used_families.append(rel_family)
    career_family = select_rhythm_family(base_seed, "sections_v2", "career_visibility", used_families)

    sections = [
        _mind_section(
            seed=base_seed,
            asc_sign=asc_sign,
            asc_ruler=asc_ruler,
            asc_ruler_sign=asc_ruler_sign,
            asc_house=asc_house,
            loop_signature=loop_signature,
            profile=mind_profile,
            family=mind_family,
        ),
        _relationship_section(
            seed=base_seed,
            dsc_sign=dsc_sign,
            r7=r7,
            r7_sign=r7_sign,
            r7_house=r7_house,
            moon_house=moon_house,
            profile=relationship_profile,
            family=rel_family,
        ),
        _career_section(
            seed=base_seed,
            mc_sign=mc_sign,
            mc_ruler=mc_ruler,
            mc_ruler_sign=mc_ruler_sign,
            mc_house=mc_house,
            profile=career_profile,
            family=career_family,
        ),
    ]
    if migration_mode == "active":
        return _apply_spine_to_sections(
            sections,
            master_selector=master_selector,
        )
    return sections


def build_supporting_threads(
    *,
    chart_data: Mapping[str, Any],
    planets: List[Mapping[str, Any]],
    natal_graph: Mapping[str, Any],
    max_threads: int = 4,
    master_selector: Mapping[str, Any] | None = None,
    migration_mode: str = "legacy",
    sections: Sequence[Mapping[str, Any]] | None = None,
) -> List[Dict[str, Any]]:
    sections_payload = (
        list(sections)
        if isinstance(sections, Sequence)
        else build_sections_v2(
            chart_data=chart_data,
            planets=planets,
            natal_graph=natal_graph,
            master_selector=master_selector,
            migration_mode=migration_mode,
        )
    )
    threads: List[Dict[str, Any]] = []
    for section in sections_payload[: min(max_threads, 3)]:
        body = str(section.get("body") or "").strip()
        micro = str(section.get("micro") or "").strip()
        threads.append(
            {
                "id": section.get("legacy_id") or section.get("id"),
                "title": section.get("title", ""),
                "one_liner": section.get("subtitle", ""),
                "paragraph": _build_thread_paragraph(str(section.get("subtitle") or ""), body, micro),
                "body": body,
                "detail_blocks": list(section.get("detail_blocks") or []),
                "micro": micro,
                "chips": list(section.get("chips") or []),
                "section_id": section.get("id"),
                "evidence": [],
            }
        )
    return threads
