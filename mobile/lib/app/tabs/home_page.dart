// ignore_for_file: unused_element, unused_field, prefer_final_fields

import 'dart:convert';

import 'package:flutter/cupertino.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/tabs/calendar_hub_page.dart';
import 'package:mobile/app/tabs/period_detail_page.dart';
import 'package:mobile/app/tabs/profile_page.dart';
import 'package:mobile/app/tabs/sky_event_detail_page.dart';
import 'package:mobile/app/tabs/sky_event_feed_page.dart';
import 'package:mobile/app/theme/app_theme_mode_provider.dart';
import 'package:mobile/app/timing/narrative_dtos.dart';
import 'package:mobile/app/timing/source_guards.dart';
import 'package:mobile/app/timing/transit_repositories.dart';
import 'package:mobile/design/astro/astro_theme_extension.dart';
import 'package:mobile/design/astro/astro_theme_generator.dart';
import 'package:mobile/design/astro/element_scores.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class HomePage extends ConsumerStatefulWidget {
  const HomePage({super.key});

  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {
  static const String _baseUrl = 'http://127.0.0.1:5000';
  static const Duration _natalCacheTtl = Duration(minutes: 5);
  static const Duration _skyCacheTtl = Duration(seconds: 60);

  bool _loading = false;
  String? _error;
  bool _coreStoryExpanded = false;
  String _coreStory = '';
  String _sunSign = '—';
  String _moonSign = '—';
  String _risingSign = '—';
  List<PeriodCardDto> _periodCards = const <PeriodCardDto>[];
  List<_SkyFeedItemData> _skyFeedItems = const <_SkyFeedItemData>[];
  String _skyFeedSummary = '';
  PeriodCoreDto? _periodCore;
  String? _lastKey;
  final NarrativeRepository _narrativeRepository = NarrativeRepository();

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(userProfileProvider).valueOrNull;
    final user = Supabase.instance.client.auth.currentUser;
    _maybeBootstrap(profile, user);

    final scores = _computeElementScores(
      profile: profile,
      userId: user?.id,
      email: user?.email,
      sun: _sunSign,
      moon: _moonSign,
      rising: _risingSign,
    );

    final themed = withAstroTheme(
      withProfileTheme(Theme.of(context)),
      astroTheme: astroThemeFromElementScores(scores),
    );

    return Theme(
      data: themed,
      child: Builder(
        builder: (context) {
          final profileTheme = context.profileTheme;
          final colors = profileTheme.colors;
          final skyBulletin = _skyFeedItems.isNotEmpty
              ? _buildSkyBulletinFromFeed(
                  items: _skyFeedItems,
                  summary: _skyFeedSummary,
                )
              : _buildSkyBulletin(_periodCards);
          final skyHeroItem = _skyFeedItems.isNotEmpty
              ? _skyFeedItems.first
              : null;
          final displayName = _displayName(profile, user);
          final heroBody = _coreStory.trim().isNotEmpty
              ? _coreStory.trim()
              : (_loading
                    ? 'Bugunun hikayesi yukleniyor...'
                    : 'Bugun icin kisa yorum henuz hazir degil.');
          final activeCard = _periodCards.isNotEmpty
              ? _periodCards.first
              : null;
          final activeTitle = activeCard?.title.trim().isNotEmpty == true
              ? activeCard?.title ?? 'Bugunun acilisi'
              : 'Bugunun acilisi';
          final activeSubtitle = activeCard?.subtitle.trim().isNotEmpty == true
              ? activeCard?.subtitle ?? 'Bugun bende ne aciliyor?'
              : 'Bugun bende ne aciliyor?';
          final dailyCards = _periodCards.take(3).toList(growable: false);
          final collectiveCard = _periodCards.length > 1
              ? _periodCards[1]
              : activeCard;
          final periodBigPicture = _periodCore?.bigPicture.trim() ?? '';
          final lineText = periodBigPicture.isNotEmpty
              ? periodBigPicture
              : heroBody;
          final avatarUrl = (user?.userMetadata?['avatar_url'] ?? '')
              .toString()
              .trim();
          final weekItems = _buildWeekItems(dailyCards);
          final showTimingPanel = _shouldShowTimingPanel(
            periodCore: _periodCore,
            heroBody: heroBody,
            activeTitle: activeTitle,
            activeSubtitle: activeSubtitle,
          );

          return DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: Theme.of(context).brightness == Brightness.dark
                    ? <Color>[
                        const Color(0xFF09080F),
                        const Color(0xFF120F1A),
                        colors.bg,
                      ]
                    : <Color>[
                        const Color(0xFFF5F0FF),
                        const Color(0xFFFFFBFF),
                        colors.bg,
                      ],
                stops: const <double>[0, 0.36, 1],
              ),
            ),
            child: JoviaPageScaffold(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(0, 10, 0, 24),
                children: [
                  _HomeReferenceHeader(
                    displayName: displayName,
                    avatarUrl: avatarUrl.isEmpty ? null : avatarUrl,
                    dateLabel: _formatHomeToday(DateTime.now()),
                    onActionTap: () => _showHomeMenu(context),
                  ),
                  const SizedBox(height: 18),
                  _HomeReferenceHeroCard(
                    title: activeTitle,
                    body: heroBody,
                    prompt: activeSubtitle,
                    weekItems: weekItems,
                    onOpen: activeCard == null
                        ? () => _openTiming(context)
                        : () => _openPeriodDetails(context, activeCard),
                    footer: _HomeSignStateRow(
                      sunSign: _sunSign,
                      moonSign: _moonSign,
                      risingSign: _risingSign,
                    ),
                  ),
                  const SizedBox(height: 26),
                  _HomeSectionLead(
                    title: 'Senin planların',
                    subtitle: 'Bu hafta akışın ve kolektif nabız yan yana.',
                  ),
                  const SizedBox(height: 14),
                  _HomeReferencePlanBoard(
                    activeCard: activeCard,
                    dailyCards: dailyCards,
                    bulletin: skyBulletin,
                    skyItem: skyHeroItem,
                    lineText: lineText,
                    loading: _loading && dailyCards.isEmpty,
                    onOpenActive: activeCard == null
                        ? () => _openTiming(context)
                        : () => _openPeriodDetails(context, activeCard),
                    onOpenCard: (card) => _openPeriodDetails(context, card),
                    onOpenSky: () {
                      if (skyHeroItem != null) {
                        _openSkyEventDetail(context, skyHeroItem);
                      } else if (collectiveCard != null) {
                        _openPeriodDetails(context, collectiveCard);
                      } else {
                        _openTiming(context);
                      }
                    },
                    onOpenCalendar: () => _openTiming(context),
                  ),
                  if (_skyFeedItems.length > 1) ...[
                    const SizedBox(height: 18),
                    _HomeSkyEventList(
                      items: _skyFeedItems.skip(1).take(2).toList(),
                      onOpenItem: (item) => _openSkyEventDetail(context, item),
                      onOpenAll: () => _openSkyFeed(context),
                    ),
                  ],
                  if (showTimingPanel) ...[
                    const SizedBox(height: 24),
                    _HomeReferenceTimingCard(
                      title: (_periodCore?.title.trim().isEmpty ?? true)
                          ? 'Aktif period'
                          : (_periodCore?.title ?? 'Aktif period'),
                      body: (_periodCore?.coreStory.trim().isEmpty ?? true)
                          ? (_periodCore?.bigPicture ?? '')
                          : (_periodCore?.coreStory ?? ''),
                      onTap: () => _openTiming(context),
                    ),
                  ],
                  if (_error != null) ...[
                    const SizedBox(height: 18),
                    Text(
                      _error ?? '',
                      style: context.profileTheme.typography.micro.copyWith(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  bool _shouldShowTimingPanel({
    required PeriodCoreDto? periodCore,
    required String heroBody,
    required String activeTitle,
    required String activeSubtitle,
  }) {
    if (periodCore == null) {
      return false;
    }
    final title = (periodCore.title).trim().toLowerCase();
    final coreStory = (periodCore.coreStory).trim().toLowerCase();
    final bigPicture = (periodCore.bigPicture).trim().toLowerCase();
    final hero = heroBody.trim().toLowerCase();
    final activeTitleNorm = activeTitle.trim().toLowerCase();
    final activeSubtitleNorm = activeSubtitle.trim().toLowerCase();
    final titleRepeats = title.isEmpty || title == activeTitleNorm;
    final bodyCandidate = coreStory.isNotEmpty ? coreStory : bigPicture;
    final bodyRepeats =
        bodyCandidate.isEmpty ||
        bodyCandidate == hero ||
        bodyCandidate == activeSubtitleNorm;
    return !(titleRepeats && bodyRepeats);
  }

  List<_HomeWeekItemData> _buildWeekItems(List<PeriodCardDto> cards) {
    const weekdayLabels = <String>[
      'Pzt',
      'Sal',
      'Çar',
      'Per',
      'Cum',
      'Cmt',
      'Paz',
    ];
    final now = DateTime.now();
    return List<_HomeWeekItemData>.generate(7, (index) {
      final date = DateTime(now.year, now.month, now.day + index);
      final card = index < cards.length ? cards[index] : null;
      return _HomeWeekItemData(
        weekdayLabel: weekdayLabels[date.weekday - 1],
        dayNumber: date.day,
        isToday: index == 0,
        isHighlighted: card != null,
        accent: _homeAccentForIndex(index),
        card: card,
      );
    });
  }

  Color _homeAccentForIndex(int index) {
    const accents = <Color>[
      Color(0xFFFFB84D),
      Color(0xFF8AB6FF),
      Color(0xFFE79BFF),
      Color(0xFF88E6D7),
      Color(0xFFFF9EBC),
      Color(0xFFC0A4FF),
      Color(0xFFFFD780),
    ];
    return accents[index % accents.length];
  }

  String _formatHomeToday(DateTime date) {
    const months = <String>[
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
    return '${date.day} ${months[date.month - 1]}';
  }

  Widget _buildTransitCarousel(BuildContext context) {
    final profileTheme = context.profileTheme;
    final typo = profileTheme.typography;

    if (_loading && _periodCards.isEmpty) {
      return ListView.separated(
        scrollDirection: Axis.horizontal,
        itemBuilder: (_, i) => const _TransitPlaceholderCard(),
        separatorBuilder: (_, i) => SizedBox(width: profileTheme.spacing.sm),
        itemCount: 3,
      );
    }

    if (_periodCards.isEmpty) {
      return _GlassCard(
        child: Align(
          alignment: Alignment.centerLeft,
          child: Text(
            'Period kartlari hazir oldugunda burada gorunecek.',
            style: typo.body.copyWith(color: profileTheme.colors.muted),
          ),
        ),
      );
    }

    final cards = _periodCards.take(5).toList(growable: false);
    return ListView.separated(
      scrollDirection: Axis.horizontal,
      itemCount: cards.length,
      separatorBuilder: (_, i) => SizedBox(width: profileTheme.spacing.sm),
      itemBuilder: (context, index) {
        final card = cards[index];
        return SizedBox(
          width: 286,
          child: _TransitSummaryCard(
            card: card,
            accent: _accentForIndex(index),
            showSticker: index % 3 == 0,
            onTap: () => _openPeriodDetails(context, card),
          ),
        );
      },
    );
  }

  Color _accentForIndex(int index) {
    final colors = context.profileTheme.colors;
    final accents = <Color>[colors.primary, colors.lavender, colors.lime];
    return accents[index % accents.length];
  }

  void _maybeBootstrap(Map<String, dynamic>? profile, User? user) {
    if (!_hasProfile(profile)) {
      return;
    }
    final key =
        '${profile?['birth_date']}|${profile?['birth_time']}|${profile?['place'] ?? profile?['city']}|${profile?['timezone']}|${user?.id}';
    if (_lastKey == key) {
      return;
    }
    _lastKey = key;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || profile == null) {
        return;
      }
      _loadHomeData(profile);
    });
  }

  Future<void> _loadHomeData(Map<String, dynamic> profile) async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final client = ApiClient(baseUrl: _baseUrl);
      final natalPayload = _buildNatalPayload(profile);

      final responses = await Future.wait<dynamic>([
        client.post(
          '/interpret/ui',
          data: natalPayload,
          cacheTtl: _natalCacheTtl,
        ),
        client.get(
          '/sky/now',
          queryParameters: <String, dynamic>{
            'tz': _resolveTimezone(profile),
            'limit': 4,
          },
          cacheTtl: _skyCacheTtl,
        ),
        _narrativeRepository.fetchDailyNarrative(
          profile: profile,
          selectedDate: DateTime.now(),
        ),
      ]);

      final interpretMap = _asMap((responses[0] as Response<dynamic>).data);
      final skyMap = _asMap((responses[1] as Response<dynamic>).data);
      final periodMap = TransitRequestBuilder.asMap(responses[2]);
      final periodNarrative = NarrativeResponse.fromMap(periodMap);
      final periodEvents = pickPeriodEventCards(
        periodNarrative.eventCards,
        context: 'Home/Donem Kartlari',
      );
      final periodCards = <PeriodCardDto>[
        for (var i = 0; i < periodEvents.length; i++)
          PeriodCardDto.fromEventCard(eventCard: periodEvents[i], index: i),
      ];

      final summary = _extractNatalSummary(interpretMap);
      final sun = _toTrSign(_extractPlanetSign(interpretMap, 'Sun'));
      final moon = _toTrSign(_extractPlanetSign(interpretMap, 'Moon'));
      final rising = _toTrSign(_extractRisingSign(interpretMap));

      if (!mounted) {
        return;
      }

      setState(() {
        _coreStory = summary;
        _sunSign = sun;
        _moonSign = moon;
        _risingSign = rising;
        _periodCore = periodNarrative.periodCore;
        _periodCards = periodCards;
        _skyFeedSummary = _extractSkySummary(skyMap);
        _skyFeedItems = _extractSkyFeedItems(skyMap);
        _loading = false;
      });
    } on DioException catch (_) {
      // Fallback: keep page useful if /interpret/ui is not ready.
      await _loadWithFallbackEndpoints(profile);
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _error = e.toString();
      });
    }
  }

  Future<void> _loadWithFallbackEndpoints(Map<String, dynamic> profile) async {
    try {
      final client = ApiClient(baseUrl: _baseUrl);
      final natalPayload = _buildNatalPayload(profile);

      final responses = await Future.wait<dynamic>([
        client.post('/interpret', data: natalPayload, cacheTtl: _natalCacheTtl),
        client.get(
          '/sky/now',
          queryParameters: <String, dynamic>{
            'tz': _resolveTimezone(profile),
            'limit': 4,
          },
          cacheTtl: _skyCacheTtl,
        ),
        _narrativeRepository.fetchDailyNarrative(
          profile: profile,
          selectedDate: DateTime.now(),
        ),
      ]);

      final interpretMap = _asMap((responses[0] as Response<dynamic>).data);
      final skyMap = _asMap((responses[1] as Response<dynamic>).data);
      final periodMap = TransitRequestBuilder.asMap(responses[2]);
      final periodNarrative = NarrativeResponse.fromMap(periodMap);
      final periodEvents = pickPeriodEventCards(
        periodNarrative.eventCards,
        context: 'Home/Donem Kartlari/Fallback',
      );
      final periodCards = <PeriodCardDto>[
        for (var i = 0; i < periodEvents.length; i++)
          PeriodCardDto.fromEventCard(eventCard: periodEvents[i], index: i),
      ];

      if (!mounted) {
        return;
      }

      setState(() {
        _coreStory = _extractNatalSummary(interpretMap);
        _sunSign = _toTrSign(_extractPlanetSign(interpretMap, 'Sun'));
        _moonSign = _toTrSign(_extractPlanetSign(interpretMap, 'Moon'));
        _risingSign = _toTrSign(_extractRisingSign(interpretMap));
        _periodCore = periodNarrative.periodCore;
        _periodCards = periodCards;
        _skyFeedSummary = _extractSkySummary(skyMap);
        _skyFeedItems = _extractSkyFeedItems(skyMap);
        _loading = false;
        _error = null;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _error = 'Home verisi alinamadi: $e';
      });
    }
  }

  Map<String, dynamic> _buildNatalPayload(Map<String, dynamic> profile) {
    final place = _resolvePlace(profile);
    return <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': _normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'locale': 'tr',
    };
  }

  String _resolvePlace(Map<String, dynamic> profile) {
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

  String _resolveTimezone(Map<String, dynamic> profile) {
    final raw = (profile['timezone'] ?? '').toString().trim();
    if (raw.contains('/')) {
      return raw;
    }
    return 'Europe/Istanbul';
  }

  bool _hasProfile(Map<String, dynamic>? profile) {
    if (profile == null) {
      return false;
    }
    final birthDate = (profile['birth_date'] ?? '').toString().trim();
    final birthTime = (profile['birth_time'] ?? '').toString().trim();
    final place = _resolvePlace(profile);
    return birthDate.isNotEmpty && birthTime.isNotEmpty && place.isNotEmpty;
  }

  String _displayName(Map<String, dynamic>? profile, User? user) {
    final fromProfile = (profile?['full_name'] ?? profile?['name'] ?? '')
        .toString()
        .trim();
    if (fromProfile.isNotEmpty) {
      return fromProfile;
    }
    final fromMail = (user?.email ?? '').split('@').first.trim();
    if (fromMail.isNotEmpty) {
      return fromMail;
    }
    return 'Arkadasim';
  }

  void _openTiming(BuildContext context) {
    Navigator.of(
      context,
    ).push(MaterialPageRoute<void>(builder: (_) => const CalendarHubPage()));
  }

  void _openPeriodDetails(BuildContext context, PeriodCardDto card) {
    if (!assertPeriodSource(card, context: 'Home/Donem Kartlari')) {
      return;
    }
    Navigator.of(context, rootNavigator: true).push(
      MaterialPageRoute<void>(
        builder: (_) => PeriodDetailPage(card: card, periodCore: _periodCore),
      ),
    );
  }

  void _openSkyEventDetail(BuildContext context, _SkyFeedItemData item) {
    final dto = item.toDto();
    if (dto.eventKey.isEmpty) {
      return;
    }
    Navigator.of(context, rootNavigator: true).push(
      _adaptiveSwipeRoute<void>(context, (_) => SkyEventDetailPage(item: dto)),
    );
  }

  void _openSkyFeed(BuildContext context) {
    Navigator.of(
      context,
      rootNavigator: true,
    ).push(_adaptiveSwipeRoute<void>(context, (_) => const SkyEventFeedPage()));
  }

  _SkyBulletin _buildSkyBulletin(List<PeriodCardDto> cards) {
    // TODO: Swap this derived source with /sky/now when backend endpoint is available.
    if (cards.isEmpty) {
      return const _SkyBulletin(
        summary: 'Bugun gokyuzu sakin.',
        chips: <String>['Kolektif', 'Gozlem'],
        highlights: <_SkyHighlight>[],
      );
    }

    final sorted = [...cards]
      ..sort((a, b) => _skyScore(b).compareTo(_skyScore(a)));
    final selected = sorted.take(4).toList(growable: false);
    final highlights = <_SkyHighlight>[
      for (final card in selected)
        _SkyHighlight(
          title: card.title.isNotEmpty ? card.title : 'Genel Gokyuzu Etkisi',
          blurb: _collectiveBlurb(card),
        ),
    ];
    final chips = _buildSkyChips(selected);
    return _SkyBulletin(
      summary: _collectiveSummary(chips),
      chips: chips,
      highlights: highlights,
    );
  }

  _SkyBulletin _buildSkyBulletinFromFeed({
    required List<_SkyFeedItemData> items,
    required String summary,
  }) {
    if (items.isEmpty) {
      return _buildSkyBulletin(const <PeriodCardDto>[]);
    }
    final hero = items.first;
    return _SkyBulletin(
      summary: summary.trim().isNotEmpty ? summary.trim() : hero.summary,
      chips: hero.previewChips.take(3).toList(growable: false),
      highlights: [
        for (final item in items)
          _SkyHighlight(title: item.title, blurb: item.summary),
      ],
    );
  }

  double _skyScore(PeriodCardDto card) {
    final haystack = '${card.title} ${card.subtitle} ${card.timeHint}'
        .toLowerCase();
    double score = 1.0;
    if (haystack.contains('saturn') ||
        haystack.contains('uranus') ||
        haystack.contains('neptune') ||
        haystack.contains('pluto')) {
      score += 2.0;
    }
    if (haystack.contains('long') || haystack.contains('uzun')) {
      score += 1.0;
    }
    if (haystack.contains('retro') ||
        haystack.contains('station') ||
        haystack.contains('ingress') ||
        haystack.contains('exact') ||
        haystack.contains('peak')) {
      score += 0.7;
    }
    return score;
  }

  String _collectiveSummary(List<String> chips) {
    final lower = chips.map((e) => e.toLowerCase()).toSet();
    String first =
        'Bu donemde kolektif ritimde yavas ama kalici degisimler one cikiyor.';
    if (lower.contains('donusum')) {
      first = 'Kolektif alanda donusum ve yeniden yapilanma etkisi belirgin.';
    } else if (lower.contains('yapi')) {
      first =
          'Yapi, sinir ve sorumluluk temalari kolektif alanda agirlik kazaniyor.';
    } else if (lower.contains('degisim')) {
      first =
          'Degisim ve yenilenme basliklari genel atmosferde daha gorunur durumda.';
    }

    String second = 'Hizdan cok sureklilik ve planli adimlar destekleniyor.';
    if (lower.contains('belirsizlik')) {
      second =
          'Algilar ve beklentilerde dalgalanmalar olabilecegi icin netlik onemli.';
    } else if (lower.contains('retro')) {
      second =
          'Gecmis temalara donup duzeltme yapmak, yeni adimlardan daha verimli olabilir.';
    }
    return '$first $second';
  }

  List<String> _buildSkyChips(List<PeriodCardDto> cards) {
    final chips = <String>{};
    for (final card in cards) {
      final haystack = '${card.title} ${card.subtitle} ${card.timeHint}'
          .toLowerCase();
      if (haystack.contains('retro')) {
        chips.add('Retro');
      }
      if (haystack.contains('saturn')) {
        chips.add('Yapi');
      }
      if (haystack.contains('pluto')) {
        chips.add('Donusum');
      }
      if (haystack.contains('uranus')) {
        chips.add('Degisim');
      }
      if (haystack.contains('neptune')) {
        chips.add('Belirsizlik');
      }
      if (haystack.contains('long') || haystack.contains('uzun')) {
        chips.add('Uzun Dongu');
      }
      if (chips.length >= 3) {
        break;
      }
    }
    if (chips.isEmpty) {
      return const <String>['Kolektif', 'Ritim'];
    }
    return chips.take(3).toList(growable: false);
  }

  String _collectiveBlurb(PeriodCardDto card) {
    final source = card.subtitle.trim().isNotEmpty
        ? card.subtitle.trim()
        : card.timeHint.trim();
    if (source.isEmpty) {
      return 'Genel atmosferde bu etkinin kademeli olarak guclenmesi bekleniyor.';
    }
    final cut = source.split(RegExp(r'[.!?]')).first.trim();
    final clean = cut.isEmpty ? source : cut;
    return clean.length > 140 ? '${clean.substring(0, 140).trim()}...' : clean;
  }

  String _extractSkySummary(Map<String, dynamic> map) {
    final summary = (map['summary_tr'] ?? '').toString().trim();
    if (summary.isNotEmpty) {
      return summary;
    }
    final hero = _asMap(map['hero']);
    return (hero['summary_tr'] ?? '').toString().trim();
  }

  List<_SkyFeedItemData> _extractSkyFeedItems(Map<String, dynamic> map) {
    final items = map['items'];
    if (items is! List) {
      return const <_SkyFeedItemData>[];
    }
    return items
        .whereType<Map>()
        .map(
          (item) => _SkyFeedItemData.fromMap(Map<String, dynamic>.from(item)),
        )
        .where((item) => item.title.isNotEmpty && item.summary.isNotEmpty)
        .toList();
  }

  Future<void> _showHomeMenu(BuildContext context) async {
    final profile = context.profileTheme;
    await showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        return Consumer(
          builder: (context, ref, _) {
            final currentMode = ref.watch(joviaThemeModeProvider);
            return Padding(
              padding: EdgeInsets.all(profile.spacing.lg),
              child: JoviaSurfaceCard(
                padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
                radius: 30,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    JoviaEditorialHeroBlock(
                      label: 'Quick control',
                      title: 'Menü',
                      body:
                          'Profil, görünüm ve temel ayarlara daha premium bir panelden eriş.',
                      surface: false,
                      accent: const JoviaIllustrationAccent(
                        asset: JoviaIllustrationAsset.layers,
                        width: 70,
                        height: 70,
                        opacity: 0.74,
                      ),
                    ),
                    const SizedBox(height: 16),
                    JoviaSurfaceCard(
                      radius: 24,
                      padding: const EdgeInsets.all(14),
                      child: JoviaUtilityRow(
                        label: 'Profile',
                        title: 'Profili düzenle',
                        body: 'Profil ekranına git ve bilgilerini güncelle.',
                        leading: const JoviaUiIcon(
                          asset: JoviaUiAsset.profileComet,
                          size: 18,
                        ),
                        onTap: () {
                          Navigator.of(sheetContext).pop();
                          Navigator.of(context).push(
                            MaterialPageRoute<void>(
                              builder: (_) => const ProfilePage(),
                            ),
                          );
                        },
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Tema modu',
                      style: profile.typography.eyebrow.copyWith(
                        color: profile.colors.textLight,
                        letterSpacing: 1.45,
                      ),
                    ),
                    const SizedBox(height: 10),
                    JoviaModeSwitch<JoviaThemeMode>(
                      value: currentMode,
                      leadingValue: JoviaThemeMode.dark,
                      leadingLabel: 'Dark',
                      trailingValue: JoviaThemeMode.light,
                      trailingLabel: 'Light',
                      onChanged: (mode) {
                        ref.read(joviaThemeModeProvider.notifier).setMode(mode);
                      },
                    ),
                    const SizedBox(height: 16),
                    JoviaSurfaceCard(
                      radius: 24,
                      padding: const EdgeInsets.all(14),
                      child: JoviaUtilityRow(
                        label: 'Session',
                        title: 'Çıkış yap',
                        body: 'Mevcut oturumu kapat ve giriş ekranına dön.',
                        leading: const JoviaUiIcon(
                          asset: JoviaUiAsset.profileComet,
                          size: 18,
                        ),
                        onTap: () async {
                          Navigator.of(sheetContext).pop();
                          await Supabase.instance.client.auth.signOut();
                        },
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
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
      } catch (_) {}
    }
    return <String, dynamic>{};
  }

  String _extractNatalSummary(Map<String, dynamic> map) {
    final pub = map['public'];
    if (pub is Map) {
      final ui = pub['core_story_ui'];
      if (ui is Map && (ui['text'] ?? '').toString().trim().isNotEmpty) {
        return (ui['text'] ?? '').toString().trim();
      }
      if ((pub['core_story'] ?? '').toString().trim().isNotEmpty) {
        return (pub['core_story'] ?? '').toString();
      }
    }
    final directUi = map['core_story_ui'];
    if (directUi is Map &&
        (directUi['text'] ?? '').toString().trim().isNotEmpty) {
      return (directUi['text'] ?? '').toString().trim();
    }
    final direct = (map['core_story'] ?? '').toString().trim();
    if (direct.isNotEmpty) {
      return direct;
    }
    return (map['summary'] ?? map['narrative_text'] ?? '').toString().trim();
  }

  String _extractPlanetSign(Map<String, dynamic> map, String planetName) {
    final targets = <String>{
      planetName.toLowerCase(),
      if (planetName.toLowerCase() == 'ascendant') ...{'ascendant', 'asc'},
    };

    for (final scope in _natalScopes(map)) {
      final planets = scope['planets'];
      if (planets is List) {
        for (final raw in planets) {
          if (raw is! Map) {
            continue;
          }
          final name = (raw['planet'] ?? raw['name'] ?? raw['body'] ?? '')
              .toString()
              .toLowerCase();
          if (!targets.contains(name)) {
            continue;
          }
          final sign = (raw['sign'] ?? raw['zodiac_sign'] ?? '')
              .toString()
              .trim();
          if (sign.isNotEmpty) {
            return sign;
          }
        }
      }

      final signMap = scope['planet_signs'] ?? scope['signs'];
      if (signMap is Map) {
        for (final entry in signMap.entries) {
          final key = entry.key.toString().toLowerCase();
          if (!targets.contains(key)) {
            continue;
          }
          final sign = entry.value.toString().trim();
          if (sign.isNotEmpty) {
            return sign;
          }
        }
      }
    }
    return '—';
  }

  String _extractRisingSign(Map<String, dynamic> map) {
    final fromPlanet = _extractPlanetSign(map, 'Ascendant');
    if (fromPlanet != '—') {
      return fromPlanet;
    }
    for (final scope in _natalScopes(map)) {
      final angles = scope['angles'];
      if (angles is Map) {
        final sign = (angles['ascendant_sign'] ?? angles['asc_sign'] ?? '')
            .toString()
            .trim();
        if (sign.isNotEmpty) {
          return sign;
        }
      }
    }
    return '—';
  }

  List<Map<String, dynamic>> _natalScopes(Map<String, dynamic> map) {
    final scopes = <Map<String, dynamic>>[map];
    final pub = _asMap(map['public']);
    if (pub.isNotEmpty) {
      scopes.add(pub);
    }
    final metaInfo = _asMap(map['meta_info']);
    if (metaInfo.isNotEmpty) {
      scopes.add(metaInfo);
    }
    return scopes;
  }

  String _toTrSign(String raw) {
    const signs = <String, String>{
      'aries': 'Koc',
      'taurus': 'Boga',
      'gemini': 'Ikizler',
      'cancer': 'Yengec',
      'leo': 'Aslan',
      'virgo': 'Basak',
      'libra': 'Terazi',
      'scorpio': 'Akrep',
      'sagittarius': 'Yay',
      'capricorn': 'Oglak',
      'aquarius': 'Kova',
      'pisces': 'Balik',
      'koc': 'Koc',
      'koç': 'Koc',
      'boga': 'Boga',
      'boğa': 'Boga',
      'yengec': 'Yengec',
      'yengeç': 'Yengec',
      'basak': 'Basak',
      'başak': 'Basak',
      'ikizler': 'Ikizler',
      'terazi': 'Terazi',
      'akrep': 'Akrep',
      'yay': 'Yay',
      'oglak': 'Oglak',
      'oğlak': 'Oglak',
      'kova': 'Kova',
      'balik': 'Balik',
      'balık': 'Balik',
    };
    final key = raw.trim().toLowerCase();
    return signs[key] ?? (raw.trim().isEmpty ? '—' : raw.trim());
  }

  String _normalizeBirthTime(String raw) {
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
}

class _HomeWeekItemData {
  const _HomeWeekItemData({
    required this.weekdayLabel,
    required this.dayNumber,
    required this.isToday,
    required this.isHighlighted,
    required this.accent,
    required this.card,
  });

  final String weekdayLabel;
  final int dayNumber;
  final bool isToday;
  final bool isHighlighted;
  final Color accent;
  final PeriodCardDto? card;
}

class _HomeReferenceHeader extends StatelessWidget {
  const _HomeReferenceHeader({
    required this.displayName,
    required this.avatarUrl,
    required this.dateLabel,
    required this.onActionTap,
  });

  final String displayName;
  final String? avatarUrl;
  final String dateLabel;
  final VoidCallback onActionTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final firstName = displayName.trim().split(RegExp(r'\s+')).first.trim();

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: Row(
        children: [
          _HomeReferenceAvatar(
            imageUrl: avatarUrl,
            fallbackLabel: firstName.isEmpty ? '?' : firstName.substring(0, 1),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Merhaba ${firstName.isEmpty ? 'sen' : firstName}',
                  style: profile.typography.card.copyWith(
                    color: profile.colors.text,
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Bugün $dateLabel',
                  style: profile.typography.bodyCompact.copyWith(
                    color: profile.colors.textLight,
                  ),
                ),
              ],
            ),
          ),
          _HomeReferenceActionButton(
            icon: Icons.search_rounded,
            onTap: onActionTap,
            isDark: isDark,
          ),
        ],
      ),
    );
  }
}

class _HomeReferenceAvatar extends StatelessWidget {
  const _HomeReferenceAvatar({
    required this.imageUrl,
    required this.fallbackLabel,
  });

  final String? imageUrl;
  final String fallbackLabel;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      width: 46,
      height: 46,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFFFC89A), Color(0xFFA78BFA)],
        ),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFA78BFA).withValues(alpha: 0.22),
            blurRadius: 16,
            offset: const Offset(0, 10),
            spreadRadius: -10,
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(2.4),
        child: ClipOval(
          child: Container(
            color: profile.colors.surface,
            alignment: Alignment.center,
            child: (imageUrl ?? '').trim().isEmpty
                ? Text(
                    fallbackLabel.toUpperCase(),
                    style: profile.typography.body.copyWith(
                      color: profile.colors.text,
                      fontWeight: FontWeight.w700,
                    ),
                  )
                : Image.network(
                    imageUrl!,
                    fit: BoxFit.cover,
                    errorBuilder: (_, _, _) => Text(
                      fallbackLabel.toUpperCase(),
                      style: profile.typography.body.copyWith(
                        color: profile.colors.text,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
          ),
        ),
      ),
    );
  }
}

