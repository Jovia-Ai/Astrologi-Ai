import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../people/friend_profile_page.dart';
import '../profile/profile_models.dart';
import 'ai_page.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'bond_models.dart';
import 'story_studio_page.dart';

class BondResultPage extends StatelessWidget {
  const BondResultPage({
    super.key,
    required this.response,
    required this.youName,
    required this.partnerName,
    required this.bondType,
    this.partnerPersonId,
  });

  final Map<String, dynamic> response;
  final String youName;
  final String partnerName;
  final BondType bondType;
  final String? partnerPersonId;

  @override
  Widget build(BuildContext context) {
    final displayYouName = _presentableSelfName(youName, fallback: 'Sen');
    final displayPartnerName = _presentableName(
      partnerName,
      fallback: 'Diger kisi',
    );
    final public = _asMap(response['public']);
    final scores = _asMap(public['scores']);
    final rawScores = _asMap(public['raw_scores']);
    final contextualScores = _asMap(public['contextual_scores']);
    final drivers = _asMap(public['drivers']);
    final resonanceScores = _asMap(public['resonance_scores']);
    final partnerAResonance = _asMap(resonanceScores['partner_a']);
    final partnerBResonance = _asMap(resonanceScores['partner_b']);
    final relationshipResonance = _asMap(resonanceScores['relationship']);
    final derivedContext = _asMap(public['derived_context']);
    final partnerAActivated = _toMapList(derivedContext['partner_a_activated']);
    final partnerBActivated = _toMapList(derivedContext['partner_b_activated']);
    final asymmetryNotes = _toStringList(derivedContext['asymmetry_notes']);
    final synastryImprint = _asMap(public['synastry_imprint']);
    final narrativeReady = _asMap(public['narrative_ready']);
    final partnerAStory = _asMap(narrativeReady['partner_a_story']);
    final partnerBStory = _asMap(narrativeReady['partner_b_story']);
    final narrative = _asMap(public['narrative']);
    final narrativeBlocks = _toProfileNarrativeBlocks(narrative['blocks']);
    final display = _asMap(public['display']);
    final aspectsLines = _toStringList(_asMap(display['aspects_lines'])['top']);
    final touchLines = _toStringList(display['touchpoints_lines']);
    final relationshipSummary = _firstNonEmpty([
      for (final block in narrativeBlocks) block.teaser,
      for (final block in narrativeBlocks) block.body,
      (synastryImprint['summary'] ?? '').toString(),
      (synastryImprint['theme'] ?? '').toString(),
      '$displayYouName ve $displayPartnerName arasindaki dinamik bu lenste okunuyor.',
    ]);
    final flowLines = _uniqueLines([
      ...touchLines.take(3),
      ..._driverLines(drivers).take(2),
    ]);
    final tensionLines = _uniqueLines([
      ...asymmetryNotes.take(3),
      ..._activationLines(
        partnerAActivated,
        owner: displayPartnerName,
        target: displayYouName,
      ).take(2),
      ..._activationLines(
        partnerBActivated,
        owner: displayYouName,
        target: displayPartnerName,
      ).take(2),
    ]);
    final lessonText = _firstNonEmpty([
      for (final block in narrativeBlocks) block.micro,
      for (final block in narrativeBlocks) block.body,
      (synastryImprint['lesson'] ?? '').toString(),
      relationshipSummary,
    ]);
    final emotionalText = _firstNonEmpty([
      (synastryImprint['emotional_dynamic'] ?? '').toString(),
      (partnerAStory['lived_as'] ?? '').toString(),
      (partnerBStory['lived_as'] ?? '').toString(),
      tensionLines.isNotEmpty ? tensionLines.first : '',
    ]);

    final themed = withProfileTheme(Theme.of(context));

    return Theme(
      data: themed,
      child: Builder(
        builder: (context) {
          final spacing = context.profileTheme.spacing;
          final colors = context.profileTheme.colors;
          final typo = context.profileTheme.typography;
          return Scaffold(
            appBar: AppBar(
              title: Text(
                'BOND SONUCU',
                style: typo.navigationLabel(color: colors.text),
              ),
            ),
            body: ListView(
              padding: EdgeInsets.fromLTRB(
                spacing.lg,
                spacing.lg,
                spacing.lg,
                spacing.xl,
              ),
              children: [
                _GlassCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '$displayYouName + $displayPartnerName',
                        style: typo.pageTitle.copyWith(color: colors.text),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Tür: ${bondType.label}',
                        style: typo.meta.copyWith(color: colors.muted),
                      ),
                      const SizedBox(height: 14),
                      Text(
                        relationshipSummary,
                        style: typo.bodyCompact.copyWith(color: colors.text),
                      ),
                    ],
                  ),
                ),
                if (synastryImprint.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _GlassCard(
                    child: _SynastryImprintSection(
                      imprint: synastryImprint,
                      sourceYouName: youName,
                      sourcePartnerName: partnerName,
                      youName: displayYouName,
                      partnerName: displayPartnerName,
                      sectionTitle: 'Bagin imzalari',
                    ),
                  ),
                ],
                const SizedBox(height: 12),
                _GlassCard(
                  child: JoviaActionRail(
                    title: 'Sonraki adim',
                    body:
                        'Bu bagi daha derin okumaya, paylasmaya ya da baska bir lensten tekrar bakmaya devam edebilirsin.',
                    showTopDivider: false,
                    primaryAction: MinimalCTAButton(
                      label: (partnerPersonId ?? '').trim().isNotEmpty
                          ? 'Kisinin profiline git'
                          : 'Bu bagi sor',
                      emphasized: true,
                      onTap: () {
                        if ((partnerPersonId ?? '').trim().isNotEmpty) {
                          Navigator.of(context).push(
                            MaterialPageRoute<void>(
                              builder: (_) =>
                                  FriendProfilePage(personId: partnerPersonId!),
                            ),
                          );
                          return;
                        }
                        Navigator.of(context).push(
                          MaterialPageRoute<void>(
                            builder: (_) => const AiPage(),
                          ),
                        );
                      },
                    ),
                    secondaryActions: [
                      if ((partnerPersonId ?? '').trim().isNotEmpty)
                        MinimalCTAButton(
                          label: 'Bu bagi sor',
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute<void>(
                                builder: (_) => const AiPage(),
                              ),
                            );
                          },
                        ),
                      MinimalCTAButton(
                        label: 'Karta cevir',
                        onTap: () {
                          Navigator.of(context).push(
                            MaterialPageRoute<void>(
                              builder: (_) => const StoryStudioPage(),
                            ),
                          );
                        },
                      ),
                      MinimalCTAButton(
                        label: 'Baska lense don',
                        onTap: () => Navigator.of(context).maybePop(),
                      ),
                    ],
                  ),
                ),
                if (narrativeBlocks.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _GlassCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Bagin anlatisi',
                          style: typo.sectionTitle.copyWith(color: colors.text),
                        ),
                        const SizedBox(height: 10),
                        for (
                          var i = 0;
                          i < narrativeBlocks.take(3).length;
                          i++
                        ) ...[
                          _NarrativeBlockCard(block: narrativeBlocks[i]),
                          if (i != narrativeBlocks.take(3).length - 1)
                            const Padding(
                              padding: EdgeInsets.symmetric(vertical: 10),
                              child: Divider(height: 1),
                            ),
                        ],
                      ],
                    ),
                  ),
                ],
                if (flowLines.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _GlassCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Ne akiyor',
                          style: typo.sectionTitle.copyWith(color: colors.text),
                        ),
                        const SizedBox(height: 10),
                        for (final line in flowLines) ...[
                          Text('• $line'),
                          const SizedBox(height: 6),
                        ],
                      ],
                    ),
                  ),
                ],
                if (tensionLines.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _GlassCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Ne zorluyor',
                          style: typo.sectionTitle.copyWith(color: colors.text),
                        ),
                        const SizedBox(height: 10),
                        for (final line in tensionLines) ...[
                          Text('• $line'),
                          const SizedBox(height: 6),
                        ],
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 12),
                _GlassCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Bu bag ne ogretiyor',
                        style: typo.sectionTitle.copyWith(color: colors.text),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        lessonText,
                        style: typo.bodyCompact.copyWith(color: colors.text),
                      ),
                    ],
                  ),
                ),
                if (emotionalText.trim().isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _GlassCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Duygusal dinamik',
                          style: typo.sectionTitle.copyWith(color: colors.text),
                        ),
                        const SizedBox(height: 10),
                        Text(
                          emotionalText,
                          style: typo.bodyCompact.copyWith(color: colors.text),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 12),
                _GlassCard(
                  child: Theme(
                    data: Theme.of(
                      context,
                    ).copyWith(dividerColor: Colors.transparent),
                    child: ExpansionTile(
                      tilePadding: EdgeInsets.zero,
                      childrenPadding: const EdgeInsets.only(top: 8),
                      title: Text(
                        'Teknik detaylar',
                        style: typo.sectionTitle.copyWith(color: colors.text),
                      ),
                      subtitle: Text(
                        'Skorlar ve aspect cizgileri ana yuzeyden gizli tutuluyor.',
                        style: typo.meta.copyWith(color: colors.muted),
                      ),
                      children: [
                        if (scores.isNotEmpty)
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: _orderedScoreEntries(scores).map((entry) {
                              return _ScoreChip(
                                label:
                                    '${_scoreLabel(entry.key)}: ${entry.value}',
                              );
                            }).toList(),
                          ),
                        if (rawScores.isNotEmpty || contextualScores.isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(top: 16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                if (rawScores.isNotEmpty) ...[
                                  Text(
                                    'Ham skorlar',
                                    style: typo.cardTitle.copyWith(
                                      color: colors.text,
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  Wrap(
                                    spacing: 8,
                                    runSpacing: 8,
                                    children: _orderedScoreEntries(rawScores).map((
                                      entry,
                                    ) {
                                      return _ScoreChip(
                                        label:
                                            '${_scoreLabel(entry.key)}: ${entry.value}',
                                      );
                                    }).toList(),
                                  ),
                                ],
                                if (contextualScores.isNotEmpty) ...[
                                  const SizedBox(height: 12),
                                  Text(
                                    'Baglamsal skorlar',
                                    style: typo.cardTitle.copyWith(
                                      color: colors.text,
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  Wrap(
                                    spacing: 8,
                                    runSpacing: 8,
                                    children:
                                        _orderedScoreEntries(
                                          contextualScores,
                                        ).map((entry) {
                                          final deltaText = _scoreDeltaText(
                                            rawScores[entry.key],
                                            entry.value,
                                          );
                                          return _ScoreChip(
                                            label:
                                                '${_scoreLabel(entry.key)}: ${entry.value}$deltaText',
                                          );
                                        }).toList(),
                                  ),
                                ],
                              ],
                            ),
                          ),
                        if (relationshipResonance.isNotEmpty) ...[
                          const SizedBox(height: 16),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children:
                                _orderedScoreEntries(
                                  relationshipResonance,
                                ).map((entry) {
                                  return _ScoreChip(
                                    label:
                                        '${_scoreLabel(entry.key)}: ${entry.value}',
                                  );
                                }).toList(),
                          ),
                        ],
                        if (partnerAResonance.isNotEmpty ||
                            partnerBResonance.isNotEmpty ||
                            aspectsLines.isNotEmpty ||
                            touchLines.isNotEmpty ||
                            partnerAStory.isNotEmpty ||
                            partnerBStory.isNotEmpty ||
                            drivers.isNotEmpty) ...[
                          const SizedBox(height: 16),
                          if (partnerAStory.isNotEmpty)
                            _StorySummary(
                              title: '$displayPartnerName sende',
                              story: partnerAStory,
                              domainLabel: _domainLabel,
                            ),
                          if (partnerAStory.isNotEmpty &&
                              partnerBStory.isNotEmpty)
                            const SizedBox(height: 12),
                          if (partnerBStory.isNotEmpty)
                            _StorySummary(
                              title: '$displayYouName onda',
                              story: partnerBStory,
                              domainLabel: _domainLabel,
                            ),
                          if (drivers.isNotEmpty) ...[
                            const SizedBox(height: 12),
                            for (final entry in _orderedScoreEntries(
                              drivers,
                            )) ...[
                              Text(
                                _scoreLabel(entry.key),
                                style: typo.cardTitle.copyWith(
                                  color: colors.text,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                _driverText(entry.value),
                                style: typo.bodyCompact.copyWith(
                                  color: colors.text,
                                ),
                              ),
                              const SizedBox(height: 8),
                            ],
                          ],
                          if (aspectsLines.isNotEmpty) ...[
                            const SizedBox(height: 12),
                            for (final line in aspectsLines.take(8)) ...[
                              Text('• $line'),
                              const SizedBox(height: 6),
                            ],
                          ],
                          if (touchLines.isNotEmpty) ...[
                            const SizedBox(height: 12),
                            for (final line in touchLines.take(8)) ...[
                              Text('• $line'),
                              const SizedBox(height: 6),
                            ],
                          ],
                        ],
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  String _firstNonEmpty(List<String> values) {
    for (final value in values) {
      final trimmed = value.trim();
      if (trimmed.isNotEmpty) {
        return trimmed;
      }
    }
    return '';
  }

  List<String> _driverLines(Map<String, dynamic> drivers) {
    return _orderedScoreEntries(drivers)
        .map(
          (entry) => '${_scoreLabel(entry.key)}: ${_driverText(entry.value)}',
        )
        .where((line) => !line.endsWith(': —'))
        .toList();
  }

  List<String> _activationLines(
    List<Map<String, dynamic>> rows, {
    required String owner,
    required String target,
  }) {
    return rows.map((row) {
      final domain = _domainLabel((row['domain'] ?? '').toString());
      final because = _toStringList(row['because']).take(2).join(' • ');
      final score = (row['score'] ?? '').toString().trim();
      final scoreSuffix = score.isEmpty ? '' : ' ($score)';
      if (because.isEmpty) {
        return '$owner -> $target: $domain$scoreSuffix';
      }
      return '$owner -> $target: $domain$scoreSuffix • $because';
    }).toList();
  }

  List<String> _uniqueLines(Iterable<String> values) {
    final seen = <String>{};
    final lines = <String>[];
    for (final value in values) {
      final trimmed = value.trim();
      if (trimmed.isEmpty || !seen.add(trimmed)) {
        continue;
      }
      lines.add(trimmed);
    }
    return lines;
  }

  Map<String, dynamic> _asMap(dynamic raw) {
    if (raw is Map<String, dynamic>) {
      return raw;
    }
    if (raw is Map) {
      return Map<String, dynamic>.from(raw);
    }
    return <String, dynamic>{};
  }

  List<String> _toStringList(dynamic raw) {
    if (raw is! List) {
      return const <String>[];
    }
    return raw.map((item) => item.toString()).toList();
  }

  List<Map<String, dynamic>> _toMapList(dynamic raw) {
    if (raw is! List) {
      return const <Map<String, dynamic>>[];
    }
    return raw
        .whereType<Map>()
        .map((item) => Map<String, dynamic>.from(item))
        .toList();
  }

  List<ProfileNarrativeBlock> _toProfileNarrativeBlocks(dynamic raw) {
    if (raw is! List) {
      return const <ProfileNarrativeBlock>[];
    }
    return raw
        .whereType<Map>()
        .map(
          (item) =>
              ProfileNarrativeBlock.fromMap(Map<String, dynamic>.from(item)),
        )
        .where((item) => item.hasContent)
        .toList();
  }

  List<MapEntry<String, dynamic>> _orderedScoreEntries(
    Map<String, dynamic> scores,
  ) {
    const order = <String>[
      'bond',
      'depth',
      'spark',
      'freedom',
      'risk_index',
      'confidence',
      'familiarity_resonance',
      'promise_alignment',
      'growth_tension',
      'trigger_load',
      'mutuality',
      'asymmetry',
      'magnetic_intensity',
      'sustainable_bond',
    ];

    final ranked = <MapEntry<String, dynamic>>[];
    for (final key in order) {
      if (scores.containsKey(key)) {
        ranked.add(MapEntry(key, scores[key]));
      }
    }
    for (final entry in scores.entries) {
      if (!order.contains(entry.key)) {
        ranked.add(entry);
      }
    }
    return ranked;
  }

  String _scoreDeltaText(dynamic rawValue, dynamic contextualValue) {
    if (rawValue is! num || contextualValue is! num) {
      return '';
    }
    final delta = contextualValue - rawValue;
    if (delta == 0) {
      return '';
    }
    if (delta > 0) {
      return ' (+${delta.toInt()})';
    }
    return ' (${delta.toInt()})';
  }

  String _scoreLabel(String key) {
    switch (key) {
      case 'bond':
        return 'Bağ';
      case 'depth':
        return 'Derinlik';
      case 'spark':
        return 'Kıvılcım';
      case 'freedom':
        return 'Özgürlük';
      case 'risk_index':
        return 'Risk';
      case 'confidence':
        return 'Güven';
      case 'familiarity_resonance':
        return 'Tanıdıklık';
      case 'promise_alignment':
        return 'Vaat Uyumu';
      case 'growth_tension':
        return 'Büyüme Gerilimi';
      case 'trigger_load':
        return 'Tetiklenme Yükü';
      case 'mutuality':
        return 'Karşılıklılık';
      case 'asymmetry':
        return 'Asimetri';
      case 'magnetic_intensity':
        return 'Manyetik Yoğunluk';
      case 'sustainable_bond':
        return 'Sürdürülebilir Bağ';
      default:
        return key;
    }
  }

  String _domainLabel(String key) {
    switch (key) {
      case 'identity':
        return 'Kimlik';
      case 'mind_communication':
        return 'Zihin / İletişim';
      case 'relationships':
        return 'İlişkiler';
      case 'intimacy_depth':
        return 'Mahremiyet / Derinlik';
      case 'career_visibility':
        return 'Görünürlük / Kariyer';
      case 'home_roots':
        return 'Ev / Kökler';
      case 'creativity_talent':
        return 'Yaratıcılık';
      case 'meaning_learning':
        return 'Anlam / Öğrenme';
      case 'private_inner_world':
        return 'İç Dünya / Özel Alan';
      case 'social_future':
        return 'Sosyal Alan / Gelecek';
      default:
        return key;
    }
  }

  String _driverText(dynamic value) {
    if (value is List && value.isNotEmpty) {
      return value.map((item) => item.toString()).join(', ');
    }
    return '—';
  }

  String _presentableName(String raw, {required String fallback}) {
    return _presentableNameInternal(
      raw,
      fallback: fallback,
      allowHandleFallback: true,
    );
  }

  String _presentableSelfName(String raw, {required String fallback}) {
    final user = Supabase.instance.client.auth.currentUser;
    final metadata = user?.userMetadata ?? const <String, dynamic>{};
    final first = (metadata['first_name'] ?? metadata['firstName'] ?? '')
        .toString()
        .trim();
    final last = (metadata['last_name'] ?? metadata['lastName'] ?? '')
        .toString()
        .trim();
    final candidates = <String>[
      (metadata['full_name'] ?? metadata['fullName'] ?? '').toString(),
      (metadata['display_name'] ?? metadata['displayName'] ?? '').toString(),
      (metadata['name'] ?? '').toString(),
      if (first.isNotEmpty || last.isNotEmpty) '$first $last'.trim(),
      raw,
    ];
    for (final candidate in candidates) {
      final presentable = _presentableNameInternal(
        candidate,
        fallback: '',
        allowHandleFallback: false,
      );
      if (presentable.isNotEmpty) {
        return presentable;
      }
    }
    return fallback;
  }

  String _presentableNameInternal(
    String raw, {
    required String fallback,
    required bool allowHandleFallback,
  }) {
    final trimmed = raw.trim();
    if (trimmed.isEmpty) {
      return fallback;
    }
    if (trimmed.contains('@')) {
      final local = trimmed.split('@').first.trim();
      if (local.isEmpty) {
        return fallback;
      }
      final parts = local
          .split(RegExp(r'[._-]+'))
          .where((part) => part.trim().isNotEmpty)
          .map((part) {
            final word = part.trim();
            return word[0].toUpperCase() + word.substring(1);
          })
          .toList();
      if (parts.isEmpty) {
        return fallback;
      }
      return parts.join(' ');
    }
    if (_looksLikeSystemHandle(trimmed) && !allowHandleFallback) {
      return fallback;
    }
    return trimmed;
  }

  bool _looksLikeSystemHandle(String value) {
    final trimmed = value.trim();
    if (trimmed.isEmpty) {
      return false;
    }
    if (trimmed.contains('@')) {
      return true;
    }
    return !trimmed.contains(' ') &&
        (RegExp(r'[0-9]').hasMatch(trimmed) ||
            trimmed.contains('_') ||
            trimmed.contains('.'));
  }
}

class _StorySummary extends StatelessWidget {
  const _StorySummary({
    required this.title,
    required this.story,
    required this.domainLabel,
  });

  final String title;
  final Map<String, dynamic> story;
  final String Function(String) domainLabel;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final typo = profile.typography;
    final primary = (story['primary_domain'] ?? '').toString();
    final secondary = (story['secondary_domain'] ?? '').toString();
    final surface = (story['surface_domain'] ?? '').toString();
    final background = (story['background_domain'] ?? '').toString();
    final livedAs = (story['lived_as'] ?? '').toString().trim();
    final mode = (story['mode'] ?? '').toString().trim();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: typo.cardTitle.copyWith(color: colors.text)),
        const SizedBox(height: 6),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            if (primary.isNotEmpty)
              _ScoreChip(label: 'Ana: ${domainLabel(primary)}'),
            if (secondary.isNotEmpty)
              _ScoreChip(label: 'İkinci: ${domainLabel(secondary)}'),
            if (surface.isNotEmpty && surface != primary)
              _ScoreChip(label: 'Yüzeyde: ${domainLabel(surface)}'),
            if (background.isNotEmpty &&
                background != primary &&
                background != secondary)
              _ScoreChip(label: 'Arka plan: ${domainLabel(background)}'),
          ],
        ),
        if (livedAs.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(livedAs, style: typo.bodyCompact.copyWith(color: colors.text)),
        ],
        if (mode.isNotEmpty) ...[
          const SizedBox(height: 4),
          Text('Mod: $mode', style: typo.meta.copyWith(color: colors.muted)),
        ],
      ],
    );
  }
}

