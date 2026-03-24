from app.builders.output_compactor import build_user_compact


def test_user_compact_prefers_concrete_evidence_for_abstract_fragments() -> None:
    fragments = {
        "identity": {
            "slots": {
                "cause": {
                    "text": "Kimliğini oluşturan temel yapı istikrar ve güven ihtiyacına dayanır",
                    "supporting_facts": [{"text": "Dışarıdan sakin, kararlı ve dayanıklı algılanırsın."}],
                },
                "mechanism": {
                    "text": "görünür olma ihtiyacı",
                    "supporting_facts": [{"text": "İlk izlenimde daha baskın ve merkezde algılanırsın."}],
                },
                "potential": {
                    "text": "Bu güven veren, bağlılık odaklı bir partner yapar",
                    "supporting_facts": [{"text": "Eleştiri geldiğinde içeride neyin sarsıldığını daha net görürsün."}],
                },
            }
        }
    }

    compact = build_user_compact(fragments)
    domain = compact["domains"][0]
    texts = [item["text"] for item in domain["highlights"]]

    assert any("İlk izlenimde daha baskın" in text for text in texts)
    assert any("Eleştiri geldiğinde" in text for text in texts)
    assert "görünür olma ihtiyacı." not in domain["summary"]
    assert "Bu güven veren" not in domain["summary"]
