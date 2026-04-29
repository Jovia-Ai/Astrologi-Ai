// Home v12 live-data provider katmanı.
//
// Legacy [HomePage] ile aynı `NarrativeRepository.fetchDailyNarrative` çağrısını
// kullanır; bunu `HomeV2Snapshot` DTO'suna sarar. Widget'lar direkt DTO'dan
// okur — başarısızlıkta `null` döner, widget mock fallback'i tutar.

import 'dart:async' show TimeoutException;

import 'package:flutter/foundation.dart' show debugPrint, debugPrintStack;
import 'package:flutter/material.dart' show Color;
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/timing/transit_repositories.dart';

// ─── Repository provider ───────────────────────────────────────

final _narrativeRepositoryProvider = Provider<NarrativeRepository>(
  (ref) => NarrativeRepository(),
);

final _apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

/// `/sky/now` — "şu an gökyüzünde ne oluyor" feed'i. Hero + liste.
/// Askew banner asıl kaynağı. 30sn timeout (cold-start backend için rahat).
final homeV2SkyNowProvider = FutureProvider<SkyNowDto?>((ref) async {
  final client = ref.watch(_apiClientProvider);
  final response = await client
      .get(
        '/sky/now',
        queryParameters: const {'tz': 'Europe/Istanbul', 'limit': '4'},
        receiveTimeout: const Duration(seconds: 30),
        cacheTtl: const Duration(seconds: 60),
      )
      .timeout(
        const Duration(seconds: 35),
        onTimeout: () => throw TimeoutException(
          'sky/now 35sn timeout',
          const Duration(seconds: 35),
        ),
      );
  final data = response.data;
  if (data is! Map) return null;
  return SkyNowDto.fromMap(Map<String, dynamic>.from(data));
});

/// Sky hero → Askew banner DTO dönüşümü. Null hero → null banner.
HomeV2AskewBanner? homeV2AskewFromSkyHero(SkyFeedItemDto? hero) {
  if (hero == null) return null;

  final badge = hero.badge.trim();
  final timing = hero.relativeTiming.trim();
  final eyebrowParts = <String>[
    if (timing.isNotEmpty) timing.toUpperCase(),
    if (badge.isNotEmpty) badge.toUpperCase(),
  ];
  final eyebrow = eyebrowParts.isNotEmpty
      ? eyebrowParts.join(' · ')
      : 'YAKIN GEÇİŞ';

  final iso = hero.exactAt.isNotEmpty ? hero.exactAt : hero.startsAt;
  String dateLabel = '—';
  final parsed = DateTime.tryParse(iso);
  if (parsed != null) {
    final local = parsed.toLocal();
    dateLabel =
        '${local.day.toString().padLeft(2, '0')}.${local.month.toString().padLeft(2, '0')}';
  }

  final name = hero.shortTitle.trim().isNotEmpty
      ? hero.shortTitle
      : (hero.title.trim().isNotEmpty ? hero.title : 'Gökyüzü olayı');
  final sub = hero.summary.trim();

  return HomeV2AskewBanner(
    eyebrow: eyebrow,
    date: dateLabel,
    name: name,
    sub: sub,
  );
}

// ─── Snapshot provider ─────────────────────────────────────────

final homeV2SnapshotProvider = FutureProvider<HomeV2Snapshot?>((ref) async {
  // Profil 6 sn'de gelmezse hata fırlat — sessizce hang kalmasın.
  final Map<String, dynamic>? profile = await ref
      .watch(userProfileProvider.future)
      .timeout(
        const Duration(seconds: 6),
        onTimeout: () => throw TimeoutException(
          'Profil yüklenemedi (6sn timeout)',
          const Duration(seconds: 6),
        ),
      );
  if (profile == null) return null;

  final repo = ref.watch(_narrativeRepositoryProvider);
  final today = DateTime.now();

  final Map<String, dynamic> narrativeMap;
  try {
    narrativeMap = await repo
        .fetchDailyNarrative(
          profile: profile,
          selectedDate: today,
          focusedRange: true,
          includeBestTimes: false,
          responseMode: 'public_only',
          payloadProfile: TransitPayloadProfile.home,
          visibleDaysLimit: 7,
          receiveTimeout: const Duration(seconds: 40),
          requestSla: ApiRequestSla.background,
          cachePolicy: NarrativeCachePolicy.disabled,
          locale: 'tr',
        )
        .timeout(
          const Duration(seconds: 45),
          onTimeout: () => throw TimeoutException(
            'Narrative endpoint 45sn timeout',
            const Duration(seconds: 45),
          ),
        );
  } catch (e, st) {
    // Re-throw; provider error state'ine geçer, dev chip bunu gösterir.
    debugPrint('[home_v2_providers] fetchDailyNarrative failed: $e');
    debugPrintStack(stackTrace: st, maxFrames: 6);
    rethrow;
  }

  final narrative = NarrativeResponse.fromMap(narrativeMap);

  return HomeV2Snapshot(
    today: today,
    displayName: _extractDisplayName(profile),
    narrative: narrative,
  );
});

