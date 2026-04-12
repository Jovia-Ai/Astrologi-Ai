import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/timing/transit_repositories.dart';
import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/l10n/current_localizations.dart';
import 'package:mobile/l10n/l10n.dart';

class ProfileRelationshipPreview extends StatefulWidget {
  const ProfileRelationshipPreview({
    super.key,
    required this.profile,
    this.narrativeRepository,
    this.selectedDate,
  });

  final Map<String, dynamic>? profile;
  final NarrativeRepository? narrativeRepository;
  final DateTime? selectedDate;

  @override
  State<ProfileRelationshipPreview> createState() =>
      _ProfileRelationshipPreviewState();
}

class _ProfileRelationshipPreviewState
    extends State<ProfileRelationshipPreview> {
  late final NarrativeRepository _narrativeRepository;
  late final DateTime _selectedDate;

  bool _loading = false;
  String? _error;
  String? _notice;
  NarrativeResponse? _narrative;
  String? _lastProfileKey;
  int _requestEpoch = 0;

  @override
  void initState() {
    super.initState();
    _narrativeRepository = widget.narrativeRepository ?? NarrativeRepository();
    _selectedDate = TransitRequestBuilder.stripDate(
      widget.selectedDate ?? DateTime.now(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final profile = widget.profile;
    _maybeBootstrap(profile);

    if (!TransitRequestBuilder.hasProfile(profile)) {
      return JoviaReadingPanel(
        label: l10n.relationshipPreviewLabel,
        title: l10n.relationshipPreviewBirthDataRequiredTitle,
        body: l10n.relationshipPreviewBirthDataRequiredBody,
      );
    }

    final narrative = _narrative;
    final viewModel = _ProfileRelationshipViewModel.fromNarrative(
      narrative,
      selectedDate: _selectedDate,
    );
    final colors = context.profileTheme.colors;
    final typo = context.profileTheme.typography;

    if (_error != null && narrative == null) {
      return JoviaReadingPanel(
        label: l10n.relationshipPreviewLabel,
        title: l10n.relationshipPreviewLoadFailedTitle,
        body: _error!,
      );
    }

    return JoviaSurfaceCard(
      padding: const EdgeInsets.fromLTRB(20, 22, 20, 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          JoviaEditorialHeroBlock(
            surface: false,
            label: l10n.relationshipPreviewMainThemeLabel,
            title: viewModel.hook,
            body: viewModel.primarySummary,
            large: true,
            titleMaxLines: 4,
            bodyMaxLines: 6,
            accent: const JoviaIllustrationAccent(
              asset: JoviaIllustrationAsset.heart,
              width: 68,
              height: 68,
              opacity: 0.76,
            ),
            footer: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  viewModel.metaLine,
                  style: typo.meta.copyWith(
                    color: colors.textLight,
                    height: 1.45,
                  ),
                ),
                if (viewModel.primary != null) ...[
                  const SizedBox(height: 14),
                  _RelationshipMiniTimeline(card: viewModel.primary!),
                ],
                if (_error != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    _error!,
                    style: typo.meta.copyWith(
                      color: Theme.of(context).colorScheme.error,
                      height: 1.4,
                    ),
                  ),
                ] else if ((_notice ?? '').trim().isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text(
                    _notice!,
                    style: typo.meta.copyWith(
                      color: colors.textLight,
                      height: 1.4,
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 20),
          const ThinDivider(),
          const SizedBox(height: 16),
          _RelationshipNarrativeSection(
            label: l10n.relationshipPreviewDriversLabel,
            paragraphs: viewModel.driverParagraphs,
          ),
          const SizedBox(height: 16),
          const ThinDivider(),
          const SizedBox(height: 16),
          _RelationshipNarrativeSection(
            label: l10n.relationshipPreviewBackdropLabel,
            paragraphs: viewModel.backdropParagraphs,
          ),
          const SizedBox(height: 16),
          const ThinDivider(),
          const SizedBox(height: 16),
          _RelationshipNarrativeSection(
            label: l10n.relationshipPreviewUpperMeaningLabel,
            paragraphs: <String>[viewModel.upperMeaning],
            child:
                viewModel.supportingAsideTitle.isEmpty &&
                    viewModel.supportingAsideBody.isEmpty
                ? null
                : Padding(
                    padding: const EdgeInsets.only(top: 12),
                    child: JoviaUtilityRow(
                      label: l10n.relationshipPreviewSupportingThemeLabel,
                      title: viewModel.supportingAsideTitle,
                      body: viewModel.supportingAsideBody,
                      meta: [
                        if (viewModel.supportingAsideMeta.isNotEmpty)
                          viewModel.supportingAsideMeta,
                      ],
                    ),
                  ),
          ),
          if (viewModel.evidenceLines.isNotEmpty) ...[
            const SizedBox(height: 16),
            const ThinDivider(),
            const SizedBox(height: 8),
            _RelationshipWhyItMattersDisclosure(lines: viewModel.evidenceLines),
          ],
          if (_loading) ...[
            const SizedBox(height: 16),
            const ThinDivider(),
            const SizedBox(height: 14),
            const LinearProgressIndicator(),
          ],
        ],
      ),
    );
  }

  void _maybeBootstrap(Map<String, dynamic>? profile) {
    if (!TransitRequestBuilder.hasProfile(profile)) {
      return;
    }
    final key =
        '${profile?['birth_date']}|${profile?['birth_time']}|${profile?['place'] ?? profile?['city']}|${profile?['timezone']}|${TransitRequestBuilder.fmtDate(_selectedDate)}|relationship';
    if (_lastProfileKey == key) {
      return;
    }
    _lastProfileKey = key;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || profile == null) {
        return;
      }
      _loadNarrative(profile);
    });
  }

  Future<void> _loadNarrative(Map<String, dynamic> profile) async {
    final requestEpoch = ++_requestEpoch;
    setState(() {
      _loading = true;
      _error = null;
      _notice = null;
    });
    try {
      final response = await _fetchNarrative(
        profile,
        lens: 'relationship',
        receiveTimeout: ApiClient.timeoutFor(ApiRequestSla.background),
      );
      if (!mounted || requestEpoch != _requestEpoch) {
        return;
      }
      setState(() {
        _narrative = NarrativeResponse.fromMap(response);
        _loading = false;
      });
    } on DioException catch (exc) {
      final fallback = await _tryGeneralFallback(
        profile,
        requestEpoch: requestEpoch,
        cause: exc,
      );
      if (fallback) {
        return;
      }
      if (!mounted || requestEpoch != _requestEpoch) {
        return;
      }
      setState(() {
        _loading = false;
        _error = _friendlyError(exc);
      });
    } catch (exc) {
      if (!mounted || requestEpoch != _requestEpoch) {
        return;
      }
      setState(() {
        _loading = false;
        _error = context.l10n.errorGeneric;
      });
    }
  }

  Future<Map<String, dynamic>> _fetchNarrative(
    Map<String, dynamic> profile, {
    required String lens,
    required Duration receiveTimeout,
  }) {
    return _narrativeRepository.fetchDailyNarrative(
      profile: profile,
      selectedDate: _selectedDate,
      lens: lens,
      focusedRange: true,
      includeBestTimes: false,
      responseMode: 'public_only',
      payloadProfile: TransitPayloadProfile.relationshipPreview,
      receiveTimeout: receiveTimeout,
      requestSla: lens == 'relationship'
          ? ApiRequestSla.background
          : ApiRequestSla.interactive,
    );
  }

  Future<bool> _tryGeneralFallback(
    Map<String, dynamic> profile, {
    required int requestEpoch,
    required DioException cause,
  }) async {
    final status = cause.response?.statusCode ?? 0;
    final canFallback =
        cause.type == DioExceptionType.receiveTimeout ||
        cause.type == DioExceptionType.connectionTimeout ||
        status >= 500;
    if (!canFallback) {
      return false;
    }
    try {
      final response = await _fetchNarrative(
        profile,
        lens: 'general',
        receiveTimeout: ApiClient.timeoutFor(ApiRequestSla.interactive),
      );
      if (!mounted || requestEpoch != _requestEpoch) {
        return true;
      }
      setState(() {
        _narrative = NarrativeResponse.fromMap(response);
        _loading = false;
        _error = null;
        _notice = context.l10n.relationshipPreviewFallbackNotice;
      });
      return true;
    } catch (_) {
      return false;
    }
  }

  String _friendlyError(DioException exc) {
    if (exc.type == DioExceptionType.receiveTimeout ||
        exc.type == DioExceptionType.connectionTimeout) {
      return context.l10n.relationshipPreviewTimeout;
    }
    final status = exc.response?.statusCode;
    if (status == 422) {
      return context.l10n.relationshipPreviewInvalidProfile;
    }
    if (status != null && status >= 500) {
      return context.l10n.relationshipPreviewServerError;
    }
    return exc.message ?? context.l10n.relationshipPreviewFetchFailed;
  }
}

