// ignore_for_file: unused_element, unused_field, prefer_final_fields

import 'dart:async';
import 'dart:convert';

import 'package:flutter/cupertino.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/performance/load_tuning.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/tabs/calendar_hub_page.dart';
import 'package:mobile/app/tabs/period_detail_navigation.dart';
import 'package:mobile/app/tabs/period_detail_page.dart';
import 'package:mobile/app/tabs/sky_event_detail_page.dart';
import 'package:mobile/app/tabs/sky_event_feed_page.dart';
import 'package:mobile/app/telemetry/perf_telemetry.dart';
import 'package:mobile/app/widgets/forum_cta.dart';
import 'package:mobile/app/widgets/forum_social_preview_strip.dart';
import 'package:mobile/app/preferences/jovia_app_preferences_provider.dart';
import 'package:mobile/app/timing/daily_transit_selection.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/timing/source_guards.dart';
import 'package:mobile/app/timing/stack_clause_gate.dart';
import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/app/timing/transit_repositories.dart';
import 'package:mobile/design/astro/astro_theme_extension.dart';
import 'package:mobile/design/astro/astro_theme_generator.dart';
import 'package:mobile/design/astro/element_scores.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_app_menu_scope.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/l10n/app_localizations.dart';
import 'package:mobile/l10n/l10n.dart';

String _firstHomeTextValue(Iterable<String?> values) {
  for (final value in values) {
    final trimmed = value?.trim() ?? '';
    if (trimmed.isNotEmpty) {
      return trimmed;
    }
  }
  return '';
}

EventCardDto _promoteHomePeriodEventToDaily(
  EventCardDto card, {
  required AppLocalizations l10n,
}) {
  final feltLine = _firstHomeTextValue([
    card.feltLineTr,
    card.headline,
    card.title,
    card.signatureTr,
  ]);
  final whyLine = _firstHomeTextValue([
    card.whyItFeelsThisWayTr,
    card.opening,
    card.essence,
    card.whyNow,
  ]);
  final guidanceLine = _firstHomeTextValue([
    card.guidanceMicroTr,
    if (card.guidance.isNotEmpty) card.guidance.first,
    card.whatItBuilds,
    card.asks,
  ]);
  final signalLabel = _firstHomeTextValue([
    card.signalLabelTr,
    card.timeHintTr,
    card.signatureTr,
    l10n.homeSignalFallback,
  ]);
  return card.copyWith(
    horizon: 'daily',
    feltLineTr: feltLine,
    whyItFeelsThisWayTr: whyLine,
    guidanceMicroTr: guidanceLine,
    signalLabelTr: signalLabel,
  );
}

PeriodCardDto _buildHomePeriodCoreFallbackCard(
  PeriodCoreDto periodCore, {
  required AppLocalizations l10n,
}) {
  return PeriodCardDto(
    id: 'home-period-core',
    title: periodCore.title.trim().isNotEmpty
        ? periodCore.title.trim()
        : l10n.homeActivePeriodTitle,
    subtitle: periodCore.coreStory.trim().isNotEmpty
        ? periodCore.coreStory.trim()
        : (periodCore.bigPicture.trim().isNotEmpty
              ? periodCore.bigPicture.trim()
              : l10n.homeActivePeriodBody),
    timeHint: periodCore.upperMeaning.trim(),
  );
}

class HomeTransitSnapshot {
  const HomeTransitSnapshot({
    required this.periodCore,
    required this.periodCards,
    required this.dailyCards,
    required this.calendarDays,
    required this.todayDayMeta,
  });

  final PeriodCoreDto? periodCore;
  final List<PeriodCardDto> periodCards;
  final List<EventCardDto> dailyCards;
  final Map<String, NarrativeCalendarDay> calendarDays;
  final NarrativeCalendarDay? todayDayMeta;
}

enum HomeDailyRenderState { loading, ready, degraded, empty }

class _HomeFastHighlight {
  const _HomeFastHighlight({
    required this.id,
    required this.kind,
    required this.title,
    required this.summary,
  });

  final String id;
  final String kind;
  final String title;
  final String summary;

  factory _HomeFastHighlight.fromMap(
    Map<String, dynamic> map, {
    required int index,
  }) {
    return _HomeFastHighlight(
      id: (map['id'] ?? 'home-fast-$index').toString().trim(),
      kind: (map['kind'] ?? '').toString().trim(),
      title: (map['title'] ?? '').toString().trim(),
      summary: (map['summary'] ?? '').toString().trim(),
    );
  }
}

class _HomeFastPayload {
  const _HomeFastPayload({
    required this.headline,
    required this.summary,
    required this.energyBadge,
    required this.energyFocus,
    required this.energySummary,
    required this.highlights,
    required this.sectionStates,
    required this.cacheStatus,
  });

  final String headline;
  final String summary;
  final String energyBadge;
  final String energyFocus;
  final String energySummary;
  final List<_HomeFastHighlight> highlights;
  final Map<String, String> sectionStates;
  final String cacheStatus;

  bool get hasContent =>
      headline.isNotEmpty ||
      summary.isNotEmpty ||
      energyFocus.isNotEmpty ||
      energySummary.isNotEmpty ||
      highlights.isNotEmpty;

  String get transitSummaryState =>
      (sectionStates['transit_summary'] ?? '').trim().toLowerCase();

  bool get isTransitDeferred => transitSummaryState == 'deferred';

  bool get canUseTransitPreview => transitSummaryState != 'deferred';

  List<_HomeFastHighlight> get transitHighlights => [
    for (final item in highlights)
      if (item.kind.trim().toLowerCase() == 'transit' &&
          (item.title.isNotEmpty || item.summary.isNotEmpty))
        item,
  ];

  bool get hasTransitHighlights => transitHighlights.isNotEmpty;

  factory _HomeFastPayload.fromMap(Map<String, dynamic> map) {
    final energy = map['energy'] is Map
        ? Map<String, dynamic>.from(map['energy'] as Map)
        : const <String, dynamic>{};
    final highlightsRaw = map['highlights'];
    final sectionStatesRaw = map['section_states'];
    return _HomeFastPayload(
      headline: (map['headline'] ?? '').toString().trim(),
      summary: (map['summary'] ?? '').toString().trim(),
      energyBadge: (energy['badge'] ?? '').toString().trim(),
      energyFocus: (energy['focus'] ?? '').toString().trim(),
      energySummary: (energy['summary'] ?? '').toString().trim(),
      highlights: highlightsRaw is List
          ? [
              for (var index = 0; index < highlightsRaw.length; index++)
                if (highlightsRaw[index] is Map)
                  _HomeFastHighlight.fromMap(
                    Map<String, dynamic>.from(highlightsRaw[index] as Map),
                    index: index,
                  ),
            ]
          : const <_HomeFastHighlight>[],
      sectionStates: sectionStatesRaw is Map
          ? <String, String>{
              for (final entry in sectionStatesRaw.entries)
                entry.key.toString(): (entry.value ?? '').toString().trim(),
            }
          : const <String, String>{},
      cacheStatus: (map['cache_status'] ?? '').toString().trim(),
    );
  }
}

EventCardDto? buildHomeFastFallbackDailyCardFromPayloadMap(
  Map<String, dynamic> map, {
  required AppLocalizations l10n,
}) {
  return _buildHomeFastFallbackDailyCard(
    _HomeFastPayload.fromMap(map),
    l10n: l10n,
  );
}

PeriodCoreDto? buildHomeFastPeriodCoreFromPayloadMap(
  Map<String, dynamic> map, {
  required AppLocalizations l10n,
}) {
  return _buildHomeFastPeriodCore(_HomeFastPayload.fromMap(map), l10n: l10n);
}

List<PeriodCardDto> buildHomeFastPeriodCardsFromPayloadMap(
  Map<String, dynamic> map, {
  required AppLocalizations l10n,
}) {
  return _buildHomeFastPeriodCards(_HomeFastPayload.fromMap(map), l10n: l10n);
}

EventCardDto? _buildHomeFastFallbackDailyCard(
  _HomeFastPayload payload, {
  required AppLocalizations l10n,
}) {
  if (!payload.canUseTransitPreview) {
    return null;
  }
  final transitHighlight = payload.transitHighlights.firstWhere(
    (item) => item.title.isNotEmpty || item.summary.isNotEmpty,
    orElse: () =>
        const _HomeFastHighlight(id: '', kind: '', title: '', summary: ''),
  );
  final hasTransitHighlight =
      transitHighlight.title.isNotEmpty || transitHighlight.summary.isNotEmpty;
  if (!hasTransitHighlight) {
    return null;
  }
  final title = _firstHomeTextValue([
    transitHighlight.title,
    l10n.homeDailyTransitLabel,
  ]);
  final body = _firstHomeTextValue([transitHighlight.summary]);
  final prompt = l10n.homeHeroPrompt;
  if (title.isEmpty && body.isEmpty) {
    return null;
  }
  return EventCardDto.fromMap({
    'event_id': transitHighlight.id.isNotEmpty
        ? transitHighlight.id
        : 'home-fast-daily-fallback',
    'headline': title,
    'opening': body,
    'essence': body,
    'felt_line_tr': title,
    'why_it_feels_this_way_tr': body,
    'signal_label_tr': prompt,
    'tone_label_tr': payload.energyFocus,
    'what_it_builds': prompt,
    'horizon': 'daily',
    'source_horizon': transitHighlight.kind.trim().toLowerCase() == 'transit'
        ? 'daily'
        : 'period',
    'today_facing_fallback': false,
    'tags': {'phase': 'preview', 'duration': 'day', 'domain': 'general'},
  });
}

PeriodCoreDto? _buildHomeFastPeriodCore(
  _HomeFastPayload payload, {
  required AppLocalizations l10n,
}) {
  if (!payload.canUseTransitPreview) {
    return null;
  }
  final title = _firstHomeTextValue([payload.energyFocus, payload.headline]);
  final coreStory = _firstHomeTextValue([
    payload.summary,
    payload.energySummary,
  ]);
  final upperMeaning = payload.energyBadge;
  final bigPicture = _firstHomeTextValue([
    payload.energySummary,
    payload.summary,
  ]);
  if (title.isEmpty && coreStory.isEmpty && bigPicture.isEmpty) {
    return null;
  }
  return PeriodCoreDto(
    title: title.isNotEmpty ? title : l10n.homeActivePeriodTitle,
    coreStory: coreStory,
    upperMeaning: upperMeaning,
    bigPicture: bigPicture,
    mechanism: '',
    tags: const <PeriodCoreTagDto>[],
  );
}

List<PeriodCardDto> _buildHomeFastPeriodCards(
  _HomeFastPayload payload, {
  required AppLocalizations l10n,
}) {
  if (!payload.canUseTransitPreview) {
    return const <PeriodCardDto>[];
  }
  final transitHighlights = payload.transitHighlights;
  final cards = <PeriodCardDto>[
    for (var index = 0; index < transitHighlights.length; index++)
      if (transitHighlights[index].title.isNotEmpty ||
          transitHighlights[index].summary.isNotEmpty)
        PeriodCardDto(
          id: transitHighlights[index].id.isNotEmpty
              ? transitHighlights[index].id
              : 'home-fast-card-$index',
          title: transitHighlights[index].title.isNotEmpty
              ? transitHighlights[index].title
              : l10n.homeActivePeriodTitle,
          subtitle: transitHighlights[index].summary,
          timeHint: transitHighlights[index].kind,
        ),
  ];
  if (cards.isNotEmpty) {
    return cards;
  }
  final fallbackTitle = _firstHomeTextValue([
    payload.energyFocus,
    payload.headline,
  ]);
  final fallbackSubtitle = _firstHomeTextValue([
    payload.summary,
    payload.energySummary,
  ]);
  if (fallbackTitle.isEmpty && fallbackSubtitle.isEmpty) {
    return const <PeriodCardDto>[];
  }
  return <PeriodCardDto>[
    PeriodCardDto(
      id: 'home-fast-fallback',
      title: fallbackTitle.isNotEmpty
          ? fallbackTitle
          : l10n.homeActivePeriodTitle,
      subtitle: fallbackSubtitle,
      timeHint: payload.energyBadge,
    ),
  ];
}

HomeTransitSnapshot buildHomeTransitSnapshot({
  required NarrativeResponse narrative,
  required DateTime today,
  required AppLocalizations l10n,
}) {
  final todayKey = TransitRequestBuilder.fmtDate(
    TransitRequestBuilder.stripDate(today),
  );
  final selection = selectDailyTransitCardsForDate(
    narrative: narrative,
    selectedDate: today,
  );
  final periodEvents = selection.periodCards;
  final periodCards = <PeriodCardDto>[
    for (var i = 0; i < periodEvents.length; i++)
      PeriodCardDto.fromEventCard(eventCard: periodEvents[i], index: i),
  ];
  final periodCore = narrative.periodCore;
  if (periodCards.isEmpty && periodCore != null) {
    periodCards.add(_buildHomePeriodCoreFallbackCard(periodCore, l10n: l10n));
  }
  return HomeTransitSnapshot(
    periodCore: narrative.periodCore,
    periodCards: periodCards,
    dailyCards: selection.dailyCards,
    calendarDays: narrative.calendarDays,
    todayDayMeta: narrative.calendarDays[todayKey],
  );
}

String describeHomeDailyCardSource(EventCardDto? card) {
  if (card == null) {
    return 'none';
  }
  if (card.eventId.trim() == 'home-fast-daily-fallback') {
    return 'home_fast_fallback';
  }
  if (isDailyTransitCardBackedByPeriod(card)) {
    return 'period_derived';
  }
  if (card.eventId.trim().isNotEmpty) {
    return 'daily_event_card';
  }
  return 'daily_unknown';
}

String resolveHomeDailySourceType({
  required EventCardDto? card,
  required NarrativeCalendarDay? dayMeta,
}) {
  if (hasAuthoritativeHomeDailyCard(card)) {
    return 'authoritative_daily';
  }
  if (card != null && card.eventId.trim() == 'home-fast-daily-fallback') {
    return 'fast_preview';
  }
  if (card != null && isDailyTransitCardBackedByPeriod(card)) {
    return 'period_derived';
  }
  if ((dayMeta?.microSummaryTr.trim().isNotEmpty ?? false)) {
    return 'meta_only';
  }
  if (card != null) {
    return 'non_authoritative_daily';
  }
  return 'none';
}

String resolveHomeDailyResponseAnchorDay(
  Map<String, dynamic> payload, {
  required String fallbackDayKey,
}) {
  final direct = _firstHomeTextValue([
    payload['selected_date']?.toString(),
    payload['anchor_date']?.toString(),
  ]);
  if (direct.isNotEmpty) {
    return direct;
  }
  final publicRaw = payload['public'] is Map
      ? Map<String, dynamic>.from(payload['public'] as Map)
      : const <String, dynamic>{};
  final fromPublic = _firstHomeTextValue([
    publicRaw['selected_date']?.toString(),
    publicRaw['anchor_date']?.toString(),
  ]);
  if (fromPublic.isNotEmpty) {
    return fromPublic;
  }
  final debugRaw = payload['debug'] is Map
      ? Map<String, dynamic>.from(payload['debug'] as Map)
      : const <String, dynamic>{};
  final selectedDayPublic = debugRaw['selected_day_public'] is Map
      ? Map<String, dynamic>.from(debugRaw['selected_day_public'] as Map)
      : const <String, dynamic>{};
  final fromDebug = _firstHomeTextValue([
    selectedDayPublic['date']?.toString(),
  ]);
  if (fromDebug.isNotEmpty) {
    return fromDebug;
  }
  return fallbackDayKey;
}

bool _sameHomeDailyCard(EventCardDto? left, EventCardDto? right) {
  if (left == null || right == null) {
    return left == right;
  }
  return left.eventId.trim() == right.eventId.trim() &&
      left.feltLineTr.trim() == right.feltLineTr.trim() &&
      left.opening.trim() == right.opening.trim() &&
      left.whyItFeelsThisWayTr.trim() == right.whyItFeelsThisWayTr.trim() &&
      left.guidanceMicroTr.trim() == right.guidanceMicroTr.trim();
}

bool hasUsableHomeDailyCardCopy(EventCardDto? card) {
  if (card == null) {
    return false;
  }
  return _firstHomeTextValue([
    card.opening,
    card.whyItFeelsThisWayTr,
    card.guidanceMicroTr,
    card.essence,
  ]).isNotEmpty;
}

bool hasAuthoritativeHomeDailyCard(EventCardDto? card) {
  if (card == null) {
    return false;
  }
  if (!hasUsableHomeDailyCardCopy(card)) {
    return false;
  }
  if (card.eventId.trim() == 'home-fast-daily-fallback') {
    return false;
  }
  return !isDailyTransitCardBackedByPeriod(card);
}

bool hasAuthoritativeHomeDailyContent({
  required List<EventCardDto> dailyCards,
}) {
  for (final card in dailyCards) {
    if (hasAuthoritativeHomeDailyCard(card)) {
      return true;
    }
  }
  return false;
}

int scoreHomeDailyCardStrength(EventCardDto? card) {
  if (card == null) {
    return 0;
  }
  var score = 0;
  if (card.feltLineTr.trim().isNotEmpty || card.headline.trim().isNotEmpty) {
    score += 3;
  }
  if (card.opening.trim().isNotEmpty) {
    score += 6;
  }
  if (card.whyItFeelsThisWayTr.trim().isNotEmpty) {
    score += 5;
  }
  if (card.guidanceMicroTr.trim().isNotEmpty) {
    score += 4;
  }
  if (card.houseTouchpointHintTr.trim().isNotEmpty) {
    score += 2;
  }
  if (card.essence.trim().isNotEmpty) {
    score += 2;
  }

  final horizon = card.horizon.trim().toLowerCase();
  final sourceHorizon = card.sourceHorizon.trim().toLowerCase();
  if (horizon == 'daily') {
    score += 2;
  }
  if (sourceHorizon == 'daily') {
    score += 2;
  }
  if (!isDailyTransitCardBackedByPeriod(card)) {
    score += 5;
  } else {
    score -= 4;
  }
  if (card.eventId.trim().isNotEmpty &&
      card.eventId.trim() != 'home-fast-daily-fallback') {
    score += 1;
  }
  return score;
}

List<EventCardDto> _mergeHomeDailyCards({
  required List<EventCardDto> incoming,
  required List<EventCardDto> current,
}) {
  if (incoming.isEmpty) {
    return current;
  }
  if (current.isEmpty) {
    return incoming;
  }
  final incomingScore = scoreHomeDailyCardStrength(incoming.first);
  final currentScore = scoreHomeDailyCardStrength(current.first);
  if (incomingScore > currentScore) {
    return incoming;
  }
  return current;
}

String _homeDailyResolutionReason({
  required List<EventCardDto> dailyCards,
  required NarrativeCalendarDay? dayMeta,
}) {
  if (hasAuthoritativeHomeDailyContent(dailyCards: dailyCards)) {
    return 'authoritative_daily_card';
  }
  final firstCard = dailyCards.isNotEmpty ? dailyCards.first : null;
  if (firstCard != null &&
      firstCard.eventId.trim() == 'home-fast-daily-fallback') {
    return 'fast_preview_only';
  }
  if (firstCard != null && isDailyTransitCardBackedByPeriod(firstCard)) {
    return 'period_derived_only';
  }
  if (hasHomeMetaOnlyContent(dailyCards: dailyCards, dayMeta: dayMeta)) {
    return 'meta_only';
  }
  return 'empty';
}

