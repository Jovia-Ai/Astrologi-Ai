import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api_client.dart';
import '../api/api_environment.dart';
import '../chart_lab/chart_templates.dart';
import '../chart_lab/endpoint_catalog.dart';
import '../chart_lab/event_story_screen.dart';
import '../chart_lab/models/event_card_dto.dart';
import '../chart_lab/widgets/event_card_tile.dart';
import '../profile/profile_providers.dart';

class ChartLabPage extends ConsumerStatefulWidget {
  const ChartLabPage({super.key});

  @override
  ConsumerState<ChartLabPage> createState() => _ChartLabPageState();
}

class _ChartLabPageState extends ConsumerState<ChartLabPage> {
  final _baseUrlController = TextEditingController(
    text: ApiEnvironment.apiBaseUrl,
  );
  final _pathController = TextEditingController(text: '/api/v1/charts/build');
  final _requestController = TextEditingController();
  final _queryController = TextEditingController(text: '{}');
  final _encoder = const JsonEncoder.withIndent('  ');

  late EndpointAction _selectedAction;
  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _lastResponse;
  String? _lastText;
  int? _statusCode;
  DateTime _focusedMonth = _firstDayOfMonth(DateTime.now());
  DateTime _selectedDay = _stripDate(DateTime.now());
  Map<String, List<Map<String, dynamic>>> _eventsByDay =
      <String, List<Map<String, dynamic>>>{};
  List<Map<String, dynamic>> _bestTimeItems = <Map<String, dynamic>>[];
  String? _bestTimesError;
  Map<String, dynamic>? _bestTimesErrorBody;
  String? _periodSummaryText;
  bool _periodSummaryLoading = false;
  String? _periodSummaryError;
  bool _resultExpanded = true;
  bool _showDevControls = false;
  String _lastAutofillKey = '';

  @override
  void initState() {
    super.initState();
    _selectedAction = endpointCatalog.first;
    _applyAction(_selectedAction);
  }

  @override
  void dispose() {
    _baseUrlController.dispose();
    _pathController.dispose();
    _requestController.dispose();
    _queryController.dispose();
    super.dispose();
  }

  void _applyAction(EndpointAction action, {Map<String, dynamic>? profile}) {
    _pathController.text = action.path;
    final payload = _buildPayloadForAction(action, profile);
    final encoded = _encoder.convert(payload);
    if (action.method == 'POST') {
      _requestController.text = encoded;
    } else {
      _queryController.text = encoded;
    }
  }

  Map<String, dynamic> _buildPayloadForAction(
    EndpointAction action,
    Map<String, dynamic>? profile,
  ) {
    final base = Map<String, dynamic>.from(
      chartTemplates[action.templateKey] ?? const <String, dynamic>{},
    );
    if (profile == null) {
      return base;
    }

    final city = (profile['city'] ?? '').toString().trim();
    final country = (profile['country'] ?? '').toString().trim();
    final birthDate = (profile['birth_date'] ?? '').toString();
    final birthTime = (profile['birth_time'] ?? '').toString();
    final normalizedBirthTime = _normalizeBirthTime(birthTime);
    final name = (profile['name'] ?? '').toString();
    final birthPlace = city.isEmpty ? country : city;
    final now = DateTime.now();
    final end = now.add(const Duration(days: 14));
    final startIso = _asDate(now);
    final endIso = _asDate(end);

    if (action.path.startsWith('/interpret')) {
      base['birth_date'] = birthDate;
      base['birth_time'] = normalizedBirthTime;
      base['birth_place'] = birthPlace;
      base['locale'] = (base['locale'] as String?) ?? 'tr';
    }

    if (action.path.startsWith('/transits')) {
      base['birth_date'] = birthDate;
      base['birth_time'] = normalizedBirthTime;
      base['birth_place'] = birthPlace;
      base['tz'] = 'Europe/Istanbul';
      if (action.path == '/transits') {
        base['transit_date'] = (base['transit_date'] as String?) ?? startIso;
        base['transit_place'] =
            (base['transit_place'] as String?) ?? birthPlace;
        base.remove('start');
        base.remove('end');
      } else {
        base['start'] = (base['start'] as String?) ?? startIso;
        base['end'] = (base['end'] as String?) ?? endIso;
      }
    }

    if (action.path.startsWith('/transit/calendar')) {
      base['birth_date'] = birthDate;
      base['birth_time'] = normalizedBirthTime;
      base['birth_place'] = birthPlace;
      base['tz'] = 'Europe/Istanbul';
      if (action.id == 'transit.calendar') {
        base['start'] = (base['start'] as String?) ?? startIso;
        base['end'] = (base['end'] as String?) ?? endIso;
        base['view'] = (base['view'] as String?) ?? 'public';
        base.remove('date');
      } else if (action.path == '/transit/calendar/day') {
        base['date'] = (base['date'] as String?) ?? _asDate(_selectedDay);
        base['view'] = (base['view'] as String?) ?? 'public';
        base.remove('start');
        base.remove('end');
      } else if (action.path == '/transit/calendar') {
        base['start'] = (base['start'] as String?) ?? startIso;
        base['end'] = (base['end'] as String?) ?? endIso;
        base['view'] = (base['view'] as String?) ?? 'public';
        base.remove('date');
      } else if (action.path == '/transit/calendar/best-times') {
        base['start'] = (base['start'] as String?) ?? startIso;
        base['end'] = (base['end'] as String?) ?? endIso;
        base['intent'] = (base['intent'] as String?) ?? 'business';
        base['view'] = (base['view'] as String?) ?? 'public';
        base.remove('date');
      } else {
        base['start'] = (base['start'] as String?) ?? startIso;
        base['end'] = (base['end'] as String?) ?? endIso;
      }
    }

    if (action.path == '/api/v1/charts/build') {
      base['tz'] = 'Europe/Istanbul';
      base['a'] = {
        'name': name,
        'data': {
          'birthDate': birthDate,
          'birthTime': birthTime,
          'birthPlace': birthPlace,
        },
      };
    }

    if (action.path.contains('/synastry/analyze')) {
      base['partner_a'] = {
        'birthDate': birthDate,
        'birthTime': birthTime,
        'birthPlace': birthPlace,
      };
    }

    return base;
  }