class _ProfileRelationshipViewModel {
  const _ProfileRelationshipViewModel({
    required this.hook,
    required this.primarySummary,
    required this.metaLine,
    required this.driverParagraphs,
    required this.backdropParagraphs,
    required this.upperMeaning,
    required this.supportingAsideTitle,
    required this.supportingAsideBody,
    required this.supportingAsideMeta,
    required this.evidenceLines,
    required this.primary,
  });

  final String hook;
  final String primarySummary;
  final String metaLine;
  final List<String> driverParagraphs;
  final List<String> backdropParagraphs;
  final String upperMeaning;
  final String supportingAsideTitle;
  final String supportingAsideBody;
  final String supportingAsideMeta;
  final List<String> evidenceLines;
  final EventCardDto? primary;

  factory _ProfileRelationshipViewModel.fromNarrative(
    NarrativeResponse? narrative, {
    required DateTime selectedDate,
  }) {
    final blocks = _RelationshipNarrativeBlocks.fromNarrative(narrative);
    final primary = blocks.primary;

    final evidenceLines = _buildRelationshipNarrativeEvidence(
      primary: primary,
      drivers: blocks.driverCards,
      backdrops: blocks.backdropCards,
    );

    final metaPieces = <String>[
      _formatDateLabel(selectedDate),
      if ((primary?.timeHintTr ?? '').trim().isNotEmpty)
        primary!.timeHintTr.trim()
      else if ((primary?.timing.timingNote ?? '').trim().isNotEmpty)
        primary!.timing.timingNote.trim(),
      if (primary?.isPeriodDerived == true)
        currentL10n().relationshipPreviewPeriodToToday,
    ];

    return _ProfileRelationshipViewModel(
      hook: normalizeTurkishText(blocks.hook),
      primarySummary: normalizeTurkishText(
        _joinSentences([blocks.primarySummary, blocks.playfulLine]),
      ),
      metaLine: normalizeTurkishText(
        metaPieces.where((item) => item.trim().isNotEmpty).join(' • '),
      ),
      driverParagraphs: blocks.driverParagraphs
          .map(normalizeTurkishText)
          .toList(),
      backdropParagraphs: blocks.backdropParagraphs
          .map(normalizeTurkishText)
          .toList(),
      upperMeaning: normalizeTurkishText(blocks.upperMeaning),
      supportingAsideTitle: normalizeTurkishText(blocks.supportingAsideTitle),
      supportingAsideBody: normalizeTurkishText(blocks.supportingAsideBody),
      supportingAsideMeta: normalizeTurkishText(blocks.supportingAsideMeta),
      evidenceLines: evidenceLines.map(normalizeTurkishText).toList(),
      primary: primary,
    );
  }
}

class _RelationshipNarrativeSection extends StatelessWidget {
  const _RelationshipNarrativeSection({
    required this.label,
    required this.paragraphs,
    this.child,
  });

  final String label;
  final List<String> paragraphs;
  final Widget? child;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final cleanParagraphs = paragraphs
        .map(normalizeTurkishText)
        .where((item) => item.isNotEmpty)
        .toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          turkishToUpper(label),
          style: profile.typography.monoEyebrow.copyWith(
            color: profile.colors.textLight,
            letterSpacing: 1.65,
          ),
        ),
        const SizedBox(height: 8),
        for (var index = 0; index < cleanParagraphs.length; index++) ...[
          Text(
            cleanParagraphs[index],
            style: profile.typography.bodyCompact.copyWith(
              color: profile.colors.text,
              height: 1.56,
            ),
          ),
          if (index != cleanParagraphs.length - 1) const SizedBox(height: 12),
        ],
        if (child != null) ...[child!],
      ],
    );
  }
}

class _RelationshipNarrativeBlocks {
  const _RelationshipNarrativeBlocks({
    required this.hook,
    required this.primarySummary,
    required this.driverParagraphs,
    required this.backdropParagraphs,
    required this.upperMeaning,
    required this.supportingAsideTitle,
    required this.supportingAsideBody,
    required this.supportingAsideMeta,
    required this.playfulLine,
    required this.primary,
    required this.driverCards,
    required this.backdropCards,
  });

  final String hook;
  final String primarySummary;
  final List<String> driverParagraphs;
  final List<String> backdropParagraphs;
  final String upperMeaning;
  final String supportingAsideTitle;
  final String supportingAsideBody;
  final String supportingAsideMeta;
  final String playfulLine;
  final EventCardDto? primary;
  final List<EventCardDto> driverCards;
  final List<EventCardDto> backdropCards;

