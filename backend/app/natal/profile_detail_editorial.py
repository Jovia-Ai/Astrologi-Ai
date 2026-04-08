from __future__ import annotations

from typing import Any, Mapping, Sequence

from app.narrative.humanize_tr import (
    cleanup_tr_punctuation,
    humanize_tr_text,
    sentence_safe_clamp,
    split_tr_sentences,
)

MAX_EDITORIAL_DETAIL_BLOCKS = 7


def _clean_text(text: Any, *, max_sentences: int = 2, max_chars: int = 260) -> str:
    value = cleanup_tr_punctuation(str(text or "").strip())
    if not value:
        return ""
    humanized = humanize_tr_text(value, max_sentences=max_sentences)
    clamped = sentence_safe_clamp(
        humanized,
        max_chars=max_chars,
        max_sentences=max_sentences,
    )
    return cleanup_tr_punctuation(str(clamped or "").strip())


def _normalize_blocks(
    values: Sequence[Any] | None,
    *,
    max_blocks: int = MAX_EDITORIAL_DETAIL_BLOCKS,
) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in values or []:
        clean = _clean_text(item, max_sentences=3, max_chars=320)
        if not clean:
            continue
        key = clean.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(clean)
        if len(out) >= max_blocks:
            break
    return out


def _split_sentences(value: str, *, max_sentences: int = 5) -> list[str]:
    text = _clean_text(value, max_sentences=max_sentences + 1, max_chars=900)
    if not text:
        return []
    out: list[str] = []
    for item in split_tr_sentences(text):
        clean = _clean_text(item, max_sentences=1, max_chars=240)
        if clean:
            out.append(clean)
        if len(out) >= max_sentences:
            break
    return out


def _join_labels(values: Sequence[Any] | None, *, limit: int = 2) -> str:
    labels = [
        cleanup_tr_punctuation(str(item or "").strip())
        for item in (values or [])[:limit]
        if str(item or "").strip()
    ]
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    return f"{labels[0]} ve {labels[1]}"


def _first_non_empty(*values: Any) -> str:
    for value in values:
        clean = _clean_text(value, max_sentences=2, max_chars=260)
        if clean:
            return clean
    return ""


def _infer_thread_family(thread: Mapping[str, Any]) -> str:
    label = (
        f"{str(thread.get('section_id') or thread.get('id') or '').strip()} "
        f"{str(thread.get('title') or '').strip()}"
    ).lower()
    if "mind" in label or "zihin" in label:
        return "mind_mechanics"
    if "identity" in label or "kimlik" in label:
        return "outer_inner_split"
    if (
        "career" in label
        or "kariyer" in label
        or "görünür" in label
        or "gorunur" in label
        or "iş" in label
        or "is" in label
    ):
        return "visible_power"
    if "relation" in label or "iliş" in label or "yakın" in label:
        return "intimacy_guard"
    return "placement_signature"


def _chip_values(thread: Mapping[str, Any]) -> list[str]:
    return [
        cleanup_tr_punctuation(str(item or "").strip())
        for item in (thread.get("chips") or [])
        if cleanup_tr_punctuation(str(item or "").strip())
    ][:4]


def _mc_sign_from_chips(chips: Sequence[str]) -> str:
    for chip in chips:
        lower = chip.lower()
        if lower.startswith("mc "):
            return cleanup_tr_punctuation(chip[3:].strip())
        if lower.startswith("mc"):
            return cleanup_tr_punctuation(chip[2:].strip())
    return ""


def _visible_power_sign_vibe(sign: str) -> str:
    return {
        "Koç": "ataklık, cesaret ve doğrudanlık",
        "Boğa": "sakin güç, kalite ve güven",
        "İkizler": "zihinsel canlılık, temas ve akış",
        "Yengeç": "koruyuculuk, sezgi ve duygusal zeka",
        "Aslan": "özgüven, sıcaklık ve görünür karizma",
        "Başak": "incelik, düzen ve güven veren kalite",
        "Terazi": "denge, estetik ve ilişki zekâsı",
        "Akrep": "derinlik, manyetik etki ve sezgisel güç",
        "Yay": "ufuk, ilham ve geniş perspektif",
        "Oğlak": "ciddiyet, yapı ve kalıcı etki",
        "Kova": "özgünlük, fikir gücü ve farklı bakış",
        "Balık": "yumuşaklık, sezgi ve geçirgen çekim",
    }.get(sign, "belli bir ton ve ilişki biçimi")


