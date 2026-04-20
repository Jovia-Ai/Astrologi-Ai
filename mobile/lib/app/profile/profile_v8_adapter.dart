import 'package:flutter/material.dart';

@immutable
class ProfileV8InsightCell {
  const ProfileV8InsightCell({
    required this.label,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.tint,
  });

  final String label;
  final String title;
  final String subtitle;
  final IconData icon;
  final Color tint;
}

@immutable
class ProfileV8PastLayer {
  const ProfileV8PastLayer({
    required this.eyebrow,
    required this.placement,
    required this.headline,
    required this.body,
    this.highlight = '',
  });

  final String eyebrow;
  final String placement;
  final String headline;
  final String body;
  final String highlight;

  bool get hasContent {
    return headline.trim().isNotEmpty || body.trim().isNotEmpty;
  }
}

@immutable
class ProfileV8Differentiator {
  const ProfileV8Differentiator({
    required this.eyebrow,
    required this.headline,
    required this.body,
    required this.stat,
    required this.statLabel,
    required this.accent,
  });

  final String eyebrow;
  final String headline;
  final String body;
  final String stat;
  final String statLabel;
  final String accent;

  bool get hasContent {
    return headline.trim().isNotEmpty ||
        eyebrow.trim().isNotEmpty ||
        stat.trim().isNotEmpty;
  }
}

@immutable
class ProfileV8Talent {
  const ProfileV8Talent({
    required this.eyebrow,
    required this.headline,
    required this.accent,
  });

  final String eyebrow;
  final String headline;
  final String accent;

  bool get hasContent {
    return eyebrow.trim().isNotEmpty || headline.trim().isNotEmpty;
  }
}

@immutable
class ProfileV8TextSection {
  const ProfileV8TextSection({
    required this.eyebrow,
    required this.headline,
    required this.body,
    this.bullets = const <String>[],
    this.chips = const <String>[],
    this.callout,
    this.footer,
    this.cta,
    this.growth,
    this.proofRaw = '',
  });

  final String eyebrow;
  final String headline;
  final String body;
  final List<String> bullets;
  final List<String> chips;
  final String? callout;
  final String? footer;
  final String? cta;
  final String? growth;

  /// Thread-level astrological credit line (voice spec v2.1 §11.4).
  /// Title Case, middle-dot separator: "Satürn · 3. ev · Oğlak".
  /// Empty string when backend omits or thread is not live.
  final String proofRaw;

  bool get hasContent {
    return headline.trim().isNotEmpty ||
        body.trim().isNotEmpty ||
        bullets.isNotEmpty ||
        chips.isNotEmpty ||
        (callout ?? '').trim().isNotEmpty ||
        (footer ?? '').trim().isNotEmpty ||
        (cta ?? '').trim().isNotEmpty ||
        (growth ?? '').trim().isNotEmpty;
  }
}

@immutable
class ProfileV8Data {
  const ProfileV8Data({
    required this.identityQuote,
    required this.topInsights,
    this.uniqueBlock,
    this.differentiators = const <ProfileV8Differentiator>[],
    this.originSection,
    this.pastLayers = const <ProfileV8PastLayer>[],
    this.firstImpressionSection,
    this.talents = const <String>[],
    this.talentItems = const <ProfileV8Talent>[],
    this.conversationSection,
    this.effectSection,
    this.defenseSection,
    this.firstFeltSection,
    this.collectiveSection,
    this.intimacySection,
    this.mindSection,
    this.ctaSection,
    this.skippedSectionKeys = const <String>[],
  });

  final String identityQuote;
  final List<ProfileV8InsightCell> topInsights;
  final ProfileV8TextSection? uniqueBlock;
  final List<ProfileV8Differentiator> differentiators;
  final ProfileV8TextSection? originSection;
  final List<ProfileV8PastLayer> pastLayers;
  final ProfileV8TextSection? firstImpressionSection;
  final List<String> talents;
  final List<ProfileV8Talent> talentItems;
  final ProfileV8TextSection? conversationSection;
  final ProfileV8TextSection? effectSection;
  final ProfileV8TextSection? defenseSection;
  final ProfileV8TextSection? firstFeltSection;
  final ProfileV8TextSection? collectiveSection;
  final ProfileV8TextSection? intimacySection;
  final ProfileV8TextSection? mindSection;
  final ProfileV8TextSection? ctaSection;
  final List<String> skippedSectionKeys;

  bool get hasRenderableContent {
    return identityQuote.trim().isNotEmpty ||
        topInsights.any(
          (item) =>
              item.title.trim().isNotEmpty || item.subtitle.trim().isNotEmpty,
        ) ||
        uniqueBlock?.hasContent == true ||
        differentiators.isNotEmpty ||
        originSection?.hasContent == true ||
        firstImpressionSection?.hasContent == true ||
        talents.isNotEmpty ||
        talentItems.isNotEmpty ||
        conversationSection?.hasContent == true ||
        effectSection?.hasContent == true ||
        defenseSection?.hasContent == true ||
        firstFeltSection?.hasContent == true ||
        collectiveSection?.hasContent == true ||
        intimacySection?.hasContent == true ||
        mindSection?.hasContent == true ||
        ctaSection?.hasContent == true;
  }
}

class ProfileV8Adapter {
  const ProfileV8Adapter._();

  static const List<String> _internalKeyBlocklist = <String>[
    '_bundle',
    '_pattern',
    '_internal',
    '_debug',
    'relational_pattern_bundle',
    'angle_identity_bundle',
    'soft_capacity_bundle',
  ];

  static const Map<String, String> _archetypeLabelByKey = <String, String>{
    'relational_pattern_bundle': 'İlişki akışı',
    'angle_identity_bundle': 'Kimlik ekseni',
    'soft_capacity_bundle': 'Yumuşak kapasite',
  };

