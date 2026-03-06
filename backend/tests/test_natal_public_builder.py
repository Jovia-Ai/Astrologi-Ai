from app.natal.public_builder import build_public_natal_view


def test_public_natal_view_includes_supporting_threads_and_graph() -> None:
    response = {
        "core_story": "Kisa test metni.",
        "core_story_ui": {"headline": "Baslik", "text": "Kisa omurga metni."},
        "meta": {"pressure_index": 0.4, "support_index": 0.6},
        "meaning_weighting": {"primary_theme": "identity", "confidence": 0.72},
        "narrative_anchor": {"domain": "identity"},
        "profile_narrative": {
            "profile_public": {
                "engine_version": "profile_narrative_v1",
                "blocks": [
                    {
                        "id": "mind_voice",
                        "headline": "Zihin tonu",
                        "teaser": "Kisa teaser.",
                        "body": "Akici profile body metni.",
                        "chips": ["Satürn 3.ev", "Merkür 1.ev"],
                    }
                ],
            },
            "profile_internal": {
                "blocks_debug": [
                    {
                        "id": "mind_voice",
                        "template_id": "mind_voice:structured",
                        "primary_signature_id": "mind_saturn_third",
                        "evidence": [{"type": "placement"}, {"type": "aspect"}],
                    }
                ]
            },
        },
        "sections_v2": [
            {
                "id": "mind_system",
                "title": "Zihin–eylem–kontrol",
                "subtitle": "Netleşince hızlanıyorsun.",
                "body": "Akıcı tema metni.",
                "micro": "Kısa örnek.",
                "chips": ["Yükselen Oğlak", "Satürn 3. ev"],
            }
        ],
        "supporting_threads": [
            {
                "id": "identity_mechanics",
                "title": "Kimlik",
                "one_liner": "Kisa cizgi.",
                "paragraph": "Daha uzun aciklama.",
                "evidence": [{"type": "house_ruler"}],
            }
        ],
        "natal_graph_compact": {
            "house_rulers": {"1": {"primary_ruler": "Saturn"}},
            "dominant_loops": [{"signature": "Saturn→Mars→Mercury", "count": 2}],
            "importance": {"Saturn": 0.88},
            "ignored": "x",
        },
    }

    public = build_public_natal_view(response, locale="tr")
    assert public["supporting_threads"]
    assert public["supporting_threads"][0]["id"] == "identity_mechanics"
    assert public["profile_narrative"]["profile_public"]["blocks"]
    assert "profile_internal" not in public["profile_narrative"]
    assert public["sections_v2"]
    assert public["sections_v2"][0]["id"] == "mind_system"
    assert isinstance(public.get("core_story_ui"), dict)
    assert public["core_story_ui"].get("text")
    compact = public["natal_graph_compact"]
    assert isinstance(compact, dict)
    assert "house_rulers" in compact
    assert "ignored" not in compact

    debug_public = build_public_natal_view(response, locale="tr", include_debug=True)
    assert debug_public["profile_narrative"]["profile_internal"]["blocks_debug"]
