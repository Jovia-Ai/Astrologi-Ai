import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/tabs/period_detail_page.dart';
import 'package:mobile/app/tabs/period_marker_detail_page.dart';
import 'package:mobile/app/tabs/transit_detail_page.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/timing/source_guards.dart';
import 'package:mobile/app/timing/transit_repositories.dart';

class CalendarHubPage extends StatelessWidget {
  const CalendarHubPage({super.key, this.profileOverride});

  final Map<String, dynamic>? profileOverride;

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Calendar'),
          bottom: const TabBar(
            tabs: <Tab>[Tab(text: 'Daily'), Tab(text: 'Period')],
          ),
        ),
        body: TabBarView(
          children: <Widget>[
            DailyCalendarTab(profileOverride: profileOverride),
            PeriodCalendarTab(profileOverride: profileOverride),
          ],
        ),
      ),
    );
  }
}

class DailyCalendarTab extends ConsumerStatefulWidget {
  const DailyCalendarTab({super.key, this.profileOverride});

  final Map<String, dynamic>? profileOverride;

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
  TimelineDto? _dailyTimeline;
  bool _wrongSource = false;
  String? _lastProfileKey;

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
    if (profileAsync.hasError && profile == null) {
      return _ErrorText('Profil verisi yuklenemedi.');
    }
    if (!TransitRequestBuilder.hasProfile(profile)) {
      return const _ErrorText('Takvim icin once profil dogum verisini tamamlayin.');
    }