String homeDailyDegradedReason({
  required bool loading,
  required List<EventCardDto> dailyCards,
  required NarrativeCalendarDay? dayMeta,
  required String? errorMessage,
}) {
  if (hasAuthoritativeHomeDailyContent(dailyCards: dailyCards)) {
    return 'none';
  }
  if (loading) {
    return 'loading';
  }
  final firstCard = dailyCards.isNotEmpty ? dailyCards.first : null;
  if (firstCard != null &&
      firstCard.eventId.trim() == 'home-fast-daily-fallback') {
    return 'fast_preview_only';
  }
  if (firstCard != null && isDailyTransitCardBackedByPeriod(firstCard)) {
    return 'period_derived_only';
  }
  if (hasHomeMetaOnlyContent(dailyCards: dailyCards, dayMeta: dayMeta)) {
    return 'meta_only';
  }
  if ((errorMessage ?? '').trim().isNotEmpty) {
    return 'request_error';
  }
  if (dailyCards.isNotEmpty) {
    return 'non_authoritative_card';
  }
  return 'empty';
}

HomeDailyRenderState resolveHomeDailyRenderState({
  required bool loading,
  required List<EventCardDto> dailyCards,
  required NarrativeCalendarDay? dayMeta,
  required String? errorMessage,
}) {
  if (hasAuthoritativeHomeDailyContent(dailyCards: dailyCards)) {
    return HomeDailyRenderState.ready;
  }
  if (loading) {
    return HomeDailyRenderState.loading;
  }
  final reason = homeDailyDegradedReason(
    loading: loading,
    dailyCards: dailyCards,
    dayMeta: dayMeta,
    errorMessage: errorMessage,
  );
  if (reason == 'empty') {
    return HomeDailyRenderState.empty;
  }
  return HomeDailyRenderState.degraded;
}

String homeDailyRenderStateToken(HomeDailyRenderState state) {
  return switch (state) {
    HomeDailyRenderState.loading => 'loading',
    HomeDailyRenderState.ready => 'ready',
    HomeDailyRenderState.degraded => 'degraded',
    HomeDailyRenderState.empty => 'empty',
  };
}

String homeDailyRenderStateCopy(
  HomeDailyRenderState state, {
  required AppLocalizations l10n,
  required String degradedReason,
}) {
  return switch (state) {
    HomeDailyRenderState.loading => l10n.homeStoryLoading,
    HomeDailyRenderState.ready => '',
    HomeDailyRenderState.degraded =>
      degradedReason == 'meta_only'
          ? l10n.homePeriodCardsPending
          : l10n.homeStoryUnavailable,
    HomeDailyRenderState.empty => l10n.homePeriodCardsPending,
  };
}

class HomeDayContext {
  const HomeDayContext({
    required this.timezone,
    required this.nowProfileTimezone,
    required this.today,
    required this.dayKey,
    required this.source,
  });

  final String timezone;
  final DateTime nowProfileTimezone;
  final DateTime today;
  final String dayKey;
  final String source;
}

Duration? _parseTimezoneOffset(String rawTimezone, {Duration? fallbackOffset}) {
  final normalized = rawTimezone.trim();
  if (normalized.isEmpty) {
    return fallbackOffset;
  }
  final lower = normalized.toLowerCase();
  if (lower == 'utc' || lower == 'gmt' || lower == 'z') {
    return Duration.zero;
  }
  if (lower == 'europe/istanbul' || lower == 'turkey') {
    return const Duration(hours: 3);
  }
  final compact = normalized.replaceAll(' ', '');
  final patterns = <RegExp>[
    RegExp(r'^(?:utc|gmt)([+-])(\d{1,2})(?::?(\d{2}))?$', caseSensitive: false),
    RegExp(r'^([+-])(\d{1,2})(?::?(\d{2}))?$'),
  ];
  for (final pattern in patterns) {
    final match = pattern.firstMatch(compact);
    if (match == null) {
      continue;
    }
    final sign = match.group(1) == '-' ? -1 : 1;
    final hours = int.tryParse(match.group(2) ?? '') ?? 0;
    final minutes = int.tryParse(match.group(3) ?? '') ?? 0;
    return Duration(hours: hours * sign, minutes: minutes * sign);
  }
  return fallbackOffset;
}

HomeDayContext buildHomeDayContext(
  Map<String, dynamic>? profile, {
  DateTime? utcNow,
  DateTime? localNow,
}) {
  final nowLocal = localNow ?? DateTime.now();
  final resolvedProfile = profile ?? const <String, dynamic>{};
  final timezone = TransitRequestBuilder.resolveTimezone(resolvedProfile);
  final localTimezoneName = nowLocal.timeZoneName.trim().toLowerCase();
  final fallbackOffset =
      localTimezoneName.isNotEmpty &&
          timezone.trim().toLowerCase() == localTimezoneName
      ? nowLocal.timeZoneOffset
      : null;
  final parsedOffset = _parseTimezoneOffset(
    timezone,
    fallbackOffset: fallbackOffset,
  );
  final nowInProfileTimezone = parsedOffset == null
      ? nowLocal
      : (utcNow ?? nowLocal.toUtc()).add(parsedOffset);
  final normalizedToday = TransitRequestBuilder.stripDate(nowInProfileTimezone);
  return HomeDayContext(
    timezone: timezone,
    nowProfileTimezone: nowInProfileTimezone,
    today: normalizedToday,
    dayKey: TransitRequestBuilder.fmtDate(normalizedToday),
    source: parsedOffset == null ? 'local_fallback' : 'profile_timezone',
  );
}

bool hasStrongHomeDailyContent({required List<EventCardDto> dailyCards}) {
  return hasAuthoritativeHomeDailyContent(dailyCards: dailyCards);
}

bool hasHomeMetaOnlyContent({
  required List<EventCardDto> dailyCards,
  required NarrativeCalendarDay? dayMeta,
}) {
  final microSummary = dayMeta?.microSummaryTr.trim() ?? '';
  return microSummary.isNotEmpty &&
      !hasStrongHomeDailyContent(dailyCards: dailyCards);
}

bool hasUsableHomeDailyContent({
  required List<EventCardDto> dailyCards,
  required NarrativeCalendarDay? dayMeta,
}) {
  return hasStrongHomeDailyContent(dailyCards: dailyCards) ||
      hasHomeMetaOnlyContent(dailyCards: dailyCards, dayMeta: dayMeta);
}

String homeCalendarDayFallbackReasonCode({
  required int rawDailyEventCardsCount,
  required List<EventCardDto> dailyCards,
  required NarrativeCalendarDay? dayMeta,
}) {
  if (rawDailyEventCardsCount == 0) {
    return 'daily_event_cards_empty';
  }
  if (hasHomeMetaOnlyContent(dailyCards: dailyCards, dayMeta: dayMeta)) {
    return 'meta_only_content';
  }
  if (!hasStrongHomeDailyContent(dailyCards: dailyCards)) {
    return 'no_strong_daily_card';
  }
  return 'none';
}

bool shouldRunHomeCalendarDayFallback({
  required int rawDailyEventCardsCount,
  required List<EventCardDto> dailyCards,
  required NarrativeCalendarDay? dayMeta,
}) {
  if (rawDailyEventCardsCount == 0) {
    return true;
  }
  return !hasAuthoritativeHomeDailyContent(dailyCards: dailyCards);
}

HomeTransitSnapshot mergeHomeTransitSnapshot({
  required HomeTransitSnapshot incoming,
  PeriodCoreDto? currentPeriodCore,
  List<PeriodCardDto> currentPeriodCards = const <PeriodCardDto>[],
  List<EventCardDto> currentDailyCards = const <EventCardDto>[],
  Map<String, NarrativeCalendarDay> currentCalendarDays =
      const <String, NarrativeCalendarDay>{},
  NarrativeCalendarDay? currentTodayDayMeta,
}) {
  return HomeTransitSnapshot(
    periodCore: incoming.periodCore ?? currentPeriodCore,
    periodCards: incoming.periodCards.isNotEmpty
        ? incoming.periodCards
        : currentPeriodCards,
    dailyCards: _mergeHomeDailyCards(
      incoming: incoming.dailyCards,
      current: currentDailyCards,
    ),
    calendarDays: incoming.calendarDays.isNotEmpty
        ? incoming.calendarDays
        : currentCalendarDays,
    todayDayMeta: incoming.todayDayMeta ?? currentTodayDayMeta,
  );
}

String buildHomeDefaultHeroBody({
  EventCardDto? todayDailyCard,
  PeriodCardDto? activeCard,
  PeriodCoreDto? periodCore,
  required String natalSummary,
  required bool loading,
  required AppLocalizations l10n,
}) {
  return _firstHomeTextValue([
    todayDailyCard?.opening,
    todayDailyCard?.essence,
    activeCard?.subtitle,
    periodCore?.coreStory,
    periodCore?.bigPicture,
    natalSummary,
    if (loading) l10n.homeStoryLoading,
    l10n.homeStoryUnavailable,
  ]);
}

String _humanizeHomeToneLabel(String? raw) {
  final normalized = normalizeTurkishText(raw ?? '');
  if (normalized.isEmpty) {
    return '';
  }
  switch (normalized.trim().toLowerCase()) {
    case 'yuksek_tempo':
      return 'Yüksek tempo';
    case 'yogun':
      return 'Yoğun';
    case 'hareketli':
      return 'Hareketli';
    case 'sakin':
      return 'Sakin';
    case 'ince':
      return 'İnce';
  }
  final spaced = normalized.replaceAll('_', ' ');
  return toBeginningOfSentenceCase(spaced) ?? spaced;
}

bool _shouldPreferHomeDayMeta(EventCardDto? card) {
  if (card == null) {
    return false;
  }
  final sourceHorizon = card.sourceHorizon.trim().toLowerCase();
  final horizon = card.horizon.trim().toLowerCase();
  return card.todayFacingFallback ||
      card.isPeriodDerived ||
      sourceHorizon == 'period' ||
      (horizon.isNotEmpty && horizon != 'daily');
}

String buildHomeDailyFallbackHeroBody({
  required EventCardDto? card,
  required NarrativeCalendarDay? dayMeta,
  required bool loading,
  required AppLocalizations l10n,
}) {
  return _firstHomeTextValue([
    dayMeta?.microSummaryTr,
    card?.opening,
    card?.whyItFeelsThisWayTr,
    card?.guidanceMicroTr,
    card?.essence,
    if (loading) l10n.homeStoryLoading,
    l10n.homeStoryUnavailable,
  ]);
}

