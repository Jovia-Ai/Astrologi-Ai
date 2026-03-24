import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:mobile/app/profile/profile_repository.dart';
import 'package:mobile/app/tabs/tabs_shell.dart';
import 'package:mobile/design/theme/profile_theme_extension.dart';
import 'package:mobile/design/widgets/jovia_editorial.dart';

class OnboardingBirthPage extends StatefulWidget {
  const OnboardingBirthPage({super.key});

  @override
  State<OnboardingBirthPage> createState() => _OnboardingBirthPageState();
}

class _OnboardingBirthPageState extends State<OnboardingBirthPage> {
  final _profileRepo = ProfileRepository();
  final _birthDateController = TextEditingController();
  final _birthTimeController = TextEditingController();
  final _cityController = TextEditingController();
  final _countryController = TextEditingController();

  bool _isLoading = true;
  bool _isSaving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadExistingBirthData();
  }

  @override
  void dispose() {
    _birthDateController.dispose();
    _birthTimeController.dispose();
    _cityController.dispose();
    _countryController.dispose();
    super.dispose();
  }

  Future<void> _loadExistingBirthData() async {
    final uid = Supabase.instance.client.auth.currentUser?.id;
    if (uid == null) {
      if (mounted) {
        setState(() {
          _error = 'Session expired. Please login again.';
          _isLoading = false;
        });
      }
      return;
    }

    try {
      final row = await _profileRepo.getProfile(uid);
      if (row != null && mounted) {
        _birthDateController.text = (row['birth_date'] ?? '').toString();
        _birthTimeController.text = (row['birth_time'] ?? '').toString();
        _cityController.text = (row['city'] ?? '').toString();
        _countryController.text = (row['country'] ?? '').toString();
      }
    } catch (e) {
      if (mounted) {
        setState(() => _error = 'Failed to load birth data: $e');
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _save() async {
    final uid = Supabase.instance.client.auth.currentUser?.id;
    if (uid == null) {
      setState(() => _error = 'Session expired. Please login again.');
      return;
    }

    final birthDate = _birthDateController.text.trim();
    final birthTime = _birthTimeController.text.trim();
    final city = _cityController.text.trim();
    final country = _countryController.text.trim();
    final place = country.isEmpty ? city : '$city, $country';
    final timezone = DateTime.now().timeZoneName;

    if (birthDate.isEmpty || birthTime.isEmpty || place.isEmpty) {
      setState(
        () => _error = 'Please fill birth date, time, city and country.',
      );
      return;
    }

    setState(() {
      _isSaving = true;
      _error = null;
    });

    try {
      await _profileRepo.upsertBirthData(
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

      if (mounted) {
        Navigator.of(
          context,
        ).pushReplacement(MaterialPageRoute(builder: (_) => const TabsShell()));
      }
    } catch (e) {
      if (mounted) {
        setState(() => _error = 'Failed to save birth data: $e');
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    final bottomInset = MediaQuery.of(context).viewInsets.bottom;
    final profile = context.profileTheme;
    final spacing = profile.spacing;

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
          padding: EdgeInsets.fromLTRB(
            spacing.s24,
            spacing.s20,
            spacing.s24,
            spacing.s20 + bottomInset,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const JoviaProfileTopBar(
                label: 'Dogum',
                centerText: 'temel veriler',
                reserveTrailingSpace: true,
              ),
              SizedBox(height: spacing.s24),
              const JoviaSectionHeader(
                label: 'Onboarding',
                title: 'Haritanin dogum eksenini tamamla',
                body:
                    'Bu bilgiler backend akisina aynen gider; burada sadece tipografik omurga profile yaklasti.',
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
                      controller: _birthDateController,
                      decoration: const InputDecoration(
                        labelText: 'Birth date (YYYY-MM-DD)',
                      ),
                    ),
                    SizedBox(height: spacing.s12),
                    TextField(
                      controller: _birthTimeController,
                      decoration: const InputDecoration(
                        labelText: 'Birth time (HH:mm)',
                      ),
                    ),
                    SizedBox(height: spacing.s12),
                    TextField(
                      controller: _cityController,
                      decoration: const InputDecoration(labelText: 'City'),
                    ),
                    SizedBox(height: spacing.s12),
                    TextField(
                      controller: _countryController,
                      decoration: const InputDecoration(labelText: 'Country'),
                    ),
                    SizedBox(height: spacing.s24),
                    ElevatedButton(
                      onPressed: _isSaving ? null : _save,
                      child: _isSaving
                          ? const SizedBox(
                              height: 18,
                              width: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Continue'),
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
