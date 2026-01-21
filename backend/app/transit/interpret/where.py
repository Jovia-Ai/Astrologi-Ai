HOUSE_LABELS_TR = {
    1: "kimlik ve durus",
    2: "para ve ozdeger",
    3: "zihin ve iletisim",
    4: "ev ve ic guven",
    5: "yaraticilik ve keyif",
    6: "ritim ve saglik",
    7: "iliskiler ve ortaklik",
    8: "yakinlik ve guven",
    9: "yon ve anlam",
    10: "kariyer ve gorunurluk",
    11: "cevre ve gelecek plani",
    12: "ic dunya ve cozunme",
}

ANGLE_LABELS_TR = {
    "ASC": "kimlik ve dis imaj",
    "DSC": "iliskiler ve bag dinamigi",
    "MC": "kariyer ve yon",
    "IC": "ev, kokler ve ic guven",
}


def build_where_sentence(context: dict) -> str:
    natal_house = context.get("natal_target_house")
    transit_house = context.get("transit_house")
    natal_point = context.get("natal_point")
    if context.get("is_angle") and natal_point in ANGLE_LABELS_TR:
        return f"Bunu en cok {ANGLE_LABELS_TR[natal_point]} tarafinda hissedebilirsin."

    if isinstance(natal_house, int) and 1 <= natal_house <= 12:
        natal_label = HOUSE_LABELS_TR[natal_house]
        if isinstance(transit_house, int) and 1 <= transit_house <= 12:
            transit_label = HOUSE_LABELS_TR[transit_house]
            return (
                f"Bunu en cok {natal_label} alaninda hissedebilirsin; "
                f"etkisi {transit_label} tarafina da tasabilir."
            )
        return f"Bunu en cok {natal_label} alaninda hissedebilirsin."

    overlay = context.get("transit_in_natal_house")
    if isinstance(overlay, int) and 1 <= overlay <= 12:
        return f"Etkisi {HOUSE_LABELS_TR[overlay]} tarafina da tasabilir."

    return "Bunu gunluk akis icinde daha belirgin hissedebilirsin."
