import 'package:flutter/foundation.dart';

class NarrativeCopy {
  const NarrativeCopy({
    required this.title,
    required this.short,
    required this.medium,
    required this.long,
  });

  final String title;
  final String short;
  final String medium;
  final String long;

  factory NarrativeCopy.fromMap(Map<String, dynamic> map) {
    return NarrativeCopy(
      title: (map['title'] ?? '').toString(),
      short: (map['short'] ?? '').toString(),
      medium: (map['medium'] ?? '').toString(),
      long: (map['long'] ?? '').toString(),
    );
  }
}

class NarrativeBlock {
  const NarrativeBlock({
    required this.id,
    required this.type,
    required this.horizon,
    required this.intensity,
    required this.domains,
    required this.copy,
    required this.why,
    required this.meta,
    this.cta,
  });

  final String id;
  final String type;
  final String horizon;
  final double intensity;
  final List<String> domains;
  final NarrativeCopy copy;
  final List<String> why;
  final Map<String, dynamic> meta;
  final Map<String, dynamic>? cta;

  factory NarrativeBlock.fromMap(Map<String, dynamic> map) {
    final domainsRaw = map['domains'];
    final whyRaw = map['why'];
    return NarrativeBlock(
      id: (map['id'] ?? '').toString(),
      type: (map['type'] ?? '').toString(),
      horizon: (map['horizon'] ?? '').toString(),
      intensity: ((map['intensity'] ?? 0) as num).toDouble(),
      domains: domainsRaw is List
          ? [for (final d in domainsRaw) d.toString()]
          : const <String>[],
      copy: NarrativeCopy.fromMap(
        map['copy'] is Map
            ? Map<String, dynamic>.from(map['copy'] as Map)
            : <String, dynamic>{},
      ),
      why: whyRaw is List
          ? [for (final d in whyRaw) d.toString()]
          : const <String>[],
      meta: map['meta'] is Map
          ? Map<String, dynamic>.from(map['meta'] as Map)
          : <String, dynamic>{},
      cta: map['cta'] is Map
          ? Map<String, dynamic>.from(map['cta'] as Map)
          : null,
    );
  }
}

class NarrativeScreen {
  const NarrativeScreen({
    required this.title,
    required this.blocks,
    this.eventsCount = 0,
    this.signalsCount = 0,
    this.hasSignals = false,
    this.date,
  });

  final String title;
  final List<NarrativeBlock> blocks;
  final int eventsCount;
  final int signalsCount;
  final bool hasSignals;
  final String? date;

  factory NarrativeScreen.fromMap(Map<String, dynamic> map) {
    final raw = map['blocks'];
    final blocks = raw is List
        ? raw
              .whereType<Map>()
              .map((e) => NarrativeBlock.fromMap(Map<String, dynamic>.from(e)))
              .toList()
        : <NarrativeBlock>[];

    return NarrativeScreen(
      title: (map['title'] ?? '').toString(),
      blocks: blocks,
      eventsCount: (map['events_count'] ?? 0) as int,
      signalsCount: (map['signals_count'] ?? 0) as int,
      hasSignals: (map['has_signals'] ?? false) == true,
      date: map['date']?.toString(),
    );
  }
}

class NarrativeCalendarDay {
  const NarrativeCalendarDay({
    required this.date,
    required this.rating,
    required this.heat,
    required this.eventCount,
    required this.signalsCount,
    required this.hasSignals,
    required this.isCritical,
    required this.labels,
    required this.criticalReasons,
    required this.signalLabelTr,
    required this.toneLabelTr,
    required this.microSummaryTr,
  });

  final String date;
  final int rating;
  final int heat;
  final int eventCount;
  final int signalsCount;
  final bool hasSignals;
  final bool isCritical;
  final List<String> labels;
  final List<String> criticalReasons;
  final String signalLabelTr;
  final String toneLabelTr;
  final String microSummaryTr;

  factory NarrativeCalendarDay.fromMap(Map<String, dynamic> map) {
    final labelsRaw = map['labels'];
    return NarrativeCalendarDay(
      date: (map['date'] ?? '').toString(),
      rating: (map['rating'] ?? 0) as int,
      heat: (map['heat'] ?? 0) as int,
      eventCount: (map['event_count'] ?? 0) as int,
      signalsCount: (map['signals_count'] ?? 0) as int,
      hasSignals: (map['has_signals'] ?? false) == true,
      isCritical: (map['is_critical'] ?? false) == true,
      labels: labelsRaw is List
          ? [for (final l in labelsRaw) l.toString()]
          : const <String>[],
      criticalReasons: map['critical_reasons'] is List
          ? [
              for (final reason in map['critical_reasons'] as List)
                reason.toString(),
            ]
          : const <String>[],
      signalLabelTr: (map['signal_label_tr'] ?? '').toString(),
      toneLabelTr: (map['tone_label_tr'] ?? '').toString(),
      microSummaryTr: (map['micro_summary_tr'] ?? '').toString(),
    );
  }
}

List<EventCardDto> _parseEventCards(Map<String, dynamic> publicRaw) {
  final direct = _parseEventCardsFromAny(publicRaw['event_cards']);
  if (direct.isNotEmpty) {
    return direct;
  }
  return _parseEventCardsFromAny(publicRaw['event_cards_sample']);
}

List<EventCardDto> _parseEventCardsByKey(
  Map<String, dynamic> publicRaw,
  String key,
) {
  return _parseEventCardsFromAny(publicRaw[key]);
}

List<EventCardDto> _parseEventCardsFromAny(dynamic raw) {
  if (raw is List) {
    return [
      for (final card in raw)
        if (card is Map) EventCardDto.fromMap(Map<String, dynamic>.from(card)),
    ];
  }

  if (raw is Map) {
    final map = Map<String, dynamic>.from(raw);
    final items = map['items'] ?? map['cards'];
    if (items is List) {
      return [
        for (final card in items)
          if (card is Map)
            EventCardDto.fromMap(Map<String, dynamic>.from(card)),
      ];
    }
  }

  return const <EventCardDto>[];
}

class DailySelectionDto {
  const DailySelectionDto({
    required this.usedPeriodFallback,
    required this.periodOnlyNote,
    required this.dailyCount,
    required this.periodCount,
  });

  final bool usedPeriodFallback;
  final String periodOnlyNote;
  final int dailyCount;
  final int periodCount;

  factory DailySelectionDto.fromMap(Map<String, dynamic> map) {
    return DailySelectionDto(
      usedPeriodFallback: (map['used_period_fallback'] ?? false) == true,
      periodOnlyNote: (map['period_only_note'] ?? '').toString(),
      dailyCount: map['daily_count'] is int
          ? map['daily_count'] as int
          : int.tryParse((map['daily_count'] ?? '').toString()) ?? 0,
      periodCount: map['period_count'] is int
          ? map['period_count'] as int
          : int.tryParse((map['period_count'] ?? '').toString()) ?? 0,
    );
  }
}

List<PeriodPeakTimelineItemDto> _parsePeriodPeakTimeline(
  Map<String, dynamic> publicRaw,
) {
  final raw = publicRaw['period_peak_timeline'];
  if (raw is! List) {
    return const <PeriodPeakTimelineItemDto>[];
  }
  return [
    for (final item in raw)
      if (item is Map)
        PeriodPeakTimelineItemDto.fromMap(Map<String, dynamic>.from(item)),
  ];
}

class NarrativeResponse {
  const NarrativeResponse({
    required this.blocks,
    required this.spaceHub,
    required this.personalTransit,
    required this.calendarDay,
    required this.feedSnippet,
    required this.calendarDays,
    required this.periodCore,
    required this.eventCards,
    required this.dailyEventCards,
    required this.periodEventCards,
    required this.dailySelection,
    required this.periodPeakTimeline,
    required this.timeline,
  });

