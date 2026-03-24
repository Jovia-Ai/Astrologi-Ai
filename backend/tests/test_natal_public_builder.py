import re

from app.natal.public_builder import build_public_natal_view


def test_public_natal_view_includes_supporting_threads_and_graph() -> None:
    response = {
        "core_story": "Kisa test metni.",
        "core_story_ui": {"headline": "Baslik", "text": "Kisa omurga metni."},
        "planets": [
            {"planet": "Moon", "house": 8, "sign": "Scorpio"},
            {"planet": "Saturn", "house": 4, "sign": "Aquarius"},
            {"planet": "Mercury", "house": 3, "sign": "Virgo"},
        ],
        "aspects": [
            {"planet1": "Moon", "planet2": "Saturn", "aspect": "square", "orb": 0.8},
            {"planet1": "Mercury", "planet2": "Saturn", "aspect": "trine", "orb": 1.1},
        ],
        "meta": {"pressure_index": 0.4, "support_index": 0.6},
        "meaning_weighting": {"primary_theme": "identity", "confidence": 0.72},
        "narrative_anchor": {"domain": "identity"},
        "personality_imprint": {
            "engine_version": "personality_imprint_v1",
            "library_version": "personality_imprint_library_tr_v6",
            "locale": "tr",
            "headline": "Kişilik İmzası",
            "render_shape": {
                "headline": "Kişilik İmzası",
                "subfields": ["aura", "trait", "drive"],
                "optional_subfield": "shadow",
            },
            "entries": [
                {
                    "key": "sun_house_10",
                    "kind": "house_placement",
                    "label_tr": "Güneş 10. Ev",
                    "tags": ["başarı", "görünürlük", "hedef"],
                    "aura": "Sende saygı uyandıran, hedefe dönük ve görünür olmak isteyen güçlü bir enerji olabilir.",
                    "trait": "Sen yaptığın şeyin ciddiye alınmasını, emeklerinin karşılık bulmasını ve iz bırakmayı istersin.",
                    "drive": "İçinde bir şey başarma, yükselme ve kendi değerinle görünür olma arzusu güçlüdür.",
                    "shadow": "Bazen değeri sadece başarıyla ölçme ya da kendine fazla baskı kurma eğilimi oluşabilir.",
                    "background_hint": "",
                    "gift": "Bu yerleşim sende hedef bilinci, güçlü duruş ve kamusal alanda parlayan bir merkez yaratır.",
                    "support_keys": ["moon_leo"],
                }
            ],
            "extra_entries": [
                {
                    "key": "venus_house_12",
                    "kind": "house_placement",
                    "label_tr": "Venüs 12. Ev",
                    "tags": ["gizli", "ince", "ruhsal"],
                    "aura": "Sende yumuşak, zarif ve tam çözülemeyen bir kalp enerjisi olabilir.",
                    "trait": "Sen sevgiyi her zaman yüksek sesle değil, çoğu zaman sessiz ve derin katmanlarda yaşarsın.",
                    "drive": "İçinde ruhsal yakınlık, ince bağlar ve görünmeyen sevgi alışverişi kurma ihtiyacı vardır.",
                    "shadow": "Bazen duygularını açık ifade etmek yerine geri çekilebilir ya da ulaşılmaz kişilere çekilebilirsin.",
                    "background_hint": "Yakınlık alanında temkinli olmayı erken dönemde öğrenmiş olabilirsin.",
                    "gift": "Bu yerleşim sende çok ince bir sezgi, saf bir sadakat ve ruha dokunan bir sevgi yaratır.",
                    "support_keys": ["venus_sagittarius"],
                }
            ],
            "support_entries": [
                {
                    "key": "moon_leo",
                    "kind": "sign_placement",
                    "label_tr": "Ay Aslan",
                    "tags": ["sicak", "gorunur duygu", "gururlu kalp"],
                    "aura": "Kalbin losta yasamiyor; baglandiginda sicakligin fark edilir hale geliyor.",
                    "trait": "Sen duygularini buyuk, canli ve icten bir yerden yasarsin.",
                    "drive": "Icinde sevilmek, gorulmek ve kalpten verdigin seyin karsilik buldugunu hissetmek isteyen guclu bir ihtiyac vardir.",
                    "shadow": "Bazen gurur yarasi, onay ihtiyaci ya da dramatik tepkiler one cikabilir.",
                }
                ,
                {
                    "key": "venus_sagittarius",
                    "kind": "sign_placement",
                    "label_tr": "Venüs Yay",
                    "tags": ["özgür sevgi", "neşe", "açık kalp"],
                    "aura": "Kalbin dar odada yaşamıyor; sevgi sende alan, neşe ve dürüstlük isteyebilir.",
                    "trait": "Sen sevgide özgürlük, içtenlik ve birlikte genişleme duygusu ararsın.",
                    "drive": "İçinde ilham duymak, hayatı paylaşırken çoğalmak ve sevginin canlı kalmasını istemek vardır.",
                    "shadow": "Bazen bağ derinleşmeden alan istemeye kaçabilir ya da fazla rahat davranabilirsin.",
                }
            ],
            "bundles": [
                {
                    "id": "sun_house_10",
                    "dominant_key": "sun_house_10",
                    "dominant_kind": "house_placement",
                    "related_planets": ["Sun"],
                    "support_keys": ["moon_leo"],
                }
            ],
            "extra_bundles": [
                {
                    "id": "venus_house_12",
                    "dominant_key": "venus_house_12",
                    "dominant_kind": "house_placement",
                    "related_planets": ["Venus"],
                    "support_keys": ["venus_sagittarius"],
                }
            ],
            "selection_debug": {"selected_keys": ["sun_house_10"]},
        },
        "profile_narrative": {
            "profile_public": {
                "engine_version": "profile_narrative_v2",
                "blocks": [
                    {
                        "id": "mind_voice",
                        "headline": "Zihin tonu",
                        "teaser": "Kisa teaser.",
                        "body": "Akici profile body metni.",
                        "micro": "Kısa ama ayrı bir mikro içgörü.",
                        "astro_hint": "Merkür 1. ev, Satürn 3. ev",
                        "astro_sources": ["Merkür 1. ev", "Satürn 3. ev"],
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
    assert public["personality_imprint"]["headline"] == "Kişilik İmzası"
    assert public["personality_imprint"]["entries"][0]["key"] == "sun_house_10"
    assert public["personality_imprint"]["extra_entries"][0]["key"] == "venus_house_12"
    assert public["personality_imprint"]["entries"][0]["support_keys"] == ["moon_leo"]
    assert public["personality_imprint"]["entries"][0]["gift"] == "Bu yerleşim sende hedef bilinci, güçlü duruş ve kamusal alanda parlayan bir merkez yaratır."
    assert public["personality_imprint"]["extra_entries"][0]["background_hint"] == "Yakınlık alanında temkinli olmayı erken dönemde öğrenmiş olabilirsin."
    assert public["personality_imprint"]["support_entries"][0]["key"] == "moon_leo"
    assert public["personality_imprint"]["bundles"][0]["support_keys"] == ["moon_leo"]
    assert public["personality_imprint"]["extra_bundles"][0]["support_keys"] == ["venus_sagittarius"]
    assert "selection_debug" not in public["personality_imprint"]
    assert public["profile_narrative"]["profile_public"]["blocks"]
    assert public["profile_narrative"]["profile_public"]["blocks"][0]["micro"]
    block = public["profile_narrative"]["profile_public"]["blocks"][0]
    insight_modules = public["profile_narrative"]["profile_public"]["insight_modules"]
    assert len(insight_modules) == 1
    assert insight_modules[0]["module_id"] == "moon_defense_mechanism"
    assert insight_modules[0]["headline"] == "Senin savunma mekanizman"
    assert insight_modules[0]["moon_sign"] == "Scorpio"
    assert insight_modules[0]["title"] == "İncinmemek için hep tetikte kalıyorsun"
    assert insight_modules[0]["share_text"].startswith("Senin savunma mekanizman:")
    assert insight_modules[0]["meta"]["expandable"] is True
    assert insight_modules[0]["priority"] == 32
    assert block["astro_hint"]
    assert block["astro_sources"] == ["Merkür 1. ev", "Satürn 3. ev"]
    assert public["profile_narrative"]["profile_public"]["schema_version"] == "profile_narrative_public_v3"
    assert public["profile_narrative"]["profile_public"]["core_blocks"]
    assert public["profile_narrative"]["profile_public"]["detail_cards"]
    assert public["profile_narrative"]["profile_public"]["core_blocks"][0]["family"] == "mind_mechanics"
    assert "3. ev" not in block["astro_hint"]
    assert "Merkür" not in block["astro_hint"]
    assert all("ev" not in chip.lower() for chip in block["chips"])
    assert "profile_internal" not in public["profile_narrative"]
    assert public["sections_v2"]
    assert public["sections_v2"][0]["id"] == "mind_system"
    assert isinstance(public.get("core_story_ui"), dict)
    assert public["core_story_ui"].get("text")
    compact = public["natal_graph_compact"]
    assert isinstance(compact, dict)
    assert "house_rulers" in compact
    assert "ignored" not in compact
    assert public["narrative_v2"]["contract_version"] == "narrative_v2_draft_2026_03"
    selector = public["narrative_v2"]["aspect_bundle_selector"]
    assert selector["selected_bundles"]
    assert selector["max_primary_bundles"] == 3

    debug_public = build_public_natal_view(response, locale="tr", include_debug=True)
    assert debug_public["personality_imprint"]["selection_debug"]["selected_keys"] == ["sun_house_10"]
    assert debug_public["profile_narrative"]["profile_internal"]["blocks_debug"]
    assert "section_priority_matrix" in debug_public["narrative_v2"]
    assert "migration_map" in debug_public["narrative_v2"]


def test_public_natal_view_naturalizes_profile_copy_and_humanizes_chips() -> None:
    response = {
        "core_story": "Kısa test metni.",
        "meta": {"pressure_index": 0.4, "support_index": 0.6},
        "narrative_anchor": {"domain": "identity"},
        "profile_narrative": {
            "profile_public": {
                "engine_version": "profile_narrative_v2",
                "blocks": [
                    {
                        "id": "luck_creation",
                        "headline": "Sende akış nerede hızlanıyor",
                        "teaser": "Sende kapı açan taraf, şans sende tesadüf değil.",
                        "body": (
                            "Kimlik hattında yön duygusu ve büyük resim birlikte belirgin. "
                            "Yakınlık sende yüzey değil. "
                            "İçeride söz senin kasın. "
                            "Kariyer hattında görünürlük ve kalite standardı birlikte çalışıyor."
                        ),
                        "micro": "Akış tarafında cesaret ile sezgi aynı kapıyı çalıştırıyor.",
                        "astro_hint": "Zihinsel tarafta cümle disiplini ile sezgi aynı anda devrede.",
                        "astro_sources": ["Jüpiter 5. ev", "Mars-Neptün üçgeni"],
                        "chips": ["Upgrade", "Kalibrasyon", "İç Ayar", "Sistem + Yenilik"],
                    }
                ],
            }
        },
    }

    public = build_public_natal_view(response, locale="tr")
    block = public["profile_narrative"]["profile_public"]["blocks"][0]
    body = str(block["body"]).lower()

    assert block["headline"] == "Şansın en kolay nerede açılıyor"
    assert "sende kapı açan taraf" not in str(block["teaser"]).lower()
    assert "tesadüf gibi değil" in str(block["teaser"]).lower()
    assert "kimlik hattında" not in body
    assert "kariyer hattında" not in body
    assert "yakınlık sende yüzey değil" not in body
    assert "söz senin kasın" not in body
    assert "yakınlık senin için yüzeyde kalan bir şey değil" in body
    assert "sözü seçme ve yerli yerine koyma becerin güçlü" in body
    assert "zihinsel tarafta" not in str(block["astro_hint"]).lower()
    assert "cümle disiplinin" in str(block["astro_hint"]).lower()
    assert "akış tarafında" not in str(block["micro"]).lower()
    assert "gerekir" not in str(block["micro"]).lower()
    body_first = re.split(r"(?<=[.!?])\s+", str(block["body"]).strip())[0]
    assert body_first
    teaser_tokens = set(re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", str(block["teaser"]).lower()))
    first_tokens = set(re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]+", body_first.lower()))
    overlap = len(teaser_tokens & first_tokens) / len(teaser_tokens | first_tokens)
    assert overlap < 0.8
    assert block["astro_sources"] == ["Jüpiter 5. ev", "Mars-Neptün üçgeni"]
    assert block["chips"] == ["Yenilik", "İç Denge", "Yapı ve Yenilik"]


def test_public_natal_view_profile_copy_cleanup_is_deterministic() -> None:
    response = {
        "core_story": "Kısa test metni.",
        "meta": {"pressure_index": 0.2, "support_index": 0.8},
        "narrative_anchor": {"domain": "identity"},
        "profile_narrative": {
            "profile_public": {
                "engine_version": "profile_narrative_v2",
                "blocks": [
                    {
                        "id": "mind_voice",
                        "headline": "Karar alırken içinde olan şey",
                        "teaser": "Yakınlık sende yüzey değil; güven kurdukça büyür.",
                        "body": (
                            "Sende ilk hissedilen şey, Akici bir cümle kuruyorsun. "
                            "Sende düşünürken ilk görülen taraf, içerde tonu tartman. "
                            "Sende kapı açan taraf, şans sende tesadüf değil. "
                            "İçeride söz senin kasın."
                        ),
                        "micro": "Zihinsel tarafta cümle disiplini ile sezgi aynı anda devrede.",
                        "astro_hint": "Kimlik hattında yön duygusu ve büyük resim birlikte belirgin.",
                        "chips": ["Kalibrasyon", "İç Ayar", "Upgrade"],
                    }
                ],
            }
        },
    }

    first = build_public_natal_view(response, locale="tr")
    second = build_public_natal_view(response, locale="tr")

    assert first["profile_narrative"]["profile_public"]["blocks"] == second["profile_narrative"]["profile_public"]["blocks"]
    body = str(first["profile_narrative"]["profile_public"]["blocks"][0]["body"])
    starters = [sentence for sentence in re.split(r"(?<=[.!?])\s+", body) if sentence.strip()]
    assert sum(1 for sentence in starters if sentence.lower().startswith("sende ")) <= 1


def test_public_natal_view_softens_core_story_and_sectional_coaching_language() -> None:
    response = {
        "core_story": (
            "Varlığını güçlü biçimde hissettirme ve görünür olma ihtiyacı kimliğinin merkezindedir. "
            "Bu ihtiyaç yükseldiğinde, Aşırı ben-merkezcilik, her şeyi kişisel algılama daha kolay tetiklenebilir.\n\n"
            "Psikolojik temelinde ‘ben kimim ve nasıl görünmeliyim.\n\n"
            "Böylece Dürüst ve net olduğunda insanlara yön ve cesaret verirsin."
        ),
        "meta": {"pressure_index": 0.4, "support_index": 0.6},
        "narrative_anchor": {"domain": "identity"},
        "sections_v2": [
            {
                "id": "mind_system",
                "title": "Zihin",
                "subtitle": "Netleşince hızlanıyorsun; ritim hızın çarpanı.",
                "body": (
                    "Burada ustalık daha çok düşünmek değil, sınırı daha iyi çizmek ve ritmini korumak; "
                    "çünkü ritim bozulduğunda sistem yoruluyor, ritim oturduğunda ise çok hızlı toparlanıyorsun."
                ),
                "micro": "Az cümleyle sınır koyduğunda hem zihnin hem ritmin rahatlıyor; sende hız çoğu zaman bu sadeleşmeden geliyor.",
            }
        ],
        "supporting_threads": [
            {
                "id": "career_visibility",
                "title": "Kariyer",
                "one_liner": "Sahneye çıkınca etkilisin; ama önce içeride olgunlaştırıyorsun.",
                "paragraph": (
                    "Bu yüzden seni en çok büyüten şey bir anda büyük çıkışlar değil, küçük ama düzenli görünürlük adımlarıyla ritim kurmak. "
                    "Burada hız, mükemmeli beklemekten değil yayınlanabilir iyi seviyesini tutarlı biçimde çoğaltmaktan geliyor."
                ),
                "body": "Kariyerde senin gücün güçlü.",
                "micro": "Görünürlüğü küçük ve düzenli dozlarla taşıman, sende baskıyı azaltırken etkiyi büyütüyor.",
            }
        ],
    }

    public = build_public_natal_view(response, locale="tr")

    core_story = str(public["core_story"])
    assert "Bu ihtiyaç yükseldiğinde" not in core_story
    assert "Böylece Dürüst" not in core_story
    assert "İçeride sık sık 'ben kimim ve nasıl görünmeliyim?'" in core_story

    section = public["sections_v2"][0]
    assert "ritim hızın çarpanı" not in str(section["subtitle"]).lower()
    assert "çarpanı" not in str(section["subtitle"]).lower()
    assert "ritim bozulduğunda sistem yoruluyor" not in str(section["body"]).lower()

    thread = public["supporting_threads"][0]
    assert "görünürlük adımları" not in str(thread["paragraph"]).lower()
    assert "yayınlanabilir iyi seviyesi" not in str(thread["paragraph"]).lower()
    assert "küçük ve düzenli dozlarla" not in str(thread["micro"]).lower()