// ─── Snapshot DTO + türetmeler ─────────────────────────────────

class HomeV2Snapshot {
  const HomeV2Snapshot({
    required this.today,
    required this.displayName,
    required this.narrative,
  });

  final DateTime today;
  final String displayName;
  final NarrativeResponse narrative;

  String get salutation => greetingForHour(today.hour);

  String get formattedDate => _formatTurkishLongDate(today);

  /// "Aslan burcunda" — günün Ay burcu etiketi (varsa).
  String? get moonSignLabel => _extractMoonSignLabel(narrative.dailyEventCards);

  List<HomeV2SkyCard> get skyCards =>
      _buildSkyCards(narrative.dailyEventCards, today);

  HomeV2AskewBanner? get askewBanner =>
      _buildAskewBanner(narrative.periodEventCards, today);

  List<HomeV2WeekDay> get weekDays =>
      _buildWeekDays(narrative.calendarDays, today);
}

// ─── Manifesto yardımcıları ────────────────────────────────────

String greetingForHour(int hour) {
  if (hour < 6) return 'İyi geceler';
  if (hour < 12) return 'Günaydın';
  if (hour < 18) return 'Tünaydın';
  return 'İyi akşamlar';
}

String _extractDisplayName(Map<String, dynamic> profile) {
  final full = (profile['full_name'] as String?)?.trim() ?? '';
  if (full.isNotEmpty) {
    return full.split(RegExp(r'\s+')).first;
  }
  final name = (profile['name'] as String?)?.trim() ?? '';
  if (name.isNotEmpty) return name;
  final email = (profile['email'] as String?)?.trim() ?? '';
  if (email.contains('@')) return email.split('@').first;
  return 'Arkadaşım';
}

const _trMonths = <String>[
  'Ocak',
  'Şubat',
  'Mart',
  'Nisan',
  'Mayıs',
  'Haziran',
  'Temmuz',
  'Ağustos',
  'Eylül',
  'Ekim',
  'Kasım',
  'Aralık',
];

const _trWeekdays = <int, String>{
  DateTime.monday: 'Pazartesi',
  DateTime.tuesday: 'Salı',
  DateTime.wednesday: 'Çarşamba',
  DateTime.thursday: 'Perşembe',
  DateTime.friday: 'Cuma',
  DateTime.saturday: 'Cumartesi',
  DateTime.sunday: 'Pazar',
};

const _trWeekdaysShort = <int, String>{
  DateTime.monday: 'Pzt',
  DateTime.tuesday: 'Sal',
  DateTime.wednesday: 'Çar',
  DateTime.thursday: 'Per',
  DateTime.friday: 'Cum',
  DateTime.saturday: 'Cmt',
  DateTime.sunday: 'Paz',
};

String _formatTurkishLongDate(DateTime d) {
  final month = _trMonths[d.month - 1];
  final weekday = _trWeekdays[d.weekday] ?? '';
  return '${d.day} $month $weekday';
}

String? _extractMoonSignLabel(List<EventCardDto> cards) {
  for (final card in cards) {
    final body = card.transitBody.toLowerCase();
    if (body.contains('moon') || body.contains('ay')) {
      final sig = card.signatureTr.trim();
      if (sig.isNotEmpty) {
        // "Ay · Aslan'da" → "Aslan burcunda"
        final cleaned = sig
            .replaceFirst(RegExp(r'^Ay[\s·]*', caseSensitive: false), '')
            .replaceAll("'da", '')
            .replaceAll("'de", '')
            .replaceAll("’da", '')
            .replaceAll("’de", '')
            .trim();
        if (cleaned.isNotEmpty) return '$cleaned burcunda';
      }
    }
  }
  return null;
}