class _HomeReferenceActionButton extends StatelessWidget {
  const _HomeReferenceActionButton({
    required this.icon,
    required this.onTap,
    required this.isDark,
  });

  final IconData icon;
  final VoidCallback onTap;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: isDark
          ? Colors.white.withValues(alpha: 0.06)
          : Colors.white.withValues(alpha: 0.72),
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: isDark
                  ? Colors.white.withValues(alpha: 0.12)
                  : Colors.black.withValues(alpha: 0.06),
            ),
          ),
          child: Icon(
            icon,
            size: 20,
            color: isDark ? Colors.white : const Color(0xFF16141A),
          ),
        ),
      ),
    );
  }
}

class _HomeReferenceHeroCard extends StatelessWidget {
  const _HomeReferenceHeroCard({
    required this.title,
    required this.body,
    required this.prompt,
    required this.weekItems,
    required this.onOpen,
    required this.footer,
  });

  final String title;
  final String body;
  final String prompt;
  final List<_HomeWeekItemData> weekItems;
  final VoidCallback onOpen;
  final Widget footer;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: TweenAnimationBuilder<double>(
        tween: Tween<double>(begin: 0, end: 1),
        duration: const Duration(milliseconds: 650),
        curve: Curves.easeOutCubic,
        builder: (context, value, child) {
          return Opacity(
            opacity: value,
            child: Transform.translate(
              offset: Offset(0, 18 * (1 - value)),
              child: child,
            ),
          );
        },
        child: Container(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(34),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: isDark
                  ? const <Color>[
                      Color(0xFF201A2E),
                      Color(0xFF171520),
                      Color(0xFF121017),
                    ]
                  : const <Color>[
                      Color(0xFFB698FF),
                      Color(0xFFD6C7FF),
                      Color(0xFFF8F3FF),
                    ],
            ),
            border: Border.all(
              color: isDark
                  ? Colors.white.withValues(alpha: 0.08)
                  : Colors.white.withValues(alpha: 0.54),
            ),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFFA78BFA).withValues(alpha: 0.22),
                blurRadius: 28,
                offset: const Offset(0, 18),
                spreadRadius: -18,
              ),
            ],
          ),
          child: Stack(
            children: [
              Positioned(
                right: -18,
                top: -8,
                child: JoviaIllustrationAccent(
                  asset: JoviaIllustrationAsset.planet,
                  width: 138,
                  height: 138,
                  opacity: isDark ? 0.92 : 0.98,
                ),
              ),
              Positioned(
                left: -22,
                bottom: 78,
                child: JoviaIllustrationAccent(
                  asset: JoviaIllustrationAsset.shape,
                  width: 72,
                  height: 72,
                  opacity: isDark ? 0.16 : 0.12,
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Günün teması',
                    style: profile.typography.bodyCompact.copyWith(
                      color: isDark
                          ? Colors.white.withValues(alpha: 0.72)
                          : const Color(0xFF3E315E),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 240),
                    child: Text(
                      title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.editorialHeadline.copyWith(
                        color: isDark ? Colors.white : const Color(0xFF161122),
                        fontSize: 34,
                        height: 1.02,
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 232),
                    child: Text(
                      body,
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.bodyReading.copyWith(
                        color: isDark
                            ? Colors.white.withValues(alpha: 0.82)
                            : const Color(0xFF3F3355),
                        fontSize: 14.8,
                        height: 1.5,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          prompt,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: profile.typography.bodyCompact.copyWith(
                            color: isDark
                                ? Colors.white.withValues(alpha: 0.76)
                                : const Color(0xFF5A4E75),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      _HomeHeroButton(onTap: onOpen),
                    ],
                  ),
                  const SizedBox(height: 16),
                  footer,
                  const SizedBox(height: 18),
                  _HomeWeekStrip(items: weekItems, fallbackTap: onOpen),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _HomeHeroButton extends StatelessWidget {
  const _HomeHeroButton({required this.onTap});

  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Material(
      color: isDark ? Colors.white : const Color(0xFF15131A),
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          child: Text(
            'Aç',
            style: context.profileTheme.typography.buttonLabel.copyWith(
              color: isDark ? const Color(0xFF17131E) : Colors.white,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ),
    );
  }
}

class _HomeWeekStrip extends StatelessWidget {
  const _HomeWeekStrip({required this.items, required this.fallbackTap});

  final List<_HomeWeekItemData> items;
  final VoidCallback fallbackTap;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          for (var index = 0; index < items.length; index++) ...[
            _HomeWeekDayChip(
              item: items[index],
              onTap: items[index].card == null ? fallbackTap : null,
            ),
            if (index != items.length - 1) const SizedBox(width: 10),
          ],
        ],
      ),
    );
  }
}

class _HomeWeekDayChip extends StatelessWidget {
  const _HomeWeekDayChip({required this.item, this.onTap});

  final _HomeWeekItemData item;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final child = AnimatedContainer(
      duration: const Duration(milliseconds: 240),
      curve: Curves.easeOutCubic,
      width: 52,
      padding: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        color: item.isToday
            ? (isDark ? Colors.white : const Color(0xFF16131D))
            : (isDark
                  ? Colors.white.withValues(alpha: 0.08)
                  : Colors.white.withValues(alpha: 0.72)),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: item.isToday
              ? item.accent.withValues(alpha: 0.68)
              : (isDark
                    ? Colors.white.withValues(alpha: 0.08)
                    : Colors.black.withValues(alpha: 0.06)),
        ),
        boxShadow: item.isToday
            ? [
                BoxShadow(
                  color: item.accent.withValues(alpha: 0.28),
                  blurRadius: 18,
                  offset: const Offset(0, 10),
                  spreadRadius: -10,
                ),
              ]
            : null,
      ),
      child: Column(
        children: [
          Text(
            item.weekdayLabel,
            style: context.profileTheme.typography.micro.copyWith(
              color: item.isToday
                  ? (isDark ? const Color(0xFF16131D) : Colors.white)
                  : (isDark
                        ? Colors.white.withValues(alpha: 0.76)
                        : const Color(0xFF6B6480)),
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '${item.dayNumber}',
            style: context.profileTheme.typography.body.copyWith(
              color: item.isToday
                  ? (isDark ? const Color(0xFF16131D) : Colors.white)
                  : (isDark ? Colors.white : const Color(0xFF16131D)),
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: item.isHighlighted ? item.accent : Colors.transparent,
            ),
          ),
        ],
      ),
    );
    if (onTap == null) {
      return child;
    }
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: child,
    );
  }
}