class HomePage extends ConsumerStatefulWidget {
  const HomePage({super.key});

  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage>
    with WidgetsBindingObserver, TickerProviderStateMixin {
  static const String _baseUrl = 'http://127.0.0.1:5000';

  bool _loading = false;
  int _homeLoadVersion = 0;
  String? _error;
  bool _coreStoryExpanded = false;
  String _coreStory = '';
  String _sunSign = '—';
  String _moonSign = '—';
  String _risingSign = '—';
  List<PeriodCardDto> _periodCards = const <PeriodCardDto>[];
  List<EventCardDto> _todayDailyCards = const <EventCardDto>[];
  Map<String, NarrativeCalendarDay> _homeCalendarDays =
      const <String, NarrativeCalendarDay>{};
  List<_SkyFeedItemData> _skyFeedItems = const <_SkyFeedItemData>[];
  String _skyFeedSummary = '';
  PeriodCoreDto? _periodCore;
  NarrativeCalendarDay? _todayDayMeta;
  String? _lastKey;
  String? _lastLoadedDayKey;
  HomeDayContext? _homeDayContext;
  int _homeFastRetryAttempt = 0;
  int _selectedWeekIndex = 0;
  final NarrativeRepository _narrativeRepository = NarrativeRepository();

  late final AnimationController _heroEnterController;
  late final AnimationController _starController;
  late final AnimationController _contentEnterController;

  String _firstHomeText(Iterable<String?> values) {
    return _firstHomeTextValue(values);
  }

  HomeDayContext _resolveDayContext(Map<String, dynamic>? profile) {
    final context = buildHomeDayContext(profile);
    _homeDayContext = context;
    return context;
  }

  @override
  void initState() {
    super.initState();
    _heroEnterController = AnimationController(
      duration: const Duration(milliseconds: 350),
      vsync: this,
    )..forward();
    _starController = AnimationController(
      duration: const Duration(seconds: 8),
      vsync: this,
    )..repeat();
    _contentEnterController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    )..forward();
    WidgetsBinding.instance.addObserver(this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) {
        return;
      }
      PerfTelemetry.logPointOnce(
        'startup.first_home_visible',
        'first_home_visible',
      );
    });
  }

  void _retry() {
    setState(() {
      _lastKey = null;
      _error = null;
    });
  }

  Widget _staggerItem(int index, Widget child) {
    final start = (index * 0.08).clamp(0.0, 0.6);
    final end = (start + 0.35).clamp(0.0, 1.0);
    final animation = CurvedAnimation(
      parent: _contentEnterController,
      curve: Interval(start, end, curve: Curves.easeOutCubic),
    );
    return FadeTransition(
      opacity: animation,
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0, 0.06),
          end: Offset.zero,
        ).animate(animation),
        child: child,
      ),
    );
  }

  @override
  void dispose() {
    _heroEnterController.dispose();
    _starController.dispose();
    _contentEnterController.dispose();
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state != AppLifecycleState.resumed) {
      return;
    }
    final profile = ref.read(userProfileProvider).asData?.value;
    if (!_hasProfile(profile)) {
      return;
    }
    final dayContext = _resolveDayContext(profile);
    final todayKey = dayContext.dayKey;
    if (_lastLoadedDayKey != todayKey ||
        !hasStrongHomeDailyContent(dailyCards: _todayDailyCards)) {
      _lastKey = null;
      _maybeBootstrap(profile, Supabase.instance.client.auth.currentUser);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final profile = ref.watch(userProfileProvider).asData?.value;
    final user = Supabase.instance.client.auth.currentUser;
    final dayContext = _homeDayContext ?? buildHomeDayContext(profile);
    _maybeBootstrap(profile, user);

    final scores = _computeElementScores(
      profile: profile,
      userId: user?.id,
      email: user?.email,
      sun: _sunSign,
      moon: _moonSign,
      rising: _risingSign,
    );

    final themed = withAstroTheme(
      withProfileTheme(Theme.of(context)),
      astroTheme: astroThemeFromElementScores(scores),
    );

    return Theme(
      data: themed,
      child: Builder(
        builder: (context) {
          final profileTheme = context.profileTheme;
          final colors = profileTheme.colors;
          final skyBulletin = _skyFeedItems.isNotEmpty
              ? _buildSkyBulletinFromFeed(
                  items: _skyFeedItems,
                  summary: _skyFeedSummary,
                )
              : _buildSkyBulletin(_periodCards);
          final skyHeroItem = _skyFeedItems.isNotEmpty
              ? _skyFeedItems.first
              : null;
          final displayName = _displayName(profile, user);
          final activeCard = _periodCards.isNotEmpty
              ? _periodCards.first
              : null;
          final todayDailyCard = _todayDailyCards.isNotEmpty
              ? _todayDailyCards.first
              : null;
          final periodPreviewCards = _periodCards
              .take(3)
              .toList(growable: false);
          final weekPreviewCards = _todayDailyCards
              .take(7)
              .toList(growable: false);
          final collectiveCard = _periodCards.length > 1
              ? _periodCards[1]
              : activeCard;
          final periodBigPicture = _periodCore?.bigPicture.trim() ?? '';
          final weekItems = _buildWeekItems(
            context,
            weekPreviewCards,
            calendarDays: _homeCalendarDays,
            selectedIndex: _selectedWeekIndex,
            baseDay: dayContext.today,
          );
          final selectedWeekItem = weekItems.isEmpty
              ? null
              : weekItems[_selectedWeekIndex.clamp(0, weekItems.length - 1)];
          final selectedDailyCard = selectedWeekItem?.card;
          final isSelectedToday =
              selectedWeekItem == null || selectedWeekItem.isToday;
          final selectedDayMeta = isSelectedToday
              ? (selectedWeekItem?.dayMeta ?? _todayDayMeta)
              : selectedWeekItem.dayMeta;
          final selectedDailyCards = selectedDailyCard == null
              ? const <EventCardDto>[]
              : <EventCardDto>[selectedDailyCard];
          final selectedDailyRenderState = resolveHomeDailyRenderState(
            loading: _loading,
            dailyCards: selectedDailyCards,
            dayMeta: selectedDayMeta,
            errorMessage: _error,
          );
          final selectedDailyDegradedReason = homeDailyDegradedReason(
            loading: _loading,
            dailyCards: selectedDailyCards,
            dayMeta: selectedDayMeta,
            errorMessage: _error,
          );
          final selectedDailyStatusCopy = homeDailyRenderStateCopy(
            selectedDailyRenderState,
            l10n: l10n,
            degradedReason: selectedDailyDegradedReason,
          );
          final shouldUsePeriodHeroFallback =
              selectedDailyRenderState != HomeDailyRenderState.ready &&
              (activeCard != null || _periodCore != null);
          final todayFallbackTitle = _firstHomeText([
            todayDailyCard?.feltLineTr,
            todayDailyCard?.headline,
            selectedDayMeta?.toneLabelTr,
            l10n.homeDailyTransitLabel,
          ]);
          final todayFallbackPrompt = _firstHomeText([
            todayDailyCard?.signalLabelTr,
            todayDailyCard?.houseTouchpointHintTr,
            selectedDayMeta?.signalLabelTr,
            l10n.homeHeroPrompt,
          ]);
          final todayFallbackBody = buildHomeDailyFallbackHeroBody(
            card: todayDailyCard,
            dayMeta: selectedDayMeta,
            loading: _loading,
            l10n: l10n,
          );
          final selectedFallbackTitle = _firstHomeText([
            selectedDailyCard?.feltLineTr,
            selectedDailyCard?.headline,
            l10n.homeDailyTransitLabel,
          ]);
          final selectedFallbackPrompt = _firstHomeText([
            selectedDailyCard?.signalLabelTr,
            selectedDailyCard?.houseTouchpointHintTr,
            l10n.homeHeroPrompt,
          ]);
          final selectedFallbackBody = buildHomeDailyFallbackHeroBody(
            card: selectedDailyCard,
            dayMeta: null,
            loading: _loading,
            l10n: l10n,
          );
          final periodFallbackTitle = _resolveHomeHeroTitle(
            selectedCard: activeCard,
            fallbackTitle: l10n.homeActivePeriodTitle,
          );
          final periodFallbackPrompt = _resolveHomeHeroPrompt(
            selectedCard: activeCard,
            fallbackPrompt: l10n.homeHeroPrompt,
          );
          final periodFallbackBody = buildHomeDefaultHeroBody(
            todayDailyCard: todayDailyCard,
            activeCard: activeCard,
            periodCore: _periodCore,
            natalSummary: _coreStory,
            loading: _loading,
            l10n: l10n,
          );
          final resolvedDailyTitle = isSelectedToday
              ? _resolveHomeDailyHeroTitle(
                  card: todayDailyCard,
                  dayMeta: selectedDayMeta,
                  fallbackTitle: todayFallbackTitle,
                )
              : _resolveHomeDailyHeroTitle(
                  card: selectedDailyCard,
                  dayMeta: selectedDayMeta,
                  fallbackTitle: selectedFallbackTitle,
                );
          final resolvedDailySubtitle = isSelectedToday
              ? _resolveHomeDailyHeroPrompt(
                  card: todayDailyCard,
                  dayMeta: selectedDayMeta,
                  fallbackPrompt: todayFallbackPrompt,
                )
              : _resolveHomeDailyHeroPrompt(
                  card: selectedDailyCard,
                  dayMeta: selectedDayMeta,
                  fallbackPrompt: selectedFallbackPrompt,
                );
          final resolvedDailyBody = isSelectedToday
              ? _resolveHomeDailyHeroBody(
                  card: todayDailyCard,
                  dayMeta: selectedDayMeta,
                  fallbackBody: todayFallbackBody,
                )
              : _resolveHomeDailyHeroBody(
                  card: selectedDailyCard,
                  dayMeta: selectedDayMeta,
                  fallbackBody: selectedFallbackBody,
                );
          // PR7b hand-off wiring: attach the stack synergy clause to whichever
          // narrative line the user is about to see, gated by a rolling 7-day
          // cooldown (per-device, persisted via Supabase auth metadata). Uses
          // the active daily card's stack_clause_tr — the card the user is
          // actually looking at (today when viewing today, selected otherwise).
          // When shouldUsePeriodHeroFallback is true the daily path is skipped
          // below, so `resolvedDailyBodyWithClause` never reaches the screen
          // and markClauseShown is naturally skipped.
          final activeDailyCard = isSelectedToday
              ? todayDailyCard
              : selectedDailyCard;
          final stackClausePrefs = ref.watch(joviaAppPreferencesProvider);
          final stackClauseEnabled = ref.watch(stackClauseFeatureEnabledProvider);
          final stackClauseNowMs = DateTime.now().millisecondsSinceEpoch;
          final showStackClause = stackClauseShouldShow(
            stackClauseTr: activeDailyCard?.stackClauseTr ?? '',
            lastShownMs: stackClausePrefs.stackClauseLastShownAtMs,
            nowMs: stackClauseNowMs,
            featureEnabled: stackClauseEnabled,
          );
          final resolvedDailyBodyWithClause = stackClauseComposeLine(
            baseText: resolvedDailyBody,
            stackClauseTr: activeDailyCard?.stackClauseTr ?? '',
            showStackClause: showStackClause,
          );
          final activeTitle = shouldUsePeriodHeroFallback
              ? periodFallbackTitle
              : resolvedDailyTitle;
          final activeSubtitle = shouldUsePeriodHeroFallback
              ? _firstHomeText([selectedDailyStatusCopy, periodFallbackPrompt])
              : resolvedDailySubtitle;
          final selectedHeroBody = shouldUsePeriodHeroFallback
              ? _firstHomeTextValue([
                  selectedDailyStatusCopy,
                  periodFallbackBody,
                ])
              : resolvedDailyBodyWithClause;
          // Mark the clause as shown only when we actually commit to the
          // daily path AND the gate said yes. The period fallback branch
          // above drops the clause silently, which is the intended
          // behaviour (no "yoğun gün" cue attached to period narrative).
          if (showStackClause && !shouldUsePeriodHeroFallback) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (!mounted) return;
              ref
                  .read(joviaAppPreferencesProvider.notifier)
                  .markClauseShown(stackClauseNowMs);
            });
          }
          final showTimingPanel = _shouldShowTimingPanel(
            periodCore: _periodCore,
            heroBody: selectedHeroBody,
            activeTitle: activeTitle,
            activeSubtitle: activeSubtitle,
          );

          return DecoratedBox(
            decoration: Theme.of(context).brightness == Brightness.dark
                ? BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: <Color>[
                        const Color(0xFF09080F),
                        const Color(0xFF120F1A),
                        colors.bg,
                      ],
                      stops: const <double>[0, 0.36, 1],
                    ),
                  )
                : const BoxDecoration(color: Colors.white),
            child: JoviaPageScaffold(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(0, 10, 0, 24),
                children: [
                  _HomeReferenceHeader(
                    displayName: displayName,
                    dateLabel: _formatHomeToday(context, dayContext.today),
                    onActionTap: () =>
                        JoviaAppMenuScope.maybeOf(context)?.openMenu(),
                  ),
                  const SizedBox(height: 18),
                  FadeTransition(
                    opacity: CurvedAnimation(
                      parent: _heroEnterController,
                      curve: Curves.easeOutCubic,
                    ),
                    child: SlideTransition(
                      position:
                          Tween<Offset>(
                            begin: const Offset(0, 0.08),
                            end: Offset.zero,
                          ).animate(
                            CurvedAnimation(
                              parent: _heroEnterController,
                              curve: Curves.easeOutCubic,
                            ),
                          ),
                      child: _HomeReferenceHeroCard(
                        title: activeTitle,
                        body: selectedHeroBody,
                        prompt: activeSubtitle,
                        weekItems: weekItems,
                        starRotation: _starController,
                        onSelectDay: (item) {
                          if (item.isSelected) {
                            _openHomeDay(
                              context,
                              profile,
                              item.date,
                              initialBundle: _buildInitialHomeDayBundle(
                                date: item.date,
                                card: item.card,
                                dayMeta: item.dayMeta,
                              ),
                            );
                            return;
                          }
                          setState(() => _selectedWeekIndex = item.index);
                        },
                        onOpen: () => _openHomeDay(
                          context,
                          profile,
                          selectedWeekItem?.date ?? dayContext.today,
                          initialBundle: _buildInitialHomeDayBundle(
                            date: selectedWeekItem?.date ?? dayContext.today,
                            card: selectedWeekItem?.card,
                            dayMeta: selectedWeekItem?.dayMeta,
                          ),
                        ),
                        footer: _HomeSignStateRow(
                          sunSign: _sunSign,
                          moonSign: _moonSign,
                          risingSign: _risingSign,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 26),
                  _staggerItem(
                    0,
                    _HomeSectionLead(
                      title: context.l10n.homePlansTitle,
                      subtitle: context.l10n.homePlansSubtitle,
                    ),
                  ),
                  const SizedBox(height: 14),
                  _staggerItem(1, const ForumCTA()),
                  const SizedBox(height: 14),
                  _staggerItem(2, const SocialPreviewStrip()),
                  const SizedBox(height: 14),
                  _staggerItem(
                    3,
                    _HomeReferencePlanBoard(
                      activeCard: activeCard,
                      dailyCards: periodPreviewCards,
                      bulletin: skyBulletin,
                      skyItem: skyHeroItem,
                      lineText: periodBigPicture.isNotEmpty
                          ? periodBigPicture
                          : selectedHeroBody,
                      loading: _loading && periodPreviewCards.isEmpty,
                      onOpenActive: activeCard == null
                          ? () => _openTiming(context)
                          : () =>
                                _openTransitCard(context, profile, activeCard),
                      onOpenCard: (card) =>
                          _openTransitCard(context, profile, card),
                      onOpenSky: () {
                        if (skyHeroItem != null) {
                          _openSkyEventDetail(context, skyHeroItem);
                        } else if (collectiveCard != null) {
                          _openPeriodDetails(context, collectiveCard);
                        } else {
                          _openTiming(context);
                        }
                      },
                      onOpenCalendar: () => _openTiming(context),
                    ),
                  ),
                  if (_skyFeedItems.length > 1) ...[
                    const SizedBox(height: 18),
                    _staggerItem(
                      4,
                      _HomeSkyEventList(
                        items: _skyFeedItems.skip(1).take(2).toList(),
                        onOpenItem: (item) =>
                            _openSkyEventDetail(context, item),
                        onOpenAll: () => _openSkyFeed(context),
                      ),
                    ),
                  ],
                  if (showTimingPanel) ...[
                    const SizedBox(height: 24),
                    _staggerItem(
                      5,
                      _HomeReferenceTimingCard(
                        title: (_periodCore?.title.trim().isEmpty ?? true)
                            ? context.l10n.homeActivePeriodTitle
                            : (_periodCore?.title ??
                                  context.l10n.homeActivePeriodTitle),
                        body: (_periodCore?.coreStory.trim().isEmpty ?? true)
                            ? (_periodCore?.bigPicture ?? '')
                            : (_periodCore?.coreStory ?? ''),
                        onTap: () => _openTiming(context),
                      ),
                    ),
                  ],
                  if (_error != null) ...[
                    const SizedBox(height: 18),
                    Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.cloud_off_outlined,
                          size: 40,
                          color: Colors.grey[400],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          _error ?? '',
                          textAlign: TextAlign.center,
                          style: context.profileTheme.typography.micro.copyWith(
                            color: context.profileTheme.colors.textLight,
                            height: 1.4,
                          ),
                        ),
                        const SizedBox(height: 16),
                        TextButton(
                          onPressed: _retry,
                          child: Text(context.l10n.commonRetry),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  bool _shouldShowTimingPanel({
    required PeriodCoreDto? periodCore,
    required String heroBody,
    required String activeTitle,
    required String activeSubtitle,
  }) {
    if (periodCore == null) {
      return false;
    }
    final title = (periodCore.title).trim().toLowerCase();
    final coreStory = (periodCore.coreStory).trim().toLowerCase();
    final bigPicture = (periodCore.bigPicture).trim().toLowerCase();
    final hero = heroBody.trim().toLowerCase();
    final activeTitleNorm = activeTitle.trim().toLowerCase();
    final activeSubtitleNorm = activeSubtitle.trim().toLowerCase();
    final titleRepeats = title.isEmpty || title == activeTitleNorm;
    final bodyCandidate = coreStory.isNotEmpty ? coreStory : bigPicture;
    final bodyRepeats =
        bodyCandidate.isEmpty ||
        bodyCandidate == hero ||
        bodyCandidate == activeSubtitleNorm;
    return !(titleRepeats && bodyRepeats);
  }

  List<_HomeWeekItemData> _buildWeekItems(
    BuildContext context,
    List<EventCardDto> cards, {
    required Map<String, NarrativeCalendarDay> calendarDays,
    required int selectedIndex,
    required DateTime baseDay,
  }) {
    final locale = Localizations.localeOf(context).toLanguageTag();
    final now = TransitRequestBuilder.stripDate(baseDay);
    return List<_HomeWeekItemData>.generate(7, (index) {
      final date = DateTime(now.year, now.month, now.day + index);
      final card = index < cards.length ? cards[index] : null;
      final dayKey = TransitRequestBuilder.fmtDate(
        TransitRequestBuilder.stripDate(date),
      );
      final dayMeta = calendarDays[dayKey];
      final rawWeekday = DateFormat(
        'EEE',
        locale,
      ).format(date).replaceAll('.', '');
      final weekdayLabel = toBeginningOfSentenceCase(rawWeekday);
      return _HomeWeekItemData(
        index: index,
        date: date,
        weekdayLabel: weekdayLabel,
        dayNumber: date.day,
        isToday: index == 0,
        isSelected: index == selectedIndex,
        isHighlighted: card != null || dayMeta != null,
        accent: _homeAccentForIndex(index),
        card: card,
        dayMeta: dayMeta,
      );
    });
  }

  Color _homeAccentForIndex(int index) {
    const accents = <Color>[
      Color(0xFFD8FF72),
      Color(0xFFD8CBFF),
      Color(0xFFEBA5FF),
      Color(0xFFA6F0CF),
      Color(0xFFFFB4D5),
      Color(0xFFCAB4FF),
      Color(0xFFB9FF8C),
    ];
    return accents[index % accents.length];
  }

  String _formatHomeToday(BuildContext context, DateTime date) {
    return MaterialLocalizations.of(context).formatMediumDate(date);
  }

  String _resolveHomeHeroTitle({
    required PeriodCardDto? selectedCard,
    required String fallbackTitle,
  }) {
    final selectedTitle = selectedCard?.title.trim() ?? '';
    if (selectedTitle.isNotEmpty) {
      return selectedTitle;
    }
    return fallbackTitle;
  }

  String _resolveHomeHeroBody({
    required PeriodCardDto? selectedCard,
    required String fallbackBody,
  }) {
    final opening = selectedCard?.eventCard?.opening.trim() ?? '';
    if (opening.isNotEmpty) {
      return opening;
    }
    final subtitle = selectedCard?.subtitle.trim() ?? '';
    if (subtitle.isNotEmpty) {
      return subtitle;
    }
    return fallbackBody;
  }

  String _resolveHomeHeroPrompt({
    required PeriodCardDto? selectedCard,
    required String fallbackPrompt,
  }) {
    final builds = selectedCard?.eventCard?.whatItBuilds.trim() ?? '';
    if (builds.isNotEmpty) {
      return builds;
    }
    final subtitle = selectedCard?.subtitle.trim() ?? '';
    if (subtitle.isNotEmpty) {
      return subtitle;
    }
    return fallbackPrompt;
  }

  String _resolveHomeDailyHeroTitle({
    required EventCardDto? card,
    required NarrativeCalendarDay? dayMeta,
    required String fallbackTitle,
  }) {
    final preferDayMeta = _shouldPreferHomeDayMeta(card);
    final toneLabel = _humanizeHomeToneLabel(dayMeta?.toneLabelTr);
    if (preferDayMeta && toneLabel.isNotEmpty) {
      return toneLabel;
    }
    final feltLine = card?.feltLineTr.trim() ?? '';
    if (feltLine.isNotEmpty) {
      return feltLine;
    }
    if (toneLabel.isNotEmpty) {
      return toneLabel;
    }
    final microSummary = dayMeta?.microSummaryTr.trim() ?? '';
    if (microSummary.isNotEmpty) {
      return microSummary;
    }
    final headline = card?.headline.trim() ?? '';
    if (headline.isNotEmpty) {
      return headline;
    }
    final title = card?.title.trim() ?? '';
    if (title.isNotEmpty) {
      return title;
    }
    return fallbackTitle;
  }

  String _resolveHomeDailyHeroBody({
    required EventCardDto? card,
    required NarrativeCalendarDay? dayMeta,
    required String fallbackBody,
  }) {
    final preferDayMeta = _shouldPreferHomeDayMeta(card);
    final microSummary = dayMeta?.microSummaryTr.trim() ?? '';
    if (preferDayMeta && microSummary.isNotEmpty) {
      return microSummary;
    }
    final opening = card?.opening.trim() ?? '';
    if (opening.isNotEmpty) {
      return opening;
    }
    final whyLine = card?.whyItFeelsThisWayTr.trim() ?? '';
    final guidanceLine = card?.guidanceMicroTr.trim() ?? '';
    final body = [
      whyLine,
      guidanceLine,
    ].where((line) => line.isNotEmpty).join('\n');
    if (body.isNotEmpty) {
      return body;
    }
    if (microSummary.isNotEmpty) {
      return microSummary;
    }
    final essence = card?.essence.trim() ?? '';
    if (essence.isNotEmpty) {
      return essence;
    }
    return fallbackBody;
  }

  String _resolveHomeDailyHeroPrompt({
    required EventCardDto? card,
    required NarrativeCalendarDay? dayMeta,
    required String fallbackPrompt,
  }) {
    final preferDayMeta = _shouldPreferHomeDayMeta(card);
    final daySignal = dayMeta?.signalLabelTr.trim() ?? '';
    if (preferDayMeta && daySignal.isNotEmpty) {
      return daySignal;
    }
    final signalLabel = card?.signalLabelTr.trim() ?? '';
    if (signalLabel.isNotEmpty) {
      return signalLabel;
    }
    final houseHint = card?.houseTouchpointHintTr.trim() ?? '';
    if (houseHint.isNotEmpty) {
      return houseHint;
    }
    if (daySignal.isNotEmpty) {
      return daySignal;
    }
    return fallbackPrompt;
  }

  Widget _buildTransitCarousel(BuildContext context) {
    final profileTheme = context.profileTheme;
    final typo = profileTheme.typography;
    final profile = ref.read(userProfileProvider).asData?.value;

    if (_loading && _periodCards.isEmpty) {
      return ListView.separated(
        scrollDirection: Axis.horizontal,
        itemBuilder: (_, i) => const _TransitPlaceholderCard(),
        separatorBuilder: (_, i) => SizedBox(width: profileTheme.spacing.sm),
        itemCount: 3,
      );
    }

    if (_periodCards.isEmpty) {
      return _GlassCard(
        child: Align(
          alignment: Alignment.centerLeft,
          child: Text(
            context.l10n.homePeriodCardsPending,
            style: typo.body.copyWith(color: profileTheme.colors.muted),
          ),
        ),
      );
    }

    final cards = _periodCards.take(5).toList(growable: false);
    return ListView.separated(
      scrollDirection: Axis.horizontal,
      itemCount: cards.length,
      separatorBuilder: (_, i) => SizedBox(width: profileTheme.spacing.sm),
      itemBuilder: (context, index) {
        final card = cards[index];
        return SizedBox(
          width: 286,
          child: _TransitSummaryCard(
            card: card,
            accent: _accentForIndex(index),
            showSticker: index % 3 == 0,
            onTap: () => _openTransitCard(context, profile, card),
          ),
        );
      },
    );
  }

  Color _accentForIndex(int index) {
    final colors = context.profileTheme.colors;
    final accents = <Color>[colors.primary, colors.lavender, colors.lime];
    return accents[index % accents.length];
  }

  void _maybeBootstrap(Map<String, dynamic>? profile, User? user) {
    if (!_hasProfile(profile)) {
      return;
    }
    final dayContext = _resolveDayContext(profile);
    final todayKey = dayContext.dayKey;
    final key =
        '${profile?['birth_date']}|${profile?['birth_time']}|${profile?['place'] ?? profile?['city']}|${profile?['timezone']}|${user?.id}|$todayKey';
    if (_lastKey == key) {
      return;
    }
    _lastKey = key;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || profile == null) {
        return;
      }
      _loadHomeData(profile, dayContext: dayContext);
    });
  }

  Future<void> _loadHomeData(
    Map<String, dynamic> profile, {
    required HomeDayContext dayContext,
  }) async {
    final requestVersion = ++_homeLoadVersion;
    _homeFastRetryAttempt = 0;
    _homeDayContext = dayContext;
    _lastLoadedDayKey = dayContext.dayKey;
    setState(() {
      _loading = true;
      _error = null;
    });

    final client = ApiClient(baseUrl: _baseUrl);
    final natalPayload = _buildNatalPayload(profile);
    final userId = Supabase.instance.client.auth.currentUser?.id;

    unawaited(
      _loadSkySection(
        client: client,
        profile: profile,
        requestVersion: requestVersion,
      ),
    );

    unawaited(
      _loadFastHomePreview(
        client: client,
        profile: profile,
        userId: userId,
        requestVersion: requestVersion,
        dayContext: dayContext,
      ),
    );
    unawaited(
      _loadNarrativeSection(
        profile: profile,
        requestVersion: requestVersion,
        dayContext: dayContext,
      ),
    );
    unawaited(
      _loadNatalSection(
        client: client,
        natalPayload: natalPayload,
        requestVersion: requestVersion,
      ),
    );
  }

  bool _isActiveHomeLoad(int requestVersion) =>
      mounted && requestVersion == _homeLoadVersion;

  bool _hasResolvedTodayTransit() {
    return hasStrongHomeDailyContent(dailyCards: _todayDailyCards);
  }

  Future<void> _loadNarrativeSection({
    required Map<String, dynamic> profile,
    required int requestVersion,
    required HomeDayContext dayContext,
  }) async {
    final localeCode = Localizations.localeOf(context).languageCode;
    final l10n = context.l10n;
    try {
      final periodMap = await _narrativeRepository.fetchDailyNarrative(
        profile: profile,
        selectedDate: dayContext.today,
        focusedRange: true,
        includeBestTimes: false,
        responseMode: 'public_only',
        payloadProfile: TransitPayloadProfile.home,
        visibleDaysLimit: 7,
        receiveTimeout: LoadTuning.homeNarrativeTimeout,
        requestSla: ApiRequestSla.background,
        cachePolicy: NarrativeCachePolicy.disabled,
        locale: localeCode,
      );
      final responseAnchorDay = resolveHomeDailyResponseAnchorDay(
        periodMap,
        fallbackDayKey: dayContext.dayKey,
      );
      final periodNarrative = NarrativeResponse.fromMap(periodMap);
      final snapshot = buildHomeTransitSnapshot(
        narrative: periodNarrative,
        today: dayContext.today,
        l10n: l10n,
      );
      final mergedSnapshot = mergeHomeTransitSnapshot(
        incoming: snapshot,
        currentPeriodCore: _periodCore,
        currentPeriodCards: _periodCards,
        currentDailyCards: _todayDailyCards,
        currentCalendarDays: _homeCalendarDays,
        currentTodayDayMeta: _todayDayMeta,
      );
      HomeTransitSnapshot resolvedSnapshot = mergedSnapshot;

      final hasStrongIncomingContent = hasStrongHomeDailyContent(
        dailyCards: resolvedSnapshot.dailyCards,
      );
      final hasMetaOnlyIncomingContent = hasHomeMetaOnlyContent(
        dailyCards: resolvedSnapshot.dailyCards,
        dayMeta: resolvedSnapshot.todayDayMeta,
      );
      final fallbackReasonCode = homeCalendarDayFallbackReasonCode(
        rawDailyEventCardsCount: periodNarrative.dailyEventCards.length,
        dailyCards: resolvedSnapshot.dailyCards,
        dayMeta: resolvedSnapshot.todayDayMeta,
      );
      final shouldRunFallback = shouldRunHomeCalendarDayFallback(
        rawDailyEventCardsCount: periodNarrative.dailyEventCards.length,
        dailyCards: resolvedSnapshot.dailyCards,
        dayMeta: resolvedSnapshot.todayDayMeta,
      );

      if (shouldRunFallback) {
        PerfTelemetry.logEvent(
          'forced_calendar_day_fallback',
          data: <String, Object?>{
            'selected_day_key': dayContext.dayKey,
            'response_anchor_day': responseAnchorDay,
            'timezone': dayContext.timezone,
            'day_context_source': dayContext.source,
            'reason_code': fallbackReasonCode,
            'incoming_daily_count': snapshot.dailyCards.length,
            'raw_daily_event_cards_count':
                periodNarrative.dailyEventCards.length,
            'incoming_has_meta_only': hasMetaOnlyIncomingContent,
            'source_type': resolveHomeDailySourceType(
              card: snapshot.dailyCards.isNotEmpty
                  ? snapshot.dailyCards.first
                  : null,
              dayMeta: snapshot.todayDayMeta,
            ),
            'has_authoritative_daily_card': hasAuthoritativeHomeDailyContent(
              dailyCards: snapshot.dailyCards,
            ),
            'degraded_reason': homeDailyDegradedReason(
              loading: false,
              dailyCards: snapshot.dailyCards,
              dayMeta: snapshot.todayDayMeta,
              errorMessage: null,
            ),
          },
        );
        final detailFallbackSnapshot = await _loadHomeDailyCalendarDayFallback(
          profile: profile,
          localeCode: localeCode,
          l10n: l10n,
          requestVersion: requestVersion,
          dayContext: dayContext,
          reasonCode: fallbackReasonCode,
        );
        if (detailFallbackSnapshot != null) {
          resolvedSnapshot = mergeHomeTransitSnapshot(
            incoming: detailFallbackSnapshot,
            currentPeriodCore: resolvedSnapshot.periodCore,
            currentPeriodCards: resolvedSnapshot.periodCards,
            currentDailyCards: resolvedSnapshot.dailyCards,
            currentCalendarDays: resolvedSnapshot.calendarDays,
            currentTodayDayMeta: resolvedSnapshot.todayDayMeta,
          );
        }
      }

      if (!_isActiveHomeLoad(requestVersion)) {
        return;
      }

      final currentDailyCard = _todayDailyCards.isNotEmpty
          ? _todayDailyCards.first
          : null;
      final incomingDailyCard = resolvedSnapshot.dailyCards.isNotEmpty
          ? resolvedSnapshot.dailyCards.first
          : null;
      final resolvedDailyCard = resolvedSnapshot.dailyCards.isNotEmpty
          ? resolvedSnapshot.dailyCards.first
          : null;
      final hasStrongResolvedContent = hasStrongHomeDailyContent(
        dailyCards: resolvedSnapshot.dailyCards,
      );
      final hasMetaOnlyResolvedContent = hasHomeMetaOnlyContent(
        dailyCards: resolvedSnapshot.dailyCards,
        dayMeta: resolvedSnapshot.todayDayMeta,
      );
      final hasAuthoritativeDailyCard = hasAuthoritativeHomeDailyContent(
        dailyCards: resolvedSnapshot.dailyCards,
      );
      final sourceType = resolveHomeDailySourceType(
        card: resolvedDailyCard,
        dayMeta: resolvedSnapshot.todayDayMeta,
      );
      final degradedReason = homeDailyDegradedReason(
        loading: false,
        dailyCards: resolvedSnapshot.dailyCards,
        dayMeta: resolvedSnapshot.todayDayMeta,
        errorMessage: null,
      );
      final renderState = resolveHomeDailyRenderState(
        loading: false,
        dailyCards: resolvedSnapshot.dailyCards,
        dayMeta: resolvedSnapshot.todayDayMeta,
        errorMessage: null,
      );
      PerfTelemetry.logEvent(
        'home_daily_transit_merge',
        data: <String, Object?>{
          'selected_day_key': dayContext.dayKey,
          'response_anchor_day': responseAnchorDay,
          'timezone': dayContext.timezone,
          'day_context_source': dayContext.source,
          'response_mode': 'public_only',
          'current_daily_count': _todayDailyCards.length,
          'incoming_daily_count': snapshot.dailyCards.length,
          'resolved_daily_count': resolvedSnapshot.dailyCards.length,
          'raw_daily_event_cards_count': periodNarrative.dailyEventCards.length,
          'current_source': describeHomeDailyCardSource(currentDailyCard),
          'incoming_source': describeHomeDailyCardSource(incomingDailyCard),
          'resolved_source': describeHomeDailyCardSource(resolvedDailyCard),
          'source_type': sourceType,
          'current_strength': scoreHomeDailyCardStrength(currentDailyCard),
          'incoming_strength': scoreHomeDailyCardStrength(incomingDailyCard),
          'resolved_strength': scoreHomeDailyCardStrength(resolvedDailyCard),
          'incoming_has_strong_content': hasStrongIncomingContent,
          'incoming_has_meta_only_content': hasMetaOnlyIncomingContent,
          'resolved_has_strong_content': hasStrongResolvedContent,
          'resolved_has_meta_only_content': hasMetaOnlyResolvedContent,
          'has_authoritative_daily_card': hasAuthoritativeDailyCard,
          'degraded_reason': degradedReason,
          'render_state': homeDailyRenderStateToken(renderState),
          'fallback_reason_code': shouldRunFallback
              ? fallbackReasonCode
              : 'none',
          'incoming_calendar_days': snapshot.calendarDays.length,
          'resolved_calendar_days': resolvedSnapshot.calendarDays.length,
          'incoming_has_today_day_meta': snapshot.todayDayMeta != null,
          'resolved_has_today_day_meta': resolvedSnapshot.todayDayMeta != null,
          'overwrite_prevented':
              currentDailyCard != null &&
              incomingDailyCard != null &&
              _sameHomeDailyCard(resolvedDailyCard, currentDailyCard) &&
              !_sameHomeDailyCard(currentDailyCard, incomingDailyCard),
          'resolution_reason': _homeDailyResolutionReason(
            dailyCards: resolvedSnapshot.dailyCards,
            dayMeta: resolvedSnapshot.todayDayMeta,
          ),
        },
      );
      PerfTelemetry.logEvent(
        'home_daily_render_state',
        data: <String, Object?>{
          'selected_day_key': dayContext.dayKey,
          'response_anchor_day': responseAnchorDay,
          'source_type': sourceType,
          'has_authoritative_daily_card': hasAuthoritativeDailyCard,
          'degraded_reason': degradedReason,
          'render_state': homeDailyRenderStateToken(renderState),
        },
      );
      if (hasMetaOnlyResolvedContent && !hasStrongResolvedContent) {
        PerfTelemetry.logEvent(
          'meta_only_render',
          data: <String, Object?>{
            'selected_day_key': dayContext.dayKey,
            'response_anchor_day': responseAnchorDay,
            'timezone': dayContext.timezone,
            'day_context_source': dayContext.source,
            'resolved_daily_count': resolvedSnapshot.dailyCards.length,
            'fallback_reason_code': shouldRunFallback
                ? fallbackReasonCode
                : 'none',
            'source_type': sourceType,
            'has_authoritative_daily_card': hasAuthoritativeDailyCard,
            'degraded_reason': degradedReason,
          },
        );
      }

      setState(() {
        _periodCore = resolvedSnapshot.periodCore;
        _periodCards = resolvedSnapshot.periodCards;
        _todayDailyCards = resolvedSnapshot.dailyCards;
        _homeCalendarDays = resolvedSnapshot.calendarDays;
        _todayDayMeta = resolvedSnapshot.todayDayMeta;
        _loading = false;
        _error = null;
      });
      if (resolvedSnapshot.calendarDays.length < 7) {
        _hydrateHomeWeekCalendarDays(
          profile: profile,
          requestVersion: requestVersion,
          dayContext: dayContext,
        );
      }
    } catch (e) {
      if (!_isActiveHomeLoad(requestVersion)) {
        return;
      }
      PerfTelemetry.logEvent(
        'home_daily_render_state',
        data: <String, Object?>{
          'selected_day_key': dayContext.dayKey,
          'response_anchor_day': dayContext.dayKey,
          'source_type': resolveHomeDailySourceType(
            card: _todayDailyCards.isNotEmpty ? _todayDailyCards.first : null,
            dayMeta: _todayDayMeta,
          ),
          'has_authoritative_daily_card': hasAuthoritativeHomeDailyContent(
            dailyCards: _todayDailyCards,
          ),
          'degraded_reason': 'request_error',
          'render_state': homeDailyRenderStateToken(
            resolveHomeDailyRenderState(
              loading: false,
              dailyCards: _todayDailyCards,
              dayMeta: _todayDayMeta,
              errorMessage: '$e',
            ),
          ),
        },
      );
      setState(() {
        _loading = false;
        final hasFallbackContent =
            _coreStory.trim().isNotEmpty ||
            _skyFeedItems.isNotEmpty ||
            _sunSign != '—' ||
            _moonSign != '—' ||
            _risingSign != '—';
        if (_periodCards.isEmpty &&
            _todayDailyCards.isEmpty &&
            !hasFallbackContent) {
          _error = _friendlyHomeLoadError(e, l10n);
        }
      });
    }
  }

  Future<HomeTransitSnapshot?> _loadHomeDailyCalendarDayFallback({
    required Map<String, dynamic> profile,
    required String localeCode,
    required AppLocalizations l10n,
    required int requestVersion,
    required HomeDayContext dayContext,
    required String reasonCode,
  }) async {
    PerfTelemetry.logEvent(
      'home_daily_transit_detail_fallback_start',
      data: <String, Object?>{
        'selected_day_key': dayContext.dayKey,
        'timezone': dayContext.timezone,
        'day_context_source': dayContext.source,
        'reason_code': reasonCode,
      },
    );
    try {
      final narrativeMap = await _narrativeRepository.fetchDailyNarrative(
        profile: profile,
        selectedDate: dayContext.today,
        focusedRange: true,
        includeBestTimes: false,
        responseMode: 'full',
        payloadProfile: TransitPayloadProfile.calendarDay,
        visibleDaysLimit: 7,
        receiveTimeout: LoadTuning.homeNarrativeTimeout,
        requestSla: ApiRequestSla.background,
        cachePolicy: NarrativeCachePolicy.disabled,
        locale: localeCode,
      );
      final responseAnchorDay = resolveHomeDailyResponseAnchorDay(
        narrativeMap,
        fallbackDayKey: dayContext.dayKey,
      );
      if (!_isActiveHomeLoad(requestVersion)) {
        return null;
      }
      final narrative = NarrativeResponse.fromMap(narrativeMap);
      final snapshot = buildHomeTransitSnapshot(
        narrative: narrative,
        today: dayContext.today,
        l10n: l10n,
      );
      final sourceType = resolveHomeDailySourceType(
        card: snapshot.dailyCards.isNotEmpty ? snapshot.dailyCards.first : null,
        dayMeta: snapshot.todayDayMeta,
      );
      final hasAuthoritativeDailyCard = hasAuthoritativeHomeDailyContent(
        dailyCards: snapshot.dailyCards,
      );
      final degradedReason = homeDailyDegradedReason(
        loading: false,
        dailyCards: snapshot.dailyCards,
        dayMeta: snapshot.todayDayMeta,
        errorMessage: null,
      );
      PerfTelemetry.logEvent(
        'home_daily_transit_detail_fallback_end',
        data: <String, Object?>{
          'status': 'ok',
          'daily_count': snapshot.dailyCards.length,
          'calendar_days': snapshot.calendarDays.length,
          'has_today_day_meta': snapshot.todayDayMeta != null,
          'selected_day_key': dayContext.dayKey,
          'response_anchor_day': responseAnchorDay,
          'timezone': dayContext.timezone,
          'day_context_source': dayContext.source,
          'reason_code': reasonCode,
          'source_type': sourceType,
          'has_authoritative_daily_card': hasAuthoritativeDailyCard,
          'degraded_reason': degradedReason,
        },
      );
      return snapshot;
    } catch (error) {
      PerfTelemetry.logEvent(
        'home_daily_transit_detail_fallback_end',
        data: <String, Object?>{
          'status': 'error',
          'error_type': error.runtimeType.toString(),
          'selected_day_key': dayContext.dayKey,
          'response_anchor_day': dayContext.dayKey,
          'timezone': dayContext.timezone,
          'day_context_source': dayContext.source,
          'reason_code': reasonCode,
          'source_type': 'none',
          'has_authoritative_daily_card': false,
          'degraded_reason': 'request_error',
        },
      );
      return null;
    }
  }

  Future<void> _hydrateHomeWeekCalendarDays({
    required Map<String, dynamic> profile,
    required int requestVersion,
    required HomeDayContext dayContext,
  }) async {
    final localeCode = Localizations.localeOf(context).languageCode;
    try {
      final narrativeMap = await _narrativeRepository.fetchDailyNarrative(
        profile: profile,
        selectedDate: dayContext.today,
        focusedRange: false,
        includeBestTimes: false,
        responseMode: 'full',
        payloadProfile: TransitPayloadProfile.calendarPeriod,
        visibleDaysLimit: 7,
        receiveTimeout: LoadTuning.homeWeekNarrativeTimeout,
        requestSla: ApiRequestSla.background,
        cachePolicy: NarrativeCachePolicy.disabled,
        locale: localeCode,
      );
      if (!_isActiveHomeLoad(requestVersion)) {
        return;
      }
      final narrative = NarrativeResponse.fromMap(narrativeMap);
      if (narrative.calendarDays.isEmpty) {
        return;
      }
      final todayKey = dayContext.dayKey;
      setState(() {
        _homeCalendarDays = narrative.calendarDays;
        _todayDayMeta = narrative.calendarDays[todayKey] ?? _todayDayMeta;
      });
    } catch (_) {}
  }

  Future<void> _loadFastHomePreview({
    required ApiClient client,
    required Map<String, dynamic> profile,
    required String? userId,
    required int requestVersion,
    required HomeDayContext dayContext,
    int attempt = 0,
  }) async {
    final l10n = context.l10n;
    try {
      final response = await client.get(
        '/home/fast',
        queryParameters: _buildHomeFastQuery(
          profile,
          userId: userId,
          dayContext: dayContext,
        ),
        receiveTimeout: LoadTuning.homeFastTimeout,
        requestSla: ApiRequestSla.fast,
      );
      final payload = _HomeFastPayload.fromMap(_asMap(response.data));
      if (!_isActiveHomeLoad(requestVersion) || !payload.hasContent) {
        if (payload.isTransitDeferred &&
            attempt < LoadTuning.maxHomeFastDeferredRetries) {
          _scheduleFastHomeRetry(
            client: client,
            profile: profile,
            userId: userId,
            requestVersion: requestVersion,
            nextAttempt: attempt + 1,
            dayContext: dayContext,
          );
        }
        return;
      }
      final fastPeriodCore = _buildHomeFastPeriodCore(payload, l10n: l10n);
      final fastPeriodCards = _buildHomeFastPeriodCards(payload, l10n: l10n);
      final fastDailyFallback = _buildHomeFastFallbackDailyCard(
        payload,
        l10n: l10n,
      );
      if (fastDailyFallback != null &&
          !hasAuthoritativeHomeDailyContent(dailyCards: _todayDailyCards)) {
        PerfTelemetry.logEvent(
          'home_daily_fast_preview_ignored',
          data: <String, Object?>{
            'selected_day_key': dayContext.dayKey,
            'response_anchor_day': dayContext.dayKey,
            'source_type': 'fast_preview',
            'has_authoritative_daily_card': false,
            'degraded_reason': 'fast_preview_only',
            'transit_summary_state': payload.transitSummaryState,
          },
        );
      }
      setState(() {
        if (_periodCore == null && fastPeriodCore != null) {
          _periodCore = fastPeriodCore;
        }
        if (_periodCards.isEmpty && fastPeriodCards.isNotEmpty) {
          _periodCards = fastPeriodCards;
        }
        if (_coreStory.trim().isEmpty && payload.summary.isNotEmpty) {
          _coreStory = payload.summary;
        }
        if (_skyFeedSummary.trim().isEmpty &&
            payload.energySummary.isNotEmpty) {
          _skyFeedSummary = payload.energySummary;
        }
        if (_error != null &&
            (_periodCards.isNotEmpty || _coreStory.trim().isNotEmpty)) {
          _error = null;
        }
        if (_periodCards.isNotEmpty || _coreStory.trim().isNotEmpty) {
          _loading = false;
        }
      });
      if (payload.isTransitDeferred &&
          attempt < LoadTuning.maxHomeFastDeferredRetries) {
        _scheduleFastHomeRetry(
          client: client,
          profile: profile,
          userId: userId,
          requestVersion: requestVersion,
          nextAttempt: attempt + 1,
          dayContext: dayContext,
        );
      }
    } catch (e) {
      debugPrint('Home fast load skipped: $e');
      if (attempt < LoadTuning.maxHomeFastDeferredRetries &&
          _isActiveHomeLoad(requestVersion) &&
          !_hasResolvedTodayTransit()) {
        _scheduleFastHomeRetry(
          client: client,
          profile: profile,
          userId: userId,
          requestVersion: requestVersion,
          nextAttempt: attempt + 1,
          dayContext: dayContext,
        );
      }
    }
  }

  void _scheduleFastHomeRetry({
    required ApiClient client,
    required Map<String, dynamic> profile,
    required String? userId,
    required int requestVersion,
    required int nextAttempt,
    required HomeDayContext dayContext,
  }) {
    if (nextAttempt <= _homeFastRetryAttempt ||
        nextAttempt > LoadTuning.maxHomeFastDeferredRetries) {
      return;
    }
    _homeFastRetryAttempt = nextAttempt;
    Future<void>.delayed(LoadTuning.homeFastDeferredRetryDelay).then((_) {
      if (!_isActiveHomeLoad(requestVersion) || _hasResolvedTodayTransit()) {
        return;
      }
      _loadFastHomePreview(
        client: client,
        profile: profile,
        userId: userId,
        requestVersion: requestVersion,
        dayContext: dayContext,
        attempt: nextAttempt,
      );
    });
  }

  Future<void> _loadSkySection({
    required ApiClient client,
    required Map<String, dynamic> profile,
    required int requestVersion,
  }) async {
    try {
      final response = await client.get(
        '/sky/now',
        queryParameters: <String, dynamic>{
          'tz': _resolveTimezone(profile),
          'limit': 4,
        },
        receiveTimeout: LoadTuning.homeSkyTimeout,
        cacheTtl: LoadTuning.homeSkyCacheTtl,
      );
      final skyMap = _asMap((response).data);
      if (!_isActiveHomeLoad(requestVersion)) {
        return;
      }
      setState(() {
        _skyFeedSummary = _extractSkySummary(skyMap);
        _skyFeedItems = _extractSkyFeedItems(skyMap);
      });
    } catch (e) {
      debugPrint('Home sky load skipped: $e');
    }
  }

  Future<void> _loadNatalSection({
    required ApiClient client,
    required Map<String, dynamic> natalPayload,
    required int requestVersion,
  }) async {
    try {
      final response = await _fetchNatalInterpretResponse(
        client: client,
        natalPayload: natalPayload,
      );
      final interpretMap = _asMap(response.data);
      final summary = _extractNatalSummary(interpretMap);
      final sun = _toTrSign(_extractPlanetSign(interpretMap, 'Sun'));
      final moon = _toTrSign(_extractPlanetSign(interpretMap, 'Moon'));
      final rising = _toTrSign(_extractRisingSign(interpretMap));
      if (!_isActiveHomeLoad(requestVersion)) {
        return;
      }
      setState(() {
        _coreStory = summary;
        _sunSign = sun;
        _moonSign = moon;
        _risingSign = rising;
        if (summary.trim().isNotEmpty) {
          _loading = false;
          _error = null;
        }
      });
    } catch (e) {
      debugPrint('Home natal load skipped: $e');
    }
  }

  String _friendlyHomeLoadError(Object error, AppLocalizations l10n) {
    if (error is DioException) {
      if (error.type == DioExceptionType.receiveTimeout ||
          error.type == DioExceptionType.connectionTimeout) {
        return l10n.homeRequestTimedOut;
      }
      final status = error.response?.statusCode;
      if (status == 422) {
        return l10n.calendarInvalidDateOrProfile;
      }
    }
    return l10n.homeDataLoadFailed('$error');
  }

  Future<Response<dynamic>> _fetchNatalInterpretResponse({
    required ApiClient client,
    required Map<String, dynamic> natalPayload,
  }) async {
    return client.post(
      '/interpret/ui',
      data: <String, dynamic>{...natalPayload, 'summary_only': true},
      requestSla: ApiRequestSla.background,
      cacheTtl: LoadTuning.homeNatalCacheTtl,
    );
  }

  Map<String, dynamic> _buildNatalPayload(Map<String, dynamic> profile) {
    final place = _resolvePlace(profile);
    final payload = <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': _normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'locale': Localizations.localeOf(context).languageCode,
    };
    TransitRequestBuilder.appendKnownLocationFields(payload, profile: profile);
    return payload;
  }

  Map<String, dynamic> _buildHomeFastQuery(
    Map<String, dynamic> profile, {
    required String? userId,
    required HomeDayContext dayContext,
  }) {
    final place = _resolvePlace(profile);
    final query = <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': _normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'transit_place': place,
      'date': dayContext.dayKey,
      'tz': _resolveTimezone(profile),
      'locale': Localizations.localeOf(context).languageCode,
      'lens': 'general',
      if (userId != null && userId.isNotEmpty) 'user_id': userId,
    };
    TransitRequestBuilder.appendKnownLocationFields(
      query,
      profile: profile,
      includeTransit: true,
    );
    return query;
  }

  String _resolvePlace(Map<String, dynamic> profile) {
    final city = (profile['city'] ?? '').toString().trim();
    final country = (profile['country'] ?? '').toString().trim();
    final placeRaw = (profile['place'] ?? '').toString().trim();
    if (placeRaw.isNotEmpty) {
      return placeRaw;
    }
    if (city.isEmpty) {
      return country;
    }
    if (country.isEmpty) {
      return city;
    }
    return '$city, $country';
  }

  String _resolveTimezone(Map<String, dynamic> profile) {
    final raw = TransitRequestBuilder.resolveTimezone(profile);
    if (raw.contains('/')) {
      return raw;
    }
    return 'Europe/Istanbul';
  }

  bool _hasProfile(Map<String, dynamic>? profile) {
    if (profile == null) {
      return false;
    }
    final birthDate = (profile['birth_date'] ?? '').toString().trim();
    final birthTime = (profile['birth_time'] ?? '').toString().trim();
    final place = _resolvePlace(profile);
    return birthDate.isNotEmpty && birthTime.isNotEmpty && place.isNotEmpty;
  }

  String _displayName(Map<String, dynamic>? profile, User? user) {
    final fromProfile = (profile?['full_name'] ?? profile?['name'] ?? '')
        .toString()
        .trim();
    if (fromProfile.isNotEmpty) {
      return fromProfile;
    }
    final fromMail = (user?.email ?? '').split('@').first.trim();
    if (fromMail.isNotEmpty) {
      return fromMail;
    }
    return 'Arkadasim';
  }

  void _openTiming(BuildContext context) {
    Navigator.of(
      context,
    ).push(MaterialPageRoute<void>(builder: (_) => const CalendarHubPage()));
  }

  Future<void> _openHomeDay(
    BuildContext context,
    Map<String, dynamic>? profile,
    DateTime day, {
    CalendarDayBundle? initialBundle,
  }) async {
    if (!_hasProfile(profile)) {
      _openTiming(context);
      return;
    }
    final resolvedProfile = profile;
    if (resolvedProfile == null) {
      _openTiming(context);
      return;
    }
    final localeCode = Localizations.localeOf(context).languageCode;
    final returnedDate = await Navigator.of(context, rootNavigator: true)
        .push<DateTime>(
          buildCalendarDayPageRoute<DateTime>(
            context: context,
            initialDate: DateTime(day.year, day.month, day.day),
            source: 'home_preview',
            builder: (_) => CalendarDayPage(
              profile: resolvedProfile,
              initialDate: DateTime(day.year, day.month, day.day),
              initialBundle: initialBundle,
              localeCode: localeCode,
              source: 'home_preview',
            ),
          ),
        );
    if (!mounted || returnedDate == null) {
      return;
    }
    final normalized = DateTime(
      returnedDate.year,
      returnedDate.month,
      returnedDate.day,
    );
    final dayContext = _homeDayContext ?? _resolveDayContext(profile);
    final todayDate = dayContext.today;
    final dayOffset = normalized.difference(todayDate).inDays;
    if (dayOffset >= 0 && dayOffset < 7 && dayOffset != _selectedWeekIndex) {
      setState(() => _selectedWeekIndex = dayOffset);
    }
  }

  CalendarDayBundle? _buildInitialHomeDayBundle({
    required DateTime date,
    required EventCardDto? card,
    required NarrativeCalendarDay? dayMeta,
  }) {
    if (card == null) {
      return null;
    }
    return seedCalendarDayBundleFromDailyEventCard(
      date: date,
      card: card,
      selectedDayMeta: dayMeta,
      periodCore: _periodCore,
    );
  }

  void _openTransitCard(
    BuildContext context,
    Map<String, dynamic>? profile,
    PeriodCardDto card,
  ) {
    final dayContext = _homeDayContext ?? _resolveDayContext(profile);
    final focusDay = resolvePeriodCardFocusDate(
      card,
      fallbackDay: dayContext.today,
    );
    if (focusDay != null) {
      _openHomeDay(
        context,
        profile,
        focusDay,
        initialBundle: seedCalendarDayBundleFromPeriodCard(
          date: focusDay,
          card: card,
          periodCore: _periodCore,
        ),
      );
      return;
    }
    _openPeriodDetails(context, card);
  }

  void _openPeriodDetails(BuildContext context, PeriodCardDto card) {
    if (!assertPeriodSource(card, context: 'Home/Donem Kartlari')) {
      return;
    }
    Navigator.of(context, rootNavigator: true).push(
      MaterialPageRoute<void>(
        builder: (_) => PeriodDetailPage(
          card: card,
          periodCore: _periodCore,
          routeSource: PeriodDetailRouteSource.home,
        ),
      ),
    );
  }

  void _openSkyEventDetail(BuildContext context, _SkyFeedItemData item) {
    final dto = item.toDto();
    if (dto.eventKey.isEmpty) {
      return;
    }
    Navigator.of(context, rootNavigator: true).push(
      _adaptiveSwipeRoute<void>(context, (_) => SkyEventDetailPage(item: dto)),
    );
  }

  void _openSkyFeed(BuildContext context) {
    Navigator.of(
      context,
      rootNavigator: true,
    ).push(_adaptiveSwipeRoute<void>(context, (_) => const SkyEventFeedPage()));
  }

  _SkyBulletin _buildSkyBulletin(List<PeriodCardDto> cards) {
    // TODO: Swap this derived source with /sky/now when backend endpoint is available.
    if (cards.isEmpty) {
      return const _SkyBulletin(
        summary: 'Bugün gökyüzü sakin.',
        chips: <String>['Kolektif', 'Gozlem'],
        highlights: <_SkyHighlight>[],
      );
    }

    final sorted = [...cards]
      ..sort((a, b) => _skyScore(b).compareTo(_skyScore(a)));
    final selected = sorted.take(4).toList(growable: false);
    final highlights = <_SkyHighlight>[
      for (final card in selected)
        _SkyHighlight(
          title: card.title.isNotEmpty ? card.title : 'Genel Gokyuzu Etkisi',
          blurb: _collectiveBlurb(card),
        ),
    ];
    final chips = _buildSkyChips(selected);
    return _SkyBulletin(
      summary: _collectiveSummary(chips),
      chips: chips,
      highlights: highlights,
    );
  }

  _SkyBulletin _buildSkyBulletinFromFeed({
    required List<_SkyFeedItemData> items,
    required String summary,
  }) {
    if (items.isEmpty) {
      return _buildSkyBulletin(const <PeriodCardDto>[]);
    }
    final hero = items.first;
    return _SkyBulletin(
      summary: summary.trim().isNotEmpty ? summary.trim() : hero.summary,
      chips: hero.previewChips.take(3).toList(growable: false),
      highlights: [
        for (final item in items)
          _SkyHighlight(title: item.title, blurb: item.summary),
      ],
    );
  }

  double _skyScore(PeriodCardDto card) {
    final haystack = '${card.title} ${card.subtitle} ${card.timeHint}'
        .toLowerCase();
    double score = 1.0;
    if (haystack.contains('saturn') ||
        haystack.contains('uranus') ||
        haystack.contains('neptune') ||
        haystack.contains('pluto')) {
      score += 2.0;
    }
    if (haystack.contains('long') || haystack.contains('uzun')) {
      score += 1.0;
    }
    if (haystack.contains('retro') ||
        haystack.contains('station') ||
        haystack.contains('ingress') ||
        haystack.contains('exact') ||
        haystack.contains('peak')) {
      score += 0.7;
    }
    return score;
  }

  String _collectiveSummary(List<String> chips) {
    final lower = chips.map((e) => e.toLowerCase()).toSet();
    String first =
        'Bu dönemde kolektif ritimde yavaş ama kalıcı değişimler öne çıkıyor.';
    if (lower.contains('donusum')) {
      first = 'Kolektif alanda dönüşüm ve yeniden yapılanma etkisi belirgin.';
    } else if (lower.contains('yapi')) {
      first =
          'Yapı, sınır ve sorumluluk temaları kolektif alanda ağırlık kazanıyor.';
    } else if (lower.contains('degisim')) {
      first =
          'Değişim ve yenilenme başlıkları genel atmosferde daha görünür durumda.';
    }

    String second = 'Hizdan cok sureklilik ve planli adimlar destekleniyor.';
    if (lower.contains('belirsizlik')) {
      second =
          'Algilar ve beklentilerde dalgalanmalar olabilecegi icin netlik onemli.';
    } else if (lower.contains('retro')) {
      second =
          'Gecmis temalara donup duzeltme yapmak, yeni adimlardan daha verimli olabilir.';
    }
    return '$first $second';
  }

  List<String> _buildSkyChips(List<PeriodCardDto> cards) {
    final chips = <String>{};
    for (final card in cards) {
      final haystack = '${card.title} ${card.subtitle} ${card.timeHint}'
          .toLowerCase();
      if (haystack.contains('retro')) {
        chips.add('Retro');
      }
      if (haystack.contains('saturn')) {
        chips.add('Yapi');
      }
      if (haystack.contains('pluto')) {
        chips.add('Donusum');
      }
      if (haystack.contains('uranus')) {
        chips.add('Degisim');
      }
      if (haystack.contains('neptune')) {
        chips.add('Belirsizlik');
      }
      if (haystack.contains('long') || haystack.contains('uzun')) {
        chips.add('Uzun Dongu');
      }
      if (chips.length >= 3) {
        break;
      }
    }
    if (chips.isEmpty) {
      return const <String>['Kolektif', 'Ritim'];
    }
    return chips.take(3).toList(growable: false);
  }

  String _collectiveBlurb(PeriodCardDto card) {
    final source = card.subtitle.trim().isNotEmpty
        ? card.subtitle.trim()
        : card.timeHint.trim();
    if (source.isEmpty) {
      return 'Genel atmosferde bu etkinin kademeli olarak guclenmesi bekleniyor.';
    }
    final cut = source.split(RegExp(r'[.!?]')).first.trim();
    final clean = cut.isEmpty ? source : cut;
    return clean.length > 140 ? '${clean.substring(0, 140).trim()}...' : clean;
  }

  String _extractSkySummary(Map<String, dynamic> map) {
    final summary = (map['summary_tr'] ?? '').toString().trim();
    if (summary.isNotEmpty) {
      return summary;
    }
    final hero = _asMap(map['hero']);
    return (hero['summary_tr'] ?? '').toString().trim();
  }

  List<_SkyFeedItemData> _extractSkyFeedItems(Map<String, dynamic> map) {
    final items = map['items'];
    if (items is! List) {
      return const <_SkyFeedItemData>[];
    }
    return items
        .whereType<Map>()
        .map(
          (item) => _SkyFeedItemData.fromMap(Map<String, dynamic>.from(item)),
        )
        .where((item) => item.title.isNotEmpty && item.summary.isNotEmpty)
        .toList();
  }

  Map<String, dynamic> _asMap(dynamic data) {
    if (data == null) {
      return <String, dynamic>{};
    }
    if (data is Map<String, dynamic>) {
      return data;
    }
    if (data is Map) {
      return Map<String, dynamic>.from(data);
    }
    if (data is String) {
      try {
        final decoded = jsonDecode(data);
        if (decoded is Map) {
          return Map<String, dynamic>.from(decoded);
        }
      } catch (_) {}
    }
    return <String, dynamic>{};
  }

  String _extractNatalSummary(Map<String, dynamic> map) {
    final pub = map['public'];
    if (pub is Map) {
      final ui = pub['core_story_ui'];
      if (ui is Map && (ui['text'] ?? '').toString().trim().isNotEmpty) {
        return (ui['text'] ?? '').toString().trim();
      }
      if ((pub['core_story'] ?? '').toString().trim().isNotEmpty) {
        return (pub['core_story'] ?? '').toString();
      }
    }
    final directUi = map['core_story_ui'];
    if (directUi is Map &&
        (directUi['text'] ?? '').toString().trim().isNotEmpty) {
      return (directUi['text'] ?? '').toString().trim();
    }
    final direct = (map['core_story'] ?? '').toString().trim();
    if (direct.isNotEmpty) {
      return direct;
    }
    return (map['summary'] ?? map['narrative_text'] ?? '').toString().trim();
  }

  String _extractPlanetSign(Map<String, dynamic> map, String planetName) {
    final targets = <String>{
      planetName.toLowerCase(),
      if (planetName.toLowerCase() == 'ascendant') ...{'ascendant', 'asc'},
    };

    for (final scope in _natalScopes(map)) {
      final planets = scope['planets'];
      if (planets is List) {
        for (final raw in planets) {
          if (raw is! Map) {
            continue;
          }
          final name = (raw['planet'] ?? raw['name'] ?? raw['body'] ?? '')
              .toString()
              .toLowerCase();
          if (!targets.contains(name)) {
            continue;
          }
          final sign = (raw['sign'] ?? raw['zodiac_sign'] ?? '')
              .toString()
              .trim();
          if (sign.isNotEmpty) {
            return sign;
          }
        }
      }

      final signMap = scope['planet_signs'] ?? scope['signs'];
      if (signMap is Map) {
        for (final entry in signMap.entries) {
          final key = entry.key.toString().toLowerCase();
          if (!targets.contains(key)) {
            continue;
          }
          final sign = entry.value.toString().trim();
          if (sign.isNotEmpty) {
            return sign;
          }
        }
      }
    }
    return '—';
  }

  String _extractRisingSign(Map<String, dynamic> map) {
    final fromPlanet = _extractPlanetSign(map, 'Ascendant');
    if (fromPlanet != '—') {
      return fromPlanet;
    }
    for (final scope in _natalScopes(map)) {
      final angles = scope['angles'];
      if (angles is Map) {
        final sign = (angles['ascendant_sign'] ?? angles['asc_sign'] ?? '')
            .toString()
            .trim();
        if (sign.isNotEmpty) {
          return sign;
        }
      }
    }
    return '—';
  }

  List<Map<String, dynamic>> _natalScopes(Map<String, dynamic> map) {
    final scopes = <Map<String, dynamic>>[map];
    final pub = _asMap(map['public']);
    if (pub.isNotEmpty) {
      scopes.add(pub);
    }
    final metaInfo = _asMap(map['meta_info']);
    if (metaInfo.isNotEmpty) {
      scopes.add(metaInfo);
    }
    return scopes;
  }

  String _toTrSign(String raw) {
    const signs = <String, String>{
      'aries': 'Koc',
      'taurus': 'Boga',
      'gemini': 'Ikizler',
      'cancer': 'Yengec',
      'leo': 'Aslan',
      'virgo': 'Basak',
      'libra': 'Terazi',
      'scorpio': 'Akrep',
      'sagittarius': 'Yay',
      'capricorn': 'Oglak',
      'aquarius': 'Kova',
      'pisces': 'Balik',
      'koc': 'Koc',
      'koç': 'Koc',
      'boga': 'Boga',
      'boğa': 'Boga',
      'yengec': 'Yengec',
      'yengeç': 'Yengec',
      'basak': 'Basak',
      'başak': 'Basak',
      'ikizler': 'Ikizler',
      'terazi': 'Terazi',
      'akrep': 'Akrep',
      'yay': 'Yay',
      'oglak': 'Oglak',
      'oğlak': 'Oglak',
      'kova': 'Kova',
      'balik': 'Balik',
      'balık': 'Balik',
    };
    final key = raw.trim().toLowerCase();
    return signs[key] ?? (raw.trim().isEmpty ? '—' : raw.trim());
  }

  String _normalizeBirthTime(String raw) {
    final value = raw.trim();
    if (value.isEmpty) {
      return '12:00';
    }
    final parts = value.split(':');
    if (parts.length >= 2) {
      final hour = (int.tryParse(parts[0]) ?? 12).clamp(0, 23);
      final minute = (int.tryParse(parts[1]) ?? 0).clamp(0, 59);
      return '${hour.toString().padLeft(2, '0')}:${minute.toString().padLeft(2, '0')}';
    }
    return value;
  }
}

