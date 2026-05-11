// Profile v9 adapter — `/interpret/ui` payload'ını v9'un buzdağı modeline
// uygun yüzey + derinlik (Tam Okuma) data class'larına çeviren saf
// transformation katmanı.
//
// Tasarım kuralları:
//   • Pure — widget kodu YOK, sadece map → typed data dönüşümü.
//   • Null-safe — eksik alanlarda `null` veya boş liste döner, exception YOK.
//   • Conservative — payload şeması değişirse adapter düşmez, eksik bölüm
//     gelmez ama uygulama açık kalır.
//   • Frontend dökümante edilmiş §1-§7 plana sadık (default cevaplar
//     onaylanmış: tek Yükselen, 5 yüzey bölümü, conversation_hooks
//     konsolide, sections_v2 atlanır, detail_cards tek kaynak).
//
// Backend response yapısı (özet):
//   payload = { "public": { ... } }
//   public.profile_v8.{hero, identity_axis, insight_strip, differentiators,
//                      first_impression, archetype_portal, ...}
//   public.profile_narrative.profile_public.detail_cards[]
//   public.personality_imprint.entries[]   (içe-dönük zenginleştirme için)
//
// F3.1: sadece bu dosyayı yazıyoruz. F3.2'de profile_page_v9.dart bu
// adapter'ın çıktısını render edecek.

import 'package:mobile/app/profile/layered_kart.dart';

// ═══════════════════════════════════════════════════════════════════
// SURFACE (Yüzey) — 5 editöryal bölüm
// ═══════════════════════════════════════════════════════════════════

class V9HeroData {
  const V9HeroData({
    required this.displayName,
    required this.locationAge,
    required this.sunSign,
    required this.moonSign,
    required this.risingSign,
  });

  final String displayName;
  final String locationAge; // "İstanbul, Tr · 30 yaş"
  final String sunSign;
  final String moonSign;
  final String risingSign;
}

class V9IdentityQuote {
  const V9IdentityQuote({
    required this.eyebrow,
    required this.quoteHead,
    required this.quoteTailItalic,
    required this.subtitle,
  });

  /// "KİMLİK EKSENİ" — eyebrow.
  final String eyebrow;

  /// Quote'un düz (Inter) başlangıç kısmı.
  final String quoteHead;

  /// Quote'un italik (Fraunces) bitiş kısmı.
  final String quoteTailItalic;

  /// Quote altında ortalanmış sub-paragraph (≤2 cümle).
  final String subtitle;
}

class V9InsightTile {
  const V9InsightTile({
    required this.eyebrow,
    required this.title,
    required this.subtitle,
  });

  /// "AURA" / "YÖNETİCİ" / "İÇ RİTİM"
  final String eyebrow;

  /// Fraunces italic (örn. "Sessiz disiplin")
  final String title;

  /// Mono küçük (örn. "Toprak baskın · Öncü")
  final String subtitle;
}

class V9Differentiator {
  const V9Differentiator({
    required this.tone,
    required this.illust,
    required this.label,
    required this.core,
    this.cardLinkId,
  });

  final LayeredKartTone tone;
  final LayeredKartIllust illust;

  /// Layer 1 — orb/stellium etiketi (mono caps).
  /// Örn. "AY △ VENÜS · 0°14′" veya "5 GEZEGEN · 1. EV"
  final String label;

  /// Layer 2 — italik çekirdek cümle.
  /// Örn. "Estetik zeka doğuştan."
  final String core;

  /// Tap target — açılınca hangi Tam Okuma kartına gider.
  final String? cardLinkId;
}

class V9FirstImpression {
  const V9FirstImpression({
    required this.eyebrow,
    required this.headline,
    required this.body,
  });

  /// "İLK İZLENİM"
  final String eyebrow;

  /// Fraunces italik (örn. "Önce mesafeli görünür, sonra sıcak çıkar.")
  final String headline;

  /// Sans body — ilk izlenim açıklaması.
  final String body;
}

class V9SurfaceCta {
  const V9SurfaceCta({
    required this.eyebrow,
    required this.bodyHead,
    required this.bodyTailItalic,
  });

  /// "TAM OKUMA"
  final String eyebrow;

  /// "Derinleşmek için"
  final String bodyHead;

  /// "devam et" (Fraunces italik, lime accent)
  final String bodyTailItalic;
}

