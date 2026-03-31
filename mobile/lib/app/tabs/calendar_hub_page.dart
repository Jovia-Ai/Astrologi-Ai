import 'dart:ui' show lerpDouble;

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/tabs/period_detail_page.dart';
import 'package:mobile/app/tabs/period_marker_detail_page.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/timing/period_peak_timeline_widget.dart';
import 'package:mobile/app/timing/source_guards.dart';
import 'package:mobile/app/timing/transit_repositories.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

enum CalendarViewportMode { month, week }

const List<String> _kCalendarMonthNames = <String>[
  'Ocak',
  'Subat',
  'Mart',
  'Nisan',
  'Mayis',
  'Haziran',
  'Temmuz',
  'Agustos',
  'Eylul',
  'Ekim',
  'Kasim',
  'Aralik',
];

const List<String> _kCalendarWeekdayNames = <String>[
  'Pazartesi',
  'Sali',
  'Carsamba',
  'Persembe',
  'Cuma',
  'Cumartesi',
  'Pazar',
];

const List<String> _kCalendarWeekdayLabels = <String>[
  'Pzt',
  'Sal',
  'Car',
  'Per',
  'Cum',
  'Cmt',
  'Paz',
];

abstract class CalendarDataSource {
  Future<Map<String, dynamic>> fetchDailyNarrative({
    required Map<String, dynamic> profile,
    required DateTime selectedDate,
  });

  Future<Map<String, dynamic>> fetchCalendar({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
    String include = 'markers,themes,intent_summary',
  });

  Future<Map<String, dynamic>> fetchBestTimes({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
  });
}

class NetworkCalendarDataSource implements CalendarDataSource {
  NetworkCalendarDataSource({
    NarrativeRepository? narrativeRepository,
    CalendarRepository? calendarRepository,
  }) : _narrativeRepository = narrativeRepository ?? NarrativeRepository(),
       _calendarRepository = calendarRepository ?? CalendarRepository();

  final NarrativeRepository _narrativeRepository;
  final CalendarRepository _calendarRepository;

  @override
  Future<Map<String, dynamic>> fetchDailyNarrative({
    required Map<String, dynamic> profile,
    required DateTime selectedDate,
  }) {
    return _narrativeRepository.fetchDailyNarrative(
      profile: profile,
      selectedDate: selectedDate,
    );
  }

  @override
  Future<Map<String, dynamic>> fetchCalendar({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
    String include = 'markers,themes,intent_summary',
  }) {
    return _calendarRepository.fetchCalendar(
      profile: profile,
      focusedDate: focusedDate,
      include: include,
    );
  }

  @override
  Future<Map<String, dynamic>> fetchBestTimes({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
  }) {
    return _calendarRepository.fetchBestTimes(
      profile: profile,
      focusedDate: focusedDate,
    );
  }
}

class CalendarDayBundle {
  const CalendarDayBundle({
    required this.date,
    required this.calendarDays,
    required this.selectedDayMeta,
    required this.dailyEventCards,
    required this.periodCards,
    required this.usedPeriodFallback,
    required this.periodOnlyNote,
    required this.markers,
    required this.bestTimes,
    required this.timeline,
    required this.periodCore,
    required this.wrongSource,
  });

  final DateTime date;
  final Map<String, NarrativeCalendarDay> calendarDays;
  final NarrativeCalendarDay? selectedDayMeta;
  final List<EventCardDto> dailyEventCards;
  final List<PeriodCardDto> periodCards;
  final bool usedPeriodFallback;
  final String periodOnlyNote;
  final List<PeriodMarkerDto> markers;
  final List<CalendarBestTimeItem> bestTimes;
  final TimelineDto? timeline;
  final PeriodCoreDto? periodCore;
  final bool wrongSource;

  String get summary {
    final human = _buildDailyHumanCardViewModel(
      card: dailyEventCards.isNotEmpty ? dailyEventCards.first : null,
      dayMeta: selectedDayMeta,
      date: date,
    );
    final heroBody = human.heroBody.trim();
    if (heroBody.isNotEmpty) {
      return _condenseCalendarCopy(heroBody, maxChars: 180);
    }
    final timelineSummary = timeline?.summary.trim() ?? '';
    if (timelineSummary.isNotEmpty) {
      return _condenseCalendarCopy(timelineSummary, maxChars: 180);
    }
    return 'Secili gune dokunup gunun ritmini, kartlarini ve uzun donem etkisini ac.';
  }

  String get headline {
    final human = _buildDailyHumanCardViewModel(
      card: dailyEventCards.isNotEmpty ? dailyEventCards.first : null,
      dayMeta: selectedDayMeta,
      date: date,
    );
    if (human.feltLine.trim().isNotEmpty) {
      return human.feltLine.trim();
    }
    return _formatCalendarDayTitle(date);
  }
}

String _calendarDayKey(DateTime value) =>
    TransitRequestBuilder.fmtDate(TransitRequestBuilder.stripDate(value));

String _formatCalendarMonthTitle(DateTime date) =>
    '${_kCalendarMonthNames[date.month - 1]} ${date.year}';

String _formatCalendarDayTitle(DateTime day) {
  final weekday = _kCalendarWeekdayNames[day.weekday - 1];
  final month = _kCalendarMonthNames[day.month - 1];
  return '$weekday, ${day.day} $month';
}

String _formatCalendarShortWeekday(DateTime day) =>
    _kCalendarWeekdayLabels[day.weekday - 1];

double _calendarWeekAnchorAlignmentY(
  List<DateTime> monthDays,
  DateTime selectedDay,
) {
  final selectedKey = _calendarDayKey(selectedDay);
  final selectedIndex = monthDays.indexWhere(
    (day) => _calendarDayKey(day) == selectedKey,
  );
  if (selectedIndex < 0) {
    return 0;
  }
  final rowCount = (monthDays.length / 7).round();
  if (rowCount <= 1) {
    return 0;
  }
  final rowIndex = selectedIndex ~/ 7;
  return -1 + ((2 * rowIndex) / (rowCount - 1));
}

int _calendarAnchorRowIndex(List<DateTime> monthDays, DateTime selectedDay) {
  final selectedKey = _calendarDayKey(selectedDay);
  final selectedIndex = monthDays.indexWhere(
    (day) => _calendarDayKey(day) == selectedKey,
  );
  if (selectedIndex < 0) {
    return 0;
  }
  return selectedIndex ~/ 7;
}

List<List<DateTime>> _calendarWeekRows(List<DateTime> monthDays) {
  final rows = <List<DateTime>>[];
  for (var index = 0; index < monthDays.length; index += 7) {
    rows.add(monthDays.sublist(index, index + 7));
  }
  return rows;
}

String _condenseCalendarCopy(String text, {int maxChars = 220}) {
  final trimmed = text.trim();
  if (trimmed.isEmpty) {
    return '';
  }
  if (trimmed.length <= maxChars) {
    return trimmed;
  }
  return '${trimmed.substring(0, maxChars).trimRight()}...';
}

class _DailyHumanCardViewModel {
  const _DailyHumanCardViewModel({
    required this.feltLine,
    required this.whyLine,
    required this.guidanceLine,
    required this.signalLabel,
    required this.toneLabel,
    required this.houseTouchpointHint,
    required this.isCritical,
  });

  final String feltLine;
  final String whyLine;
  final String guidanceLine;
  final String signalLabel;
  final String toneLabel;
  final String houseTouchpointHint;
  final bool isCritical;

  String get heroBody => [
    whyLine.trim(),
    guidanceLine.trim(),
  ].where((line) => line.isNotEmpty).join('\n');

  String get cardBody => [
    whyLine.trim(),
    guidanceLine.trim(),
  ].where((line) => line.isNotEmpty).join('\n');

  List<String> get meta => [
    if (houseTouchpointHint.trim().isNotEmpty) houseTouchpointHint.trim(),
  ];
}

class _EventCardSelectionResult {
  const _EventCardSelectionResult({
    required this.dailyCards,
    required this.periodCards,
    required this.usedPeriodFallback,
    required this.periodOnlyNote,
  });

  final List<EventCardDto> dailyCards;
  final List<EventCardDto> periodCards;
  final bool usedPeriodFallback;
  final String periodOnlyNote;
}

String _firstNonEmpty(Iterable<String?> values) {
  for (final value in values) {
    final trimmed = value?.trim() ?? '';
    if (trimmed.isNotEmpty) {
      return trimmed;
    }
  }
  return '';
}

bool _looksTechnicalAstroCopy(String text) {
  final normalized = text.trim().toLowerCase();
  if (normalized.isEmpty) {
    return false;
  }
  const blockedFragments = <String>[
    '↔',
    'square',
    'trine',
    'opposition',
    'conjunction',
    'moon',
    'sun',
    'mercury',
    'venus',
    'mars',
    'saturn',
    'uranus',
    'neptune',
    'pluto',
    'güneş',
    'ay ',
    'merkür',
    'venüs',
    'mars',
    'satürn',
    'uranüs',
    'neptün',
    'plüton',
    '. ev',
    ' evde',
    'kare',
    'karşıt',
    'üçgen',
    'ucgen',
    'kavuşum',
    'kavusum',
    'ekseni',
    'gerilim',
    'dinamik',
    'mekanizma',
    'enerji',
    'süreç',
    'surec',
    'denge',
  ];
  for (final fragment in blockedFragments) {
    if (normalized.contains(fragment)) {
      return true;
    }
  }
  return false;
}

String _safeHumanLine(String text) {
  final trimmed = text.trim();
  if (trimmed.isEmpty || _looksTechnicalAstroCopy(trimmed)) {
    return '';
  }
  return _condenseCalendarCopy(trimmed, maxChars: 120);
}

String _fallbackSignalLabel(NarrativeCalendarDay? dayMeta) {
  if (dayMeta == null) {
    return '';
  }
  if (dayMeta.isCritical) {
    return 'Hassas gün.';
  }
  if (dayMeta.heat >= 3 || dayMeta.signalsCount >= 4) {
    return 'Yüksek tempo.';
  }
  if (dayMeta.signalsCount >= 3) {
    return 'Bugün yoğun.';
  }
  if (dayMeta.signalsCount == 2) {
    return 'Bugün iki şey belirgin.';
  }
  if (dayMeta.signalsCount == 1) {
    return 'Tek bir şey öne çıkıyor.';
  }
  if (dayMeta.heat >= 2 && dayMeta.eventCount == 0) {
    return 'Bugün biraz karışık.';
  }
  return 'Bugün sakin.';
}

String _fallbackWhyLine(NarrativeCalendarDay? dayMeta) {
  if (dayMeta?.isCritical == true) {
    return 'Bir şeylere bugün çabuk takılabilirsin.';
  }
  if ((dayMeta?.signalsCount ?? 0) >= 3) {
    return 'Aynı anda birkaç şey dikkatini çekebilir.';
  }
  if ((dayMeta?.signalsCount ?? 0) >= 1) {
    return 'Tek bir şey günün ritmini biraz öne itiyor.';
  }
  return 'Bugün ritim biraz daha sade akıyor.';
}

String _fallbackGuidanceLine(NarrativeCalendarDay? dayMeta) {
  if (dayMeta?.isCritical == true) {
    return 'Bir nefes daha iyi gelir.';
  }
  if ((dayMeta?.signalsCount ?? 0) >= 3) {
    return 'Her şeye aynı anda yüklenme.';
  }
  if ((dayMeta?.signalsCount ?? 0) >= 1) {
    return 'Acele etme.';
  }
  return 'Bugünü biraz sade bırak.';
}

_DailyHumanCardViewModel _buildDailyHumanCardViewModel({
  EventCardDto? card,
  NarrativeCalendarDay? dayMeta,
  required DateTime date,
}) {
  final feltLine = _firstNonEmpty([
    card?.feltLineTr,
    _safeHumanLine(card?.headline ?? ''),
    _safeHumanLine(card?.title ?? ''),
    dayMeta?.microSummaryTr,
    _fallbackSignalLabel(dayMeta),
    _formatCalendarDayTitle(date),
  ]);
  final whyLine = _firstNonEmpty([
    card?.whyItFeelsThisWayTr,
    _safeHumanLine(card?.opening ?? ''),
    _safeHumanLine(card?.whyNow ?? ''),
    _fallbackWhyLine(dayMeta),
  ]);
  final guidanceLine = _firstNonEmpty([
    card?.guidanceMicroTr,
    if ((card?.guidance ?? const <String>[]).isNotEmpty)
      _safeHumanLine(card!.guidance.first),
    if ((card?.watchOut ?? const <String>[]).isNotEmpty)
      _safeHumanLine(card!.watchOut.first),
    _fallbackGuidanceLine(dayMeta),
  ]);
  final signalLabel = _firstNonEmpty([
    card?.signalLabelTr,
    dayMeta?.signalLabelTr,
    _fallbackSignalLabel(dayMeta),
  ]);
  final toneLabel = _firstNonEmpty([card?.toneLabelTr, dayMeta?.toneLabelTr]);
  final houseTouchpointHint = _firstNonEmpty([
    card?.houseTouchpointHintTr,
    if ((card?.houseTouchpointTr ?? '').trim().isNotEmpty)
      'En çok ${card!.houseTouchpointTr.trim()} tarafında belli olabilir.',
  ]);
  return _DailyHumanCardViewModel(
    feltLine: feltLine,
    whyLine: whyLine,
    guidanceLine: guidanceLine,
    signalLabel: signalLabel,
    toneLabel: toneLabel,
    houseTouchpointHint: houseTouchpointHint,
    isCritical: dayMeta?.isCritical == true,
  );
}

double _scoreEventCardForToday(EventCardDto card, DateTime selectedDate) {
  var score = 0.0;

  if (card.eventFamily == 'lunation_trigger' ||
      card.eventFamily == 'eclipse_trigger') {
    score += 38;
  }

  score += switch (card.transitBody.trim().toLowerCase()) {
    'moon' => 24,
    'sun' => 18,
    'mercury' => 16,
    'mars' => 16,
    'venus' => 10,
    _ => 0,
  };

  score += switch (card.aspect.trim().toLowerCase()) {
    'opposition' => 18,
    'square' => 18,
    'conjunction' => 15,
    'quincunx' => 13,
    'trine' => 10,
    'sextile' => 8,
    _ => 6,
  };

  final orb = card.orbDeg;
  if (orb != null) {
    score += (20 - (orb * 5)).clamp(0, 20).toDouble();
  }

  final exactInDays = card.tags.exactInDays;
  if (exactInDays != null) {
    score += switch (exactInDays) {
      0 => 18,
      1 => 12,
      2 => 6,
      _ => exactInDays >= 5 ? 0 : 4,
    };
  }

  final phase = card.phase.trim().toLowerCase();
  if (phase == 'exact' || phase == 'exactish') {
    score += 16;
  } else if (phase == 'applying') {
    score += 8;
  }

  if (const {
    'asc',
    'dsc',
    'mc',
    'ic',
  }.contains(card.natalPoint.trim().toLowerCase())) {
    score += 14;
  }

  if (card.natalPromiseScore != null) {
    score += card.natalPromiseScore!.clamp(0, 1) * 14;
  }
  score += card.tags.intensity.clamp(0, 1) * 8;

  int? dayDelta(String raw) {
    final value = raw.trim();
    if (value.length < 10) {
      return null;
    }
    final parsed = DateTime.tryParse(value.substring(0, 10));
    if (parsed == null) {
      return null;
    }
    final normalizedSelected = DateTime(
      selectedDate.year,
      selectedDate.month,
      selectedDate.day,
    );
    return parsed.difference(normalizedSelected).inDays.abs();
  }

  for (final entry in <({String raw, double exact, double near})>[
    (raw: card.timing.peakDateUtc, exact: 16, near: 8),
    (raw: card.timing.entryDateUtc, exact: 10, near: 4),
  ]) {
    final delta = dayDelta(entry.raw);
    if (delta == null) {
      continue;
    }
    if (delta == 0) {
      score += entry.exact;
    } else if (delta == 1) {
      score += entry.near;
    }
  }

  if (card.horizon.trim().toLowerCase() == 'daily') {
    score += 18;
  }
  if (card.bucket.trim().toLowerCase() == 'short') {
    score += 12;
  }

  score += switch (card.importanceTier.trim().toLowerCase()) {
    'critical' => 10,
    'high' => 6,
    _ => 0,
  };

  return score;
}