  final List<NarrativeBlock> blocks;
  final NarrativeScreen spaceHub;
  final NarrativeScreen personalTransit;
  final NarrativeScreen calendarDay;
  final NarrativeScreen feedSnippet;
  final Map<String, NarrativeCalendarDay> calendarDays;
  final PeriodCoreDto? periodCore;
  final List<EventCardDto> eventCards;
  final List<EventCardDto> dailyEventCards;
  final List<EventCardDto> periodEventCards;
  final DailySelectionDto? dailySelection;
  final List<PeriodPeakTimelineItemDto> periodPeakTimeline;
  final TimelineDto? timeline;

  factory NarrativeResponse.fromMap(Map<String, dynamic> map) {
    final blocksRaw = map['blocks'];
    final blocks = blocksRaw is List
        ? blocksRaw
              .whereType<Map>()
              .map((e) => NarrativeBlock.fromMap(Map<String, dynamic>.from(e)))
              .toList()
        : <NarrativeBlock>[];

    final publicRaw = map['public'] is Map
        ? Map<String, dynamic>.from(map['public'] as Map)
        : map;

    final screens = map['screens'] is Map
        ? Map<String, dynamic>.from(map['screens'] as Map)
        : <String, dynamic>{};

    final calendarRaw = map['calendar'] is Map
        ? Map<String, dynamic>.from(map['calendar'] as Map)
        : <String, dynamic>{};
    final daysRaw = calendarRaw['days'];
    final calendarDays = <String, NarrativeCalendarDay>{};
    if (daysRaw is List) {
      for (final item in daysRaw) {
        if (item is! Map) {
          continue;
        }
        final day = NarrativeCalendarDay.fromMap(
          Map<String, dynamic>.from(item),
        );
        if (day.date.isNotEmpty) {
          calendarDays[day.date] = day;
        }
      }
    }

    return NarrativeResponse(
      blocks: blocks,
      spaceHub: NarrativeScreen.fromMap(
        screens['space_hub'] is Map
            ? Map<String, dynamic>.from(screens['space_hub'] as Map)
            : <String, dynamic>{},
      ),
      personalTransit: NarrativeScreen.fromMap(
        screens['personal_transit'] is Map
            ? Map<String, dynamic>.from(screens['personal_transit'] as Map)
            : <String, dynamic>{},
      ),
      calendarDay: NarrativeScreen.fromMap(
        screens['calendar_day'] is Map
            ? Map<String, dynamic>.from(screens['calendar_day'] as Map)
            : <String, dynamic>{},
      ),
      feedSnippet: NarrativeScreen.fromMap(
        screens['feed_snippet'] is Map
            ? Map<String, dynamic>.from(screens['feed_snippet'] as Map)
            : <String, dynamic>{},
      ),
      calendarDays: calendarDays,
      periodCore: publicRaw['period_core'] is Map
          ? PeriodCoreDto.fromMap(
              Map<String, dynamic>.from(publicRaw['period_core'] as Map),
            )
          : null,
      eventCards: _parseEventCards(publicRaw),
      dailyEventCards: _parseEventCardsByKey(publicRaw, 'daily_event_cards'),
      periodEventCards: _parseEventCardsByKey(publicRaw, 'period_event_cards'),
      dailySelection: publicRaw['daily_selection'] is Map
          ? DailySelectionDto.fromMap(
              Map<String, dynamic>.from(publicRaw['daily_selection'] as Map),
            )
          : null,
      periodPeakTimeline: _parsePeriodPeakTimeline(publicRaw),
      timeline: publicRaw['timeline'] is Map
          ? TimelineDto.fromMap(
              Map<String, dynamic>.from(publicRaw['timeline'] as Map),
            )
          : null,
    );
  }
}

class PeriodCoreTagDto {
  const PeriodCoreTagDto({required this.type, required this.value});

  final String type;
  final String value;

  factory PeriodCoreTagDto.fromMap(Map<String, dynamic> map) {
    return PeriodCoreTagDto(
      type: (map['type'] ?? '').toString(),
      value: (map['value'] ?? '').toString(),
    );
  }
}

class PeriodCoreDto {
  const PeriodCoreDto({
    required this.title,
    required this.coreStory,
    required this.upperMeaning,
    required this.bigPicture,
    required this.mechanism,
    required this.tags,
  });

  final String title;
  final String coreStory;
  final String upperMeaning;
  final String bigPicture;
  final String mechanism;
  final List<PeriodCoreTagDto> tags;

  factory PeriodCoreDto.fromMap(Map<String, dynamic> map) {
    final tagsRaw = map['tags'];
    return PeriodCoreDto(
      title: (map['title'] ?? '').toString(),
      coreStory: (map['core_story'] ?? '').toString(),
      upperMeaning: (map['upper_meaning'] ?? '').toString(),
      bigPicture: (map['big_picture'] ?? '').toString(),
      mechanism: (map['mechanism'] ?? '').toString(),
      tags: tagsRaw is List
          ? [
              for (final tag in tagsRaw)
                if (tag is Map)
                  PeriodCoreTagDto.fromMap(Map<String, dynamic>.from(tag)),
            ]
          : const <PeriodCoreTagDto>[],
    );
  }
}

class PeriodStoryDto {
  const PeriodStoryDto({
    required this.title,
    required this.lead,
    required this.bigPicture,
    required this.mechanism,
    required this.contribution,
    required this.upperMeaning,
  });

  final String title;
  final String lead;
  final String bigPicture;
  final String mechanism;
  final String contribution;
  final String upperMeaning;

  bool get hasContent =>
      title.trim().isNotEmpty ||
      lead.trim().isNotEmpty ||
      bigPicture.trim().isNotEmpty ||
      mechanism.trim().isNotEmpty ||
      contribution.trim().isNotEmpty ||
      upperMeaning.trim().isNotEmpty;

  factory PeriodStoryDto.fromMap(Map<String, dynamic> map) {
    return PeriodStoryDto(
      title: (map['title'] ?? '').toString(),
      lead: (map['lead'] ?? '').toString(),
      bigPicture: (map['big_picture'] ?? '').toString(),
      mechanism: (map['mechanism'] ?? '').toString(),
      contribution: (map['contribution'] ?? map['upper_meaning'] ?? '')
          .toString(),
      upperMeaning: (map['upper_meaning'] ?? '').toString(),
    );
  }
}

class EventCardTagDto {
  const EventCardTagDto({
    required this.duration,
    required this.phase,
    required this.domain,
    required this.intensity,
    this.exactInDays,
  });

  final String duration;
  final String phase;
  final String domain;
  final double intensity;
  final int? exactInDays;

  factory EventCardTagDto.fromMap(Map<String, dynamic> map) {
    return EventCardTagDto(
      duration: (map['duration'] ?? '').toString(),
      phase: (map['phase'] ?? '').toString(),
      domain: (map['domain'] ?? '').toString(),
      intensity: ((map['intensity'] ?? 0) as num).toDouble(),
      exactInDays: map['exact_in_days'] is int
          ? map['exact_in_days'] as int
          : int.tryParse((map['exact_in_days'] ?? '').toString()),
    );
  }
}

class EventCardTimingDto {
  const EventCardTimingDto({
    required this.entryDateUtc,
    required this.peakDateUtc,
    required this.exitDateUtc,
    required this.timingNote,
  });

  final String entryDateUtc;
  final String peakDateUtc;
  final String exitDateUtc;
  final String timingNote;