class _HomeSectionLead extends StatelessWidget {
  const _HomeSectionLead({required this.title, required this.subtitle});

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: profile.typography.section.copyWith(
              color: profile.colors.text,
              fontSize: 28,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            subtitle,
            style: profile.typography.bodyCompact.copyWith(
              color: profile.colors.textLight,
            ),
          ),
        ],
      ),
    );
  }
}

class _HomeReferencePlanBoard extends StatelessWidget {
  const _HomeReferencePlanBoard({
    required this.activeCard,
    required this.dailyCards,
    required this.bulletin,
    required this.skyItem,
    required this.lineText,
    required this.loading,
    required this.onOpenActive,
    required this.onOpenCard,
    required this.onOpenSky,
    required this.onOpenCalendar,
  });

  final PeriodCardDto? activeCard;
  final List<PeriodCardDto> dailyCards;
  final _SkyBulletin bulletin;
  final _SkyFeedItemData? skyItem;
  final String lineText;
  final bool loading;
  final VoidCallback onOpenActive;
  final ValueChanged<PeriodCardDto> onOpenCard;
  final VoidCallback onOpenSky;
  final VoidCallback onOpenCalendar;

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.of(context).size.width < 392;
    final skyTitle = skyItem?.title ?? 'Kolektif nabız';
    final skyBody = skyItem?.hook.isNotEmpty == true
        ? skyItem!.hook
        : bulletin.summary;
    final thirdCard = dailyCards.length > 1 ? dailyCards[1] : activeCard;