EventCardDto _convertPeriodToDaily(EventCardDto card, DateTime selectedDate) {
  final fallbackHuman = _buildDailyHumanCardViewModel(
    card: card,
    dayMeta: null,
    date: selectedDate,
  );
  return card.copyWith(
    horizon: 'daily',
    signalLabelTr: card.signalLabelTr.trim().isNotEmpty
        ? card.signalLabelTr
        : 'Bugün en çok bu öne çıkıyor.',
    feltLineTr: card.feltLineTr.trim().isNotEmpty
        ? card.feltLineTr
        : fallbackHuman.feltLine,
    whyItFeelsThisWayTr: card.whyItFeelsThisWayTr.trim().isNotEmpty
        ? card.whyItFeelsThisWayTr
        : fallbackHuman.whyLine,
    guidanceMicroTr: card.guidanceMicroTr.trim().isNotEmpty
        ? card.guidanceMicroTr
        : fallbackHuman.guidanceLine,
  );
}

_EventCardSelectionResult _deriveEventCardSelection({
  required NarrativeResponse narrative,
  required DateTime selectedDate,
}) {
  if (narrative.dailyEventCards.isNotEmpty ||
      narrative.periodEventCards.isNotEmpty) {
    return _EventCardSelectionResult(
      dailyCards: narrative.dailyEventCards,
      periodCards: narrative.periodEventCards,
      usedPeriodFallback: narrative.dailySelection?.usedPeriodFallback == true,
      periodOnlyNote: narrative.dailySelection?.periodOnlyNote.trim() ?? '',
    );
  }

  final scored = [
    for (final card in narrative.eventCards)
      (card: card, score: _scoreEventCardForToday(card, selectedDate)),
  ]..sort((a, b) => b.score.compareTo(a.score));

  final dailyCards = <EventCardDto>[
    for (final entry in scored)
      if (entry.card.horizon.trim().toLowerCase() != 'period') entry.card,
  ].take(2).toList(growable: false);
  final periodCards = <EventCardDto>[
    for (final entry in scored)
      if (entry.card.horizon.trim().toLowerCase() == 'period') entry.card,
  ].take(3).toList(growable: false);

  if (dailyCards.isNotEmpty) {
    return _EventCardSelectionResult(
      dailyCards: dailyCards,
      periodCards: periodCards,
      usedPeriodFallback: false,
      periodOnlyNote: '',
    );
  }
  if (periodCards.isNotEmpty) {
    return _EventCardSelectionResult(
      dailyCards: <EventCardDto>[
        _convertPeriodToDaily(periodCards.first, selectedDate),
      ],
      periodCards: periodCards,
      usedPeriodFallback: true,
      periodOnlyNote:
          'Bugün kısa vadeli bir tetikten çok, arkada çalışan tema öne çıkıyor.',
    );
  }
  return const _EventCardSelectionResult(
    dailyCards: <EventCardDto>[],
    periodCards: <EventCardDto>[],
    usedPeriodFallback: false,
    periodOnlyNote: '',
  );
}

List<CalendarBestTimeItem> _extractBestTimesFromNarrativePayload(
  Map<String, dynamic> data,
) {
  final out = <CalendarBestTimeItem>[];
  final publicRaw = data['public'] is Map
      ? Map<String, dynamic>.from(data['public'] as Map)
      : data;

  List<dynamic>? pickList(dynamic raw) => raw is List ? raw : null;

  final direct =
      pickList(publicRaw['best_times']) ??
      pickList(publicRaw['featured_windows']);
  if (direct != null) {
    for (final row in direct) {
      if (row is! Map) {
        continue;
      }
      final mapRow = Map<String, dynamic>.from(row);
      final label =
          (mapRow['label'] ??
                  mapRow['title'] ??
                  mapRow['time_label'] ??
                  mapRow['window'] ??
                  mapRow['date'] ??
                  '')
              .toString()
              .trim();
      final reason =
          (mapRow['focus'] ?? mapRow['theme'] ?? mapRow['reason'] ?? '')
              .toString()
              .trim();
      if (label.isEmpty && reason.isEmpty) {
        continue;
      }
      out.add(
        CalendarBestTimeItem(
          label: reason.isEmpty ? label : '$label • $reason',
        ),
      );
    }
    if (out.isNotEmpty) {
      return out.take(6).toList(growable: false);
    }
  }

  final narrative = NarrativeResponse.fromMap(data);
  final primary = narrative.blocks.where((b) => b.type == 'best_time_primary');
  for (final block in primary) {
    final date = (block.meta['date'] ?? '').toString().trim();
    final score = (block.meta['score'] ?? '').toString().trim();
    final label = date.isNotEmpty ? date : block.copy.title.trim();
    final detail = block.copy.short.trim().isNotEmpty
        ? block.copy.short.trim()
        : score;
    if (label.isEmpty && detail.isEmpty) {
      continue;
    }
    out.add(
      CalendarBestTimeItem(label: detail.isEmpty ? label : '$label • $detail'),
    );
  }
  final lists = narrative.blocks.where((b) => b.type == 'best_time_list');
  for (final block in lists) {
    final candidates = block.meta['candidates'];
    if (candidates is! List) {
      continue;
    }
    for (final row in candidates.take(6)) {
      if (row is! Map) {
        continue;
      }
      final mapRow = Map<String, dynamic>.from(row);
      final date = (mapRow['date'] ?? '').toString().trim();
      final score = (mapRow['score'] ?? '').toString().trim();
      if (date.isEmpty && score.isEmpty) {
        continue;
      }
      out.add(
        CalendarBestTimeItem(
          label: score.isEmpty ? date : '$date • skor $score',
        ),
      );
    }
  }
  return out.take(6).toList(growable: false);
}

List<CalendarBestTimeItem> _extractBestTimesFromBestTimesPayload(
  Map<String, dynamic> data,
) {
  final out = <CalendarBestTimeItem>[];
  final list = (data['best_times'] is List)
      ? (data['best_times'] as List)
      : (data['windows'] is List)
      ? (data['windows'] as List)
      : (data['candidates'] is List)
      ? (data['candidates'] as List)
      : const <dynamic>[];
  for (final row in list) {
    if (row is! Map) {
      continue;
    }
    final mapRow = Map<String, dynamic>.from(row);
    final label =
        (mapRow['label'] ??
                mapRow['time_label'] ??
                mapRow['window'] ??
                mapRow['date'] ??
                '')
            .toString()
            .trim();
    final focus = (mapRow['focus'] ?? mapRow['reason'] ?? mapRow['theme'] ?? '')
        .toString()
        .trim();
    if (label.isEmpty && focus.isEmpty) {
      continue;
    }
    out.add(
      CalendarBestTimeItem(label: focus.isEmpty ? label : '$label • $focus'),
    );
  }
  return out.take(6).toList(growable: false);
}

Future<CalendarDayBundle> _loadCalendarDayBundle({
  required CalendarDataSource dataSource,
  required Map<String, dynamic> profile,
  required DateTime selectedDay,
}) async {
  final normalizedDate = TransitRequestBuilder.stripDate(selectedDay);
  final responses = await Future.wait<Map<String, dynamic>>([
    dataSource.fetchDailyNarrative(
      profile: profile,
      selectedDate: normalizedDate,
    ),
    dataSource.fetchCalendar(
      profile: profile,
      focusedDate: normalizedDate,
      include: 'markers',
    ),
  ]);
  final narrativeMap = responses[0];
  final narrative = NarrativeResponse.fromMap(narrativeMap);
  final periodCalendar = PeriodCalendarDto.fromMap(responses[1]);
  final narrativeBest = _extractBestTimesFromNarrativePayload(narrativeMap);
  final fallbackBest = narrativeBest.isNotEmpty
      ? const <CalendarBestTimeItem>[]
      : _extractBestTimesFromBestTimesPayload(
          await dataSource.fetchBestTimes(
            profile: profile,
            focusedDate: normalizedDate,
          ),
        );
  final selection = _deriveEventCardSelection(
    narrative: narrative,
    selectedDate: normalizedDate,
  );
  final dailyCards = selection.dailyCards;
  final periodCards = <PeriodCardDto>[
    for (var index = 0; index < selection.periodCards.length; index++)
      PeriodCardDto.fromEventCard(
        eventCard: selection.periodCards[index],
        index: index,
      ),
  ];
  final periodInNarrative =
      selection.periodCards.isNotEmpty && selection.dailyCards.isEmpty;
  return CalendarDayBundle(
    date: normalizedDate,
    calendarDays: narrative.calendarDays,
    selectedDayMeta: narrative.calendarDays[_calendarDayKey(normalizedDate)],
    dailyEventCards: dailyCards,
    periodCards: periodCards,
    usedPeriodFallback: selection.usedPeriodFallback,
    periodOnlyNote: selection.periodOnlyNote,
    markers: periodCalendar.markers,
    bestTimes: narrativeBest.isNotEmpty ? narrativeBest : fallbackBest,
    timeline: narrative.timeline,
    periodCore: narrative.periodCore ?? periodCalendar.periodCore,
    wrongSource:
        (periodInNarrative || dailyCards.isEmpty) &&
        periodCards.isEmpty &&
        narrative.periodCore == null,
  );
}

class CalendarHubPage extends ConsumerStatefulWidget {
  const CalendarHubPage({
    super.key,
    this.profileOverride,
    this.dataSource,
    this.initialSelectedDay,
    this.initialViewportMode = CalendarViewportMode.month,
  });

  final Map<String, dynamic>? profileOverride;
  final CalendarDataSource? dataSource;
  final DateTime? initialSelectedDay;
  final CalendarViewportMode initialViewportMode;

  @override
  ConsumerState<CalendarHubPage> createState() => _CalendarHubPageState();
}

