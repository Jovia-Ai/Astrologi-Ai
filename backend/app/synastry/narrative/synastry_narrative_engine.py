from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from app.synastry.narrative.phrase_lib_tr_synastry import (
    asymmetry_phrase,
    bundle_mechanism,
    clean_synastry_public_block,
    comfort_trigger_snapshot,
    domain_chip,
    domain_label,
    domain_room,
    mode_chip,
    mode_label,
    mode_line,
    mutuality_phrase,
    shared_theme_chip,
    shared_theme_line,
    support_chip,
    support_line,
    sustainability_band,
    tension_chip,
    tension_line,
)


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _top_bundle(bundles: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    return bundles[0] if bundles else {}


def _unique(items: Sequence[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        if not item:
            continue
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _story_debug_payload(
    *,
    block_id: str,
    template_id: str,
    story: Mapping[str, Any],
    bundles: Sequence[Mapping[str, Any]],
    extra: Mapping[str, Any] | None = None,
) -> dict:
    top_bundle = _top_bundle(bundles)
    evidence = list(top_bundle.get("evidence") or [])[:6]
    payload = {
        "id": block_id,
        "template_id": template_id,
        "primary_domain": story.get("primary_domain"),
        "secondary_domain": story.get("secondary_domain"),
        "surface_domain": story.get("surface_domain"),
        "mode": story.get("mode"),
        "modifier": story.get("modifier"),
        "routed_through": story.get("routed_through"),
        "top_bundle_kind": top_bundle.get("kind"),
        "top_bundle_score": round(_safe_float(top_bundle.get("score")), 4),
        "evidence": evidence,
    }
    if extra:
        payload.update(extra)
    return payload


def _public_block(
    block_id: str,
    headline: str,
    teaser: str,
    body: str,
    chips: Sequence[str],
    micro: str,
) -> dict:
    return clean_synastry_public_block(
        {
        "id": block_id,
        "headline": headline.strip(),
        "teaser": teaser.strip(),
        "body": body.strip(),
        "chips": _unique([chip.strip() for chip in chips if isinstance(chip, str)])[:4],
        "micro": micro.strip(),
        }
    )


def _pick_variant(seed: str, options: Sequence[str]) -> str:
    values = [option for option in options if option]
    if not values:
        return ""
    index = sum(ord(char) for char in str(seed or "")) % len(values)
    return values[index]


def _opening_headline(opener: str, verb: str, primary: str) -> str:
    if primary == "home_roots":
        return f"{opener} güven ve kök duygusunu {verb}"
    if primary == "intimacy_depth":
        return f"{opener} mahremiyet ve yoğunluk alanını {verb}"
    if primary == "private_inner_world":
        return f"{opener} iç dünya ve özel alanı {verb}"
    if primary == "social_future":
        return f"{opener} sosyal alan ve ortak akışı {verb}"
    return f"{opener} {domain_label(primary)} alanını {verb}"


def _opening_micro(primary: str, secondary: str, modifier: str) -> str:
    if primary == "home_roots" and secondary == "private_inner_world":
        return "Bağın önce güven verip sonra daha içte derinleşmesi burada belirgin."
    if primary == "intimacy_depth":
        return "İlginin kısa sürede daha kişisel ve yoğun bir yere inmesi burada çok tipik."
    if primary == "private_inner_world":
        return "Bir yakınlığın önce içerde büyüyüp sonra dışarı yansıması burada tanıdık."
    if primary == "social_future":
        return "Birlikte olma hissinin önce ortak alan ve akışta görünmesi burada hemen fark ediliyor."
    if modifier == "private_or_deepened":
        return "İlk sıcaklığın zamanla daha içte ve daha derin bir bağa dönmesi burada belirgin."
    return f"{domain_label(primary).capitalize()} ilk anda kendini belli ediyor."


def _build_opening_block(
    *,
    block_id: str,
    template_id: str,
    opener: str,
    verb: str,
    teaser_prefix: str,
    story: Mapping[str, Any],
    bundles: Sequence[Mapping[str, Any]],
) -> tuple[dict, dict]:
    primary = str(story.get("primary_domain") or "")
    secondary = str(story.get("secondary_domain") or "")
    surface_domain = str(story.get("surface_domain") or "")
    background_domain = str(story.get("background_domain") or "")
    mode = str(story.get("mode") or "")
    modifier = str(story.get("modifier") or "")
    lived_as = str(story.get("lived_as") or "")
    top_bundle = _top_bundle(bundles)
    mechanism = bundle_mechanism(top_bundle.get("kind"))
    teaser_prefix_key = f" {teaser_prefix.lower()} "
    direction = "sende" if " sende " in teaser_prefix_key else "onda"

    headline = _opening_headline(opener, verb, primary)
    teaser_seed = f"{block_id}:{primary}:{secondary}:{mode}:{modifier}"
    if primary == "home_roots" and secondary == "private_inner_world":
        teaser = _pick_variant(
            teaser_seed,
            (
                f"{teaser_prefix} önce güven ve yerleşme hissini uyandırıyor; sonra bunu daha içte yaşayan bir hatta taşıyor.",
                f"{teaser_prefix} önce güven tarafını açıyor; ardından bağı daha içerde çalışan bir yere indiriyor.",
            ),
        )
    elif primary == "intimacy_depth":
        teaser = _pick_variant(
            teaser_seed,
            (
                f"{teaser_prefix} yüzeyde kalmıyor; doğrudan derin bağ ve mahremiyet tarafına iniyor.",
                f"{teaser_prefix} kısa sürede daha kişisel, daha yoğun bir temas alanı açıyor.",
            ),
        )
    elif primary == "private_inner_world":
        teaser = _pick_variant(
            teaser_seed,
            (
                f"{teaser_prefix} açıkta kalan bir çekimden çok, içeride büyüyen bir yakınlık alanı açıyor.",
                f"{teaser_prefix} dışarıdan hemen görünmeyen, ama içerde büyüyen bir bağ duygusu yaratıyor.",
            ),
        )
    elif primary == "social_future":
        teaser = _pick_variant(
            teaser_seed,
            (
                f"{teaser_prefix} birlikte akma, ortak alan ve sosyal ritim tarafını görünür kılıyor.",
                f"{teaser_prefix} ortak çevre, beraber akış ve gelecek hissini öne çıkarıyor.",
            ),
        )
    else:
        teaser = _pick_variant(
            teaser_seed,
            (
                f"{teaser_prefix} en çok {domain_label(primary)} alanını öne çekiyor.",
                f"{teaser_prefix} ilk olarak {domain_label(primary)} tarafında kendini gösteriyor.",
            ),
        )

    body_parts = [
        _pick_variant(
            teaser_seed + ":lead",
            (
                f"Bu temas {direction} ilk anda görünen çekimin ötesinde {domain_label(primary)} tarafını da harekete geçiriyor.",
                f"İlk çekimin altında {direction} {domain_label(primary)} alanına da uzanan bir şey var.",
            ),
        )
    ]
    if lived_as:
        body_parts.append(lived_as)
    elif secondary:
        body_parts.append(
            _pick_variant(
                teaser_seed + ":secondary",
                (
                    f"İçerde {domain_label(secondary)} da eşlik ettiği için bu temas tek bir hatta akmıyor.",
                    f"Bunun altında {domain_label(secondary)} da çalıştığı için ilişki tek katmanlı kalmıyor.",
                ),
            )
        )
    else:
        body_parts.append(f"Bu etki {mode_label(mode)} bir tona kayıyor.")
    if surface_domain and surface_domain not in {primary, secondary}:
        body_parts.append(
            _pick_variant(
                teaser_seed + ":surface",
                (
                    f"Dışarıda ilk görünen şey daha çok {domain_label(surface_domain)} gibi dursa da, asıl hikaye içeride başka bir yerde kuruluyor.",
                    f"İlk bakışta {domain_label(surface_domain)} öne çıksa da, bağın asıl ağırlığı daha içeride toplanıyor.",
                ),
            )
        )
    elif secondary:
        body_parts.append(
            _pick_variant(
                teaser_seed + ":undertone",
                (
                    f"{domain_label(secondary).capitalize()} bu alanın tonunu sessizce belirliyor.",
                    f"{domain_label(secondary).capitalize()} burada ikinci bir damar gibi çalışıyor.",
                ),
            )
        )
    if background_domain and background_domain not in {primary, secondary}:
        body_parts.append(
            _pick_variant(
                teaser_seed + ":background",
                (
                    f"{domain_label(background_domain).capitalize()} duygusu da bu ilişkinin arka planında kendini hissettiriyor.",
                    f"Arka planda {domain_label(background_domain)} tarafı da bağı sessizce besliyor.",
                ),
            )
        )
    if mechanism:
        body_parts.append(mechanism)
    body = " ".join(body_parts[:4])
    chips = [domain_chip(primary), domain_chip(secondary), domain_chip(background_domain), mode_chip(mode)]
    micro = _opening_micro(primary, secondary, modifier)

    debug = _story_debug_payload(
        block_id=block_id,
        template_id=template_id,
        story=story,
        bundles=bundles,
        extra={"mechanism_line": mechanism},
    )
    public = _public_block(block_id, headline, teaser, body, chips, micro)
    return public, debug


def _compare_growth(a_growth: float, b_growth: float) -> str:
    if abs(a_growth - b_growth) <= 0.08:
        return "Büyüme çağrısı iki tarafta da benzer kuvvette çalışıyor."
    if a_growth > b_growth:
        return "Bu bağ seni daha erken dönüştürmeye zorluyor."
    return "Bu bağ karşı tarafı daha erken dönüştürmeye zorluyor."


def build_synastry_narrative(
    *,
    partner_a_name: str,
    partner_b_name: str,
    activation_bundles: Mapping[str, Sequence[Mapping[str, Any]]],
    domain_rankings: Mapping[str, Sequence[Mapping[str, Any]]],
    relational_modes: Mapping[str, Mapping[str, Any]],
    resonance_scores: Mapping[str, Any],
    corrected_scores: Mapping[str, Any],
    narrative_ready: Mapping[str, Any],
) -> dict:
    partner_a_story = narrative_ready.get("partner_a_story") if isinstance(narrative_ready, Mapping) else {}
    partner_b_story = narrative_ready.get("partner_b_story") if isinstance(narrative_ready, Mapping) else {}
    relationship_core = narrative_ready.get("relationship_core") if isinstance(narrative_ready, Mapping) else {}
    relationship_shape = narrative_ready.get("relationship_shape") if isinstance(narrative_ready, Mapping) else {}

    partner_a_bundles = list(activation_bundles.get("partner_a") or [])
    partner_b_bundles = list(activation_bundles.get("partner_b") or [])
    partner_a_rows = list(domain_rankings.get("partner_a") or [])
    partner_b_rows = list(domain_rankings.get("partner_b") or [])

    blocks: list[dict] = []
    blocks_debug: list[dict] = []

    block, debug = _build_opening_block(
        block_id="what_you_open_in_them",
        template_id="synastry_opening_outbound_v1",
        opener="Sen onda",
        verb="açıyorsun",
        teaser_prefix="Senden giden etki onda",
        story=partner_b_story if isinstance(partner_b_story, Mapping) else {},
        bundles=partner_b_bundles,
    )
    blocks.append(block)
    blocks_debug.append(debug)

    block, debug = _build_opening_block(
        block_id="what_they_open_in_you",
        template_id="synastry_opening_inbound_v1",
        opener="O sende",
        verb="açıyor",
        teaser_prefix="Ondan gelen etki sende",
        story=partner_a_story if isinstance(partner_a_story, Mapping) else {},
        bundles=partner_a_bundles,
    )
    blocks.append(block)
    blocks_debug.append(debug)

    a_primary = str((partner_a_story or {}).get("primary_domain") or "")
    b_primary = str((partner_b_story or {}).get("primary_domain") or "")
    shared_theme = str((relationship_core or {}).get("shared_theme") or "")
    if a_primary == b_primary and a_primary:
        rooms_teaser = f"Bu bağ ikinizde de en çok {domain_label(a_primary)} alanını hareketlendiriyor."
        rooms_body = (
            f"İlişki iki tarafta da aynı ana odaya basıyor ve bu yüzden temas hızlıca ortak bir merkeze oturuyor. "
            f"{shared_theme_line(shared_theme).capitalize()}. "
            f"Yine de alt tonlar tamamen aynı değil; sende ve onda açılan ikinci kapılar ritmi değiştiriyor."
        )
    else:
        rooms_teaser = f"Sende {domain_label(a_primary)}, onda {domain_label(b_primary)} öne çıkıyor."
        rooms_body = _pick_variant(
            f"rooms:{a_primary}:{b_primary}:{shared_theme}",
            (
                f"Aynı temas ikinizde de aynı kapıyı açmıyor. Sende {domain_room(a_primary)}, onda ise {domain_room(b_primary)} ilk tepkiyi oluşturuyor. {shared_theme_line(shared_theme).capitalize()}.",
                f"Bu ilişki iki tarafta aynı merkezden yaşanmıyor. Sende {domain_room(a_primary)}, onda ise {domain_room(b_primary)} daha hızlı çalışıyor. {shared_theme_line(shared_theme).capitalize()}.",
            ),
        )
    blocks.append(
        _public_block(
            "main_rooms_of_relationship",
            "Bu bağın ana odaları farklı çalışıyor",
            rooms_teaser,
            rooms_body,
            [domain_chip(a_primary), domain_chip(b_primary), shared_theme_chip(shared_theme)],
            "Aynı ilişki iki tarafta farklı merkezlerden yaşanıyor.",
        )
    )
    blocks_debug.append(
        {
            "id": "main_rooms_of_relationship",
            "template_id": "synastry_main_rooms_v1",
            "partner_a_top_domains": [row.get("domain") for row in partner_a_rows[:3]],
            "partner_b_top_domains": [row.get("domain") for row in partner_b_rows[:3]],
            "shared_theme": shared_theme,
        }
    )

    shared_support = str((relationship_core or {}).get("shared_support") or "")
    shared_tension = str((relationship_core or {}).get("shared_tension") or "")
    a_growth = _safe_float((relational_modes.get("partner_a") or {}).get("growth_pull"))
    b_growth = _safe_float((relational_modes.get("partner_b") or {}).get("growth_pull"))
    growth_body = _pick_variant(
        f"growth:{shared_support}:{shared_tension}",
        (
            f"{support_line(shared_support).capitalize()}. {tension_line(shared_tension).capitalize()}. {_compare_growth(a_growth, b_growth)}",
            f"{support_line(shared_support).capitalize()}. Ama aynı hatta {tension_line(shared_tension)}. {_compare_growth(a_growth, b_growth)}",
        ),
    )
    blocks.append(
        _public_block(
            "growth_axis",
            "Bu bağın ortak dersi çekimi taşıyabilmek",
            support_line(shared_support).capitalize(),
            growth_body,
            [support_chip(shared_support), tension_chip(shared_tension), "gelişim"],
            "Gelişim desteği ve gerilim aynı hatta çalışıyor.",
        )
    )
    blocks_debug.append(
        {
            "id": "growth_axis",
            "template_id": "synastry_growth_axis_v1",
            "shared_support": shared_support,
            "shared_tension": shared_tension,
            "partner_a_growth_pull": round(a_growth, 4),
            "partner_b_growth_pull": round(b_growth, 4),
        }
    )

    a_mode = relational_modes.get("partner_a") if isinstance(relational_modes, Mapping) else {}
    b_mode = relational_modes.get("partner_b") if isinstance(relational_modes, Mapping) else {}
    a_comfort = _safe_float((a_mode or {}).get("comfort_pull"))
    b_comfort = _safe_float((b_mode or {}).get("comfort_pull"))
    a_trigger = _safe_float((a_mode or {}).get("trigger_load"))
    b_trigger = _safe_float((b_mode or {}).get("trigger_load"))
    comfort_teaser = f"Sende deneyim {comfort_trigger_snapshot(a_comfort, a_trigger)}, onda ise {comfort_trigger_snapshot(b_comfort, b_trigger)}."
    if a_trigger > b_trigger + 0.08:
        trigger_line = "Tetik yükü sende daha erken yükseldiği için ritmi taşıyan taraf çoğu an sen oluyorsun."
    elif b_trigger > a_trigger + 0.08:
        trigger_line = "Tetik yükü onda daha erken yükseldiği için bağın ağırlığı karşı tarafta daha keskin hissediliyor."
    else:
        trigger_line = "Tetik yükü iki tarafta da yakın çalıştığı için bağ aynı anda hem yakın hem yorucu olabiliyor."
    comfort_body = _pick_variant(
        f"comfort:{round(a_comfort, 2)}:{round(b_comfort, 2)}:{round(a_trigger, 2)}:{round(b_trigger, 2)}",
        (
            f"Bu ilişki sende {comfort_trigger_snapshot(a_comfort, a_trigger)} bir iz bırakıyor. Karşı tarafta bu deneyim {comfort_trigger_snapshot(b_comfort, b_trigger)}. {trigger_line}",
            f"Sende bu temas {comfort_trigger_snapshot(a_comfort, a_trigger)} hissediliyor; onda ise deneyim {comfort_trigger_snapshot(b_comfort, b_trigger)} kalıyor. {trigger_line}",
        ),
    )
    blocks.append(
        _public_block(
            "comfort_vs_trigger",
            "Yakınlık ve yük aynı yere birikmiyor",
            comfort_teaser,
            comfort_body,
            ["tanıdıklık", "tetik", "ritim farkı"],
            "Konfor ve yük iki tarafta aynı yerde birikmiyor.",
        )
    )
    blocks_debug.append(
        {
            "id": "comfort_vs_trigger",
            "template_id": "synastry_comfort_trigger_v1",
            "partner_a_comfort_pull": round(a_comfort, 4),
            "partner_a_trigger_load": round(a_trigger, 4),
            "partner_b_comfort_pull": round(b_comfort, 4),
            "partner_b_trigger_load": round(b_trigger, 4),
        }
    )

    mutuality = _safe_float((relationship_shape or {}).get("mutuality"))
    asymmetry = _safe_float((relationship_shape or {}).get("asymmetry"))
    sustainability = _safe_float((relationship_shape or {}).get("sustainability"))
    corrected_bond = _safe_float(corrected_scores.get("bond"))
    corrected_depth = _safe_float(corrected_scores.get("depth"))
    corrected_risk = _safe_float(corrected_scores.get("risk_index"))
    long_term_teaser = f"{mutuality_phrase(mutuality).capitalize()} ve bağın taşıma kapasitesi {sustainability_band(sustainability)}."
    long_term_body = _pick_variant(
        f"long:{shared_tension}:{round(asymmetry, 2)}:{round(sustainability, 2)}",
        (
            f"Bu ilişki yalnız çekimle değil, taşıdığı iç düzenle şekilleniyor. {tension_line(shared_tension).capitalize()}. Uzun vadede bu ilişki {asymmetry_phrase(asymmetry)} ve bu yüzden taşıma kapasitesi {sustainability_band(sustainability)} kalıyor.",
            f"İlişkinin kaderini yalnız arzu belirlemiyor; içindeki baskı ve taşıma kapasitesi de belirliyor. {tension_line(shared_tension).capitalize()}. Uzun vadede bağ {asymmetry_phrase(asymmetry)} ve bu yüzden {sustainability_band(sustainability)} bir yapı gösteriyor.",
        ),
    )
    blocks.append(
        _public_block(
            "long_term_shape",
            "Uzun vadede belirleyici olan şey taşıma kapasitesi",
            long_term_teaser,
            long_term_body,
            [tension_chip(shared_tension), sustainability_band(sustainability), "uzun vade"],
            "Karşılıklılık var, ama ritim tamamen simetrik değil.",
        )
    )
    blocks_debug.append(
        {
            "id": "long_term_shape",
            "template_id": "synastry_long_term_shape_v1",
            "mutuality": round(mutuality, 4),
            "asymmetry": round(asymmetry, 4),
            "sustainability": round(sustainability, 4),
            "bond": round(corrected_bond, 4),
            "depth": round(corrected_depth, 4),
            "risk_index": round(corrected_risk, 4),
        }
    )

    return {
        "public": {"blocks": blocks},
        "debug": {
            "blocks_debug": blocks_debug,
            "input_summary": {
                "partner_a_name": partner_a_name,
                "partner_b_name": partner_b_name,
                "partner_a_story": partner_a_story,
                "partner_b_story": partner_b_story,
                "relationship_core": relationship_core,
                "relationship_shape": relationship_shape,
            },
        },
    }