    return RefreshIndicator(
      onRefresh: () => _loadDaily(profile!),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: ListTile(
              leading: const Icon(Icons.event),
              title: const Text('Tarih sec'),
              subtitle: Text(TransitRequestBuilder.fmtDate(_selectedDay)),
              onTap: () async {
                final picked = await showDatePicker(
                  context: context,
                  initialDate: _selectedDay,
                  firstDate: DateTime.now().subtract(const Duration(days: 365)),
                  lastDate: DateTime.now().add(const Duration(days: 365)),
                );
                if (picked == null) {
                  return;
                }
                setState(
                  () => _selectedDay = TransitRequestBuilder.stripDate(picked),
                );
                await _loadDaily(profile!);
              },
            ),
          ),
          const SizedBox(height: 10),
          if (_loading) const LinearProgressIndicator(),
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(_error!, style: const TextStyle(color: Colors.red)),
          ],
          if (_bestTimes.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Text(
              'Best Times',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            SizedBox(
              height: 44,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _bestTimes.length,
                separatorBuilder: (_, _) => const SizedBox(width: 8),
                itemBuilder: (context, index) {
                  final item = _bestTimes[index];
                  return Chip(
                    label: Text(
                      item.label,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  );
                },
              ),
            ),
          ],
          if (kDebugMode && _wrongSource)
            const Padding(
              padding: EdgeInsets.only(top: 8),
              child: Text(
                'Data mismatch: wrong source',
                style: TextStyle(color: Colors.orange),
              ),
            ),
          if (!_loading && _dailyEventCards.isEmpty && _error == null)
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Text(
                _dailyTimeline?.summary.trim().isNotEmpty == true
                    ? _dailyTimeline!.summary.trim()
                    : 'Secili gun icin daily event card bulunamadi.',
              ),
            ),
          if (_dailyTimeline != null &&
              _dailyEventCards.isEmpty &&
              (_dailyTimeline!.lines.isNotEmpty ||
                  _dailyTimeline!.summary.trim().isNotEmpty)) ...[
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Gunluk Akis',
                      style: TextStyle(fontWeight: FontWeight.w700),
                    ),
                    if (_dailyTimeline!.summary.trim().isNotEmpty) ...[
                      const SizedBox(height: 6),
                      Text(_dailyTimeline!.summary.trim()),
                    ],
                    for (final line in _dailyTimeline!.lines.take(3)) ...[
                      const SizedBox(height: 6),
                      Text(line),
                    ],
                  ],
                ),
              ),
            ),
          ],
          if (_dailyEventCards.isNotEmpty) ...[
            const SizedBox(height: 8),
            for (final card in _dailyEventCards)
              if (assertDailySource(card, context: 'CalendarHub/Daily'))
                Card(
                  child: InkWell(
                    onTap: () {
                      Navigator.of(context, rootNavigator: true).push(
                        MaterialPageRoute<void>(
                          builder: (_) => TransitDetailPage(card: card),
                        ),
                      );
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            card.title.isNotEmpty ? card.title : 'Aktif Transit',
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                          if (card.signatureTr.trim().isNotEmpty ||
                              card.signature.trim().isNotEmpty) ...[
                            const SizedBox(height: 6),
                            Text(
                              card.signatureTr.trim().isNotEmpty
                                  ? card.signatureTr.trim()
                                  : card.signature.trim(),
                              style: const TextStyle(color: Colors.black54),
                            ),
                          ],
                          const SizedBox(height: 6),
                          Text(
                            card.teaser.trim().isNotEmpty
                                ? card.teaser.trim()
                                : (card.whyNow.trim().isNotEmpty
                                      ? card.whyNow.trim()
                                      : 'Detaylar icin karti ac.'),
                          ),
                          if (card.upper.trim().isNotEmpty) ...[
                            const SizedBox(height: 6),
                            Text(
                              card.upper.trim(),
                              style: const TextStyle(color: Colors.black87),
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ),
          ],
          if (_dailyMarkers.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Text(
              'Markerlar',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            for (final marker in _dailyMarkers)
              Card(
                child: ListTile(
                  title: Text(
                    marker.title.isNotEmpty ? marker.title : 'Gunluk marker',
                  ),
                  subtitle: Text(
                    marker.summary.isNotEmpty
                        ? marker.summary
                        : (marker.timeHint.isNotEmpty
                              ? marker.timeHint
                              : 'Detaylar icin ac.'),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    Navigator.of(context, rootNavigator: true).push(
                      MaterialPageRoute<void>(
                        builder: (_) =>
                            PeriodMarkerDetailPage(marker: marker),
                      ),
                    );
                  },
                ),
              ),
          ],
        ],
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

    final direct = pickList(publicRaw['best_times']) ?? pickList(publicRaw['featured_windows']);
    if (direct != null) {
      for (final row in direct) {
        if (row is! Map) {
          continue;
        }
        final mapRow = Map<String, dynamic>.from(row);
        final label = (mapRow['label'] ??
                mapRow['title'] ??
                mapRow['time_label'] ??
                mapRow['window'] ??
                mapRow['date'] ??
                '')
            .toString()
            .trim();
        final reason = (mapRow['focus'] ?? mapRow['theme'] ?? mapRow['reason'] ?? '')
            .toString()
            .trim();
        if (label.isEmpty && reason.isEmpty) {
          continue;
        }
        out.add(_BestTimeItem(label: reason.isEmpty ? label : '$label • $reason'));
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
      out.add(_BestTimeItem(label: detail.isEmpty ? label : '$label • $detail'));
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
        out.add(_BestTimeItem(label: score.isEmpty ? date : '$date • skor $score'));
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
      final label = (mapRow['label'] ??
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
      out.add(_BestTimeItem(label: focus.isEmpty ? label : '$label • $focus'));
    }
    return out.take(6).toList(growable: false);
  }
}

class _BestTimeItem {
  const _BestTimeItem({required this.label});

  final String label;
}

class PeriodCalendarTab extends ConsumerStatefulWidget {
  const PeriodCalendarTab({super.key, this.profileOverride, this.embedded = false});

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
  bool _wrongSource = false;
  String? _lastProfileKey;

  @override
  Widget build(BuildContext context) {
    final profileAsync = widget.profileOverride == null
        ? ref.watch(userProfileProvider)
        : const AsyncValue<Map<String, dynamic>?>.data(null);
    final profile = widget.profileOverride ?? profileAsync.valueOrNull;
    _maybeBootstrap(profile);

    if (profileAsync.isLoading && profile == null) {
      if (widget.embedded) {
        return const Padding(
          padding: EdgeInsets.all(16),
          child: Center(child: CircularProgressIndicator()),
        );
      }
      return const Center(child: CircularProgressIndicator());
    }
    if (profileAsync.hasError && profile == null) {
      if (widget.embedded) {
        return const Padding(
          padding: EdgeInsets.all(16),
          child: Card(
            child: Padding(
              padding: EdgeInsets.all(12),
              child: Text('Profil verisi yuklenemedi.'),
            ),
          ),
        );
      }
      return const _ErrorText('Profil verisi yuklenemedi.');
    }
    if (!TransitRequestBuilder.hasProfile(profile)) {
      if (widget.embedded) {
        return const Padding(
          padding: EdgeInsets.all(16),
          child: Card(
            child: Padding(
              padding: EdgeInsets.all(12),
              child: Text('Period icin once profil dogum verisini tamamlayin.'),
            ),
          ),
        );
      }
      return const _ErrorText('Period icin once profil dogum verisini tamamlayin.');
    }

    final cards = _periodCards;
    for (final card in cards) {
      assert(card is! EventCardDto, 'Data mismatch: wrong source');
    }

    final content = Padding(
      padding: widget.embedded
          ? const EdgeInsets.fromLTRB(16, 10, 16, 0)
          : const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (_loading) const LinearProgressIndicator(),
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(_error!, style: const TextStyle(color: Colors.red)),
          ],
          if (kDebugMode && _wrongSource)
            const Padding(
              padding: EdgeInsets.only(top: 8),
              child: Text(
                'Data mismatch: wrong source',
                style: TextStyle(color: Colors.orange),
              ),
            ),
          _PeriodCoreHero(core: _periodCore),
          const SizedBox(height: 10),
          if (!_loading && cards.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(12),
                child: Text('Period marker/kart bulunamadi.'),
              ),
            ),
          if (cards.isNotEmpty) ...[
            const Padding(
              padding: EdgeInsets.only(top: 4, bottom: 8),
              child: Text(
                'Donem Kartlari',
                style: TextStyle(fontWeight: FontWeight.w700),
              ),
            ),
          ],
          for (final card in cards)
            if (assertPeriodSource(card, context: 'CalendarHub/Period/Card'))
              Card(
                child: ListTile(
                  title: Text(card.title),
                  subtitle: Text(
                    card.subtitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    Navigator.of(context, rootNavigator: true).push(
                      MaterialPageRoute<void>(
                        builder: (_) => PeriodDetailPage(
                          card: card,
                          periodCore: _periodCore,
                        ),
                      ),
                    );
                  },
                ),
              ),
        ],
      ),
    );

    if (widget.embedded) {
      return content;
    }

    return RefreshIndicator(
      onRefresh: () => _loadPeriod(profile!),
      child: ListView(
        padding: EdgeInsets.zero,
        children: [content],
      ),
    );
  }

  Future<void> _loadPeriod(Map<String, dynamic> profile) async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final responses = await Future.wait<Map<String, dynamic>>([
        _narrativeRepository.fetchDailyNarrative(
          profile: profile,
          selectedDate: DateTime.now(),
        ),
        _calendarRepository.fetchCalendar(
          profile: profile,
          focusedDate: DateTime.now(),
          include: 'markers,themes,intent_summary',
        ),
      ]);
      final narrative = NarrativeResponse.fromMap(responses[0]);
      final calendar = PeriodCalendarDto.fromMap(responses[1]);
      final periodEvents = pickPeriodEventCards(
        narrative.eventCards,
        context: 'CalendarHub/Period',
      );
      final cards = <PeriodCardDto>[
        for (var i = 0; i < periodEvents.length; i++)
          PeriodCardDto.fromEventCard(eventCard: periodEvents[i], index: i),
      ];
      if (!mounted) {
        return;
      }
      setState(() {
        _periodCore = narrative.periodCore ?? calendar.periodCore;
        _periodCards = cards;
        _wrongSource = calendar.hasWrongSource;
        _loading = false;
      });
    } on DioException catch (exc) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _error = exc.message ?? 'Period veri alinamadi.';
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
}

class _PeriodCoreHero extends StatelessWidget {
  const _PeriodCoreHero({required this.core});

  final PeriodCoreDto? core;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              core?.title.trim().isNotEmpty == true
                  ? core!.title.trim()
                  : 'Bu Donemin Ana Temasi',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text(
              core?.coreStory.trim().isNotEmpty == true
                  ? core!.coreStory.trim()
                  : 'Period ozeti henuz hazir degil.',
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
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Text(message),
          ),
        ),
      ],
    );
  }
}
