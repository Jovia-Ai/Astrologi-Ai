from __future__ import annotations

from typing import Dict, Optional


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
    "North Node": "Kuzey Ay Düğümü",
}

SIGN_TR = {
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

ASPECT_TR = {
    "conjunction": "kavuşumda",
    "sextile": "sekstilde",
    "square": "karede",
    "trine": "üçgende",
    "opposition": "karşıtta",
}

ASPECT_NAME_TR = {
    "conjunction": "kavuşumu",
    "sextile": "sekstili",
    "square": "karesi",
    "trine": "üçgeni",
    "opposition": "karşıtlığı",
}

BODY_THEMES = {
    "Sun": "görünürlük, yön ve merkez duygusu",
    "Moon": "duygusal ritim, ihtiyaçlar ve güven hissi",
    "Mercury": "iletişim, planlar, trafik ve teknik akış",
    "Venus": "ilişkiler, zevkler, para ve yakınlık dengesi",
    "Mars": "dürtü, hareket, çatışma ve hız",
    "Jupiter": "büyüme, fırsatlar, inanç ve genişleme",
    "Saturn": "sınırlar, sorumluluklar ve yapı kurma",
    "Uranus": "ani değişimler, özgürleşme ve sürpriz kırılmalar",
    "Neptune": "belirsizlik, sezgi, çözülme ve ilham",
    "Pluto": "güç, kriz, dönüşüm ve köklü yeniden yapılanma",
}


def _body(body: Optional[str]) -> str:
    return BODY_TR.get(body or "", body or "Gökyüzü")


def _sign(sign: Optional[str]) -> str:
    return SIGN_TR.get(sign or "", sign or "")


def _theme(body: Optional[str]) -> str:
    return BODY_THEMES.get(body or "", "kolektif atmosfer")


def build_event_copy(
    *,
    event_type: str,
    primary_body: Optional[str],
    secondary_body: Optional[str] = None,
    sign: Optional[str] = None,
    aspect: Optional[str] = None,
    eclipse_kind: Optional[str] = None,
) -> Dict[str, str | None]:
    body_a = _body(primary_body)
    body_b = _body(secondary_body)
    sign_tr = _sign(sign)
    theme_a = _theme(primary_body)
    aspect_state = ASPECT_TR.get(aspect or "", "temasta")
    aspect_name = ASPECT_NAME_TR.get(aspect or "", "teması")

    if event_type == "retrograde_start":
        return {
            "title_tr": f"{body_a} retrosu başlıyor",
            "short_title_tr": f"{body_a} retro",
            "summary_tr": f"{body_a} yavaşlayıp geriye dönerken {theme_a} alanlarında eski başlıklar yeniden açılabilir.",
            "general_meaning_tr": f"Bu gökyüzü olayı yeni hız kurmaktan çok revizyonu, gecikmiş konuşmaları ve yarım kalan işleri görünür kılar. Kolektif akışta 'önce dön, bak, düzelt' ihtiyacı artar.",
            "what_it_can_feel_like_tr": "Aynı konu tekrar tekrar masaya geliyor gibi hissedilebilir. Kararlar hemen netleşmeyebilir; zihin daha çok eksik parçayı toplamak isteyebilir.",
            "what_to_watch_tr": "Acele imza, dağınık plan ve varsayımla ilerleme daha fazla hata çıkarabilir. Eski meseleleri kapattığını sanarken yeniden gündeme gelmesine şaşırmamak gerekir.",
            "how_to_work_with_it_tr": "Takvim, mesaj, evrak ve teknik akışları sadeleştirmek en verimli kullanım olur. Yeni başlangıçtan önce düzeltme ve temizlik yapmak daha güçlü sonuç verir.",
            "who_feels_it_stronger_tr": f"Özellikle haritasında {body_a} ve değişken burçlar belirgin olanlar bu ritmi daha net fark edebilir.",
        }

    if event_type == "retrograde_end":
        return {
            "title_tr": f"{body_a} retrodan çıkıyor",
            "short_title_tr": f"{body_a} direkt",
            "summary_tr": f"{body_a} yeniden ileri harekete geçerken {theme_a} alanlarında tıkanan akış çözülmeye başlayabilir.",
            "general_meaning_tr": "Bu moment kolektif olarak netlik, toparlanma ve yeniden ilerleme isteğini yükseltir. Geri dönülen başlıklar artık karar ve uygulama aşamasına geçebilir.",
            "what_it_can_feel_like_tr": "Uzun süredir ağır ilerleyen konularda ferahlama hissi gelebilir. Yine de hız hemen tam açılmayabilir; ilk günler ayar dönemi gibi çalışır.",
            "what_to_watch_tr": "Retro bitti diye tüm pürüzlerin anında kapanacağını varsaymamak gerekir. Eksik kalan düzeltmeleri atlamak aynı sorunu yeniden üretebilir.",
            "how_to_work_with_it_tr": "Revize edilen planı adım adım devreye almak iyi sonuç verir. İletişimde ve iş akışında net öncelik listesi kurmak momentum kazandırır.",
            "who_feels_it_stronger_tr": f"Özellikle haritasında {body_a} güçlü çalışanlar ve bu gezegenin natal açılarını taşıyanlar açılmayı daha hızlı hissedebilir.",
        }

    if event_type == "ingress":
        return {
            "title_tr": f"{body_a} {sign_tr} burcuna geçiyor",
            "short_title_tr": f"{body_a} {sign_tr}'ta",
            "summary_tr": f"{body_a} {sign_tr} alanına geçerken kolektif atmosferin tonu değişiyor; {theme_a} yeni bir üslupla çalışmaya başlıyor.",
            "general_meaning_tr": "Burç geçişleri uzun bir dönemin ana vurgusunu değiştirir. Aynı konu artık başka bir tarz, başka bir öncelik ve başka bir tepki biçimiyle yaşanır.",
            "what_it_can_feel_like_tr": f"Havadaki dil ve tepki biçimi farklılaşabilir. {body_a} konularında yeni bir ritim kurma ihtiyacı belirginleşir.",
            "what_to_watch_tr": "Eski tempoyu yeni döneme taşımaya çalışmak sürtünme yaratabilir. Yeni tonun ne istediğini anlamadan acele sonuç aramak verimi düşürür.",
            "how_to_work_with_it_tr": "Yeni dönemin temasına uyum sağlayan küçük ayarlar yapmak en doğru başlangıç olur. Önce gözlem, sonra hız mantığı burada daha iyi çalışır.",
            "who_feels_it_stronger_tr": f"Özellikle haritasında {sign_tr} ve {body_a} bağlantıları güçlü olanlar geçişin yön değişimini daha görünür yaşayabilir.",
        }

    if event_type == "lunation_new_moon":
        return {
            "title_tr": f"{sign_tr} Yeniayı",
            "short_title_tr": f"{sign_tr} Yeniayı",
            "summary_tr": f"{sign_tr} yeniayı kolektif alanda yeni niyet, yeni başlangıç ve taze odak ihtiyacını artırır.",
            "general_meaning_tr": "Yeniaylar bir döngünün tohum anıdır. Hangi konuda sayfa açılacağı, önümüzdeki iki haftada neyin büyüyeceği ve gündemin hangi başlığa kayacağı burada belli olur.",
            "what_it_can_feel_like_tr": "İçten içe bir başlangıç dürtüsü gelebilir ama her şey henüz tam görünür olmayabilir. Sessiz hazırlık ve niyet kurma hali öne çıkabilir.",
            "what_to_watch_tr": "Belirsiz zeminde büyük beklenti kurmak hayal kırıklığı yaratabilir. Henüz filiz aşamasındaki konuyu erken zorlamak yerine alan açmak daha sağlıklıdır.",
            "how_to_work_with_it_tr": "Niyet, sade plan ve temiz başlangıçlar desteklenir. Küçük ama net bir adım, dağınık büyük kararlardan daha faydalı olur.",
            "who_feels_it_stronger_tr": f"Özellikle haritasında {sign_tr} vurgusu olanlar ve bu derecelere yakın gezegen taşıyanlar bu yeniayı daha belirgin hissedebilir.",
        }

    if event_type == "lunation_full_moon":
        return {
            "title_tr": f"{sign_tr} Dolunayı",
            "short_title_tr": f"{sign_tr} Dolunayı",
            "summary_tr": f"{sign_tr} dolunayı bazı konuları görünür, duygusal ve sonuç odaklı hale getirir; birikmiş gerilim artık saklanmak istemez.",
            "general_meaning_tr": "Dolunaylar farkındalık ve sonuç anlarıdır. Bir süredir büyüyen başlıkların ne durumda olduğu, neyin tamamlandığı ve neyin taşınamadığı daha açık görünür.",
            "what_it_can_feel_like_tr": "Duygular daha hızlı yükselebilir. Karşıt ihtiyaçlar aynı anda görünür olduğu için 'şimdi karar ver' baskısı artabilir.",
            "what_to_watch_tr": "Anlık duygusal yükselişi kalıcı gerçeklik sanmamak gerekir. Tepkiyle karar almak yerine görünür olan veriyi sakin biçimde toplamak daha güvenlidir.",
            "how_to_work_with_it_tr": "Tamamlanması gerekeni tamamlamak, gereksiz yükü bırakmak ve ilişkilerde açık konuşmak bu dönemi verimli kullanır. Temiz bir kapanış çoğu zaman yeni kapı açar.",
            "who_feels_it_stronger_tr": f"Özellikle haritasında {sign_tr} ekseni çalışanlar ve bu derecelerde kişisel gezegenleri olanlar dolunay temasını daha yoğun yaşayabilir.",
        }

    if event_type == "eclipse":
        eclipse_label = eclipse_kind or "Tutulma"
        return {
            "title_tr": f"{sign_tr} {eclipse_label}",
            "short_title_tr": f"{sign_tr} {eclipse_label}",
            "summary_tr": f"{sign_tr} hattındaki tutulma kolektif gündemi hızla yön değiştirebilen, kadersel hissedilen bir döneme taşıyabilir.",
            "general_meaning_tr": "Tutulmalar normal lunasyonlardan daha güçlü eşik anlarıdır. Görmezden gelinen konular hızla belirginleşebilir ve kolektif atmosfer daha yüksek sesle yön değiştirebilir.",
            "what_it_can_feel_like_tr": "Hızlı gelişmeler, ani fark edişler ve büyük resimde dönüm noktası hissi öne çıkabilir. Bazı süreçler kontrol etmekten çok cevap vermeyi gerektirebilir.",
            "what_to_watch_tr": "Her ani gelişmeyi sonsuz ve kesin sanmak doğru olmaz. Yüksek duygusal yoğunlukta abartılı yorum ve keskin kararlar daha sonra revizyon isteyebilir.",
            "how_to_work_with_it_tr": "Gündeme gelen mesajı not etmek, acele kader anlatısı kurmadan gelişmeleri izlemek ve temel zemini korumak en sağlıklı kullanım olur. Esneklik burada güçtür.",
            "who_feels_it_stronger_tr": f"Özellikle haritasında {sign_tr} dereceleri tetiklenenler, tutulma hattında kişisel gezegenleri olanlar ve aksları çalışanlar bu dönemi daha güçlü hissedebilir.",
        }

    return {
        "title_tr": f"{body_a} {aspect_name} {body_b}",
        "short_title_tr": f"{body_a}-{body_b} {aspect_name}",
        "summary_tr": f"{body_a} ile {body_b} arasındaki {aspect_name}, kolektif atmosferde {theme_a} ile {_theme(secondary_body)} başlıklarını aynı anda hareketlendirebilir.",
        "general_meaning_tr": f"Bu açı gökyüzünde iki farklı ihtiyacın birbirine cevap verdiği bir moment yaratır. Özellikle {body_a.lower()} ve {body_b.lower()} temaları aynı masada konuşulmaya başlar.",
        "what_it_can_feel_like_tr": f"{body_a} tarafı ile {body_b} tarafı arasında hız farkı ya da beklenti farkı hissedilebilir. Gündem biraz daha tartışmalı, hareketli ya da dikkat çekici olabilir.",
        "what_to_watch_tr": "Tek bir başlığa kilitlenip diğer ihtiyacı yok saymak gerilim yaratabilir. Bu tip açıları iyi kullanmak için çatışma kadar fırsat tarafını da görmek gerekir.",
        "how_to_work_with_it_tr": f"İki temayı rakip gibi değil, birlikte okunması gereken sinyal gibi ele almak faydalıdır. Bugünlerde 'hangi başlık öne çıkıyor?' kadar 'hangi denge kuruluyor?' sorusu da önemlidir.",
        "who_feels_it_stronger_tr": f"Özellikle haritasında {body_a} ve {body_b} arasında yakın açıları olanlar ya da bu gezegenlerin çalıştığı burçlar vurgulu olanlar bu {aspect_state} daha net hissedebilir.",
    }