  String _normalizeBirthTime(String value) {
    final raw = value.trim();
    if (raw.isEmpty) {
      return '12:00';
    }
    final parts = raw.split(':');
    if (parts.length >= 2) {
      final hour = int.tryParse(parts[0]) ?? 12;
      final minute = int.tryParse(parts[1]) ?? 0;
      final hh = hour.clamp(0, 23).toString().padLeft(2, '0');
      final mm = minute.clamp(0, 59).toString().padLeft(2, '0');
      return '$hh:$mm';
    }
    return raw;
  }

  String _fmtDate(DateTime date) {
    final month = date.month.toString().padLeft(2, '0');
    final day = date.day.toString().padLeft(2, '0');
    return '${date.year}-$month-$day';
  }

  String _asDate(DateTime date) => _fmtDate(date);

  DateTime _monthStart(DateTime focusedMonth) {
    return DateTime(focusedMonth.year, focusedMonth.month, 1);
  }

  DateTime _monthEnd(DateTime focusedMonth) {
    return DateTime(focusedMonth.year, focusedMonth.month + 1, 0);
  }

  DateTime _clampSelectedDayToMonth(DateTime selected, DateTime focusedMonth) {
    final end = _monthEnd(focusedMonth);
    final day = selected.day.clamp(1, end.day);
    return DateTime(focusedMonth.year, focusedMonth.month, day);
  }

  String _dayKey(DateTime date) => _fmtDate(_stripDate(date));

  static DateTime _stripDate(DateTime date) {
    return DateTime(date.year, date.month, date.day);
  }

  static DateTime _firstDayOfMonth(DateTime date) {
    return DateTime(date.year, date.month, 1);
  }

  void _autofillFromProfile(Map<String, dynamic> profile) {
    final key =
        '${_selectedAction.id}|${profile['name']}|${profile['birth_date']}|${profile['birth_time']}|${profile['city']}|${profile['country']}';
    if (key == _lastAutofillKey) {
      return;
    }
    _lastAutofillKey = key;
    _applyAction(_selectedAction, profile: profile);
  }

  Map<String, dynamic> _parseJsonMap(String raw) {
    if (raw.trim().isEmpty) {
      return <String, dynamic>{};
    }
    final parsed = jsonDecode(raw);
    if (parsed is Map<String, dynamic>) {
      return parsed;
    }
    if (parsed is Map) {
      return Map<String, dynamic>.from(parsed);
    }
    throw const FormatException('JSON must be an object.');
  }

  Future<void> _runRequest() async {
    FocusScope.of(context).unfocus();
    setState(() {
      _loading = true;
      _error = null;
      _lastResponse = null;
      _lastText = null;
      _statusCode = null;
      if (_pathController.text.trim() == '/transits') {
        _eventsByDay = <String, List<Map<String, dynamic>>>{};
      }
      if (_isCalendarAction(_pathController.text.trim())) {
        _bestTimeItems = <Map<String, dynamic>>[];
        _bestTimesError = null;
        _bestTimesErrorBody = null;
        _periodSummaryText = null;
        _periodSummaryError = null;
        _periodSummaryLoading = true;
      }
    });

    try {
      final baseUrl = _baseUrlController.text.trim();
      final path = _pathController.text.trim();
      final url = '$baseUrl$path';
      final client = ApiClient(baseUrl: baseUrl);
      final isInterpret = url.contains('/interpret');
      final tag = isInterpret ? 'interpret' : 'chartlab';

      if (kDebugMode) {
        debugPrint('$tag request url=$url');
      }

      Response<dynamic> response;
      if (_selectedAction.method == 'GET') {
        final query = _parseJsonMap(_queryController.text);
        if (kDebugMode) {
          debugPrint('$tag payload=${jsonEncode(query)}');
        }
        if (_isCalendarAction(path)) {
          await _runCalendarAction(client, path: path, baseQuery: query);
          return;
        }
        response = await client.get(path, queryParameters: query);
      } else {
        final payload = _parseJsonMap(_requestController.text);
        if (kDebugMode) {
          debugPrint('$tag payload=${jsonEncode(payload)}');
        }
        response = await client.post(path, data: payload);
      }

      debugPrint('$tag response status=${response.statusCode}');
      debugPrint('$tag raw body=${response.data}');
      if (isInterpret) {
        debugPrint('interpret response status=${response.statusCode}');
        debugPrint('interpret raw body=${response.data}');
        debugPrint('interpret data type=${response.data.runtimeType}');
      }
      if (kDebugMode) {
        debugPrint('$tag response status=${response.statusCode}');
        debugPrint('$tag response dataType=${response.data.runtimeType}');
        debugPrint('$tag response data=${response.data}');
        _debugChunkedBody(tag, response.data);
      }

      final data = _asMap(response.data);
      final uiText = _extractDisplayText(path, data);
      final eventsByDay = _isCalendarAction(path)
          ? _extractEventsByDay(data)
          : <String, List<Map<String, dynamic>>>{};

      setState(() {
        _statusCode = response.statusCode;
        _lastResponse = data;
        _lastText = (uiText ?? '').trim();
        _eventsByDay = eventsByDay;
        _error = null;
        _loading = false;
      });
    } on DioException catch (exc) {
      final status = exc.response?.statusCode;
      final body = exc.response?.data;
      final baseUrl = _baseUrlController.text.trim();
      final path = _pathController.text.trim();
      final url = '$baseUrl$path';
      final isInterpret = url.contains('/interpret');
      final tag = isInterpret ? 'interpret' : 'chartlab';
      debugPrint('$tag response status=${status ?? 0}');
      debugPrint('$tag raw body=$body');
      if (kDebugMode) {
        debugPrint('$tag response status=${status ?? 0}');
        debugPrint('$tag response dataType=${body.runtimeType}');
        debugPrint('$tag response data=$body');
        _debugChunkedBody(tag, body);
      }
      final responseMap = _asMap(body);
      final friendly = _friendlyError(exc, status, responseMap);
      setState(() {
        _statusCode = status;
        _error = friendly;
        _lastResponse = responseMap;
        _lastText = null;
        _eventsByDay = <String, List<Map<String, dynamic>>>{};
        _bestTimeItems = <Map<String, dynamic>>[];
        _bestTimesError = null;
        _bestTimesErrorBody = null;
        _periodSummaryLoading = false;
        _loading = false;
      });
    } on FormatException catch (exc) {
      setState(() {
        _error = exc.toString();
        _lastResponse = null;
        _lastText = null;
        _eventsByDay = <String, List<Map<String, dynamic>>>{};
        _bestTimeItems = <Map<String, dynamic>>[];
        _bestTimesError = null;
        _bestTimesErrorBody = null;
        _periodSummaryLoading = false;
        _loading = false;
      });
    } catch (exc) {
      setState(() {
        _error = exc.toString();
        _lastResponse = null;
        _lastText = null;
        _eventsByDay = <String, List<Map<String, dynamic>>>{};
        _bestTimeItems = <Map<String, dynamic>>[];
        _bestTimesError = null;
        _bestTimesErrorBody = null;
        _periodSummaryLoading = false;
        _loading = false;
      });
    }
  }