// ─── Sky rail yardımcıları ─────────────────────────────────────

enum HomeV2SkyTone { now, neutral, blush, lavender }

class HomeV2SkyCard {
  const HomeV2SkyCard({
    required this.tone,
    required this.when,
    required this.planet,
    required this.title,
    required this.italic,
    required this.suffix,
    required this.sub,
    required this.meta,
  });

  final HomeV2SkyTone tone;
  final String when;
  final HomeV2Planet planet;
  final String title;
  final String? italic;
  final String? suffix;
  final String sub;
  final String meta;
}

enum HomeV2Planet { sun, moon, mercury, venus, mars, saturn, unknown }

HomeV2Planet _planetFromBody(String body) {
  final b = body.toLowerCase();
  if (b.contains('sun') || b.contains('güneş') || b.contains('gunes')) {
    return HomeV2Planet.sun;
  }
  if (b.contains('moon') || b.startsWith('ay')) return HomeV2Planet.moon;
  if (b.contains('mercury') || b.contains('merkür') || b.contains('merkur')) {
    return HomeV2Planet.mercury;
  }
  if (b.contains('venus') || b.contains('venüs')) return HomeV2Planet.venus;
  if (b.contains('mars')) return HomeV2Planet.mars;
  if (b.contains('saturn') || b.contains('satürn') || b.contains('saturn')) {
    return HomeV2Planet.saturn;
  }
  return HomeV2Planet.unknown;
}

List<HomeV2SkyCard> _buildSkyCards(List<EventCardDto> cards, DateTime today) {
  if (cards.isEmpty) return const [];
  final result = <HomeV2SkyCard>[];
  for (var i = 0; i < cards.length && result.length < 5; i++) {
    final card = cards[i];
    final tone = i == 0
        ? HomeV2SkyTone.now
        : _toneForIndex(i, card.transitBody);
    result.add(
      HomeV2SkyCard(
        tone: tone,
        when: _whenLabelFor(card, today, isFirst: i == 0),
        planet: _planetFromBody(card.transitBody),
        title: _titlePrefixFor(card),
        italic: _titleItalicFor(card),
        suffix: _titleSuffixFor(card),
        sub: _subtitleFor(card),
        meta: _metaFor(card),
      ),
    );
  }
  return result;
}

HomeV2SkyTone _toneForIndex(int i, String body) {
  final p = _planetFromBody(body);
  if (p == HomeV2Planet.venus) return HomeV2SkyTone.blush;
  if (p == HomeV2Planet.moon || p == HomeV2Planet.saturn) {
    return HomeV2SkyTone.lavender;
  }
  return HomeV2SkyTone.neutral;
}

String _whenLabelFor(EventCardDto card, DateTime today, {required bool isFirst}) {
  final t = card.timeHintTr.trim();
  if (isFirst) return 'Şimdi';
  if (t.isNotEmpty) return t;
  return '—';
}

String _titlePrefixFor(EventCardDto card) {
  final sig = card.signatureTr.trim();
  if (sig.isEmpty) return card.title.isNotEmpty ? card.title : card.headline;
  // Virgül öncesi prefix, sonrası italic adaya aday
  final comma = sig.indexOf(',');
  if (comma > 0) return '${sig.substring(0, comma + 1)} ';
  return sig;
}

String? _titleItalicFor(EventCardDto card) {
  final sig = card.signatureTr.trim();
  final comma = sig.indexOf(',');
  if (comma <= 0) return null;
  final rest = sig.substring(comma + 1).trim();
  // "Başak'a geçer" → italic "Başak'a", suffix " geçer"
  final space = rest.indexOf(' ');
  if (space > 0) return rest.substring(0, space);
  return rest;
}

String? _titleSuffixFor(EventCardDto card) {
  final sig = card.signatureTr.trim();
  final comma = sig.indexOf(',');
  if (comma <= 0) return null;
  final rest = sig.substring(comma + 1).trim();
  final space = rest.indexOf(' ');
  if (space > 0) return ' ${rest.substring(space + 1)}';
  return null;
}