class _NarrativeBlockCard extends StatelessWidget {
  const _NarrativeBlockCard({required this.block});

  final ProfileNarrativeBlock block;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final typo = profile.typography;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (block.headline.isNotEmpty)
          Text(
            block.headline,
            style: typo.cardTitle.copyWith(color: colors.text),
          ),
        if (block.teaser.isNotEmpty) ...[
          const SizedBox(height: 4),
          Text(block.teaser, style: typo.meta.copyWith(color: colors.muted)),
        ],
        if (block.body.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(
            block.body,
            style: typo.bodyCompact.copyWith(color: colors.text),
          ),
        ],
        if (block.micro.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(
            block.micro,
            style: typo.bodyCompact.copyWith(
              color: colors.text,
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
        if (block.chips.isNotEmpty) ...[
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: block.chips
                .take(4)
                .map((chip) => _ScoreChip(label: chip))
                .toList(),
          ),
        ],
      ],
    );
  }
}

class _ScoreChip extends StatelessWidget {
  const _ScoreChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: profile.spacing.sm,
        vertical: profile.spacing.xs,
      ),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(profile.radii.pillRadius),
        color: profile.colors.bg,
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      child: Text(
        label,
        style: profile.typography.label.copyWith(color: profile.colors.text),
      ),
    );
  }
}