class ProfileV9SurfaceData {
  const ProfileV9SurfaceData({
    required this.hero,
    this.identityQuote,
    this.insightTiles = const [],
    this.differentiators = const [],
    this.firstImpression,
    this.cta,
  });

  final V9HeroData hero;
  final V9IdentityQuote? identityQuote;
  final List<V9InsightTile> insightTiles; // ≤3
  final List<V9Differentiator> differentiators; // ≤3
  final V9FirstImpression? firstImpression;
  final V9SurfaceCta? cta;

  bool get hasNarrativeContent =>
      identityQuote != null ||
      insightTiles.isNotEmpty ||
      differentiators.isNotEmpty ||
      firstImpression != null;
}

// ═══════════════════════════════════════════════════════════════════
// DEPTH (Tam Okuma) — 4 eksen × kart galerisi
// ═══════════════════════════════════════════════════════════════════

enum TamOkumaAxis { kimlik, iliski, kariyer, golge }

extension TamOkumaAxisLabel on TamOkumaAxis {
  String get label {
    switch (this) {
      case TamOkumaAxis.kimlik:
        return 'Kimlik';
      case TamOkumaAxis.iliski:
        return 'İlişki';
      case TamOkumaAxis.kariyer:
        return 'Kariyer';
      case TamOkumaAxis.golge:
        return 'Gölge';
    }
  }

  String get eye {
    switch (this) {
      case TamOkumaAxis.kimlik:
        return '01';
      case TamOkumaAxis.iliski:
        return '02';
      case TamOkumaAxis.kariyer:
        return '03';
      case TamOkumaAxis.golge:
        return '04';
    }
  }

  String get headerEye => '$label ekseni';
}

class V9TamOkumaIntro {
  const V9TamOkumaIntro({
    required this.eyebrow,
    required this.quoteHead,
    required this.quoteTailItalic,
    required this.subtitle,
  });

  final String eyebrow;
  final String quoteHead;
  final String quoteTailItalic;
  final String subtitle;
}

class ProfileV9TamOkumaData {
  const ProfileV9TamOkumaData({
    required this.cardsByAxis,
    required this.introByAxis,
    this.hiddenCount = 0,
  });

  final Map<TamOkumaAxis, List<LayeredKartData>> cardsByAxis;
  final Map<TamOkumaAxis, V9TamOkumaIntro> introByAxis;

  /// Yüzeyde gösterilen motiflerle eşleşip Tam Okuma'dan filtrelenen kart
  /// sayısı. Telemetry/debug için — UI'da gösterilmez.
  final int hiddenCount;

  bool get isEmpty => cardsByAxis.values.every((list) => list.isEmpty);
}

// ═══════════════════════════════════════════════════════════════════
// ROOT PAYLOAD WRAPPER
// ═══════════════════════════════════════════════════════════════════

class ProfileV9Data {
  const ProfileV9Data({required this.surface, required this.tamOkuma});

  final ProfileV9SurfaceData surface;
  final ProfileV9TamOkumaData tamOkuma;
}

// ═══════════════════════════════════════════════════════════════════
// ADAPTER ENTRY POINT
// ═══════════════════════════════════════════════════════════════════

class ProfileV9Adapter {
  const ProfileV9Adapter._();