  bool _isCalendarAction(String path) {
    return path.startsWith('/transit/calendar');
  }

  Future<void> _runCalendarAction(
    ApiClient client, {
    required String path,
    required Map<String, dynamic> baseQuery,
  }) async {
    final monthStart = _monthStart(_focusedMonth);
    final monthEnd = _monthEnd(_focusedMonth);
    final selectedDayKey = _dayKey(_selectedDay);

    final common = <String, dynamic>{
      'birth_date': (baseQuery['birth_date'] ?? '').toString(),
      'birth_time': _normalizeBirthTime(
        (baseQuery['birth_time'] ?? '').toString(),
      ),
      'birth_place': (baseQuery['birth_place'] ?? '').toString(),
      'tz': (baseQuery['tz'] ?? 'Europe/Istanbul').toString(),
      'transit_place':
          (baseQuery['transit_place'] ?? baseQuery['birth_place'] ?? '')
              .toString(),
      'view': (baseQuery['view'] ?? 'public').toString(),
    };

    Future<void> loadPeriodSummary() async {
      try {
        final periodResp = await client.post(
          '/transits',
          data: {
            'birth_date': common['birth_date'],
            'birth_time': common['birth_time'],
            'birth_place': common['birth_place'],
            'transit_date': selectedDayKey,
            'transit_place': common['transit_place'],
            'tz': common['tz'],
          },
        );
        final periodData = _asMap(periodResp.data);
        _periodSummaryText = _extractDisplayText('/transits', periodData);
        _periodSummaryError = null;
      } on DioException catch (exc) {
        _periodSummaryError = _friendlyError(
          exc,
          exc.response?.statusCode,
          _asMap(exc.response?.data),
        );
      } finally {
        _periodSummaryLoading = false;
      }
    }

    final isCalendarRangeAction = _selectedAction.id == 'transit.calendar';
    final isCalendarDayAction = _selectedAction.id == 'transit.calendar.day';

    if (isCalendarRangeAction) {
      final query = <String, dynamic>{
        ...common,
        'start': _fmtDate(monthStart),
        'end': _fmtDate(monthEnd),
      };
      final resp = await client.get(
        '/transit/calendar/day',
        queryParameters: query,
      );
      final map = _asMap(resp.data);
      final days = _extractEventsByDay(map);
      final bestQuery = <String, dynamic>{
        ...common,
        'intent': (baseQuery['intent'] ?? 'beauty_care_nourish').toString(),
        'start': query['start'],
        'end': query['end'],
        'top': (baseQuery['top'] ?? 5).toString(),
      };
      List<Map<String, dynamic>> best = <Map<String, dynamic>>[];
      String? bestErr;
      Map<String, dynamic>? bestErrBody;
      try {
        final bestResp = await client.get(
          '/transit/calendar/best-times',
          queryParameters: bestQuery,
        );
        best = _extractBestTimes(_asMap(bestResp.data));
      } on DioException catch (exc) {
        bestErrBody = _asMap(exc.response?.data);
        bestErr = _friendlyBestTimesError(
          exc.response?.statusCode,
          bestErrBody,
          exc,
        );
      }
      if (kDebugMode) {
        final firstDayKey = days.keys.isNotEmpty ? days.keys.first : '-';
        final firstDayCount = days.keys.isNotEmpty
            ? days[firstDayKey]!.length
            : 0;
        debugPrint(
          'calendar parse keys=${map.keys.toList()} dayCount=${days.length} sample=$firstDayKey:$firstDayCount',
        );
      }
      await loadPeriodSummary();
      setState(() {
        _statusCode = resp.statusCode;
        _lastResponse = map;
        _eventsByDay = days;
        _bestTimeItems = best;
        _bestTimesError = bestErr;
        _bestTimesErrorBody = bestErrBody;
        _error = null;
        _loading = false;
      });
      return;
    }

    if (isCalendarDayAction) {
      final query = <String, dynamic>{...common, 'date': selectedDayKey};
      final resp = await client.get(
        '/transit/calendar/day',
        queryParameters: query,
      );
      final map = _asMap(resp.data);
      final dayEvents = _extractDayEvents(map);
      if (kDebugMode) {
        debugPrint(
          'calendar/day parse keys=${map.keys.toList()} eventCount=${dayEvents.length}',
        );
      }
      await loadPeriodSummary();
      setState(() {
        _statusCode = resp.statusCode;
        _lastResponse = map;
        _eventsByDay[_dayKey(_selectedDay)] = dayEvents;
        _error = null;
        _loading = false;
      });
      return;
    }

    if (path == '/transit/calendar/best-times') {
      final query = <String, dynamic>{
        ...common,
        'intent': (baseQuery['intent'] ?? 'beauty_care_nourish').toString(),
        'start': _fmtDate(monthStart),
        'end': _fmtDate(monthEnd),
        'top': (baseQuery['top'] ?? 5).toString(),
      };
      int? statusCode;
      Map<String, dynamic>? map;
      List<Map<String, dynamic>> best = <Map<String, dynamic>>[];
      String? bestErr;
      Map<String, dynamic>? bestErrBody;
      try {
        final resp = await client.get(
          '/transit/calendar/best-times',
          queryParameters: query,
        );
        statusCode = resp.statusCode;
        map = _asMap(resp.data);
        best = _extractBestTimes(map);
        if (kDebugMode) {
          debugPrint(
            'best-times parse keys=${map.keys.toList()} itemCount=${best.length}',
          );
        }
      } on DioException catch (exc) {
        statusCode = exc.response?.statusCode;
        bestErrBody = _asMap(exc.response?.data);
        bestErr = _friendlyBestTimesError(statusCode, bestErrBody, exc);
        if (kDebugMode) {
          debugPrint(
            'best-times parse error status=$statusCode body=$bestErrBody',
          );
        }
      }
      await loadPeriodSummary();
      setState(() {
        _statusCode = statusCode;
        _lastResponse = map;
        _bestTimeItems = best;
        _bestTimesError = bestErr;
        _bestTimesErrorBody = bestErrBody;
        _error = null;
        _loading = false;
      });
      return;
    }

    throw StateError('Unsupported calendar path: $path');
  }