  bool get hasAny =>
      entryDateUtc.trim().isNotEmpty ||
      peakDateUtc.trim().isNotEmpty ||
      exitDateUtc.trim().isNotEmpty;

  factory EventCardTimingDto.fromMap(Map<String, dynamic> map) {
    return EventCardTimingDto(
      entryDateUtc: (map['entry_date_utc'] ?? map['entryDateUtc'] ?? '')
          .toString(),
      peakDateUtc: (map['peak_date_utc'] ?? map['peakDateUtc'] ?? '')
          .toString(),
      exitDateUtc: (map['exit_date_utc'] ?? map['exitDateUtc'] ?? '')
          .toString(),
      timingNote: (map['timing_note'] ?? map['timingNote'] ?? '').toString(),
    );
  }
}

class EventCardDto {
  const EventCardDto({
    required this.eventId,
    required this.transitBody,
    required this.natalPoint,
    required this.aspect,
    required this.phase,
    required this.bucket,
    required this.orbDeg,
    required this.headline,
    required this.opening,
    required this.essence,
    required this.asks,
    required this.watchout,
    required this.whatItBuilds,
    required this.technicalNote,
    required this.title,
    required this.signature,
    required this.signatureTr,
    required this.teaser,
    required this.bigPicture,
    required this.mechanism,
    required this.horizon,
    required this.tone,
    required this.sectionLabels,
    required this.whyNow,
    required this.conflict,
    required this.shadow,
    required this.upper,
    required this.extraLine,
    required this.timeHint,
    required this.timeHintTr,
    required this.guidance,
    required this.watchOut,
    required this.hookTags,
    required this.tags,
    required this.timing,
    required this.derivedContext,
    required this.scene,
    required this.narrativeProvenance,
    required this.feltLineTr,
    required this.whyItFeelsThisWayTr,
    required this.guidanceMicroTr,
    required this.signalLabelTr,
    required this.toneLabelTr,
    required this.houseTouchpointTr,
    required this.houseTouchpointHintTr,
    required this.eventFamily,
    required this.eventKind,
    required this.importanceTier,
    required this.natalPromiseScore,
    this.periodStory,
    this.storyTrackId,
  });

  final String eventId;
  final String transitBody;
  final String natalPoint;
  final String aspect;
  final String phase;
  final String bucket;
  final double? orbDeg;
  final String headline;
  final String opening;
  final String essence;
  final String asks;
  final String watchout;
  final String whatItBuilds;
  final String technicalNote;
  final String title;
  final String signature;
  final String signatureTr;
  final String teaser;
  final String bigPicture;
  final String mechanism;
  final String horizon;
  final String tone;
  final Map<String, String> sectionLabels;
  final String whyNow;
  final String conflict;
  final String shadow;
  final String upper;
  final String extraLine;
  final String timeHint;
  final String timeHintTr;
  final List<String> guidance;
  final List<String> watchOut;
  final List<String> hookTags;
  final EventCardTagDto tags;
  final EventCardTimingDto timing;
  final Map<String, dynamic> derivedContext;
  final Map<String, dynamic> scene;
  final Map<String, dynamic> narrativeProvenance;
  final String feltLineTr;
  final String whyItFeelsThisWayTr;
  final String guidanceMicroTr;
  final String signalLabelTr;
  final String toneLabelTr;
  final String houseTouchpointTr;
  final String houseTouchpointHintTr;
  final String eventFamily;
  final String eventKind;
  final String importanceTier;
  final double? natalPromiseScore;
  final PeriodStoryDto? periodStory;
  final String? storyTrackId;

  static String _s(Map<String, dynamic> map, String a, [String? b]) {
    final value = map[a] ?? (b != null ? map[b] : null);
    return value == null ? '' : value.toString();
  }

  static List<String> _ls(Map<String, dynamic> map, String a, [String? b]) {
    final value = map[a] ?? (b != null ? map[b] : null);
    if (value is List) {
      return value.map((item) => item.toString()).toList();
    }
    return const <String>[];
  }

  static Map<String, String> _labels(Map<String, dynamic> map) {
    final value = map['section_labels'];
    if (value is Map) {
      final out = <String, String>{};
      value.forEach((k, v) => out[k.toString()] = v.toString());
      return out;
    }
    return const <String, String>{};
  }

  static Map<String, dynamic> _dynamicMap(
    Map<String, dynamic> map,
    String a, [
    String? b,
  ]) {
    final value = map[a] ?? (b != null ? map[b] : null);
    if (value is Map) {
      return Map<String, dynamic>.from(value);
    }
    return const <String, dynamic>{};
  }

  EventCardDto copyWith({
    String? eventId,
    String? transitBody,
    String? natalPoint,
    String? aspect,
    String? phase,
    String? bucket,
    double? orbDeg,
    String? headline,
    String? opening,
    String? essence,
    String? asks,
    String? watchout,
    String? whatItBuilds,
    String? technicalNote,
    String? title,
    String? signature,
    String? signatureTr,
    String? teaser,
    String? bigPicture,
    String? mechanism,
    String? horizon,
    String? tone,
    Map<String, String>? sectionLabels,
    String? whyNow,
    String? conflict,
    String? shadow,
    String? upper,
    String? extraLine,
    String? timeHint,
    String? timeHintTr,
    List<String>? guidance,
    List<String>? watchOut,
    List<String>? hookTags,
    EventCardTagDto? tags,
    EventCardTimingDto? timing,
    Map<String, dynamic>? derivedContext,
    Map<String, dynamic>? scene,
    Map<String, dynamic>? narrativeProvenance,
    String? feltLineTr,
    String? whyItFeelsThisWayTr,
    String? guidanceMicroTr,
    String? signalLabelTr,
    String? toneLabelTr,
    String? houseTouchpointTr,
    String? houseTouchpointHintTr,
    String? eventFamily,
    String? eventKind,
    String? importanceTier,
    double? natalPromiseScore,
    PeriodStoryDto? periodStory,
    String? storyTrackId,
  }) {
    return EventCardDto(
      eventId: eventId ?? this.eventId,
      transitBody: transitBody ?? this.transitBody,
      natalPoint: natalPoint ?? this.natalPoint,
      aspect: aspect ?? this.aspect,
      phase: phase ?? this.phase,
      bucket: bucket ?? this.bucket,
      orbDeg: orbDeg ?? this.orbDeg,
      headline: headline ?? this.headline,
      opening: opening ?? this.opening,
      essence: essence ?? this.essence,
      asks: asks ?? this.asks,
      watchout: watchout ?? this.watchout,
      whatItBuilds: whatItBuilds ?? this.whatItBuilds,
      technicalNote: technicalNote ?? this.technicalNote,
      title: title ?? this.title,
      signature: signature ?? this.signature,
      signatureTr: signatureTr ?? this.signatureTr,
      teaser: teaser ?? this.teaser,
      bigPicture: bigPicture ?? this.bigPicture,
      mechanism: mechanism ?? this.mechanism,
      horizon: horizon ?? this.horizon,
      tone: tone ?? this.tone,
      sectionLabels: sectionLabels ?? this.sectionLabels,
      whyNow: whyNow ?? this.whyNow,
      conflict: conflict ?? this.conflict,
      shadow: shadow ?? this.shadow,
      upper: upper ?? this.upper,
      extraLine: extraLine ?? this.extraLine,
      timeHint: timeHint ?? this.timeHint,
      timeHintTr: timeHintTr ?? this.timeHintTr,
      guidance: guidance ?? this.guidance,
      watchOut: watchOut ?? this.watchOut,
      hookTags: hookTags ?? this.hookTags,
      tags: tags ?? this.tags,
      timing: timing ?? this.timing,
      derivedContext: derivedContext ?? this.derivedContext,
      scene: scene ?? this.scene,
      narrativeProvenance: narrativeProvenance ?? this.narrativeProvenance,
      feltLineTr: feltLineTr ?? this.feltLineTr,
      whyItFeelsThisWayTr: whyItFeelsThisWayTr ?? this.whyItFeelsThisWayTr,
      guidanceMicroTr: guidanceMicroTr ?? this.guidanceMicroTr,
      signalLabelTr: signalLabelTr ?? this.signalLabelTr,
      toneLabelTr: toneLabelTr ?? this.toneLabelTr,
      houseTouchpointTr: houseTouchpointTr ?? this.houseTouchpointTr,
      houseTouchpointHintTr:
          houseTouchpointHintTr ?? this.houseTouchpointHintTr,
      eventFamily: eventFamily ?? this.eventFamily,
      eventKind: eventKind ?? this.eventKind,
      importanceTier: importanceTier ?? this.importanceTier,
      natalPromiseScore: natalPromiseScore ?? this.natalPromiseScore,
      periodStory: periodStory ?? this.periodStory,
      storyTrackId: storyTrackId ?? this.storyTrackId,
    );
  }

