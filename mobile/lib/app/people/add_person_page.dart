import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../profile/profile_providers.dart';
import 'people_providers.dart';
import 'people_repository.dart';
import 'person_profile.dart';

class AddPersonPage extends ConsumerStatefulWidget {
  const AddPersonPage({super.key, this.initialPerson});

  final PersonProfile? initialPerson;

  @override
  ConsumerState<AddPersonPage> createState() => _AddPersonPageState();
}

class _AddPersonPageState extends ConsumerState<AddPersonPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _birthDateController = TextEditingController();
  final _birthTimeController = TextEditingController();
  final _cityController = TextEditingController();
  final _countryController = TextEditingController(text: 'TR');

  DateTime? _birthDate;
  TimeOfDay? _birthTime;
  bool _saving = false;

  bool get _isEditMode => widget.initialPerson != null;

  @override
  void initState() {
    super.initState();
    final initial = widget.initialPerson;
    if (initial == null) {
      return;
    }
    _nameController.text = initial.name;
    _birthDateController.text = initial.birthDate;
    _birthTimeController.text = (initial.birthTime ?? '').trim();
    _cityController.text = initial.city;
    _countryController.text = initial.country;

    _birthDate = DateTime.tryParse(initial.birthDate);
    final rawTime = (initial.birthTime ?? '').trim();
    final parts = rawTime.split(':');
    if (parts.length >= 2) {
      final hour = int.tryParse(parts[0]);
      final minute = int.tryParse(parts[1]);
      if (hour != null && minute != null) {
        _birthTime = TimeOfDay(hour: hour, minute: minute);
      }
    }
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(_isEditMode ? 'Kişiyi Düzenle' : 'Kişi Ekle')),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              TextFormField(
                controller: _nameController,
                textCapitalization: TextCapitalization.words,
                decoration: const InputDecoration(labelText: 'Ad'),
                validator: (value) {
                  if ((value ?? '').trim().isEmpty) {
                    return 'Ad zorunlu';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _birthDateController,
                readOnly: true,
                decoration: const InputDecoration(labelText: 'Doğum tarihi'),
                onTap: _pickBirthDate,
                validator: (value) {
                  if ((value ?? '').trim().isEmpty) {
                    return 'Doğum tarihi zorunlu';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _birthTimeController,
                readOnly: true,
                decoration: const InputDecoration(
                  labelText: 'Doğum saati (opsiyonel)',
                ),
                onTap: _pickBirthTime,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _cityController,
                textCapitalization: TextCapitalization.words,
                decoration: const InputDecoration(labelText: 'Şehir'),
                validator: (value) {
                  if ((value ?? '').trim().isEmpty) {
                    return 'Şehir zorunlu';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _countryController,
                textCapitalization: TextCapitalization.characters,
                decoration: const InputDecoration(labelText: 'Ülke'),
                validator: (value) {
                  if ((value ?? '').trim().isEmpty) {
                    return 'Ülke zorunlu';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 8),
              Text(
                'Doğum saati boş bırakılırsa varsayılan 12:00 kullanılır.',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                onPressed: _saving ? null : _save,
                icon: _saving
                    ? const SizedBox(
                        height: 16,
                        width: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.save_outlined),
                label: Text(_saving ? 'Kaydediliyor...' : 'Kaydet'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _pickBirthDate() async {
    final now = DateTime.now();
    final initial = _birthDate ?? DateTime(now.year - 25, now.month, now.day);
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(1900, 1, 1),
      lastDate: now,
    );
    if (picked == null) {
      return;
    }
    setState(() {
      _birthDate = picked;
      _birthDateController.text =
          '${picked.year.toString().padLeft(4, '0')}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
    });
  }

  Future<void> _pickBirthTime() async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _birthTime ?? const TimeOfDay(hour: 12, minute: 0),
    );
    if (picked == null) {
      return;
    }
    setState(() {
      _birthTime = picked;
      _birthTimeController.text =
          '${picked.hour.toString().padLeft(2, '0')}:${picked.minute.toString().padLeft(2, '0')}';
    });
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final ownerUserId = ref.read(currentUserIdProvider);
    if (ownerUserId == null) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Önce giriş yapmalısın.')));
      return;
    }

    setState(() => _saving = true);

    try {
      final repository = ref.read(peopleRepositoryProvider);
      if (_isEditMode) {
        await repository.updatePerson(
          ownerUserId: ownerUserId,
          personId: widget.initialPerson!.id,
          name: _nameController.text.trim(),
          birthDate: _birthDateController.text.trim(),
          birthTime: _birthTimeController.text.trim().isEmpty
              ? null
              : _birthTimeController.text.trim(),
          city: _cityController.text.trim(),
          country: _countryController.text.trim(),
        );
      } else {
        await repository.createPerson(
          ownerUserId: ownerUserId,
          name: _nameController.text.trim(),
          birthDate: _birthDateController.text.trim(),
          birthTime: _birthTimeController.text.trim().isEmpty
              ? null
              : _birthTimeController.text.trim(),
          city: _cityController.text.trim(),
          country: _countryController.text.trim(),
        );
      }

      ref.invalidate(peopleListProvider);

      if (!mounted) {
        return;
      }
      Navigator.of(context).pop(true);
    } catch (error) {
      if (!mounted) {
        return;
      }
      final message = error is PeopleQueryException
          ? error.userMessage
          : 'Kayıt başarısız: $error';
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }
}