def _family_tension_line(family: str) -> str:
    return {
        "visible_power": "Bu görünürlük hattında başka bir katman daha var: insanlar seni bazen yalnızca olduğun gibi değil, görmek istedikleri gibi de okuyabiliyor.",
        "mind_mechanics": "Bu yüzden insanlar dışarıda sakin bir zihin görse de içeride aynı anda birkaç şeyi tarttığını fark etmeyebiliyor.",
        "intimacy_guard": "Bu yüzden yakınlık sende yalnızca sevgiyle değil, güven eşiğiyle de açılıyor; bağ güçlenirken temkin de aynı anda çalışabiliyor.",
        "outer_inner_split": "Bu da dışarıda bıraktığın etki ile içeride yaşadığın ritim arasında zaman zaman belirgin bir fark yaratabiliyor.",
        "self_definition": "Bu çizgide insanlar sende çoğu zaman kim olduğunu değil, kendini nasıl taşıdığını da güçlü biçimde okuyor.",
        "placement_signature": "Bu yerleşim senden yalnızca belli bir özellik değil, belli bir davranış ritmi de çıkarıyor.",
        "tone_signature": "Bu ton sende yüzeyde bir özellik gibi görünse de altta çok daha derin bir eğilim çalıştırıyor.",
        "contradiction_core": "Bu temanın içinde iki ayrı yön aynı anda çalıştığı için bazen dışarıda çelişkili gibi okunman da mümkün.",
    }.get(
        family,
        "Bu çizgide görünen şey ile içeride çalışan şey her zaman aynı hızda ilerlemiyor.",
    )


def _family_origin_line(family: str) -> str:
    return {
        "visible_power": "Görülmek, ciddiye alınmak ve ürettiğin şeyin hakkıyla okunması bu yüzden sende sadece iş konusu değil; daha derin bir eşik gibi çalışabiliyor.",
        "mind_mechanics": "Zihninin önce içerde toparlanmak istemesi çoğu zaman fazla düşünmekten değil, doğru cümleyi bulma ihtiyacından geliyor.",
        "intimacy_guard": "Bu yüzden bağ kurarken yalnızca hissetmek yetmiyor; içinin gerçekten gevşediğini anlaman da gerekiyor.",
        "outer_inner_split": "İnsanların ilk gördüğü taraf ile senin kendini içeride yaşama biçimin bu yüzden farklı katmanlar taşıyabiliyor.",
        "self_definition": "Burada öğrenilen şey çoğu zaman başkalarının beklentisine göre şekil almak değil, kendi çizgisini içeriden netleştirmek oluyor.",
        "placement_signature": "Bu yerleşimin güçlü yanı kadar korunmak isteyen tarafı da var; bu yüzden tepkin çoğu zaman yalnızca anlık değil, daha eski bir iz de taşıyor.",
        "tone_signature": "Bu tonun altında çoğu zaman alışılmış bir refleks değil, zamanla öğrenilmiş bir korunma biçimi de çalışabiliyor.",
        "contradiction_core": "Bu çelişkinin zorlayıcı tarafı, iki ihtiyacın da gerçek olması; biri bastırıldığında diğeri de tam rahatlamıyor.",
    }.get(
        family,
        "Burada görünen davranışın altında daha eski ve daha köklü bir eşik de çalışıyor olabilir.",
    )