  /// Ana giriş — hem `/interpret/ui` natal payload'ını hem Supabase profile
  /// map'ini alır, v9 surface + Tam Okuma data'sını üretir.
  static ProfileV9Data fromInputs({
    required Map<String, dynamic>? natalPayload,
    required Map<String, dynamic>? supabaseProfile,
    String? authDisplayName,
    String? authAvatarUrl,
  }) {
    final publicScope = _publicScope(natalPayload);
    final profileV8 = _asMap(publicScope['profile_v8']);
    final profileNarrative = _asMap(publicScope['profile_narrative']);
    final profilePublic = _asMap(profileNarrative['profile_public']);
    final detailCards = _asListOfMaps(profilePublic['detail_cards']);

    final hero = _buildHero(
      heroPayload: _asMap(profileV8['hero']),
      supabaseProfile: supabaseProfile,
      authDisplayName: authDisplayName,
    );
    final identityQuote = _buildIdentityQuote(
      identityAxis: _asMap(profileV8['identity_axis']),
      coreStoryUi: _asMap(publicScope['core_story_ui']),
    );
    final insightTiles = _buildInsightTiles(
      strip: _asListOfMaps(profileV8['insight_strip']),
      personalityImprint: _asMap(publicScope['personality_imprint']),
    );
    final differentiators = _buildDifferentiators(
      raw: _asListOfMaps(profileV8['differentiators']),
      detailCards: detailCards,
    );
    final firstImpression = _buildFirstImpression(
      _asMap(profileV8['first_impression']),
      conversationHooks: _asMap(profileV8['conversation_hooks']),
    );
    final cta = _buildCta(_asMap(profileV8['archetype_portal']));

    final surface = ProfileV9SurfaceData(
      hero: hero,
      identityQuote: identityQuote,
      insightTiles: insightTiles,
      differentiators: differentiators,
      firstImpression: firstImpression,
      cta: cta,
    );

    // Surface↔Depth dedupe: yüzeyde differentiator olarak gösterilen motiflerin
    // detail_card karşılığı varsa Tam Okuma'da TEKRAR göstermeyiz. Bu, "aynı
    // cümleyi iki yerde görme" hissini önler.
    final hiddenIds = <String>{
      for (final d in differentiators)
        if (d.cardLinkId != null && d.cardLinkId!.isNotEmpty) d.cardLinkId!,
    };

    final tamOkuma = _buildTamOkuma(
      detailCards: detailCards,
      hiddenIds: hiddenIds,
    );

    return ProfileV9Data(surface: surface, tamOkuma: tamOkuma);
  }

  // ── HERO ──────────────────────────────────────────────────────────

  static V9HeroData _buildHero({
    required Map<String, dynamic> heroPayload,
    required Map<String, dynamic>? supabaseProfile,
    String? authDisplayName,
  }) {
    final displayName = _firstNonEmpty([
      _asString(heroPayload['display_name']),
      _asString(supabaseProfile?['full_name']),
      _asString(supabaseProfile?['name']),
      authDisplayName,
    ]).isEmpty
        ? 'Profil'
        : _firstNonEmpty([
            _asString(heroPayload['display_name']),
            _asString(supabaseProfile?['full_name']),
            _asString(supabaseProfile?['name']),
            authDisplayName,
          ]);

    final locationAge =
        _asString(heroPayload['location_age']) ??
        _composeLocationAge(supabaseProfile);

    return V9HeroData(
      displayName: displayName,
      locationAge: locationAge,
      sunSign: _asString(heroPayload['sun_sign']) ?? '—',
      moonSign: _asString(heroPayload['moon_sign']) ?? '—',
      risingSign: _asString(heroPayload['rising_sign']) ?? '—',
    );
  }

  static String _composeLocationAge(Map<String, dynamic>? profile) {
    if (profile == null) return '';
    final city = _asString(profile['city']) ?? '';
    final country = _asString(profile['country']) ?? '';
    final birthDate = _asString(profile['birth_date']) ?? '';
    final parts = <String>[];
    if (city.isNotEmpty) {
      parts.add(country.isNotEmpty ? '$city, $country' : city);
    } else if (country.isNotEmpty) {
      parts.add(country);
    }
    if (birthDate.isNotEmpty) {
      final segs = birthDate.split('-');
      if (segs.length == 3) {
        final year = int.tryParse(segs[0]);
        if (year != null) {
          final age = DateTime.now().year - year;
          parts.add('$age yaş');
        }
      }
    }
    return parts.join(' · ');
  }

  // ── IDENTITY QUOTE ────────────────────────────────────────────────

  static V9IdentityQuote? _buildIdentityQuote({
    required Map<String, dynamic> identityAxis,
    required Map<String, dynamic> coreStoryUi,
  }) {
    final eyebrow =
        (_asString(identityAxis['eyebrow']) ?? 'KİMLİK EKSENİ').toUpperCase();

    // Önce identity_axis.headline, yoksa core_story_ui.headline.
    final raw = _asString(identityAxis['headline']) ??
        _asString(coreStoryUi['headline']);
    if (raw == null || raw.trim().isEmpty) return null;

    // İtalik split: cümleyi sondaki birkaç kelimeden böleriz; backend'in
    // "italik" semantiği yok, frontend tipografik tercih.
    final split = _splitForItalic(raw.trim());

    final subtitle = _trimToSentences(
          _asString(identityAxis['body']) ?? _asString(coreStoryUi['text']) ?? '',
          maxSentences: 2,
        ) ??
        '';

    return V9IdentityQuote(
      eyebrow: eyebrow,
      quoteHead: split.head,
      quoteTailItalic: split.tail,
      subtitle: subtitle,
    );
  }

