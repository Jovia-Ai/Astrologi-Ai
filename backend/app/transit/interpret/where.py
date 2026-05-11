HOUSE_LABELS_TR = {
    1: "kimlik ve duruş",
    2: "para ve özdeğer",
    3: "zihin ve iletişim",
    4: "ev ve iç güven",
    5: "yaratıcılık ve keyif",
    6: "ritim ve sağlık",
    7: "ilişkiler ve ortaklık",
    8: "yakınlık ve güven",
    9: "yön ve anlam",
    10: "kariyer ve görünürlük",
    11: "çevre ve gelecek planı",
    12: "iç dünya ve çözünme",
}

ANGLE_LABELS_TR = {
    "ASC": "kimlik ve dış imaj",
    "DSC": "ilişkiler ve bağ dinamiği",
    "MC": "kariyer ve yön",
    "IC": "ev, kökler ve iç güven",
}


def build_where_sentence(context: dict) -> str:
    natal_house = context.get("natal_target_house")
    transit_house = context.get("transit_house")
    natal_point = context.get("natal_point")
    if context.get("is_angle") and natal_point in ANGLE_LABELS_TR:
        return f"Bunu en çok {ANGLE_LABELS_TR[natal_point]} tarafında hissedebilirsin."

    if isinstance(natal_house, int) and 1 <= natal_house <= 12:
        natal_label = HOUSE_LABELS_TR[natal_house]
        if isinstance(transit_house, int) and 1 <= transit_house <= 12:
            transit_label = HOUSE_LABELS_TR[transit_house]
            return (
                f"Bunu en çok {natal_label} alanında hissedebilirsin; "
                f"etkisi {transit_label} tarafına da taşabilir."
            )
        return f"Bunu en çok {natal_label} alanında hissedebilirsin."

    overlay = context.get("transit_in_natal_house")
    if isinstance(overlay, int) and 1 <= overlay <= 12:
        return f"Etkisi {HOUSE_LABELS_TR[overlay]} tarafına da taşabilir."

    return "Bunu günlük akış içinde daha belirgin hissedebilirsin."