  static ProfileV8Data fromPayload({
    required Map<String, dynamic>? payload,
    required Map<String, dynamic>? fastPayload,
    required String identityHeadline,
    required String identitySummary,
    required List<String> identityDrivers,
    required String dominantElementLabel,
    required Iterable<Map<String, dynamic>> narrativeCards,
    required Iterable<Map<String, dynamic>> insightModules,
    required Iterable<Map<String, dynamic>> supportingThreads,
  }) {
    final map = payload ?? const <String, dynamic>{};
    final publicScope = _asMap(map['public']);
    final metaScope = _asMap(map['meta_info']);
    final profileV8 = _firstNonEmptyMap(<Map<String, dynamic>>[
      _pathMap(publicScope, const ['profile_v8']),
      _pathMap(map, const ['profile_v8']),
      _pathMap(metaScope, const ['profile_v8']),
    ]);

    final profilePublic = _firstNonEmptyMap(<Map<String, dynamic>>[
      _pathMap(map, const ['profile_narrative', 'profile_public']),
      _pathMap(publicScope, const ['profile_narrative', 'profile_public']),
      _pathMap(metaScope, const ['profile_narrative', 'profile_public']),
    ]);

    final cards = _dedupeCards(<Map<String, dynamic>>[
      ...narrativeCards.map(_normalizeCard),
      ..._readCardField(profilePublic, 'core_blocks'),
      ..._readCardField(profilePublic, 'extra_blocks'),
      ..._readCardField(profilePublic, 'detail_cards'),
      ..._readCardField(profilePublic, 'blocks'),
    ]);

    final modules = _dedupeByIdentity(<Map<String, dynamic>>[
      ...insightModules.map(_normalizeModule),
      ..._asListOfMaps(profilePublic['insight_modules']).map(_normalizeModule),
    ], (item) => _identityKey(item, const ['module_id', 'headline', 'title']));

    final threads = _dedupeByIdentity(<Map<String, dynamic>>[
      ...supportingThreads.map(_normalizeThread),
      ..._readThreadField(map, 'sections_v2').map(_normalizeThread),
      ..._readThreadField(publicScope, 'sections_v2').map(_normalizeThread),
      ..._readThreadField(metaScope, 'sections_v2').map(_normalizeThread),
      ..._readThreadField(map, 'supporting_threads').map(_normalizeThread),
      ..._readThreadField(
        publicScope,
        'supporting_threads',
      ).map(_normalizeThread),
      ..._readThreadField(
        metaScope,
        'supporting_threads',
      ).map(_normalizeThread),
    ], (item) => _identityKey(item, const ['id', 'title', 'subtitle']));

    final personalityImprint = _firstNonEmptyMap(<Map<String, dynamic>>[
      _asMap(map['personality_imprint']),
      _asMap(publicScope['personality_imprint']),
      _asMap(metaScope['personality_imprint']),
    ]);

    final entries = <Map<String, dynamic>>[
      ..._asListOfMaps(personalityImprint['entries']),
      ..._asListOfMaps(personalityImprint['support_entries']),
      ..._asListOfMaps(personalityImprint['extra_entries']),
    ];
    final extraEntries = _asListOfMaps(personalityImprint['extra_entries']);

    final quote = _shortenForProfile(
      _firstText(<dynamic>[
            _pathValue(publicScope, const ['narrative_anchor', 'text']),
            _pathValue(publicScope, const ['narrative_anchor', 'summary']),
            _pathValue(publicScope, const ['core_story_ui', 'text']),
            publicScope['core_story'],
            publicScope['upper_meaning'],
            _pathValue(map, const ['core_story_ui', 'text']),
            map['core_story'],
            map['upper_meaning'],
            identityHeadline,
            identitySummary,
          ]) ??
          '',
      limit: 260,
    );

    final auraEntry = _firstMapWhere(
      entries,
      (item) =>
          safeText(item['aura']) != null ||
          safeText(item['label_tr']) != null ||
          safeText(item['label']) != null,
    );

    final fastMap = fastPayload ?? const <String, dynamic>{};
    final fastProfile = _asMap(fastMap['profile_fast']);
    final houseOne = _pathMap(map, const [
      'natal_graph_compact',
      'house_rulers',
      '1',
    ]);
    final rulerRaw = _firstText(<dynamic>[
      fastProfile['chart_ruler'],
      houseOne['primary_ruler'],
    ]);
    final rulerHouseRaw = _firstText(<dynamic>[
      fastProfile['chart_ruler_house'],
      houseOne['primary_house'],
    ]);

    final topInsights = <ProfileV8InsightCell>[
      ProfileV8InsightCell(
        label: 'Aura',
        title:
            _humanizeInsightText(
              _firstText(<dynamic>[
                    auraEntry['aura'],
                    _pathValue(publicScope, const ['meta_summary', 'identity']),
                    dominantElementLabel,
                  ]) ??
                  '',
            ).isEmpty
            ? 'Auran net'
            : _humanizeInsightText(
                _firstText(<dynamic>[
                      auraEntry['aura'],
                      _pathValue(publicScope, const [
                        'meta_summary',
                        'identity',
                      ]),
                      dominantElementLabel,
                    ]) ??
                    '',
              ),
        subtitle: _humanizeInsightText(
          _firstText(<dynamic>[
                auraEntry['label_tr'],
                auraEntry['label'],
                _pathValue(publicScope, const ['narrative_anchor', 'domain']),
              ]) ??
              '',
        ),
        icon: Icons.blur_on_rounded,
        tint: const Color(0xFFD2F2A0),
      ),
      ProfileV8InsightCell(
        label: 'Yönetici',
        title:
            _humanizeInsightText(_planetLabelTr(rulerRaw ?? '') ?? '').isEmpty
            ? 'Yönetici etki'
            : _humanizeInsightText(_planetLabelTr(rulerRaw ?? '') ?? ''),
        subtitle: rulerHouseRaw == null || rulerHouseRaw.trim().isEmpty
            ? 'Kimlik çizgini tutarlı kılıyor.'
            : '${rulerHouseRaw.trim()}. ev',
        icon: Icons.public_rounded,
        tint: const Color(0xFFF0F0F3),
      ),
      ProfileV8InsightCell(
        label: 'İç ritim',
        title:
            _humanizeInsightText(
              _firstText(<dynamic>[
                    identityDrivers.isNotEmpty ? identityDrivers.first : null,
                    _pathValue(publicScope, const [
                      'meaning_weighting',
                      'primary_theme',
                    ]),
                    _pathValue(publicScope, const ['meta_summary', 'theme']),
                  ]) ??
                  '',
            ).isEmpty
            ? 'Ritmin dengeli'
            : _humanizeInsightText(
                _firstText(<dynamic>[
                      identityDrivers.isNotEmpty ? identityDrivers.first : null,
                      _pathValue(publicScope, const [
                        'meaning_weighting',
                        'primary_theme',
                      ]),
                      _pathValue(publicScope, const ['meta_summary', 'theme']),
                    ]) ??
                    '',
              ),
        subtitle: _humanizeInsightText(
          _firstText(<dynamic>[
                identityDrivers.length > 1 ? identityDrivers[1] : null,
                _pathValue(publicScope, const ['meta_summary', 'summary']),
                _pathValue(publicScope, const ['narrative_anchor', 'domain']),
              ]) ??
              '',
        ),
        icon: Icons.graphic_eq_rounded,
        tint: const Color(0xFFDDD8FC),
      ),
    ];

    final uniqueCard = _pickCard(
      cards,
      families: const <String>{
        'outer_inner_split',
        'self_definition',
        'identity',
        'contradiction_core',
      },
      keywords: const <String>[
        'kimlik',
        'farklı',
        'farkli',
        'dışarıdan',
        'disaridan',
      ],
    );

    final uniqueBlock = _makeSection(
      eyebrow: 'SENİ FARKLI KILAN',
      headlineCandidates: <dynamic>[
        uniqueCard?['title'],
        identityHeadline,
        personalityImprint['headline'],
        entries.isNotEmpty ? entries.first['label_tr'] : null,
      ],
      bodyCandidates: <dynamic>[
        uniqueCard?['summary'],
        uniqueCard?['body'],
        identitySummary,
        _pathValue(publicScope, const ['core_story_ui', 'text']),
        publicScope['core_story'],
        publicScope['upper_meaning'],
      ],
      bulletCandidates: <dynamic>[
        entries.isNotEmpty
            ? <dynamic>[
                entries.first['trait'],
                entries.first['drive'],
                entries.first['gift'],
                entries.first['shadow'],
              ]
            : null,
      ],
      chipCandidates: <dynamic>[uniqueCard?['chips'], identityDrivers],
    );

    final originCard = _pickCard(
      cards,
      families: const <String>{'protection_pattern'},
      keywords: const <String>[
        'geçmiş',
        'gecmis',
        'kök',
        'kok',
        'saturn',
        '12. ev',
        '12th',
        'neden',
      ],
      excluded: <String>{_cardIdentity(uniqueCard)},
    );
    final originThread = _pickThread(
      threads,
      keywords: const <String>['geçmiş', 'gecmis', 'neden', 'kök', 'kok'],
    );
    final originSection = _makeSection(
      eyebrow: 'BU NEREDEN GELİYOR OLABİLİR',
      headlineCandidates: <dynamic>[
        originCard?['title'],
        originThread?['title'],
      ],
      bodyCandidates: <dynamic>[
        extraEntries.isNotEmpty ? extraEntries.first['background_hint'] : null,
        extraEntries.isNotEmpty ? extraEntries.first['shadow'] : null,
        originCard?['summary'],
        originCard?['body'],
        originThread?['body'],
        originThread?['subtitle'],
      ],
      bulletCandidates: <dynamic>[
        originThread?['detail_blocks'],
        originCard?['detail_blocks'],
      ],
      chipCandidates: <dynamic>[
        originCard?['chips'],
        extraEntries.isNotEmpty ? extraEntries.first['tags'] : null,
      ],
      proofRawCandidates: <dynamic>[originThread?['proof_raw']],
    );

    final firstImpressionCard = _pickCard(
      cards,
      families: const <String>{'outer_inner_split'},
      keywords: const <String>[
        'ilk izlenim',
        'ilk hissedilen',
        'disaridan',
        'dışarıdan',
        'insanlar sende',
      ],
      excluded: <String>{_cardIdentity(uniqueCard), _cardIdentity(originCard)},
    );
    final firstImpressionSection = _makeSection(
      eyebrow: 'İLK İZLENİM',
      headlineCandidates: <dynamic>[firstImpressionCard?['title']],
      bodyCandidates: <dynamic>[
        firstImpressionCard?['summary'],
        firstImpressionCard?['body'],
      ],
      bulletCandidates: <dynamic>[firstImpressionCard?['detail_blocks']],
      chipCandidates: <dynamic>[firstImpressionCard?['chips']],
    );

    final talents = _buildTalents(
      publicScope: publicScope,
      profilePublic: profilePublic,
      cards: cards,
    );

    final conversationThread = _pickThread(
      threads,
      keywords: const <String>[
        'konuş',
        'konus',
        'sohbet',
        'iletişim',
        'iletisim',
      ],
    );
    final conversationCard = _pickCard(
      cards,
      keywords: const <String>[
        'konuş',
        'konus',
        'sohbet',
        'iletişim',
        'iletisim',
      ],
    );
    final conversationSection = _makeSection(
      eyebrow: 'BU KİŞİYLE NE KONUŞULUR',
      headlineCandidates: <dynamic>[
        conversationThread?['title'],
        conversationCard?['title'],
      ],
      bodyCandidates: <dynamic>[
        conversationThread?['body'],
        conversationThread?['subtitle'],
        conversationCard?['summary'],
        conversationCard?['body'],
      ],
      bulletCandidates: <dynamic>[
        conversationThread?['detail_blocks'],
        conversationCard?['detail_blocks'],
      ],
      chipCandidates: <dynamic>[
        conversationThread?['chips'],
        conversationCard?['chips'],
      ],
      proofRawCandidates: <dynamic>[conversationThread?['proof_raw']],
    );

    final effectThread = _pickThread(
      threads,
      keywords: const <String>['etki', 'etkiler', 'hisset', 'duygu'],
    );
    final effectCard = _pickCard(
      cards,
      keywords: const <String>['etki', 'etkiler', 'hisset', 'duygu'],
      families: const <String>{'contradiction_core'},
    );
    final effectSection = _makeSection(
      eyebrow: 'SENİ NASIL ETKİLER',
      headlineCandidates: <dynamic>[
        effectThread?['title'],
        effectCard?['title'],
      ],
      bodyCandidates: <dynamic>[
        effectThread?['subtitle'],
        effectCard?['summary'],
        effectCard?['body'],
      ],
      bulletCandidates: <dynamic>[
        effectThread?['detail_blocks'],
        effectCard?['detail_blocks'],
      ],
      chipCandidates: <dynamic>[effectCard?['chips']],
      footerCandidates: <dynamic>[effectThread?['body']],
      proofRawCandidates: <dynamic>[effectThread?['proof_raw']],
    );

    final defenseModule = _pickModule(
      modules,
      keywords: const <String>['savunma', 'koru', 'defense', 'protection'],
    );
    final defenseCard = _pickCard(
      cards,
      families: const <String>{'protection_pattern'},
      keywords: const <String>['savunma', 'koru', 'tetikte', 'zorlandığında'],
    );
    final defenseSection = _makeSection(
      eyebrow: 'SAVUNMA MEKANİZMAN',
      headlineCandidates: <dynamic>[
        defenseModule?['title'],
        defenseModule?['headline'],
        defenseCard?['title'],
      ],
      bodyCandidates: <dynamic>[
        defenseModule?['body'],
        defenseModule?['subheadline'],
        defenseCard?['summary'],
        defenseCard?['body'],
      ],
      bulletCandidates: <dynamic>[defenseCard?['detail_blocks']],
      chipCandidates: <dynamic>[defenseCard?['chips']],
    );

    final firstFeltCard = _pickCard(
      cards,
      keywords: const <String>[
        'ilk hissedilen',
        'ilk his',
        'insanların sende ilk fark ettiği',
      ],
      excluded: <String>{_cardIdentity(firstImpressionCard)},
    );
    final firstFeltSection = _makeSection(
      eyebrow: 'İLK HİSSEDİLEN ŞEY',
      headlineCandidates: <dynamic>[firstFeltCard?['title']],
      bodyCandidates: <dynamic>[
        firstFeltCard?['summary'],
        firstFeltCard?['body'],
      ],
      bulletCandidates: <dynamic>[firstFeltCard?['detail_blocks']],
      chipCandidates: <dynamic>[firstFeltCard?['chips']],
    );

    final collective = _firstNonEmptyMap(<Map<String, dynamic>>[
      _asMap(map['collective']),
      _asMap(publicScope['collective']),
      _asMap(metaScope['collective']),
    ]);
    final collectiveSection = _makeSection(
      eyebrow: 'KOLEKTİFTEN',
      headlineCandidates: <dynamic>[
        collective['title'],
        collective['headline'],
        collective['summary_tr'],
      ],
      bodyCandidates: <dynamic>[
        collective['summary_tr'],
        collective['summary'],
      ],
      bulletCandidates: <dynamic>[
        _asListOfMaps(collective['items'])
            .map(
              (item) => safeText(item['summary_tr']) ?? safeText(item['title']),
            )
            .whereType<String>()
            .toList(),
      ],
    );

    final intimacyCard = _pickCard(
      cards,
      families: const <String>{'intimacy_guard'},
      keywords: const <String>['yakınlık', 'yakinlik', 'ilişki', 'iliski'],
    );
    final intimacyThread = _pickThread(
      threads,
      keywords: const <String>['yakınlık', 'yakinlik', 'ilişki', 'iliski'],
    );
    final intimacySection = _makeSection(
      eyebrow: 'YAKINLIK',
      headlineCandidates: <dynamic>[
        intimacyCard?['title'],
        intimacyThread?['title'],
      ],
      bodyCandidates: <dynamic>[
        intimacyCard?['summary'],
        intimacyCard?['body'],
        intimacyThread?['subtitle'],
        intimacyThread?['body'],
      ],
      bulletCandidates: <dynamic>[
        intimacyThread?['detail_blocks'],
        intimacyCard?['detail_blocks'],
      ],
      chipCandidates: <dynamic>[
        intimacyCard?['chips'],
        intimacyThread?['chips'],
      ],
      proofRawCandidates: <dynamic>[intimacyThread?['proof_raw']],
    );

    final mindCard = _pickCard(
      cards,
      families: const <String>{'mind_mechanics'},
      keywords: const <String>['zihin', 'zihinsel', 'mind', 'mental'],
    );
    final mindThread = _pickThread(
      threads,
      keywords: const <String>['zihin', 'zihinsel', 'mind', 'mental'],
      preferredIds: const <String>['mind_system', 'mind_mechanics'],
    );
    final mindSection = _makeSection(
      eyebrow: 'ZİHİNSEL İŞLEYİŞ',
      headlineCandidates: <dynamic>[mindCard?['title'], mindThread?['title']],
      bodyCandidates: <dynamic>[
        mindCard?['summary'],
        mindCard?['body'],
        mindThread?['subtitle'],
        mindThread?['body'],
      ],
      bulletCandidates: <dynamic>[
        mindThread?['detail_blocks'],
        mindCard?['detail_blocks'],
      ],
      chipCandidates: <dynamic>[mindCard?['chips'], mindThread?['chips']],
      proofRawCandidates: <dynamic>[mindThread?['proof_raw']],
    );

    final bundleLabels =
        _asListOfMaps(
              _pathValue(publicScope, const [
                'narrative_v2',
                'aspect_bundle_selector',
                'selected_bundles',
              ]),
            )
            .map(
              (item) =>
                  safeText(item['bundle_type']) ?? safeText(item['bundle_id']),
            )
            .whereType<String>()
            .toList();

    final ctaSection = _makeSection(
      eyebrow: 'ARKETİP PORTALI',
      headlineCandidates: <dynamic>[
        _pathValue(publicScope, const ['cta', 'headline']),
        'Seni yöneten eksenleri birlikte gör.',
      ],
      bodyCandidates: <dynamic>[
        _pathValue(publicScope, const ['cta', 'body']),
        _firstText(bundleLabels),
        'Kimlik · Savunma · Yakınlık · Zihin',
      ],
      chipCandidates: <dynamic>[bundleLabels],
      ctaCandidates: <dynamic>[
        _pathValue(publicScope, const ['cta', 'label']),
        'Arketip akışını aç →',
      ],
    );

    final skipped = <String>[];
    void track(String key, ProfileV8TextSection? section) {
      if (section == null || !section.hasContent) {
        skipped.add(key);
      }
    }

    track('unique', uniqueBlock);
    track('origin', originSection);
    track('first_impression', firstImpressionSection);
    if (talents.isEmpty) {
      skipped.add('talents');
    }
    track('conversation', conversationSection);
    track('effect', effectSection);
    track('defense', defenseSection);
    track('first_felt', firstFeltSection);
    track('collective', collectiveSection);
    track('intimacy', intimacySection);
    track('mind', mindSection);

    final legacyData = ProfileV8Data(
      identityQuote: quote,
      topInsights: topInsights,
      uniqueBlock: uniqueBlock,
      originSection: originSection,
      firstImpressionSection: firstImpressionSection,
      talents: talents,
      conversationSection: conversationSection,
      effectSection: effectSection,
      defenseSection: defenseSection,
      firstFeltSection: firstFeltSection,
      collectiveSection: collectiveSection,
      intimacySection: intimacySection,
      mindSection: mindSection,
      ctaSection: ctaSection,
      skippedSectionKeys: skipped,
    );

    if (profileV8.isNotEmpty) {
      final v8Data = _fromProfileV8Contract(
        profileV8: profileV8,
        identityHeadline: identityHeadline,
        identitySummary: identitySummary,
        dominantElementLabel: dominantElementLabel,
      );
      return _mergePreferV8(primary: v8Data, fallback: legacyData);
    }

    return legacyData;
  }