  factory EventCardDto.fromMap(Map<String, dynamic> map) {
    final headline = _s(map, 'headline', 'title');
    final opening = _s(map, 'opening').trim().isNotEmpty
        ? _s(map, 'opening')
        : _s(map, 'teaser');
    final essence = _s(map, 'essence').trim().isNotEmpty
        ? _s(map, 'essence')
        : _s(map, 'big_picture', 'conflict');
    final asks = _s(map, 'asks').trim().isNotEmpty
        ? _s(map, 'asks')
        : _s(map, 'upper', 'upper_meaning');
    final watchout = _s(map, 'watchout').trim().isNotEmpty
        ? _s(map, 'watchout')
        : _s(map, 'shadow');
    final whatItBuilds = _s(map, 'what_it_builds').trim().isNotEmpty
        ? _s(map, 'what_it_builds')
        : _s(map, 'upper_meaning');
    final rawOrb = map['orb_deg'];
    final rawNatalPromise = map['natal_promise'] is Map
        ? Map<String, dynamic>.from(map['natal_promise'] as Map)
        : const <String, dynamic>{};
    return EventCardDto(
      eventId: _s(map, 'event_id', 'eventId'),
      transitBody: _s(map, 'transit_body', 'transitBody'),
      natalPoint: _s(map, 'natal_point', 'natalPoint'),
      aspect: _s(map, 'aspect'),
      phase: _s(map, 'phase'),
      bucket: _s(map, 'bucket'),
      orbDeg: rawOrb is num ? rawOrb.toDouble() : double.tryParse('$rawOrb'),
      headline: headline,
      opening: opening,
      essence: essence,
      asks: asks,
      watchout: watchout,
      whatItBuilds: whatItBuilds,
      technicalNote: _s(map, 'technical_note', 'extra_line'),
      title: headline.trim().isNotEmpty ? headline : _s(map, 'title'),
      signature: _s(map, 'signature'),
      signatureTr: _s(map, 'signature_tr', 'signatureTr'),
      teaser: opening,
      bigPicture: essence,
      mechanism: _s(map, 'mechanism'),
      horizon: _s(map, 'horizon'),
      tone: _s(map, 'tone'),
      sectionLabels: _labels(map),
      whyNow: _s(map, 'why_now', 'whyNow'),
      conflict: essence,
      shadow: watchout,
      upper: asks,
      extraLine: _s(map, 'extra_line', 'extraLine'),
      timeHint: _s(map, 'time_hint', 'timeHint'),
      timeHintTr: _s(map, 'time_hint_tr', 'timeHintTr'),
      guidance: _ls(map, 'guidance'),
      watchOut: _ls(map, 'watch_out', 'watchOut'),
      hookTags: _ls(map, 'hook_tags', 'hookTags'),
      timing: EventCardTimingDto.fromMap(
        map['timing'] is Map
            ? Map<String, dynamic>.from(map['timing'] as Map)
            : const <String, dynamic>{},
      ),
      derivedContext: map['derived_context'] is Map
          ? Map<String, dynamic>.from(map['derived_context'] as Map)
          : const <String, dynamic>{},
      scene: map['scene'] is Map
          ? Map<String, dynamic>.from(map['scene'] as Map)
          : const <String, dynamic>{},
      narrativeProvenance: _dynamicMap(
        map,
        'narrative_provenance',
        'narrativeProvenance',
      ),
      feltLineTr: _s(map, 'felt_line_tr', 'feltLineTr'),
      whyItFeelsThisWayTr: _s(
        map,
        'why_it_feels_this_way_tr',
        'whyItFeelsThisWayTr',
      ),
      guidanceMicroTr: _s(map, 'guidance_micro_tr', 'guidanceMicroTr'),
      signalLabelTr: _s(map, 'signal_label_tr', 'signalLabelTr'),
      toneLabelTr: _s(map, 'tone_label_tr', 'toneLabelTr'),
      houseTouchpointTr: _s(map, 'house_touchpoint_tr', 'houseTouchpointTr'),
      houseTouchpointHintTr: _s(
        map,
        'house_touchpoint_hint_tr',
        'houseTouchpointHintTr',
      ),
      eventFamily: _s(map, 'event_family', 'eventFamily'),
      eventKind: _s(map, 'event_kind', 'eventKind'),
      importanceTier: _s(map, 'importance_tier', 'importanceTier'),
      natalPromiseScore: rawNatalPromise['score'] is num
          ? (rawNatalPromise['score'] as num).toDouble()
          : double.tryParse('${rawNatalPromise['score'] ?? ''}'),
      periodStory: map['period_story'] is Map
          ? PeriodStoryDto.fromMap(
              Map<String, dynamic>.from(map['period_story'] as Map),
            )
          : null,
      storyTrackId: _s(map, 'story_track_id').trim().isEmpty
          ? null
          : _s(map, 'story_track_id').trim(),
      tags: EventCardTagDto.fromMap(
        map['tags'] is Map
            ? Map<String, dynamic>.from(map['tags'] as Map)
            : const <String, dynamic>{},
      ),
    );
  }
}

class PeriodPeakTimelineItemDto {
  const PeriodPeakTimelineItemDto({
    required this.eventId,
    required this.title,
    required this.signatureTr,
    required this.peakDateUtc,
    required this.entryDateUtc,
    required this.exitDateUtc,
    required this.bucket,
    required this.phase,
    required this.timeHintTr,
    required this.eventCard,
  });

  final String eventId;
  final String title;
  final String signatureTr;
  final String peakDateUtc;
  final String entryDateUtc;
  final String exitDateUtc;
  final String bucket;
  final String phase;
  final String timeHintTr;
  final EventCardDto? eventCard;

  bool get canOpenDetail => eventCard != null;

  String get displayTitle {
    final direct = title.trim();
    if (direct.isNotEmpty) {
      return direct;
    }
    final signature = signatureTr.trim();
    if (signature.isNotEmpty) {
      return signature;
    }
    return 'Period etkisi';
  }

  factory PeriodPeakTimelineItemDto.fromMap(Map<String, dynamic> map) {
    return PeriodPeakTimelineItemDto(
      eventId: (map['event_id'] ?? map['eventId'] ?? '').toString(),
      title: (map['title'] ?? '').toString(),
      signatureTr: (map['signature_tr'] ?? map['signatureTr'] ?? '').toString(),
      peakDateUtc: (map['peak_date_utc'] ?? map['peakDateUtc'] ?? '')
          .toString(),
      entryDateUtc: (map['entry_date_utc'] ?? map['entryDateUtc'] ?? '')
          .toString(),
      exitDateUtc: (map['exit_date_utc'] ?? map['exitDateUtc'] ?? '')
          .toString(),
      bucket: (map['bucket'] ?? '').toString(),
      phase: (map['phase'] ?? '').toString(),
      timeHintTr: (map['time_hint_tr'] ?? map['timeHintTr'] ?? '').toString(),
      eventCard: map['event_card'] is Map
          ? EventCardDto.fromMap(
              Map<String, dynamic>.from(map['event_card'] as Map),
            )
          : null,
    );
  }
}