    if (loading && activeCard == null && dailyCards.isEmpty) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 32),
        child: Center(child: CircularProgressIndicator()),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: Column(
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                flex: compact ? 1 : 11,
                child: _HomeColorPlanCard(
                  title: activeCard?.title.isNotEmpty == true
                      ? activeCard!.title
                      : 'Günün planı',
                  metaTop: activeCard?.timeHint.trim().isNotEmpty == true
                      ? activeCard!.timeHint.trim()
                      : 'Primary',
                  body: activeCard?.subtitle.trim().isNotEmpty == true
                      ? activeCard!.subtitle.trim()
                      : lineText,
                  footer:
                      activeCard?.eventCard?.signatureTr.trim().isNotEmpty ==
                          true
                      ? activeCard!.eventCard!.signatureTr.trim()
                      : 'Takvime geç',
                  palette: const _HomeCardPalette.sunset(),
                  onTap: onOpenActive,
                  tall: true,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                flex: compact ? 1 : 9,
                child: Column(
                  children: [
                    _HomeColorPlanCard(
                      title: skyTitle,
                      metaTop: skyItem?.badge.isNotEmpty == true
                          ? skyItem!.badge
                          : 'Collective',
                      body: skyBody,
                      footer:
                          skyItem?.previewChips.skip(1).take(2).join(' • ') ??
                          bulletin.chips.take(2).join(' • '),
                      palette: const _HomeCardPalette.sky(),
                      onTap: onOpenSky,
                    ),
                    const SizedBox(height: 12),
                    _HomeColorPlanCard(
                      title: thirdCard?.title.isNotEmpty == true
                          ? thirdCard!.title
                          : 'Takvim',
                      metaTop: thirdCard?.timeHint.trim().isNotEmpty == true
                          ? thirdCard!.timeHint.trim()
                          : 'Week',
                      body: thirdCard?.subtitle.trim().isNotEmpty == true
                          ? thirdCard!.subtitle.trim()
                          : 'Önündeki 1 haftalık akışı aç.',
                      footer: '1 haftalık görünüm',
                      palette: const _HomeCardPalette.candy(),
                      onTap: thirdCard != null
                          ? () => onOpenCard(thirdCard)
                          : onOpenCalendar,
                      compact: true,
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _HomeReferenceTimingCard(
            title: 'Haftalık takvim',
            body:
                'Mevcut takvim akışını küçük görünümden aç ve tüm haftayı gör.',
            onTap: onOpenCalendar,
          ),
        ],
      ),
    );
  }
}