class _SynastryImprintSection extends StatelessWidget {
  const _SynastryImprintSection({
    required this.imprint,
    required this.sourceYouName,
    required this.sourcePartnerName,
    required this.youName,
    required this.partnerName,
    this.sectionTitle,
  });

  final Map<String, dynamic> imprint;
  final String sourceYouName;
  final String sourcePartnerName;
  final String youName;
  final String partnerName;
  final String? sectionTitle;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final typo = profile.typography;
    final pairSignature = _personalizeImprintEntries(
      _toImprintList(imprint['pair_signature']),
      sourceAName: sourceYouName,
      sourceBName: sourcePartnerName,
      aName: youName,
      bName: partnerName,
    );
    final aToB = _personalizeImprintEntries(
      _toImprintList(imprint['a_to_b']),
      sourceAName: sourceYouName,
      sourceBName: sourcePartnerName,
      aName: youName,
      bName: partnerName,
    );
    final bToA = _personalizeImprintEntries(
      _toImprintList(imprint['b_to_a']),
      sourceAName: sourceYouName,
      sourceBName: sourcePartnerName,
      aName: youName,
      bName: partnerName,
    );
    final togetherField = _personalizeImprintEntries(
      _toImprintList(imprint['together_field']),
      sourceAName: sourceYouName,
      sourceBName: sourcePartnerName,
      aName: youName,
      bName: partnerName,
    );
    final sweetSpots = _personalizeImprintTextRows(
      _toImprintTextList(imprint['sweet_spots']),
      sourceAName: sourceYouName,
      sourceBName: sourcePartnerName,
      aName: youName,
      bName: partnerName,
    );
    final frictionPoints = _personalizeImprintTextRows(
      _toImprintTextList(imprint['friction_points']),
      sourceAName: sourceYouName,
      sourceBName: sourcePartnerName,
      aName: youName,
      bName: partnerName,
    );
    final headline = (imprint['headline'] ?? 'İkinizin Arasında')
        .toString()
        .trim();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          (sectionTitle ?? headline).trim(),
          style: typo.sectionTitle.copyWith(color: colors.text),
        ),
        const SizedBox(height: 8),
        Text(
          'Sen onda ne açıyorsun, o sende ne uyandırıyor, birlikte nasıl bir alan kuruyorsunuz.',
          style: typo.bodyCompact.copyWith(color: colors.muted),
        ),
        if ((sectionTitle ?? '').trim().isNotEmpty &&
            headline.isNotEmpty &&
            headline != sectionTitle) ...[
          const SizedBox(height: 8),
          Text(headline, style: typo.meta.copyWith(color: colors.textLight)),
        ],
        if (pairSignature.isNotEmpty) ...[
          const SizedBox(height: 16),
          _ImprintGroup(title: 'Bağın İmzaları', entries: pairSignature),
        ],
        if (aToB.isNotEmpty) ...[
          const SizedBox(height: 16),
          _ImprintGroup(title: '$youName onda', entries: aToB),
        ],
        if (bToA.isNotEmpty) ...[
          const SizedBox(height: 16),
          _ImprintGroup(title: '$partnerName sende', entries: bToA),
        ],
        if (togetherField.isNotEmpty) ...[
          const SizedBox(height: 16),
          _ImprintGroup(title: 'Birlikte Alanınız', entries: togetherField),
        ],
        if (sweetSpots.isNotEmpty || frictionPoints.isNotEmpty) ...[
          const SizedBox(height: 16),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              if (sweetSpots.isNotEmpty)
                _ImprintTextPanel(
                  title: 'Tatlı Çalışan Yer',
                  rows: sweetSpots,
                  accentColor: colors.text,
                ),
              if (frictionPoints.isNotEmpty)
                _ImprintTextPanel(
                  title: 'Zorlayan Yer',
                  rows: frictionPoints,
                  accentColor: colors.muted,
                ),
            ],
          ),
        ],
      ],
    );
  }
}