def _family_strength_line(family: str) -> str:
    return {
        "visible_power": "Senin görünürlüğün çoğu zaman gürültüyle değil, nüansla güçleniyor; doğru tavır, doğru zaman ve doğru bağ çok daha kalıcı iz bırakabiliyor.",
        "mind_mechanics": "İyi çalıştığında bu yapı sana sadece hız değil, güçlü bir ayıklama ve isabetli ifade becerisi de veriyor.",
        "intimacy_guard": "İyi çalıştığında bu yapı sana yüzeyde değil, gerçekten değen ve güven veren bir bağ kurma gücü veriyor.",
        "outer_inner_split": "Bu fark seni dağınık yapmıyor; tam tersine, hem dışarıda hem içeride ayrı ayrı güçlü kalabilen bir yapı kuruyor.",
        "self_definition": "İyi çalıştığında bu çizgi sende yalnızca dikkat çekmek değil, insanlarda net bir iz bırakmak anlamına geliyor.",
        "placement_signature": "Bu yerleşim doğru çalıştığında sende yalnızca özellik değil, güçlü bir ağırlık ve güven duygusu bırakıyor.",
        "tone_signature": "İyi çalıştığında bu ton sende yalnızca his değil, başkalarının da rahatça ayırt ettiği bir imza yaratıyor.",
        "contradiction_core": "Bu iki yön beraber çalıştığında seni dağıtmıyor; tam tersine seni daha katmanlı, daha sahici ve daha güçlü kılıyor.",
    }.get(
        family,
        "İyi çalıştığında bu tema sende yalnızca davranış değil, kalıcı bir etki de yaratıyor.",
    )


def _thread_astro_line(family: str, *, chips: Sequence[str], thread: Mapping[str, Any]) -> str:
    if family == "visible_power":
        mc_sign = _mc_sign_from_chips(chips)
        ruler = chips[1] if len(chips) > 1 else ""
        if mc_sign and ruler:
            return _clean_text(
                f"MC'nin {mc_sign} olması sende dışarıda {_visible_power_sign_vibe(mc_sign)} okunmasını kolaylaştırıyor; {ruler} vurgusu ise bu görünürlüğün önce içeride süzülüp sonra ortaya çıkmasına neden oluyor.",
                max_sentences=2,
                max_chars=280,
            )
        if mc_sign:
            return _clean_text(
                f"MC'nin {mc_sign} olması sende dışarıda {_visible_power_sign_vibe(mc_sign)} bırakıyor; bu yüzden insanlar sadece ne yaptığını değil, onu nasıl taşıdığını da fark ediyor.",
                max_sentences=2,
                max_chars=260,
            )
    return _family_astro_line(
        family,
        astro_sources=thread.get("astro_sources") if isinstance(thread.get("astro_sources"), list) else [],
        astro_hint=str(thread.get("astro_hint") or "").strip(),
        chips=chips,
    )


def _build_thread_editorial_scaffold(
    thread: Mapping[str, Any],
    *,
    family: str,
) -> list[str]:
    summary = _clean_text(
        thread.get("one_liner") or thread.get("summary") or "",
        max_sentences=2,
        max_chars=220,
    )
    sentences = _split_sentences(
        str(thread.get("paragraph") or thread.get("body") or "").strip(),
        max_sentences=5,
    )
    if summary and sentences and sentences[0].lower() == summary.lower():
        sentences = sentences[1:]
    chips = _chip_values(thread)
    opening = _first_non_empty(sentences[0] if sentences else "", summary)
    astro_line = _thread_astro_line(family, chips=chips, thread=thread)
    contextual_strength = _first_non_empty(
        sentences[2] if len(sentences) > 2 else "",
        sentences[1] if len(sentences) > 1 else "",
        thread.get("micro") or "",
        _family_strength_line(family),
    )
    family_strength = _family_strength_line(family)
    if family == "visible_power":
        contextual_strength = family_strength
    elif family_strength and family_strength.lower() not in contextual_strength.lower():
        if family == "visible_power" and "nüans" not in contextual_strength.lower():
            contextual_strength = _clean_text(
                f"{contextual_strength} {family_strength}",
                max_sentences=3,
                max_chars=320,
            )
    caption = _first_non_empty(thread.get("micro") or "", _family_caption_line(family))
    blocks = [
        opening or _family_strength_line(family),
        astro_line,
        _family_tension_line(family),
        _family_origin_line(family),
        contextual_strength,
        _family_growth_line(family),
        caption,
    ]
    return _normalize_blocks(blocks)


