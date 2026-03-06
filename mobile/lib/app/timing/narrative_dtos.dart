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
    );
  }
}

List<EventCardDto> _parseEventCards(Map<String, dynamic> publicRaw) {
  final raw = publicRaw['event_cards'];

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

  final sample = publicRaw['event_cards_sample'];
  if (sample is List) {
    return [
      for (final card in sample)
        if (card is Map) EventCardDto.fromMap(Map<String, dynamic>.from(card)),
    ];
  }

  return const <EventCardDto>[];
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

class EventCardDto {
  const EventCardDto({
    required this.eventId,
    required this.title,
    required this.signature,
    required this.signatureTr,
    required this.teaser,
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
    required this.derivedContext,
    required this.scene,
    this.periodStory,
    this.storyTrackId,
  });

  final String eventId;
  final String title;
  final String signature;
  final String signatureTr;
  final String teaser;
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
  final Map<String, dynamic> derivedContext;
  final Map<String, dynamic> scene;
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

  factory EventCardDto.fromMap(Map<String, dynamic> map) {
    return EventCardDto(
      eventId: _s(map, 'event_id', 'eventId'),
      title: _s(map, 'title'),
      signature: _s(map, 'signature'),
      signatureTr: _s(map, 'signature_tr', 'signatureTr'),
      teaser: _s(map, 'teaser'),
      horizon: _s(map, 'horizon'),
      tone: _s(map, 'tone'),
      sectionLabels: _labels(map),
      whyNow: _s(map, 'why_now', 'whyNow'),
      conflict: _s(map, 'conflict'),
      shadow: _s(map, 'shadow'),
      upper: _s(map, 'upper', 'upper_meaning'),
      extraLine: _s(map, 'extra_line', 'extraLine'),
      timeHint: _s(map, 'time_hint', 'timeHint'),
      timeHintTr: _s(map, 'time_hint_tr', 'timeHintTr'),
      guidance: _ls(map, 'guidance'),
      watchOut: _ls(map, 'watch_out', 'watchOut'),
      hookTags: _ls(map, 'hook_tags', 'hookTags'),
      derivedContext: map['derived_context'] is Map
          ? Map<String, dynamic>.from(map['derived_context'] as Map)
          : const <String, dynamic>{},
      scene: map['scene'] is Map
          ? Map<String, dynamic>.from(map['scene'] as Map)
          : const <String, dynamic>{},
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
    final id = (map['id'] ??
            map['marker_id'] ??
            map['event_id'] ??
            map['slug'] ??
            map['key'] ??
            '')
        .toString()
        .trim();
    final title = (map['title'] ??
            map['label'] ??
            map['headline'] ??
            map['name'] ??
            '')
        .toString()
        .trim();
    final summary = (map['summary'] ??
            map['subtitle'] ??
            map['description'] ??
            map['core_story'] ??
            '')
        .toString()
        .trim();
    final timing = map['timing'];
    final timeHint = (map['range'] ??
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

  factory PeriodThemeDto.fromMap(Map<String, dynamic> map, {required int index}) {
    final labelPack = map['label_pack'] is Map
        ? Map<String, dynamic>.from(map['label_pack'] as Map)
        : const <String, dynamic>{};
    final id = (map['id'] ??
            map['theme_id'] ??
            map['event_id'] ??
            map['label'] ??
            'theme-$index')
        .toString()
        .trim();
    final title = (map['title'] ??
            map['label'] ??
            labelPack['short'] ??
            labelPack['full'] ??
            'Tema ${index + 1}')
        .toString()
        .trim();
    final summary = (map['summary'] ??
            map['description'] ??
            map['why'] ??
            map['note'] ??
            map['theme'] ??
            '')
        .toString()
        .trim();
    final timeHint = (map['time_hint'] ??
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
    final entries = byDate.entries
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
    final topDates = top.map((entry) => entry.key).where((e) => e.isNotEmpty).toList();
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
    return PeriodCardDto(
      id: eventCard.eventId.isNotEmpty ? eventCard.eventId : 'event-$index',
      title: eventCard.title.trim().isNotEmpty
          ? eventCard.title.trim()
          : 'Period',
      subtitle: eventCard.teaser.trim().isNotEmpty
          ? eventCard.teaser.trim()
          : (eventCard.whyNow.trim().isNotEmpty
                ? eventCard.whyNow.trim()
                : 'Bu donemin ana akisi.'),
      timeHint: eventCard.signatureTr.trim().isNotEmpty
          ? eventCard.signatureTr.trim()
          : (eventCard.timeHintTr.trim().isNotEmpty
                ? eventCard.timeHintTr.trim()
                : eventCard.upper.trim()),
      eventCard: eventCard,
    );
  }

  factory PeriodCardDto.fromMarker({
    required PeriodMarkerDto marker,
    required PeriodCoreDto? periodCore,
    required int index,
  }) {
    final title = marker.title.isNotEmpty
        ? marker.title
        : (periodCore?.title.trim().isNotEmpty == true
              ? periodCore!.title.trim()
              : 'Period');
    final subtitle = marker.summary.isNotEmpty
        ? marker.summary
        : (periodCore?.coreStory.trim().isNotEmpty == true
              ? periodCore!.coreStory.trim()
              : 'Bu donemin ana temasi.');
    final timeHint = marker.timeHint.isNotEmpty
        ? marker.timeHint
        : (periodCore?.upperMeaning.trim().isNotEmpty == true
              ? periodCore!.upperMeaning.trim()
              : '');
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
          PeriodThemeDto.fromMap(
            Map<String, dynamic>.from(item),
            index: i,
          ),
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
          ? (Map<String, dynamic>.from(publicRaw['period_core'] as Map))['featured_events']
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
              title: (interpretation['headline'] ??
                      interpretation['headline_short'] ??
                      mapItem['label'] ??
                      '')
                  .toString()
                  .trim(),
              summary: (interpretation['summary'] ?? '').toString().trim(),
              timeHint: (interpretation['time_hint'] ??
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