class _CalendarHubPageState extends ConsumerState<CalendarHubPage>
    with TickerProviderStateMixin {
  late DateTime _selectedDay;
  late CalendarViewportMode _viewportMode;
  late final CalendarDataSource _dataSource;

  bool _loading = false;
  String? _error;
  CalendarDayBundle? _bundle;
  String? _lastProfileKey;

  @override
  void initState() {
    super.initState();
    _selectedDay = TransitRequestBuilder.stripDate(
      widget.initialSelectedDay ?? DateTime.now(),
    );
    _viewportMode = widget.initialViewportMode;
    _dataSource = widget.dataSource ?? NetworkCalendarDataSource();
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    final profileAsync = widget.profileOverride == null
        ? ref.watch(userProfileProvider)
        : const AsyncValue<Map<String, dynamic>?>.data(null);
    final profileMap = widget.profileOverride ?? profileAsync.valueOrNull;
    _maybeBootstrap(profileMap);

    return Scaffold(
      backgroundColor: profile.colors.bg,
      appBar: AppBar(
        leadingWidth: 52,
        leading: Padding(
          padding: const EdgeInsets.only(left: 12),
          child: JoviaGlassIconButton(
            onTap: () => Navigator.of(context).maybePop(),
            child: const JoviaUiIcon(asset: JoviaUiAsset.back, size: 18),
          ),
        ),
        title: Text(
          'TAKVIM',
          style: profile.typography.navigationLabel(color: profile.colors.text),
        ),
      ),
      body: _buildBody(
        context: context,
        profileMap: profileMap,
        profileAsync: profileAsync,
        spacing: spacing,
      ),
    );
  }

  Widget _buildBody({
    required BuildContext context,
    required Map<String, dynamic>? profileMap,
    required AsyncValue<Map<String, dynamic>?> profileAsync,
    required dynamic spacing,
  }) {
    final profile = context.profileTheme;
    if (profileAsync.isLoading && profileMap == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (profileAsync.hasError && profileMap == null) {
      return const _ErrorText('Profil verisi yuklenemedi.');
    }
    if (!TransitRequestBuilder.hasProfile(profileMap)) {
      return const _ErrorText(
        'Takvim icin once profil dogum verisini tamamlayin.',
      );
    }

    return SafeArea(
      top: false,
      child: JoviaPageScaffold(
        padding: EdgeInsets.fromLTRB(
          spacing.pageHorizontal,
          spacing.xs,
          spacing.pageHorizontal,
          spacing.pageBottom,
        ),
        child: RefreshIndicator(
          onRefresh: () => _loadBundle(profileMap!),
          child: ListView(
            padding: EdgeInsets.zero,
            physics: const AlwaysScrollableScrollPhysics(),
            children: [
              const JoviaSectionHeader(
                label: 'Timing',
                title: 'Birlesik takvim',
                body:
                    'Ay ve hafta akisini ayni yuzde takip et. Bir gune dokundugunda o gunun sayfasi acilir; uzun donem etkisi baglam olarak korunur.',
                variant: JoviaSectionHeaderVariant.editorial,
              ),
              SizedBox(height: spacing.sectionToContent),
              _CalendarViewportSwitch(
                mode: _viewportMode,
                onChanged: (mode) => setState(() => _viewportMode = mode),
              ),
              SizedBox(height: spacing.majorSectionGap),
              _UnifiedCalendarPanel(
                selectedDay: _selectedDay,
                viewportMode: _viewportMode,
                calendarDays:
                    _bundle?.calendarDays ??
                    const <String, NarrativeCalendarDay>{},
                onPickDate: () => _showDatePicker(profileMap!),
                onShiftBackward: () => _shiftViewport(profileMap!, -1),
                onShiftForward: () => _shiftViewport(profileMap!, 1),
                onOpenDay: (day) => _openDayPage(profileMap!, day),
              ),
              if (_loading) ...[
                SizedBox(height: spacing.sectionToContent),
                const LinearProgressIndicator(),
              ],
              if (_error != null) ...[
                SizedBox(height: spacing.sectionToContent),
                Text(
                  _error!,
                  style: profile.typography.meta.copyWith(
                    color: Theme.of(context).colorScheme.error,
                  ),
                ),
              ],
              SizedBox(height: spacing.majorSectionGap),
              _SelectedDayHeroCard(
                day: _selectedDay,
                bundle: _bundle,
                onOpenDay: () => _openDayPage(profileMap!, _selectedDay),
              ),
              if ((_bundle?.periodCore != null ||
                  (_bundle?.periodCards.isNotEmpty ?? false))) ...[
                SizedBox(height: spacing.majorSectionGap),
                _LongTermEffectBand(
                  periodCore: _bundle?.periodCore,
                  periodCards: _bundle?.periodCards ?? const <PeriodCardDto>[],
                  onOpenPeriodCard: _openPeriodCardDetail,
                ),
              ],
              if (_bundle != null && _bundle!.bestTimes.isNotEmpty) ...[
                SizedBox(height: spacing.majorSectionGap),
                JoviaReadingPanel(
                  label: 'Timing',
                  title: 'Secili gun pencereleri',
                  child: Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      for (final item in _bundle!.bestTimes)
                        _CalendarInfoPill(label: item.label, highlighted: true),
                    ],
                  ),
                ),
              ],
              if (kDebugMode && (_bundle?.wrongSource ?? false))
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text(
                    'Data mismatch: wrong source',
                    style: profile.typography.meta.copyWith(
                      color: Colors.orange,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _showDatePicker(Map<String, dynamic> profile) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDay,
      firstDate: DateTime.now().subtract(const Duration(days: 365 * 2)),
      lastDate: DateTime.now().add(const Duration(days: 365 * 2)),
    );
    if (picked == null) {
      return;
    }
    final normalized = TransitRequestBuilder.stripDate(picked);
    setState(() => _selectedDay = normalized);
    await _loadBundle(profile);
  }

  Future<void> _shiftViewport(Map<String, dynamic> profile, int delta) async {
    late final DateTime next;
    if (_viewportMode == CalendarViewportMode.month) {
      final targetMonth = DateTime(
        _selectedDay.year,
        _selectedDay.month + delta,
      );
      final lastDay = DateTime(targetMonth.year, targetMonth.month + 1, 0).day;
      next = DateTime(
        targetMonth.year,
        targetMonth.month,
        _selectedDay.day.clamp(1, lastDay),
      );
    } else {
      next = TransitRequestBuilder.stripDate(
        _selectedDay.add(Duration(days: delta * 7)),
      );
    }
    setState(() => _selectedDay = next);
    await _loadBundle(profile);
  }

  Future<void> _openDayPage(Map<String, dynamic> profile, DateTime day) async {
    final normalized = TransitRequestBuilder.stripDate(day);
    setState(() => _selectedDay = normalized);
    final initialBundle =
        _bundle != null &&
            _calendarDayKey(_bundle!.date) == _calendarDayKey(normalized)
        ? _bundle
        : null;
    final returnedDate = await Navigator.of(context, rootNavigator: true)
        .push<DateTime>(
          MaterialPageRoute<DateTime>(
            builder: (_) => CalendarDayPage(
              profile: profile,
              initialDate: normalized,
              initialBundle: initialBundle,
              dataSource: _dataSource,
              source: 'calendar_hub',
            ),
          ),
        );
    if (returnedDate == null) {
      if (_bundle == null ||
          _calendarDayKey(_bundle!.date) != _calendarDayKey(_selectedDay)) {
        await _loadBundle(profile);
      }
      return;
    }
    final resolvedDate = TransitRequestBuilder.stripDate(returnedDate);
    if (_calendarDayKey(resolvedDate) == _calendarDayKey(_selectedDay) &&
        _bundle != null &&
        _calendarDayKey(_bundle!.date) == _calendarDayKey(resolvedDate)) {
      return;
    }
    setState(() => _selectedDay = resolvedDate);
    await _loadBundle(profile);
  }

  void _openPeriodCardDetail(PeriodCardDto card) {
    Navigator.of(context, rootNavigator: true).push(
      MaterialPageRoute<void>(
        builder: (_) => PeriodDetailPage(
          card: card,
          periodCore: _bundle?.periodCore,
          routeSource: 'calendar_hub_long_term',
        ),
      ),
    );
  }

  void _maybeBootstrap(Map<String, dynamic>? profile) {
    if (!TransitRequestBuilder.hasProfile(profile)) {
      return;
    }
    final key =
        '${profile?['birth_date']}|${profile?['birth_time']}|${profile?['place'] ?? profile?['city']}|${profile?['timezone']}|${_calendarDayKey(_selectedDay)}';
    if (_lastProfileKey == key) {
      return;
    }
    _lastProfileKey = key;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || profile == null) {
        return;
      }
      _loadBundle(profile);
    });
  }

  Future<void> _loadBundle(Map<String, dynamic> profile) async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final bundle = await _loadCalendarDayBundle(
        dataSource: _dataSource,
        profile: profile,
        selectedDay: _selectedDay,
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _bundle = bundle;
        _loading = false;
      });
    } on DioException catch (exc) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _error = exc.response?.statusCode == 422
            ? 'Gonderilen tarih/alanlar gecersiz (422).'
            : (exc.message ?? 'Takvim verisi alinamadi.');
      });
    } catch (exc) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _error = exc.toString();
      });
    }
  }
}

class _CalendarViewportSwitch extends StatelessWidget {
  const _CalendarViewportSwitch({required this.mode, required this.onChanged});

  final CalendarViewportMode mode;
  final ValueChanged<CalendarViewportMode> onChanged;

  @override
  Widget build(BuildContext context) {
    return JoviaSegmentedControl<CalendarViewportMode>(
      value: mode,
      options: CalendarViewportMode.values,
      labelBuilder: (mode) => switch (mode) {
        CalendarViewportMode.month => 'Ay',
        CalendarViewportMode.week => 'Hafta',
      },
      onChanged: onChanged,
    );
  }
}

class _UnifiedCalendarPanel extends StatelessWidget {
  const _UnifiedCalendarPanel({
    required this.selectedDay,
    required this.viewportMode,
    required this.calendarDays,
    required this.onPickDate,
    required this.onShiftBackward,
    required this.onShiftForward,
    required this.onOpenDay,
  });

  final DateTime selectedDay;
  final CalendarViewportMode viewportMode;
  final Map<String, NarrativeCalendarDay> calendarDays;
  final VoidCallback onPickDate;
  final VoidCallback onShiftBackward;
  final VoidCallback onShiftForward;
  final ValueChanged<DateTime> onOpenDay;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final visibleDays = _monthVisibleDays();
    final weekRows = _calendarWeekRows(visibleDays);
    final isMonth = viewportMode == CalendarViewportMode.month;
    final rowCount = (visibleDays.length / 7).round().clamp(1, 6);
    final anchorRowIndex = _calendarAnchorRowIndex(visibleDays, selectedDay);
    final anchorY = _calendarWeekAnchorAlignmentY(visibleDays, selectedDay);