class TimelineDto {
  const TimelineDto({
    required this.date,
    required this.summary,
    required this.lines,
    required this.dotIntensity,
  });

  final String date;
  final String summary;
  final List<String> lines;
  final int dotIntensity;

  factory TimelineDto.fromMap(Map<String, dynamic> map) {
    final linesRaw = map['lines'];
    return TimelineDto(
      date: (map['date'] ?? '').toString(),
      summary: (map['summary'] ?? '').toString(),
      lines: linesRaw is List
          ? [for (final line in linesRaw) line.toString()]
          : const <String>[],
      dotIntensity: (map['dot_intensity'] ?? 0) as int,
    );
  }
}

class PeriodMarkerDto {
  const PeriodMarkerDto({
    required this.id,
    required this.title,
    required this.summary,
    required this.timeHint,
    required this.raw,
  });

  final String id;
  final String title;
  final String summary;
  final String timeHint;
  final Map<String, dynamic> raw;

  factory PeriodMarkerDto.fromMap(Map<String, dynamic> map) {
    final id =
        (map['id'] ??
                map['marker_id'] ??
                map['event_id'] ??
                map['slug'] ??
                map['key'] ??
                '')
            .toString()
            .trim();
    final title =
        (map['title'] ?? map['label'] ?? map['headline'] ?? map['name'] ?? '')
            .toString()
            .trim();
    final summary =
        (map['summary'] ??
                map['subtitle'] ??
                map['description'] ??
                map['core_story'] ??
                '')
            .toString()
            .trim();
    final timing = map['timing'];
    final timeHint =
        (map['range'] ??
                map['time_hint'] ??
                map['time_hint_tr'] ??
                (timing is Map ? timing['timing_note'] : null) ??
                map['label'] ??
                '')
            .toString()
            .trim();
    return PeriodMarkerDto(
      id: id,
      title: title,
      summary: summary,
      timeHint: timeHint,
      raw: map,
    );
  }
}

class PeriodThemeDto {
  const PeriodThemeDto({
    required this.id,
    required this.title,
    required this.summary,
    required this.timeHint,
    required this.raw,
  });

  final String id;
  final String title;
  final String summary;
  final String timeHint;
  final Map<String, dynamic> raw;

  factory PeriodThemeDto.fromMap(
    Map<String, dynamic> map, {
    required int index,
  }) {
    final labelPack = map['label_pack'] is Map
        ? Map<String, dynamic>.from(map['label_pack'] as Map)
        : const <String, dynamic>{};
    final id =
        (map['id'] ??
                map['theme_id'] ??
                map['event_id'] ??
                map['label'] ??
                'theme-$index')
            .toString()
            .trim();
    final title =
        (map['title'] ??
                map['label'] ??
                labelPack['short'] ??
                labelPack['full'] ??
                'Tema ${index + 1}')
            .toString()
            .trim();
    final summary =
        (map['summary'] ??
                map['description'] ??
                map['why'] ??
                map['note'] ??
                map['theme'] ??
                '')
            .toString()
            .trim();
    final timeHint =
        (map['time_hint'] ??
                map['range'] ??
                labelPack['where'] ??
                map['phase_kind'] ??
                '')
            .toString()
            .trim();
    return PeriodThemeDto(
      id: id.isNotEmpty ? id : 'theme-$index',
      title: title.isNotEmpty ? title : 'Tema ${index + 1}',
      summary: summary,
      timeHint: timeHint,
      raw: map,
    );
  }
}

class IntentSummaryDto {
  const IntentSummaryDto({
    required this.intent,
    required this.title,
    required this.summary,
    required this.timeHint,
    required this.raw,
  });

  final String intent;
  final String title;
  final String summary;
  final String timeHint;
  final Map<String, dynamic> raw;

  factory IntentSummaryDto.fromMap(
    String intent,
    Map<String, dynamic> map, {
    required int index,
  }) {
    final byDate = map['by_date'] is Map
        ? Map<String, dynamic>.from(map['by_date'] as Map)
        : const <String, dynamic>{};
    final entries =
        byDate.entries
            .where((entry) => entry.value is Map)
            .map(
              (entry) => MapEntry(
                entry.key,
                Map<String, dynamic>.from(entry.value as Map),
              ),
            )
            .toList()
          ..sort(
            (a, b) => (((b.value['score'] ?? 0) as num).toDouble()).compareTo(
              ((a.value['score'] ?? 0) as num).toDouble(),
            ),
          );
    final top = entries.take(2).toList(growable: false);
    final topDates = top
        .map((entry) => entry.key)
        .where((e) => e.isNotEmpty)
        .toList();
    final topRatings = top
        .map((entry) => (entry.value['rating'] ?? '').toString().trim())
        .where((e) => e.isNotEmpty)
        .toList();
    final title = _intentTitle(intent, index: index);
    final summary = topDates.isEmpty
        ? '$title icin bu donemde takip edilecek pencereler var.'
        : '$title odagi icin one cikan gunler: ${topDates.join(', ')}.';
    final timeHint = topRatings.isEmpty
        ? ''
        : 'Puanlar: ${topRatings.join(' / ')}';
    return IntentSummaryDto(
      intent: intent,
      title: title,
      summary: summary,
      timeHint: timeHint,
      raw: map,
    );
  }

  static String _intentTitle(String intent, {required int index}) {
    switch (intent) {
      case 'beauty_care':
        return 'Bakim ve Beden';
      case 'business':
        return 'Is ve Uretim';
      case 'money':
        return 'Para ve Kaynak';
      case 'relationship':
        return 'Iliski ve Uyum';
      default:
        return intent.trim().isNotEmpty ? intent : 'Niyet ${index + 1}';
    }
  }
}

class PeriodCardDto {
  const PeriodCardDto({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.timeHint,
    this.eventCard,
    this.marker,
    this.theme,
    this.intentSummary,
  });

  final String id;
  final String title;
  final String subtitle;
  final String timeHint;
  final EventCardDto? eventCard;
  final PeriodMarkerDto? marker;
  final PeriodThemeDto? theme;
  final IntentSummaryDto? intentSummary;

  factory PeriodCardDto.fromEventCard({
    required EventCardDto eventCard,
    required int index,
  }) {
    String pickFirst(List<String> values) {
      for (final value in values) {
        final trimmed = value.trim();
        if (trimmed.isNotEmpty) {
          return trimmed;
        }
      }
      return '';
    }

    final story = eventCard.periodStory;
    return PeriodCardDto(
      id: eventCard.eventId.isNotEmpty ? eventCard.eventId : 'event-$index',
      title: eventCard.title.trim().isNotEmpty
          ? eventCard.title.trim()
          : 'Period',
      subtitle: pickFirst([
        eventCard.opening,
        eventCard.essence,
        eventCard.teaser,
        eventCard.whyNow,
        story?.lead ?? '',
        story?.bigPicture ?? '',
        'Bu donemin ana akisi.',
      ]),
      timeHint: pickFirst([
        eventCard.timeHintTr,
        eventCard.signatureTr,
        eventCard.whyNow,
      ]),
      eventCard: eventCard,
    );
  }