  static ProfileV8Data _fromProfileV8Contract({
    required Map<String, dynamic> profileV8,
    required String identityHeadline,
    required String identitySummary,
    required String dominantElementLabel,
  }) {
    final hero = _asMap(profileV8['hero']);
    final identityAxis = _asMap(profileV8['identity_axis']);

    final quote = _shortenForProfile(
      _firstText(<dynamic>[
            identityAxis['headline'],
            identityAxis['body'],
            identityHeadline,
            identitySummary,
          ]) ??
          '',
      limit: 260,
    );

    final topInsights = _buildInsightsFromV8(
      profileV8['insight_strip'],
      hero: hero,
      dominantElementLabel: dominantElementLabel,
    );
    final differentiatorMaps = _asListOfMaps(profileV8['differentiators']);
    final uniqueBlock = _buildDifferentiatorsSection(differentiatorMaps);
    final differentiators = _buildDifferentiatorsList(differentiatorMaps);
    final originSection = _sectionFromEditorialMap(
      _asMap(profileV8['past_teaser']),
    );
    final pastLayers = _buildPastLayers(profileV8['past_teasers']);
    final firstImpressionSection = _sectionFromEditorialMap(
      _asMap(profileV8['first_impression']),
    );
    final talents = _buildTalentsFromV8(profileV8['talents']);
    final talentItems = _buildTalentItemsFromV8(profileV8['talents']);
    final conversationSection = _sectionFromEditorialMap(
      _asMap(profileV8['conversation_hooks']),
    );
    final effectSection = _sectionFromEditorialListMap(
      _asMap(profileV8['affects_you']),
    );
    final defenseSection = _sectionFromEditorialMap(
      _asMap(profileV8['defense']),
    );
    final firstFeltSection = _normalizeFirstFeltSection(
      _sectionFromEditorialMap(_asMap(profileV8['first_felt'])),
    );
    final collectiveSection = _sectionFromEditorialMap(
      _asMap(profileV8['mission_preview']),
    );
    final intimacySection = _sectionFromEditorialMap(
      _asMap(profileV8['intimacy']),
    );
    final mindSection = _sectionFromEditorialMap(_asMap(profileV8['mind']));
    final ctaSection = _buildArchetypePortalSection(
      _asMap(profileV8['archetype_portal']),
    );

    final skipped = <String>[];
    void track(String key, ProfileV8TextSection? section) {
      if (section == null || !section.hasContent) {
        skipped.add(key);
      }
    }

    track('unique', uniqueBlock);
    track('origin', originSection);
    track('first_impression', firstImpressionSection);
    if (talents.isEmpty) {
      skipped.add('talents');
    }
    track('conversation', conversationSection);
    track('effect', effectSection);
    track('defense', defenseSection);
    track('first_felt', firstFeltSection);
    track('collective', collectiveSection);
    track('intimacy', intimacySection);
    track('mind', mindSection);
    track('cta', ctaSection);

    return ProfileV8Data(
      identityQuote: quote,
      topInsights: topInsights,
      uniqueBlock: uniqueBlock,
      differentiators: differentiators,
      originSection: originSection,
      pastLayers: pastLayers,
      firstImpressionSection: firstImpressionSection,
      talents: talents,
      talentItems: talentItems,
      conversationSection: conversationSection,
      effectSection: effectSection,
      defenseSection: defenseSection,
      firstFeltSection: firstFeltSection,
      collectiveSection: collectiveSection,
      intimacySection: intimacySection,
      mindSection: mindSection,
      ctaSection: ctaSection,
      skippedSectionKeys: skipped,
    );
  }

