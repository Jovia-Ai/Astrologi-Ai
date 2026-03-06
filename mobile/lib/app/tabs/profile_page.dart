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
import 'package:mobile/design/astro/astro_theme_extension.dart';
import 'package:mobile/design/astro/astro_theme_generator.dart';
import 'package:mobile/design/astro/element_scores.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';

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
              final spacing = profileTheme.spacing;
              final typo = profileTheme.typography;
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
              final natalView = Padding(
                padding: EdgeInsets.fromLTRB(
                  spacing.lg,
                  spacing.xl,
                  spacing.lg,
                  0,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _GlassCard(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Natal Yorum', style: typo.h2),
                          SizedBox(height: spacing.sm),
                          if (_isNatalLoading)
                            Row(
                              children: [
                                const SizedBox(
                                  height: 16,
                                  width: 16,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                ),
                                SizedBox(width: spacing.sm),
                                Text('Yukleniyor...', style: typo.body),
                              ],
                            )
                          else if (_natalError != null)
                            Text(
                              _natalError ?? '',
                              style: typo.body.copyWith(
                                color: Theme.of(context).colorScheme.error,
                              ),
                            )
                          else if ((_natalSummary ?? '').trim().isNotEmpty)
                            Text((_natalSummary ?? '').trim(), style: typo.body)
                          else
                            Text(
                              'Natal yorum henuz hazir degil.',
                              style: typo.body.copyWith(color: colors.muted),
                            ),
                          if (_supportingThreads.isNotEmpty) ...[
                            const _EditorialDivider(),
                            _SupportingThreadsSection(
                              items: _supportingThreads,
                            ),
                          ],
                        ],
                      ),
                    ),
                    SizedBox(height: spacing.xl),
                    if (!widget.readOnly) ...[
                      _GlassCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Arkadaslar', style: typo.h2),
                            SizedBox(height: spacing.sm),
                            Wrap(
                              spacing: spacing.sm,
                              runSpacing: spacing.sm,
                              children: [
                                OutlinedButton.icon(
                                  onPressed: () {
                                    Navigator.of(context).push(
                                      MaterialPageRoute<void>(
                                        builder: (_) => const PeopleListPage(),
                                      ),
                                    );
                                  },
                                  icon: const Icon(Icons.groups_outlined),
                                  label: const Text('Arkadaşlarını gör'),
                                ),
                                ElevatedButton.icon(
                                  onPressed: () {
                                    Navigator.of(context).push(
                                      MaterialPageRoute<void>(
                                        builder: (_) => const AddPersonPage(),
                                      ),
                                    );
                                  },
                                  icon: const Icon(Icons.person_add_alt_1),
                                  label: const Text('+ Kişi Ekle'),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      SizedBox(height: spacing.xl),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: OutlinedButton.icon(
                          onPressed: () async {
                            await Supabase.instance.client.auth.signOut();
                          },
                          icon: const Icon(Icons.logout),
                          label: const Text('Sign out'),
                        ),
                      ),
                    ] else
                      Align(
                        alignment: Alignment.centerLeft,
                        child: OutlinedButton.icon(
                          onPressed: () => Navigator.of(
                            context,
                            rootNavigator: true,
                          ).maybePop(),
                          icon: const Icon(Icons.arrow_back),
                          label: const Text('Geri Dön'),
                        ),
                      ),
                  ],
                ),
              );
              final contentView = _segmentIndex == 0
                  ? natalView
                  : PeriodCalendarTab(
                      profileOverride: widget.profileOverride,
                      embedded: true,
                    );

              return Scaffold(
                backgroundColor: colors.bg,
                body: CustomScrollView(
                  slivers: [
                    SliverAppBar(
                      expandedHeight: 360,
                      pinned: false,
                      floating: false,
                      automaticallyImplyLeading: false,
                      backgroundColor: Colors.transparent,
                      surfaceTintColor: Colors.transparent,
                      elevation: 0,
                      flexibleSpace: FlexibleSpaceBar(
                        background: _ProfileHeroScene(
                          displayName: displayName,
                          username: username,
                          avatarUrl: avatarUrl.isEmpty ? null : avatarUrl,
                          isAvatarUploading: _isAvatarUploading,
                          onAvatarEdit: widget.readOnly
                              ? null
                              : _pickAndUploadAvatar,
                          readOnly: widget.readOnly,
                          onSettingsTap: widget.readOnly || uid == null
                              ? null
                              : () => _showSettingsSheet(
                                  context: context,
                                  ref: ref,
                                  uid: uid,
                                  repo: repo,
                                  currentUserEmail: currentUserEmail,
                                ),
                        ),
                      ),
                    ),
                    SliverToBoxAdapter(child: const _EditorialDivider()),
                    SliverToBoxAdapter(
                      child: Padding(
                        padding: EdgeInsets.fromLTRB(
                          spacing.lg,
                          spacing.sm,
                          spacing.lg,
                          0,
                        ),
                        child: _GlassCard(
                          child: _ProfileStatsRow(
                            items: [
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
                        ),
                      ),
                    ),
                    if (kDebugMode)
                      SliverToBoxAdapter(
                        child: Padding(
                          padding: EdgeInsets.fromLTRB(
                            spacing.lg,
                            spacing.sm,
                            spacing.lg,
                            0,
                          ),
                          child: Align(
                            alignment: Alignment.centerLeft,
                            child: _ElementDebugChip(scores: elementScores),
                          ),
                        ),
                      ),
                    SliverToBoxAdapter(
                      child: Padding(
                        padding: EdgeInsets.fromLTRB(
                          spacing.lg,
                          spacing.xl,
                          spacing.lg,
                          0,
                        ),
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
                    ),
                    SliverToBoxAdapter(child: contentView),
                    SliverToBoxAdapter(child: SizedBox(height: spacing.xxl)),
                  ],
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
      final sun = _extractPlanetSign(map, 'Sun');
      final moon = _extractPlanetSign(map, 'Moon');
      final rising = _extractRisingSign(map);

      if (!mounted) {
        return;
      }

      setState(() {
        _natalSummary = summary;
        _supportingThreads = supportingThreads;
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
