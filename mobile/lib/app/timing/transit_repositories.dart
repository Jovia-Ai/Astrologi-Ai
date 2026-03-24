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
    final month = stripDate(selectedDate);
    final start = fmtDate(DateTime(month.year, month.month, 1));
    final end = fmtDate(DateTime(month.year, month.month + 1, 0));
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

  static Map<String, dynamic> buildTransitPayload({
    required Map<String, dynamic> profile,
    required DateTime transitDate,
  }) {
    final place = resolvePlace(profile);
    return <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'transit_date': fmtDate(stripDate(transitDate)),
      'transit_time': '12:00',
      'transit_place': place,
      'context_mode': 'context-lite',
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
  NarrativeRepository({ApiClient? client}) : _client = client ?? ApiClient();

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

  Future<Map<String, dynamic>> fetchTransitSummary({
    required Map<String, dynamic> profile,
    required DateTime transitDate,
  }) async {
    final response = await _client.post(
      '/transits',
      data: TransitRequestBuilder.buildTransitPayload(
        profile: profile,
        transitDate: transitDate,
      ),
    );
    return TransitRequestBuilder.asMap(response.data);
  }
}

class SkyFeedItemDto {
  const SkyFeedItemDto({
    required this.id,
    required this.title,
    required this.summary,
    required this.badge,
    required this.relativeTiming,
    required this.tags,
  });

  final String id;
  final String title;
  final String summary;
  final String badge;
  final String relativeTiming;
  final List<String> tags;

  factory SkyFeedItemDto.fromMap(Map<String, dynamic> map) {
    final tagsRaw = map['tags'];
    return SkyFeedItemDto(
      id: (map['id'] ?? '').toString(),
      title: ((map['short_title_tr'] ?? map['title_tr']) ?? '').toString(),
      summary: (map['summary_tr'] ?? '').toString(),
      badge: (map['badge_tr'] ?? '').toString(),
      relativeTiming: (map['relative_timing_tr'] ?? '').toString(),
      tags: tagsRaw is List
          ? [for (final tag in tagsRaw) tag.toString()]
          : const <String>[],
    );
  }
}

class SkyNowDto {
  const SkyNowDto({
    required this.summary,
    required this.chips,
    required this.items,
  });

  final String summary;
  final List<String> chips;
  final List<SkyFeedItemDto> items;

  factory SkyNowDto.fromMap(Map<String, dynamic> map) {
    final itemsRaw = map['items'];
    final items = itemsRaw is List
        ? [
            for (final item in itemsRaw)
              if (item is Map)
                SkyFeedItemDto.fromMap(Map<String, dynamic>.from(item)),
          ]
        : const <SkyFeedItemDto>[];
    final chips = <String>[];
    for (final item in items) {
      for (final tag in item.tags) {
        if (!chips.contains(tag)) {
          chips.add(tag);
        }
        if (chips.length >= 3) {
          break;
        }
      }
      if (chips.length >= 3) {
        break;
      }
    }
    return SkyNowDto(
      summary: (map['summary_tr'] ?? '').toString(),
      chips: chips,
      items: items,
    );
  }
}

class SkyRepository {
  SkyRepository({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;

  Future<Map<String, dynamic>> fetchNow({
    required String tz,
    int limit = 4,
  }) async {
    final response = await _client.get(
      '/sky/now',
      queryParameters: <String, dynamic>{'tz': tz, 'limit': '$limit'},
    );
    return TransitRequestBuilder.asMap(response.data);
  }
}

class CalendarRepository {
  CalendarRepository({ApiClient? client}) : _client = client ?? ApiClient();

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