  factory PeriodCardDto.fromMarker({
    required PeriodMarkerDto marker,
    required PeriodCoreDto? periodCore,
    required int index,
  }) {
    final periodTitle = periodCore?.title.trim() ?? '';
    final periodStory = periodCore?.coreStory.trim() ?? '';
    final periodUpperMeaning = periodCore?.upperMeaning.trim() ?? '';
    final title = marker.title.isNotEmpty
        ? marker.title
        : (periodTitle.isNotEmpty ? periodTitle : 'Period');
    final subtitle = marker.summary.isNotEmpty
        ? marker.summary
        : (periodStory.isNotEmpty ? periodStory : 'Bu donemin ana temasi.');
    final timeHint = marker.timeHint.isNotEmpty
        ? marker.timeHint
        : (periodUpperMeaning.isNotEmpty ? periodUpperMeaning : '');
    return PeriodCardDto(
      id: marker.id.isNotEmpty ? marker.id : 'period-$index',
      title: title,
      subtitle: subtitle,
      timeHint: timeHint,
      eventCard: null,
      marker: marker,
    );
  }

  factory PeriodCardDto.fromTheme({
    required PeriodThemeDto theme,
    required int index,
  }) {
    return PeriodCardDto(
      id: theme.id.isNotEmpty ? theme.id : 'theme-$index',
      title: theme.title,
      subtitle: theme.summary.isNotEmpty
          ? theme.summary
          : 'Bu donemde one cikan tema.',
      timeHint: theme.timeHint,
      eventCard: null,
      theme: theme,
    );
  }

  factory PeriodCardDto.fromIntentSummary({
    required IntentSummaryDto intentSummary,
    required int index,
  }) {
    return PeriodCardDto(
      id: intentSummary.intent.isNotEmpty
          ? 'intent-${intentSummary.intent}'
          : 'intent-$index',
      title: intentSummary.title,
      subtitle: intentSummary.summary,
      timeHint: intentSummary.timeHint,
      eventCard: null,
      intentSummary: intentSummary,
    );
  }
}

@immutable
class PeriodDetailSectionDto {
  const PeriodDetailSectionDto({required this.title, required this.body});

  final String title;
  final String body;
}

@immutable
class PeriodDetailMetaRowDto {
  const PeriodDetailMetaRowDto({required this.label, required this.value});

  final String label;
  final String value;
}

@immutable
class PeriodDetailNarrativeDto {
  const PeriodDetailNarrativeDto({
    required this.eyebrow,
    required this.headline,
    required this.summary,
    required this.timingNote,
    required this.umbrellaTitle,
    required this.umbrellaBody,
    required this.chips,
    required this.sections,
    required this.metaRows,
    required this.detailRendererVersion,
    required this.routeSource,
    required this.sectionSources,
  });

  final String eyebrow;
  final String headline;
  final String summary;
  final String timingNote;
  final String umbrellaTitle;
  final String umbrellaBody;
  final List<String> chips;
  final List<PeriodDetailSectionDto> sections;
  final List<PeriodDetailMetaRowDto> metaRows;
  final String detailRendererVersion;
  final String routeSource;
  final Map<String, String> sectionSources;

  bool get hasMetaRows => metaRows.any((row) => row.value.trim().isNotEmpty);
  bool get hasUmbrella => umbrellaBody.trim().isNotEmpty;
}

String _cleanDetailText(String value) {
  return value.replaceAll(RegExp(r'\s+'), ' ').trim();
}

String _protectDetailOrdinals(String value) {
  return value.replaceAllMapped(
    RegExp(r'(\b\d{1,2})\.(\s*Ev\b)', caseSensitive: false),
    (match) => '${match.group(1)}<EV_DOT>${match.group(2)}',
  );
}

String _restoreDetailOrdinals(String value) {
  return value.replaceAll('<EV_DOT>', '.');
}

List<String> _splitDetailSentences(String value) {
  final cleaned = _cleanDetailText(value);
  if (cleaned.isEmpty) {
    return const <String>[];
  }
  final protected = _protectDetailOrdinals(cleaned);
  final parts = protected
      .split(RegExp(r'(?<=[.!?])\s+'))
      .map(_restoreDetailOrdinals)
      .map(_cleanDetailText)
      .where((part) => part.isNotEmpty)
      .toList();
  if (parts.isNotEmpty) {
    return parts;
  }
  return <String>[_restoreDetailOrdinals(protected)];
}

String _normalizeDetailText(String value) {
  return _cleanDetailText(
    value
        .toLowerCase()
        .replaceAll(RegExp(r'[^\w\s]', unicode: true), ' ')
        .replaceAll(RegExp(r'\s+'), ' '),
  );
}

double _detailSimilarity(String left, String right) {
  final leftTokens = _normalizeDetailText(
    left,
  ).split(' ').where((token) => token.isNotEmpty).toSet();
  final rightTokens = _normalizeDetailText(
    right,
  ).split(' ').where((token) => token.isNotEmpty).toSet();
  if (leftTokens.isEmpty || rightTokens.isEmpty) {
    return 0;
  }
  final overlap = leftTokens.intersection(rightTokens).length;
  final union = leftTokens.union(rightTokens).length;
  if (union == 0) {
    return 0;
  }
  return overlap / union;
}

bool _isDetailDuplicate(String candidate, Iterable<String> existing) {
  final normalizedCandidate = _normalizeDetailText(candidate);
  if (normalizedCandidate.isEmpty) {
    return true;
  }
  for (final item in existing) {
    final normalizedItem = _normalizeDetailText(item);
    if (normalizedItem.isEmpty) {
      continue;
    }
    if (normalizedItem == normalizedCandidate) {
      return true;
    }
    if (normalizedItem.length > 16 &&
        (normalizedItem.contains(normalizedCandidate) ||
            normalizedCandidate.contains(normalizedItem))) {
      return true;
    }
    if (_detailSimilarity(candidate, item) >= 0.72) {
      return true;
    }
  }
  return false;
}

String _firstDistinctSnippet(
  List<String> candidates, {
  List<String> avoid = const <String>[],
  int maxSentences = 1,
}) {
  final seen = <String>[...avoid];
  for (final candidate in candidates) {
    final sentence = _mergeDistinctSnippets(
      <String>[candidate],
      avoid: seen,
      maxSentences: maxSentences,
    );
    if (sentence.isNotEmpty) {
      return sentence;
    }
  }
  return '';
}

String _mergeDistinctSnippets(
  List<String> candidates, {
  List<String> avoid = const <String>[],
  int maxSentences = 3,
}) {
  final sentences = <String>[];
  final seen = <String>[...avoid];

  for (final candidate in candidates) {
    for (final sentence in _splitDetailSentences(candidate)) {
      if (_isDetailDuplicate(sentence, seen)) {
        continue;
      }
      sentences.add(sentence);
      seen.add(sentence);
      if (sentences.length >= maxSentences) {
        return sentences.join(' ');
      }
    }
  }

  return sentences.join(' ');
}

String _listToNarrative(
  List<String> items, {
  String prefix = '',
  int maxSentences = 2,
}) {
  final merged = _mergeDistinctSnippets(items, maxSentences: maxSentences);
  if (merged.isEmpty) {
    return '';
  }
  if (prefix.trim().isEmpty) {
    return merged;
  }
  return '$prefix $merged';
}

List<String> _uniqueDetailLabels(List<String> values, {int limit = 3}) {
  final out = <String>[];
  for (final value in values) {
    final cleaned = _cleanDetailText(value);
    if (cleaned.isEmpty || _isDetailDuplicate(cleaned, out)) {
      continue;
    }
    out.add(cleaned);
    if (out.length >= limit) {
      break;
    }
  }
  return out;
}