  factory _RelationshipNarrativeBlocks.fromNarrative(
    NarrativeResponse? narrative,
  ) {
    final driverCards = _pickRelationshipDriverCards(narrative);
    final primary = driverCards.isNotEmpty
        ? driverCards.first
        : _pickRelationshipFallbackCard(narrative);
    final secondary = _pickRelationshipCounterweight(driverCards);
    final backdropCards = _pickRelationshipBackdropCards(
      narrative,
      exclude: driverCards,
    );
    final supportingAside = _pickRelationshipSupportingCard(
      narrative,
      exclude: <EventCardDto>[...driverCards, ...backdropCards],
    );
    final playfulLine = _buildRelationshipPlayfulLine(
      primary: primary,
      drivers: driverCards,
      backdrops: backdropCards,
    );

    final driverParagraphs = driverCards
        .take(3)
        .map(_buildRelationshipDriverParagraph)
        .where((item) => item.trim().isNotEmpty)
        .toList();
    final backdropParagraphs = backdropCards
        .take(2)
        .map(_buildRelationshipBackdropParagraph)
        .where((item) => item.trim().isNotEmpty)
        .toList();

    if (backdropParagraphs.isEmpty) {
      final fallback = _buildRelationshipPeriodCoreFallback(
        narrative?.periodCore,
      );
      if (fallback.isNotEmpty) {
        backdropParagraphs.add(fallback);
      }
    }

    return _RelationshipNarrativeBlocks(
      hook: _buildRelationshipNarrativeHook(
        primary: primary,
        secondary: secondary,
        backdrops: backdropCards,
      ),
      primarySummary: _buildRelationshipPrimarySummary(
        primary: primary,
        secondary: secondary,
        backdrops: backdropCards,
        periodCore: narrative?.periodCore,
      ),
      driverParagraphs: driverParagraphs.isEmpty
          ? <String>[currentL10n().relationshipPreviewDefaultDriversFallback]
          : driverParagraphs,
      backdropParagraphs: backdropParagraphs.isEmpty
          ? <String>[currentL10n().relationshipPreviewDefaultBackdropFallback]
          : backdropParagraphs,
      upperMeaning: _buildRelationshipUpperMeaning(
        primary: primary,
        secondary: secondary,
        backdrops: backdropCards,
        periodCore: narrative?.periodCore,
      ),
      supportingAsideTitle: _buildRelationshipSupportingTitle(supportingAside),
      supportingAsideBody: _buildRelationshipSupportingBody(supportingAside),
      supportingAsideMeta: _firstNonEmpty([
        supportingAside?.timeHintTr,
        supportingAside?.timing.timingNote,
      ]),
      playfulLine: playfulLine,
      primary: primary,
      driverCards: driverCards,
      backdropCards: backdropCards,
    );
  }
}

EventCardDto? _pickRelationshipCounterweight(List<EventCardDto> drivers) {
  for (final card in drivers.skip(1)) {
    if (_relationshipMode(card) == 'polarity' ||
        _relationshipMode(card) == 'friction' ||
        _relationshipRunsThroughMind(card)) {
      return card;
    }
  }
  return drivers.length > 1 ? drivers[1] : null;
}

class _RelationshipMiniTimeline extends StatelessWidget {
  const _RelationshipMiniTimeline({required this.card});

  final EventCardDto card;

  int _activeStage() {
    final phase = card.phase.trim().toLowerCase();
    return switch (phase) {
      'exact' || 'exactish' => 2,
      'separating' => 3,
      'applying' => 1,
      _ => card.timing.entryDateUtc.trim().isNotEmpty ? 0 : 1,
    };
  }

  @override
  Widget build(BuildContext context) {
    final stages = <String>[
      context.l10n.relationshipPreviewStageStarted,
      context.l10n.relationshipPreviewStageIntensifying,
      context.l10n.relationshipPreviewStagePeak,
      context.l10n.relationshipPreviewStageResolving,
    ];
    final profile = context.profileTheme;
    final activeStage = _activeStage();
    return Row(
      children: [
        for (var index = 0; index < stages.length; index++) ...[
          _RelationshipMiniTimelineNode(
            label: stages[index],
            active: index <= activeStage,
            emphasized: index == activeStage,
          ),
          if (index != stages.length - 1)
            Expanded(
              child: Container(
                height: 1,
                margin: const EdgeInsets.only(bottom: 18),
                color: profile.colors.strokeSoft.withValues(
                  alpha: index < activeStage ? 0.95 : 0.56,
                ),
              ),
            ),
        ],
      ],
    );
  }
}

List<EventCardDto> _pickRelationshipDriverCards(NarrativeResponse? narrative) {
  if (narrative == null) {
    return const <EventCardDto>[];
  }

  final pool = _dedupeRelationshipCards(<EventCardDto>[
    ...narrative.dailyEventCards,
    ...narrative.eventCards.where(_isDriverLikeRelationshipCard),
  ]);
  final candidates =
      pool
          .where(_hasReadableRelationshipCopy)
          .where(_isRelationshipCandidate)
          .toList()
        ..sort(
          (left, right) => _relationshipNarrativeScore(
            right,
            periodLayer: false,
          ).compareTo(_relationshipNarrativeScore(left, periodLayer: false)),
        );

  final selected = <EventCardDto>[];
  final seenSimilarity = <String>{};

  for (final card in candidates) {
    if (selected.length >= 3) {
      break;
    }
    final score = _relationshipNarrativeScore(card, periodLayer: false);
    if (selected.isNotEmpty && score < 0.28) {
      continue;
    }
    final similarityKey = _relationshipSimilarityKey(card);
    if (seenSimilarity.contains(similarityKey)) {
      continue;
    }
    selected.add(card);
    seenSimilarity.add(similarityKey);
  }

  if (selected.isEmpty && candidates.isNotEmpty) {
    return <EventCardDto>[candidates.first];
  }
  return selected;
}

List<EventCardDto> _pickRelationshipBackdropCards(
  NarrativeResponse? narrative, {
  required List<EventCardDto> exclude,
}) {
  if (narrative == null) {
    return const <EventCardDto>[];
  }

  final excludedKeys = exclude
      .map(_relationshipIdentityKey)
      .where((item) => item.isNotEmpty)
      .toSet();
  final pool = _dedupeRelationshipCards(<EventCardDto>[
    ...narrative.periodEventCards,
    ...narrative.eventCards.where(_isBackdropLikeRelationshipCard),
  ]);
  final candidates =
      pool
          .where(
            (card) => !excludedKeys.contains(_relationshipIdentityKey(card)),
          )
          .where(_hasReadableRelationshipCopy)
          .where(_isRelationshipCandidate)
          .where(
            (card) =>
                _relationshipProjectedScore(card) >= 0.24 ||
                const <String>{
                  'venus',
                  'dsc',
                  'moon',
                  'mars',
                }.contains(_relationshipFocusKey(card)),
          )
          .toList()
        ..sort(
          (left, right) => _relationshipNarrativeScore(
            right,
            periodLayer: true,
          ).compareTo(_relationshipNarrativeScore(left, periodLayer: true)),
        );

  final selected = <EventCardDto>[];
  final seenSimilarity = <String>{};

  for (final card in candidates) {
    if (selected.length >= 2) {
      break;
    }
    final score = _relationshipNarrativeScore(card, periodLayer: true);
    if (selected.isNotEmpty && score < 0.34) {
      continue;
    }
    final similarityKey = _relationshipSimilarityKey(card);
    if (seenSimilarity.contains(similarityKey)) {
      continue;
    }
    selected.add(card);
    seenSimilarity.add(similarityKey);
  }

  if (selected.isEmpty && candidates.isNotEmpty) {
    return <EventCardDto>[candidates.first];
  }
  if (selected.length < 2) {
    for (final card in candidates) {
      if (selected.any(
        (existing) =>
            _relationshipIdentityKey(existing) ==
            _relationshipIdentityKey(card),
      )) {
        continue;
      }
      if (!const <String>{
        'venus',
        'dsc',
        'moon',
        'mars',
      }.contains(_relationshipFocusKey(card))) {
        continue;
      }
      selected.add(card);
      if (selected.length >= 2) {
        break;
      }
    }
  }
  return selected;
}

