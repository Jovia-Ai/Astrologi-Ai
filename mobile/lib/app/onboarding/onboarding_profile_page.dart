import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:mobile/app/tabs/tabs_shell.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';
import 'package:mobile/l10n/l10n.dart';

import '../profile/profile_providers.dart';

class OnboardingProfilePage extends ConsumerStatefulWidget {
  const OnboardingProfilePage({super.key});

  @override
  ConsumerState<OnboardingProfilePage> createState() =>
      _OnboardingProfilePageState();
}

class _OnboardingProfilePageState extends ConsumerState<OnboardingProfilePage> {
  final _nameController = TextEditingController();
  final _birthDateController = TextEditingController();
  final _birthTimeController = TextEditingController();
  final _cityController = TextEditingController();
  final _countryController = TextEditingController();
  bool _isSaving = false;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadExistingProfile();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _birthDateController.dispose();
    _birthTimeController.dispose();
    _cityController.dispose();
    _countryController.dispose();
    super.dispose();
  }

  Future<void> _loadExistingProfile() async {
    final uid = Supabase.instance.client.auth.currentUser?.id;
    if (uid == null) {
      if (mounted) {
        setState(() {
          _error = context.l10n.sessionExpiredLoginAgain;
          _isLoading = false;
        });
      }
      return;
    }

    try {
      final profile = await ref.read(userProfileProvider.future);
      if (profile != null && mounted) {
        _nameController.text = (profile['name'] ?? '').toString();
        _birthDateController.text = (profile['birth_date'] ?? '').toString();
        _birthTimeController.text = (profile['birth_time'] ?? '').toString();
        _cityController.text = (profile['city'] ?? '').toString();
        _countryController.text = (profile['country'] ?? '').toString();
      }
    } catch (e) {
      if (mounted) {
        setState(() => _error = context.l10n.errorFailedToLoadProfile('$e'));
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _save() async {
    final l10n = context.l10n;
    final uid = Supabase.instance.client.auth.currentUser?.id;
    if (uid == null) {
      setState(() => _error = l10n.sessionExpiredLoginAgain);
      return;
    }

    final name = _nameController.text.trim();
    final birthDate = _birthDateController.text.trim();
    final birthTime = _birthTimeController.text.trim();
    final city = _cityController.text.trim();
    final country = _countryController.text.trim();
    if (name.isEmpty ||
        birthDate.isEmpty ||
        birthTime.isEmpty ||
        city.isEmpty ||
        country.isEmpty) {
      setState(() => _error = l10n.errorPleaseFillAllFields);
      return;
    }

    setState(() {
      _isSaving = true;
      _error = null;
    });

    try {
      final repo = ref.read(profileRepositoryProvider);
      final email = Supabase.instance.client.auth.currentUser?.email;
      final place = country.isEmpty ? city : '$city, $country';
      final timezone = DateTime.now().timeZoneName;

      await repo.upsertProfileBasics(userId: uid, fullName: name, email: email);
      await repo.upsertBirthData(
        userId: uid,
        birthDate: birthDate,
        birthTime: birthTime,
        place: place,
        city: city,
        country: country,
        timezone: timezone,
        latitude: null,
        longitude: null,
      );
      ref.invalidate(userProfileProvider);
      if (mounted) {
        Navigator.of(
          context,
        ).pushReplacement(MaterialPageRoute(builder: (_) => const TabsShell()));
      }
    } catch (e) {
      if (mounted) {
        setState(() => _error = l10n.errorFailedToSaveProfile('$e'));
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;
    final profile = context.profileTheme;
    final spacing = profile.spacing;
    final l10n = context.l10n;

    return Scaffold(
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SafeArea(
              child: SingleChildScrollView(
                keyboardDismissBehavior:
                    ScrollViewKeyboardDismissBehavior.onDrag,
                padding: EdgeInsets.fromLTRB(
                  spacing.s24,
                  spacing.s20,
                  spacing.s24,
                  spacing.s20 + bottomInset,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    JoviaProfileTopBar(
                      label: l10n.onboardingProfileTopLabel,
                      centerText: l10n.onboardingProfileTopCenter,
                      reserveTrailingSpace: true,
                    ),
                    SizedBox(height: spacing.s24),
                    JoviaSectionHeader(
                      label: l10n.onboardingSectionLabel,
                      title: l10n.onboardingProfileTitle,
                      body: l10n.onboardingProfileBody,
                      variant: JoviaSectionHeaderVariant.editorial,
                    ),
                    SizedBox(height: spacing.s24),
                    JoviaSurfaceCard(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          if (_error != null) ...[
                            Text(
                              _error!,
                              style: profile.typography.meta.copyWith(
                                color: Theme.of(context).colorScheme.error,
                              ),
                            ),
                            SizedBox(height: spacing.s12),
                          ],
                          TextField(
                            controller: _nameController,
                            decoration: InputDecoration(
                              labelText: l10n.nameLabel,
                            ),
                          ),
                          SizedBox(height: spacing.s12),
                          TextField(
                            controller: _birthDateController,
                            decoration: InputDecoration(
                              labelText: l10n.birthDateLabel,
                            ),
                          ),
                          SizedBox(height: spacing.s12),
                          TextField(
                            controller: _birthTimeController,
                            decoration: InputDecoration(
                              labelText: l10n.birthTimeLabel,
                            ),
                          ),
                          SizedBox(height: spacing.s12),
                          TextField(
                            controller: _cityController,
                            decoration: InputDecoration(
                              labelText: l10n.cityLabel,
                            ),
                          ),
                          SizedBox(height: spacing.s12),
                          TextField(
                            controller: _countryController,
                            decoration: InputDecoration(
                              labelText: l10n.countryLabel,
                            ),
                          ),
                          SizedBox(height: spacing.s20),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              onPressed: _isSaving ? null : _save,
                              child: _isSaving
                                  ? const SizedBox(
                                      height: 18,
                                      width: 18,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                      ),
                                    )
                                  : Text(l10n.commonSave),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