class _DetailSourceValue {
  const _DetailSourceValue({required this.value, required this.source});

  final String value;
  final String source;
}

class _DetailSourceCandidate {
  const _DetailSourceCandidate({required this.source, required this.value});

  final String source;
  final String value;
}

_DetailSourceValue _firstSourceValue(
  List<_DetailSourceCandidate> candidates, {
  List<String> avoid = const <String>[],
  int maxSentences = 2,
}) {
  for (final candidate in candidates) {
    final text = _mergeDistinctSnippets(
      <String>[candidate.value],
      avoid: avoid,
      maxSentences: maxSentences,
    );
    if (text.isNotEmpty) {
      return _DetailSourceValue(value: text, source: candidate.source);
    }
  }
  return const _DetailSourceValue(value: '', source: 'empty');
}

extension PeriodCardDetailNarrativeX on PeriodCardDto {
  PeriodDetailNarrativeDto buildDetailNarrative({
    required PeriodCoreDto? periodCore,
    String routeSource = 'unknown',
  }) {
    final event = eventCard;
    final story = event?.periodStory;

    if (event == null) {
      final eyebrow = _firstDistinctSnippet(
        [periodCore?.title ?? ''],
        avoid: <String>[title],
        maxSentences: 1,
      );
      final summary = _firstDistinctSnippet([
        subtitle,
        periodCore?.coreStory ?? '',
        'Bu donemde one cikan tema burada toplanir.',
      ], maxSentences: 2);
      final timingNote = _firstDistinctSnippet(
        [timeHint],
        avoid: <String>[summary],
        maxSentences: 2,
      );
      return PeriodDetailNarrativeDto(
        eyebrow: eyebrow,
        headline: title.trim().isNotEmpty ? title.trim() : 'Donem',
        summary: summary.isNotEmpty
            ? summary
            : 'Bu doneme ait ozet anlatim bulunamadi.',
        timingNote: timingNote,
        umbrellaTitle: '',
        umbrellaBody: '',
        chips: const <String>[],
        sections: <PeriodDetailSectionDto>[
          PeriodDetailSectionDto(
            title: 'Bu donemin ozu',
            body: summary.isNotEmpty
                ? summary
                : 'Bu doneme ait ozet anlatim bulunamadi.',
          ),
        ],
        metaRows: <PeriodDetailMetaRowDto>[
          if (timeHint.trim().isNotEmpty)
            PeriodDetailMetaRowDto(label: 'Zaman', value: timeHint.trim()),
        ],
        detailRendererVersion: 'period_detail_v3',
        routeSource: routeSource,
        sectionSources: const <String, String>{
          'headline': 'period_card.title',
          'opening': 'period_card.subtitle',
          'essence': 'period_card.subtitle',
          'mechanism': 'empty',
          'asks': 'empty',
          'watchout': 'empty',
          'what_it_builds': 'empty',
          'technical_note': 'empty',
          'umbrella': 'empty',
        },
      );
    }

    final headline = _firstSourceValue([
      _DetailSourceCandidate(source: 'event.headline', value: event.headline),
      _DetailSourceCandidate(source: 'event.title', value: event.title),
      _DetailSourceCandidate(source: 'period_card.title', value: title),
    ], maxSentences: 1);
    final opening = _firstSourceValue([
      _DetailSourceCandidate(source: 'event.opening', value: event.opening),
      _DetailSourceCandidate(source: 'event.teaser', value: event.teaser),
      _DetailSourceCandidate(source: 'period_card.subtitle', value: subtitle),
    ], maxSentences: 2);
    final timing = _firstSourceValue(
      [
        _DetailSourceCandidate(
          source: 'event.time_hint_tr',
          value: event.timeHintTr,
        ),
        _DetailSourceCandidate(source: 'event.why_now', value: event.whyNow),
        _DetailSourceCandidate(
          source: 'event.timing.timing_note',
          value: event.timing.timingNote,
        ),
        _DetailSourceCandidate(
          source: 'period_card.time_hint',
          value: timeHint,
        ),
      ],
      avoid: <String>[opening.value],
      maxSentences: 2,
    );
    final essence = _firstSourceValue(
      [
        _DetailSourceCandidate(source: 'event.essence', value: event.essence),
        _DetailSourceCandidate(
          source: 'event.big_picture',
          value: event.bigPicture,
        ),
        _DetailSourceCandidate(source: 'event.conflict', value: event.conflict),
      ],
      avoid: <String>[opening.value],
      maxSentences: 2,
    );
    final mechanism = _firstSourceValue(
      [
        _DetailSourceCandidate(
          source: 'event.mechanism',
          value: event.mechanism,
        ),
        _DetailSourceCandidate(source: 'event.why_now', value: event.whyNow),
      ],
      avoid: <String>[opening.value, timing.value, essence.value],
      maxSentences: 2,
    );
    final asks = _firstSourceValue(
      [
        _DetailSourceCandidate(source: 'event.asks', value: event.asks),
        _DetailSourceCandidate(source: 'event.upper', value: event.upper),
        _DetailSourceCandidate(
          source: 'event.guidance',
          value: _listToNarrative(event.guidance, prefix: 'Kucuk pratik:'),
        ),
      ],
      avoid: <String>[
        opening.value,
        timing.value,
        essence.value,
        mechanism.value,
      ],
      maxSentences: 2,
    );
    final builds = _firstSourceValue(
      [
        _DetailSourceCandidate(
          source: 'event.what_it_builds',
          value: event.whatItBuilds,
        ),
      ],
      avoid: <String>[
        opening.value,
        timing.value,
        essence.value,
        mechanism.value,
        asks.value,
      ],
      maxSentences: 1,
    );
    final watchout = _firstSourceValue(
      [
        _DetailSourceCandidate(source: 'event.watchout', value: event.watchout),
        _DetailSourceCandidate(source: 'event.shadow', value: event.shadow),
        _DetailSourceCandidate(
          source: 'event.watch_out',
          value: _listToNarrative(
            event.watchOut,
            prefix: 'Bunu zorlastiran sey genelde su olur:',
          ),
        ),
      ],
      avoid: <String>[
        opening.value,
        timing.value,
        essence.value,
        mechanism.value,
        asks.value,
        builds.value,
      ],
      maxSentences: 2,
    );
    final umbrellaTitle = _firstSourceValue(
      [
        _DetailSourceCandidate(
          source: 'period_story.title',
          value: story?.title ?? '',
        ),
      ],
      avoid: <String>[headline.value],
      maxSentences: 1,
    );
    final umbrellaBody = _firstSourceValue(
      [
        _DetailSourceCandidate(
          source: 'period_story.lead',
          value: story?.lead ?? '',
        ),
        _DetailSourceCandidate(
          source: 'period_story.big_picture',
          value: story?.bigPicture ?? '',
        ),
      ],
      avoid: <String>[opening.value, essence.value],
      maxSentences: 2,
    );

    final sections = <PeriodDetailSectionDto>[
      if (essence.value.isNotEmpty)
        PeriodDetailSectionDto(title: 'Bu donemin ozu', body: essence.value),
      if (mechanism.value.isNotEmpty)
        PeriodDetailSectionDto(title: 'Nasil calisiyor', body: mechanism.value),
      if (asks.value.isNotEmpty)
        PeriodDetailSectionDto(title: 'Senden ne istiyor', body: asks.value),
      if (watchout.value.isNotEmpty)
        PeriodDetailSectionDto(
          title: 'Dikkat edilmesi gereken',
          body: watchout.value,
        ),
      if (builds.value.isNotEmpty)
        PeriodDetailSectionDto(
          title: 'Sende neyi gelistiriyor',
          body: builds.value,
        ),
    ];

    final metaRows = <PeriodDetailMetaRowDto>[
      if (event.signatureTr.trim().isNotEmpty)
        PeriodDetailMetaRowDto(label: 'Etki', value: event.signatureTr.trim()),
      if (timing.value.trim().isNotEmpty)
        PeriodDetailMetaRowDto(label: 'Zaman', value: timing.value.trim()),
      if (event.technicalNote.trim().isNotEmpty)
        PeriodDetailMetaRowDto(
          label: 'Teknik not',
          value: event.technicalNote.trim(),
        ),
    ];

    return PeriodDetailNarrativeDto(
      eyebrow: umbrellaTitle.value,
      headline: headline.value.isNotEmpty ? headline.value : 'Donem',
      summary: opening.value.isNotEmpty
          ? opening.value
          : (subtitle.trim().isNotEmpty
                ? subtitle.trim()
                : 'Bu doneme ait ozet anlatim bulunamadi.'),
      timingNote: timing.value,
      umbrellaTitle: umbrellaTitle.value,
      umbrellaBody: umbrellaBody.value,
      chips: _uniqueDetailLabels([
        event.tags.domain,
        event.tags.phase,
        event.tags.duration,
      ]),
      sections: sections.isNotEmpty
          ? sections
          : <PeriodDetailSectionDto>[
              PeriodDetailSectionDto(
                title: 'Bu donemin ozu',
                body: subtitle.trim().isNotEmpty
                    ? subtitle.trim()
                    : 'Bu doneme ait ozet anlatim bulunamadi.',
              ),
            ],
      metaRows: metaRows,
      detailRendererVersion: 'period_detail_v3',
      routeSource: routeSource,
      sectionSources: <String, String>{
        'headline': headline.source,
        'opening': opening.source,
        'essence': essence.source,
        'mechanism': mechanism.source,
        'asks': asks.source,
        'watchout': watchout.source,
        'what_it_builds': builds.source,
        'technical_note': event.technicalNote.trim().isNotEmpty
            ? 'event.technical_note'
            : 'empty',
        'umbrella': umbrellaBody.source,
      },
    );
  }
}