    return JoviaReadingPanel(
      label: 'Calendar',
      title: isMonth
          ? _formatCalendarMonthTitle(selectedDay)
          : '${_formatCalendarMonthTitle(selectedDay)} • Hafta',
      body: isMonth
          ? 'Ay gorunumunden bir gune dokunup o gunun sayfasina gec.'
          : 'Hafta gorunumunde secili haftaya odaklan, gunu acip detayda sag-sol ilerle.',
      large: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              JoviaGlassIconButton(
                onTap: onShiftBackward,
                child: const JoviaUiIcon(asset: JoviaUiAsset.back, size: 18),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  isMonth
                      ? _formatCalendarMonthTitle(selectedDay)
                      : _formatCalendarDayTitle(selectedDay),
                  textAlign: TextAlign.center,
                  style: profile.typography.cardTitle.copyWith(
                    color: profile.colors.text,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              JoviaGlassIconButton(
                onTap: onShiftForward,
                child: const JoviaUiIcon(
                  asset: JoviaUiAsset.chevronRight,
                  size: 18,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Align(
            alignment: Alignment.centerLeft,
            child: _CalendarActionChip(label: 'Tarih sec', onTap: onPickDate),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              for (final label in _kCalendarWeekdayLabels)
                Expanded(
                  child: Center(
                    child: Text(
                      label,
                      style: profile.typography.eyebrow.copyWith(
                        color: profile.colors.textLight,
                      ),
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 10),
          TweenAnimationBuilder<double>(
            tween: Tween<double>(end: isMonth ? 0 : 1),
            duration: const Duration(milliseconds: 400),
            curve: Curves.easeInOutCubic,
            builder: (context, progress, _) {
              final heightFactor = lerpDouble(1, 1 / rowCount, progress) ?? 1;
              final alignmentY = lerpDouble(0, anchorY, progress) ?? 0;
              return ClipRect(
                child: Align(
                  alignment: Alignment(0, alignmentY),
                  heightFactor: heightFactor,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      for (
                        var rowIndex = 0;
                        rowIndex < weekRows.length;
                        rowIndex++
                      )
                        _AnimatedCalendarWeekRow(
                          days: weekRows[rowIndex],
                          calendarDays: calendarDays,
                          selectedDay: selectedDay,
                          isAnchorRow: rowIndex == anchorRowIndex,
                          rowDistance: (rowIndex - anchorRowIndex).abs(),
                          collapseTowardTop: rowIndex > anchorRowIndex,
                          collapseProgress: progress,
                          bottomSpacing: rowIndex == weekRows.length - 1
                              ? 0
                              : 8,
                          onOpenDay: onOpenDay,
                        ),
                    ],
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  List<DateTime> _monthVisibleDays() {
    final firstDay = DateTime(selectedDay.year, selectedDay.month, 1);
    final firstWeekday = firstDay.weekday;
    final gridStart = firstDay.subtract(Duration(days: firstWeekday - 1));
    final daysInMonth = DateTime(
      selectedDay.year,
      selectedDay.month + 1,
      0,
    ).day;
    final totalCells = ((firstWeekday - 1 + daysInMonth + 6) ~/ 7) * 7;
    return List<DateTime>.generate(
      totalCells,
      (index) =>
          TransitRequestBuilder.stripDate(gridStart.add(Duration(days: index))),
    );
  }
}

class _SelectedDayHeroCard extends StatelessWidget {
  const _SelectedDayHeroCard({
    required this.day,
    required this.bundle,
    required this.onOpenDay,
  });

  final DateTime day;
  final CalendarDayBundle? bundle;
  final VoidCallback onOpenDay;

  @override
  Widget build(BuildContext context) {
    final dayMeta = bundle?.selectedDayMeta;
    final human = _buildDailyHumanCardViewModel(
      card: bundle?.dailyEventCards.isNotEmpty == true
          ? bundle!.dailyEventCards.first
          : null,
      dayMeta: dayMeta,
      date: day,
    );
    return JoviaEditorialHeroBlock(
      label: 'Gunun temasi',
      title: human.feltLine,
      body: human.heroBody.isNotEmpty
          ? human.heroBody
          : (bundle?.summary ??
                'Bir gune dokundugunda o gunun kartlari, markerlari ve uzun donem baglami ayrintili acilir.'),
      large: true,
      footer: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _CalendarInfoPill(
                label: '${day.day} ${_kCalendarMonthNames[day.month - 1]}',
                highlighted: true,
              ),
              if (human.signalLabel.isNotEmpty)
                _CalendarInfoPill(
                  label: human.signalLabel,
                  highlighted: human.isCritical,
                ),
            ],
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: JoviaPrimaryButton(label: 'Gunu ac', onTap: onOpenDay),
          ),
        ],
      ),
    );
  }
}

class _LongTermEffectBand extends StatelessWidget {
  const _LongTermEffectBand({
    required this.periodCore,
    required this.periodCards,
    required this.onOpenPeriodCard,
  });

  final PeriodCoreDto? periodCore;
  final List<PeriodCardDto> periodCards;
  final ValueChanged<PeriodCardDto> onOpenPeriodCard;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final summary = periodCore?.coreStory.trim().isNotEmpty == true
        ? periodCore!.coreStory.trim()
        : (periodCore?.bigPicture.trim().isNotEmpty == true
              ? periodCore!.bigPicture.trim()
              : 'Bu gunun arkasinda calisan daha uzun bir donem etkisi var.');
    return JoviaReadingPanel(
      label: 'Baglam',
      title: periodCore?.title.trim().isNotEmpty == true
          ? periodCore!.title.trim()
          : 'Uzun donem etkisi',
      body: _condenseCalendarCopy(summary, maxChars: 220),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (periodCards.isNotEmpty)
            JoviaUtilityRow(
              title: periodCards.first.title,
              body: periodCards.first.subtitle,
              trailing: const JoviaUiIcon(
                asset: JoviaUiAsset.chevronRight,
                size: 16,
              ),
              onTap: () => onOpenPeriodCard(periodCards.first),
            )
          else
            Text(
              'Gunun arka planinda calisan donem hikayesini gun sayfasinda daha uzun okuyabilirsin.',
              style: profile.typography.bodyCompact.copyWith(
                color: profile.colors.muted,
              ),
            ),
        ],
      ),
    );
  }
}

class _PeriodEventCardsSection extends StatelessWidget {
  const _PeriodEventCardsSection({
    required this.periodCards,
    required this.note,
    required this.onOpenPeriodCard,
  });

  final List<PeriodCardDto> periodCards;
  final String note;
  final ValueChanged<PeriodCardDto> onOpenPeriodCard;

  @override
  Widget build(BuildContext context) {
    final spacing = context.profileTheme.spacing;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        JoviaSectionHeader(
          label: 'Uzun donem',
          title: 'Uzun dönem bugün de etkili',
          body: note.trim().isNotEmpty
              ? note.trim()
              : 'Bugünün arkasında çalışan daha uzun bir tema da burada duruyor.',
        ),
        SizedBox(height: spacing.sectionToContent),
        for (var index = 0; index < periodCards.length; index++) ...[
          JoviaTopicSurface(
            eyebrow: 'Uzun dönem',
            title: periodCards[index].title,
            body: periodCards[index].subtitle,
            meta: [
              if (periodCards[index].timeHint.trim().isNotEmpty)
                periodCards[index].timeHint.trim(),
            ],
            secondaryAction: MinimalCTAButton(
              label: 'Detayi ac',
              onTap: () => onOpenPeriodCard(periodCards[index]),
            ),
            onTap: () => onOpenPeriodCard(periodCards[index]),
          ),
          if (index != periodCards.length - 1)
            SizedBox(height: spacing.sectionToContent),
        ],
      ],
    );
  }
}

class ProfileCalendarPreviewStrip extends ConsumerStatefulWidget {
  const ProfileCalendarPreviewStrip({
    super.key,
    this.profileOverride,
    this.dataSource,
    this.initialDate,
  });

  final Map<String, dynamic>? profileOverride;
  final CalendarDataSource? dataSource;
  final DateTime? initialDate;

  @override
  ConsumerState<ProfileCalendarPreviewStrip> createState() =>
      _ProfileCalendarPreviewStripState();
}

class _ProfileCalendarPreviewStripState
    extends ConsumerState<ProfileCalendarPreviewStrip> {
  late final CalendarDataSource _dataSource;
  late DateTime _baseDay;
  late DateTime _stripStartDay;
  bool _loading = false;
  String? _error;
  CalendarDayBundle? _bundle;
  final Map<String, CalendarDayBundle> _bundleCache =
      <String, CalendarDayBundle>{};
  String? _lastProfileKey;
  int _requestEpoch = 0;

  @override
  void initState() {
    super.initState();
    _dataSource = widget.dataSource ?? NetworkCalendarDataSource();
    _baseDay = TransitRequestBuilder.stripDate(
      widget.initialDate ?? DateTime.now(),
    );
    _stripStartDay = _baseDay;
  }

  @override
  Widget build(BuildContext context) {
    final profileAsync = widget.profileOverride == null
        ? ref.watch(userProfileProvider)
        : const AsyncValue<Map<String, dynamic>?>.data(null);
    final profile = widget.profileOverride ?? profileAsync.valueOrNull;
    _maybeBootstrap(profile);

    if (profileAsync.isLoading && profile == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (!TransitRequestBuilder.hasProfile(profile)) {
      return const JoviaReadingPanel(
        label: 'Timing',
        title: 'Takvim icin dogum verisi gerekiyor',
        body:
            'Dogum tarihi, saati ve yeri tamamlandiginda gunluk takvim acilir.',
      );
    }

    final bundle = _bundle;
    final heroData = _resolvePreviewHeroData(bundle);
    final visibleDays = List<DateTime>.generate(
      7,
      (index) => TransitRequestBuilder.stripDate(
        _stripStartDay.add(Duration(days: index)),
      ),
    );
    final todayKey = _calendarDayKey(DateTime.now());

    return _ProfileCalendarPreviewHero(
      contentKey: heroData.contentKey,
      label: heroData.label,
      title: heroData.title,
      body: heroData.body,
      isCritical: heroData.isCritical,
      footer: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_error != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Text(
                _error!,
                style: context.profileTheme.typography.meta.copyWith(
                  color: Theme.of(context).colorScheme.error,
                ),
              ),
            ),
          Row(
            children: [
              Expanded(
                child: MinimalCTAButton(
                  label: 'Gunu ac',
                  onTap: () => _openDayPage(profile!, _baseDay),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: JoviaPrimaryButton(
                  label: 'Takvimi ac',
                  onTap: () {
                    Navigator.of(context).push(
                      MaterialPageRoute<void>(
                        builder: (_) => CalendarHubPage(
                          profileOverride: widget.profileOverride,
                          dataSource: _dataSource,
                          initialSelectedDay: _baseDay,
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 108,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemBuilder: (context, index) {
                final day = visibleDays[index];
                final meta = bundle?.calendarDays[_calendarDayKey(day)];
                return _ProfileCalendarMiniDayCard(
                  day: day,
                  meta: meta,
                  isSelected: _calendarDayKey(day) == _calendarDayKey(_baseDay),
                  isToday: _calendarDayKey(day) == todayKey,
                  onTap: () => _handlePreviewDayTap(profile!, day),
                );
              },
              separatorBuilder: (context, _) => const SizedBox(width: 10),
              itemCount: visibleDays.length,
            ),
          ),
          if (_loading) ...[
            const SizedBox(height: 14),
            const LinearProgressIndicator(),
          ],
          if (bundle?.periodCore != null) ...[
            const SizedBox(height: 14),
            Text(
              'Uzun donem etkisi: ${bundle!.periodCore!.title.trim().isNotEmpty ? bundle.periodCore!.title.trim() : 'arka planda aktif'}',
              style: context.profileTheme.typography.metaSoft.copyWith(
                color: context.profileTheme.colors.textLight,
              ),
            ),
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
        '${profile?['birth_date']}|${profile?['birth_time']}|${profile?['place'] ?? profile?['city']}|${profile?['timezone']}|${_calendarDayKey(_baseDay)}';
    if (_lastProfileKey == key) {
      return;
    }
    _lastProfileKey = key;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || profile == null) {
        return;
      }
      _loadBundle(profile);
    });
  }

  Future<void> _loadBundle(Map<String, dynamic> profile) async {
    final requestDay = _baseDay;
    final requestKey = _calendarDayKey(requestDay);
    final requestEpoch = ++_requestEpoch;
    setState(() {
      _bundle = _bundleCache[requestKey] ?? _bundle;
      _loading = !_bundleCache.containsKey(requestKey);
      _error = null;
    });
    try {
      final bundle = await _loadCalendarDayBundle(
        dataSource: _dataSource,
        profile: profile,
        selectedDay: requestDay,
      );
      if (!mounted) {
        return;
      }
      _bundleCache[requestKey] = bundle;
      if (requestEpoch != _requestEpoch ||
          requestKey != _calendarDayKey(_baseDay)) {
        return;
      }
      setState(() {
        _bundle = bundle;
        _loading = false;
      });
    } catch (exc) {
      if (!mounted) {
        return;
      }
      if (requestEpoch != _requestEpoch ||
          requestKey != _calendarDayKey(_baseDay)) {
        return;
      }
      setState(() {
        _loading = false;
        _error = exc.toString();
      });
    }
  }

  Future<void> _handlePreviewDayTap(
    Map<String, dynamic> profile,
    DateTime day,
  ) async {
    final resolved = TransitRequestBuilder.stripDate(day);
    if (_calendarDayKey(resolved) == _calendarDayKey(_baseDay)) {
      await _openDayPage(profile, resolved);
      return;
    }
    setState(() {
      _baseDay = resolved;
      _syncPreviewWindow(resolved);
    });
    await _loadBundle(profile);
  }

  Future<void> _openDayPage(Map<String, dynamic> profile, DateTime day) async {
    final dayKey = _calendarDayKey(day);
    final returned = await Navigator.of(context, rootNavigator: true)
        .push<DateTime>(
          MaterialPageRoute<DateTime>(
            builder: (_) => CalendarDayPage(
              profile: profile,
              initialDate: day,
              initialBundle:
                  _bundleCache[dayKey] ??
                  (_bundle != null && _calendarDayKey(_bundle!.date) == dayKey
                      ? _bundle
                      : null),
              dataSource: _dataSource,
              source: 'profile_calendar_preview',
            ),
          ),
        );
    final resolved = TransitRequestBuilder.stripDate(returned ?? day);
    if (_calendarDayKey(resolved) == _calendarDayKey(_baseDay)) {
      return;
    }
    setState(() {
      _baseDay = resolved;
      _syncPreviewWindow(resolved);
    });
    await _loadBundle(profile);
  }

  void _syncPreviewWindow(DateTime selectedDay) {
    final normalized = TransitRequestBuilder.stripDate(selectedDay);
    final startKey = _calendarDayKey(_stripStartDay);
    final endKey = _calendarDayKey(
      TransitRequestBuilder.stripDate(
        _stripStartDay.add(const Duration(days: 6)),
      ),
    );
    final selectedKey = _calendarDayKey(normalized);
    if (selectedKey.compareTo(startKey) >= 0 &&
        selectedKey.compareTo(endKey) <= 0) {
      return;
    }
    _stripStartDay = TransitRequestBuilder.stripDate(
      normalized.subtract(const Duration(days: 2)),
    );
  }

  _PreviewHeroData _resolvePreviewHeroData(CalendarDayBundle? activeBundle) {
    final selectedKey = _calendarDayKey(_baseDay);
    final cachedBundle = _bundleCache[selectedKey];
    final bundle =
        cachedBundle ??
        (activeBundle != null &&
                _calendarDayKey(activeBundle.date) == selectedKey
            ? activeBundle
            : null);
    final meta =
        bundle?.selectedDayMeta ?? activeBundle?.calendarDays[selectedKey];
    final human = _buildDailyHumanCardViewModel(
      card: bundle?.dailyEventCards.isNotEmpty == true
          ? bundle!.dailyEventCards.first
          : null,
      dayMeta: meta,
      date: _baseDay,
    );
    final title = human.feltLine.isNotEmpty
        ? human.feltLine
        : (bundle?.headline ?? _formatCalendarDayTitle(_baseDay));
    final body = human.heroBody.isNotEmpty
        ? human.heroBody
        : (bundle?.summary ??
              'Yakin gunleri hizlica tara, bir gune dokunup gun sayfasina gec.');
    return _PreviewHeroData(
      contentKey: selectedKey,
      label: 'Gunun temasi',
      title: title,
      body: body,
      isCritical:
          bundle?.selectedDayMeta?.isCritical == true ||
          meta?.isCritical == true,
    );
  }
}

class _PreviewHeroData {
  const _PreviewHeroData({
    required this.contentKey,
    required this.label,
    required this.title,
    required this.body,
    required this.isCritical,
  });

  final String contentKey;
  final String label;
  final String title;
  final String body;
  final bool isCritical;
}

class _ProfileCalendarPreviewHero extends StatelessWidget {
  const _ProfileCalendarPreviewHero({
    required this.contentKey,
    required this.label,
    required this.title,
    required this.body,
    required this.isCritical,
    required this.footer,
  });

  final String contentKey;
  final String label;
  final String title;
  final String body;
  final bool isCritical;
  final Widget footer;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final labelStyle = profile.typography.eyebrow.copyWith(
      color: profile.colors.textLight,
      letterSpacing: 1.5,
    );
    final titleStyle = profile.typography.pageTitle.copyWith(
      color: profile.colors.text,
      fontSize: 27,
      height: 1.08,
    );
    final bodyStyle = profile.typography.bodyCompact.copyWith(
      color: profile.colors.textLight,
      fontSize: 13,
      height: 1.42,
    );
    return JoviaSurfaceCard(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            height: _heroTextSlotHeight(labelStyle, 1),
            child: _PreviewHeroAnimatedText(
              text: label.toUpperCase(),
              textStyle: labelStyle,
              maxLines: 1,
              delay: Duration.zero,
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: _heroTextSlotHeight(titleStyle, 3),
            child: _PreviewHeroAnimatedText(
              text: title,
              textStyle: titleStyle,
              maxLines: 3,
              delay: const Duration(milliseconds: 36),
            ),
          ),
          if (body.trim().isNotEmpty) ...[
            const SizedBox(height: 12),
            SizedBox(
              height: _heroTextSlotHeight(bodyStyle, 5),
              child: _PreviewHeroAnimatedText(
                text: body,
                textStyle: bodyStyle,
                maxLines: 5,
                delay: const Duration(milliseconds: 72),
              ),
            ),
          ],
          const SizedBox(height: 16),
          KeyedSubtree(key: ValueKey<String>(contentKey), child: footer),
        ],
      ),
    );
  }
}

class _PreviewHeroAnimatedText extends StatefulWidget {
  const _PreviewHeroAnimatedText({
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
  State<_PreviewHeroAnimatedText> createState() =>
      _PreviewHeroAnimatedTextState();
}

class _PreviewHeroAnimatedTextState extends State<_PreviewHeroAnimatedText>
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
  void didUpdateWidget(covariant _PreviewHeroAnimatedText oldWidget) {
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
    if (_previousText == null) {
      return Align(
        alignment: Alignment.topLeft,
        child: _buildText(_currentText),
      );
    }

    final delayFraction =
        widget.delay.inMilliseconds / _controller.duration!.inMilliseconds;
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
              if (_previousText != null)
                Opacity(
                  opacity: 1 - outgoing.value,
                  child: Transform.translate(
                    offset: Offset(0, -10 * outgoing.value),
                    child: _buildText(_previousText!),
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

double _heroTextSlotHeight(TextStyle style, int lines) {
  final fontSize = style.fontSize ?? 14;
  final lineHeight = style.height ?? 1.2;
  return (fontSize * lineHeight * lines) + 2;
}

class _ProfileCalendarMiniDayCard extends StatelessWidget {
  const _ProfileCalendarMiniDayCard({
    required this.day,
    required this.meta,
    required this.isSelected,
    required this.isToday,
    required this.onTap,
  });

  final DateTime day;
  final NarrativeCalendarDay? meta;
  final bool isSelected;
  final bool isToday;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final signalCount = meta == null
        ? 0
        : (meta!.signalsCount > 3 ? 3 : meta!.signalsCount);
    final emphasisColor = meta?.isCritical == true
        ? colors.warmAccent
        : colors.primary;
    final fillColor = isSelected
        ? Color.alphaBlend(
            colors.primary.withValues(alpha: 0.16),
            colors.surface.withValues(alpha: 0.68),
          )
        : isToday
        ? Color.alphaBlend(
            colors.primary.withValues(alpha: 0.06),
            colors.surface.withValues(alpha: 0.58),
          )
        : colors.surface.withValues(alpha: 0.52);
    final borderColor = isSelected
        ? colors.primary.withValues(alpha: 0.9)
        : isToday
        ? colors.primary.withValues(alpha: 0.42)
        : colors.strokeSoft.withValues(alpha: 0.74);
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(22),
      child: AnimatedContainer(
        key: ValueKey<String>('profilePreviewDay_${_calendarDayKey(day)}'),
        duration: const Duration(milliseconds: 220),
        curve: Curves.easeOutCubic,
        width: 76,
        padding: const EdgeInsets.fromLTRB(10, 10, 10, 10),
        decoration: BoxDecoration(
          color: fillColor,
          borderRadius: BorderRadius.circular(22),
          border: Border.all(color: borderColor, width: isSelected ? 1.2 : 1),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: colors.primary.withValues(alpha: 0.16),
                    blurRadius: 18,
                    offset: const Offset(0, 10),
                    spreadRadius: -12,
                  ),
                ]
              : isToday
              ? [
                  BoxShadow(
                    color: colors.primary.withValues(alpha: 0.08),
                    blurRadius: 16,
                    offset: const Offset(0, 8),
                    spreadRadius: -14,
                  ),
                ]
              : null,
        ),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final compact = constraints.maxHeight < 88;
            return Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                AnimatedContainer(
                  duration: const Duration(milliseconds: 220),
                  curve: Curves.easeOutCubic,
                  width: isSelected
                      ? 20
                      : isToday
                      ? 14
                      : 8,
                  height: 3,
                  decoration: BoxDecoration(
                    color: isSelected
                        ? emphasisColor
                        : isToday
                        ? emphasisColor.withValues(alpha: 0.44)
                        : colors.separator.withValues(alpha: 0.34),
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
                Text(
                  _formatCalendarShortWeekday(day),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: profile.typography.eyebrow.copyWith(
                    color: isSelected
                        ? colors.text
                        : isToday
                        ? colors.primary.withValues(alpha: 0.88)
                        : colors.textLight,
                    fontSize: compact ? 10 : 11,
                    height: 1,
                  ),
                ),
                Text(
                  '${day.day}',
                  style: profile.typography.section.copyWith(
                    color: colors.text,
                    fontSize: compact ? 24 : 28,
                    fontWeight: isSelected ? FontWeight.w700 : FontWeight.w600,
                    height: 1,
                  ),
                ),
                if (signalCount > 0)
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      for (var i = 0; i < signalCount; i++) ...[
                        Container(
                          width: compact ? 5 : 6,
                          height: compact ? 5 : 6,
                          margin: EdgeInsets.symmetric(
                            horizontal: compact ? 1.5 : 2,
                          ),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: meta?.isCritical == true
                                ? colors.warmAccent
                                : colors.primary,
                          ),
                        ),
                      ],
                    ],
                  )
                else
                  Container(
                    width: compact ? 6 : 8,
                    height: compact ? 6 : 8,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: colors.separator.withValues(alpha: 0.42),
                    ),
                  ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class CalendarDayPage extends StatefulWidget {
  const CalendarDayPage({
    super.key,
    required this.profile,
    required this.initialDate,
    this.initialBundle,
    this.dataSource,
    this.source = 'unknown',
  });

  final Map<String, dynamic> profile;
  final DateTime initialDate;
  final CalendarDayBundle? initialBundle;
  final CalendarDataSource? dataSource;
  final String source;

  @override
  State<CalendarDayPage> createState() => _CalendarDayPageState();
}

class _CalendarDayPageState extends State<CalendarDayPage> {
  static const int _kInitialPage = 1000;

  late final CalendarDataSource _dataSource;
  late final PageController _pageController;
  late DateTime _activeDate;
  final Map<String, CalendarDayBundle> _cache = <String, CalendarDayBundle>{};
  final Set<String> _loadingKeys = <String>{};

  @override
  void initState() {
    super.initState();
    _dataSource = widget.dataSource ?? NetworkCalendarDataSource();
    _activeDate = TransitRequestBuilder.stripDate(widget.initialDate);
    _pageController = PageController(initialPage: _kInitialPage);
    if (widget.initialBundle != null) {
      _cache[_calendarDayKey(widget.initialBundle!.date)] =
          widget.initialBundle!;
    }
    _ensureLoaded(_activeDate);
    _prefetchNeighbors(_activeDate);
  }

  Future<void> _ensureLoaded(DateTime date) async {
    final key = _calendarDayKey(date);
    if (_cache.containsKey(key) || _loadingKeys.contains(key)) {
      return;
    }
    setState(() => _loadingKeys.add(key));
    try {
      final bundle = await _loadCalendarDayBundle(
        dataSource: _dataSource,
        profile: widget.profile,
        selectedDay: date,
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _cache[key] = bundle;
        _loadingKeys.remove(key);
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() => _loadingKeys.remove(key));
    }
  }

  void _prefetchNeighbors(DateTime center) {
    _ensureLoaded(
      TransitRequestBuilder.stripDate(center.subtract(const Duration(days: 1))),
    );
    _ensureLoaded(
      TransitRequestBuilder.stripDate(center.add(const Duration(days: 1))),
    );
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return PopScope<DateTime>(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) {
          return;
        }
        Navigator.of(context).pop(_activeDate);
      },
      child: Scaffold(
        backgroundColor: profile.colors.bg,
        appBar: AppBar(
          leadingWidth: 52,
          leading: Padding(
            key: const ValueKey<String>('calendarDayBack'),
            padding: const EdgeInsets.only(left: 12),
            child: JoviaGlassIconButton(
              onTap: () => Navigator.of(context).pop(_activeDate),
              child: const JoviaUiIcon(asset: JoviaUiAsset.back, size: 18),
            ),
          ),
          title: Text(
            'GUN',
            style: profile.typography.navigationLabel(
              color: profile.colors.text,
            ),
          ),
        ),
        body: SafeArea(
          top: false,
          child: PageView.builder(
            controller: _pageController,
            scrollDirection: Axis.horizontal,
            onPageChanged: (index) {
              final date = TransitRequestBuilder.stripDate(
                widget.initialDate.add(Duration(days: index - _kInitialPage)),
              );
              setState(() => _activeDate = date);
              _ensureLoaded(date);
              _prefetchNeighbors(date);
            },
            itemBuilder: (context, index) {
              final date = TransitRequestBuilder.stripDate(
                widget.initialDate.add(Duration(days: index - _kInitialPage)),
              );
              final key = _calendarDayKey(date);
              final bundle = _cache[key];
              final loading = _loadingKeys.contains(key) && bundle == null;
              return _CalendarDayPageContent(
                date: date,
                bundle: bundle,
                loading: loading,
                source: widget.source,
              );
            },
          ),
        ),
      ),
    );
  }
}

class _CalendarDayPageContent extends StatelessWidget {
  const _CalendarDayPageContent({
    required this.date,
    required this.bundle,
    required this.loading,
    required this.source,
  });

  final DateTime date;
  final CalendarDayBundle? bundle;
  final bool loading;
  final String source;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    final heroHuman = _buildDailyHumanCardViewModel(
      card: bundle?.dailyEventCards.isNotEmpty == true
          ? bundle!.dailyEventCards.first
          : null,
      dayMeta: bundle?.selectedDayMeta,
      date: date,
    );
    return JoviaPageScaffold(
      padding: EdgeInsets.fromLTRB(
        spacing.pageHorizontal,
        spacing.xs,
        spacing.pageHorizontal,
        spacing.pageBottom,
      ),
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          JoviaEditorialHeroBlock(
            label: 'Gun',
            title: heroHuman.feltLine,
            body: heroHuman.heroBody.isNotEmpty
                ? heroHuman.heroBody
                : (bundle?.summary ??
                      'Bu gunun kartlari ve baglami yuklenirken bekleniyor.'),
            large: true,
            accent: JoviaIllustrationAccent(
              asset: (bundle?.selectedDayMeta?.isCritical ?? false)
                  ? JoviaIllustrationAsset.sunGrowth
                  : JoviaIllustrationAsset.planet,
              width: 72,
              height: 72,
              opacity: 0.82,
            ),
            footer: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _CalendarInfoPill(
                  label: '${date.day} ${_kCalendarMonthNames[date.month - 1]}',
                  highlighted: true,
                ),
                if (heroHuman.signalLabel.isNotEmpty)
                  _CalendarInfoPill(
                    label: heroHuman.signalLabel,
                    highlighted: heroHuman.isCritical,
                  ),
              ],
            ),
          ),
          if (loading) ...[
            SizedBox(height: spacing.sectionToContent),
            const LinearProgressIndicator(),
          ],
          if (bundle != null && bundle!.dailyEventCards.isNotEmpty) ...[
            SizedBox(height: spacing.majorSectionGap),
            JoviaSectionHeader(
              label: 'Bugun',
              title: 'Bugünün vurgusu',
              body: bundle!.usedPeriodFallback
                  ? bundle!.periodOnlyNote
                  : 'Bugün sende daha çok hissedilen şey burada açılıyor.',
            ),
            SizedBox(height: spacing.sectionToContent),
            for (final card in bundle!.dailyEventCards) ...[
              Builder(
                builder: (context) {
                  final human = _buildDailyHumanCardViewModel(
                    card: card,
                    dayMeta: bundle!.selectedDayMeta,
                    date: date,
                  );
                  return JoviaTopicSurface(
                    eyebrow: human.signalLabel.isNotEmpty
                        ? human.signalLabel
                        : 'Bugun',
                    title: human.feltLine,
                    body: human.cardBody.isNotEmpty
                        ? human.cardBody
                        : 'Detaylar icin karti ac.',
                    meta: human.meta,
                    secondaryAction: MinimalCTAButton(
                      label: 'Detayi ac',
                      onTap: () {
                        Navigator.of(context, rootNavigator: true).push(
                          MaterialPageRoute<void>(
                            builder: (_) => PeriodDetailPage(
                              card: PeriodCardDto.fromEventCard(
                                eventCard: card,
                                index: 0,
                              ),
                              periodCore: null,
                              routeSource: '${source}_day_card',
                            ),
                          ),
                        );
                      },
                    ),
                  );
                },
              ),
              SizedBox(height: spacing.sectionToContent),
            ],
          ],
          if (bundle != null && bundle!.periodCards.isNotEmpty) ...[
            SizedBox(height: spacing.majorSectionGap),
            _PeriodEventCardsSection(
              periodCards: bundle!.periodCards,
              note: bundle!.periodOnlyNote,
              onOpenPeriodCard: (card) {
                Navigator.of(context, rootNavigator: true).push(
                  MaterialPageRoute<void>(
                    builder: (_) => PeriodDetailPage(
                      card: card,
                      periodCore: bundle!.periodCore,
                      routeSource: '${source}_day_period',
                    ),
                  ),
                );
              },
            ),
          ] else if (bundle != null && bundle!.periodCore != null) ...[
            SizedBox(height: spacing.majorSectionGap),
            _LongTermEffectBand(
              periodCore: bundle!.periodCore,
              periodCards: bundle!.periodCards,
              onOpenPeriodCard: (card) {
                Navigator.of(context, rootNavigator: true).push(
                  MaterialPageRoute<void>(
                    builder: (_) => PeriodDetailPage(
                      card: card,
                      periodCore: bundle!.periodCore,
                      routeSource: '${source}_day_period',
                    ),
                  ),
                );
              },
            ),
          ] else if (!loading) ...[
            SizedBox(height: spacing.majorSectionGap),
            EmptyStateBlock(
              title: 'Bugun sakin',
              body: bundle?.timeline?.summary.trim().isNotEmpty == true
                  ? bundle!.timeline!.summary.trim()
                  : 'Bu gun icin belirgin bir kart cikmadi. Sag-sol kaydirip komsu gunlere bakabilirsin.',
            ),
          ],
          if (bundle != null && bundle!.markers.isNotEmpty) ...[
            SizedBox(height: spacing.majorSectionGap),
            JoviaReadingPanel(
              label: 'Markers',
              title: 'Gunun markerlari',
              child: Column(
                children: [
                  for (
                    var index = 0;
                    index < bundle!.markers.length;
                    index++
                  ) ...[
                    JoviaUtilityRow(
                      title: bundle!.markers[index].title.isNotEmpty
                          ? bundle!.markers[index].title
                          : 'Gunluk marker',
                      body: bundle!.markers[index].summary.isNotEmpty
                          ? bundle!.markers[index].summary
                          : (bundle!.markers[index].timeHint.isNotEmpty
                                ? bundle!.markers[index].timeHint
                                : 'Detaylar icin ac.'),
                      trailing: const JoviaUiIcon(
                        asset: JoviaUiAsset.chevronRight,
                        size: 16,
                      ),
                      onTap: () {
                        Navigator.of(context, rootNavigator: true).push(
                          MaterialPageRoute<void>(
                            builder: (_) => PeriodMarkerDetailPage(
                              marker: bundle!.markers[index],
                            ),
                          ),
                        );
                      },
                    ),
                    if (index != bundle!.markers.length - 1)
                      const ThinDivider(),
                  ],
                ],
              ),
            ),
          ],
          if (bundle != null &&
              (bundle!.timeline?.lines.isNotEmpty == true ||
                  bundle!.timeline?.summary.trim().isNotEmpty == true)) ...[
            SizedBox(height: spacing.majorSectionGap),
            JoviaReadingPanel(
              label: 'Flow',
              title: 'Gunun akis notlari',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (bundle!.timeline?.summary.trim().isNotEmpty == true)
                    Text(
                      bundle!.timeline!.summary.trim(),
                      style: profile.typography.bodyCompact.copyWith(
                        color: profile.colors.text,
                      ),
                    ),
                  for (final line
                      in bundle!.timeline?.lines.take(4) ??
                          const <String>[]) ...[
                    const SizedBox(height: 8),
                    Text(
                      line,
                      style: profile.typography.bodyCompact.copyWith(
                        color: profile.colors.muted,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class DailyCalendarTab extends ConsumerStatefulWidget {
  const DailyCalendarTab({
    super.key,
    this.profileOverride,
    this.embedded = false,
  });

  final Map<String, dynamic>? profileOverride;
  final bool embedded;

  @override
  ConsumerState<DailyCalendarTab> createState() => _DailyCalendarTabState();
}

class _DailyCalendarTabState extends ConsumerState<DailyCalendarTab> {
  final NarrativeRepository _narrativeRepository = NarrativeRepository();
  final CalendarRepository _calendarRepository = CalendarRepository();

  DateTime _selectedDay = TransitRequestBuilder.stripDate(DateTime.now());
  bool _loading = false;
  String? _error;
  List<EventCardDto> _dailyEventCards = const <EventCardDto>[];
  List<PeriodCardDto> _periodEventCards = const <PeriodCardDto>[];
  List<PeriodMarkerDto> _dailyMarkers = const <PeriodMarkerDto>[];
  List<CalendarBestTimeItem> _bestTimes = const <CalendarBestTimeItem>[];
  Map<String, NarrativeCalendarDay> _calendarDays =
      const <String, NarrativeCalendarDay>{};
  TimelineDto? _dailyTimeline;
  bool _wrongSource = false;
  String _periodOnlyNote = '';
  String? _lastProfileKey;

  @override
  Widget build(BuildContext context) {
    final profileTheme = context.profileTheme;
    final profileAsync = widget.profileOverride == null
        ? ref.watch(userProfileProvider)
        : const AsyncValue<Map<String, dynamic>?>.data(null);
    final profile = widget.profileOverride ?? profileAsync.valueOrNull;
    _maybeBootstrap(profile);

    if (profileAsync.isLoading && profile == null) {
      return const Center(child: CircularProgressIndicator());
    }
    if (profileAsync.hasError && profile == null) {
      return _ErrorText('Profil verisi yuklenemedi.');
    }
    if (!TransitRequestBuilder.hasProfile(profile)) {
      return const _ErrorText(
        'Takvim icin once profil dogum verisini tamamlayin.',
      );
    }

    final content = _DailyCalendarContent(
      selectedDay: _selectedDay,
      selectedSummary: _selectedSummary(),
      selectedDayMeta: _calendarDays[_dayKey(_selectedDay)],
      loading: _loading,
      error: _error,
      wrongSource: _wrongSource,
      bestTimes: _bestTimes,
      eventCards: _dailyEventCards,
      periodCards: _periodEventCards,
      periodOnlyNote: _periodOnlyNote,
      markers: _dailyMarkers,
      timeline: _dailyTimeline,
      calendarDays: _calendarDays,
      onPickDate: () => _showDatePicker(profile!),
      onSelectDay: (day) => _handleDaySelection(profile!, day),
      onShiftMonth: (delta) => _shiftMonth(profile!, delta),
      onOpenEventCard: _openDailyDetail,
      onOpenMarker: _openMarkerDetail,
    );

    if (widget.embedded) {
      return RefreshIndicator(
        onRefresh: () => _loadDaily(profile!),
        child: content,
      );
    }

    return RefreshIndicator(
      onRefresh: () => _loadDaily(profile!),
      child: Padding(
        padding: EdgeInsets.fromLTRB(
          profileTheme.spacing.pageHorizontal,
          profileTheme.spacing.pageTop,
          profileTheme.spacing.pageHorizontal,
          profileTheme.spacing.pageBottom,
        ),
        child: content,
      ),
    );
  }

  Future<void> _showDatePicker(Map<String, dynamic> profile) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDay,
      firstDate: DateTime.now().subtract(const Duration(days: 365 * 2)),
      lastDate: DateTime.now().add(const Duration(days: 365 * 2)),
    );
    if (picked == null) {
      return;
    }
    final normalized = TransitRequestBuilder.stripDate(picked);
    if (_dayKey(normalized) == _dayKey(_selectedDay)) {
      return;
    }
    setState(() => _selectedDay = normalized);
    await _loadDaily(profile);
  }

  Future<void> _handleDaySelection(
    Map<String, dynamic> profile,
    DateTime day,
  ) async {
    final normalized = TransitRequestBuilder.stripDate(day);
    if (_dayKey(normalized) == _dayKey(_selectedDay)) {
      return;
    }
    setState(() => _selectedDay = normalized);
    await _loadDaily(profile);
  }

  Future<void> _shiftMonth(Map<String, dynamic> profile, int delta) async {
    final targetMonth = DateTime(_selectedDay.year, _selectedDay.month + delta);
    final clamped = _clampSelectedDayToMonth(_selectedDay, targetMonth);
    setState(() => _selectedDay = clamped);
    await _loadDaily(profile);
  }

  DateTime _clampSelectedDayToMonth(
    DateTime selectedDay,
    DateTime targetMonth,
  ) {
    final lastDay = DateTime(targetMonth.year, targetMonth.month + 1, 0).day;
    return DateTime(
      targetMonth.year,
      targetMonth.month,
      selectedDay.day.clamp(1, lastDay),
    );
  }

  String _selectedSummary() {
    final selectedMeta = _calendarDays[_dayKey(_selectedDay)];
    final human = _buildDailyHumanCardViewModel(
      card: _dailyEventCards.isNotEmpty ? _dailyEventCards.first : null,
      dayMeta: selectedMeta,
      date: _selectedDay,
    );
    if (human.heroBody.isNotEmpty) {
      return _condenseCopy(human.heroBody, maxChars: 180);
    }
    final timelineSummary = _dailyTimeline?.summary.trim() ?? '';
    if (timelineSummary.isNotEmpty) {
      return _condenseCopy(timelineSummary, maxChars: 180);
    }
    if (selectedMeta?.microSummaryTr.trim().isNotEmpty == true) {
      return _condenseCopy(selectedMeta!.microSummaryTr.trim(), maxChars: 180);
    }
    return 'Secili gune dokunup event kartlarini, markerlari ve gunun ritmini asagida takip et.';
  }

  String _condenseCopy(String text, {int maxChars = 220}) {
    final trimmed = text.trim();
    if (trimmed.isEmpty) {
      return '';
    }
    if (trimmed.length <= maxChars) {
      return trimmed;
    }
    return '${trimmed.substring(0, maxChars).trimRight()}...';
  }

  String _dayKey(DateTime value) =>
      TransitRequestBuilder.fmtDate(TransitRequestBuilder.stripDate(value));

  void _openDailyDetail(EventCardDto card) {
    final detailCard = PeriodCardDto.fromEventCard(eventCard: card, index: 0);
    Navigator.of(context, rootNavigator: true).push(
      MaterialPageRoute<void>(
        builder: (_) => PeriodDetailPage(
          card: detailCard,
          periodCore: null,
          routeSource: 'calendar_hub_daily',
        ),
      ),
    );
  }

  void _openMarkerDetail(PeriodMarkerDto marker) {
    Navigator.of(context, rootNavigator: true).push(
      MaterialPageRoute<void>(
        builder: (_) => PeriodMarkerDetailPage(marker: marker),
      ),
    );
  }

  Future<void> _loadDaily(Map<String, dynamic> profile) async {
    setState(() {
      _loading = true;
      _error = null;
      _wrongSource = false;
      _periodOnlyNote = '';
    });

    try {
      final responses = await Future.wait<Map<String, dynamic>>([
        _narrativeRepository.fetchDailyNarrative(
          profile: profile,
          selectedDate: _selectedDay,
        ),
        _calendarRepository.fetchCalendar(
          profile: profile,
          focusedDate: _selectedDay,
          include: 'markers',
        ),
      ]);
      final map = responses[0];
      final narrative = NarrativeResponse.fromMap(map);
      final periodCalendar = PeriodCalendarDto.fromMap(responses[1]);
      final publicRaw = map['public'] is Map
          ? Map<String, dynamic>.from(map['public'] as Map)
          : map;
      if (publicRaw['markers'] is List &&
          (publicRaw['markers'] as List).isNotEmpty) {
        debugPrint('DailyCalendarTab ignored period markers from narrative.');
      }
      final narrativeBest = _extractBestTimesFromNarrativeMap(map);
      final fallbackBest = narrativeBest.isNotEmpty
          ? const <CalendarBestTimeItem>[]
          : await _loadBestTimesFallback(profile);
      final selection = _deriveEventCardSelection(
        narrative: narrative,
        selectedDate: _selectedDay,
      );
      final periodInNarrative =
          selection.periodCards.isNotEmpty && selection.dailyCards.isEmpty;
      if (periodInNarrative) {
        debugPrint('DailyCalendarTab ignored period-only narrative payload.');
      }
      if (!mounted) {
        return;
      }
      setState(() {
        _dailyEventCards = selection.dailyCards;
        _periodEventCards = <PeriodCardDto>[
          for (var index = 0; index < selection.periodCards.length; index++)
            PeriodCardDto.fromEventCard(
              eventCard: selection.periodCards[index],
              index: index,
            ),
        ];
        _dailyMarkers = periodCalendar.markers;
        _calendarDays = narrative.calendarDays;
        _dailyTimeline = narrative.timeline;
        _bestTimes = narrativeBest.isNotEmpty ? narrativeBest : fallbackBest;
        _periodOnlyNote = selection.periodOnlyNote;
        _wrongSource =
            (periodInNarrative || selection.dailyCards.isEmpty) &&
            _periodEventCards.isEmpty;
        _loading = false;
      });
    } on DioException catch (exc) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _periodEventCards = const <PeriodCardDto>[];
        _dailyMarkers = const <PeriodMarkerDto>[];
        _calendarDays = const <String, NarrativeCalendarDay>{};
        _dailyTimeline = null;
        _bestTimes = const <CalendarBestTimeItem>[];
        _periodOnlyNote = '';
        _error = _friendlyError(exc);
      });
    } catch (exc) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _periodEventCards = const <PeriodCardDto>[];
        _dailyMarkers = const <PeriodMarkerDto>[];
        _calendarDays = const <String, NarrativeCalendarDay>{};
        _dailyTimeline = null;
        _bestTimes = const <CalendarBestTimeItem>[];
        _periodOnlyNote = '';
        _error = exc.toString();
      });
    }
  }

  Future<List<CalendarBestTimeItem>> _loadBestTimesFallback(
    Map<String, dynamic> profile,
  ) async {
    try {
      final map = await _calendarRepository.fetchBestTimes(
        profile: profile,
        focusedDate: _selectedDay,
      );
      return _extractBestTimesFromBestTimesMap(map);
    } catch (_) {
      return const <CalendarBestTimeItem>[];
    }
  }

  void _maybeBootstrap(Map<String, dynamic>? profile) {
    if (!TransitRequestBuilder.hasProfile(profile)) {
      return;
    }
    final key =
        '${profile?['birth_date']}|${profile?['birth_time']}|${profile?['place'] ?? profile?['city']}|${profile?['timezone']}|${TransitRequestBuilder.fmtDate(_selectedDay)}';
    if (_lastProfileKey == key) {
      return;
    }
    _lastProfileKey = key;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || profile == null) {
        return;
      }
      _loadDaily(profile);
    });
  }

  String _friendlyError(DioException exc) {
    final status = exc.response?.statusCode;
    if (status == 422) {
      return 'Gonderilen tarih/alanlar gecersiz (422).';
    }
    return exc.message ?? 'Daily veri alinamadi.';
  }

  List<CalendarBestTimeItem> _extractBestTimesFromNarrativeMap(
    Map<String, dynamic> data,
  ) {
    final out = <CalendarBestTimeItem>[];
    final publicRaw = data['public'] is Map
        ? Map<String, dynamic>.from(data['public'] as Map)
        : data;

    List<dynamic>? pickList(dynamic raw) {
      if (raw is List) {
        return raw;
      }
      return null;
    }

    final direct =
        pickList(publicRaw['best_times']) ??
        pickList(publicRaw['featured_windows']);
    if (direct != null) {
      for (final row in direct) {
        if (row is! Map) {
          continue;
        }
        final mapRow = Map<String, dynamic>.from(row);
        final label =
            (mapRow['label'] ??
                    mapRow['title'] ??
                    mapRow['time_label'] ??
                    mapRow['window'] ??
                    mapRow['date'] ??
                    '')
                .toString()
                .trim();
        final reason =
            (mapRow['focus'] ?? mapRow['theme'] ?? mapRow['reason'] ?? '')
                .toString()
                .trim();
        if (label.isEmpty && reason.isEmpty) {
          continue;
        }
        out.add(
          CalendarBestTimeItem(
            label: reason.isEmpty ? label : '$label • $reason',
          ),
        );
      }
      if (out.isNotEmpty) {
        return out.take(6).toList(growable: false);
      }
    }

    final narrative = NarrativeResponse.fromMap(data);
    final primary = narrative.blocks.where(
      (b) => b.type == 'best_time_primary',
    );
    for (final block in primary) {
      final date = (block.meta['date'] ?? '').toString().trim();
      final score = (block.meta['score'] ?? '').toString().trim();
      final label = date.isNotEmpty ? date : block.copy.title.trim();
      final detail = block.copy.short.trim().isNotEmpty
          ? block.copy.short.trim()
          : score;
      if (label.isEmpty && detail.isEmpty) {
        continue;
      }
      out.add(
        CalendarBestTimeItem(
          label: detail.isEmpty ? label : '$label • $detail',
        ),
      );
    }
    final lists = narrative.blocks.where((b) => b.type == 'best_time_list');
    for (final block in lists) {
      final candidates = block.meta['candidates'];
      if (candidates is! List) {
        continue;
      }
      for (final row in candidates.take(6)) {
        if (row is! Map) {
          continue;
        }
        final mapRow = Map<String, dynamic>.from(row);
        final date = (mapRow['date'] ?? '').toString().trim();
        final score = (mapRow['score'] ?? '').toString().trim();
        if (date.isEmpty && score.isEmpty) {
          continue;
        }
        out.add(
          CalendarBestTimeItem(
            label: score.isEmpty ? date : '$date • skor $score',
          ),
        );
      }
    }
    return out.take(6).toList(growable: false);
  }

  List<CalendarBestTimeItem> _extractBestTimesFromBestTimesMap(
    Map<String, dynamic> data,
  ) {
    final out = <CalendarBestTimeItem>[];
    final list = (data['best_times'] is List)
        ? (data['best_times'] as List)
        : (data['windows'] is List)
        ? (data['windows'] as List)
        : (data['candidates'] is List)
        ? (data['candidates'] as List)
        : const <dynamic>[];
    for (final row in list) {
      if (row is! Map) {
        continue;
      }
      final mapRow = Map<String, dynamic>.from(row);
      final label =
          (mapRow['label'] ??
                  mapRow['time_label'] ??
                  mapRow['window'] ??
                  mapRow['date'] ??
                  '')
              .toString()
              .trim();
      final focus =
          (mapRow['focus'] ?? mapRow['reason'] ?? mapRow['theme'] ?? '')
              .toString()
              .trim();
      if (label.isEmpty && focus.isEmpty) {
        continue;
      }
      out.add(
        CalendarBestTimeItem(label: focus.isEmpty ? label : '$label • $focus'),
      );
    }
    return out.take(6).toList(growable: false);
  }
}

class _DailyCalendarContent extends StatelessWidget {
  const _DailyCalendarContent({
    required this.selectedDay,
    required this.selectedSummary,
    required this.selectedDayMeta,
    required this.loading,
    required this.error,
    required this.wrongSource,
    required this.bestTimes,
    required this.eventCards,
    required this.periodCards,
    required this.periodOnlyNote,
    required this.markers,
    required this.timeline,
    required this.calendarDays,
    required this.onPickDate,
    required this.onSelectDay,
    required this.onShiftMonth,
    required this.onOpenEventCard,
    required this.onOpenMarker,
  });