class _HomeWeekItemData {
  const _HomeWeekItemData({
    required this.index,
    required this.date,
    required this.weekdayLabel,
    required this.dayNumber,
    required this.isToday,
    required this.isSelected,
    required this.isHighlighted,
    required this.accent,
    required this.card,
    required this.dayMeta,
  });

  final int index;
  final DateTime date;
  final String weekdayLabel;
  final int dayNumber;
  final bool isToday;
  final bool isSelected;
  final bool isHighlighted;
  final Color accent;
  final EventCardDto? card;
  final NarrativeCalendarDay? dayMeta;
}

class _HomeReferenceHeader extends StatelessWidget {
  const _HomeReferenceHeader({
    required this.displayName,
    required this.dateLabel,
    required this.onActionTap,
  });

  final String displayName;
  final String dateLabel;
  final VoidCallback onActionTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final firstName = displayName.trim().split(RegExp(r'\s+')).first.trim();
    final l10n = context.l10n;
    final greetingName = firstName.isEmpty
        ? l10n.homeGreetingFallbackName
        : firstName;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.homeGreeting(greetingName),
                  style: profile.typography.card.copyWith(
                    color: profile.colors.text,
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  l10n.homeTodayLabel(dateLabel),
                  style: profile.typography.bodyCompact.copyWith(
                    color: profile.colors.textLight,
                  ),
                ),
              ],
            ),
          ),
          _HomeReferenceActionButton(
            onTap: onActionTap,
            isDark: isDark,
            child: JoviaUiIcon(
              asset: JoviaUiAsset.menuStack,
              size: 18,
              color: isDark ? Colors.white : const Color(0xFF16141A),
            ),
          ),
        ],
      ),
    );
  }
}