class _ImprintGroup extends StatelessWidget {
  const _ImprintGroup({required this.title, required this.entries});

  final String title;
  final List<Map<String, dynamic>> entries;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final typo = profile.typography;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: typo.cardTitle.copyWith(color: colors.text)),
        const SizedBox(height: 10),
        for (var i = 0; i < entries.length; i++) ...[
          _ImprintEntryCard(entry: entries[i]),
          if (i != entries.length - 1) const SizedBox(height: 10),
        ],
      ],
    );
  }
}

class _ImprintEntryCard extends StatelessWidget {
  const _ImprintEntryCard({required this.entry});

  final Map<String, dynamic> entry;

  @override
  Widget build(BuildContext context) {
    final label = (entry['label'] ?? '').toString().trim();
    final oneLiner = (entry['one_liner'] ?? '').toString().trim();
    final astroHint = (entry['astro_hint_soft'] ?? '').toString().trim();

    return JoviaTopicSurface(
      eyebrow: 'Bag imzasi',
      title: label,
      body: oneLiner,
      meta: [if (astroHint.isNotEmpty) astroHint],
    );
  }
}

class _ImprintTextPanel extends StatelessWidget {
  const _ImprintTextPanel({
    required this.title,
    required this.rows,
    required this.accentColor,
  });