  final DateTime selectedDay;
  final String selectedSummary;
  final NarrativeCalendarDay? selectedDayMeta;
  final bool loading;
  final String? error;
  final bool wrongSource;
  final List<CalendarBestTimeItem> bestTimes;
  final List<EventCardDto> eventCards;
  final List<PeriodCardDto> periodCards;
  final String periodOnlyNote;
  final List<PeriodMarkerDto> markers;
  final TimelineDto? timeline;
  final Map<String, NarrativeCalendarDay> calendarDays;
  final VoidCallback onPickDate;
  final ValueChanged<DateTime> onSelectDay;
  final ValueChanged<int> onShiftMonth;
  final ValueChanged<EventCardDto> onOpenEventCard;
  final ValueChanged<PeriodMarkerDto> onOpenMarker;

  static const List<String> _monthNames = <String>[
    'Ocak',
    'Subat',
    'Mart',
    'Nisan',
    'Mayis',
    'Haziran',
    'Temmuz',
    'Agustos',
    'Eylul',
    'Ekim',
    'Kasim',
    'Aralik',
  ];

  static const List<String> _weekdayNames = <String>[
    'Pazartesi',
    'Sali',
    'Carsamba',
    'Persembe',
    'Cuma',
    'Cumartesi',
    'Pazar',
  ];

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    final typo = profile.typography;
    final heroHuman = _buildDailyHumanCardViewModel(
      card: eventCards.isNotEmpty ? eventCards.first : null,
      dayMeta: selectedDayMeta,
      date: selectedDay,
    );