EventCardDto? _pickRelationshipSupportingCard(
  NarrativeResponse? narrative, {
  required List<EventCardDto> exclude,
}) {
  if (narrative == null) {
    return null;
  }

  final excludedKeys = exclude
      .map(_relationshipIdentityKey)
      .where((item) => item.isNotEmpty)
      .toSet();
  final pool = _dedupeRelationshipCards(<EventCardDto>[
    ...narrative.dailyEventCards,
    ...narrative.periodEventCards,
    ...narrative.eventCards,
  ]);
  final candidates =
      pool
          .where(
            (card) => !excludedKeys.contains(_relationshipIdentityKey(card)),
          )
          .where(_hasReadableRelationshipCopy)
          .where(_isRelationshipCandidate)
          .where(
            (card) =>
                _relationshipProjectedScore(card) >= 0.22 ||
                const <String>{
                  'venus',
                  'dsc',
                  'moon',
                  'mars',
                  'mercury',
                }.contains(_relationshipFocusKey(card)),
          )
          .toList()
        ..sort(
          (left, right) =>
              _relationshipNarrativeScore(
                right,
                periodLayer: _isBackdropLikeRelationshipCard(right),
              ).compareTo(
                _relationshipNarrativeScore(
                  left,
                  periodLayer: _isBackdropLikeRelationshipCard(left),
                ),
              ),
        );

  for (final card in candidates) {
    if (_relationshipNarrativeScore(
          card,
          periodLayer: _isBackdropLikeRelationshipCard(card),
        ) <
        0.26) {
      continue;
    }
    return card;
  }
  return null;
}

EventCardDto? _pickRelationshipFallbackCard(NarrativeResponse? narrative) {
  if (narrative == null) {
    return null;
  }
  for (final card in <EventCardDto>[
    ...narrative.dailyEventCards,
    ...narrative.periodEventCards,
    ...narrative.eventCards,
  ]) {
    if (_hasReadableRelationshipCopy(card)) {
      return card;
    }
  }
  return null;
}

List<EventCardDto> _dedupeRelationshipCards(Iterable<EventCardDto> cards) {
  final out = <EventCardDto>[];
  final seen = <String>{};
  for (final card in cards) {
    final key = _relationshipIdentityKey(card);
    if (key.isEmpty || seen.add(key)) {
      out.add(card);
    }
  }
  return out;
}

bool _isDriverLikeRelationshipCard(EventCardDto card) {
  final bucket = card.bucket.trim().toLowerCase();
  final horizon = card.horizon.trim().toLowerCase();
  final sourceHorizon = card.sourceHorizon.trim().toLowerCase();
  return horizon == 'daily' ||
      sourceHorizon == 'daily' ||
      bucket == 'short' ||
      bucket == 'medium';
}

bool _isBackdropLikeRelationshipCard(EventCardDto card) {
  final bucket = card.bucket.trim().toLowerCase();
  final horizon = card.horizon.trim().toLowerCase();
  final sourceHorizon = card.sourceHorizon.trim().toLowerCase();
  return bucket == 'long' || horizon == 'period' || sourceHorizon == 'period';
}

bool _isRelationshipCandidate(EventCardDto card) {
  if (_relationshipProjectedScore(card) >= 0.18) {
    return true;
  }
  if (const <String>{
    'venus',
    'dsc',
    'moon',
    'mars',
    'mercury',
    'sun',
    'asc',
    'lilith',
  }.contains(_relationshipFocusKey(card))) {
    return true;
  }
  final houses = <int>{
    _relationshipHouse(card, 'target_house'),
    _relationshipHouse(card, 'source_house'),
  }.where((item) => item > 0).toSet();
  if (houses.any((item) => const <int>{5, 7, 8, 12}.contains(item))) {
    return true;
  }
  return const <String>{
    'venus',
    'moon',
    'mars',
    'jupiter',
    'saturn',
    'neptune',
    'lilith',
    'nodes',
  }.contains(_relationshipSourceFamily(card));
}

bool _hasReadableRelationshipCopy(EventCardDto card) {
  return [
    card.feltLineTr,
    card.whyItFeelsThisWayTr,
    card.guidanceMicroTr,
    card.title,
    card.opening,
    card.essence,
    card.bigPicture,
  ].any((item) => item.trim().isNotEmpty);
}

double _relationshipNarrativeScore(
  EventCardDto card, {
  required bool periodLayer,
}) {
  var score = _relationshipProjectedScore(card) * (periodLayer ? 1.55 : 1.7);

  score += switch (_relationshipFocusKey(card)) {
    'venus' => 0.46,
    'dsc' => 0.42,
    'moon' => 0.30,
    'mars' => 0.28,
    'mercury' => 0.16,
    'sun' => 0.12,
    'asc' => 0.08,
    'lilith' => 0.10,
    _ => 0.0,
  };

  final targetHouse = _relationshipHouse(card, 'target_house');
  final sourceHouse = _relationshipHouse(card, 'source_house');
  if (const <int>{5, 7, 8}.contains(targetHouse)) {
    score += 0.18;
  }
  if (const <int>{5, 7, 8}.contains(sourceHouse)) {
    score += 0.12;
  }
  if (targetHouse == 12) {
    score += 0.08;
  }
  if (_relationshipIsPrivate(card)) {
    score += 0.04;
  }

  score += switch (_relationshipMode(card)) {
    'flow' => 0.10,
    'opening' => 0.11,
    'polarity' => 0.12,
    'friction' => 0.11,
    'intensify' => 0.10,
    'concentration' => 0.05,
    _ => 0.04,
  };

  if (periodLayer) {
    if (_isBackdropLikeRelationshipCard(card)) {
      score += 0.18;
    }
    if (card.bucket.trim().toLowerCase() == 'long') {
      score += 0.08;
    }
    if (const <String>{
      'neptune',
      'saturn',
      'nodes',
    }.contains(_relationshipSourceFamily(card))) {
      score += 0.07;
    }
  } else {
    if (_isDriverLikeRelationshipCard(card)) {
      score += 0.16;
    }
    if (!card.isPeriodDerived) {
      score += 0.10;
    }
    if (const <String>{
      'short',
      'medium',
    }.contains(card.bucket.trim().toLowerCase())) {
      score += 0.06;
    }
  }

  if (!_hasReadableRelationshipCopy(card)) {
    score -= 1.0;
  }
  return score;
}

double _relationshipProjectedScore(EventCardDto card) {
  final projected = card.lensProjection['projected_scores'];
  if (projected is Map) {
    return _asDouble(projected['relationships']);
  }
  return _asDouble(card.domainScores['relationships']);
}

double _asDouble(dynamic value) {
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse('$value') ?? 0.0;
}

int _relationshipHouse(EventCardDto card, String key) {
  final raw = card.semanticCore[key];
  if (raw is num) {
    return raw.toInt();
  }
  return int.tryParse('${raw ?? ''}') ?? 0;
}

String _relationshipIdentityKey(EventCardDto card) {
  final eventId = card.eventId.trim();
  if (eventId.isNotEmpty) {
    return eventId;
  }
  return [
    card.transitBody.trim().toLowerCase(),
    card.natalPoint.trim().toLowerCase(),
    card.aspect.trim().toLowerCase(),
    card.phase.trim().toLowerCase(),
    card.bucket.trim().toLowerCase(),
  ].join('|');
}