class _HomeCardPalette {
  const _HomeCardPalette({
    required this.background,
    required this.foreground,
    required this.surface,
    required this.chip,
  });

  const _HomeCardPalette.sunset()
    : background = const <Color>[Color(0xFFFFC15A), Color(0xFFFFAE45)],
      foreground = const Color(0xFF1C1407),
      surface = const Color(0x40FFFFFF),
      chip = const Color(0xFFFFE2AA);

  const _HomeCardPalette.sky()
    : background = const <Color>[Color(0xFFB6D3FF), Color(0xFF8BB8FF)],
      foreground = const Color(0xFF12203D),
      surface = const Color(0x42FFFFFF),
      chip = const Color(0xFFDCEAFF);

  const _HomeCardPalette.candy()
    : background = const <Color>[Color(0xFFF9B7FF), Color(0xFFE9A3FF)],
      foreground = const Color(0xFF33153A),
      surface = const Color(0x42FFFFFF),
      chip = const Color(0xFFFFD8FF);

  final List<Color> background;
  final Color foreground;
  final Color surface;
  final Color chip;
}

class _HomeColorPlanCard extends StatelessWidget {
  const _HomeColorPlanCard({
    required this.title,
    required this.metaTop,
    required this.body,
    required this.footer,
    required this.palette,
    required this.onTap,
    this.tall = false,
    this.compact = false,
  });

