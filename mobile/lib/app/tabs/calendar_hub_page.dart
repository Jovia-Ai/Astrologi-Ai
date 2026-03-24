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
import 'package:mobile/design/widgets/jovia_assets.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

enum _CalendarHubTab { daily, period }

class CalendarHubPage extends StatefulWidget {
  const CalendarHubPage({super.key, this.profileOverride});

  final Map<String, dynamic>? profileOverride;

  @override
  State<CalendarHubPage> createState() => _CalendarHubPageState();
}

class _CalendarHubPageState extends State<CalendarHubPage> {
  _CalendarHubTab _tab = _CalendarHubTab.daily;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final spacing = profile.spacing;
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
      body: SafeArea(
        top: false,
        child: JoviaPageScaffold(
          padding: EdgeInsets.fromLTRB(
            spacing.pageHorizontal,
            spacing.xs,
            spacing.pageHorizontal,
            spacing.pageBottom,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              JoviaSectionHeader(
                label: 'Timing',
                title: 'Gunluk takvim',
                body:
                    'Tum tarihleri ay gorunumunde takip et, bir gune dokunup gunluk akisi ve donem etkilerini ayni yerden oku.',
                variant: JoviaSectionHeaderVariant.editorial,
              ),
              SizedBox(height: spacing.sectionToContent),
              JoviaSegmentedControl<_CalendarHubTab>(
                value: _tab,
                options: _CalendarHubTab.values,
                labelBuilder: (tab) => switch (tab) {
                  _CalendarHubTab.daily => 'Takvim',
                  _CalendarHubTab.period => 'Period',
                },
                onChanged: (tab) => setState(() => _tab = tab),
              ),
              SizedBox(height: spacing.majorSectionGap),
              Expanded(
                child: AnimatedSwitcher(
                  duration: profile.motion.page,
                  switchInCurve: profile.motion.curve,
                  switchOutCurve: profile.motion.curve,
                  child: _tab == _CalendarHubTab.daily
                      ? DailyCalendarTab(
                          key: const ValueKey<String>('calendar_daily'),
                          profileOverride: widget.profileOverride,
                          embedded: true,
                        )
                      : PeriodCalendarTab(
                          key: const ValueKey<String>('calendar_period'),
                          profileOverride: widget.profileOverride,
                          embedded: true,
                        ),
                ),
              ),
            ],
          ),
        ),
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
  List<PeriodMarkerDto> _dailyMarkers = const <PeriodMarkerDto>[];
  List<_BestTimeItem> _bestTimes = const <_BestTimeItem>[];
  Map<String, NarrativeCalendarDay> _calendarDays =
      const <String, NarrativeCalendarDay>{};
  TimelineDto? _dailyTimeline;
  bool _wrongSource = false;
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
    final timelineSummary = _dailyTimeline?.summary.trim() ?? '';
    if (timelineSummary.isNotEmpty) {
      return _condenseCopy(timelineSummary, maxChars: 180);
    }
    final day = _calendarDays[_dayKey(_selectedDay)];
    if (day != null && day.labels.isNotEmpty) {
      return _condenseCopy(day.labels.take(2).join(' • '), maxChars: 180);
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
          ? const <_BestTimeItem>[]
          : await _loadBestTimesFallback(profile);
      final periodInNarrative =
          narrative.periodCore != null && narrative.eventCards.isEmpty;
      if (periodInNarrative) {
        debugPrint('DailyCalendarTab ignored period-only narrative payload.');
      }
      final dailyCards = pickDailyEventCards(
        narrative.eventCards,
        context: 'CalendarHub/Daily',
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _dailyEventCards = dailyCards;
        _dailyMarkers = periodCalendar.markers;
        _calendarDays = narrative.calendarDays;
        _dailyTimeline = narrative.timeline;
        _bestTimes = narrativeBest.isNotEmpty ? narrativeBest : fallbackBest;
        _wrongSource = periodInNarrative || dailyCards.isEmpty;
        _loading = false;
      });
    } on DioException catch (exc) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _dailyMarkers = const <PeriodMarkerDto>[];
        _calendarDays = const <String, NarrativeCalendarDay>{};
        _dailyTimeline = null;
        _bestTimes = const <_BestTimeItem>[];
        _error = _friendlyError(exc);
      });
    } catch (exc) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _dailyMarkers = const <PeriodMarkerDto>[];
        _calendarDays = const <String, NarrativeCalendarDay>{};
        _dailyTimeline = null;
        _bestTimes = const <_BestTimeItem>[];
        _error = exc.toString();
      });
    }
  }

  Future<List<_BestTimeItem>> _loadBestTimesFallback(
    Map<String, dynamic> profile,
  ) async {
    try {
      final map = await _calendarRepository.fetchBestTimes(
        profile: profile,
        focusedDate: _selectedDay,
      );
      return _extractBestTimesFromBestTimesMap(map);
    } catch (_) {
      return const <_BestTimeItem>[];
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

  List<_BestTimeItem> _extractBestTimesFromNarrativeMap(
    Map<String, dynamic> data,
  ) {
    final out = <_BestTimeItem>[];
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
          _BestTimeItem(label: reason.isEmpty ? label : '$label • $reason'),
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
        _BestTimeItem(label: detail.isEmpty ? label : '$label • $detail'),
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
          _BestTimeItem(label: score.isEmpty ? date : '$date • skor $score'),
        );
      }
    }
    return out.take(6).toList(growable: false);
  }

  List<_BestTimeItem> _extractBestTimesFromBestTimesMap(
    Map<String, dynamic> data,
  ) {
    final out = <_BestTimeItem>[];
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
      out.add(_BestTimeItem(label: focus.isEmpty ? label : '$label • $focus'));
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
  final List<_BestTimeItem> bestTimes;
  final List<EventCardDto> eventCards;
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
          body: selectedSummary,
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
                  if ((selectedDayMeta?.signalsCount ?? 0) > 0)
                    _CalendarInfoPill(
                      label: '${selectedDayMeta!.signalsCount} sinyal',
                    ),
                  if (selectedDayMeta?.isCritical == true)
                    const _CalendarInfoPill(
                      label: 'Kritik gun',
                      highlighted: true,
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
        if (!loading && eventCards.isEmpty && error == null)
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
            label: 'Cards',
            title: 'Gunluk kartlar',
            body: 'Secili tarihin aktif transit anlatimi burada aciliyor.',
          ),
          SizedBox(height: spacing.sectionToContent),
          for (final card in eventCards)
            if (assertDailySource(card, context: 'CalendarHub/Daily')) ...[
              JoviaTopicSurface(
                eyebrow: card.signatureTr.trim().isNotEmpty
                    ? card.signatureTr.trim()
                    : (card.signature.trim().isNotEmpty
                          ? card.signature.trim()
                          : 'Aktif transit'),
                title: card.title.isNotEmpty ? card.title : 'Aktif Transit',
                body: card.opening.trim().isNotEmpty
                    ? card.opening.trim()
                    : (card.whyNow.trim().isNotEmpty
                          ? card.whyNow.trim()
                          : 'Detaylar icin karti ac.'),
                meta: [
                  if (card.whatItBuilds.trim().isNotEmpty)
                    card.whatItBuilds.trim(),
                ],
                secondaryAction: MinimalCTAButton(
                  label: 'Detayi ac',
                  onTap: () => onOpenEventCard(card),
                ),
                onTap: () => onOpenEventCard(card),
              ),
              SizedBox(height: spacing.sectionToContent),
            ],
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

    return JoviaPressable(
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
              borderRadius: BorderRadius.circular(profile.radii.cardRadius - 2),
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

class _BestTimeItem {
  const _BestTimeItem({required this.label});

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
      final narrativeMap = await _narrativeRepository.fetchTransitSummary(
        profile: profile,
        transitDate: now,
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