class PeriodCalendarDto {
  const PeriodCalendarDto({
    required this.periodCore,
    required this.markers,
    required this.themes,
    required this.intentSummaries,
    required this.cards,
    required this.hasWrongSource,
  });

  final PeriodCoreDto? periodCore;
  final List<PeriodMarkerDto> markers;
  final List<PeriodThemeDto> themes;
  final List<IntentSummaryDto> intentSummaries;
  final List<PeriodCardDto> cards;
  final bool hasWrongSource;

  factory PeriodCalendarDto.fromMap(Map<String, dynamic> map) {
    final publicRaw = map['public'] is Map
        ? Map<String, dynamic>.from(map['public'] as Map)
        : map;

    final periodCore = publicRaw['period_core'] is Map
        ? PeriodCoreDto.fromMap(
            Map<String, dynamic>.from(publicRaw['period_core'] as Map),
          )
        : null;

    final markers = <PeriodMarkerDto>[];
    final markerRaw = publicRaw['markers'] ?? publicRaw['period_markers'];
    if (markerRaw is List) {
      for (final item in markerRaw) {
        if (item is! Map) {
          continue;
        }
        markers.add(PeriodMarkerDto.fromMap(Map<String, dynamic>.from(item)));
      }
    }

    final themes = <PeriodThemeDto>[];
    final themeRaw = publicRaw['themes'];
    if (themeRaw is List) {
      for (var i = 0; i < themeRaw.length; i++) {
        final item = themeRaw[i];
        if (item is! Map) {
          continue;
        }
        themes.add(
          PeriodThemeDto.fromMap(Map<String, dynamic>.from(item), index: i),
        );
      }
    }

    final intentSummaries = <IntentSummaryDto>[];
    final intentRaw = publicRaw['intent_summary'];
    if (intentRaw is Map) {
      var index = 0;
      for (final entry in intentRaw.entries) {
        if (entry.value is! Map) {
          continue;
        }
        intentSummaries.add(
          IntentSummaryDto.fromMap(
            entry.key.toString(),
            Map<String, dynamic>.from(entry.value as Map),
            index: index,
          ),
        );
        index += 1;
      }
    }

    if (markers.isEmpty && periodCore != null) {
      final featured = publicRaw['period_core'] is Map
          ? (Map<String, dynamic>.from(
              publicRaw['period_core'] as Map,
            ))['featured_events']
          : null;
      if (featured is List) {
        for (final item in featured) {
          if (item is! Map) {
            continue;
          }
          final mapItem = Map<String, dynamic>.from(item);
          final interpretation = mapItem['interpretation'] is Map
              ? Map<String, dynamic>.from(mapItem['interpretation'] as Map)
              : const <String, dynamic>{};
          final timing = mapItem['timing'] is Map
              ? Map<String, dynamic>.from(mapItem['timing'] as Map)
              : const <String, dynamic>{};
          markers.add(
            PeriodMarkerDto(
              id: (mapItem['event_id'] ?? '').toString().trim(),
              title:
                  (interpretation['headline'] ??
                          interpretation['headline_short'] ??
                          mapItem['label'] ??
                          '')
                      .toString()
                      .trim(),
              summary: (interpretation['summary'] ?? '').toString().trim(),
              timeHint:
                  (interpretation['time_hint'] ??
                          timing['timing_note'] ??
                          mapItem['phase'] ??
                          '')
                      .toString()
                      .trim(),
              raw: mapItem,
            ),
          );
        }
      }
    }

    final cards = <PeriodCardDto>[];
    if (themes.isNotEmpty) {
      cards.addAll([
        for (var i = 0; i < themes.length && i < 4; i++)
          PeriodCardDto.fromTheme(theme: themes[i], index: i),
      ]);
    }
    if (cards.isEmpty && intentSummaries.isNotEmpty) {
      cards.addAll([
        for (var i = 0; i < intentSummaries.length && i < 4; i++)
          PeriodCardDto.fromIntentSummary(
            intentSummary: intentSummaries[i],
            index: i,
          ),
      ]);
    }
    if (cards.isEmpty && periodCore != null) {
      cards.add(
        PeriodCardDto(
          id: 'period-core',
          title: periodCore.title.trim().isNotEmpty
              ? periodCore.title.trim()
              : 'Bu Donemin Ana Temasi',
          subtitle: periodCore.coreStory.trim().isNotEmpty
              ? periodCore.coreStory.trim()
              : 'Bu donem icin period ozeti bulunamadi.',
          timeHint: periodCore.upperMeaning.trim(),
          eventCard: null,
        ),
      );
    }
    if (cards.isEmpty && markers.isNotEmpty) {
      cards.addAll([
        for (var i = 0; i < markers.length && i < 4; i++)
          PeriodCardDto.fromMarker(
            marker: markers[i],
            periodCore: periodCore,
            index: i,
          ),
      ]);
    }

    final hasEventCards =
        publicRaw['event_cards'] is List &&
        (publicRaw['event_cards'] as List).isNotEmpty;
    if (hasEventCards) {
      debugPrint('PeriodCalendarDto ignored event_cards in period source.');
    }
    final hasWrongSource =
        cards.isEmpty &&
        periodCore == null &&
        markers.isEmpty &&
        themes.isEmpty &&
        intentSummaries.isEmpty &&
        hasEventCards;

    return PeriodCalendarDto(
      periodCore: periodCore,
      markers: markers,
      themes: themes,
      intentSummaries: intentSummaries,
      cards: cards,
      hasWrongSource: hasWrongSource,
    );
  }
}