String _subtitleFor(EventCardDto card) {
  // Öncelik: oneLiner (tek cümlelik kısa etki) → feltLineTr → whyItFeels
  // ThisWayTr → essence → headline. `_EVENT_CARD_DISPLAY_TEXT_KEYS`
  // whitelist'indeki alanlar.
  final candidates = [
    card.oneLiner,
    card.feltLineTr,
    card.whyItFeelsThisWayTr,
    card.essence,
    card.headline,
  ];
  for (final c in candidates) {
    final t = c.trim();
    if (t.isNotEmpty) return t;
  }
  return '';
}

String _metaFor(EventCardDto card) {
  final hint = card.timeHintTr.trim();
  if (hint.isNotEmpty) return hint.toUpperCase();
  return card.signalLabelTr.trim().toUpperCase();
}

// ─── Askew banner yardımcıları ─────────────────────────────────

class HomeV2AskewBanner {
  const HomeV2AskewBanner({
    required this.eyebrow,
    required this.date,
    required this.name,
    required this.sub,
  });

  final String eyebrow;
  final String date;
  final String name;
  final String sub;
}

HomeV2AskewBanner? _buildAskewBanner(
  List<EventCardDto> periodCards,
  DateTime today,
) {
  if (periodCards.isEmpty) return null;
  final card = periodCards.first;
  // Tarih formu "22.04" — peak/entry date öncelikli
  final startRaw = card.timing.peakDateUtc.isNotEmpty
      ? card.timing.peakDateUtc
      : card.timing.entryDateUtc;
  String dateLabel = '—';
  int? daysAway;
  final parsed = DateTime.tryParse(startRaw);
  if (parsed != null) {
    final local = parsed.toLocal();
    dateLabel =
        '${local.day.toString().padLeft(2, '0')}.${local.month.toString().padLeft(2, '0')}';
    daysAway = DateTime(local.year, local.month, local.day)
        .difference(DateTime(today.year, today.month, today.day))
        .inDays;
  }
  final eyebrow = daysAway != null && daysAway > 0
      ? '$daysAway GÜN SONRA · BÜYÜK GEÇİŞ'
      : 'YAKIN GEÇİŞ';
  final name = card.signatureTr.trim().isNotEmpty
      ? card.signatureTr.trim()
      : (card.title.isNotEmpty ? card.title : card.headline);
  final sub = [
    card.feltLineTr,
    card.essence,
    card.opening,
    card.bigPicture,
  ].firstWhere((s) => s.trim().isNotEmpty, orElse: () => '');

  return HomeV2AskewBanner(
    eyebrow: eyebrow,
    date: dateLabel,
    name: name,
    sub: sub,
  );
}

// ─── Week strip yardımcıları ───────────────────────────────────

enum HomeV2WeekDayTone { idle, active, blushDay, lavDay }

class HomeV2WeekDay {
  const HomeV2WeekDay({
    required this.date,
    required this.numLabel,
    required this.nameLabel,
    required this.tone,
    this.accentColor,
  });

  final DateTime date;
  final String numLabel;
  final String nameLabel;
  final HomeV2WeekDayTone tone;
  final Color? accentColor;
}

List<HomeV2WeekDay> _buildWeekDays(
  Map<String, NarrativeCalendarDay> calendarDays,
  DateTime today,
) {
  final result = <HomeV2WeekDay>[];
  for (var i = 0; i < 7; i++) {
    final d = DateTime(today.year, today.month, today.day).add(
      Duration(days: i),
    );
    final key = _fmtDateKey(d);
    final meta = calendarDays[key];
    HomeV2WeekDayTone tone;
    if (i == 0) {
      tone = HomeV2WeekDayTone.active;
    } else if (meta?.isCritical ?? false) {
      tone = HomeV2WeekDayTone.lavDay;
    } else if ((meta?.rating ?? 0) >= 4) {
      tone = HomeV2WeekDayTone.blushDay;
    } else {
      tone = HomeV2WeekDayTone.idle;
    }
    result.add(
      HomeV2WeekDay(
        date: d,
        numLabel: d.day.toString(),
        nameLabel: (_trWeekdaysShort[d.weekday] ?? '').toUpperCase(),
        tone: tone,
      ),
    );
  }
  return result;
}

String _fmtDateKey(DateTime d) {
  return '${d.year.toString().padLeft(4, '0')}-'
      '${d.month.toString().padLeft(2, '0')}-'
      '${d.day.toString().padLeft(2, '0')}';
}

