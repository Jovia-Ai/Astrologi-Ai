from __future__ import annotations

from typing import Dict, Mapping

SENTENCE_TEMPLATES = {
    "cause": (
        "Kimliğinin kökünde {text} ile ilgili derin bir yapı bulunur.",
        "Kimliğin, erken dönemden itibaren {text} üzerinden şekillenmeye başlar.",
    ),
    "mechanism": (
        "Bu nedenle kimliğini ortaya koyma biçimin {text} üzerinden çalışır.",
        "Bu yapı, kimliğini ifade ederken {text} şeklinde bir düzen kurar.",
    ),
    "effect": (
        "Bu yapı, dış dünyada {text} olarak algılanabilir.",
        "Başkaları seni zaman zaman {text} üzerinden deneyimleyebilir.",
    ),
    "shadow": (
        "Ancak bu gerilim dengelenmediğinde {text} eğilimi ortaya çıkabilir.",
        "Bu noktada sorun davranış değil; onu yöneten içsel basınçtır.",
    ),
    "potential": (
        "Yine de bu yapı doğru regüle edildiğinde {text} açığa çıkar.",
        "Kimliğini bu merkezden kurduğunda, {text} doğal bir güç haline gelir.",
    ),
}

def build_identity_pilot(
    phase2_slots: Mapping[str, Mapping[str, str]],
    regulation: Mapping[str, float],
) -> str:
    energy_pressure = float(regulation.get("energy_pressure", 0.0) or 0.0)
    slot_weights = regulation.get("slot_weights", {})
    sentences: list[str] = []

    if cause := phase2_slots.get("cause"):
        template_index = 1 if energy_pressure >= 0.6 else 0
        sentences.append(SENTENCE_TEMPLATES["cause"][template_index].format(text=cause["text"]))

    if mechanism := phase2_slots.get("mechanism"):
        template_index = 1 if energy_pressure >= 0.7 else 0
        sentences.append(SENTENCE_TEMPLATES["mechanism"][template_index].format(text=mechanism["text"]))

    if effect := phase2_slots.get("effect"):
        sentences.append(SENTENCE_TEMPLATES["effect"][0].format(text=effect["text"]))

    shadow = phase2_slots.get("shadow")
    if shadow:
        sentences.append(SENTENCE_TEMPLATES["shadow"][0].format(text=shadow["text"]))
        if slot_weights.get("shadow", 0.0) >= 0.25:
            sentences.append(SENTENCE_TEMPLATES["shadow"][1].format(text=shadow["text"]))

    if potential := phase2_slots.get("potential"):
        template_index = 1 if energy_pressure >= 0.5 else 0
        sentences.append(SENTENCE_TEMPLATES["potential"][template_index].format(text=potential["text"]))

    return " ".join(sentences).strip()