String _relationshipSimilarityKey(EventCardDto card) {
  return [
    _relationshipSourceFamily(card),
    _relationshipFocusKey(card),
    _relationshipMode(card),
    _isBackdropLikeRelationshipCard(card) ? 'period' : 'daily',
  ].join('|');
}

String _relationshipSourceFamily(EventCardDto card) {
  final body = card.transitBody.trim().toLowerCase();
  if (body == 'north node' || body == 'south node') {
    return 'nodes';
  }
  return body;
}

String _buildRelationshipNarrativeHook({
  required EventCardDto? primary,
  required EventCardDto? secondary,
  required List<EventCardDto> backdrops,
}) {
  if (primary == null) {
    return 'Iliskilerde ana tema yavas yavas netlesiyor.';
  }

  final primaryMode = _relationshipMode(primary);
  final secondaryMode = secondary == null ? '' : _relationshipMode(secondary);

  if (const <String>{'flow', 'opening'}.contains(primaryMode) &&
      const <String>{'polarity', 'friction'}.contains(secondaryMode)) {
    return 'Yakinlasma var, ama kesinlik yok.';
  }
  if (const <String>{'flow', 'opening'}.contains(primaryMode) &&
      _hasHeavyRelationshipBackdrop(backdrops)) {
    return 'Yakinlasma var; ama netlik henuz tam degil.';
  }
  if (primaryMode == 'polarity') {
    return 'Bir yandan yaklasmak, bir yandan korunmak istiyorsun.';
  }
  if (primaryMode == 'friction') {
    return 'Cekim var; ama rahat ilerlemiyor.';
  }
  if (primaryMode == 'intensify') {
    return 'Cekim guclu; ama bunu nereye koyacagin henuz net degil.';
  }
  return 'Yakinlasma kolaylasiyor.';
}

String _buildRelationshipPrimarySummary({
  required EventCardDto? primary,
  required EventCardDto? secondary,
  required List<EventCardDto> backdrops,
  required PeriodCoreDto? periodCore,
}) {
  if (primary == null) {
    return 'Bugun iliski tarafinda hareket var, ama tek bir tema henuz tam olarak secilemiyor.';
  }

  final primaryMode = _relationshipMode(primary);
  final secondaryMode = secondary == null ? '' : _relationshipMode(secondary);
  final hasThinkingLine =
      secondary != null && _relationshipRunsThroughMind(secondary);
  final heavyBackdrop = _hasHeavyRelationshipBackdrop(backdrops);

  if (const <String>{'flow', 'opening'}.contains(primaryMode)) {
    final middle = hasThinkingLine
        ? 'Ama ayni anda buna ne kadar guvenecegin, bunu nasil soyleyecegin ve fazla mi buyuttugun tarafi da calisiyor.'
        : heavyBackdrop
        ? 'Ama altta netlik ve sinir konusunu zorlayan daha agir bir donem de suruyor.'
        : 'Bugunun guzel tarafi, kucuk bir yumusamanin bile gercek hissettirmesi.';
    final closing =
        const <String>{'polarity', 'friction'}.contains(secondaryMode) ||
            heavyBackdrop
        ? 'Yani gunun ozeti: yakinlasma var, ama kesinlik yok.'
        : 'Yani gunun ozeti: yakinlasma daha kolay, ama yine de acele etmemek daha iyi.';
    return _joinSentences([
      'Birine karsi yumusama, yaklasma istegi ve temas etme ihtimali var.',
      middle,
      closing,
    ]);
  }

  if (primaryMode == 'polarity') {
    return _joinSentences([
      'Bir yandan acilmak, konusmak ve yaklasmak istiyorsun.',
      'Bir yandan da kendini korumak, fazla anlam yuklememek ve geri cekilmek istiyorsun.',
      'Bu kararsizlik gibi gorunse de aslinda ayni anda iki ihtiyacin calismasi.',
    ]);
  }

  if (primaryMode == 'friction') {
    return _joinSentences([
      'Bugun iliskide cekim varsa bile rahat akmiyor.',
      'Hoslanma, ifade etme ve guvenme taraflari ayni hizda gitmeyebilir.',
      heavyBackdrop
          ? 'Bu yuzden kucuk bir seyi hemen kesin cevap gibi okumamak daha iyi.'
          : 'Buradaki surtunme seni daha net olmaya zorluyor.',
    ]);
  }

  final fallback = _firstNonEmpty([
    primary.feltLineTr,
    primary.whyItFeelsThisWayTr,
    periodCore?.coreStory,
  ]);
  return fallback.isNotEmpty
      ? _softenRawLine(fallback)
      : 'Bugun iliski tarafinda belirgin bir hareket var.';
}

String _buildRelationshipDriverParagraph(EventCardDto card) {
  return _joinSentences([
    _buildRelationshipDriverLead(card),
    _buildRelationshipConcreteLine(card),
    _buildRelationshipInterpretiveLine(card),
  ]);
}

String _buildRelationshipBackdropParagraph(EventCardDto card) {
  return _joinSentences([
    _buildRelationshipBackdropLead(card),
    _buildRelationshipBackdropConcreteLine(card),
    _buildRelationshipBackdropMeaningLine(card),
  ]);
}

String _buildRelationshipUpperMeaning({
  required EventCardDto? primary,
  required EventCardDto? secondary,
  required List<EventCardDto> backdrops,
  required PeriodCoreDto? periodCore,
}) {
  if (primary == null) {
    final fallback = _firstNonEmpty([
      periodCore?.upperMeaning,
      periodCore?.bigPicture,
      periodCore?.coreStory,
    ]);
    return fallback.isNotEmpty
        ? _softenRawLine(fallback)
        : 'Bu surec iliski tarafinda neyi ciddiye aldigini zamanla daha net gosterecek.';
  }

  final primaryMode = _relationshipMode(primary);
  if (const <String>{'flow', 'opening'}.contains(primaryMode)) {
    return _joinSentences([
      'Kalp tarafi aciliyor, ama zihnin hemen teslim olmuyor.',
      'Bu iyi bir sey; cunku kucuk bir yakinligi buyuk bir kesinlik sanmadan once neyin gercekten olgunlastigini gorebiliyorsun.',
    ]);
  }
  if (primaryMode == 'polarity') {
    return _joinSentences([
      'Ayni anda hem yaklasmak hem korunmak istemen zayiflik degil.',
      'Bu donem sana siniri ve samimiyeti ayni yerde tutmayi ogretiyor.',
    ]);
  }
  if (primaryMode == 'friction') {
    return _joinSentences([
      'Bu donem iliskide neyi istedigini romantik bir fikir olarak degil, gercek bir ihtiyac olarak ayirt etmeyi ogretiyor.',
      'O yuzden rahat ilerlemeyen sey bile uzun vadede daha dogru bir secime donebilir.',
    ]);
  }

  final fallback = _firstNonEmpty([
    periodCore?.upperMeaning,
    periodCore?.bigPicture,
    primary.upper,
    primary.whatItBuilds,
  ]);
  return fallback.isNotEmpty
      ? _softenRawLine(fallback)
      : 'Bu surec iliski icinde neyi gercekten istedigini daha netlestiriyor.';
}