  List<Map<String, dynamic>> _extractDayEvents(Map<String, dynamic> dayData) {
    final dayUi = dayData['day_ui'];
    if (dayUi is Map) {
      final nestedEvents = dayUi['events'];
      if (nestedEvents is List) {
        return [
          for (final event in nestedEvents)
            if (event is Map) Map<String, dynamic>.from(event),
        ];
      }
    }
    final events = dayData['events'];
    if (events is! List) {
      return <Map<String, dynamic>>[];
    }
    return [
      for (final event in events)
        if (event is Map) Map<String, dynamic>.from(event),
    ];
  }

  List<Map<String, dynamic>> _extractBestTimes(Map<String, dynamic> data) {
    final fromBestTimes = data['best_times'];
    if (fromBestTimes is List) {
      return [
        for (final row in fromBestTimes)
          if (row is Map) Map<String, dynamic>.from(row),
      ];
    }
    final fromWindows = data['windows'];
    if (fromWindows is List) {
      return [
        for (final row in fromWindows)
          if (row is Map) Map<String, dynamic>.from(row),
      ];
    }
    final candidates = data['candidates'];
    if (candidates is List) {
      return [
        for (final row in candidates)
          if (row is Map) Map<String, dynamic>.from(row),
      ];
    }
    return <Map<String, dynamic>>[];
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
      } catch (_) {
        return <String, dynamic>{};
      }
    }
    return <String, dynamic>{};
  }

  String? _extractTransitsText(Map<String, dynamic> data, {int maxEvents = 6}) {
    dynamic events = data['events'];
    if (events == null && data['public'] is Map) {
      events = (data['public'] as Map)['events'];
    }
    if (events is! List || events.isEmpty) {
      return null;
    }

    final buf = StringBuffer();
    var count = 0;

    for (final event in events) {
      if (count >= maxEvents) {
        break;
      }
      if (event is! Map) {
        continue;
      }

      final blocks = event['blocks'];
      if (blocks is! List) {
        continue;
      }

      String? headline;
      String? summary;
      final guidance = <String>[];
      final watchOut = <String>[];
      String? timeHint;
      String? whereText;

      for (final block in blocks) {
        if (block is! Map) {
          continue;
        }
        final type = block['type']?.toString();
        final text = block['text']?.toString();
        final items = block['items'];

        if (type == 'headline' && (text?.trim().isNotEmpty ?? false)) {
          headline ??= text!.trim();
        }
        if (type == 'summary' && (text?.trim().isNotEmpty ?? false)) {
          summary ??= text!.trim();
        }
        if (type == 'where' && (text?.trim().isNotEmpty ?? false)) {
          whereText ??= text!.trim();
        }
        if (type == 'time_hint' && (text?.trim().isNotEmpty ?? false)) {
          timeHint ??= text!.trim();
        }

        if (type == 'guidance' && items is List) {
          guidance.clear();
          guidance.addAll(
            items
                .map((x) => x.toString())
                .where((x) => x.trim().isNotEmpty)
                .take(3),
          );
        }
        if (type == 'watch_out' && items is List) {
          watchOut.clear();
          watchOut.addAll(
            items
                .map((x) => x.toString())
                .where((x) => x.trim().isNotEmpty)
                .take(2),
          );
        }
      }

      final hasHeadline = headline != null && headline.isNotEmpty;
      final hasSummary = summary != null && summary.isNotEmpty;
      if (!hasHeadline && !hasSummary) {
        continue;
      }

      buf.writeln('* ${headline ?? "Etki"}');
      if (summary != null) {
        buf.writeln('  $summary');
      }
      if (whereText != null) {
        buf.writeln('  Yer: $whereText');
      }
      if (timeHint != null) {
        buf.writeln('  Zaman: $timeHint');
      }
      if (guidance.isNotEmpty) {
        buf.writeln('  Oneri:');
        for (final item in guidance) {
          buf.writeln('   - $item');
        }
      }
      if (watchOut.isNotEmpty) {
        buf.writeln('  Dikkat: ${watchOut.join(", ")}');
      }
      buf.writeln();
      count++;
    }

    final out = buf.toString().trim();
    return out.isEmpty ? null : out;
  }

  String? _extractDisplayText(String path, Map<String, dynamic> data) {
    String? pick(dynamic value) {
      final text = value?.toString();
      if (text == null) {
        return null;
      }
      final trimmed = text.trim();
      return trimmed.isEmpty ? null : trimmed;
    }

    String? uiText;
    if (path.startsWith('/interpret')) {
      final pub = data['public'];
      if (pub is Map && pub['core_story'] != null) {
        uiText = pub['core_story'].toString();
      } else if (data['core_story'] != null) {
        uiText = data['core_story'].toString();
      }
    }

    if (uiText == null && path == '/transits') {
      uiText = _extractTransitsText(data);
    }

    if (uiText != null && uiText.trim().isNotEmpty) {
      return uiText;
    }

    final public = data['public'];
    if (public is Map) {
      final p = public.cast<String, dynamic>();
      return pick(p['core_story']) ??
          pick(p['narrative_text']) ??
          pick(p['summary']) ??
          pick(p['text']);
    }

    return pick(data['core_story']) ??
        pick(data['narrative_text']) ??
        pick(data['summary']) ??
        pick(data['text']) ??
        pick(data['message']);
  }

  String _friendlyError(Object error, int? status, Map<String, dynamic>? body) {
    if (status == 403) {
      return 'Bu endpoint debug/internal erisim istiyor (403).';
    }
    if (status == 422) {
      final detail = body?['detail'];
      return 'Tarih araligi veya zorunlu alanlar hatali (422).'
          '${detail == null ? '' : '\nDetail: ${jsonEncode(detail)}'}';
    }
    if (status == 500) {
      final detail = body?['detail'];
      if (detail is Map && detail['message'] != null) {
        return 'Sunucu hatasi (500): ${detail['message']}';
      }
      if (detail is String && detail.trim().isNotEmpty) {
        return 'Sunucu hatasi (500): $detail';
      }
      return 'Sunucu hatasi (500). Lutfen tekrar deneyin.';
    }
    if (status != null) {
      return 'HTTP $status';
    }
    return error.toString();
  }

  String _friendlyBestTimesError(
    int? status,
    Map<String, dynamic>? body,
    Object error,
  ) {
    if (status == 422) {
      return 'Best Times icin tarih araligi hatali (422). Ay araligi tekrar hesaplandi, yeniden deneyin.';
    }
    if (status == 500) {
      final detail = body?['detail'];
      if (detail is Map && detail['message'] != null) {
        return 'Best Times su an olusturulamadi: ${detail['message']}';
      }
      return 'Best Times su an olusturulamadi (500).';
    }
    return _friendlyError(error, status, body);
  }

  Map<String, List<Map<String, dynamic>>> _extractEventsByDay(
    Map<String, dynamic> data,
  ) {
    final grouped = <String, List<Map<String, dynamic>>>{};

    dynamic days = data['days'];
    if (days == null && data['calendar'] is Map) {
      days = (data['calendar'] as Map)['days'];
    }
    if (days == null && data['calendar_public'] is Map) {
      days = (data['calendar_public'] as Map)['days'];
    }
    if (days == null && data['calendar_ui'] is Map) {
      days = (data['calendar_ui'] as Map)['days'];
    }
    if (days is List) {
      for (final entry in days) {
        if (entry is! Map) {
          continue;
        }
        final dayMap = Map<String, dynamic>.from(entry);
        final dateKey = _dateKeyFromAny(dayMap['date']);
        if (dateKey == null) {
          continue;
        }
        final rawEvents = dayMap['events'] ?? dayMap['top_events'];
        final events = <Map<String, dynamic>>[];
        if (rawEvents is List) {
          for (final event in rawEvents) {
            if (event is Map) {
              final m = Map<String, dynamic>.from(event);
              m.putIfAbsent('date', () => dateKey);
              events.add(m);
            }
          }
        }
        grouped[dateKey] = events;
      }
      return grouped;
    }

    final events = data['events'];
    if (events is List) {
      for (final event in events) {
        if (event is! Map) {
          continue;
        }
        final eventMap = Map<String, dynamic>.from(event);
        final dateKey = _dateKeyFromAny(eventMap['date']);
        if (dateKey == null) {
          continue;
        }
        grouped
            .putIfAbsent(dateKey, () => <Map<String, dynamic>>[])
            .add(eventMap);
      }
    }
    return grouped;
  }

  String? _dateKeyFromAny(dynamic raw) {
    final value = raw?.toString().trim();
    if (value == null || value.isEmpty) {
      return null;
    }
    if (value.length >= 10) {
      final maybe = value.substring(0, 10);
      final parsed = DateTime.tryParse(maybe);
      if (parsed != null) {
        return _asDate(_stripDate(parsed));
      }
    }
    final parsed = DateTime.tryParse(value);
    if (parsed != null) {
      return _asDate(_stripDate(parsed));
    }
    return null;
  }

  String _prettyJson(dynamic data) {
    try {
      return _encoder.convert(data);
    } catch (_) {
      return data?.toString() ?? '';
    }
  }

  void _debugChunkedBody(String tag, dynamic data) {
    final s = data?.toString() ?? '<null>';
    for (var i = 0; i < s.length; i += 800) {
      final end = (i + 800).clamp(0, s.length).toInt();
      debugPrint('$tag body chunk: ${s.substring(i, end)}');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (kDebugMode) {
      debugPrint(
        'CHART_LAB_BUILD loading=$_loading status=$_statusCode err=${_error != null} textLen=${_lastText?.length ?? 0}',
      );
    }
    final profileAsync = ref.watch(userProfileProvider);
    final profile = profileAsync.valueOrNull;
    if (profile != null) {
      _autofillFromProfile(profile);
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Chart Lab'),
        actions: [
          IconButton(
            tooltip: _showDevControls
                ? 'Dev kontrolleri gizle'
                : 'Dev kontrolleri goster',
            onPressed: () {
              setState(() => _showDevControls = !_showDevControls);
            },
            icon: Icon(_showDevControls ? Icons.code_off : Icons.code),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildFormSection(profile: profile),
              const SizedBox(height: 16),
              _buildResultCard(),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFormSection({required Map<String, dynamic>? profile}) {
    final isUiAction = _pathController.text.trim().startsWith('/interpret');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (profile == null) ...[
          Text(
            'Complete profile first.',
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
          const SizedBox(height: 12),
        ],
        DropdownButtonFormField<EndpointAction>(
          initialValue: _selectedAction,
          decoration: const InputDecoration(labelText: 'Action'),
          items: [
            for (final action in endpointCatalog)
              DropdownMenuItem(value: action, child: Text(action.label)),
          ],
          onChanged: (value) {
            if (value == null) {
              return;
            }
            setState(() => _selectedAction = value);
            _applyAction(value, profile: profile);
          },
        ),
        const SizedBox(height: 12),
        if (_showDevControls) ...[
          TextField(
            controller: _baseUrlController,
            decoration: const InputDecoration(labelText: 'Backend Base URL'),
          ),
          const SizedBox(height: 6),
          Text(
            ApiEnvironment.usesLoopbackHost
                ? 'Fiziksel iPhone icin API_BASE_URL degerini LAN IP, tunnel veya hosted URL olarak verin.'
                : 'Aktif API base URL: ${ApiEnvironment.apiBaseUrl}',
            style: const TextStyle(fontSize: 12, color: Colors.black54),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _pathController,
            decoration: const InputDecoration(labelText: 'Endpoint Path'),
          ),
          const SizedBox(height: 12),
          if (_selectedAction.method == 'POST') ...[
            SizedBox(
              height: 180,
              child: TextField(
                controller: _requestController,
                maxLines: null,
                expands: true,
                keyboardType: TextInputType.multiline,
                textAlignVertical: TextAlignVertical.top,
                decoration: const InputDecoration(
                  labelText: 'Request JSON',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
              ),
            ),
          ] else ...[
            SizedBox(
              height: 180,
              child: TextField(
                controller: _queryController,
                maxLines: null,
                expands: true,
                keyboardType: TextInputType.multiline,
                textAlignVertical: TextAlignVertical.top,
                decoration: const InputDecoration(
                  labelText: 'Query JSON',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
              ),
            ),
          ],
          const SizedBox(height: 12),
        ] else ...[
          Text(
            isUiAction
                ? 'Profil verileriyle yorum calistirilir.'
                : 'Profil verileriyle varsayilan payload calistirilir.',
            style: const TextStyle(fontSize: 12, color: Colors.black54),
          ),
          const SizedBox(height: 12),
        ],
        ElevatedButton(
          onPressed: _loading ? null : _runRequest,
          child: _loading
              ? const SizedBox(
                  height: 18,
                  width: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Run'),
        ),
      ],
    );
  }

  Widget _buildResultCard() {
    final isCalendarView = _isCalendarAction(_pathController.text.trim());
    final periodCore = _extractPeriodCore(_lastResponse);
    final eventCards = _extractEventCards(_lastResponse);
    final timeline = _extractTimeline(_lastResponse);
    final hasAnyResult =
        _statusCode != null ||
        _error != null ||
        (_lastText != null && _lastText!.trim().isNotEmpty) ||
        _lastResponse != null ||
        _eventsByDay.isNotEmpty ||
        eventCards.isNotEmpty ||
        isCalendarView;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                const Expanded(
                  child: Text(
                    'Response',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                  ),
                ),
                if (hasAnyResult)
                  IconButton(
                    onPressed: () {
                      setState(() => _resultExpanded = !_resultExpanded);
                    },
                    icon: Icon(
                      _resultExpanded ? Icons.expand_less : Icons.expand_more,
                    ),
                  ),
              ],
            ),
            if (!hasAnyResult) ...[
              const SizedBox(height: 8),
              const Text("Henuz sonuc yok. Run'a basinca burada gorunecek."),
            ] else if (_resultExpanded) ...[
              const SizedBox(height: 8),
              if (_loading) ...[
                const Center(child: CircularProgressIndicator()),
                const SizedBox(height: 12),
              ],
              if (kDebugMode) ...[
                Text('Status: ${_statusCode ?? "-"}'),
                const SizedBox(height: 8),
              ],
              if (_error != null)
                SelectableText(
                  _error!,
                  style: const TextStyle(color: Colors.red),
                ),
              if (_error == null && isCalendarView) ...[
                const SizedBox(height: 8),
                _buildPeriodSummaryBanner(),
                const SizedBox(height: 10),
                _buildBestTimesSection(),
                const SizedBox(height: 12),
                _buildTransitsCalendar(),
              ] else if (_error == null && eventCards.isNotEmpty) ...[
                if (periodCore != null) ...[
                  _buildPublicPeriodCoreCard(periodCore),
                  const SizedBox(height: 10),
                ],
                _buildPublicEventCards(eventCards, timeline: timeline),
                if (timeline != null) ...[
                  const SizedBox(height: 10),
                  _buildPublicTimelineCard(timeline),
                ],
              ] else if (_error == null &&
                  (periodCore != null || timeline != null)) ...[
                if (periodCore != null) ...[
                  _buildPublicPeriodCoreCard(periodCore),
                  const SizedBox(height: 10),
                ],
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.black12),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Text(
                    'Bu donem icin gosterilecek event card bulunmuyor.',
                  ),
                ),
                if (timeline != null) ...[
                  const SizedBox(height: 10),
                  _buildPublicTimelineCard(timeline),
                ],
              ] else if (_lastText != null && _lastText!.trim().isNotEmpty) ...[
                const SizedBox(height: 12),
                SelectableText(_lastText!),
              ],
              if (kDebugMode && _lastResponse != null) ...[
                const SizedBox(height: 12),
                ExpansionTile(
                  tilePadding: EdgeInsets.zero,
                  childrenPadding: EdgeInsets.zero,
                  title: const Text('Debug JSON'),
                  children: [SelectableText(_prettyJson(_lastResponse))],
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }

  Map<String, dynamic>? _extractPeriodCore(Map<String, dynamic>? data) {
    if (data == null) {
      return null;
    }
    final pub = data['public'];
    if (pub is Map && pub['period_core'] is Map) {
      return Map<String, dynamic>.from(pub['period_core'] as Map);
    }
    if (data['period_core'] is Map) {
      return Map<String, dynamic>.from(data['period_core'] as Map);
    }
    return null;
  }

  List<Map<String, dynamic>> _extractEventCards(Map<String, dynamic>? data) {
    if (data == null) {
      return const <Map<String, dynamic>>[];
    }
    final pub = data['public'];
    dynamic raw;
    if (pub is Map) {
      raw = pub['event_cards'];
    }
    raw ??= data['event_cards'];
    if (raw is! List) {
      return const <Map<String, dynamic>>[];
    }
    return [
      for (final item in raw)
        if (item is Map) Map<String, dynamic>.from(item),
    ];
  }

  Map<String, dynamic>? _extractTimeline(Map<String, dynamic>? data) {
    if (data == null) {
      return null;
    }
    final pub = data['public'];
    if (pub is Map && pub['timeline'] is Map) {
      return Map<String, dynamic>.from(pub['timeline'] as Map);
    }
    if (data['timeline'] is Map) {
      return Map<String, dynamic>.from(data['timeline'] as Map);
    }
    return null;
  }

  Widget _buildPublicPeriodCoreCard(Map<String, dynamic> periodCore) {
    final title = (periodCore['title'] ?? '').toString().trim();
    final coreStory = (periodCore['core_story'] ?? '').toString().trim();
    final upper = (periodCore['upper_meaning'] ?? '').toString().trim();
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.blue.withValues(alpha: 0.24)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title.isNotEmpty ? title : 'Period Core',
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
          if (coreStory.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(coreStory),
          ],
          if (upper.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(upper, style: const TextStyle(color: Colors.black54)),
          ],
        ],
      ),
    );
  }

  Widget _buildPublicEventCards(
    List<Map<String, dynamic>> cards, {
    Map<String, dynamic>? timeline,
  }) {
    final timelineSummary = (timeline?['summary'] ?? '').toString().trim();
    final timelineLines = timeline?['lines'] is List
        ? (timeline!['lines'] as List)
              .map((e) => e.toString().trim())
              .where((e) => e.isNotEmpty)
              .toList()
        : const <String>[];
    final items = cards.map(EventCardDto.fromMap).toList();
    if (items.isEmpty) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.black12),
          borderRadius: BorderRadius.circular(10),
        ),
        child: const Text('Aktif hikaye karti bulunmuyor.'),
      );
    }

    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: items.length,
      separatorBuilder: (_, _) => const SizedBox(height: 10),
      itemBuilder: (context, index) {
        final card = items[index];
        return EventCardTile(
          card: card,
          onTap: () {
            Navigator.of(context).push(
              MaterialPageRoute<void>(
                builder: (_) => EventStoryScreen(
                  card: card,
                  timelineSummary: timelineSummary,
                  timelineLines: timelineLines,
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildPublicTimelineCard(Map<String, dynamic> timeline) {
    final summary = (timeline['summary'] ?? '').toString().trim();
    final lines = timeline['lines'] is List
        ? (timeline['lines'] as List).map((e) => e.toString()).toList()
        : const <String>[];
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.03),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.black12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Timeline', style: TextStyle(fontWeight: FontWeight.w600)),
          if (summary.isNotEmpty) ...[const SizedBox(height: 6), Text(summary)],
          if (lines.isNotEmpty) ...[
            const SizedBox(height: 6),
            for (final line in lines.take(3)) Text('• $line'),
          ],
        ],
      ),
    );
  }

  Widget _buildPeriodSummaryBanner() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.blue.withValues(alpha: 0.24)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Period Summary',
            style: TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 6),
          if (_periodSummaryLoading)
            const Text('Yukleniyor...')
          else if (_periodSummaryError != null)
            Text(
              _periodSummaryError!,
              style: const TextStyle(color: Colors.red),
            )
          else if (_periodSummaryText != null && _periodSummaryText!.isNotEmpty)
            Text(_periodSummaryText!)
          else
            const Text('Ozet bulunamadi.'),
        ],
      ),
    );
  }

  Widget _buildBestTimesSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.green.withValues(alpha: 0.20)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Best Times',
            style: TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 6),
          if (_bestTimesError != null)
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _bestTimesError!,
                  style: const TextStyle(color: Colors.red),
                ),
                if (kDebugMode && _bestTimesErrorBody != null) ...[
                  const SizedBox(height: 8),
                  SelectableText(_prettyJson(_bestTimesErrorBody)),
                ],
              ],
            )
          else if (_bestTimeItems.isEmpty)
            const Text('Best times sonucu yok.')
          else
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (final item in _bestTimeItems.take(5))
                  Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: Text(_bestTimeLine(item)),
                  ),
              ],
            ),
        ],
      ),
    );
  }

  String _bestTimeLine(Map<String, dynamic> item) {
    final date = item['date']?.toString() ?? '-';
    final score = item['score']?.toString();
    final summary =
        item['summary']?.toString() ?? item['reason']?.toString() ?? '';
    if (score != null && score.isNotEmpty) {
      return '• $date (score: $score) ${summary.trim()}';
    }
    return '• $date ${summary.trim()}'.trim();
  }

  Widget _buildTransitsCalendar() {
    final month = _focusedMonth;
    final firstDay = _monthStart(month);
    final firstWeekday = firstDay.weekday;
    final gridStart = firstDay.subtract(Duration(days: firstWeekday - 1));
    final daysInMonth = _monthEnd(month).day;
    final totalCells = ((firstWeekday - 1 + daysInMonth + 6) ~/ 7) * 7;
    final monthTitle = '${month.year} ${_trMonthName(month.month)}';
    final selectedEvents =
        _eventsByDay[_dayKey(_selectedDay)] ?? <Map<String, dynamic>>[];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            IconButton(
              onPressed: _loading
                  ? null
                  : () async {
                      final targetMonth = DateTime(
                        month.year,
                        month.month - 1,
                        1,
                      );
                      final clamped = _clampSelectedDayToMonth(
                        _selectedDay,
                        targetMonth,
                      );
                      setState(() {
                        _focusedMonth = targetMonth;
                        _selectedDay = clamped;
                      });
                      await _runRequest();
                    },
              icon: const Icon(Icons.chevron_left),
            ),
            Expanded(
              child: Text(
                monthTitle,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            IconButton(
              onPressed: _loading
                  ? null
                  : () async {
                      final targetMonth = DateTime(
                        month.year,
                        month.month + 1,
                        1,
                      );
                      final clamped = _clampSelectedDayToMonth(
                        _selectedDay,
                        targetMonth,
                      );
                      setState(() {
                        _focusedMonth = targetMonth;
                        _selectedDay = clamped;
                      });
                      await _runRequest();
                    },
              icon: const Icon(Icons.chevron_right),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Row(
          children: const [
            _WeekdayCell('Pzt'),
            _WeekdayCell('Sal'),
            _WeekdayCell('Car'),
            _WeekdayCell('Per'),
            _WeekdayCell('Cum'),
            _WeekdayCell('Cmt'),
            _WeekdayCell('Paz'),
          ],
        ),
        const SizedBox(height: 4),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: totalCells,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 7,
            mainAxisSpacing: 6,
            crossAxisSpacing: 6,
            childAspectRatio: 1.15,
          ),
          itemBuilder: (context, index) {
            final day = gridStart.add(Duration(days: index));
            final isCurrentMonth = day.month == month.month;
            final isSelected = _dayKey(day) == _dayKey(_selectedDay);
            final events =
                _eventsByDay[_dayKey(day)] ?? <Map<String, dynamic>>[];

            return GestureDetector(
              onTap: () {
                setState(() {
                  _selectedDay = _stripDate(day);
                  if (!isCurrentMonth) {
                    _focusedMonth = DateTime(day.year, day.month, 1);
                  }
                });
              },
              child: Container(
                decoration: BoxDecoration(
                  color: isSelected
                      ? Theme.of(
                          context,
                        ).colorScheme.primary.withValues(alpha: 0.16)
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: isSelected
                        ? Theme.of(context).colorScheme.primary
                        : Colors.black12,
                  ),
                ),
                child: Center(
                  child: SizedBox(
                    height: 44,
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          '${day.day}',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: isCurrentMonth
                                ? Colors.black87
                                : Colors.black38,
                          ),
                        ),
                        const SizedBox(height: 4),
                        _EventDots(count: events.length),
                      ],
                    ),
                  ),
                ),
              ),
            );
          },
        ),
        const SizedBox(height: 14),
        Builder(
          builder: (context) {
            final dayCount = selectedEvents.length;
            return Text(
              '${_dayKey(_selectedDay)} • $dayCount event',
              style: const TextStyle(fontWeight: FontWeight.w600),
            );
          },
        ),
        const SizedBox(height: 8),
        if (selectedEvents.isEmpty)
          const Text(
            'Bu gun icin event yok.',
            style: TextStyle(color: Colors.black54),
          )
        else
          Column(
            children: [
              for (final event in selectedEvents) ...[
                _buildEventCard(event),
                const SizedBox(height: 8),
              ],
            ],
          ),
      ],
    );
  }

  Widget _buildEventCard(Map<String, dynamic> event) {
    final display = _extractEventDisplay(event);
    final tier = event['tier']?.toString().trim();
    final severity = event['severity_tag']?.toString().trim();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.black12),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  display.headline,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              if (tier != null && tier.isNotEmpty)
                _pill(label: tier, bg: Colors.blue.withValues(alpha: 0.12)),
              if (severity != null && severity.isNotEmpty) ...[
                const SizedBox(width: 6),
                _pill(
                  label: severity,
                  bg: Colors.orange.withValues(alpha: 0.14),
                ),
              ],
            ],
          ),
          if (display.signature != null) ...[
            const SizedBox(height: 6),
            Text(
              display.signature!,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                height: 1.2,
                color: Theme.of(
                  context,
                ).textTheme.bodySmall?.color?.withValues(alpha: 0.7),
              ),
            ),
          ],
          if (display.summary != null) ...[
            const SizedBox(height: 6),
            Text(display.summary!),
          ],
          if (display.whereText != null) ...[
            const SizedBox(height: 6),
            Text(
              'Yer: ${display.whereText!}',
              style: const TextStyle(fontSize: 12),
            ),
          ],
          if (display.timeHint != null) ...[
            const SizedBox(height: 4),
            Text(
              'Zaman: ${display.timeHint!}',
              style: const TextStyle(fontSize: 12),
            ),
          ],
          const SizedBox(height: 8),
          TextButton(
            onPressed: () => _showEventDetails(event),
            child: const Text('Detaya in'),
          ),
        ],
      ),
    );
  }

  Widget _pill({required String label, required Color bg}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(label, style: const TextStyle(fontSize: 11)),
    );
  }

  _EventDisplay _extractEventDisplay(Map<String, dynamic> event) {
    String? headline;
    String? signature;
    String? summary;
    String? whereText;
    String? timeHint;

    final blocks = event['blocks'];
    if (blocks is List) {
      for (final block in blocks) {
        if (block is! Map) {
          continue;
        }
        final type = block['type']?.toString();
        final text = block['text']?.toString();
        if (text == null || text.trim().isEmpty) {
          continue;
        }
        final trimmed = text.trim();
        if (type == 'headline') {
          headline ??= trimmed;
        } else if (type == 'signature') {
          signature ??= trimmed;
        } else if (type == 'summary') {
          summary ??= trimmed;
        } else if (type == 'where') {
          whereText ??= trimmed;
        } else if (type == 'time_hint') {
          timeHint ??= trimmed;
        }
      }
    }

    headline ??= event['label']?.toString();
    summary ??= event['description']?.toString();

    return _EventDisplay(
      headline: headline ?? 'Transit Etkisi',
      signature: signature,
      summary: summary,
      whereText: whereText,
      timeHint: timeHint,
    );
  }

  void _showEventDetails(Map<String, dynamic> event) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        final blocks = event['blocks'];
        final body = <String>[];
        if (blocks is List) {
          for (final block in blocks) {
            if (block is! Map) {
              continue;
            }
            final type = block['type']?.toString() ?? 'block';
            final text = block['text']?.toString();
            final items = block['items'];
            if (text != null && text.trim().isNotEmpty) {
              body.add('$type: ${text.trim()}');
            } else if (items is Map && items.isNotEmpty) {
              body.add('$type:\n${_prettyJson(items)}');
            } else if (items is List && items.isNotEmpty) {
              body.add('$type:\n${_prettyJson(items)}');
            }
          }
        }
        final fallback = body.isEmpty ? _prettyJson(event) : body.join('\n\n');
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: SingleChildScrollView(child: SelectableText(fallback)),
          ),
        );
      },
    );
  }

  String _trMonthName(int month) {
    const names = <String>[
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
    return names[month - 1];
  }
}

class _WeekdayCell extends StatelessWidget {
  const _WeekdayCell(this.label);

  final String label;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Center(
        child: Text(
          label,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
        ),
      ),
    );
  }
}

class _EventDots extends StatelessWidget {
  const _EventDots({required this.count});

  final int count;

  @override
  Widget build(BuildContext context) {
    final dotCount = count > 3 ? 3 : count;
    if (dotCount <= 0) {
      return const SizedBox(height: 10);
    }
    return SizedBox(
      height: 10,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          for (var i = 0; i < dotCount; i++) ...[
            Container(
              width: 5,
              height: 5,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary,
                shape: BoxShape.circle,
              ),
            ),
            if (i < dotCount - 1) const SizedBox(width: 3),
          ],
        ],
      ),
    );
  }
}

class _EventDisplay {
  const _EventDisplay({
    required this.headline,
    required this.signature,
    required this.summary,
    required this.whereText,
    required this.timeHint,
  });

  final String headline;
  final String? signature;
  final String? summary;
  final String? whereText;
  final String? timeHint;
}
