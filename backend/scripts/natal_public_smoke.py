from app.natal.public_builder import build_public_natal_view


def main() -> None:
    engine_response = {
        "core_story": "Bu donem kimlik duzende daha saglam bir cizgi kurmana yardimci olabilir.",
        "user_compact": {"identity": "Kisa ozet"},
        "upper_meaning_selected": {"enabled": True, "text": "Genis bir perspektif"},
        "meta": {"pressure_index": 0.61, "support_index": 0.78},
        "meaning_weighting": {
            "primary_theme": "identity",
            "secondary_theme": "relationships",
            "upper_meaning_allowed": True,
            "pressure_index": 0.61,
            "support_index": 0.78,
            "confidence": 0.7,
            "load_state": "medium",
            "extra": "should_not_leak",
        },
        "data_quality": {"summary": {"confidence": 0.7}},
        "narrative_anchor": {"domain": "identity"},
        "premium_mode": False,
    }
    public = build_public_natal_view(engine_response, locale="tr")
    print(public)
    print("public keys:", sorted(public.keys()))


if __name__ == "__main__":
    main()
