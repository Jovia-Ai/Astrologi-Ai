import 'dart:convert';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/l10n/current_localizations.dart';

// Screen -> endpoint -> keys
// CalendarHub/Daily -> POST /transit/narrative -> public.event_cards, public.best_times
// CalendarHub/Period -> POST /transit/narrative -> public.period_core + public.event_cards[horizon=period]
// CalendarHub/Period -> GET /transit/calendar -> markers/themes/intent_summary (marker support only)
// Home/Donem Kartlari -> POST /transit/narrative -> public.event_cards[horizon=period]
// Profile/Donem -> same PeriodCalendarTab source split as CalendarHub/Period

enum TransitPayloadProfile {
  full,
  home,
  calendarDay,
  calendarPeriod,
  relationshipPreview,
}

enum SubscriptionTier { free, premium }

extension on TransitPayloadProfile {
  String get wireValue => switch (this) {
    TransitPayloadProfile.full => 'full',
    TransitPayloadProfile.home => 'home',
    TransitPayloadProfile.calendarDay => 'calendar_day',
    TransitPayloadProfile.calendarPeriod => 'calendar_period',
    TransitPayloadProfile.relationshipPreview => 'relationship_preview',
  };
}

extension on SubscriptionTier {
  String get wireValue => this == SubscriptionTier.premium ? 'premium' : 'free';
}

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

  static double? _readCoordinate(
    Map<String, dynamic> profile,
    List<String> keys,
  ) {
    for (final key in keys) {
      final value = profile[key];
      if (value is num) {
        return value.toDouble();
      }
      final text = value?.toString().trim() ?? '';
      if (text.isEmpty) {
        continue;
      }
      final parsed = double.tryParse(text.replaceAll(',', '.'));
      if (parsed != null) {
        return parsed;
      }
    }
    return null;
  }

  static double? resolveLatitude(Map<String, dynamic> profile) {
    return _readCoordinate(profile, const ['latitude', 'lat']);
  }

  static double? resolveLongitude(Map<String, dynamic> profile) {
    return _readCoordinate(profile, const ['longitude', 'lng', 'lon']);
  }

  static String resolveTimezone(
    Map<String, dynamic> profile, {
    String fallback = 'Europe/Istanbul',
  }) {
    final raw = (profile['timezone'] ?? '').toString().trim();
    return raw.isNotEmpty ? raw : fallback;
  }

  static void appendKnownLocationFields(
    Map<String, dynamic> payload, {
    required Map<String, dynamic> profile,
    bool includeTransit = false,
  }) {
    final latitude = resolveLatitude(profile);
    final longitude = resolveLongitude(profile);
    final timezone = (profile['timezone'] ?? '').toString().trim();
    if (latitude != null) {
      payload['birth_latitude'] = latitude;
      if (includeTransit) {
        payload['transit_latitude'] = latitude;
      }
    }
    if (longitude != null) {
      payload['birth_longitude'] = longitude;
      if (includeTransit) {
        payload['transit_longitude'] = longitude;
      }
    }
    if (timezone.isNotEmpty) {
      payload['birth_timezone'] = timezone;
      if (includeTransit) {
        payload['transit_timezone'] = timezone;
      }
    }
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
    String lens = 'general',
    bool focusedRange = false,
    bool includeBestTimes = true,
    String responseMode = 'full',
    TransitPayloadProfile payloadProfile = TransitPayloadProfile.full,
    SubscriptionTier subscriptionTier = SubscriptionTier.free,
    int? visibleDaysLimit,
    String locale = 'tr',
  }) {
    final month = stripDate(selectedDate);
    final selected = fmtDate(selectedDate);
    final start = focusedRange
        ? selected
        : fmtDate(DateTime(month.year, month.month, 1));
    final end = focusedRange
        ? selected
        : fmtDate(DateTime(month.year, month.month + 1, 0));
    final place = resolvePlace(profile);

    final payload = <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'transit_place': place,
      'start': start,
      'end': end,
      'selected_date': selected,
      'tz': resolveTimezone(profile),
      'intent': 'general',
      'include_best_times': includeBestTimes,
      'lens': lens.trim().isNotEmpty ? lens.trim() : 'general',
      'response_mode': responseMode.trim().isNotEmpty
          ? responseMode.trim()
          : 'full',
      'payload_profile': payloadProfile.wireValue,
      'subscription_tier': subscriptionTier.wireValue,
      if (visibleDaysLimit != null && visibleDaysLimit > 0)
        'visible_days_limit': visibleDaysLimit,
      'locale': locale,
    };
    appendKnownLocationFields(payload, profile: profile, includeTransit: true);
    return payload;
  }

  static Map<String, dynamic> buildTransitPayload({
    required Map<String, dynamic> profile,
    required DateTime transitDate,
    String locale = 'tr',
  }) {
    final place = resolvePlace(profile);
    final payload = <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'transit_date': fmtDate(stripDate(transitDate)),
      'transit_time': '12:00',
      'transit_place': place,
      'context_mode': 'context-lite',
      'locale': locale,
    };
    appendKnownLocationFields(payload, profile: profile, includeTransit: true);
    return payload;
  }

  static Map<String, dynamic> buildCalendarQuery({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
    String include = 'markers,themes,intent_summary',
    SubscriptionTier subscriptionTier = SubscriptionTier.free,
    int? visibleDaysLimit,
    String locale = 'tr',
  }) {
    final start = fmtDate(DateTime(focusedDate.year, focusedDate.month, 1));
    final end = fmtDate(DateTime(focusedDate.year, focusedDate.month + 1, 0));
    final place = resolvePlace(profile);

    final payload = <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'transit_place': place,
      'start': start,
      'end': end,
      'anchor_date': fmtDate(stripDate(focusedDate)),
      'tz': resolveTimezone(profile),
      'view': 'public',
      'include': include,
      'subscription_tier': subscriptionTier.wireValue,
      if (visibleDaysLimit != null && visibleDaysLimit > 0)
        'visible_days_limit': '$visibleDaysLimit',
      'locale': locale,
    };
    appendKnownLocationFields(payload, profile: profile, includeTransit: true);
    return payload;
  }

  static Map<String, dynamic> buildBestTimesQuery({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
    String locale = 'tr',
  }) {
    final start = fmtDate(DateTime(focusedDate.year, focusedDate.month, 1));
    final end = fmtDate(DateTime(focusedDate.year, focusedDate.month + 1, 0));
    final place = resolvePlace(profile);
    final payload = <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'transit_place': place,
      'start': start,
      'end': end,
      'tz': resolveTimezone(profile),
      'intent': 'general',
      'top': '5',
      'locale': locale,
    };
    appendKnownLocationFields(payload, profile: profile, includeTransit: true);
    return payload;
  }

  static SubscriptionTier resolveSubscriptionTier(
    Map<String, dynamic>? profile,
  ) {
    if (profile == null) {
      return SubscriptionTier.free;
    }
    final directTier = (profile['subscription_tier'] ?? profile['tier'] ?? '')
        .toString()
        .trim()
        .toLowerCase();
    if (directTier == 'premium') {
      return SubscriptionTier.premium;
    }
    final premiumFlags = <Object?>[
      profile['is_premium'],
      profile['premium'],
      profile['has_premium'],
    ];
    for (final value in premiumFlags) {
      if (value == true) {
        return SubscriptionTier.premium;
      }
      if (value is String && value.trim().toLowerCase() == 'true') {
        return SubscriptionTier.premium;
      }
    }
    return SubscriptionTier.free;
  }
}

