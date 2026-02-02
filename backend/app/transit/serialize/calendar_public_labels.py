LABEL_TRANSLATIONS = {
    "değer/çekim": "çekim ve değer teması",
    "genişleme": "büyüme",
    "yoğunlaşma": "yoğun enerji",
    "yaralanma": "hassasiyet",
    "gerilim": "zorlayıcı etki",
    "hareket": "tempo",
    "zihin": "odak",
    "irade": "motivasyon",
    "algı": "sezgi",
    "ev": "ev/aile",
    "iş": "iş/kariyer",
}


def humanize_label(label: str) -> str:
    out = label or ""
    for k, v in LABEL_TRANSLATIONS.items():
        out = out.replace(k, v)
    out = out.replace("↔", "—")
    out = out.replace("(— ↔ ev)", "(ev/aile)")
    out = out.replace("(— ↔ iş)", "(iş/kariyer)")
    out = out.replace("+", "•")
    out = " ".join(out.split())
    return out


def humanize_labels(labels: list[str]) -> list[str]:
    return [humanize_label(x) for x in labels if x]
