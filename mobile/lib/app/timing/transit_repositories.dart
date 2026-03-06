import 'dart:convert';

import 'package:mobile/app/api/api_client.dart';

// Screen -> endpoint -> keys
// CalendarHub/Daily -> POST /transit/narrative -> public.event_cards, public.best_times
// CalendarHub/Period -> POST /transit/narrative -> public.period_core + public.event_cards[horizon=period]
// CalendarHub/Period -> GET /transit/calendar -> markers/themes/intent_summary (marker support only)
// Home/Donem Kartlari -> POST /transit/narrative -> public.event_cards[horizon=period]
// Profile/Donem -> same PeriodCalendarTab source split as CalendarHub/Period

class TransitRequestBuilder {
  const TransitRequestBuilder._();

  static bool hasProfile(Map<String, dynamic>? profile) {
    if (profile == null) {
      return false;
    }
    final birthDate = (profile['birth_date'] ?? '').toString().trim();
    final birthTime = (profile['birth_time'] ?? '').toString().trim();
    final place = resolvePlace(profile);
    return birthDate.isNotEmpty && birthTime.isNotEmpty && place.isNotEmpty;
  }

  static String resolvePlace(Map<String, dynamic> profile) {
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

  static String normalizeBirthTime(String raw) {
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

  static String fmtDate(DateTime date) {
    final month = date.month.toString().padLeft(2, '0');
    final day = date.day.toString().padLeft(2, '0');
    return '${date.year}-$month-$day';
  }

  static DateTime stripDate(DateTime value) =>
      DateTime(value.year, value.month, value.day);

  static Map<String, dynamic> asMap(dynamic data) {
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

  static Map<String, dynamic> buildNarrativePayload({
    required Map<String, dynamic> profile,
    required DateTime selectedDate,
  }) {
    final now = DateTime.now();
    final start = fmtDate(DateTime(now.year, now.month, 1));
    final end = fmtDate(DateTime(now.year, now.month + 1, 0));
    final place = resolvePlace(profile);

    return <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'transit_place': place,
      'start': start,
      'end': end,
      'selected_date': fmtDate(selectedDate),
      'tz': (profile['timezone'] ?? 'Europe/Istanbul').toString().trim(),
      'intent': 'general',
      'include_best_times': true,
      'lens': 'general',
    };
  }

  static Map<String, dynamic> buildCalendarQuery({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
    String include = 'markers,themes,intent_summary',
  }) {
    final start = fmtDate(DateTime(focusedDate.year, focusedDate.month, 1));
    final end = fmtDate(DateTime(focusedDate.year, focusedDate.month + 1, 0));
    final place = resolvePlace(profile);

    return <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'transit_place': place,
      'start': start,
      'end': end,
      'tz': (profile['timezone'] ?? 'Europe/Istanbul').toString().trim(),
      'view': 'public',
      'include': include,
    };
  }

  static Map<String, dynamic> buildBestTimesQuery({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
  }) {
    final start = fmtDate(DateTime(focusedDate.year, focusedDate.month, 1));
    final end = fmtDate(DateTime(focusedDate.year, focusedDate.month + 1, 0));
    final place = resolvePlace(profile);
    return <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'transit_place': place,
      'start': start,
      'end': end,
      'tz': (profile['timezone'] ?? 'Europe/Istanbul').toString().trim(),
      'intent': 'general',
      'top': '5',
    };
  }
}

class NarrativeRepository {
  NarrativeRepository({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: 'http://127.0.0.1:5000');

  final ApiClient _client;

  Future<Map<String, dynamic>> fetchDailyNarrative({
    required Map<String, dynamic> profile,
    required DateTime selectedDate,
  }) async {
    final response = await _client.post(
      '/transit/narrative',
      data: TransitRequestBuilder.buildNarrativePayload(
        profile: profile,
        selectedDate: selectedDate,
      ),
    );
    return TransitRequestBuilder.asMap(response.data);
  }
}

class CalendarRepository {
  CalendarRepository({ApiClient? client})
    : _client = client ?? ApiClient(baseUrl: 'http://127.0.0.1:5000');

  final ApiClient _client;

  Future<Map<String, dynamic>> fetchCalendar({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
    String include = 'markers,themes,intent_summary',
  }) async {
    final response = await _client.get(
      '/transit/calendar',
      queryParameters: TransitRequestBuilder.buildCalendarQuery(
        profile: profile,
        focusedDate: focusedDate,
        include: include,
      ),
    );
    return TransitRequestBuilder.asMap(response.data);
  }

  Future<Map<String, dynamic>> fetchBestTimes({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
  }) async {
    final response = await _client.get(
      '/transit/calendar/best-times',
      queryParameters: TransitRequestBuilder.buildBestTimesQuery(
        profile: profile,
        focusedDate: focusedDate,
      ),
    );
    return TransitRequestBuilder.asMap(response.data);
  }
}