  final String title;
  final String metaTop;
  final String body;
  final String footer;
  final _HomeCardPalette palette;
  final VoidCallback onTap;
  final bool tall;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0, end: 1),
      duration: Duration(milliseconds: tall ? 620 : 700),
      curve: Curves.easeOutCubic,
      builder: (context, value, child) {
        return Opacity(
          opacity: value,
          child: Transform.translate(
            offset: Offset(0, 16 * (1 - value)),
            child: child,
          ),
        );
      },
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(28),
          child: Container(
            constraints: BoxConstraints(minHeight: tall ? 212 : 100),
            padding: EdgeInsets.fromLTRB(
              compact ? 14 : 16,
              compact ? 14 : 16,
              compact ? 14 : 16,
              compact ? 14 : 16,
            ),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(28),
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: palette.background,
              ),
              boxShadow: [
                BoxShadow(
                  color: palette.background.last.withValues(alpha: 0.24),
                  blurRadius: 24,
                  offset: const Offset(0, 16),
                  spreadRadius: -18,
                ),
              ],
            ),
            child: Stack(
              children: [
                Positioned(
                  right: -16,
                  top: -12,
                  child: Container(
                    width: compact ? 68 : 84,
                    height: compact ? 68 : 84,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.white.withValues(alpha: 0.18),
                    ),
                  ),
                ),
                Positioned(
                  right: 18,
                  bottom: 18,
                  child: Container(
                    width: compact ? 42 : 50,
                    height: compact ? 42 : 50,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: palette.surface,
                    ),
                    child: Icon(
                      compact
                          ? Icons.auto_awesome_rounded
                          : Icons.wb_sunny_outlined,
                      color: palette.foreground.withValues(alpha: 0.82),
                      size: compact ? 18 : 22,
                    ),
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 5,
                      ),
                      decoration: BoxDecoration(
                        color: palette.surface,
                        borderRadius: BorderRadius.circular(999),
                      ),
                      child: Text(
                        metaTop,
                        style: profile.typography.micro.copyWith(
                          color: palette.foreground.withValues(alpha: 0.82),
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    const SizedBox(height: 14),
                    ConstrainedBox(
                      constraints: BoxConstraints(
                        maxWidth: compact ? 150 : 180,
                      ),
                      child: Text(
                        title,
                        maxLines: compact ? 2 : 3,
                        overflow: TextOverflow.ellipsis,
                        style: profile.typography.section.copyWith(
                          color: palette.foreground,
                          fontSize: compact ? 22 : 30,
                          height: 1.04,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      body,
                      maxLines: compact ? 2 : 4,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.bodyCompact.copyWith(
                        color: palette.foreground.withValues(alpha: 0.82),
                        height: 1.45,
                      ),
                    ),
                    SizedBox(height: compact ? 18 : 28),
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            footer,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: profile.typography.bodyCompact.copyWith(
                              color: palette.foreground.withValues(alpha: 0.88),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Icon(
                          Icons.arrow_outward_rounded,
                          color: palette.foreground,
                          size: 18,
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _HomeReferenceTimingCard extends StatelessWidget {
  const _HomeReferenceTimingCard({
    required this.title,
    required this.body,
    required this.onTap,
  });

  final String title;
  final String body;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(26),
          child: Container(
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(26),
              color: isDark
                  ? Colors.white.withValues(alpha: 0.06)
                  : Colors.white.withValues(alpha: 0.82),
              border: Border.all(
                color: isDark
                    ? Colors.white.withValues(alpha: 0.08)
                    : Colors.black.withValues(alpha: 0.05),
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: profile.typography.card.copyWith(
                          color: profile.colors.text,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        body,
                        style: profile.typography.bodyCompact.copyWith(
                          color: profile.colors.textLight,
                          height: 1.45,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: const Color(0xFFA78BFA).withValues(alpha: 0.18),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Icon(
                    Icons.calendar_month_rounded,
                    color: Color(0xFF7B5AF8),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _HomeAuraHeader extends StatelessWidget {
  const _HomeAuraHeader({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    return Container(
      constraints: const BoxConstraints(minHeight: 170),
      decoration: BoxDecoration(
        color: colors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: colors.strokeSoft, width: 1.5),
        boxShadow: [profile.shadows.cardShadow],
      ),
      child: Stack(
        children: [
          Positioned(
            right: 10,
            top: 10,
            child: Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: colors.lavender.withValues(alpha: 0.22),
                borderRadius: BorderRadius.circular(36),
              ),
            ),
          ),
          Padding(padding: const EdgeInsets.fromLTRB(0, 0, 0, 0), child: child),
        ],
      ),
    );
  }
}

class _HomeSignStateRow extends StatelessWidget {
  const _HomeSignStateRow({
    required this.sunSign,
    required this.moonSign,
    required this.risingSign,
  });

  final String sunSign;
  final String moonSign;
  final String risingSign;

  @override
  Widget build(BuildContext context) {
    final chips = <String>[
      if (sunSign.trim().isNotEmpty && sunSign.trim() != '—') 'Gunes $sunSign',
      if (moonSign.trim().isNotEmpty && moonSign.trim() != '—') 'Ay $moonSign',
      if (risingSign.trim().isNotEmpty && risingSign.trim() != '—')
        'Yukselen $risingSign',
    ];

    if (chips.isEmpty) {
      return const SizedBox.shrink();
    }

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          for (var index = 0; index < chips.length; index++) ...[
            JoviaMetaPill(label: chips[index]),
            if (index != chips.length - 1) const SizedBox(width: 8),
          ],
        ],
      ),
    );
  }
}

class _HomeOpeningHeroCard extends StatelessWidget {
  const _HomeOpeningHeroCard({
    required this.title,
    required this.body,
    required this.prompt,
    required this.onOpen,
    required this.footer,
  });

  final String title;
  final String body;
  final String prompt;
  final VoidCallback onOpen;
  final Widget footer;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return _HomePosterShell(
      padding: const EdgeInsets.all(12),
      child: _HomePosterStage(
        wash: JoviaColorAsset.wash03,
        primaryIllustration: JoviaIllustrationAsset.planet,
        secondaryIllustration: JoviaIllustrationAsset.shape,
        minHeight: 548,
        primaryTop: 36,
        primaryRight: 52,
        primaryWidth: 184,
        primaryHeight: 184,
        secondaryTop: 140,
        secondaryLeft: -34,
        secondaryWidth: 86,
        secondaryHeight: 86,
        washOpacity: 0.055,
        padding: const EdgeInsets.fromLTRB(22, 20, 22, 22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 196),
            Text(
              'BUGUNUN ACILISI',
              style: profile.typography.monoEyebrow.copyWith(
                color: profile.colors.textLight,
                fontSize: 11.5,
                letterSpacing: 1.9,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              title,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.editorialHeadline.copyWith(
                color: profile.colors.text,
                fontSize: 34,
                height: 1.02,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              body,
              maxLines: 4,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.bodyReading.copyWith(
                color: profile.colors.textLight,
                fontSize: 15.6,
                height: 1.6,
              ),
            ),
            const SizedBox(height: 18),
            JoviaSurfaceCard(
              backgroundColor: isDark
                  ? const Color(0xFF090807)
                  : Color.alphaBlend(
                      profile.colors.warmAccent.withValues(alpha: 0.08),
                      profile.colors.panelSoft,
                    ),
              borderColor: profile.colors.warmAccent.withValues(alpha: 0.16),
              radius: 30,
              padding: const EdgeInsets.fromLTRB(18, 16, 16, 16),
              shadow: false,
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Bugunun acilis sorusu',
                          style: profile.typography.monoEyebrow.copyWith(
                            color: profile.colors.textLight,
                            fontSize: 11.5,
                            letterSpacing: 1.7,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          prompt,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: profile.typography.bodyCompact.copyWith(
                            color: profile.colors.text,
                            fontWeight: FontWeight.w600,
                            height: 1.42,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 14),
                  MinimalCTAButton(
                    label: 'Aç',
                    emphasized: true,
                    onTap: onOpen,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            footer,
          ],
        ),
      ),
    );
  }
}

class _HomePosterShell extends StatelessWidget {
  const _HomePosterShell({
    required this.child,
    this.padding = const EdgeInsets.all(12),
    this.radius = 34,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final double radius;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return JoviaSurfaceCard(
      backgroundColor: isDark
          ? const Color(0xFF030303)
          : Color.alphaBlend(
              profile.colors.primary.withValues(alpha: 0.05),
              profile.colors.panelStrong,
            ),
      borderColor: profile.colors.strokeSoft,
      radius: radius,
      padding: padding,
      child: child,
    );
  }
}

class _HomePosterStage extends StatelessWidget {
  const _HomePosterStage({
    required this.child,
    required this.wash,
    required this.primaryIllustration,
    this.radius = 28,
    this.height,
    this.minHeight,
    this.primaryRight = -18,
    this.primaryTop,
    this.primaryWidth = 148,
    this.primaryHeight = 148,
    this.secondaryIllustration,
    this.secondaryLeft = -24,
    this.secondaryTop,
    this.secondaryWidth = 80,
    this.secondaryHeight = 80,
    this.washOpacity = 0.05,
    this.padding = const EdgeInsets.all(18),
  });

  final Widget child;
  final JoviaColorAsset wash;
  final JoviaIllustrationAsset primaryIllustration;
  final double radius;
  final double? height;
  final double? minHeight;
  final double primaryRight;
  final double? primaryTop;
  final double primaryWidth;
  final double primaryHeight;
  final JoviaIllustrationAsset? secondaryIllustration;
  final double secondaryLeft;
  final double? secondaryTop;
  final double secondaryWidth;
  final double secondaryHeight;
  final double washOpacity;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final secondaryAsset = secondaryIllustration;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      height: height,
      constraints: BoxConstraints(minHeight: minHeight ?? 0),
      decoration: BoxDecoration(
        color: isDark
            ? const Color(0xFF050505)
            : Color.alphaBlend(
                Colors.white.withValues(alpha: 0.3),
                profile.colors.heroBase,
              ),
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(color: profile.colors.strokeSoft),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(radius - 1),
        child: Stack(
          children: [
            Positioned.fill(
              child: JoviaColorWash(
                asset: wash,
                opacity: washOpacity * 0.5,
                alignment: Alignment.topCenter,
              ),
            ),
            Positioned(
              right: primaryRight,
              top: primaryTop,
              child: JoviaIllustrationAccent(
                asset: primaryIllustration,
                width: primaryWidth,
                height: primaryHeight,
                opacity: 0.92,
              ),
            ),
            if (secondaryAsset != null)
              Positioned(
                left: secondaryLeft,
                top: secondaryTop,
                child: JoviaIllustrationAccent(
                  asset: secondaryAsset,
                  width: secondaryWidth,
                  height: secondaryHeight,
                  opacity: 0.1,
                ),
              ),
            Padding(padding: padding, child: child),
          ],
        ),
      ),
    );
  }
}

class _HomeEditorialLine extends StatelessWidget {
  const _HomeEditorialLine({required this.label, required this.text});

  final String label;
  final String text;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14),
      child: JoviaSurfaceCard(
        radius: 30,
        padding: const EdgeInsets.fromLTRB(20, 22, 20, 24),
        backgroundColor: isDark
            ? profile.colors.panelStrong
            : Color.alphaBlend(
                Colors.white.withValues(alpha: 0.56),
                profile.colors.panelSoft,
              ),
        borderColor: profile.colors.strokeSoft,
        shadow: false,
        child: Column(
          children: [
            Text(
              label.toUpperCase(),
              textAlign: TextAlign.center,
              style: profile.typography.monoEyebrow.copyWith(
                color: profile.colors.textLight,
                fontSize: 11.5,
                letterSpacing: 1.9,
              ),
            ),
            const SizedBox(height: 12),
            Container(width: 92, height: 1, color: profile.colors.separator),
            const SizedBox(height: 14),
            Text(
              text,
              textAlign: TextAlign.center,
              maxLines: 4,
              overflow: TextOverflow.ellipsis,
              style: profile.typography.section.copyWith(
                color: profile.colors.text,
                fontSize: 26,
                height: 1.2,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HomeDailyUpdateStrip extends StatelessWidget {
  const _HomeDailyUpdateStrip({
    required this.cards,
    required this.loading,
    required this.onOpen,
  });

  final List<PeriodCardDto> cards;
  final bool loading;
  final ValueChanged<PeriodCardDto> onOpen;

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const SizedBox(
        height: 132,
        child: Center(child: CircularProgressIndicator()),
      );
    }
    if (cards.isEmpty) {
      return const SizedBox(
        height: 200,
        child: JoviaSurfaceCard(
          child: Align(
            alignment: Alignment.centerLeft,
            child: Text('Daily update strip su an bos.'),
          ),
        ),
      );
    }

    return SizedBox(
      height: 246,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: cards.length,
        separatorBuilder: (context, index) => const SizedBox(width: 12),
        itemBuilder: (context, index) {
          final card = cards[index];
          final meta = card.timeHint.trim().isNotEmpty
              ? card.timeHint.trim()
              : 'Timing';
          final subtitle = card.subtitle.trim().isNotEmpty
              ? card.subtitle.trim()
              : 'Detayi ac';
          final textMaxWidth = index == 1 ? 154.0 : 162.0;
          final accentAsset = <JoviaIllustrationAsset>[
            JoviaIllustrationAsset.planet,
            JoviaIllustrationAsset.sunMountain,
            JoviaIllustrationAsset.layers,
          ][index % 3];
          return SizedBox(
            width: 272,
            child: JoviaPressable(
              onTap: () => onOpen(card),
              borderRadius: BorderRadius.circular(20),
              child: _HomePosterShell(
                padding: const EdgeInsets.all(10),
                radius: 28,
                child: _HomePosterStage(
                  wash: index.isEven
                      ? JoviaColorAsset.wash14
                      : JoviaColorAsset.wash05,
                  primaryIllustration: accentAsset,
                  secondaryIllustration: JoviaIllustrationAsset.shape,
                  primaryTop: 14,
                  primaryRight: index == 1 ? -2 : 8,
                  primaryWidth: index == 1 ? 108 : 92,
                  primaryHeight: index == 1 ? 108 : 92,
                  secondaryTop: 70,
                  secondaryLeft: -26,
                  secondaryWidth: 70,
                  secondaryHeight: 70,
                  radius: 22,
                  height: 224,
                  minHeight: 224,
                  washOpacity: 0.05,
                  padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        meta.toUpperCase(),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: context.profileTheme.typography.monoEyebrow
                            .copyWith(
                              color: context.profileTheme.colors.textLight,
                              fontSize: 11.2,
                              letterSpacing: 1.65,
                            ),
                      ),
                      const SizedBox(height: 8),
                      const SizedBox(height: 24),
                      ConstrainedBox(
                        constraints: BoxConstraints(maxWidth: textMaxWidth),
                        child: Text(
                          card.title.isNotEmpty ? card.title : 'Aktif akis',
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: context.profileTheme.typography.section
                              .copyWith(
                                color: context.profileTheme.colors.text,
                                fontSize: 18.4,
                                height: 1.12,
                              ),
                        ),
                      ),
                      const SizedBox(height: 10),
                      ConstrainedBox(
                        constraints: BoxConstraints(maxWidth: textMaxWidth),
                        child: Text(
                          subtitle,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: context.profileTheme.typography.metaSoft
                              .copyWith(
                                color: context.profileTheme.colors.textLight,
                                height: 1.34,
                              ),
                        ),
                      ),
                      const Spacer(),
                      IgnorePointer(
                        child: Align(
                          alignment: Alignment.centerLeft,
                          child: MinimalCTAButton(
                            label: 'Aç',
                            emphasized: true,
                            onTap: null,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _HomeActiveThemeCard extends StatelessWidget {
  const _HomeActiveThemeCard({required this.card, required this.onOpen});

  final PeriodCardDto? card;
  final VoidCallback onOpen;

  @override
  Widget build(BuildContext context) {
    final titleValue = card?.title.trim() ?? '';
    final subtitleValue = card?.subtitle.trim() ?? '';
    final signatureValue = card?.eventCard?.signatureTr.trim() ?? '';
    final title = titleValue.isNotEmpty ? titleValue : 'Aktif tema bekleniyor';
    final body = subtitleValue.isNotEmpty
        ? subtitleValue
        : 'Period akisindan gelen aktif tema burada kompakt kart olarak gorunecek.';
    final timeHint = card?.timeHint.trim() ?? '';

    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 430;
        final metaChips = <String>[
          if (timeHint.isNotEmpty) timeHint,
          if (signatureValue.isNotEmpty) signatureValue,
        ].take(compact ? 1 : 2).toList(growable: false);

        final cta = MinimalCTAButton(
          label: 'Temayı aç',
          emphasized: true,
          onTap: onOpen,
        );

        return _HomePosterShell(
          child: _HomePosterStage(
            wash: JoviaColorAsset.wash14,
            primaryIllustration: compact
                ? JoviaIllustrationAsset.planet
                : JoviaIllustrationAsset.sunMountain,
            secondaryIllustration: JoviaIllustrationAsset.shape,
            primaryTop: 18,
            primaryRight: compact ? -10 : 14,
            primaryWidth: compact ? 132 : 170,
            primaryHeight: compact ? 132 : 170,
            secondaryTop: 104,
            secondaryLeft: -24,
            secondaryWidth: 68,
            secondaryHeight: 68,
            radius: 28,
            minHeight: compact ? 292 : 336,
            washOpacity: 0.06,
            padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  timeHint.isNotEmpty ? timeHint.toUpperCase() : 'SIMDI AKTIF',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: context.profileTheme.typography.monoEyebrow.copyWith(
                    color: context.profileTheme.colors.textLight,
                    fontSize: 11.5,
                    letterSpacing: 1.8,
                  ),
                ),
                SizedBox(height: compact ? 58 : 72),
                Text(
                  title,
                  maxLines: compact ? 2 : 2,
                  overflow: TextOverflow.ellipsis,
                  style: context.profileTheme.typography.editorialHeadline
                      .copyWith(
                        color: context.profileTheme.colors.text,
                        fontWeight: FontWeight.w600,
                        fontSize: compact ? 28 : 34,
                        height: 1.04,
                      ),
                ),
                const SizedBox(height: 12),
                Text(
                  body,
                  maxLines: compact ? 3 : 3,
                  overflow: TextOverflow.ellipsis,
                  style: context.profileTheme.typography.bodyReading.copyWith(
                    color: context.profileTheme.colors.textLight,
                    fontSize: 15.4,
                    height: 1.56,
                  ),
                ),
                if (metaChips.isNotEmpty) ...[
                  const SizedBox(height: 14),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: [
                        for (
                          var index = 0;
                          index < metaChips.length;
                          index++
                        ) ...[
                          JoviaMetaPill(label: metaChips[index]),
                          if (index != metaChips.length - 1)
                            const SizedBox(width: 8),
                        ],
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 18),
                Align(alignment: Alignment.centerLeft, child: cta),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _HomeCollectivePulseCard extends StatelessWidget {
  const _HomeCollectivePulseCard({
    required this.bulletin,
    required this.card,
    required this.skyItem,
    required this.onOpenThread,
  });

  final _SkyBulletin bulletin;
  final PeriodCardDto? card;
  final _SkyFeedItemData? skyItem;
  final VoidCallback onOpenThread;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final chips =
        skyItem?.previewChips.take(3).toList(growable: false) ??
        bulletin.chips.take(2).toList(growable: false);
    final cardTitle = card?.title.trim() ?? '';
    final fallbackCard = card;
    final blurb =
        skyItem?.summary ??
        (fallbackCard == null
            ? bulletin.summary
            : _blurbFromCard(fallbackCard));
    final title =
        skyItem?.title ?? (cardTitle.isNotEmpty ? cardTitle : 'Acik konular');
    return JoviaSurfaceCard(
      radius: 34,
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
      child: Stack(
        children: [
          Positioned(
            right: -8,
            top: 2,
            child: JoviaIllustrationAccent(
              asset: JoviaIllustrationAsset.sunMountain,
              width: 128,
              height: 128,
              opacity: 0.8,
            ),
          ),
          Positioned(
            right: 44,
            top: 30,
            child: Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: profile.colors.primary.withValues(alpha: 0.16),
              ),
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'KOLEKTIF KONU',
                style: profile.typography.monoEyebrow.copyWith(
                  color: profile.colors.textLight,
                  fontSize: 11.5,
                  letterSpacing: 1.85,
                ),
              ),
              const SizedBox(height: 10),
              Container(width: 146, height: 1, color: profile.colors.separator),
              const SizedBox(height: 16),
              Text(
                title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: profile.typography.editorialHeadline.copyWith(
                  color: profile.colors.text,
                  fontSize: 31,
                  height: 1.02,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 14),
              ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 300),
                child: Text(
                  blurb,
                  maxLines: 4,
                  overflow: TextOverflow.ellipsis,
                  style: profile.typography.bodyReading.copyWith(
                    color: profile.colors.textLight,
                    fontSize: 15.0,
                    height: 1.62,
                  ),
                ),
              ),
              if (chips.isNotEmpty) ...[
                const SizedBox(height: 16),
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    for (final chip in chips) JoviaMetaPill(label: chip),
                  ],
                ),
              ],
              const SizedBox(height: 18),
              Wrap(
                spacing: 10,
                runSpacing: 10,
                children: [
                  MinimalCTAButton(
                    label: "Thread'e gir",
                    emphasized: true,
                    onTap: onOpenThread,
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _blurbFromCard(PeriodCardDto card) {
    final source = card.subtitle.trim().isNotEmpty
        ? card.subtitle.trim()
        : card.timeHint.trim();
    if (source.isEmpty) {
      return 'Genel atmosferde bu etkinin kademeli olarak guclenmesi bekleniyor.';
    }
    final cut = source.split(RegExp(r'[.!?]')).first.trim();
    final clean = cut.isEmpty ? source : cut;
    return clean.length > 140 ? '${clean.substring(0, 140).trim()}...' : clean;
  }
}

class _HomeCollectiveHighlightsRow extends StatelessWidget {
  const _HomeCollectiveHighlightsRow({required this.items});

  final List<_SkyHighlight> items;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const SizedBox.shrink();
    }
    final accents = <Color>[
      context.profileTheme.colors.primary,
      context.profileTheme.colors.lavender,
      context.profileTheme.colors.lime,
    ];
    return SizedBox(
      height: 152,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: items.length,
        separatorBuilder: (_, _) => const SizedBox(width: 12),
        itemBuilder: (context, index) {
          return SizedBox(
            width: 240,
            child: _SkyMiniCard(
              item: items[index],
              accent: accents[index % accents.length],
            ),
          );
        },
      ),
    );
  }
}

class _HomeSkyEventList extends StatelessWidget {
  const _HomeSkyEventList({
    required this.items,
    required this.onOpenItem,
    required this.onOpenAll,
  });

  final List<_SkyFeedItemData> items;
  final ValueChanged<_SkyFeedItemData> onOpenItem;
  final VoidCallback onOpenAll;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const SizedBox.shrink();
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final item in items) ...[
          _HomeSkyEventCard(item: item, onTap: () => onOpenItem(item)),
          if (item != items.last) const SizedBox(height: 14),
        ],
        const SizedBox(height: 14),
        JoviaSurfaceCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Acik konular',
                style: context.profileTheme.typography.cardTitle,
              ),
              const SizedBox(height: 10),
              Text(
                'Kolektifte su an calisan tum basliklara buradan gir.',
                style: context.profileTheme.typography.bodyCompact.copyWith(
                  color: context.profileTheme.colors.textLight,
                ),
              ),
              const SizedBox(height: 16),
              MinimalCTAButton(
                label: 'Tum konular',
                emphasized: true,
                onTap: onOpenAll,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _HomeSkyEventCard extends StatelessWidget {
  const _HomeSkyEventCard({required this.item, required this.onTap});

  final _SkyFeedItemData item;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return JoviaTopicSurface(
      eyebrow: item.previewChips.isNotEmpty ? item.previewChips.first : null,
      title: item.title,
      body: item.hook,
      meta: item.previewChips.skip(1).take(2).toList(growable: false),
      secondaryAction: const Icon(Icons.arrow_outward_rounded, size: 18),
      onTap: onTap,
    );
  }
}

class _SkyMiniCard extends StatelessWidget {
  const _SkyMiniCard({required this.item, required this.accent});

  final _SkyHighlight item;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    final typo = context.profileTheme.typography;
    final colors = context.profileTheme.colors;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colors.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: colors.strokeSoft, width: 1.5),
        boxShadow: [context.profileTheme.shadows.cardShadow],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 28,
            height: 6,
            decoration: BoxDecoration(
              color: accent.withValues(alpha: 0.55),
              borderRadius: BorderRadius.circular(999),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            item.title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: typo.body.copyWith(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: colors.text,
            ),
          ),
          const SizedBox(height: 4),
          Expanded(
            child: Text(
              item.blurb,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
              style: typo.micro.copyWith(color: colors.textLight, height: 1.3),
            ),
          ),
        ],
      ),
    );
  }
}

class _SkyHighlight {
  const _SkyHighlight({required this.title, required this.blurb});

  final String title;
  final String blurb;
}

class _SkyFeedItemData {
  const _SkyFeedItemData({
    required this.id,
    required this.slug,
    required this.eventType,
    required this.title,
    required this.shortTitle,
    required this.summary,
    required this.badge,
    required this.relativeTiming,
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
  final String startsAt;
  final String exactAt;
  final String endsAt;
  final List<String> tags;
  final List<String> bodies;
  final String aspect;
  final String sign;
  final Map<String, dynamic> personalizationCta;

  String get hook => toDto().hookTr;

  List<String> get previewChips => toDto().previewChips;

  SkyFeedItemDto toDto() {
    return SkyFeedItemDto(
      id: id,
      slug: slug,
      eventType: eventType,
      title: title,
      shortTitle: shortTitle,
      summary: summary,
      badge: badge,
      relativeTiming: relativeTiming,
      phase: '',
      status: '',
      startsAt: startsAt,
      exactAt: exactAt,
      endsAt: endsAt,
      tags: tags,
      bodies: bodies,
      aspect: aspect,
      sign: sign,
      personalizationCta: personalizationCta,
    );
  }

  factory _SkyFeedItemData.fromMap(Map<String, dynamic> map) {
    final dto = SkyFeedItemDto.fromMap(map);
    return _SkyFeedItemData(
      id: dto.id.trim(),
      slug: dto.slug.trim(),
      eventType: dto.eventType.trim(),
      title: dto.title.trim(),
      shortTitle: dto.shortTitle.trim(),
      summary: dto.summary.trim(),
      badge: dto.badge.trim(),
      relativeTiming: dto.relativeTiming.trim(),
      startsAt: dto.startsAt.trim(),
      exactAt: dto.exactAt.trim(),
      endsAt: dto.endsAt.trim(),
      tags: dto.tags,
      bodies: dto.bodies,
      aspect: dto.aspect.trim(),
      sign: dto.sign.trim(),
      personalizationCta: dto.personalizationCta,
    );
  }
}

class _SkyBulletin {
  const _SkyBulletin({
    required this.summary,
    required this.chips,
    required this.highlights,
  });

  final String summary;
  final List<String> chips;
  final List<_SkyHighlight> highlights;
}

class _GlassCard extends StatelessWidget {
  const _GlassCard({
    required this.child,
    this.padding = const EdgeInsets.all(18),
  });

  final Widget child;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: profile.colors.panelStrong,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: profile.colors.strokeSoft, width: 1.15),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.09),
            blurRadius: 14,
            offset: const Offset(0, 8),
            spreadRadius: -12,
          ),
        ],
      ),
      child: child,
    );
  }
}

class _TransitSummaryCard extends StatelessWidget {
  const _TransitSummaryCard({
    required this.card,
    required this.accent,
    required this.showSticker,
    required this.onTap,
  });

  final PeriodCardDto card;
  final Color accent;
  final bool showSticker;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final typo = context.profileTheme.typography;
    final colors = context.profileTheme.colors;

    final overview = card.subtitle.trim();
    final badgeMeta = card.timeHint.trim();
    final badgeTitle = badgeMeta.isNotEmpty ? badgeMeta : 'Period';

    return _GlassCard(
      padding: const EdgeInsets.all(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Stack(
          children: [
            if (showSticker)
              Positioned(
                right: 4,
                top: 4,
                child: Container(
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    color: accent.withValues(alpha: 0.35),
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        card.title.isNotEmpty ? card.title : 'Aktif Transit',
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: typo.body.copyWith(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: colors.text,
                          height: 1.2,
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    _TransitBadge(
                      title: badgeTitle.isNotEmpty ? badgeTitle : 'Transit',
                      meta: '',
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  overview.isNotEmpty ? overview : 'Detaylar icin karti ac.',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: typo.body.copyWith(
                    fontSize: 14.5,
                    color: colors.muted,
                    height: 1.4,
                  ),
                ),
                const Spacer(),
                Row(
                  children: [
                    const Spacer(),
                    OutlinedButton(
                      onPressed: onTap,
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size(0, 30),
                        visualDensity: VisualDensity.compact,
                        backgroundColor: colors.surface,
                        side: BorderSide(color: colors.strokeSoft, width: 1.5),
                        foregroundColor: colors.primary,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(999),
                        ),
                      ),
                      child: const Text('Detaylar ->'),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

Route<T> _adaptiveSwipeRoute<T>(BuildContext context, WidgetBuilder builder) {
  final platform = Theme.of(context).platform;
  if (platform == TargetPlatform.iOS || platform == TargetPlatform.macOS) {
    return CupertinoPageRoute<T>(builder: builder);
  }
  return MaterialPageRoute<T>(builder: builder);
}

class _TransitBadge extends StatelessWidget {
  const _TransitBadge({required this.title, required this.meta});

  final String title;
  final String meta;

  @override
  Widget build(BuildContext context) {
    final typo = context.profileTheme.typography;
    final colors = context.profileTheme.colors;
    return Container(
      constraints: const BoxConstraints(maxWidth: 118),
      height: 28,
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: colors.lime,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.end,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: typo.micro.copyWith(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: colors.primary,
              height: 1,
            ),
          ),
          if (meta.trim().isNotEmpty)
            Text(
              meta,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: typo.micro.copyWith(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: colors.primary.withValues(alpha: 0.8),
                height: 1,
              ),
            ),
        ],
      ),
    );
  }
}

class _TransitPlaceholderCard extends StatelessWidget {
  const _TransitPlaceholderCard();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 290,
      child: _GlassCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            _LineBox(widthFactor: 0.6, height: 14),
            SizedBox(height: 10),
            _LineBox(widthFactor: 0.8, height: 10),
            SizedBox(height: 14),
            _LineBox(widthFactor: 1.0, height: 10),
            SizedBox(height: 8),
            _LineBox(widthFactor: 0.95, height: 10),
            SizedBox(height: 8),
            _LineBox(widthFactor: 0.7, height: 10),
          ],
        ),
      ),
    );
  }
}

class _LineBox extends StatelessWidget {
  const _LineBox({required this.widthFactor, required this.height});

  final double widthFactor;
  final double height;

  @override
  Widget build(BuildContext context) {
    final astro = context.astroTheme;
    return FractionallySizedBox(
      widthFactor: widthFactor,
      child: Container(
        height: height,
        decoration: BoxDecoration(
          color: astro.border.withValues(alpha: 0.45),
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }
}

ElementScores _computeElementScores({
  required Map<String, dynamic>? profile,
  required String? userId,
  required String? email,
  required String sun,
  required String moon,
  required String rising,
}) {
  final fromProfile = _extractElementScoresFromProfile(profile);
  if (fromProfile != null) {
    return fromProfile;
  }

  final fromSigns = _extractElementScoresFromSigns(
    sun: sun,
    moon: moon,
    rising: rising,
  );
  if (fromSigns != null) {
    return fromSigns;
  }

  final seed = userId ?? email ?? 'anon';
  final hash = seed.codeUnits.fold<int>(
    17,
    (acc, c) => (acc * 31 + c) & 0x7fffffff,
  );
  final dominant = hash % 4;
  final values = <double>[0.22, 0.22, 0.22, 0.22];
  values[dominant] += 0.34;
  return ElementScores(
    fire: values[0],
    water: values[1],
    air: values[2],
    earth: values[3],
  ).normalize();
}

ElementScores? _extractElementScoresFromProfile(Map<String, dynamic>? profile) {
  if (profile == null) {
    return null;
  }

  final direct = _extractElementScoresFromAny(profile);
  if (direct != null) {
    return direct;
  }

  for (final key in const <String>[
    'element_scores',
    'elements',
    'natal_element_scores',
    'astro_element_scores',
  ]) {
    final nested = _extractElementScoresFromAny(profile[key]);
    if (nested != null) {
      return nested;
    }
  }

  return null;
}

ElementScores? _extractElementScoresFromAny(dynamic source) {
  if (source is! Map) {
    return null;
  }
  final map = Map<String, dynamic>.from(source);
  final keys = map.keys.map((k) => k.toLowerCase()).toSet();
  if (!keys.contains('fire') ||
      !keys.contains('water') ||
      !keys.contains('air') ||
      !keys.contains('earth')) {
    return null;
  }
  return ElementScores.fromMap(map);
}

ElementScores? _extractElementScoresFromSigns({
  required String sun,
  required String moon,
  required String rising,
}) {
  final weights = <AstroElement, double>{
    AstroElement.fire: 0,
    AstroElement.water: 0,
    AstroElement.air: 0,
    AstroElement.earth: 0,
  };

  void addSign(String sign, double weight) {
    final s = sign.trim().toLowerCase();
    if (s.isEmpty || s == '—') {
      return;
    }

    const fire = <String>{
      'aries',
      'leo',
      'sagittarius',
      'koc',
      'koç',
      'aslan',
      'yay',
    };
    const earth = <String>{
      'taurus',
      'virgo',
      'capricorn',
      'boga',
      'boğa',
      'basak',
      'başak',
      'oglak',
      'oğlak',
    };
    const air = <String>{
      'gemini',
      'libra',
      'aquarius',
      'ikizler',
      'terazi',
      'kova',
    };
    const water = <String>{
      'cancer',
      'scorpio',
      'pisces',
      'yengec',
      'yengeç',
      'akrep',
      'balik',
      'balık',
    };

    if (fire.contains(s)) {
      weights[AstroElement.fire] = (weights[AstroElement.fire] ?? 0) + weight;
    } else if (water.contains(s)) {
      weights[AstroElement.water] = (weights[AstroElement.water] ?? 0) + weight;
    } else if (air.contains(s)) {
      weights[AstroElement.air] = (weights[AstroElement.air] ?? 0) + weight;
    } else if (earth.contains(s)) {
      weights[AstroElement.earth] = (weights[AstroElement.earth] ?? 0) + weight;
    }
  }

  addSign(sun, 0.4);
  addSign(moon, 0.35);
  addSign(rising, 0.25);

  if (weights.values.every((v) => v == 0)) {
    return null;
  }

  return ElementScores(
    fire: weights[AstroElement.fire] ?? 0,
    water: weights[AstroElement.water] ?? 0,
    air: weights[AstroElement.air] ?? 0,
    earth: weights[AstroElement.earth] ?? 0,
  ).normalize();
}