  static ProfileV8Data _mergePreferV8({
    required ProfileV8Data primary,
    required ProfileV8Data fallback,
  }) {
    final merged = ProfileV8Data(
      identityQuote: primary.identityQuote.trim().isNotEmpty
          ? primary.identityQuote
          : fallback.identityQuote,
      topInsights: primary.topInsights.isNotEmpty
          ? primary.topInsights
          : fallback.topInsights,
      uniqueBlock: _preferSection(primary.uniqueBlock, fallback.uniqueBlock),
      differentiators: primary.differentiators.isNotEmpty
          ? primary.differentiators
          : fallback.differentiators,
      originSection: _preferSection(primary.originSection, fallback.originSection),
      pastLayers: primary.pastLayers.isNotEmpty
          ? primary.pastLayers
          : fallback.pastLayers,
      firstImpressionSection: _preferSection(
        primary.firstImpressionSection,
        fallback.firstImpressionSection,
      ),
      talents: primary.talents.isNotEmpty ? primary.talents : fallback.talents,
      talentItems: primary.talentItems.isNotEmpty
          ? primary.talentItems
          : fallback.talentItems,
      conversationSection: _preferSection(
        primary.conversationSection,
        fallback.conversationSection,
      ),
      effectSection: _preferSection(primary.effectSection, fallback.effectSection),
      defenseSection: _preferSection(
        primary.defenseSection,
        fallback.defenseSection,
      ),
      firstFeltSection: _preferSection(
        primary.firstFeltSection,
        fallback.firstFeltSection,
      ),
      collectiveSection: _preferSection(
        primary.collectiveSection,
        fallback.collectiveSection,
      ),
      intimacySection: _preferSection(
        primary.intimacySection,
        fallback.intimacySection,
      ),
      mindSection: _preferSection(primary.mindSection, fallback.mindSection),
      ctaSection: _preferSection(primary.ctaSection, fallback.ctaSection),
      skippedSectionKeys: _mergeSkippedKeys(
        primary: primary.skippedSectionKeys,
        fallback: fallback.skippedSectionKeys,
      ),
    );
    return merged;
  }

  static ProfileV8TextSection? _preferSection(
    ProfileV8TextSection? primary,
    ProfileV8TextSection? fallback,
  ) {
    if (primary != null && primary.hasContent) {
      final hasBullets = primary.bullets.any((item) => item.trim().isNotEmpty);
      final fallbackBullets =
          fallback?.bullets.where((item) => item.trim().isNotEmpty).toList() ??
              const <String>[];
      final primaryGrowth = (primary.growth ?? '').trim();
      final fallbackGrowth = (fallback?.growth ?? '').trim();
      final mergedGrowth = primaryGrowth.isNotEmpty
          ? primary.growth
          : (fallbackGrowth.isNotEmpty ? fallback!.growth : null);
      if (!hasBullets && fallbackBullets.isNotEmpty) {
        return ProfileV8TextSection(
          eyebrow: primary.eyebrow,
          headline: primary.headline,
          body: primary.body,
          bullets: fallbackBullets,
          chips: primary.chips.isNotEmpty ? primary.chips : (fallback?.chips ?? const <String>[]),
          callout: primary.callout,
          footer: primary.footer,
          cta: primary.cta,
          growth: mergedGrowth,
        );
      }
      if (primaryGrowth.isEmpty && fallbackGrowth.isNotEmpty) {
        return ProfileV8TextSection(
          eyebrow: primary.eyebrow,
          headline: primary.headline,
          body: primary.body,
          bullets: primary.bullets,
          chips: primary.chips,
          callout: primary.callout,
          footer: primary.footer,
          cta: primary.cta,
          growth: fallback!.growth,
        );
      }
      return primary;
    }
    if (fallback != null && fallback.hasContent) {
      return fallback;
    }
    return null;
  }

  static List<String> _mergeSkippedKeys({
    required List<String> primary,
    required List<String> fallback,
  }) {
    final merged = <String>{...primary, ...fallback};
    return merged.toList(growable: false);
  }