String _buildRelationshipSupportingTitle(EventCardDto? card) {
  if (card == null) {
    return '';
  }
  return switch (_relationshipSourceFamily(card)) {
    'nodes' => 'Eski aliskanliklar da kendini hatirlatiyor.',
    'moon' => 'Duygusal taraf daha kolay yumusayabilir.',
    'venus' => 'Kucuk ama gercek bir yakinlasma daha var.',
    'jupiter' => 'Beklenti de kolayca buyuyebilir.',
    _ => _firstNonEmpty([card.feltLineTr, card.title]),
  };
}

String _buildRelationshipSupportingBody(EventCardDto? card) {
  if (card == null) {
    return '';
  }
  if (_relationshipSourceFamily(card) == 'nodes') {
    return 'Bu tema tanidik gelen ama seni yormus iliski aliskanliklarini tekrar hatirlatabilir. Fark etmek bile ayni donguye geri donmemek icin faydali.';
  }
  if (_relationshipMode(card) == 'flow' ||
      _relationshipMode(card) == 'opening') {
    return 'Ana hikaye daha buyuk olsa da burada iliskiyi yumusatan kucuk bir destek var. Tam da bu yuzden sert duran bir sey biraz daha kolaylasabilir.';
  }
  if (_relationshipMode(card) == 'polarity') {
    return 'Bu yan tema hem yaklasma hem geri durma istegini ayni anda canli tutuyor. Ana hikayeye ince bir fazla dusunme payi ekliyor.';
  }
  return _joinSentences([
    _buildRelationshipConcreteLine(card),
    _buildRelationshipInterpretiveLine(card),
  ]);
}

String _buildRelationshipPlayfulLine({
  required EventCardDto? primary,
  required List<EventCardDto> drivers,
  required List<EventCardDto> backdrops,
}) {
  if (primary == null || _isHeavyRelationshipDay(primary, backdrops)) {
    return '';
  }
  for (final card in drivers) {
    if (_relationshipIdentityKey(card) == _relationshipIdentityKey(primary)) {
      continue;
    }
    if (_relationshipRunsThroughMind(card) &&
        _relationshipMode(card) == 'polarity') {
      return 'Mesaj atma enerjisi var; sonra bir kosede onun analizini yapma enerjisi de var.';
    }
  }
  if (_relationshipRunsThroughMind(primary) &&
      _relationshipMode(primary) == 'polarity') {
    return 'Bir sey hissetmek kolay; onu fazla dusunmemek o kadar kolay degil.';
  }
  return '';
}

List<String> _buildRelationshipNarrativeEvidence({
  required EventCardDto? primary,
  required List<EventCardDto> drivers,
  required List<EventCardDto> backdrops,
}) {
  final lines = <String>[];
  if (primary != null) {
    lines.add(
      'Bu yorum once ${_relationshipFocus(primary).toLowerCase()} gostergelerine yaslandi; o yuzden anlati iliski, yakinlasma ve iletisim tarafinda toplandi.',
    );
  }
  if (drivers.isNotEmpty) {
    lines.add(
      '${drivers.take(2).map(_relationshipAstroSignature).join(' ve ')} bugunun ana kisa ve orta vade hattini kuruyor.',
    );
  }
  if (backdrops.isNotEmpty) {
    lines.add(
      '${backdrops.take(2).map(_relationshipAstroSignature).join(' ve ')} ise altta daha uzun sure calisan donemi tasiyor.',
    );
  }
  if (primary != null && (primary.houseTouchpointTr).trim().isNotEmpty) {
    lines.add(
      'En erken ${primary.houseTouchpointTr.trim()} tarafinda hissedilmesi de bu yuzden.',
    );
  }
  return lines.take(4).toList();
}

String _buildRelationshipDriverLead(EventCardDto card) {
  final signature = _relationshipAstroSignature(card);
  final phaseLine = _relationshipTimingPhrase(card);
  final span = _relationshipSpanLabel(card);
  return switch (_relationshipMode(card)) {
    'opening' => '$signature $span bir acilma ve $phaseLine.',
    'polarity' => '$signature $span bir karsitlik ve $phaseLine.',
    'friction' => '$signature $span bir surtunme ve $phaseLine.',
    'intensify' => '$signature $span bir yogunlasma ve $phaseLine.',
    'concentration' => '$signature $span bir odaklanma ve $phaseLine.',
    _ => '$signature $span bir akis ve $phaseLine.',
  };
}

String _buildRelationshipConcreteLine(EventCardDto card) {
  final focusKey = _relationshipFocusKey(card);
  final mode = _relationshipMode(card);

  if (focusKey == 'venus' && _relationshipIsPrivate(card)) {
    return 'Birini daha cok dusunmek, mesaj atmanin kolaylasmasi ya da kucuk bir temasin sende daha fazla etki birakmasi gibi calisabilir.';
  }
  if (focusKey == 'venus') {
    return switch (mode) {
      'friction' =>
        'Hoslandigin kisiyi tam istedigin gibi anlatamamak, kucuk bir seyi buyutmek ya da alinmak gibi calisabilir.',
      'intensify' =>
        'Cekim daha ham, daha durust ve biraz da saklamasi zor bir yerden gelebilir.',
      _ =>
        'Araniz yumusayabilir, iletisim rahatlayabilir ya da karsi tarafin ilgisi daha acik hissedilebilir.',
    };
  }
  if (focusKey == 'dsc') {
    return switch (mode) {
      'friction' =>
        'Karsi tarafin tavriyla senin sinirin ayni yere gelmeyebilir; biri yaklasirken digeri frene basabilir.',
      _ =>
        'Araniz yumusayabilir, birbirinize yaklasmaniz kolaylasabilir ya da karsi tarafi daha acik okuyabilirsin.',
    };
  }
  if (focusKey == 'mercury') {
    return switch (mode) {
      'polarity' =>
        'Bir yandan konusmak istersin, bir yandan da yanlis anlasilmamak icin kendini tutarsin.',
      'friction' =>
        'Hissettigin sey baska, bunu soyleme bicimin baska bir yerden gelebilir.',
      _ =>
        'Bir mesaj, bir konusma ya da soylenen bir sey sende beklediginden daha fazla etki birakabilir.',
    };
  }
  if (focusKey == 'moon') {
    return 'Bir konusma ya da karsilasma daha guvenli hissettirebilir; kimin yaninda gevsedigini daha net anlarsin.';
  }
  if (focusKey == 'mars') {
    return 'Yaklasmak istersin ama kendi alanini da kaybetmek istemezsin.';
  }
  if (focusKey == 'sun') {
    return 'Iliski meselesi dogrudan kendini nasil gosterdigin sorusuna baglanabilir.';
  }
  if (_relationshipRunsThroughMind(card)) {
    return 'Bir mesaj, bir konusma ya da soylenen bir sey sende beklediginden daha fazla etki birakabilir.';
  }
  if (_relationshipIsPrivate(card)) {
    return 'Disaridan buyuk gorunmese de iceride olup biten sey gercek olabilir.';
  }
  return 'Kucuk bir temas ya da kisa bir konusma dusundugunden daha belirleyici olabilir.';
}