  /// Cümleyi son N kelimeyi italik kalacak şekilde böler.
  /// Örn: "Güç sende zaten var." → head:"Güç sende", tail:"zaten var."
  static ({String head, String tail}) _splitForItalic(String sentence) {
    final words = sentence.split(RegExp(r'\s+'));
    if (words.length <= 2) {
      return (head: '', tail: sentence);
    }
    // Son 2-3 kelime italik (cümleye göre)
    final italicCount = words.length >= 5 ? 2 : 1;
    final headWords = words.sublist(0, words.length - italicCount);
    final tailWords = words.sublist(words.length - italicCount);
    return (head: headWords.join(' '), tail: tailWords.join(' '));
  }

  // ── INSIGHT STRIP (3 mini tile) ───────────────────────────────────

  static List<V9InsightTile> _buildInsightTiles({
    required List<Map<String, dynamic>> strip,
    required Map<String, dynamic> personalityImprint,
  }) {
    if (strip.isEmpty) return const [];

    return strip.take(3).map((cell) {
      return V9InsightTile(
        eyebrow: (_asString(cell['eyebrow']) ?? '').toUpperCase(),
        title: _asString(cell['title']) ?? '',
        subtitle: _asString(cell['subtitle']) ?? '',
      );
    }).toList(growable: false);
  }

  // ── DIFFERENTIATORS (3 nadir/güçlü an) ────────────────────────────

  static List<V9Differentiator> _buildDifferentiators({
    required List<Map<String, dynamic>> raw,
    required List<Map<String, dynamic>> detailCards,
  }) {
    if (raw.isEmpty) return const [];

    // Her differentiator'ı detail_cards içinde benzer family/headline ile
    // eşleştirip cardLinkId üretiriz (surface→depth navigation + dedupe için).
    return raw.take(3).toList(growable: false).asMap().entries.map((entry) {
      final i = entry.key;
      final d = entry.value;
      final eyebrow =
          (_asString(d['eyebrow']) ?? '').trim().toUpperCase();
      final headline = _asString(d['headline']) ?? '';
      final stat = (_asString(d['stat']) ?? '').trim();
      final statLabel = (_asString(d['stat_label']) ?? '').trim();
      // Layer 1 etiketi: eyebrow + stat varsa stat
      final label = stat.isNotEmpty
          ? (statLabel.isNotEmpty
              ? '$eyebrow · $stat'
              : '$eyebrow · $stat')
          : eyebrow;

      // Tone & illust pozisyona göre rotasyon — 3 farklı pastel ritim.
      final tone = _toneForDifferentiator(i, headline);
      final illust = _illustForDifferentiator(i, headline);

      // Surface→depth link: differentiator → detail_card (multi-signal match).
      final linkedCard = _findLinkedCard(
        headline: headline,
        eyebrow: eyebrow,
        cards: detailCards,
      );

      return V9Differentiator(
        tone: tone,
        illust: illust,
        label: label,
        core: headline,
        cardLinkId: linkedCard,
      );
    }).toList(growable: false);
  }

  static LayeredKartTone _toneForDifferentiator(int index, String headline) {
    // Heuristik: zihin/düşünce → lime, stellium/kimlik → lav, geçmiş → peach.
    final lower = headline.toLowerCase();
    if (lower.contains('zihin') ||
        lower.contains('estetik') ||
        lower.contains('kavuşum')) {
      return LayeredKartTone.lime;
    }
    if (lower.contains('geçmiş') ||
        lower.contains('dönüş') ||
        lower.contains('plüton')) {
      return LayeredKartTone.peach;
    }
    if (lower.contains('stellium') ||
        lower.contains('iç ses') ||
        lower.contains('sorumluluk')) {
      return LayeredKartTone.lav;
    }
    // Fallback: pozisyon rotasyonu
    return [
      LayeredKartTone.lime,
      LayeredKartTone.lav,
      LayeredKartTone.peach,
    ][index % 3];
  }