  static List<ProfileV8InsightCell> _buildInsightsFromV8(
    dynamic raw, {
    required Map<String, dynamic> hero,
    required String dominantElementLabel,
  }) {
    final source = _asListOfMaps(raw);
    final cells = <ProfileV8InsightCell>[];

    for (final item in source.take(3)) {
      final label = _firstText(<dynamic>[item['eyebrow'], item['label']]) ?? '';
      final title = _humanizeInsightText(
        _firstText(<dynamic>[item['title']]) ?? '',
      );
      final subtitle = _humanizeInsightText(
        _firstText(<dynamic>[item['subtitle']]) ?? '',
      );
      if (label.trim().isEmpty &&
          title.trim().isEmpty &&
          subtitle.trim().isEmpty) {
        continue;
      }
      final fallback = _defaultInsight(
        index: cells.length,
        hero: hero,
        dominantElementLabel: dominantElementLabel,
      );
      cells.add(
        ProfileV8InsightCell(
          label: label.trim().isEmpty ? fallback.label : label,
          title: title.trim().isEmpty
              ? fallback.title
              : _shortenForProfile(title, limit: 64),
          subtitle: subtitle.trim().isEmpty
              ? fallback.subtitle
              : _shortenForProfile(subtitle, limit: 84),
          icon: _iconForInsightType(_firstText(<dynamic>[item['icon_type']])),
          tint: _accentToColor(_firstText(<dynamic>[item['accent']])),
        ),
      );
    }

    if (cells.isNotEmpty) {
      while (cells.length < 3) {
        cells.add(
          _defaultInsight(
            index: cells.length,
            hero: hero,
            dominantElementLabel: dominantElementLabel,
          ),
        );
      }
      return cells.take(3).toList();
    }

    return <ProfileV8InsightCell>[
      _defaultInsight(
        index: 0,
        hero: hero,
        dominantElementLabel: dominantElementLabel,
      ),
      _defaultInsight(
        index: 1,
        hero: hero,
        dominantElementLabel: dominantElementLabel,
      ),
      _defaultInsight(
        index: 2,
        hero: hero,
        dominantElementLabel: dominantElementLabel,
      ),
    ];
  }

  static ProfileV8InsightCell _defaultInsight({
    required int index,
    required Map<String, dynamic> hero,
    required String dominantElementLabel,
  }) {
    switch (index) {
      case 0:
        return ProfileV8InsightCell(
          label: 'Aura',
          title: _humanizeInsightText(dominantElementLabel).isEmpty
              ? 'Auran net'
              : _humanizeInsightText(dominantElementLabel),
          subtitle: 'Dışarıdan güven veren bir ton.',
          icon: Icons.blur_on_rounded,
          tint: const Color(0xFFD2F2A0),
        );
      case 1:
        final ruler =
            _planetLabelTr(_firstText(<dynamic>[hero['sun_sign']]) ?? '') ?? '';
        return ProfileV8InsightCell(
          label: 'Yönetici',
          title: _humanizeInsightText(ruler).isEmpty
              ? 'Yönetici etki'
              : _humanizeInsightText(ruler),
          subtitle: 'Kimlik çizgini tutarlı kılıyor.',
          icon: Icons.public_rounded,
          tint: const Color(0xFFF0F0F3),
        );
      default:
        return const ProfileV8InsightCell(
          label: 'İç ritim',
          title: 'Ritmin dengeli',
          subtitle: 'Kararlarını iç dengeyle alırsın.',
          icon: Icons.graphic_eq_rounded,
          tint: Color(0xFFDDD8FC),
        );
    }
  }

  static ProfileV8TextSection? _buildDifferentiatorsSection(
    List<Map<String, dynamic>> items,
  ) {
    if (items.isEmpty) {
      return null;
    }
    final first = items.first;
    final bullets = <String>[];
    final chips = <String>[];

    for (final item in items.take(3)) {
      final eyebrow = _firstText(<dynamic>[item['eyebrow']]) ?? '';
      final headline = _firstText(<dynamic>[item['headline']]) ?? '';
      final stat = _firstText(<dynamic>[item['stat']]) ?? '';
      final statLabel = _firstText(<dynamic>[item['stat_label']]) ?? '';
      final bullet = <String>[
        if (eyebrow.trim().isNotEmpty) eyebrow.trim(),
        if (headline.trim().isNotEmpty) headline.trim(),
        if (stat.trim().isNotEmpty)
          statLabel.trim().isEmpty
              ? stat.trim()
              : '${stat.trim()} ${statLabel.trim()}',
      ].join(' · ');
      if (bullet.trim().isNotEmpty) {
        bullets.add(_shortenForProfile(bullet, limit: 140));
      }
      if (eyebrow.trim().isNotEmpty && chips.length < 4) {
        chips.add(eyebrow.trim());
      }
    }

    final section = ProfileV8TextSection(
      eyebrow: _firstText(<dynamic>[first['eyebrow']]) ?? 'SENİ FARKLI KILAN',
      headline: _shortenForProfile(
        _firstText(<dynamic>[first['headline'], 'Seni farklı kılan']) ?? '',
        limit: 120,
      ),
      body: _shortenForProfile(
        _firstText(<dynamic>[first['body']]) ?? '',
        limit: 200,
      ),
      bullets: bullets,
      chips: _sanitizeChipList(chips, max: 4),
    );
    return section.hasContent ? section : null;
  }

  static List<ProfileV8Differentiator> _buildDifferentiatorsList(
    List<Map<String, dynamic>> items,
  ) {
    final out = <ProfileV8Differentiator>[];
    for (final item in items.take(3)) {
      final eyebrow = _firstText(<dynamic>[item['eyebrow']]) ?? '';
      final headline = _firstText(<dynamic>[item['headline']]) ?? '';
      final body = _firstText(<dynamic>[item['body']]) ?? '';
      final stat = _firstText(<dynamic>[item['stat']]) ?? '';
      final statLabel = _firstText(<dynamic>[item['stat_label']]) ?? '';
      final accent = (_firstText(<dynamic>[item['accent']]) ?? 'lime')
          .trim()
          .toLowerCase();
      final entry = ProfileV8Differentiator(
        eyebrow: _shortenForProfile(eyebrow, limit: 40),
        headline: _shortenForProfile(headline, limit: 80),
        body: _shortenForProfile(body, limit: 100),
        stat: stat.trim(),
        statLabel: statLabel.trim(),
        accent: accent,
      );
      if (entry.hasContent) {
        out.add(entry);
      }
    }
    return List<ProfileV8Differentiator>.unmodifiable(out);
  }

  static ProfileV8TextSection? _sectionFromEditorialMap(
    Map<String, dynamic> section,
  ) {
    if (section.isEmpty) {
      return null;
    }
    final headline = _shortenForProfile(
      _firstText(<dynamic>[section['headline']]) ?? '',
      limit: 120,
    );
    final rawBody = _shortenForProfile(
      _firstText(<dynamic>[section['body']]) ?? '',
      limit: 220,
    );
    final body = _normalizedBody(headline: headline, body: rawBody);
    final resolved = ProfileV8TextSection(
      eyebrow: _firstText(<dynamic>[section['eyebrow']]) ?? '',
      headline: headline,
      body: body,
      chips: _sanitizeChipList(section['chips'], max: 4),
      callout: _firstText(<dynamic>[section['callout'], section['highlight']]),
      footer: _shortenForProfile(
        _firstText(<dynamic>[section['footer']]) ?? '',
        limit: 110,
      ),
      cta: _firstText(<dynamic>[section['footer_cta']]),
      growth: _firstText(<dynamic>[section['growth']]),
    );
    return resolved.hasContent ? resolved : null;
  }

  static ProfileV8TextSection? _sectionFromEditorialListMap(
    Map<String, dynamic> section,
  ) {
    if (section.isEmpty) {
      return null;
    }
    final headline = _shortenForProfile(
      _firstText(<dynamic>[section['headline']]) ?? '',
      limit: 120,
    );
    final rawBody = _shortenForProfile(
      _firstText(<dynamic>[section['body']]) ?? '',
      limit: 220,
    );
    final body = _normalizedBody(headline: headline, body: rawBody);
    final resolved = ProfileV8TextSection(
      eyebrow: _firstText(<dynamic>[section['eyebrow']]) ?? '',
      headline: headline,
      body: body,
      bullets: safeTextList(section['rows'], max: 5)
          .map((item) => _shortenForProfile(item, limit: 130))
          .where((item) => item.trim().isNotEmpty)
          .toList(growable: false),
      footer: _shortenForProfile(
        _firstText(<dynamic>[section['footer']]) ?? '',
        limit: 110,
      ),
    );
    return resolved.hasContent ? resolved : null;
  }

