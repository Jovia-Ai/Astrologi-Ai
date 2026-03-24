// ignore_for_file: unused_element, unused_field, prefer_final_fields

import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/tabs/calendar_hub_page.dart';
import 'package:mobile/app/tabs/period_detail_page.dart';
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

  bool _loading = false;
  String? _error;
  bool _coreStoryExpanded = false;
  String _coreStory = '';
  String _sunSign = '—';
  String _moonSign = '—';
  String _risingSign = '—';
  List<PeriodCardDto> _periodCards = const <PeriodCardDto>[];
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
          final skyBulletin = _buildSkyBulletin(_periodCards);
          final displayName = _displayName(profile, user);
          final heroBody = _coreStory.trim().isNotEmpty
              ? _coreStory.trim()
              : (_loading
                    ? 'Bugunun hikayesi yukleniyor...'
                    : 'Bugun icin kisa yorum henuz hazir degil.');
          final activeCard = _periodCards.isNotEmpty
              ? _periodCards.first
              : null;
          final dailyCards = _periodCards.take(3).toList(growable: false);
          final collectiveCard = _periodCards.length > 1
              ? _periodCards[1]
              : activeCard;
          final lineText = _periodCore?.bigPicture.trim().isNotEmpty == true
              ? _periodCore!.bigPicture.trim()
              : heroBody;

          return DecoratedBox(
            decoration: BoxDecoration(
              color: colors.bg,
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  colors.bg,
                  colors.bg,
                  colors.surface.withValues(alpha: 0.92),
                ],
                stops: const [0, 0.58, 1],
              ),
            ),
            child: JoviaPageScaffold(
              child: ListView(
                padding: EdgeInsets.zero,
                children: [
                  JoviaProfileTopBar(
                    label: 'Anasayfa',
                    centerText: displayName,
                    reserveTrailingSpace: true,
                  ),
                  const SizedBox(height: 16),
                  _HomeOpeningHeroCard(
                    title: activeCard?.title.trim().isNotEmpty == true
                        ? activeCard!.title
                        : 'Bugunun acilisi',
                    body: heroBody,
                    prompt: activeCard?.subtitle.trim().isNotEmpty == true
                        ? activeCard!.subtitle
                        : 'Bugun bende ne aciliyor?',
                    onOpen: activeCard == null
                        ? () => _openTiming(context)
                        : () => _openPeriodDetails(context, activeCard),
                    footer: _HomeSignStateRow(
                      sunSign: _sunSign,
                      moonSign: _moonSign,
                      risingSign: _risingSign,
                    ),
                  ),
                  const SizedBox(height: 24),
                  _HomeEditorialLine(label: 'Gunun cizgisi', text: lineText),
                  const SizedBox(height: 24),
                  JoviaSectionHeader(
                    label: 'Daily update',
                    title: 'Bugun one cikan akislar',
                    variant: JoviaSectionHeaderVariant.editorial,
                  ),
                  const SizedBox(height: 10),
                  _HomeDailyUpdateStrip(
                    cards: dailyCards,
                    loading: _loading && dailyCards.isEmpty,
                    onOpen: (card) => _openPeriodDetails(context, card),
                  ),
                  const SizedBox(height: 24),
                  Padding(
                    padding: const EdgeInsets.only(right: 18),
                    child: JoviaSectionHeader(
                      label: 'Active theme',
                      title: activeCard?.title.trim().isNotEmpty == true
                          ? activeCard!.title
                          : 'Aktif tema bekleniyor',
                      body: activeCard?.subtitle.trim().isNotEmpty == true
                          ? activeCard!.subtitle
                          : 'Bugunun temasini period akisindan okuyacaksin.',
                      variant: JoviaSectionHeaderVariant.editorial,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Padding(
                    padding: const EdgeInsets.only(right: 14),
                    child: _HomeActiveThemeCard(
                      card: activeCard,
                      onOpen: activeCard == null
                          ? () => _openTiming(context)
                          : () => _openPeriodDetails(context, activeCard),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Padding(
                    padding: const EdgeInsets.only(left: 8),
                    child: JoviaSectionHeader(
                      label: 'Collective pulse',
                      title: 'Kolektif nabiz',
                      body: skyBulletin.summary,
                      variant: JoviaSectionHeaderVariant.editorial,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _HomeCollectivePulseCard(
                    bulletin: skyBulletin,
                    card: collectiveCard,
                    onOpenThread: () {
                      if (collectiveCard != null) {
                        _openPeriodDetails(context, collectiveCard);
                      } else {
                        _openTiming(context);
                      }
                    },
                    onOpenDetails: skyBulletin.highlights.isEmpty
                        ? null
                        : () => _openSkyDetails(context, skyBulletin),
                  ),
                  if (skyBulletin.highlights.length > 1) ...[
                    const SizedBox(height: 14),
                    _HomeCollectiveHighlightsRow(
                      items: skyBulletin.highlights.skip(1).take(2).toList(),
                    ),
                  ],
                  if (_periodCore != null) ...[
                    const SizedBox(height: 24),
                    Padding(
                      padding: const EdgeInsets.only(left: 18),
                      child: JoviaReadingPanel(
                        label: 'Timing',
                        title: _periodCore!.title.trim().isEmpty
                            ? 'Aktif period'
                            : _periodCore!.title,
                        body: _periodCore!.coreStory.trim().isEmpty
                            ? _periodCore!.bigPicture
                            : _periodCore!.coreStory,
                      ),
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
        client.post('/interpret/ui', data: natalPayload),
        _narrativeRepository.fetchDailyNarrative(
          profile: profile,
          selectedDate: DateTime.now(),
        ),
      ]);

      final interpretMap = _asMap((responses[0] as Response<dynamic>).data);
      final periodMap = TransitRequestBuilder.asMap(responses[1]);
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
        client.post('/interpret', data: natalPayload),
        _narrativeRepository.fetchDailyNarrative(
          profile: profile,
          selectedDate: DateTime.now(),
        ),
      ]);

      final interpretMap = _asMap((responses[0] as Response<dynamic>).data);
      final periodMap = TransitRequestBuilder.asMap(responses[1]);
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

  void _openSkyDetails(BuildContext context, _SkyBulletin bulletin) {
    final profile = context.profileTheme;
    final colors = profile.colors;
    final typo = profile.typography;
    if (bulletin.highlights.isEmpty) {
      return;
    }
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) {
        return Padding(
          padding: EdgeInsets.all(profile.spacing.lg),
          child: _GlassCard(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Gokyuzunde Ne Var?',
                  style: typo.h2.copyWith(color: colors.text),
                ),
                SizedBox(height: profile.spacing.sm),
                for (final item in bulletin.highlights) ...[
                  Text(
                    item.title,
                    style: typo.body.copyWith(
                      fontWeight: FontWeight.w600,
                      color: colors.text,
                    ),
                  ),
                  SizedBox(height: profile.spacing.xs),
                  Text(
                    item.blurb,
                    style: typo.body.copyWith(color: colors.muted),
                  ),
                  SizedBox(height: profile.spacing.sm),
                ],
              ],
            ),
          ),
        );
      },
    );
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
    return JoviaSurfaceCard(
      padding: const EdgeInsets.fromLTRB(22, 22, 22, 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Align(
            alignment: Alignment.topCenter,
            child: JoviaIllustrationAccent(
              asset: JoviaIllustrationAsset.planet,
              width: 84,
              height: 84,
              opacity: 0.92,
            ),
          ),
          const SizedBox(height: 18),
          Text(
            'BUGUNUN ACILISI',
            style: profile.typography.eyebrow.copyWith(
              color: profile.colors.textLight,
              letterSpacing: 1.7,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            title,
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.heroTitle.copyWith(
              color: profile.colors.text,
              fontSize: 30,
              height: 1.04,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            body,
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.body.copyWith(
              color: profile.colors.textLight,
              height: 1.45,
            ),
          ),
          const SizedBox(height: 18),
          JoviaSurfaceCard(
            padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
            color: profile.colors.surface.withValues(alpha: 0.72),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Bugunun acilis sorusu',
                        style: profile.typography.eyebrow.copyWith(
                          color: profile.colors.textLight,
                          letterSpacing: 1.2,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        prompt,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: profile.typography.body.copyWith(
                          color: profile.colors.text,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                MinimalCTAButton(label: 'Ac', emphasized: true, onTap: onOpen),
              ],
            ),
          ),
          const SizedBox(height: 16),
          footer,
        ],
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
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 22),
      child: Column(
        children: [
          Text(
            label.toUpperCase(),
            textAlign: TextAlign.center,
            style: profile.typography.eyebrow.copyWith(
              color: profile.colors.textLight,
              letterSpacing: 1.8,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            text,
            textAlign: TextAlign.center,
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.card.copyWith(
              color: profile.colors.text,
              fontSize: 24,
              height: 1.22,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
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
        height: 132,
        child: JoviaSurfaceCard(
          child: Align(
            alignment: Alignment.centerLeft,
            child: Text('Daily update strip su an bos.'),
          ),
        ),
      );
    }

    return SizedBox(
      height: 132,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: cards.length,
        separatorBuilder: (context, index) => const SizedBox(width: 12),
        itemBuilder: (context, index) {
          final card = cards[index];
          final meta = card.timeHint.trim().isNotEmpty
              ? card.timeHint.trim()
              : 'Timing';
          return SizedBox(
            width: 248,
            child: JoviaPressable(
              onTap: () => onOpen(card),
              borderRadius: BorderRadius.circular(20),
              child: JoviaSurfaceCard(
                padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      meta.toUpperCase(),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: context.profileTheme.typography.eyebrow.copyWith(
                        color: context.profileTheme.colors.textLight,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      card.title.isNotEmpty ? card.title : 'Aktif akis',
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: context.profileTheme.typography.cardTitle,
                    ),
                    const Spacer(),
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: [
                          JoviaMetaPill(
                            label: card.subtitle.trim().isNotEmpty
                                ? card.subtitle.trim()
                                : 'Detayi ac',
                          ),
                        ],
                      ),
                    ),
                  ],
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
    final title = card?.title.trim().isNotEmpty == true
        ? card!.title
        : 'Aktif tema bekleniyor';
    final body = card?.subtitle.trim().isNotEmpty == true
        ? card!.subtitle
        : 'Period akisindan gelen aktif tema burada kompakt kart olarak gorunecek.';
    final timeHint = card?.timeHint.trim() ?? '';

    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 430;
        final metaChips = <String>[
          if (timeHint.isNotEmpty) timeHint,
          if ((card?.eventCard?.signatureTr ?? '').trim().isNotEmpty)
            card!.eventCard!.signatureTr.trim(),
        ].take(compact ? 1 : 2).toList(growable: false);

        final cta = MinimalCTAButton(
          label: 'Temayi ac',
          emphasized: true,
          onTap: onOpen,
        );

        return JoviaSurfaceCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const JoviaIllustrationAccent(
                    asset: JoviaIllustrationAsset.planet,
                    width: 56,
                    height: 56,
                    opacity: 0.9,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      timeHint.isNotEmpty
                          ? timeHint.toUpperCase()
                          : 'SIMDI AKTIF',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: context.profileTheme.typography.eyebrow.copyWith(
                        color: context.profileTheme.colors.textLight,
                        letterSpacing: 1.6,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                title,
                maxLines: compact ? 2 : 3,
                overflow: TextOverflow.ellipsis,
                style: context.profileTheme.typography.card.copyWith(
                  color: context.profileTheme.colors.text,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                body,
                maxLines: compact ? 3 : 4,
                overflow: TextOverflow.ellipsis,
                style: context.profileTheme.typography.bodyCompact.copyWith(
                  color: context.profileTheme.colors.textLight,
                ),
              ),
              if (metaChips.isNotEmpty) ...[
                const SizedBox(height: 12),
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
              const SizedBox(height: 14),
              if (compact)
                Align(alignment: Alignment.centerLeft, child: cta)
              else
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        body,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: context.profileTheme.typography.micro.copyWith(
                          color: context.profileTheme.colors.textLight,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    cta,
                  ],
                ),
            ],
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
    required this.onOpenThread,
    this.onOpenDetails,
  });

  final _SkyBulletin bulletin;
  final PeriodCardDto? card;
  final VoidCallback onOpenThread;
  final VoidCallback? onOpenDetails;

  @override
  Widget build(BuildContext context) {
    final chips = bulletin.chips.take(2).toList(growable: false);
    final blurb = card == null ? bulletin.summary : _blurbFromCard(card!);
    final title = card?.title.trim().isNotEmpty == true
        ? card!.title
        : 'Acik konular';

    return JoviaSurfaceCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'KOLEKTIF KONU',
            style: context.profileTheme.typography.eyebrow.copyWith(
              color: context.profileTheme.colors.textLight,
              letterSpacing: 1.6,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            title,
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
            style: context.profileTheme.typography.heroTitle.copyWith(
              color: context.profileTheme.colors.text,
              fontSize: 28,
              height: 1.06,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            blurb,
            maxLines: 3,
            overflow: TextOverflow.ellipsis,
            style: context.profileTheme.typography.bodyCompact.copyWith(
              color: context.profileTheme.colors.textLight,
            ),
          ),
          if (chips.isNotEmpty) ...[
            const SizedBox(height: 12),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  for (var index = 0; index < chips.length; index++) ...[
                    JoviaMetaPill(label: chips[index]),
                    if (index != chips.length - 1) const SizedBox(width: 8),
                  ],
                ],
              ),
            ),
          ],
          if (onOpenDetails != null) ...[
            const SizedBox(height: 14),
            MinimalCTAButton(label: 'Notlar', onTap: onOpenDetails),
          ],
          const SizedBox(height: 16),
          JoviaPrimaryButton(label: "Thread'e gir", onTap: onOpenThread),
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
        color: profile.colors.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: profile.colors.strokeSoft, width: 1.5),
        boxShadow: [profile.shadows.cardShadow],
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