  static LayeredKartIllust _illustForDifferentiator(int index, String headline) {
    final lower = headline.toLowerCase();
    if (lower.contains('zihin') ||
        lower.contains('düşün') ||
        lower.contains('konj') ||
        lower.contains('kavuşum')) {
      return LayeredKartIllust.conj;
    }
    if (lower.contains('stellium') ||
        lower.contains('iç ses') ||
        lower.contains('sorumluluk') ||
        lower.contains('birden fazla')) {
      return LayeredKartIllust.stellium;
    }
    if (lower.contains('geçmiş') ||
        lower.contains('dönüş') ||
        lower.contains('katman')) {
      return LayeredKartIllust.past;
    }
    if (lower.contains('gerilim') ||
        lower.contains('kare') ||
        lower.contains('zıt')) {
      return LayeredKartIllust.square;
    }
    // Fallback: pozisyon rotasyonu
    return [
      LayeredKartIllust.conj,
      LayeredKartIllust.stellium,
      LayeredKartIllust.past,
    ][index % 3];
  }

  /// Differentiator → en yakın detail_card eşleştirmesi (multi-signal).
  ///
  /// 3 stratejide arar:
  ///   1. **Title prefix** — headline ilk anlamlı kelimesi card.title'da geçiyor mu?
  ///   2. **Astro-source overlap** — eyebrow'daki gezegen/açı token'ları
  ///      card.astro_sources ile ≥2 örtüşme veriyor mu? (örn. "AY △ VENÜS"
  ///      → ["Moon", "Venus"] eşleşmesi)
  ///   3. **Title contains** — card.title headline içinde tam geçiyor mu?
  ///
  /// İlk eşleşmede `card_key` veya `id` döner. Hiç eşleşme yoksa `null`.
  static String? _findLinkedCard({
    required String headline,
    required String eyebrow,
    required List<Map<String, dynamic>> cards,
  }) {
    if (cards.isEmpty) return null;
    final headlineLower = headline.toLowerCase().trim();
    final headlineFirstWord = _firstMeaningfulWord(headlineLower);

    // Eyebrow'dan astro token'ları çıkar (örn. "AY △ VENÜS · 0°14′" →
    // ["ay", "venus", "venüs"]). Sayılar/semboller atılır.
    final eyebrowTokens = <String>{};
    for (final piece
        in eyebrow.toLowerCase().split(RegExp(r'[\s·\u00b7,/+\-]+'))) {
      final cleaned = piece.replaceAll(RegExp(r'[°′″\d]+'), '').trim();
      if (cleaned.length >= 2 &&
          !RegExp(r'^[△□☌♂♀]$').hasMatch(cleaned)) {
        eyebrowTokens.add(cleaned);
      }
    }

    for (final card in cards) {
      final title = (_asString(card['title']) ?? '').toLowerCase();
      final cardId = _asString(card['card_key']) ?? _asString(card['id']);
      if (cardId == null) continue;

      // Strateji 1: title prefix headline'ın ilk kelimesi ile başlıyor mu?
      if (headlineFirstWord != null &&
          headlineFirstWord.length > 3 &&
          title.startsWith(headlineFirstWord)) {
        return cardId;
      }

      // Strateji 2: astro_sources ↔ eyebrow token overlap
      if (eyebrowTokens.isNotEmpty) {
        final astroLower = _asListOfStrings(card['astro_sources'])
            .map((s) => s.toLowerCase())
            .toSet();
        var overlap = 0;
        for (final t in eyebrowTokens) {
          if (astroLower.any((src) => src.contains(t))) overlap++;
        }
        if (overlap >= 2) return cardId;
      }

      // Strateji 3: title headline içinde tam geçiyor mu?
      if (title.length >= 4 && headlineLower.contains(title)) {
        return cardId;
      }
    }
    return null;
  }

  /// Headline başındaki ilk anlamlı (>3 karakter, alphabetic) kelime.
  static String? _firstMeaningfulWord(String text) {
    for (final word in text.split(RegExp(r'\s+'))) {
      final cleaned = word.replaceAll(RegExp(r'[^a-zçğıöşüâîû]'), '');
      if (cleaned.length > 3) return cleaned;
    }
    return null;
  }

  // ── FIRST IMPRESSION ──────────────────────────────────────────────

