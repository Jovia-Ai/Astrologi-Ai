// ignore_for_file: unused_element

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:mobile/app/api/api_client.dart';
import 'package:mobile/app/people/add_person_page.dart';
import 'package:mobile/app/people/people_list_page.dart';
import 'package:mobile/app/people/people_providers.dart';
import 'package:mobile/app/profile/profile_providers.dart';
import 'package:mobile/app/profile/profile_repository.dart';
import 'package:mobile/app/tabs/calendar_hub_page.dart';
import 'package:mobile/app/theme/app_theme_mode_provider.dart';
import 'package:mobile/design/astro/astro_theme_extension.dart';
import 'package:mobile/design/astro/astro_theme_generator.dart';
import 'package:mobile/design/astro/element_scores.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({
    super.key,
    this.viewedUserId,
    this.profileOverride,
    this.readOnly = false,
  });

  final String? viewedUserId;
  final Map<String, dynamic>? profileOverride;
  final bool readOnly;

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  static const String _baseUrl = 'http://127.0.0.1:5000';

  final _nameController = TextEditingController();
  final _birthDateController = TextEditingController();
  final _birthTimeController = TextEditingController();
  final _cityController = TextEditingController();
  final _countryController = TextEditingController();

  bool _didSeed = false;
  bool _isSaving = false;
  String? _saveMessage;
  bool _isAvatarUploading = false;
  String? _avatarUrl;

  bool _isNatalLoading = false;
  String? _natalSummary;
  String? _natalError;
  List<_SupportingThreadItem> _supportingThreads = const [];
  List<_ProfileNarrativeCard> _profilePrimaryCards = const [];
  List<_ProfileNarrativeCard> _profilePlacementCards = const [];
  List<_ProfileInsightModule> _profileInsightModules = const [];
  String _sunSign = '—';
  String _moonSign = '—';
  String _risingSign = '—';
  String? _lastNatalKey;
  int _segmentIndex = 0;

  @override
  void dispose() {
    _nameController.dispose();
    _birthDateController.dispose();
    _birthTimeController.dispose();
    _cityController.dispose();
    _countryController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer(
      builder: (context, ref, _) {
        final profileAsync = widget.profileOverride == null
            ? ref.watch(userProfileProvider)
            : const AsyncValue<Map<String, dynamic>?>.data(null);
        final uid = ref.watch(currentUserIdProvider);
        final repo = ref.watch(profileRepositoryProvider);
        final currentUserEmail =
            Supabase.instance.client.auth.currentUser?.email;
        final peopleAsync = ref.watch(peopleListProvider);
        final authAvatarUrl = Supabase
            .instance
            .client
            .auth
            .currentUser
            ?.userMetadata?['avatar_url']
            ?.toString();
        final profile = widget.profileOverride ?? profileAsync.valueOrNull;
        final elementScores = _computeElementScores(
          profile: profile,
          userId: widget.viewedUserId ?? uid,
          email: currentUserEmail,
        );

        final themed = withAstroTheme(
          withProfileTheme(Theme.of(context)),
          astroTheme: astroThemeFromElementScores(elementScores),
        );

        return Theme(
          data: themed,
          child: Builder(
            builder: (context) {
              final profileTheme = context.profileTheme;
              final colors = profileTheme.colors;
              final friendsCount = widget.readOnly
                  ? 0
                  : peopleAsync.valueOrNull?.length ?? 0;
              final natalCount =
                  ((_natalSummary ?? '').trim().isNotEmpty ? 1 : 0) +
                  _supportingThreads.length;
              final astroCount = [_sunSign, _moonSign, _risingSign]
                  .where((sign) => sign.trim().isNotEmpty && sign.trim() != '—')
                  .length;

              if (profile != null) {
                if (!_didSeed) {
                  _nameController.text = _nameController.text.isEmpty
                      ? (profile['full_name'] ?? profile['name'] ?? '')
                            .toString()
                      : _nameController.text;
                  _birthDateController.text = _birthDateController.text.isEmpty
                      ? (profile['birth_date'] ?? '').toString()
                      : _birthDateController.text;
                  _birthTimeController.text = _birthTimeController.text.isEmpty
                      ? (profile['birth_time'] ?? '').toString()
                      : _birthTimeController.text;
                  _cityController.text = _cityController.text.isEmpty
                      ? (profile['city'] ?? '').toString()
                      : _cityController.text;
                  _countryController.text = _countryController.text.isEmpty
                      ? (profile['country'] ?? '').toString()
                      : _countryController.text;
                  _avatarUrl = (profile['avatar_url'] ?? authAvatarUrl ?? '')
                      .toString();
                  _didSeed = true;
                }
                _maybeLoadNatalInterpretation(profile);
              }

              final displayName = _displayName(profile);
              final username = _displayUsername(
                profile: profile,
                email: currentUserEmail,
              );
              final avatarUrl = (_avatarUrl ?? authAvatarUrl ?? '').trim();
              final summaryText = (_natalSummary ?? '').trim();
              final heroBody = summaryText.isNotEmpty
                  ? summaryText
                  : (_isNatalLoading
                        ? 'Natal yorum yukleniyor.'
                        : 'Dogum bilgileri tamamlandiginda profil okumasi burada acilacak.');
              final dominantElementLabel = _dominantElementLabel(elementScores);
              final contentView = _segmentIndex == 0
                  ? _ProfileRecoveryReadingBody(
                      isLoading: _isNatalLoading,
                      error: _natalError,
                      summary: summaryText,
                      supportingThreads: _supportingThreads,
                      primaryCards: _profilePrimaryCards,
                      placementCards: _profilePlacementCards,
                      insightModules: _profileInsightModules,
                      readOnly: widget.readOnly,
                      onOpenPeople: widget.readOnly
                          ? null
                          : () {
                              Navigator.of(context).push(
                                MaterialPageRoute<void>(
                                  builder: (_) => const PeopleListPage(),
                                ),
                              );
                            },
                      onAddPerson: widget.readOnly
                          ? null
                          : () {
                              Navigator.of(context).push(
                                MaterialPageRoute<void>(
                                  builder: (_) => const AddPersonPage(),
                                ),
                              );
                            },
                    )
                  : SizedBox(
                      height: 780,
                      child: PeriodCalendarTab(
                        profileOverride: widget.profileOverride,
                        embedded: true,
                      ),
                    );

              return Scaffold(
                backgroundColor: colors.bg,
                body: DecoratedBox(
                  decoration: BoxDecoration(
                    color: colors.bg,
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        colors.bg,
                        colors.bg,
                        colors.surface.withValues(alpha: 0.94),
                      ],
                      stops: const [0, 0.56, 1],
                    ),
                  ),
                  child: JoviaPageScaffold(
                    child: ListView(
                      padding: EdgeInsets.zero,
                      children: [
                        JoviaProfileTopBar(
                          label: 'Profile',
                          centerText: username,
                          onActionTap: widget.readOnly || uid == null
                              ? null
                              : () => _showProfileMenu(
                                  context: context,
                                  ref: ref,
                                  uid: uid,
                                  repo: repo,
                                  currentUserEmail: currentUserEmail,
                                ),
                          actionAsset: widget.readOnly || uid == null
                              ? null
                              : JoviaUiAsset.menuStack,
                          reserveTrailingSpace: widget.readOnly || uid == null,
                        ),
                        const SizedBox(height: 16),
                        _ProfileIdentityHeaderCard(
                          displayName: displayName,
                          username: username,
                          heroBody: heroBody,
                          avatarUrl: avatarUrl.isEmpty ? null : avatarUrl,
                          isAvatarUploading: _isAvatarUploading,
                          onAvatarEdit: widget.readOnly
                              ? null
                              : _pickAndUploadAvatar,
                          dominantElementLabel: dominantElementLabel,
                          sunSign: _sunSign,
                          moonSign: _moonSign,
                          risingSign: _risingSign,
                          stats: [
                            _ProfileStatItem(
                              value: friendsCount.toString(),
                              label: 'Arkadas',
                              onTap: widget.readOnly
                                  ? null
                                  : () {
                                      Navigator.of(context).push(
                                        MaterialPageRoute<void>(
                                          builder: (_) =>
                                              const PeopleListPage(),
                                        ),
                                      );
                                    },
                            ),
                            _ProfileStatItem(
                              value: natalCount.toString(),
                              label: 'Yorum',
                            ),
                            _ProfileStatItem(
                              value: astroCount.toString(),
                              label: 'Astro',
                            ),
                          ],
                        ),
                        if (kDebugMode) ...[
                          const SizedBox(height: 12),
                          Align(
                            alignment: Alignment.centerLeft,
                            child: _ElementDebugChip(scores: elementScores),
                          ),
                        ],
                        const SizedBox(height: 18),
                        JoviaSurfaceCard(
                          padding: const EdgeInsets.all(6),
                          child: _ProfileTabBar(
                            currentIndex: _segmentIndex,
                            onChanged: (value) {
                              if (value == _segmentIndex) {
                                return;
                              }
                              setState(() => _segmentIndex = value);
                            },
                          ),
                        ),
                        const SizedBox(height: 24),
                        contentView,
                        const SizedBox(height: 20),
                        widget.readOnly
                            ? MinimalCTAButton(
                                label: 'Geri don',
                                onTap: () => Navigator.of(
                                  context,
                                  rootNavigator: true,
                                ).maybePop(),
                              )
                            : MinimalCTAButton(
                                label: 'Cikis yap',
                                onTap: () async {
                                  await Supabase.instance.client.auth.signOut();
                                },
                              ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }

  Future<void> _pickAndUploadAvatar() async {
    final uid = Supabase.instance.client.auth.currentUser?.id;
    if (uid == null || _isAvatarUploading) {
      return;
    }

    try {
      final picker = ImagePicker();
      final picked = await picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1400,
        imageQuality: 88,
      );
      if (picked == null) {
        return;
      }

      setState(() => _isAvatarUploading = true);
      final bytes = await picked.readAsBytes();
      final ext = picked.name.toLowerCase().endsWith('.png') ? 'png' : 'jpg';
      final path = '$uid/avatar.$ext';
      final contentType = ext == 'png' ? 'image/png' : 'image/jpeg';

      await Supabase.instance.client.storage
          .from('avatars')
          .uploadBinary(
            path,
            bytes,
            fileOptions: FileOptions(
              upsert: true,
              cacheControl: '3600',
              contentType: contentType,
            ),
          );
      final publicUrl = Supabase.instance.client.storage
          .from('avatars')
          .getPublicUrl(path);

      await Supabase.instance.client.auth.updateUser(
        UserAttributes(data: <String, dynamic>{'avatar_url': publicUrl}),
      );

      if (!mounted) {
        return;
      }
      setState(() => _avatarUrl = publicUrl);
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Profil resmi güncellendi')));
    } catch (error) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Profil resmi yüklenemedi: $error')),
      );
    } finally {
      if (mounted) {
        setState(() => _isAvatarUploading = false);
      }
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
    final keys = map.keys.map((k) => k.toLowerCase()).toSet();
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
    // Replace this with backend-provided element scores when API adds it.
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

  String _dominantElementLabel(ElementScores scores) {
    return switch (scores.dominant) {
      AstroElement.fire => 'Ateş baskın',
      AstroElement.water => 'Su baskın',
      AstroElement.air => 'Hava baskın',
      AstroElement.earth => 'Toprak baskın',
    };
  }

  String _displayName(Map<String, dynamic>? profile) {
    final fromProfile = (profile?['full_name'] ?? profile?['name'] ?? '')
        .toString()
        .trim();
    if (fromProfile.isNotEmpty) {
      return fromProfile;
    }
    final fromInput = _nameController.text.trim();
    if (fromInput.isNotEmpty) {
      return fromInput;
    }
    return 'Isimsiz Profil';
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

  void _maybeLoadNatalInterpretation(Map<String, dynamic> profile) {
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
      _loadNatalInterpretation(profile);
    });
  }

  Future<void> _loadNatalInterpretation(Map<String, dynamic> profile) async {
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
      'locale': 'tr',
    };

    setState(() {
      _isNatalLoading = true;
      _natalError = null;
    });

    try {
      final client = ApiClient(baseUrl: _baseUrl);
      final response = await client.post('/interpret', data: payload);
      final map = _asMap(response.data);
      final summary = _extractNatalSummary(map);
      final supportingThreads = _extractSupportingThreads(map);
      final profileBlocks = _extractProfileNarrativeCards(map, field: 'blocks');
      final coreBlocks = _extractProfileNarrativeCards(
        map,
        field: 'core_blocks',
      );
      final extraBlocks = _extractProfileNarrativeCards(
        map,
        field: 'extra_blocks',
      );
      final detailCards = _extractProfileNarrativeCards(
        map,
        field: 'detail_cards',
      );
      final primaryCards = _mergeNarrativeCards([
        ...coreBlocks,
        ...extraBlocks,
        if (coreBlocks.isEmpty && extraBlocks.isEmpty) ...profileBlocks,
        ...detailCards.where((item) => !item.isPlacementLike),
      ]);
      final placementCards = _selectPlacementCards(detailCards);
      final insightModules = _extractProfileInsightModules(map);
      final sun = _extractPlanetSign(map, 'Sun');
      final moon = _extractPlanetSign(map, 'Moon');
      final rising = _extractRisingSign(map);

      if (!mounted) {
        return;
      }

      setState(() {
        _natalSummary = summary;
        _supportingThreads = supportingThreads;
        _profilePrimaryCards = primaryCards;
        _profilePlacementCards = placementCards;
        _profileInsightModules = insightModules;
        _sunSign = _toTrSign(sun);
        _moonSign = _toTrSign(moon);
        _risingSign = _toTrSign(rising);
        _isNatalLoading = false;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _isNatalLoading = false;
        _supportingThreads = const [];
        _natalError = 'Natal yorum alinamadi: $e';
      });
    }
  }

  Future<void> _showSettingsSheet({
    required BuildContext context,
    required WidgetRef ref,
    required String uid,
    required ProfileRepository repo,
    required String? currentUserEmail,
  }) async {
    final profile = context.profileTheme;
    final astro = context.astroTheme;
    final spacing = profile.spacing;
    final typo = profile.typography;
    final inputDecoration = _profileInputDecoration(context);

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        return Padding(
          padding: EdgeInsets.only(
            left: spacing.lg,
            right: spacing.lg,
            top: spacing.lg,
            bottom: MediaQuery.of(sheetContext).viewInsets.bottom + spacing.lg,
          ),
          child: _GlassCard(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text('Profil Ayarlari', style: typo.h2),
                  SizedBox(height: spacing.md),
                  TextField(
                    controller: _nameController,
                    style: typo.body,
                    decoration: inputDecoration.copyWith(labelText: 'Name'),
                  ),
                  SizedBox(height: spacing.sm),
                  TextField(
                    controller: _birthDateController,
                    style: typo.body,
                    decoration: inputDecoration.copyWith(
                      labelText: 'Birth date (YYYY-MM-DD)',
                    ),
                  ),
                  SizedBox(height: spacing.sm),
                  TextField(
                    controller: _birthTimeController,
                    style: typo.body,
                    decoration: inputDecoration.copyWith(
                      labelText: 'Birth time (HH:mm)',
                    ),
                  ),
                  SizedBox(height: spacing.sm),
                  TextField(
                    controller: _cityController,
                    style: typo.body,
                    decoration: inputDecoration.copyWith(labelText: 'City'),
                  ),
                  SizedBox(height: spacing.sm),
                  TextField(
                    controller: _countryController,
                    style: typo.body,
                    decoration: inputDecoration.copyWith(labelText: 'Country'),
                  ),
                  SizedBox(height: spacing.sm),
                  if (_saveMessage != null)
                    Text(
                      _saveMessage ?? '',
                      style: typo.micro.copyWith(
                        color:
                            (_saveMessage ?? '').toLowerCase().startsWith(
                              'error',
                            )
                            ? Theme.of(context).colorScheme.error
                            : Theme.of(context).colorScheme.primary,
                      ),
                    ),
                  SizedBox(height: spacing.md),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: astro.accent,
                      foregroundColor: astro.text,
                      disabledBackgroundColor: astro.accent.withValues(
                        alpha: 0.45,
                      ),
                      disabledForegroundColor: astro.text.withValues(
                        alpha: 0.75,
                      ),
                    ),
                    onPressed: _isSaving
                        ? null
                        : () async {
                            await _saveProfile(
                              ref: ref,
                              uid: uid,
                              repo: repo,
                              currentUserEmail: currentUserEmail,
                            );
                            if (!sheetContext.mounted) {
                              return;
                            }
                            if ((_saveMessage ?? '').startsWith('Saved')) {
                              Navigator.of(sheetContext).pop();
                            }
                          },
                    child: _isSaving
                        ? const SizedBox(
                            height: 18,
                            width: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Save'),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Future<void> _showProfileMenu({
    required BuildContext context,
    required WidgetRef ref,
    required String uid,
    required ProfileRepository repo,
    required String? currentUserEmail,
  }) async {
    final profile = context.profileTheme;
    final currentMode = ref.read(joviaThemeModeProvider);
    await showModalBottomSheet<void>(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (sheetContext) {
        return Padding(
          padding: EdgeInsets.all(profile.spacing.lg),
          child: JoviaSurfaceCard(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Menu',
                  style: profile.typography.card.copyWith(
                    color: profile.colors.text,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 16),
                JoviaUtilityRow(
                  label: 'Profil',
                  title: 'Profili duzenle',
                  body: 'Isim, dogum bilgileri ve diger ayarlari ac.',
                  leading: const JoviaUiIcon(
                    asset: JoviaUiAsset.settingsRings,
                    size: 18,
                  ),
                  onTap: () {
                    Navigator.of(sheetContext).pop();
                    _showSettingsSheet(
                      context: context,
                      ref: ref,
                      uid: uid,
                      repo: repo,
                      currentUserEmail: currentUserEmail,
                    );
                  },
                ),
                const SizedBox(height: 12),
                const ThinDivider(),
                const SizedBox(height: 12),
                Text(
                  'Tema',
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
                        label: 'Koyu mod',
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
                        label: 'Acik mod',
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

  Future<void> _saveProfile({
    required WidgetRef ref,
    required String uid,
    required ProfileRepository repo,
    required String? currentUserEmail,
  }) async {
    setState(() {
      _isSaving = true;
      _saveMessage = null;
    });
    try {
      if (_readName().isEmpty ||
          _readBirthDate().isEmpty ||
          _readBirthTime().isEmpty ||
          _readCity().isEmpty ||
          _readCountry().isEmpty) {
        throw Exception('Please fill all fields.');
      }

      final place = _readCountry().isEmpty
          ? _readCity()
          : '${_readCity()}, ${_readCountry()}';
      final timezone = DateTime.now().timeZoneName;

      await repo.upsertProfileBasics(
        userId: uid,
        fullName: _readName(),
        email: currentUserEmail,
      );

      await repo.upsertBirthData(
        userId: uid,
        birthDate: _readBirthDate(),
        birthTime: _readBirthTime(),
        place: place,
        city: _readCity(),
        country: _readCountry(),
        timezone: timezone,
        latitude: null,
        longitude: null,
      );

      ref.invalidate(userProfileProvider);
      _lastNatalKey = null;
      _saveMessage = 'Saved successfully.';
    } catch (e) {
      _saveMessage = 'Error: $e';
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
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
    return <String, dynamic>{};
  }

  String _extractNatalSummary(Map<String, dynamic> map) {
    final public = map['public'];
    if (public is Map) {
      final ui = public['core_story_ui'];
      if (ui is Map && (ui['text'] ?? '').toString().trim().isNotEmpty) {
        return (ui['text'] ?? '').toString().trim();
      }
      if ((public['core_story'] ?? '').toString().trim().isNotEmpty) {
        return (public['core_story'] ?? '').toString();
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
    final fallback = (map['narrative_text'] ?? map['summary'] ?? '')
        .toString()
        .trim();
    return fallback;
  }

  Map<String, dynamic> _extractProfilePublicPayload(Map<String, dynamic> map) {
    for (final scope in _natalScopes(map)) {
      final narrative = _asMap(scope['profile_narrative']);
      final profilePublic = _asMap(narrative['profile_public']);
      if (profilePublic.isNotEmpty) {
        return profilePublic;
      }
    }
    return <String, dynamic>{};
  }

  List<_ProfileNarrativeCard> _extractProfileNarrativeCards(
    Map<String, dynamic> map, {
    required String field,
  }) {
    final profilePublic = _extractProfilePublicPayload(map);
    final raw = profilePublic[field];
    if (raw is! List) {
      return const [];
    }
    return raw
        .whereType<Map>()
        .map(
          (item) =>
              _ProfileNarrativeCard.fromMap(Map<String, dynamic>.from(item)),
        )
        .where((item) => item.title.isNotEmpty && item.previewBody.isNotEmpty)
        .toList();
  }

  List<_ProfileInsightModule> _extractProfileInsightModules(
    Map<String, dynamic> map,
  ) {
    final profilePublic = _extractProfilePublicPayload(map);
    final raw = profilePublic['insight_modules'];
    if (raw is! List) {
      return const [];
    }
    return raw
        .whereType<Map>()
        .map(
          (item) =>
              _ProfileInsightModule.fromMap(Map<String, dynamic>.from(item)),
        )
        .where((item) => item.headline.isNotEmpty && item.title.isNotEmpty)
        .toList();
  }

  List<_ProfileNarrativeCard> _mergeNarrativeCards(
    List<_ProfileNarrativeCard> items,
  ) {
    final seen = <String>{};
    final out = <_ProfileNarrativeCard>[];
    for (final item in items) {
      if (item.isPlacementLike) {
        continue;
      }
      final key = item.cardKey.isNotEmpty ? item.cardKey : item.title;
      if (key.isEmpty || !seen.add(key)) {
        continue;
      }
      out.add(item);
    }
    return out;
  }

  List<_ProfileNarrativeCard> _selectPlacementCards(
    List<_ProfileNarrativeCard> items,
  ) {
    final preferred = items.where((item) => item.isPlacementLike).toList();
    if (preferred.isNotEmpty) {
      return preferred.take(4).toList();
    }
    return items.take(4).toList();
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
          if (targets.contains(name)) {
            final sign = (raw['sign'] ?? raw['zodiac_sign'] ?? '')
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
        for (final entry in signMap.entries) {
          final key = entry.key.toString().toLowerCase();
          if (targets.contains(key)) {
            final sign = entry.value.toString().trim();
            if (sign.isNotEmpty) {
              return sign;
            }
          }
        }
      }

      final formatted = scope['formatted_positions'];
      if (formatted is List) {
        final pattern = RegExp(
          '^$planetName\\s+in\\s+([A-Za-z]+)',
          caseSensitive: false,
        );
        for (final line in formatted) {
          final text = line.toString().trim();
          final match = pattern.firstMatch(text);
          if (match != null) {
            return match.group(1) ?? '—';
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

      final metaInfo = scope['meta_info'];
      if (metaInfo is Map) {
        final sign = (metaInfo['ascendant_sign'] ?? metaInfo['asc_sign'] ?? '')
            .toString()
            .trim();
        if (sign.isNotEmpty) {
          return sign;
        }
      }

      final houses = scope['formatted_houses'];
      if (houses is List) {
        final pattern = RegExp(
          r'^1st House in ([A-Za-z]+)',
          caseSensitive: false,
        );
        for (final line in houses) {
          final text = line.toString().trim();
          final match = pattern.firstMatch(text);
          if (match != null) {
            return match.group(1) ?? '—';
          }
        }
      }
    }
    return '—';
  }

  List<Map<String, dynamic>> _natalScopes(Map<String, dynamic> map) {
    final scopes = <Map<String, dynamic>>[map];
    final public = _asMap(map['public']);
    if (public.isNotEmpty) {
      scopes.add(public);
    }
    final metaInfo = _asMap(map['meta_info']);
    if (metaInfo.isNotEmpty) {
      scopes.add(metaInfo);
    }
    return scopes;
  }

  List<_SupportingThreadItem> _extractSupportingThreads(
    Map<String, dynamic> map,
  ) {
    for (final scope in _natalScopes(map)) {
      final raw = scope['supporting_threads'];
      if (raw is! List) {
        continue;
      }
      final parsed = raw
          .whereType<Map>()
          .map(
            (item) =>
                _SupportingThreadItem.fromMap(Map<String, dynamic>.from(item)),
          )
          .where((item) => item.title.isNotEmpty && item.oneLiner.isNotEmpty)
          .toList();
      if (parsed.isNotEmpty) {
        return parsed;
      }
    }
    return const [];
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
      'koç': 'Koc',
      'koc': 'Koc',
      'boğa': 'Boga',
      'boga': 'Boga',
      'yengeç': 'Yengec',
      'yengec': 'Yengec',
      'başak': 'Basak',
      'basak': 'Basak',
      'ikizler': 'Ikizler',
      'terazi': 'Terazi',
      'akrep': 'Akrep',
      'yay': 'Yay',
      'oğlak': 'Oglak',
      'oglak': 'Oglak',
      'kova': 'Kova',
      'balık': 'Balik',
      'balik': 'Balik',
    };
    final key = raw.trim().toLowerCase();
    return signs[key] ?? (raw.trim().isEmpty ? '—' : raw.trim());
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

  String _readName() => _nameController.text.trim();
  String _readBirthDate() => _birthDateController.text.trim();
  String _readBirthTime() => _birthTimeController.text.trim();
  String _readCity() => _cityController.text.trim();
  String _readCountry() => _countryController.text.trim();
}

class _SupportingThreadItem {
  final String id;
  final String title;
  final String oneLiner;
  final String paragraph;

  const _SupportingThreadItem({
    required this.id,
    required this.title,
    required this.oneLiner,
    required this.paragraph,
  });

  factory _SupportingThreadItem.fromMap(Map<String, dynamic> map) {
    String s(String key) => (map[key] ?? '').toString().trim();
    return _SupportingThreadItem(
      id: s('id'),
      title: s('title'),
      oneLiner: s('one_liner'),
      paragraph: s('paragraph'),
    );
  }
}

class _ProfileNarrativeCard {
  const _ProfileNarrativeCard({
    required this.cardKey,
    required this.id,
    required this.family,
    required this.origin,
    required this.eyebrow,
    required this.title,
    required this.summary,
    required this.body,
    required this.micro,
    required this.chips,
  });

  final String cardKey;
  final String id;
  final String family;
  final String origin;
  final String eyebrow;
  final String title;
  final String summary;
  final String body;
  final String micro;
  final List<String> chips;

  String get previewBody {
    final bodyText = body.trim();
    if (bodyText.isNotEmpty) {
      return bodyText;
    }
    final summaryText = summary.trim();
    if (summaryText.isNotEmpty) {
      return summaryText;
    }
    return micro.trim();
  }

  bool get isPlacementLike =>
      origin == 'personality_imprint' ||
      family == 'placement_signature' ||
      family == 'tone_signature';

  factory _ProfileNarrativeCard.fromMap(Map<String, dynamic> map) {
    List<String> normalizeChips(dynamic raw) {
      if (raw is! List) {
        return const [];
      }
      return raw
          .map((item) => item.toString().trim())
          .where((item) {
            if (item.isEmpty) {
              return false;
            }
            final lower = item.toLowerCase();
            if (lower.contains('_')) {
              return false;
            }
            if (lower == 'moon_sign' ||
                lower == 'sun_sign' ||
                lower == 'rising_sign' ||
                lower == 'ascendant') {
              return false;
            }
            return true;
          })
          .take(4)
          .toList();
    }

    String pickTitle() {
      final title = (map['title'] ?? '').toString().trim();
      if (title.isNotEmpty) {
        return title;
      }
      return (map['headline'] ?? '').toString().trim();
    }

    String pickSummary() {
      final summary = (map['summary'] ?? '').toString().trim();
      if (summary.isNotEmpty) {
        return summary;
      }
      return (map['teaser'] ?? '').toString().trim();
    }

    String pickEyebrow() {
      final eyebrow = (map['eyebrow'] ?? '').toString().trim();
      if (eyebrow.isNotEmpty) {
        return eyebrow;
      }
      final family = (map['family'] ?? '').toString().trim();
      return switch (family) {
        'placement_signature' => 'Kişilik izi',
        'tone_signature' => 'Ton izi',
        'mind_mechanics' => 'Zihnin nasıl çalışıyor',
        'intimacy_guard' => 'Yakınlık sende nasıl açılıyor',
        'creative_channel' => 'Fırsatın aktığı yer',
        _ => '',
      };
    }

    return _ProfileNarrativeCard(
      cardKey: (map['card_key'] ?? '').toString().trim(),
      id: (map['id'] ?? '').toString().trim(),
      family: (map['family'] ?? '').toString().trim(),
      origin: (map['origin'] ?? '').toString().trim(),
      eyebrow: pickEyebrow(),
      title: pickTitle(),
      summary: pickSummary(),
      body: (map['body'] ?? '').toString().trim(),
      micro: (map['micro'] ?? '').toString().trim(),
      chips: normalizeChips(map['chips']),
    );
  }
}

class _ProfileInsightModule {
  const _ProfileInsightModule({
    required this.moduleId,
    required this.headline,
    required this.subheadline,
    required this.title,
    required this.body,
  });

  final String moduleId;
  final String headline;
  final String subheadline;
  final String title;
  final String body;

  factory _ProfileInsightModule.fromMap(Map<String, dynamic> map) {
    final content = map['content'] is Map<String, dynamic>
        ? map['content'] as Map<String, dynamic>
        : (map['content'] is Map
              ? Map<String, dynamic>.from(map['content'] as Map)
              : <String, dynamic>{});
    return _ProfileInsightModule(
      moduleId: (map['module_id'] ?? '').toString().trim(),
      headline: (map['headline'] ?? '').toString().trim(),
      subheadline: (map['subheadline'] ?? '').toString().trim(),
      title: (content['title'] ?? map['title'] ?? '').toString().trim(),
      body: (content['body'] ?? map['body'] ?? '').toString().trim(),
    );
  }
}

class _SupportingThreadsSection extends StatelessWidget {
  const _SupportingThreadsSection({required this.items});

  final List<_SupportingThreadItem> items;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final typo = profile.typography;

    return Container(
      decoration: BoxDecoration(
        color: profile.colors.surface,
        borderRadius: BorderRadius.circular(profile.radii.cardRadius * 0.65),
        border: Border.all(color: profile.colors.strokeSoft, width: 1.5),
      ),
      child: Padding(
        padding: EdgeInsets.symmetric(
          horizontal: profile.spacing.md,
          vertical: profile.spacing.sm,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Yan Temalar',
              style: typo.body.copyWith(fontWeight: FontWeight.w700),
            ),
            SizedBox(height: profile.spacing.xs),
            for (final item in items)
              ExpansionTile(
                dense: true,
                tilePadding: EdgeInsets.zero,
                collapsedShape: const Border(),
                shape: const Border(),
                iconColor: profile.colors.primary,
                collapsedIconColor: profile.colors.textLight,
                childrenPadding: EdgeInsets.only(
                  left: profile.spacing.xs,
                  right: profile.spacing.xs,
                  bottom: profile.spacing.xs,
                ),
                title: Text(
                  item.title,
                  style: typo.body.copyWith(fontWeight: FontWeight.w600),
                ),
                subtitle: Text(item.oneLiner, style: typo.micro),
                children: [
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(item.paragraph, style: typo.body),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

class _ElementDebugChip extends StatelessWidget {
  const _ElementDebugChip({required this.scores});

  final ElementScores scores;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final astro = context.astroTheme;
    final label = switch (scores.dominant) {
      AstroElement.fire => '🔥 Fire',
      AstroElement.water => '🌊 Water',
      AstroElement.air => '🌬 Air',
      AstroElement.earth => '🌱 Earth',
    };
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: profile.spacing.sm,
        vertical: profile.spacing.xs,
      ),
      decoration: BoxDecoration(
        color: astro.highlight.withValues(alpha: 0.18),
        border: Border.all(color: astro.accent.withValues(alpha: 0.35)),
        borderRadius: BorderRadius.circular(profile.radii.pillRadius),
      ),
      child: Text(
        label,
        style: profile.typography.micro.copyWith(color: astro.text),
      ),
    );
  }
}

InputDecoration _profileInputDecoration(BuildContext context) {
  final profile = context.profileTheme;
  return InputDecoration(
    labelStyle: profile.typography.micro.copyWith(
      color: profile.colors.textLight,
    ),
    floatingLabelStyle: profile.typography.micro.copyWith(
      color: profile.colors.primary,
    ),
    filled: true,
    fillColor: profile.colors.surface,
    contentPadding: EdgeInsets.symmetric(
      horizontal: profile.spacing.md,
      vertical: profile.spacing.sm,
    ),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(profile.radii.cardRadius * 0.55),
      borderSide: BorderSide(color: profile.colors.separator, width: 1),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(profile.radii.cardRadius * 0.55),
      borderSide: BorderSide(color: profile.colors.separator, width: 1),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(profile.radii.cardRadius * 0.55),
      borderSide: BorderSide(color: profile.colors.primary, width: 1.5),
    ),
  );
}

class _ProfileHeroScene extends StatelessWidget {
  const _ProfileHeroScene({
    required this.displayName,
    required this.username,
    required this.avatarUrl,
    required this.isAvatarUploading,
    required this.onAvatarEdit,
    required this.readOnly,
    required this.onSettingsTap,
  });

  final String displayName;
  final String username;
  final String? avatarUrl;
  final bool isAvatarUploading;
  final VoidCallback? onAvatarEdit;
  final bool readOnly;
  final VoidCallback? onSettingsTap;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final astro = context.astroTheme;
    final colors = profile.colors;
    final settingsTap = onSettingsTap;
    final bottomInset = MediaQuery.paddingOf(context).top;

    double clamp(double value, double min, double max) {
      if (value < min) return min;
      if (value > max) return max;
      return value;
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;
        final largeTileW = clamp(width * 0.58, 240, 260);
        const largeTileH = 280.0;
        final leftTileW = clamp(width * 0.42, 170, 190);
        const leftTileH = 210.0;

        return Stack(
          fit: StackFit.expand,
          children: <Widget>[
            DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: <Color>[
                    astro.auraStops.first,
                    colors.brandPurple,
                    colors.brandLavender,
                  ],
                ),
              ),
            ),
            Align(
              alignment: Alignment.bottomLeft,
              child: IgnorePointer(
                child: Container(
                  height: 144,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.bottomLeft,
                      end: Alignment.topLeft,
                      colors: <Color>[
                        Colors.black.withValues(alpha: 0.18),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
              ),
            ),
            Positioned(
              top: bottomInset + 56,
              left: width - largeTileW + 20,
              child: _FloatingTile(
                width: largeTileW,
                height: largeTileH,
                radius: 28,
                rotationDeg: -10,
                fill: colors.brandLavender.withValues(alpha: 0.94),
                stroke: Colors.white.withValues(alpha: 0.18),
              ),
            ),
            Positioned(
              top: bottomInset + 48,
              left: 20,
              child: _FloatingTile(
                width: leftTileW,
                height: leftTileH,
                radius: 24,
                rotationDeg: 10,
                fill: colors.brandPurple.withValues(alpha: 0.92),
                stroke: Colors.white.withValues(alpha: 0.16),
              ),
            ),
            Positioned(
              top: bottomInset + 122,
              left: clamp(width * 0.44, 140, 184),
              child: _FloatingTile(
                width: 140,
                height: 160,
                radius: 22,
                rotationDeg: -6,
                fill: colors.brandLime.withValues(alpha: 0.9),
                stroke: Colors.white.withValues(alpha: 0.14),
              ),
            ),
            Positioned(
              top: bottomInset + 220,
              left: 24,
              child: Transform.rotate(
                angle: -0.16,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.82),
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(
                      color: colors.brandPurple.withValues(alpha: 0.12),
                    ),
                  ),
                  child: Text(
                    'NEON WAVES',
                    style: profile.typography.meta.copyWith(
                      color: colors.brandPurple.withValues(alpha: 0.82),
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ),
            ),
            SafeArea(
              bottom: false,
              child: Padding(
                padding: EdgeInsets.fromLTRB(
                  profile.spacing.s20,
                  profile.spacing.s12,
                  profile.spacing.s20,
                  profile.spacing.s24,
                ),
                child: Column(
                  children: <Widget>[
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: <Widget>[
                        if (settingsTap != null)
                          _HeaderActionButton(
                            icon: Icons.settings_outlined,
                            onTap: settingsTap,
                            sceneStyle: true,
                          ),
                        if (readOnly)
                          _HeaderActionButton(
                            icon: Icons.arrow_back_rounded,
                            onTap: () => Navigator.of(
                              context,
                              rootNavigator: true,
                            ).maybePop(),
                            sceneStyle: true,
                          ),
                      ],
                    ),
                    const Spacer(),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: <Widget>[
                        _AvatarHalo(
                          size: 82,
                          imageUrl: avatarUrl,
                          isUploading: isAvatarUploading,
                          onEdit: onAvatarEdit,
                          heroStyle: true,
                        ),
                        SizedBox(width: profile.spacing.s12),
                        Expanded(
                          child: Padding(
                            padding: EdgeInsets.only(
                              bottom: profile.spacing.s8,
                            ),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                Text(
                                  displayName,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: profile.typography.heroTitle.copyWith(
                                    color: Colors.white.withValues(alpha: 0.95),
                                    height: 1.06,
                                  ),
                                ),
                                SizedBox(height: profile.spacing.s4),
                                Text(
                                  username,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: profile.typography.meta.copyWith(
                                    color: Colors.white.withValues(alpha: 0.85),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

class _ProfileRecoveryHeroFooter extends StatelessWidget {
  const _ProfileRecoveryHeroFooter({
    required this.username,
    required this.sunSign,
    required this.moonSign,
    required this.risingSign,
  });

  final String username;
  final String sunSign;
  final String moonSign;
  final String risingSign;

  @override
  Widget build(BuildContext context) {
    final chips = <String>[
      if (username.trim().isNotEmpty) username.trim(),
      if (sunSign.trim().isNotEmpty && sunSign.trim() != '—') 'Gunes $sunSign',
      if (moonSign.trim().isNotEmpty && moonSign.trim() != '—') 'Ay $moonSign',
      if (risingSign.trim().isNotEmpty && risingSign.trim() != '—')
        'Yukselen $risingSign',
    ];
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

class _ProfileIdentityHeaderCard extends StatelessWidget {
  const _ProfileIdentityHeaderCard({
    required this.displayName,
    required this.username,
    required this.heroBody,
    required this.avatarUrl,
    required this.isAvatarUploading,
    required this.onAvatarEdit,
    required this.dominantElementLabel,
    required this.sunSign,
    required this.moonSign,
    required this.risingSign,
    required this.stats,
  });

  final String displayName;
  final String username;
  final String heroBody;
  final String? avatarUrl;
  final bool isAvatarUploading;
  final VoidCallback? onAvatarEdit;
  final String dominantElementLabel;
  final String sunSign;
  final String moonSign;
  final String risingSign;
  final List<_ProfileStatItem> stats;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return JoviaSurfaceCard(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'WHO AM I?',
            style: profile.typography.eyebrow.copyWith(
              color: profile.colors.textLight,
              letterSpacing: 1.6,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _AvatarHalo(
                size: 82,
                imageUrl: avatarUrl,
                onEdit: onAvatarEdit,
                isUploading: isAvatarUploading,
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      displayName,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.heroTitle.copyWith(
                        color: profile.colors.text,
                        fontSize: 28,
                        height: 1.02,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      username,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: profile.typography.bodyCompact.copyWith(
                        color: profile.colors.textLight,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          _ProfileRecoveryHeroFooter(
            username: '',
            sunSign: sunSign,
            moonSign: moonSign,
            risingSign: risingSign,
          ),
          const SizedBox(height: 14),
          Text(
            dominantElementLabel,
            style: profile.typography.body.copyWith(
              color: profile.colors.text,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            heroBody,
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.bodyCompact.copyWith(
              color: profile.colors.textLight,
              height: 1.45,
            ),
          ),
          const SizedBox(height: 16),
          const ThinDivider(),
          const SizedBox(height: 14),
          _ProfileStatsRow(items: stats),
        ],
      ),
    );
  }
}

class _ProfileRecoveryReadingBody extends StatelessWidget {
  const _ProfileRecoveryReadingBody({
    required this.isLoading,
    required this.error,
    required this.summary,
    required this.supportingThreads,
    required this.primaryCards,
    required this.placementCards,
    required this.insightModules,
    required this.readOnly,
    this.onOpenPeople,
    this.onAddPerson,
  });

  final bool isLoading;
  final String? error;
  final String summary;
  final List<_SupportingThreadItem> supportingThreads;
  final List<_ProfileNarrativeCard> primaryCards;
  final List<_ProfileNarrativeCard> placementCards;
  final List<_ProfileInsightModule> insightModules;
  final bool readOnly;
  final VoidCallback? onOpenPeople;
  final VoidCallback? onAddPerson;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        JoviaReadingPanel(
          label: 'Natal',
          title: 'Ana okuma',
          large: true,
          child: _ProfileRecoverySummaryBlock(
            isLoading: isLoading,
            error: error,
            summary: summary,
          ),
        ),
        if (placementCards.isNotEmpty) ...[
          const SizedBox(height: 22),
          _ProfileEditorialFlow(cards: placementCards),
        ],
        if (insightModules.isNotEmpty) ...[
          const SizedBox(height: 24),
          for (final module in insightModules) ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 10),
              child: _ProfileInsightModuleCard(module: module),
            ),
            if (module != insightModules.last) const SizedBox(height: 18),
          ],
        ],
        if (primaryCards.isNotEmpty) ...[
          const SizedBox(height: 24),
          _ProfileEditorialFlow(cards: primaryCards),
        ],
        if (supportingThreads.isNotEmpty) ...[
          const SizedBox(height: 24),
          JoviaReadingPanel(
            label: 'Katmanlar',
            title: 'Destekleyen izler',
            child: Column(
              children: [
                for (
                  var index = 0;
                  index < supportingThreads.length;
                  index++
                ) ...[
                  JoviaUtilityRow(
                    title: supportingThreads[index].title,
                    body: supportingThreads[index].oneLiner,
                  ),
                  if (index != supportingThreads.length - 1) ...[
                    const SizedBox(height: 10),
                    const ThinDivider(),
                    const SizedBox(height: 10),
                  ],
                ],
              ],
            ),
          ),
        ],
        if (!readOnly) ...[
          const SizedBox(height: 24),
          JoviaActionRail(
            title: 'Kisi alani',
            body:
                'Arkadaslarini ve referans profilleri buradan yonetebilirsin.',
            primaryAction: MinimalCTAButton(
              label: 'Arkadaslarini gor',
              emphasized: true,
              onTap: onOpenPeople,
            ),
            secondaryActions: [
              MinimalCTAButton(label: '+ Kisi ekle', onTap: onAddPerson),
            ],
          ),
        ],
      ],
    );
  }
}

class _ProfileEditorialFlow extends StatelessWidget {
  const _ProfileEditorialFlow({required this.cards});

  final List<_ProfileNarrativeCard> cards;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 390;
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            for (var index = 0; index < cards.length; index++) ...[
              Padding(
                padding: compact || index == 0
                    ? EdgeInsets.zero
                    : EdgeInsets.only(
                        left: index.isOdd ? 18 : 0,
                        right: index.isOdd ? 0 : 18,
                      ),
                child: _ProfileEditorialCard(
                  card: cards[index],
                  featured: index == 0,
                ),
              ),
              if (index != cards.length - 1)
                SizedBox(height: index == 0 ? 20 : 16),
            ],
          ],
        );
      },
    );
  }
}

class _ProfileRecoverySummaryBlock extends StatelessWidget {
  const _ProfileRecoverySummaryBlock({
    required this.isLoading,
    required this.error,
    required this.summary,
  });

  final bool isLoading;
  final String? error;
  final String summary;

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 8),
        child: Center(child: CircularProgressIndicator()),
      );
    }
    if ((error ?? '').trim().isNotEmpty) {
      return Text(
        error!,
        style: context.profileTheme.typography.bodyCompact.copyWith(
          color: Theme.of(context).colorScheme.error,
        ),
      );
    }
    if (summary.trim().isEmpty) {
      return Text(
        'Natal okuma henuz hazir degil.',
        style: context.profileTheme.typography.bodyCompact.copyWith(
          color: context.profileTheme.colors.textLight,
        ),
      );
    }
    return Text(
      summary,
      style: context.profileTheme.typography.bodyCompact.copyWith(
        color: context.profileTheme.colors.text,
      ),
    );
  }
}

class _ProfileEditorialCard extends StatelessWidget {
  const _ProfileEditorialCard({required this.card, this.featured = false});

  final _ProfileNarrativeCard card;
  final bool featured;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return JoviaSurfaceCard(
      padding: EdgeInsets.fromLTRB(
        featured ? 22 : 18,
        featured ? 22 : 18,
        featured ? 22 : 18,
        featured ? 20 : 18,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (card.eyebrow.trim().isNotEmpty) ...[
            Text(
              card.eyebrow.toUpperCase(),
              style: profile.typography.eyebrow.copyWith(
                color: profile.colors.textLight,
                letterSpacing: 1.3,
              ),
            ),
            const SizedBox(height: 10),
          ],
          Text(
            card.title,
            style: profile.typography.card.copyWith(
              color: profile.colors.text,
              fontSize: featured ? 30 : 22,
              height: 1.08,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            card.previewBody,
            maxLines: featured ? 8 : 5,
            overflow: TextOverflow.ellipsis,
            style: profile.typography.bodyCompact.copyWith(
              color: profile.colors.text,
              height: 1.45,
            ),
          ),
          if (card.chips.isNotEmpty) ...[
            const SizedBox(height: 14),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final chip in card.chips) JoviaMetaPill(label: chip),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

class _ProfileInsightModuleCard extends StatelessWidget {
  const _ProfileInsightModuleCard({required this.module});

  final _ProfileInsightModule module;

  @override
  Widget build(BuildContext context) {
    final card = _ProfileNarrativeCard(
      cardKey: module.moduleId,
      id: module.moduleId,
      family: 'protection_pattern',
      origin: 'insight_module',
      eyebrow: module.headline,
      title: module.title,
      summary: module.subheadline,
      body: module.body,
      micro: '',
      chips: const [],
    );
    return _ProfileEditorialCard(card: card);
  }
}

class _FloatingTile extends StatelessWidget {
  const _FloatingTile({
    required this.width,
    required this.height,
    required this.radius,
    required this.rotationDeg,
    required this.fill,
    required this.stroke,
  });

  final double width;
  final double height;
  final double radius;
  final double rotationDeg;
  final Color fill;
  final Color stroke;

  @override
  Widget build(BuildContext context) {
    return Transform.rotate(
      angle: rotationDeg * 3.1415926535 / 180.0,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(radius),
        child: Container(
          width: width,
          height: height,
          decoration: BoxDecoration(
            color: fill,
            border: Border.all(color: stroke, width: 1),
            boxShadow: <BoxShadow>[
              BoxShadow(
                blurRadius: 18,
                offset: const Offset(0, 10),
                color: Colors.black.withValues(alpha: 0.12),
              ),
            ],
          ),
          child: Stack(
            fit: StackFit.expand,
            children: <Widget>[
              DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: <Color>[
                      Colors.white.withValues(alpha: 0.18),
                      Colors.transparent,
                      Colors.black.withValues(alpha: 0.06),
                    ],
                  ),
                ),
              ),
              Positioned(
                left: 16,
                right: 16,
                bottom: 16,
                child: Container(
                  height: 10,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.18),
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
              ),
              Positioned(
                right: 14,
                top: 14,
                child: Container(
                  width: 18,
                  height: 18,
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.14),
                    shape: BoxShape.circle,
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

class _EditorialDivider extends StatelessWidget {
  const _EditorialDivider();

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: EdgeInsets.symmetric(vertical: profile.spacing.s12),
      child: Row(
        children: <Widget>[
          Expanded(
            child: Container(height: 1, color: profile.colors.strokeDivider),
          ),
          SizedBox(width: profile.spacing.s12),
          Text(
            '✦',
            style: profile.typography.meta.copyWith(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: profile.colors.brandPurple.withValues(alpha: 0.6),
            ),
          ),
          SizedBox(width: profile.spacing.s12),
          Expanded(
            child: Container(height: 1, color: profile.colors.strokeDivider),
          ),
        ],
      ),
    );
  }
}

class _CardShell extends StatelessWidget {
  const _CardShell({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Container(
      padding: EdgeInsets.all(profile.spacing.s16),
      decoration: BoxDecoration(
        color: profile.colors.surfaceCard,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: profile.colors.strokeSoft, width: 1.5),
        boxShadow: <BoxShadow>[
          BoxShadow(
            blurRadius: 18,
            offset: const Offset(0, 8),
            color: Colors.black.withValues(alpha: 0.07),
          ),
        ],
      ),
      child: child,
    );
  }
}

class _HeaderActionButton extends StatelessWidget {
  const _HeaderActionButton({
    required this.icon,
    required this.onTap,
    this.sceneStyle = false,
  });

  final IconData icon;
  final VoidCallback onTap;
  final bool sceneStyle;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Padding(
      padding: EdgeInsets.only(left: profile.spacing.xs),
      child: Material(
        color: sceneStyle
            ? Colors.white.withValues(alpha: 0.75)
            : Colors.white.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(14),
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: onTap,
          child: Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: sceneStyle
                    ? profile.colors.primary.withValues(alpha: 0.14)
                    : Colors.white.withValues(alpha: 0.22),
                width: 1,
              ),
            ),
            child: Icon(
              icon,
              size: 18,
              color: sceneStyle
                  ? profile.colors.primary
                  : profile.colors.heroText,
            ),
          ),
        ),
      ),
    );
  }
}

class _AvatarHalo extends StatelessWidget {
  const _AvatarHalo({
    required this.size,
    this.imageUrl,
    this.onEdit,
    this.isUploading = false,
    this.heroStyle = false,
  });

  final double size;
  final String? imageUrl;
  final VoidCallback? onEdit;
  final bool isUploading;
  final bool heroStyle;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: heroStyle
                  ? Colors.white.withValues(alpha: 0.18)
                  : profile.colors.lavender.withValues(alpha: 0.26),
              boxShadow: [profile.shadows.floatingShadow],
            ),
          ),
          Container(
            width: size * 0.76,
            height: size * 0.76,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: heroStyle
                  ? Colors.white.withValues(alpha: 0.96)
                  : profile.colors.surface,
              border: Border.all(
                color: heroStyle
                    ? Colors.white.withValues(alpha: 0.45)
                    : profile.colors.separator,
                width: heroStyle ? 1 : 1.5,
              ),
            ),
            alignment: Alignment.center,
            child: ClipOval(
              child: SizedBox.expand(
                child: (imageUrl ?? '').trim().isEmpty
                    ? Icon(
                        Icons.person_rounded,
                        size: size * 0.36,
                        color: heroStyle
                            ? profile.colors.primary
                            : profile.colors.primary.withValues(alpha: 0.78),
                      )
                    : Image.network(
                        imageUrl!,
                        fit: BoxFit.cover,
                        errorBuilder: (_, _, _) => Icon(
                          Icons.person_rounded,
                          size: size * 0.36,
                          color: heroStyle
                              ? profile.colors.primary
                              : profile.colors.primary.withValues(alpha: 0.78),
                        ),
                      ),
              ),
            ),
          ),
          if (isUploading)
            SizedBox(
              width: size * 0.28,
              height: size * 0.28,
              child: const CircularProgressIndicator(strokeWidth: 2),
            ),
          if (onEdit != null)
            Positioned(
              right: 0,
              bottom: 0,
              child: InkWell(
                onTap: onEdit,
                borderRadius: BorderRadius.circular(99),
                child: Container(
                  width: size * 0.28,
                  height: size * 0.28,
                  decoration: BoxDecoration(
                    color: profile.colors.primary,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: profile.colors.surface,
                      width: 1.5,
                    ),
                  ),
                  child: Icon(
                    Icons.edit_outlined,
                    size: size * 0.14,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _ProfileTabBar extends StatelessWidget {
  const _ProfileTabBar({required this.currentIndex, required this.onChanged});

  final int currentIndex;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final labels = const <String>['Natal', 'Timing'];
    return Row(
      children: [
        for (var index = 0; index < labels.length; index++)
          Expanded(
            child: InkWell(
              onTap: () => onChanged(index),
              borderRadius: BorderRadius.circular(14),
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 12),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      labels[index],
                      style: profile.typography.body.copyWith(
                        fontWeight: FontWeight.w700,
                        color: currentIndex == index
                            ? profile.colors.primary
                            : profile.colors.textLight,
                      ),
                    ),
                    const SizedBox(height: 8),
                    AnimatedContainer(
                      duration: const Duration(milliseconds: 180),
                      height: 2,
                      width: 42,
                      decoration: BoxDecoration(
                        color: currentIndex == index
                            ? profile.colors.primary
                            : Colors.transparent,
                        borderRadius: BorderRadius.circular(999),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class _ProfileStatItem {
  const _ProfileStatItem({
    required this.value,
    required this.label,
    this.onTap,
  });

  final String value;
  final String label;
  final VoidCallback? onTap;
}

class _ProfileStatsRow extends StatelessWidget {
  const _ProfileStatsRow({required this.items});

  final List<_ProfileStatItem> items;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    return Row(
      children: [
        for (var index = 0; index < items.length; index++) ...[
          Expanded(child: _StatCell(item: items[index])),
          if (index != items.length - 1)
            Container(width: 1, height: 32, color: profile.colors.separator),
        ],
      ],
    );
  }
}

class _StatCell extends StatelessWidget {
  const _StatCell({required this.item});

  final _ProfileStatItem item;

  @override
  Widget build(BuildContext context) {
    final profile = context.profileTheme;
    final child = Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          item.value,
          style: profile.typography.card.copyWith(
            fontWeight: FontWeight.w600,
            color: profile.colors.text,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          item.label,
          style: profile.typography.meta.copyWith(
            color: profile.colors.textLight,
          ),
        ),
      ],
    );
    if (item.onTap == null) {
      return child;
    }
    return InkWell(
      onTap: item.onTap,
      borderRadius: BorderRadius.circular(14),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: child,
      ),
    );
  }
}

class _GlassCard extends StatelessWidget {
  const _GlassCard({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return _CardShell(child: child);
  }
}
