from app.transit.present.public_builder import build_public_event


def main() -> None:
    main_item = {
        "event_id": "evt.main.high",
        "ranking": {"tier": "main", "weight": 1.35},
        "interpretation": {
            "headline": "Netlikte dalgalanma",
            "headline_short": "Netlikte dalgalanma",
            "one_liner": "Netlikte dalgalanma; bunu en cok kimlik ve gorunurluk tarafinda hissedebilirsin. Uzun vadede netlik oturabilir.",
            "summary": "Kontrol etmeye alistikca netlik zorlanabilir. Kucuk denemelerle daha gercek bir ifade ortaya cikabilir.",
            "where_short": "kimlik ve gorunurluk",
            "where": "Bunu en cok kimlik ve gorunurluk alaninda hissedebilirsin.",
            "time_hint": "Etki kademeli ilerler; bazi gunler daha belirgin hissedilebilir.",
            "do": [
                "Gunu sadelestir: tek bir oncelik sec.",
                "Kucuk geri donuslu denemeler yap.",
                "Uygulama: Kontrolu gevsettikce daha gercek bir ifade ortaya cikabilir.",
            ],
            "watch": ["Belirsizligi hata gibi okumamaya dikkat et.", "Belirsizlikten kacmak zorlayabilir."],
        },
    }
    flavor_item = {
        "event_id": "evt.flavor.low",
        "ranking": {"tier": "flavor", "weight": 0.75},
        "interpretation": {
            "headline": "Kisa bir vurgu",
            "summary": "Bu etki belirgin bir vurgu yaratabilir.",
            "where_short": "gunluk duzen",
            "time_hint": "Etki kisa sureli ve hafif olabilir.",
            "do": ["Ritme sadik kal.", "Ritme sadik kal."],
            "watch": ["Rahatliga kapilma", "Rahatliga kapilmak"],
        },
    }

    print("MAIN/HIGH public blocks:")
    print(build_public_event(main_item).model_dump())
    print("\nFLAVOR/LOW public blocks:")
    print(build_public_event(flavor_item).model_dump())


if __name__ == "__main__":
    main()