class NarrativeRepository {
  NarrativeRepository({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;
  static const Duration _narrativeCacheTtl = Duration(minutes: 3);
  static const Duration _transitSummaryCacheTtl = Duration(minutes: 2);

  Future<Map<String, dynamic>> fetchDailyNarrative({
    required Map<String, dynamic> profile,
    required DateTime selectedDate,
    String lens = 'general',
    bool focusedRange = false,
    bool includeBestTimes = true,
    String responseMode = 'full',
    TransitPayloadProfile payloadProfile = TransitPayloadProfile.full,
    SubscriptionTier? subscriptionTier,
    int? visibleDaysLimit,
    Duration? receiveTimeout,
    ApiRequestSla requestSla = ApiRequestSla.interactive,
    String locale = 'tr',
  }) async {
    final resolvedTier =
        subscriptionTier ??
        TransitRequestBuilder.resolveSubscriptionTier(profile);
    final response = await _client.post(
      '/transit/narrative',
      data: TransitRequestBuilder.buildNarrativePayload(
        profile: profile,
        selectedDate: selectedDate,
        lens: lens,
        focusedRange: focusedRange,
        includeBestTimes: includeBestTimes,
        responseMode: responseMode,
        payloadProfile: payloadProfile,
        subscriptionTier: resolvedTier,
        visibleDaysLimit: visibleDaysLimit,
        locale: locale,
      ),
      receiveTimeout: receiveTimeout,
      requestSla: requestSla,
      cacheTtl: _narrativeCacheTtl,
    );
    return TransitRequestBuilder.asMap(response.data);
  }

  Future<Map<String, dynamic>> fetchTransitSummary({
    required Map<String, dynamic> profile,
    required DateTime transitDate,
    String locale = 'tr',
  }) async {
    final response = await _client.post(
      '/transits',
      data: TransitRequestBuilder.buildTransitPayload(
        profile: profile,
        transitDate: transitDate,
        locale: locale,
      ),
      cacheTtl: _transitSummaryCacheTtl,
    );
    return TransitRequestBuilder.asMap(response.data);
  }
}

class SkyFeedItemDto {
  const SkyFeedItemDto({
    required this.id,
    required this.slug,
    required this.eventType,
    required this.title,
    required this.shortTitle,
    required this.summary,
    required this.badge,
    required this.relativeTiming,
    required this.phase,
    required this.status,
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
  final String phase;
  final String status;
  final String startsAt;
  final String exactAt;
  final String endsAt;
  final List<String> tags;
  final List<String> bodies;
  final String aspect;
  final String sign;
  final Map<String, dynamic> personalizationCta;

  factory SkyFeedItemDto.fromMap(Map<String, dynamic> map) {
    final tagsRaw = map['tags'];
    final bodiesRaw = map['bodies'];
    return SkyFeedItemDto(
      id: _skyRawString(map, 'id'),
      slug: _skyRawString(map, 'slug'),
      eventType: _skyRawString(map, 'event_type'),
      title: _skyString(map, 'short_title_tr', 'title_tr'),
      shortTitle: _skyString(map, 'short_title_tr'),
      summary: _skyString(map, 'summary_tr'),
      badge: _skyString(map, 'badge_tr'),
      relativeTiming: _skyString(map, 'relative_timing_tr'),
      phase: _skyRawString(map, 'phase'),
      status: _skyRawString(map, 'status'),
      startsAt: _skyRawString(map, 'starts_at'),
      exactAt: _skyRawString(map, 'exact_at'),
      endsAt: _skyRawString(map, 'ends_at'),
      tags: tagsRaw is List
          ? normalizeTurkishTextList(tagsRaw)
          : const <String>[],
      bodies: bodiesRaw is List
          ? normalizeTurkishTextList(bodiesRaw)
          : const <String>[],
      aspect: _skyRawString(map, 'aspect'),
      sign: _skyString(map, 'sign'),
      personalizationCta: map['personalization_cta'] is Map
          ? Map<String, dynamic>.from(map['personalization_cta'] as Map)
          : const <String, dynamic>{},
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
      summary: _skyString(map, 'summary_tr'),
      chips: chips,
      items: items,
    );
  }
}

class SkyPersonalTouchpointDto {
  const SkyPersonalTouchpointDto({
    required this.point,
    required this.pointType,
    required this.aspect,
    required this.orbDeg,
    required this.house,
    required this.noteTr,
  });

  final String point;
  final String pointType;
  final String aspect;
  final double? orbDeg;
  final int? house;
  final String noteTr;

  factory SkyPersonalTouchpointDto.fromMap(Map<String, dynamic> map) {
    return SkyPersonalTouchpointDto(
      point: _skyString(map, 'point'),
      pointType: _skyString(map, 'point_type', 'pointType'),
      aspect: _skyString(map, 'aspect'),
      orbDeg: _skyDouble(map, 'orb_deg', 'orbDeg'),
      house: _skyInt(map, 'house'),
      noteTr: _skyString(map, 'note_tr', 'noteTr'),
    );
  }
}

class SkyEventPersonalizationDto {
  const SkyEventPersonalizationDto({
    required this.eventId,
    required this.eventSlug,
    required this.impactScore,
    required this.relevanceLevel,
    required this.summaryTr,
    required this.activatedAreasTr,
    required this.matchedNatalPoints,
    required this.strongestWindowStart,
    required this.strongestWindowEnd,
    required this.whyThisHitsYouTr,
    required this.howItMayShowUpTr,
    required this.bestUseTr,
    required this.watchOutTr,
    required this.microActionTr,
  });

  final String eventId;
  final String eventSlug;
  final double impactScore;
  final String relevanceLevel;
  final String summaryTr;
  final List<String> activatedAreasTr;
  final List<SkyPersonalTouchpointDto> matchedNatalPoints;
  final String strongestWindowStart;
  final String strongestWindowEnd;
  final String whyThisHitsYouTr;
  final String howItMayShowUpTr;
  final String bestUseTr;
  final String watchOutTr;
  final String microActionTr;

  factory SkyEventPersonalizationDto.fromMap(Map<String, dynamic> map) {
    final touchpointsRaw = map['matched_natal_points'];
    final astroMap = map['astro_event_v2'] is Map
        ? Map<String, dynamic>.from(map['astro_event_v2'] as Map)
        : const <String, dynamic>{};
    return SkyEventPersonalizationDto(
      eventId: _skyString(map, 'event_id', 'eventId'),
      eventSlug: _skyString(map, 'event_slug', 'eventSlug'),
      impactScore: _skyDouble(map, 'impact_score', 'impactScore') ?? 0,
      relevanceLevel: _skyString(map, 'relevance_level', 'relevanceLevel'),
      summaryTr: _skyString(map, 'summary_tr', 'summaryTr'),
      activatedAreasTr: _skyStringList(
        map,
        'activated_areas_tr',
        'activatedAreasTr',
      ),
      matchedNatalPoints: touchpointsRaw is List
          ? [
              for (final item in touchpointsRaw)
                if (item is Map)
                  SkyPersonalTouchpointDto.fromMap(
                    Map<String, dynamic>.from(item),
                  ),
            ]
          : const <SkyPersonalTouchpointDto>[],
      strongestWindowStart: _skyString(
        map,
        'strongest_window_start',
        'strongestWindowStart',
      ),
      strongestWindowEnd: _skyString(
        map,
        'strongest_window_end',
        'strongestWindowEnd',
      ),
      whyThisHitsYouTr: _skyFirstString([
        _skyString(map, 'why_this_hits_you_tr'),
        _skyString(astroMap, 'why_this_hits_you_tr'),
      ]),
      howItMayShowUpTr: _skyFirstString([
        _skyString(map, 'how_it_may_show_up_tr'),
        _skyString(astroMap, 'how_it_may_show_up_tr'),
      ]),
      bestUseTr: _skyFirstString([
        _skyString(map, 'best_use_tr'),
        _skyString(astroMap, 'best_use_tr'),
      ]),
      watchOutTr: _skyFirstString([
        _skyString(map, 'watch_out_tr'),
        _skyString(astroMap, 'watch_out_tr'),
      ]),
      microActionTr: _skyFirstString([
        _skyString(map, 'micro_action_tr'),
        _skyString(astroMap, 'micro_action_tr'),
      ]),
    );
  }
}

class SkyEventDetailDto {
  const SkyEventDetailDto({
    required this.id,
    required this.slug,
    required this.eventType,
    required this.titleTr,
    required this.shortTitleTr,
    required this.summaryTr,
    required this.generalMeaningTr,
    required this.whatItCanFeelLikeTr,
    required this.whatToWatchTr,
    required this.howToWorkWithItTr,
    required this.whoFeelsItStrongerTr,
    required this.phase,
    required this.status,
    required this.startsAt,
    required this.exactAt,
    required this.endsAt,
    required this.bodies,
    required this.aspect,
    required this.sign,
    required this.tags,
    required this.personalizationCta,
    required this.relatedEvents,
    required this.whyNowTr,
    required this.lifeDomainsTr,
    required this.giftTr,
    required this.shadowTr,
    required this.collectiveExamplesTr,
    required this.microActionTr,
  });

  final String id;
  final String slug;
  final String eventType;
  final String titleTr;
  final String shortTitleTr;
  final String summaryTr;
  final String generalMeaningTr;
  final String whatItCanFeelLikeTr;
  final String whatToWatchTr;
  final String howToWorkWithItTr;
  final String whoFeelsItStrongerTr;
  final String phase;
  final String status;
  final String startsAt;
  final String exactAt;
  final String endsAt;
  final List<String> bodies;
  final String aspect;
  final String sign;
  final List<String> tags;
  final Map<String, dynamic> personalizationCta;
  final List<SkyFeedItemDto> relatedEvents;
  final String whyNowTr;
  final String lifeDomainsTr;
  final String giftTr;
  final String shadowTr;
  final String collectiveExamplesTr;
  final String microActionTr;

  String get displayTitle =>
      shortTitleTr.trim().isNotEmpty ? shortTitleTr.trim() : titleTr.trim();

  factory SkyEventDetailDto.fromMap(Map<String, dynamic> map) {
    final eventMap = map['event'] is Map
        ? Map<String, dynamic>.from(map['event'] as Map)
        : const <String, dynamic>{};
    final metadataMap = eventMap['metadata'] is Map
        ? Map<String, dynamic>.from(eventMap['metadata'] as Map)
        : const <String, dynamic>{};
    final relatedRaw = map['related_events'];
    final bodiesRaw = eventMap['bodies'];
    final tagsRaw = eventMap['tags'];
    return SkyEventDetailDto(
      id: _skyString(eventMap, 'id'),
      slug: _skyString(eventMap, 'slug'),
      eventType: _skyString(eventMap, 'event_type', 'eventType'),
      titleTr: _skyString(eventMap, 'title_tr', 'titleTr'),
      shortTitleTr: _skyString(eventMap, 'short_title_tr', 'shortTitleTr'),
      summaryTr: _skyString(eventMap, 'summary_tr', 'summaryTr'),
      generalMeaningTr: _skyString(
        eventMap,
        'general_meaning_tr',
        'generalMeaningTr',
      ),
      whatItCanFeelLikeTr: _skyString(
        eventMap,
        'what_it_can_feel_like_tr',
        'whatItCanFeelLikeTr',
      ),
      whatToWatchTr: _skyString(eventMap, 'what_to_watch_tr', 'whatToWatchTr'),
      howToWorkWithItTr: _skyString(
        eventMap,
        'how_to_work_with_it_tr',
        'howToWorkWithItTr',
      ),
      whoFeelsItStrongerTr: _skyString(
        eventMap,
        'who_feels_it_stronger_tr',
        'whoFeelsItStrongerTr',
      ),
      phase: _skyString(eventMap, 'phase'),
      status: _skyString(eventMap, 'status'),
      startsAt: _skyString(eventMap, 'starts_at', 'startsAt'),
      exactAt: _skyString(eventMap, 'exact_at', 'exactAt'),
      endsAt: _skyString(eventMap, 'ends_at', 'endsAt'),
      bodies: bodiesRaw is List
          ? [for (final body in bodiesRaw) body.toString()]
          : const <String>[],
      aspect: _skyString(eventMap, 'aspect'),
      sign: _skyString(eventMap, 'sign'),
      tags: tagsRaw is List
          ? [for (final tag in tagsRaw) tag.toString()]
          : const <String>[],
      personalizationCta: map['personalization_cta'] is Map
          ? Map<String, dynamic>.from(map['personalization_cta'] as Map)
          : const <String, dynamic>{},
      relatedEvents: relatedRaw is List
          ? [
              for (final item in relatedRaw)
                if (item is Map)
                  SkyFeedItemDto.fromMap(Map<String, dynamic>.from(item)),
            ]
          : const <SkyFeedItemDto>[],
      whyNowTr: _skyFirstString([
        _skyString(eventMap, 'why_now_tr'),
        _skyString(metadataMap, 'why_now_tr'),
      ]),
      lifeDomainsTr: _skyFirstString([
        _skyString(eventMap, 'life_domains_tr'),
        _skyString(metadataMap, 'life_domains_tr'),
      ]),
      giftTr: _skyFirstString([
        _skyString(eventMap, 'gift_tr'),
        _skyString(metadataMap, 'gift_tr'),
      ]),
      shadowTr: _skyFirstString([
        _skyString(eventMap, 'shadow_tr'),
        _skyString(metadataMap, 'shadow_tr'),
      ]),
      collectiveExamplesTr: _skyFirstString([
        _skyString(eventMap, 'collective_examples_tr'),
        _skyString(metadataMap, 'collective_examples_tr'),
      ]),
      microActionTr: _skyFirstString([
        _skyString(eventMap, 'micro_action_tr'),
        _skyString(metadataMap, 'micro_action_tr'),
      ]),
    );
  }
}

extension SkyFeedItemPresentationX on SkyFeedItemDto {
  String get eventKey => slug.trim().isNotEmpty ? slug.trim() : id.trim();

  String get hookTr => _skyHookFromText(summary);

  List<String> get previewChips {
    final chips = <String>[];
    final typeChip = _skyTypeChip(eventType, fallback: badge);
    final timingChip = _skyTimingChip(relativeTiming);
    final meaningChip = _skyMeaningChipFromText(
      '$summary ${tags.join(' ')} ${bodies.join(' ')} $aspect $sign $title',
    );
    if (typeChip.isNotEmpty) {
      chips.add(typeChip);
    }
    if (timingChip.isNotEmpty && !chips.contains(timingChip)) {
      chips.add(timingChip);
    }
    if (meaningChip.isNotEmpty && !chips.contains(meaningChip)) {
      chips.add(meaningChip);
    }
    return chips;
  }
}

class SkyRepository {
  SkyRepository({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;
  static const Duration _skyCacheTtl = Duration(seconds: 60);
  static const Duration _skyDetailCacheTtl = Duration(seconds: 60);
  static const Duration _skyPersonalCacheTtl = Duration(seconds: 30);

  Future<Map<String, dynamic>> fetchNow({
    required String tz,
    int limit = 4,
  }) async {
    final response = await _client.get(
      '/sky/now',
      queryParameters: <String, dynamic>{'tz': tz, 'limit': '$limit'},
      cacheTtl: _skyCacheTtl,
    );
    return TransitRequestBuilder.asMap(response.data);
  }

  Future<SkyNowDto> fetchFeed({
    required String tz,
    int limit = 12,
    String window = 'week',
  }) async {
    final response = await _client.get(
      '/sky/feed',
      queryParameters: <String, dynamic>{
        'tz': tz,
        'limit': '$limit',
        'window': window,
      },
      cacheTtl: _skyCacheTtl,
    );
    return SkyNowDto.fromMap(TransitRequestBuilder.asMap(response.data));
  }

  Future<SkyEventDetailDto> fetchEventDetail({
    required String idOrSlug,
    required String tz,
  }) async {
    final response = await _client.get(
      '/sky/events/${Uri.encodeComponent(idOrSlug)}',
      queryParameters: <String, dynamic>{'tz': tz},
      cacheTtl: _skyDetailCacheTtl,
    );
    return SkyEventDetailDto.fromMap(
      TransitRequestBuilder.asMap(response.data),
    );
  }

  Future<SkyEventPersonalizationDto> personalizeEvent({
    required String idOrSlug,
    required Map<String, dynamic> profile,
    required String tz,
  }) async {
    final response = await _client.post(
      '/sky/events/${Uri.encodeComponent(idOrSlug)}/personalize?tz=${Uri.encodeQueryComponent(tz)}',
      data: <String, dynamic>{
        'birth_date': (profile['birth_date'] ?? '').toString().trim(),
        'birth_time': TransitRequestBuilder.normalizeBirthTime(
          (profile['birth_time'] ?? '').toString(),
        ),
        'birth_place': TransitRequestBuilder.resolvePlace(profile),
      },
      receiveTimeout: const Duration(seconds: 20),
      cacheTtl: _skyPersonalCacheTtl,
    );
    return SkyEventPersonalizationDto.fromMap(
      TransitRequestBuilder.asMap(response.data),
    );
  }
}

class CalendarRepository {
  CalendarRepository({ApiClient? client}) : _client = client ?? ApiClient();

  final ApiClient _client;
  static const Duration _calendarCacheTtl = Duration(minutes: 3);
  static const Duration _bestTimesCacheTtl = Duration(minutes: 3);

  Future<Map<String, dynamic>> fetchCalendar({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
    String include = 'markers,themes,intent_summary',
    SubscriptionTier? subscriptionTier,
    int? visibleDaysLimit = 7,
    ApiRequestSla requestSla = ApiRequestSla.interactive,
    String locale = 'tr',
  }) async {
    final resolvedTier =
        subscriptionTier ??
        TransitRequestBuilder.resolveSubscriptionTier(profile);
    final response = await _client.get(
      '/transit/calendar',
      queryParameters: TransitRequestBuilder.buildCalendarQuery(
        profile: profile,
        focusedDate: focusedDate,
        include: include,
        subscriptionTier: resolvedTier,
        visibleDaysLimit: visibleDaysLimit,
        locale: locale,
      ),
      requestSla: requestSla,
      cacheTtl: _calendarCacheTtl,
    );
    return TransitRequestBuilder.asMap(response.data);
  }

  Future<Map<String, dynamic>> fetchBestTimes({
    required Map<String, dynamic> profile,
    required DateTime focusedDate,
    ApiRequestSla requestSla = ApiRequestSla.background,
    String locale = 'tr',
  }) async {
    final response = await _client.get(
      '/transit/calendar/best-times',
      queryParameters: TransitRequestBuilder.buildBestTimesQuery(
        profile: profile,
        focusedDate: focusedDate,
        locale: locale,
      ),
      requestSla: requestSla,
      cacheTtl: _bestTimesCacheTtl,
    );
    return TransitRequestBuilder.asMap(response.data);
  }
}

String _skyString(Map<String, dynamic> map, String a, [String? b]) {
  final value = map[a] ?? (b == null ? null : map[b]);
  if (value == null) {
    return '';
  }
  return normalizeTurkishText(value.toString().trim());
}

String _skyRawString(Map<String, dynamic> map, String a, [String? b]) {
  final value = map[a] ?? (b == null ? null : map[b]);
  if (value == null) {
    return '';
  }
  return value.toString().trim();
}

List<String> _skyStringList(Map<String, dynamic> map, String a, [String? b]) {
  final value = map[a] ?? (b == null ? null : map[b]);
  if (value is! List) {
    return const <String>[];
  }
  return normalizeTurkishTextList(value);
}

double? _skyDouble(Map<String, dynamic> map, String a, [String? b]) {
  final value = map[a] ?? (b == null ? null : map[b]);
  if (value is num) {
    return value.toDouble();
  }
  if (value is String && value.trim().isNotEmpty) {
    return double.tryParse(value.trim());
  }
  return null;
}

int? _skyInt(Map<String, dynamic> map, String a, [String? b]) {
  final value = map[a] ?? (b == null ? null : map[b]);
  if (value is int) {
    return value;
  }
  if (value is num) {
    return value.toInt();
  }
  if (value is String && value.trim().isNotEmpty) {
    return int.tryParse(value.trim());
  }
  return null;
}

String _skyFirstString(List<String> values) {
  for (final value in values) {
    final trimmed = value.trim();
    if (trimmed.isNotEmpty) {
      return trimmed;
    }
  }
  return '';
}

String _skyHookFromText(String raw) {
  final l10n = currentL10n();
  final trimmed = raw.trim();
  if (trimmed.isEmpty) {
    return l10n.transitSkyCollectiveFallback;
  }
  final cut = trimmed.split(RegExp(r'[.!?]')).first.trim();
  final candidate = cut.isEmpty ? trimmed : cut;
  return candidate.length > 116
      ? '${candidate.substring(0, 116).trim()}...'
      : candidate;
}

String _skyTypeChip(String eventType, {String fallback = ''}) {
  final l10n = currentL10n();
  switch (eventType.trim()) {
    case 'ingress':
      return l10n.transitSkyTypeIngress;
    case 'lunation_full_moon':
      return l10n.transitSkyTypeFullMoon;
    case 'lunation_new_moon':
      return l10n.transitSkyTypeNewMoon;
    case 'exact_aspect_major':
      return l10n.transitSkyTypeExactAspect;
    case 'eclipse':
      return l10n.transitSkyTypeEclipse;
    case 'retrograde_start':
      return l10n.transitSkyTypeRetroStart;
    case 'retrograde_end':
      return l10n.transitSkyTypeRetroEnd;
    default:
      return fallback.trim();
  }
}

String _skyTimingChip(String relativeTiming) {
  final l10n = currentL10n();
  final trimmed = relativeTiming.trim();
  if (trimmed.isEmpty) {
    return '';
  }
  final lower = trimmed.toLowerCase();
  if (lower.contains('right now')) {
    return l10n.transitSkyTimingNow;
  }
  if (lower.contains('this week')) {
    return l10n.transitSkyTimingThisWeek;
  }
  if (lower.contains('in ') || lower.contains('icinde')) {
    return trimmed;
  }
  if (lower.contains('ago') || lower.contains('once')) {
    return trimmed;
  }
  return trimmed;
}

String _skyMeaningChipFromText(String raw) {
  final l10n = currentL10n();
  final lower = raw.toLowerCase();
  if (lower.contains('venus') ||
      lower.contains('taurus') ||
      lower.contains('libra') ||
      lower.contains('iliski') ||
      lower.contains('ilişki')) {
    return l10n.transitMeaningRelationships;
  }
  if (lower.contains('para') ||
      lower.contains('money') ||
      lower.contains('kaynak')) {
    return l10n.transitMeaningMoney;
  }
  if (lower.contains('sun') ||
      lower.contains('leo') ||
      lower.contains('gorunur') ||
      lower.contains('görünür')) {
    return l10n.transitMeaningVisibility;
  }
  if (lower.contains('mercury') ||
      lower.contains('gemini') ||
      lower.contains('virgo') ||
      lower.contains('karar')) {
    return l10n.transitMeaningDecision;
  }
  if (lower.contains('moon') ||
      lower.contains('cancer') ||
      lower.contains('yakin') ||
      lower.contains('yakın')) {
    return l10n.transitMeaningCloseness;
  }
  if (lower.contains('saturn') ||
      lower.contains('capricorn') ||
      lower.contains('yapi')) {
    return l10n.transitMeaningBuilding;
  }
  if (lower.contains('full moon') ||
      lower.contains('dolunay') ||
      lower.contains('birak')) {
    return l10n.transitMeaningRelease;
  }
  if (lower.contains('mars') ||
      lower.contains('aries') ||
      lower.contains('gerilim')) {
    return l10n.transitMeaningTension;
  }
  if (lower.contains('exact') ||
      lower.contains('net') ||
      lower.contains('gorunur')) {
    return l10n.transitMeaningClarifying;
  }
  if (lower.contains('pluto') ||
      lower.contains('scorpio') ||
      lower.contains('donus')) {
    return l10n.transitMeaningTransformation;
  }
  return '';
}