    return ListView(
      padding: EdgeInsets.zero,
      physics: const AlwaysScrollableScrollPhysics(),
      children: [
        _CalendarMonthPanel(
          selectedDay: selectedDay,
          calendarDays: calendarDays,
          onPickDate: onPickDate,
          onSelectDay: onSelectDay,
          onShiftMonth: onShiftMonth,
        ),
        SizedBox(height: spacing.majorSectionGap),
        JoviaReadingPanel(
          label: 'Day',
          title: _selectedDayTitle(selectedDay),
          body: heroHuman.heroBody.isNotEmpty
              ? heroHuman.heroBody
              : selectedSummary,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _CalendarInfoPill(
                    label:
                        '${selectedDay.day} ${_monthNames[selectedDay.month - 1]}',
                    highlighted: true,
                  ),
                  if (heroHuman.signalLabel.isNotEmpty)
                    _CalendarInfoPill(
                      label: heroHuman.signalLabel,
                      highlighted: heroHuman.isCritical,
                    ),
                  if (timeline?.lines.isNotEmpty == true)
                    _CalendarInfoPill(
                      label: '${timeline!.lines.length} okuma notu',
                    ),
                ],
              ),
              if (selectedDayMeta != null && selectedDayMeta!.labels.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      for (final label in selectedDayMeta!.labels.take(4))
                        _CalendarInfoPill(label: label),
                    ],
                  ),
                ),
            ],
          ),
        ),
        if (loading) ...[
          SizedBox(height: spacing.sectionToContent),
          const LinearProgressIndicator(),
        ],
        if (error != null) ...[
          SizedBox(height: spacing.sectionToContent),
          Text(
            error!,
            style: typo.meta.copyWith(
              color: Theme.of(context).colorScheme.error,
            ),
          ),
        ],
        if (bestTimes.isNotEmpty) ...[
          SizedBox(height: spacing.majorSectionGap),
          JoviaReadingPanel(
            label: 'Timing',
            title: 'Gun icin iyi pencereler',
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final item in bestTimes)
                  _CalendarInfoPill(label: item.label, highlighted: true),
              ],
            ),
          ),
        ],
        if (kDebugMode && wrongSource)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              'Data mismatch: wrong source',
              style: typo.meta.copyWith(color: Colors.orange),
            ),
          ),
        if (timeline != null &&
            eventCards.isEmpty &&
            (timeline!.lines.isNotEmpty || timeline!.summary.trim().isNotEmpty))
          Padding(
            padding: EdgeInsets.only(top: spacing.majorSectionGap),
            child: JoviaReadingPanel(
              label: 'Flow',
              title: 'Gunluk akis',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (timeline!.summary.trim().isNotEmpty)
                    Text(
                      timeline!.summary.trim(),
                      style: typo.bodyCompact.copyWith(
                        color: profile.colors.text,
                      ),
                    ),
                  for (final line in timeline!.lines.take(3)) ...[
                    const SizedBox(height: 6),
                    Text(
                      line,
                      style: typo.bodyCompact.copyWith(
                        color: profile.colors.muted,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        if (!loading &&
            eventCards.isEmpty &&
            periodCards.isEmpty &&
            error == null)
          Padding(
            padding: EdgeInsets.only(top: spacing.majorSectionGap),
            child: EmptyStateBlock(
              title: 'Secili gun sakin',
              body: timeline?.summary.trim().isNotEmpty == true
                  ? timeline!.summary.trim()
                  : 'Bu gun icin belirgin event karti yok. Takvimden baska bir gun secip akisi kontrol edebilirsin.',
            ),
          ),
        if (eventCards.isNotEmpty) ...[
          SizedBox(height: spacing.majorSectionGap),
          JoviaSectionHeader(
            label: 'Bugun',
            title: 'Bugünün vurgusu',
            body: periodOnlyNote.trim().isNotEmpty
                ? periodOnlyNote.trim()
                : 'Bugün sende öne çıkan şey burada açılıyor.',
          ),
          SizedBox(height: spacing.sectionToContent),
          for (final card in eventCards)
            if (assertDailySource(card, context: 'CalendarHub/Daily')) ...[
              Builder(
                builder: (context) {
                  final human = _buildDailyHumanCardViewModel(
                    card: card,
                    dayMeta: selectedDayMeta,
                    date: selectedDay,
                  );
                  return JoviaTopicSurface(
                    eyebrow: human.signalLabel.isNotEmpty
                        ? human.signalLabel
                        : 'Bugun',
                    title: human.feltLine,
                    body: human.cardBody.isNotEmpty
                        ? human.cardBody
                        : 'Detaylar icin karti ac.',
                    meta: human.meta,
                    secondaryAction: MinimalCTAButton(
                      label: 'Detayi ac',
                      onTap: () => onOpenEventCard(card),
                    ),
                    onTap: () => onOpenEventCard(card),
                  );
                },
              ),
              SizedBox(height: spacing.sectionToContent),
            ],
        ],
        if (periodCards.isNotEmpty) ...[
          SizedBox(height: spacing.majorSectionGap),
          _PeriodEventCardsSection(
            periodCards: periodCards,
            note: periodOnlyNote,
            onOpenPeriodCard: (card) {
              Navigator.of(context, rootNavigator: true).push(
                MaterialPageRoute<void>(
                  builder: (_) => PeriodDetailPage(
                    card: card,
                    periodCore: null,
                    routeSource: 'calendar_hub_period_section',
                  ),
                ),
              );
            },
          ),
        ],
        if (markers.isNotEmpty) ...[
          SizedBox(height: spacing.majorSectionGap),
          JoviaReadingPanel(
            label: 'Markers',
            title: 'Gunluk markerlar',
            child: Column(
              children: [
                for (var index = 0; index < markers.length; index++) ...[
                  JoviaUtilityRow(
                    title: markers[index].title.isNotEmpty
                        ? markers[index].title
                        : 'Gunluk marker',
                    body: markers[index].summary.isNotEmpty
                        ? markers[index].summary
                        : (markers[index].timeHint.isNotEmpty
                              ? markers[index].timeHint
                              : 'Detaylar icin ac.'),
                    trailing: const JoviaUiIcon(
                      asset: JoviaUiAsset.chevronRight,
                      size: 16,
                    ),
                    onTap: () => onOpenMarker(markers[index]),
                  ),
                  if (index != markers.length - 1) const ThinDivider(),
                ],
              ],
            ),
          ),
        ],
      ],
    );
  }

  String _selectedDayTitle(DateTime day) {
    final weekday = _weekdayNames[day.weekday - 1];
    final month = _monthNames[day.month - 1];
    return '$weekday, ${day.day} $month';
  }
}

class _CalendarMonthPanel extends StatelessWidget {
  const _CalendarMonthPanel({
    required this.selectedDay,
    required this.calendarDays,
    required this.onPickDate,
    required this.onSelectDay,
    required this.onShiftMonth,
  });

  final DateTime selectedDay;
  final Map<String, NarrativeCalendarDay> calendarDays;
  final VoidCallback onPickDate;
  final ValueChanged<DateTime> onSelectDay;
  final ValueChanged<int> onShiftMonth;

  static const List<String> _monthNames = <String>[
    'Ocak',
    'Subat',
    'Mart',
    'Nisan',
    'Mayis',
    'Haziran',
    'Temmuz',
    'Agustos',
    'Eylul',
    'Ekim',
    'Kasim',
    'Aralik',
  ];

  static const List<String> _weekdayLabels = <String>[
    'Pzt',
    'Sal',
    'Car',
    'Per',
    'Cum',
    'Cmt',
    'Paz',
  ];

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final monthTitle =
        '${_monthNames[selectedDay.month - 1]} ${selectedDay.year}';
    final firstDay = DateTime(selectedDay.year, selectedDay.month, 1);
    final firstWeekday = firstDay.weekday;
    final gridStart = firstDay.subtract(Duration(days: firstWeekday - 1));
    final daysInMonth = DateTime(
      selectedDay.year,
      selectedDay.month + 1,
      0,
    ).day;
    final totalCells = ((firstWeekday - 1 + daysInMonth + 6) ~/ 7) * 7;

    return JoviaReadingPanel(
      label: 'Calendar',
      title: monthTitle,
      body:
          'Takvim gibi gorunen ay gorunumu burada. Gune dokun, gunluk datayi ayni akista ac.',
      large: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              JoviaGlassIconButton(
                onTap: () => onShiftMonth(-1),
                child: const JoviaUiIcon(asset: JoviaUiAsset.back, size: 18),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Center(
                  child: Text(
                    monthTitle,
                    textAlign: TextAlign.center,
                    style: profile.typography.cardTitle.copyWith(
                      color: profile.colors.text,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              JoviaGlassIconButton(
                onTap: () => onShiftMonth(1),
                child: const JoviaUiIcon(
                  asset: JoviaUiAsset.chevronRight,
                  size: 18,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Align(
            alignment: Alignment.centerLeft,
            child: _CalendarActionChip(label: 'Tarih sec', onTap: onPickDate),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              for (final label in _weekdayLabels)
                Expanded(
                  child: Center(
                    child: Text(
                      label,
                      style: profile.typography.eyebrow.copyWith(
                        color: profile.colors.textLight,
                      ),
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 10),
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: totalCells,
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 7,
              mainAxisSpacing: 8,
              crossAxisSpacing: 8,
              childAspectRatio: 0.96,
            ),
            itemBuilder: (context, index) {
              final day = gridStart.add(Duration(days: index));
              final dayKey = _dayKey(day);
              return _CalendarDayCell(
                day: day,
                meta: calendarDays[dayKey],
                isSelected: dayKey == _dayKey(selectedDay),
                isCurrentMonth: day.month == selectedDay.month,
                onTap: () => onSelectDay(day),
              );
            },
          ),
        ],
      ),
    );
  }

  String _dayKey(DateTime value) =>
      TransitRequestBuilder.fmtDate(TransitRequestBuilder.stripDate(value));
}

class _AnimatedCalendarWeekRow extends StatelessWidget {
  const _AnimatedCalendarWeekRow({
    required this.days,
    required this.calendarDays,
    required this.selectedDay,
    required this.isAnchorRow,
    required this.rowDistance,
    required this.collapseTowardTop,
    required this.collapseProgress,
    required this.bottomSpacing,
    required this.onOpenDay,
  });

  final List<DateTime> days;
  final Map<String, NarrativeCalendarDay> calendarDays;
  final DateTime selectedDay;
  final bool isAnchorRow;
  final int rowDistance;
  final bool collapseTowardTop;
  final double collapseProgress;
  final double bottomSpacing;
  final ValueChanged<DateTime> onOpenDay;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final eased = Curves.easeInOutCubic.transform(collapseProgress);
    final rowCollapse = isAnchorRow ? 0.0 : eased;
    final translateY = isAnchorRow
        ? 0.0
        : lerpDouble(
                0,
                collapseTowardTop
                    ? -(18 + (rowDistance * 6))
                    : 18 + (rowDistance * 6),
                eased,
              ) ??
              0;
    final opacity = isAnchorRow
        ? 1.0
        : (lerpDouble(1, 0, rowCollapse) ?? 0).clamp(0.0, 1.0);
    final heightFactor = isAnchorRow
        ? 1.0
        : (lerpDouble(1, 0.02, rowCollapse) ?? 1.0);
    final spacingFactor = isAnchorRow
        ? 1.0
        : (lerpDouble(1, 0, rowCollapse) ?? 0.0);
    final anchorGlow = isAnchorRow
        ? (lerpDouble(0, 1, eased) ?? 0).toDouble()
        : 0.0;

    return Transform.translate(
      offset: Offset(0, translateY),
      child: Opacity(
        opacity: opacity,
        child: ClipRect(
          child: Align(
            alignment: collapseTowardTop
                ? Alignment.bottomCenter
                : Alignment.topCenter,
            heightFactor: heightFactor,
            child: Container(
              padding: isAnchorRow
                  ? EdgeInsets.symmetric(
                      horizontal: lerpDouble(0, 2, anchorGlow) ?? 0,
                      vertical: lerpDouble(0, 2, anchorGlow) ?? 0,
                    )
                  : EdgeInsets.zero,
              decoration: isAnchorRow
                  ? BoxDecoration(
                      borderRadius: BorderRadius.circular(
                        lerpDouble(
                              0,
                              profile.radii.cardRadius - 2,
                              anchorGlow,
                            ) ??
                            0,
                      ),
                      color: profile.colors.primary.withValues(
                        alpha: (lerpDouble(0, 0.06, anchorGlow) ?? 0).clamp(
                          0,
                          1,
                        ),
                      ),
                      border: Border.all(
                        color: profile.colors.primary.withValues(
                          alpha: (lerpDouble(0, 0.1, anchorGlow) ?? 0).clamp(
                            0,
                            1,
                          ),
                        ),
                      ),
                    )
                  : null,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      for (var index = 0; index < days.length; index++) ...[
                        Expanded(
                          child: AspectRatio(
                            aspectRatio: 0.96,
                            child: _CalendarDayCell(
                              day: days[index],
                              meta: calendarDays[_calendarDayKey(days[index])],
                              isSelected:
                                  _calendarDayKey(days[index]) ==
                                  _calendarDayKey(selectedDay),
                              isCurrentMonth:
                                  days[index].month == selectedDay.month,
                              onTap: () => onOpenDay(days[index]),
                            ),
                          ),
                        ),
                        if (index != days.length - 1) const SizedBox(width: 8),
                      ],
                    ],
                  ),
                  if (bottomSpacing > 0)
                    SizedBox(height: bottomSpacing * spacingFactor),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _CalendarDayCell extends StatelessWidget {
  const _CalendarDayCell({
    required this.day,
    required this.meta,
    required this.isSelected,
    required this.isCurrentMonth,
    required this.onTap,
  });

  final DateTime day;
  final NarrativeCalendarDay? meta;
  final bool isSelected;
  final bool isCurrentMonth;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final signals = meta?.signalsCount ?? 0;
    final critical = meta?.isCritical == true;
    final fill = isSelected
        ? Color.alphaBlend(
            colors.primary.withValues(alpha: 0.18),
            colors.surface.withValues(alpha: 0.88),
          )
        : critical
        ? colors.warmAccent.withValues(alpha: 0.12)
        : signals > 0
        ? colors.primary.withValues(alpha: 0.08)
        : colors.surface.withValues(alpha: isCurrentMonth ? 0.46 : 0.26);
    final border = isSelected
        ? colors.primary.withValues(alpha: 0.9)
        : critical
        ? colors.warmAccent.withValues(alpha: 0.72)
        : colors.separator.withValues(alpha: isCurrentMonth ? 0.46 : 0.22);
    final textColor = isCurrentMonth
        ? colors.text
        : colors.textLight.withValues(alpha: 0.65);

    return KeyedSubtree(
      key: ValueKey<String>('calendarDayCell_${_calendarDayKey(day)}'),
      child: JoviaPressable(
        onTap: onTap,
        borderRadius: BorderRadius.circular(profile.radii.cardRadius - 2),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final compact = constraints.maxHeight < 72;
            final dotSize = compact ? 4.0 : 5.0;
            final dotSpacing = compact ? 3.0 : 4.0;
            final dayStyle = profile.typography.cardTitle.copyWith(
              color: textColor,
              fontWeight: isSelected ? FontWeight.w700 : FontWeight.w600,
              fontSize: compact ? 15 : 17,
              height: 1.0,
            );

            return Container(
              padding: EdgeInsets.symmetric(
                horizontal: compact ? 7 : 8,
                vertical: compact ? 8 : 10,
              ),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(
                  profile.radii.cardRadius - 2,
                ),
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Colors.white.withValues(alpha: isSelected ? 0.16 : 0.08),
                    fill,
                  ],
                ),
                border: Border.all(color: border),
                boxShadow: isSelected
                    ? [
                        BoxShadow(
                          color: colors.primary.withValues(alpha: 0.16),
                          blurRadius: 18,
                          offset: const Offset(0, 12),
                          spreadRadius: -14,
                        ),
                      ]
                    : null,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('${day.day}', style: dayStyle),
                  const Spacer(),
                  if (signals > 0)
                    Row(
                      children: [
                        for (
                          var index = 0;
                          index < (signals > 3 ? 3 : signals);
                          index++
                        ) ...[
                          Container(
                            width: dotSize,
                            height: dotSize,
                            margin: EdgeInsets.only(
                              right: index == 2 ? 0 : dotSpacing,
                            ),
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: critical
                                  ? colors.warmAccent
                                  : colors.primary.withValues(alpha: 0.9),
                            ),
                          ),
                        ],
                      ],
                    )
                  else
                    Container(
                      width: compact ? 12 : 16,
                      height: 1,
                      color: colors.separator.withValues(alpha: 0.45),
                    ),
                  if (!compact && critical) ...[
                    const SizedBox(height: 4),
                    Text(
                      'peak',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.meta.copyWith(
                        color: colors.warmAccent,
                        fontSize: 10,
                        height: 1.0,
                      ),
                    ),
                  ] else if (!compact && signals > 0) ...[
                    const SizedBox(height: 4),
                    Text(
                      '$signals etki',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.meta.copyWith(
                        color: colors.textLight,
                        fontSize: 10,
                        height: 1.0,
                      ),
                    ),
                  ],
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

class _CalendarActionChip extends StatelessWidget {
  const _CalendarActionChip({required this.label, this.onTap});

  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return JoviaPressable(
      onTap: onTap,
      borderRadius: BorderRadius.circular(profile.radii.pillRadius + 6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(profile.radii.pillRadius + 6),
          color: profile.colors.chipBg.withValues(alpha: 0.82),
          border: Border.all(
            color: profile.colors.chipBorder.withValues(alpha: 0.86),
          ),
        ),
        child: Text(
          label,
          style: profile.typography.chipLabel.copyWith(
            color: profile.colors.text,
          ),
        ),
      ),
    );
  }
}

class _CalendarInfoPill extends StatelessWidget {
  const _CalendarInfoPill({required this.label, this.highlighted = false});

  final String label;
  final bool highlighted;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final fill = highlighted
        ? profile.colors.primary.withValues(alpha: 0.14)
        : profile.colors.chipBg.withValues(alpha: 0.72);
    final border = highlighted
        ? profile.colors.primary.withValues(alpha: 0.34)
        : profile.colors.chipBorder.withValues(alpha: 0.74);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(profile.radii.pillRadius + 4),
        color: fill,
        border: Border.all(color: border),
      ),
      child: Text(
        label,
        style: profile.typography.chipLabel.copyWith(
          color: profile.colors.text,
          fontWeight: highlighted ? FontWeight.w600 : FontWeight.w500,
        ),
      ),
    );
  }
}

class CalendarBestTimeItem {
  const CalendarBestTimeItem({required this.label});

  final String label;
}

class PeriodCalendarTab extends ConsumerStatefulWidget {
  const PeriodCalendarTab({
    super.key,
    this.profileOverride,
    this.embedded = false,
  });

  final Map<String, dynamic>? profileOverride;
  final bool embedded;

  @override
  ConsumerState<PeriodCalendarTab> createState() => _PeriodCalendarTabState();
}

class _PeriodCalendarTabState extends ConsumerState<PeriodCalendarTab> {
  final NarrativeRepository _narrativeRepository = NarrativeRepository();
  final CalendarRepository _calendarRepository = CalendarRepository();

  bool _loading = false;
  String? _error;
  PeriodCoreDto? _periodCore;
  List<PeriodCardDto> _periodCards = const <PeriodCardDto>[];
  List<PeriodPeakTimelineItemDto> _periodPeakTimeline =
      const <PeriodPeakTimelineItemDto>[];
  bool _wrongSource = false;
  String? _lastProfileKey;

  @override
  Widget build(BuildContext context) {
    final profileTheme = context.profileTheme;
    final colors = profileTheme.colors;
    final typo = profileTheme.typography;
    final profileAsync = widget.profileOverride == null
        ? ref.watch(userProfileProvider)
        : const AsyncValue<Map<String, dynamic>?>.data(null);
    final profile = widget.profileOverride ?? profileAsync.valueOrNull;
    _maybeBootstrap(profile);

    if (profileAsync.isLoading && profile == null) {
      if (widget.embedded) {
        return const Padding(
          padding: EdgeInsets.all(24),
          child: Center(child: CircularProgressIndicator()),
        );
      }
      return const Center(child: CircularProgressIndicator());
    }
    if (profileAsync.hasError && profile == null) {
      if (widget.embedded) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: JoviaReadingPanel(
            label: 'Timing',
            title: 'Profil verisi yuklenemedi',
            body:
                'Period akisini gormek icin once profil verisinin acilmasi gerekiyor.',
          ),
        );
      }
      return const _ErrorText('Profil verisi yuklenemedi.');
    }
    if (!TransitRequestBuilder.hasProfile(profile)) {
      if (widget.embedded) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: JoviaReadingPanel(
            label: 'Timing',
            title: 'Dogum verisini tamamla',
            body:
                'Period akisi, profilindeki dogum tarihi, saat ve yer bilgisi tamamlandiginda acilir.',
          ),
        );
      }
      return const _ErrorText(
        'Period icin once profil dogum verisini tamamlayin.',
      );
    }

    final cards = _periodCards;
    for (final card in cards) {
      assert(card is! EventCardDto, 'Data mismatch: wrong source');
    }

    if (widget.embedded) {
      final visibleCards = cards.take(3).toList(growable: false);

      return Padding(
        padding: EdgeInsets.fromLTRB(
          profileTheme.spacing.pageHorizontal,
          profileTheme.spacing.pageTop,
          profileTheme.spacing.pageHorizontal,
          0,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            JoviaSectionHeader(
              label: 'Timing',
              title: 'Sana ozel zamanlama',
              body: _condenseCopy(
                _periodCore?.coreStory.trim().isNotEmpty == true
                    ? _periodCore!.coreStory.trim()
                    : 'Onunde acilan donemleri burada daha sakin bir sirayla okuyabilirsin.',
              ),
            ),
            SizedBox(height: profileTheme.spacing.sectionToContent),
            if (_periodCore != null)
              JoviaReadingPanel(
                label: 'Period',
                title: _periodCore!.title.trim().isNotEmpty
                    ? _periodCore!.title.trim()
                    : 'Bu donemin ana temasi',
                body: _condenseCopy(
                  _periodCore!.coreStory.trim().isNotEmpty
                      ? _periodCore!.coreStory.trim()
                      : _periodCore!.bigPicture,
                  maxChars: 200,
                ),
              ),
            if (_periodCore != null)
              SizedBox(height: profileTheme.spacing.majorSectionGap),
            if (_error != null) ...[
              Text(
                _error!,
                style: typo.meta.copyWith(
                  color: Theme.of(context).colorScheme.error,
                ),
              ),
              SizedBox(height: profileTheme.spacing.sectionToContent),
            ],
            if (_loading && visibleCards.isEmpty)
              const EmptyStateBlock(
                title: 'Timing hazirlaniyor',
                body: 'Kisisel donemlerin editoryal listesi yukleniyor.',
              )
            else if (!_loading && visibleCards.isEmpty)
              const EmptyStateBlock(
                title: 'Secili donem yok',
                body:
                    'Aktif period kartlari hazir oldugunda burada goreceksin.',
              )
            else
              Column(
                children: [
                  for (var index = 0; index < visibleCards.length; index++) ...[
                    JoviaInsightListItem(
                      title: visibleCards[index].title,
                      body: _condenseCopy(
                        visibleCards[index].subtitle,
                        maxChars: 180,
                      ),
                      meta: <String>[
                        if (visibleCards[index].timeHint.trim().isNotEmpty)
                          visibleCards[index].timeHint.trim(),
                      ],
                      trailing: JoviaUiIcon(
                        asset: JoviaUiAsset.chevronRight,
                        color: colors.primary,
                        size: 16,
                      ),
                      onTap: () {
                        Navigator.of(context, rootNavigator: true).push(
                          MaterialPageRoute<void>(
                            builder: (_) => PeriodDetailPage(
                              card: visibleCards[index],
                              periodCore: _periodCore,
                              routeSource: 'profile_timing',
                            ),
                          ),
                        );
                      },
                    ),
                    if (index != visibleCards.length - 1) const ThinDivider(),
                  ],
                ],
              ),
            SizedBox(height: profileTheme.spacing.majorSectionGap),
            JoviaPrimaryButton(
              label: 'Takvimi ac',
              onTap: () {
                Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (_) => CalendarHubPage(
                      profileOverride: widget.profileOverride,
                    ),
                  ),
                );
              },
            ),
            if (_periodPeakTimeline.isNotEmpty) ...[
              SizedBox(height: profileTheme.spacing.majorSectionGap),
              JoviaReadingPanel(
                label: 'Timeline',
                title: 'Kisa peak listesi',
                child: PeriodPeakTimelineWidget(
                  items: _periodPeakTimeline,
                  compact: true,
                  framed: false,
                  title: 'Kisa peak listesi',
                  subtitle:
                      'Onundeki etkilerin guclendigi tarihleri sirayla takip et.',
                  onTapItem: (item) => _openTimelineDetail(context, item),
                ),
              ),
            ],
          ],
        ),
      );
    }

    final content = Padding(
      padding: widget.embedded
          ? EdgeInsets.fromLTRB(
              profileTheme.spacing.pageHorizontal,
              profileTheme.spacing.sm,
              profileTheme.spacing.pageHorizontal,
              0,
            )
          : EdgeInsets.fromLTRB(
              profileTheme.spacing.pageHorizontal,
              profileTheme.spacing.pageTop,
              profileTheme.spacing.pageHorizontal,
              profileTheme.spacing.pageBottom,
            ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (_loading) const LinearProgressIndicator(),
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(
              _error!,
              style: typo.meta.copyWith(
                color: Theme.of(context).colorScheme.error,
              ),
            ),
          ],
          if (kDebugMode && _wrongSource)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                'Data mismatch: wrong source',
                style: typo.meta.copyWith(color: Colors.orange),
              ),
            ),
          _PeriodCoreHero(core: _periodCore),
          const SizedBox(height: 10),
          if (_periodPeakTimeline.isNotEmpty) ...[
            PeriodPeakTimelineWidget(
              items: _periodPeakTimeline,
              compact: widget.embedded,
              onTapItem: (item) => _openTimelineDetail(context, item),
            ),
            const SizedBox(height: 10),
          ],
          if (!_loading && cards.isEmpty)
            JoviaReadingPanel(
              label: 'Period',
              title: 'Donem karti bulunamadi',
              body: 'Period marker/kart bulunamadi.',
            ),
          if (cards.isNotEmpty) ...[
            JoviaReadingPanel(
              label: 'Timing',
              title: 'Donem kartlari',
              child: Column(
                children: [
                  for (var index = 0; index < cards.length; index++)
                    if (assertPeriodSource(
                      cards[index],
                      context: 'CalendarHub/Period/Card',
                    )) ...[
                      JoviaUtilityRow(
                        title: cards[index].title,
                        body: cards[index].subtitle,
                        meta: [
                          if (cards[index].timeHint.trim().isNotEmpty)
                            cards[index].timeHint.trim(),
                        ],
                        trailing: const JoviaUiIcon(
                          asset: JoviaUiAsset.chevronRight,
                          size: 16,
                        ),
                        onTap: () {
                          Navigator.of(context, rootNavigator: true).push(
                            MaterialPageRoute<void>(
                              builder: (_) => PeriodDetailPage(
                                card: cards[index],
                                periodCore: _periodCore,
                                routeSource: 'calendar_hub_period',
                              ),
                            ),
                          );
                        },
                      ),
                      if (index != cards.length - 1) const ThinDivider(),
                    ],
                ],
              ),
            ),
          ],
        ],
      ),
    );

    if (widget.embedded) {
      return content;
    }

    return RefreshIndicator(
      onRefresh: () => _loadPeriod(profile!),
      child: ListView(padding: EdgeInsets.zero, children: [content]),
    );
  }

  Future<void> _loadPeriod(Map<String, dynamic> profile) async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final now = DateTime.now();
      final narrativeMap = await _narrativeRepository.fetchDailyNarrative(
        profile: profile,
        selectedDate: now,
      );
      final narrative = NarrativeResponse.fromMap(narrativeMap);
      final periodEvents = pickPeriodEventCards(
        narrative.eventCards,
        context: 'CalendarHub/Period',
      );
      final narrativeCards = <PeriodCardDto>[
        for (var i = 0; i < periodEvents.length; i++)
          PeriodCardDto.fromEventCard(eventCard: periodEvents[i], index: i),
      ];
      PeriodCalendarDto calendar = const PeriodCalendarDto(
        periodCore: null,
        markers: <PeriodMarkerDto>[],
        themes: <PeriodThemeDto>[],
        intentSummaries: <IntentSummaryDto>[],
        cards: <PeriodCardDto>[],
        hasWrongSource: false,
      );
      if (narrative.periodCore == null && narrativeCards.isEmpty) {
        final calendarMap = await _calendarRepository.fetchCalendar(
          profile: profile,
          focusedDate: now,
          include: 'markers,themes,intent_summary',
        );
        calendar = PeriodCalendarDto.fromMap(calendarMap);
      }
      final cards = narrativeCards.isNotEmpty ? narrativeCards : calendar.cards;
      if (!mounted) {
        return;
      }
      setState(() {
        _periodCore = narrative.periodCore ?? calendar.periodCore;
        _periodCards = cards;
        _periodPeakTimeline = narrative.periodPeakTimeline;
        _wrongSource = calendar.hasWrongSource;
        _loading = false;
      });
    } on DioException catch (exc) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _error = _friendlyPeriodError(exc);
      });
    } catch (exc) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _error = exc.toString();
      });
    }
  }

  void _maybeBootstrap(Map<String, dynamic>? profile) {
    if (!TransitRequestBuilder.hasProfile(profile)) {
      return;
    }
    final now = DateTime.now();
    final key =
        '${profile?['birth_date']}|${profile?['birth_time']}|${profile?['place'] ?? profile?['city']}|${profile?['timezone']}|${now.year}-${now.month}';
    if (_lastProfileKey == key) {
      return;
    }
    _lastProfileKey = key;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || profile == null) {
        return;
      }
      _loadPeriod(profile);
    });
  }

  String _friendlyPeriodError(DioException exc) {
    if (exc.type == DioExceptionType.receiveTimeout ||
        exc.type == DioExceptionType.connectionTimeout) {
      return 'Transit ozeti zamaninda donmedi. Donem ekranini hafiflettim; tekrar dener misin?';
    }
    final status = exc.response?.statusCode;
    if (status == 422) {
      return 'Gonderilen tarih veya profil alanlari gecersiz (422).';
    }
    return exc.message ?? 'Period veri alinamadi.';
  }

  void _openTimelineDetail(
    BuildContext context,
    PeriodPeakTimelineItemDto item,
  ) {
    final eventCard = item.eventCard;
    if (eventCard == null) {
      return;
    }
    final card = PeriodCardDto.fromEventCard(eventCard: eventCard, index: 0);
    Navigator.of(context, rootNavigator: true).push(
      MaterialPageRoute<void>(
        builder: (_) => PeriodDetailPage(
          card: card,
          periodCore: _periodCore,
          routeSource: 'calendar_hub_timeline',
        ),
      ),
    );
  }

  String _condenseCopy(String text, {int maxChars = 220}) {
    final trimmed = text.trim();
    if (trimmed.isEmpty) {
      return '';
    }
    final sentences = trimmed
        .split(RegExp(r'(?<=[.!?])\s+'))
        .map((item) => item.trim())
        .where((item) => item.isNotEmpty)
        .toList();
    final joined = sentences.isEmpty ? trimmed : sentences.take(2).join(' ');
    if (joined.length <= maxChars) {
      return joined;
    }
    return '${joined.substring(0, maxChars).trimRight()}...';
  }
}

class _PeriodCoreHero extends StatelessWidget {
  const _PeriodCoreHero({required this.core});

  final PeriodCoreDto? core;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final typo = profile.typography;

    return JoviaSurfaceCard(
      child: Padding(
        padding: EdgeInsets.zero,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              core?.title.trim().isNotEmpty == true
                  ? core!.title.trim()
                  : 'Bu Donemin Ana Temasi',
              style: typo.cardTitle.copyWith(color: colors.text),
            ),
            const SizedBox(height: 8),
            Text(
              core?.coreStory.trim().isNotEmpty == true
                  ? core!.coreStory.trim()
                  : 'Period ozeti henuz hazir degil.',
              style: typo.bodyCompact.copyWith(color: colors.muted),
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorText extends StatelessWidget {
  const _ErrorText(this.message);

  final String message;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return JoviaPageScaffold(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          JoviaSurfaceCard(
            child: Text(
              message,
              style: profile.typography.bodyCompact.copyWith(
                color: profile.colors.text,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
