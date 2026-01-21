OUTER = {"Pluto", "Neptune", "Uranus"}
SOCIAL = {"Saturn", "Jupiter"}
PERSONAL = {"Sun", "Moon", "Mercury", "Venus", "Mars"}

SOFT_THEME_LINES = {
    "identity": "Bu destek kimlik ve duruş tarafında daha net bir akış sağlayabilir.",
    "relationships": "Bağ kurma ve iletişim daha yumuşak ilerleyebilir.",
    "career": "Kariyer yönü ve görünürlük tarafında düzenli destek oluşabilir.",
    "home": "Ev ve iç güven alanında istikrar hissi artabilir.",
    "inner": "İç dünyada dinginlik ve içe çekilme ihtiyacı dengelenebilir.",
}


def body_class(body: str) -> str:
    if body in OUTER:
        return "outer"
    if body in SOCIAL:
        return "social"
    if body in PERSONAL:
        return "personal"
    return "other"


def build_mechanism_sentence(event: dict) -> str:
    polarity = event.get("polarity", "neutral")
    phase = event.get("phase", "applying")
    transit_body = event.get("transit_body")
    cls = body_class(transit_body)
    theme = event.get("primary_theme")

    if transit_body == "Neptune" and polarity == "hard":
        if phase == "applying":
            return (
                "Netlik azalırken zihin boşlukları doldurmak isteyebilir; varsayım yerine somut veri toplamak iyi gelir."
            )
        return "Belirsizlik çözüldükçe, sınırlar ve beklentiler daha gerçekçi hale gelir."

    if transit_body == "Uranus" and polarity == "hard":
        return "Ani değişim dürtüsü artabilir; kontrolü zorlamak yerine esnek kalmak daha iyi sonuç verir."

    if transit_body == "Saturn" and polarity == "hard":
        return "Baskı arttığında tempo ve sınırlar test olur; ritim kurduğunda etki dayanıklılığa döner."

    if transit_body == "Pluto" and polarity == "hard":
        return "Kontrol edilemeyen bir dönüşüm tetiklenir; eski stratejiler çalışmaz hale gelir."

    if cls == "outer" and polarity == "hard":
        return "Eski yöntemler çalışmadığında sistem kendini güncellemek ister; küçük ama net kararlar süreci sağlıklı taşır."

    if polarity == "hard" and phase == "applying":
        return "Baskı artarken acele karar veya gereksiz sertleşme eğilimi doğabilir; yavaşlatmak denge sağlar."

    if polarity == "hard":
        return "Bu etki önce gerer, sonra doğru sınır kurulduğunda güçlenmeye dönüşür."

    if polarity == "soft" and phase == "applying":
        return "Akış açıldığında doğru kanala girerse hızlı ilerleme sağlayabilir."

    if polarity == "soft":
        if theme in SOFT_THEME_LINES:
            return SOFT_THEME_LINES[theme]
        return "Küçük adımlar büyük sonuç üretir; fırsatı somutlaştırmak etkili olur."

    return "Bu etki farkındalıkla yönetildiğinde nötr bir ayar gibi çalışır."