  static List<String> _buildTalentsFromV8(dynamic raw) {
    final result = <String>[];
    for (final item in _asListOfMaps(raw)) {
      final eyebrow = _firstText(<dynamic>[item['eyebrow']]) ?? '';
      final text = _firstText(<dynamic>[item['text']]) ?? '';
      if (text.trim().isEmpty) {
        continue;
      }
      final combined = eyebrow.trim().isEmpty
          ? text.trim()
          : '${eyebrow.trim()}: ${text.trim()}';
      final normalized = _shortenForProfile(
        _humanizeInsightText(combined),
        limit: 86,
      );
      if (_isInternalKey(normalized) || _looksLikeAstroPlacement(normalized)) {
        continue;
      }
      final duplicate = result.any(
        (existing) => existing.toLowerCase() == normalized.toLowerCase(),
      );
      if (!duplicate) {
        result.add(normalized);
      }
      if (result.length >= 3) {
        break;
      }
    }
    return result;
  }

  static List<ProfileV8PastLayer> _buildPastLayers(dynamic raw) {
    final out = <ProfileV8PastLayer>[];
    for (final item in _asListOfMaps(raw)) {
      final headline = _firstText(<dynamic>[item['headline']]) ?? '';
      final body = _firstText(<dynamic>[item['body']]) ?? '';
      if (headline.trim().isEmpty && body.trim().isEmpty) {
        continue;
      }
      final placement = _sanitizeChipList(item['chips'], max: 2).join(' · ');
      final highlight = _firstText(<dynamic>[item['highlight']]) ?? '';
      out.add(
        ProfileV8PastLayer(
          eyebrow:
              _firstText(<dynamic>[item['eyebrow']]) ??
                  'BU NEREDEN GELİYOR OLABİLİR',
          placement: placement,
          headline: _shortenForProfile(headline, limit: 140),
          body: _shortenForProfile(body, limit: 260),
          highlight: highlight,
        ),
      );
      if (out.length >= 4) {
        break;
      }
    }
    return List<ProfileV8PastLayer>.unmodifiable(out);
  }

  static List<ProfileV8Talent> _buildTalentItemsFromV8(dynamic raw) {
    final out = <ProfileV8Talent>[];
    for (final item in _asListOfMaps(raw).take(3)) {
      final eyebrow = _firstText(<dynamic>[item['eyebrow']]) ?? '';
      final text = _firstText(<dynamic>[item['text']]) ?? '';
      if (text.trim().isEmpty) {
        continue;
      }
      final accent = (_firstText(<dynamic>[item['accent']]) ?? 'lime')
          .trim()
          .toLowerCase();
      final headline = _shortenForProfile(
        _humanizeInsightText(text),
        limit: 64,
      );
      if (_isInternalKey(headline) || _looksLikeAstroPlacement(headline)) {
        continue;
      }
      final duplicate = out.any(
        (existing) =>
            existing.headline.toLowerCase() == headline.toLowerCase(),
      );
      if (duplicate) {
        continue;
      }
      out.add(
        ProfileV8Talent(
          eyebrow: _shortenForProfile(eyebrow, limit: 24),
          headline: headline,
          accent: accent,
        ),
      );
    }
    return List<ProfileV8Talent>.unmodifiable(out);
  }

  static ProfileV8TextSection? _buildArchetypePortalSection(
    Map<String, dynamic> portal,
  ) {
    if (portal.isEmpty) {
      return null;
    }
    final labels = <String>[];
    for (final item in _asListOfMaps(portal['items'])) {
      final key = _firstText(<dynamic>[item['key']]) ?? '';
      final display = _firstText(<dynamic>[item['display_label']]) ?? '';
      final resolved = display.trim().isNotEmpty
          ? display.trim()
          : _archetypeLabelByKey[key.toLowerCase()];
      final candidate = (resolved ?? '').trim();
      if (candidate.isEmpty || _isInternalKey(candidate)) {
        continue;
      }
      final duplicate = labels.any(
        (existing) => existing.toLowerCase() == candidate.toLowerCase(),
      );
      if (!duplicate) {
        labels.add(candidate);
      }
      if (labels.length >= 3) {
        break;
      }
    }

    final section = ProfileV8TextSection(
      eyebrow: 'ARKETİP PORTALI',
      headline: _shortenForProfile(
        _firstText(<dynamic>[portal['headline']]) ?? '',
        limit: 120,
      ),
      body: _shortenForProfile(
        _firstText(<dynamic>[portal['body']]) ?? '',
        limit: 200,
      ),
      chips: labels,
      cta: _firstText(<dynamic>[portal['cta_label'], 'Arketip akışını aç →']),
    );
    return section.hasContent ? section : null;
  }

  static IconData _iconForInsightType(String? type) {
    switch ((type ?? '').trim().toLowerCase()) {
      case 'ring':
        return Icons.public_rounded;
      case 'wave':
        return Icons.graphic_eq_rounded;
      case 'dot':
      default:
        return Icons.blur_on_rounded;
    }
  }

  static Color _accentToColor(String? accent) {
    switch ((accent ?? '').trim().toLowerCase()) {
      case 'lime':
        return const Color(0xFFD2F2A0);
      case 'lavender':
        return const Color(0xFFDDD8FC);
      case 'stone':
      case 'neutral':
      default:
        return const Color(0xFFF0F0F3);
    }
  }

  static String _humanizeInsightText(String raw) {
    final compact = raw.replaceAll(RegExp(r'\s+'), ' ').trim();
    if (compact.isEmpty) {
      return '';
    }
    return compact
        .replaceAll('_', ' ')
        .replaceAll('-', ' ')
        .replaceAllMapped(
          RegExp(r'\bhouse\s+(\d+)\b', caseSensitive: false),
          (match) => '${match.group(1)}. ev',
        )
        .replaceAllMapped(
          RegExp(r'\bsun\b', caseSensitive: false),
          (_) => 'Güneş',
        )
        .replaceAllMapped(
          RegExp(r'\bmoon\b', caseSensitive: false),
          (_) => 'Ay',
        )
        .replaceAllMapped(
          RegExp(r'\bmercury\b', caseSensitive: false),
          (_) => 'Merkür',
        )
        .replaceAllMapped(
          RegExp(r'\bvenus\b', caseSensitive: false),
          (_) => 'Venüs',
        )
        .replaceAllMapped(
          RegExp(r'\bmars\b', caseSensitive: false),
          (_) => 'Mars',
        )
        .replaceAllMapped(
          RegExp(r'\bjupiter\b', caseSensitive: false),
          (_) => 'Jüpiter',
        )
        .replaceAllMapped(
          RegExp(r'\bsaturn\b', caseSensitive: false),
          (_) => 'Satürn',
        )
        .replaceAllMapped(
          RegExp(r'\buranus\b', caseSensitive: false),
          (_) => 'Uranüs',
        )
        .replaceAllMapped(
          RegExp(r'\bneptune\b', caseSensitive: false),
          (_) => 'Neptün',
        )
        .replaceAllMapped(
          RegExp(r'\bpluto\b', caseSensitive: false),
          (_) => 'Plüton',
        )
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();
  }

  static String _shortenForProfile(String text, {required int limit}) {
    final compact = text.replaceAll(RegExp(r'\s+'), ' ').trim();
    if (compact.length <= limit) {
      return compact;
    }
    return '${compact.substring(0, limit - 1).trimRight()}…';
  }

  static List<String> _sanitizeChipList(dynamic value, {int max = 4}) {
    final out = <String>[];
    for (final candidate in safeTextList(value, max: max * 2)) {
      final clean = candidate.trim();
      if (clean.isEmpty || _isInternalKey(clean)) {
        continue;
      }
      final duplicate = out.any(
        (existing) => existing.toLowerCase() == clean.toLowerCase(),
      );
      if (duplicate) {
        continue;
      }
      out.add(clean);
      if (out.length >= max) {
        break;
      }
    }
    return out;
  }

  static bool _isInternalKey(String value) {
    final lower = value.toLowerCase();
    return _internalKeyBlocklist.any((token) => lower.contains(token));
  }

