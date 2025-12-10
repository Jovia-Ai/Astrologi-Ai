"""Combined insight builder for natal interpretation output."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping


def build_combined_insights(meta_info: Mapping[str, Any], interpretation: Mapping[str, List[str]]) -> List[str]:
    """Synthesize higher-level interpretations from rule outputs and meta data."""

    insights: List[str] = []
    planet_signs: Mapping[str, str] = meta_info.get("planet_signs", {})
    planet_houses: Mapping[str, int] = meta_info.get("planet_houses", {})
    stelliums: Mapping[int, int] = meta_info.get("stelliums", {})
    element_counts: Mapping[str, int] = meta_info.get("element_counts", {})
    modality_counts: Mapping[str, int] = meta_info.get("modality_counts", {})

    sun_sign = planet_signs.get("Sun")
    moon_sign = planet_signs.get("Moon")
    if sun_sign and moon_sign and sun_sign == moon_sign:
        insights.append(
            f"Güneş'in ve Ay'ın {sun_sign} burcunda birleşmesi kimliğinle duygularının aynı titreşimden beslendiğini, içeride ne hissediyorsan dışarıda onu yansıttığını gösteriyor."
        )

    asc_sign = planet_signs.get("Ascendant")
    if sun_sign and asc_sign and sun_sign == asc_sign:
        insights.append(
            f"Güneş ile yükselenin aynı burçta olması, dışarı sunduğun imaj ile içsel benliğin arasında güçlü bir köprü kuruyor; bu da seni tanıyanların seni hızlıca çözmesini sağlıyor."
        )

    for house, count in sorted(stelliums.items()):
        insights.append(
            f"{house}. evdeki {count} gezegenlik yoğunluk, hayatının bu alanında tekrar eden dersler ve sürekli derinleşen bir farkındalık olduğunu anlatıyor."
        )

    dominant_element = _find_dominant(element_counts)
    if dominant_element:
        insights.append(
            f"Element dağılımında {dominant_element} vurgusu öne çıkıyor; kararlarını verirken doğal olarak bu elementin niteliklerine yaslanıyorsun."
        )

    dominant_modality = _find_dominant(modality_counts)
    if dominant_modality:
        insights.append(
            f"Modalite tarafında {dominant_modality} etkisi baskın; hayatı bu ritimde kurduğunda daha dengede hissediyorsun."
        )

    nodes = planet_signs.get("North Node")
    if nodes:
        insights.append(
            f"Kuzey Ay Düğümü'nün {nodes} burcunda olması, ruhsal evrimini bu burcun ilişkisel ve davranışsal dersleri üzerinden tamamlamaya çağırıyor."
        )

    lilith_sign = planet_signs.get("Lilith")
    if lilith_sign:
        insights.append(
            f"Lilith'in {lilith_sign} burcunda olması, gölgede tuttuğun cesaretini ne zaman sahiplenirsen yaratıcılığının da o kadar hızla açıldığını hatırlatıyor."
        )

    # Interpretation category emphasis
    category_counts = {section: len(entries or []) for section, entries in interpretation.items()}
    strong_sections = [section for section, count in category_counts.items() if count >= 3]
    if strong_sections:
        joined = ", ".join(strong_sections)
        insights.append(
            f"{joined} temalarından gelen tekrar eden mesajlar, bu dönem özellikle bu alanları beslediğinde tüm haritanın dengeleneceğini gösteriyor."
        )

    if not insights:
        insights.append("Haritan genel olarak dengeli görünse de, sezgilerini dinleyip güçlü olduğunu bildiğin alanları daha bilinçli kurguladığında etkini artırırsın.")

    return insights[:6]


def _find_dominant(counter: Mapping[str, int]) -> str | None:
    top_item = None
    top_value = 0
    for key, value in counter.items():
        if value > top_value:
            top_item = key
            top_value = value
    if top_value >= 4:
        return top_item
    return None