def _family_growth_line(family: str) -> str:
    return {
        "visible_power": "Asıl güç, başkalarının projeksiyonunu taşımadan net görünmek için kendini küçültmeyi bıraktığında büyüyor.",
        "mind_mechanics": "Asıl güç, hızını bastırmadan ama kendini yormadan daha net konuşabildiğinde belirginleşiyor.",
        "intimacy_guard": "Asıl rahatlama, yakınlık ile yük taşımayı aynı şey olmaktan çıkardığında geliyor.",
        "outer_inner_split": "Asıl denge, dışarıda bıraktığın iz ile içeride yaşadığın şeyi birbirine yaklaştırdığında kuruluyor.",
        "self_definition": "Asıl netlik, başkalarının seni nasıl okuduğundan çok kendi çizgine sadık kaldığında güçleniyor.",
        "placement_signature": "Asıl güç, bu tonu bastırmadan ama daha bilinçli taşımayı öğrendiğinde ortaya çıkıyor.",
        "tone_signature": "Bu ton sende doğal; mesele onu savunma yerine bilinçli bir ifade haline getirebilmek.",
        "contradiction_core": "Asıl denge, bu iki yönü birbirine karşı kullanmak yerine aynı sistemin parçası yapabildiğinde geliyor.",
    }.get(
        family,
        "Asıl güç, bu tarafını daha bilinçli ve daha net taşıyabildiğinde belirginleşiyor.",
    )


def _family_caption_line(family: str) -> str:
    return {
        "visible_power": "Senin etkin gürültüyle değil, ağırlık ve nüansla fark ediliyor.",
        "mind_mechanics": "Senin zihnin yalnızca hızlı değil; doğru çalıştığında yön de verebiliyor.",
        "intimacy_guard": "Senin sevme biçimin hafif değil; doğru yerde çok gerçek, çok derin ve çok sadık.",
        "outer_inner_split": "İnsanlar sende sadece duruşu değil, o duruşun altındaki hassas çizgiyi de hissediyor.",
        "self_definition": "İnsanlar sende yalnızca kim olduğunu değil, onu nasıl taşıdığını da okuyor.",
        "placement_signature": "Bu yerleşim sende sadece bir özellik değil, belli bir iz bırakma biçimi kuruyor.",
        "tone_signature": "Bu ton sende dikkat çekmek için değil; doğal olarak hissedildiği için iz bırakıyor.",
        "contradiction_core": "Bu çelişki seni zayıflatmıyor; doğru çalıştığında seni daha katmanlı ve daha gerçek kılıyor.",
    }.get(
        family,
        "Bu tema sende yalnızca görünmüyor; zamanla nasıl iz bıraktığını da belirliyor.",
    )


def _family_astro_line(
    family: str,
    *,
    astro_sources: Sequence[Any] | None = None,
    astro_hint: str = "",
    chips: Sequence[Any] | None = None,
) -> str:
    labels = _join_labels(astro_sources, limit=2)
    if not labels:
        labels = _join_labels(chips, limit=2)
    if labels:
        return {
            "visible_power": f"Bu görünürlük hattını en çok {labels} taşıyor.",
            "mind_mechanics": f"Bu zihinsel ritmi en çok {labels} hattı belirginleştiriyor.",
            "intimacy_guard": f"Bu yakınlık temasını en çok {labels} hattı açıyor.",
            "outer_inner_split": f"Bu dışarı-içeri farkını en çok {labels} çizgisi görünür kılıyor.",
            "self_definition": f"Bu ilk izlenim hattının altında en çok {labels} çalışıyor.",
            "placement_signature": f"Bu yerleşimin tonu en çok {labels} üzerinden okunuyor.",
            "tone_signature": f"Bu tonun omurgasında en çok {labels} hissediliyor.",
            "contradiction_core": f"Bu iki yönün birbirine sürtündüğü yer en çok {labels} hattında belirginleşiyor.",
        }.get(family, f"Bu temayı en çok {labels} hattı taşıyor.")
    return _clean_text(astro_hint, max_sentences=1, max_chars=180)