String _buildRelationshipInterpretiveLine(EventCardDto card) {
  if (_relationshipIsPrivate(card)) {
    return 'Bu haritada yakinlik once icte hissedilir; o yuzden her sey disaridan buyuk gorunmese de his gercek olabilir.';
  }
  return switch (_relationshipMode(card)) {
    'opening' || 'flow' =>
      'Bu yuzden kucuk bir yumusamayi hemen buyuk bir kesinlik sanmamak daha iyi.',
    'polarity' =>
      'Bu kararsizlik degil; ayni anda iki ihtiyacin calistigini gosteriyor.',
    'friction' =>
      'Buradaki surtunme kotu degil; seni daha net olmaya zorluyor.',
    'intensify' =>
      'Burada his gercek; sadece hemen duzene girmek zorunda degil.',
    _ => '',
  };
}

String _buildRelationshipBackdropLead(EventCardDto card) {
  final signature = _relationshipAstroSignature(card);
  final sourceFamily = _relationshipSourceFamily(card);
  final focusKey = _relationshipFocusKey(card);
  if (sourceFamily == 'neptune' && focusKey == 'dsc') {
    return '$signature uzun suredir iliski tarafinda sis yaratiyor.';
  }
  if (sourceFamily == 'saturn' && focusKey == 'dsc') {
    return '$signature iliskiyi ciddiyet ve dayanma gucu tarafindan siniyor.';
  }
  if (sourceFamily == 'nodes' && focusKey == 'venus') {
    return '$signature eski sevme bicimlerini tekrar one cikariyor.';
  }
  if (sourceFamily == 'chiron') {
    return '$signature yakinlik ve guven tarafinda yumusama getiriyor.';
  }
  return '$signature uzun vadeli bir donem etkisi ve ${_relationshipTimingPhrase(card)}.';
}

String _buildRelationshipBackdropConcreteLine(EventCardDto card) {
  final sourceFamily = _relationshipSourceFamily(card);
  final focusKey = _relationshipFocusKey(card);
  if (sourceFamily == 'neptune' && focusKey == 'dsc') {
    return 'Birine cekilmek kolay olabilir ama niyeti net okumak o kadar kolay olmayabilir.';
  }
  if (sourceFamily == 'saturn' && focusKey == 'dsc') {
    return 'Sicaklik varsa bile bunun emek, sureklilik ve sorumluluk tasiyip tasimadigina bakiyorsun.';
  }
  if (sourceFamily == 'nodes' && focusKey == 'venus') {
    return 'Tanidik gelen ama seni yormus iliski aliskanliklari tekrar gorunur olabilir.';
  }
  if (sourceFamily == 'chiron') {
    return 'Yakinlik, guven ve kontrol ihtiyacin ayni anda daha yumusak bir noktaya gelebilir.';
  }
  return _firstNonEmpty([
    _stripGenericCopy(card.whyItFeelsThisWayTr),
    _stripGenericCopy(card.bigPicture),
    _stripGenericCopy(card.whatItBuilds),
  ]);
}

String _buildRelationshipBackdropMeaningLine(EventCardDto card) {
  final sourceFamily = _relationshipSourceFamily(card);
  final focusKey = _relationshipFocusKey(card);
  if (sourceFamily == 'neptune' && focusKey == 'dsc') {
    return 'Bu donem sana neyin gercek, neyin hayal oldugunu ayirma dersi veriyor.';
  }
  if (sourceFamily == 'saturn' && focusKey == 'dsc') {
    return 'Bu da his yetiyor mu sorusunu daha onemli hale getiriyor.';
  }
  if (sourceFamily == 'nodes' && focusKey == 'venus') {
    return 'Amaci seni geriye cekmek degil; neyi sevgi sandigini degistirmek.';
  }
  if (sourceFamily == 'chiron') {
    return 'Bu da sert duran bir yerde iyilesme ihtimali oldugunu gosteriyor.';
  }
  return _firstNonEmpty([
    _stripGenericCopy(card.whatItBuilds),
    _stripGenericCopy(card.guidanceMicroTr),
    _stripGenericCopy(card.asks),
  ]);
}

String _buildRelationshipPeriodCoreFallback(PeriodCoreDto? periodCore) {
  final coreStory = _stripGenericCopy(periodCore?.coreStory ?? '');
  if (coreStory.isEmpty) {
    return '';
  }
  return _joinSentences([
    'Altta tek gunluk olmayan bir donem hatti da var.',
    coreStory,
  ]);
}

bool _hasHeavyRelationshipBackdrop(List<EventCardDto> backdrops) {
  for (final card in backdrops) {
    if (const <String>{
          'neptune',
          'saturn',
        }.contains(_relationshipSourceFamily(card)) &&
        _relationshipMode(card) == 'friction') {
      return true;
    }
  }
  return false;
}

bool _isHeavyRelationshipDay(
  EventCardDto primary,
  List<EventCardDto> backdrops,
) {
  final primaryHeavy =
      const <String>{
        'neptune',
        'saturn',
      }.contains(_relationshipSourceFamily(primary)) &&
      _relationshipMode(primary) == 'friction';
  return primaryHeavy ||
      (_hasHeavyRelationshipBackdrop(backdrops) &&
          !const <String>{
            'flow',
            'opening',
          }.contains(_relationshipMode(primary)));
}

bool _relationshipRunsThroughMind(EventCardDto card) {
  return _relationshipFocusKey(card) == 'mercury' ||
      _relationshipChannelLine(card).contains('cumle') ||
      (card.semanticCore['source_house_domain'] ?? '').toString() == 'mind';
}

String _relationshipAstroSignature(EventCardDto card) {
  return '${_relationshipAstroName(card.transitBody)}-${_relationshipAstroName(card.natalPoint)} ${_relationshipAspectName(card.aspect)}';
}

String _relationshipAstroName(String value) {
  final key = value.trim().toLowerCase();
  return switch (key) {
    'sun' => 'Gunes',
    'moon' => 'Ay',
    'mercury' => 'Merkur',
    'venus' => 'Venus',
    'mars' => 'Mars',
    'jupiter' => 'Jupiter',
    'saturn' => 'Saturn',
    'uranus' => 'Uranus',
    'neptune' => 'Neptun',
    'pluto' => 'Pluto',
    'north node' => 'Kuzey Ay Dugumu',
    'south node' => 'Guney Ay Dugumu',
    'descendant' || 'dsc' => 'DSC',
    'ascendant' || 'asc' => 'ASC',
    'fortune' => 'Fortune',
    'vertex' => 'Vertex',
    'lilith' => 'Lilith',
    'chiron' => 'Chiron',
    _ => value.trim().isEmpty ? 'Tema' : value.trim(),
  };
}

String _relationshipAspectName(String value) {
  return switch (value.trim().toLowerCase()) {
    'trine' => 'ucgeni',
    'sextile' => 'sekstili',
    'square' => 'karesi',
    'opposition' => 'karsitligi',
    'conjunction' => 'kavusumu',
    _ => 'acisi',
  };
}

String _relationshipSpanLabel(EventCardDto card) {
  return switch (card.bucket.trim().toLowerCase()) {
    'short' => 'kisa vadeli',
    'long' => 'uzun vadeli',
    _ => 'orta vadeli',
  };
}