  static String? safeText(dynamic value) {
    if (value == null) {
      return null;
    }
    if (value is String) {
      final text = value.trim();
      if (text.isEmpty) {
        return null;
      }
      if (_isInternalKey(text)) {
        return null;
      }
      if (_looksLikeMapDump(text)) {
        return null;
      }
      return text;
    }
    if (value is num || value is bool) {
      return value.toString();
    }
    if (value is Map) {
      for (final key in const <String>[
        'headline',
        'title',
        'label',
        'display_label',
        'text',
        'summary',
        'value',
        'name',
        'display',
        'body',
        'subtitle',
      ]) {
        final candidate = safeText(value[key]);
        if (candidate != null && candidate.isNotEmpty) {
          return candidate;
        }
      }
      return null;
    }
    if (value is List) {
      final lines = <String>[];
      for (final item in value) {
        final candidate = safeText(item);
        if (candidate == null || candidate.isEmpty) {
          continue;
        }
        lines.add(candidate);
        if (lines.length >= 4) {
          break;
        }
      }
      if (lines.isEmpty) {
        return null;
      }
      return lines.join(' · ');
    }
    final fallback = value.toString().trim();
    return fallback.isEmpty ? null : fallback;
  }

  static List<String> safeTextList(dynamic value, {int max = 5}) {
    final items = <String>[];
    void add(dynamic source) {
      if (items.length >= max) {
        return;
      }
      final text = safeText(source);
      if (text == null || text.isEmpty) {
        return;
      }
      final duplicate = items.any(
        (existing) => existing.toLowerCase() == text.toLowerCase(),
      );
      if (!duplicate) {
        items.add(text);
      }
    }

    if (value is List) {
      for (final item in value) {
        if (items.length >= max) {
          break;
        }
        if (item is Map) {
          add(item['text']);
          add(item['headline']);
          add(item['summary']);
          add(item['title']);
          add(item['label']);
          add(item['value']);
          if (items.length >= max) {
            break;
          }
          add(item);
        } else {
          add(item);
        }
      }
      return items;
    }

    if (value is Map) {
      add(value['text']);
      add(value['headline']);
      add(value['summary']);
      add(value['title']);
      add(value['label']);
      add(value['display_label']);
      add(value['body']);
      return items;
    }

    add(value);
    return items;
  }

  static List<Map<String, dynamic>> _readCardField(
    Map<String, dynamic> source,
    String field,
  ) {
    return _asListOfMaps(source[field]).map(_normalizeCard).toList();
  }

  static List<Map<String, dynamic>> _readThreadField(
    Map<String, dynamic> source,
    String field,
  ) {
    return _asListOfMaps(source[field]).map(_normalizeThread).toList();
  }

  static Map<String, dynamic> _normalizeCard(Map<String, dynamic> raw) {
    return <String, dynamic>{
      'id': safeText(raw['id']) ?? '',
      'card_key': safeText(raw['card_key']) ?? '',
      'family': safeText(raw['family']) ?? '',
      'eyebrow': safeText(raw['eyebrow']) ?? '',
      'title': _firstText(<dynamic>[raw['title'], raw['headline']]) ?? '',
      'summary': _firstText(<dynamic>[raw['summary'], raw['teaser']]) ?? '',
      'body': safeText(raw['body']) ?? '',
      'micro': safeText(raw['micro']) ?? '',
      'detail_blocks': safeTextList(raw['detail_blocks'], max: 6),
      'chips': safeTextList(raw['chips'], max: 4),
    };
  }

  static Map<String, dynamic> _normalizeModule(Map<String, dynamic> raw) {
    final content = _asMap(raw['content']);
    return <String, dynamic>{
      'module_id': safeText(raw['module_id']) ?? '',
      'headline': safeText(raw['headline']) ?? '',
      'subheadline': safeText(raw['subheadline']) ?? '',
      'title': _firstText(<dynamic>[content['title'], raw['title']]) ?? '',
      'body': _firstText(<dynamic>[content['body'], raw['body']]) ?? '',
    };
  }

  static Map<String, dynamic> _normalizeThread(Map<String, dynamic> raw) {
    return <String, dynamic>{
      'id': safeText(raw['id']) ?? '',
      'title': safeText(raw['title']) ?? '',
      'subtitle':
          _firstText(<dynamic>[raw['one_liner'], raw['subtitle']]) ?? '',
      'body': _firstText(<dynamic>[raw['paragraph'], raw['body']]) ?? '',
      'chips': safeTextList(raw['chips'], max: 4),
      'detail_blocks': safeTextList(raw['detail_blocks'], max: 6),
      // Voice spec v2.1 §11.4 passthrough. Empty string when backend omits
      // (legacy caller) or thread is not among the live 3 (identity /
      // relationships / career).
      'proof_raw': safeText(raw['proof_raw']) ?? '',
    };
  }

  static List<Map<String, dynamic>> _dedupeCards(
    List<Map<String, dynamic>> cards,
  ) {
    return _dedupeByIdentity(cards, (card) {
      return _identityKey(card, const <String>['card_key', 'id', 'title']);
    });
  }

  static List<T> _dedupeByIdentity<T>(
    Iterable<T> items,
    String Function(T item) identity,
  ) {
    final seen = <String>{};
    final result = <T>[];
    for (final item in items) {
      final key = identity(item).trim();
      if (key.isEmpty || !seen.add(key)) {
        continue;
      }
      result.add(item);
    }
    return result;
  }

  static String _identityKey(Map<String, dynamic> item, List<String> keys) {
    for (final key in keys) {
      final value = safeText(item[key]);
      if (value != null && value.isNotEmpty) {
        return value.toLowerCase();
      }
    }
    return '';
  }

  static Map<String, dynamic>? _pickCard(
    List<Map<String, dynamic>> cards, {
    Set<String> families = const <String>{},
    List<String> keywords = const <String>[],
    Set<String> excluded = const <String>{},
  }) {
    final familyNormalized = families.map((item) => item.toLowerCase()).toSet();

    for (final card in cards) {
      if (excluded.contains(_cardIdentity(card))) {
        continue;
      }
      final family = (safeText(card['family']) ?? '').toLowerCase();
      if (familyNormalized.contains(family)) {
        return card;
      }
    }

    for (final card in cards) {
      if (excluded.contains(_cardIdentity(card))) {
        continue;
      }
      final haystack = [
        safeText(card['title']) ?? '',
        safeText(card['summary']) ?? '',
        safeText(card['body']) ?? '',
        safeText(card['family']) ?? '',
        safeText(card['eyebrow']) ?? '',
      ].join(' ').toLowerCase();
      if (_containsAny(haystack, keywords)) {
        return card;
      }
    }

    for (final card in cards) {
      if (excluded.contains(_cardIdentity(card))) {
        continue;
      }
      if ((safeText(card['title']) ?? '').isNotEmpty ||
          (safeText(card['body']) ?? '').isNotEmpty ||
          (safeText(card['summary']) ?? '').isNotEmpty) {
        return card;
      }
    }
    return null;
  }

  static Map<String, dynamic>? _pickThread(
    List<Map<String, dynamic>> threads, {
    List<String> keywords = const <String>[],
    List<String> preferredIds = const <String>[],
  }) {
    for (final thread in threads) {
      final id = (safeText(thread['id']) ?? '').toLowerCase();
      if (preferredIds.any((item) => id == item.toLowerCase())) {
        return thread;
      }
    }

    for (final thread in threads) {
      final haystack = [
        safeText(thread['title']) ?? '',
        safeText(thread['subtitle']) ?? '',
        safeText(thread['body']) ?? '',
        safeText(thread['id']) ?? '',
      ].join(' ').toLowerCase();
      if (_containsAny(haystack, keywords)) {
        return thread;
      }
    }

    for (final thread in threads) {
      if ((safeText(thread['title']) ?? '').isNotEmpty &&
          ((safeText(thread['subtitle']) ?? '').isNotEmpty ||
              (safeText(thread['body']) ?? '').isNotEmpty)) {
        return thread;
      }
    }
    return null;
  }

  static Map<String, dynamic>? _pickModule(
    List<Map<String, dynamic>> modules, {
    required List<String> keywords,
  }) {
    for (final module in modules) {
      final haystack = [
        safeText(module['headline']) ?? '',
        safeText(module['title']) ?? '',
        safeText(module['body']) ?? '',
        safeText(module['module_id']) ?? '',
      ].join(' ').toLowerCase();
      if (_containsAny(haystack, keywords)) {
        return module;
      }
    }
    return modules.isEmpty ? null : modules.first;
  }

