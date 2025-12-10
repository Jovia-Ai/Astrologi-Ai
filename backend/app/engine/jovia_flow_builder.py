class JoviaNarrativeFlowEngine:
    """
    Takes the final 4 weighted sentences (cause, mechanism, shadow, potential)
    and stitches them into a connected, flowing paragraph.
    """

    CONNECTORS = {
        "identity": {
            "cause_mechanism": "Bu yüzden ",
            "mechanism_shadow": "Ancak ",
            "shadow_potential": "Yine de "
        },
        "psychology": {
            "cause_mechanism": "Bu nedenle duygusal süreçlerinde ",
            "mechanism_shadow": "Fakat ",
            "shadow_potential": "Buna rağmen "
        },
        "relationships": {
            "cause_mechanism": "Bu nedenle bağlarında ",
            "mechanism_shadow": "Fakat ilişkisel düzlemde ",
            "shadow_potential": "Yine de ilişki dinamiklerinde "
        },
        "mind": {
            "cause_mechanism": "Bu nedenle zihinsel süreçlerinde ",
            "mechanism_shadow": "Ancak düşünsel olarak ",
            "shadow_potential": "Yine de zihinsel potansiyelin "
        },
        "career": {
            "cause_mechanism": "Bu nedenle iş hayatında ",
            "mechanism_shadow": "Fakat profesyonel düzlemde ",
            "shadow_potential": "Yine de kariyer yolunda "
        },
        "karma": {
            "cause_mechanism": "Bu nedenle ruhsal yolculuğunda ",
            "mechanism_shadow": "Fakat karmasal olarak ",
            "shadow_potential": "Yine de kader seni "
        }
    }

    def build_flow(self, cat: str, cause: str, mechanism: str, shadow: str, potential: str) -> str:
        c = self.CONNECTORS.get(cat, self.CONNECTORS["identity"])

        out = ""

        if cause:
            out += cause.strip()
            if not cause.strip().endswith((".", "!", "?")):
                out += "."
            out += " "

        if mechanism:
            out += c["cause_mechanism"] + mechanism.strip()
            if not mechanism.strip().endswith((".", "!", "?")):
                out += "."
            out += " "

        if shadow:
            out += c["mechanism_shadow"] + shadow.strip()
            if not shadow.strip().endswith((".", "!", "?")):
                out += "."
            out += " "

        if potential:
            out += c["shadow_potential"] + potential.strip()
            if not potential.strip().endswith((".", "!", "?")):
                out += "."

        return out.strip()