class _HomeReferenceActionButton extends StatelessWidget {
  const _HomeReferenceActionButton({
    required this.child,
    required this.onTap,
    required this.isDark,
  });

  final Widget child;
  final VoidCallback onTap;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: isDark
          ? Colors.white.withValues(alpha: 0.06)
          : Colors.white.withValues(alpha: 0.72),
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: isDark
                  ? Colors.white.withValues(alpha: 0.12)
                  : Colors.black.withValues(alpha: 0.06),
            ),
          ),
          child: Center(child: child),
        ),
      ),
    );
  }
}

class _HomeReferenceHeroCard extends StatelessWidget {
  const _HomeReferenceHeroCard({
    required this.title,
    required this.body,
    required this.prompt,
    required this.weekItems,
    required this.starRotation,
    required this.onSelectDay,
    required this.onOpen,
    required this.footer,
  });

  final String title;
  final String body;
  final String prompt;
  final List<_HomeWeekItemData> weekItems;
  final Animation<double> starRotation;
  final ValueChanged<_HomeWeekItemData> onSelectDay;
  final VoidCallback onOpen;
  final Widget footer;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final labelStyle = profile.typography.monoEyebrow.copyWith(
      color: profile.colors.textLight,
      fontSize: 10.8,
      letterSpacing: 1.6,
    );
    final titleStyle = profile.typography.editorialHeadline.copyWith(
      color: profile.colors.text,
      fontSize: 25,
      height: 1.08,
    );
    final bodyStyle = profile.typography.bodyCompact.copyWith(
      color: profile.colors.textLight,
      fontSize: 13,
      height: 1.42,
    );
    final promptStyle = profile.typography.bodyCompact.copyWith(
      color: profile.colors.textLight,
      fontSize: 13,
      height: 1.34,
    );
    final surfaceGradient = isDark
        ? <Color>[
            Color.alphaBlend(
              profile.colors.primary.withValues(alpha: 0.16),
              profile.colors.heroBase,
            ),
            Color.alphaBlend(
              Colors.white.withValues(alpha: 0.02),
              profile.colors.surface,
            ),
          ]
        : const <Color>[Color(0xFFFFFFFF), Color(0xFFF8F9FC)];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: TweenAnimationBuilder<double>(
        tween: Tween<double>(begin: 0, end: 1),
        duration: const Duration(milliseconds: 650),
        curve: Curves.easeOutCubic,
        builder: (context, value, child) {
          return Opacity(
            opacity: value,
            child: Transform.translate(
              offset: Offset(0, 18 * (1 - value)),
              child: child,
            ),
          );
        },
        child: DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(34),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: surfaceGradient,
            ),
            border: Border.all(color: profile.colors.strokeSoft),
            boxShadow: [
              BoxShadow(
                color: profile.colors.lavender.withValues(
                  alpha: isDark ? 0.14 : 0.18,
                ),
                blurRadius: 34,
                offset: const Offset(0, 20),
                spreadRadius: -20,
              ),
            ],
          ),
          child: JoviaSurfaceCard(
            radius: 34,
            backgroundColor: isDark
                ? Colors.transparent
                : const Color(0xFFFFFFFF),
            borderColor: isDark
                ? Colors.transparent
                : profile.colors.strokeSoft.withValues(alpha: 0.72),
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 16),
            shadow: false,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(
                  height: _homeHeroSlotHeight(labelStyle, 1),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      RotationTransition(
                        turns: starRotation,
                        child: Text(
                          '✦',
                          style: labelStyle.copyWith(fontSize: 10),
                        ),
                      ),
                      const SizedBox(width: 5),
                      Expanded(
                        child: _HomeHeroAnimatedText(
                          text: context.l10n.homeDailyTransitLabel,
                          textStyle: labelStyle,
                          maxLines: 1,
                          delay: Duration.zero,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 10),
                SizedBox(
                  height: _homeHeroSlotHeight(titleStyle, 3),
                  child: _HomeHeroAnimatedText(
                    text: title,
                    textStyle: titleStyle,
                    maxLines: 3,
                    delay: const Duration(milliseconds: 34),
                  ),
                ),
                const SizedBox(height: 10),
                SizedBox(
                  height: _homeHeroSlotHeight(bodyStyle, 4),
                  child: _HomeHeroAnimatedText(
                    text: body,
                    textStyle: bodyStyle,
                    maxLines: 4,
                    delay: const Duration(milliseconds: 68),
                  ),
                ),
                const SizedBox(height: 14),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.fromLTRB(14, 12, 12, 12),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(22),
                    color: isDark
                        ? Colors.white.withValues(alpha: 0.04)
                        : Colors.white,
                    border: Border.all(
                      color: profile.colors.strokeSoft,
                      width: 1,
                    ),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: SizedBox(
                          height: _homeHeroSlotHeight(promptStyle, 2),
                          child: _HomeHeroAnimatedText(
                            text: prompt,
                            textStyle: promptStyle,
                            maxLines: 2,
                            delay: const Duration(milliseconds: 92),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      _HomeHeroButton(onTap: onOpen),
                    ],
                  ),
                ),
                const SizedBox(height: 14),
                footer,
                const SizedBox(height: 18),
                _HomeWeekStrip(
                  items: weekItems,
                  onSelectItem: onSelectDay,
                  onOpenSelected: onOpen,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _HomeHeroButton extends StatelessWidget {
  const _HomeHeroButton({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 11),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(999),
            color: isDark
                ? Colors.white.withValues(alpha: 0.92)
                : profile.colors.warmAccent,
            border: Border.all(
              color: isDark
                  ? Colors.white.withValues(alpha: 0.1)
                  : profile.colors.chipBorder,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                context.l10n.commonOpen,
                style: profile.typography.buttonLabel.copyWith(
                  color: isDark
                      ? const Color(0xFF17131E)
                      : profile.colors.heroText,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(width: 6),
              Icon(
                Icons.arrow_outward_rounded,
                size: 14,
                color: isDark
                    ? const Color(0xFF17131E)
                    : profile.colors.heroText,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _HomeWeekStrip extends StatelessWidget {
  const _HomeWeekStrip({
    required this.items,
    required this.onSelectItem,
    required this.onOpenSelected,
  });

  final List<_HomeWeekItemData> items;
  final ValueChanged<_HomeWeekItemData> onSelectItem;
  final VoidCallback onOpenSelected;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          for (var index = 0; index < items.length; index++) ...[
            _HomeWeekDayChip(
              item: items[index],
              onTap: () {
                if (items[index].isSelected) {
                  onOpenSelected();
                  return;
                }
                onSelectItem(items[index]);
              },
            ),
            if (index != items.length - 1) const SizedBox(width: 10),
          ],
        ],
      ),
    );
  }
}

class _HomeWeekDayChip extends StatelessWidget {
  const _HomeWeekDayChip({required this.item, this.onTap});

  final _HomeWeekItemData item;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final profile = context.profileTheme;
    final child = AnimatedContainer(
      duration: const Duration(milliseconds: 240),
      curve: Curves.easeOutCubic,
      width: 54,
      padding: const EdgeInsets.symmetric(vertical: 9),
      decoration: BoxDecoration(
        color: item.isSelected
            ? (isDark
                  ? Colors.white.withValues(alpha: 0.96)
                  : profile.colors.warmAccent)
            : item.isToday
            ? (isDark
                  ? Colors.white.withValues(alpha: 0.08)
                  : profile.colors.surface)
            : (isDark
                  ? Colors.white.withValues(alpha: 0.05)
                  : profile.colors.surface.withValues(alpha: 0.82)),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: item.isSelected
              ? item.accent.withValues(alpha: 0.52)
              : item.isToday
              ? item.accent.withValues(alpha: 0.34)
              : (isDark
                    ? profile.colors.strokeSoft
                    : Colors.black.withValues(alpha: 0.05)),
        ),
        boxShadow: item.isSelected
            ? [
                BoxShadow(
                  color: item.accent.withValues(alpha: 0.24),
                  blurRadius: 20,
                  offset: const Offset(0, 12),
                  spreadRadius: -12,
                ),
              ]
            : item.isToday
            ? [
                BoxShadow(
                  color: item.accent.withValues(alpha: 0.14),
                  blurRadius: 18,
                  offset: const Offset(0, 10),
                  spreadRadius: -14,
                ),
              ]
            : null,
      ),
      child: Column(
        children: [
          Text(
            item.weekdayLabel,
            style: context.profileTheme.typography.micro.copyWith(
              color: item.isSelected
                  ? (isDark ? const Color(0xFF16131D) : profile.colors.heroText)
                  : item.isToday
                  ? item.accent.withValues(alpha: isDark ? 0.88 : 0.94)
                  : (isDark
                        ? Colors.white.withValues(alpha: 0.76)
                        : profile.colors.textLight),
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '${item.dayNumber}',
            style: context.profileTheme.typography.body.copyWith(
              color: item.isSelected
                  ? (isDark ? const Color(0xFF16131D) : profile.colors.heroText)
                  : (isDark ? Colors.white : profile.colors.text),
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          Container(
            width: item.isSelected ? 12 : 6,
            height: 6,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(999),
              color: item.isHighlighted
                  ? item.accent
                  : item.isToday
                  ? item.accent.withValues(alpha: 0.38)
                  : Colors.transparent,
            ),
          ),
        ],
      ),
    );
    if (onTap == null) {
      return child;
    }
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: child,
    );
  }
}

double _homeHeroSlotHeight(TextStyle style, int lines) {
  final fontSize = style.fontSize ?? 14;
  final lineHeight = style.height ?? 1.2;
  return (fontSize * lineHeight * lines) + 2;
}

class _HomeHeroAnimatedText extends StatefulWidget {
  const _HomeHeroAnimatedText({
    required this.text,
    required this.textStyle,
    required this.maxLines,
    required this.delay,
  });

  final String text;
  final TextStyle textStyle;
  final int maxLines;
  final Duration delay;

  @override
  State<_HomeHeroAnimatedText> createState() => _HomeHeroAnimatedTextState();
}

class _HomeHeroAnimatedTextState extends State<_HomeHeroAnimatedText>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late String _currentText;
  String? _previousText;

  @override
  void initState() {
    super.initState();
    _currentText = widget.text;
    _controller =
        AnimationController(
          vsync: this,
          duration: const Duration(milliseconds: 320),
          value: 1,
        )..addStatusListener((status) {
          if (status == AnimationStatus.completed && mounted) {
            setState(() => _previousText = null);
          }
        });
  }

  @override
  void didUpdateWidget(covariant _HomeHeroAnimatedText oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.text == widget.text) {
      return;
    }
    _previousText = _currentText;
    _currentText = widget.text;
    _controller.forward(from: 0);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final previousText = _previousText;
    if (previousText == null) {
      return Align(
        alignment: Alignment.topLeft,
        child: _buildText(_currentText),
      );
    }

    final controllerDuration =
        _controller.duration ?? const Duration(milliseconds: 320);
    final delayFraction =
        widget.delay.inMilliseconds / controllerDuration.inMilliseconds;
    final outgoingEnd = (delayFraction + 0.44).clamp(0.0, 0.86);
    final incomingStart = (delayFraction + 0.16).clamp(0.0, 0.94);

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final outgoing = CurvedAnimation(
          parent: _controller,
          curve: Interval(
            delayFraction.clamp(0.0, 1.0),
            outgoingEnd.toDouble(),
            curve: Curves.easeIn,
          ),
        );
        final incoming = CurvedAnimation(
          parent: _controller,
          curve: Interval(
            incomingStart.toDouble(),
            1,
            curve: Curves.easeOutCubic,
          ),
        );
        return ClipRect(
          child: Stack(
            alignment: Alignment.topLeft,
            children: [
              if (previousText.isNotEmpty)
                Opacity(
                  opacity: 1 - outgoing.value,
                  child: Transform.translate(
                    offset: Offset(0, -10 * outgoing.value),
                    child: _buildText(previousText),
                  ),
                ),
              Opacity(
                opacity: incoming.value,
                child: Transform.translate(
                  offset: Offset(0, 12 * (1 - incoming.value)),
                  child: _buildText(_currentText),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildText(String value) {
    return Text(
      value,
      maxLines: widget.maxLines,
      overflow: TextOverflow.ellipsis,
      style: widget.textStyle,
    );
  }
}

class _HomeSectionLead extends StatelessWidget {
  const _HomeSectionLead({required this.title, required this.subtitle});

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: profile.typography.section.copyWith(
              color: profile.colors.text,
              fontSize: 28,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            subtitle,
            style: profile.typography.bodyCompact.copyWith(
              color: profile.colors.textLight,
            ),
          ),
        ],
      ),
    );
  }
}

class _HomeReferencePlanBoard extends StatelessWidget {
  const _HomeReferencePlanBoard({
    required this.activeCard,
    required this.dailyCards,
    required this.bulletin,
    required this.skyItem,
    required this.lineText,
    required this.loading,
    required this.onOpenActive,
    required this.onOpenCard,
    required this.onOpenSky,
    required this.onOpenCalendar,
  });

  final PeriodCardDto? activeCard;
  final List<PeriodCardDto> dailyCards;
  final _SkyBulletin bulletin;
  final _SkyFeedItemData? skyItem;
  final String lineText;
  final bool loading;
  final VoidCallback onOpenActive;
  final ValueChanged<PeriodCardDto> onOpenCard;
  final VoidCallback onOpenSky;
  final VoidCallback onOpenCalendar;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final compact = MediaQuery.of(context).size.width < 392;
    final skyTitle = skyItem?.title ?? l10n.homeCollectivePulse;
    final skyHook = skyItem?.hook.trim() ?? '';
    final skyBody = skyHook.isNotEmpty ? skyHook : bulletin.summary;
    final thirdCard = dailyCards.length > 1 ? dailyCards[1] : activeCard;
    final activeTimeHint = activeCard?.timeHint.trim() ?? '';
    final skyBadge = skyItem?.badge.trim() ?? '';
    final thirdTimeHint = thirdCard?.timeHint.trim() ?? '';
    final activeTitle = activeCard?.title.trim() ?? '';
    final activeSubtitle = activeCard?.subtitle.trim() ?? '';
    final activeSignature = activeCard?.eventCard?.signatureTr.trim() ?? '';
    final thirdTitle = thirdCard?.title.trim() ?? '';
    final thirdSubtitle = thirdCard?.subtitle.trim() ?? '';
    final activeMeta = _compactHomeMeta(
      activeTimeHint.isNotEmpty ? activeTimeHint : l10n.homePrimaryMeta,
    );
    final skyMeta = _compactHomeMeta(
      skyBadge.isNotEmpty ? skyBadge : l10n.homeCollectiveMeta,
    );
    final weekMeta = _compactHomeMeta(
      thirdTimeHint.isNotEmpty ? thirdTimeHint : l10n.homeWeekMeta,
    );

    if (loading && activeCard == null && dailyCards.isEmpty) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 32),
        child: Center(child: CircularProgressIndicator()),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: Column(
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                flex: compact ? 1 : 11,
                child: _HomeColorPlanCard(
                  title: activeTitle.isNotEmpty
                      ? activeTitle
                      : l10n.homeDayPlan,
                  metaTop: activeMeta,
                  body: activeSubtitle.isNotEmpty ? activeSubtitle : lineText,
                  footer: activeSignature.isNotEmpty
                      ? activeSignature
                      : l10n.homeGoToCalendar,
                  palette: const _HomeCardPalette.sunset(),
                  onTap: onOpenActive,
                  tall: true,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                flex: compact ? 1 : 9,
                child: Column(
                  children: [
                    _HomeColorPlanCard(
                      title: skyTitle,
                      metaTop: skyMeta,
                      body: skyBody,
                      footer:
                          skyItem?.previewChips.skip(1).take(2).join(' • ') ??
                          bulletin.chips.take(2).join(' • '),
                      palette: const _HomeCardPalette.sky(),
                      onTap: onOpenSky,
                    ),
                    const SizedBox(height: 12),
                    _HomeColorPlanCard(
                      title: thirdTitle.isNotEmpty
                          ? thirdTitle
                          : l10n.homeCalendarTitle,
                      metaTop: weekMeta,
                      body: thirdSubtitle.isNotEmpty
                          ? thirdSubtitle
                          : l10n.homeWeekFlowOpen,
                      footer: l10n.homeWeekView,
                      palette: const _HomeCardPalette.candy(),
                      onTap: thirdCard != null
                          ? () => onOpenCard(thirdCard)
                          : onOpenCalendar,
                      compact: true,
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _HomeReferenceTimingCard(
            title: l10n.homeWeeklyCalendar,
            body: l10n.homeWeeklyCalendarBody,
            onTap: onOpenCalendar,
          ),
        ],
      ),
    );
  }
}

class _HomeCardPalette {
  const _HomeCardPalette({
    required this.background,
    required this.foreground,
    required this.surface,
    required this.chip,
    required this.wash,
    required this.illustration,
  });

  const _HomeCardPalette.sunset()
    : background = const <Color>[Color(0xFFEFFFF0), Color(0xFFD8FF72)],
      foreground = const Color(0xFF1A1A14),
      surface = const Color(0xFFFFFFFF),
      chip = const Color(0xFFEAECEF),
      wash = JoviaColorAsset.wash08,
      illustration = JoviaIllustrationAsset.sunGrowth;

  const _HomeCardPalette.sky()
    : background = const <Color>[Color(0xFFF6F2FF), Color(0xFFE0D3FF)],
      foreground = const Color(0xFF1D1A27),
      surface = const Color(0xFFFFFFFF),
      chip = const Color(0xFFEAE6F5),
      wash = JoviaColorAsset.wash11,
      illustration = JoviaIllustrationAsset.planet;

  const _HomeCardPalette.candy()
    : background = const <Color>[Color(0xFFFFF1FB), Color(0xFFF2D5FF)],
      foreground = const Color(0xFF281A26),
      surface = const Color(0xFFFFFFFF),
      chip = const Color(0xFFEFE7F4),
      wash = JoviaColorAsset.wash09,
      illustration = JoviaIllustrationAsset.layers;

  final List<Color> background;
  final Color foreground;
  final Color surface;
  final Color chip;
  final JoviaColorAsset wash;
  final JoviaIllustrationAsset illustration;
}

class _HomeGalleryIllustrationPanel extends StatelessWidget {
  const _HomeGalleryIllustrationPanel({
    required this.palette,
    required this.height,
    this.compact = false,
  });

  final _HomeCardPalette palette;
  final double height;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final radius = compact ? 24.0 : 28.0;
    final illustrationSize = compact ? 62.0 : height * 0.7;
    return Container(
      height: height,
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(radius),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: palette.background,
        ),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(radius),
        child: Stack(
          children: [
            Positioned.fill(
              child: JoviaColorWash(
                asset: palette.wash,
                opacity: compact ? 0.18 : 0.24,
                alignment: Alignment.topCenter,
              ),
            ),
            Positioned(
              right: compact ? -10 : -6,
              top: compact ? -8 : -4,
              child: Container(
                width: compact ? 54 : 72,
                height: compact ? 54 : 72,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withValues(alpha: 0.22),
                ),
              ),
            ),
            Positioned(
              left: 0,
              right: 0,
              bottom: compact ? 2 : 6,
              child: Center(
                child: JoviaIllustrationAccent(
                  asset: palette.illustration,
                  width: illustrationSize,
                  height: illustrationSize,
                  opacity: 0.96,
                ),
              ),
            ),
            Positioned(
              left: compact ? 10 : 14,
              bottom: compact ? 10 : 14,
              child: Container(
                width: compact ? 16 : 24,
                height: 4,
                decoration: BoxDecoration(
                  color: profile.colors.surface.withValues(alpha: 0.85),
                  borderRadius: BorderRadius.circular(999),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HomeColorPlanCard extends StatelessWidget {
  const _HomeColorPlanCard({
    required this.title,
    required this.metaTop,
    required this.body,
    required this.footer,
    required this.palette,
    required this.onTap,
    this.tall = false,
    this.compact = false,
  });

  final String title;
  final String metaTop;
  final String body;
  final String footer;
  final _HomeCardPalette palette;
  final VoidCallback onTap;
  final bool tall;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final panelHeight = tall
        ? 164.0
        : compact
        ? 84.0
        : 104.0;
    final minHeight = tall
        ? 292.0
        : compact
        ? 156.0
        : 178.0;
    final titleStyle = profile.typography.card.copyWith(
      color: palette.foreground,
      fontSize: tall
          ? 22
          : compact
          ? 16.5
          : 18.5,
      height: 1.12,
      fontWeight: FontWeight.w600,
    );
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0, end: 1),
      duration: Duration(milliseconds: tall ? 620 : 700),
      curve: Curves.easeOutCubic,
      builder: (context, value, child) {
        return Opacity(
          opacity: value,
          child: Transform.translate(
            offset: Offset(0, 16 * (1 - value)),
            child: child,
          ),
        );
      },
      child: JoviaPressable(
        onTap: onTap,
        borderRadius: BorderRadius.circular(32),
        child: Container(
          constraints: BoxConstraints(minHeight: minHeight),
          padding: EdgeInsets.all(compact ? 12 : 14),
          decoration: BoxDecoration(
            color: palette.surface,
            borderRadius: BorderRadius.circular(32),
            border: Border.all(color: palette.chip.withValues(alpha: 0.96)),
            boxShadow: [
              BoxShadow(
                color: palette.background.last.withValues(alpha: 0.16),
                blurRadius: 26,
                offset: const Offset(0, 16),
                spreadRadius: -20,
              ),
            ],
          ),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final canUseFlexibleGap = constraints.hasBoundedHeight;
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  _HomeGalleryIllustrationPanel(
                    palette: palette,
                    height: panelHeight,
                    compact: compact,
                  ),
                  SizedBox(height: compact ? 12 : 14),
                  Text(
                    turkishToUpper(metaTop.trim().isEmpty ? 'Şimdi' : metaTop),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: profile.typography.monoEyebrow.copyWith(
                      color: palette.foreground.withValues(alpha: 0.62),
                      fontSize: 10.8,
                      letterSpacing: 1.5,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    title,
                    maxLines: compact ? 2 : 3,
                    overflow: TextOverflow.ellipsis,
                    style: titleStyle,
                  ),
                  if (body.trim().isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      body,
                      maxLines: tall
                          ? 3
                          : compact
                          ? 2
                          : 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.bodyCompact.copyWith(
                        color: palette.foreground.withValues(alpha: 0.78),
                        fontSize: compact ? 12.8 : 13.4,
                        height: 1.45,
                      ),
                    ),
                  ],
                  if (canUseFlexibleGap) const Spacer(),
                  const SizedBox(height: 14),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          footer,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: profile.typography.metaSoft.copyWith(
                            color: palette.foreground.withValues(alpha: 0.82),
                            fontWeight: FontWeight.w600,
                            fontSize: compact ? 11.8 : 12.4,
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Icon(
                        Icons.arrow_outward_rounded,
                        color: palette.foreground,
                        size: 18,
                      ),
                    ],
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}

String _compactHomeMeta(String raw) {
  final trimmed = raw.trim();
  if (trimmed.isEmpty) {
    return trimmed;
  }
  final semicolonIndex = trimmed.indexOf(';');
  final shortened = semicolonIndex > 0
      ? trimmed.substring(0, semicolonIndex).trim()
      : trimmed;
  if (shortened.length <= 18) {
    return shortened;
  }
  return '${shortened.substring(0, 18).trim()}...';
}

class _HomeReferenceTimingCard extends StatelessWidget {
  const _HomeReferenceTimingCard({
    required this.title,
    required this.body,
    required this.onTap,
  });

  final String title;
  final String body;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(26),
          child: Container(
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(26),
              color: isDark
                  ? Colors.white.withValues(alpha: 0.06)
                  : profile.colors.surface,
              border: Border.all(
                color: isDark
                    ? Colors.white.withValues(alpha: 0.08)
                    : profile.colors.strokeSoft,
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: profile.typography.card.copyWith(
                          color: profile.colors.text,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        body,
                        style: profile.typography.bodyCompact.copyWith(
                          color: profile.colors.textLight,
                          height: 1.45,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: profile.colors.primary.withValues(alpha: 0.34),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(
                    Icons.calendar_month_rounded,
                    color: profile.colors.heroText,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _HomeAuraHeader extends StatelessWidget {
  const _HomeAuraHeader({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    return Container(
      constraints: const BoxConstraints(minHeight: 170),
      decoration: BoxDecoration(
        color: colors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: colors.strokeSoft, width: 1.5),
        boxShadow: [profile.shadows.cardShadow],
      ),
      child: Stack(
        children: [
          Positioned(
            right: 10,
            top: 10,
            child: Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: colors.lavender.withValues(alpha: 0.22),
                borderRadius: BorderRadius.circular(36),
              ),
            ),
          ),
          Padding(padding: const EdgeInsets.fromLTRB(0, 0, 0, 0), child: child),
        ],
      ),
    );
  }
}

class _HomeSignStateRow extends StatelessWidget {
  const _HomeSignStateRow({
    required this.sunSign,
    required this.moonSign,
    required this.risingSign,
  });

  final String sunSign;
  final String moonSign;
  final String risingSign;

  @override
  Widget build(BuildContext context) {
    final chips = <String>[
      if (sunSign.trim().isNotEmpty && sunSign.trim() != '—') 'Gunes $sunSign',
      if (moonSign.trim().isNotEmpty && moonSign.trim() != '—') 'Ay $moonSign',
      if (risingSign.trim().isNotEmpty && risingSign.trim() != '—')
        'Yukselen $risingSign',
    ];

    if (chips.isEmpty) {
      return const SizedBox.shrink();
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          for (var index = 0; index < chips.length; index++) ...[
            JoviaMetaPill(label: chips[index]),
            if (index != chips.length - 1) const SizedBox(width: 8),
          ],
        ],
      ),
    );
  }
}

class _HomeOpeningHeroCard extends StatelessWidget {
  const _HomeOpeningHeroCard({
    required this.title,
    required this.body,
    required this.prompt,
    required this.onOpen,
    required this.footer,
  });

  final String title;
  final String body;
  final String prompt;
  final VoidCallback onOpen;
  final Widget footer;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return _HomePosterShell(
      padding: const EdgeInsets.all(12),
      child: _HomePosterStage(
        wash: JoviaColorAsset.wash03,
        primaryIllustration: JoviaIllustrationAsset.planet,
        secondaryIllustration: JoviaIllustrationAsset.shape,
        minHeight: 548,
        primaryTop: 36,
        primaryRight: 52,
        primaryWidth: 184,
        primaryHeight: 184,
        secondaryTop: 140,
        secondaryLeft: -34,
        secondaryWidth: 86,
        secondaryHeight: 86,
        washOpacity: 0.055,
        padding: const EdgeInsets.fromLTRB(22, 20, 22, 22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 196),
            Text(
              turkishToUpper(context.l10n.homeHeroOpening),
              style: profile.typography.monoEyebrow.copyWith(
                color: profile.colors.textLight,
                fontSize: 11.5,
                letterSpacing: 1.9,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              title,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.editorialHeadline.copyWith(
                color: profile.colors.text,
                fontSize: 34,
                height: 1.02,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              body,
              maxLines: 4,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.bodyReading.copyWith(
                color: profile.colors.textLight,
                fontSize: 15.6,
                height: 1.6,
              ),
            ),
            const SizedBox(height: 18),
            JoviaSurfaceCard(
              backgroundColor: isDark
                  ? const Color(0xFF090807)
                  : Color.alphaBlend(
                      profile.colors.warmAccent.withValues(alpha: 0.08),
                      profile.colors.panelSoft,
                    ),
              borderColor: profile.colors.warmAccent.withValues(alpha: 0.16),
              radius: 30,
              padding: const EdgeInsets.fromLTRB(18, 16, 16, 16),
              shadow: false,
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          context.l10n.homeHeroQuestionTitle,
                          style: profile.typography.monoEyebrow.copyWith(
                            color: profile.colors.textLight,
                            fontSize: 11.5,
                            letterSpacing: 1.7,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          prompt,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: profile.typography.bodyCompact.copyWith(
                            color: profile.colors.text,
                            fontWeight: FontWeight.w600,
                            height: 1.42,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 14),
                  MinimalCTAButton(
                    label: context.l10n.commonOpen,
                    emphasized: true,
                    onTap: onOpen,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            footer,
          ],
        ),
      ),
    );
  }
}

class _HomePosterShell extends StatelessWidget {
  const _HomePosterShell({
    required this.child,
    this.padding = const EdgeInsets.all(12),
    this.radius = 34,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final double radius;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return JoviaSurfaceCard(
      backgroundColor: isDark
          ? const Color(0xFF030303)
          : Color.alphaBlend(
              profile.colors.primary.withValues(alpha: 0.05),
              profile.colors.panelStrong,
            ),
      borderColor: profile.colors.strokeSoft,
      radius: radius,
      padding: padding,
      child: child,
    );
  }
}

class _HomePosterStage extends StatelessWidget {
  const _HomePosterStage({
    required this.child,
    required this.wash,
    required this.primaryIllustration,
    this.radius = 28,
    this.height,
    this.minHeight,
    this.primaryRight = -18,
    this.primaryTop,
    this.primaryWidth = 148,
    this.primaryHeight = 148,
    this.secondaryIllustration,
    this.secondaryLeft = -24,
    this.secondaryTop,
    this.secondaryWidth = 80,
    this.secondaryHeight = 80,
    this.washOpacity = 0.05,
    this.padding = const EdgeInsets.all(18),
  });

  final Widget child;
  final JoviaColorAsset wash;
  final JoviaIllustrationAsset primaryIllustration;
  final double radius;
  final double? height;
  final double? minHeight;
  final double primaryRight;
  final double? primaryTop;
  final double primaryWidth;
  final double primaryHeight;
  final JoviaIllustrationAsset? secondaryIllustration;
  final double secondaryLeft;
  final double? secondaryTop;
  final double secondaryWidth;
  final double secondaryHeight;
  final double washOpacity;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final secondaryAsset = secondaryIllustration;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      height: height,
      constraints: BoxConstraints(minHeight: minHeight ?? 0),
      decoration: BoxDecoration(
        color: isDark
            ? const Color(0xFF050505)
            : Color.alphaBlend(
                Colors.white.withValues(alpha: 0.3),
                profile.colors.heroBase,
              ),
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(radius - 1),
        child: Stack(
          children: [
            Positioned.fill(
              child: JoviaColorWash(
                asset: wash,
                opacity: washOpacity * 0.5,
                alignment: Alignment.topCenter,
              ),
            ),
            Positioned(
              right: primaryRight,
              top: primaryTop,
              child: JoviaIllustrationAccent(
                asset: primaryIllustration,
                width: primaryWidth,
                height: primaryHeight,
                opacity: 0.92,
              ),
            ),
            if (secondaryAsset != null)
              Positioned(
                left: secondaryLeft,
                top: secondaryTop,
                child: JoviaIllustrationAccent(
                  asset: secondaryAsset,
                  width: secondaryWidth,
                  height: secondaryHeight,
                  opacity: 0.1,
                ),
              ),
            Padding(padding: padding, child: child),
          ],
        ),
      ),
    );
  }
}

class _HomeEditorialLine extends StatelessWidget {
  const _HomeEditorialLine({required this.label, required this.text});

  final String label;
  final String text;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: JoviaSurfaceCard(
        radius: 30,
        padding: const EdgeInsets.fromLTRB(20, 22, 20, 24),
        backgroundColor: isDark
            ? profile.colors.panelStrong
            : Color.alphaBlend(
                Colors.white.withValues(alpha: 0.56),
                profile.colors.panelSoft,
              ),
        borderColor: profile.colors.strokeSoft,
        shadow: false,
        child: Column(
          children: [
            Text(
              turkishToUpper(label),
              textAlign: TextAlign.center,
              style: profile.typography.monoEyebrow.copyWith(
                color: profile.colors.textLight,
                fontSize: 11.5,
                letterSpacing: 1.9,
              ),
            ),
            const SizedBox(height: 12),
            Container(width: 92, height: 1, color: profile.colors.separator),
            const SizedBox(height: 14),
            Text(
              text,
              textAlign: TextAlign.center,
              maxLines: 4,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.section.copyWith(
                color: profile.colors.text,
                fontSize: 26,
                height: 1.2,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HomeDailyUpdateStrip extends StatelessWidget {
  const _HomeDailyUpdateStrip({
    required this.cards,
    required this.loading,
    required this.onOpen,
  });

  final List<PeriodCardDto> cards;
  final bool loading;
  final ValueChanged<PeriodCardDto> onOpen;

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const SizedBox(
        height: 132,
        child: Center(child: CircularProgressIndicator()),
      );
    }
    if (cards.isEmpty) {
      return const SizedBox(
        height: 200,
        child: JoviaSurfaceCard(
          child: Align(
            alignment: Alignment.centerLeft,
            child: Text('Daily update strip su an bos.'),
          ),
        ),
      );
    }

    return SizedBox(
      height: 246,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: cards.length,
        separatorBuilder: (context, index) => const SizedBox(width: 12),
        itemBuilder: (context, index) {
          final card = cards[index];
          final meta = card.timeHint.trim().isNotEmpty
              ? card.timeHint.trim()
              : context.l10n.homeTimingMeta;
          final subtitle = card.subtitle.trim().isNotEmpty
              ? card.subtitle.trim()
              : context.l10n.homeOpenDetail;
          final textMaxWidth = index == 1 ? 154.0 : 162.0;
          final accentAsset = <JoviaIllustrationAsset>[
            JoviaIllustrationAsset.planet,
            JoviaIllustrationAsset.sunMountain,
            JoviaIllustrationAsset.layers,
          ][index % 3];
          return SizedBox(
            width: 272,
            child: JoviaPressable(
              onTap: () => onOpen(card),
              borderRadius: BorderRadius.circular(20),
              child: _HomePosterShell(
                padding: const EdgeInsets.all(10),
                radius: 28,
                child: _HomePosterStage(
                  wash: index.isEven
                      ? JoviaColorAsset.wash14
                      : JoviaColorAsset.wash05,
                  primaryIllustration: accentAsset,
                  secondaryIllustration: JoviaIllustrationAsset.shape,
                  primaryTop: 14,
                  primaryRight: index == 1 ? -2 : 8,
                  primaryWidth: index == 1 ? 108 : 92,
                  primaryHeight: index == 1 ? 108 : 92,
                  secondaryTop: 70,
                  secondaryLeft: -26,
                  secondaryWidth: 70,
                  secondaryHeight: 70,
                  radius: 22,
                  height: 224,
                  minHeight: 224,
                  washOpacity: 0.05,
                  padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        turkishToUpper(meta),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: context.profileTheme.typography.monoEyebrow
                            .copyWith(
                              color: context.profileTheme.colors.textLight,
                              fontSize: 11.2,
                              letterSpacing: 1.65,
                            ),
                      ),
                      const SizedBox(height: 8),
                      const SizedBox(height: 24),
                      ConstrainedBox(
                        constraints: BoxConstraints(maxWidth: textMaxWidth),
                        child: Text(
                          card.title.isNotEmpty ? card.title : 'Aktif akis',
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: context.profileTheme.typography.section
                              .copyWith(
                                color: context.profileTheme.colors.text,
                                fontSize: 18.4,
                                height: 1.12,
                              ),
                        ),
                      ),
                      const SizedBox(height: 10),
                      ConstrainedBox(
                        constraints: BoxConstraints(maxWidth: textMaxWidth),
                        child: Text(
                          subtitle,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: context.profileTheme.typography.metaSoft
                              .copyWith(
                                color: context.profileTheme.colors.textLight,
                                height: 1.34,
                              ),
                        ),
                      ),
                      const Spacer(),
                      IgnorePointer(
                        child: Align(
                          alignment: Alignment.centerLeft,
                          child: MinimalCTAButton(
                            label: context.l10n.commonOpen,
                            emphasized: true,
                            onTap: null,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _HomeActiveThemeCard extends StatelessWidget {
  const _HomeActiveThemeCard({required this.card, required this.onOpen});

  final PeriodCardDto? card;
  final VoidCallback onOpen;

  @override
  Widget build(BuildContext context) {
    final titleValue = card?.title.trim() ?? '';
    final subtitleValue = card?.subtitle.trim() ?? '';
    final signatureValue = card?.eventCard?.signatureTr.trim() ?? '';
    final title = titleValue.isNotEmpty
        ? titleValue
        : context.l10n.homeActiveThemePending;
    final body = subtitleValue.isNotEmpty
        ? subtitleValue
        : context.l10n.homeActiveThemeBody;
    final timeHint = card?.timeHint.trim() ?? '';

    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 430;
        final metaChips = <String>[
          if (timeHint.isNotEmpty) timeHint,
          if (signatureValue.isNotEmpty) signatureValue,
        ].take(compact ? 1 : 2).toList(growable: false);

        final cta = MinimalCTAButton(
          label: context.l10n.homeOpenTheme,
          emphasized: true,
          onTap: onOpen,
        );

        return _HomePosterShell(
          child: _HomePosterStage(
            wash: JoviaColorAsset.wash14,
            primaryIllustration: compact
                ? JoviaIllustrationAsset.planet
                : JoviaIllustrationAsset.sunMountain,
            secondaryIllustration: JoviaIllustrationAsset.shape,
            primaryTop: 18,
            primaryRight: compact ? -10 : 14,
            primaryWidth: compact ? 132 : 170,
            primaryHeight: compact ? 132 : 170,
            secondaryTop: 104,
            secondaryLeft: -24,
            secondaryWidth: 68,
            secondaryHeight: 68,
            radius: 28,
            minHeight: compact ? 292 : 336,
            washOpacity: 0.06,
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  timeHint.isNotEmpty
                      ? turkishToUpper(timeHint)
                      : turkishToUpper(context.l10n.homeNowActive),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: context.profileTheme.typography.monoEyebrow.copyWith(
                    color: context.profileTheme.colors.textLight,
                    fontSize: 11.5,
                    letterSpacing: 1.8,
                  ),
                ),
                SizedBox(height: compact ? 58 : 72),
                Text(
                  title,
                  maxLines: compact ? 2 : 2,
                  overflow: TextOverflow.ellipsis,
                  style: context.profileTheme.typography.editorialHeadline
                      .copyWith(
                        color: context.profileTheme.colors.text,
                        fontWeight: FontWeight.w600,
                        fontSize: compact ? 28 : 34,
                        height: 1.04,
                      ),
                ),
                const SizedBox(height: 12),
                Text(
                  body,
                  maxLines: compact ? 3 : 3,
                  overflow: TextOverflow.ellipsis,
                  style: context.profileTheme.typography.bodyReading.copyWith(
                    color: context.profileTheme.colors.textLight,
                    fontSize: 15.4,
                    height: 1.56,
                  ),
                ),
                if (metaChips.isNotEmpty) ...[
                  const SizedBox(height: 14),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        for (
                          var index = 0;
                          index < metaChips.length;
                          index++
                        ) ...[
                          JoviaMetaPill(label: metaChips[index]),
                          if (index != metaChips.length - 1)
                            const SizedBox(width: 8),
                        ],
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 18),
                Align(alignment: Alignment.centerLeft, child: cta),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _HomeCollectivePulseCard extends StatelessWidget {
  const _HomeCollectivePulseCard({
    required this.bulletin,
    required this.card,
    required this.skyItem,
    required this.onOpenThread,
  });

  final _SkyBulletin bulletin;
  final PeriodCardDto? card;
  final _SkyFeedItemData? skyItem;
  final VoidCallback onOpenThread;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final chips =
        skyItem?.previewChips.take(3).toList(growable: false) ??
        bulletin.chips.take(2).toList(growable: false);
    final cardTitle = card?.title.trim() ?? '';
    final fallbackCard = card;
    final blurb =
        skyItem?.summary ??
        (fallbackCard == null
            ? bulletin.summary
            : _blurbFromCard(fallbackCard));
    final title =
        skyItem?.title ??
        (cardTitle.isNotEmpty ? cardTitle : context.l10n.homeOpenTopicsTitle);
    return JoviaSurfaceCard(
      radius: 34,
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
      child: Stack(
        children: [
          Positioned(
            right: -8,
            top: 2,
            child: JoviaIllustrationAccent(
              asset: JoviaIllustrationAsset.sunMountain,
              width: 128,
              height: 128,
              opacity: 0.8,
            ),
          ),
          Positioned(
            right: 44,
            top: 30,
            child: Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: profile.colors.primary.withValues(alpha: 0.16),
              ),
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'KOLEKTIF KONU',
                style: profile.typography.monoEyebrow.copyWith(
                  color: profile.colors.textLight,
                  fontSize: 11.5,
                  letterSpacing: 1.85,
                ),
              ),
              const SizedBox(height: 10),
              Container(width: 146, height: 1, color: profile.colors.separator),
              const SizedBox(height: 16),
              Text(
                title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.editorialHeadline.copyWith(
                  color: profile.colors.text,
                  fontSize: 31,
                  height: 1.02,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 14),
              ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 300),
                child: Text(
                  blurb,
                  maxLines: 4,
                  overflow: TextOverflow.ellipsis,
                  style: profile.typography.bodyReading.copyWith(
                    color: profile.colors.textLight,
                    fontSize: 15.0,
                    height: 1.62,
                  ),
                ),
              ),
              if (chips.isNotEmpty) ...[
                const SizedBox(height: 16),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    for (final chip in chips) JoviaMetaPill(label: chip),
                  ],
                ),
              ],
              const SizedBox(height: 18),
              Wrap(
                spacing: 10,
                runSpacing: 10,
                children: [
                  MinimalCTAButton(
                    label: "Thread'e gir",
                    emphasized: true,
                    onTap: onOpenThread,
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _blurbFromCard(PeriodCardDto card) {
    final source = card.subtitle.trim().isNotEmpty
        ? card.subtitle.trim()
        : card.timeHint.trim();
    if (source.isEmpty) {
      return 'Genel atmosferde bu etkinin kademeli olarak guclenmesi bekleniyor.';
    }
    final cut = source.split(RegExp(r'[.!?]')).first.trim();
    final clean = cut.isEmpty ? source : cut;
    return clean.length > 140 ? '${clean.substring(0, 140).trim()}...' : clean;
  }
}

class _HomeCollectiveHighlightsRow extends StatelessWidget {
  const _HomeCollectiveHighlightsRow({required this.items});

  final List<_SkyHighlight> items;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const SizedBox.shrink();
    }
    final accents = <Color>[
      context.profileTheme.colors.primary,
      context.profileTheme.colors.lavender,
      context.profileTheme.colors.lime,
    ];
    return SizedBox(
      height: 152,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: items.length,
        separatorBuilder: (_, _) => const SizedBox(width: 12),
        itemBuilder: (context, index) {
          return SizedBox(
            width: 240,
            child: _SkyMiniCard(
              item: items[index],
              accent: accents[index % accents.length],
            ),
          );
        },
      ),
    );
  }
}

class _HomeSkyEventList extends StatelessWidget {
  const _HomeSkyEventList({
    required this.items,
    required this.onOpenItem,
    required this.onOpenAll,
  });

  final List<_SkyFeedItemData> items;
  final ValueChanged<_SkyFeedItemData> onOpenItem;
  final VoidCallback onOpenAll;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const SizedBox.shrink();
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final item in items) ...[
          _HomeSkyEventCard(item: item, onTap: () => onOpenItem(item)),
          if (item != items.last) const SizedBox(height: 14),
        ],
        const SizedBox(height: 14),
        JoviaSurfaceCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                context.l10n.homeOpenTopicsTitle,
                style: context.profileTheme.typography.cardTitle,
              ),
              const SizedBox(height: 10),
              Text(
                context.l10n.homeOpenTopicsBody,
                style: context.profileTheme.typography.bodyCompact.copyWith(
                  color: context.profileTheme.colors.textLight,
                ),
              ),
              const SizedBox(height: 16),
              MinimalCTAButton(
                label: context.l10n.homeAllTopics,
                emphasized: true,
                onTap: onOpenAll,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _HomeSkyEventCard extends StatelessWidget {
  const _HomeSkyEventCard({required this.item, required this.onTap});

  final _SkyFeedItemData item;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return JoviaTopicSurface(
      eyebrow: item.previewChips.isNotEmpty ? item.previewChips.first : null,
      title: item.title,
      body: item.hook,
      meta: item.previewChips.skip(1).take(2).toList(growable: false),
      secondaryAction: const Icon(Icons.arrow_outward_rounded, size: 18),
      onTap: onTap,
    );
  }
}

class _SkyMiniCard extends StatelessWidget {
  const _SkyMiniCard({required this.item, required this.accent});

  final _SkyHighlight item;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    final typo = context.profileTheme.typography;
    final colors = context.profileTheme.colors;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colors.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: colors.strokeSoft, width: 1.5),
        boxShadow: [context.profileTheme.shadows.cardShadow],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 28,
            height: 6,
            decoration: BoxDecoration(
              color: accent.withValues(alpha: 0.55),
              borderRadius: BorderRadius.circular(999),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            item.title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: typo.body.copyWith(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: colors.text,
            ),
          ),
          const SizedBox(height: 4),
          Expanded(
            child: Text(
              item.blurb,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
              style: typo.micro.copyWith(color: colors.textLight, height: 1.3),
            ),
          ),
        ],
      ),
    );
  }
}

class _SkyHighlight {
  const _SkyHighlight({required this.title, required this.blurb});

  final String title;
  final String blurb;
}

class _SkyFeedItemData {
  const _SkyFeedItemData({
    required this.id,
    required this.slug,
    required this.eventType,
    required this.title,
    required this.shortTitle,
    required this.summary,
    required this.badge,
    required this.relativeTiming,
    required this.startsAt,
    required this.exactAt,
    required this.endsAt,
    required this.tags,
    required this.bodies,
    required this.aspect,
    required this.sign,
    required this.personalizationCta,
  });

  final String id;
  final String slug;
  final String eventType;
  final String title;
  final String shortTitle;
  final String summary;
  final String badge;
  final String relativeTiming;
  final String startsAt;
  final String exactAt;
  final String endsAt;
  final List<String> tags;
  final List<String> bodies;
  final String aspect;
  final String sign;
  final Map<String, dynamic> personalizationCta;

  String get hook => toDto().hookTr;

  List<String> get previewChips => toDto().previewChips;

  SkyFeedItemDto toDto() {
    return SkyFeedItemDto(
      id: id,
      slug: slug,
      eventType: eventType,
      title: title,
      shortTitle: shortTitle,
      summary: summary,
      badge: badge,
      relativeTiming: relativeTiming,
      phase: '',
      status: '',
      startsAt: startsAt,
      exactAt: exactAt,
      endsAt: endsAt,
      tags: tags,
      bodies: bodies,
      aspect: aspect,
      sign: sign,
      personalizationCta: personalizationCta,
    );
  }

  factory _SkyFeedItemData.fromMap(Map<String, dynamic> map) {
    final dto = SkyFeedItemDto.fromMap(map);
    return _SkyFeedItemData(
      id: dto.id.trim(),
      slug: dto.slug.trim(),
      eventType: dto.eventType.trim(),
      title: dto.title.trim(),
      shortTitle: dto.shortTitle.trim(),
      summary: dto.summary.trim(),
      badge: dto.badge.trim(),
      relativeTiming: dto.relativeTiming.trim(),
      startsAt: dto.startsAt.trim(),
      exactAt: dto.exactAt.trim(),
      endsAt: dto.endsAt.trim(),
      tags: dto.tags,
      bodies: dto.bodies,
      aspect: dto.aspect.trim(),
      sign: dto.sign.trim(),
      personalizationCta: dto.personalizationCta,
    );
  }
}

class _SkyBulletin {
  const _SkyBulletin({
    required this.summary,
    required this.chips,
    required this.highlights,
  });

  final String summary;
  final List<String> chips;
  final List<_SkyHighlight> highlights;
}

class _GlassCard extends StatelessWidget {
  const _GlassCard({
    required this.child,
    this.padding = const EdgeInsets.all(18),
  });

  final Widget child;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: profile.colors.panelStrong,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: profile.colors.strokeSoft, width: 1.15),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.09),
            blurRadius: 14,
            offset: const Offset(0, 8),
            spreadRadius: -12,
          ),
        ],
      ),
      child: child,
    );
  }
}

class _TransitSummaryCard extends StatelessWidget {
  const _TransitSummaryCard({
    required this.card,
    required this.accent,
    required this.showSticker,
    required this.onTap,
  });

  final PeriodCardDto card;
  final Color accent;
  final bool showSticker;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final typo = context.profileTheme.typography;
    final colors = context.profileTheme.colors;

    final overview = card.subtitle.trim();
    final badgeMeta = card.timeHint.trim();
    final badgeTitle = badgeMeta.isNotEmpty ? badgeMeta : 'Period';

    return _GlassCard(
      padding: const EdgeInsets.all(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Stack(
          children: [
            if (showSticker)
              Positioned(
                right: 4,
                top: 4,
                child: Container(
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    color: accent.withValues(alpha: 0.35),
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Hero(
                        tag: 'transit_title_${card.id}',
                        child: Material(
                          type: MaterialType.transparency,
                          child: Text(
                            card.title.isNotEmpty
                                ? card.title
                                : 'Aktif Transit',
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: typo.body.copyWith(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                              color: colors.text,
                              height: 1.2,
                            ),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    _TransitBadge(
                      title: badgeTitle.isNotEmpty ? badgeTitle : 'Transit',
                      meta: '',
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  overview.isNotEmpty ? overview : 'Detaylar icin karti ac.',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: typo.body.copyWith(
                    fontSize: 14.5,
                    color: colors.muted,
                    height: 1.4,
                  ),
                ),
                const Spacer(),
                Row(
                  children: [
                    const Spacer(),
                    OutlinedButton(
                      onPressed: onTap,
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size(0, 30),
                        visualDensity: VisualDensity.compact,
                        backgroundColor: colors.surface,
                        side: BorderSide(color: colors.strokeSoft, width: 1.5),
                        foregroundColor: colors.primary,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(999),
                        ),
                      ),
                      child: const Text('Detaylar ->'),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

Route<T> _adaptiveSwipeRoute<T>(BuildContext context, WidgetBuilder builder) {
  final platform = Theme.of(context).platform;
  if (platform == TargetPlatform.iOS || platform == TargetPlatform.macOS) {
    return CupertinoPageRoute<T>(builder: builder);
  }
  return MaterialPageRoute<T>(builder: builder);
}

class _TransitBadge extends StatelessWidget {
  const _TransitBadge({required this.title, required this.meta});

  final String title;
  final String meta;

  @override
  Widget build(BuildContext context) {
    final typo = context.profileTheme.typography;
    final colors = context.profileTheme.colors;
    return Container(
      constraints: const BoxConstraints(maxWidth: 118),
      height: 28,
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: colors.lime,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.end,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: typo.micro.copyWith(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: colors.primary,
              height: 1,
            ),
          ),
          if (meta.trim().isNotEmpty)
            Text(
              meta,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: typo.micro.copyWith(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: colors.primary.withValues(alpha: 0.8),
                height: 1,
              ),
            ),
        ],
      ),
    );
  }
}

class _TransitPlaceholderCard extends StatelessWidget {
  const _TransitPlaceholderCard();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 290,
      child: _GlassCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            _LineBox(widthFactor: 0.6, height: 14),
            SizedBox(height: 10),
            _LineBox(widthFactor: 0.8, height: 10),
            SizedBox(height: 14),
            _LineBox(widthFactor: 1.0, height: 10),
            SizedBox(height: 8),
            _LineBox(widthFactor: 0.95, height: 10),
            SizedBox(height: 8),
            _LineBox(widthFactor: 0.7, height: 10),
          ],
        ),
      ),
    );
  }
}

class _LineBox extends StatelessWidget {
  const _LineBox({required this.widthFactor, required this.height});

  final double widthFactor;
  final double height;

  @override
  Widget build(BuildContext context) {
    final astro = context.astroTheme;
    return FractionallySizedBox(
      widthFactor: widthFactor,
      child: Container(
        height: height,
        decoration: BoxDecoration(
          color: astro.border.withValues(alpha: 0.45),
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }
}

ElementScores _computeElementScores({
  required Map<String, dynamic>? profile,
  required String? userId,
  required String? email,
  required String sun,
  required String moon,
  required String rising,
}) {
  final fromProfile = _extractElementScoresFromProfile(profile);
  if (fromProfile != null) {
    return fromProfile;
  }

  final fromSigns = _extractElementScoresFromSigns(
    sun: sun,
    moon: moon,
    rising: rising,
  );
  if (fromSigns != null) {
    return fromSigns;
  }

  final seed = userId ?? email ?? 'anon';
  final hash = seed.codeUnits.fold<int>(
    17,
    (acc, c) => (acc * 31 + c) & 0x7fffffff,
  );
  final dominant = hash % 4;
  final values = <double>[0.22, 0.22, 0.22, 0.22];
  values[dominant] += 0.34;
  return ElementScores(
    fire: values[0],
    water: values[1],
    air: values[2],
    earth: values[3],
  ).normalize();
}

ElementScores? _extractElementScoresFromProfile(Map<String, dynamic>? profile) {
  if (profile == null) {
    return null;
  }

  final direct = _extractElementScoresFromAny(profile);
  if (direct != null) {
    return direct;
  }

  for (final key in const <String>[
    'element_scores',
    'elements',
    'natal_element_scores',
    'astro_element_scores',
  ]) {
    final nested = _extractElementScoresFromAny(profile[key]);
    if (nested != null) {
      return nested;
    }
  }

  return null;
}

ElementScores? _extractElementScoresFromAny(dynamic source) {
  if (source is! Map) {
    return null;
  }
  final map = Map<String, dynamic>.from(source);
  final keys = map.keys.map((k) => k.toLowerCase()).toSet();
  if (!keys.contains('fire') ||
      !keys.contains('water') ||
      !keys.contains('air') ||
      !keys.contains('earth')) {
    return null;
  }
  return ElementScores.fromMap(map);
}

ElementScores? _extractElementScoresFromSigns({
  required String sun,
  required String moon,
  required String rising,
}) {
  final weights = <AstroElement, double>{
    AstroElement.fire: 0,
    AstroElement.water: 0,
    AstroElement.air: 0,
    AstroElement.earth: 0,
  };

  void addSign(String sign, double weight) {
    final s = sign.trim().toLowerCase();
    if (s.isEmpty || s == '—') {
      return;
    }

    const fire = <String>{
      'aries',
      'leo',
      'sagittarius',
      'koc',
      'koç',
      'aslan',
      'yay',
    };
    const earth = <String>{
      'taurus',
      'virgo',
      'capricorn',
      'boga',
      'boğa',
      'basak',
      'başak',
      'oglak',
      'oğlak',
    };
    const air = <String>{
      'gemini',
      'libra',
      'aquarius',
      'ikizler',
      'terazi',
      'kova',
    };
    const water = <String>{
      'cancer',
      'scorpio',
      'pisces',
      'yengec',
      'yengeç',
      'akrep',
      'balik',
      'balık',
    };

    if (fire.contains(s)) {
      weights[AstroElement.fire] = (weights[AstroElement.fire] ?? 0) + weight;
    } else if (water.contains(s)) {
      weights[AstroElement.water] = (weights[AstroElement.water] ?? 0) + weight;
    } else if (air.contains(s)) {
      weights[AstroElement.air] = (weights[AstroElement.air] ?? 0) + weight;
    } else if (earth.contains(s)) {
      weights[AstroElement.earth] = (weights[AstroElement.earth] ?? 0) + weight;
    }
  }

  addSign(sun, 0.4);
  addSign(moon, 0.35);
  addSign(rising, 0.25);

  if (weights.values.every((v) => v == 0)) {
    return null;
  }

  return ElementScores(
    fire: weights[AstroElement.fire] ?? 0,
    water: weights[AstroElement.water] ?? 0,
    air: weights[AstroElement.air] ?? 0,
    earth: weights[AstroElement.earth] ?? 0,
  ).normalize();
}
