import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/theme/app_theme_mode_provider.dart';
import 'package:mobile/app/timing/turkish_text.dart';
import 'package:mobile/design/astro/astro_theme_extension.dart';
import 'package:mobile/design/astro/astro_theme_generator.dart';
import 'package:mobile/design/astro/element_scores.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/l10n/current_localizations.dart';
import 'package:mobile/l10n/l10n.dart';

class ProfilePageV2Experiment extends ConsumerStatefulWidget {
  const ProfilePageV2Experiment({
    super.key,
    this.viewedUserId,
    this.profileOverride,
    this.readOnly = false,
  });

  final String? viewedUserId;
  final Map<String, dynamic>? profileOverride;
  final bool readOnly;

  @override
  ConsumerState<ProfilePageV2Experiment> createState() =>
      _ProfilePageV2ExperimentState();
}

class _ProfilePageV2ExperimentState
    extends ConsumerState<ProfilePageV2Experiment> {
  static const String _baseUrl = 'http://127.0.0.1:5000';

  final PageController _identityRailController = PageController(
    viewportFraction: 0.84,
  );
  _ProfileMode _mode = _ProfileMode.natal;
  String _sunSign = '—';
  String _moonSign = '—';
  String _risingSign = '—';
  String? _avatarUrl;
  String? _lastNatalKey;
  bool _isIdentityLoading = false;
  _IdentityContext? _identityContext;

  @override
  void dispose() {
    _identityRailController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final profileAsync = widget.profileOverride == null
        ? ref.watch(userProfileProvider)
        : const AsyncValue<Map<String, dynamic>?>.data(null);
    final uid = ref.watch(currentUserIdProvider);
    final currentUserEmail = Supabase.instance.client.auth.currentUser?.email;
    final authAvatarUrl = Supabase
        .instance
        .client
        .auth
        .currentUser
        ?.userMetadata?['avatar_url']
        ?.toString();
    final profile = widget.profileOverride ?? profileAsync.asData?.value;
    final elementScores = _computeElementScores(
      profile: profile,
      userId: widget.viewedUserId ?? uid,
      email: currentUserEmail,
    );
    final themed = withAstroTheme(
      withProfileTheme(Theme.of(context)),
      astroTheme: astroThemeFromElementScores(elementScores),
    );

    if (profile != null) {
      _avatarUrl = (profile['avatar_url'] ?? authAvatarUrl ?? '').toString();
      _maybeLoadIdentityPayload(profile);
    }

    return Theme(
      data: themed,
      child: Builder(
        builder: (context) {
          final displayName = _displayName(profile);
          final username = _displayUsername(
            profile: profile,
            email: currentUserEmail,
          );
          final dominantElementLabel = _dominantElementLabel(elementScores);
          final avatarUrl = (_avatarUrl ?? authAvatarUrl ?? '').trim();
          final profileTheme = context.profileTheme;

          return Scaffold(
            backgroundColor: const Color(0xFF080607),
            body: DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    const Color(0xFF130D0C),
                    const Color(0xFF080607),
                    profileTheme.colors.surface.withValues(alpha: 0.92),
                  ],
                ),
              ),
              child: Stack(
                children: [
                  const _NocturneBackdrop(),
                  JoviaPageScaffold(
                    padding: const EdgeInsets.fromLTRB(20, 18, 20, 28),
                    child: SingleChildScrollView(
                      physics: const BouncingScrollPhysics(),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          JoviaProfileTopBar(
                            label: l10n.profileExperimentPreviewLabel,
                            centerText: l10n.profileExperimentCenterText,
                            onBackTap: () => Navigator.of(context).maybePop(),
                            onActionTap: () => _showExperimentMenu(context),
                            actionAsset: JoviaUiAsset.menuStack,
                            actionTooltip: l10n.profileExperimentMenuTooltip,
                          ),
                          const SizedBox(height: 14),
                          _NocturneIdentityHero(
                            displayName: displayName,
                            username: username,
                            avatarUrl: avatarUrl.isEmpty ? null : avatarUrl,
                            signatureLine:
                                _identityContext?.overview ??
                                l10n.profileExperimentHeroFallback,
                            sunSign: _sunSign,
                            moonSign: _moonSign,
                            risingSign: _risingSign,
                            isLoading: _isIdentityLoading,
                            readOnly: widget.readOnly,
                            onBackTap: () => Navigator.of(context).maybePop(),
                            onMenuTap: () => _showExperimentMenu(context),
                          ),
                          const SizedBox(height: 22),
                          _NocturneIdentityRow(
                            controller: _identityRailController,
                            auraLine: _identityContext?.auraLine ?? '',
                            auraSourceLabel:
                                _identityContext?.auraSourceLabel ?? '',
                            rulerName: _identityContext?.rulerName ?? '',
                            rulerHouse: _identityContext?.rulerHouse,
                            dominantElementLabel: dominantElementLabel,
                            signatureLabel:
                                _identityContext?.summaryLabel ??
                                l10n.profileExperimentSignatureFallback,
                            sunSign: _sunSign,
                            moonSign: _moonSign,
                            risingSign: _risingSign,
                          ),
                          const SizedBox(height: 20),
                          _NocturneModeSurface(
                            mode: _mode,
                            onChanged: (value) => setState(() => _mode = value),
                          ),
                          const SizedBox(height: 18),
                          JoviaSurfaceCard(
                            radius: 28,
                            backgroundColor: profileTheme.colors.surface
                                .withValues(alpha: 0.58),
                            borderColor: profileTheme.colors.strokeSoft
                                .withValues(alpha: 0.68),
                            child: Text(
                              _mode == _ProfileMode.natal
                                  ? l10n.profileExperimentNatalPanelBody
                                  : l10n.profileExperimentTimingPanelBody,
                              style: profileTheme.typography.body.copyWith(
                                color: profileTheme.colors.textLight,
                                height: 1.5,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Future<void> _showExperimentMenu(BuildContext context) async {
    final l10n = context.l10n;
    final profile = context.profileTheme;
    final currentMode = ref.read(joviaThemeModeProvider);
    await showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        return Padding(
          padding: EdgeInsets.fromLTRB(
            profile.spacing.lg,
            profile.spacing.lg,
            profile.spacing.lg,
            profile.spacing.lg,
          ),
          child: JoviaSurfaceCard(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.profileExperimentMenuTitle,
                  style: profile.typography.card.copyWith(
                    color: profile.colors.text,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  l10n.profileExperimentMenuBody,
                  style: profile.typography.body.copyWith(
                    color: profile.colors.textLight,
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  l10n.menuThemeMode,
                  style: profile.typography.eyebrow.copyWith(
                    color: profile.colors.textLight,
                    letterSpacing: 1.4,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: MinimalCTAButton(
                        label: l10n.themeModeDark,
                        emphasized: currentMode == JoviaThemeMode.dark,
                        onTap: () {
                          ref
                              .read(joviaThemeModeProvider.notifier)
                              .setMode(JoviaThemeMode.dark);
                          Navigator.of(sheetContext).pop();
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: MinimalCTAButton(
                        label: l10n.themeModeLight,
                        emphasized: currentMode == JoviaThemeMode.light,
                        onTap: () {
                          ref
                              .read(joviaThemeModeProvider.notifier)
                              .setMode(JoviaThemeMode.light);
                          Navigator.of(sheetContext).pop();
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _maybeLoadIdentityPayload(Map<String, dynamic> profile) {
    if (!_hasBirthData(profile)) {
      return;
    }
    final city = (profile['city'] ?? '').toString().trim();
    final country = (profile['country'] ?? '').toString().trim();
    final placeRaw = (profile['place'] ?? '').toString().trim();
    final place = placeRaw.isNotEmpty
        ? placeRaw
        : (city.isEmpty
              ? country
              : (country.isEmpty ? city : '$city, $country'));
    final key =
        '${profile['birth_date']}|${profile['birth_time']}|$place|${profile['timezone'] ?? ''}';
    if (_lastNatalKey == key) {
      return;
    }
    _lastNatalKey = key;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) {
        return;
      }
      _loadIdentityPayload(profile);
    });
  }

  Future<void> _loadIdentityPayload(Map<String, dynamic> profile) async {
    final city = (profile['city'] ?? '').toString().trim();
    final country = (profile['country'] ?? '').toString().trim();
    final placeRaw = (profile['place'] ?? '').toString().trim();
    final place = placeRaw.isNotEmpty
        ? placeRaw
        : (city.isEmpty
              ? country
              : (country.isEmpty ? city : '$city, $country'));
    final payload = <String, dynamic>{
      'birth_date': (profile['birth_date'] ?? '').toString().trim(),
      'birth_time': _normalizeBirthTime(
        (profile['birth_time'] ?? '').toString(),
      ),
      'birth_place': place,
      'locale': Localizations.localeOf(context).languageCode,
    };

    setState(() => _isIdentityLoading = true);

    try {
      final client = ApiClient(baseUrl: _baseUrl);
      final response = await client.post('/interpret', data: payload);
      final map = _asMap(response.data);
      final blocks = _extractProfileNarrativeCards(map, field: 'blocks');
      final coreBlocks = _extractProfileNarrativeCards(
        map,
        field: 'core_blocks',
      );
      final extraBlocks = _extractProfileNarrativeCards(
        map,
        field: 'extra_blocks',
      );
      final identityContext = _buildIdentityContext(
        map: map,
        blocks: blocks,
        coreBlocks: coreBlocks,
        extraBlocks: extraBlocks,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _identityContext = identityContext;
        _sunSign = _toTrSign(_extractPlanetSign(map, 'Sun'));
        _moonSign = _toTrSign(_extractPlanetSign(map, 'Moon'));
        _risingSign = _toTrSign(_extractRisingSign(map));
        _isIdentityLoading = false;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() => _isIdentityLoading = false);
    }
  }

  ElementScores _computeElementScores({
    required Map<String, dynamic>? profile,
    required String? userId,
    required String? email,
  }) {
    final fromProfile = _extractElementScoresFromProfile(profile);
    if (fromProfile != null) {
      return fromProfile;
    }

    final fromSigns = _extractElementScoresFromKnownSigns();
    if (fromSigns != null) {
      return fromSigns;
    }

    return _deterministicElementScores(seed: userId ?? email ?? 'anon');
  }

  ElementScores? _extractElementScoresFromProfile(
    Map<String, dynamic>? profile,
  ) {
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
    final keys = map.keys.map((key) => key.toLowerCase()).toSet();
    if (!keys.contains('fire') ||
        !keys.contains('water') ||
        !keys.contains('air') ||
        !keys.contains('earth')) {
      return null;
    }
    return ElementScores.fromMap(map);
  }

  ElementScores? _extractElementScoresFromKnownSigns() {
    final weights = <AstroElement, double>{
      AstroElement.fire: 0,
      AstroElement.water: 0,
      AstroElement.air: 0,
      AstroElement.earth: 0,
    };

    void addSign(String sign, double weight) {
      final element = _elementFromSign(sign);
      if (element == null) {
        return;
      }
      weights[element] = (weights[element] ?? 0) + weight;
    }

    addSign(_sunSign, 0.4);
    addSign(_moonSign, 0.35);
    addSign(_risingSign, 0.25);
    if (weights.values.every((value) => value == 0)) {
      return null;
    }
    return ElementScores(
      fire: weights[AstroElement.fire] ?? 0,
      water: weights[AstroElement.water] ?? 0,
      air: weights[AstroElement.air] ?? 0,
      earth: weights[AstroElement.earth] ?? 0,
    ).normalize();
  }

  AstroElement? _elementFromSign(String rawSign) {
    final sign = rawSign.trim().toLowerCase();
    if (sign.isEmpty || sign == '—') {
      return null;
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
    if (fire.contains(sign)) {
      return AstroElement.fire;
    }
    if (water.contains(sign)) {
      return AstroElement.water;
    }
    if (air.contains(sign)) {
      return AstroElement.air;
    }
    if (earth.contains(sign)) {
      return AstroElement.earth;
    }
    return null;
  }

  ElementScores _deterministicElementScores({required String seed}) {
    final hash = seed.codeUnits.fold<int>(
      17,
      (acc, value) => (acc * 31 + value) & 0x7fffffff,
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

  String _dominantElementLabel(ElementScores scores) {
    return switch (scores.dominant) {
      AstroElement.fire => currentL10n().profileExperimentFireDominant,
      AstroElement.water => currentL10n().profileExperimentWaterDominant,
      AstroElement.air => currentL10n().profileExperimentAirDominant,
      AstroElement.earth => currentL10n().profileExperimentEarthDominant,
    };
  }

  String _displayName(Map<String, dynamic>? profile) {
    final fromProfile = (profile?['full_name'] ?? profile?['name'] ?? '')
        .toString()
        .trim();
    if (fromProfile.isNotEmpty) {
      return fromProfile;
    }
    return currentL10n().profileExperimentUnnamedProfile;
  }

  String _displayUsername({
    required Map<String, dynamic>? profile,
    required String? email,
  }) {
    final raw = (profile?['username'] ?? profile?['handle'] ?? '')
        .toString()
        .trim();
    if (raw.isNotEmpty) {
      return raw.startsWith('@') ? raw : '@$raw';
    }
    final mailPart = (email ?? '').split('@').first.trim();
    if (mailPart.isNotEmpty) {
      return '@${mailPart.toLowerCase()}';
    }
    final fallback = _displayName(
      profile,
    ).toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), '');
    return fallback.isEmpty ? '@profile' : '@$fallback';
  }

  bool _hasBirthData(Map<String, dynamic>? profile) {
    if (profile == null) {
      return false;
    }
    final birthDate = (profile['birth_date'] ?? '').toString().trim();
    final birthTime = (profile['birth_time'] ?? '').toString().trim();
    final city = (profile['city'] ?? '').toString().trim();
    final country = (profile['country'] ?? '').toString().trim();
    final placeRaw = (profile['place'] ?? '').toString().trim();
    final place = placeRaw.isNotEmpty
        ? placeRaw
        : (city.isEmpty
              ? country
              : (country.isEmpty ? city : '$city, $country'));
    return birthDate.isNotEmpty && birthTime.isNotEmpty && place.isNotEmpty;
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

  Map<String, dynamic> _asMap(dynamic value) {
    if (value is Map<String, dynamic>) {
      return value;
    }
    if (value is Map) {
      return value.map((key, item) => MapEntry(key.toString(), item));
    }
    return const {};
  }

  Map<String, dynamic> _extractPublicField(
    Map<String, dynamic> map,
    String field,
  ) {
    final direct = _asMap(map['public']);
    if (direct[field] is Map) {
      return _asMap(direct[field]);
    }
    final narrative = _asMap(direct['profile_narrative']);
    final profilePublic = _asMap(narrative['profile_public']);
    if (profilePublic[field] is Map) {
      return _asMap(profilePublic[field]);
    }
    return const {};
  }

  List<_NarrativeCard> _extractProfileNarrativeCards(
    Map<String, dynamic> map, {
    required String field,
  }) {
    final public = _asMap(map['public']);
    final narrative = _asMap(public['profile_narrative']);
    final profilePublic = _asMap(narrative['profile_public']);
    final raw = profilePublic[field];
    if (raw is! List) {
      return const [];
    }
    return raw
        .whereType<Map>()
        .map((item) => _NarrativeCard.fromMap(Map<String, dynamic>.from(item)))
        .where((item) => item.previewBody.isNotEmpty)
        .toList();
  }

  _IdentityContext _buildIdentityContext({
    required Map<String, dynamic> map,
    required List<_NarrativeCard> blocks,
    required List<_NarrativeCard> coreBlocks,
    required List<_NarrativeCard> extraBlocks,
  }) {
    final leadCard = _pickLeadIdentityCard([
      ...coreBlocks,
      ...extraBlocks,
      if (coreBlocks.isEmpty && extraBlocks.isEmpty) ...blocks,
    ]);
    final personalityImprint = _extractPublicField(map, 'personality_imprint');
    final auraLead = _extractAuraLead(personalityImprint);
    final natalGraphCompact = _extractPublicField(map, 'natal_graph_compact');
    final rulerInfo = _extractAscRulerInfo(natalGraphCompact);
    return _IdentityContext(
      overview: leadCard?.previewBody ?? '',
      summaryLabel: leadCard?.eyebrow ?? '',
      auraLine: auraLead?.aura ?? '',
      auraSourceLabel: auraLead?.label ?? '',
      rulerName: rulerInfo == null ? '' : _planetLabelTr(rulerInfo.planet),
      rulerHouse: rulerInfo?.house,
    );
  }

  _NarrativeCard? _pickLeadIdentityCard(List<_NarrativeCard> cards) {
    const preferredFamilies = <String>{
      'self_definition',
      'outer_inner_split',
      'identity',
    };
    for (final card in cards) {
      if (card.id == 'identity_aura') {
        return card;
      }
    }
    for (final card in cards) {
      if (preferredFamilies.contains(card.family)) {
        return card;
      }
    }
    return cards.isEmpty ? null : cards.first;
  }

  _AuraLead? _extractAuraLead(Map<String, dynamic> personalityImprint) {
    for (final field in const <String>[
      'entries',
      'support_entries',
      'extra_entries',
    ]) {
      final raw = personalityImprint[field];
      if (raw is! List) {
        continue;
      }
      for (final item in raw.whereType<Map>()) {
        final mapItem = Map<String, dynamic>.from(item);
        final aura = (mapItem['aura'] ?? '').toString().trim();
        final label = (mapItem['label_tr'] ?? '').toString().trim();
        if (aura.isNotEmpty || label.isNotEmpty) {
          return _AuraLead(label: label, aura: aura);
        }
      }
    }
    return null;
  }

  _AscRulerInfo? _extractAscRulerInfo(Map<String, dynamic> graph) {
    final houseRulers = _asMap(graph['house_rulers']);
    final houseOne = _asMap(houseRulers['1']);
    final ruler = (houseOne['primary_ruler'] ?? '').toString().trim();
    if (ruler.isEmpty) {
      return null;
    }
    final house = houseOne['primary_house'] is int
        ? houseOne['primary_house'] as int
        : int.tryParse((houseOne['primary_house'] ?? '').toString());
    return _AscRulerInfo(planet: ruler, house: house);
  }

  String _planetLabelTr(String raw) {
    final labels = isCurrentLocaleTurkish()
        ? const <String, String>{
            'sun': 'Güneş',
            'moon': 'Ay',
            'mercury': 'Merkür',
            'venus': 'Venüs',
            'mars': 'Mars',
            'jupiter': 'Jüpiter',
            'saturn': 'Satürn',
            'uranus': 'Uranüs',
            'neptune': 'Neptün',
            'pluto': 'Plüton',
          }
        : const <String, String>{
            'sun': 'Sun',
            'moon': 'Moon',
            'mercury': 'Mercury',
            'venus': 'Venus',
            'mars': 'Mars',
            'jupiter': 'Jupiter',
            'saturn': 'Saturn',
            'uranus': 'Uranus',
            'neptune': 'Neptune',
            'pluto': 'Pluto',
          };
    final key = raw.trim().toLowerCase();
    return labels[key] ?? (raw.trim().isEmpty ? '—' : raw.trim());
  }

  String _extractPlanetSign(Map<String, dynamic> map, String planetName) {
    for (final scope in <Map<String, dynamic>>[_asMap(map['public']), map]) {
      final planets = scope['planets'];
      if (planets is List) {
        for (final entry in planets.whereType<Map>()) {
          final normalized = Map<String, dynamic>.from(entry);
          final name = (normalized['name'] ?? normalized['planet'] ?? '')
              .toString()
              .trim()
              .toLowerCase();
          if (name == planetName.toLowerCase()) {
            final sign = (normalized['sign'] ?? normalized['sign_name'] ?? '')
                .toString()
                .trim();
            if (sign.isNotEmpty) {
              return sign;
            }
          }
        }
      }

      final signMap = scope['planet_signs'] ?? scope['signs'];
      if (signMap is Map) {
        final sign =
            (signMap[planetName] ??
                    signMap[planetName.toLowerCase()] ??
                    signMap[planetName.toUpperCase()] ??
                    '')
                .toString()
                .trim();
        if (sign.isNotEmpty) {
          return sign;
        }
      }
    }
    return '';
  }

  String _extractRisingSign(Map<String, dynamic> map) {
    for (final scope in <Map<String, dynamic>>[_asMap(map['public']), map]) {
      final angles = scope['angles'];
      if (angles is Map) {
        final sign = (angles['ascendant_sign'] ?? angles['asc_sign'] ?? '')
            .toString()
            .trim();
        if (sign.isNotEmpty) {
          return sign;
        }
      }
      final metaInfo = scope['meta_info'];
      if (metaInfo is Map) {
        final sign =
            (metaInfo['rising_sign'] ?? metaInfo['ascendant_sign'] ?? '')
                .toString()
                .trim();
        if (sign.isNotEmpty) {
          return sign;
        }
      }
    }
    return '';
  }

  String _toTrSign(String raw) {
    final signs = isCurrentLocaleTurkish()
        ? const <String, String>{
            'aries': 'Koç',
            'taurus': 'Boğa',
            'gemini': 'İkizler',
            'cancer': 'Yengeç',
            'leo': 'Aslan',
            'virgo': 'Başak',
            'libra': 'Terazi',
            'scorpio': 'Akrep',
            'sagittarius': 'Yay',
            'capricorn': 'Oğlak',
            'aquarius': 'Kova',
            'pisces': 'Balık',
            'koç': 'Koç',
            'koc': 'Koç',
            'boğa': 'Boğa',
            'boga': 'Boğa',
            'yengeç': 'Yengeç',
            'yengec': 'Yengeç',
            'başak': 'Başak',
            'basak': 'Başak',
            'oğlak': 'Oğlak',
            'oglak': 'Oğlak',
            'balık': 'Balık',
            'balik': 'Balık',
          }
        : const <String, String>{
            'aries': 'Aries',
            'taurus': 'Taurus',
            'gemini': 'Gemini',
            'cancer': 'Cancer',
            'leo': 'Leo',
            'virgo': 'Virgo',
            'libra': 'Libra',
            'scorpio': 'Scorpio',
            'sagittarius': 'Sagittarius',
            'capricorn': 'Capricorn',
            'aquarius': 'Aquarius',
            'pisces': 'Pisces',
            'koç': 'Aries',
            'koc': 'Aries',
            'boğa': 'Taurus',
            'boga': 'Taurus',
            'yengeç': 'Cancer',
            'yengec': 'Cancer',
            'başak': 'Virgo',
            'basak': 'Virgo',
            'oğlak': 'Capricorn',
            'oglak': 'Capricorn',
            'balık': 'Pisces',
            'balik': 'Pisces',
          };
    final key = raw.trim().toLowerCase();
    return signs[key] ?? (raw.trim().isEmpty ? '—' : raw.trim());
  }
}

enum _ProfileMode { natal, timing }

class _NocturneBackdrop extends StatelessWidget {
  const _NocturneBackdrop();

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Stack(
        children: [
          Positioned(
            top: -70,
            right: -50,
            child: _GlowOrb(
              size: 220,
              colors: const [Color(0x66E1C3AC), Color(0x00E1C3AC)],
            ),
          ),
          Positioned(
            top: 200,
            left: -80,
            child: _GlowOrb(
              size: 200,
              colors: const [Color(0x33D89252), Color(0x00D89252)],
            ),
          ),
          Positioned(
            top: 110,
            left: 24,
            right: 24,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(38),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 16, sigmaY: 16),
                child: Container(
                  height: 260,
                  color: Colors.white.withValues(alpha: 0.015),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _GlowOrb extends StatelessWidget {
  const _GlowOrb({required this.size, required this.colors});

  final double size;
  final List<Color> colors;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: RadialGradient(colors: colors),
      ),
    );
  }
}

class _NocturneIdentityHero extends StatelessWidget {
  const _NocturneIdentityHero({
    required this.displayName,
    required this.username,
    required this.avatarUrl,
    required this.signatureLine,
    required this.sunSign,
    required this.moonSign,
    required this.risingSign,
    required this.isLoading,
    required this.readOnly,
    required this.onBackTap,
    required this.onMenuTap,
  });

  final String displayName;
  final String username;
  final String? avatarUrl;
  final String signatureLine;
  final String sunSign;
  final String moonSign;
  final String risingSign;
  final bool isLoading;
  final bool readOnly;
  final VoidCallback onBackTap;
  final VoidCallback onMenuTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final l10n = context.l10n;
    return Container(
      height: 620,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(38),
        border: Border.all(
          color: profile.colors.strokeSoft.withValues(alpha: 0.72),
          width: 1.2,
        ),
        boxShadow: [profile.shadows.cardShadow],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(38),
        child: Stack(
          fit: StackFit.expand,
          children: [
            _PortraitBackdrop(imageUrl: avatarUrl),
            DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withValues(alpha: 0.12),
                    Colors.black.withValues(alpha: 0.18),
                    Colors.black.withValues(alpha: 0.78),
                    Colors.black.withValues(alpha: 0.94),
                  ],
                  stops: const [0, 0.28, 0.72, 1],
                ),
              ),
            ),
            Positioned(
              top: 18,
              left: 18,
              right: 18,
              child: Row(
                children: [
                  _FloatingIconButton(
                    icon: JoviaUiAsset.back,
                    onTap: onBackTap,
                  ),
                  const Spacer(),
                  _FloatingPill(
                    label: readOnly
                        ? l10n.profileExperimentPreviewLabel
                        : l10n.menuEditProfile,
                    onTap: onMenuTap,
                  ),
                ],
              ),
            ),
            Positioned(
              left: 18,
              right: 18,
              bottom: 18,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(30),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 22, sigmaY: 22),
                  child: JoviaSurfaceCard(
                    radius: 30,
                    padding: const EdgeInsets.fromLTRB(20, 20, 20, 20),
                    backgroundColor: Colors.black.withValues(alpha: 0.46),
                    borderColor: Colors.white.withValues(alpha: 0.12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    displayName,
                                    style: profile.typography.hero.copyWith(
                                      color: Colors.white,
                                      height: 0.96,
                                      fontSize:
                                          profile.typography.hero.fontSize! + 6,
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    username,
                                    style: profile.typography.body.copyWith(
                                      color: Colors.white.withValues(
                                        alpha: 0.72,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 12),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text(
                                  l10n.profileExperimentSeeProfile,
                                  style: profile.typography.micro.copyWith(
                                    color: Colors.white.withValues(alpha: 0.84),
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                const SizedBox(height: 18),
                                Row(
                                  children: const [
                                    _IconBubble(icon: JoviaUiAsset.orbitPlanet),
                                    SizedBox(width: 8),
                                    _IconBubble(icon: JoviaUiAsset.chatOrbit),
                                  ],
                                ),
                              ],
                            ),
                          ],
                        ),
                        const SizedBox(height: 14),
                        AnimatedOpacity(
                          duration: const Duration(milliseconds: 180),
                          opacity: isLoading ? 0.65 : 1,
                          child: Text(
                            signatureLine.trim().isEmpty
                                ? l10n.profileExperimentHeroLineFallback
                                : signatureLine.trim(),
                            style: profile.typography.body.copyWith(
                              color: Colors.white.withValues(alpha: 0.82),
                              height: 1.4,
                            ),
                            maxLines: 3,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(height: 18),
                        Row(
                          children: [
                            Expanded(
                              child: _MetricColumn(
                                value: sunSign,
                                label: l10n.profileSunLabel,
                              ),
                            ),
                            Expanded(
                              child: _MetricColumn(
                                value: moonSign,
                                label: l10n.profileMoonLabel,
                              ),
                            ),
                            Expanded(
                              child: _MetricColumn(
                                value: risingSign,
                                label: l10n.profileRisingLabel,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 18),
                        _GradientActionBar(
                          label: l10n.profileOpenIdentityReading,
                          onTap: onMenuTap,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PortraitBackdrop extends StatelessWidget {
  const _PortraitBackdrop({required this.imageUrl});

  final String? imageUrl;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    if (imageUrl != null && imageUrl!.trim().isNotEmpty) {
      return ColorFiltered(
        colorFilter: const ColorFilter.matrix([
          0.2126,
          0.7152,
          0.0722,
          0,
          0,
          0.2126,
          0.7152,
          0.0722,
          0,
          0,
          0.2126,
          0.7152,
          0.0722,
          0,
          0,
          0,
          0,
          0,
          1,
          0,
        ]),
        child: Image.network(
          imageUrl!,
          fit: BoxFit.cover,
          errorBuilder: (_, _, _) => _PortraitFallback(profile: profile),
        ),
      );
    }
    return _PortraitFallback(profile: profile);
  }
}

class _PortraitFallback extends StatelessWidget {
  const _PortraitFallback({required this.profile});

  final ProfileTheme profile;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Colors.white.withValues(alpha: 0.96),
            const Color(0xFFBEB6B2),
            const Color(0xFF191415),
          ],
        ),
      ),
      child: Stack(
        fit: StackFit.expand,
        children: [
          Positioned(
            top: 52,
            left: 20,
            child: Text(
              'JOVIA',
              style: profile.typography.hero.copyWith(
                color: Colors.black.withValues(alpha: 0.04),
                fontSize: 74,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          Positioned(
            top: 120,
            right: -30,
            child: Container(
              width: 280,
              height: 360,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(180),
                gradient: RadialGradient(
                  colors: [
                    Colors.black.withValues(alpha: 0.18),
                    Colors.black.withValues(alpha: 0.0),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FloatingIconButton extends StatelessWidget {
  const _FloatingIconButton({required this.icon, required this.onTap});

  final JoviaUiAsset icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(18),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
        child: Material(
          color: Colors.black.withValues(alpha: 0.38),
          child: InkWell(
            onTap: onTap,
            child: SizedBox(
              width: 52,
              height: 52,
              child: Center(
                child: JoviaUiIcon(asset: icon, size: 20, color: Colors.white),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _FloatingPill extends StatelessWidget {
  const _FloatingPill({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return ClipRRect(
      borderRadius: BorderRadius.circular(999),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
        child: Material(
          color: Colors.black.withValues(alpha: 0.44),
          child: InkWell(
            onTap: onTap,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              child: Text(
                label,
                style: profile.typography.micro.copyWith(
                  color: Colors.white,
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

class _IconBubble extends StatelessWidget {
  const _IconBubble({required this.icon});

  final JoviaUiAsset icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 38,
      height: 38,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: Colors.white.withValues(alpha: 0.12),
        border: Border.all(color: Colors.white.withValues(alpha: 0.18)),
      ),
      child: Center(
        child: JoviaUiIcon(asset: icon, size: 16, color: Colors.white),
      ),
    );
  }
}

class _MetricColumn extends StatelessWidget {
  const _MetricColumn({required this.value, required this.label});

  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: profile.typography.card.copyWith(
            color: Colors.white,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: 3),
        Text(
          label,
          style: profile.typography.micro.copyWith(
            color: Colors.white.withValues(alpha: 0.7),
          ),
        ),
      ],
    );
  }
}

class _GradientActionBar extends StatelessWidget {
  const _GradientActionBar({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(999),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(999),
            gradient: const LinearGradient(
              colors: [Color(0xFF71D4FF), Color(0xFFF6BC67), Color(0xFFF46E97)],
            ),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: profile.typography.body.copyWith(
              color: const Color(0xFF1B1718),
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
      ),
    );
  }
}

class _NocturneIdentityRow extends StatelessWidget {
  const _NocturneIdentityRow({
    required this.controller,
    required this.auraLine,
    required this.auraSourceLabel,
    required this.rulerName,
    required this.rulerHouse,
    required this.dominantElementLabel,
    required this.signatureLabel,
    required this.sunSign,
    required this.moonSign,
    required this.risingSign,
  });

  final PageController controller;
  final String auraLine;
  final String auraSourceLabel;
  final String rulerName;
  final int? rulerHouse;
  final String dominantElementLabel;
  final String signatureLabel;
  final String sunSign;
  final String moonSign;
  final String risingSign;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final cards = <_NocturneRailCardData>[
      _NocturneRailCardData(
        label: l10n.profileExperimentAuraLabel,
        title: auraSourceLabel.isEmpty
            ? l10n.profileExperimentSignatureFallback
            : auraSourceLabel,
        body: auraLine.isEmpty ? dominantElementLabel : auraLine,
        chips: [dominantElementLabel, signatureLabel],
        gradient: const [Color(0xFFE1BEA6), Color(0xFF6C473A)],
      ),
      _NocturneRailCardData(
        label: l10n.profileExperimentRulerLabel,
        title: rulerName.isEmpty ? l10n.profileExperimentWaiting : rulerName,
        body: rulerHouse == null
            ? l10n.profileExperimentRulerBodyFallback
            : l10n.profileHouseEmphasis(rulerHouse!),
        chips: [
          if (rulerHouse != null) l10n.profileHouseEmphasis(rulerHouse!),
          l10n.profileExperimentRisingTrace,
        ],
        gradient: const [Color(0xFFB9B4D9), Color(0xFF473C5B)],
      ),
      _NocturneRailCardData(
        label: l10n.profileExperimentSignatureLabel,
        title: dominantElementLabel,
        body: signatureLabel,
        chips: [sunSign, moonSign, risingSign],
        gradient: const [Color(0xFFD79A59), Color(0xFF513320)],
      ),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Builder(
          builder: (context) {
            final profile = context.profileTheme;
            return Row(
              children: [
                Expanded(
                  child: Text(
                    l10n.profileExperimentSpotlightCards,
                    style: profile.typography.eyebrow.copyWith(
                      color: profile.colors.textLight,
                      letterSpacing: 1.8,
                    ),
                  ),
                ),
                Text(
                  l10n.profileExperimentSwipe,
                  style: profile.typography.micro.copyWith(
                    color: profile.colors.textLight.withValues(alpha: 0.8),
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            );
          },
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 236,
          child: PageView.builder(
            controller: controller,
            itemCount: cards.length,
            physics: const BouncingScrollPhysics(),
            itemBuilder: (context, index) {
              final card = cards[index];
              return AnimatedBuilder(
                animation: controller,
                builder: (context, child) {
                  double page = 0;
                  if (controller.hasClients) {
                    page = controller.page ?? controller.initialPage.toDouble();
                  }
                  final distance = (page - index).abs().clamp(0.0, 1.2);
                  final scale = 1 - (distance * 0.08);
                  final opacity = 1 - (distance * 0.18);
                  final translate = distance * 18;
                  return Transform.translate(
                    offset: Offset(distance * 8, translate),
                    child: Transform.scale(
                      scale: scale,
                      alignment: Alignment.topCenter,
                      child: Opacity(
                        opacity: opacity,
                        child: Padding(
                          padding: const EdgeInsets.only(right: 12),
                          child: _IdentitySpotlightCard(data: card),
                        ),
                      ),
                    ),
                  );
                },
              );
            },
          ),
        ),
        const SizedBox(height: 12),
        Center(
          child: AnimatedBuilder(
            animation: controller,
            builder: (context, _) {
              final profile = context.profileTheme;
              final page = controller.hasClients
                  ? (controller.page ?? controller.initialPage.toDouble())
                  : 0.0;
              return Row(
                mainAxisSize: MainAxisSize.min,
                children: List.generate(cards.length, (index) {
                  final activeDistance = (page - index).abs().clamp(0.0, 1.0);
                  final active = 1 - activeDistance;
                  return AnimatedContainer(
                    duration: const Duration(milliseconds: 220),
                    width: lerpDouble(10, 30, active)!,
                    height: 6,
                    margin: const EdgeInsets.symmetric(horizontal: 4),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(999),
                      color: Color.lerp(
                        profile.colors.textLight.withValues(alpha: 0.22),
                        profile.colors.primary.withValues(alpha: 0.92),
                        active,
                      ),
                    ),
                  );
                }),
              );
            },
          ),
        ),
      ],
    );
  }
}

class _IdentitySpotlightCard extends StatelessWidget {
  const _IdentitySpotlightCard({required this.data});

  final _NocturneRailCardData data;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return ClipRRect(
      borderRadius: BorderRadius.circular(30),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 16, sigmaY: 16),
        child: Container(
          padding: const EdgeInsets.all(1.1),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(30),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white.withValues(alpha: 0.22),
                Colors.white.withValues(alpha: 0.06),
              ],
            ),
          ),
          child: DecoratedBox(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(29),
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  data.gradient.first.withValues(alpha: 0.26),
                  profile.colors.surface.withValues(alpha: 0.92),
                  data.gradient.last.withValues(alpha: 0.3),
                ],
              ),
            ),
            child: Stack(
              children: [
                Positioned(
                  top: -18,
                  right: -18,
                  child: Container(
                    width: 110,
                    height: 110,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: RadialGradient(
                        colors: [
                          data.gradient.first.withValues(alpha: 0.34),
                          data.gradient.last.withValues(alpha: 0.02),
                        ],
                      ),
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 18, 18, 18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        turkishToUpper(data.label),
                        style: profile.typography.eyebrow.copyWith(
                          color: profile.colors.textLight,
                          letterSpacing: 1.6,
                        ),
                      ),
                      const Spacer(),
                      Text(
                        data.title,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: profile.typography.card.copyWith(
                          color: profile.colors.text,
                          fontWeight: FontWeight.w700,
                          height: 1.06,
                          fontSize: profile.typography.card.fontSize! + 4,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        data.body,
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                        style: profile.typography.body.copyWith(
                          color: profile.colors.textLight,
                          height: 1.38,
                        ),
                      ),
                      const SizedBox(height: 14),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: data.chips
                            .where((item) => item.trim().isNotEmpty)
                            .take(3)
                            .map(
                              (item) => Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 8,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.white.withValues(alpha: 0.05),
                                  borderRadius: BorderRadius.circular(999),
                                  border: Border.all(
                                    color: Colors.white.withValues(alpha: 0.09),
                                  ),
                                ),
                                child: Text(
                                  item,
                                  style: profile.typography.micro.copyWith(
                                    color: profile.colors.text,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                              ),
                            )
                            .toList(),
                      ),
                    ],
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

class _NocturneRailCardData {
  const _NocturneRailCardData({
    required this.label,
    required this.title,
    required this.body,
    required this.chips,
    required this.gradient,
  });

  final String label;
  final String title;
  final String body;
  final List<String> chips;
  final List<Color> gradient;
}

class _NocturneModeSurface extends StatelessWidget {
  const _NocturneModeSurface({required this.mode, required this.onChanged});

  final _ProfileMode mode;
  final ValueChanged<_ProfileMode> onChanged;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final profile = context.profileTheme;
    return JoviaSurfaceCard(
      radius: 28,
      backgroundColor: profile.colors.surface.withValues(alpha: 0.74),
      borderColor: profile.colors.strokeSoft.withValues(alpha: 0.72),
      padding: const EdgeInsets.all(8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l10n.profileExperimentFocusTitle,
            style: profile.typography.eyebrow.copyWith(
              color: profile.colors.textLight,
              letterSpacing: 1.4,
            ),
          ),
          const SizedBox(height: 12),
          JoviaSegmentedControl<_ProfileMode>(
            value: mode,
            options: const [_ProfileMode.natal, _ProfileMode.timing],
            labelBuilder: (value) => value == _ProfileMode.natal
                ? l10n.profileExperimentNatalFocus
                : l10n.profileExperimentTimingFocus,
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }
}

class _IdentityContext {
  const _IdentityContext({
    required this.overview,
    required this.summaryLabel,
    required this.auraLine,
    required this.auraSourceLabel,
    required this.rulerName,
    required this.rulerHouse,
  });

  final String overview;
  final String summaryLabel;
  final String auraLine;
  final String auraSourceLabel;
  final String rulerName;
  final int? rulerHouse;
}

class _AuraLead {
  const _AuraLead({required this.label, required this.aura});

  final String label;
  final String aura;
}

class _AscRulerInfo {
  const _AscRulerInfo({required this.planet, required this.house});

  final String planet;
  final int? house;
}

class _NarrativeCard {
  const _NarrativeCard({
    required this.id,
    required this.family,
    required this.eyebrow,
    required this.summary,
    required this.body,
  });

  final String id;
  final String family;
  final String eyebrow;
  final String summary;
  final String body;

  String get previewBody {
    if (summary.trim().isNotEmpty) {
      return summary.trim();
    }
    return body.trim();
  }

  factory _NarrativeCard.fromMap(Map<String, dynamic> map) {
    return _NarrativeCard(
      id: (map['id'] ?? '').toString().trim(),
      family: (map['family'] ?? '').toString().trim(),
      eyebrow: (map['eyebrow'] ?? map['label'] ?? '').toString().trim(),
      summary: (map['summary'] ?? map['teaser'] ?? '').toString().trim(),
      body: (map['body'] ?? map['paragraph'] ?? '').toString().trim(),
    );
  }
}