  final String title;
  final List<Map<String, dynamic>> rows;
  final Color accentColor;

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(minWidth: 220, maxWidth: 420),
      child: JoviaReadingPanel(
        title: title,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (var i = 0; i < rows.length; i++) ...[
              Text(
                rows[i]['text'].toString(),
                style: context.profileTheme.typography.bodyCompact.copyWith(
                  color: accentColor,
                ),
              ),
              if (i != rows.length - 1) const SizedBox(height: 8),
            ],
          ],
        ),
      ),
    );
  }
}

class _GlassCard extends StatelessWidget {
  const _GlassCard({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return JoviaReadingPanel(padding: const EdgeInsets.all(18), child: child);
  }
}

List<Map<String, dynamic>> _toImprintList(dynamic raw) {
  if (raw is! List) {
    return const <Map<String, dynamic>>[];
  }
  return raw
      .whereType<Map>()
      .map((item) => Map<String, dynamic>.from(item))
      .where(
        (item) =>
            (item['label'] ?? '').toString().trim().isNotEmpty &&
            (item['one_liner'] ?? '').toString().trim().isNotEmpty,
      )
      .toList();
}

List<Map<String, dynamic>> _toImprintTextList(dynamic raw) {
  if (raw is! List) {
    return const <Map<String, dynamic>>[];
  }
  return raw
      .whereType<Map>()
      .map((item) => Map<String, dynamic>.from(item))
      .where((item) => (item['text'] ?? '').toString().trim().isNotEmpty)
      .toList();
}

List<Map<String, dynamic>> _personalizeImprintEntries(
  List<Map<String, dynamic>> entries, {
  required String sourceAName,
  required String sourceBName,
  required String aName,
  required String bName,
}) {
  return entries.map((entry) {
    return <String, dynamic>{
      ...entry,
      'label': _personalizeImprintText(
        (entry['label'] ?? '').toString(),
        sourceAName: sourceAName,
        sourceBName: sourceBName,
        aName: aName,
        bName: bName,
      ),
      'one_liner': _personalizeImprintText(
        (entry['one_liner'] ?? '').toString(),
        sourceAName: sourceAName,
        sourceBName: sourceBName,
        aName: aName,
        bName: bName,
      ),
      'astro_hint_soft': _personalizeImprintText(
        (entry['astro_hint_soft'] ?? '').toString(),
        sourceAName: sourceAName,
        sourceBName: sourceBName,
        aName: aName,
        bName: bName,
      ),
    };
  }).toList();
}

List<Map<String, dynamic>> _personalizeImprintTextRows(
  List<Map<String, dynamic>> rows, {
  required String sourceAName,
  required String sourceBName,
  required String aName,
  required String bName,
}) {
  return rows.map((row) {
    return <String, dynamic>{
      ...row,
      'text': _personalizeImprintText(
        (row['text'] ?? '').toString(),
        sourceAName: sourceAName,
        sourceBName: sourceBName,
        aName: aName,
        bName: bName,
      ),
    };
  }).toList();
}

const String _imprintHardConsonants = 'fstkcpşhçFSTKCPŞHÇ';
const String _imprintBackVowels = 'aıouAIOU';
const String _imprintFrontVowels = 'eiöüEİÖÜ';

String _lastImprintVowel(String text) {
  for (final char in text.split('').reversed) {
    if (_imprintBackVowels.contains(char) ||
        _imprintFrontVowels.contains(char)) {
      return char;
    }
  }
  return 'a';
}

bool _imprintEndsWithVowel(String text) {
  if (text.isEmpty) {
    return false;
  }
  final char = text[text.length - 1];
  return _imprintBackVowels.contains(char) ||
      _imprintFrontVowels.contains(char);
}

String _imprintWithSuffix(String text, String suffix) => "$text'$suffix";

String _imprintGenitiveSuffix(String text) {
  final vowel = _lastImprintVowel(text);
  if ('aıAI'.contains(vowel)) {
    return _imprintEndsWithVowel(text) ? 'nın' : 'ın';
  }
  if ('ouOU'.contains(vowel)) {
    return _imprintEndsWithVowel(text) ? 'nun' : 'un';
  }
  if ('öüÖÜ'.contains(vowel)) {
    return _imprintEndsWithVowel(text) ? 'nün' : 'ün';
  }
  return _imprintEndsWithVowel(text) ? 'nin' : 'in';
}

String _imprintDativeSuffix(String text) {
  final vowel = _lastImprintVowel(text);
  final base = _imprintBackVowels.contains(vowel) ? 'a' : 'e';
  return _imprintEndsWithVowel(text) ? 'y$base' : base;
}

String _imprintLocativeSuffix(String text) {
  final vowel = _lastImprintVowel(text);
  final base = _imprintBackVowels.contains(vowel) ? 'a' : 'e';
  final lastChar = text.isEmpty ? '' : text[text.length - 1];
  final prefix = _imprintHardConsonants.contains(lastChar) ? 't' : 'd';
  return '$prefix$base';
}

String _imprintAblativeSuffix(String text) {
  final locative = _imprintLocativeSuffix(text);
  return '$locative${locative.endsWith('a') ? 'n' : 'n'}';
}

String _imprintAccusativeSuffix(String text) {
  final vowel = _lastImprintVowel(text);
  String base;
  if ('aıAI'.contains(vowel)) {
    base = 'ı';
  } else if ('ouOU'.contains(vowel)) {
    base = 'u';
  } else if ('öüÖÜ'.contains(vowel)) {
    base = 'ü';
  } else {
    base = 'i';
  }
  return _imprintEndsWithVowel(text) ? 'y$base' : base;
}

String _imprintInstrumentalSuffix(String text) {
  final vowel = _lastImprintVowel(text);
  final base = _imprintBackVowels.contains(vowel) ? 'la' : 'le';
  return _imprintEndsWithVowel(text) ? 'y$base' : base;
}

String _personalizeImprintText(
  String value, {
  required String sourceAName,
  required String sourceBName,
  required String aName,
  required String bName,
}) {
  var text = value.trim();
  if (text.isEmpty) {
    return '';
  }

  final rawA = sourceAName.trim();
  final rawB = sourceBName.trim();
  if (rawA.isNotEmpty && rawA != aName) {
    text = text.replaceAll(rawA, aName);
  }
  if (rawB.isNotEmpty && rawB != bName) {
    text = text.replaceAll(rawB, bName);
  }

  final replacements = <MapEntry<String, String>>[
    MapEntry('Partner A', aName),
    MapEntry('Partner B', bName),
    MapEntry(
      "A, B'yi",
      '$aName, ${_imprintWithSuffix(bName, _imprintAccusativeSuffix(bName))}',
    ),
    MapEntry(
      "A, B'yı",
      '$aName, ${_imprintWithSuffix(bName, _imprintAccusativeSuffix(bName))}',
    ),
    MapEntry(
      "A, B'yle",
      '$aName, ${_imprintWithSuffix(bName, _imprintInstrumentalSuffix(bName))}',
    ),
    MapEntry(
      "A, B'yla",
      '$aName, ${_imprintWithSuffix(bName, _imprintInstrumentalSuffix(bName))}',
    ),
    MapEntry(
      "B, A'yi",
      '$bName, ${_imprintWithSuffix(aName, _imprintAccusativeSuffix(aName))}',
    ),
    MapEntry(
      "B, A'yı",
      '$bName, ${_imprintWithSuffix(aName, _imprintAccusativeSuffix(aName))}',
    ),
    MapEntry(
      "B, A'yle",
      '$bName, ${_imprintWithSuffix(aName, _imprintInstrumentalSuffix(aName))}',
    ),
    MapEntry(
      "B, A'yla",
      '$bName, ${_imprintWithSuffix(aName, _imprintInstrumentalSuffix(aName))}',
    ),
    MapEntry("A'nın", _imprintWithSuffix(aName, _imprintGenitiveSuffix(aName))),
    MapEntry("A'nin", _imprintWithSuffix(aName, _imprintGenitiveSuffix(aName))),
    MapEntry("B'nin", _imprintWithSuffix(bName, _imprintGenitiveSuffix(bName))),
    MapEntry("B'nın", _imprintWithSuffix(bName, _imprintGenitiveSuffix(bName))),
    MapEntry("A'ya", _imprintWithSuffix(aName, _imprintDativeSuffix(aName))),
    MapEntry("A'ye", _imprintWithSuffix(aName, _imprintDativeSuffix(aName))),
    MapEntry("B'ya", _imprintWithSuffix(bName, _imprintDativeSuffix(bName))),
    MapEntry("B'ye", _imprintWithSuffix(bName, _imprintDativeSuffix(bName))),
    MapEntry("A'da", _imprintWithSuffix(aName, _imprintLocativeSuffix(aName))),
    MapEntry("A'de", _imprintWithSuffix(aName, _imprintLocativeSuffix(aName))),
    MapEntry("B'da", _imprintWithSuffix(bName, _imprintLocativeSuffix(bName))),
    MapEntry("B'de", _imprintWithSuffix(bName, _imprintLocativeSuffix(bName))),
    MapEntry("A'dan", _imprintWithSuffix(aName, _imprintAblativeSuffix(aName))),
    MapEntry("A'den", _imprintWithSuffix(aName, _imprintAblativeSuffix(aName))),
    MapEntry("B'dan", _imprintWithSuffix(bName, _imprintAblativeSuffix(bName))),
    MapEntry("B'den", _imprintWithSuffix(bName, _imprintAblativeSuffix(bName))),
    MapEntry(
      "A'yi",
      _imprintWithSuffix(aName, _imprintAccusativeSuffix(aName)),
    ),
    MapEntry(
      "A'yı",
      _imprintWithSuffix(aName, _imprintAccusativeSuffix(aName)),
    ),
    MapEntry(
      "B'yi",
      _imprintWithSuffix(bName, _imprintAccusativeSuffix(bName)),
    ),
    MapEntry(
      "B'yı",
      _imprintWithSuffix(bName, _imprintAccusativeSuffix(bName)),
    ),
    MapEntry(
      "A'yle",
      _imprintWithSuffix(aName, _imprintInstrumentalSuffix(aName)),
    ),
    MapEntry(
      "A'yla",
      _imprintWithSuffix(aName, _imprintInstrumentalSuffix(aName)),
    ),
    MapEntry(
      "B'yle",
      _imprintWithSuffix(bName, _imprintInstrumentalSuffix(bName)),
    ),
    MapEntry(
      "B'yla",
      _imprintWithSuffix(bName, _imprintInstrumentalSuffix(bName)),
    ),
  ];

  for (final replacement in replacements) {
    text = text.replaceAll(replacement.key, replacement.value);
  }

  text = text.replaceAll(RegExp(r'\bA\b'), aName);
  text = text.replaceAll(RegExp(r'\bB\b'), bName);
  return text;
}