  static ProfileV8TextSection? _makeSection({
    required String eyebrow,
    List<dynamic> headlineCandidates = const <dynamic>[],
    List<dynamic> bodyCandidates = const <dynamic>[],
    List<dynamic> bulletCandidates = const <dynamic>[],
    List<dynamic> chipCandidates = const <dynamic>[],
    List<dynamic> footerCandidates = const <dynamic>[],
    List<dynamic> ctaCandidates = const <dynamic>[],
    List<dynamic> calloutCandidates = const <dynamic>[],
    List<dynamic> proofRawCandidates = const <dynamic>[],
  }) {
    final headline = _shortenForProfile(
      _firstText(headlineCandidates) ?? '',
      limit: 120,
    );
    final body = _shortenForProfile(
      _firstText(bodyCandidates) ?? '',
      limit: 220,
    );
    final bullets = <String>[];
    for (final candidate in bulletCandidates) {
      for (final item in safeTextList(candidate, max: 6)) {
        final duplicate = bullets.any(
          (existing) => existing.toLowerCase() == item.toLowerCase(),
        );
        if (!duplicate && !_isInternalKey(item)) {
          bullets.add(item);
        }
      }
      if (bullets.length >= 6) {
        break;
      }
    }
    final chips = <String>[];
    for (final candidate in chipCandidates) {
      for (final item in safeTextList(candidate, max: 5)) {
        final duplicate = chips.any(
          (existing) => existing.toLowerCase() == item.toLowerCase(),
        );
        if (!duplicate && !_isInternalKey(item)) {
          chips.add(item);
        }
      }
      if (chips.length >= 5) {
        break;
      }
    }

    final section = ProfileV8TextSection(
      eyebrow: eyebrow,
      headline: headline,
      body: body,
      bullets: bullets,
      chips: chips,
      callout: _firstText(calloutCandidates),
      footer: _firstText(footerCandidates),
      cta: _firstText(ctaCandidates),
      // Voice spec v2.1 §11.4 — first non-empty proof_raw across candidates.
      // safeText (via _firstText) normalizes null / whitespace / non-string.
      proofRaw: _firstText(proofRawCandidates) ?? '',
    );
    return section.hasContent ? section : null;
  }

  static List<String> _buildTalents({
    required Map<String, dynamic> publicScope,
    required Map<String, dynamic> profilePublic,
    required List<Map<String, dynamic>> cards,
  }) {
    final result = <String>[];

    void addAll(dynamic source, {int max = 3}) {
      for (final item in safeTextList(source, max: max)) {
        if (_isInternalKey(item)) {
          continue;
        }
        final normalized = _shortenForProfile(
          _humanizeInsightText(item),
          limit: 86,
        );
        if (_isInternalKey(normalized) || _looksLikeAstroPlacement(normalized)) {
          continue;
        }
        final duplicate = result.any(
          (existing) => existing.toLowerCase() == normalized.toLowerCase(),
        );
        if (!duplicate) {
          result.add(normalized);
        }
      }
    }

    addAll(_pathValue(publicScope, const ['user_compact', 'micro_insights']));
    addAll(publicScope['micro_insights']);
    addAll(_pathValue(publicScope, const ['meta_summary', 'highlights']));

    if (result.isEmpty) {
      addAll(publicScope['theme_scores']);
      addAll(publicScope['meaning_weighting']);
    }

    if (result.isEmpty && cards.isNotEmpty) {
      addAll(cards.first['chips']);
      addAll(cards.length > 1 ? cards[1]['chips'] : null);
    }

    if (result.length > 3) {
      return result.take(3).toList();
    }
    return result;
  }

  static String _cardIdentity(Map<String, dynamic>? card) {
    if (card == null) {
      return '';
    }
    return _identityKey(card, const <String>['card_key', 'id', 'title']);
  }

  static ProfileV8TextSection? _normalizeFirstFeltSection(
    ProfileV8TextSection? section,
  ) {
    if (section == null || !section.hasContent) {
      return section;
    }
    var headline = section.headline.trim();
    var body = section.body.trim();
    if (_looksLikeAstroPlacement(headline) && body.isNotEmpty) {
      headline = body;
      body = '';
    }
    if (_looksLikeAstroPlacement(headline) && body.isEmpty) {
      headline = 'İlk anda sakin, kısa sürede güçlü bir iz bırakıyorsun.';
    }
    body = _normalizedBody(headline: headline, body: body);
    final normalized = ProfileV8TextSection(
      eyebrow: section.eyebrow,
      headline: headline,
      body: body,
      bullets: section.bullets,
      chips: section.chips,
      callout: section.callout,
      footer: section.footer,
      cta: section.cta,
    );
    return normalized.hasContent ? normalized : null;
  }

  static String _normalizedBody({required String headline, required String body}) {
    final h = headline.replaceAll(RegExp(r'\s+'), ' ').trim().toLowerCase();
    final b = body.replaceAll(RegExp(r'\s+'), ' ').trim();
    if (b.isEmpty) {
      return '';
    }
    if (h.isNotEmpty && b.toLowerCase() == h) {
      return '';
    }
    return b;
  }

  static bool _looksLikeAstroPlacement(String text) {
    final lower = text.toLowerCase().replaceAll(RegExp(r'\s+'), ' ').trim();
    if (lower.isEmpty) {
      return false;
    }
    final hasHouse = RegExp(r'\b\d{1,2}\.?\s*ev\b').hasMatch(lower);
    final hasPlanet = RegExp(
      r'\b(güneş|ay|merkür|venüs|mars|jüpiter|satürn|uranüs|neptün|plüton|sun|moon|mercury|venus|mars|jupiter|saturn|uranus|neptune|pluto)\b',
    ).hasMatch(lower);
    return hasHouse && hasPlanet;
  }

  static bool _containsAny(String text, List<String> keywords) {
    final normalized = text.toLowerCase();
    for (final keyword in keywords) {
      if (normalized.contains(keyword.toLowerCase())) {
        return true;
      }
    }
    return false;
  }

  static String? _planetLabelTr(String raw) {
    const labels = <String, String>{
      'sun': 'Güneş',
      'moon': 'Ay',
      'mercury': 'Merkür',
      'venus': 'Venüs',
      'mars': 'Mars',
      'jupiter': 'Jüpiter',
      'saturn': 'Satürn',
      'uranus': 'Uranüs',
      'neptune': 'Neptün',
      'pluto': 'Plüton',
    };
    final key = raw.trim().toLowerCase();
    if (key.isEmpty) {
      return null;
    }
    return labels[key] ?? raw.trim();
  }

  static String? _firstText(Iterable<dynamic> values) {
    for (final value in values) {
      final text = safeText(value);
      if (text != null && text.trim().isNotEmpty) {
        return text.trim();
      }
    }
    return null;
  }

  static Map<String, dynamic> _asMap(dynamic value) {
    if (value is Map<String, dynamic>) {
      return value;
    }
    if (value is Map) {
      return value.map((key, dynamic nested) {
        return MapEntry(key.toString(), nested);
      });
    }
    return <String, dynamic>{};
  }

  static List<Map<String, dynamic>> _asListOfMaps(dynamic value) {
    if (value is! List) {
      return const <Map<String, dynamic>>[];
    }
    final result = <Map<String, dynamic>>[];
    for (final item in value) {
      final mapped = _asMap(item);
      if (mapped.isNotEmpty) {
        result.add(mapped);
      }
    }
    return result;
  }

  static Map<String, dynamic> _pathMap(
    Map<String, dynamic> source,
    List<String> path,
  ) {
    dynamic current = source;
    for (final segment in path) {
      if (current is! Map) {
        return <String, dynamic>{};
      }
      current = current[segment];
    }
    return _asMap(current);
  }

  static dynamic _pathValue(Map<String, dynamic> source, List<String> path) {
    dynamic current = source;
    for (final segment in path) {
      if (current is! Map) {
        return null;
      }
      current = current[segment];
      if (current == null) {
        return null;
      }
    }
    return current;
  }

  static Map<String, dynamic> _firstNonEmptyMap(
    Iterable<Map<String, dynamic>> maps,
  ) {
    for (final map in maps) {
      if (map.isNotEmpty) {
        return map;
      }
    }
    return <String, dynamic>{};
  }

  static Map<String, dynamic> _firstMapWhere(
    Iterable<Map<String, dynamic>> maps,
    bool Function(Map<String, dynamic> item) test,
  ) {
    for (final map in maps) {
      if (test(map)) {
        return map;
      }
    }
    return <String, dynamic>{};
  }

  static bool _looksLikeMapDump(String input) {
    final text = input.trim();
    return text.startsWith('{') && text.endsWith('}') && text.contains(':');
  }
}