def build_editorial_detail_blocks_for_thread(
    thread: Mapping[str, Any],
) -> list[str]:
    explicit = _normalize_blocks(thread.get("detail_blocks"))
    if explicit:
        return explicit
    family = _infer_thread_family(thread)
    scaffold = _build_thread_editorial_scaffold(thread, family=family)
    if scaffold:
        return scaffold
    fallback = _split_sentences(
        str(thread.get("paragraph") or thread.get("body") or thread.get("one_liner") or "").strip(),
        max_sentences=4,
    )
    return _normalize_blocks(fallback)


def build_editorial_detail_blocks_for_profile_block(
    block: Mapping[str, Any],
    *,
    supporting_blocks: Sequence[Any] | None = None,
) -> list[str]:
    explicit = _normalize_blocks(block.get("detail_blocks"))
    if explicit:
        return explicit

    supporting = _normalize_blocks(supporting_blocks)
    if supporting:
        return supporting

    family = str(block.get("family") or "").strip()
    summary = _clean_text(
        block.get("teaser") or block.get("summary") or "",
        max_sentences=2,
        max_chars=220,
    )
    sentences = _split_sentences(str(block.get("body") or "").strip(), max_sentences=4)
    if summary and sentences and sentences[0].lower() == summary.lower():
        sentences = sentences[1:]
    astro_line = _family_astro_line(
        family,
        astro_sources=block.get("astro_sources") if isinstance(block.get("astro_sources"), list) else [],
        astro_hint=str(block.get("astro_hint") or "").strip(),
        chips=block.get("chips") if isinstance(block.get("chips"), list) else [],
    )
    growth = _family_growth_line(family)
    micro = _clean_text(block.get("micro") or "", max_sentences=1, max_chars=180)
    caption = micro if micro else _family_caption_line(family)

    blocks: list[str] = []
    if sentences:
        blocks.append(sentences[0])
    elif summary:
        blocks.append(summary)
    if astro_line:
        blocks.append(astro_line)
    if len(sentences) > 1:
        blocks.extend(sentences[1:])
    if growth:
        blocks.append(growth)
    if caption:
        blocks.append(caption)
    return _normalize_blocks(blocks)


def build_editorial_detail_blocks_for_imprint_entry(
    entry: Mapping[str, Any],
    *,
    support_entries_by_key: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[str]:
    kind = str(entry.get("kind") or "").strip()
    family = {
        "aspect": "contradiction_core",
        "sign_placement": "tone_signature",
    }.get(kind, "placement_signature")

    trait = _clean_text(entry.get("trait") or "", max_sentences=2, max_chars=240)
    drive = _clean_text(entry.get("drive") or "", max_sentences=2, max_chars=240)
    shadow = _clean_text(entry.get("shadow") or "", max_sentences=2, max_chars=240)
    gift = _clean_text(entry.get("gift") or "", max_sentences=2, max_chars=240)
    background = _clean_text(entry.get("background_hint") or "", max_sentences=2, max_chars=220)

    support_line = ""
    for key in entry.get("support_keys") or []:
        support = (support_entries_by_key or {}).get(str(key).strip())
        if not isinstance(support, Mapping):
            continue
        support_label = cleanup_tr_punctuation(str(support.get("label_tr") or "").strip())
        support_text = _clean_text(
            support.get("gift")
            or support.get("trait")
            or support.get("aura")
            or "",
            max_sentences=1,
            max_chars=180,
        )
        if support_label and support_text:
            support_line = _clean_text(
                f"Bu temayı {support_label} tarafı da güçlendiriyor; {support_text[0].lower() + support_text[1:] if len(support_text) > 1 else support_text.lower()}",
                max_sentences=2,
                max_chars=260,
            )
            break
        if support_text:
            support_line = support_text
            break

    blocks = [
        trait,
        drive,
        support_line,
        shadow,
        gift,
        background,
        _family_growth_line(family),
    ]
    return _normalize_blocks(blocks)