String _relationshipTimingPhrase(EventCardDto card) {
  return switch (card.phase.trim().toLowerCase()) {
    'exact' || 'exactish' => 'bugun en guclu yerinde',
    'applying' => 'simdi yukseliyor',
    'separating' => 'etkisi hala suruyor',
    _ => 'bu aralar belirgin',
  };
}

String _stripGenericCopy(String value) {
  final clean = normalizeTurkishText(value);
  if (clean.isEmpty) {
    return '';
  }
  return clean
      .replaceFirst(RegExp(r'^Bunu en çok\s+', caseSensitive: false), '')
      .replaceFirst(RegExp(r'^Bu tema\s+', caseSensitive: false), '')
      .replaceFirst(RegExp(r'^Bu etki\s+', caseSensitive: false), '')
      .replaceFirst(RegExp(r'^Bu süreç\s+', caseSensitive: false), '')
      .replaceFirst(RegExp(r'^Bu dönem\s+', caseSensitive: false), '');
}

class _RelationshipMiniTimelineNode extends StatelessWidget {
  const _RelationshipMiniTimelineNode({
    required this.label,
    required this.active,
    required this.emphasized,
  });

  final String label;
  final bool active;
  final bool emphasized;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final nodeColor = emphasized
        ? colors.neonPink
        : active
        ? colors.text
        : colors.textLight;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: emphasized ? 9 : 7,
          height: emphasized ? 9 : 7,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: nodeColor.withValues(alpha: emphasized ? 0.92 : 0.78),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: profile.typography.meta.copyWith(
            color: nodeColor,
            fontWeight: emphasized ? FontWeight.w700 : FontWeight.w500,
          ),
        ),
      ],
    );
  }
}

class _RelationshipWhyItMattersDisclosure extends StatefulWidget {
  const _RelationshipWhyItMattersDisclosure({required this.lines});

  final List<String> lines;

  @override
  State<_RelationshipWhyItMattersDisclosure> createState() =>
      _RelationshipWhyItMattersDisclosureState();
}

class _RelationshipWhyItMattersDisclosureState
    extends State<_RelationshipWhyItMattersDisclosure> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        JoviaPressable(
          onTap: () => setState(() => _expanded = !_expanded),
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    context.l10n.relationshipPreviewWhyImportant,
                    style: profile.typography.cardTitle.copyWith(
                      fontSize: 17,
                      color: colors.text,
                    ),
                  ),
                ),
                Icon(
                  _expanded ? Icons.remove : Icons.add,
                  size: 18,
                  color: colors.textLight,
                ),
              ],
            ),
          ),
        ),
        AnimatedCrossFade(
          duration: const Duration(milliseconds: 180),
          crossFadeState: _expanded
              ? CrossFadeState.showSecond
              : CrossFadeState.showFirst,
          firstChild: const SizedBox.shrink(),
          secondChild: Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (final line in widget.lines.take(4)) ...[
                  Text(
                    line,
                    style: profile.typography.bodyCompact.copyWith(
                      color: colors.textLight,
                      height: 1.5,
                    ),
                  ),
                  if (line != widget.lines.take(4).last)
                    const SizedBox(height: 10),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }
}

String _firstNonEmpty(Iterable<String?> values) {
  for (final value in values) {
    final clean = normalizeTurkishText(value ?? '');
    if (clean.isNotEmpty) {
      return clean;
    }
  }
  return '';
}

String _relationshipFocus(EventCardDto card) {
  return switch (_relationshipFocusKey(card)) {
    'venus' => 'Yakinlik ve cekim',
    'moon' => 'Duygusal guven',
    'mars' => 'Arzu ve sinir',
    'mercury' => 'Sozun ve niyetin',
    'sun' => 'Kalbinin gorunur tarafi',
    'dsc' => 'Karsilikli denge',
    'asc' => 'Iliskideki durusun',
    _ => 'Iliski alani',
  };
}

String _relationshipFocusKey(EventCardDto card) {
  final key = card.natalPoint.trim().toLowerCase();
  if (key == 'descendant') {
    return 'dsc';
  }
  if (key == 'ascendant') {
    return 'asc';
  }
  return key;
}

String _relationshipMode(EventCardDto card) {
  final semantic = (card.semanticCore['aspect_mode'] ?? '')
      .toString()
      .trim()
      .toLowerCase();
  if (semantic.isNotEmpty) {
    return semantic;
  }
  return switch (card.aspect.trim().toLowerCase()) {
    'opposition' => 'polarity',
    'square' => 'friction',
    'conjunction' => 'intensify',
    'sextile' => 'opening',
    'trine' => 'flow',
    _ => 'flow',
  };
}

bool _relationshipIsPrivate(EventCardDto card) {
  final haystack = _normalizeCopy(
    [
      card.houseTouchpointTr,
      card.houseTouchpointHintTr,
      (card.semanticCore['target_house_domain'] ?? '').toString(),
      (card.semanticCore['source_house_domain'] ?? '').toString(),
    ].join(' '),
  );
  return haystack.contains('inner') ||
      RegExp(r'\bic\b').hasMatch(haystack) ||
      haystack.contains('icte') ||
      haystack.contains('ice') ||
      haystack.contains('geri plan') ||
      haystack.contains('arka plan') ||
      haystack.contains('12');
}

String _relationshipChannelLine(EventCardDto card) {
  final haystack = _normalizeCopy(
    [
      card.whyItFeelsThisWayTr,
      card.houseTouchpointHintTr,
      (card.semanticCore['source_house_domain'] ?? '').toString(),
      card.transitBody,
      card.natalPoint,
    ].join(' '),
  );
  if (haystack.contains('mind') ||
      haystack.contains('konus') ||
      haystack.contains('mesaj') ||
      haystack.contains('yazi') ||
      haystack.contains('mercury')) {
    return 'Bunu en erken soyledigin, sustugun ya da yarida biraktigin cumlelerde fark edebilirsin.';
  }
  if (haystack.contains('relationship') ||
      haystack.contains('partner') ||
      haystack.contains('dsc')) {
    return 'En cok karsi tarafla kurdugun denge, beklenti ve tempo icinde gorunur olur.';
  }
  return '';
}

String _joinSentences(List<String> parts) {
  return parts
      .map(normalizeTurkishText)
      .where((item) => item.isNotEmpty)
      .join(' ');
}

String _softenRawLine(String value) {
  final clean = normalizeTurkishText(value);
  if (clean.isEmpty) {
    return '';
  }
  if (clean.endsWith('.') || clean.endsWith('!') || clean.endsWith('?')) {
    return clean;
  }
  final lower = clean.toLowerCase();
  if (lower.startsWith('bu süreç') ||
      lower.startsWith('bu dönem') ||
      lower.startsWith('bu etki')) {
    return clean;
  }
  return '$clean.';
}

String _normalizeCopy(String value) {
  return normalizeTurkishText(value)
      .toLowerCase()
      .replaceAll('ç', 'c')
      .replaceAll('ğ', 'g')
      .replaceAll('ı', 'i')
      .replaceAll('ö', 'o')
      .replaceAll('ş', 's')
      .replaceAll('ü', 'u')
      .replaceAll(RegExp(r'[^\w\s]', unicode: true), ' ')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();
}

String _formatDateLabel(DateTime value) {
  return DateFormat('d MMMM y', currentL10n().localeName).format(value);
}