  /// İlk izlenim + conversation_hooks konsolide (default §5).
  static V9FirstImpression? _buildFirstImpression(
    Map<String, dynamic> firstImpression, {
    Map<String, dynamic> conversationHooks = const {},
  }) {
    final headline = _asString(firstImpression['headline']) ??
        _asString(conversationHooks['headline']) ??
        '';
    if (headline.trim().isEmpty) return null;

    final body = _asString(firstImpression['body']) ??
        _asString(conversationHooks['body']) ??
        '';

    return V9FirstImpression(
      eyebrow:
          (_asString(firstImpression['eyebrow']) ?? 'İLK İZLENİM').toUpperCase(),
      headline: headline,
      body: body,
    );
  }

  // ── CTA ───────────────────────────────────────────────────────────

  static V9SurfaceCta? _buildCta(Map<String, dynamic> archetypePortal) {
    final ctaLabel = _asString(archetypePortal['cta_label']) ?? '';
    if (ctaLabel.trim().isEmpty) {
      // Fallback: sabit CTA — derinliğe köprü her zaman görünmeli.
      return const V9SurfaceCta(
        eyebrow: 'TAM OKUMA',
        bodyHead: 'Derinleşmek için',
        bodyTailItalic: 'devam et',
      );
    }
    final split = _splitForItalic(ctaLabel.trim());
    return V9SurfaceCta(
      eyebrow: 'TAM OKUMA',
      bodyHead: split.head,
      bodyTailItalic: split.tail,
    );
  }

  // ── TAM OKUMA — family→axis dağıtımı ─────────────────────────────

  static ProfileV9TamOkumaData _buildTamOkuma({
    required List<Map<String, dynamic>> detailCards,
    Set<String> hiddenIds = const {},
  }) {
    final byAxis = <TamOkumaAxis, List<LayeredKartData>>{
      TamOkumaAxis.kimlik: [],
      TamOkumaAxis.iliski: [],
      TamOkumaAxis.kariyer: [],
      TamOkumaAxis.golge: [],
    };
    var hiddenCount = 0;

    for (final card in detailCards) {
      final family = _asString(card['family']) ?? '';
      final axis = _familyToAxis(family);
      if (axis == null) continue;

      final cardId = _asString(card['card_key']) ?? _asString(card['id']) ?? '';
      // Yüzeyde gösterilen motifleri Tam Okuma'da TEKRAR gösterme.
      if (cardId.isNotEmpty && hiddenIds.contains(cardId)) {
        hiddenCount++;
        continue;
      }

      final tone = _familyToTone(family);
      final illust = _familyToIllust(family);

      byAxis[axis]!.add(
        LayeredKartData(
          id: cardId.isNotEmpty ? cardId : 'card_${byAxis[axis]!.length}',
          tone: tone,
          illust: illust,
          label: _asListOfStrings(card['astro_sources']).join(' · '),
          core: _asString(card['title']) ?? '',
          eyebrow: _asString(card['eyebrow']),
          summary: _asString(card['summary']),
          body: _asString(card['body']),
          detailBlocks: _asListOfStrings(card['detail_blocks']),
          chips: _asListOfStrings(card['chips']),
          astroSources: _asListOfStrings(card['astro_sources']),
          family: family,
        ),
      );
    }

    final introByAxis = <TamOkumaAxis, V9TamOkumaIntro>{
      for (final axis in TamOkumaAxis.values)
        axis: _introForAxis(axis, byAxis[axis]!),
    };

    return ProfileV9TamOkumaData(
      cardsByAxis: byAxis,
      introByAxis: introByAxis,
      hiddenCount: hiddenCount,
    );
  }

  /// Backend `family` → 4 ekseninden biri.
  /// Plan §6'daki harita.
  static TamOkumaAxis? _familyToAxis(String family) {
    switch (family) {
      // Kimlik
      case 'self_definition':
      case 'mind_mechanics':
      case 'outer_inner_split':
      case 'contradiction_core':
      case 'tone_signature':
      case 'placement_signature':
        return TamOkumaAxis.kimlik;
      // İlişki
      case 'intimacy_guard':
      case 'desire_style':
      case 'relational_pattern_bundle':
        return TamOkumaAxis.iliski;
      // Kariyer
      case 'visible_power':
      case 'creative_channel':
        return TamOkumaAxis.kariyer;
      // Gölge
      case 'protection_pattern':
      case 'retreat_recharge':
      case 'control_vs_flow':
        return TamOkumaAxis.golge;
      default:
        return null;
    }
  }

