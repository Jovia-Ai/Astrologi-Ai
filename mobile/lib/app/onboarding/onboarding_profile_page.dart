import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:mobile/app/tabs/tabs_shell.dart';

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
          _error = 'Session expired. Please log in again.';
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
        setState(() => _error = 'Failed to load profile: $e');
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
      setState(() => _error = 'Session expired. Please log in again.');
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
      setState(() => _error = 'Please fill all fields.');
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
        setState(() => _error = 'Failed to save profile: $e');
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

    return Scaffold(
      appBar: AppBar(title: const Text('Profile Setup')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SafeArea(
              child: SingleChildScrollView(
                keyboardDismissBehavior:
                    ScrollViewKeyboardDismissBehavior.onDrag,
                padding: EdgeInsets.fromLTRB(16, 16, 16, 16 + bottomInset),
                child: Column(
                  children: [
                    if (_error != null) ...[
                      Text(
                        _error!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],
                    TextField(
                      controller: _nameController,
                      decoration: const InputDecoration(labelText: 'Name'),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _birthDateController,
                      decoration: const InputDecoration(
                        labelText: 'Birth date (YYYY-MM-DD)',
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _birthTimeController,
                      decoration: const InputDecoration(
                        labelText: 'Birth time (HH:mm)',
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _cityController,
                      decoration: const InputDecoration(labelText: 'City'),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _countryController,
                      decoration: const InputDecoration(labelText: 'Country'),
                    ),
                    const SizedBox(height: 20),
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
                            : const Text('Save'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