  static LayeredKartTone _familyToTone(String family) {
    switch (family) {
      case 'mind_mechanics':
      case 'creative_channel':
        return LayeredKartTone.lime;
      case 'visible_power':
      case 'desire_style':
      case 'control_vs_flow':
        return LayeredKartTone.peach;
      case 'intimacy_guard':
      case 'retreat_recharge':
        return LayeredKartTone.blush;
      case 'self_definition':
      case 'outer_inner_split':
      case 'contradiction_core':
      case 'protection_pattern':
      case 'placement_signature':
      case 'tone_signature':
      case 'relational_pattern_bundle':
      default:
        return LayeredKartTone.lav;
    }
  }

  static LayeredKartIllust _familyToIllust(String family) {
    switch (family) {
      case 'self_definition':
      case 'placement_signature':
      case 'tone_signature':
        return LayeredKartIllust.opening;
      case 'mind_mechanics':
        return LayeredKartIllust.conj;
      case 'outer_inner_split':
      case 'contradiction_core':
      case 'protection_pattern':
        return LayeredKartIllust.square;
      case 'intimacy_guard':
      case 'desire_style':
      case 'relational_pattern_bundle':
        return LayeredKartIllust.opening;
      case 'visible_power':
      case 'creative_channel':
        return LayeredKartIllust.nn;
      case 'retreat_recharge':
      case 'control_vs_flow':
        return LayeredKartIllust.past;
      default:
        return LayeredKartIllust.opening;
    }
  }

  static V9TamOkumaIntro _introForAxis(
    TamOkumaAxis axis,
    List<LayeredKartData> cards,
  ) {
    // İlk kart varsa intro'yu onun başlığından türet — yoksa default fallback.
    if (cards.isNotEmpty) {
      final lead = cards.first;
      final split = _splitForItalic(lead.core);
      return V9TamOkumaIntro(
        eyebrow: axis.headerEye.toUpperCase(),
        quoteHead: split.head,
        quoteTailItalic: split.tail,
        subtitle: lead.summary ?? lead.body?.split('.').first ?? '',
      );
    }
    return V9TamOkumaIntro(
      eyebrow: axis.headerEye.toUpperCase(),
      quoteHead: '',
      quoteTailItalic: 'Bu eksen henüz hazır değil.',
      subtitle: '',
    );
  }

  // ── HELPERS ───────────────────────────────────────────────────────

  static Map<String, dynamic> _publicScope(Map<String, dynamic>? payload) {
    if (payload == null) return const {};
    final pub = payload['public'];
    if (pub is Map<String, dynamic>) return pub;
    return payload; // Bazı endpoint'ler public wrap'siz döner
  }

  static Map<String, dynamic> _asMap(Object? value) {
    if (value is Map<String, dynamic>) return value;
    if (value is Map) {
      return value.map((k, v) => MapEntry(k.toString(), v));
    }
    return const {};
  }

  static List<Map<String, dynamic>> _asListOfMaps(Object? value) {
    if (value is! List) return const [];
    return value
        .whereType<Map>()
        .map((m) => m.map((k, v) => MapEntry(k.toString(), v)))
        .toList(growable: false);
  }

  static List<String> _asListOfStrings(Object? value) {
    if (value is! List) return const [];
    return value
        .map((e) => e?.toString() ?? '')
        .where((s) => s.isNotEmpty)
        .toList(growable: false);
  }

  static String? _asString(Object? value) {
    if (value == null) return null;
    final s = value.toString();
    return s.isEmpty ? null : s;
  }

  static String _firstNonEmpty(List<String?> candidates) {
    for (final c in candidates) {
      if (c != null && c.trim().isNotEmpty) return c.trim();
    }
    return '';
  }

  static String? _trimToSentences(String text, {required int maxSentences}) {
    if (text.trim().isEmpty) return null;
    final sentences = text.split(RegExp(r'(?<=[.!?])\s+'));
    if (sentences.length <= maxSentences) return text.trim();
    return sentences.take(maxSentences).join(' ').trim();
  }
}
